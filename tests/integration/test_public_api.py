"""Integration tests exercising the public API surface."""

from __future__ import annotations

import numpy as np

import scw
from scw.math_core import Covector, LinearMap, Matrix, Vector, VectorSpace


def test_public_reexports() -> None:
    assert scw.Vector is Vector
    assert scw.Covector is Covector
    assert scw.Matrix is Matrix
    assert scw.LinearMap is LinearMap
    assert scw.VectorSpace is VectorSpace


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
