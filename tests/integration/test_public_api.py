"""Integration tests exercising the public API surface."""

from __future__ import annotations

import numpy as np
import pytest

import scw
from scw.math_core import (
    Basis,
    Covector,
    LinearMap,
    Matrix,
    Tensor,
    Vector,
    VectorSpace,
    einsum,
)
from scw.numerical import lu, solve, solve_ivp, svd


def test_public_reexports() -> None:
    assert scw.Vector is Vector
    assert scw.Covector is Covector
    assert scw.Matrix is Matrix
    assert scw.LinearMap is LinearMap
    assert scw.VectorSpace is VectorSpace
    assert scw.Tensor is Tensor
    assert scw.Basis is Basis


def test_version_is_a_string() -> None:
    assert isinstance(scw.__version__, str)
    assert scw.__version__.count(".") >= 1


def test_linear_map_accepts_vector_and_returns_correct_dimension() -> None:
    t = LinearMap.from_matrix(Matrix([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]))
    out = t.apply(Vector([1.0, 0.0, -1.0]))
    assert out.dimension == 2


def test_end_to_end_workflow() -> None:
    a = Matrix([[2.0, 0.0], [0.0, 3.0]])
    t = LinearMap.from_matrix(a)
    v = Vector([1.0, 1.0])
    alpha = Covector([1.0, -1.0])
    assert alpha(t.apply(v)) == np.dot(alpha.data, a.data @ v.data)


def test_tensor_matrix_bridge() -> None:
    # A Matrix, a Tensor and a Basis describe the same linear object.
    a = Matrix([[2.0, 1.0], [0.0, 3.0]])
    t = Tensor(a.data)
    assert np.allclose(t.contract(Tensor.eye(2)).data, a.data)
    space = VectorSpace(2, name="V")
    basis = Basis([Vector([1.0, 0.0], space=space), Vector([0.0, 1.0], space=space)])
    v = Vector([1.0, 2.0], space=space)
    assert basis.from_coordinates(basis.to_coordinates(v)) == v
    assert np.allclose(a.apply(v).data, t.contract(Tensor(v.data)).data)


def test_einsum_bridge_to_numpy() -> None:
    a = Tensor([[1.0, 2.0], [3.0, 4.0]])
    b = Tensor([[5.0, 6.0], [7.0, 8.0]])
    assert np.allclose(einsum("ij,jk->ik", a, b).data, a.data @ b.data)


def test_symbolic_round_trip_to_numeric() -> None:
    pytest.importorskip("sympy")
    from sympy import symbols

    from scw.symbolic import SymbolicMatrix, to_symbolic

    a, b = symbols("a b")
    m = SymbolicMatrix([[a, 1], [2, b]]).subs({a: 4, b: 3})
    assert m.to_numeric() == Matrix([[4.0, 1.0], [2.0, 3.0]])
    numeric = Matrix([[2.0, 0.0], [0.0, 5.0]])
    assert to_symbolic(numeric).to_numeric() == numeric


def test_numerical_reexports() -> None:
    from scw.numerical import (
        EighResult,
        LeastSquaresResult,
        LUResult,
        ODESolution,
        QRResult,
        SVDResult,
        cholesky,
        eigh,
        lstsq,
        lu,
        qr,
        solve_ivp,
        svd,
    )

    assert all(callable(fn) for fn in (lu, qr, svd, cholesky, eigh, lstsq, solve_ivp))
    assert all(
        isinstance(cls, type)
        for cls in (
            LUResult,
            QRResult,
            SVDResult,
            EighResult,
            LeastSquaresResult,
            ODESolution,
        )
    )


def test_decomposition_and_solve_agree_on_a_linear_system() -> None:
    a = Matrix([[4.0, 7.0], [2.0, 6.0]])
    b = Vector([1.0, 0.0])
    x = solve(a, b)
    # A factorization must reconstruct A, so applying it to x recovers b.
    np.testing.assert_allclose(lu(a).reconstruct().data @ x.data, b.data, atol=1e-9)
    np.testing.assert_allclose(svd(a).reconstruct().data @ x.data, b.data, atol=1e-9)


def test_ode_solution_feeds_back_into_the_domain_layer() -> None:
    # The trajectory is a sequence of Vectors, usable by the core operations.
    def field(t, y):
        return Vector([-y.data[1], y.data[0]])

    sol = solve_ivp(field, (0.0, 1.0), Vector([1.0, 0.0]), t_eval=[0.0, 1.0])
    first, last = sol.state_at(0), sol.state_at(1)
    assert first.dimension == last.dimension == 2
    assert first.dot(first) == pytest.approx(1.0)
