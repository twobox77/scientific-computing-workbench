"""Unit tests for :class:`scw.math_core.Vector`."""

from __future__ import annotations

import numpy as np
import pytest

from scw.exceptions import DimensionError, NonFiniteError
from scw.math_core import Vector, VectorSpace


def test_dimension_and_data() -> None:
    v = Vector([1.0, 2.0, 3.0])
    assert v.dimension == 3
    assert v.space == VectorSpace(3)


def test_data_is_copied_on_construction() -> None:
    source = np.array([1.0, 2.0, 3.0])
    v = Vector(source)
    source[0] = 99.0
    assert v.data[0] == 1.0


def test_data_view_is_read_only() -> None:
    v = Vector([1.0, 2.0])
    with pytest.raises(ValueError):
        v.data[0] = 5.0


def test_to_numpy_copy_semantics() -> None:
    v = Vector([1.0, 2.0])
    copy = v.to_numpy()
    copy[0] = 7.0
    assert v.data[0] == 1.0
    assert np.shares_memory(v.to_numpy(copy=False), v.data)


def test_addition_and_subtraction() -> None:
    a = Vector([1.0, 2.0])
    b = Vector([3.0, 4.0])
    assert (a + b).to_numpy().tolist() == [4.0, 6.0]
    assert (b - a).to_numpy().tolist() == [2.0, 2.0]
    assert (-a).to_numpy().tolist() == [-1.0, -2.0]


def test_scalar_multiplication_both_sides() -> None:
    a = Vector([1.0, -2.0])
    assert (a * 3).to_numpy().tolist() == [3.0, -6.0]
    assert (3 * a).to_numpy().tolist() == [3.0, -6.0]
    assert (a / 2).to_numpy().tolist() == [0.5, -1.0]


def test_division_by_zero_rejected() -> None:
    with pytest.raises(ZeroDivisionError):
        Vector([1.0, 2.0]) / 0.0


def test_dot_and_norm() -> None:
    a = Vector([3.0, 4.0])
    b = Vector([1.0, 0.0])
    assert a.dot(b) == 3.0
    assert a.norm() == pytest.approx(5.0)
    assert a.norm(p=1) == pytest.approx(7.0)


def test_norm_does_not_underflow_or_overflow() -> None:
    tiny = Vector([0.0, 0.0, 0.0, 2.2250738585072014e-308])
    assert tiny.norm() > 0.0
    huge = Vector([1e200, 1e200])
    assert np.isfinite(huge.norm())


def test_norm_rejects_non_positive_order() -> None:
    with pytest.raises(ValueError):
        Vector([1.0, 2.0]).norm(p=0)


def test_dot_requires_vector() -> None:
    with pytest.raises(TypeError):
        Vector([1.0]).dot([1.0])  # type: ignore[arg-type]


def test_multiplying_by_vector_is_rejected() -> None:
    with pytest.raises(TypeError):
        Vector([1.0, 2.0]) * Vector([1.0, 2.0])


def test_dimension_mismatch_rejected() -> None:
    with pytest.raises(DimensionError):
        Vector([1.0, 2.0]) + Vector([1.0, 2.0, 3.0])
    with pytest.raises(DimensionError):
        Vector([1.0, 2.0]).dot(Vector([1.0, 2.0, 3.0]))


def test_different_named_spaces_rejected() -> None:
    a = Vector([1.0, 2.0], space=VectorSpace(2, name="A"))
    b = Vector([1.0, 2.0], space=VectorSpace(2, name="B"))
    with pytest.raises(DimensionError):
        a + b


def test_non_finite_rejected() -> None:
    with pytest.raises(NonFiniteError):
        Vector([1.0, float("nan")])
    with pytest.raises(NonFiniteError):
        Vector([1.0, float("inf")])


def test_wrong_ndim_rejected() -> None:
    with pytest.raises(DimensionError):
        Vector([[1.0, 2.0]])


def test_space_dimension_mismatch_rejected() -> None:
    with pytest.raises(DimensionError):
        Vector([1.0, 2.0], space=VectorSpace(3))


def test_is_zero() -> None:
    assert Vector([0.0, 0.0]).is_zero()
    assert not Vector([1e-3, 0.0]).is_zero()
    assert Vector([1e-3, 0.0]).is_zero(atol=1e-2)


def test_equality_and_hash() -> None:
    a = Vector([1.0, 2.0])
    b = Vector([1.0, 2.0])
    assert a == b
    assert hash(a) == hash(b)
    assert a != Vector([1.0, 3.0])
    assert (a == "not a vector") is False


def test_repr_mentions_type() -> None:
    assert repr(Vector([1.0, 2.0])).startswith("Vector(")
