"""Local HCMUS regulation search demo."""

import argparse
import json
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

from simcse_lab.model.encoders import SimCSEEncoder, verify_snapshot
from simcse_lab.regulation_excerpts import render_excerpt
from simcse_lab.retrieval.search import RetrievalIndex


def group_results(index, ranked, limit=3, *, require_signal=False):
    groups = {}
    eligible = {}
    for _, score, chunk_id in ranked:
        chunk = index.by_chunk[chunk_id]
        topic = chunk["topic_id"]
        groups.setdefault(topic, []).append((chunk, score))
        if not require_signal or score != 0:
            eligible.setdefault(topic, None)
    return [
        sorted(groups[topic], key=lambda item: item[0]["doc_id"] != "hcmus-qcdt-2026")
        for topic in list(eligible)[:limit]
    ]


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


def _edition_body(chunk: dict, index) -> str:
    siblings = [index.chunks[i] for i in index.groups[chunk["article_id"]]] if index is not None else []
    excerpt = render_excerpt(chunk, siblings)
    if not excerpt and chunk["clause"] is None:
        opening = min((c for c in siblings if c["clause"] is not None),
                      key=lambda c: c.get("char_start", 0), default=None)
        if opening:
            excerpt = (f'<details class="read-more"><summary>Đọc Khoản {escape(str(opening["clause"]))} '
                       f'ở đầu Điều</summary>{render_excerpt(opening, siblings)}</details>')
    amendments = []
    for change in chunk.get("sua_doi", []):
        note = ("Bảng xếp loại ở điểm b khoản 2 đã được sửa đổi."
                if chunk["doc_id"] == "hcmus-qcdt-2021" and change["so_hieu"] == "91/QĐ-KHTN"
                else escape(change["noi_dung"]))
        link = source_link(change["source_url"], f'Xem QĐ {change["so_hieu"]}')
        amendments.append(f'<aside class="amendment">{note} {link}</aside>')
    decision = source_link(chunk.get("source_url", ""), f'QĐ {chunk["so_hieu"]}')
    issued = date.fromisoformat(chunk["ngay_ban_hanh"])
    return (f'{"".join(amendments)}<div class="passage">{excerpt}</div>'
            f'<p class="source-line">Văn bản gốc · {decision} · {issued:%d/%m/%Y}</p>')


