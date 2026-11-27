import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from apps.app import (
    _asks_graduation_conditions, _graduation_citations, _load_d1_chunks, _load_d1_sources,
    answer, create_demo, render_groups,
)
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
    assert "bản chép từ bản scan" not in rendered and "Điểm SimCSE-VN 1,000" in rendered
    assert "&lt;fixture&gt;" in baseline
    index.vectors = index.vectors.copy()
    index.vectors[:, 0] = 0
    results, lexical, status = answer(index, "a <fixture>", weight=0.5, threshold=0.8)
    assert results and "Độ tin cậy thấp đối với trích đoạn hạng đầu của Hybrid" in status
    assert 'class="topic-panel" open' not in results and 'class="topic-panel" open' in lexical
    assert "trích đoạn hạng đầu của SimCSE-VN" in answer(index, "fixture", threshold=0.8)[2]


def test_reasons_use_each_displayed_chunk_cosine_after_grouping(monkeypatch):
    index = fixture_index()
    scores = ([10., -6., 4., 5., 5.], [-0.10, 0.95, 0.8, 0.5, 0.5])
    monkeypatch.setattr(index, "score", lambda _: iter([scores]))
    ranked, lexical, _ = answer(index, "a", weight=0.5, edition="hcmus-qcdt-2021", cohort="K24")
    for html in (ranked, lexical):
        first, _, alternatives = html.partition('<details class="edition">')
        assert "Điểm khớp với câu hỏi: -0,10." in first
        edition = next(block for block in alternatives.split('<details class="edition">')
                       if block.startswith("<summary>Quy chế 2026 · Điều 3 · Khoản 1"))
        assert "Điểm khớp với câu hỏi: 0,80." in edition.split("</details>", 1)[0]
        assert "0,95" not in html
    assert "thứ tự kết quả dựa trên điểm BM25" in lexical
    assert "thứ tự kết quả dựa trên điểm BM25" not in ranked


@pytest.mark.parametrize(("weight", "badge"), [
    (None, "Điểm SimCSE-VN 0,950"),
    (0, "Điểm SimCSE-VN 0,950"),
    (0.5, "Điểm Hybrid 1,000"),
    (1, "Điểm BM25 10,000"),
])
def test_rank_badge_uses_the_leading_article_before_edition_display_order(monkeypatch, weight, badge):
    index = fixture_index()
    scores = ([10., -6., 4., 5., 5.], [-0.10, 0.95, 0.8, 0.5, 0.5])
    monkeypatch.setattr(index, "score", lambda _: iter([scores]))
    ranked, lexical, _ = answer(index, "a", weight=weight)
    for html, expected in ((ranked, badge), (lexical, "Điểm BM25 10,000")):
        header = html.split('<summary class="topic-summary">', 1)[1].split("</summary>", 1)[0]
        assert f'<span class="rank-badge">{expected}</span>' in header
        assert "Quy chế 2026" in header and "của Quy chế 2021" in header


def test_comparison_edition_does_not_raise_a_cohorts_rank_score(monkeypatch):
    index = fixture_index()
    scores = ([4., 2., 12., 1., 5.], [0.2, 0.1, 0.9, 0., 0.3])
    monkeypatch.setattr(index, "score", lambda _: iter([scores]))
    ranked, lexical, _ = answer(index, "a", weight=0.5, edition="hcmus-qcdt-2021", cohort="K24")
    # The 2026 comparison article scores 1 in Hybrid and 12 in BM25.
    assert "Điểm Hybrid 0,247" in ranked and "Điểm Hybrid 1,000" not in ranked
    assert "Điểm BM25 4,000" in lexical and "Điểm BM25 12,000" not in lexical


def test_keyword_rank_badge_uses_first_nonzero_article_even_when_negative(monkeypatch):
    index = fixture_index()
    monkeypatch.setattr(index, "score", lambda _: iter([([0., 0., -1.25, 0., -2.], [0.5] * 5)]))
    _, lexical, _ = answer(index, "a", weight=0.6)
    assert "Điểm BM25 -1,250" in lexical and "Điểm BM25 0,000" not in lexical


def test_pure_bm25_warning_uses_first_article_with_signal(monkeypatch):
    index = fixture_index()
    monkeypatch.setattr(index, "score", lambda _: iter([([0., 0., -1.25, 0., -2.], [0.99, 0.99, 0.1, 0.99, 0.1])]))
    ranked, _, notice = answer(index, "a", weight=1, threshold=0.7, cohort="Tra cứu chung")
    assert "Độ tin cậy thấp" in notice and "Điều 3" in notice
    assert 'class="topic-panel" open' not in ranked


