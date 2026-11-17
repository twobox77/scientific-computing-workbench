# Public API

SCW exposes a small, deliberately stable surface. Everything documented here is
importable from the top-level ``scw`` package or from ``scw.math_core`` /
``scw.numerical``.

## Stability

Every public name carries a stability level, tagged on each section below:

| Level | Meaning |
| --- | --- |
| **stable** | Frozen since 1.0. Breaking changes only in a major release. |
| **provisional** | Shipped and usable, but may change in a `0.y` release (with a CHANGELOG note). |
| **experimental** | May change in any release; use with care. |
| **deprecated** | Scheduled for removal; still works, emits a `DeprecationWarning`. |

At 1.0 **every** public namespace is **stable**; the other levels remain in the
vocabulary for future evolution. The exact list of frozen names (and their
levels) lives in
[`docs/public-api-frozen.json`](public-api-frozen.json) and is checked by CI
(`scripts/public_api.py --check`). Removing or renaming a **stable** name is a
breaking change: it follows the [deprecation policy](stability.md) and is
recorded in `CHANGELOG.md`. See [API stability and deprecation](stability.md)
for the full policy.

## Frozen public surface

The block below is generated from each namespace's ``__all__``; do not edit it
by hand — run `python scripts/public_api.py`.

<!-- public-api:start -->
| Namespace | Stability | Public names |
| --- | --- | --- |
| `scw` | stable | `Basis`, `Covector`, `LinearMap`, `Matrix`, `Tensor`, `Vector`, `VectorSpace`, `__version__`, `einsum` |
| `scw.config` | stable | `DEFAULT_ATOL`, `DEFAULT_DTYPE`, `DEFAULT_RTOL` |
| `scw.exceptions` | stable | `ConvergenceError`, `DimensionError`, `ExperimentError`, `NonFiniteError`, `NumericalError`, `SCWError`, `ShapeError`, `SymbolicError` |
| `scw.math_core` | stable | `Basis`, `Covector`, `LinearMap`, `Matrix`, `Tensor`, `Vector`, `VectorSpace`, `einsum` |
| `scw.numerical` | stable | `EighResult`, `LUResult`, `LeastSquaresResult`, `METHODS`, `ODESolution`, `QRResult`, `SVDResult`, `cholesky`, `det`, `eigh`, `inverse`, `lstsq`, `lu`, `qr`, `solve`, `solve_ivp`, `svd` |
| `scw.manifold` | stable | `CotangentSpace`, `EuclideanSpace`, `Manifold`, `Metric`, `Sphere`, `TangentSpace`, `point_coordinates` |
| `scw.physics` | stable | `CentralGravity`, `ConservativeForce`, `ConstantForce`, `Drag`, `Force`, `Particle`, `SpringForce`, `System`, `Trajectory`, `simulate` |
| `scw.experiments` | stable | `Artifact`, `Dataset`, `Experiment`, `GENERATORS`, `ResultStore`, `RunRecord`, `canonical_json`, `derive_seed`, `environment_fingerprint`, `jsonable` |
| `scw.symbolic` | stable | `SymbolicMatrix`, `SymbolicVector`, `to_symbolic` |
| `scw.visualization` | stable | `new_3d_figure`, `new_figure`, `plot_function`, `plot_matrix`, `plot_ode_solution`, `plot_surface`, `plot_vector`, `plot_vector_field`, `plot_vectors`, `plot_vectors_3d` |
<!-- public-api:end -->

## Design rules

- **Typed mathematical objects.** A `Vector` is not a raw array; a `Covector`
  is a distinct type with different operations; a `LinearMap` carries its
  domain and codomain explicitly.
- **Explicit failure.** Dimension, shape and finiteness problems raise
  `scw.exceptions.SCWError` subclasses (which also derive from `ValueError`),
  never silent garbage.
- **Defensive copies.** Constructors copy their input; mutating the array you
  passed in never changes an SCW object. Accessors return read-only views.
- **One dtype policy.** Everything is `float64` (`scw.config.DEFAULT_DTYPE`).

## `scw.math_core`

**Stability: stable.**

### `VectorSpace`

```python
VectorSpace(3)                 # R^3
VectorSpace(3, name="V")       # a named space; equality includes the name
```

A named space is *not* equal to an unnamed space of the same dimension, so
mixing them raises `DimensionError`. Use names to make units or bases explicit.

### `Vector`

