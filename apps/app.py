"""Local regulation search for HCMUS and the optional ViRHE4QA corpus."""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

from simcse_lab.model.encoders import SimCSEEncoder, verify_snapshot
from simcse_lab.regulation_excerpts import render_excerpt
from simcse_lab.retrieval.ingest import article_chunks
from simcse_lab.retrieval.search import RetrievalIndex

D1_ARCHIVE = "https://github.com/DoPhamPhucTinh/R2GQA/blob/0653933b6f28b8a05bb822997aed734f7590670e/ViRHE4QA.zip"


ALL = "Tra cứu chung"
COHORTS = ("K21", "K22", "K23", "K24", "K25", "K26 trở đi", "Trước K21", ALL)
TRACKS = ("Chính quy", "Từ xa", ALL)
EARLY_COHORT_NOTICE = ("Demo chưa có quy chế nền cho khóa tuyển trước năm 2021. "
                       "Bạn có thể chọn Tra cứu chung để tham khảo hai văn bản hiện có.")


def _load_d1_sources() -> dict:
    folder = Path(__file__).resolve().parents[1] / "data" / "d1"
    documents = json.loads((folder / "documents.json").read_text(encoding="utf-8"))
    with (folder / "pdf_pages.tsv").open(encoding="utf-8", newline="") as stream:
        pages = {row["article_id"]: (row["first_page"], row["last_page"])
                 for row in csv.DictReader(stream, delimiter="\t")}
    with (folder / "sources.tsv").open(encoding="utf-8", newline="") as stream:
        return {row["article_id"]: {**documents[row["document"]], **row, "pages": pages.get(row["article_id"])}
                for row in csv.DictReader(stream, delimiter="\t")}


def _group_ranked_articles(index, ranked, limit=3, *, require_signal=False):
    groups = {}
    leaders = {}
    for _, score, chunk_id in ranked:
        chunk = index.by_chunk[chunk_id]
        topic = chunk["topic_id"]
        groups.setdefault(topic, []).append((chunk, score))
        if not require_signal or score != 0:
            # Capture the article giving the topic its rank before choosing which edition to display.
            leaders.setdefault(topic, (chunk, score))
    ordered = [
        sorted(groups[topic], key=lambda item: item[0]["doc_id"] != "hcmus-qcdt-2026")
        for topic in list(leaders)[:limit]
    ]
    return ordered, leaders


def group_results(index, ranked, limit=3, *, require_signal=False):
    groups, _ = _group_ranked_articles(index, ranked, limit, require_signal=require_signal)
    return groups


def source_link(url: str, label: str) -> str:
    if not url:
        return escape(label)
    address = urlsplit(url)
    if address.scheme != "https" or not address.netloc:
        return escape(label)
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(label)}</a>'


def _edition(chunk: dict) -> str:
    return {"hcmus-qcdt-2026": "Quy chế 2026", "hcmus-qcdt-2021": "Quy chế 2021"}.get(
        chunk["doc_id"], chunk["title"]
    )


def _citation(chunk: dict) -> str:
    label = f"Điều {chunk['article']}"
    if chunk["clause"] is not None:
        label += f" · Khoản {chunk['clause']}"
    return escape(label)


def _result_reason(text: str) -> str:
    return ('<details class="read-more result-reason"><summary>Vì sao có kết quả này?</summary>'
            f'<p>{escape(text)}</p></details>')


def _display_score(score: float, places: int) -> str:
    return f"{round(score, places) + 0.0:.{places}f}".replace(".", ",")


def _rank_method(weight: float | None) -> str:
    if weight == 1:
        return "BM25"
    return "SimCSE-VN" if weight is None or weight == 0 else "Hybrid"


def _rank_badge(label: str, score: float | None = None) -> str:
    if score is not None:
        label = f"Điểm {label} {_display_score(score, 3)}"
    return f'<span class="rank-badge">{escape(label)}</span>'


def _score_reason(cosine: float, *, heading: bool = False, keywords: bool = False) -> str:
    value = _display_score(cosine, 2)
    subject = "tiêu đề Điều" if heading else "đoạn trích"
    text = (f"Điểm khớp với câu hỏi: {value}. "
            f"Trên thang từ −1 đến 1, điểm càng cao thì {subject} càng gần nghĩa với câu hỏi.")
    if keywords:
        text += " Trong chế độ từ khóa, thứ tự kết quả dựa trên điểm BM25."
    return _result_reason(text)


