"""Evaluate three retrieval methods on D1-test with the frozen D1-dev settings."""

import argparse
import csv
import io
import json
import platform
import subprocess
import sys
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from data.prepare_virhe4qa import SHA256, prepare
from experiments.external_dataset.run_dense_dev import read_rows, write_rows
from simcse_lab.evaluation.metrics import evaluate_d1
from simcse_lab.evaluation.stats import paired_bootstrap, warning_metrics
from simcse_lab.model.encoders import MAX_LENGTH, MODEL_ID, REVISION, SimCSEEncoder, verify_snapshot
from simcse_lab.provenance import base_commit
from simcse_lab.retrieval.ingest import article_chunks


FROZEN_CONFIG = Path("experiments/external_dataset/results/D1-dev-tuning/summary.json")
PUBLISHED_E1 = Path("experiments/external_dataset/results/E1/d1-test.json")
RETRIEVAL_SCRIPT = Path("experiments/external_dataset/run_retrieval.py")
METHODS = ("bm25", "dense", "hybrid")
RESAMPLES = 1000
BOOTSTRAP_SEED = 42


def saved_test_queries(summary_path: Path, summary: dict) -> dict:
    """Locate the authenticated question file for a published or replayed E1 run."""
    if "verification" in summary:
        return summary["verification"]["inputs"]["queries.jsonl"]
    # Older runners emitted the same deterministic split without an input manifest.
    # Authenticate that split against the independent, published verification.
    canonical = json.loads(PUBLISHED_E1.read_bytes())
    if summary["dataset"] != canonical["dataset"]:
        raise ValueError("Legacy E1 dataset differs from the verified D1-test split")
    record = canonical["verification"]["inputs"]["queries.jsonl"]
    return {"path": (summary_path.parent / "inputs/queries.jsonl").as_posix(), "sha256": record["sha256"]}


def _prepare_test(input_path: Path, model_path: Path, frozen: dict, output: Path) -> tuple[list[dict], dict, int, str]:
    content = input_path.read_bytes()
    if sha256(content).hexdigest() != SHA256 or frozen["dataset"]["sha256"] != SHA256:
        raise ValueError("D1 CSV does not match the frozen dataset")
    snapshot = verify_snapshot(model_path)
    if frozen["checkpoint"] != {"model": MODEL_ID, "revision": REVISION, "snapshot_sha256": snapshot}:
        raise ValueError("Checkpoint does not match D1-dev")

    source = csv.DictReader(io.StringIO(content.decode("utf-8-sig"), newline=""), strict=True)
    corpus, queries, split = prepare(list(source))
    test = [query for query in queries if query["split"] == "test"]
    if (len(test), split["test"]["gold_contexts"], len(corpus)) != (759, 238, 297):
        raise ValueError("Unexpected D1-test group split")

    encoder = SimCSEEncoder(str(model_path), "cpu")
    chunks = [chunk for passage in corpus for chunk in article_chunks(passage, encoder.count_tokens, MAX_LENGTH)]
    if len(chunks) != frozen["chunks"]:
        raise ValueError("Rebuilt chunk count differs from D1-dev")
    write_rows(output / "corpus.jsonl", chunks)
    write_rows(output / "queries.jsonl", test)
    (output / "split.json").write_text(json.dumps(split, indent=2) + "\n", encoding="utf-8")
    return test, split, len(chunks), str(encoder.torch.__version__)


