"""Property-based tests for the algebraic laws of the core types."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from scw.math_core import Covector, Matrix, Vector

floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
    allow_subnormal=False,
)


@st.composite
def vectors(draw, n: int = 4) -> Vector:
    return Vector(draw(st.lists(floats, min_size=n, max_size=n)))


@settings(max_examples=200, deadline=None)
@given(u=vectors(), v=vectors(), w=vectors())
def test_addition_is_commutative(u: Vector, v: Vector, w: Vector) -> None:
    assert np.allclose((u + v).data, (v + u).data)


@settings(max_examples=200, deadline=None)
@given(u=vectors(), v=vectors(), w=vectors())
def test_addition_is_associative(u: Vector, v: Vector, w: Vector) -> None:
    assert np.allclose(((u + v) + w).data, (u + (v + w)).data)


@settings(max_examples=200, deadline=None)
@given(u=vectors(), v=vectors(), a=floats)
def test_scalar_distributes_over_addition(u: Vector, v: Vector, a: float) -> None:
    assert np.allclose((a * (u + v)).data, (a * u + a * v).data)


@settings(max_examples=200, deadline=None)
@given(v=vectors())
def test_norm_is_non_negative(v: Vector) -> None:
    assert v.norm() >= 0.0


@settings(max_examples=200, deadline=None)
@given(v=vectors())
def test_norm_zero_iff_zero(v: Vector) -> None:
    if v.is_zero():
        assert v.norm() == pytest.approx(0.0)
    else:
        assert v.norm() > 0.0


@settings(max_examples=200, deadline=None)
@given(u=vectors(), v=vectors())
def test_dot_is_symmetric(u: Vector, v: Vector) -> None:
    assert u.dot(v) == pytest.approx(v.dot(u))


@settings(max_examples=200, deadline=None)
@given(
    alpha=st.lists(floats, min_size=4, max_size=4),
    u=vectors(),
    v=vectors(),
)
def test_pairing_is_linear(alpha, u: Vector, v: Vector) -> None:
    a = Covector(alpha)
    assert a(u + v) == pytest.approx(a(u) + a(v))


@settings(max_examples=200, deadline=None)
@given(
    alpha=st.lists(floats, min_size=4, max_size=4),
    v=vectors(),
    c=floats,
)
def test_pairing_scalar_linearity(alpha, v: Vector, c: float) -> None:
    a = Covector(alpha)
    assert a(c * v) == pytest.approx(c * a(v))


@settings(max_examples=100, deadline=None)
@given(
    rows=st.integers(min_value=1, max_value=4),
    cols=st.integers(min_value=1, max_value=4),
    seed=st.integers(min_value=0, max_value=10_000),
)
def test_matrix_vector_product_matches_numpy(rows: int, cols: int, seed: int) -> None:
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((rows, cols))
    m = Matrix(raw)
    v = Vector(rng.standard_normal(cols))
    assert np.allclose(m.apply(v).data, raw @ v.data)
