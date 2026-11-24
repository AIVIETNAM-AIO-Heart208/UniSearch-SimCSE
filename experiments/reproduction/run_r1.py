r"""Reproduce SimCSE STS results with the official code at a pinned commit.

Usage (from the repo root, Python 3.9-3.11 to create the venv):
    python experiments/reproduction/run_r1.py            # R1: sup-simcse-bert-base-uncased, pooler cls
    python experiments/reproduction/run_r1.py --exp R2   # unsup-simcse-bert-base-uncased, cls_before_pooler
    python experiments/reproduction/run_r1.py --exp R3   # bert-base-uncased (no fine-tuning), avg_first_last
On Windows: experiments\reproduction\run_r1.bat [R1|R2|R3]

What it does:
  1. Get princeton-nlp/SimCSE at commit 235f89e into experiments/reproduction/SimCSE (GitHub zip if missing).
  2. Create .venv-repro (repo root) and install experiments/reproduction/requirements-r1.txt.
  3. Verify the STS inputs and restore them from the pinned SentEval archive if needed.
  4. Run the official evaluation.py (--task_set sts --mode test).
  5. Save eval_log.txt, metrics.json, env.txt, pip_freeze.txt and status.txt in a fresh outputs/reproduction/ directory.

Only the Python standard library is used here, so it runs before the venv exists.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

if __package__:
    from .run_output import create_run_dir
else:
    from run_output import create_run_dir

HERE = Path(__file__).resolve().parent          # experiments/reproduction
ROOT = HERE.parents[1]                          # repo root
SIMCSE_DIR = HERE / "SimCSE"
SIMCSE_COMMIT = "235f89e0244b23673b69fbbc4a1cd9868c5a5c24"
EVALUATOR_SHA256 = "f020a0747c773b7f0c412c18a1e4fb237392d3da0321a3974ba665715469dd1a"
SIMCSE_ZIP = f"https://github.com/princeton-nlp/SimCSE/archive/{SIMCSE_COMMIT}.zip"
SENTEVAL_REVISION = "e145e8bb659b2aa2669f32ef79cb4cdef6c58fef"
SENTEVAL_TAR = f"https://huggingface.co/datasets/princeton-nlp/datasets-for-simcse/resolve/{SENTEVAL_REVISION}/senteval.tar"
SENTEVAL_SHA256 = "bc43c148f7be97471c78fc4255399d3158cb99dfe8f2221999c918338b138c38"
STS_INPUTS_SHA256 = "7872ce7a0841174929c9dbad56cd9ee6a6934c63f26508a463dbfd686203e54a"
REQ_FILE = HERE / "requirements-r1.txt"
TASKS = ["STS12", "STS13", "STS14", "STS15", "STS16", "STSBenchmark", "SICKRelatedness"]

# Reference numbers (Spearman x 100, "all" setting).
# README of SimCSE @ 235f89e (evaluation section) and paper Table 5.
EXPERIMENTS = {
    "R1": {
        "model": "princeton-nlp/sup-simcse-bert-base-uncased",
        "revision": "2d82fab19ac3a73a20dd20333d27eb8a52d6e97f",
        "pooler": "cls",
        "ref_readme": [75.30, 84.67, 80.19, 85.40, 80.82, 84.26, 80.39, 81.58],
        "ref_paper": [75.30, 84.67, 80.19, 85.40, 80.82, 84.25, 80.39, 81.57],
    },
    "R2": {
        "model": "princeton-nlp/unsup-simcse-bert-base-uncased",
        "revision": "218baf6bc48c463a53f5b4e1c568299537fab124",
        "pooler": "cls_before_pooler",
        "ref_readme": None,  # README lists only the average (76.25)
        "ref_paper": [68.40, 82.41, 74.38, 80.91, 78.56, 76.85, 72.23, 76.25],
    },
    "R3": {
        "model": "bert-base-uncased",
        "revision": "86b5e0934494bd15c9632b12f734a8a67f723594",
        "pooler": "avg_first_last",
        "ref_readme": None,
        "ref_paper": [39.70, 59.38, 49.67, 66.03, 66.19, 53.87, 62.06, 56.70],
    },
}
TOLERANCE = 0.5  # max |diff| on the average vs reference to call it "reproduced"


def now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


class Status:
    def __init__(self, out_dir: Path):
        self.path = out_dir / "status.txt"
        self.path.write_text("", encoding="utf-8")

    def __call__(self, msg: str):
        line = f"[{now()}] {msg}"
        print(line, flush=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def venv_python(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def run(cmd, log=None, **kw):
    """Run a command, streaming output to console (and to `log` if given)."""
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace", **kw)
    out = []
    for line in proc.stdout:
        print(line, end="", flush=True)
        out.append(line)
        if log is not None:
            log.write(line)
            log.flush()
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(map(str, cmd))}")
    return "".join(out)


def download(url: str, dest: Path, status: Status):
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url, timeout=90) as r, tmp.open("wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        done, last = 0, 0.0
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            if time.time() - last > 15:
                pct = f"{100 * done / total:.0f}%" if total else "?"
                status(f"  downloading {dest.name}: {done / 1e6:.0f} MB ({pct})")
                last = time.time()
    tmp.replace(dest)
    status(f"  downloaded {dest.name}: {dest.stat().st_size / 1e6:.0f} MB")


def simcse_commit() -> str:
    if (SIMCSE_DIR / ".git").exists():
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=SIMCSE_DIR, text=True).strip()
    marker = SIMCSE_DIR / "COMMIT"
    return marker.read_text().strip() if marker.exists() else "unknown"


def verify_evaluator(directory: Path) -> None:
    """Verify the same Python sources for Git and ZIP checkouts, allowing CRLF."""
    files = [directory / "evaluation.py", *(directory / "SentEval/senteval").rglob("*.py")]
    digest = hashlib.sha256()
    for path in sorted(files, key=lambda p: p.relative_to(directory).as_posix()):
        name = path.relative_to(directory).as_posix()
        content = path.read_bytes().replace(b"\r\n", b"\n")
        digest.update(name.encode() + b"\0" + hashlib.sha256(content).digest())
    if digest.hexdigest() != EVALUATOR_SHA256:
        raise RuntimeError("SimCSE evaluation source differs from the pinned commit")


def ensure_simcse(status: Status):
    if (SIMCSE_DIR / "evaluation.py").exists():
        status(f"SimCSE code present at {SIMCSE_DIR} (commit {simcse_commit()})")
    else:
        status("Downloading SimCSE source at the pinned commit")
        SIMCSE_DIR.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=SIMCSE_DIR.parent) as tmp:
            zpath = Path(tmp) / "simcse.zip"
            download(SIMCSE_ZIP, zpath, status)
            with zipfile.ZipFile(zpath) as archive:
                archive.extractall(tmp)
            source = Path(tmp) / f"SimCSE-{SIMCSE_COMMIT}"
            verify_evaluator(source)
            (source / "COMMIT").write_text(SIMCSE_COMMIT + "\n")
            if not (SIMCSE_DIR / "evaluation.py").exists():
                source.rename(SIMCSE_DIR)
    commit = simcse_commit()
    if commit != SIMCSE_COMMIT:
        raise RuntimeError(f"SimCSE commit is {commit}, expected {SIMCSE_COMMIT}")
    verify_evaluator(SIMCSE_DIR)
    return commit


def ensure_venv(venv: Path, base_python: str, skip_install: bool, status: Status):
    py = venv_python(venv)
    created = not py.exists()
    if created:
        ver = subprocess.check_output([base_python, "-c", "import sys;print('%d.%d' % sys.version_info[:2])"], text=True).strip()
        major, minor = map(int, ver.split("."))
        if not (major == 3 and 9 <= minor <= 11):
            raise RuntimeError(
                f"Base Python is {ver}; need 3.9-3.11 (SentEval needs numpy<1.24, which has no wheels for newer Python). "
                "Pass --python <path to python3.10/3.11>, e.g. a conda env.")
        status(f"Creating venv {venv} with Python {ver}")
        subprocess.check_call([base_python, "-m", "venv", str(venv)])
    if skip_install:
        status("Skipping package install (--skip-install)")
        return py
    status("Checking pinned packages with pip and installing missing or mismatched versions")
    with (venv / "pip_install_log.txt").open("w", encoding="utf-8") as log:
        if created:
            run([str(py), "-m", "pip", "install", "--upgrade", "pip"], log=log)
        run([str(py), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(REQ_FILE)], log=log)
    return py


def sts_inputs() -> list[str]:
    # The files opened by the pinned SentEval STS loaders (including train/dev).
    subsets = [
        ("MSRpar", "MSRvid", "SMTeuroparl", "surprise.OnWN", "surprise.SMTnews"),
        ("FNWN", "headlines", "OnWN"),
        ("deft-forum", "deft-news", "headlines", "images", "OnWN", "tweet-news"),
        ("answers-forums", "answers-students", "belief", "headlines", "images"),
        ("answer-answer", "headlines", "plagiarism", "postediting", "question-question"),
    ]
    names = [f"STS/STS{year}-en-test/STS.{kind}.{subset}.txt"
             for year, group in enumerate(subsets, 12) for subset in group for kind in ("input", "gs")]
    names.extend(f"STS/STSBenchmark/sts-{split}.csv" for split in ("train", "dev", "test"))
    return sorted(names + ["SICK/SICK_train.txt", "SICK/SICK_trial.txt", "SICK/SICK_test_annotated.txt"])


def sts_data_matches(directory: Path, names: list[str]) -> bool:
    digest = hashlib.sha256()
    for name in names:
        file = directory / name
        if not file.is_file():
            return False
        digest.update(name.encode() + b"\0" + hashlib.sha256(file.read_bytes()).digest())
    return digest.hexdigest() == STS_INPUTS_SHA256


def ensure_senteval_data(status: Status):
    ddir = SIMCSE_DIR / "SentEval" / "data" / "downstream"
    names = sts_inputs()
    if sts_data_matches(ddir, names):
        status("Verified cached SentEval STS inputs")
        return
    ddir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ddir) as tmp:
        staging = Path(tmp)
        tar_path = staging / "senteval.tar"
        download(SENTEVAL_TAR, tar_path, status)
        if hashlib.sha256(tar_path.read_bytes()).hexdigest() != SENTEVAL_SHA256:
            raise RuntimeError("SentEval archive SHA-256 mismatch")
        with tarfile.open(tar_path) as archive:
            for name in names:
                member = archive.getmember(name)
                if not member.isfile():
                    raise ValueError(f"Expected a regular file: {name}")
                target = staging / name
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
        if not sts_data_matches(staging, names):
            raise RuntimeError("SentEval STS input SHA-256 mismatch")
        for name in names:
            target = ddir / name
            target.parent.mkdir(parents=True, exist_ok=True)
            (staging / name).replace(target)


def parse_sts_table(log_text: str):
    """Return the 8 numbers (7 STS tasks + Avg.) from evaluation.py's final STS table."""
    lines = log_text.splitlines()
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].startswith("|") and lines[i].strip("|").split("|", 1)[0].strip() == TASKS[0]:
            header = [c.strip() for c in lines[i].strip("|").split("|")]
            if header != TASKS + ["Avg."]:
                raise ValueError("Unexpected STS table columns")
            for row in lines[i + 1:i + 4]:
                if row.startswith("|"):
                    vals = [c.strip() for c in row.strip("|").split("|")]
                    scores = list(map(float, vals))
                    if len(scores) != len(header) or not all(math.isfinite(v) and abs(v) <= 100 for v in scores):
                        raise ValueError("Invalid STS scores")
                    # evaluation.py averages the seven displayed (already rounded) scores.
                    if scores[-1] != round(sum(scores[:-1]) / len(TASKS), 2):
                        raise ValueError("STS average differs from the seven task scores")
                    return dict(zip(header, scores))
            raise ValueError("Missing scores in the final STS table")
    raise RuntimeError("Could not find the STS result table in the evaluation log")


