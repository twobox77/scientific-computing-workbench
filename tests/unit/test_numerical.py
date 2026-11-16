"""Unit tests for :mod:`scw.numerical.linalg`."""

from __future__ import annotations

import numpy as np
import pytest

from scw.math_core import Matrix, Vector
from scw.numerical import det, inverse, solve


def test_solve_linear_system() -> None:
    a = Matrix([[3.0, 1.0], [1.0, 2.0]])
    b = Vector([9.0, 8.0])
    x = solve(a, b)
    assert np.allclose(a.data @ x.data, b.data)


def test_solve_requires_square() -> None:
    with pytest.raises(ValueError):
        solve(Matrix([[1.0, 2.0]]), Vector([1.0]))


def test_solve_dimension_mismatch() -> None:
    with pytest.raises(ValueError):
        solve(Matrix([[1.0, 0.0], [0.0, 1.0]]), Vector([1.0, 2.0, 3.0]))


def test_solve_type_errors() -> None:
    with pytest.raises(TypeError):
        solve([[1.0]], Vector([1.0]))  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        solve(Matrix([[1.0]]), [1.0])  # type: ignore[arg-type]


def test_inverse_round_trip() -> None:
    a = Matrix([[4.0, 7.0], [2.0, 6.0]])
    identity = a @ inverse(a)
    assert np.allclose(identity.data, np.eye(2))


def test_inverse_requires_square() -> None:
    with pytest.raises(ValueError):
        inverse(Matrix([[1.0, 2.0]]))


def test_inverse_type_error() -> None:
    with pytest.raises(TypeError):
        inverse([[1.0]])  # type: ignore[arg-type]


def test_det() -> None:
    assert det(Matrix([[4.0, 7.0], [2.0, 6.0]])) == pytest.approx(10.0)


def test_det_requires_square() -> None:
    with pytest.raises(ValueError):
        det(Matrix([[1.0, 2.0]]))


def test_det_type_error() -> None:
    with pytest.raises(TypeError):
        det([[1.0]])  # type: ignore[arg-type]
