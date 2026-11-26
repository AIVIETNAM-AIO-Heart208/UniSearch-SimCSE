"""Evaluate the saved rankings for the finalized HCMUS test set."""

from __future__ import annotations

import argparse
import json
import platform
import tempfile
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path

from experiments.application.analyze_d1_overlap import _word_set
from simcse_lab.evaluation.d2 import LEVELS, METHODS, evaluate_d2
from simcse_lab.provenance import base_commit
from simcse_lab.retrieval.hcmus import load_article_map, load_regulations, regulation_articles


FROZEN_CONFIG = Path("experiments/external_dataset/results/D1-dev-tuning/summary.json")


def _value(value: float | None) -> str:
    return "—" if value is None else f"{value:.4f}"


def _check_saved_hashes(run: dict, blobs: dict[str, bytes]) -> bool:
    keys = {"input_sha256": ("queries", "corpus"), "ranking_sha256": METHODS}
    if not keys.keys() & run.keys():
        return False
    for section, names in keys.items():
        for name in names:
            if sha256(blobs[name]).hexdigest() != run[section][name]:
                raise ValueError(f"{name}: SHA-256 differs from the saved HCMUS run")
    return True


def _table(report: dict) -> str:
    frozen = report["frozen"]
    scores = [("All in-scope", report["overall"]), *report["overlap"]["groups"].items()]
    if report["form"] is not None:
        scores.append(("Form in-scope", report["form"]))
    lines = [
        "# Retrieval on D2-test", "",
        f"Fixed BM25 weight `{frozen['weight']}` and warning threshold `{frozen['threshold']}`.", "",
        "| Slice | Queries | Method | Level | Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR@10 |",
        "|---|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for name, group in scores:
        for method in METHODS:
            metrics = group["metrics"][method]
            for level in LEVELS:
                values = " | ".join(map(_value, metrics[level].values()))
                lines.append(f"| {name} | {group['n']} | {method} | {level} | {values} |")
            clause = metrics["clause"]
            lines.append(f"| {name} | {clause['n']} | {method} | clause | {_value(clause['hit_at_1'])} | — | — | — | — |")
    if (baseline := report["random_baseline"]) is not None:
        for level in LEVELS:
            values = " | ".join(map(_value, baseline[level].values()))
            lines.append(f"| All in-scope | {report['overall']['n']} | random | {level} | {values} |")
    lines += ["", "## Paired 95% confidence intervals", "",
              "| Slice | Level | Metric | Hybrid − BM25 | Lower | Upper |", "|---|---|---|---:|---:|---:|"]
    for name, group in scores:
        if (comparison := group["hybrid_minus_bm25"]) is not None:
            for level, metrics in comparison["levels"].items():
                for metric, interval in metrics.items():
                    lines.append(f"| {name} | {level} | {metric} | "
                                 f"{_value(interval['delta'])} | {_value(interval['lower'])} | {_value(interval['upper'])} |")
    warning = report["warnings"]
    lines += ["", "## Hybrid warnings", "",
              f"Coverage {_value(warning['coverage'])} across {warning['n_queries']} questions. "
              f"False confidence {_value(warning['false_confidence'])} "
              f"({warning['n_confident_out_of_scope']}/{warning['n_out_of_scope']}).", "",
              "| Group | All | In scope | Article Hit@1 | Topic Hit@1 |", "|---|---:|---:|---:|---:|"]
    for name, group in warning["groups"].items():
        lines.append(f"| {name} | {group['n']} | {group['n_in_scope']} | "
                     f"{_value(group['hit_at_1']['article'])} | {_value(group['hit_at_1']['topic'])} |")
    if warning["false_confident_queries"]:
        lines += ["", "| Out-of-scope query marked confident | Top article | Cosine |", "|---|---|---:|"]
        for row in warning["false_confident_queries"]:
            lines.append(f"| `{row['qid']}` | `{row['top_article_id']}` | {row['cosine']:.6f} |")
    lines += ["", "See [summary.json](summary.json) for the group cutoffs, risk-coverage points and input hashes."]
    if report["overall"]["n"]:
        lines += ["", "[Risk-coverage figure](risk-coverage.png)"]
    if not report["run"]["retrieval_hashes_verified"]:
        lines += ["", "This legacy retrieval summary records the configuration and query count. "
                  "Input and ranking hashes are recorded at evaluation time."]
    return "\n".join(lines) + "\n"


def _plot(report: dict, output: Path) -> None:
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    from matplotlib.ticker import PercentFormatter

    fig = Figure(figsize=(5.3, 3.3), layout="constrained")
    FigureCanvasAgg(fig)
    ax = fig.subplots()
    fixed = report["operating_point"]
    for level, color in (("article", "#176482"), ("topic", "#8B501D")):
        pairs = [(p["coverage"], p["risk"][level]) for p in report["risk_coverage"] if p["risk"][level] is not None]
        x, y = zip(*pairs)
        ax.plot(x, y, marker=".", linewidth=1.2, color=color, label=level.capitalize())
        if fixed["risk"][level] is not None:
            ax.scatter(fixed["coverage"], fixed["risk"][level], color=color, s=40, edgecolor="white", zorder=3)
    ax.axvline(fixed["coverage"], color="#586372", linestyle="--", linewidth=0.9,
               label=f"Fixed threshold ({fixed['threshold']:.6f})")
    ax.set(xlim=(0, 1.02), ylim=(0, 1.03), xlabel="Coverage", ylabel="Risk (top-1 error)",
           title="Hybrid risk-coverage on D2-test")
    ax.xaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, fontsize=8)
    fig.savefig(output, dpi=300)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queries", type=Path, default=Path("data/d2/queries_d2.jsonl"))
    parser.add_argument("--chunks", type=Path, required=True, help="Corpus used for the saved runs")
    parser.add_argument("--runs", type=Path, required=True, help="Output directory of run_retrieval.py run")
    parser.add_argument("--output", type=Path, required=True, help="New directory for the evaluation")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Use a new output directory")
    topic_path = Path("data/d2/article_map.tsv")
    paths = {"config": FROZEN_CONFIG, "topic_map": topic_path, "queries": args.queries,
             "corpus": args.chunks, "run_summary": args.runs / "summary.json",
             **{method: args.runs / "runs" / f"{method}.jsonl" for method in METHODS}}
    try:
        blobs = {name: path.read_bytes() for name, path in paths.items()}
        frozen, run = (json.loads(blobs[name]) for name in ("config", "run_summary"))
        config = frozen["selected"]
        if (frozen["split"], run["corpus"], run["split"], run["weight"], run["model_revision"]) != (
            "D1-dev", "hcmus", "test", config["weight"], frozen["checkpoint"]["revision"],
        ):
            raise ValueError("Saved runs must use HCMUS test and the frozen weight and checkpoint revision")
        verified = _check_saved_hashes(run, blobs)

        def rows(name: str) -> list[dict]:
            return [json.loads(line) for line in blobs[name].splitlines()]

        queries = rows("queries")
        if len(queries) != run["queries"]:
            raise ValueError("Saved run query count differs from the labels")
        topics = {article: row["topic_id"] for article, row in load_article_map(topic_path).items()}
        articles = {}
        sources = {}
        for doc, text in load_regulations(Path.cwd()):
            sources[doc["doc_id"]] = {"path": doc.get("text_file", doc["file"]),
                                      "sha256": doc.get("text_sha256", doc["sha256"])}
            articles.update((a["article_id"], a) for a in regulation_articles(text, doc["doc_id"], doc["so_dieu"]))
        if len(topics) != 51 or len(set(topics.values())) != 26:
            raise ValueError("Expected the complete HCMUS topic map")
        report = evaluate_d2(queries, {method: rows(method) for method in METHODS}, rows("corpus"),
                             articles, topics, threshold=config["threshold"], tokenize=_word_set)
    except (OSError, KeyError, TypeError, ValueError) as exc:
        parser.error(str(exc))
    report["frozen"] = {"weight": config["weight"], "threshold": config["threshold"],
                        "model_revision": run["model_revision"]}
    report["inputs"] = {name: {"path": path.as_posix(), "sha256": sha256(blobs[name]).hexdigest()}
                        for name, path in paths.items()}
    report["regulations"] = sources
    report["run"] = {"git_commit": base_commit(),
                     "python": platform.python_version(), "platform": platform.platform(), "device": "cpu",
                     "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
                     "retrieval_hashes_verified": verified,
                     "pyvi": version("pyvi"),
                     "matplotlib": version("matplotlib") if report["overall"]["n"] else None}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=args.output.parent) as temp:
        staging = Path(temp) / "evaluation"
        staging.mkdir()
        if report["overall"]["n"]:
            _plot(report, staging / "risk-coverage.png")
        (staging / "summary.json").write_bytes((json.dumps(report, indent=2, allow_nan=False) + "\n").encode())
        (staging / "d2-test.md").write_bytes(_table(report).encode())
        if args.output.exists():
            parser.error("Use a new output directory")
        staging.rename(args.output)
    print(f"Scored {report['n_queries']} D2 questions in {args.output}")


if __name__ == "__main__":
    main()
