"""Check the worked example in the report (method.tex, Section ``sec:method-example``).

The example uses the sentences of Figure 1 in Gao et al. (2021) with
*illustrative* cosine similarities chosen by us, not model outputs. This test
rebuilds embeddings with exactly those cosines to the first anchor, runs our
``infonce_loss`` and checks the per-anchor loss printed in the report, the
softmax probabilities and the gradient claim. It also reads method.tex and
checks that every cosine, logit and computed value appears in the Worked
Example subsection, so the report and this file cannot drift apart.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest
import torch

from simcse_lab.model.infonce import infonce_loss

# Anchor x_1 = "Two dogs are running."
# Unsupervised: cosines of h_1 (dropout mask z) to the second views (mask z') of
#   x_1 itself, "A man surfing on the sea.", "A kid is on a skateboard."
UNSUP_COS = (0.80, 0.70, 0.60)
# Supervised: cosines of h_1 to the entailment hypotheses
#   "There are animals outdoors." (own positive), "There is a man.", "A kid is skateboarding."
SUP_POS_COS = (0.80, 0.40, 0.45)
#   and to the contradiction hypotheses
#   "The pets are sitting on a couch." (own hard negative),
#   "The man wears a business suit.", "A kid is inside the house."
SUP_NEG_COS = (0.75, 0.30, 0.35)

# Values printed in the report, rounded to the digits shown there.
REPORT = {
    "unsup_tau0.05": 0.143,
    "unsup_tau1": 1.002,
    "sup_tau0.05": 0.314,
    "sup_tau0.05_alpha2": 0.552,
    "sup_tau0.05_no_hard": 0.0012,
}
# Softmax probabilities printed in the report (row 1).
REPORT_PROB = {
    "unsup_positive_tau0.05": 0.87,
    "unsup_positive_tau1": 0.37,
    "sup_positive_tau0.05": 0.73,
    "sup_hard_negative_tau0.05": 0.27,
    "sup_hard_negative_tau0.05_alpha2": 0.42,
}
# Logits printed for the unsupervised row at tau = 0.05 (cosine / tau).
REPORT_LOGITS = (16, 14, 12)


def batch_with_row0_cosines(pos_cos, neg_cos=None, n_extra_dims=4):
    """Embeddings whose cosines from z1[0] to z2[j] / z3[j] are exactly the given values.

    z1[0] is the basis vector e_0. Each candidate is c * e_0 + sqrt(1 - c^2) * e_k
    with its own basis vector e_k, so only its angle to e_0 is fixed. The other
    anchors get unrelated basis vectors; their rows are not used.
    """
    n = len(pos_cos)
    cands = list(pos_cos) + list(neg_cos or ())
    d = 1 + len(cands) + n + n_extra_dims
    eye = torch.eye(d, dtype=torch.float64)

    def cand(c, k):
        return c * eye[0] + math.sqrt(1.0 - c * c) * eye[k]

    z1 = torch.stack([eye[0]] + [eye[1 + len(cands) + i] for i in range(1, n)])
    z2 = torch.stack([cand(c, 1 + j) for j, c in enumerate(pos_cos)])
    z3 = None
    if neg_cos is not None:
        z3 = torch.stack([cand(c, 1 + n + j) for j, c in enumerate(neg_cos)])
    return z1, z2, z3


def row0_loss(pos_cos, neg_cos=None, *, tau, w=0.0):
    z1, z2, z3 = batch_with_row0_cosines(pos_cos, neg_cos)
    return infonce_loss(z1, z2, z3, temperature=tau, hard_negative_weight=w, reduction="none")[0].item()


def closed_form(pos_cos, neg_cos=(), *, tau, alpha=1.0):
    """-log softmax at the positive, from Eq. 4 / Eq. 8 directly."""
    num = math.exp(pos_cos[0] / tau)
    den = sum(math.exp(c / tau) for c in pos_cos)
    den += sum((alpha if j == 0 else 1.0) * math.exp(c / tau) for j, c in enumerate(neg_cos))
    return -math.log(num / den)


METHOD_TEX = Path(__file__).resolve().parents[1] / "docs" / "report" / "sections" / "method.tex"


def example_text() -> str:
    """The Worked Example subsection of the report, up to the next subsection."""
    tex = METHOD_TEX.read_text(encoding="utf-8")
    start = tex.index("\\label{sec:method-example}")
    return tex[start : tex.index("\\subsection", start)]


def test_constructed_cosines_are_exact():
    z1, z2, z3 = batch_with_row0_cosines(SUP_POS_COS, SUP_NEG_COS)
    assert z3 is not None
    cos = torch.nn.functional.cosine_similarity
    assert torch.allclose(cos(z1[0:1], z2), torch.tensor(SUP_POS_COS, dtype=torch.float64), atol=1e-12)
    assert torch.allclose(cos(z1[0:1], z3), torch.tensor(SUP_NEG_COS, dtype=torch.float64), atol=1e-12)


def test_report_text_matches_test_values():
    # The Worked Example in method.tex prints the same cosines, logits and values.
    text = example_text()
    for c in UNSUP_COS + SUP_POS_COS + SUP_NEG_COS:
        assert f"${c:.2f}$" in text, f"cosine {c:.2f} missing from method.tex"
    for logit, c in zip(REPORT_LOGITS, UNSUP_COS):
        assert round(c / 0.05) == logit
        assert f"${logit}$" in text, f"logit {logit} missing from method.tex"
    for value in list(REPORT.values()) + list(REPORT_PROB.values()):
        assert f"{value}$" in text, f"value {value} missing from method.tex"


@pytest.mark.parametrize(
    "key,pos,neg,tau,w",
    [
        ("unsup_tau0.05", UNSUP_COS, None, 0.05, 0.0),
        ("unsup_tau1", UNSUP_COS, None, 1.0, 0.0),
        ("sup_tau0.05", SUP_POS_COS, SUP_NEG_COS, 0.05, 0.0),
        ("sup_tau0.05_alpha2", SUP_POS_COS, SUP_NEG_COS, 0.05, math.log(2.0)),
        ("sup_tau0.05_no_hard", SUP_POS_COS, None, 0.05, 0.0),
    ],
)
def test_report_numbers(key, pos, neg, tau, w):
    ours = row0_loss(pos, neg, tau=tau, w=w)
    expected = closed_form(pos, neg or (), tau=tau, alpha=math.exp(w))
    assert abs(ours - expected) < 1e-12
    digits = len(repr(REPORT[key]).split(".")[1])
    assert round(ours, digits) == REPORT[key], f"{key}: computed {ours:.6f}, report says {REPORT[key]}"


def logits_row0(pos_cos, neg_cos=(), *, tau, alpha=1.0):
    """Row-1 logits: cos / tau, plus log(alpha) on the anchor's own hard negative."""
    logits = torch.tensor(list(pos_cos) + list(neg_cos), dtype=torch.float64) / tau
    if neg_cos:
        logits[len(pos_cos)] += math.log(alpha)
    return logits


