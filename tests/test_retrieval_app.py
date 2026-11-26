import sys
from pathlib import Path

import numpy as np
import pytest

from apps.app import answer, create_demo
from simcse_lab.retrieval.hcmus import prepare_corpus, regulation_articles
from simcse_lab.retrieval.search import RetrievalIndex


@pytest.mark.parametrize("existing", ["latency.json", "demo-check.json"])
def test_benchmark_preserves_previous_outputs(existing, tmp_path, monkeypatch):
    from experiments.application import benchmark_cpu

    path = tmp_path / existing
    path.write_bytes(b"previous run")
    monkeypatch.setattr(sys, "argv", ["benchmark_cpu", "--demo", "--output", str(tmp_path / "latency.json")])
    with pytest.raises(SystemExit) as error:
        benchmark_cpu.main()
    assert error.value.code == 2
    assert path.read_bytes() == b"previous run"


class FixtureEncoder:
    def encode(self, texts, batch_size):
        return np.broadcast_to([1.0, 0.0], (len(texts), 2))


def fixture_index():
    pytest.importorskip("rank_bm25")
    chunks = []
    for article_id, doc_id, topic in [
        ("a", "hcmus-qcdt-2021", "T1"),
        ("b", "hcmus-qcdt-2026", "T1"),
        ("c", "hcmus-qcdt-2026", "T1"),
        ("d", "hcmus-qcdt-2021", "T2"),
    ]:
        for n in range(2 if article_id == "a" else 1):
            chunks.append(dict(article_id=article_id, chunk_id=f"{article_id}{n}", doc_id=doc_id,
                               article=len(chunks) + 1, article_title=article_id, clause=1,
                               topic_id=topic, title=doc_id, so_hieu=doc_id, ngay_ban_hanh="2026-09-29",
                               hieu_luc="Dữ liệu kiểm thử", text=article_id + " <fixture>",
                               nguyen_van=doc_id.endswith("2021")))
    return RetrievalIndex(chunks, FixtureEncoder(), tokenize=str)


def test_fusion_uses_all_articles_and_article_minmax_for_excerpts():
    index = fixture_index()
    scores = ([10., -6., 4., 5., 5.], [-0.1, 0.95, 0.8, 0.5, 0.5])
    ranked, cosine = index.rank(scores, "hybrid", weight=0.5, k=1)
    assert ranked == [["a", 1.0, "a0"]]
    assert cosine == -0.1
    assert index.rank(scores, "hybrid", weight=0) == index.rank(scores, "dense")
    assert index.rank(scores, "hybrid", weight=1) == index.rank(scores, "bm25")
    below_min = ([10., 2., 4., 5., 5.], scores[1])
    assert index.rank(below_min, "hybrid", weight=0.5, k=1) == ([["a", 1.0, "a1"]], 0.95)
    tied, _ = index.rank(([0.] * 5, [0.5] * 5), "hybrid")
    assert tied == [[article, 0.0, f"{article}0"] for article in "abcd"]


def test_bm25_without_query_embedding(monkeypatch):
    index = fixture_index()
    monkeypatch.setattr(index.encoder, "encode", lambda *_: pytest.fail("BM25 encoded the question"))
    ranked = index.rank_bm25("a")
    cosine = [-0.1, 0.95, 0.8, 0.5, 0.5]
    assert ranked[0][2] == "a0"
    full_ranked, confidence = index.rank((index._bm25_scores("a"), cosine), "bm25")
    assert ranked == full_ranked
    assert confidence == -0.1
    assert index.rank((index._bm25_scores("a"), cosine), "dense")[0][0][2] == "a1"


def test_app_group_order_plain_text_and_warning():
    index = fixture_index()
    assert "Nhập câu hỏi" in answer(index, " ")[2]
    rendered, baseline, status = answer(index, "fixture")
    assert "Chưa cấu hình ngưỡng" in status
    assert rendered.count("<section ") == 2
    assert rendered.index("Điều 3") < rendered.index("Điều 1")
    assert "Điều 4" in rendered and "bản chép từ bản scan" in rendered
    assert "do ChatGPT chép, nhóm đã hiệu đính" in rendered
    assert "&lt;fixture&gt;" in baseline
    index.vectors = index.vectors.copy()
    index.vectors[:, 0] = 0
    results, _, status = answer(index, "fixture", weight=0.5, threshold=0.8)
    assert results and "Độ tin cậy thấp đối với trích đoạn hạng đầu của Hybrid" in status
    assert "trích đoạn hạng đầu của SimCSE-VN" in answer(index, "fixture", threshold=0.8)[2]


