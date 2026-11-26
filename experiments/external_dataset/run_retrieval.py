"""Prepare HCMUS or export article-level retrieval runs for D1 and HCMUS."""

import argparse
import json
import math
import subprocess
from hashlib import sha256
from pathlib import Path

if __package__:
    from .run_dense_dev import read_rows, write_rows
else:
    from run_dense_dev import read_rows, write_rows
from simcse_lab.evaluation.metrics import evaluate_d1
from simcse_lab.model.encoders import REVISION, SimCSEEncoder, verify_snapshot
from simcse_lab.retrieval.search import RetrievalIndex


def checked_corpus_output(root, output):
    root = root.resolve()
    destination = (root / output).resolve()
    corpus_file = (destination / "corpus.jsonl").resolve()
    try:
        relative_dir = destination.relative_to(root).as_posix()
        relative_file = corpus_file.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("HCMUS output must be inside the repository") from exc
    git = ["git", "-C", str(root)]
    tracked = subprocess.check_output([*git, "ls-files", "-z", "--", f":(literal){relative_dir}"])
    for relative in (relative_dir + "/", relative_file):
        ignored = subprocess.run([*git, "check-ignore", "-q", "--", relative], capture_output=True)
        if ignored.returncode != 0:
            raise ValueError("HCMUS output must be Git-ignored and untracked")
    if tracked:
        raise ValueError("HCMUS output must be Git-ignored and untracked")
    return destination


def validate_run(rows, questions, chunk_articles, count):
    if len(rows) != len(questions) or {row["qid"] for row in rows} != {q["qid"] for q in questions}:
        raise ValueError("Unexpected run qids")
    for row in rows:
        ranked = row["ranked"]
        if len(ranked) != count or len({item[0] for item in ranked}) != count:
            raise ValueError(f"{row['qid']}: wrong number of distinct articles")
        if ranked != sorted(ranked, key=lambda item: (-item[1], item[0])):
            raise ValueError(f"{row['qid']}: invalid ranking order")
        if not math.isfinite(row["top1_dense_cos"]) or abs(row["top1_dense_cos"]) > 1:
            raise ValueError(f"{row['qid']}: invalid confidence cosine")
        for article_id, score, chunk_id in ranked:
            if not math.isfinite(score) or chunk_articles.get(chunk_id) != article_id:
                raise ValueError(f"{row['qid']}: invalid ranked item")


