# The cl_forward extract below is kept verbatim, so silence the checks it trips.
# pyright: reportOptionalMemberAccess=false, reportPossiblyUnboundVariable=false
"""Reference implementations for checking ``simcse_lab.model.infonce`` (R4).

Two references, each independent of ``infonce_loss``:

1. ``naive_loss``: evaluates SimCSE Eq. 4 (unsupervised) and Eq. 8 (supervised
   with weight alpha; alpha = 1 is Eq. 5) term by term with Python loops, using
   ``alpha = exp(w)`` and ``alpha ** delta_ij`` as written in the paper, so the
   log-weight trick is tested rather than assumed.
2. ``cl_forward_loss``: the loss block of the official ``cl_forward``, copied
   verbatim and fed through a stand-in ``cls`` object.

Kept inside ``tests/`` on purpose: ``experiments/reproduction/SimCSE/`` is
git-ignored, so tests must not import from it.
"""

from __future__ import annotations

import math
from types import SimpleNamespace

import torch
import torch.nn as nn
from torch import Tensor


def naive_loss(
    z1: Tensor,
    z2: Tensor,
    z3: Tensor | None = None,
    *,
    temperature: float = 0.05,
    hard_negative_weight: float = 0.0,
) -> Tensor:
    """Mean of l_i from SimCSE Eq. 4 (z3 is None) or Eq. 8 (z3 given), by loops.

    No max-subtraction, so use float64 and temperature >= ~0.01: exp(1 / tau)
    overflows float32 already at tau < ~0.0113.
    """
    n = z1.size(0)
    alpha = math.exp(hard_negative_weight)

    def sim(a: Tensor, b: Tensor) -> Tensor:
        return (a * b).sum() / (a.norm() * b.norm())

    total = torch.zeros((), dtype=z1.dtype)
    for i in range(n):
        numerator = torch.exp(sim(z1[i], z2[i]) / temperature)
        denominator = torch.zeros((), dtype=z1.dtype)
        for j in range(n):
            denominator = denominator + torch.exp(sim(z1[i], z2[j]) / temperature)
            if z3 is not None:
                delta_ij = 1 if i == j else 0
                denominator = denominator + alpha**delta_ij * torch.exp(sim(z1[i], z3[j]) / temperature)
        total = total - torch.log(numerator / denominator)
    return total / n


# ---------------------------------------------------------------------------
# Extract from the official SimCSE code.
# Source: https://github.com/princeton-nlp/SimCSE
#   commit 235f89e0244b23673b69fbbc4a1cd9868c5a5c24, file simcse/models.py
#   - class Similarity: lines 35-46
#   - loss computation inside cl_forward: lines 193-211
# Copyright (c) 2021 Princeton Natural Language Processing, MIT License.
# Both blocks are byte-for-byte copies (tests/test_infonce.py checks this when
# the upstream checkout exists). `cls` is a stand-in object that supplies the
# three attributes the block reads: cls.sim, cls.device and
# cls.model_args.hard_negative_weight. Distributed all_gather (lines 169-191)
# and the MLM loss (lines 213-218) are not part of this check.
# ---------------------------------------------------------------------------


class Similarity(nn.Module):
    """
    Dot product or cosine similarity
    """

    def __init__(self, temp):
        super().__init__()
        self.temp = temp
        self.cos = nn.CosineSimilarity(dim=-1)

    def forward(self, x, y):
        return self.cos(x, y) / self.temp


def cl_forward_loss(z1, z2, z3=None, *, temperature=0.05, hard_negative_weight=0.0):
    # Set-up, not from the original: the inputs cl_forward has at line 193.
    cls = SimpleNamespace(
        sim=Similarity(temp=temperature),
        device=z1.device,
        model_args=SimpleNamespace(hard_negative_weight=hard_negative_weight),
    )
    num_sent = 2 if z3 is None else 3

    # --- verbatim: simcse/models.py lines 193-211 ---
    cos_sim = cls.sim(z1.unsqueeze(1), z2.unsqueeze(0))
    # Hard negative
    if num_sent >= 3:
        z1_z3_cos = cls.sim(z1.unsqueeze(1), z3.unsqueeze(0))
        cos_sim = torch.cat([cos_sim, z1_z3_cos], 1)

    labels = torch.arange(cos_sim.size(0)).long().to(cls.device)
    loss_fct = nn.CrossEntropyLoss()

    # Calculate loss with hard negatives
    if num_sent == 3:
        # Note that weights are actually logits of weights
        z3_weight = cls.model_args.hard_negative_weight
        weights = torch.tensor(
            [[0.0] * (cos_sim.size(-1) - z1_z3_cos.size(-1)) + [0.0] * i + [z3_weight] + [0.0] * (z1_z3_cos.size(-1) - i - 1) for i in range(z1_z3_cos.size(-1))]
        ).to(cls.device)
        cos_sim = cos_sim + weights

    loss = loss_fct(cos_sim, labels)
    # --- end verbatim ---
    return loss