```python
v = Vector([1.0, 2.0, 3.0])
v + w, v - w, 2.0 * v, v / 2.0     # arithmetic
v.dot(w)                            # inner product
v.norm()                            # Euclidean norm (scale-aware)
v.norm(p=1)                         # p-norm
v.is_zero()                         # exact-zero test
v.to_numpy()                        # copy (default) or read-only view
```

`v.data` is a read-only NumPy view. The Euclidean norm is computed with a
scale factor so it neither underflows (all-subnormal inputs) nor overflows
(large inputs).

### `Covector`

```python
alpha = Covector([2.0, 0.0, -1.0])
alpha(v)             # natural pairing alpha(v)  ==  alpha.evaluate(v)
alpha + beta         # covectors add
3.0 * alpha          # scalar scaling
```

A covector pairs with a vector of the same dimension; mismatched dimensions
raise `DimensionError`. `Covector` is intentionally **not** a `Vector`: the two
do not substitute for one another anywhere in the API.

### `Matrix`

```python
m = Matrix([[1.0, 2.0], [3.0, 4.0]])
m.shape, m.rows, m.columns
m + n, m - n, 2.0 * m
m @ n                # matrix product (validates inner dimensions)
m.apply(v)           # ==  m @ v, returns a Vector
m.transpose(), m.T
```

`Matrix @ Matrix` is matrix multiplication; `Matrix * scalar` is scaling.
Using `*` between two matrices raises `TypeError` to avoid the classic
element-wise-vs-matrix-product mistake.

### `LinearMap`

```python
t = LinearMap.from_matrix(Matrix([[1.0, 2.0], [3.0, 4.0]]))
t.domain, t.codomain          # inferred from the matrix shape
t.apply(v)                    # ==  t(v); validates the input dimension
t.compose(s)                  # t . s  (apply s first)
t @ s                         # operator form of compose
```

The representing matrix has `codomain.dimension` rows and
`domain.dimension` columns. Passing explicit `domain=` / `codomain=` spaces
whose dimensions disagree with the matrix raises `DimensionError`.

### `Tensor`

An order-`r` array of components. A scalar has order 0, a vector order 1, a
matrix order 2.

```python
t = Tensor([[1.0, 2.0], [3.0, 4.0]])
t.order, t.shape, t.size       # 2, (2, 2), 4
t + u, t - u, -t, 2.0 * t      # same-shape arithmetic
t.outer(u)                     # tensor product; order adds
t.contract(u)                  # contract t's last axis with u's first
t.contract(u, axis=0, other_axis=1)   # explicit axes
t.trace()                      # contract axis 0 with axis 1
t.trace(axis1=1, axis2=3)      # explicit axes for higher order
Tensor.zeros((2, 3))           # zero tensor of a shape
Tensor.eye(3)                  # order-2 identity
```

`outer` stacks indices (`a.outer(b)` has order `a.order + b.order`). `contract`
requires the two contracted axes to have equal size and keeps the remaining
indices in order (self first, then other); `Matrix @ Matrix` is the order-2
case. `trace` requires two distinct, equally sized axes and a tensor of order
at least 2. `*` between a tensor and another tensor/array raises `TypeError` —
use `outer`.

For readability, `einsum("ij,jk->ik", a, b)` performs the same contraction as
`a.contract(b)` using Einstein-summation subscripts. It validates the
subscript string and operand orders, then delegates to `numpy.einsum`; a
repeated index not appearing in the output is summed, an index appearing only
in the output is broadcast.

### `Basis`

An ordered basis of a vector space, for converting between vectors and
coordinates.

```python
b = Basis([Vector([1.0, 0.0]), Vector([1.0, 1.0])])
b.dimension, len(b)            # 2
b.vectors                      # the basis vectors, in order
b.to_matrix()                  # columns are the basis vectors
b.to_coordinates(v)            # coefficients of v in this basis
b.from_coordinates([1.0, 2.0]) # rebuild the vector
```

Construction validates that the vectors share one space, that there are exactly
`space.dimension` of them, and that they are linearly independent; violations
raise `DimensionError`.

## `scw.numerical`

**Stability: stable.**

SciPy-backed linear algebra and ODE integration on `Matrix` / `Vector` inputs.

### Linear systems

```python
from scw.numerical import solve, inverse, det, lstsq

solve(a, b)      # a x = b (square a)
inverse(a)       # a^-1
det(a)           # determinant
lstsq(a, b)      # least-squares solution for any shape
```