def verify_d1_dev(args):
    summary = json.loads(args.manifest.read_text(encoding="utf-8"))
    queries = [row for row in read_rows(args.queries) if row["split"] == "dev"]
    if len(queries) != summary["queries"] or len({row["qid"] for row in queries}) != len(queries):
        raise ValueError("Unexpected D1-dev query manifest")
    contexts = {row["article_id"] for row in read_rows(args.corpus)}
    if len(contexts) != 297:
        raise ValueError("Expected all 297 D1 source contexts")
    for method, entry in summary["runs"].items():
        path = args.manifest.parent / entry["path"]
        if sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"{method}: SHA-256 mismatch")
        rows = read_rows(path)
        for row in rows:
            for article, _, chunk in row["ranked"]:
                if (article not in contexts or not chunk.startswith(article + ":")
                        or not chunk[len(article) + 1:].isdigit()):
                    raise ValueError(f"{method}: invalid D1 article/chunk ID")
        if args.chunks:
            chunk_articles = {c["chunk_id"]: c["article_id"] for c in read_rows(args.chunks)}
        else:
            chunk_articles = {chunk: chunk.rsplit(":", 1)[0] for row in rows for _, _, chunk in row["ranked"]}
        validate_run(rows, queries, chunk_articles, 20)
        metrics = evaluate_d1(queries, rows)
        if metrics != entry["metrics"]:
            raise ValueError(f"{method}: saved metrics differ from recomputed metrics")
        print(f"{method}: {json.dumps(metrics)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_subparsers(dest="command", required=True)
    verify = mode.add_parser("verify-d1-dev", help="Verify handoff runs without loading a model")
    verify.add_argument("--manifest", type=Path, required=True)
    verify.add_argument("--queries", type=Path, default=Path("data/processed/d1/queries.jsonl"))
    verify.add_argument("--corpus", type=Path, default=Path("data/processed/d1/corpus.jsonl"))
    verify.add_argument("--chunks", type=Path, help="Optional tokenized chunk catalog for exact ID lookup")
    prepare = mode.add_parser("prepare-hcmus")
    prepare.add_argument("--only-2021", action="store_true", help="Prepare a partial corpus for local verification")
    run = mode.add_parser("run")
    run.add_argument("--corpus", choices=("d1", "hcmus"), required=True)
    run.add_argument("--chunks", type=Path, required=True)
    run.add_argument("--queries", type=Path, required=True)
    run.add_argument("--split", choices=("dev", "test"), required=True)
    run.add_argument("--methods", nargs="+", choices=("bm25", "dense", "hybrid"), required=True)
    run.add_argument("--weight", type=float, help="BM25 weight required when running hybrid")
    for command in (prepare, run):
        command.add_argument("--model-path", type=Path, required=True)
        command.add_argument("--output", type=Path, required=True, help="New output directory")
    args = parser.parse_args()
    if args.command == "verify-d1-dev":
        verify_d1_dev(args)
        return
    if args.command == "prepare-hcmus":
        from simcse_lab.retrieval.hcmus import prepare_corpus

        try:
            args.output = checked_corpus_output(Path.cwd(), args.output)
        except (OSError, ValueError, subprocess.CalledProcessError) as exc:
            parser.error(str(exc))
    if args.output.exists():
        parser.error("Use a new output directory")
    if args.command == "run" and "hybrid" in args.methods and (args.weight is None or not 0 <= args.weight <= 1):
        parser.error("Hybrid requires --weight in [0, 1]")

    import torch

    torch.set_num_threads(4)
    verify_snapshot(args.model_path)
    encoder = SimCSEEncoder(str(args.model_path), "cpu")
    if args.command == "prepare-hcmus":
        selected = {"hcmus-qcdt-2021"} if args.only_2021 else None
        try:
            chunks = prepare_corpus(Path.cwd(), encoder.count_tokens, selected)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        write_rows(args.output / "corpus.jsonl", chunks)
        print(f"{len({chunk['article_id'] for chunk in chunks})} articles, {len(chunks)} chunks")
        return

    if args.corpus == "hcmus":
        inputs = {name: path.read_bytes() for name, path in (("corpus", args.chunks), ("queries", args.queries))}
        corpus = [json.loads(line) for line in inputs["corpus"].splitlines()]
        query_rows = [json.loads(line) for line in inputs["queries"].splitlines()]
    else:
        corpus, query_rows = read_rows(args.chunks), read_rows(args.queries)
    expected_source = "virhe4qa" if args.corpus == "d1" else "d2"
    if args.corpus == "hcmus" and args.split != "test":
        parser.error("The HCMUS question set only has a test split")
    queries = [q for q in query_rows if q["split"] == args.split]
    if not queries or any(q["source"] != expected_source for q in queries):
        parser.error(f"No valid {expected_source} queries for {args.split}")
    if len({q["qid"] for q in queries}) != len(queries):
        parser.error("Duplicate qids")
    index = RetrievalIndex(corpus, encoder)
    articles, count = (297, 20) if args.corpus == "d1" else (51, 51)
    if len(index.groups) != articles:
        parser.error(f"{args.corpus} requires {articles} articles")
    results = {method: [] for method in args.methods}
    for query, scores in zip(queries, index.score([q["question"] for q in queries])):
        for method, rows in results.items():
            ranked, cosine = index.rank(scores, method, weight=args.weight or 0.0, k=count)
            rows.append({"qid": query["qid"], "ranked": ranked, "top1_dense_cos": cosine})
    summary = {"corpus": args.corpus, "split": args.split, "model_revision": REVISION,
               "weight": args.weight, "queries": len(queries), "metrics": {}}
    if args.corpus == "hcmus":
        summary["input_sha256"] = {name: sha256(blob).hexdigest() for name, blob in inputs.items()}
        summary["ranking_sha256"] = {}
    chunk_articles = {chunk_id: chunk["article_id"] for chunk_id, chunk in index.by_chunk.items()}
    for method, rows in results.items():
        path = args.output / "runs" / f"{method}.jsonl"
        write_rows(path, rows)
        saved = read_rows(path)
        validate_run(saved, queries, chunk_articles, count)
        if args.corpus == "d1":
            summary["metrics"][method] = evaluate_d1(queries, saved)
        else:
            summary["ranking_sha256"][method] = sha256(path.read_bytes()).hexdigest()
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
