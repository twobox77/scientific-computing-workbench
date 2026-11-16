# Contributing

## Setup

```bash
uv sync --all-extras
uv run pre-commit install
```

## Quality gates

Every change must pass:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src/scw
uv run pytest
```

## Conventions

- Keep the dependency direction: the domain layer never imports the CLI,
  Jupyter, plotting or file-system code.
- Every public operation validates its dimensions/shapes and fails loudly.
- Prefer tolerances (`numpy.testing.assert_allclose`) over exact float
  equality in tests.
- Add tests with behaviour: unit tests for methods, Hypothesis tests for
  algebraic laws, and an example when a feature is user-facing.
