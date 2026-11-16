"""Property-based tests for the algebraic laws of the core types.

Comparisons of two differently-rounded computations use a scale-aware
tolerance (``assert_close``): the specification requires the laws only
"within floating tolerance" (§7.2), and the naive default absolute tolerance
is far too tight once operands reach ``1e6`` and results cancel toward zero.
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from scw.math_core import Covector, Matrix, Vector

# Wide range, used by the norm properties which must stay finite and
# non-negative across the whole representable span.
floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
    allow_subnormal=False,
)

# Narrower range for the algebraic-law properties.  Products of these values
# stay well-conditioned, so the accumulated rounding error is tiny compared to
# the tolerance below, while a genuine algebraic mistake would differ by orders
# of magnitude more.
law_floats = st.floats(
    min_value=-1e3,
    max_value=1e3,
    allow_nan=False,
    allow_infinity=False,
    allow_subnormal=False,
)

_ATOL = 1e-6
_RTOL = 1e-9


def assert_close(lhs, rhs) -> None:
    np.testing.assert_allclose(lhs, rhs, rtol=_RTOL, atol=_ATOL)


@st.composite
def vectors(draw, n: int = 4) -> Vector:
    return Vector(draw(st.lists(floats, min_size=n, max_size=n)))


@st.composite
def law_vectors(draw, n: int = 4) -> Vector:
    return Vector(draw(st.lists(law_floats, min_size=n, max_size=n)))


@settings(max_examples=200, deadline=None)
@given(u=law_vectors(), v=law_vectors(), w=law_vectors())
def test_addition_is_commutative(u: Vector, v: Vector, w: Vector) -> None:
    assert_close((u + v).data, (v + u).data)


@settings(max_examples=200, deadline=None)
@given(u=law_vectors(), v=law_vectors(), w=law_vectors())
def test_addition_is_associative(u: Vector, v: Vector, w: Vector) -> None:
    assert_close(((u + v) + w).data, (u + (v + w)).data)


@settings(max_examples=200, deadline=None)
@given(u=law_vectors(), v=law_vectors(), a=law_floats)
def test_scalar_distributes_over_addition(u: Vector, v: Vector, a: float) -> None:
    assert_close((a * (u + v)).data, (a * u + a * v).data)


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
@given(u=law_vectors(), v=law_vectors())
def test_dot_is_symmetric(u: Vector, v: Vector) -> None:
    assert u.dot(v) == pytest.approx(v.dot(u), rel=_RTOL, abs=_ATOL)


@settings(max_examples=200, deadline=None)
@given(
    alpha=st.lists(law_floats, min_size=4, max_size=4),
    u=law_vectors(),
    v=law_vectors(),
)
def test_pairing_is_linear(alpha, u: Vector, v: Vector) -> None:
    a = Covector(alpha)
    assert a(u + v) == pytest.approx(a(u) + a(v), rel=_RTOL, abs=_ATOL)


@settings(max_examples=200, deadline=None)
@given(
    alpha=st.lists(law_floats, min_size=4, max_size=4),
    v=law_vectors(),
    c=law_floats,
)
def test_pairing_scalar_linearity(alpha, v: Vector, c: float) -> None:
    a = Covector(alpha)
    assert a(c * v) == pytest.approx(c * a(v), rel=_RTOL, abs=_ATOL)


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
