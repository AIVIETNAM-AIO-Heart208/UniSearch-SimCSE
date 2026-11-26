"""Guard explicit edition intent, source availability, and paired display metrics."""

import json
import unicodedata
from hashlib import sha256
from pathlib import Path

import pytest

from experiments.application.compare_edition_display import CONTROL, PILOT_SLICES, prefer_edition, requested_edition


@pytest.mark.parametrize(("text", "year"), [
    ("Theo bản năm 2021, xếp giờ giảng thế nào?", "2021"),
    ("TRONG QUY CHẾ ĐÀO TẠO TRÌNH ĐỘ ĐẠI HỌC BAN HÀNH NĂM 2026, Điều 10 nói gì?", "2026"),
    (unicodedata.normalize("NFD", "Theo quy chế 2021 thì sao?"), "2021"),
    ("Theo quy che nam 2021 tinh diem the nao?", "2021"),
    ("Em muốn tra quy chế của năm 2021.", "2021"),
    ("Theo QĐ 1175/QĐ-KHTN (2021) thì sao?", "2021"),
    ("Quyết định số 3087 năm 2026 quy định thế nào?", "2026"),
    ("Theo QĐ 1175 năm 2026 thì sao?", None),
    ("Em khóa 2021, muốn đọc quy chế 2026.", "2026"),
    ("Em K24, xem bản 2026 cho học kỳ 2 năm học 2025–2026.", "2026"),
    ("Theo quy chế 2021, trường xử lý học kỳ 1 năm 2026 thế nào?", "2021"),
    ("Em nhập học năm 2021, quy chế nào áp dụng cho em?", None),
    ("Khóa tuyển sinh năm 2026 có được phúc tra không?", None),
    ("Em K24 muốn xem điểm.", None),
    ("Quy chế năm học 2025–2026 áp dụng thế nào?", None),
    ("Quy chế 2026-2027 áp dụng cho ai?", None),
    ("Ngày 29/09/2026 em có được đăng ký không?", None),
    ("So sánh bản 2021 và bản 2026.", None),
    ("Theo quy chế 2021 hay 2026?", None),
    ("Hai bản quy chế 2021 và 2026 khác nhau thế nào?", None),
    ("Quy chế 2021 khác với bản mới thế nào?", None),
    ("Không dùng quy chế 2021.", None),
    ("Em không muốn xem quy chế 2021.", None),
    ("Phí cấp mẫu đơn phiên bản 2021 là bao nhiêu?", None),
    ("Theo bạn năm 2021 thì thế nào?", None),
    ("Theo quy chế 2023, em xem ở đâu?", None),
    ("Điểm môn thực hành được tính thế nào?", None),
])
def test_edition_requires_an_unambiguous_document_reference(text, year):
    assert requested_edition(text) == year


def test_preference_preserves_all_topics_editions_and_same_edition_order():
    recent = ({"doc_id": "hcmus-qcdt-2026"}, .8)
    old_a, old_b = ({"doc_id": "hcmus-qcdt-2021"}, .7), ({"doc_id": "hcmus-qcdt-2021"}, .5)
    groups = [[recent, old_a, old_b], [recent]]
    assert prefer_edition(groups, "2021") == [[old_a, old_b, recent], [recent]]
    assert prefer_edition(groups, "2026") == groups
    assert prefer_edition(groups, None) == groups
    assert groups == [[recent, old_a, old_b], [recent]]


def test_saved_display_comparison_uses_the_frozen_control_and_all_four_query_slices():
    result = json.loads((CONTROL.parent / "edition-display-pilot/summary.json").read_bytes())
    control = (CONTROL / "summary.json").read_bytes()
    assert sha256(control).hexdigest() == result["control_summary_sha256"]
    assert sha256(Path("apps/search.css").read_bytes()).hexdigest() == result["source_sha256"]["search.css"]
    original = {r["qid"]: r for r in map(json.loads, (CONTROL / "predictions.jsonl").read_bytes().splitlines())}
    assert len(result["cases"]) == len(original) == 16
    assert result["config"] == json.loads(control)["config"]
    assert {r["qid"] for r in result["cases"]} == set(original)
    for row in result["cases"]:
        gold = original[row["qid"]]
        a = gold["variants"]["A"]
        assert row["qid"] in PILOT_SLICES[row["slice"]]
        detected = row["slice"].removeprefix("edition_") if row["slice"].startswith("edition_") else None
        assert requested_edition(gold["question"]) == detected == row["requested_edition"]
        assert (row["cosine"], row["accepted"], row["top_chunk"]) == (a["cosine"], a["accepted"], a["chunk_id"])
        assert row["views"]["current"]["sha256"] == a["view_sha256"]
        if detected is None:
            assert row["views"]["requested"]["sha256"] == a["view_sha256"]
    for key, slices in [(None, result["overall"]), *result["slices"].items()]:
        rows = [r for r in result["cases"] if key is None or r["slice"] == key]
        assert slices["in_scope"] == sum(r["scope"] == "in" for r in rows)
        for name in ("current", "requested"):
            expected = [r["qid"] for r in rows if r["scope"] == "in" and r["views"][name]["evidence_path"] == []]
            assert expected == slices[name + "_visible"]
