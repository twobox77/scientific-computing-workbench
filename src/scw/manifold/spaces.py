"""Tangent and cotangent spaces attached to a point of a manifold.

A tangent space ``T_pM`` is a genuine :class:`~scw.math_core.spaces.VectorSpace`,
so tangent vectors are ordinary :class:`~scw.math_core.vector.Vector` objects
and every linear-algebra operation works unchanged.  What makes them *tangent*
is the extra identity they carry: the manifold and the base point.  Because that
identity is part of the space's equality, a vector in ``T_pM`` and a vector in
``T_qM`` (``p != q``) are rejected by the same dimension/space checks that
already guard vectors from different named spaces.

The cotangent space is the dual, so covectors are ordinary
:class:`~scw.math_core.covector.Covector` objects whose ``dual_space`` is the
matching tangent space.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from scw.config import DEFAULT_DTYPE
from scw.exceptions import DimensionError, NonFiniteError
from scw.math_core.spaces import VectorSpace


def point_coordinates(point: Any, dimension: int) -> tuple[float, ...]:
    """Validate ``point`` and return it as a hashable tuple of ``dimension`` floats."""
    try:
        arr = np.array(point, dtype=DEFAULT_DTYPE)
    except (TypeError, ValueError) as exc:
        raise DimensionError(f"a point must be a sequence of numbers: {exc}") from exc
    if arr.ndim != 1 or arr.size != dimension:
        raise DimensionError(
            f"a point needs {dimension} coordinates, got shape {arr.shape}"
        )
    if not np.all(np.isfinite(arr)):
        raise NonFiniteError("point coordinates contain NaN or infinite values")
    return tuple(float(x) for x in arr)


@dataclass(frozen=True, kw_only=True)
class TangentSpace(VectorSpace):
    """The tangent space ``T_pM`` at ``point`` of ``manifold``.

    ``point`` is the validated coordinate tuple, so two tangent spaces compare
    equal exactly when they sit over the same point of the same manifold.
    """

    manifold: Any
    point: tuple[float, ...]

    def __str__(self) -> str:
        return f"T_{self.point}{self.manifold}"


@dataclass(frozen=True, kw_only=True)
class CotangentSpace(VectorSpace):
    """The cotangent space ``T*_pM`` at ``point`` of ``manifold`` (the dual)."""

    manifold: Any
    point: tuple[float, ...]

    def __str__(self) -> str:
        return f"T*_{self.point}{self.manifold}"