def _evaluate(args: argparse.Namespace, staging: Path) -> None:
    start = perf_counter()
    config_bytes = FROZEN_CONFIG.read_bytes()
    frozen = json.loads(config_bytes)
    weight = frozen["selected"]["weight"]
    threshold = frozen["selected"]["threshold"]
    if frozen["split"] != "D1-dev" or not (0 <= weight <= 1 and -1 <= threshold <= 1):
        raise ValueError("Expected valid settings selected on D1-dev")

    input_dir = staging / "inputs"
    print(f"Rebuilding D1 with frozen weight={weight} and threshold={threshold}", flush=True)
    queries, split, n_chunks, torch_version = _prepare_test(args.input, args.model_path, frozen, input_dir)
    print(f"Prepared {n_chunks} chunks and {len(queries)} D1-test queries", flush=True)

    output_dir = staging / "retrieval"

    def retrieval_args(directory: Path) -> list[str]:
        return [
            RETRIEVAL_SCRIPT.as_posix(), "run", "--corpus", "d1", "--split", "test",
            "--chunks", (directory / "inputs/corpus.jsonl").as_posix(),
            "--queries", (directory / "inputs/queries.jsonl").as_posix(),
            "--methods", *METHODS, "--weight", str(weight),
            "--model-path", args.model_path.as_posix(), "--output", (directory / "retrieval").as_posix(),
        ]

    def record(path: Path) -> dict:
        return {"path": (args.output / path.relative_to(staging)).as_posix(),
                "sha256": sha256(path.read_bytes()).hexdigest()}

    subprocess.run([sys.executable, "-X", "utf8", "-B", *retrieval_args(staging)], check=True)
    paths = {method: output_dir / "runs" / f"{method}.jsonl" for method in METHODS}
    runs = {method: read_rows(path) for method, path in paths.items()}
    metrics = {method: evaluate_d1(queries, run, hit_cutoffs=(1, 3, 5, 10)) for method, run in runs.items()}
    retrieval_summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    base_metrics = {method: {key: scores[key] for key in ("hit_at_1", "hit_at_3", "mrr_at_10")}
                    for method, scores in metrics.items()}
    if base_metrics != retrieval_summary["metrics"]:
        raise ValueError("Metrics differ after reading the saved retrieval runs")

    intervals = paired_bootstrap(queries, runs["bm25"], runs["hybrid"],
                                 n_resamples=RESAMPLES, seed=BOOTSTRAP_SEED)
    warnings = warning_metrics(queries, runs["hybrid"], threshold=threshold)
    summary = {
        "split": "D1-test", "queries": len(queries), "contexts": split["contexts"], "chunks": n_chunks,
        "dataset": {"source": split["source"], "sha256": split["sha256"], "split_seed": split["seed"],
                    "test_gold_contexts": split["test"]["gold_contexts"]},
        "checkpoint": frozen["checkpoint"],
        "frozen": {"path": FROZEN_CONFIG.as_posix(), "sha256": sha256(config_bytes).hexdigest(),
                   "weight": weight, "threshold": threshold},
        "run": {
            "git_commit": base_commit(),
            "runner_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "retrieval_sha256": sha256(RETRIEVAL_SCRIPT.read_bytes()).hexdigest(),
            "input": args.input.as_posix(), "retrieval_arguments": retrieval_args(args.output),
            "device": "cpu", "threads": 4, "batch_size": 16,
            "platform": platform.platform(), "python": platform.python_version(), "torch": torch_version,
            "packages": {name: version(name) for name in frozen["run"]["packages"]},
            "elapsed_seconds": perf_counter() - start,
        },
        "metrics": metrics,
        "verification": {"inputs": {name: record(input_dir / name)
                                    for name in ("corpus.jsonl", "queries.jsonl", "split.json")}},
        "hybrid_minus_bm25": intervals,
        "hybrid_warning_metrics": warnings,
        "rankings": {method: record(path) for method, path in paths.items()},
    }
    (staging / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"hybrid_minus_bm25": intervals, "hybrid_warning_metrics": warnings}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Pinned ViRHE4QA CSV")
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New output directory")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Use a new output directory")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=args.output.parent) as temp:
        staging = Path(temp) / "evaluation"
        staging.mkdir()
        _evaluate(args, staging)
        if args.output.exists():
            parser.error("Use a new output directory")
        staging.rename(args.output)


if __name__ == "__main__":
    main()
