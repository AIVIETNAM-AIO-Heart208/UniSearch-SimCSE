"""Check D2 scoring with hand-labelled synthetic data and saved rankings."""

import pytest

from simcse_lab.evaluation.d2 import evaluate_d2
from simcse_lab.retrieval.hcmus import chunk_clause_id, regulation_clauses
from simcse_lab.retrieval.ingest import article_chunks


@pytest.fixture
def dataset():
    texts = {"a": "First article\n3. first rule\n3. second rule",
             "alt": "Other edition\n1. alternative", "b": "Second topic\n1. recall"}
    articles = {key: {"article_id": key, "text": text, "char_start": 0} for key, text in texts.items()}
    topics = {"a": "t1", "alt": "t1", "b": "t2"}
    chunks = []
    target_chunks = {}
    for article, source in articles.items():
        for chunk in article_chunks(source, lambda text: len(text.split())):
            chunk["topic_id"] = topics[article]
            clause = chunk_clause_id(chunk, regulation_clauses(source))
            if clause:
                target_chunks.setdefault(article, chunk["chunk_id"])
            # Exercise the legacy shape with clause numbers and offsets only.
            chunks.append(chunk)
    queries = [
        {"qid": "1", "question": "second rule", "in_scope": True, "origin": "team",
         "gold_article_ids": ["a"], "gold_clause_ids": ["a:khoan-3:2"]},
        {"qid": "2", "question": "alternative", "in_scope": True, "origin": "form",
         "gold_article_ids": ["alt"], "gold_clause_ids": ["alt:khoan-1"]},
        {"qid": "3", "question": "unrelated", "in_scope": False, "origin": "team",
         "gold_article_ids": [], "gold_clause_ids": []},
    ]
    for row in queries:
        row.update(source="d2", split="test")

    def ranking(qid, order, confidence):
        return {"qid": qid, "top1_dense_cos": confidence,
                "ranked": [[article, 3 - index, target_chunks[article]] for index, article in enumerate(order)]}

    bm25 = [ranking("1", ("a", "alt", "b"), 0.6), ranking("2", ("alt", "b", "a"), 0.65),
            ranking("3", ("b", "a", "alt"), 0.9)]
    hybrid = [ranking("1", ("a", "b", "alt"), 0.6), ranking("2", ("a", "alt", "b"), 0.6), bm25[2]]
    return queries, {"bm25": bm25, "dense": bm25, "hybrid": hybrid}, chunks, articles, topics


def test_d2_levels_intervals_and_tied_risk_points(dataset):
    result = evaluate_d2(*dataset, threshold=0.6, tokenize=lambda text: set(text.split()))
    hybrid = result["overall"]["metrics"]["hybrid"]
    assert hybrid["article"]["hit_at_1"] == 0.5 and hybrid["article"]["mrr_at_10"] == 0.75
    assert hybrid["topic"]["hit_at_1"] == 1.0
    assert hybrid["clause"] == {"n": 2, "hit_at_1": 0.0}
    assert result["overall"]["metrics"]["bm25"]["clause"] == {"n": 2, "hit_at_1": 0.5}
    assert result["overall"]["hybrid_minus_bm25"]["levels"]["article"]["hit_at_1"]["delta"] == -0.5
    assert result["random_baseline"]["article"]["hit_at_1"] == pytest.approx(1 / 3)
    assert result["form"]["qids"] == ["2"]
    assert result["risk_coverage"][0]["risk"] == {"article": None, "topic": None}
    assert [point["accepted"] for point in result["risk_coverage"]] == [1, 3]
    assert result["operating_point"]["risk"] == {"article": 0.5, "topic": 0.0}
    assert result["warnings"]["false_confidence"] == 1.0


def test_d2_rejects_ambiguous_clause_labels_and_mismatched_chunks(dataset):
    queries, runs, chunks, articles, topics = dataset
    queries[0]["gold_clause_ids"] = ["a:khoan-3"]
    with pytest.raises(ValueError, match="gold_clause_ids"):
        evaluate_d2(*dataset, threshold=0.6, tokenize=lambda text: set(text.split()))
    queries[0]["gold_clause_ids"] = ["a:khoan-3:2"]
    runs["hybrid"][0]["ranked"][0][2] = runs["hybrid"][0]["ranked"][1][2]
    with pytest.raises(ValueError, match="does not belong"):
        evaluate_d2(*dataset, threshold=0.6, tokenize=lambda text: set(text.split()))


def test_d2_empty_in_scope_groups_have_undefined_accuracy(dataset):
    queries, runs, chunks, articles, topics = dataset
    result = evaluate_d2(queries[2:], {m: rows[2:] for m, rows in runs.items()}, chunks, articles, topics,
                         threshold=0.95, tokenize=lambda s: set(s.split()))
    assert result["overall"]["n"] == 0
    assert result["overall"]["hybrid_minus_bm25"] is None
    assert result["overall"]["metrics"]["hybrid"]["article"]["hit_at_1"] is None
    assert result["operating_point"]["accepted"] == 0
    assert result["warnings"]["false_confidence"] == 0.0
