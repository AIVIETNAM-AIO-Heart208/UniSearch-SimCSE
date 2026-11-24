"""Hand-scored JSONL examples for paired intervals and warning evaluation."""

import json
import random

import pytest

from simcse_lab.evaluation.stats import paired_bootstrap, select_threshold, warning_metrics


def query(qid, gold, source="virhe4qa", split="dev"):
    return {"qid": qid, "question": "example", "source": source, "split": split,
            "in_scope": bool(gold), "gold_article_ids": gold, "gold_clause_ids": [],
            "origin": "team" if source == "d2" else None}


def run_row(qid, ranking, cosine):
    # Tied ranking scores test that the published order is authoritative.
    return {"qid": qid, "ranked": [[a, 1.0, f"{a}:chunk"] for a in ranking],
            "top1_dense_cos": cosine}


def d1_run(qid, gold_rank, cosine=0.5):
    ranking = [f"d{i}" for i in range(19)]
    ranking.insert(gold_rank - 1, "answer")
    return run_row(qid, ranking, cosine)


def test_paired_bootstrap_sign_cutoff_seed_and_qid_alignment():
    queries = [query("a", ["answer"]), query("b", ["answer"])]
    baseline = [d1_run("a", 1), d1_run("b", 11)]
    candidate = [d1_run("b", 1), d1_run("a", 2)]
    state = random.getstate()
    result = paired_bootstrap(queries, baseline, candidate)
    assert result == paired_bootstrap(reversed(queries), reversed(baseline), reversed(candidate))
    assert random.getstate() == state
    assert (result["n_in_scope"], result["n_resamples"], result["seed"]) == (2, 1000, 42)
    assert result["levels"] == {"article": {
        "mrr_at_10": {"delta": 0.25, "lower": -0.5, "upper": 1.0},
        "hit_at_1": {"delta": 0.0, "lower": -1.0, "upper": 1.0},
    }}
    # Seed 42 draws (b,a), then (a,a). Their mean RR changes are 0.25 and -0.5.
    two_draws = paired_bootstrap(queries, baseline, candidate, n_resamples=2)["levels"]["article"]
    assert two_draws["mrr_at_10"] == pytest.approx(
        {"delta": 0.25, "lower": -0.48125, "upper": 0.23125})
    assert two_draws["hit_at_1"] == pytest.approx(
        {"delta": 0.0, "lower": -0.975, "upper": -0.025})


def test_multiple_gold_and_rank_ten_on_a_single_question():
    queries = [query(7, ["answer", "also-correct"])]
    old, new = d1_run(7, 11), d1_run(7, 10)
    new["ranked"][-1] = ["also-correct", 1.0, "another-chunk"]
    result = paired_bootstrap(queries, [old], [new])["levels"]["article"]
    assert result["mrr_at_10"] == pytest.approx(dict.fromkeys(("delta", "lower", "upper"), 0.1))
    assert result["hit_at_1"] == dict.fromkeys(("delta", "lower", "upper"), 0.0)


def test_topic_collapse_precedes_cutoff_and_bootstrap_excludes_out_of_scope():
    topics = {**{f"d{i}": "same" for i in range(10)}, "other-version": "gold", "gold": "gold"}
    articles = list(topics)
    queries = [query(1, ["gold"], "d2", "test"), query(2, [], "d2", "test")]
    baseline = [run_row(q["qid"], articles, 0.0) for q in queries]
    candidate = [run_row(q["qid"], ["other-version", *articles[:10], "gold"], 0.0)
                 for q in queries]
    result = paired_bootstrap(queries, baseline, candidate, article_to_topic=topics)
    assert result["n_in_scope"] == 1
    for metric in ("hit_at_1", "mrr_at_10"):
        assert result["levels"]["article"][metric] == dict.fromkeys(("delta", "lower", "upper"), 0)
    assert result["levels"]["topic"]["mrr_at_10"]["delta"] == 0.5
    assert result["levels"]["topic"]["hit_at_1"]["delta"] == 1.0


def test_fixed_warning_has_distinct_denominators_and_uses_raw_cosine():
    topics = {"A": "T1", "B": "T1", "C": "T2"}
    cases = [(["A"], "BAC", 0.5), (["C"], "CBA", 0.9), (["B"], "CAB", 0.49),
             (["A"], "ACB", -0.5), ([], "ABC", 0.8), ([], "BCA", 0.1), ([], "BAC", 0.7)]
    queries = [query(i, gold, "d2", "test") for i, (gold, _, _) in enumerate(cases)]
    run = [run_row(i, rank, cos) for i, (_, rank, cos) in enumerate(cases)]
    result = warning_metrics(queries, reversed(run), threshold=0.5, article_to_topic=topics)
    assert result == {
        "threshold": 0.5, "n_queries": 7, "coverage": 4 / 7,
        "n_out_of_scope": 3, "n_confident_out_of_scope": 2, "false_confidence": 2 / 3,
        "groups": {"confident": {"n": 4, "n_in_scope": 2, "hit_at_1": {"article": 0.5, "topic": 1}},
                   "warned": {"n": 3, "n_in_scope": 2, "hit_at_1": {"article": 0.5, "topic": 0.5}}},
    }