def _graduation_reason(chunk: dict, cohort: str | None) -> str:
    reason = (f"Khoản {chunk['clause']} Điều {chunk['article']} của {_edition(chunk)} "
              "liệt kê các điều kiện xét và công nhận tốt nghiệp.")
    if cohort and cohort != ALL:
        context = f"Bạn đã chọn {cohort}. "
        if cohort != "K26 trở đi" and chunk["doc_id"] == "hcmus-qcdt-2026":
            context += "Bản 2026 được mở để đối chiếu với quy chế 2021 theo Điều 27. "
        reason = context + reason
    return _result_reason(reason)


def _edition_body(chunk: dict, index, *, expand_excerpt: bool = False, scores=None,
                  cohort: str | None = None, keywords: bool = False) -> str:
    siblings = [index.chunks[i] for i in index.groups[chunk["article_id"]]] if index is not None else []
    excerpt = render_excerpt(chunk, siblings, expand=expand_excerpt)
    reason = ""
    if expand_excerpt and scores is not None:
        reason = _graduation_reason(chunk, cohort)
    elif scores is not None:
        reason = _score_reason(_chunk_cosine(index, scores, chunk),
                               heading=not excerpt and chunk["clause"] is None, keywords=keywords)
    if not excerpt and chunk["clause"] is None:
        opening = min((c for c in siblings if c["clause"] is not None),
                      key=lambda c: c.get("char_start", 0), default=None)
        if opening:
            opening_reason = (_score_reason(_chunk_cosine(index, scores, opening), keywords=keywords)
                              if scores is not None else "")
            excerpt = (f'<details class="read-more"><summary>Đọc Khoản {escape(str(opening["clause"]))} '
                       f'ở đầu Điều</summary>{render_excerpt(opening, siblings)}{opening_reason}</details>')
    amendments = []
    for change in chunk.get("sua_doi", []):
        note = ("Bảng xếp loại ở điểm b khoản 2 đã được sửa đổi."
                if chunk["doc_id"] == "hcmus-qcdt-2021" and change["so_hieu"] == "91/QĐ-KHTN"
                else escape(change["noi_dung"]))
        link = source_link(change["source_url"], f'Xem QĐ {change["so_hieu"]}')
        amendments.append(f'<aside class="amendment">{note} {link}</aside>')
    decision = source_link(chunk.get("source_url", ""), f'QĐ {chunk["so_hieu"]}')
    issued = date.fromisoformat(chunk["ngay_ban_hanh"])
    return (f'{"".join(amendments)}<div class="passage">{excerpt}</div>{reason}'
            f'<p class="source-line">Văn bản gốc · {decision} · {issued:%d/%m/%Y}</p>')


