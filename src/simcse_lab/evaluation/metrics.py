"""Calculate D1 retrieval metrics from complete top-20 rankings."""

from statistics import fmean

from simcse_lab.evaluation.stats import _queries, _ranked_articles, _run, first_relevant_rank


def query_metrics(ranked, gold, *, hit_cutoffs=(1, 3)):
    if not hit_cutoffs or any(type(k) is not int or not 1 <= k <= 20 for k in hit_cutoffs):
        raise ValueError("Hit cutoffs must be integers in the D1 top 20")
    rank = first_relevant_rank(ranked, gold, max(10, max(hit_cutoffs)))
    return {
        **{f"hit_at_{k}": int(rank is not None and rank <= k) for k in hit_cutoffs},
        "mrr_at_10": 1 / rank if rank is not None and rank <= 10 else 0.0,
    }


def evaluate_d1(queries, runs, *, hit_cutoffs=(1, 3)):
    manifest = _queries(queries)
    if any(query["source"] != "virhe4qa" for query in manifest.values()):
        raise ValueError("Expected queries from ViRHE4QA")
    run_map = _run(runs, manifest)
    per_query = [
        query_metrics(_ranked_articles(run_map[qid], None), set(query["gold_article_ids"]), hit_cutoffs=hit_cutoffs)
        for qid, query in manifest.items()
    ]
    return {key: fmean(row[key] for row in per_query) for key in per_query[0]}
