# Development

## Set up

```bash
uv sync --all-extras      # create .venv and install everything
uv run pre-commit install # optional: run ruff on every commit
```

## Documentation site

The MkDocs site is built from `docs/` and published to GitHub Pages at
<https://twobox77.github.io/scientific-computing-workbench/>. The `Docs`
workflow (`.github/workflows/docs.yml`) builds with `--strict` and deploys on
every push to `main` that touches `docs/`, `mkdocs.yml` or `README.md`.

```bash
uv run mkdocs serve -a 127.0.0.1:8000   # live preview
uv run mkdocs build --strict            # what CI runs
```

## Layout

```text
src/scw/
  math_core/      domain types: VectorSpace, Vector, Covector, Matrix, LinearMap
  numerical/      SciPy-backed linear algebra, decompositions and ODE solving
  symbolic/       (boundary only in Phase 1)
  visualization/  (boundary only in Phase 1)
  physics/        Newtonian mechanics: particles, forces, systems, simulation
  experiments/    experiment tracking, run records, datasets, reproducibility
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
uv run python scripts/complexity_guard.py
uv run python scripts/sync_progress.py --check
uv run python scripts/public_api.py --check
uv run ruff format --check .
uv run mypy src/scw
uv run pytest --cov=scw --cov-report=term-missing
```

- Core math modules must stay at **≥ 90%** coverage.
- Float comparisons use a tolerance (`numpy.testing.assert_allclose`,
  `pytest.approx`); never exact equality on computed floats.
- Public operations validate dimensions/shapes and fail explicitly.
- The public API surface is **frozen**: adding or removing a name in a public
  namespace's ``__all__`` requires regenerating `docs/public-api-frozen.json`
  and the `docs/api.md` table with `uv run python scripts/public_api.py`, and
  following the [stability policy](stability.md).

## Adding a feature

1. Add type hints and a docstring stating inputs, outputs and error behaviour.
2. Add unit tests; add a Hypothesis property test when an algebraic law applies.
3. Add or extend an example under `examples/`.
4. Keep the dependency direction intact.
5. Update `CHANGELOG.md` and the relevant page under `docs/`.

## Versioning

Semantic Versioning. From 1.0 the major number marks backwards-incompatible
changes; a breaking change to a stable name goes through the
[stability and deprecation policy](stability.md) and is recorded in
`CHANGELOG.md`. The public surface is frozen in
`docs/public-api-frozen.json`; regenerate it with
`uv run python scripts/public_api.py` whenever a namespace's `__all__` changes.

## Release checklist

1. Move the `[Unreleased]` notes into a dated `## [x.y.z] - YYYY-MM-DD`
   section in `CHANGELOG.md` and update the compare links.
2. Bump the version in `pyproject.toml` and `src/scw/__init__.py` (they must
   match the tag; the release workflow checks this).
3. `uv run python scripts/sync_progress.py` to refresh the README table.
4. Run the quality gates above and `bash scripts/verify_install.sh symbolic visualization`.
5. Tag and push: `git tag vX.Y.Z && git push origin vX.Y.Z`. The release
   workflow builds the wheel/sdist, generates the notes with
   `scripts/make_release_notes.py`, creates the GitHub release and uploads the
   artifacts.
