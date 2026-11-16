"""Unit tests for :class:`scw.math_core.Covector`."""

from __future__ import annotations

import pytest

from scw.exceptions import DimensionError, NonFiniteError
from scw.math_core import Covector, Vector


def test_evaluate_pairing() -> None:
    alpha = Covector([2.0, 0.0, -1.0])
    v = Vector([1.0, 2.0, 3.0])
    assert alpha.evaluate(v) == pytest.approx(-1.0)
    assert alpha(v) == pytest.approx(-1.0)


def test_covector_is_not_a_vector() -> None:
    alpha = Covector([1.0, 2.0])
    assert not isinstance(alpha, Vector)
    assert type(alpha) is not type(Vector([1.0, 2.0]))


def test_pairing_dimension_mismatch() -> None:
    with pytest.raises(DimensionError):
        Covector([1.0, 2.0]).evaluate(Vector([1.0, 2.0, 3.0]))


def test_pairing_requires_vector() -> None:
    with pytest.raises(TypeError):
        Covector([1.0]).evaluate([1.0])  # type: ignore[arg-type]


def test_linear_combinations() -> None:
    a = Covector([1.0, 2.0])
    b = Covector([3.0, 4.0])
    assert (a + b).to_numpy().tolist() == [4.0, 6.0]
    assert (b - a).to_numpy().tolist() == [2.0, 2.0]
    assert (2 * a).to_numpy().tolist() == [2.0, 4.0]
    assert (a / 2).to_numpy().tolist() == [0.5, 1.0]
    assert (-a).to_numpy().tolist() == [-1.0, -2.0]


def test_covector_multiplication_rejected() -> None:
    with pytest.raises(TypeError):
        Covector([1.0, 2.0]) * Covector([1.0, 2.0])


def test_division_by_zero_rejected() -> None:
    with pytest.raises(ZeroDivisionError):
        Covector([1.0, 2.0]) / 0.0


def test_non_finite_rejected() -> None:
    with pytest.raises(NonFiniteError):
        Covector([1.0, float("nan")])


def test_wrong_ndim_rejected() -> None:
    with pytest.raises(DimensionError):
        Covector([[1.0, 2.0]])


def test_equality_and_hash() -> None:
    a = Covector([1.0, 2.0])
    b = Covector([1.0, 2.0])
    assert a == b
    assert hash(a) == hash(b)
    assert a != Covector([1.0, 3.0])
    assert (a == 5) is False


def test_repr_mentions_type() -> None:
    assert repr(Covector([1.0])).startswith("Covector(")
