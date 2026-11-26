"""Exercise the running HCMUS demo in Chrome, including a browser-side connection failure."""

from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import Page, expect, sync_playwright


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
    page.get_by_role("link", name="Tra văn bản khác của Trường").focus()
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
    edition.get_by_text("Xem bảng gốc năm 2021 (đã sửa đổi)", exact=True).click()
    captions = edition.locator("caption:visible")
    expect(captions).to_have_count(2)
    for caption in captions.all():
        expect(caption).to_contain_text("QĐ 91/QĐ-KHTN")
    captions.first.scroll_into_view_if_needed()
    capture("bang-goc-2021")

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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:7860")
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
            page.close()
            print(f"Chrome {width} x {height}: passed")
        browser.close()


if __name__ == "__main__":
    main()
