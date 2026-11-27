"""Measure single-query CPU retrieval on the verified HCMUS corpus."""

import argparse
import hashlib
import json
import os
import platform
from contextlib import ExitStack
from pathlib import Path
from time import perf_counter
from unittest.mock import patch

import numpy as np
import torch

from simcse_lab.model import encoders
from simcse_lab.retrieval.search import RetrievalIndex, maxp


QUERIES = (
    "Đào tạo từ xa lưu bản ghi buổi bảo vệ đồ án như thế nào?",
    "Sinh viên trình độ năm thứ ba muốn chuyển trường thì cần xem điều nào?",
    "Khi nghỉ học để tham gia nghĩa vụ quân sự, kết quả đã tích lũy được bảo lưu không?",
    "Chương trình đào tạo thường xuyên văn bằng thứ hai có thời gian chuẩn bao lâu?",
    "Đăng ký cùng lúc hai chương trình, học kỳ hè được tối đa bao nhiêu tín chỉ?",
    "Mấy giờ thủy triều lên ở Vũng Tàu ngày mai?",
)
WEIGHT = 0.6
THRESHOLD = 0.6201629042625427
METHODS = ("bm25", "dense", "hybrid")


def measure(index, question, method):
    segment_seconds = 0.0
    segment = encoders.segment

    def timed_segment(text):
        nonlocal segment_seconds
        start = perf_counter()
        result = segment(text)
        segment_seconds += perf_counter() - start
        return result

    index.encoder.token_ids.cache_clear()
    with patch.object(encoders, "segment", timed_segment), patch.object(index, "tokenize", timed_segment):
        start = perf_counter()
        encode_seconds = 0.0
        if method == "bm25":
            index.rank_bm25(question)
        else:
            vector = index.encoder.encode([question], index.batch_size)[0]
            encode_seconds = perf_counter() - start - segment_seconds
            cosines = index.vectors @ vector
            if method == "dense":
                maxp(index.chunks, cosines, k=len(index.groups))
            else:
                dense = np.clip(cosines, -1, 1).astype(float).tolist()
                index.rank((index._bm25_scores(question), dense), "hybrid", weight=WEIGHT)
        total = perf_counter() - start
    return {
        "total_ms": total * 1000,
        "segment_ms": segment_seconds * 1000,
        "encode_ms": encode_seconds * 1000,
        "search_ms": (total - segment_seconds - encode_seconds) * 1000,
    }


def check_demo(index):
    from gradio_client import Client
    from apps.app import create_demo

    demo = create_demo(index, WEIGHT, THRESHOLD)
    try:
        _, url, _ = demo.launch(server_name="127.0.0.1", share=False, prevent_thread_lock=True, quiet=True)
        client = Client(url, verbose=False)
        rows = []
        for question in QUERIES:
            results, baseline, warning = client.predict(question, "Tra cứu chung", api_name="/search")
            for html in (results, baseline):
                assert html.count('<section aria-label=') == 3
                assert 'Khoản' in html and 'Áp dụng theo khóa tuyển sinh' in html
                assert 'ChatGPT' not in html and 'Điểm xếp hạng' not in html
                assert '3087' in html and '2026' in html
                assert all(
                    card.index("3087") < card.index("1175")
                    for card in html.split("<section")[1:] if "3087" in card and "1175" in card
                )
            rows.append({"question": question, "warning": warning,
                         "hybrid_topics": results.count('<section aria-label='),
                         "bm25_topics": baseline.count('<section aria-label=')})
        assert any(row["warning"] for row in rows)
        return rows
    finally:
        demo.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=Path("data/processed/d2/corpus.jsonl"))
    parser.add_argument("--model-path", type=Path, default=Path("outputs/d1-model"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    demo_path = args.output.with_name("demo-check.json")
    if args.output.exists() or (args.demo and (demo_path.exists() or args.output == demo_path)):
        parser.error("Choose new, distinct output files for the measurements and demo check")
    data = args.corpus.read_bytes()
    chunks = [json.loads(line) for line in data.splitlines() if line.strip()]
    size = (len({c["article_id"] for c in chunks}), len({c["topic_id"] for c in chunks}))
    if size != (51, 26):
        parser.error("Expected the full D2 corpus with 51 articles and 26 topics")
    torch.set_num_threads(4)
    encoders.verify_snapshot(args.model_path)
    encoder = encoders.SimCSEEncoder(str(args.model_path), "cpu")
    start = perf_counter()
    index = RetrievalIndex(chunks, encoder)
    build_ms = (perf_counter() - start) * 1000
    for question in QUERIES:
        for method in METHODS:
            measure(index, question, method)
    samples = {method: [] for method in METHODS}
    for repeat in range(10):
        order = METHODS[repeat % len(METHODS):] + METHODS[:repeat % len(METHODS)]
        for question in QUERIES:
            for method in order:
                samples[method].append({"question": question, "repeat": repeat + 1, **measure(index, question, method)})
    percentiles = {
        method: {
            field: np.percentile([row[field] for row in rows], [50, 95]).tolist()
            for field in ("total_ms", "segment_ms", "encode_ms", "search_ms")
        }
        for method, rows in samples.items()
    }
    result = {
        "platform": platform.platform(), "cpu": os.environ.get("PROCESSOR_IDENTIFIER") or platform.processor(),
        "logical_cpus": os.cpu_count(), "torch": torch.__version__, "torch_threads": torch.get_num_threads(),
        "checkpoint": encoders.REVISION, "corpus_sha256": hashlib.sha256(data).hexdigest(),
        "articles": size[0], "topics": size[1], "chunks": len(chunks), "weight": WEIGHT, "threshold": THRESHOLD,
        "build_ms": build_ms, "percentiles_p50_p95_ms": percentiles, "samples": samples,
    }
    artifacts = {args.output: result}
    if args.demo:
        artifacts[demo_path] = check_demo(index)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ExitStack() as rollback:
        for path, content in artifacts.items():
            with path.open("x", encoding="utf-8") as stream:
                rollback.callback(path.unlink)
                json.dump(content, stream, ensure_ascii=False, indent=2, allow_nan=False)
                stream.write("\n")
        rollback.pop_all()


if __name__ == "__main__":
    main()