def render_groups(groups, index=None, *, expand_first: bool = True, question: str = "",
                  keyword_matches: bool = False) -> str:
    cards = []
    editions = {}
    for number, chunks in enumerate(groups, 1):
        primary, primary_score = chunks[0]
        editions.setdefault(primary["doc_id"], primary)
        alternatives = []
        for chunk, score in chunks[1:]:
            editions.setdefault(chunk["doc_id"], chunk)
            other_title = (f'<span class="other-title">{escape(chunk["article_title"])}</span>'
                           if chunk["article_title"] != primary["article_title"] else "")
            match = (' <span class="keyword-match">· Khớp từ khóa</span>'
                     if keyword_matches and primary_score == 0 and score != 0 else "")
            alternatives.append(
                f'<details class="edition"><summary>{escape(_edition(chunk))} · {_citation(chunk)}'
                f'{match}{other_title}</summary>{_edition_body(chunk, index)}</details>'
            )
        opened = " open" if number == 1 and expand_first else ""
        cards.append(
            f'<section aria-label="Kết quả {number}" class="topic"><details class="topic-panel"{opened}>'
            f'<summary class="topic-summary"><span class="rank" aria-hidden="true">{number}</span>'
            f'<span class="topic-label"><span class="reference">{escape(_edition(primary))} · {_citation(primary)}</span>'
            f'<span role="heading" aria-level="2" class="topic-title">{escape(primary["article_title"])}</span>'
            f'</span></summary><div class="topic-body">{_edition_body(primary, index)}'
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


def answer(index, question, weight=None, threshold=None):
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
    keyword_groups = group_results(index, baseline, require_signal=True)
    if keyword_groups:
        lexical = render_groups(keyword_groups, index, question=question, keyword_matches=True)
    else:
        lexical = (f'<p class="empty-keywords" data-query="{escape(question, quote=True)}">'
                   'Không có từ khóa giúp xếp hạng các Điều. Hãy thử một cụm trong quy chế, như “hoãn thi”.</p>')
        if weight == 1:
            return lexical, lexical, ""
    ranked, cosine = index.rank(scores, "dense" if weight is None else "hybrid", weight=weight or 0)
    status = "Đang dùng SimCSE-VN. Chưa cấu hình trọng số Hybrid." if weight is None else ""
    if threshold is None:
        status += " Chưa cấu hình ngưỡng cảnh báo."
    elif cosine < threshold:
        method = "SimCSE-VN" if weight is None else "Hybrid"
        first = index.by_chunk[ranked[0][2]]
        status += (f" Độ tin cậy thấp đối với trích đoạn hạng đầu của {method} "
                   f"({_edition(first)}, {_citation(first)}). Hãy đối chiếu văn bản gốc hoặc hỏi Phòng Đào tạo.")
    groups = keyword_groups if weight == 1 else group_results(index, ranked)
    return (render_groups(groups, index, question=question, keyword_matches=weight == 1,
                          expand_first=threshold is None or cosine >= threshold), lexical, status.strip())


def create_demo(index, weight=None, threshold=None):
    import gradio as gr

    # Load the local sheet verbatim. Gradio's component scoping rewrites selectors
    # inside :is() and cannot reach the outer mobile page padding.
    stylesheet = Path(__file__).with_name("search.css").read_text(encoding="utf-8")
    interaction = Path(__file__).with_name("search.js").read_text(encoding="utf-8")
    with gr.Blocks(title="Tra cứu quy chế HCMUS", theme=gr.themes.Base(), head=f"<style>{stylesheet}</style>",
                   js=interaction) as demo:
        with gr.Column(elem_id="regulations"):
            gr.HTML('<header class="search-header" lang="vi"><p>Trường Đại học Khoa học Tự nhiên · ĐHQG-HCM</p>'
                    '<h1>Tra cứu quy chế đào tạo</h1>'
                    '<p class="intro">Tìm Điều, Khoản trong hai quy chế đại học năm 2026 và 2021. '
                    + source_link("https://ttpc.hcmus.edu.vn/he-thong-van-ban-quan-ly-noi-bo/",
                                  "Tra văn bản khác của Trường") + '</p></header>',
                    padding=False)
            with gr.Row(elem_id="question-row", equal_height=False):
                question = gr.Textbox(label="Câu hỏi", placeholder="Ví dụ: Điểm trung bình tích lũy được tính thế nào?",
                                      lines=1, max_lines=3, scale=5, min_width=160, elem_id="question")
                submit = gr.Button("Tra cứu", variant="primary", scale=0, min_width=110, elem_id="search-button")
            gr.HTML('<p id="search-feedback" role="status"></p>', padding=False, container=False)
            status = gr.Markdown(elem_id="search-status", padding=False)
            with gr.Tabs(elem_id="search-results"):
                with gr.Tab("Kết quả tra cứu", elem_id="ranked-tab"):
                    results = gr.HTML(padding=False)
                with gr.Tab("Từ khóa (BM25)", elem_id="keyword-tab"):
                    baseline = gr.HTML(padding=False)

            def search(query):
                return answer(index, query, weight, threshold)

            gr.Examples(["Điểm trung bình tích lũy được tính thế nào?", "Khi nào sinh viên được hoãn thi?"],
                        inputs=question, outputs=[results, baseline, status], fn=search, run_on_click=True,
                        cache_examples=False, api_name=False, label="Câu hỏi gợi ý", elem_id="sample-questions")

        gr.on(triggers=[submit.click, question.submit], fn=search, inputs=question,
              outputs=[results, baseline, status], api_name="search", trigger_mode="always_last")
    return demo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
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

    import torch

    torch.set_num_threads(4)
    verify_snapshot(args.model_path)
    index = RetrievalIndex(chunks, SimCSEEncoder(str(args.model_path), "cpu"))
    create_demo(index, args.weight, args.threshold).launch(server_name="127.0.0.1", share=False)


if __name__ == "__main__":
    main()
