"""Rank D1-dev with the pinned Vietnamese SimCSE checkpoint."""

import argparse
import json
import platform
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

from simcse_lab.evaluation.metrics import evaluate_d1
from simcse_lab.model.encoders import MAX_LENGTH, MODEL_ID, REVISION, SimCSEEncoder, verify_snapshot
from simcse_lab.provenance import base_commit
from simcse_lab.retrieval.ingest import article_chunks
from simcse_lab.retrieval.search import maxp


def read_rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n" for row in rows)
    path.write_bytes(content.encode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/processed/d1"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--device", default="cpu", choices=("cpu", "cuda"))
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if min(args.batch_size, args.threads) < 1:
        parser.error("batch-size and threads must be positive")

    import torch

    torch.set_num_threads(args.threads)
    source = read_rows(args.data / "corpus.jsonl")
    queries = [row for row in read_rows(args.data / "queries.jsonl") if row["split"] == "dev"]
    split = json.loads((args.data / "split.json").read_text(encoding="utf-8"))
    if len(queries) != split["dev"]["queries"] or len(source) != split["contexts"]:
        raise ValueError("Prepared files disagree with the split summary")
    article_ids = {row["article_id"] for row in source}
    if len(article_ids) != len(source) or any(
        len(query["gold_article_ids"]) != 1 or query["gold_article_ids"][0] not in article_ids
        for query in queries
    ):
        raise ValueError("Expected unique corpus article IDs and one valid gold ID per query")
    expected = {"9542", "9512", "9538", "9539"}
    if not expected <= {row["qid"] for row in queries}:
        raise ValueError("Dev queries are missing the forced group")
    if args.smoke:
        queries = queries[:3]
        source = source[:25]

    snapshot_hashes = verify_snapshot(args.model_path)
    encoder = SimCSEEncoder(str(args.model_path), args.device)
    print(f"Loaded {MODEL_ID}; chunking {len(source)} contexts", flush=True)
    chunks = []
    for row in source:
        article = article_chunks(row, encoder.count_tokens, MAX_LENGTH)
        for chunk in article:
            if chunk["text"] != row["text"][chunk["char_start"]:chunk["char_end"]]:
                raise ValueError(f"Invalid source span for {chunk['chunk_id']}")
        chunks.extend(article)
    print(f"Encoding {len(chunks)} chunks and {len(queries)} dev queries", flush=True)
    vectors = encoder.encode([chunk["text"] for chunk in chunks], args.batch_size)
    questions = encoder.encode([q["question"] for q in queries], args.batch_size)
    run = []
    for query, scores in zip(queries, questions @ vectors.T):
        ranked = maxp(chunks, scores)
        run.append({"qid": query["qid"], "ranked": ranked, "top1_dense_cos": ranked[0][1]})

    work = args.data / ("dense-smoke" if args.smoke else "dense")
    write_rows(work / "corpus.jsonl", chunks)
    run_file = args.output / "runs" / "dense.jsonl"
    write_rows(run_file, run)
    saved = read_rows(run_file)
    chunk_map = {chunk["chunk_id"]: chunk for chunk in read_rows(work / "corpus.jsonl")}
    for row in saved:
        for article_id, _, chunk_id in row["ranked"]:
            if chunk_map[chunk_id]["article_id"] != article_id:
                raise ValueError(f"Saved chunk {chunk_id} belongs to a different article")
    metrics = evaluate_d1(queries, saved)
    if metrics != evaluate_d1(queries, run):
        raise ValueError("Metrics changed after reading the saved run")

    best_example = next(
        (query, row) for query, row in zip(queries, saved)
        if row["ranked"][0][0] in query["gold_article_ids"]
    ) if metrics["hit_at_1"] else None
    example = None
    if best_example:
        query, row = best_example
        article_id, _, chunk_id = row["ranked"][0]
        chunk = chunk_map[chunk_id]
        example = {"qid": query["qid"], "rank": 1, "gold_article_id": article_id,
                   "chunk_id": chunk_id, "article": chunk["article"], "clause": chunk["clause"],
                   "char_start": chunk["char_start"], "char_end": chunk["char_end"]}
    summary = {
        "split": "dev", "smoke": args.smoke, "queries": len(queries), "contexts": len(source),
        "chunks": len(chunks), "scale": "0-1", "metrics": metrics, "example": example,
        "dataset": split, "model": MODEL_ID, "revision": REVISION,
        "model_sha256": snapshot_hashes["model.safetensors"], "snapshot_sha256": snapshot_hashes,
        "config": {"max_length": MAX_LENGTH, "overlap_words": 24, "pooling": "pooler_output",
                   "device": args.device, "batch_size": args.batch_size, "threads": args.threads,
                   "search": "NumPy cosine, MaxP, top 20"},
        "environment": {
            "platform": platform.platform(), "python": platform.python_version(),
            "packages": {name: version(name) for name in
                         ("torch", "transformers", "numpy", "pyvi", "scikit-learn", "sklearn-crfsuite")},
        },
        "base_commit": base_commit(),
        "command": subprocess.list2cmdline([sys.executable, *sys.argv]),
    }
    (args.output / "metrics.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(metrics, indent=2), flush=True)


if __name__ == "__main__":
    main()
