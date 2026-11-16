"""Property-based tests for the numerical services.

The laws here are "reconstruct the matrix from its factors" and "solve then
apply recovers the right-hand side".  They compare two differently-rounded
computations, so the tolerance is scale-aware (``rtol=1e-9, atol=1e-6``); see
the note in ``tests/property/test_vector_properties.py``.
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from scipy.linalg import expm

from scw.math_core import Matrix, Vector
from scw.numerical import cholesky, eigh, lu, qr, solve, solve_ivp, svd

_ATOL = 1e-6
_RTOL = 1e-9


def assert_close(lhs, rhs) -> None:
    np.testing.assert_allclose(lhs, rhs, rtol=_RTOL, atol=_ATOL)


@st.composite
def square_matrices(draw, n: int = 4) -> Matrix:
    entries = draw(
        st.lists(st.floats(-1e3, 1e3, allow_nan=False), min_size=n * n, max_size=n * n)
    )
    return Matrix(np.asarray(entries).reshape(n, n))


@st.composite
def rectangular_matrices(draw) -> Matrix:
    m = draw(st.integers(min_value=1, max_value=4))
    n = draw(st.integers(min_value=1, max_value=4))
    entries = draw(
        st.lists(st.floats(-1e3, 1e3, allow_nan=False), min_size=m * n, max_size=m * n)
    )
    return Matrix(np.asarray(entries).reshape(m, n))


@st.composite
def symmetric_positive_definite(draw, n: int = 3) -> Matrix:
    raw = draw(
        st.lists(
            st.floats(-10.0, 10.0, allow_nan=False), min_size=n * n, max_size=n * n
        )
    )
    b = np.asarray(raw).reshape(n, n)
    return Matrix(b @ b.T + n * np.eye(n))


@settings(max_examples=100, deadline=None)
@given(a=square_matrices())
def test_lu_reconstructs(a: Matrix) -> None:
    assert_close(lu(a).reconstruct().data, a.data)


@settings(max_examples=100, deadline=None)
@given(a=rectangular_matrices())
def test_qr_reconstructs(a: Matrix) -> None:
    assert_close(qr(a).reconstruct().data, a.data)


@settings(max_examples=100, deadline=None)
@given(a=rectangular_matrices())
def test_svd_reconstructs(a: Matrix) -> None:
    assert_close(svd(a).reconstruct().data, a.data)


@settings(max_examples=100, deadline=None)
@given(a=rectangular_matrices())
def test_svd_singular_values_are_non_negative_and_sorted(a: Matrix) -> None:
    s = svd(a).s.data
    assert np.all(s >= -1e-12)
    assert np.all(np.diff(s) <= 1e-9)


@settings(max_examples=100, deadline=None)
@given(a=symmetric_positive_definite())
def test_cholesky_reconstructs(a: Matrix) -> None:
    lower = cholesky(a)
    assert_close(lower.data @ lower.data.T, a.data)


@settings(max_examples=100, deadline=None)
@given(a=symmetric_positive_definite())
def test_eigh_reconstructs_symmetric_matrix(a: Matrix) -> None:
    result = eigh(a)
    assert_close(result.reconstruct().data, a.data)


@settings(max_examples=100, deadline=None)
@given(a=symmetric_positive_definite())
def test_eigh_eigenvalues_ascending(a: Matrix) -> None:
    w = eigh(a).eigenvalues.data
    assert np.all(np.diff(w) >= -1e-9)


@settings(max_examples=100, deadline=None)
@given(seed=st.integers(min_value=0, max_value=10_000))
def test_solve_then_apply_recovers_rhs(seed: int) -> None:
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((3, 3))
    while abs(np.linalg.det(raw)) < 1e-3:  # keep the system well-conditioned
        raw = rng.standard_normal((3, 3))
    a = Matrix(raw)
    b = Vector(rng.standard_normal(3))
    x = solve(a, b)
    assert_close(a.data @ x.data, b.data)


@settings(max_examples=50, deadline=None)
@given(rate=st.floats(0.1, 5.0, allow_nan=False))
def test_linear_ode_matches_matrix_exponential(rate: float) -> None:
    # y' = -rate * y, y(0) = 1  =>  y(t) = exp(-rate t).
    sol = solve_ivp(
        lambda t, y: -rate * y,
        (0.0, 1.0),
        Vector([1.0]),
        t_eval=[0.0, 0.5, 1.0],
        rtol=1e-10,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        sol.y.ravel(), np.exp(-rate * sol.t), rtol=1e-6, atol=1e-9
    )


@settings(max_examples=50, deadline=None)
@given(seed=st.integers(min_value=0, max_value=10_000))
def test_linear_system_solution_satisfies_ode(seed: int) -> None:
    # A constant-coefficient linear ODE y' = A y has solution exp(A t) y0; the
    # integrator must agree with the exact matrix exponential.
    rng = np.random.default_rng(seed)
    a = rng.standard_normal((2, 2)) * 0.1
    y0 = rng.standard_normal(2)
    sol = solve_ivp(
        lambda t, y: Vector(a @ y.data),
        (0.0, 1.0),
        Vector(y0),
        t_eval=[1.0],
        method="DOP853",
        rtol=1e-10,
        atol=1e-12,
    )
    np.testing.assert_allclose(sol.y[-1], expm(a) @ y0, rtol=1e-6, atol=1e-9)


@pytest.mark.parametrize("method", ["RK45", "DOP853"])
def test_energy_conservation_for_oscillator(method: str) -> None:
    def field(t, y):
        return Vector([y.data[1], -y.data[0]])

    sol = solve_ivp(
        field, (0.0, 20.0), Vector([1.0, 0.0]), method=method, rtol=1e-10, atol=1e-12
    )
    energy = sol.y[:, 0] ** 2 + sol.y[:, 1] ** 2
    np.testing.assert_allclose(energy, np.ones_like(energy), rtol=1e-6, atol=1e-9)
