"""Run the six cohort scenarios in an offline browser and record their results."""

from __future__ import annotations

import argparse
import csv
import json
import platform
import random
import re
import tempfile
import zipfile
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path

from playwright.sync_api import Browser, Error, sync_playwright

from experiments.application.cohort_study.check_ui import choose, send


VIEWPORT = {"width": 1440, "height": 900}
CARDS = {"K24": "k24", "K26": "k26", "Tra chung": "chung"}
LISTEN = """() => {
    const start = performance.now();
    window.observedActions = [];
    const mark = (action, value) => window.observedActions.push({
        action, value, ms: Math.round((performance.now() - start) * 10) / 10
    });
    document.addEventListener('input', e => {
        if (e.target.id === 'query') mark('enter_question', e.target.value);
    }, true);
    document.addEventListener('change', e => {
        if (e.target.id === 'admission') mark('choose_cohort', e.target.value);
    }, true);
    document.addEventListener('submit', e => {
        if (e.target.id === 'search-form') mark('send_question');
        if (e.target.id === 'cohort-form') mark('confirm_cohort');
    }, true);
    document.addEventListener('click', e => {
        if (e.target.closest('#result-content blockquote, #result-content .passage p')) mark('point');
    }, true);
}"""
READ_PASSAGE = """node => {
    const scope = node.closest('.scope-answer');
    const panel = node.closest('.edition, .topic-panel');
    const summary = panel?.querySelector(':scope > summary');
    return {
        reference: (scope ? node.parentElement.querySelector('h4') :
                    summary.querySelector('.reference') || summary.firstChild).textContent.trim(),
        passage: node.innerText,
        answer: scope ? scope.querySelector('h3').innerText : node.innerText,
        source: (scope || panel).querySelector('.source-line a').getAttribute('href')
    };
}"""


def first_passage_is_correct(scenario: str, reading: dict) -> bool:
    """Score the recorded text and its citation after the browser has pointed to a paragraph."""
    if not reading:
        return False
    ref, text = reading["reference"], reading["passage"].lower()
    answer = reading["answer"].lower()
    document = reading["source"].split("#")[0]
    if scenario == "Tra chung":
        return ((ref, document) in {
            ("Quy chế 2026 · Điều 10 · Khoản 3", "van-ban/quy-che-2026.pdf"),
            ("Quy chế 2021 · Điều 9 · Khoản 2", "van-ban/quy-che-2021.pdf"),
        } and "thành phần bao gồm" in text and "điểm chuyên cần" in text)
    if document != "van-ban/quy-che-2026.pdf":
        return False
    if scenario == "K24":
        return (ref == "Quy chế 2026 · Điều 27 · Khoản 2" and "2025 trở về trước" in text
                and "trường lựa chọn" in answer and "quy định mới có lợi hơn" in answer and "k24" in answer)
    return (ref == "Quy chế 2026 · Điều 27 · Khoản 1" and "từ năm học 2026-2027" in text
            and "quy chế 2026 áp dụng cho k26" in answer)


def observe(browser: Browser, kit: Path, output: Path, trial: str, arm: str, scenario: str) -> dict:
    context = browser.new_context(viewport=VIEWPORT, locale="vi-VN", offline=True)
    context.set_default_timeout(5000)
    remote, errors = [], []
    context.on("request", lambda req: remote.append(req.url) if req.url.startswith(("https:", "http:")) else None)
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))
    reading = {}
    opened_source, source_error = "", ""
    try:
        page.goto((kit / f"phieu-{CARDS[scenario]}.html").as_uri())
        question = page.locator("#task-question").inner_text()
        role = page.locator("main > h1 + p").inner_text()
        year = re.search(r"nhập học.*?năm (20[0-9]{2})", role).group(1)
        page.goto((kit / f"mau-{arm.lower()}.html").as_uri())
        page.locator("#workspace:visible, #cohort-panel:visible").first.wait_for()
        page.evaluate(LISTEN)
        picker = page.get_by_role("combobox", name="Năm nhập học")
        if picker.is_visible():
            choose(page, year)
        send(page, question)
        if picker.is_visible():
            choose(page, year)
        # Pick by visible reading order. The navigation has no expected edition, article or clause.
        passage = page.locator("#result-content blockquote:visible, #result-content .passage p:visible").first
        if passage.is_visible():
            passage.click()
            reading = passage.evaluate(READ_PASSAGE)
    except Error as exc:
        errors.append(str(exc).splitlines()[0])
    finally:
        actions = page.evaluate("window.observedActions || []")
        photo = f"anh/{trial}-{arm}-{CARDS[scenario]}.png"
        page.screenshot(path=output / photo, full_page=True, caret="hide")
        if reading:
            try:
                link = page.locator("#result-content .source-line a:visible").first
                with page.expect_popup() as opened:
                    link.click()
                opened.value.wait_for_url(re.compile(r"/van-ban/[^/]+\.pdf(?:#.*)?$"))
                opened_source = "van-ban/" + opened.value.url.split("/van-ban/")[-1]
            except Error as exc:
                source_error = str(exc).splitlines()[0]
        context.close()
    return {"trial": trial, "arm": arm, "scenario": scenario, "actions": actions, "reading": reading,
            "screenshot": photo, "opened_source": opened_source, "source_error": source_error,
            "remote_requests": remote, "errors": errors}