def venv_info(py: Path):
    code = r"""
import json, platform, sys
info = {"python": sys.version.split()[0]}
import torch, transformers, numpy, scipy, sklearn
info.update(torch=torch.__version__, transformers=transformers.__version__, numpy=numpy.__version__,
            scipy=scipy.__version__, scikit_learn=sklearn.__version__,
            cuda_available=torch.cuda.is_available(), torch_threads=torch.get_num_threads())
info["device"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"
print(json.dumps(info))
"""
    out = subprocess.check_output([str(py), "-c", code], text=True)
    return json.loads(out.strip().splitlines()[-1])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--exp", default="R1", choices=sorted(EXPERIMENTS))
    ap.add_argument("--python", default=sys.executable, help="Base Python 3.9-3.11 used to create the venv")
    ap.add_argument("--venv", default=str(ROOT / ".venv-repro"))
    ap.add_argument("--skip-install", action="store_true")
    ap.add_argument("--model", help="Override model (debugging only; result is then not R1/R2/R3)")
    args = ap.parse_args()

    exp = dict(EXPERIMENTS[args.exp])
    run_id = f"debug-{args.exp}" if args.model else args.exp
    out_dir = create_run_dir(ROOT, run_id)
    status = Status(out_dir)
    t0 = time.time()
    status(f"Start {run_id}: model={args.model or exp['model']} pooler={exp['pooler']} output={out_dir.relative_to(ROOT)}")
    try:
        commit = ensure_simcse(status)
        py = ensure_venv(Path(args.venv).resolve(), args.python, args.skip_install, status)
        ensure_senteval_data(status)

        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        env.setdefault("HF_HOME", str(ROOT / ".cache" / "huggingface"))
        if args.model:
            local = Path(args.model)
            model_path = str(local.resolve()) if local.exists() else args.model
        else:
            weights = "model.safetensors" if args.exp == "R3" else "pytorch_model.bin"
            code = ("from huggingface_hub import snapshot_download; import sys; "
                    "print(snapshot_download(sys.argv[1], revision=sys.argv[2], "
                    "allow_patterns=['*.json','vocab.txt',sys.argv[3]]))")
            model_path = subprocess.check_output([str(py), "-c", code, exp["model"], exp["revision"], weights],
                                                 text=True, encoding="utf-8", env=env).strip()
        cmd = [str(py), "evaluation.py", "--model_name_or_path", model_path, "--pooler", exp["pooler"],
               "--task_set", "sts", "--mode", "test"]
        status("Running: " + " ".join(cmd[1:]) + f"  (cwd={SIMCSE_DIR})")
        t_eval = time.time()
        with (out_dir / "eval_log.txt").open("w", encoding="utf-8") as log:
            log_text = run(cmd, log=log, cwd=SIMCSE_DIR, env=env)
        eval_seconds = round(time.time() - t_eval, 1)

        table = parse_sts_table(log_text)
        ours = [table[t] for t in TASKS] + [table["Avg."]]
        names = TASKS + ["Avg."]
        metrics = {"exp": run_id, "model": args.model or exp["model"], "pooler": exp["pooler"],
                   "metric": "Spearman x100, 'all' setting, test", "scores": dict(zip(names, ours))}
        for key in (() if args.model else ("ref_readme", "ref_paper")):
            ref = exp[key]
            if ref:
                diffs = [round(a - b, 2) for a, b in zip(ours, ref)]
                metrics[key] = dict(zip(names, ref))
                metrics["diff_vs_" + key[4:]] = dict(zip(names, diffs))
        main_ref = exp["ref_readme"] or exp["ref_paper"]
        if not args.model:
            metrics["model_revision"] = exp["revision"]
            metrics["avg_abs_diff_vs_main_ref"] = round(abs(ours[-1] - main_ref[-1]), 2)
            metrics["reproduced_within_tolerance"] = metrics["avg_abs_diff_vs_main_ref"] <= TOLERANCE
            metrics["tolerance"] = TOLERANCE
        metrics["eval_seconds"] = eval_seconds
        info = venv_info(py)
        freeze = subprocess.check_output([str(py), "-c", (
            "import importlib.metadata as m;"
            "print('\\n'.join(sorted(f\"{d.metadata['Name']}=={d.version}\" for d in m.distributions())))")],
            text=True)
        (out_dir / "pip_freeze.txt").write_text(freeze, encoding="utf-8")
        env_lines = [
            f"experiment: {run_id}",
            f"finished: {now()}",
            f"total_seconds: {round(time.time() - t0, 1)}",
            f"eval_seconds: {eval_seconds}",
            f"evaluation argv (cwd=experiments/reproduction/SimCSE): {json.dumps(cmd[1:], ensure_ascii=False)}",
            f"simcse_repo: https://github.com/princeton-nlp/SimCSE @ {commit}",
            f"model: {args.model or exp['model']} @ {exp['revision'] if not args.model else 'debug override'}",
            f"senteval_revision: {SENTEVAL_REVISION} | archive_sha256: {SENTEVAL_SHA256}",
            f"os: {platform.platform()}",
            f"machine: {platform.machine()} | cpu: {platform.processor() or 'n/a'} | logical_cpus: {os.cpu_count()}",
            f"device: {info.get('device')} | cuda_available: {info.get('cuda_available')} | torch_threads: {info.get('torch_threads')}",
            f"python (venv): {info.get('python')}",
            "packages: " + ", ".join(f"{k}={info[k]}" for k in ("torch", "transformers", "numpy", "scipy", "scikit_learn")),
            "deviation_from_repo_requirements: repo pins transformers==4.2.1, scipy==1.5.4, scikit-learn==0.24.0 "
            "and recommends torch 1.7.1; this run uses the versions above (see docs/application/PROJECT.md 4.5). "
            "numpy<1.24 is required by SentEval's loadFile (ragged np.array).",
            "full package list: pip_freeze.txt",
        ]
        (out_dir / "env.txt").write_text("\n".join(env_lines) + "\n", encoding="utf-8")
        (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        verdict = "DEBUG" if args.model else ("REPRODUCED" if metrics["reproduced_within_tolerance"] else "DIFFERS")
        status(f"DONE {run_id}: avg={ours[-1]:.2f} ({verdict})")
        return int(verdict == "DIFFERS")
    except Exception as e:
        status(f"FAILED: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="backslashreplace")
    sys.exit(main())
