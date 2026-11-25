"""Measure lexical-overlap groups from a saved D1-test retrieval run."""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import platform
import subprocess
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
from statistics import fmean, median, quantiles

from simcse_lab.evaluation.metrics import evaluate_d1
from simcse_lab.evaluation.stats import first_relevant_rank, paired_bootstrap
from simcse_lab.retrieval.preprocess import segment


E1_SUMMARY = Path("experiments/external_dataset/results/E1/d1-test.json")
METHODS = ("bm25", "dense", "hybrid")
BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_SEED = 42


def _checked_bytes(path: Path, expected_hash: str) -> bytes:
    data = path.read_bytes()
    if sha256(data).hexdigest() != expected_hash:
        raise ValueError(f"SHA-256 mismatch: {path}")
    return data


def _rows(record: dict[str, str]) -> list[dict]:
    return [json.loads(line) for line in _checked_bytes(Path(record["path"]), record["sha256"]).splitlines()]


def _gold_texts(data: bytes, queries: list[dict]) -> dict[str, str]:
    by_qid = {query["qid"]: query for query in queries}
    gold_texts = {}
    matched_qids = set()
    rows = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""), strict=True)
    for row in rows:
        qid = row["index"]
        if qid not in by_qid:
            continue
        query = by_qid[qid]
        text = row["context"]
        article_id = sha256(text.encode("utf-8")).hexdigest()
        if row["question"] != query["question"] or [article_id] != query["gold_article_ids"]:
            raise ValueError(f"CSV question or gold passage disagrees with the saved input: {qid}")
        matched_qids.add(qid)
        gold_texts[article_id] = text
    if matched_qids != by_qid.keys():
        raise ValueError("CSV must cover every saved D1-test question")
    return gold_texts


def _word_set(text: str) -> set[str]:
    return {token for token in segment(text).lower().split() if any(char.isalnum() for char in token)}


def _evaluate_groups(groups: dict[str, list[dict]], run_rows: dict[str, list[dict]]) -> dict:
    runs = {method: {row["qid"]: row for row in rows} for method, rows in run_rows.items()}
    results = {}
    for group, queries in groups.items():
        group_runs = {method: [run[q["qid"]] for q in queries] for method, run in runs.items()}
        metrics = {method: evaluate_d1(queries, rows) for method, rows in group_runs.items()}
        for method, rows in group_runs.items():
            ranks = [
                first_relevant_rank((hit[0] for hit in row["ranked"]), set(query["gold_article_ids"]), 10)
                for query, row in zip(queries, rows, strict=True)
            ]
            metrics[method].update({
                f"hit_at_{k}": fmean(rank is not None and rank <= k for rank in ranks)
                for k in (5, 10)
            })
        interval = paired_bootstrap(
            queries, group_runs["bm25"], group_runs["hybrid"],
            n_resamples=BOOTSTRAP_RESAMPLES, seed=BOOTSTRAP_SEED,
        )
        results[group] = {"metrics": metrics, "hybrid_minus_bm25": interval["levels"]["article"]}
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--e1-summary", type=Path, default=E1_SUMMARY)
    parser.add_argument("--input", type=Path, help="Pinned CSV, defaults to the path in the E1 summary")
    parser.add_argument("--output", type=Path, required=True, help="New result JSON file")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Use a new output file")

    e1_bytes = args.e1_summary.read_bytes()
    e1 = json.loads(e1_bytes)
    if e1["split"] != "D1-test":
        raise ValueError("Expected a saved D1-test run")
    query_record = e1["verification"]["inputs"]["queries.jsonl"]
    queries = _rows(query_record)
    if (len({query["qid"] for query in queries}) != len(queries) or len(queries) != e1["queries"]
            or any((q["source"], q["split"], q["in_scope"]) != ("virhe4qa", "test", True) for q in queries)):
        raise ValueError("Expected distinct in-scope ViRHE4QA test questions")
    csv_path = args.input or Path(e1["run"]["input"])
    csv_hash = e1["dataset"]["sha256"]
    gold_text = _gold_texts(_checked_bytes(csv_path, csv_hash), queries)
    gold_words = {article: _word_set(text) for article, text in gold_text.items()}
    overlaps, lengths = {}, {}
    for query in queries:
        qid = query["qid"]
        reference = gold_words[query["gold_article_ids"][0]]
        question = _word_set(query["question"])
        union = question | reference
        overlaps[qid] = len(question & reference) / len(union) if union else 0.0
        lengths[qid] = len(reference)

    low_cut, medium_cut = quantiles(overlaps.values(), n=3, method="inclusive")
    groups = {"low": [], "medium": [], "high": []}
    for query in queries:
        overlap = overlaps[query["qid"]]
        group = "low" if overlap <= low_cut else "medium" if overlap <= medium_cut else "high"
        groups[group].append(query)
    if not all(groups.values()):
        raise ValueError("Tertile cutoffs must produce three nonempty groups")

    run_rows = {method: _rows(e1["rankings"][method]) for method in METHODS}
    for method, rows in run_rows.items():
        if any(e1["metrics"][method][key] != value for key, value in evaluate_d1(queries, rows).items()):
            raise ValueError(f"Saved E1 metrics disagree with the {method} run")
    results = _evaluate_groups(groups, run_rows)
    for group, members in groups.items():
        qids = sorted(query["qid"] for query in members)
        results[group].update({
            "queries": len(qids), "qids": qids,
            "jaccard_range": [min(overlaps[qid] for qid in qids), max(overlaps[qid] for qid in qids)],
            "median_gold_unique_tokens": median(lengths[qid] for qid in qids),
        })
    for method in METHODS:
        for metric, value in e1["metrics"][method].items():
            combined = math.fsum(
                result["metrics"][method][metric] * result["queries"] for result in results.values()
            ) / len(queries)
            if not math.isclose(combined, value, rel_tol=0, abs_tol=1e-15):
                raise ValueError(f"Group metrics do not reproduce E1: {method} {metric}")

    summary = {
        "split": "D1-test", "queries": len(queries), "frozen": e1["frozen"],
        "inputs": {
            "e1_summary": {"path": args.e1_summary.as_posix(), "sha256": sha256(e1_bytes).hexdigest()},
            "csv": {"path": csv_path.as_posix(), "sha256": csv_hash},
            "queries": query_record, "rankings": e1["rankings"],
        },
        "grouping": {
            "similarity": "Jaccard on distinct lowercased Pyvi tokens with an alphanumeric character",
            "reference": "Full gold passage from the pinned CSV",
            "cutoffs": [low_cut, medium_cut],
            "method": "Inclusive, linearly interpolated 1/3 and 2/3 quantiles",
            "intervals": "low: j <= q1; medium: q1 < j <= q2; high: j > q2",
        },
        "bootstrap": {"n_resamples": BOOTSTRAP_RESAMPLES, "seed": BOOTSTRAP_SEED, "confidence_level": 0.95},
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "device": "cpu",
            "processor": platform.processor(),
            **{name: version(name) for name in ("pyvi", "scikit-learn", "sklearn-crfsuite", "python-crfsuite")},
        },
        "run": {
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "runner_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "arguments": {
                "e1_summary": args.e1_summary.as_posix(), "input": csv_path.as_posix(),
                "output": args.output.as_posix(),
            },
        },
        "groups": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(summary, file, indent=2, allow_nan=False)
        file.write("\n")
    print(f"Saved D1-test lexical-overlap results to {args.output}")


if __name__ == "__main__":
    main()
