import json
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

import pytest

from data.prepare_virhe4qa import prepare, source_record
from experiments.external_dataset.evaluate_d1_test import PUBLISHED_E1, saved_test_queries
from experiments.external_dataset.run_dense_dev import write_rows
from simcse_lab.evaluation.metrics import query_metrics
from simcse_lab.evaluation.stats import _rr_at_10
from simcse_lab.retrieval.ingest import article_chunks
from simcse_lab.retrieval.preprocess import normalize
from simcse_lab.retrieval.search import maxp


def test_legacy_and_current_e1_queries_use_verified_hashes(tmp_path):
    published = json.loads(PUBLISHED_E1.read_bytes())
    record = published["verification"]["inputs"]["queries.jsonl"]
    assert saved_test_queries(PUBLISHED_E1, published) == record
    old = {"dataset": published["dataset"]}
    assert saved_test_queries(tmp_path / "summary.json", old) == {
        "path": (tmp_path / "inputs/queries.jsonl").as_posix(), "sha256": record["sha256"],
    }
    with pytest.raises(ValueError, match="dataset differs"):
        saved_test_queries(tmp_path / "summary.json", {"dataset": {}})


@pytest.mark.parametrize("entry", [
    ["-m", "experiments.external_dataset.run_retrieval"],
    ["experiments/external_dataset/run_retrieval.py"],
])
def test_retrieval_cli_entry_points(entry, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.setenv("PYTHONPATH", str(root / "src"))
    result = subprocess.run([sys.executable, *entry, "--help"], cwd=root, check=True, capture_output=True)
    assert b"verify-d1-dev" in result.stdout


def test_run_jsonl_uses_lf(tmp_path: Path) -> None:
    output = tmp_path / "runs" / "dense.jsonl"
    write_rows(output, [{"qid": "q1"}, {"qid": "q2"}])

    assert output.read_bytes() == b'{"qid": "q1"}\n{"qid": "q2"}\n'


def test_d1_dev_manifest_hashes_match_rankings() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / "experiments/external_dataset/results/D1-dev-retrieval-check/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for method, entry in manifest["runs"].items():
        ranking_path = manifest_path.parent / entry["path"]
        assert sha256(ranking_path.read_bytes()).hexdigest() == entry["sha256"], method


@pytest.mark.parametrize("rank, expected", [
    (1, (1, 1, 1.0)), (2, (0, 1, 0.5)), (10, (0, 0, 0.1)), (11, (0, 0, 0.0)),
])
def test_metrics(rank, expected):
    ranked = list(range(1, 21))
    scores = query_metrics(ranked, {rank})
    assert tuple(scores.values()) == expected
    assert scores["mrr_at_10"] == _rr_at_10(ranked, {rank})


def test_maxp_before_truncation_and_ties():
    chunks = [
        {"article_id": a, "chunk_id": c}
        for a, c in (("b", "b2"), ("b", "b1"), ("b", "b3"), ("a", "a1"))
    ]
    assert maxp(chunks, [0.9, 0.9, 0.85, 0.85], 2) == [
        ["b", 0.9, "b1"], ["a", 0.85, "a1"],
    ]
    assert maxp(chunks, [0.9] * 4, 1) == [["a", 0.9, "a1"]]


def test_chunk_windows_keep_source_offsets():
    text = "Điều 6. Ví dụ\n1. Một hai ba bốn năm sáu\n2. Hai ba."
    chunks = article_chunks(source_record(text), lambda s: len(s.split()) + 2, limit=6, overlap=1)
    assert {row["clause"] for row in chunks} == {None, 1, 2}
    assert "sáu" in " ".join(row["text"] for row in chunks)
    for row in chunks:
        assert row["text"] == text[row["char_start"]:row["char_end"]]
        assert len(row["text"].split()) + 2 <= 6


def test_duplicate_question_with_different_gold_fails():
    with pytest.raises(ValueError, match="10, 20"):
        prepare([
            {"index": "10", "question": "Câu hỏi?", "context": "A"},
            {"index": "20", "question": "Câu hỏi?", "context": "B"},
        ])


def test_normalization_preserves_internal_tone():
    assert normalize("khoà khoá qua cạo quán quản quý") == "khòa khóa qua cạo quán quản quý"
    assert normalize("kho\u0301a khoá") == "khóa khóa"