`solve`, `inverse` and `det` require square (and, where relevant, consistently
shaped) inputs. `lstsq` works for over- and under-determined systems and returns
a `LeastSquaresResult`:

```python
r = lstsq(a, b)
r.solution         # minimum-norm solution, a Vector
r.rank             # numerical rank of a
r.residual_norm    # ||a x - b||  (0.0 for a consistent/underdetermined system)
r.singular_values  # singular values of a, a Vector
```

### Decompositions

```python
from scw.numerical import lu, qr, svd, cholesky, eigh

lu(a)                 # A = P L U;  factors .p, .lower, .upper
qr(a)                 # A = Q R;    factors .q, .r  (mode="full"|"economic")
svd(a)                # A = U diag(s) Vh;  .u, .s, .vh, plus .rank()
cholesky(a)           # A = L L^T  (symmetric positive-definite), returns L
eigh(a)               # A = V diag(w) V^T;  .eigenvalues, .eigenvectors
```

Each factorization result exposes `reconstruct()`, so a factor can be checked by
rebuilding the original matrix:

```python
import numpy as np
np.allclose(lu(a).reconstruct().data, a.data)   # True
svd(a).rank()                                    # scale-aware numerical rank
```

`cholesky` and `eigh` require a symmetric input and raise `NumericalError`
otherwise (or when the matrix is not positive-definite); `lu` requires a square
matrix. `eigh` returns real eigenvalues in ascending order and orthonormal
eigenvectors.

### ODE integration

```python
from scw.math_core import Vector
from scw.numerical import solve_ivp, METHODS

def rhs(t, y):          # y' = -y
    return -1.0 * y

sol = solve_ivp(rhs, (0.0, 5.0), Vector([1.0]), t_eval=[0.0, 5.0])
sol.t               # time grid
sol.y               # states, shape (n_points, dimension)
sol.final_state     # Vector at the last time
sol.state_at(i)     # Vector at grid point i
sol.success, sol.message, sol.method
```

The right-hand side takes `(t, Vector)` and returns a `Vector` (or any
array-like of the same dimension). `method` must be one of `METHODS` (`RK45`,
`RK23`, `DOP853`, `Radau`, `BDF`, `LSODA`); `rtol`, `atol`, `max_step`,
`first_step` and `t_eval` mirror SciPy. Passing `dense_output=True` enables
`sol.interpolate(t)` for the state at an arbitrary time. A failed integration
raises `ConvergenceError` unless `raise_on_failure=False`.

## Exceptions

**Stability: stable.**

```python
from scw.exceptions import (
    SCWError,
    ConvergenceError,
    DimensionError,
    NonFiniteError,
    NumericalError,
    ShapeError,
    SymbolicError,
)
```

Every SCW error is a subclass of `SCWError`. The value-like ones
(`DimensionError`, `ShapeError`, `NonFiniteError`, `NumericalError`,
`SymbolicError`) also subclass `ValueError`, so `except ValueError` catches
them too. `ConvergenceError` (a failed ODE integration or iterative method)
also subclasses `RuntimeError`.

## `scw.visualization`

**Stability: stable.**

Optional Matplotlib adapter, installed with the `visualization` extra. The core
never imports Matplotlib; these helpers read domain objects and return the
Matplotlib `Axes` they drew on (or a `(Figure, Axes)` pair from `new_figure`).
Select a non-interactive backend (`matplotlib.use("Agg")`) before importing in
headless environments.

```python
import matplotlib
matplotlib.use("Agg")

import numpy as np
from scw.math_core import Matrix, Vector
from scw.numerical import solve_ivp
from scw.visualization import (
    new_figure, new_3d_figure,
    plot_vector, plot_vectors, plot_function, plot_vector_field,
    plot_matrix, plot_ode_solution, plot_vectors_3d, plot_surface,
)

fig, ax = new_figure(figsize=(4, 4))
plot_vector(Vector([2.0, 1.0]), ax=ax, label="v")

plot_function(np.sin, (0.0, 2 * np.pi), samples=256)
plot_vector_field(lambda x, y: (-y, x), (-2.0, 2.0), (-2.0, 2.0), normalize=True)
plot_matrix(Matrix([[1.0, 2.0], [3.0, 4.0]]), annotate=True)
plot_ode_solution(solve_ivp(lambda t, y: Vector(-y.data), (0.0, 5.0), Vector([1.0])))

fig, ax = new_3d_figure()
plot_vectors_3d([Vector([1.0, 0.0, 0.0]), Vector([0.0, 1.0, 1.0])], ax=ax)
plot_surface(lambda x, y: np.sin(x) * np.cos(y), (-3.0, 3.0), (-3.0, 3.0))
```

