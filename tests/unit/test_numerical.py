"""Unit tests for :mod:`scw.numerical.linalg`."""

from __future__ import annotations

import numpy as np
import pytest

from scw.math_core import Matrix, Vector
from scw.numerical import det, inverse, lstsq, solve


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


def test_lstsq_exact_system() -> None:
    a = Matrix([[3.0, 1.0], [1.0, 2.0]])
    b = Vector([9.0, 8.0])
    result = lstsq(a, b)
    np.testing.assert_allclose(a.data @ result.solution.data, b.data)
    assert result.rank == 2
    assert result.residual_norm == pytest.approx(0.0, abs=1e-9)


def test_lstsq_overdetermined_minimizes_residual() -> None:
    a = Matrix([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    b = Vector([1.0, 1.0, 3.0])
    result = lstsq(a, b)
    # Normal equations: A^T A x = A^T b.
    normal = a.data.T @ a.data
    rhs = a.data.T @ b.data
    np.testing.assert_allclose(normal @ result.solution.data, rhs, atol=1e-9)
    assert result.residual_norm > 0.0


def test_lstsq_underdetermined_returns_minimum_norm() -> None:
    a = Matrix([[1.0, 0.0, 1.0], [0.0, 1.0, 1.0]])
    b = Vector([1.0, 1.0])
    result = lstsq(a, b)
    np.testing.assert_allclose(a.data @ result.solution.data, b.data, atol=1e-9)
    assert result.residual_norm == 0.0


def test_lstsq_dimension_mismatch() -> None:
    with pytest.raises(ValueError):
        lstsq(Matrix([[1.0, 0.0], [0.0, 1.0]]), Vector([1.0, 2.0, 3.0]))


def test_lstsq_type_errors() -> None:
    with pytest.raises(TypeError):
        lstsq([[1.0]], Vector([1.0]))  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        lstsq(Matrix([[1.0]]), [1.0])  # type: ignore[arg-type]
