"""Property-based tests for :class:`scw.math_core.LinearMap` and
:class:`scw.math_core.Matrix`, covering the algebraic laws required by the
specification (§7.2).
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from scw.math_core import LinearMap, Matrix, Vector

floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
    allow_subnormal=False,
)

# Matrix entries are bounded more tightly: a 3x3 triple product scales as
# ``M**3``, so ``|entry| <= 1e2`` keeps the accumulated rounding error of an
# associativity check near ``1e-8`` (comfortably under the tolerance below)
# while still catching real algebraic mistakes, which differ by O(1) or more.
matrix_floats = st.floats(
    min_value=-1e2,
    max_value=1e2,
    allow_nan=False,
    allow_infinity=False,
    allow_subnormal=False,
)

# Floating-point comparisons of computed products are approximate by nature;
# the specification requires associativity only "within tolerance" (§7.2).
_ATOL = 1e-6
_RTOL = 1e-9


def assert_close(lhs: np.ndarray, rhs: np.ndarray) -> None:
    np.testing.assert_allclose(lhs, rhs, rtol=_RTOL, atol=_ATOL)


@st.composite
def matrices(draw, rows: int = 3, cols: int = 3) -> Matrix:
    raw = draw(st.lists(matrix_floats, min_size=rows * cols, max_size=rows * cols))
    return Matrix(np.array(raw).reshape(rows, cols))


@st.composite
def vectors(draw, n: int = 3) -> Vector:
    return Vector(draw(st.lists(floats, min_size=n, max_size=n)))


@settings(max_examples=200, deadline=None)
@given(t=matrices(), u=vectors(), v=vectors())
def test_map_preserves_addition(t: Matrix, u: Vector, v: Vector) -> None:
    m = LinearMap.from_matrix(t)
    assert_close(m.apply(u + v).data, (m.apply(u) + m.apply(v)).data)


@settings(max_examples=200, deadline=None)
@given(t=matrices(), v=vectors(), c=floats)
def test_map_preserves_scalar_multiplication(t: Matrix, v: Vector, c: float) -> None:
    m = LinearMap.from_matrix(t)
    assert_close(m.apply(c * v).data, (c * m.apply(v)).data)


@settings(max_examples=200, deadline=None)
@given(t=matrices(), v=vectors())
def test_map_zero_goes_to_zero(t: Matrix, v: Vector) -> None:
    m = LinearMap.from_matrix(t)
    zero = Vector(np.zeros(v.dimension))
    assert_close(m.apply(zero).data, np.zeros(m.codomain.dimension))


@settings(max_examples=200, deadline=None)
@given(t=matrices(), v=vectors())
def test_apply_matches_numpy(t: Matrix, v: Vector) -> None:
    m = LinearMap.from_matrix(t)
    assert_close(m.apply(v).data, t.data @ v.data)


@settings(max_examples=200, deadline=None)
@given(s=matrices(), t=matrices(), v=vectors())
def test_composition_matches_sequential_application(
    s: Matrix, t: Matrix, v: Vector
) -> None:
    outer = LinearMap.from_matrix(t)
    inner = LinearMap.from_matrix(s)
    composed = outer.compose(inner)
    assert_close(composed.apply(v).data, outer.apply(inner.apply(v)).data)


@settings(max_examples=200, deadline=None)
@given(a=matrices(), b=matrices())
def test_matrix_product_matches_numpy(a: Matrix, b: Matrix) -> None:
    assert_close((a @ b).data, a.data @ b.data)


@settings(max_examples=200, deadline=None)
@given(a=matrices(), b=matrices())
def test_transpose_involution(a: Matrix, b: Matrix) -> None:
    assert a.transpose().transpose() == a
    assert_close((a @ b).transpose().data, (b.transpose() @ a.transpose()).data)


@settings(max_examples=200, deadline=None)
@given(a=matrices(), b=matrices(), c=matrices())
def test_matrix_multiplication_associative(a: Matrix, b: Matrix, c: Matrix) -> None:
    assert_close(((a @ b) @ c).data, (a @ (b @ c)).data)


@settings(max_examples=200, deadline=None)
@given(a=matrices(), b=matrices())
def test_matrix_addition_commutative(a: Matrix, b: Matrix) -> None:
    assert (a + b) == (b + a)


def test_matrix_multiplication_dimension_rule_is_enforced() -> None:
    a = Matrix(np.zeros((2, 3)))
    b = Matrix(np.zeros((2, 2)))
    with pytest.raises(ValueError):
        a @ b


@settings(max_examples=200, deadline=None)
@given(a=matrices())
def test_matrix_shape_is_preserved_under_operations(a: Matrix) -> None:
    assert (a + a).shape == a.shape
    assert (2.0 * a).shape == a.shape
    assert a.transpose().shape == (a.shape[1], a.shape[0])
