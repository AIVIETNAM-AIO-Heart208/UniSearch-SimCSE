"""Map original source spans to model-sized chunks."""

from __future__ import annotations

import re
from typing import Pattern

_CLAUSE = re.compile(r"(?m)^[ \t]*(?:Khoản[ \t]+)?(\d+)[.)][ \t]+")


def clause_spans(text: str, pattern: Pattern[str]) -> list[tuple[int, int, int | None]]:
    """Return character ranges and the printed number of each clause."""
    boundaries = [(0, None)]
    boundaries.extend((match.start(), int(match[1])) for match in pattern.finditer(text))
    return [(start, end, number) for (start, number), (end, _) in
            zip(boundaries, boundaries[1:] + [(len(text), None)])]


def article_chunks(source, count_tokens, limit=256, overlap=24, clause_pattern=_CLAUSE):
    text = source["text"]
    chunks = []
    for start, end, clause in clause_spans(text, clause_pattern):
        words = list(re.finditer(r"\S+", text[start:end]))
        left = 0
        while left < len(words):
            begin = start + words[left].start()
            low, high = left + 1, len(words)
            best = left
            while low <= high:
                middle = (low + high) // 2
                stop = start + words[middle - 1].end()
                if count_tokens(text[begin:stop]) <= limit:
                    best = middle
                    low = middle + 1
                else:
                    high = middle - 1
            if best == left:
                raise ValueError(f"One word exceeds token limit in {source['article_id']} at {begin}")
            stop = start + words[best - 1].end()
            chunks.append(dict(
                source, chunk_id=f"{source['article_id']}:{len(chunks):04d}",
                clause=clause, text=text[begin:stop], char_start=begin, char_end=stop,
            ))
            if best == len(words):
                break
            left = max(left + 1, best - overlap)
    return chunks
