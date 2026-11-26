"""Replay the open HCMUS pilot to compare default and explicitly requested editions."""

from __future__ import annotations

import argparse
import json
import platform
import re
import tempfile
import unicodedata
from collections import defaultdict
from collections.abc import Iterator
from hashlib import sha256
from html import escape
from pathlib import Path

from apps import app
from experiments.application.compare_clause_scope import evidence_path
from simcse_lab.retrieval.search import RetrievalIndex

CONTROL = Path("experiments/application/results/clause-scope-pilot")
# Manually classified from the wording before replay. Used only for reporting.
PILOT_SLICES = {
    "edition_2021": ("pilot-01", "pilot-03", "pilot-05"),
    "edition_2026": ("pilot-07", "pilot-09", "pilot-11", "pilot-13"),
    "academic_year_only": ("pilot-06", "pilot-08"),
    "no_year": ("pilot-02", "pilot-04", "pilot-10", "pilot-12", "pilot-14", "pilot-15", "pilot-16"),
}
YEAR = r"(?:19|20)\d{2}"
# A period or an admission date can coexist with an explicit edition in one query.
CONTEXT_YEAR = re.compile(
    rf"\b{YEAR}\s*[-–—/]\s*(?:{YEAR}|\d{{2}})\b|"
    rf"\b(?:khoá|khóa|khoa tuyen sinh|năm học|nam hoc|nhập học|nhap hoc|tuyển sinh|tuyen sinh"
    rf"|học (?:kỳ|kì) [12]|học kỳ hè)"
    rf"(?:\s+(?:tuyển sinh|tuyển|nhập học))?(?:\s+(?:năm|nam))?\s+{YEAR}\b|"
    rf"\b(?:ngày\s+)?\d{{1,2}}[/.-]\d{{1,2}}[/.-]{YEAR}\b"
)
REFERENCE = re.compile(
    rf"\b(?:quy chế(?: đào tạo(?: trình độ đại học)?)?|quy che(?: dao tao(?: trinh do dai hoc)?)?"
    rf"|(?:^|(?<=theo )|(?<=trong )|(?<=xem )|(?<=đọc )|(?<=tra )|(?<=mở )|(?<=chọn ))"
    rf"(?:phiên bản|phien ban|bản|văn bản|van ban))"
    rf"\s+(?:ban hành\s+|ban hanh\s+)?(?:(?:của |cua )?(?:năm|nam)\s+)?({YEAR})\b"
)
DECISION = re.compile(rf"\b(?:qđ|quyết định)\s+(?:số\s+)?(1175|3087)(?:/qđ-khtn)?"
                      rf"[\s,(]+(?:năm\s+)?({YEAR})\b")
DECISION_YEARS = {"1175": "2021", "3087": "2026"}
NEGATED = re.compile(r"\b(?:trừ|ngoại trừ|bỏ qua|(?:không|đừng)"
                     r"(?: (?:phải|muốn|dùng|sử dụng|áp dụng|xem|theo|đọc|mở|chọn)){0,3})\s*$")
COMPARE_EDITIONS = re.compile(r"\b(?:hai|2) (?:bản|phiên bản|quy chế)|"
                              r"\b(?:với|và|hay|khác) (?:bản|quy chế) (?:cũ|mới|còn lại)\b")


def requested_edition(question: str) -> str | None:
    """Prefer one supported, expressly named document. Abstain on ambiguous references."""
    text = unicodedata.normalize("NFC", question).casefold()
    text = CONTEXT_YEAR.sub(" ", " ".join(text.split()))
    matches = list(REFERENCE.finditer(text))
    decisions = list(DECISION.finditer(text))
    if any(DECISION_YEARS[m[1]] != m[2] for m in decisions):
        return None
    years = {m[1] for m in matches} | {m[2] for m in decisions}
    if (len(years) != 1 or COMPARE_EDITIONS.search(text)
            or any(NEGATED.search(text[:m.start()]) for m in [*matches, *decisions])):
        return None
    year = next(iter(years))
    if year not in DECISION_YEARS.values() or set(re.findall(rf"\b{YEAR}\b", text)) != {year}:
        return None
    return year


