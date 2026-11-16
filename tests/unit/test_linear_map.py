"""Unit tests for :class:`scw.math_core.LinearMap`."""

from __future__ import annotations

import pytest

from scw.exceptions import DimensionError
from scw.math_core import LinearMap, Matrix, Vector, VectorSpace


def test_from_matrix_infers_dimensions() -> None:
    t = LinearMap.from_matrix(Matrix([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]))
    assert t.codomain.dimension == 2
    assert t.domain.dimension == 3


def test_apply_returns_codomain_vector() -> None:
    t = LinearMap(Matrix([[1.0, 0.0], [0.0, 1.0]]))
    out = t.apply(Vector([3.0, 4.0]))
    assert out.space == t.codomain
    assert out.to_numpy().tolist() == [3.0, 4.0]


def test_call_is_alias_for_apply() -> None:
    t = LinearMap(Matrix([[2.0]]))
    assert t(Vector([3.0])).to_numpy().tolist() == [6.0]


def test_explicit_domain_codomain_validated() -> None:
    with pytest.raises(DimensionError):
        LinearMap(
            Matrix([[1.0, 2.0]]),
            codomain=VectorSpace(2),
            domain=VectorSpace(2),
        )


def test_apply_dimension_validation() -> None:
    t = LinearMap(Matrix([[1.0, 2.0]]))
    with pytest.raises(DimensionError):
        t.apply(Vector([1.0, 2.0, 3.0]))


def test_apply_requires_vector() -> None:
    with pytest.raises(TypeError):
        LinearMap(Matrix([[1.0]])).apply([1.0])  # type: ignore[arg-type]


def test_composition() -> None:
    s = LinearMap(Matrix([[2.0, 0.0], [0.0, 2.0]]))
    t = LinearMap(Matrix([[1.0, 1.0], [0.0, 1.0]]))
    composed = t.compose(s)
    assert composed.domain.dimension == 2
    assert composed.codomain.dimension == 2
    v = Vector([1.0, 1.0])
    assert (
        composed.apply(v).to_numpy().tolist() == t.apply(s.apply(v)).to_numpy().tolist()
    )


def test_composition_dimension_mismatch() -> None:
    s = LinearMap(Matrix([[1.0, 2.0, 3.0]]))  # 1x3
    t = LinearMap(Matrix([[1.0, 2.0]]))  # 1x2
    with pytest.raises(DimensionError):
        t.compose(s)


def test_composition_requires_map() -> None:
    with pytest.raises(TypeError):
        LinearMap(Matrix([[1.0]])).compose(Matrix([[1.0]]))  # type: ignore[arg-type]


def test_matmul_operator() -> None:
    s = LinearMap(Matrix([[1.0, 0.0], [0.0, 1.0]]))
    t = LinearMap(Matrix([[2.0, 0.0], [0.0, 2.0]]))
    assert (t @ s) == t.compose(s)


def test_equality_and_hash() -> None:
    a = LinearMap(Matrix([[1.0, 2.0]]))
    b = LinearMap(Matrix([[1.0, 2.0]]))
    assert a == b
    assert hash(a) == hash(b)
    assert a != LinearMap(Matrix([[1.0, 3.0]]))
    assert (a == 1) is False


def test_repr_mentions_domain_and_codomain() -> None:
    text = repr(LinearMap(Matrix([[1.0]])))
    assert "domain=" in text and "codomain=" in text
