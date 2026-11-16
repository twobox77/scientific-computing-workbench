# Architecture decisions

SCW is a modular monolith.  The dependency direction is strict:

```
User interfaces (Python API | CLI | Jupyter)
        v
Application layer (use cases, workflows, experiment runner)
        v
Domain layer (Vector, Covector, Matrix, LinearMap, spaces)
        v
Numerical infrastructure (NumPy, SciPy, optional backends)
```

The domain layer must not import the CLI, Jupyter, plotting, or the file
system.  Numerical backends are wrapped behind adapters so the domain model is
not polluted by third-party types.

## Decisions

| Topic | Decision |
|---|---|
| Architecture | Modular monolith |
| Interfaces | Python API, CLI, Jupyter |
| Math core | Own semantics and types; NumPy / SciPy do the number crunching |
| Layout | `src/` layout, single repository |
| Python | 3.12+ (CI tests 3.12 and 3.13) |
| Dependencies | `uv` with a committed `uv.lock` |
| Quality | Ruff, pytest, Hypothesis, pre-commit, mypy |
| Docs | MkDocs Material |

## Numerical policy

Default dtype is `float64`.  Comparisons in tests use tolerances
(`numpy.testing.assert_allclose`), never exact float equality.  Linear systems
are solved with a stable factorization (`scipy.linalg.solve`), not by forming
an explicit inverse.
