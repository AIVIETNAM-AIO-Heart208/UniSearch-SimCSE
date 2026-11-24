"""InfoNCE loss used by SimCSE, implemented independently of the official code.

Notation follows Gao et al. (2021), "SimCSE: Simple Contrastive Learning of
Sentence Embeddings", EMNLP:

* Unsupervised (Eq. 4): ``z1`` and ``z2`` are two dropout views of the same
  batch of sentences; row ``i`` of ``z2`` is the positive of row ``i`` of ``z1``
  and every other row of ``z2`` is an in-batch negative.
* Supervised (Eq. 5, weighted as in Eq. 8 of Section 6.3): ``z2`` holds the
  entailment positives and ``z3`` the contradiction hard negatives. Every row
  of ``z3`` is an extra negative for every anchor; the anchor's own hard
  negative is weighted by ``alpha``. ``alpha = 1`` is Eq. 5.

The weight is passed in log space, ``hard_negative_weight = w = log(alpha)``,
as in the official ``--hard_negative_weight`` argument, because
``exp(s / tau + w) == alpha * exp(s / tau)``. ``w = 0`` means ``alpha = 1``.

The function works on embeddings that are already gathered. Collecting
embeddings across GPUs (``all_gather`` in the official ``cl_forward``) is the
caller's job and is out of scope here.
"""

from __future__ import annotations

import math
from typing import Literal

import torch
from torch import Tensor

__all__ = ["infonce_loss"]


def _unit_rows(values: Tensor) -> Tensor:
    # Match nn.CosineSimilarity's forward and backward for sub-epsilon norms.
    if values.dtype in (torch.float16, torch.bfloat16):
        values = values.float()
    norms = values.norm(dim=-1, keepdim=True).clone()
    with torch.no_grad():
        norms.clamp_min_(1e-8)
    return values / norms


def _cosine_logits(a: Tensor, b: Tensor, temperature: float) -> Tensor:
    """Return the (len(a), len(b)) matrix of cos(a_i, b_j) / temperature."""
    return _unit_rows(a) @ _unit_rows(b).T / temperature


def infonce_loss(
    z1: Tensor,
    z2: Tensor,
    z3: Tensor | None = None,
    *,
    temperature: float = 0.05,
    hard_negative_weight: float = 0.0,
    reduction: Literal["mean", "none"] = "mean",
) -> Tensor:
    """SimCSE InfoNCE loss with in-batch negatives and optional hard negatives.

    Args:
        z1: Anchor embeddings, shape ``(N, d)``.
        z2: Positive embeddings, shape ``(N, d)``; ``z2[i]`` pairs with ``z1[i]``.
        z3: Optional hard-negative embeddings, shape ``(N, d)``; ``z3[i]`` is the
            hard negative of ``z1[i]``.
        temperature: Softmax temperature ``tau`` (> 0). SimCSE default: 0.05.
        hard_negative_weight: ``w = log(alpha)`` added to the logit of each
            anchor's own hard negative. Requires ``z3`` unless it is 0.
        reduction: ``"mean"`` returns the batch mean (a scalar); ``"none"``
            returns the per-anchor losses, shape ``(N,)``.

    Returns:
        The loss in the dtype of ``z1``.

    Raises:
        ValueError: On mismatched shapes, dtypes or devices, empty embeddings,
            non-floating inputs, non-finite parameters, a non-positive
            temperature, a non-zero ``hard_negative_weight``
            without ``z3``, or an unknown reduction.
    """
    if z1.ndim != 2 or z1.shape != z2.shape:
        raise ValueError(f"z1 and z2 must both be (N, d); got {tuple(z1.shape)} and {tuple(z2.shape)}")
    if z1.size(0) == 0:
        raise ValueError("the batch is empty")
    if z1.size(1) == 0 or not z1.is_floating_point():
        raise ValueError("embeddings must have a positive dimension and a floating dtype")
    if z3 is not None and z3.shape != z1.shape:
        raise ValueError(f"z3 must match z1 {tuple(z1.shape)}; got {tuple(z3.shape)}")
    others = (z2,) if z3 is None else (z2, z3)
    if any(z.dtype != z1.dtype or z.device != z1.device for z in others):
        raise ValueError("z1, z2 and z3 must share dtype and device")
    if not math.isfinite(temperature) or temperature <= 0:
        raise ValueError(f"temperature must be > 0 and finite; got {temperature}")
    if not math.isfinite(hard_negative_weight):
        raise ValueError("hard_negative_weight must be finite")
    if z3 is None and hard_negative_weight != 0:
        raise ValueError("hard_negative_weight is set but no hard negatives (z3) were given")
    if reduction not in ("mean", "none"):
        raise ValueError(f"reduction must be 'mean' or 'none'; got {reduction!r}")

    # Row i: logits of anchor i against every candidate; positives on the diagonal.
    logits = _cosine_logits(z1, z2, temperature)  # (N, N)
    positive = logits.diagonal()

    if z3 is not None:
        hard = _cosine_logits(z1, z3, temperature)  # (N, N)
        if hard_negative_weight != 0:
            # alpha^{delta_ij}: only anchor i's own hard negative (j == i) is reweighted.
            hard.diagonal().add_(hard_negative_weight)
        logits = torch.cat([logits, hard], dim=1)  # (N, 2N)

    # -log softmax at the positive, written out as logsumexp - positive.
    losses = torch.logsumexp(logits, dim=1) - positive
    return (losses.mean() if reduction == "mean" else losses).to(z1.dtype)
