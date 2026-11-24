"""Load verified HCMUS regulations and preserve offsets into their source text."""

import csv
import hashlib
import re
from pathlib import Path

import yaml

from .ingest import article_chunks


_ARTICLE = re.compile(r"(?m)^[ \t#*]*Điều[ \t]+(\d+)[ \t]*[.:][ \t*]*(\S[^\r\n]*)")
_SECTION_END = re.compile(r"(?im)^[ \t#*]*(?:chương[ \t]+[ivxlcdm]+\b|nơi nhận[ \t]*:)")
_CLAUSE = re.compile(r"(?mi)^[ \t*]*(?:Khoản[ \t]+)?(\d+)[.)][ \t]+")


def load_article_map(path):
    articles = {}
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            article_id = f"{row['doc_id']}:dieu-{int(row['dieu'])}"
            if article_id in articles or not row["topic_id"] or not row["title"].strip():
                raise ValueError(f"Invalid article mapping for {article_id}")
            articles[article_id] = row
    return articles


def regulation_articles(text, doc_id, expected_count):
    headings = list(_ARTICLE.finditer(text))
    numbers = [int(heading[1]) for heading in headings]
    expected = list(range(1, expected_count + 1))
    # The 2026 transcription includes the three articles of the signing decision.
    if doc_id == "hcmus-qcdt-2026" and numbers == [1, 2, 3] + expected:
        headings, numbers = headings[3:], numbers[3:]
    if numbers != expected:
        raise ValueError(f"{doc_id}: expected regulation articles {expected}, found {numbers}")
    for index, (heading, article) in enumerate(zip(headings, numbers)):
        start = heading.start()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        boundary = _SECTION_END.search(text, heading.end(), end)
        if boundary is not None:
            end = boundary.start()
        yield {
            "doc_id": doc_id, "article_id": f"{doc_id}:dieu-{article}",
            "article": article, "article_title": heading[2].strip(" *\t"),
            "text": text[start:end], "char_start": start,
        }


def prepare_corpus(root, count_tokens, doc_ids=None):
    documents = yaml.safe_load((root / "data/d2/documents.yaml").read_text(encoding="utf-8"))["documents"]
    mapping = load_article_map(root / "data/d2/article_map.tsv")
    if len(mapping) != 51 or len({row["topic_id"] for row in mapping.values()}) != 26:
        raise ValueError("Expected 51 articles and 26 topics in the HCMUS mapping")
    chunks, articles = [], set()
    for doc in documents:
        doc_id = doc["doc_id"]
        if doc_ids is not None and doc_id not in doc_ids:
            continue
        path = root / doc.get("text_file", doc["file"])
        if not path.is_file():
            raise FileNotFoundError(f"Missing source for {doc_id}: {path}")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != doc.get("text_sha256", doc["sha256"]):
            raise ValueError(f"SHA-256 mismatch: {path}")
        text = data.decode("utf-8-sig")
        for source in regulation_articles(text, doc_id, doc["so_dieu"]):
            mapped_article = mapping[source["article_id"]]
            source["article_title"] = mapped_article["title"]
            articles.add(source["article_id"])
            for chunk in article_chunks(source, count_tokens, clause_pattern=_CLAUSE):
                start = chunk["char_start"] + source["char_start"]
                end = chunk["char_end"] + source["char_start"]
                if chunk["text"] != text[start:end] or count_tokens(chunk["text"]) > 256:
                    raise ValueError(f"Invalid source span or token count: {chunk['chunk_id']}")
                chunk.update(char_start=start, char_end=end, topic_id=mapped_article["topic_id"])
                for key in ("title", "so_hieu", "ngay_ban_hanh", "hieu_luc", "trang_thai", "source_url", "nguyen_van"):
                    chunk[key] = doc[key].isoformat() if key == "ngay_ban_hanh" else doc[key]
                chunk["sua_doi"] = [
                    {**change, "ngay_ban_hanh": str(change["ngay_ban_hanh"])}
                    for change in doc.get("sua_doi", []) if change["dieu"] == source["article"]
                ]
                chunks.append(chunk)
    mapped = mapping.keys() if doc_ids is None else {
        article_id for article_id in mapping if article_id.split(":")[0] in doc_ids
    }
    if not chunks or articles != mapped:
        raise ValueError("Corpus articles do not match article_map.tsv")
    return chunks
