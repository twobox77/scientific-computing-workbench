# SCW — Scientific Computing Workbench

A personal scientific-computing workbench in Python: typed mathematical
objects over NumPy / SciPy, packaged with reproducible, testable tooling.

- **Architecture**: modular monolith (`src/` layout, single repository).
- **Interfaces**: Python API, CLI, Jupyter.
- **Math core**: SCW defines the semantics and types (Vector, Covector, Matrix,
  LinearMap); NumPy / SciPy do the low-level number crunching.
- **Python**: 3.12+ (CI tests 3.12 and 3.13).
- **License**: MIT.

The specification and Phase 1 plan live in
[`docs/spec/`](docs/spec/) (see `SCW_1.0_...md`).

## Status (Phase 1)

This is the **walking skeleton**: a working engineering baseline plus the first
mathematical objects, not a complete scientific library.

Supported today:

- `scw.math_core`: `VectorSpace`, `Vector`, `Covector`, `Matrix`, `LinearMap`,
  with dimension/shape validation and read-only data access.
- `scw.numerical`: `solve`, `inverse`, `det` (SciPy-backed).
- CLI: `scw version`, `scw doctor`.
- Unit, property-based (Hypothesis), integration and regression tests.

Not supported yet: tensors, symbolic calculus, ODE/PDE solvers, manifolds,
physics simulation, plotting. See the roadmap in the specification.

Documentation: [Public API](docs/api.md), [Development](docs/development.md),
[Quickstart](docs/tutorials/quickstart.md).

## Install

```bash
uv sync --all-extras
```

## Use

```python
from scw.math_core import Covector, LinearMap, Matrix, Vector

v = Vector([1.0, 2.0, 3.0])
w = Vector([4.0, 5.0, 6.0])
v.norm()          # Euclidean norm
v.dot(w)          # inner product

alpha = Covector([2.0, 0.0, -1.0])
alpha.evaluate(v)  # natural pairing alpha(v)

t = LinearMap.from_matrix(Matrix([[1.0, 2.0], [3.0, 4.0]]))
t.apply(Vector([1.0, 1.0]))
```

```bash
uv run scw version
uv run scw doctor
```

## Develop

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src/scw
uv run pre-commit install
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for conventions and quality gates, and
[`docs/`](docs/) for architecture and mathematics notes.