def test_empty_groups_and_no_out_of_scope_are_json_null():
    result = warning_metrics([query("q", ["answer"])], [d1_run("q", 2)], threshold=-1)
    assert result["coverage"] == 1
    assert result["false_confidence"] is None
    assert result["groups"]["warned"] == {"n": 0, "n_in_scope": 0, "hit_at_1": {"article": None}}
    assert result["groups"]["confident"]["hit_at_1"] == {"article": 0.0}
    json.dumps(result, allow_nan=False)
    queries, run = [query(1, [], "d2", "test")], [run_row(1, ["a"], -1)]
    result = warning_metrics(queries, run, threshold=0.0, article_to_topic={"a": "topic"})
    assert result["coverage"] == result["false_confidence"] == 0
    assert result["groups"]["warned"]["hit_at_1"] == {"article": None, "topic": None}
    with pytest.raises(ValueError, match="in-scope"):
        paired_bootstrap(queries, run, run, article_to_topic={"a": "topic"})


def test_dev_threshold_ties_rounding_and_transfer():
    scores = [0.9, 0.8, 0.5, 0.5, 0.5, -0.1]
    queries = [query(i, ["answer"]) for i in range(len(scores))]
    run = [d1_run(i, 1, s) for i, s in enumerate(scores)]
    theta = select_threshold(queries, reversed(run))
    assert theta == 0.5
    assert select_threshold(queries, run, min_coverage=1.0) == -0.1
    assert select_threshold(queries, run, min_coverage=0.01) == 0.9
    assert warning_metrics(queries, run, threshold=theta)["coverage"] == 5 / 6
    held_out = [query(0, ["answer"], split="test")]
    assert warning_metrics(held_out, [d1_run(0, 1, 0.2)], threshold=theta)["coverage"] == 0


@pytest.mark.parametrize("source", ["virhe4qa", "d2"])
def test_threshold_cannot_be_fitted_on_test(source):
    with pytest.raises(ValueError, match="D1-dev"):
        select_threshold([query(1, ["answer"], source, "test")], [d1_run(1, 1)])


@pytest.mark.parametrize("bad_rows", [[], [d1_run("wrong", 1)], [d1_run("q", 1)] * 2])
def test_mismatched_or_duplicate_qids_never_silently_drop_queries(bad_rows):
    with pytest.raises(ValueError, match="qid"):
        paired_bootstrap([query("q", ["answer"])], [d1_run("q", 1)], bad_rows)


@pytest.mark.parametrize("invalid_cosine", [None, float("nan"), float("inf"), -1.01, True])
def test_unusable_cosine_is_never_classified_as_a_warning(invalid_cosine):
    qs, run = [query(1, ["answer"])], [d1_run(1, 1, invalid_cosine)]
    with pytest.raises(ValueError, match="top1_dense_cos"):
        warning_metrics(qs, run, threshold=0.5)
    with pytest.raises(ValueError, match="top1_dense_cos"):
        select_threshold(qs, run)


def test_float32_endpoint_roundoff_is_consistent_for_fit_and_scoring():
    qs, run = [query(1, ["answer"])], [d1_run(1, 1, 1.00000012)]
    theta = select_threshold(qs, run)
    assert theta == warning_metrics(qs, run, threshold=theta)["coverage"] == 1


def test_manifest_ranking_and_topic_map_integrity():
    qs, run = [query("q", ["a"], "d2", "test")], [run_row("q", ["a", "b"], 0.4)]
    for topics in (None, {"b": "T"}, {"a": "T"}, {"a": "T", "b": "T", "c": "U"}):
        with pytest.raises(ValueError):
            warning_metrics(qs, run, threshold=0.5, article_to_topic=topics)
    with pytest.raises(ValueError, match="duplicate article"):
        warning_metrics(qs, [run_row("q", ["a", "a"], 0.4)], threshold=0, article_to_topic={"a": "T"})
    with pytest.raises(ValueError, match="top-20"):
        paired_bootstrap([query("q", ["a"])], run, run)
    with pytest.raises(ValueError, match="duplicate qid"):
        select_threshold(qs * 2, run)
    with pytest.raises(ValueError, match="single"):
        select_threshold([*qs, query(1, ["a"])], run)
    with pytest.raises(ValueError, match="in_scope"):
        warning_metrics([dict(qs[0], in_scope=False)], run, threshold=0)
    with pytest.raises(ValueError, match="at least one query"):
        warning_metrics([], [], threshold=0.8)


def test_calibration_rejects_corrupt_rankings_even_with_a_valid_cosine():
    qs, row = [query(1, ["answer"])], d1_run(1, 1)
    row["ranked"][1][1] = 2
    with pytest.raises(ValueError, match="descending"):
        select_threshold(qs, [row])
    row["ranked"][1][1] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        select_threshold(qs, [row])


def test_malformed_dataset_id_is_reported_as_invalid_input():
    with pytest.raises(ValueError, match="single"):
        select_threshold([query(1, ["answer"], source=[])], [])


def test_invalid_controls_cannot_produce_a_report():
    qs, run = [query(1, ["answer"])], [d1_run(1, 1)]
    with pytest.raises(ValueError, match="n_resamples"):
        paired_bootstrap(qs, run, run, n_resamples=1)
    with pytest.raises(ValueError, match="threshold"):
        warning_metrics(qs, run, threshold=float("nan"))
    for coverage in (0, 1.01, float("nan")):
        with pytest.raises(ValueError, match="min_coverage"):
            select_threshold(qs, run, min_coverage=coverage)
