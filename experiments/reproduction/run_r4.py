"""R4: measure how closely our InfoNCE matches the references and record it.

Usage (from the repo root; needs torch and pytest):
    python experiments/reproduction/run_r4.py

Writes experiments/reproduction/results/R4/:
    metrics.json    max |ours - ref| per reference and dtype, with the grid and seed
    env.txt         interpreter and package versions
    pytest_log.txt  output of `pytest tests/test_infonce.py`

The grid, seed and tolerances are imported from tests/test_infonce.py, so the
recorded numbers describe exactly the cases the tests assert on.
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "results" / "R4"
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]

import torch  # noqa: E402

import test_infonce as t  # noqa: E402  # pyright: ignore[reportMissingImports]
from infonce_reference import Similarity, cl_forward_loss, naive_loss  # noqa: E402  # pyright: ignore[reportMissingImports]
from simcse_lab.model.infonce import _cosine_logits, infonce_loss  # noqa: E402


def max_diff(cases, reference, dtype):
    worst, worst_case = 0.0, None
    for case in cases:
        n, d, tau, w, hard = case
        z1, z2, z3 = t.make_batch(n, d, hard=hard, dtype=dtype)
        ours = infonce_loss(z1, z2, z3, temperature=tau, hard_negative_weight=w).item()
        ref = reference(z1, z2, z3, temperature=tau, hard_negative_weight=w).item()
        diff = abs(ours - ref)
        if diff > worst:
            worst, worst_case = diff, t.case_id(case)
    return {"max_abs_diff": worst, "worst_case": worst_case, "n_cases": len(cases)}


def split(cases):
    """Separate unsupervised, supervised with float32-exact w, and the rest."""
    exact = {0.0, 1.0, -0.5}
    return {
        "unsup": [c for c in cases if not c[4]],
        "sup_w_exact_in_fp32": [c for c in cases if c[4] and c[3] in exact],
        "sup_w_log_half_or_log_two": [c for c in cases if c[4] and c[3] not in exact],
    }


def cl_forward_float64_weights(z1, z2, z3=None, *, temperature, hard_negative_weight):
    """cl_forward's loss with the weight matrix built in z1's dtype (diagnostic only).

    Isolates the one float32 step in cl_forward's float64 path: if this variant
    matches infonce_loss to ~1e-15, that step explains the remaining gap.
    """
    sim = Similarity(temperature)
    logits = sim(z1.unsqueeze(1), z2.unsqueeze(0))
    n = z1.size(0)
    if z3 is not None:
        hard = sim(z1.unsqueeze(1), z3.unsqueeze(0))
        hard = hard + hard_negative_weight * torch.eye(n, dtype=hard.dtype)
        logits = torch.cat([logits, hard], 1)
    return torch.nn.CrossEntropyLoss()(logits, torch.arange(n))


def float32_breakdown(cases):
    """Where the float32 gap starts: the cosine logits or the cross-entropy step."""
    logit_gap = head_gap = 0.0
    for n, d, tau, _, _ in cases:
        z1, z2, _ = t.make_batch(n, d, hard=False, dtype=torch.float32)
        ref_logits = Similarity(tau)(z1.unsqueeze(1), z2.unsqueeze(0))
        logit_gap = max(logit_gap, (_cosine_logits(z1, z2, tau) - ref_logits).abs().max().item())
        # Same logits, two loss heads: logsumexp - positive vs CrossEntropyLoss.
        ours = (torch.logsumexp(ref_logits, 1) - ref_logits.diagonal()).mean()
        head_gap = max(head_gap, abs(ours.item() - torch.nn.CrossEntropyLoss()(ref_logits, torch.arange(n)).item()))
    return {"max_abs_logit_gap": logit_gap, "max_abs_loss_head_gap_same_logits": head_gap}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    results = {}
    for name, ref, cases, dtype in [
        ("naive_loop_float64", naive_loss, t.SMALL, torch.float64),
        ("cl_forward_float64", cl_forward_loss, t.SMALL + t.LARGE, torch.float64),
        ("cl_forward_float32", cl_forward_loss, t.SMALL, torch.float32),
    ]:
        results[name] = {group: max_diff(cs, ref, dtype) for group, cs in split(cases).items()}
        print(name, json.dumps(results[name], indent=1))
    log_w = [c for c in t.SMALL + t.LARGE if c[4] and c[3] not in {0.0, 1.0, -0.5}]
    diagnostics = {
        "cl_forward_float64_with_float64_weights_log_w": max_diff(log_w, cl_forward_float64_weights, torch.float64),
        "float32_breakdown_unsup_cases": float32_breakdown([c for c in t.SMALL if not c[4]]),
    }
    print("diagnostics", json.dumps(diagnostics, indent=1))
    measure_seconds = time.perf_counter() - start

    log = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_infonce.py", "-q", "-p", "no:cacheprovider"],
        cwd=ROOT, capture_output=True, text=True,
    )
    (OUT / "pytest_log.txt").write_text(log.stdout + log.stderr, encoding="utf-8")
    summary = log.stdout.strip().splitlines()[-1] if log.stdout.strip() else ""

    metrics = {
        "experiment": "R4",
        "description": "infonce_loss vs a naive loop over SimCSE Eq. 4 / Eq. 8 (alpha = 1 is Eq. 5) "
                       "and vs the verbatim cl_forward loss block (SimCSE @235f89e)",
        "acceptance": {"atol_float64": t.ATOL, "atol_float32": t.ATOL_FP32},
        "grid": {
            "batch_sizes": list(t.BATCH_SIZES),
            "large_batch_sizes_cl_forward_only": list(t.LARGE_BATCH_SIZES),
            "dims": list(t.DIMS),
            "temperatures": list(t.TEMPERATURES),
            "hard_negative_weights_log_alpha": list(t.HARD_NEGATIVE_WEIGHTS),
            "inputs": "z1 ~ N(0, I); z2 = z1 + 0.8 * N(0, I); z3 = z1 + 1.0 * N(0, I)",
        },
        "seed": t.SEED,
        "results": results,
        "diagnostics": diagnostics,
        "pytest": {"returncode": log.returncode, "summary": summary},
        "measure_seconds": round(measure_seconds, 1),
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    import pytest

    (OUT / "env.txt").write_text(
        "\n".join([
            "experiment: R4",
            f"finished: {datetime.now().astimezone().isoformat(timespec='seconds')}",
            "command (cwd=repo root): python experiments/reproduction/run_r4.py",
            "reference: https://github.com/princeton-nlp/SimCSE @ 235f89e0244b23673b69fbbc4a1cd9868c5a5c24, "
            "simcse/models.py L35-46 and L193-211 (copied into tests/infonce_reference.py)",
            f"os: {platform.platform()}",
            f"python: {platform.python_version()} ({sys.executable})",
            f"packages: torch={torch.__version__}, pytest={pytest.__version__}",
            "note: system interpreter, not .venv-repro from R1-R3; R4 needs only torch and pytest on CPU.",
        ]) + "\n",
        encoding="utf-8",
    )
    print(f"pytest: {summary} (returncode {log.returncode})")
    # Relative path: the absolute one has Vietnamese characters a cp1252 console cannot print.
    print(f"wrote {OUT.relative_to(ROOT).as_posix()}")
    return log.returncode


if __name__ == "__main__":
    sys.exit(main())