def render_groups(groups, index=None, *, expand_first: bool = True, question: str = "",
                  keyword_matches: bool = False, full_excerpts=(), scores=None, cohort: str | None = None,
                  rank_leaders=None, rank_method: str = "") -> str:
    def edition_body(chunk):
        return _edition_body(chunk, index, expand_excerpt=chunk.get("chunk_id") in full_excerpts,
                             scores=scores, cohort=cohort, keywords=keyword_matches)

    cards = []
    editions = {}
    for number, chunks in enumerate(groups, 1):
        primary, primary_score = chunks[0]
        editions.setdefault(primary["doc_id"], primary)
        badge = origin = ""
        if rank_leaders is not None:
            leader, rank_score = rank_leaders[primary["topic_id"]]
            if leader["chunk_id"] in full_excerpts:
                badge = _rank_badge("Chọn theo khóa" if cohort and cohort != ALL else "Chọn theo điều kiện tốt nghiệp")
            else:
                badge = _rank_badge(rank_method, rank_score)
            if leader["article_id"] != primary["article_id"]:
                origin = (f'<span class="rank-origin">Xếp theo Điều {escape(str(leader["article"]))} '
                          f'của {escape(_edition(leader))}</span>')
        alternatives = []
        for chunk, score in chunks[1:]:
            editions.setdefault(chunk["doc_id"], chunk)
            other_title = (f'<span class="other-title">{escape(chunk["article_title"])}</span>'
                           if chunk["article_title"] != primary["article_title"] else "")
            match = (' <span class="keyword-match">· Khớp từ khóa</span>'
                     if keyword_matches and primary_score == 0 and score != 0 else "")
            body = edition_body(chunk)
            alternatives.append(
                f'<details class="edition"><summary>{escape(_edition(chunk))} · {_citation(chunk)}'
                f'{match}{other_title}</summary>{body}</details>'
            )
        opened = " open" if number == 1 and expand_first else ""
        body = edition_body(primary)
        cards.append(
            f'<section aria-label="Kết quả {number}" class="topic"><details class="topic-panel"{opened}>'
            f'<summary class="topic-summary"><span class="rank" aria-hidden="true">{number}</span>'
            f'<span class="topic-label">{badge}<span class="reference">{escape(_edition(primary))} · {_citation(primary)}</span>'
            f'<span role="heading" aria-level="2" class="topic-title">{escape(primary["article_title"])}</span>{origin}'
            f'</span></summary><div class="topic-body">{body}'
            f'{"".join(alternatives)}</div></details></section>'
        )
    if not cards:
        return ""
    scope = []
    for chunk in editions.values():
        status = chunk.get("trang_thai")
        scope.append(f'<p><strong>{escape(_edition(chunk))} · {escape(chunk["title"])}</strong><br>'
                     f'{escape(chunk["hieu_luc"])}{(" " + escape(status)) if status else ""}</p>')
    return (f'<div class="reading" lang="vi" data-query="{escape(question, quote=True)}">'
            f'<div class="result-tools"><span role="status">{len(cards)} chủ đề gần nhất</span>'
            f'<details class="scope"><summary>Áp dụng theo khóa tuyển sinh</summary>{"".join(scope)}</details>'
            f'</div>{"".join(cards)}</div>')


def _cohort_groups(index, ranked, edition, *, keywords=False):
    selected = ranked if edition is None else [item for item in ranked if index.by_chunk[item[2]]["doc_id"] == edition]
    groups, leaders = _group_ranked_articles(index, selected, require_signal=keywords)
    if edition == "hcmus-qcdt-2021":
        by_topic = {group[0][0]["topic_id"]: group for group in groups}
        for _, score, chunk_id in ranked:
            chunk = index.by_chunk[chunk_id]
            if chunk["doc_id"] == "hcmus-qcdt-2026" and chunk["topic_id"] in by_topic:
                by_topic[chunk["topic_id"]].append((chunk, score))
    return groups, leaders


def _chunk_cosine(index, scores, chunk):
    return next(scores[1][i] for i in index.groups[chunk["article_id"]]
                if index.chunks[i]["chunk_id"] == chunk["chunk_id"])


def _asks_graduation_conditions(question: str) -> bool:
    # Only redirect broad eligibility questions. A qualifier such as "hồ sơ",
    # "hạng giỏi" or "ai ký" changes the evidence the student needs.
    decomposed = unicodedata.normalize("NFD", question.casefold().replace("đ", "d"))
    words = re.findall(r"[a-z0-9]+", "".join(c for c in decomposed if not unicodedata.combining(c)))
    text = " ".join(words)
    if not re.search(r"\b(tot nghiep|ra truong)\b", text) or not re.search(
        r"\b(dieu kien|yeu cau|can gi|can (?:dap ung|dat)|can nhung gi)\b", text
    ):
        return False
    generic = ("dieu kien|yeu cau|tot nghiep|ra truong|cong nhan|dap ung|sinh vien|"
               "nhung|nhu the nao|the nao|la|gi|nao|muon|can|dat|phai|du|de|thi|"
               "em|minh|toi|duoc|xet|cac|gom|bao gom|xin|cho|hoi|biet|cua|co|vay|a|va|k[0-9]{2}")
    return not re.sub(r"\b(?:" + generic + r")\b", "", text).strip()


def _graduation_citations(index):
    # Resolve the cited list from the document itself. If an edition has
    # competing lists, leave its retrieved articles in their original order.
    found = {}
    for indices in index.groups.values():
        chunk = index.chunks[indices[0]]
        if "tốt nghiệp" not in chunk["article_title"].casefold():
            continue
        for i in indices:
            candidate = index.chunks[i]
            lead, _, listing = " ".join(candidate["text"].casefold().split()).partition(":")
            if listing.lstrip().startswith("a)") and candidate["clause"] is not None and re.fullmatch(
                r"\d+[.)] sinh viên .*tốt nghiệp khi có đủ các điều kiện sau", lead
            ):
                found.setdefault(chunk["doc_id"], []).append(candidate)
    return {items[0]["article_id"]: items[0]["chunk_id"] for items in found.values() if len(items) == 1}


