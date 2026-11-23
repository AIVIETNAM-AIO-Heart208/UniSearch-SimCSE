"""Reproduce SimCSE STS results with the official code at a pinned commit.

Usage (from the repo root, Python 3.9-3.11 to create the venv):
    python experiments/reproduction/run_r1.py            # R1: sup-simcse-bert-base-uncased, pooler cls
    python experiments/reproduction/run_r1.py --exp R2   # unsup-simcse-bert-base-uncased, cls_before_pooler
    python experiments/reproduction/run_r1.py --exp R3   # bert-base-uncased (no fine-tuning), avg_first_last
On Windows: experiments\reproduction\run_r1.bat [R1|R2|R3]

What it does (each step is skipped if already done):
  1. Get princeton-nlp/SimCSE at commit 235f89e into experiments/reproduction/SimCSE (GitHub zip if missing).
  2. Create .venv-repro (repo root) and install experiments/reproduction/requirements-r1.txt.
  3. Download SentEval STS data (senteval.tar, same URL as SentEval/data/downstream/download_dataset.sh).
  4. Run the official evaluation.py (--task_set sts --mode test).
  5. Save experiments/reproduction/results/<exp>/: eval_log.txt, metrics.json, env.txt, pip_freeze.txt, status.txt.

Only the Python standard library is used here, so it runs before the venv exists.
"""
import argparse
import datetime as dt
import hashlib
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent          # experiments/reproduction
ROOT = HERE.parents[1]                          # repo root
SIMCSE_DIR = HERE / "SimCSE"
SIMCSE_COMMIT = "235f89e0244b23673b69fbbc4a1cd9868c5a5c24"
SIMCSE_ZIP = f"https://github.com/princeton-nlp/SimCSE/archive/{SIMCSE_COMMIT}.zip"
SENTEVAL_TAR = "https://huggingface.co/datasets/princeton-nlp/datasets-for-simcse/resolve/main/senteval.tar"
REQ_FILE = HERE / "requirements-r1.txt"
TASKS = ["STS12", "STS13", "STS14", "STS15", "STS16", "STSBenchmark", "SICKRelatedness"]

