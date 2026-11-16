"""Regression tests for :mod:`scw.manifold`.

These pin the manifold-specific edge cases that are easy to get subtly wrong:
that the metric is rejected when it is not a valid (symmetric, positive
definite) metric, that the sphere metric vanishes exactly at the poles and is
excluded there, that tangent spaces are distinguished by base point, and that
``flat``/``sharp`` are exact inverses on a well-conditioned metric.
"""

from __future__ import annotations

import numpy as np
import pytest

from scw.exceptions import DimensionError, NumericalError
from scw.manifold import EuclideanSpace, Metric, Sphere
from scw.math_core import Vector


def test_metric_rejects_rank_deficient_matrix() -> None:
    # Regression: a singular "metric" (zero eigenvalue) is not positive
    # definite and must be rejected, not silently accepted.
    with pytest.raises(NumericalError):
        Metric([[1.0, 1.0], [1.0, 1.0]], point=(0.0, 0.0))


def test_metric_rejects_indefinite_matrix() -> None:
    with pytest.raises(NumericalError):
        Metric([[1.0, 0.0], [0.0, -1.0]], point=(0.0, 0.0))


def test_metric_accepts_near_symmetric_within_tolerance() -> None:
    # A matrix that is symmetric up to round-off must be accepted; the
    # symmetry check uses a scale-aware tolerance, not exact equality.
    g = Metric([[1.0, 0.5 + 1e-15], [0.5, 1.0]], point=(0.0, 0.0))
    assert g.dimension == 2


def test_sphere_metric_vanishes_at_pole() -> None:
    # Regression: at theta -> 0 the metric component g_phiphi = r^2 sin^2(theta)
    # vanishes, so the coordinate chart degenerates and the pole is rejected.
    s = Sphere(radius=1.0)
    with pytest.raises(DimensionError):
        s.metric((0.0, 0.0))
    with pytest.raises(DimensionError):
        s.metric((np.pi, 0.0))


def test_sphere_metric_near_pole_is_small_but_positive() -> None:
    s = Sphere(radius=1.0)
    theta = 1e-6
    g = s.metric((theta, 0.0))
    assert g.components[1, 1] > 0.0
    assert g.components[1, 1] == pytest.approx(theta**2, rel=1e-6)


def test_tangent_spaces_separated_by_point_not_just_dimension() -> None:
    # Regression: two points of the same manifold give distinct tangent spaces
    # even though the dimensions match, so tangent vectors cannot be mixed.
    e = EuclideanSpace(3)
    p = (0.0, 0.0, 0.0)
    q = (0.0, 0.0, 1e-12)
    assert e.tangent_space(p) != e.tangent_space(q)


def test_flat_sharp_exact_inverse_for_identity_metric() -> None:
    # Regression: with the identity metric flat and sharp are the identity on
    # coordinates, so the round-trip must be bit-for-bit exact.
    e = EuclideanSpace(2)
    p = (3.0, -4.0)
    g = e.metric(p)
    v = e.tangent_vector([1.5, -2.25], point=p)
    back = g.sharp(g.flat(v))
    np.testing.assert_array_equal(back.data, v.data)


def test_metric_norm_is_scale_aware_for_tiny_components() -> None:
    # Regression: the metric norm is computed from the Cholesky factor, so a
    # tiny tangent vector must not underflow to zero.
    g = Metric(np.diag([1e-300, 1e-300]), point=(0.0, 0.0))
    v = g.sharp(g.flat(Vector([1.0, 1.0], space=g.tangent_space)))
    assert g.norm(v) > 0.0
