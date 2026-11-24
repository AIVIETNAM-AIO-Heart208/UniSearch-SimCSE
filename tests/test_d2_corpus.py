"""Check the public topic map and the reproducible private corpus preparation."""

import csv
import hashlib
from pathlib import Path

import pytest
import yaml

from data.d2 import prepare_2026


def test_corpus_manifest_identifies_both_sources_and_their_index_inputs():
    root = Path(__file__).resolve().parents[1]
    documents = yaml.safe_load((root / "data/d2/documents.yaml").read_bytes())["documents"]
    by_id = {doc["doc_id"]: doc for doc in documents}
    assert len(documents) == 2 and set(by_id) == {"hcmus-qcdt-2021", "hcmus-qcdt-2026"}
    for doc in documents:
        for key in ("title", "so_hieu", "hieu_luc", "trang_thai", "source_url"):
            assert isinstance(doc[key], str) and doc[key].strip(), (doc["doc_id"], key)
    public = by_id["hcmus-qcdt-2021"]
    assert hashlib.sha256((root / public["text_file"]).read_bytes()).hexdigest() == public["text_sha256"]
    transcribed = by_id["hcmus-qcdt-2026"]
    assert root / transcribed["base_file"] == prepare_2026.BASE
    assert root / transcribed["file"] == prepare_2026.TARGET
    assert transcribed["base_sha256"] == prepare_2026.BASE_SHA256
    assert transcribed["sha256"] == prepare_2026.TARGET_SHA256


def test_topic_map_covers_each_regulation_article_once():
    path = Path(__file__).resolve().parents[1] / "data/d2/article_map.tsv"
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    articles = [(r["doc_id"], int(r["dieu"])) for r in rows]
    expected = {(f"hcmus-qcdt-{year}", n) for year, last in [(2021, 24), (2026, 27)]
                for n in range(1, last + 1)}
    assert len(articles) == len(expected) and set(articles) == expected
    assert len({r["topic_id"] for r in rows}) == 26


def test_corrections_are_reproducible_and_preserve_existing_data(tmp_path, monkeypatch):
    base = "\n".join(old for old, new in prepare_2026.CORRECTIONS).encode()
    expected = "\n".join(new for old, new in prepare_2026.CORRECTIONS).encode()
    source, target = tmp_path / "base.md", tmp_path / "corrected.md"
    source.write_bytes(base)
    monkeypatch.setattr(prepare_2026, "BASE_SHA256", hashlib.sha256(base).hexdigest())
    monkeypatch.setattr(prepare_2026, "TARGET_SHA256", hashlib.sha256(expected).hexdigest())
    prepare_2026.prepare(source, target)
    prepare_2026.prepare(source, target)
    assert source.read_bytes() == base and target.read_bytes() == expected
    target.write_bytes(b"another version")
    with pytest.raises(ValueError, match="Destination"):
        prepare_2026.prepare(source, target)
    source.write_bytes(b"wrong input")
    with pytest.raises(ValueError, match="base transcription"):
        prepare_2026.prepare(source, target)
    assert target.read_bytes() == b"another version"