Invalid input raises `TypeError` (non-`Vector`/`Matrix`, non-callable field),
`DimensionError` (wrong vector dimension or field output shape) or
`NumericalError` (bad range or too few samples). Importing
`scw.visualization` without the extra raises an actionable `ImportError`. See
[Visualization](mathematics/visualization.md).

## `scw.manifold`

**Stability: stable.**

Curvature-aware geometry on top of the flat core (roadmap §11, 0.6).  A
`TangentSpace` *is* a `VectorSpace`, so tangent vectors are ordinary `Vector`
objects that additionally know their base point — operations reject mixing
`T_pM` and `T_qM` when `p != q`.  `Metric` wraps the symmetric positive-definite
matrix of the metric and provides `inner`, `norm` and the musical isomorphisms
`flat` / `sharp`.

```python
import numpy as np
from scw.manifold import EuclideanSpace, Sphere

plane = EuclideanSpace(3, name="E")
p = (1.0, 2.0, 3.0)
v = plane.tangent_vector([1.0, 0.0, 0.0], point=p)     # Vector in T_pM
alpha = plane.cotangent_covector([1.0, 0.0, 0.0], point=p)  # Covector in T*_pM

g = plane.metric(p)          # identity metric
g.inner(v, v)                # 1.0
g.sharp(g.flat(v)).data      # flat lowers, sharp raises: back to v

sphere = Sphere(radius=2.0)  # round S^2, chart (theta, phi)
gs = sphere.metric((np.pi / 2, 0.0))
gs.components                # diag(4, 4) at the equator
```

A `Metric` validates its components (symmetric, positive definite) and raises
`NumericalError` otherwise; a point at a sphere pole raises `DimensionError`.
See [Manifolds](mathematics/manifolds.md).

## `scw.physics`

**Stability: stable.**

Newtonian mechanics on top of the core and numerical layers (roadmap §11, 0.7).
A `Particle` is a point mass whose `position` and `velocity` are ordinary
`Vector`s; a `Force` answers `force(particle, t) -> Vector`; a `System` groups
particles with the forces acting on all of them and reports the conserved
quantities; `simulate` integrates the equations of motion with
`scw.numerical.solve_ivp` and returns a `Trajectory`.

```python
import numpy as np
from scw.math_core import Vector
from scw.physics import Particle, System, ConstantForce, simulate

ball = Particle(1.0, Vector([0.0, 0.0]), Vector([3.0, 4.0]))
system = System([ball], ConstantForce([0.0, -9.81]))   # uniform gravity
traj = simulate(system, (0.0, 1.0), t_eval=np.linspace(0.0, 1.0, 51))

traj.positions(0)        # particle 0 positions, shape (n_points, 2)
traj.velocities(0)       # particle 0 velocities
traj.states(0)           # particle 0 as a list of Particle objects
traj.total_energy()      # mechanical energy at each time (conservative forces)
traj.momentum()          # total momentum at each time
```

### Forces

```python
from scw.physics import ConstantForce, SpringForce, CentralGravity, Drag

ConstantForce([0.0, -9.81])            # uniform field,  F = const
SpringForce([0.0, 0.0], stiffness=4.0) # Hooke's law,   F = -k (x - anchor)
CentralGravity([0.0, 0.0], mu=1.0)     # inverse-square, F = -mu m (x-c)/|x-c|^3
Drag(coefficient=0.5)                  # linear drag,   F = -c v (not conservative)
```

The first three subclass `ConservativeForce`, so they also provide
`potential_energy(particle, t)` and satisfy `F = -grad U`. `Drag` is not
conservative: a `System` that includes it cannot report a potential or total
energy (that raises `NumericalError`).

### `System`

```python
system = System([a, b], [gravity, drag], name="two-body")
system.particle(0)          # or system.particle("name")
system.net_force(p, t)      # sum of every force on p
system.acceleration(p, t)   # net_force / mass
system.total_momentum()     # sum of m v
system.kinetic_energy()     # sum of (1/2) m |v|^2
system.potential_energy(t)  # requires conservative forces
system.total_energy(t)      # K + U
```

