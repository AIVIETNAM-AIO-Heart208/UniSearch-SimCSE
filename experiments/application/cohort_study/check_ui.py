"""Exercise the extracted study ZIP in offline Chrome and optionally photograph each route."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
import zipfile
from collections.abc import Callable
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import Page, expect, sync_playwright


HERE = Path(__file__).resolve().parent


def send(page: Page, text: str) -> None:
    field = page.get_by_role("textbox", name="Câu hỏi của bạn")
    field.fill(text)
    field.press("Enter")


def choose(page: Page, year: str) -> None:
    page.get_by_label("Năm nhập học", exact=True).select_option(year)
    page.locator("#confirm-cohort").click()


def check_width(page: Page) -> None:
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), page.url


def check_scenarios(a: Page, b: Page, kit: Path, study: dict, capture: Callable) -> None:
    for scenario in study["scenarios"]:
        card = a.context.new_page()
        card.goto((kit / f"phieu-{scenario['id']}.html").as_uri())
        text = card.locator("#task-question").inner_text()
        check_width(card)
        capture(card, "phieu-" + scenario["id"], scenario["title"])
        card.close()
        contents = []
        for arm, page in (("a", a), ("b", b)):
            page.reload()
            first = arm == "a"
            scope = scenario["id"] != "chung"
            year = "2026" if scenario["id"] == "k26" else "2024"
            if first:
                expect(page.locator("#workspace")).to_be_hidden()
                expect(page.locator("#cohort-alternative")).to_be_hidden()
                page.locator("#confirm-cohort").click()
                expect(page.locator("#admission")).to_be_focused()
                assert not page.locator("#admission").evaluate("node => node.checkValidity()")
                choose(page, year)
            else:
                expect(page.locator("#workspace")).to_be_visible()
                expect(page.locator("#cohort-panel")).to_be_hidden()
            send(page, text)
            if scope and not first:
                expect(page.locator("#admission")).to_be_focused()
                expect(page.locator("#query")).to_have_value(text)
                expect(page.locator("#results")).to_be_hidden()
                capture(page, "b-hoi-khoa", "Mẫu B hỏi năm sau câu cá nhân")
                choose(page, year)
            expect(page.locator("#cohort-panel")).to_be_hidden()
            expect(page.locator("#result-heading")).to_be_focused()
            result = page.locator("#result-content")
            if scope:
                expected = "1" if year == "2026" else "2"
                expect(result.locator("[data-clause]")).to_have_count(1)
                expect(result.locator("[data-clause]")).to_have_attribute("data-clause", expected)
                expect(result.locator("h3")).to_contain_text("K" + year[-2:])
                expect(result.locator("blockquote")).to_contain_text("2026-2027" if expected == "1" else "Trường lựa chọn")
                expect(result.get_by_role("link")).to_have_attribute("href", "van-ban/quy-che-2026.pdf#page=21")
            else:
                expect(result.locator(".topic-panel[open] .reference").first).to_have_text("Quy chế 2026 · Điều 10 · Khoản 3")
                expect(result.locator(".passage:visible").first).to_contain_text("điểm chuyên cần")
                expect(result.locator(".source-line a:visible").first).to_have_attribute("href", "van-ban/quy-che-2026.pdf#page=10")
                if not first:
                    expect(page.locator("#session-bar")).to_be_hidden()
            check_width(page)
            contents.append(result.inner_html())
            capture(page, f"{arm}-{scenario['id']}", "Mẫu " + arm.upper() + " · " + scenario["id"])
        assert contents[0] == contents[1], scenario["id"]


def check_bank(a: Page, b: Page, kit: Path, cases: list[dict], personal: str, capture: Callable) -> None:
    expected_questions = [row["question"] for row in cases] + [personal]
    for page in (a, b):
        assert page.locator(".question-option").all_text_contents() == expected_questions
    b.reload()  # No stored year: every development question must still be searchable.
    for case in cases:
        rendered = []
        for arm, page in (("a", a), ("b", b)):
            send(page, case["question"])
            expect(page.locator("#cohort-panel")).to_be_hidden()
            expect(page.locator(".topic-panel")).to_have_count(3)
            expect(page.locator(".topic-panel[open]")).to_have_count(int(case["accepted"]))
            warning = page.locator("#search-status").inner_text().strip()
            assert bool(warning) == (not case["accepted"])
            year = case["views"]["requested"]["primary_clause"].split(":")[0][-4:]
            expect(page.locator(".reference").first).to_contain_text("Quy chế " + year)
            links = page.locator("#result-content a").evaluate_all("nodes => nodes.map(n => n.getAttribute('href'))")
            assert all(url.startswith("van-ban/") and (kit / urlsplit(url).path).is_file() for url in links)
            rendered.append((page.locator("#result-content").inner_html(), warning))
            check_width(page)
            assert page.locator("#query").evaluate("node => node.scrollHeight <= node.clientHeight + 1"), case["qid"]
            capture(page, arm + "-" + case["qid"], case["question"])
        assert rendered[0] == rendered[1], case["qid"]


def check_interactions(a: Page, b: Page, personal: str, cases: list[dict], capture: Callable) -> None:
    a.locator("#restart").click()
    expect(a.locator("#workspace")).to_be_hidden()
    expect(a.locator("#admission")).to_have_value("")
    b.locator("#restart").click()
    expect(b.locator("#query")).to_be_focused()
    b.locator("#query").press("Enter")
    expect(b.locator("#results")).to_be_hidden()
    b.locator("#question-list > summary").focus()
    b.keyboard.press("Enter")
    expect(b.locator(".question-option").first).to_be_visible()
    capture(b, "b-danh-sach", "Chọn một câu trong bộ thử")
    b.keyboard.press("Tab")
    expect(b.locator(".question-option").first).to_be_focused()
    b.keyboard.press("Enter")
    expect(b.locator(".reference").first).to_contain_text("Quy chế 2021")
    send(b, personal)
    b.locator("#query").fill(cases[5]["question"])
    expect(b.locator("#cohort-panel")).to_be_hidden()
    b.locator("#query").press("Enter")
    expect(b.locator("#cohort-panel")).to_be_hidden()
    expect(b.locator("#session-bar")).to_be_hidden()
    send(b, "Em K24. " + personal)
    expect(b.locator('[data-clause="2"]')).to_be_visible()
    expect(b.locator("#cohort-panel")).to_be_hidden()
    send(b, personal + " K26")
    expect(b.locator('[data-clause="1"]')).to_be_visible()
    send(b, personal)
    b.locator("#cohort-alternative").click()
    expect(b.locator("#result-content [data-clause]")).to_have_count(2)
    capture(b, "b-chua-ro-khoa", "Đối chiếu cả hai khoản khi chưa rõ khóa")
    send(b, personal)
    choose(b, "2024")
    send(b, personal)
    expect(b.locator('[data-clause="2"]')).to_be_visible()
    b.locator("#change-cohort").click()
    b.locator("#cohort-alternative").click()
    expect(b.locator("#change-cohort")).to_be_focused()
    b.locator("#change-cohort").click()
    choose(b, "2026")
    expect(b.locator('[data-clause="1"]')).to_be_visible()
    expect(b.locator("#result-content [data-clause]")).to_have_count(1)
    # A stored K26 cannot override an explicitly requested 2021 edition.
    send(b, cases[0]["question"])
    expect(b.locator(".reference").first).to_contain_text("Quy chế 2021")
    send(b, cases[14]["question"])
    b.locator(".topic-panel[open] .edition > summary").first.click()
    expect(b.locator(".edition[open] .passage").first).to_contain_text("điểm chuyên cần")
    earlier = b.locator(".edition[open] .source-line a").first
    expect(earlier).to_have_attribute("href", "van-ban/quy-che-2021.pdf#page=8")
    with b.expect_popup() as opened_pdf:
        earlier.click()
    opened_pdf.value.wait_for_url(re.compile(r"quy-che-2021\.pdf#page=8$"))
    opened_pdf.value.close()
    capture(b, "b-doi-chieu", "Căn cứ về điểm thực hành trong cả hai bản")
    send(b, "Thư viện mở cửa mấy giờ?")
    expect(b.locator("#no-match")).to_be_visible()
    expect(b.locator("#question-list > summary")).to_be_focused()
    expect(b.locator(".topic")).to_have_count(0)
    capture(b, "b-ngoai-bo", "Khi câu nhập chưa có trong bộ thử")
    b.locator("#restart").click()
    expect(b.locator("#session-bar")).to_be_hidden()
    expect(b.locator("#results")).to_be_hidden()
    expect(b.locator("#query")).to_have_value("")


def check_kit(archive: Path, screenshots: Path | None) -> None:
    study = json.loads((HERE / "study.json").read_bytes())
    cases = json.loads((HERE.parent / "results/edition-display-pilot/summary.json").read_bytes())["cases"]
    photos: dict[Path, str] = {}
    if screenshots:
        screenshots.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix="thu nghiem khoa ") as temp, sync_playwright() as pw:
        kit = Path(temp)
        with zipfile.ZipFile(archive) as bundle:
            assert bundle.testzip() is None
            bundle.extractall(kit)
        browser = pw.chromium.launch(channel="chrome")
        for width, height in ((1440, 900), (390, 844), (320, 700)):
            context = browser.new_context(viewport={"width": width, "height": height}, offline=True)
            remote, errors = [], []
            context.on("request", lambda req: remote.append(req.url) if req.url.startswith(("http:", "https:")) else None)
            context.on("page", lambda page: page.on("pageerror", lambda err: errors.append(str(err))))

            def capture(page: Page, name: str, label: str) -> None:
                if screenshots is None or width == 320:
                    return
                relative = Path(str(width)) / (name + ".png")
                if relative not in photos:
                    photos[relative] = label
                    page.screenshot(path=screenshots / relative, caret="hide")

            a, b = context.new_page(), context.new_page()
            a.goto((kit / "mau-a.html").as_uri())
            b.goto((kit / "mau-b.html").as_uri())
            capture(a, "a-bat-dau", "Mẫu A · Màn hình đầu")
            capture(b, "b-bat-dau", "Mẫu B · Màn hình đầu")
            check_scenarios(a, b, kit, study, capture)
            check_bank(a, b, kit, cases, study["personal_question"], capture)
            check_interactions(a, b, study["personal_question"], cases, capture)
            guide = kit / "huong-dan-mo-phong.html"
            if not guide.is_file():
                guide = kit / "huong-dan-dieu-phoi.html"  # Archived walkthrough kits.
            b.goto(guide.as_uri())
            for href in b.locator("a").evaluate_all("nodes => nodes.map(n => n.getAttribute('href'))"):
                assert (kit / urlsplit(href).path).is_file(), href
            a.reload()
            choose(a, "2024")
            send(a, study["personal_question"])
            with a.expect_popup() as pdf:
                a.locator("#result-content a").click()
            pdf.value.wait_for_url(re.compile(r"quy-che-2026\.pdf#page=21$"))
            pdf.value.close()
            b.goto((kit / "mau-b.html").as_uri())
            send(b, cases[14]["question"])
            link = b.locator('a[href="van-ban/quyet-dinh-91.html"]')
            for details in link.locator("xpath=ancestor::details").all():
                if not details.evaluate("node => node.open"):
                    details.locator(":scope > summary").click()
            with b.expect_popup() as opened:
                link.click()
            supplement = opened.value
            supplement.wait_for_load_state()
            assert supplement.locator("img").evaluate_all("nodes => nodes.length === 2 && nodes.every(n => n.naturalWidth > 0)")
            assert not errors and not remote, (errors, remote)
            context.close()
            print(f"{width}px: 6 assigned journeys, 16 paired results, keyboard, reset, scope and local references passed")
        browser.close()
    if screenshots:
        files = "".join('<li><a href="' + path.as_posix() + '">' + path.as_posix() + "</a> · " + escape(label) + "</li>"
                        for path, label in sorted(photos.items()))
        index = screenshots / "muc-luc.html"
        index.write_text('<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" '
                         'content="width=device-width,initial-scale=1"><title>Ảnh hai mẫu</title><main>'
                         '<p>Viết cho: người đánh giá giao diện</p><h1>Ảnh hai mẫu tra cứu</h1><ul>' + files +
                         "</ul></main></html>", encoding="utf-8")
        with zipfile.ZipFile(screenshots / "anh-hai-mau.zip", "w", zipfile.ZIP_DEFLATED) as zipped:
            for path in [index, *(screenshots / photo for photo in sorted(photos))]:
                zipped.write(path, path.relative_to(screenshots))
        print(f"{len(photos)} screenshots and index: {screenshots}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--screenshots", type=Path, help="New directory for a separate UI review archive")
    args = parser.parse_args()
    check_kit(args.archive, args.screenshots)
