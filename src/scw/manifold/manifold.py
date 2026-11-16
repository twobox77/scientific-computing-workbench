"""Manifolds: smooth spaces carrying a metric, and their tangent geometry.

A manifold here is a finite-dimensional real manifold described by a single
coordinate chart.  Each concrete manifold knows how to produce the
:class:`~scw.manifold.metric.Metric` at any point of its chart, and — through
that metric — the tangent and cotangent spaces at the point.

Two concrete manifolds are provided:

* :class:`EuclideanSpace` — flat ``R^n`` with the identity metric;
* :class:`Sphere` — the round 2-sphere in spherical coordinates ``(theta, phi)``
  with the standard metric ``diag(r^2, r^2 sin^2 theta)``.

Tangent and cotangent vectors are ordinary :class:`~scw.math_core.vector.Vector`
and :class:`~scw.math_core.covector.Covector` objects living in the typed
:class:`~scw.manifold.spaces.TangentSpace` / ``CotangentSpace`` of the point, so
they interoperate with the whole linear-algebra core while still refusing to
mix vectors based at different points.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from scw.exceptions import DimensionError
from scw.manifold.metric import Metric
from scw.manifold.spaces import (
    CotangentSpace,
    TangentSpace,
    point_coordinates,
)
from scw.math_core.covector import Covector
from scw.math_core.vector import Vector


class Manifold(ABC):
    """A finite-dimensional real manifold given by one coordinate chart.

    Subclasses provide :attr:`dimension` and :meth:`metric`.  Everything else —
    the tangent/cotangent spaces and the typed constructors for tangent vectors
    and cotangent covectors — is derived from those two.
    """

    dimension: int

    @property
    def name(self) -> str | None:
        """A human-readable name, or ``None``."""
        return None

    @abstractmethod
    def metric(self, point: Any) -> Metric:
        """The metric tensor at ``point`` (validating ``point`` as a chart point)."""

    def _check_point(self, point: Any) -> tuple[float, ...]:
        return point_coordinates(point, self.dimension)

    def tangent_space(self, point: Any) -> TangentSpace:
        """The tangent space ``T_pM`` at ``point``."""
        coords = self._check_point(point)
        return TangentSpace(dimension=self.dimension, manifold=self, point=coords)

    def cotangent_space(self, point: Any) -> CotangentSpace:
        """The cotangent space ``T*_pM`` at ``point`` (the dual of ``T_pM``)."""
        coords = self._check_point(point)
        return CotangentSpace(dimension=self.dimension, manifold=self, point=coords)

    def tangent_vector(self, data: Any, *, point: Any) -> Vector:
        """Build a tangent vector at ``point`` (a :class:`Vector` in ``T_pM``)."""
        return Vector(data, space=self.tangent_space(point))

    def cotangent_covector(self, data: Any, *, point: Any) -> Covector:
        """Build a cotangent covector at ``point`` (a covector in ``T*_pM``)."""
        return Covector(data, dual_space=self.tangent_space(point))

    def __str__(self) -> str:
        return self.name if self.name is not None else f"Manifold(R^{self.dimension})"


@dataclass(frozen=True)
class EuclideanSpace(Manifold):
    """Flat Euclidean space ``R^n`` with the standard (identity) metric."""

    dimension: int
    name: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.dimension, int):
            raise TypeError("dimension must be an int")
        if self.dimension <= 0:
            raise ValueError("dimension must be positive")

    def metric(self, point: Any) -> Metric:
        self._check_point(point)
        return Metric(np.eye(self.dimension), manifold=self, point=point)

    def __str__(self) -> str:
        return self.name if self.name is not None else f"E^{self.dimension}"


@dataclass(frozen=True)
class Sphere(Manifold):
    """The round 2-sphere ``S^2`` of radius ``radius`` in spherical coordinates.

    A point is ``(theta, phi)`` with ``theta`` the polar angle in ``(0, pi)``
    and ``phi`` the azimuth.  The standard metric is
    ``diag(radius^2, radius^2 sin^2 theta)``; it degenerates at the poles
    ``theta in {0, pi}``, which are outside this chart.
    """

    radius: float = 1.0
    dimension: int = field(init=False, default=2)
    name: str | None = None

    def __post_init__(self) -> None:
        if not np.isfinite(self.radius) or self.radius <= 0.0:
            raise ValueError("radius must be a positive finite number")

    def _polar_angle(self, point: Any) -> float:
        theta, _ = self._check_point(point)
        if not 0.0 < theta < np.pi:
            raise DimensionError(
                f"polar angle must lie strictly in (0, pi), got {theta}"
            )
        return theta

    def metric(self, point: Any) -> Metric:
        theta = self._polar_angle(point)
        r2 = self.radius * self.radius
        components = np.diag([r2, r2 * float(np.sin(theta)) ** 2])
        return Metric(components, manifold=self, point=point)

    def __str__(self) -> str:
        label = self.name if self.name is not None else "S^2"
        return f"{label} (r={self.radius:g})"
