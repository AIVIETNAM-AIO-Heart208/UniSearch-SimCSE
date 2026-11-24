"""Calculate D1 retrieval metrics from complete top-20 rankings."""

from statistics import fmean

from simcse_lab.evaluation.stats import _queries, _ranked_articles, _run, first_relevant_rank


def query_metrics(ranked, gold):
    rank = first_relevant_rank(ranked, gold, 10)
    return {
        "hit_at_1": int(rank == 1),
        "hit_at_3": int(rank is not None and rank <= 3),
        "mrr_at_10": 1 / rank if rank is not None else 0.0,
    }


def evaluate_d1(queries, runs):
    manifest = _queries(queries)
    if any(query["source"] != "virhe4qa" for query in manifest.values()):
        raise ValueError("Expected queries from ViRHE4QA")
    run_map = _run(runs, manifest)
    per_query = [
        query_metrics(_ranked_articles(run_map[qid], None), set(query["gold_article_ids"]))
        for qid, query in manifest.items()
    ]
    return {key: fmean(row[key] for row in per_query) for key in per_query[0]}
