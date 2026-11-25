"""Export complete D1-dev chunk scores and select the retrieval settings."""

import argparse
import csv
import io
import json
import platform
import subprocess
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

from data.prepare_virhe4qa import SEED, SHA256, prepare
from experiments.external_dataset.run_dense_dev import read_rows, write_rows
from simcse_lab.evaluation.metrics import evaluate_d1
from simcse_lab.evaluation.stats import select_threshold, warning_metrics
from simcse_lab.model.encoders import MAX_LENGTH, MODEL_ID, REVISION, SimCSEEncoder, verify_snapshot
from simcse_lab.retrieval.ingest import article_chunks
from simcse_lab.retrieval.search import RetrievalIndex


BATCH_SIZE = 16
THREADS = 4
MIN_COVERAGE = 0.8


def _prepare_dev(csv_path: Path) -> tuple[list[dict], list[dict], dict]:
    content = csv_path.read_bytes()
    if sha256(content).hexdigest() != SHA256:
        raise ValueError("D1 CSV does not match the pinned SHA-256")
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig"), newline=""), strict=True)
    corpus, queries, split = prepare(list(reader))
    dev = [query for query in queries if query["split"] == "dev"]
    if len(dev) != 224 or len(corpus) != 297:
        raise ValueError("Expected 224 D1-dev queries and 297 source passages")
    return corpus, dev, split


def _export_scores(index, queries, path: Path):
    import numpy as np

    scores = list(index.score([query["question"] for query in queries]))
    if len(scores) != len(queries):
        raise ValueError("Expected one score pair per dev query")
    lexical, dense = zip(*scores)
    bm25 = np.asarray(lexical, dtype=np.float64)
    cosine = np.asarray(dense, dtype=np.float64)
    expected_shape = (len(queries), len(index.chunks))
    if bm25.shape != expected_shape or cosine.shape != expected_shape:
        raise ValueError("Scores must cover every dev query and chunk")
    if not np.isfinite(bm25).all() or not np.isfinite(cosine).all():
        raise ValueError("Non-finite chunk scores")

    qids = [query["qid"] for query in queries]
    chunk_ids = [chunk["chunk_id"] for chunk in index.chunks]
    article_ids = [chunk["article_id"] for chunk in index.chunks]
    np.savez_compressed(path, qids=qids, chunk_ids=chunk_ids, article_ids=article_ids,
                        bm25=bm25, cosine=cosine)
    with np.load(path, allow_pickle=False) as saved:
        if (saved["qids"].tolist() != qids or saved["chunk_ids"].tolist() != chunk_ids
                or saved["article_ids"].tolist() != article_ids
                or not np.array_equal(saved["bm25"], bm25) or not np.array_equal(saved["cosine"], cosine)):
            raise ValueError("Score IDs or values changed after export")
        return list(zip(saved["bm25"].tolist(), saved["cosine"].tolist()))


def _sweep(index, queries, scores):
    trials, runs = [], {}
    for step in range(11):
        weight = step / 10
        run = []
        for query, score_pair in zip(queries, scores):
            ranked, cosine = index.rank(score_pair, "hybrid", weight=weight, k=20)
            run.append({"qid": query["qid"], "ranked": ranked, "top1_dense_cos": cosine})
        runs[weight] = run
        trials.append({"weight": weight, **evaluate_d1(queries, run)})

    selected = max(trials, key=lambda trial: (trial["mrr_at_10"], -trial["weight"]))
    return trials, selected, runs[selected["weight"]]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Pinned ViRHE4QA CSV")
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New output directory")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Use a new output directory")

    import torch

    start = perf_counter()
    corpus, queries, split = _prepare_dev(args.input)
    snapshot = verify_snapshot(args.model_path)
    torch.set_num_threads(THREADS)
    torch.manual_seed(SEED)
    encoder = SimCSEEncoder(str(args.model_path), "cpu")
    chunks = [chunk for passage in corpus for chunk in article_chunks(passage, encoder.count_tokens, MAX_LENGTH)]
    print(f"Encoding {len(chunks)} chunks and {len(queries)} D1-dev queries on CPU", flush=True)
    index = RetrievalIndex(chunks, encoder, batch_size=BATCH_SIZE)
    score_path = args.output / "scores.npz"
    args.output.mkdir(parents=True)
    scores = _export_scores(index, queries, score_path)
    print(f"Exported and reloaded {len(queries)} by {len(chunks)} chunk scores per method", flush=True)

    trials, selected, run = _sweep(index, queries, scores)
    rank_path = args.output / "selected.jsonl"
    write_rows(rank_path, run)
    saved_run = read_rows(rank_path)
    if run != saved_run:
        raise ValueError("Selected ranking changed after export")
    threshold = select_threshold(queries, saved_run, min_coverage=MIN_COVERAGE)
    warnings = warning_metrics(queries, saved_run, threshold=threshold)

    summary = {
        "split": "D1-dev",
        "queries": len(queries),
        "contexts": len(corpus),
        "chunks": len(chunks),
        "dataset": {"source": split["source"], "sha256": split["sha256"], "split_seed": split["seed"],
                    "dev_gold_contexts": split["dev"]["gold_contexts"], "forced_dev_qids": split["forced_dev_qids"]},
        "checkpoint": {"model": MODEL_ID, "revision": REVISION, "snapshot_sha256": snapshot},
        "run": {
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "runner_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "arguments": {"input": args.input.as_posix(), "model_path": args.model_path.as_posix(),
                          "output": args.output.as_posix()},
            "device": "cpu", "threads": THREADS, "batch_size": BATCH_SIZE,
            "torch_seed": SEED, "max_tokens": MAX_LENGTH, "overlap_words": 24,
            "pooling": "pooler_output", "cosine": "NumPy dot product of unit-normalized float32 vectors",
            "bm25": {"k1": index.bm25.k1, "b": index.bm25.b, "epsilon": index.bm25.epsilon},
            "platform": platform.platform(), "python": platform.python_version(), "torch": str(torch.__version__),
            "packages": {name: version(name) for name in
                         ("numpy", "transformers", "pyvi", "scikit-learn", "sklearn-crfsuite",
                          "python-crfsuite", "rank-bm25", "safetensors")},
            "elapsed_seconds": perf_counter() - start,
        },
        "selection": {"maximize": "MRR@10", "weight_tie_break": "smaller BM25 weight",
                      "min_coverage": MIN_COVERAGE},
        "trials": trials,
        "selected": {**selected, "threshold": threshold},
        "warning_metrics": warnings,
        "artifacts": {path.stem: {"path": path.as_posix(), "sha256": sha256(path.read_bytes()).hexdigest()}
                      for path in (score_path, rank_path)},
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(summary["selected"]), flush=True)
    print(f"Coverage {warnings['groups']['confident']['n']}/{len(queries)}; {summary['run']['elapsed_seconds']:.1f}s total")


if __name__ == "__main__":
    main()
