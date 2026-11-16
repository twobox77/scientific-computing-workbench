"""Unit tests for :mod:`scw.manifold` (tangent geometry and metrics)."""

from __future__ import annotations

import numpy as np
import pytest

from scw.exceptions import DimensionError, NonFiniteError, NumericalError
from scw.manifold import (
    CotangentSpace,
    EuclideanSpace,
    Metric,
    Sphere,
    TangentSpace,
)
from scw.math_core import Covector, Vector


def test_euclidean_dimension_and_name() -> None:
    e = EuclideanSpace(3, name="E")
    assert e.dimension == 3
    assert e.name == "E"
    assert str(e) == "E"


def test_euclidean_rejects_bad_dimension() -> None:
    with pytest.raises(TypeError):
        EuclideanSpace(2.5)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        EuclideanSpace(0)


def test_sphere_dimension_is_two_and_fixed() -> None:
    s = Sphere(radius=2.0)
    assert s.dimension == 2
    with pytest.raises(TypeError):
        Sphere(dimension=3)  # type: ignore[call-arg]


def test_sphere_rejects_bad_radius() -> None:
    with pytest.raises(ValueError):
        Sphere(radius=0.0)
    with pytest.raises(ValueError):
        Sphere(radius=float("nan"))


def test_tangent_space_is_a_vector_space() -> None:
    e = EuclideanSpace(3)
    ts = e.tangent_space((1.0, 2.0, 3.0))
    assert isinstance(ts, TangentSpace)
    assert ts.dimension == 3
    assert ts.point == (1.0, 2.0, 3.0)


def test_tangent_and_cotangent_space_are_dual() -> None:
    e = EuclideanSpace(2)
    ts = e.tangent_space((0.0, 0.0))
    cts = e.cotangent_space((0.0, 0.0))
    assert isinstance(cts, CotangentSpace)
    assert ts != cts
    assert ts.dimension == cts.dimension == 2


def test_tangent_spaces_differ_by_point() -> None:
    e = EuclideanSpace(2)
    assert e.tangent_space((1.0, 0.0)) != e.tangent_space((0.0, 1.0))
    assert e.tangent_space((1.0, 0.0)) == e.tangent_space((1.0, 0.0))


def test_tangent_spaces_differ_by_manifold() -> None:
    a = EuclideanSpace(2, name="A")
    b = EuclideanSpace(2, name="B")
    assert a.tangent_space((0.0, 0.0)) != b.tangent_space((0.0, 0.0))


def test_tangent_vector_lives_in_tangent_space() -> None:
    e = EuclideanSpace(3)
    p = (1.0, 2.0, 3.0)
    v = e.tangent_vector([1.0, 0.0, 0.0], point=p)
    assert isinstance(v, Vector)
    assert v.space == e.tangent_space(p)


def test_tangent_vectors_at_different_points_do_not_mix() -> None:
    e = EuclideanSpace(3)
    v = e.tangent_vector([1.0, 0.0, 0.0], point=(1.0, 2.0, 3.0))
    w = e.tangent_vector([1.0, 0.0, 0.0], point=(1.0, 2.0, 4.0))
    with pytest.raises(DimensionError):
        v + w


def test_tangent_vectors_at_same_point_add() -> None:
    e = EuclideanSpace(3)
    p = (1.0, 2.0, 3.0)
    v = e.tangent_vector([1.0, 0.0, 0.0], point=p)
    w = e.tangent_vector([0.0, 2.0, 0.0], point=p)
    np.testing.assert_allclose((v + w).data, [1.0, 2.0, 0.0])
    assert (v + w).space == e.tangent_space(p)


def test_cotangent_covector_dual_space() -> None:
    e = EuclideanSpace(3)
    p = (1.0, 2.0, 3.0)
    alpha = e.cotangent_covector([1.0, 0.0, 0.0], point=p)
    assert isinstance(alpha, Covector)
    assert alpha.dual_space == e.tangent_space(p)


def test_point_wrong_dimension_rejected() -> None:
    e = EuclideanSpace(3)
    with pytest.raises(DimensionError):
        e.tangent_space((1.0, 2.0))


def test_point_non_finite_rejected() -> None:
    e = EuclideanSpace(2)
    with pytest.raises(NonFiniteError):
        e.tangent_space((1.0, float("inf")))


def test_euclidean_metric_is_identity() -> None:
    e = EuclideanSpace(3)
    g = e.metric((1.0, 2.0, 3.0))
    np.testing.assert_allclose(g.components, np.eye(3))
    assert g.dimension == 3
    assert g.point == (1.0, 2.0, 3.0)


def test_sphere_metric_components() -> None:
    s = Sphere(radius=2.0)
    theta = np.pi / 3
    g = s.metric((theta, 0.5))
    r2 = 4.0
    np.testing.assert_allclose(g.components, np.diag([r2, r2 * np.sin(theta) ** 2]))


