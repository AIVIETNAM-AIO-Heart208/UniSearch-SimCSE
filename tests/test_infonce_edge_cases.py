"""Regression cases outside the original R4 benchmark grid."""

import pytest
import torch

from infonce_reference import cl_forward_loss
from simcse_lab.model.infonce import infonce_loss


def test_sub_epsilon_vectors_match_official_loss_and_gradients():
    tiny = torch.eye(2, dtype=torch.float64) * 1e-10
    positive = torch.eye(2, dtype=torch.float64)
    values = []
    for loss_fn in (infonce_loss, cl_forward_loss):
        anchor = tiny.clone().requires_grad_()
        loss = loss_fn(anchor, positive)
        values.append((loss, torch.autograd.grad(loss, anchor)[0]))
    for actual, expected in zip(*values):
        torch.testing.assert_close(actual, expected)


def test_zero_half_precision_vectors_have_a_finite_loss():
    zeros = torch.zeros(2, 3, dtype=torch.float16)
    actual = infonce_loss(zeros, zeros)
    expected = cl_forward_loss(zeros.float(), zeros.float()).half()
    torch.testing.assert_close(actual, expected)


@pytest.mark.parametrize("kwargs", [{"temperature": float("inf")}, {"hard_negative_weight": float("nan")}])
def test_nonfinite_hyperparameters_are_rejected(kwargs):
    batch = torch.eye(2)
    with pytest.raises(ValueError, match="finite"):
        infonce_loss(batch, batch, batch, **kwargs)