def prefer_edition(groups: list, year: str | None) -> list:
    """Change only display order inside a topic. Keep ties and alternate editions."""
    if year is None:
        return groups
    doc_id = "hcmus-qcdt-" + year
    return [sorted(group, key=lambda entry: entry[0]["doc_id"] != doc_id) for group in groups]


class ReplayIndex(RetrievalIndex):
    """Use production ranking with the exact per-chunk scores from the control run."""

    def __init__(self, chunks: list, rows: list) -> None:
        self.chunks = chunks
        self.by_chunk = {c["chunk_id"]: c for c in chunks}
        self.groups = defaultdict(list)
        for pos, chunk in enumerate(chunks):
            self.groups[chunk["article_id"]].append(pos)
        self.scores = {r["question"]: (r["raw_bm25"], r["raw_cosine"]) for r in rows}

    def score(self, questions: list[str]) -> Iterator[tuple[list[float], list[float]]]:
        return (self.scores[question] for question in questions)


def html_view(question: str, message: str, body: str) -> bytes:
    # Same document wrapper as the archived control, checked byte for byte.
    return ('<!doctype html><html lang="vi"><meta charset="utf-8"><title>Tra cứu quy chế HCMUS</title>'
            '<link rel="stylesheet" href="search.css"><body class="gradio-container"><main id="regulations">'
            f'<h1>{escape(question)}</h1><p role="status">{escape(message)}</p>{body}</main></body></html>').encode()


def compare(index: ReplayIndex, row: dict, config: dict, html_dir: Path) -> dict:
    question, control = row["question"], row["variants"]["A"]
    ranked, cosine = index.rank(index.scores[question], "hybrid", weight=config["weight"])
    expected = list(map(list, zip(row["article_order"], row["article_scores"], row["selected_chunks"]["A"])))
    accepted = cosine >= config["threshold"]
    if ranked != expected or len(ranked) != 51 or cosine != control["cosine"] or accepted != control["accepted"]:
        raise ValueError(f"{row['qid']}: frozen retrieval or confidence mismatch")
    body, _, warning = app.answer(index, question, config["weight"], config["threshold"])
    baseline = app.group_results(index, ranked)
    year = requested_edition(question)
    views = {"current": baseline, "requested": prefer_edition(baseline, year)}
    case = {"qid": row["qid"], "question": question, "scope": row["scope"], "requested_edition": year,
            "accepted": accepted, "cosine": cosine, "top_article": ranked[0][0], "top_chunk": ranked[0][2],
            "clause_hit": control["clause_hit"], "editions_in_first_topic": [c["doc_id"] for c, _ in baseline[0]],
            "ranking_sha256": sha256(json.dumps(ranked, separators=(",", ":")).encode()).hexdigest(), "views": {}}
    for name, groups in views.items():
        content = app.render_groups(groups, index, question=question, expand_first=accepted)
        page = html_view(question, warning, content)
        digest = sha256(page).hexdigest()
        primary = groups[0][0][0]
        steps = evidence_path(row, groups[0], index, accepted)
        if name == "current" and (content != body or digest != control["view_sha256"]
                                  or steps != control["evidence_path"] or primary["chunk_id"] != control["primary_chunk_id"]):
            raise ValueError(f"{row['qid']}: displayed control differs from the archived run")
        filename = f"{row['qid']}-{name}.html"
        (html_dir / filename).write_bytes(page)
        case["views"][name] = {"primary_chunk": primary["chunk_id"], "primary_clause": primary["clause_id"],
                               "evidence_path": steps, "visible_evidence": steps == [] if row["scope"] == "in" else None,
                               "html": "html/" + filename, "sha256": digest}
    return case