def test_d1_filters_no_signal_before_cutoff_and_confidence(monkeypatch):
    pytest.importorskip("gradio")
    index = fixture_index()
    for chunk in index.chunks:
        chunk.update(char_start=0, char_end=len(chunk["text"]))
    monkeypatch.setattr(index, "score", lambda _: iter([([0., 0., 0., 0., -1.5], [0.99] * 4 + [0.1])]))
    demo = create_demo(index, 1, 0.7, get_d1_index=lambda: index)
    search = next(event.fn for event in demo.fns.values() if event.api_name == "search_d1")
    html = search("a", "Tra cứu chung")
    assert html.count('class="topic-panel"') == 1 and "Điểm BM25 -1,500" in html
    assert "Độ khớp thấp" in html and 'class="topic-panel" open' not in html


@pytest.mark.parametrize(("question", "matches"), [
    ("Điều kiện xét công nhận tốt nghiệp là gì?", True),
    ("De duoc tot nghiep em can dap ung nhung gi?", True),
    ("Điều kiện để tốt nghiệp loại giỏi là gì?", False),
    ("Khi đủ điều kiện tốt nghiệp thì em nộp hồ sơ thế nào?", False),
    ("Ai ký quyết định công nhận tốt nghiệp cho sinh viên đủ điều kiện?", False),
    ("Điều kiện xét học bổng là gì?", False),
])
def test_general_graduation_requirements(question, matches):
    assert _asks_graduation_conditions(question) is matches


def test_graduation_citation_requires_a_unique_list_in_the_edition():
    clause = dict(doc_id="edition", article_id="article", article_title="Xét tốt nghiệp", clause=8,
                  chunk_id="list", text="8. Sinh viên được xét tốt nghiệp khi có đủ các điều kiện sau:\na) Tích lũy đủ.")
    index = SimpleNamespace(chunks=[clause], groups={"article": [0]})
    assert _graduation_citations(index) == {"article": "list"}
    index.chunks.append(dict(clause, chunk_id="other", article_id="other-article"))
    index.groups["other-article"] = [1]
    assert _graduation_citations(index) == {}


def test_only_a_prioritized_graduation_topic_gets_a_selection_badge(monkeypatch):
    index = fixture_index()
    clause = index.by_chunk["a0"]
    clause.update(article_title="Xét tốt nghiệp",
                  text="1. Sinh viên được xét tốt nghiệp khi có đủ các điều kiện sau: a) Tích lũy đủ.")
    monkeypatch.setattr(index, "score", lambda _: iter([([1., 1., 4., 3., 2.], [0.1, 0.1, 0.4, 0.3, 0.2])]))
    question = "Điều kiện xét tốt nghiệp là gì?"
    ranked, lexical, _ = answer(index, question, weight=0.6, edition=clause["doc_id"], cohort="K24")
    for html, method in ((ranked, "Hybrid"), (lexical, "BM25")):
        headers = html.split('<summary class="topic-summary">')[1:]
        assert '<span class="rank-badge">Chọn theo khóa</span>' in headers[0].split("</summary>", 1)[0]
        assert f'<span class="rank-badge">Điểm {method} ' in headers[1].split("</summary>", 1)[0]
    general, _, _ = answer(index, question, weight=0.6, cohort="Tra cứu chung")
    assert '<span class="rank-badge">Chọn theo điều kiện tốt nghiệp</span>' in general
    newer, _, _ = answer(index, question, weight=0.6, edition="hcmus-qcdt-2026", cohort="K26 trở đi")
    assert "Chọn theo khóa" not in newer and "Điểm Hybrid " in newer


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
    scores = ([0., 0.], [0.12, 0.81])
    html = render_groups([[(heading, 1.)]], index, scores=scores)
    passage, _, below = html.partition('</details></details></div>')
    assert "Điểm khớp với câu hỏi: 0,12." in passage
    assert "Điểm khớp với câu hỏi: 0,81." in below and "tiêu đề Điều" in below


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


def test_d1_loader_accepts_sources_and_precomputed_windows(tmp_path):
    from data.prepare_virhe4qa import source_record

    path = tmp_path / "corpus.jsonl"
    source = source_record("Điều 1. Tốt nghiệp\n1. Điều kiện xét.")
    path.write_text(json.dumps(source), encoding="utf-8")
    chunks = _load_d1_chunks(path, lambda text: len(text.split()))
    assert [c["clause"] for c in chunks] == [None, 1]
    assert all(c["text"] == source["text"][c["char_start"]:c["char_end"]] for c in chunks)
    path.write_text("\n".join(json.dumps(chunk) for chunk in chunks), encoding="utf-8")
    assert _load_d1_chunks(path, lambda _: pytest.fail("unexpected tokenization")) == chunks
    path.write_text(json.dumps(dict(source, doc_id="hcmus-qcdt-2021")), encoding="utf-8")
    with pytest.raises(ValueError, match="ViRHE4QA"):
        _load_d1_chunks(path, len)


