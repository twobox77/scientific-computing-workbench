"""Property-based tests for :mod:`scw.manifold`.

The laws checked here are the ones a Riemannian metric must satisfy: symmetry,
positive-definiteness of the induced inner product, bilinearity, the
Cauchy-Schwarz inequality, and that ``flat`` and ``sharp`` are inverse
isomorphisms between tangent vectors and cotangent covectors.  Comparisons
between differently-rounded computations use a scale-aware tolerance
(``rtol=1e-9, atol=1e-6``); see ``tests/property/test_vector_properties.py``.
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from scw.manifold import EuclideanSpace, Metric, Sphere
from scw.math_core import Covector

_ATOL = 1e-6
_RTOL = 1e-9

_finite = st.floats(-1e3, 1e3, allow_nan=False, allow_infinity=False)
_positive = st.floats(0.1, 1e3, allow_nan=False, allow_infinity=False)


@st.composite
def spd_matrix(draw, n: int = 3):
    raw = draw(st.lists(_finite, min_size=n * n, max_size=n * n))
    b = np.asarray(raw).reshape(n, n)
    return b @ b.T + n * np.eye(n)


@st.composite
def point_and_vectors(draw, dimension: int = 3):
    point = draw(st.lists(_finite, min_size=dimension, max_size=dimension))
    u = draw(st.lists(_finite, min_size=dimension, max_size=dimension))
    v = draw(st.lists(_finite, min_size=dimension, max_size=dimension))
    return point, np.asarray(u), np.asarray(v)


@settings(max_examples=100, deadline=None)
@given(matrix=spd_matrix())
def test_metric_accepts_symmetric_positive_definite(matrix: np.ndarray) -> None:
    custom = Metric(matrix, point=(0.0, 0.0, 0.0))
    assert custom.dimension == 3
    np.testing.assert_allclose(custom.components, matrix, rtol=_RTOL, atol=_ATOL)


@settings(max_examples=100, deadline=None)
@given(data=point_and_vectors())
def test_inner_product_is_symmetric(data) -> None:
    point, u, v = data
    e = EuclideanSpace(3)
    g = e.metric(point)
    uv = e.tangent_vector(u, point=point)
    vv = e.tangent_vector(v, point=point)
    assert g.inner(uv, vv) == pytest.approx(g.inner(vv, uv), rel=_RTOL, abs=_ATOL)


@settings(max_examples=100, deadline=None)
@given(data=point_and_vectors())
def test_inner_product_is_bilinear(data) -> None:
    point, u, v = data
    e = EuclideanSpace(3)
    g = e.metric(point)
    uv = e.tangent_vector(u, point=point)
    vv = e.tangent_vector(v, point=point)
    assert g.inner(uv + vv, uv + vv) == pytest.approx(
        g.inner(uv, uv) + 2.0 * g.inner(uv, vv) + g.inner(vv, vv),
        rel=_RTOL,
        abs=_ATOL,
    )


@settings(max_examples=100, deadline=None)
@given(data=point_and_vectors())
def test_cauchy_schwarz(data) -> None:
    point, u, v = data
    e = EuclideanSpace(3)
    g = e.metric(point)
    uv = e.tangent_vector(u, point=point)
    vv = e.tangent_vector(v, point=point)
    lhs = abs(g.inner(uv, vv))
    rhs = g.norm(uv) * g.norm(vv)
    assert lhs <= rhs + _ATOL * (1.0 + rhs)


@settings(max_examples=100, deadline=None)
@given(data=point_and_vectors())
def test_flat_sharp_roundtrip(data) -> None:
    point, u, _ = data
    e = EuclideanSpace(3)
    g = e.metric(point)
    v = e.tangent_vector(u, point=point)
    back = g.sharp(g.flat(v))
    np.testing.assert_allclose(back.data, v.data, rtol=_RTOL, atol=_ATOL)
    assert back.space == v.space


@settings(max_examples=100, deadline=None)
@given(
    theta=st.floats(0.05, np.pi - 0.05, allow_nan=False),
    radius=_positive,
    u=st.lists(_finite, min_size=2, max_size=2),
    v=st.lists(_finite, min_size=2, max_size=2),
)
def test_sphere_metric_is_positive_definite(theta, radius, u, v) -> None:
    s = Sphere(radius=radius)
    p = (theta, 0.0)
    g = s.metric(p)
    uv = s.tangent_vector(u, point=p)
    vv = s.tangent_vector(v, point=p)
    assert g.inner(uv, uv) >= 0.0
    assert g.inner(uv, uv) == pytest.approx(
        radius**2 * u[0] ** 2 + radius**2 * np.sin(theta) ** 2 * u[1] ** 2,
        rel=_RTOL,
        abs=_ATOL,
    )
    assert g.inner(uv, vv) == pytest.approx(g.inner(vv, uv), rel=_RTOL, abs=_ATOL)


@settings(max_examples=100, deadline=None)
@given(
    theta=st.floats(0.05, np.pi - 0.05, allow_nan=False),
    alpha=st.lists(_finite, min_size=2, max_size=2),
)
def test_sphere_sharp_is_inverse_of_flat(theta, alpha) -> None:
    s = Sphere(radius=1.0)
    p = (theta, 0.0)
    g = s.metric(p)
    covector = Covector(alpha, dual_space=s.tangent_space(p))
    v = g.sharp(covector)
    np.testing.assert_allclose(g.flat(v).data, covector.data, rtol=_RTOL, atol=_ATOL)
