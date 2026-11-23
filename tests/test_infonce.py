"""R4: check ``infonce_loss`` against the paper equations and the official code.

Acceptance criterion (PROJECT.md section 4.5): absolute difference < 1e-6, in
float64. A float32 run is also checked, with the looser ``ATOL_FP32``: two
correct float32 implementations round differently in the cosine logits (up to
1 / tau = 100 here) and in the cross-entropy step; the measured gap is ~4e-6.

The grid and the seed are shared with ``experiments/reproduction/run_r4.py``,
which writes the measured maximum differences to ``results/R4/metrics.json``.
"""

from __future__ import annotations

import itertools
import math
from pathlib import Path
from typing import Any

import pytest
import torch

import infonce_reference
from infonce_reference import cl_forward_loss, naive_loss
from simcse_lab.model.infonce import infonce_loss

SEED = 0
ATOL = 1e-6  # acceptance criterion, float64
ATOL_FP32 = 5e-5  # ~13x the measured float32 gap (3.7e-6), so other CPUs/BLAS builds do not flake

BATCH_SIZES = (1, 2, 8, 32)
LARGE_BATCH_SIZES = (128, 512)  # cl_forward only: the naive loop is O(N^2) Python
DIMS = (16, 768)
TEMPERATURES = (0.01, 0.05, 0.1, 1.0)
# w = log(alpha). 1.0 and -0.5 are exact in float32; log(0.5) and log(2) are not,
# and cl_forward builds its weight matrix in float32 (torch.tensor of floats).
HARD_NEGATIVE_WEIGHTS = (0.0, 1.0, -0.5, math.log(0.5), math.log(2.0))


def make_batch(n: int, d: int, *, hard: bool, dtype=torch.float64, seed: int = SEED):
    """Anchors z1, positives z2 near z1 and optional hard negatives z3 almost as near.

    The hard negatives must compete with the positive: if they were unrelated to
    z1, at tau = 0.01 the positive logit would dominate by ~1 / tau, the loss
    would underflow to ~0, and a wrongly applied weight would go unnoticed.
    """
    g = torch.Generator().manual_seed(seed)
    z1 = torch.randn(n, d, generator=g, dtype=dtype)
    z2 = z1 + 0.8 * torch.randn(n, d, generator=g, dtype=dtype)
    z3 = z1 + 1.0 * torch.randn(n, d, generator=g, dtype=dtype) if hard else None
    return z1, z2, z3


def grid(batch_sizes):
    """(n, d, tau, w, hard) cases: unsupervised with w = 0, supervised with every w."""
    for n, d, tau in itertools.product(batch_sizes, DIMS, TEMPERATURES):
        yield n, d, tau, 0.0, False
        for w in HARD_NEGATIVE_WEIGHTS:
            yield n, d, tau, w, True


def case_id(case):
    n, d, tau, w, hard = case
    return f"{'sup' if hard else 'unsup'}-N{n}-d{d}-tau{tau}-w{w:.3g}"


SMALL = list(grid(BATCH_SIZES))
LARGE = list(grid(LARGE_BATCH_SIZES))


@pytest.mark.parametrize("case", SMALL, ids=[case_id(c) for c in SMALL])
def test_matches_naive_loop(case):
    n, d, tau, w, hard = case
    z1, z2, z3 = make_batch(n, d, hard=hard)
    ours = infonce_loss(z1, z2, z3, temperature=tau, hard_negative_weight=w)
    ref = naive_loss(z1, z2, z3, temperature=tau, hard_negative_weight=w)
    assert torch.isfinite(ref)
    assert abs(ours.item() - ref.item()) < ATOL


@pytest.mark.parametrize("case", SMALL + LARGE, ids=[case_id(c) for c in SMALL + LARGE])
def test_matches_cl_forward(case):
    n, d, tau, w, hard = case
    z1, z2, z3 = make_batch(n, d, hard=hard)
    ours = infonce_loss(z1, z2, z3, temperature=tau, hard_negative_weight=w)
    ref = cl_forward_loss(z1, z2, z3, temperature=tau, hard_negative_weight=w)
    assert abs(ours.item() - ref.item()) < ATOL


@pytest.mark.parametrize("case", SMALL, ids=[case_id(c) for c in SMALL])
def test_matches_cl_forward_float32(case):
    n, d, tau, w, hard = case
    z1, z2, z3 = make_batch(n, d, hard=hard, dtype=torch.float32)
    ours = infonce_loss(z1, z2, z3, temperature=tau, hard_negative_weight=w)
    ref = cl_forward_loss(z1, z2, z3, temperature=tau, hard_negative_weight=w)
    assert ours.dtype == torch.float32
    assert abs(ours.item() - ref.item()) < ATOL_FP32