def outcomes(rows: list[dict]) -> dict:
    result = {"questions": len(rows), "in_scope": sum(r["scope"] == "in" for r in rows)}
    for name in ("current", "requested"):
        result[name + "_visible"] = [r["qid"] for r in rows if r["views"][name]["visible_evidence"]]
    result["gained"] = sorted(set(result["requested_visible"]) - set(result["current_visible"]))
    result["lost"] = sorted(set(result["current_visible"]) - set(result["requested_visible"]))
    result["changed_html"] = [r["qid"] for r in rows if r["views"]["current"]["sha256"] != r["views"]["requested"]["sha256"]]
    return result


def run(output: Path) -> None:
    manifest = json.loads((CONTROL / "summary.json").read_bytes())
    files = {k: (Path(rec["path"]), rec["sha256"]) for k, rec in manifest["inputs"].items()}
    files["predictions"] = (CONTROL / "predictions.jsonl", manifest["predictions_sha256"])
    data = {}
    for name, (path, digest) in files.items():
        data[name] = path.read_bytes()
        if sha256(data[name]).hexdigest() != digest:
            raise ValueError(f"Frozen input mismatch: {path}")
    config = manifest["config"]
    frozen = json.loads(data["config"])
    if (any(config[k] != frozen["selected"][k] for k in ("weight", "threshold"))
            or config["model_revision"] != frozen["checkpoint"]["revision"]):
        raise ValueError("Control does not match the published operating point")
    rows = list(map(json.loads, data["predictions"].splitlines()))
    labels = list(map(json.loads, data["pilot"].splitlines()))
    subsets = {qid: key for key, qids in PILOT_SLICES.items() for qid in qids}
    if (len(rows) != len(labels) or len(rows) != len(subsets)
            or {r["qid"] for r in rows} != subsets.keys()):
        raise ValueError("Incomplete pilot")
    for row, label in zip(rows, labels):
        if any(row[k] != label[k] for k in ("qid", "question", "scope", "gold_clause_ids")):
            raise ValueError("Control and labelled question do not match")
    chunks = list(map(json.loads, data["corpus"].splitlines()))
    if [c["chunk_id"] for c in chunks] != manifest["raw_score_chunk_order"]:
        raise ValueError("Raw score order differs from the corpus")
    index = ReplayIndex(chunks, rows)
    html_dir = output / "html"
    html_dir.mkdir()
    css = Path("apps/search.css").read_bytes()
    if sha256(css).hexdigest() != manifest["run"]["source_sha256"]["apps/search.css"]:
        raise ValueError("Control stylesheet differs from the pilot")
    (html_dir / "search.css").write_bytes(css)
    cases = [compare(index, r, config, html_dir) for r in rows]
    for case in cases:
        case["slice"] = subsets[case["qid"]]
    report = {
        "split": manifest["split"], "control": CONTROL.as_posix(), "config": config,
        "input_sha256": {k: digest for k, (_, digest) in files.items()},
        "control_summary_sha256": sha256((CONTROL / "summary.json").read_bytes()).hexdigest(),
        "python": platform.python_version(),
        "source_sha256": {p.name: sha256(p.read_bytes()).hexdigest() for p in (
            Path(__file__), Path("experiments/application/compare_clause_scope.py"), Path("apps/app.py"),
            Path("apps/search.css"), Path("src/simcse_lab/regulation_excerpts.py"), Path("src/simcse_lab/retrieval/search.py")
        )},
        "overall": outcomes(cases), "slices": {s: outcomes([r for r in cases if r["slice"] == s]) for s in PILOT_SLICES},
        "cases": cases,
    }
    (output / "summary.json").write_bytes((json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="New local directory for the comparison and HTML")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Choose a new output directory")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=args.output.parent) as temp:
        staged = Path(temp) / "replay"
        staged.mkdir()
        run(staged)
        staged.rename(args.output)
    print(f"Compared default and requested editions on the open pilot in {args.output}")


if __name__ == "__main__":
    main()