def test_d1_document_citations():
    sources = _load_d1_sources()
    assert len(sources) == 297
    assert len({source["document"] for source in sources.values()}) == 21
    assert all(len(key) == 64 and int(source["train_row"]) >= 2 for key, source in sources.items())
    regular = sources["dc17d6c33c4c33682ef624d34a32c155ccdd929b43cb7ab58a91f9f84ebaec05"]
    distance = sources["f97d7f975931894918ac75067b27d8edfb6cf14dfdc8c70048edc0a65080fefa"]
    assert "ĐẠI HỌC CHÍNH QUY" in regular["document"] and regular["pages"] == ("25", "26")
    assert "ĐÀO TẠO TỪ XA" in distance["document"]
    for source in sources.values():
        if source["pages"]:
            first, last = map(int, source["pages"])
            assert 1 <= first <= last and source["pdf_url"].startswith("https://")


def test_hcmus_demo_without_d1():
    pytest.importorskip("gradio")
    demo = create_demo(fixture_index())
    assert "search" in {event["api_name"] for event in demo.config["dependencies"]}
    assert "search_d1" not in {event["api_name"] for event in demo.config["dependencies"]}
    assert not any(c["props"].get("elem_id") == "source-tabs" for c in demo.config["components"])


def test_graduation_capture_uses_server_settings_and_rejects_other_baselines(tmp_path, monkeypatch):
    pytest.importorskip("gradio")
    from experiments.application import check_graduation_excerpts as capture

    settings = create_demo(fixture_index(), 0, None).config
    result = '<details class="topic-panel" open><span class="reference">Quy chế 2021 · Điều 17 · Khoản 3</span>'
    client = SimpleNamespace(config=settings, predict=lambda *args, **kwargs: (result, "", ""))
    monkeypatch.setattr(capture, "Client", lambda *args, **kwargs: client)
    output = tmp_path / "capture.json"
    monkeypatch.setattr(sys, "argv", ["check_graduation_excerpts", "--output", str(output)])
    capture.main()
    actual = json.loads(output.read_bytes())
    assert actual["weight"] == 0 and actual["threshold"] is None
    checked = tmp_path / "compared.json"
    actual["weight"] = 0.6
    output.write_text(json.dumps(actual), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["check_graduation_excerpts", "--output", str(checked), "--baseline", str(output)])
    with pytest.raises(SystemExit):
        capture.main()
    assert not checked.exists()


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
    source = dict(doc_id="virhe4qa", article_id="d1-source", article=None, article_title=None, clause=None)
    windows = [dict(source, chunk_id="d1:0", text="<Đoạn> đầu", char_start=0, char_end=10),
               dict(source, chunk_id="d1:1", text="đầu và cuối", char_start=7, char_end=18)]
    d1 = RetrievalIndex(windows, FixtureEncoder(), tokenize=str)
    d1.vectors = np.array([[0.32, 0.], [0.83, 0.]])
    demo = create_demo(index, get_d1_index=lambda: d1)
    try:
        _, url, _ = demo.launch(server_name="127.0.0.1", share=False, prevent_thread_lock=True, quiet=True)
        client = Client(url, verbose=False)
        assert "Chọn khóa" in client.predict("tốt nghiệp", None, api_name="/search")[2]
        missing = client.predict("tốt nghiệp", "Trước K21", api_name="/search")
        assert not any(missing[:2]) and "chưa có quy chế" in missing[2]
        assert "Chọn hệ" in client.predict("đầu", None, api_name="/search_d1")
        assert "Chưa có văn bản" in client.predict("đầu", "Từ xa", api_name="/search_d1")
        results, baseline, status = client.predict("thực tập tốt nghiệp", "Tra cứu chung", api_name="/search")
        assert results and baseline
        for html in (results, baseline):
            assert "thực tập tốt nghiệp/dự án tốt nghiệp" in html
            assert "91/QĐ-KHTN" in html and "ChatGPT" not in html
            assert "https://drive.google.com/file/d/1jNYskZmwL866hip7yL9AHlBuLOb9y1xJ/view" in html
            assert "Bị thay thế" in html
        assert "Chưa cấu hình ngưỡng" in status
        assert "Nhập câu hỏi" in client.predict("", "Tra cứu chung", api_name="/search")[2]
        d1_html = client.predict("đầu", "Tra cứu chung", api_name="/search_d1")
        assert 'data-query="đầu"' in d1_html
        assert '<span class="rank-badge">Điểm SimCSE-VN 0,830</span>' in d1_html
        assert "d1:1" in d1_html and "Điểm khớp với câu hỏi: 0,83." in d1_html
        assert "&lt;Đoạn&gt; đầu và cuối" in d1_html and "ViRHE4QA" in d1_html
        assert "Chưa xác định văn bản" in d1_html and "train.xlsx" not in d1_html
        assert "Điều None" not in d1_html and "QĐ" not in d1_html
        assert "Nhập câu hỏi D1" in client.predict("  ", "Tra cứu chung", api_name="/search_d1")
    finally:
        demo.close()
