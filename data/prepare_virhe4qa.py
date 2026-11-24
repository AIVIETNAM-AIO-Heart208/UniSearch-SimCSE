"""Prepare the pinned ViRHE4QA subset and its context-grouped split."""

import argparse
import csv
import hashlib
import io
import json
import random
import re
from pathlib import Path

REVISION = "60ea7155134eaa426ab1d0a82d2bbbf327d1b470"
SOURCE = f"https://github.com/longstnguyen/ViRE/blob/{REVISION}/data/ViRHE4QA_v2.csv"
SHA256 = "23fb969985150599d3ad0b5229d039b8541ed335fbc29dcfa0b0d733ccaa5682"
SEED = 42


def source_record(text):
    article_id = hashlib.sha256(text.encode("utf-8")).hexdigest()
    heading = re.match(r"Điều\s+(\d+)[.)]?\s*([^\r\n]*)", text.lstrip())
    return {
        "chunk_id": article_id + ":source", "doc_id": "virhe4qa",
        "article_id": article_id, "article": int(heading[1]) if heading else None,
        "article_title": heading[2].strip() if heading else None,
        "clause": None, "text": text, "char_start": 0, "char_end": len(text),
    }


def prepare(rows):
    contexts = {}
    questions = {}
    indices = {}
    duplicates = []
    for row in rows:
        qid, question, context = row["index"], row["question"], row["context"]
        if not all(isinstance(field, str) and field.strip() for field in (qid, question, context)):
            raise ValueError(f"Missing index, question or context for {qid!r}")
        contexts.setdefault(context, None)
        if question in questions:
            old_qid, old_context = questions[question]
            if old_context != context:
                raise ValueError(f"Duplicate question has different gold contexts: {old_qid}, {qid}")
            duplicates.append(qid)
            continue
        if qid in indices:
            raise ValueError(f"Repeated index with different questions: {qid}")
        indices[qid] = context
        questions[question] = (qid, context)

    if (len(rows), len(contexts)) != (1000, 297):
        raise ValueError(f"Expected 1000 rows and 297 contexts, got {len(rows)}, {len(contexts)}")
    forced = indices["9542"]
    forced_qids = sorted(qid for qid, context in indices.items() if context == forced)
    if len(forced_qids) != 4 or not re.match(r"Điều\s+6[.)]\s*Báo cáo tiến độ thực hiện KLTN", forced):
        raise ValueError("Unexpected context group for index 9542")

    records = {context: source_record(context) for context in contexts}
    remaining = sorted({record["article_id"] for record in records.values()} - {records[forced]["article_id"]})
    dev = set(random.Random(SEED).sample(remaining, round(len(contexts) * 0.2) - 1))
    dev.add(records[forced]["article_id"])
    queries = []
    for question, (qid, context) in sorted(questions.items(), key=lambda item: item[1][0]):
        article_id = records[context]["article_id"]
        queries.append({
            "qid": qid, "question": question, "gold_article_ids": [article_id],
            "gold_clause_ids": [], "split": "dev" if article_id in dev else "test",
            "source": "virhe4qa", "origin": None, "in_scope": True,
        })
    counts = {}
    gold = {}
    for split in ("dev", "test"):
        subset = [query for query in queries if query["split"] == split]
        gold[split] = {query["gold_article_ids"][0] for query in subset}
        counts[split] = {"queries": len(subset), "gold_contexts": len(gold[split])}
    corpus = sorted(records.values(), key=lambda row: row["article_id"])
    if gold["dev"] & gold["test"] or gold["dev"] | gold["test"] != {r["article_id"] for r in corpus}:
        raise ValueError("Invalid gold context partition")
    return corpus, queries, {
        "source": SOURCE, "sha256": SHA256, "seed": SEED,
        "input_rows": len(rows), "contexts": len(corpus), "duplicates_removed": len(duplicates),
        "duplicate_indices": sorted(duplicates), "forced_dev_qids": forced_qids, **counts,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/d1/ViRHE4QA_v2.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/d1"))
    args = parser.parse_args()
    content = args.input.read_bytes()
    actual_sha = hashlib.sha256(content).hexdigest()
    if actual_sha != SHA256:
        parser.error(f"Unexpected input SHA-256: {actual_sha}. Expected {SHA256} from {SOURCE}")
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig"), newline=""), strict=True)
    corpus, queries, summary = prepare(list(reader))
    args.output.mkdir(parents=True, exist_ok=True)
    for name, rows in (("corpus.jsonl", corpus), ("queries.jsonl", queries)):
        (args.output / name).write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
        )
    (args.output / "split.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
