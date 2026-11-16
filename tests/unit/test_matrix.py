"""Unit tests for :class:`scw.math_core.Matrix`."""

from __future__ import annotations

import pytest

from scw.exceptions import DimensionError, NonFiniteError, ShapeError
from scw.math_core import Matrix, Vector


def test_shape_and_accessors() -> None:
    m = Matrix([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert m.shape == (2, 3)
    assert m.rows == 2
    assert m.columns == 3


def test_data_copied_and_read_only() -> None:
    source = [[1.0, 2.0], [3.0, 4.0]]
    m = Matrix(source)
    source[0][0] = 99.0
    assert m.data[0, 0] == 1.0
    with pytest.raises(ValueError):
        m.data[0, 0] = 5.0


def test_addition_subtraction_scaling() -> None:
    a = Matrix([[1.0, 2.0], [3.0, 4.0]])
    b = Matrix([[1.0, 1.0], [1.0, 1.0]])
    assert (a + b).data.tolist() == [[2.0, 3.0], [4.0, 5.0]]
    assert (a - b).data.tolist() == [[0.0, 1.0], [2.0, 3.0]]
    assert (2 * a).data.tolist() == [[2.0, 4.0], [6.0, 8.0]]
    assert (-a).data.tolist() == [[-1.0, -2.0], [-3.0, -4.0]]


def test_matrix_multiplication() -> None:
    a = Matrix([[1.0, 2.0], [3.0, 4.0]])
    b = Matrix([[5.0, 6.0], [7.0, 8.0]])
    assert (a @ b).data.tolist() == [[19.0, 22.0], [43.0, 50.0]]


def test_matrix_multiplication_dimension_mismatch() -> None:
    a = Matrix([[1.0, 2.0, 3.0]])
    b = Matrix([[1.0, 2.0, 3.0]])
    with pytest.raises(DimensionError):
        a @ b


def test_apply_vector() -> None:
    m = Matrix([[1.0, 2.0], [3.0, 4.0]])
    out = m.apply(Vector([1.0, 1.0]))
    assert out.to_numpy().tolist() == [3.0, 7.0]


def test_apply_dimension_mismatch() -> None:
    m = Matrix([[1.0, 2.0], [3.0, 4.0]])
    with pytest.raises(DimensionError):
        m.apply(Vector([1.0, 2.0, 3.0]))


def test_apply_requires_vector() -> None:
    with pytest.raises(TypeError):
        Matrix([[1.0]]).apply([1.0])  # type: ignore[arg-type]


def test_transpose() -> None:
    m = Matrix([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert m.transpose().shape == (3, 2)
    assert m.T.data.tolist() == [[1.0, 4.0], [2.0, 5.0], [3.0, 6.0]]


def test_shape_validation() -> None:
    with pytest.raises(ShapeError):
        Matrix([1.0, 2.0])
    with pytest.raises(ShapeError):
        Matrix([[]])


def test_non_finite_rejected() -> None:
    with pytest.raises(NonFiniteError):
        Matrix([[1.0, float("nan")]])


def test_equality_and_hash() -> None:
    a = Matrix([[1.0, 2.0]])
    b = Matrix([[1.0, 2.0]])
    assert a == b
    assert hash(a) == hash(b)
    assert a != Matrix([[1.0, 3.0]])
    assert (a == 1) is False


def test_repr_mentions_shape() -> None:
    assert "shape=(1, 2)" in repr(Matrix([[1.0, 2.0]]))
