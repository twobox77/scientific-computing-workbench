# Manifolds, tangent spaces and metrics

`scw.manifold` (roadmap §11, milestone 0.6) adds curvature-aware geometry on top
of the flat linear-algebra core.  It builds on `scw.math_core` and imports only
the mathematical core.

## Tangent and cotangent spaces

A manifold `M` is a smooth space described by one coordinate chart.  At a point
`p` the tangent space `T_pM` collects the velocity vectors of curves through
`p`, and its dual — the cotangent space `T*_pM` — holds the covectors (linear
functionals).

A `TangentSpace` *is* a `VectorSpace`, so a tangent vector is an ordinary
`Vector` and all of the linear algebra works unchanged.  What makes it
"tangent" is the extra identity it carries: the manifold and the base point.
That identity is part of the space's equality, so:

- `Vector` operations reject mixing `T_pM` and `T_qM` when `p != q`, exactly as
  they already reject vectors from differently named spaces;
- a `Covector` whose `dual_space` is the tangent space is a cotangent covector.

```python
from scw.manifold import EuclideanSpace, Sphere

plane = EuclideanSpace(2)
p = (1.0, -2.0)
v = plane.tangent_vector([1.0, 0.0], point=p)   # a Vector in T_pM
alpha = plane.cotangent_covector([1.0, 0.0], point=p)  # a Covector in T*_pM
```

## Manifolds

| Manifold | Chart | Metric |
|---|---|---|
| `EuclideanSpace(n)` | `R^n` | identity `g = I` |
| `Sphere(radius)` | `(theta, phi)`, `theta` in `(0, pi)` | `diag(r^2, r^2 sin^2 theta)` |

`Manifold` is an abstract base class; a subclass supplies `dimension` and
`metric(point)`.  Everything else — the tangent/cotangent spaces and the typed
constructors `tangent_vector` / `cotangent_covector` — is derived from those.

`Sphere` uses spherical coordinates.  The metric degenerates at the poles
(`g_phiphi = r^2 sin^2 theta -> 0` as `theta -> 0` or `pi`), which are outside
the chart; asking for the metric there raises `DimensionError`.

## The metric tensor

`Metric` wraps the symmetric positive-definite matrix `G` of the metric in the
coordinate basis.  It validates that `G` is symmetric and positive definite on
construction, then provides the operations that use it:

- `inner(u, v)` = `u^T G v` and `norm(v)` = `sqrt(g(v, v))`.  The norm is
  computed from the Cholesky factor `L` (`G = L L^T`) as `|L^T v|`, so it does
  not square the condition number of `G`.
- `flat(v)` lowers an index: it maps a tangent vector to the covector `g(v, .)`.
- `sharp(alpha)` raises an index: it maps a covector to `G^{-1} alpha`, a
  tangent vector.  `sharp` is the inverse of `flat`.

```python
sphere = Sphere(radius=2.0)
theta, phi = 1.5707963, 0.0
g = sphere.metric((theta, phi))
v = sphere.tangent_vector([1.0, 3.0], point=(theta, phi))

g.inner(v, v)              # squared length under the round metric
g.flat(v).data             # G v   (components pick up the metric)
g.sharp(g.flat(v)).data    # back to v
```

## Errors

- `TypeError` — passing a non-`Vector`/`Covector` where one is required;
- `DimensionError` — a point with the wrong number of coordinates, a tangent
  vector from a different point's tangent space, or a sphere point at a pole;
- `NonFiniteError` — non-finite point coordinates or metric components;
- `NumericalError` — metric components that are not symmetric or not positive
  definite.

See the runnable [example](https://github.com/twobox77/scientific-computing-workbench/blob/main/examples/09_manifolds.py).
