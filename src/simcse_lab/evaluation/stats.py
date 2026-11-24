"""Paired retrieval comparisons and confidence warnings for PROJECT sections 5.4 and 6.3."""

from __future__ import annotations

import math
import random
from collections.abc import Iterable, Mapping
from statistics import fmean, quantiles
from typing import Any, Union

Identifier = Union[str, int]
Row = Mapping[str, Any]
Topics = Mapping[Identifier, str]


def _valid_id(value: object) -> bool:
    return type(value) is int or (isinstance(value, str) and bool(value.strip()))


def _index(rows: Iterable[Row], name: str) -> dict[Identifier, Row]:
    result = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError(f"{name}: expected a JSON object")
        qid = row.get("qid")
        if not _valid_id(qid) or qid in result:
            raise ValueError(f"{name}: invalid or duplicate qid {qid!r}")
        result[qid] = row
    return result


def _queries(rows: Iterable[Row]) -> dict[Identifier, Row]:
    queries = _index(rows, "queries")
    if not queries:
        raise ValueError("An evaluation split must contain at least one query")
    first = next(iter(queries.values()))
    split = (first.get("source"), first.get("split"))
    if split not in (("virhe4qa", "dev"), ("virhe4qa", "test"), ("d2", "test")):
        raise ValueError("Expected a single D1-dev, D1-test or D2-test split")
    for qid, query in queries.items():
        if (query.get("source"), query.get("split")) != split:
            raise ValueError("Expected a single D1-dev, D1-test or D2-test split")
        gold = query.get("gold_article_ids")
        if not isinstance(gold, (list, tuple)) or not all(_valid_id(a) for a in gold):
            raise ValueError(f"{qid!r}: invalid gold_article_ids")
        if query.get("in_scope") is not bool(gold) or (not gold and query["source"] == "virhe4qa"):
            raise ValueError(f"{qid!r}: in_scope and gold_article_ids disagree with the dataset")
    return queries


def _run(rows: Iterable[Row], queries: Mapping[Identifier, Row]) -> dict[Identifier, Row]:
    run = _index(rows, "run")
    if run.keys() != queries.keys():
        raise ValueError(f"Run qids differ from queries: missing {queries.keys() - run.keys()}, "
                         f"unexpected {run.keys() - queries.keys()}")
    return run


def _levels(queries: Mapping[Identifier, Row], topics: Topics | None) -> tuple[str, ...]:
    if next(iter(queries.values()))["source"] != "d2":
        if topics is not None:
            raise ValueError("An article-to-topic map applies only to D2")
        return ("article",)
    if not topics or not all(isinstance(t, str) and t.strip() for t in topics.values()):
        raise ValueError("D2 requires an article-to-topic map with nonempty topic IDs")
    for qid, query in queries.items():
        if not topics.keys() >= set(query["gold_article_ids"]):
            raise ValueError(f"{qid!r}: gold article missing from the topic map")
    return ("article", "topic")


def first_relevant_rank(ranked: Iterable[Identifier], gold: set[Identifier], limit: int):
    for rank, item in enumerate(ranked, start=1):
        if rank > limit:
            break
        if item in gold:
            return rank
    return None


def _rr_at_10(ranked: Iterable[Identifier], gold: set[Identifier]) -> float:
    rank = first_relevant_rank(ranked, gold, 10)
    return 1.0 / rank if rank is not None else 0.0


def _ranked_articles(row: Row, topics: Topics | None) -> list[Identifier]:
    """Validate the published order, preserving its tie breaks."""
    ranked = row.get("ranked")
    qid = row["qid"]
    if not isinstance(ranked, (list, tuple)) or not ranked:
        raise ValueError(f"{qid!r}: expected a nonempty ranked list")
    if topics is None and len(ranked) != 20:
        raise ValueError(f"{qid!r}: expected the D1 top-20 ranking")
    articles = []
    previous_score = math.inf
    for hit in ranked:
        if not isinstance(hit, (list, tuple)) or len(hit) != 3:
            raise ValueError(f"{qid!r}: expected [article_id, score, best_chunk_id] in ranked")
        article, score, chunk = hit
        if not _valid_id(article) or not _valid_id(chunk):
            raise ValueError(f"{qid!r}: invalid article or chunk ID in ranked")
        if type(score) not in (float, int) or not math.isfinite(score):
            raise ValueError(f"{qid!r}: expected a finite ranking score")
        if score > previous_score:
            raise ValueError(f"{qid!r}: ranked scores must be in descending order")
        previous_score = score
        articles.append(article)
    distinct = set(articles)
    if len(distinct) != len(articles):
        raise ValueError(f"{qid!r}: duplicate article in ranked")
    if topics is not None and distinct != topics.keys():
        raise ValueError(f"{qid!r}: D2 ranked must contain every mapped article exactly once")
    return articles


def _score(query: Row, row: Row, topics: Topics | None) -> dict[str, float]:
    articles = _ranked_articles(row, topics)
    gold = set(query["gold_article_ids"])
    scores = {"article": _rr_at_10(articles, gold)}
    if topics is not None:
        ranked_topics = dict.fromkeys(topics[a] for a in articles)
        scores["topic"] = _rr_at_10(ranked_topics, {topics[a] for a in gold})
    return scores