def test_sphere_metric_rejects_poles() -> None:
    s = Sphere()
    with pytest.raises(DimensionError):
        s.metric((0.0, 0.0))
    with pytest.raises(DimensionError):
        s.metric((np.pi, 0.0))


def test_metric_rejects_non_square() -> None:
    with pytest.raises(DimensionError):
        Metric([[1.0, 2.0, 3.0]], point=(0.0, 0.0))


def test_metric_rejects_asymmetric() -> None:
    with pytest.raises(NumericalError):
        Metric([[1.0, 2.0], [3.0, 1.0]], point=(0.0, 0.0))


def test_metric_rejects_non_positive_definite() -> None:
    with pytest.raises(NumericalError):
        Metric([[1.0, 2.0], [2.0, 1.0]], point=(0.0, 0.0))


def test_metric_rejects_non_finite() -> None:
    with pytest.raises(NonFiniteError):
        Metric([[1.0, 0.0], [0.0, float("nan")]], point=(0.0, 0.0))


def test_metric_components_are_read_only() -> None:
    g = EuclideanSpace(2).metric((0.0, 0.0))
    with pytest.raises(ValueError):
        g.components[0, 0] = 5.0


def test_metric_inner_product_is_symmetric_and_bilinear() -> None:
    e = EuclideanSpace(3)
    p = (0.0, 0.0, 0.0)
    g = e.metric(p)
    u = e.tangent_vector([1.0, 2.0, 3.0], point=p)
    v = e.tangent_vector([-1.0, 0.0, 2.0], point=p)
    assert g.inner(u, v) == pytest.approx(g.inner(v, u))
    assert g.inner(u, v) == pytest.approx(float(np.dot(u.data, v.data)))


def test_metric_inner_uses_components() -> None:
    g = Metric(np.diag([4.0, 9.0]), point=(0.0, 0.0))
    u = Vector([1.0, 1.0], space=g.tangent_space)
    v = Vector([1.0, -1.0], space=g.tangent_space)
    # u^T G v = 4*1*1 + 9*1*(-1) = -5
    assert g.inner(u, v) == pytest.approx(-5.0)


def test_metric_norm_matches_inner_sqrt() -> None:
    g = Metric(np.diag([4.0, 9.0]), point=(0.0, 0.0))
    v = Vector([1.0, 2.0], space=g.tangent_space)
    assert g.norm(v) == pytest.approx(np.sqrt(g.inner(v, v)))


def test_metric_norm_rejects_mismatched_tangent_space() -> None:
    e = EuclideanSpace(2)
    g = e.metric((0.0, 0.0))
    other = e.tangent_vector([1.0, 0.0], point=(1.0, 1.0))
    with pytest.raises(DimensionError):
        g.norm(other)


def test_metric_inner_rejects_non_vector() -> None:
    g = EuclideanSpace(2).metric((0.0, 0.0))
    with pytest.raises(TypeError):
        g.inner([1.0, 0.0], [1.0, 0.0])  # type: ignore[arg-type]


def test_flat_sharp_are_inverse() -> None:
    e = EuclideanSpace(3)
    p = (1.0, -2.0, 0.5)
    g = e.metric(p)
    v = e.tangent_vector([0.3, -1.2, 2.5], point=p)
    alpha = g.flat(v)
    assert isinstance(alpha, Covector)
    assert alpha.dual_space == e.tangent_space(p)
    back = g.sharp(alpha)
    np.testing.assert_allclose(back.data, v.data)
    assert back.space == e.tangent_space(p)


def test_flat_sharp_inverse_on_sphere() -> None:
    s = Sphere(radius=1.5)
    p = (np.pi / 2, 0.3)
    g = s.metric(p)
    v = s.tangent_vector([0.7, -0.4], point=p)
    np.testing.assert_allclose(g.sharp(g.flat(v)).data, v.data)


def test_flat_matches_inner_against_basis_vectors() -> None:
    s = Sphere(radius=2.0)
    p = (np.pi / 3, 1.0)
    g = s.metric(p)
    v = s.tangent_vector([1.0, 2.0], point=p)
    alpha = g.flat(v)
    for e_i in ([1.0, 0.0], [0.0, 1.0]):
        basis = s.tangent_vector(e_i, point=p)
        assert alpha.evaluate(basis) == pytest.approx(g.inner(v, basis))


def test_sharp_rejects_non_covector() -> None:
    g = EuclideanSpace(2).metric((0.0, 0.0))
    with pytest.raises(TypeError):
        g.sharp([1.0, 0.0])  # type: ignore[arg-type]


def test_metric_repr_mentions_components() -> None:
    g = EuclideanSpace(2).metric((0.0, 0.0))
    assert repr(g).startswith("Metric(")


def test_manifold_is_abstract() -> None:
    from scw.manifold import Manifold

    with pytest.raises(TypeError):
        Manifold()  # type: ignore[abstract]