@pytest.mark.parametrize("hard,w", [(False, 0.0), (True, 0.0), (True, math.log(2.0))])
def test_gradients_match_cl_forward(hard, w):
    z1, z2, z3 = make_batch(8, 32, hard=hard)
    inputs = [t for t in (z1, z2, z3) if t is not None]

    def grads(loss_fn):
        leaves = [t.clone().requires_grad_(True) for t in inputs]
        loss_fn(*leaves, temperature=0.05, hard_negative_weight=w).backward()
        return [t.grad for t in leaves]

    for ours, ref in zip(grads(infonce_loss), grads(cl_forward_loss)):
        assert ours is not None and ref is not None
        assert torch.allclose(ours, ref, rtol=0, atol=ATOL)


def test_single_pair_unsupervised_is_zero():
    # One anchor and no negatives: softmax over one logit is 1, so the loss is 0.
    z1, z2, _ = make_batch(1, 16, hard=False)
    assert infonce_loss(z1, z2).item() == 0.0


def test_single_pair_with_hard_negative():
    z1, z2, z3 = make_batch(1, 16, hard=True)
    ours = infonce_loss(z1, z2, z3, hard_negative_weight=1.0)
    ref = cl_forward_loss(z1, z2, z3, hard_negative_weight=1.0)
    assert abs(ours.item() - ref.item()) < ATOL


def test_reduction_none_returns_per_anchor_losses():
    z1, z2, z3 = make_batch(8, 16, hard=True)
    per_anchor = infonce_loss(z1, z2, z3, reduction="none")
    assert per_anchor.shape == (8,)
    assert torch.all(per_anchor > 0)
    assert torch.allclose(per_anchor.mean(), infonce_loss(z1, z2, z3), rtol=0, atol=1e-12)


def test_scale_invariance():
    # Cosine similarity ignores vector norms, so rescaling rows must not change the loss.
    z1, z2, z3 = make_batch(8, 16, hard=True)
    assert z3 is not None
    scale =torch.linspace(0.1, 10.0, 8, dtype=z1.dtype).unsqueeze(1)
    a = infonce_loss(z1, z2, z3, hard_negative_weight=1.0)
    b = infonce_loss(z1 * scale, z2 * 3.0, z3 / scale, hard_negative_weight=1.0)
    assert abs(a.item() - b.item()) < 1e-12


@pytest.mark.parametrize(
    "kwargs,message",
    [
        ({"z2": torch.zeros(4, 8)}, "z1 and z2"),
        ({"z3": torch.zeros(4, 8)}, "z3 must match"),
        ({"temperature": 0.0}, "temperature"),
        ({"temperature": -0.05}, "temperature"),
        ({"z3": None, "hard_negative_weight": 1.0}, "no hard negatives"),
        ({"reduction": "sum"}, "reduction"),
        ({"z1": torch.zeros(0, 16), "z2": torch.zeros(0, 16), "z3": None}, "empty"),
        ({"z2": torch.zeros(4, 16, dtype=torch.float64)}, "dtype and device"),
        ({"z3": torch.zeros(4, 16, dtype=torch.float64)}, "dtype and device"),
    ],
)
def test_rejects_invalid_input(kwargs: dict[str, Any], message: str):
    args: dict[str, Any] = {"z1": torch.zeros(4, 16), "z2": torch.zeros(4, 16), "z3": torch.zeros(4, 16)}
    args.update(kwargs)
    z1, z2, z3 = args.pop("z1"), args.pop("z2"), args.pop("z3")
    with pytest.raises(ValueError, match=message):
        infonce_loss(z1, z2, z3, **args)


UPSTREAM = Path(__file__).resolve().parents[1] / "experiments/reproduction/SimCSE/simcse/models.py"


@pytest.mark.skipif(not UPSTREAM.exists(), reason="upstream SimCSE checkout not present (git-ignored)")
def test_reference_is_verbatim_copy_of_cl_forward():
    # Guards the claim in infonce_reference.py: both blocks are byte-for-byte copies
    # of simcse/models.py @ 235f89e (Similarity: lines 35-46; loss: lines 193-211).
    upstream = UPSTREAM.read_text(encoding="utf-8").splitlines()
    ours = Path(infonce_reference.__file__).read_text(encoding="utf-8")
    assert "\n".join(upstream[34:46]) in ours
    assert "\n".join(upstream[192:211]) in ours
