"""Manifolds: tangent/cotangent spaces and the metric tensor.

Roadmap §11, milestone 0.6.  Run with::

    uv run python examples/09_manifolds.py
"""

from __future__ import annotations

import numpy as np

from scw.manifold import EuclideanSpace, Sphere
from scw.math_core import Covector


def main() -> None:
    # --- Flat space: the metric is the identity, so nothing is surprising. ---
    plane = EuclideanSpace(2, name="R2")
    p = (1.0, -2.0)
    tp = plane.tangent_space(p)
    print("tangent space at p:", tp)

    g = plane.metric(p)
    u = plane.tangent_vector([1.0, 0.0], point=p)
    v = plane.tangent_vector([0.0, 2.0], point=p)
    print("g(u, v) =", g.inner(u, v), "| |u| =", g.norm(u))

    # flat lowers the index: tangent vector -> covector g(v, .).
    alpha = g.flat(v)
    print("flat(v) =", alpha.data, "| alpha in dual:", alpha.dual_space == tp)
    print("sharp(flat(v)) =", g.sharp(alpha).data)  # recovers v

    # Tangent vectors from different points are different types of space.
    q = (0.0, 0.0)
    w = plane.tangent_vector([1.0, 0.0], point=q)
    try:
        u + w
    except Exception as exc:  # DimensionError, an SCWError
        print("cannot add vectors based at different points:", type(exc).__name__)

    # --- The round 2-sphere: a curved metric g = diag(r^2, r^2 sin^2 theta). ---
    sphere = Sphere(radius=2.0)
    theta, phi = np.pi / 2, 0.0  # a point on the equator
    gs = sphere.metric((theta, phi))
    print("\nsphere metric at the equator:\n", gs.components)

    e_theta = sphere.tangent_vector([1.0, 0.0], point=(theta, phi))
    e_phi = sphere.tangent_vector([0.0, 1.0], point=(theta, phi))
    print("g(e_theta, e_phi) =", gs.inner(e_theta, e_phi), "(orthogonal)")
    print("|e_theta| =", gs.norm(e_theta), "| |e_phi| =", gs.norm(e_phi))

    # On a curved manifold the covector coordinates differ from the vector's:
    # flat(v) = G v, so the components pick up the metric.
    v = sphere.tangent_vector([1.0, 3.0], point=(theta, phi))
    print("v =", v.data, "-> flat(v) =", gs.flat(v).data)

    # A cotangent covector can be raised back to a tangent vector.
    alpha = Covector([2.0, 1.0], dual_space=sphere.tangent_space((theta, phi)))
    print("sharp(alpha) =", gs.sharp(alpha).data)

    # At a pole (theta = 0) the chart degenerates and is rejected.
    try:
        sphere.metric((0.0, 0.0))
    except Exception as exc:  # DimensionError
        print("pole rejected:", type(exc).__name__)


if __name__ == "__main__":
    main()
