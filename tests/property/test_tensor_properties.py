"""Property-based tests for :class:`scw.math_core.Tensor`.

Comparisons use a scale-aware tolerance (see ``test_vector_properties`` for the
rationale): tensor products raise the dynamic range, so the naive default
absolute tolerance of ``numpy.allclose`` is too tight.
"""

from __future__ import annotations

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from scw.math_core import Tensor

floats = st.floats(
    min_value=-1e2,
    max_value=1e2,
    allow_nan=False,
    allow_infinity=False,
    allow_subnormal=False,
)

_ATOL = 1e-6
_RTOL = 1e-9


def assert_close(lhs: np.ndarray, rhs: np.ndarray) -> None:
    np.testing.assert_allclose(lhs, rhs, rtol=_RTOL, atol=_ATOL)


@st.composite
def matrices(draw, rows: int = 3, cols: int = 3) -> Tensor:
    raw = draw(st.lists(floats, min_size=rows * cols, max_size=rows * cols))
    return Tensor(np.array(raw).reshape(rows, cols))


@st.composite
def vectors(draw, n: int = 3) -> Tensor:
    return Tensor(draw(st.lists(floats, min_size=n, max_size=n)))


@settings(max_examples=200, deadline=None)
@given(a=matrices(), b=matrices())
def test_outer_matches_numpy(a: Tensor, b: Tensor) -> None:
    assert a.outer(b).shape == a.shape + b.shape
    assert_close(a.outer(b).data, np.tensordot(a.data, b.data, axes=0))


@settings(max_examples=200, deadline=None)
@given(a=vectors(), b=matrices())
def test_outer_is_bilinear_in_scaling(a: Tensor, b: Tensor) -> None:
    assert_close((3.0 * a).outer(b).data, 3.0 * a.outer(b).data)


@settings(max_examples=200, deadline=None)
@given(a=vectors(), b=vectors(), c=vectors())
def test_outer_is_associative_in_shape(a: Tensor, b: Tensor, c: Tensor) -> None:
    assert a.outer(b.outer(c)).shape == (a.size, b.size, c.size)
    assert_close(a.outer(b.outer(c)).data, a.outer(b).outer(c).data)


@settings(max_examples=200, deadline=None)
@given(a=matrices(), b=matrices())
def test_contract_matches_matmul(a: Tensor, b: Tensor) -> None:
    assert_close(a.contract(b).data, a.data @ b.data)


@settings(max_examples=200, deadline=None)
@given(a=matrices(), b=matrices())
def test_contract_is_bilinear_in_scaling(a: Tensor, b: Tensor) -> None:
    assert_close((2.0 * a).contract(b).data, 2.0 * a.contract(b).data)


@settings(max_examples=200, deadline=None)
@given(a=matrices(), b=matrices(), c=matrices())
def test_contract_is_associative(a: Tensor, b: Tensor, c: Tensor) -> None:
    assert_close(a.contract(b).contract(c).data, a.contract(b.contract(c)).data)


@settings(max_examples=200, deadline=None)
@given(a=matrices())
def test_trace_matches_numpy_and_is_linear(a: Tensor) -> None:
    assert_close(a.trace().data, np.array(np.trace(a.data)))
    assert_close(a.trace().data, 2.0 * (0.5 * a).trace().data)


@settings(max_examples=200, deadline=None)
@given(a=matrices(), b=matrices())
def test_trace_of_outer_contracts_the_shared_index_pair(a: Tensor, b: Tensor) -> None:
    # a.outer(b) has indices (i, j, k, l); contracting (i, j) leaves
    # trace(a) * b, and a full double trace is trace(a) * trace(b).
    assert_close(a.outer(b).trace(axis1=0, axis2=1).data, np.trace(a.data) * b.data)
    assert_close(
        a.outer(b).trace(axis1=0, axis2=1).trace().data,
        np.array(np.trace(a.data) * np.trace(b.data)),
    )


@settings(max_examples=200, deadline=None)
@given(a=matrices(), b=matrices())
def test_addition_is_commutative(a: Tensor, b: Tensor) -> None:
    assert (a + b) == (b + a)


@settings(max_examples=200, deadline=None)
@given(a=matrices())
def test_shape_preserved_under_operations(a: Tensor) -> None:
    assert (a + a).shape == a.shape
    assert (2.0 * a).shape == a.shape
    assert (-a).shape == a.shape
