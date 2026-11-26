import sys
from html.parser import HTMLParser
from pathlib import Path

import numpy as np
import pytest

from apps.app import answer, create_demo, render_groups
from simcse_lab.retrieval.hcmus import prepare_corpus, regulation_articles
from simcse_lab.retrieval.search import RetrievalIndex


class PassageHTML(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags, self.words, self.rows = [], [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == "tr":
            self.rows.append([])

    def handle_data(self, value):
        self.words.append(value)
        if self.lasttag in {"th", "td"} and self.rows:
            self.rows[-1].append(value)


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
    rendered, baseline, status = answer(index, "a <fixture>")
    assert "Chưa cấu hình ngưỡng" in status
    assert rendered.count("<section ") == 2
    assert rendered.index("Điều 3") < rendered.index("Điều 1")
    assert "Điều 4" in rendered and "ChatGPT" not in rendered
    assert "bản chép từ bản scan" not in rendered and "Điểm xếp hạng" not in rendered
    assert "&lt;fixture&gt;" in baseline
    index.vectors = index.vectors.copy()
    index.vectors[:, 0] = 0
    results, lexical, status = answer(index, "a <fixture>", weight=0.5, threshold=0.8)
    assert results and "Độ tin cậy thấp đối với trích đoạn hạng đầu của Hybrid" in status
    assert 'class="topic-panel" open' not in results and 'class="topic-panel" open' in lexical
    assert "trích đoạn hạng đầu của SimCSE-VN" in answer(index, "fixture", threshold=0.8)[2]


def test_no_keyword_signal_does_not_produce_a_ranking():
    index = fixture_index()
    question = 'unknown "term"'
    ranked, lexical, _ = answer(index, question, weight=0.6, threshold=0.7)
    assert 'class="topic-panel"' in ranked
    assert 'class="empty-keywords"' in lexical and 'class="topic-panel"' not in lexical
    assert 'data-query="unknown &quot;term&quot;"' in lexical
    assert 'data-query="unknown &quot;term&quot;"' in ranked
    assert answer(index, question, weight=1, threshold=0.7) == (lexical, lexical, "")


def test_keyword_tab_only_lists_topics_with_evidence_and_keeps_the_other_edition():
    index = fixture_index()
    _, lexical, _ = answer(index, "a", weight=0.6)
    assert lexical.count("<section ") == 1
    assert "Quy chế 2026" in lexical and "Quy chế 2021" in lexical
    assert "Khớp từ khóa" in lexical
    assert "Điều 5" not in lexical


@pytest.mark.parametrize(("year", "source", "expected"), [
    (
        "2026",
        "### Điều 7. Tổ chức đăng ký học tập\n\n"
        "3. Gồm học phần học\n\n\n<!-- Trang 8/21 -->\n\nlại và học phần đã đạt. <trích đoạn>\n\n"
        "<!-- Trang 9/21 -->\n\n  a) Mức **tối đa** được quy định.\n\n<!-- Trang 10/21 -->",
        "Điều 7. Tổ chức đăng ký học tập\n\n"
        "3. Gồm học phần học lại và học phần đã đạt. <trích đoạn>\n  a) Mức tối đa được quy định.",
    ),
    (
        "2021",
        "3. Hạng tốt nghiệp của\r\n\f           15\r\n\r\nsinh viên có thể bị giảm đi một mức."
        "\r\n\f           16\r\n\r\n      a) Xét theo Điều 15.\r\n\f           17",
        "3. Hạng tốt nghiệp của sinh viên có thể bị giảm đi một mức.\n      a) Xét theo Điều 15.",
    ),
])
def test_app_removes_page_markers_from_displayed_excerpt(year, source, expected):
    chunk = next(chunk for chunk in fixture_index().by_chunk.values() if chunk["doc_id"].endswith(year))
    chunk["text"] = source
    rendered = render_groups([[(chunk, 1.0)]])
    visible = " ".join(" ".join(PassageHTML(rendered).words).split())
    assert "Trang " not in visible and "\f" not in visible and "**" not in visible
    assert " ".join(expected.split()) in visible
    assert chunk["text"] == source


def test_markdown_table_crossing_search_windows():
    chunk = next(c for c in fixture_index().chunks if c["doc_id"].endswith("2026"))
    table = ("| Điểm trung bình | Xếp loại/hạng |\n|---|---|\n"
             "| **a. Loại đạt** | |\n| Từ 9,0 đến 10 | Xuất sắc |\n"
             "| Từ 4,0 đến cận 5,0 | Yếu |")
    text = "3. Nội dung.\n\n" + table
    split = text.index("Xuất sắc")
    windows = [dict(chunk, chunk_id=f"c{i}", clause=3, clause_id="b:khoan-3",
                    char_start=start, char_end=end, text=text[start:end])
               for i, (start, end) in enumerate(((0, split), (text.index("|---"), len(text))))]
    index = RetrievalIndex(windows, FixtureEncoder(), tokenize=str)
    for window in windows:
        html = PassageHTML(render_groups([[(window, 0.8)]], index))
        assert html.tags.count("table") == 1 and html.tags.count("thead") == 1
        assert ["Từ 9,0 đến 10", "Xuất sắc"] in html.rows
        assert ["Từ 4,0 đến cận 5,0", "Yếu"] in html.rows
        assert "|---" not in " ".join(html.words)


def test_2021_grade_tables_and_formula_follow_printed_rows():
    root = Path(__file__).resolve().parents[1]
    corpus = prepare_corpus(root, lambda s: len(s.split()), {"hcmus-qcdt-2021"})
    for article, clause in ((15, 2), (11, 1), (6, 7)):
        chunk = next(c for c in corpus if c["article"] == article and c["clause"] == clause)
        shown = PassageHTML(render_groups([[(chunk, 0.5)]]))
        if article == 15:
            assert shown.tags.count("math") == 1 and shown.tags.count("table") == 2
            assert sum("đã sửa đổi theo QĐ 91/QĐ-KHTN" in word for word in shown.words) == 2
            assert ["Từ 5 đến cận 7", "Trung bình"] in shown.rows
            assert ["Từ 6 đến cận 7", "Trung bình khá"] in shown.rows
            assert shown.rows.count(["Dưới 4", "Kém"]) == 2
        elif article == 11:
            assert ["8,0 đến cận 9,0", "3,5", "A"] in shown.rows
            assert ["<3,0", "0,0", "F"] in shown.rows
        else:
            assert shown.tags.count("table") == 2
            assert any("18g00" in row[-1] for row in shown.rows)


def test_title_match_offers_opening_clause_separately():
    base = fixture_index().chunks[0]
    heading = dict(base, article_title="Hoãn thi", text="Điều 1. Hoãn thi", clause=None, char_start=0,
                   char_end=14, chunk_id="title")
    opening = dict(base, text="1. Nội dung của Khoản một.", clause=1, char_start=20, char_end=46)
    index = RetrievalIndex([opening, heading], FixtureEncoder(), tokenize=str)
    html = render_groups([[(heading, 1.)]], index)
    assert '<span class="reference">Quy chế 2021 · Điều 1</span>' in html
    assert "Đọc Khoản 1 ở đầu Điều</summary><p>1. Nội dung của Khoản một." in html


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
        results, baseline, status = client.predict("thực tập tốt nghiệp", api_name="/search")
        assert results and baseline
        for html in (results, baseline):
            assert "thực tập tốt nghiệp/dự án tốt nghiệp" in html
            assert "91/QĐ-KHTN" in html and "ChatGPT" not in html
            assert "https://drive.google.com/file/d/1jNYskZmwL866hip7yL9AHlBuLOb9y1xJ/view" in html
            assert "Bị thay thế" in html
        assert "Chưa cấu hình ngưỡng" in status
        assert "Nhập câu hỏi" in client.predict("", api_name="/search")[2]
    finally:
        demo.close()
