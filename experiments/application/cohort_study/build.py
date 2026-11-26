"""Package two offline cohort-selection prototypes with the same frozen search results."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
import zipfile
from hashlib import sha256
from html import escape, unescape
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
REPORT = HERE.parent / "results/edition-display-pilot/summary.json"
DEFAULT_OUTPUT = Path("outputs/development/mo-phong-chon-khoa")
DEFAULT_REPLAY = Path("outputs/development/edition-display-pilot")
SOURCE_CACHE = Path("outputs/d2/e5-source-review")
SCAN_HASHES = (
    "a9ba5c56b23d6fd5ee0d6b60a1dd71afca1f5e5badbd1763e5874e1c3c6fb582",
    "e99ac895def1cc9cdce12b662c096db2bf24fe1615798cd3bb3e0c39e49c4c38",
)


def verified_bytes(path: Path, digest: str) -> bytes:
    data = path.read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ValueError(f"Source differs from the reviewed copy: {path}")
    return data


def write_text(path: Path, text: str) -> None:
    path.write_bytes(text.encode("utf-8"))


def copy_sources(folder: Path, supplied: Path | None) -> dict[str, str]:
    documents = yaml.safe_load(Path("data/d2/documents.yaml").read_bytes())["documents"]
    by_id = {doc["doc_id"]: doc for doc in documents}
    old, new = (by_id["hcmus-qcdt-" + year] for year in ("2021", "2026"))
    urls = {}
    for doc, filename, source, digest in (
        (old, "quy-che-2021.pdf", Path(old["file"]), old["sha256"]),
        (new, "quy-che-2026.pdf", SOURCE_CACHE / "QD3087-official.pdf", new["source_sha256"]),
    ):
        (folder / filename).write_bytes(verified_bytes(supplied / filename if supplied else source, digest))
        urls[doc["source_url"]] = "van-ban/" + filename
    for page, digest in enumerate(SCAN_HASHES, start=1):
        filename = f"qd-91-trang-{page}.png"
        (folder / filename).write_bytes(verified_bytes((supplied or SOURCE_CACHE) / filename, digest))
    shutil.copyfile(HERE / "quyet-dinh-91.html", folder / "quyet-dinh-91.html")
    amendment = next(item for item in old["sua_doi"] if item["so_hieu"] == "91/QĐ-KHTN")
    urls[amendment["source_url"]] = "van-ban/quyet-dinh-91.html"
    return urls


def search_bank(report: dict, replay: Path, urls: dict[str, str], task_ids: set[str]) -> tuple[list[dict], dict[str, int]]:
    labels_path = Path("data/development/clause-scope-pilot.jsonl")
    labels = [json.loads(line) for line in verified_bytes(labels_path, report["input_sha256"]["pilot"]).splitlines()]
    cases = report["cases"]
    if [(c["qid"], c["question"]) for c in cases] != [(r["qid"], r["question"]) for r in labels]:
        raise ValueError("Question bank differs from the development pilot")
    pages = {}
    for row in labels:
        if row["qid"] in task_ids:
            for passage in row["checked_passages"]:
                key = re.fullmatch(r"hcmus-qcdt-(\d{4}):dieu-(\d+):khoan-(\d+)", passage["clause_id"])
                if key and not passage.get("point"):
                    pages[f"Quy chế {key[1]} · Điều {key[2]} · Khoản {key[3]}"] = passage["pdf_page"]
    bank = []
    for case in cases:
        view = case["views"]["requested"]
        page = verified_bytes(replay / view["html"], view["sha256"]).decode()
        match = re.search(r'<p role="status">(.*?)</p>(.*)</main></body></html>$', page, re.DOTALL)
        if not match:
            raise ValueError(f"Missing status or search content in {view['html']}")
        body = re.sub(r'href="([^"]+)"', lambda link: 'href="' + urls[link[1]] + '"', match[2])
        bank.append({"id": case["qid"], "question": case["question"], "warning": unescape(match[1]), "html": body})
    return bank, pages


def build(output: Path, replay: Path, documents: Path | None) -> None:
    if output.exists():
        raise FileExistsError(f"Choose a new output directory: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temp:
        scratch = Path(temp)
        stage = scratch / "kit"
        assets = stage / "assets"
        sources = stage / "van-ban"
        assets.mkdir(parents=True)
        sources.mkdir()
        if not replay.is_dir():
            from experiments.application.compare_edition_display import run

            replay = scratch / "replay"
            replay.mkdir()
            run(replay)
        report = json.loads(REPORT.read_bytes())
        control = json.loads(verified_bytes(HERE.parent / "results/clause-scope-pilot/summary.json",
                                            report["control_summary_sha256"]))
        if report["config"] != control["config"]:
            raise ValueError("Edition replay differs from the published pilot configuration")
        urls = copy_sources(sources, documents)
        study = json.loads((HERE / "study.json").read_bytes())
        bank, pages = search_bank(report, replay, urls, {s["question_id"] for s in study["scenarios"]})
        bank.append({"id": "personal", "question": study["personal_question"]})
        write_text(assets / "questions.js", "window.studyQuestions = " + json.dumps(bank, ensure_ascii=False)
                   + ";\nwindow.studyPages = " + json.dumps(pages, ensure_ascii=False) + ";\n")
        (assets / "search.css").write_bytes(verified_bytes(replay / "html/search.css", report["source_sha256"]["search.css"]))
        for filename in ("study.css", "study.js"):
            shutil.copyfile(HERE / filename, assets / filename)
        prototype = (HERE / "prototype.html").read_text(encoding="utf-8")
        for filename, entry in (("mau-a.html", "first"), ("mau-b.html", "when-needed")):
            write_text(stage / filename, prototype.replace("@@ENTRY@@", entry))

        card = (HERE / "scenario-card.html").read_text(encoding="utf-8")
        questions = {row["id"]: row["question"] for row in bank}
        for scenario in study["scenarios"]:
            text = card
            for key, value in (("title", scenario["title"]), ("context", scenario["context"]),
                               ("task", scenario["task"]), ("question", questions[scenario["question_id"]])):
                text = text.replace("@@" + key + "@@", escape(value))
            write_text(stage / f"phieu-{scenario['id']}.html", text)
        shutil.copyfile(HERE / "huong-dan-mo-phong.html", stage / "huong-dan-mo-phong.html")
        archive = scratch / "mo-phong-chon-khoa.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    bundle.write(path, path.relative_to(stage))
        archive.rename(stage / archive.name)
        stage.rename(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="New directory for pages and ZIP")
    parser.add_argument("--replay", type=Path, default=DEFAULT_REPLAY, help="Previous edition replay (rebuilt if absent)")
    parser.add_argument("--documents", type=Path, help="Local van-ban directory from an unpacked study kit")
    args = parser.parse_args()
    build(args.output, args.replay, args.documents)
    print(f"Offline walkthrough: {args.output / 'mo-phong-chon-khoa.zip'}")


if __name__ == "__main__":
    main()
