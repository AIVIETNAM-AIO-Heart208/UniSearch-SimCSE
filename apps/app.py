"""Local HCMUS regulation search demo."""

import argparse
import json
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

from simcse_lab.model.encoders import SimCSEEncoder, verify_snapshot
from simcse_lab.retrieval.search import RetrievalIndex


def group_results(index, ranked, limit=3):
    groups = {}
    for _, score, chunk_id in ranked:
        chunk = index.by_chunk[chunk_id]
        groups.setdefault(chunk["topic_id"], []).append((chunk, score))
    return [
        sorted(chunks, key=lambda item: item[0]["doc_id"] != "hcmus-qcdt-2026")
        for chunks in list(groups.values())[:limit]
    ]


def source_link(url, label):
    if urlsplit(url).scheme != "https":
        return ""
    return f'<p><a href="{escape(url, quote=True)}">{escape(label)}</a></p>'


def render_groups(groups):
    cards = []
    for number, chunks in enumerate(groups, 1):
        rows = []
        for chunk, score in chunks:
            heading = f"Điều {chunk['article']} — {chunk['article_title']}"
            if chunk["clause"] is not None:
                heading += f" · Khoản {chunk['clause']}"
            source = f"{chunk['title']} · {chunk['so_hieu']} · {chunk['ngay_ban_hanh']}"
            if not chunk["nguyen_van"]:
                source += " · bản chép từ bản scan"
            reference = source_link(chunk.get("source_url", ""), "Văn bản nguồn")
            amendments = "".join(
                f'<p><strong>Sửa đổi theo QĐ {escape(change["so_hieu"])}</strong> '
                f'({escape(change["ngay_ban_hanh"])}). {escape(change["noi_dung"])}</p>'
                + source_link(change["source_url"], "Văn bản sửa đổi")
                for change in chunk.get("sua_doi", [])
            )
            rows.append(
                f'<h4>{escape(heading)}</h4><p>{escape(source)} · Điểm {score:.3f}</p>'
                f'<p>{escape(chunk["hieu_luc"])}</p>'
                f'<p>{escape(chunk.get("trang_thai", ""))}</p>'
                f'{amendments}'
                f'<p style="white-space: pre-wrap">{escape(chunk["text"])}</p>'
                f'{reference}'
            )
        cards.append(f'<section aria-label="Kết quả {number}">{"".join(rows)}</section>')
    return "<hr>".join(cards)


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
    ranked, cosine = index.rank(scores, "dense" if weight is None else "hybrid", weight=weight or 0)
    baseline, _ = index.rank(scores, "bm25")
    status = "Đang dùng SimCSE-VN. Chưa cấu hình trọng số Hybrid." if weight is None else ""
    if threshold is None:
        status += " Chưa cấu hình ngưỡng cảnh báo."
    elif cosine < threshold:
        status += " Độ tin cậy thấp. Hãy đối chiếu văn bản hoặc liên hệ phòng đào tạo."
    return render_groups(group_results(index, ranked)), render_groups(group_results(index, baseline)), status.strip()


def create_demo(index, weight=None, threshold=None):
    import gradio as gr

    with gr.Blocks(title="Tra cứu quy chế HCMUS", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Tra cứu quy chế đào tạo HCMUS")
        gr.Markdown("Kết quả để tham khảo, hãy đối chiếu văn bản gốc.")
        question = gr.Textbox(label="Câu hỏi", placeholder="Nhập câu hỏi về quy chế đào tạo")
        submit = gr.Button("Tra cứu", variant="primary")
        status = gr.Markdown()
        with gr.Tabs():
            with gr.Tab("Kết quả tra cứu"):
                results = gr.HTML()
            with gr.Tab("Đối chiếu BM25"):
                baseline = gr.HTML()

        def search(query):
            return answer(index, query, weight, threshold)

        submit.click(search, question, [results, baseline, status], api_name="search")
        question.submit(search, question, [results, baseline, status], api_name=False)
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