def _interval(differences: list[float], n_resamples: int, seed: int) -> dict[str, float]:
    # Reuse the same seeded draws for each metric and level on this split.
    rng = random.Random(seed)
    means = [fmean(rng.choices(differences, k=len(differences))) for _ in range(n_resamples)]
    cuts = quantiles(means, n=40, method="inclusive")
    return {"delta": fmean(differences), "lower": cuts[0], "upper": cuts[-1]}


def paired_bootstrap(
    queries: Iterable[Row], baseline: Iterable[Row], candidate: Iterable[Row], *,
    article_to_topic: Topics | None = None, n_resamples: int = 1000, seed: int = 42,
) -> dict[str, Any]:
    """Return candidate minus baseline with two-sided 95% percentile intervals.

    Pass decoded query/run records for a single split. Both runs must cover its
    qids exactly. Resample in-scope questions with replacement. For D2, pass
    the complete article_id -> topic_id map and both levels are returned.
    """
    if type(n_resamples) is not int or n_resamples < 2 or type(seed) is not int:
        raise ValueError("n_resamples must be an integer >= 2 and seed must be an integer")
    manifest = _queries(queries)
    levels = _levels(manifest, article_to_topic)
    base, cand = _run(baseline, manifest), _run(candidate, manifest)
    differences = {level: {"mrr_at_10": [], "hit_at_1": []} for level in levels}
    # Stable pairing and draws even if the caller shuffles the JSONL records.
    for qid in sorted(manifest, key=lambda key: (isinstance(key, str), key)):
        query = manifest[qid]
        before = _score(query, base[qid], article_to_topic)
        after = _score(query, cand[qid], article_to_topic)
        if query["in_scope"]:
            for level in levels:
                differences[level]["mrr_at_10"].append(after[level] - before[level])
                differences[level]["hit_at_1"].append((after[level] == 1) - (before[level] == 1))
    n = len(differences["article"]["mrr_at_10"])
    if not n:
        raise ValueError("Paired bootstrap needs at least one in-scope query")
    intervals = {}
    for level, metrics in differences.items():
        intervals[level] = {name: _interval(values, n_resamples, seed) for name, values in metrics.items()}
    return {"n_in_scope": n, "n_resamples": n_resamples, "seed": seed, "levels": intervals}


def _cosine(row: Row) -> float:
    value = row.get("top1_dense_cos")
    # A normalized float32 dot product can overshoot a unit endpoint slightly.
    if type(value) not in (int, float) or not -1.000001 <= value <= 1.000001:
        raise ValueError(f"{row['qid']!r}: invalid top1_dense_cos {value!r}")
    return max(-1.0, min(1.0, float(value)))


def select_threshold(
    queries: Iterable[Row], run: Iterable[Row], *, min_coverage: float = 0.8,
) -> float:
    """Largest observed cosine retaining at least min_coverage on D1-dev."""
    if type(min_coverage) not in (int, float) or not 0 < min_coverage <= 1:
        raise ValueError("min_coverage must be in (0, 1]")
    manifest = _queries(queries)
    if next(iter(manifest.values()))["split"] != "dev":
        raise ValueError("Threshold selection requires D1-dev")
    scores = []
    for row in _run(run, manifest).values():
        _ranked_articles(row, topics=None)
        scores.append(_cosine(row))
    scores.sort(reverse=True)
    return next(score for count, score in enumerate(scores, 1) if count / len(scores) >= min_coverage)


def warning_metrics(
    queries: Iterable[Row], run: Iterable[Row], *, threshold: float,
    article_to_topic: Topics | None = None,
) -> dict[str, Any]:
    """Evaluate a fixed threshold. A cosine equal to it counts as confident.

    Coverage uses every query. Group Hit@1 uses only in-scope queries.
    False confidence uses only out-of-scope queries. Empty rates are None.
    The warning always uses the raw top article's chunk cosine before grouping.
    """
    if type(threshold) not in (int, float) or not -1 <= threshold <= 1:
        raise ValueError("threshold must be a finite cosine in [-1, 1]")
    manifest = _queries(queries)
    levels = _levels(manifest, article_to_topic)
    aligned = _run(run, manifest)
    groups = {name: {"n": 0, "n_in_scope": 0, "hit_at_1": dict.fromkeys(levels, 0)}
              for name in ("confident", "warned")}
    for qid, query in manifest.items():
        row = aligned[qid]
        scores = _score(query, row, article_to_topic)
        group = groups["confident" if _cosine(row) >= threshold else "warned"]
        group["n"] += 1
        if query["in_scope"]:
            group["n_in_scope"] += 1
            for level, rr in scores.items():
                group["hit_at_1"][level] += rr == 1.0
    for group in groups.values():
        n = group["n_in_scope"]
        group["hit_at_1"] = {level: count / n if n else None
                             for level, count in group["hit_at_1"].items()}
    confident = groups["confident"]
    n_out = len(manifest) - sum(group["n_in_scope"] for group in groups.values())
    n_false = confident["n"] - confident["n_in_scope"]
    return {
        "threshold": threshold, "n_queries": len(manifest), "groups": groups,
        "coverage": confident["n"] / len(manifest),
        "n_out_of_scope": n_out, "n_confident_out_of_scope": n_false,
        "false_confidence": n_false / n_out if n_out else None,
    }
