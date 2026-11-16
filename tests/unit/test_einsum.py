"""Unit tests for :func:`scw.math_core.einsum`."""

from __future__ import annotations

import numpy as np
import pytest

from scw.exceptions import ShapeError
from scw.math_core import Tensor, einsum


def test_matrix_product() -> None:
    a = Tensor([[1.0, 2.0], [3.0, 4.0]])
    b = Tensor([[5.0, 6.0], [7.0, 8.0]])
    assert np.allclose(einsum("ij,jk->ik", a, b).data, a.data @ b.data)


def test_transpose() -> None:
    a = Tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert np.array_equal(einsum("ij->ji", a).data, a.data.T)


def test_diagonal() -> None:
    a = Tensor([[1.0, 2.0], [3.0, 4.0]])
    assert np.array_equal(einsum("ii->i", a).data, np.diag(a.data))


def test_trace_via_einsum_is_scalar_tensor() -> None:
    a = Tensor([[1.0, 2.0], [3.0, 4.0]])
    result = einsum("ii->", a)
    assert result.order == 0
    assert result.data == pytest.approx(float(np.trace(a.data)))


def test_outer_product() -> None:
    u = Tensor([1.0, 2.0])
    v = Tensor([3.0, 4.0, 5.0])
    assert np.array_equal(einsum("i,j->ij", u, v).data, np.outer(u.data, v.data))


def test_implicit_output_orders_labels_alphabetically() -> None:
    a = Tensor([[1.0, 2.0], [3.0, 4.0]])
    b = Tensor([[5.0, 6.0], [7.0, 8.0]])
    assert np.allclose(einsum("ij,jk", a, b).data, a.data @ b.data)


def test_batched_contraction() -> None:
    rng = np.random.default_rng(0)
    a = Tensor(rng.standard_normal((3, 2, 4)))
    b = Tensor(rng.standard_normal((3, 4, 5)))
    out = einsum("bij,bjk->bik", a, b)
    assert out.shape == (3, 2, 5)
    assert np.allclose(out.data, np.einsum("bij,bjk->bik", a.data, b.data))


def test_no_operands_rejected() -> None:
    with pytest.raises(ShapeError):
        einsum("ij->ji")


def test_operand_count_mismatch_rejected() -> None:
    a = Tensor([[1.0, 2.0]])
    with pytest.raises(ShapeError):
        einsum("ij,jk->ik", a)


def test_operand_order_mismatch_rejected() -> None:
    a = Tensor([1.0, 2.0])
    with pytest.raises(ShapeError):
        einsum("ij->ji", a)


def test_non_tensor_operand_rejected() -> None:
    with pytest.raises(TypeError):
        einsum("ij->ji", np.eye(2))  # type: ignore[arg-type]


def test_non_string_subscripts_rejected() -> None:
    a = Tensor([[1.0]])
    with pytest.raises(TypeError):
        einsum(5, a)  # type: ignore[arg-type]


def test_non_alphabetic_labels_rejected() -> None:
    a = Tensor([[1.0, 2.0]])
    with pytest.raises(ShapeError):
        einsum("i1->1i", a)


def test_result_is_always_tensor() -> None:
    a = Tensor([[1.0, 2.0], [3.0, 4.0]])
    assert isinstance(einsum("ij->ji", a), Tensor)
