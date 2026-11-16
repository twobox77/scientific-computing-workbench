"""Manifolds and their tangent geometry (roadmap §11, 0.6).

This layer builds on :mod:`scw.math_core`: it adds curvature-aware structure —
tangent/cotangent spaces attached to a point, and the metric tensor — without
changing the flat linear-algebra core.  It imports only the mathematical core
and must not import the CLI, plotting or file-system code.
"""

from __future__ import annotations

from scw.manifold.manifold import EuclideanSpace, Manifold, Sphere
from scw.manifold.metric import Metric
from scw.manifold.spaces import CotangentSpace, TangentSpace, point_coordinates

__all__ = [
    "CotangentSpace",
    "EuclideanSpace",
    "Manifold",
    "Metric",
    "Sphere",
    "TangentSpace",
    "point_coordinates",
]
