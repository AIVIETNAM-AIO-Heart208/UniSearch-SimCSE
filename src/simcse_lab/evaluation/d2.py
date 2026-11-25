"""Score saved D2 rankings at article, topic and clause level."""

from __future__ import annotations

import random
from collections.abc import Callable, Mapping, Sequence
from math import comb
from statistics import fmean, quantiles

from simcse_lab.retrieval.hcmus import chunk_clause_id, regulation_clauses

from .stats import (
    Row, Topics, _cosine, _levels, _queries, _ranked_articles, _run,
    first_relevant_rank, paired_bootstrap, warning_metrics,
)


METHODS = ("bm25", "dense", "hybrid")
LEVELS = ("article", "topic")
HIT_CUTOFFS = (1, 3, 5, 10)


def _catalog(chunks: Sequence[Row], articles: Mapping[str, Row], topics: Topics) -> tuple[dict, dict]:
    if articles.keys() != topics.keys():
        raise ValueError("Regulations and the topic map must cover the same articles")
    clauses = {article: regulation_clauses(row) for article, row in articles.items()}
    clause_articles = {key: article for article, spans in clauses.items() for key in spans if key is not None}
    catalog = {}
    for row in chunks:
        chunk = row["chunk_id"]
        article = row["article_id"]
        if chunk in catalog or article not in articles or row["topic_id"] != topics[article]:
            raise ValueError(f"{chunk!r}: invalid or duplicate corpus chunk")
        clause = chunk_clause_id(row, clauses[article])
        source = articles[article]
        offset = source["char_start"]
        if row["text"] != source["text"][row["char_start"] - offset:row["char_end"] - offset]:
            raise ValueError(f"{chunk!r}: text does not match its source span")
        catalog[chunk] = (article, clause)
    if ({article for article, _ in catalog.values()} != articles.keys()
            or {clause for _, clause in catalog.values() if clause is not None} != clause_articles.keys()):
        raise ValueError("Corpus chunks must cover all mapped articles and their numbered clauses")
    return catalog, clause_articles


def _question_labels(query: Row, clause_articles: Mapping[str, str]) -> set[str]:
    qid = query["qid"]
    if not isinstance(query.get("question"), str) or not query["question"].strip():
        raise ValueError(f"{qid!r}: expected question text")
    if query.get("origin") not in ("team", "form", None):
        raise ValueError(f"{qid!r}: invalid question origin")
    clauses = query.get("gold_clause_ids")
    if not isinstance(clauses, (list, tuple)) or any(
        not isinstance(key, str) or key not in clause_articles
        or clause_articles[key] not in query["gold_article_ids"] for key in clauses
    ):
        raise ValueError(f"{qid!r}: gold_clause_ids must use the clause IDs of its gold articles")
    return set(clauses)


def _query_scores(query: Row, row: Row, topics: Topics, catalog: Mapping, clauses: set[str]) -> dict:
    ranked = _ranked_articles(row, topics)
    for article, _, chunk in row["ranked"]:
        if chunk not in catalog or catalog[chunk][0] != article:
            raise ValueError(f"{query['qid']!r}: {chunk!r} does not belong to {article!r}")
    _cosine(row)
    gold = set(query["gold_article_ids"])
    return {
        "article": first_relevant_rank(ranked, gold, 10),
        "topic": first_relevant_rank(dict.fromkeys(topics[a] for a in ranked), {topics[a] for a in gold}, 10),
        "clause": catalog[row["ranked"][0][2]][1] in clauses if clauses else None,
    }


def _metrics(scores: Sequence[dict]) -> dict:
    result = {}
    for level in LEVELS:
        ranks = [row[level] for row in scores]
        result[level] = {
            **{f"hit_at_{k}": fmean(rank is not None and rank <= k for rank in ranks) if ranks else None
               for k in HIT_CUTOFFS},
            "mrr_at_10": fmean(1 / rank if rank is not None else 0 for rank in ranks) if ranks else None,
        }
    clauses = [row["clause"] for row in scores if row["clause"] is not None]
    result["clause"] = {"n": len(clauses), "hit_at_1": fmean(clauses) if clauses else None}
    return result


def _slice(queries: Sequence[Row], aligned: Mapping, scores: Mapping, topics: Topics) -> dict:
    qids = [q["qid"] for q in queries]
    return {
        "n": len(qids), "qids": qids,
        "metrics": {method: _metrics([scores[method][qid] for qid in qids]) for method in METHODS},
        "hybrid_minus_bm25": paired_bootstrap(
            queries, [aligned["bm25"][qid] for qid in qids], [aligned["hybrid"][qid] for qid in qids],
            article_to_topic=topics,
        ) if qids else None,
    }


