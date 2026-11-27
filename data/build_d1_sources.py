"""Rebuild the display-only passage citations from the pinned ViRE and R2GQA releases."""

import argparse
import csv
import hashlib
import io
import unicodedata
from pathlib import Path
from zipfile import ZipFile

from data.prepare_virhe4qa import SHA256, source_record

ARCHIVE_SHA256 = "b488a13aca768f264023be00ceb9b1882fd00a542d8f4fdb371c8dbdcf2a0da1"
SOURCE_DIR = Path(__file__).with_name("d1")


def _normalized(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).split())


def _pinned(path: Path, sha256: str) -> bytes:
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != sha256:
        raise ValueError(f"Unexpected SHA-256 for {path}")
    return content


def build_sources(subset: Path, archive: Path) -> str:
    from openpyxl import load_workbook

    csv_bytes = _pinned(subset, SHA256)
    rows = list(csv.DictReader(io.StringIO(csv_bytes.decode("utf-8-sig"), newline="")))
    questions = {}
    for row in rows:
        key = int(row["index"])
        pair = (_normalized(row["context"]), _normalized(row["question"]))
        if questions.setdefault(key, pair) != pair:
            raise ValueError(f"Conflicting duplicate in the subset for index {key}")
    contexts = {row["context"] for row in rows}
    keys = {_normalized(context) for context in contexts}
    matched = set()
    titles = {}
    train_rows = {}
    with ZipFile(io.BytesIO(_pinned(archive, ARCHIVE_SHA256))) as files:
        for split in ("train", "val", "test"):
            book = load_workbook(io.BytesIO(files.read(f"raw_excel/{split}.xlsx")), read_only=True)
            try:
                sheet = iter(book.active.values)
                columns = next(sheet)
                for number, values in enumerate(sheet, 2):
                    row = dict(zip(columns, values))
                    if row["index"] is None:
                        continue
                    qid = int(row["index"])
                    context = _normalized(row["context"])
                    if qid in questions:
                        if qid in matched or (context, _normalized(row["question"])) != questions[qid]:
                            raise ValueError(f"Conflicting source row for ViRE index {qid}")
                        matched.add(qid)
                    # Document labels in the authors' test workbook conflict for identical text.
                    if split == "test" or context not in keys:
                        continue
                    title = row["document"]
                    if not title or titles.setdefault(context, title) != title:
                        raise ValueError(f"Conflicting document for {split}.xlsx row {number}")
                    if split == "train":
                        train_rows.setdefault(context, number)
            finally:
                book.close()
    if matched != questions.keys() or keys != train_rows.keys():
        raise ValueError("Incomplete source coverage")
    result = io.StringIO(newline="")
    writer = csv.writer(result, delimiter="\t", lineterminator="\n")
    writer.writerow(("article_id", "document", "train_row"))
    writer.writerows(sorted((source_record(text)["article_id"], titles[_normalized(text)],
                             train_rows[_normalized(text)]) for text in contexts))
    return result.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subset", required=True, type=Path)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=SOURCE_DIR / "sources.tsv")
    parser.add_argument("--check", action="store_true", help="Compare the rebuilt table to the saved one")
    args = parser.parse_args()
    table = build_sources(args.subset, args.archive)
    if args.check:
        if args.output.read_text(encoding="utf-8") != table:
            parser.error(f"Rebuilt source table differs from {args.output}")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(table.encode("utf-8"))
    print(f"{len(table.splitlines()) - 1} passage citations verified")


if __name__ == "__main__":
    main()
