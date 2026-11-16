"""Unit tests for :class:`scw.math_core.Tensor`."""

from __future__ import annotations

import numpy as np
import pytest

from scw.exceptions import DimensionError, NonFiniteError, ShapeError
from scw.math_core import Tensor


def test_order_shape_size() -> None:
    t = Tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert t.order == 2
    assert t.shape == (2, 3)
    assert t.size == 6


def test_scalar_tensor_has_order_zero() -> None:
    t = Tensor(3.5)
    assert t.order == 0
    assert t.shape == ()
    assert t.size == 1


def test_data_copied_and_read_only() -> None:
    source = np.array([1.0, 2.0, 3.0])
    t = Tensor(source)
    source[0] = 99.0
    assert t.data[0] == 1.0
    with pytest.raises(ValueError):
        t.data[0] = 5.0


def test_to_numpy_copy_semantics() -> None:
    t = Tensor([1.0, 2.0])
    assert np.shares_memory(t.to_numpy(copy=False), t.data)
    assert not np.shares_memory(t.to_numpy(), t.data)


def test_zeros_and_eye() -> None:
    assert Tensor.zeros((2, 3, 4)).shape == (2, 3, 4)
    assert np.array_equal(Tensor.zeros((2, 2)).data, np.zeros((2, 2)))
    assert np.array_equal(Tensor.eye(3).data, np.eye(3))


def test_zeros_rejects_bad_shape() -> None:
    with pytest.raises(TypeError):
        Tensor.zeros((2.5, 3))
    with pytest.raises(ShapeError):
        Tensor.zeros((2, -1))


def test_eye_rejects_bad_size() -> None:
    with pytest.raises(TypeError):
        Tensor.eye(2.0)  # type: ignore[arg-type]
    with pytest.raises(ShapeError):
        Tensor.eye(0)


def test_non_finite_rejected() -> None:
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(NonFiniteError):
            Tensor([1.0, bad])


def test_addition_and_subtraction() -> None:
    a = Tensor([[1.0, 2.0], [3.0, 4.0]])
    b = Tensor([[5.0, 6.0], [7.0, 8.0]])
    assert np.array_equal((a + b).data, np.array([[6.0, 8.0], [10.0, 12.0]]))
    assert np.array_equal((b - a).data, np.array([[4.0, 4.0], [4.0, 4.0]]))
    assert np.array_equal((-a).data, -a.data)


def test_addition_shape_mismatch_rejected() -> None:
    with pytest.raises(ShapeError):
        Tensor([1.0, 2.0]) + Tensor([1.0, 2.0, 3.0])


def test_scalar_multiplication_both_sides() -> None:
    a = Tensor([1.0, 2.0])
    assert np.array_equal((2 * a).data, np.array([2.0, 4.0]))
    assert np.array_equal((a * 3).data, np.array([3.0, 6.0]))


def test_tensor_times_tensor_is_rejected() -> None:
    with pytest.raises(TypeError):
        Tensor([1.0]) * Tensor([1.0])


def test_outer_product_shape_and_values() -> None:
    a = Tensor([1.0, 2.0])
    b = Tensor([3.0, 4.0, 5.0])
    out = a.outer(b)
    assert out.shape == (2, 3)
    assert np.array_equal(out.data, np.outer(a.data, b.data))


def test_outer_requires_tensor() -> None:
    with pytest.raises(TypeError):
        Tensor([1.0]).outer([1.0])  # type: ignore[arg-type]


def test_contract_reduces_order_and_matches_matmul() -> None:
    a = Tensor([[1.0, 2.0], [3.0, 4.0]])
    b = Tensor([[5.0, 6.0], [7.0, 8.0]])
    assert a.contract(b).order == 2
    assert np.allclose(a.contract(b).data, a.data @ b.data)


def test_contract_dimension_mismatch_rejected() -> None:
    a = Tensor([[1.0, 2.0, 3.0]])
    b = Tensor([[1.0, 2.0]])
    with pytest.raises(DimensionError):
        a.contract(b, axis=1, other_axis=0)


def test_contract_axis_out_of_range() -> None:
    a = Tensor([[1.0, 2.0]])
    b = Tensor([[1.0, 2.0]])
    with pytest.raises(DimensionError):
        a.contract(b, axis=5, other_axis=0)


def test_contract_axis_type_error() -> None:
    a = Tensor([[1.0, 2.0]])
    with pytest.raises(TypeError):
        a.contract(a, axis=1.0, other_axis=0)  # type: ignore[arg-type]


def test_contract_with_negative_axis() -> None:
    a = Tensor([[1.0, 2.0], [3.0, 4.0]])
    b = Tensor([[1.0, 0.0], [0.0, 1.0]])
    assert np.allclose(a.contract(b, axis=-1, other_axis=0).data, a.data @ b.data)


def test_trace_reduces_order_and_matches_numpy() -> None:
    a = Tensor([[1.0, 2.0], [3.0, 4.0]])
    assert a.trace().order == 0
    assert a.trace().data == pytest.approx(float(np.trace(a.data)))


def test_trace_higher_order_keeps_remaining_indices() -> None:
    rng = np.random.default_rng(0)
    raw = rng.standard_normal((2, 3, 4, 3))
    t = Tensor(raw)
    out = t.trace(axis1=1, axis2=3)
    assert out.shape == (2, 4)
    assert np.allclose(out.data, np.einsum("ijkj->ik", raw))


def test_trace_requires_order_at_least_two() -> None:
    with pytest.raises(DimensionError):
        Tensor([1.0, 2.0]).trace()


def test_trace_distinct_axes_required() -> None:
    with pytest.raises(DimensionError):
        Tensor([[1.0, 2.0], [3.0, 4.0]]).trace(axis1=1, axis2=1)


def test_trace_size_mismatch_rejected() -> None:
    with pytest.raises(DimensionError):
        Tensor(np.zeros((2, 3))).trace(axis1=0, axis2=1)


def test_equality_and_hash() -> None:
    a = Tensor([[1.0, 2.0]])
    b = Tensor([[1.0, 2.0]])
    assert a == b
    assert hash(a) == hash(b)
    assert a != Tensor([[1.0, 3.0]])
    assert (a == 1) is False


def test_repr_mentions_shape() -> None:
    assert "shape=(2,)" in repr(Tensor([1.0, 2.0]))
