"""Capture the HCMUS endpoint on the open pilot and paired graduation probes."""

import argparse
import hashlib
import json
import re
from pathlib import Path

from gradio_client import Client

PILOT = Path("data/development/clause-scope-pilot.jsonl")
PROBES = (
    ("conditions", "Điều kiện xét công nhận tốt nghiệp là gì", True),
    ("requirements", "Em cần đáp ứng những điều kiện nào để được xét tốt nghiệp?", True),
    ("graduate", "Muốn tốt nghiệp thì em cần đáp ứng những gì?", True),
    ("procedure", "Khi đủ điều kiện tốt nghiệp thì em nộp hồ sơ thế nào?", False),
    ("authority", "Ai ký quyết định công nhận tốt nghiệp cho sinh viên đủ điều kiện?", False),
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:7860")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--baseline", type=Path, help="Compare against a capture on the same inputs")
    args = parser.parse_args()
    client = Client(args.url, verbose=False)
    settings_tag = re.search(r'<script id="retrieval-settings" type="application/json">([^<]+)</script>',
                             client.config.get("head", ""))
    if not settings_tag:
        parser.error("The running demo does not report its retrieval settings. Launch the current apps/app.py.")
    settings = json.loads(settings_tag[1])
    baseline = None
    pilot_hash = hashlib.sha256(PILOT.read_bytes()).hexdigest()
    if args.output.exists():
        parser.error("Use a new capture path")
    if args.baseline:
        baseline = json.loads(args.baseline.read_bytes())
        if baseline["pilot_sha256"] != pilot_hash or any(baseline[k] != settings[k] for k in ("weight", "threshold")):
            parser.error("The baseline uses different pilot data or retrieval settings")
    cases = []
    for row in map(json.loads, PILOT.read_text(encoding="utf-8").splitlines()):
        gold = row["gold_clause_ids"]
        cohort = "Tra cứu chung"
        edition = re.search(r"(?:quy chế(?: năm)?|bản năm) (2021|2026)\b", row["question"].casefold())
        if edition:
            cohort = "K24" if edition[1] == "2021" else "K26 trở đi"
        cases.append((row["qid"], row["question"], cohort, gold))
    for qid, question, conditions in PROBES:
        for cohort, gold in (("K24", "hcmus-qcdt-2021:dieu-17:khoan-3"),
                             ("K26 trở đi", "hcmus-qcdt-2026:dieu-19:khoan-1")):
            cases.append((qid, question, cohort, [gold] if conditions else []))

    results = []
    for qid, question, cohort, gold in cases:
        html, lexical, notice = client.predict(question, cohort, api_name="/search")
        ref = re.search(r'<span class="reference">([^<]+)</span>', html)[1]
        match = re.fullmatch(r"Quy chế (\d+) · Điều (\d+) · Khoản (\d+)", ref)
        cid = "hcmus-qcdt-{}:dieu-{}:khoan-{}".format(*match.groups()) if match else None
        opened = re.search(r'<details class="topic-panel"( open)?>', html)[1] is not None
        results.append(dict(qid=qid, question=question, cohort=cohort, first=ref, open=opened,
                            gold=gold, correct_open=(opened and cid in gold) if gold else None,
                            response_sha256=hashlib.sha256((html + lexical + notice).encode()).hexdigest()))
    if baseline is not None:
        if len(baseline["results"]) != len(results):
            raise ValueError("Baseline and current case counts differ")
        counts = {"pilot_identical": 0, "control_identical": 0, "conditions_before": 0, "conditions_after": 0}
        for old, new in zip(baseline["results"], results):
            if any(old[k] != new[k] for k in ("qid", "question", "cohort", "gold")):
                raise ValueError("Baseline and current cases differ")
            if new["qid"].startswith("pilot-"):
                counts["pilot_identical"] += old["response_sha256"] == new["response_sha256"]
            elif new["gold"]:
                counts["conditions_before"] += old["correct_open"]
                counts["conditions_after"] += new["correct_open"]
            else:
                counts["control_identical"] += old["response_sha256"] == new["response_sha256"]
        print(json.dumps(counts))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as out:
        json.dump(dict(weight=settings["weight"], threshold=settings["threshold"],
                       pilot_sha256=pilot_hash, results=results), out, ensure_ascii=False, indent=2)
        out.write("\n")


if __name__ == "__main__":
    main()