def softmax_row0(pos_cos, neg_cos=(), *, tau, alpha=1.0):
    return torch.softmax(logits_row0(pos_cos, neg_cos, tau=tau, alpha=alpha), dim=0)


def test_report_probabilities():
    got = {
        "unsup_positive_tau0.05": softmax_row0(UNSUP_COS, tau=0.05)[0],
        "unsup_positive_tau1": softmax_row0(UNSUP_COS, tau=1.0)[0],
        "sup_positive_tau0.05": softmax_row0(SUP_POS_COS, SUP_NEG_COS, tau=0.05)[0],
        "sup_hard_negative_tau0.05": softmax_row0(SUP_POS_COS, SUP_NEG_COS, tau=0.05)[len(SUP_POS_COS)],
        "sup_hard_negative_tau0.05_alpha2": softmax_row0(SUP_POS_COS, SUP_NEG_COS, tau=0.05, alpha=2.0)[
            len(SUP_POS_COS)
        ],
    }
    for key, value in got.items():
        assert round(value.item(), 2) == REPORT_PROB[key], f"{key}: computed {value.item():.4f}"
    # Report: the four easy negatives together get less than 0.01.
    sup = softmax_row0(SUP_POS_COS, SUP_NEG_COS, tau=0.05)
    assert 1.0 - sup[0].item() - sup[len(SUP_POS_COS)].item() < 0.01
    # Consistency with the loss: p(positive) = exp(-l_1).
    assert abs(got["sup_positive_tau0.05"].item() - math.exp(-row0_loss(SUP_POS_COS, SUP_NEG_COS, tau=0.05))) < 1e-12


@pytest.mark.parametrize("alpha", [1.0, 2.0])
def test_gradient_of_negative_logit_is_its_probability(alpha):
    # Report: the gradient of l_1 w.r.t. a negative's logit equals its softmax probability.
    logits = logits_row0(SUP_POS_COS, SUP_NEG_COS, tau=0.05, alpha=alpha).requires_grad_(True)
    loss = torch.logsumexp(logits, dim=0) - logits[0]
    loss.backward()
    assert logits.grad is not None
    probs = torch.softmax(logits.detach(), dim=0)
    assert torch.allclose(logits.grad[1:], probs[1:], rtol=0, atol=1e-12)
    expected_loss = REPORT["sup_tau0.05"] if alpha == 1.0 else REPORT["sup_tau0.05_alpha2"]
    assert round(loss.item(), 3) == expected_loss