Particles must be non-empty, share one dimension and (when named) have unique
names; `forces` may be a single `Force` or an iterable of them.

### `simulate` / `Trajectory`

```python
from scw.physics import simulate
from scw.numerical import METHODS

traj = simulate(system, (0.0, 10.0), method="DOP853", t_eval=np.linspace(0, 10, 501),
                rtol=1e-11, atol=1e-13, dense_output=False)
traj.t                      # the time grid
traj.kinetic_energy()       # K(t)
traj.potential_energy()     # U(t)
traj.total_energy()         # K + U (conserved for conservative forces)
traj.momentum()             # total momentum, shape (n_points, dimension)
traj.final_system()         # the System at the last time
```

The keyword arguments mirror `scw.numerical.solve_ivp` (`method` is one of
`METHODS`). Invalid input raises `TypeError`, `DimensionError`, `ValueError`
(non-positive mass/stiffness, duplicate names) or `NonFiniteError`; a failed
integration raises `ConvergenceError`. See [Physics](mathematics/physics.md).

## `scw.symbolic`

**Stability: stable.**

Optional adapter over SymPy, installed with the `symbolic` extra. `SymbolicMatrix`
and `SymbolicVector` hold exact expressions and convert explicitly:

```python
from sympy import symbols
from scw.symbolic import SymbolicMatrix, to_symbolic

a, b = symbols("a b")
m = SymbolicMatrix([[a, 1], [2, b]])
m.free_symbols                 # {a, b}
m.subs({a: 4, b: 3}).to_numeric()   # -> scw Matrix([[4, 1], [2, 3]])
m.to_sympy().det()             # a*b - 2  (SymPy's own algebra)
to_symbolic(Matrix([[2.0, 0.0], [0.0, 5.0]]))   # lift a numeric matrix
```

`to_numeric()` / `to_numpy()` raise `SymbolicError` while any free symbol
remains. Importing `scw.symbolic` without the extra raises an actionable
`ImportError`; the numeric core never imports SymPy. See
[Symbolic algebra](mathematics/symbolic.md).

## `scw.experiments`

**Stability: stable.**

Experiment tracking, run records, datasets and reproducibility (roadmap §11,
0.8).  An `Experiment` bundles a configuration and a seed, runs a function and
captures a `RunRecord`; a `ResultStore` persists records and queries them; a
`Dataset` makes inputs reproducible too.

```python
import numpy as np
from scw.experiments import Dataset, Experiment, ResultStore

store = ResultStore("runs")
experiment = Experiment("mc", seed=42, config={"samples": 10000}, tags=("demo",), store=store)

def estimate(exp):
    x = exp.rng("sample").uniform(-1.0, 1.0, exp.config["samples"])
    return {"mean": float(x.mean())}

record = experiment.run(estimate)
record.run_id            # deterministic id (same seed/config/label -> same id)
record.results           # the returned mapping
record.environment       # python / numpy / scipy / scw versions
record.duration_seconds  # wall-clock time

store.query(experiment="mc", tag="demo")   # matching records, newest first
store.best("mean")                          # best successful run for a key
store.load(record.run_id)                   # reload a record from disk
```

`experiment.rng(label)` returns a seeded `numpy.random.Generator`; a function
that raises is captured into a failed record (`.ok` is `False`, `.error` holds
the message) when `capture=True`, otherwise the exception propagates after the
record is saved. `with_config`, `with_seed` and `sweep` return copies.

```python
dataset = Dataset.generate("points", generator="normal", shape=(1000, 2), seed=7)
dataset["x0"]                  # read-only column view
dataset.fingerprint()          # stable data hash
train, test = dataset.split([0.8, 0.2], seed=7)
Dataset.from_spec("points", dataset.spec)   # regenerate exactly
```

Invalid input raises `ExperimentError` (a `ValueError`): a bad name or seed, an
unserializable config or result, a malformed dataset, or a query for a run the
store does not hold.  See [Experiments](mathematics/experiments.md).

## Command line

```bash
scw version     # show scw / Python / NumPy / SciPy versions
scw doctor      # verify required dependencies import correctly
scw experiments summary runs/    # counts by experiment and failures
scw experiments list runs/       # recorded runs, newest first
scw experiments show <run-id> runs/
scw experiments best <key> runs/
scw --help
```