def _prefer_citations(ranked, citations):
    ordered = sorted(ranked, key=lambda item: item[0] not in citations)
    return [(article, score, citations.get(article, original)) for article, score, original in ordered]


def answer(index, question, weight=None, threshold=None, *, edition=None, cohort=None, show_reasons=True):
    question = question.strip()
    if not question:
        return "", "", "Nhập câu hỏi để tra cứu."
    try:
        scores = next(index.score([question]))
    except ValueError as exc:
        if "input exceeds" in str(exc):
            return "", "", "Câu hỏi vượt giới hạn đầu vào. Hãy rút gọn câu hỏi."
        raise
    baseline, _ = index.rank(scores, "bm25")
    citations = _graduation_citations(index) if _asks_graduation_conditions(question) else {}
    if citations:
        baseline = _prefer_citations(baseline, citations)
    keyword_groups, keyword_leaders = _cohort_groups(index, baseline, edition, keywords=True)
    display_scores = scores if show_reasons else None
    if keyword_groups:
        lexical = render_groups(keyword_groups, index, question=question, keyword_matches=True,
                                full_excerpts=citations.values(), scores=display_scores, cohort=cohort,
                                rank_leaders=keyword_leaders if show_reasons else None, rank_method="BM25")
    else:
        lexical = (f'<p class="empty-keywords" data-query="{escape(question, quote=True)}">'
                   'Không có từ khóa giúp xếp hạng các Điều. Hãy thử một cụm trong quy chế, như “hoãn thi”.</p>')
        if weight == 1:
            return lexical, lexical, ""
    ranked, _ = index.rank(scores, "dense" if weight is None else "hybrid", weight=weight or 0)
    if citations:
        ranked = _prefer_citations(ranked, citations)
    groups, leaders = (keyword_groups, keyword_leaders) if weight == 1 else _cohort_groups(index, ranked, edition)
    if not groups:
        return "", lexical, "Chưa có văn bản của khóa đã chọn trong chỉ mục."
    first = leaders[groups[0][0][0]["topic_id"]][0]
    cosine = _chunk_cosine(index, scores, first)
    status = "Đang dùng SimCSE-VN. Chưa cấu hình trọng số Hybrid." if weight is None else ""
    direct = citations.get(first["article_id"]) == first["chunk_id"]
    method = _rank_method(weight)
    if direct:
        status += " Mở Khoản liệt kê điều kiện xét và công nhận tốt nghiệp."
    elif threshold is None:
        status += " Chưa cấu hình ngưỡng cảnh báo."
    elif cosine < threshold:
        status += (f" Độ tin cậy thấp đối với trích đoạn hạng đầu của {method} "
                   f"({_edition(first)}, {_citation(first)}). Hãy đối chiếu văn bản gốc hoặc hỏi Phòng Đào tạo.")
    return (render_groups(groups, index, question=question, keyword_matches=weight == 1,
                          expand_first=direct or threshold is None or cosine >= threshold,
                          full_excerpts=citations.values(), scores=display_scores, cohort=cohort,
                          rank_leaders=leaders if show_reasons else None, rank_method=method), lexical, status.strip())


