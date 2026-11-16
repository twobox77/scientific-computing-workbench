"""Unit tests for :class:`scw.math_core.Basis`."""

from __future__ import annotations

import numpy as np
import pytest

from scw.exceptions import DimensionError
from scw.math_core import Basis, Vector, VectorSpace


@pytest.fixture
def space2() -> VectorSpace:
    return VectorSpace(2, name="V")


def test_dimension_and_vectors(space2: VectorSpace) -> None:
    e1 = Vector([1.0, 0.0], space=space2)
    e2 = Vector([1.0, 1.0], space=space2)
    b = Basis([e1, e2])
    assert b.dimension == 2
    assert len(b) == 2
    assert b.vectors == (e1, e2)
    assert b.space == space2


def test_to_matrix_columns_are_basis_vectors(space2: VectorSpace) -> None:
    e1 = Vector([1.0, 0.0], space=space2)
    e2 = Vector([1.0, 1.0], space=space2)
    b = Basis([e1, e2])
    assert np.array_equal(b.to_matrix(), np.array([[1.0, 1.0], [0.0, 1.0]]))


def test_coordinate_round_trip(space2: VectorSpace) -> None:
    e1 = Vector([1.0, 0.0], space=space2)
    e2 = Vector([1.0, 1.0], space=space2)
    b = Basis([e1, e2])
    v = Vector([3.0, 2.0], space=space2)
    coords = b.to_coordinates(v)
    assert np.allclose(coords, np.array([1.0, 2.0]))
    assert b.from_coordinates(coords) == v


def test_standard_basis_coordinates_are_the_components(space2: VectorSpace) -> None:
    b = Basis([Vector([1.0, 0.0], space=space2), Vector([0.0, 1.0], space=space2)])
    v = Vector([7.0, -2.0], space=space2)
    assert np.allclose(b.to_coordinates(v), np.array([7.0, -2.0]))


def test_empty_basis_rejected() -> None:
    with pytest.raises(DimensionError):
        Basis([])


def test_non_vector_rejected() -> None:
    with pytest.raises(TypeError):
        Basis([[1.0, 0.0], [0.0, 1.0]])  # type: ignore[list-item]


def test_wrong_count_rejected(space2: VectorSpace) -> None:
    with pytest.raises(DimensionError):
        Basis([Vector([1.0, 0.0], space=space2)])


def test_linear_dependence_rejected(space2: VectorSpace) -> None:
    e1 = Vector([1.0, 0.0], space=space2)
    with pytest.raises(DimensionError):
        Basis([e1, e1])


def test_mixed_spaces_rejected(space2: VectorSpace) -> None:
    e1 = Vector([1.0, 0.0], space=space2)
    other = Vector([0.0, 1.0])  # unnamed R^2
    with pytest.raises(DimensionError):
        Basis([e1, other])


def test_to_coordinates_wrong_space_rejected(space2: VectorSpace) -> None:
    b = Basis([Vector([1.0, 0.0], space=space2), Vector([0.0, 1.0], space=space2)])
    with pytest.raises(DimensionError):
        b.to_coordinates(Vector([1.0, 1.0]))


def test_to_coordinates_requires_vector(space2: VectorSpace) -> None:
    b = Basis([Vector([1.0, 0.0], space=space2), Vector([0.0, 1.0], space=space2)])
    with pytest.raises(TypeError):
        b.to_coordinates([1.0, 1.0])  # type: ignore[arg-type]


def test_from_coordinates_shape_validation(space2: VectorSpace) -> None:
    b = Basis([Vector([1.0, 0.0], space=space2), Vector([0.0, 1.0], space=space2)])
    with pytest.raises(DimensionError):
        b.from_coordinates([1.0, 2.0, 3.0])


def test_equality_and_repr(space2: VectorSpace) -> None:
    e1 = Vector([1.0, 0.0], space=space2)
    e2 = Vector([0.0, 1.0], space=space2)
    b1 = Basis([e1, e2])
    b2 = Basis([e1, e2])
    assert b1 == b2
    assert hash(b1) == hash(b2)
    assert b1 != Basis([e2, e1])
    assert "dimension=2" in repr(b1)
