import pytest

from data.prepare_virhe4qa import prepare, source_record
from simcse_lab.evaluation.metrics import query_metrics
from simcse_lab.evaluation.stats import _rr_at_10
from simcse_lab.retrieval.ingest import article_chunks
from simcse_lab.retrieval.preprocess import normalize
from simcse_lab.retrieval.search import maxp


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
