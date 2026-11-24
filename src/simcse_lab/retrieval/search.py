"""Rank articles by the cosine of their best chunk."""

import math


def maxp(chunks, scores, k=20):
    if len(chunks) != len(scores):
        raise ValueError("Expected one cosine per chunk")
    best = {}
    for chunk, value in zip(chunks, scores):
        article_id, chunk_id = chunk["article_id"], chunk["chunk_id"]
        score = float(value)
        if not math.isfinite(score) or abs(score) > 1.000001:
            raise ValueError(f"Invalid cosine for {chunk_id}: {score}")
        score = min(1.0, max(-1.0, score))
        previous = best.get(article_id)
        if previous is None or (-score, chunk_id) < (-previous[0], previous[1]):
            best[article_id] = (score, chunk_id)
    order = sorted(best, key=lambda article_id: (-best[article_id][0], article_id))
    return [[article_id, *best[article_id]] for article_id in order[:k]]
