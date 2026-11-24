"""Rank articles by the cosine of their best chunk."""

import math

from .preprocess import segment


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


def _scale(values):
    low, high = min(values), max(values)
    return (lambda value: (value - low) / (high - low)) if high > low else (lambda value: 0.0)


class RetrievalIndex:
    """Score a fixed set of chunks with one shared CPU index."""

    def __init__(self, chunks, encoder, batch_size=16, tokenize=segment):
        from rank_bm25 import BM25Okapi

        if not chunks:
            raise ValueError("Cannot index an empty corpus")
        self.encoder, self.batch_size, self.tokenize = encoder, batch_size, tokenize
        self.chunks = chunks
        self.by_chunk = {chunk["chunk_id"]: chunk for chunk in chunks}
        if len(self.by_chunk) != len(chunks):
            raise ValueError("Duplicate chunk IDs")
        self.groups = {}
        for index, chunk in enumerate(chunks):
            self.groups.setdefault(chunk["article_id"], []).append(index)
        texts = [chunk["text"] for chunk in chunks]
        self.bm25 = BM25Okapi([self._terms(text) for text in texts])
        self.vectors = encoder.encode(texts, batch_size)

    def _terms(self, text):
        return self.tokenize(text).lower().split()

    def _bm25_scores(self, question):
        lexical = self.bm25.get_scores(self._terms(question)).tolist()
        if not all(map(math.isfinite, lexical)):
            raise ValueError("Invalid BM25 score")
        return lexical

    def rank_bm25(self, question, k=None):
        """Rank by BM25 without embedding the question or scoring confidence."""
        return self._ranked(self._best_per_article(self._bm25_scores(question)), k)

    def score(self, questions):
        vectors = self.encoder.encode(questions, self.batch_size)
        for question, cosines in zip(questions, vectors @ self.vectors.T):
            if any(not math.isfinite(value) or abs(value) > 1.000001 for value in cosines):
                raise ValueError("Invalid cosine score")
            dense = [min(1.0, max(-1.0, float(value))) for value in cosines]
            yield self._bm25_scores(question), dense

    def rank(self, scores, method, weight=0.5, k=None):
        if method not in {"dense", "bm25", "hybrid"} or not 0 <= weight <= 1:
            raise ValueError("Expected dense, bm25 or hybrid and a weight in [0, 1]")
        lexical, dense = scores
        lexical_max = self._best_per_article(lexical)
        if method == "bm25" or (method == "hybrid" and weight == 1):
            best = lexical_max
        else:
            dense_max = self._best_per_article(dense)
            if method == "dense" or weight == 0:
                best = dense_max
            else:
                lex_scale = _scale([score for score, _ in lexical_max.values()])
                dense_scale = _scale([score for score, _ in dense_max.values()])
                fused_chunks = [
                    weight * lex_scale(b) + (1 - weight) * dense_scale(d)
                    for b, d in zip(lexical, dense)
                ]
                best = {
                    article: (weight * lex_scale(score) + (1 - weight) * dense_scale(dense_max[article][0]), idx)
                    for article, (score, idx) in lexical_max.items()
                }
                excerpts = self._best_per_article(fused_chunks)
                best = {article: (score, excerpts[article][1]) for article, (score, _) in best.items()}
        ranked = self._ranked(best, k)
        return ranked, dense[best[ranked[0][0]][1]] if ranked else None

    def _ranked(self, best, k):
        order = sorted(best, key=lambda article: (-best[article][0], article))[:k]
        return [[article, best[article][0], self.chunks[best[article][1]]["chunk_id"]] for article in order]

    def _best_per_article(self, scores):
        best = {}
        for article, indices in self.groups.items():
            index = min(indices, key=lambda i: (-scores[i], self.chunks[i]["chunk_id"]))
            best[article] = (scores[index], index)
        return best
