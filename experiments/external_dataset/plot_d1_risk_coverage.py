"""Plot E3 risk-coverage from the saved Hybrid D1-test ranking."""

from __future__ import annotations

import argparse
import json
import math
import platform
import subprocess
from hashlib import sha256
from itertools import groupby
from pathlib import Path

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from experiments.external_dataset.evaluate_d1_test import PUBLISHED_E1, saved_test_queries
from simcse_lab.evaluation.stats import _cosine, warning_metrics


FIGURE_NAME = "d1-test-risk-coverage"


def _read_rows(record: dict[str, str]) -> list[dict]:
    path = Path(record["path"])
    data = path.read_bytes()
    if sha256(data).hexdigest() != record["sha256"]:
        raise ValueError(f"SHA-256 mismatch: {path}")
    return [json.loads(line) for line in data.splitlines()]


def _curve(queries: list[dict], run: list[dict]) -> list[tuple[float, int, int]]:
    gold = {row["qid"]: set(row["gold_article_ids"]) for row in queries}
    scored = sorted(
        ((_cosine(row), row["ranked"][0][0] not in gold[row["qid"]]) for row in run),
        reverse=True,
    )
    accepted = errors = 0
    points = []
    for score, tied_rows in groupby(scored, key=lambda row: row[0]):
        for _, wrong in tied_rows:
            accepted += 1
            errors += wrong
        points.append((score, accepted, errors))
    return points


def _figure(points: list[tuple[float, int, int]], fixed: dict, size: int) -> Figure:
    fig = Figure(figsize=(5.05, 3.25), layout="constrained")
    FigureCanvasAgg(fig)
    ax = fig.subplots()
    ax.plot(
        [accepted / size for _, accepted, _ in points],
        [errors / accepted for _, accepted, errors in points],
        color="#176482", linewidth=1.55,
    )
    coverage, risk = fixed["coverage"], fixed["risk"]
    ax.vlines(coverage, 0, risk, color="#A65027", linestyle="--", linewidth=0.9)
    ax.scatter(coverage, risk, s=40, color="#AC4C20", edgecolor="white", linewidth=0.85, zorder=4)
    ax.annotate(
        f"Fixed threshold ($\\theta \\approx {fixed['threshold']:.6f}$)\n"
        f"{coverage:.2%} coverage, {risk:.2%} risk",
        xy=(coverage, risk), xytext=(0.055, 0.92), textcoords="axes fraction",
        va="top", fontsize=9.5, color="#763619", linespacing=1.45,
        arrowprops={"arrowstyle": "-", "color": "#AC4C20", "lw": 0.85, "shrinkB": 5},
    )
    ax.set(
        xlim=(0, 1.015), ylim=(0, max(0.32, max(errors / accepted for _, accepted, errors in points) + 0.04)),
        xlabel="Coverage", ylabel="Risk (top-1 error)", xticks=[0, 0.2, 0.4, 0.6, 0.8, 1],
    )
    ax.set_title("Hybrid risk-coverage on D1-test", loc="left", fontsize=12, weight="bold", pad=9)
    ax.xaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    ax.tick_params(axis="both", labelsize=9, length=3, color="#9AA9B4")
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#DDE4E9", linewidth=0.65)
    ax.spines[["top", "right"]].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_color("#9AA9B4")
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--e1-summary", type=Path, default=PUBLISHED_E1)
    parser.add_argument("--output", type=Path, required=True, help="New directory for the results")
    parser.add_argument("--pdf", type=Path, help="Path for the vector figure, defaults to the output directory")
    args = parser.parse_args()
    png = args.output / f"{FIGURE_NAME}.png"
    pdf = args.pdf or args.output / f"{FIGURE_NAME}.pdf"
    if args.output.exists() or pdf.exists() or pdf.suffix.lower() != ".pdf":
        parser.error("Use a new output directory and a new .pdf path")

    e1_bytes = args.e1_summary.read_bytes()
    e1 = json.loads(e1_bytes)
    if e1["split"] != "D1-test":
        raise ValueError("Expected the D1-test E1 summary")
    frozen = e1["frozen"]
    threshold = frozen["threshold"]
    source = {
        "e1_summary": {"path": args.e1_summary.as_posix(), "sha256": sha256(e1_bytes).hexdigest()},
        "queries": saved_test_queries(args.e1_summary, e1),
        "hybrid_ranking": e1["rankings"]["hybrid"],
    }
    queries = _read_rows(source["queries"])
    size = len(queries)
    if size != e1["queries"] or any(
        (row["source"], row["split"], row["in_scope"]) != ("virhe4qa", "test", True) for row in queries
    ):
        raise ValueError("Expected the saved in-scope ViRHE4QA test questions")
    run = _read_rows(source["hybrid_ranking"])
    warnings = warning_metrics(queries, run, threshold=threshold)
    if warnings != e1["hybrid_warning_metrics"]:
        raise ValueError("Saved warning metrics disagree with the D1-test ranking")

    confident = warnings["groups"]["confident"]
    if not confident["n"]:
        raise ValueError("Risk is undefined at the fixed threshold because it accepts no questions")
    points = _curve(queries, run)
    _, accepted, errors = next(point for point in reversed(points) if point[0] >= threshold)
    coverage, risk = accepted / size, errors / accepted
    full_errors = points[-1][2]
    if (accepted != confident["n"] or coverage != warnings["coverage"]
            or not math.isclose((accepted - errors) / accepted, confident["hit_at_1"]["article"])
            or not math.isclose((size - full_errors) / size, e1["metrics"]["hybrid"]["hit_at_1"])):
        raise ValueError("Curve counts disagree with E1 metrics")
    fixed = {"threshold": threshold, "accepted": accepted, "errors": errors, "coverage": coverage, "risk": risk}
    report = {
        "split": e1["split"], "queries": size, "method": "hybrid", "frozen": frozen, "sources": source,
        "score_key": "top1_dense_cos", "acceptance_rule": "score >= threshold",
        "operating_point": fixed,
        "full_coverage": {"accepted": size, "errors": full_errors, "coverage": 1.0, "risk": full_errors / size},
        "curve_columns": ["threshold", "accepted", "errors"], "curve": points,
        "run": {
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "python": platform.python_version(), "matplotlib": matplotlib.__version__,
            "platform": platform.platform(), "device": "cpu",
        },
    }
    args.output.mkdir(parents=True)
    pdf.parent.mkdir(parents=True, exist_ok=True)
    with matplotlib.rc_context({"pdf.fonttype": 42}):
        fig = _figure(points, fixed, size)
        fig.savefig(png, dpi=360)
        with pdf.open("xb") as output:
            fig.savefig(output, format="pdf", metadata={"CreationDate": None})
    report["figures"] = {
        kind: {"path": path.as_posix(), "sha256": sha256(path.read_bytes()).hexdigest()}
        for kind, path in (("png", png), ("pdf", pdf))
    }
    (args.output / "d1-test.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"D1-test fixed threshold {threshold}: coverage {coverage:.2%} ({accepted}/{size}), "
          f"risk {risk:.2%} ({errors}/{accepted})")


if __name__ == "__main__":
    main()