def _d1_result(index, item, rank, expanded, sources, scores, method):
    article_id, rank_score, chunk_id = item
    chunk = index.by_chunk[chunk_id]
    ref = _citation(chunk) if chunk["article"] is not None else "Đoạn nguồn"
    title = chunk["article_title"] or "Trích đoạn ViRHE4QA"
    heading_only = chunk["article"] is not None and re.fullmatch(
        rf"Điều\s+{chunk['article']}[.)]?\s*{re.escape(' '.join(title.split()))}",
        " ".join(chunk["text"].split()), re.IGNORECASE,
    ) is not None
    source = sources.get(article_id)
    label = "ViRHE4QA"
    citation = "Chưa xác định văn bản cho đoạn này."
    if source:
        label = f'UIT · {escape(source["short"])}'
        archive = source_link(D1_ARCHIVE, "Bộ dữ liệu gốc ViRHE4QA")
        citation = (f'<strong>{escape(source["document"])}</strong><br>{archive}'
                    f' · raw_excel/train.xlsx, dòng {int(source["train_row"])}')
        if source["pages"]:
            first, last = source["pages"]
            span = first if first == last else f"{first}–{last}"
            archived = urlsplit(source["pdf_url"]).hostname == "web.archive.org"
            title_link = "Mở bản lưu PDF UIT" if archived else "Mở PDF UIT"
            link = source_link(f'{source["pdf_url"]}#page={first}', f"{title_link} · trang {span}")
            citation += f"<br>{link}"
            if archived:
                citation += " · Nếu bản lưu chưa mở được, xem dòng trong bộ dữ liệu gốc ở trên."
        else:
            citation += "<br>Chưa đối chiếu được đúng trang PDF của UIT."
    siblings = sorted((index.chunks[i] for i in index.groups[article_id]), key=lambda row: row["char_start"])
    context = ""
    if len(siblings) > 1:
        # Keep original text in each window and omit any overlap with its predecessor.
        pieces = []
        end = -1
        for row in siblings:
            start = row["char_start"]
            if start > end and pieces:
                pieces.append("\n")
            pieces.append(row["text"][max(0, end - start):])
            end = max(end, row["char_end"])
        opened = " open" if heading_only and expanded else ""
        context = (f'<details class="read-more"{opened}><summary>Xem toàn bộ đoạn nguồn</summary>'
                   f'<p class="d1-text">{escape("".join(pieces))}</p></details>')
    excerpt = ('<p class="d1-match">Đoạn khớp là tiêu đề Điều.</p>' if heading_only else
               f'<p class="d1-text">{escape(chunk["text"])}</p>')
    return (f'<section aria-label="Kết quả {rank}" class="topic"><details class="topic-panel"{" open" if expanded else ""}>'
            f'<summary class="topic-summary"><span class="rank" aria-hidden="true">{rank}</span><span class="topic-label">'
            f'{_rank_badge(method, rank_score)} <span class="reference">{label} · {ref}</span>'
            f'<span role="heading" aria-level="2" class="topic-title">{escape(title)}</span>'
            f'</span></summary><div class="topic-body passage">{excerpt}'
            f'{_score_reason(_chunk_cosine(index, scores, chunk), heading=heading_only, keywords=method == "BM25")}'
            f'<p class="source-line d1-citation">{citation}</p>{context}'
            f'<details class="read-more d1-id"><summary>Mã đoạn trích</summary><code>{escape(chunk_id)}</code></details>'
            '</div></details></section>')


def _d1_panel(get_index, weight, threshold):
    import gradio as gr

    sources = _load_d1_sources()
    gr.HTML('<header class="search-header"><p>ViRHE4QA · D1</p><h1>Tra cứu đoạn nguồn</h1>'
            '<p class="intro">Chọn hệ đào tạo hoặc Tra cứu chung để đọc văn bản UIT trong bộ ViRHE4QA. '
            'Bộ dữ liệu có cả văn bản cũ.</p></header>',
            padding=False)
    track = gr.Radio(TRACKS, label="Hệ đào tạo UIT", value=None, elem_id="uit-track")
    with gr.Row(elem_id="d1-question-row", equal_height=False):
        question = gr.Textbox(label="Câu hỏi D1", placeholder="Ví dụ: Điều kiện xét công nhận tốt nghiệp là gì?",
                              lines=1, max_lines=3, scale=5, min_width=160, elem_id="d1-question")
        submit = gr.Button("Tra cứu D1", variant="primary", scale=0, min_width=110, elem_id="d1-submit")
    gr.HTML('<p id="d1-feedback" role="status"></p>', padding=False, container=False)
    result = gr.HTML(elem_id="d1-results", padding=False)

    def search(query: str, selection: str | None) -> str:
        query = query.strip()
        attrs = f'class="reading" data-query="{escape(query, quote=True)}"'
        if selection not in TRACKS:
            return '<p role="status">Chọn hệ đào tạo trước khi tra cứu.</p>'
        attrs += f' data-scope="{escape(selection, quote=True)}"'
        if not query:
            return f'<p {attrs} role="status">Nhập câu hỏi D1 để tra cứu.</p>'
        index = get_index()
        try:
            scores = next(index.score([query]))
        except ValueError as exc:
            if "input exceeds" not in str(exc):
                raise
            return f'<p {attrs} role="status">Câu hỏi vượt giới hạn đầu vào. Hãy rút gọn câu hỏi.</p>'
        ranked, _ = index.rank(scores, "dense" if weight is None else "hybrid", weight=weight or 0)
        if selection != ALL:
            ranked = [item for item in ranked if sources.get(item[0], {}).get("track") == selection]
            if not ranked:
                return f'<p {attrs} role="status">Chưa có văn bản xác định cho hệ đã chọn.</p>'
        if weight == 1:
            ranked = [item for item in ranked if item[1] != 0]
            if not ranked:
                return f'<p {attrs} role="status">Không có từ khóa khớp trong dữ liệu D1.</p>'
        ranked = ranked[:3]
        cosine = _chunk_cosine(index, scores, index.by_chunk[ranked[0][2]])
        confident = threshold is None or cosine >= threshold
        notice = "" if confident else '<p role="status">Độ khớp thấp. Hãy đối chiếu đoạn nguồn.</p>'
        method = _rank_method(weight)
        cards = "".join(_d1_result(index, item, i, confident and i == 1, sources, scores, method)
                        for i, item in enumerate(ranked, 1))
        return f'<div {attrs}>{notice}{cards}</div>'

    gr.on(triggers=[submit.click, question.submit], fn=search, inputs=[question, track], outputs=result,
          api_name="search_d1", trigger_mode="always_last")