def score(row: dict) -> list:
    actions = row["actions"]
    times = {event["action"]: event["ms"] for event in actions}
    technical_error = bool(row["errors"] or row["remote_requests"])
    pointed = "point" in times
    correct = pointed and first_passage_is_correct(row["scenario"], row["reading"])
    passed = correct and times["point"] <= 180_000 and not technical_error
    status = "đạt" if passed else "kết luận sai" if pointed else "chưa chỉ được căn cứ"
    if technical_error:
        status = "lỗi kỹ thuật"
    elif pointed and times["point"] > 180_000:
        status = "hết giờ sau gửi"
    selected = next((i for i, event in enumerate(actions) if event["action"] == "choose_cohort"), None)
    submitted = next((i for i, event in enumerate(actions) if event["action"] == "send_question"), None)
    prompt = "không hỏi khóa" if selected is None else (
        "chọn khóa trước gửi" if submitted is None or selected < submitted else "chọn khóa sau gửi")
    count = sum(event["action"] != "point" for event in actions)
    row.update(first_correct=correct, passed=passed, outcome=status, navigation_actions=count, cohort_prompt=prompt)
    return [row["trial"], row["arm"], row["scenario"],
            f"{times['send_question'] / 1000:.4f}" if submitted is not None else "",
            int(correct), int(passed), f"{times['point'] / 1000:.4f}" if passed else "", status,
            row["reading"].get("reference", ""), f"Mô phỏng Chrome · {prompt} · {count} thao tác"]


def run(archive: Path, output: Path, seed: int) -> None:
    if output.exists():
        raise FileExistsError(f"Choose a new directory: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temp, sync_playwright() as pw:
        kit, staged = Path(temp) / "kit", Path(temp) / "observation"
        (staged / "anh").mkdir(parents=True)
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(kit)
        header = ["Mã lượt", "Mẫu", "Tình huống", "Giây đến lần gửi đầu", "Căn cứ đầu đúng (1/0)",
                  "Đạt trong 180 giây (1/0)", "Giây đến căn cứ đúng", "Kết thúc",
                  "Điều/Khoản đã mở", "Thao tác mô phỏng"]
        plans = [(arm, scenario) for scenario in CARDS for arm in ("A", "B")]
        random.Random(seed).shuffle(plans)
        browser = pw.chromium.launch(channel="chrome")
        report = {"simulation": True, "human_participants": 0, "utc": datetime.now(timezone.utc).isoformat(),
                  "browser": browser.version, "playwright": version("playwright"), "python": platform.python_version(),
                  "viewport": VIEWPORT, "offline": True, "seed": seed, "archive_sha256": sha256(archive.read_bytes()).hexdigest(),
                  "runner_sha256": sha256(Path(__file__).read_bytes()).hexdigest(), "trials": []}
        for number, (arm, scenario) in enumerate(plans, start=1):
            report["trials"].append(observe(browser, kit, staged, f"MP-{number:02}", arm, scenario))
        browser.close()
        with (staged / "phieu-quan-sat-mo-phong.tsv").open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file, delimiter="\t", lineterminator="\n")
            writer.writerow(header)
            writer.writerows(score(row) for row in report["trials"])
        (staged / "nhat-ky.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        evidence = Path(temp) / "bang-chung-sau-luot.zip"
        with zipfile.ZipFile(evidence, "w", zipfile.ZIP_DEFLATED) as bundle:
            for path in sorted(staged.rglob("*")):
                if path.is_file():
                    bundle.write(path, path.relative_to(staged))
        evidence.rename(staged / evidence.name)
        staged.rename(output)
    print(f"{sum(row['passed'] for row in report['trials'])}/{len(plans)} simulated tasks passed. Evidence: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", required=True, type=Path, help="New folder, separate from human observation sheets")
    parser.add_argument("--seed", default=20261126, type=int)
    args = parser.parse_args()
    run(args.archive, args.output, args.seed)
