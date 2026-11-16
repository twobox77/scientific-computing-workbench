"""Shared pytest fixtures."""

from __future__ import annotations

import numpy as np
import pytest

from scw.math_core import Vector, VectorSpace


@pytest.fixture
def space3() -> VectorSpace:
    return VectorSpace(3, name="V")


@pytest.fixture
def rng() -> np.random.Generator:
    return np.random.default_rng(20260101)


@pytest.fixture
def random_vector(rng):
    def _make(n: int = 3, *, space: VectorSpace | None = None) -> Vector:
        return Vector(rng.standard_normal(n), space=space)

    return _make
