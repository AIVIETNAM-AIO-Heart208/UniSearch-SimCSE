"""Regression tests for clause selection, disclosure grading and the saved pilot."""

import json
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

from experiments.application.compare_clause_scope import evidence_path, select_clauses


def test_within_article_selection_ignores_titles_and_breaks_ties_deterministically():
    index = SimpleNamespace(
        chunks=[{"chunk_id": name, "clause_id": label}
                for name, label in [("title", None), ("b", "one"), ("a", "two"), ("title-only", None)]],
        groups={"x": [0, 1, 2], "y": [3]},
    )
    ranked = [["x", 1.0, "title"], ["y", 0.0, "title-only"]]
    assert select_clauses(index, ([10, 2, 2, 0], [1, .4, .4, -.1]), ranked, .6) == [
        ["x", 1.0, "a"], ["y", 0.0, "title-only"]
    ]


def test_sufficient_passage_can_require_opening_topic_edition_and_excerpt(monkeypatch):
    old = {"clause_id": "accepted"}
    recent = {"clause_id": "other"}
    row = {"qid": "pilot-05", "gold_clause_ids": ["accepted"]}
    html = ("<div class='passage'><p>Bảng điểm theo từng học phần</p><details><summary>more</summary>"
            "<p>phát kèm theo bằng tốt nghiệp</p></details></div>")
    monkeypatch.setattr("apps.app._edition_body", lambda chunk, index: html)
    assert evidence_path(row, [(recent, 1), (old, .9)], None, False) == ["open_topic", "other_edition", "read_more"]
    assert evidence_path(row, [(old, 1)], None, True) == ["read_more"]
    assert evidence_path(row, [(recent, 1)], None, True) is None


def test_published_pilot_can_replay_both_rankers_and_all_decisions_without_the_model():
    root = Path(__file__).resolve().parents[1]
    directory = root / "experiments/application/results/clause-scope-pilot"
    manifest = json.loads((directory / "summary.json").read_bytes())
    raw = (directory / "predictions.jsonl").read_bytes()
    assert sha256(raw).hexdigest() == manifest["predictions_sha256"]
    pilot = manifest["inputs"]["pilot"]
    labels = (root / pilot["path"]).read_bytes()
    assert sha256(labels).hexdigest() == pilot["sha256"]
    rows = list(map(json.loads, raw.splitlines()))
    assert [r["qid"] for r in rows] == [json.loads(line)["qid"] for line in labels.splitlines()]
    ids = manifest["raw_score_chunk_order"]
    clauses = manifest["raw_score_clause_ids"]
    articles = [c.rsplit(":", 1)[0] for c in ids]
    groups = {a: [i for i, other in enumerate(articles) if a == other] for a in set(articles)}
    weight = Fraction(str(manifest["config"]["weight"]))
    threshold = manifest["config"]["threshold"]
    for row in rows:
        b, d = row["raw_bm25"], row["raw_cosine"]
        maxima = [{a: max(values[i] for i in indices) for a, indices in groups.items()} for values in (b, d)]
        def scale(value, maximum):
            low, high = min(maximum.values()), max(maximum.values())
            return (value - low) / (high - low) if high != low else 0

        def fusion(x, y):
            return float(weight) * scale(x, maxima[0]) + float(1 - weight) * scale(y, maxima[1])

        order = sorted(groups, key=lambda a: (-fusion(maxima[0][a], maxima[1][a]), a))
        assert len(order) == 51 and order == row["article_order"]
        assert row["article_scores"] == [fusion(maxima[0][a], maxima[1][a]) for a in order]
        leaders = [min(m, key=lambda a: (-m[a], a)) for m in maxima] + [order[0]]
        assert leaders == [row["first_articles"][k] for k in ("bm25", "dense", "hybrid")]
        for pos, a in enumerate(order):
            group = groups[a]
            fused = {i: fusion(b[i], d[i]) for i in group}
            first = min(group, key=lambda i: (-fused[i], ids[i]))
            assert row["selected_chunks"]["A"][pos] == ids[first]
            candidates = [i for i in group if clauses[i]]
            if candidates:
                # Sorted lists retain duplicates, giving competition ranks (1, 1, 3).
                bs, ds = (sorted((v[i] for i in candidates), reverse=True) for v in (b, d))
                ranks = {i: weight / (1 + bs.index(b[i])) + (1 - weight) / (1 + ds.index(d[i]))
                         for i in candidates}
                first = min(candidates, key=lambda i: (-ranks[i], -fused[i], ids[i]))
            assert row["selected_chunks"]["K"][pos] == ids[first]
        assert max(b) == row["max_bm25"]
        agreement = max(b) > 0 and len(set(row["first_topics"].values())) == 1
        assert row["topic_gate"] is agreement
        for name, trial in row["variants"].items():
            family = "K" if name in ("K", "K+G") else "A"
            index = ids.index(row["selected_chunks"][family][0])
            assert (trial["chunk_id"], trial["clause_id"], trial["cosine"]) == (ids[index], clauses[index], d[index])
            assert trial["accepted"] is (d[index] >= threshold and (name in ("A", "K") or agreement))
            if row["scope"] == "in":
                assert trial["clause_hit"] is (clauses[index] in row["gold_clause_ids"])