# Reference numbers (Spearman x 100, "all" setting).
# README of SimCSE @ 235f89e (evaluation section) and paper Table 5.
EXPERIMENTS = {
    "R1": {
        "model": "princeton-nlp/sup-simcse-bert-base-uncased",
        "pooler": "cls",
        "ref_readme": [75.30, 84.67, 80.19, 85.40, 80.82, 84.26, 80.39, 81.58],
        "ref_paper": [75.30, 84.67, 80.19, 85.40, 80.82, 84.25, 80.39, 81.57],
    },
    "R2": {
        "model": "princeton-nlp/unsup-simcse-bert-base-uncased",
        "pooler": "cls_before_pooler",
        "ref_readme": None,  # README lists only the average (76.25)
        "ref_paper": [68.40, 82.41, 74.38, 80.91, 78.56, 76.85, 72.23, 76.25],
    },
    "R3": {
        "model": "bert-base-uncased",
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
    with urllib.request.urlopen(url) as r, tmp.open("wb") as f:
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
    head = SIMCSE_DIR / ".git" / "HEAD"
    if head.exists():
        ref = head.read_text().strip()
        if ref.startswith("ref:"):
            ref_file = SIMCSE_DIR / ".git" / ref.split(" ", 1)[1]
            ref = ref_file.read_text().strip() if ref_file.exists() else ref
        return ref
    marker = SIMCSE_DIR / "COMMIT"
    return marker.read_text().strip() if marker.exists() else "unknown"


def ensure_simcse(status: Status):
    if (SIMCSE_DIR / "evaluation.py").exists():
        status(f"SimCSE code present at {SIMCSE_DIR} (commit {simcse_commit()})")
    else:
        status("Downloading SimCSE source at the pinned commit")
        SIMCSE_DIR.parent.mkdir(parents=True, exist_ok=True)
        zpath = SIMCSE_DIR.parent / "simcse.zip"
        download(SIMCSE_ZIP, zpath, status)
        with zipfile.ZipFile(zpath) as z:
            z.extractall(SIMCSE_DIR.parent)
        (SIMCSE_DIR.parent / f"SimCSE-{SIMCSE_COMMIT}").rename(SIMCSE_DIR)
        (SIMCSE_DIR / "COMMIT").write_text(SIMCSE_COMMIT + "\n")
        zpath.unlink()
    commit = simcse_commit()
    if commit != SIMCSE_COMMIT:
        raise RuntimeError(f"SimCSE commit is {commit}, expected {SIMCSE_COMMIT}")
    return commit


def ensure_venv(venv: Path, base_python: str, skip_install: bool, status: Status):
    py = venv_python(venv)
    if not py.exists():
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
    req_hash = hashlib.sha256(REQ_FILE.read_bytes()).hexdigest()[:12]
    stamp = venv / f".installed-{req_hash}"
    if stamp.exists():
        status("Packages already installed for current requirements")
        return py
    status("Installing packages (torch CPU wheel ~200 MB, rest ~60 MB)")
    with (venv / "pip_install_log.txt").open("w", encoding="utf-8") as log:
        run([str(py), "-m", "pip", "install", "--upgrade", "pip"], log=log)
        run([str(py), "-m", "pip", "install", "-r", str(REQ_FILE)], log=log)
    stamp.write_text(now())
    return py


def ensure_senteval_data(status: Status):
    ddir = SIMCSE_DIR / "SentEval" / "data" / "downstream"
    needed = [ddir / "STS" / "STSBenchmark" / "sts-test.csv", ddir / "SICK" / "SICK_test_annotated.txt"] + [
        ddir / "STS" / f"STS{y}-en-test" for y in (12, 13, 14, 15, 16)]
    if all(p.exists() for p in needed):
        status("SentEval STS data present")
        return
    status("Downloading SentEval data (senteval.tar)")
    ddir.mkdir(parents=True, exist_ok=True)
    tar_path = ddir / "senteval.tar"
    if not tar_path.exists():
        download(SENTEVAL_TAR, tar_path, status)
    status("Extracting senteval.tar")
    with tarfile.open(tar_path) as t:
        for m in t.getmembers():  # refuse absolute paths / path traversal
            if m.name.startswith(("/", "\\")) or ".." in Path(m.name).parts:
                raise RuntimeError(f"Unsafe path in tar: {m.name}")
        t.extractall(ddir)
    missing = [str(p) for p in needed if not p.exists()]
    if missing:
        raise RuntimeError(f"SentEval data incomplete, missing: {missing}")
    tar_path.unlink()


def parse_sts_table(log_text: str):
    """Return the 8 numbers (7 STS tasks + Avg.) from evaluation.py's final STS table."""
    lines = log_text.splitlines()
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].startswith("|") and "STS12" in lines[i] and "SICKRelatedness" in lines[i]:
            header = [c.strip() for c in lines[i].strip("|").split("|")]
            for row in lines[i + 1:i + 4]:
                if row.startswith("|"):
                    vals = [c.strip() for c in row.strip("|").split("|")]
                    return dict(zip(header, map(float, vals)))
    raise RuntimeError("Could not find the STS result table in the evaluation log")


def venv_info(py: Path, model: str):
    code = r"""
import json, platform, sys
info = {"python": sys.version.split()[0]}
import torch, transformers, numpy, scipy, sklearn
info.update(torch=torch.__version__, transformers=transformers.__version__, numpy=numpy.__version__,
            scipy=scipy.__version__, scikit_learn=sklearn.__version__,
            cuda_available=torch.cuda.is_available(), torch_threads=torch.get_num_threads())
info["device"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"
try:
    from huggingface_hub import HfApi
    info["model_revision"] = HfApi().model_info(sys.argv[1]).sha
except Exception as e:  # offline / no access
    info["model_revision"] = "unknown (%s)" % type(e).__name__
print(json.dumps(info))
"""
    out = subprocess.check_output([str(py), "-c", code, model], text=True)
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
    if args.model:
        exp["model"] = args.model
    out_dir = HERE / "results" / args.exp
    out_dir.mkdir(parents=True, exist_ok=True)
    status = Status(out_dir)
    t0 = time.time()
    status(f"Start {args.exp}: model={exp['model']} pooler={exp['pooler']}")
    try:
        commit = ensure_simcse(status)
        py = ensure_venv(Path(args.venv).resolve(), args.python, args.skip_install, status)
        ensure_senteval_data(status)

        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        env.setdefault("HF_HOME", str(ROOT / ".cache" / "huggingface"))
        cmd = [str(py), "evaluation.py", "--model_name_or_path", exp["model"], "--pooler", exp["pooler"],
               "--task_set", "sts", "--mode", "test"]
        status("Running: " + " ".join(cmd[1:]) + f"  (cwd={SIMCSE_DIR})")
        t_eval = time.time()
        with (out_dir / "eval_log.txt").open("w", encoding="utf-8") as log:
            log_text = run(cmd, log=log, cwd=SIMCSE_DIR, env=env)
        eval_seconds = round(time.time() - t_eval, 1)

        table = parse_sts_table(log_text)
        ours = [table[t] for t in TASKS] + [table["Avg."]]
        names = TASKS + ["Avg."]
        metrics = {"exp": args.exp, "model": exp["model"], "pooler": exp["pooler"],
                   "metric": "Spearman x100, 'all' setting, test", "scores": dict(zip(names, ours))}
        for key in ("ref_readme", "ref_paper"):
            ref = exp[key]
            if ref:
                diffs = [round(a - b, 2) for a, b in zip(ours, ref)]
                metrics[key] = dict(zip(names, ref))
                metrics["diff_vs_" + key[4:]] = dict(zip(names, diffs))
        main_ref = exp["ref_readme"] or exp["ref_paper"]
        metrics["avg_abs_diff_vs_main_ref"] = round(abs(ours[-1] - main_ref[-1]), 2)
        metrics["reproduced_within_tolerance"] = metrics["avg_abs_diff_vs_main_ref"] <= TOLERANCE
        metrics["tolerance"] = TOLERANCE
        metrics["eval_seconds"] = eval_seconds
        (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

        info = venv_info(py, exp["model"])
        freeze = subprocess.check_output([str(py), "-c", (
            "import importlib.metadata as m;"
            "print('\\n'.join(sorted(f\"{d.metadata['Name']}=={d.version}\" for d in m.distributions())))")],
            text=True)
        (out_dir / "pip_freeze.txt").write_text(freeze, encoding="utf-8")
        env_lines = [
            f"experiment: {args.exp}",
            f"finished: {now()}",
            f"total_seconds: {round(time.time() - t0, 1)}",
            f"eval_seconds: {eval_seconds}",
            f"command (cwd=experiments/reproduction/SimCSE): python {' '.join(cmd[1:])}",
            f"simcse_repo: https://github.com/princeton-nlp/SimCSE @ {commit}",
            f"model: {exp['model']} @ {info.get('model_revision')}",
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
        verdict = "REPRODUCED" if metrics["reproduced_within_tolerance"] else "DIFFERS"
        status(f"DONE {args.exp}: avg={ours[-1]:.2f} vs ref {main_ref[-1]:.2f} -> {verdict} (tolerance {TOLERANCE})")
    except Exception as e:
        status(f"FAILED: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    main()
