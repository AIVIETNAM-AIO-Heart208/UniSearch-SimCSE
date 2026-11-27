"""Exercise the running regulation search demo in Chrome, including recovery after a failed request."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from playwright.sync_api import Locator, Page, expect, sync_playwright


def open_reason(parent: Locator, expected: str | re.Pattern) -> Locator:
    reason = parent.locator(":scope > .result-reason")
    body = reason.locator("p")
    expect(body).to_be_hidden()
    reason.get_by_text("Vì sao có kết quả này?", exact=True).press("Enter")
    expect(body).to_be_visible()
    expect(body).to_contain_text(expected)
    return body


SCORE = re.compile(r"Điểm khớp với câu hỏi: -?[01],\d{2}\.")


def check_journey(page: Page, url: str, screenshots: Path | None, width: int) -> None:
    def capture(name: str) -> None:
        if screenshots:
            page.screenshot(path=screenshots / f"{width}-{name}.png", caret="hide")

    page.goto(url)
    field = page.get_by_role("textbox", name="Câu hỏi")
    submit = page.get_by_role("button", name="Tra cứu", exact=True)
    topics = page.locator(".topic:visible")
    feedback = page.locator("#search-feedback")
    main = page.get_by_role("tab", name="Kết quả tra cứu", exact=True)
    keywords = page.get_by_role("tab", name="Từ khóa (BM25)", exact=True)
    expect(page.locator("#regulations")).to_have_attribute("data-search-state", "ready")
    capture("trang-dau")
    expect(field).to_be_hidden()
    page.get_by_role("radio", name="Trước K21", exact=True).check()
    expect(page.get_by_role("status").filter(has_text="chưa có quy chế nền")).to_be_visible()
    expect(field).to_be_hidden()
    expect(submit).to_be_hidden()
    expect(page.locator("#sample-questions")).to_be_hidden()
    general = page.locator("#hcmus-cohort").get_by_role("radio", name="Tra cứu chung", exact=True)
    general.check()
    general.focus()
    page.keyboard.press("Tab")
    expect(field).to_be_focused()
    expect(field).to_have_css("outline-style", "solid")
    expect(field).to_have_css("outline-width", "3px")
    capture("tieu-diem-ban-phim")

    page.get_by_role("button", name="Khi nào sinh viên được hoãn thi?").click()
    expect(topics).to_have_count(3)
    expect(topics.first).to_contain_text("Hoãn thi")
    question = "Em muốn xin chuyển trường thì cần làm gì?"
    field.fill(question)
    expect(topics).to_have_count(0)
    expect(feedback).to_contain_text("Câu hỏi đã thay đổi")
    capture("sua-cau")

    # Hold one real queue request until the loading state is visible, then fail it locally.
    route_pattern = "**/gradio_api/queue/join*"
    held = []
    page.route(route_pattern, lambda route: held.append(route))
    try:
        with page.expect_request(lambda request: "/gradio_api/queue/join" in request.url):
            submit.click()
        expect(feedback).to_have_text("Đang tra cứu…")
        expect(topics).to_have_count(0)
        capture("dang-tra")
        held[0].abort("internetdisconnected")
        expect(feedback).to_contain_text("thử lại")
        expect(topics).to_have_count(0)
        expect(field).to_have_value(question)
        capture("thu-lai")
    finally:
        page.unroute(route_pattern)

    submit.focus()
    page.keyboard.press("Enter")
    expect(topics).to_have_count(3)
    expect(topics.first).to_contain_text("chuyển trường")
    expect(feedback).to_be_empty()
    capture("phuc-hoi")

    field.fill("Điểm trung bình tích lũy được tính như thế nào và xếp loại ra sao?")
    field.press("Enter")
    edition = page.locator("#ranked-tab .topic").first.locator("details.edition").first
    edition.locator(":scope > summary").click()
    open_reason(edition, "Điểm khớp với câu hỏi: 0,65.")
    capture("diem-doan-hcmus")
    edition.get_by_text("Xem bảng gốc năm 2021 (đã sửa đổi)", exact=True).click()
    captions = edition.locator("caption:visible")
    expect(captions).to_have_count(2)
    for caption in captions.all():
        expect(caption).to_contain_text("QĐ 91/QĐ-KHTN")
    captions.first.scroll_into_view_if_needed()
    capture("bang-goc-2021")

    # Frozen scores for the open development question pilot-01.
    field.fill("Em đang đọc quy chế năm 2021. Nếu cả môn dồn vào vài buổi thì một ngày thầy được xếp nhiều nhất mấy giờ cho riêng môn đó?")
    field.press("Enter")
    expect(topics.locator(".rank-badge")).to_have_text(["Điểm Hybrid 0,977", "Điểm Hybrid 0,847", "Điểm Hybrid 0,780"])
    expect(topics.first.locator(".rank-origin")).to_have_text("Xếp theo Điều 6 của Quy chế 2021")
    topics.first.locator(".topic-summary").scroll_into_view_if_needed()
    capture("hang-hybrid")
    keywords.click()
    expect(topics.locator(".rank-badge")).to_have_text(["Điểm BM25 17,212", "Điểm BM25 16,605", "Điểm BM25 15,404"])
    expect(topics.first.locator(".rank-origin")).to_have_text("Xếp theo Điều 2 của Quy chế 2021")
    topics.first.locator(".topic-summary").scroll_into_view_if_needed()
    capture("hang-bm25")
    main.click()

    field.fill("Mấy giờ thủy triều lên ở Vũng Tàu ngày mai?")
    field.press("Enter")
    warning = page.locator("#search-status")
    expect(warning).to_be_visible()
    expect(warning).to_contain_text("Hybrid")
    expect(page.locator("#ranked-tab .topic-panel[open]")).to_have_count(0)
    main.focus()
    main.press("ArrowRight")
    expect(keywords).to_be_focused()
    expect(keywords).to_have_attribute("aria-selected", "true")
    expect(warning).to_be_hidden()
    expect(topics).to_have_count(3)
    keywords.press("Home")
    expect(main).to_be_focused()
    expect(main).to_have_attribute("aria-selected", "true")
    expect(warning).to_be_visible()

    for text, count in (("ốm", 1), ("LMS", 2)):
        field.fill(text)
        field.press("Enter")
        keywords.click()
        expect(topics).to_have_count(count)
        if count == 1:
            reason = open_reason(topics.first.locator(".topic-body"), SCORE)
            expect(reason).to_contain_text("BM25")
            capture("mot-chu-de")

    field.fill("jjjqzxvqqqzz")
    field.press("Enter")
    keywords.click()
    expect(page.locator(".empty-keywords:visible")).to_contain_text("Không có từ khóa")
    expect(topics).to_have_count(0)
    capture("tu-khoa-trong")
    field.fill(" ")
    field.press("Enter")
    expect(warning).to_be_visible()
    expect(warning).to_contain_text("Nhập câu hỏi")
    expect(topics).to_have_count(0)
    expect(page.get_by_role("button", name="Khi nào sinh viên được hoãn thi?")).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


def check_d1(page: Page, url: str, screenshots: Path | None, width: int) -> None:
    page.goto(url)
    hcmus = page.get_by_role("tab", name="HCMUS", exact=True)
    expect(hcmus).to_have_attribute("aria-selected", "true")
    d1 = page.get_by_role("tab", name="ViRHE4QA (D1)", exact=True)
    hcmus.focus()
    hcmus.press("ArrowRight")
    expect(d1).to_be_focused()
    expect(d1).to_have_attribute("aria-selected", "true")
    question = page.get_by_role("textbox", name="Câu hỏi D1", exact=True)
    prompt = "Điều kiện xét công nhận tốt nghiệp là gì"
    expect(question).to_be_hidden()
    track = page.locator("#uit-track")
    track.get_by_role("radio", name="Chính quy", exact=True).check()
    button = page.get_by_role("button", name="Tra cứu D1", exact=True)
    button.focus()
    button.press("Shift+Tab")
    expect(question).to_be_focused()
    expect(question).to_have_css("outline-style", "solid")
    if width <= 440:
        page.wait_for_function("""() => Math.abs(document.querySelector('#d1-submit').clientWidth -
            document.querySelector('#d1-question textarea').clientWidth) <= 2""")
    else:
        assert abs(button.bounding_box()["height"] - question.bounding_box()["height"]) <= 2
    question.fill(prompt)
    question.press("Enter")
    cards = page.locator("#d1-results .topic:visible")
    expect(cards).to_have_count(3, timeout=360_000)
    expect(cards.first.locator(".topic-summary")).to_contain_text("Đào tạo đại học chính quy theo học chế tín chỉ · Điều 33")
    expect(cards.first.locator(".rank-badge")).to_have_text(re.compile(r"Điểm Hybrid \d,\d{3}"))
    details = cards.first.locator(".topic-panel")
    if details.get_attribute("open") is None:
        details.locator(":scope > summary").click()
    # Rounded cosines of the two UIT excerpts for this question in the pinned demo.
    expect(cards.first.get_by_role("heading", level=2)).to_contain_text("xét tốt nghiệp")
    reason = open_reason(cards.first.locator(".topic-body"), "Điểm khớp với câu hỏi: 0,79.")
    expect(reason).to_contain_text("tiêu đề Điều")
    source = cards.first.locator(".read-more").filter(has_text="Xem toàn bộ đoạn nguồn")
    expect(source.locator(".d1-text")).to_be_visible()
    if screenshots:
        page.screenshot(path=screenshots / f"{width}-diem-doan-uit.png")
    toggle = cards.first.get_by_text("Xem toàn bộ đoạn nguồn", exact=True)
    toggle.press("Enter")
    expect(source.locator(".d1-text")).to_be_hidden()
    toggle.press("Enter")
    expect(cards.first.locator(".read-more .d1-text")).to_contain_text("nghĩa vụ học phí")
    expect(cards.first.get_by_role("link", name="Mở PDF UIT · trang 25–26")).to_be_visible()
    expect(cards.first.locator(".d1-citation")).to_contain_text("raw_excel/train.xlsx")
    expect(page.get_by_text("Tra văn bản khác của Trường")).to_be_hidden()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    track.get_by_role("radio", name="Từ xa", exact=True).check()
    expect(cards).to_have_count(0)
    feedback = page.locator("#d1-feedback")
    expect(feedback).to_contain_text("Lựa chọn đã thay đổi")
    expect(question).to_have_value(prompt)
    question.press("Enter")
    expect(cards.first.locator(".topic-summary")).to_contain_text("Đào tạo từ xa trình độ đại học · Điều 19")
    if cards.first.locator(".topic-panel").get_attribute("open") is None:
        cards.first.locator(".topic-summary").click()
    open_reason(cards.first.locator(".topic-body"), "Điểm khớp với câu hỏi: 0,74.")
    for card in cards.all():
        expect(card.locator(".reference")).to_contain_text("Đào tạo từ xa")
    # Compare the UIT scores with the saved ranking for D1-dev question 9542.
    track.get_by_role("radio", name="Tra cứu chung", exact=True).check()
    question.fill("Việc làm KLTN có thể bị dừng giữa chừng không?")
    question.press("Enter")
    expect(cards.locator(".rank-badge")).to_have_text(["Điểm Hybrid 0,997", "Điểm Hybrid 0,973", "Điểm Hybrid 0,848"])
    question.fill(prompt)
    expect(feedback).to_contain_text("Câu hỏi đã thay đổi")
    route_pattern = "**/gradio_api/queue/join*"
    held = []
    page.route(route_pattern, lambda route: held.append(route))
    try:
        with page.expect_request(lambda request: "/gradio_api/queue/join" in request.url):
            button.click()
        expect(feedback).to_have_text("Đang tra cứu…")
        expect(cards).to_have_count(0)
        held[0].abort("internetdisconnected")
        expect(feedback).to_contain_text("Nhấn Tra cứu D1 để thử lại")
        expect(question).to_have_value(prompt)
        if screenshots:
            page.screenshot(path=screenshots / f"{width}-uit-thu-lai.png")
    finally:
        page.unroute(route_pattern)
    question.press("Enter")
    expect(cards).to_have_count(3)
    expect(feedback).to_be_empty()
    question.fill("sinh viên " * 300)
    question.press("Enter")
    expect(page.locator("#d1-results [role=status]")).to_contain_text("vượt giới hạn")
    question.fill(" ")
    expect(cards).to_have_count(0)
    page.get_by_role("button", name="Tra cứu D1").click()
    expect(page.locator("#d1-results")).to_contain_text("Nhập câu hỏi D1")
    # Keep UIT cards mounted when returning to HCMUS to catch cross-tab status leaks.
    question.fill(prompt)
    question.press("Enter")
    expect(cards).to_have_count(3)
    d1.press("Home")
    expect(hcmus).to_be_focused()
    field = page.get_by_role("textbox", name="Câu hỏi", exact=True)
    cohort = page.locator("#hcmus-cohort")
    cohort.get_by_role("radio", name="K24", exact=True).check()
    field.fill(prompt)
    field.press("Enter")
    main = page.locator("#ranked-tab .topic:visible")
    expect(main.first.locator(".reference")).to_have_text("Quy chế 2021 · Điều 17 · Khoản 3")
    expect(main.first.locator(".rank-badge")).to_have_text("Chọn theo khóa")
    reason = open_reason(main.first.locator(".topic-body"), "Bạn đã chọn K24. Khoản 3 Điều 17 của Quy chế 2021")
    expect(reason).not_to_contain_text("Điểm khớp")
    if screenshots:
        page.screenshot(path=screenshots / f"{width}-ly-do-k24.png")
    expect(main.first.locator(".topic-body > .passage").get_by_text("f) Sinh viên đã đủ điều kiện", exact=False)).to_be_visible()
    expect(main.first.locator(".topic-panel[open] .topic-body > .passage").first).to_contain_text("Tích lũy đủ")
    expect(main.first.locator(".edition > summary").filter(has_text="Quy chế 2026").first).to_be_attached()
    expect(page.locator("#search-status")).to_contain_text("có lợi hơn")
    alternate = main.first.locator(".edition").filter(has=page.locator("summary", has_text="Quy chế 2026 · Điều 19 · Khoản 1"))
    alternate.locator(":scope > summary").click()
    open_reason(alternate, "Bản 2026 được mở để đối chiếu với quy chế 2021")
    cohort.get_by_role("radio", name="K26 trở đi", exact=True).check()
    expect(main).to_have_count(0)
    expect(field).to_have_value(prompt)
    field.press("Enter")
    expect(main.first.locator(".reference")).to_have_text("Quy chế 2026 · Điều 19 · Khoản 1")
    expect(main.first.locator(".rank-badge")).to_have_text("Chọn theo khóa")
    reason = open_reason(main.first.locator(".topic-body"), "Bạn đã chọn K26 trở đi. Khoản 1 Điều 19 của Quy chế 2026")
    expect(reason).not_to_contain_text("Điểm khớp")
    if screenshots:
        page.screenshot(path=screenshots / f"{width}-ly-do-k26.png")
    expect(main.first.locator(".topic-body > .passage").get_by_text("f) Thỏa các quy định", exact=False)).to_be_visible()
    expect(main.first.locator(".topic-panel[open] .topic-body > .passage").first).to_contain_text("Tích lũy đủ")
    expect(main.locator(".reference, .edition > summary").filter(has_text="Quy chế 2021")).to_have_count(0)
    expect(page.get_by_role("link", name="Tra văn bản khác của Trường")).to_be_visible()
    page.get_by_role("tab", name="Từ khóa (BM25)", exact=True).click()
    keyword_cards = page.locator("#keyword-tab .topic-summary:visible")
    expect(keyword_cards.first.locator(".rank-badge")).to_have_text("Chọn theo khóa")
    expect(keyword_cards.nth(1).locator(".rank-badge")).to_have_text(re.compile(r"Điểm BM25 -?\d+,\d{3}"))
    field.fill(" ")
    field.press("Enter")
    expect(page.locator("#search-status")).to_contain_text("Nhập câu hỏi")
    expect(page.locator("#search-status")).to_be_visible()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:7860")
    parser.add_argument("--d1", action="store_true", help="Also exercise the ViRHE4QA tab")
    parser.add_argument("--screenshots", type=Path, help="New directory for PNG evidence")
    args = parser.parse_args()
    if args.screenshots:
        args.screenshots.mkdir(parents=True, exist_ok=False)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome")
        for width, height in ((1440, 960), (320, 740)):
            page = browser.new_page(viewport={"width": width, "height": height}, locale="vi-VN")
            page.set_default_timeout(15000)
            check_journey(page, args.url, args.screenshots, width)
            if args.d1:
                check_d1(page, args.url, args.screenshots, width)
            page.close()
            print(f"Chrome {width} x {height}: passed")
        browser.close()


if __name__ == "__main__":
    main()
