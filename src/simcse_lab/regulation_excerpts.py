"""Typeset source-aligned excerpts from the two HCMUS regulation editions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape
from itertools import groupby


_LAYOUT = re.compile(r"<!--[\s\S]*?-->|(?m:^[ \t]*\f[ \t]*\d+[ \t\r]*$)")
_ITEM = re.compile(r"^(?:[-•]\s+|[a-zđ][.)]\s+|\d+[.)]\s+|#{1,6}\s+|Điều \d+[.:])")
_PDF_SCALE = re.compile(r"Thang điểm 10\s+Điểm 4\s+Điểm chữ")
_PDF_RATING = re.compile(r"Điểm trung bình\s+Xếp loại/hạng")
_PDF_TIMES = re.compile(r"Buổi sáng\s+Buổi chiều(?:\s+Buổi tối)?")
_PDF_FORMULA = ("N", "\uf0e5ai.ni", "i\uf03d1", "A\uf03dN", "\uf0e5ni", "i\uf03d1")
_TEX_FORMULA = r"A=\frac{\displaystyle\sum_{i=1}^{N}a_in_i}{\displaystyle\sum_{i=1}^{N}n_i}"


def _inline(value: str) -> str:
    # Escape the source before adding the one inline markup used in these articles.
    return re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", escape(" ".join(value.split())))


def _formula() -> str:
    # QD 1175, PDF p. 12 and QD 3087, PDF p. 15 print the same expression.
    summation = "<munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>N</mi></munderover>"
    credits = "<msub><mi>n</mi><mi>i</mi></msub>"
    grade = "<msub><mi>a</mi><mi>i</mi></msub>"
    return (
        '<div class="equation"><math display="block" '
        'aria-label="A bằng tổng các tích điểm học phần với số tín chỉ, chia cho tổng số tín chỉ">'
        f"<mi>A</mi><mo>=</mo><mfrac><mrow>{summation}{grade}<mo>·</mo>{credits}</mrow>"
        f"<mrow>{summation}{credits}</mrow></mfrac></math></div>"
    )


def _table(headers: list[str], rows: list[list[str]], caption: str) -> str:
    if not rows or any(len(row) != len(headers) for row in rows):
        return "<p>Xem bảng đầy đủ trong văn bản gốc.</p>"
    head = "".join(f'<th scope="col">{_inline(label)}</th>' for label in headers)
    bodies = []
    group = []
    for row in rows:
        if row[0].strip("*").startswith(("a. Loại ", "b. Loại ")) and not any(row[1:]):
            if group:
                bodies.append(f'<tbody>{"".join(group)}</tbody>')
            group = [f'<tr><th scope="rowgroup" colspan="{len(headers)}">{_inline(row[0].strip("*"))}</th></tr>']
        else:
            cells = "".join(f"<td>{_inline(value)}</td>" for value in row)
            group.append(f"<tr>{cells}</tr>")
    bodies.append(f'<tbody>{"".join(group)}</tbody>')
    return (f'<table><caption>{escape(caption)}</caption><thead><tr>{head}</tr></thead>'
            f'{"".join(bodies)}</table>')


def _markdown_table(lines: list[str]) -> str:
    cells = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines]
    if len(cells) < 3 or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells[1]):
        return "<p>Xem bảng đầy đủ trong văn bản gốc.</p>"
    caption = "Xếp loại theo điểm trung bình" if "Xếp loại/hạng" in cells[0] else "Quy đổi điểm học phần"
    return _table(cells[0], cells[2:], caption)


def _pdf_table(lines: list[str], kind: str) -> str:
    # The PDF text layer orders each column correctly but shifts cells vertically.
    # Read the columns independently. Printed sources: QD 1175 pp. 5, 9–10, 12–13.
    if kind == "times":
        headers = re.split(r"\s{2,}", lines[0])
        rows = []
        for line in lines[1:]:
            times = re.split(r"\s+(?=Tiết \d)", line)
            rows.append(times + [""] * (len(headers) - len(times)))
        return _table(headers, rows, "Giờ học theo buổi")
    text = "\n".join(lines[1:])
    if kind == "scale":
        ranges = re.findall(r"(?:\d+,\d+ đến (?:cận )?\d+,\d+|<\d+,\d+)", text)
        grades = re.findall(r"(\d,\d)\s+([A-F]\+?)[ \t]*$", text, re.M)
        rows = [[band, *grade] for band, grade in zip(ranges, grades)] if len(ranges) == len(grades) else []
        return _table(["Thang điểm 10", "Điểm 4", "Điểm chữ"], rows, "Quy đổi điểm học phần")
    bands = re.findall(r"[ab]\. Loại (?:không đạt|đạt)|Từ \d+ đến (?:cận )?\d+|Dưới \d+", text)
    ratings = re.findall(r"(?:Xuất sắc|Giỏi|Khá|Trung bình khá|Trung bình|Yếu|Kém)$", text, re.M)
    rows = []
    if sum(not band.startswith(("a.", "b.")) for band in bands) == len(ratings):
        labels = iter(ratings)
        rows = [[band, "" if band.startswith(("a.", "b.")) else next(labels)] for band in bands]
    return _table(["Điểm trung bình", "Xếp loại/hạng"], rows,
                  "Bảng gốc năm 2021 · đã sửa đổi theo QĐ 91/QĐ-KHTN")


def _pdf_table_kind(line: str) -> str:
    for kind, header in (("scale", _PDF_SCALE), ("rating", _PDF_RATING), ("times", _PDF_TIMES)):
        if header.fullmatch(line):
            return kind
    return ""


@dataclass(frozen=True)
class _Block:
    start: int
    end: int
    kind: str
    html: str


def _blocks(text: str, chunk: dict) -> list[_Block]:
    # Mask layout marks without shifting any offsets used by retrieval.
    masked = _LAYOUT.sub(lambda match: " " * len(match[0]), text.replace("\r", " "))
    lines = list(re.finditer(r"(?m)^[ \t]*(\S[^\n]*)$", masked))
    values = [line[1].strip() for line in lines]
    blocks = []
    i = 0
    while i < len(lines):
        line = values[i]
        end = i + 1
        kind = "p"
        table_kind = _pdf_table_kind(line)
        if line.startswith("|"):
            while end < len(lines) and values[end].startswith("|"):
                end += 1
            kind, html = "table", _markdown_table(values[i:end])
        elif table_kind:
            while end < len(lines):
                value = values[end]
                if _ITEM.match(value) and not value.startswith(("a. Loại ", "b. Loại ")):
                    break
                if table_kind == "times" and not value.startswith("Tiết "):
                    break
                end += 1
            kind, html = "table", _pdf_table(values[i:end], table_kind)
        elif line == "$$":
            while end < len(lines) and values[end] != "$$":
                end += 1
            formula = "".join("".join(values[i + 1:end]).split())
            html = _formula() if formula == _TEX_FORMULA else "<p>Xem công thức trong văn bản gốc.</p>"
            kind, end = "formula", min(end + 1, len(lines))
        elif line == "N" and tuple(v.replace(" ", "") for v in values[i:i + 6]) == _PDF_FORMULA:
            kind, html, end = "formula", _formula(), i + 6
        else:
            while end < len(lines):
                following = values[end]
                if (_ITEM.match(following) or following.startswith(("|", "$$")) or _pdf_table_kind(following)
                        or following in {"N", "Trong đó:"} or re.match(r"(?:A|ai|ni|N) là ", following)):
                    break
                gap = masked[lines[end - 1].end():lines[end].start()]
                if gap.count("\n") > 1 and values[end - 1].endswith((".", ":", "?", "!", ";")):
                    break
                end += 1
            value = re.sub(r"^#{1,6}\s+", "", " ".join(values[i:end]))
            heading = re.match(rf"^Điều {chunk['article']}[.:]\s*", value)
            if heading and value[heading.end():].startswith(chunk["article_title"]):
                value = value[heading.end() + len(chunk["article_title"]):].lstrip()
            if re.match(r"^[-•]\s+", value):
                kind, html = "li", f"<li>{_inline(value[1:])}</li>"
            elif re.match(r"^(A|ai|ni|N) là ", value):
                symbol, definition = value.split(" ", 1)
                symbol = {"ai": "aᵢ", "ni": "nᵢ"}.get(symbol, symbol)
                kind, html = "li", f"<li><strong>{symbol}</strong> {_inline(definition)}</li>"
            elif (chunk.get("clause") is not None and value.startswith(f"{chunk['clause']}. ")
                  and len(value) < 100 and not value.endswith((".", ";")) and end < len(lines)
                  and _ITEM.match(values[end])):
                html = f'<p class="clause-lead">{_inline(value.split(". ", 1)[1])}</p>'
            else:
                html = f"<p>{_inline(value)}</p>" if value else ""
        if html:
            blocks.append(_Block(lines[i].start(1), lines[end - 1].end(), kind, html))
        i = end
    return blocks


def _joined_window(chunk: dict, siblings: list[dict]) -> tuple[str, int, int]:
    """Extend only through matching source overlap inside the selected clause."""
    text = chunk["text"]
    if "char_start" not in chunk or not siblings:
        return text, 0, len(text)
    start, end = chunk["char_start"], chunk["char_end"]
    candidates = sorted((other for other in siblings
                         if other.get("article_id") == chunk.get("article_id")
                         and other.get("clause_id") == chunk.get("clause_id")
                         and other.get("clause") == chunk.get("clause") and "char_start" in other),
                        key=lambda other: other["char_start"])
    for other in reversed(candidates):
        left, right = other["char_start"], other["char_end"]
        if left < start < right and other["text"][start - left:] == text[:right - start]:
            text, start = other["text"][:start - left] + text, left
    for other in candidates:
        left, right = other["char_start"], other["char_end"]
        if left < end < right and text[left - start:] == other["text"][:end - left]:
            text, end = text + other["text"][end - left:], right
    return text, chunk["char_start"] - start, chunk["char_end"] - start


def _render(blocks: list[_Block]) -> str:
    parts = []
    for bullets, group in groupby(blocks, key=lambda block: block.kind == "li"):
        html = "".join(block.html for block in group)
        parts.append(f"<ul>{html}</ul>" if bullets else html)
    return "".join(parts)


def render_excerpt(chunk: dict, siblings: list[dict]) -> str:
    """Render the selected window, completing a paragraph, formula or table it touches."""
    text, start, end = _joined_window(chunk, siblings)
    blocks = [block for block in _blocks(text, chunk) if block.start < end and start < block.end]
    if not blocks:
        return ""
    cut = len(blocks)
    label = "Đọc tiếp trích đoạn"
    if any(block.kind == "formula" for block in blocks) and any(block.kind == "table" for block in blocks):
        cut = next(i for i, block in enumerate(blocks) if block.kind == "table")
        cut = next((i for i in range(cut - 1, -1, -1) if blocks[i].html.startswith("<p>b)")), cut)
        label = ("Xem bảng gốc năm 2021 (đã sửa đổi)"
                 if chunk["doc_id"] == "hcmus-qcdt-2021" else "Xem bảng xếp loại")
    elif len(blocks) > 3:
        for i in range(2, len(blocks)):
            if (blocks[i - 1].end - blocks[0].start >= 550 and blocks[i].kind not in {"li", "table", "formula"}
                    and not blocks[i - 1].html.endswith(":</p>")):
                cut = i
                point = re.fullmatch(r"<p>[a-zđ]\) ([^<>]{1,105}):</p>", blocks[i].html)
                if point:
                    title = point[1].removesuffix(" như sau")
                    label = "Xem " + title[0].lower() + title[1:]
                break
    excerpt = _render(blocks[:cut])
    if cut < len(blocks):
        excerpt += (f'<details class="read-more"><summary>{label}</summary>'
                    f'{_render(blocks[cut:])}</details>')
    return excerpt
