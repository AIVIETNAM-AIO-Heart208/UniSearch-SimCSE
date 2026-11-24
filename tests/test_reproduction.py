"""Protect published results and reject incomplete reproduction inputs."""

import hashlib
import io
import json
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

from experiments.reproduction import run_r1


@pytest.mark.parametrize("exp", ["R1", "R2", "R3"])
def test_published_scores_match_evaluator_log(exp):
    records = run_r1.HERE / "results" / exp
    scores = run_r1.parse_sts_table((records / "eval_log.txt").read_text(encoding="utf-8"))
    metrics = json.loads((records / "metrics.json").read_text())
    assert scores == metrics["scores"]
    assert run_r1.EXPERIMENTS[exp]["revision"] in (records / "env.txt").read_text()
    report = (run_r1.ROOT / "docs/report/sections/results.tex").read_text(encoding="utf-8")
    row, = (line for line in report.splitlines() if "&" in line and f"results/{exp}/metrics.json" in line)
    assert f"& {metrics['ref_paper']['Avg.']:.2f} & {scores['Avg.']:.2f} " in row


@pytest.mark.parametrize("row", [["0"] * 7, ["nan"] * 8, ["inf"] * 8])
def test_incomplete_or_nonfinite_sts_table_is_rejected(row):
    header = "| " + " | ".join(run_r1.TASKS + ["Avg."]) + " |"
    with pytest.raises(ValueError, match="Invalid STS scores"):
        run_r1.parse_sts_table(header + "\n| " + " | ".join(row) + " |")


def test_only_verified_data_is_installed(tmp_path, monkeypatch):
    name = "STS/test.csv"
    payload = b"dataset"
    archive = tmp_path / "fixture.tar"
    with tarfile.open(archive, "w") as tar:
        member = tarfile.TarInfo(name)
        member.size = len(payload)
        tar.addfile(member, io.BytesIO(payload))
    monkeypatch.setattr(run_r1, "SIMCSE_DIR", tmp_path)
    monkeypatch.setattr(run_r1, "sts_inputs", lambda: [name])
    monkeypatch.setattr(run_r1, "download", lambda url, dest, status: dest.write_bytes(archive.read_bytes()))
    manifest = name.encode() + b"\0" + hashlib.sha256(payload).digest()
    monkeypatch.setattr(run_r1, "STS_INPUTS_SHA256", hashlib.sha256(manifest).hexdigest())
    target = tmp_path / "SentEval/data/downstream" / name
    target.parent.mkdir(parents=True)
    target.write_bytes(b"incomplete")
    with pytest.raises(RuntimeError, match="archive SHA-256"):
        run_r1.ensure_senteval_data(lambda message: None)
    assert target.read_bytes() == b"incomplete"
    monkeypatch.setattr(run_r1, "SENTEVAL_SHA256", hashlib.sha256(archive.read_bytes()).hexdigest())
    run_r1.ensure_senteval_data(lambda message: None)
    assert target.read_bytes() == payload


def test_contradictory_sts_average_is_rejected():
    header = "| " + " | ".join(run_r1.TASKS + ["Avg."]) + " |"
    with pytest.raises(ValueError, match="STS average"):
        run_r1.parse_sts_table(header + "\n|" + "|".join(["0.00"] * 7 + ["81.58"]) + "|")


def test_zip_checkout_marker_does_not_verify_modified_code(tmp_path, monkeypatch):
    monkeypatch.setattr(run_r1, "SIMCSE_DIR", tmp_path)
    (tmp_path / "COMMIT").write_text(run_r1.SIMCSE_COMMIT)
    (tmp_path / "evaluation.py").write_text("# local edits\n")
    with pytest.raises(RuntimeError, match="evaluation source"):
        run_r1.ensure_simcse(lambda _: None)


def test_failed_reruns_preserve_published_files(tmp_path, monkeypatch):
    published = tmp_path / "experiments/reproduction/results/R1"
    published.mkdir(parents=True)
    sentinel = published / "status.txt"
    sentinel.write_text("published")
    monkeypatch.setattr(run_r1, "ROOT", tmp_path)
    monkeypatch.setattr(run_r1, "HERE", published.parents[1])

    def offline(status):
        raise RuntimeError("offline")

    monkeypatch.setattr(run_r1, "ensure_simcse", offline)
    for flags in ([], [], ["--model", "example"]):
        monkeypatch.setattr(sys, "argv", ["run_r1.py", *flags])
        with pytest.raises(RuntimeError, match="offline"):
            run_r1.main()
    assert sentinel.read_text() == "published"
    runs = tmp_path / "outputs/reproduction"
    assert len(list(runs.glob("R1-*/status.txt"))) == 2
    assert len(list(runs.glob("debug-R1-*/status.txt"))) == 1


@pytest.mark.parametrize("debug", [False, True])
def test_runner_records_the_checkpoint_it_evaluates(tmp_path, monkeypatch, debug):
    monkeypatch.setattr(run_r1, "ROOT", tmp_path)
    monkeypatch.setattr(run_r1, "ensure_simcse", lambda status: run_r1.SIMCSE_COMMIT)
    monkeypatch.setattr(run_r1, "ensure_venv", lambda *args: Path(sys.executable))
    monkeypatch.setattr(run_r1, "ensure_senteval_data", lambda status: None)
    config = run_r1.EXPERIMENTS["R1"]
    path = tmp_path / "checkpoint with spaces" / config["revision"]
    path.mkdir(parents=True)
    monkeypatch.setattr(sys, "argv", ["run_r1.py", "--model", str(path)] if debug else ["run_r1.py"])
    monkeypatch.setattr(run_r1, "venv_info", lambda py: dict.fromkeys(
        ["torch", "transformers", "numpy", "scipy", "scikit_learn"], "fixture"))

    def check_output(cmd, **kwargs):
        if "snapshot_download" in cmd[2]:
            assert not debug and cmd[3:5] == [config["model"], config["revision"]]
            return str(path)
        return "pytest==8.0\n"

    monkeypatch.setattr(run_r1.subprocess, "check_output", check_output)
    saved = run_r1.HERE / "results/R1/eval_log.txt"

    def evaluate(cmd, log, **kwargs):
        assert cmd[1:4] == ["evaluation.py", "--model_name_or_path", str(path)]
        result = saved.read_text(encoding="utf-8")
        log.write(result)
        return result

    monkeypatch.setattr(run_r1, "run", evaluate)
    assert run_r1.main() == 0
    result, = (tmp_path / "outputs/reproduction").glob("*/metrics.json")
    metrics = json.loads(result.read_text())
    assert metrics["scores"]["Avg."] == 81.58
    if debug:
        assert metrics["exp"] == "debug-R1" and "reproduced_within_tolerance" not in metrics
    else:
        assert metrics["model_revision"] == config["revision"] and metrics["reproduced_within_tolerance"]


def test_markdown_checker_supports_unicode_paths_with_spaces(tmp_path):
    script = Path(__file__).resolve().parents[1] / "tools/check_docs.py"
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    name = "Résumé file.md"
    (tmp_path / name).write_text("# Heading\n", encoding="utf-8")
    index = tmp_path / "index.md"
    index.write_text(f"[link](<{name}#heading>)", encoding="utf-8")
    subprocess.run(["git", "add", "--", name, "index.md"], cwd=tmp_path, check=True)
    cmd = [sys.executable, "-X", "utf8", str(script)]
    subprocess.run(cmd, cwd=tmp_path, check=True)
    index.write_text("[link](<missing page.md>)", encoding="utf-8")
    assert subprocess.run(cmd, cwd=tmp_path).returncode == 1