def test_regulation_ignores_signing_decision_and_preserves_offsets():
    signing = "\n".join(f"**Điều {i}.** Quyết định" for i in range(1, 4))
    regulation = "\n".join(f"## Điều {i}. Tên điều\n1. Nội dung" for i in range(1, 28))
    text = signing + "\n# Chương I\n" + regulation + "\nNơi nhận:\nLưu."
    articles = list(regulation_articles(text, "hcmus-qcdt-2026", 27))
    assert articles[0]["text"].startswith("## Điều 1.")
    assert text[articles[-1]["char_start"]:].startswith(articles[-1]["text"])
    assert "Nơi nhận" not in articles[-1]["text"]


def test_source_2021_matches_mapping_and_spans():
    root = Path(__file__).resolve().parents[1]
    selected = {"hcmus-qcdt-2021"}
    chunks = prepare_corpus(root, lambda text: len(text.split()), selected)
    assert len({c["article_id"] for c in chunks}) == 24
    assert len({c["chunk_id"] for c in chunks}) == len(chunks)
    assert chunks == prepare_corpus(root, lambda text: len(text.split()), selected)
    assert all("Nơi nhận" not in chunk["text"] for chunk in chunks)
    assert all("thực tập tốt nghiệp/dự án tốt nghiệp" in c["article_title"] for c in chunks if c["article"] == 10)
    assert all(bool(c["sua_doi"]) == (c["article"] == 15) for c in chunks)
    source = (root / "data/d2/Quy_che_dao_tao_2021_QD1175.txt").read_bytes().decode("utf-8")
    assert all(source[c["char_start"]:c["char_end"]] == c["text"] for c in chunks)


def test_hcmus_output_is_normalized_and_git_ignored(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root / "experiments/external_dataset"))
    from run_retrieval import checked_corpus_output

    assert checked_corpus_output(root, Path("data/../outputs/hcmus-check")) == root / "outputs/hcmus-check"
    assert checked_corpus_output(root, root / "data/processed/hcmus-check") == root / "data/processed/hcmus-check"
    with pytest.raises(ValueError, match="Git-ignored"):
        checked_corpus_output(root, Path("data/d2/hcmus-check"))
    with pytest.raises(ValueError, match="inside"):
        checked_corpus_output(root, Path("../outside-hcmus-check"))


def test_gradio_local_api():
    pytest.importorskip("gradio")
    from gradio_client import Client

    pytest.importorskip("rank_bm25")
    root = Path(__file__).resolve().parents[1]
    corpus = prepare_corpus(root, lambda text: len(text.split()), {"hcmus-qcdt-2021"})
    selected = [next(chunk for chunk in corpus if chunk["article"] == number) for number in (10, 15)]
    newer = dict(selected[1], doc_id="hcmus-qcdt-2026", article_id="hcmus-qcdt-2026:dieu-16",
                 chunk_id="fixture-2026", article=16, text="Văn bản kiểm thử", nguyen_van=False, sua_doi=[])
    index = RetrievalIndex([*selected, newer], FixtureEncoder(), tokenize=str)
    demo = create_demo(index)
    try:
        _, url, _ = demo.launch(server_name="127.0.0.1", share=False, prevent_thread_lock=True, quiet=True)
        client = Client(url, verbose=False)
        results, baseline, status = client.predict("fixture", api_name="/search")
        assert "bản chép từ bản scan" in results and baseline
        for html in (results, baseline):
            assert "thực tập tốt nghiệp/dự án tốt nghiệp" in html
            assert html.count("Sửa đổi theo QĐ 91/QĐ-KHTN") == 1
            assert "https://drive.google.com/file/d/1jNYskZmwL866hip7yL9AHlBuLOb9y1xJ/view" in html
            assert "Bị thay thế" in html
        assert "Chưa cấu hình ngưỡng" in status
        assert "Nhập câu hỏi" in client.predict("", api_name="/search")[2]
    finally:
        demo.close()