def _hcmus_panel(index, weight, threshold):
    import gradio as gr

    gr.HTML('<header class="search-header" lang="vi"><p>Trường Đại học Khoa học Tự nhiên · ĐHQG-HCM</p>'
            '<h1>Tra cứu quy chế đào tạo</h1>'
            '<p class="intro">Chọn khóa tuyển sinh để tìm Điều, Khoản trong hai quy chế đại học năm 2026 và 2021. '
            + source_link("https://ttpc.hcmus.edu.vn/he-thong-van-ban-quan-ly-noi-bo/",
                          "Tra văn bản khác của Trường") + '</p></header>',
            padding=False)
    cohort = gr.Radio(COHORTS, label="Khóa tuyển sinh HCMUS", value=None, elem_id="hcmus-cohort")
    with gr.Row(elem_id="question-row", equal_height=False):
        question = gr.Textbox(label="Câu hỏi", placeholder="Ví dụ: Điểm trung bình tích lũy được tính thế nào?",
                              lines=1, max_lines=3, scale=5, min_width=160, elem_id="question")
        submit = gr.Button("Tra cứu", variant="primary", scale=0, min_width=110, elem_id="search-button")
    gr.HTML(f'<p id="cohort-unavailable" role="status">{EARLY_COHORT_NOTICE}</p>'
            '<p id="search-feedback" role="status"></p>', padding=False, container=False)
    status = gr.Markdown(elem_id="search-status", padding=False)
    with gr.Tabs(elem_id="search-results"):
        with gr.Tab("Kết quả tra cứu", elem_id="ranked-tab"):
            results = gr.HTML(padding=False)
        with gr.Tab("Từ khóa (BM25)", elem_id="keyword-tab"):
            baseline = gr.HTML(padding=False)

    def search(query, selection):
        if selection not in COHORTS:
            return "", "", "Chọn khóa tuyển sinh trước khi tra cứu."
        if selection == "Trước K21":
            return "", "", EARLY_COHORT_NOTICE
        edition = None
        if selection != ALL:
            edition = "hcmus-qcdt-2026" if selection == "K26 trở đi" else "hcmus-qcdt-2021"
        ranked, lexical, notice = answer(index, query, weight, threshold, edition=edition, cohort=selection)
        if edition == "hcmus-qcdt-2021" and ranked:
            notice = (f"{selection} · Quy chế 2021. Theo Điều 27 quy chế 2026, Trường lựa chọn áp dụng "
                      "quy định mới có lợi hơn cho người học. " + notice).strip()
        scope = f'<div data-scope="{escape(selection, quote=True)}">'
        return (scope + ranked + "</div>" if ranked else "", scope + lexical + "</div>" if lexical else "", notice)

    samples = gr.Examples(["Điểm trung bình tích lũy được tính thế nào?", "Khi nào sinh viên được hoãn thi?"],
                          inputs=question, cache_examples=False, api_name=False,
                          label="Câu hỏi gợi ý", elem_id="sample-questions")
    samples.load_input_event.then(search, [question, cohort], [results, baseline, status], api_name=False)
    cohort.change(lambda: ("", "", ""), outputs=[results, baseline, status], queue=False, api_name=False)
    gr.on(triggers=[submit.click, question.submit], fn=search, inputs=[question, cohort],
          outputs=[results, baseline, status], api_name="search", trigger_mode="always_last")


