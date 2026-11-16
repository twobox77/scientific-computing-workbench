# Phase 1 Acceptance Report

This report walks the Phase 1 acceptance checklist from the specification
(§9 of `spec/SCW_1.0_Technical_Specification_and_Phase1_Plan.md`) item by item
and records the concrete evidence that each item holds in the current tree.
It is the formal close-out of Phase 1.

- **Repository**: `twobox77/scientific-computing-workbench`
- **Package version**: `0.2.0`
- **Checklist source**: specification §9 (Project & build, Math core, Testing &
  quality, UX & docs)
- **Evidence command**: the whole suite is reproduced by
  `bash scripts/verify_phase1.sh` (see [Reproduce](#reproduce)).

Legend: `[x]` met with evidence below; each line names the artefact and the
command that proves it.

---

## 9.1 Project and build

- [x] **A fresh environment installs with `uv sync --all-extras`.**
  `pyproject.toml` declares core, optional (`symbolic`, `visualization`,
  `notebook`) and `dev` dependency groups; `uv sync --all-extras` resolves and
  installs them.
- [x] **`uv.lock` is committed and CI installs from it.**
  `uv.lock` is tracked; `.github/workflows/ci.yml` runs
  `uv sync --all-extras --frozen`.
- [x] **`uv build` produces a wheel and a source distribution.**
  `uv build` emits `dist/scw-0.2.0-py3-none-any.whl` and
  `dist/scw-0.2.0.tar.gz`.
- [x] **The `src/` layout imports `scw` normally.**
  `pyproject.toml` sets `[tool.hatch.build.targets.wheel] packages = ["src/scw"]`;
  `import scw` works from an installed environment.

## 9.2 Math core

- [x] **Vector, Covector, Matrix, LinearMap expose a minimal public API.**
  Implemented in `src/scw/math_core/` and re-exported from `scw.math_core` and
  `scw`. Phase 1 extension: `Tensor` (order-r arrays, outer product,
  contraction, trace) and `Basis` (coordinates), per roadmap §11 (0.2).
- [x] **Dimension and shape errors fail explicitly.**
  `src/scw/exceptions.py` defines `SCWError`, `DimensionError`, `ShapeError`,
  `NonFiniteError` (all value-like ones subclass `ValueError`). Exercised by
  `tests/unit/` (e.g. `test_vector.py::test_dimension_mismatch_rejected`).
- [x] **Input data is copied; object state cannot change via the caller's array.**
  Constructors copy (`np.array(..., copy=True)`); accessors return read-only
  views. Pinned by `tests/regression/test_numerical_edge_cases.py`.
- [x] **Vector and Covector remain distinct types with distinct semantics.**
  `Covector` is a separate class; pairing is `evaluate`/`__call__`, not `dot`.
  Pinned by `tests/regression/test_numerical_edge_cases.py::test_covector_and_vector_are_distinct_types`.
- [x] **LinearMap validates domain/codomain dimensions.**
  `LinearMap.__init__` checks the matrix shape against the spaces;
  `tests/unit/test_linear_map.py` covers inference and mismatch.

## 9.3 Testing and quality

- [x] **`uv run pytest` passes in full.**
  157 tests pass (`tests/unit`, `tests/property`, `tests/integration`,
  `tests/regression`).
- [x] **Core math modules keep ≥ 90% coverage.**
  Total 95%; every `math_core` module ≥ 90%
  (`tensor.py` 96%, `basis.py` 98%, `vector.py` 94%, `matrix.py` 91%,
  `covector.py` 90%, `linear_map.py` 97%).
- [x] **The algebraic properties from §7.2 are covered.**
  Vector (commutativity, associativity, scalar distributivity, norm
  non-negativity, `‖v‖ = 0 ⟺ v = 0`), Covector (pairing linearity and scalar
  linearity), LinearMap (`T(u+v)=T(u)+T(v)`, `T(cv)=cT(v)`, dimension
  correctness), Matrix (shape validation, product dimension rule, NumPy
  equivalence), Tensor (outer/contract bilinearity and associativity, trace).
  In `tests/property/`.
- [x] **`ruff check .` and `ruff format --check .` pass.**
  Both clean across the tree.
- [x] **CI runs automatically on pull requests.**
  `.github/workflows/ci.yml` triggers on `pull_request` and on `push` to `main`,
  testing Python 3.12 and 3.13.

## 9.4 User experience and documentation

- [x] **`scw --help`, `scw version`, `scw doctor` run.**
  `scw version` prints `scw 0.2.0`, Python, NumPy, SciPy; `scw doctor` verifies
  the dependencies import.
- [x] **The quickstart example runs in a clean environment.**
  `examples/01`–`04` all run under `uv run python examples/...`; the notebook
  `notebooks/01_scw_quickstart.ipynb` executes.
- [x] **Docs cover install, public API, testing and the development flow.**
  `docs/index.md` (install), `docs/api.md` (public API), `docs/development.md`
  (testing and dev process), `docs/tutorials/quickstart.md`,
  `docs/architecture/decisions.md`, `docs/mathematics/vector-spaces.md`.
- [x] **The README lists what is supported and what is not.**
  `README.md` has a "Status (Phase 1)" section with explicit supported /
  not-supported lists.

---

## Beyond the Phase 1 checklist

- **0.2 Tensor** (roadmap §11): `Tensor` with outer product, contraction and
  trace; `Basis` with coordinate conversion. Tests in `tests/unit/test_tensor.py`,
  `tests/unit/test_basis.py`, `tests/property/test_tensor_properties.py`.
- **Benchmarks**: `benchmarks/bench_core.py` and
  `benchmarks/compare_numpy.py` measure the SCW overhead over raw NumPy.
- **Examples**: `examples/03_tensor_operations.py`,
  `examples/04_bases_and_coordinates.py`.

## Reproduce

```bash
uv sync --all-extras
uv run ruff check .
uv run ruff format --check .
uv run mypy src/scw
uv run pytest --cov=scw --cov-report=term-missing
uv build
uv run scw version && uv run scw doctor
uv run python examples/01_vectors_and_covectors.py   # and 02, 03, 04
uv run python benchmarks/bench_core.py
uv run mkdocs build --strict
```

## Conclusion

Phase 1 acceptance conditions (§9.1–§9.4) are all met, verified by the commands
above, and the engineering baseline is now carrying its first post-Phase-1
feature (Tensor, 0.2). The remaining roadmap items (§11: symbolic, ODE,
visualization, manifold, physics, experiments) are out of scope for Phase 1 and
tracked as future versions.
