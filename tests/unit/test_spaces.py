"""Unit tests for :class:`scw.math_core.VectorSpace`."""

from __future__ import annotations

import pytest

from scw.math_core import VectorSpace


def test_dimension_and_name() -> None:
    space = VectorSpace(3, name="V")
    assert space.dimension == 3
    assert space.name == "V"


def test_equality() -> None:
    assert VectorSpace(2) == VectorSpace(2)
    assert VectorSpace(2, name="A") == VectorSpace(2, name="A")
    assert VectorSpace(2, name="A") != VectorSpace(2, name="B")
    assert VectorSpace(2) != VectorSpace(3)


def test_str_with_and_without_name() -> None:
    assert str(VectorSpace(3)) == "R^3"
    assert str(VectorSpace(3, name="V")) == "V (R^3)"


def test_dimension_must_be_int() -> None:
    with pytest.raises(TypeError):
        VectorSpace(3.0)  # type: ignore[arg-type]


def test_dimension_must_be_positive() -> None:
    with pytest.raises(ValueError):
        VectorSpace(0)
    with pytest.raises(ValueError):
        VectorSpace(-1)