def create_demo(index, weight=None, threshold=None, *, get_d1_index=None):
    import gradio as gr

    # Load the local sheet verbatim. Gradio's component scoping rewrites selectors
    # inside :is() and cannot reach the outer mobile page padding.
    stylesheet = Path(__file__).with_name("search.css").read_text(encoding="utf-8")
    stylesheet += Path(__file__).with_name("selectors.css").read_text(encoding="utf-8")
    if get_d1_index is not None:
        stylesheet += Path(__file__).with_name("d1.css").read_text(encoding="utf-8")
    interaction = Path(__file__).with_name("search.js").read_text(encoding="utf-8")
    settings = json.dumps({"weight": weight, "threshold": threshold}, allow_nan=False)
    head = f'<style>{stylesheet}</style><script id="retrieval-settings" type="application/json">{settings}</script>'
    with gr.Blocks(title="Tra cứu quy chế đào tạo", theme=gr.themes.Base(), head=head,
                   js=interaction) as demo:
        with gr.Column(elem_id="regulations"):
            if get_d1_index is None:
                _hcmus_panel(index, weight, threshold)
            else:
                with gr.Tabs(selected="hcmus", elem_id="source-tabs"):
                    with gr.Tab("HCMUS", id="hcmus"):
                        _hcmus_panel(index, weight, threshold)
                    with gr.Tab("ViRHE4QA (D1)", id="d1", render_children=True):
                        _d1_panel(get_d1_index, weight, threshold)
    return demo


def _load_d1_chunks(path, count_tokens):
    required = {"chunk_id", "article_id", "article", "article_title", "clause", "text", "char_start", "char_end"}
    chunks = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict) or row.get("doc_id") != "virhe4qa" or not required.issubset(row):
                raise ValueError("Expected ViRHE4QA source records or chunks")
            if row["chunk_id"] == f"{row['article_id']}:source":
                chunks.extend(article_chunks(row, count_tokens))
            else:
                chunks.append(row)
    if not chunks:
        raise ValueError("Empty ViRHE4QA corpus")
    return chunks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--d1-corpus", type=Path, help="ViRHE4QA source or chunk JSONL for the D1 tab")
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--weight", type=float)
    parser.add_argument("--threshold", type=float)
    args = parser.parse_args()
    for value, low, name in ((args.weight, 0, "weight"), (args.threshold, -1, "threshold")):
        if value is not None and not low <= value <= 1:
            parser.error(f"{name} must be in [{low}, 1]")
    with args.corpus.open(encoding="utf-8") as stream:
        chunks = [json.loads(line) for line in stream if line.strip()]
    if len({chunk["article_id"] for chunk in chunks}) != 51 or len({chunk["topic_id"] for chunk in chunks}) != 26:
        parser.error("Expected the complete HCMUS corpus with 51 articles and 26 topics")

    d1_path = args.d1_corpus or next((path for path in (
        Path("outputs/d1-test/inputs/corpus.jsonl"), Path("data/processed/d1/dense/corpus.jsonl"),
        Path("data/processed/d1/corpus.jsonl")
    ) if path.is_file()), None)

    import torch

    torch.set_num_threads(4)
    verify_snapshot(args.model_path)
    encoder = SimCSEEncoder(str(args.model_path), "cpu")
    try:
        d1_chunks = _load_d1_chunks(d1_path, encoder.count_tokens) if d1_path is not None else []
    except (OSError, ValueError) as exc:
        parser.error(f"Cannot load D1 corpus {d1_path}: {exc}")
    index = RetrievalIndex(chunks, encoder)
    with ThreadPoolExecutor(max_workers=1) as worker:
        # Serve HCMUS while the second corpus is being encoded.
        d1 = worker.submit(RetrievalIndex, d1_chunks, encoder) if d1_chunks else None
        demo = create_demo(index, args.weight, args.threshold, get_d1_index=d1.result if d1 else None)
        demo.launch(server_name="127.0.0.1", share=False)


if __name__ == "__main__":
    main()
