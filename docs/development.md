# Development

## Set up

```bash
uv sync --all-extras      # create .venv and install everything
uv run pre-commit install # optional: run ruff on every commit
```

## Layout

```text
src/scw/
  math_core/      domain types: VectorSpace, Vector, Covector, Matrix, LinearMap
  numerical/      SciPy-backed linear algebra, decompositions and ODE solving
  symbolic/       (boundary only in Phase 1)
  visualization/  (boundary only in Phase 1)
  physics/        (boundary only in Phase 1)
  experiments/    (boundary only in Phase 1)
  cli/            Typer entry point
tests/
  unit/           single-type behaviour
  property/       algebraic laws (Hypothesis)
  integration/    public API working together
  regression/     previously-fixed cases, pinned
```

## Dependency direction (hard rule)

```text
user interfaces (API | CLI | Jupyter)
        v
application layer
        v
domain layer (math_core)
        v
numerical infrastructure (NumPy / SciPy)
```

`math_core` must not import the CLI, Jupyter, Matplotlib or the filesystem.
Numerical backends are reached through `scw.numerical`, never from the domain
types directly.

## Quality gates

Run all of these before pushing; CI runs the same set on Python 3.12 and 3.13:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src/scw
uv run pytest --cov=scw --cov-report=term-missing
```

- Core math modules must stay at **≥ 90%** coverage.
- Float comparisons use a tolerance (`numpy.testing.assert_allclose`,
  `pytest.approx`); never exact equality on computed floats.
- Public operations validate dimensions/shapes and fail explicitly.

## Adding a feature

1. Add type hints and a docstring stating inputs, outputs and error behaviour.
2. Add unit tests; add a Hypothesis property test when an algebraic law applies.
3. Add or extend an example under `examples/`.
4. Keep the dependency direction intact.
5. Update `CHANGELOG.md` and the relevant page under `docs/`.

## Versioning

Semantic Versioning. Before 1.0 the minor number (`0.y.0`) marks
backwards-incompatible changes; they are recorded in `CHANGELOG.md`.