def _overlap_groups(queries: Sequence[Row], articles: Mapping[str, Row], tokenize: Callable[[str], set[str]]) -> tuple:
    gold_articles = {article for query in queries for article in query["gold_article_ids"]}
    terms = {article: tokenize(articles[article]["text"]) for article in gold_articles}

    def jaccard(a: set[str], b: set[str]) -> float:
        return len(a & b) / len(a | b) if a or b else 0.0

    overlaps = {}
    for q in queries:
        question = tokenize(q["question"])
        overlaps[q["qid"]] = max(jaccard(question, terms[a]) for a in q["gold_article_ids"])
    values = list(overlaps.values())
    groups: dict[str, list[Row]] = {"low": [], "medium": [], "high": []}
    if not values:
        return None, groups
    low, high = quantiles(values, n=3, method="inclusive") if len(values) > 1 else (values[0], values[0])
    for q in queries:
        value = overlaps[q["qid"]]
        name = "low" if value <= low else "medium" if value <= high else "high"
        groups[name].append(q)
    return [low, high], groups


def _random_baseline(queries: Sequence[Row], topics: Topics) -> dict | None:
    if not queries:
        return None
    articles = sorted(topics)
    n_articles = len(articles)
    rng = random.Random(42)
    n_permutations = 1000
    grouped_orders = [tuple(dict.fromkeys(topics[a] for a in rng.sample(articles, n_articles)))
                      for _ in range(n_permutations)]
    article_rates, topic_ranks = [], []
    for q in queries:
        gold = set(q["gold_article_ids"])
        misses = [comb(n_articles - len(gold), k) / comb(n_articles, k) if k <= n_articles else 0.0
                  for k in range(11)]
        article_rates.append({**{f"hit_at_{k}": 1 - misses[k] for k in HIT_CUTOFFS},
                              "mrr_at_10": sum((misses[k - 1] - misses[k]) / k for k in range(1, 11))})
        gold_topics = {topics[a] for a in gold}
        topic_ranks.extend(first_relevant_rank(order, gold_topics, 10) for order in grouped_orders)
    return {
        "article": {key: fmean(row[key] for row in article_rates) for key in article_rates[0]},
        "topic": {**{f"hit_at_{k}": fmean(rank is not None and rank <= k for rank in topic_ranks)
                      for k in HIT_CUTOFFS},
                  "mrr_at_10": fmean(1 / rank if rank is not None else 0 for rank in topic_ranks)},
        "seed": 42, "n_permutations": n_permutations,
    }


def _risk_point(warnings: Mapping) -> dict:
    accepted = warnings["groups"]["confident"]
    return {
        "threshold": warnings["threshold"], "coverage": warnings["coverage"],
        "accepted": accepted["n"], "accepted_in_scope": accepted["n_in_scope"],
        "risk": {key: 1 - value if value is not None else None for key, value in accepted["hit_at_1"].items()},
        "false_confidence": warnings["false_confidence"],
    }


def evaluate_d2(
    queries: Sequence[Row], runs: Mapping[str, Sequence[Row]], chunks: Sequence[Row],
    articles: Mapping[str, Row], topics: Topics, *, threshold: float,
    tokenize: Callable[[str], set[str]],
) -> dict:
    """Compare the three methods on one finalized D2 test set and a fixed threshold."""
    manifest = _queries(queries)
    if next(iter(manifest.values()))["source"] != "d2" or runs.keys() != set(METHODS):
        raise ValueError("Expected D2-test queries and bm25, dense, hybrid runs")
    _levels(manifest, topics)
    catalog, clause_articles = _catalog(chunks, articles, topics)
    labels = {qid: _question_labels(query, clause_articles) for qid, query in manifest.items()}
    aligned = {method: _run(rows, manifest) for method, rows in runs.items()}
    scores = {method: {qid: _query_scores(query, rows[qid], topics, catalog, labels[qid])
                       for qid, query in manifest.items()} for method, rows in aligned.items()}
    eligible = [q for q in queries if q["in_scope"]]
    cutoffs, groups = _overlap_groups(eligible, articles, tokenize)
    fixed = warning_metrics(queries, runs["hybrid"], threshold=threshold, article_to_topic=topics)
    points = [_risk_point(warning_metrics(queries, runs["hybrid"], threshold=value, article_to_topic=topics))
              for value in sorted({_cosine(row) for row in runs["hybrid"]}, reverse=True)]
    return {
        "split": "D2-test", "n_queries": len(queries),
        "overall": _slice(eligible, aligned, scores, topics),
        "random_baseline": _random_baseline(eligible, topics),
        "overlap": {"cutoffs": cutoffs, "groups": {name: _slice(rows, aligned, scores, topics)
                                                   for name, rows in groups.items()}},
        "form": _slice([q for q in eligible if q.get("origin") == "form"], aligned, scores, topics)
        if any(q.get("origin") == "form" for q in queries) else None,
        "warnings": fixed, "operating_point": _risk_point(fixed), "risk_coverage": points,
    }
