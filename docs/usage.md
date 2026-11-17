# Usage

SCW is a layered workbench: a typed mathematical core, numerical algorithms on
top of it, and optional domain layers (manifolds, physics, experiments) plus
optional adapters (symbolic, visualization). This page is a tour of the public
surface with runnable snippets; each section links to the deeper page.

Everything below is importable from the top-level `scw` package or from the
namespace shown. See [Public API](api.md) for the frozen surface and
[API stability](stability.md) for the stability promise.

## The mathematical core — `scw.math_core`

Typed objects with their own semantics; NumPy does the number crunching.

```python
from scw.math_core import Basis, Covector, LinearMap, Matrix, Tensor, Vector

v = Vector([1.0, 2.0, 3.0])
w = Vector([4.0, 5.0, 6.0])
v.norm()             # Euclidean norm
v.dot(w)             # inner product

alpha = Covector([2.0, 0.0, -1.0])   # a covector, distinct from a vector
alpha.evaluate(v)    # natural pairing alpha(v)

t = LinearMap.from_matrix(Matrix([[1.0, 2.0], [3.0, 4.0]]))
t.apply(Vector([1.0, 1.0]))          # domain/codomain are checked

a = Tensor([[1.0, 2.0], [3.0, 4.0]])
a.outer(a)           # tensor product
a.contract(a)        # contraction (here a matrix product)
a.trace().data

basis = Basis([Vector([1.0, 0.0]), Vector([1.0, 1.0])])
basis.to_coordinates(Vector([3.0, 2.0]))   # coordinates in that basis
```

Details: [Vector spaces](mathematics/vector-spaces.md).

## Numerical algorithms — `scw.numerical`

Linear systems, factorizations (each with `reconstruct()`), and an ODE solver.
All inputs are `math_core` objects; SciPy stays behind the adapter.

```python
from scw.math_core import Matrix, Vector
from scw.numerical import lu, solve, solve_ivp

a = Matrix([[4.0, 7.0], [2.0, 6.0]])
x = solve(a, Vector([1.0, 0.0]))       # solve a x = b
lu(a).reconstruct().data               # factorizations rebuild the matrix

# Integrate y' = -y from y(0)=1 and sample a few times.
sol = solve_ivp(lambda t, y: -1.0 * y, (0.0, 2.0), Vector([1.0]), t_eval=[0.0, 2.0])
sol.final_state.data                   # ~ exp(-2)
```

Details: [Numerical methods](mathematics/numerical-methods.md).

## Symbolic algebra — `scw.symbolic` (extra)

An optional SymPy adapter; the numeric and symbolic types convert both ways.
Install with `uv sync --extra symbolic`.

```python
from scw.math_core import Matrix
from scw.symbolic import SymbolicMatrix, to_symbolic

sym = SymbolicMatrix([["a", 1], [2, "b"]])
to_symbolic(Matrix([[1.0, 2.0]])).to_numeric()   # collapse back when free of symbols
```

Details: [Symbolic algebra](mathematics/symbolic.md).

## Visualization — `scw.visualization` (extra)

Matplotlib lives behind this adapter; the core never imports it and never
returns a figure. Install with `uv sync --extra visualization`.

```python
import matplotlib
matplotlib.use("Agg")            # headless; drop this to show interactively

import numpy as np
from scw.math_core import Vector
from scw.visualization import new_figure, plot_function, plot_vector

fig, ax = new_figure()
plot_vector(Vector([2.0, 1.0]), ax=ax, label="v")
plot_function(np.sin, (0.0, 2 * np.pi), samples=256)
fig.savefig("plot.png", dpi=120)
```

Details: [Visualization](mathematics/visualization.md) and the
[Gallery](gallery.md).

## Manifolds — `scw.manifold`

Tangent and cotangent spaces attached to a point, the metric tensor, and the
musical isomorphisms `flat` / `sharp`.

```python
from scw.manifold import EuclideanSpace, Metric, Sphere
from scw.math_core import Vector

space = EuclideanSpace(2)
g = Metric([[1.0, 0.0], [0.0, 1.0]], point=(0.0, 0.0), manifold=space)
v = Vector([3.0, 4.0])
g.norm(v)          # 5.0
g.flat(v)          # lower the index -> a covector
g.sharp(g.flat(v)) # raise it back

sphere = Sphere(radius=1.0)
sphere.dimension
```

Details: [Manifolds](mathematics/manifolds.md).

## Physics — `scw.physics`

Point masses, force models (conservative forces carry a potential energy), a
system that reports momentum and energy, and a simulation driver that delegates
integration to `scw.numerical`.

```python
from scw.math_core import Vector
from scw.physics import ConstantForce, Particle, System, simulate

p = Particle(mass=1.0, position=Vector([0.0, 0.0]), velocity=Vector([0.0, 0.0]))
system = System([p], forces=[ConstantForce(Vector([1.0, 0.0]))])
traj = simulate(system, (0.0, 1.0), t_eval=[0.0, 0.5, 1.0])
traj.positions          # (n_points, dimension)
```

Details: [Physics](mathematics/physics.md).

## Experiments — `scw.experiments`

Track runs reproducibly: an `Experiment` bundles a config and a seed, records a
`RunRecord`, and a `ResultStore` persists and queries those records.

```python
from scw.experiments import Experiment, ResultStore

experiment = Experiment(name="trial", seed=7, config={"lr": 0.1})
record = experiment.run(lambda exp: {"score": exp.seed})
record.run_id                 # deterministic: same config+seed -> same id
record.results                # {"score": 7}

store = ResultStore("runs/")
store.save(record)
store.summary()["total"]
```

Details: [Experiments](mathematics/experiments.md).

## Command line

```bash
scw version                                  # SCW / Python / NumPy / SciPy versions
scw doctor                                   # confirm required dependencies
scw experiments summary runs/                # summarise a result store
scw experiments list runs/ --experiment trial
```

## Examples and notebooks

Every feature ships with a runnable example under `examples/`:

```bash
uv run python examples/01_vectors.py
uv run python examples/06_decompositions.py
uv run python examples/11_experiments.py
```

The Jupyter tutorials live in `notebooks/` (`uv run jupyter lab`); the guided
walkthroughs are under [Tutorials](tutorials/quickstart.md) and the math pages.
