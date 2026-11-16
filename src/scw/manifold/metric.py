"""Riemannian metric tensor at a point of a manifold.

A metric is the smooth assignment of a symmetric positive-definite bilinear
form ``g_p`` to each point ``p``.  At a fixed point it is just an ``n x n`` SPD
matrix ``G`` in the coordinate basis of ``T_pM``; this class wraps such a matrix
and provides the operations that *use* it:

* ``inner(u, v)`` and ``norm(v)`` — the inner product and length it induces on
  tangent vectors;
* ``flat(v)`` and ``sharp(alpha)`` — the musical isomorphisms between tangent
  vectors and cotangent covectors, which is exactly the role of the metric in
  the tangent/cotangent duality.

The class validates that ``G`` is symmetric and positive definite on
construction, so downstream code can trust it.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from scw.config import DEFAULT_ATOL, DEFAULT_RTOL
from scw.exceptions import DimensionError, NonFiniteError, NumericalError
from scw.manifold.spaces import CotangentSpace, TangentSpace, point_coordinates
from scw.math_core.covector import Covector
from scw.math_core.vector import Vector


class Metric:
    """The metric tensor ``g`` at one point, given by SPD components ``G``.

    ``manifold`` and ``point`` identify where the metric lives; ``components``
    is the symmetric positive-definite matrix of ``g`` in the coordinate basis.
    """

    __slots__ = ("_components", "_manifold", "_point", "_dimension")

    def __init__(
        self,
        components: Any,
        *,
        point: Any,
        manifold: Any = None,
    ) -> None:
        arr = np.array(components, dtype=float, copy=True)
        if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
            raise DimensionError(
                f"metric components must be a square matrix, got shape {arr.shape}"
            )
        if arr.shape[0] == 0:
            raise DimensionError("metric components must be non-empty")
        if not np.all(np.isfinite(arr)):
            raise NonFiniteError("metric components contain NaN or infinite values")
        if not np.allclose(arr, arr.T, rtol=DEFAULT_RTOL, atol=DEFAULT_ATOL):
            raise NumericalError("metric components must be symmetric")
        try:
            np.linalg.cholesky(arr)
        except np.linalg.LinAlgError as exc:
            raise NumericalError("metric components must be positive definite") from exc
        self._components = arr
        self._dimension = int(arr.shape[0])
        self._manifold = manifold
        self._point = point_coordinates(point, self._dimension)

    @property
    def components(self) -> np.ndarray:
        """Read-only view of the SPD matrix ``G``."""
        view = self._components.view()
        view.flags.writeable = False
        return view

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def manifold(self) -> Any:
        return self._manifold

    @property
    def point(self) -> tuple[float, ...]:
        return self._point

    @property
    def tangent_space(self) -> TangentSpace:
        return TangentSpace(
            dimension=self._dimension, manifold=self._manifold, point=self._point
        )

    @property
    def cotangent_space(self) -> CotangentSpace:
        return CotangentSpace(
            dimension=self._dimension, manifold=self._manifold, point=self._point
        )

    def _check_tangent(self, vector: Any, name: str) -> Vector:
        if not isinstance(vector, Vector):
            raise TypeError(f"{name} must be a Vector")
        if vector.dimension != self._dimension:
            raise DimensionError(
                f"{name} has dimension {vector.dimension}, expected {self._dimension}"
            )
        space = vector.space
        if isinstance(space, TangentSpace) and space != self.tangent_space:
            raise DimensionError(
                f"{name} belongs to {space}, not to {self.tangent_space}"
            )
        return vector

    def inner(self, u: Vector, v: Vector) -> float:
        """Metric inner product ``g(u, v) = u^T G v`` of two tangent vectors."""
        u = self._check_tangent(u, "u")
        v = self._check_tangent(v, "v")
        return float(u.data @ self._components @ v.data)

    def norm(self, v: Vector) -> float:
        """Length ``sqrt(g(v, v))`` of a tangent vector.

        Computed from the Cholesky factor ``L`` (``G = L L^T``) as ``|L^T v|``,
        which avoids squaring the condition number of ``G``.
        """
        v = self._check_tangent(v, "v")
        factor = np.linalg.cholesky(self._components)
        return float(np.linalg.norm(factor.T @ v.data))

    def flat(self, v: Vector) -> Covector:
        """Lower an index: map a tangent vector to the covector ``g(v, .)``."""
        v = self._check_tangent(v, "v")
        return Covector(self._components @ v.data, dual_space=self.tangent_space)

    def sharp(self, alpha: Covector) -> Vector:
        """Raise an index: map a covector to ``G^{-1} alpha``, a tangent vector."""
        if not isinstance(alpha, Covector):
            raise TypeError("sharp expects a Covector")
        if alpha.dimension != self._dimension:
            raise DimensionError(
                f"alpha has dimension {alpha.dimension}, expected {self._dimension}"
            )
        return Vector(
            np.linalg.solve(self._components, alpha.data), space=self.tangent_space
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Metric):
            return NotImplemented
        return (
            self._manifold == other._manifold
            and self._point == other._point
            and bool(np.array_equal(self._components, other._components))
        )

    def __repr__(self) -> str:
        return (
            f"Metric(components=array({self._components.tolist()}), "
            f"manifold={self._manifold!r}, point={self._point})"
        )
