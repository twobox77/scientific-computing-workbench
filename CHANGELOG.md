# Changelog

All notable changes to this project are documented here.  The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.8.0] - 2026-11-17

### Added

- `scw.experiments` (roadmap §11, 0.8): experiment tracking, run records,
  datasets and reproducibility, built on `scw.math_core` and
  `scw.exceptions`.  Only the result store touches the file system; the layer
  imports neither the CLI nor plotting.
  - `Experiment`: a name, seed, JSON-serializable `config` and `tags`.  `run`
    executes a function in a reproducible context and returns a `RunRecord`;
    `rng(label)` hands out a `numpy.random.Generator` seeded from
    `(seed, label)`; `with_config`, `with_seed` and `sweep` return copies.
  - `RunRecord` / `Artifact`: an immutable, self-describing record of one run
    (config, results, status, environment fingerprint, timing, artifacts) that
    round-trips through JSON.
  - `ResultStore`: a directory of JSON records plus an `index.json`, with
    atomic writes and `save`/`load`/`records`/`query`/`best`/`summary`.
  - `Dataset`: reproducible named columns with the generator `spec` that
    produced them, plus `split`, `fingerprint` and `from_spec`.
  - Reproducibility helpers: `derive_seed`, `canonical_json`, `jsonable` and
    `environment_fingerprint`; new `ExperimentError` (a `ValueError`).
- CLI: `scw experiments summary|list|show|best` to inspect a result store.
- Example `11_experiments.py` (a seeded Monte Carlo sweep, stored and queried,
  plus a reproducible dataset split).
- Unit, property (Hypothesis) and regression tests for the layer; the property
  tests check that the same seed/config reproduces results, that a dataset
  regenerates from its spec, that a store round-trips a record, and that a
  split partitions every row once.
- `docs/mathematics/experiments.md` and a `scw.experiments` section in
  `docs/api.md`; the README, offline guide and MkDocs nav list the new layer,
  example and CLI.

### Changed

- `pyproject.toml` no longer omits `src/scw/experiments/*` from coverage: the
  layer is implemented and tested, so it counts towards the coverage gate.

## [0.7.0] - 2026-11-17

### Added

- `scw.physics` (roadmap §11, 0.7): Newtonian mechanics built on the core and
  numerical layers, importing neither the CLI, plotting nor the file system.
  - `Particle`: a point mass whose `position` and `velocity` are ordinary
    `Vector`s, with `momentum` and `kinetic_energy`.
  - Force models: `ConstantForce` (uniform field), `SpringForce` (Hooke's law),
    `CentralGravity` (inverse-square) and `Drag` (linear, non-conservative).
    The first three subclass `ConservativeForce`, so they also provide
    `potential_energy` and satisfy `F = -grad U`.
  - `System`: groups particles with the forces acting on all of them and
    reports `net_force`, `acceleration`, `total_momentum`, `kinetic_energy`,
    `potential_energy` and `total_energy`.
  - `simulate` / `Trajectory`: integrate the equations of motion with
    `scw.numerical.solve_ivp`, exposing positions, velocities, states and the
    conserved quantities over time.
- Example `10_physics_simulation.py` (projectile, harmonic oscillator, orbit).
- Unit, property (Hypothesis) and regression tests for the physics layer; the
  property tests check that a conservative force is `-grad U` and that a
  conservative simulation conserves energy.
- `docs/mathematics/physics.md` and a `scw.physics` section in `docs/api.md`;
  the README, offline guide and MkDocs nav list the new layer and example.
- `scripts/make_release_notes.py`: composes each GitHub release's notes from
  a single source — the English section from `CHANGELOG.md`, the shared
  Chinese guide from `docs/offline.md` (retargeted to the version), and the
  works (examples/notebooks) added by that release, derived from git history.
  Wired into the release workflow so every future tag gets the same Chinese
  companion guide automatically.
- `docs/offline.md`: an "作品總覽" (works overview) section listing every
  example and notebook with its purpose and required extra, and how to view and
  operate SCW without network access.
- `README.md`: a "取得與更新" section stating the clone-once, then `git pull`
  rule, so repeated clones do not spawn duplicate project folders.
- Chinese `README.md`: rewrites the landing page in Chinese and consolidates
  the project plan, per-version progress and the works, each linking to its
  source (spec, acceptance report, changelog, releases, examples, notebooks,
  gallery, offline guide).  `docs/index.md` is rewritten to match.
- `scripts/sync_progress.py`: generates the README progress table from the
  specification roadmap (§11) and `CHANGELOG.md`, so a new release cannot leave
  the landing page stale.  `--check` runs in CI and a pre-commit hook keeps it
  current locally.
- `interactive` extra (`matplotlib` + `jupyterlab` + `ipykernel` + `ipympl`) and
  `notebooks/03_manifolds_interactive.ipynb`: a draggable/zoomable 3D view of
  the round sphere with sliders for the base point.
- `scripts/build_gallery.py` and the documentation **Gallery** page, showing
  every figure the plotting adapter can produce.

### Changed

- `pyproject.toml` no longer omits `src/scw/physics/*` from coverage: the layer
  is implemented and tested, so it counts towards the coverage gate.
- Backfilled releases `v0.1.0`/`v0.2.0`/`v0.3.0` (tags, notes and built
  wheel/sdist) so all six versions carry the same Chinese guide; fixed the
  `CHANGELOG.md` compare links (`[Unreleased]` and the missing `[0.6.0]`).
- `.pre-commit-config.yaml`: bump the pinned `ruff-pre-commit` from `v0.6.9` to
  `v0.17.5`, matching `uv.lock`.  The old pin flagged `UP038` in files the
  locked ruff accepts, so `pre-commit run --all-files` failed on a clean tree.

### Fixed

- Notebook sources now pass `ruff check` (import order, unused imports, no
  semicolons) so the CI lint gate is green.

## [0.6.0] - 2026-11-16

### Added

- `scw.manifold`: curvature-aware geometry on top of the flat core.
  - `TangentSpace` and `CotangentSpace` are `VectorSpace`s that carry the
    manifold and base point, so a vector in `T_pM` and one in `T_qM` (`p != q`)
    are rejected by the existing dimension/space checks.  Tangent vectors are
    ordinary `Vector`s; cotangent covectors are ordinary `Covector`s.
  - `Manifold` (ABC) with `EuclideanSpace(n)` (identity metric) and
    `Sphere(radius)` (round `S^2`, chart `(theta, phi)`, metric
    `diag(r^2, r^2 sin^2 theta)`; poles excluded).
  - `Metric`: wraps the symmetric positive-definite components, validating them
    on construction, and provides `inner`, `norm` (via the Cholesky factor) and
    the musical isomorphisms `flat` (lower an index) and `sharp` (raise one).
  - `Manifold.tangent_vector` / `cotangent_covector` build typed objects at a
    point.
- Example `09_manifolds.py`.

## [0.5.0] - 2026-11-16

### Added

- `scw.visualization`: an optional Matplotlib adapter (installed with the
  `visualization` extra) that draws SCW domain objects.  The core never imports
  Matplotlib and never returns a figure; every helper reads its input and
  returns the `Axes` it drew on.
  - 2D: `plot_vector`, `plot_vectors`, `plot_function`, `plot_vector_field`
    (with `normalize`), `plot_matrix` (heat map with optional colorbar and cell
    annotations) and `plot_ode_solution`.
  - 3D: `new_3d_figure`, `plot_vectors_3d` and `plot_surface`.
  - `new_figure` for an explicit `(Figure, Axes)` pair.
- Example `08_visualization.py` (writes PNGs into a gitignored `scw_plots/`).
- `mypy` ignores missing stubs for `mpl_toolkits` (Matplotlib ships no
  `py.typed`).

## [0.4.0] - 2026-11-16

### Added

- `scw.numerical` decompositions: `lu`, `qr`, `svd`, `cholesky` and `eigh`,
  each returning a small immutable result (`LUResult`, `QRResult`, `SVDResult`,
  `EighResult`) with `reconstruct`, plus `SVDResult.rank` (scale-aware).
- `lstsq`: minimum-norm least-squares solution of over- or under-determined
  systems, returning a `LeastSquaresResult` (solution, residuals, rank,
  singular values).
- `solve_ivp`: initial-value ODE integration wrapping
  `scipy.integrate.solve_ivp` with a `(t, Vector) -> Vector` right-hand side;
  returns an `ODESolution` with `t`, `y`, `final_state`, `state_at` and
  (with `dense_output=True`) `interpolate`.  `METHODS` lists the supported
  integrators.
- `NumericalError` (a `ValueError`) and `ConvergenceError` (a `RuntimeError`)
  domain exceptions.
- Examples `06_decompositions.py` and `07_ode_solving.py`.

### Changed

- The `float64` policy is unchanged; every new routine validates its input and
  raises an SCW exception rather than leaking a bare SciPy/NumPy error.

## [0.3.0] - 2026-11-16

### Added

- `scw.symbolic`: symbolic domain objects backed by SymPy (optional extra).
  `SymbolicMatrix` and `SymbolicVector` convert to and from the numeric
  `Matrix`/`Vector` (`to_numeric`, `from_numeric`, `to_symbolic`), support
  `subs`, and report `free_symbols`.  Importing the package without the extra
  raises an actionable `ImportError`.
- `einsum`: named Einstein-summation contraction over `Tensor`s, the readable
  form of `Tensor.contract` (validates subscripts, then delegates to NumPy).

### Changed

- `mypy` ignores missing stubs for `sympy` (it ships no `py.typed`).

### Tooling

- Complexity guard (`scripts/complexity_guard.py`, wired into CI): a static AST
  check that fails on any core `for`/`while` loop not justified with a
  `# complexity:` note, catching accidental O(n) Python rewrites of vectorized
  operations.

## [0.2.0] - 2026-11-16

### Added

- `Tensor`: order-r arrays with outer product, contraction and trace
  (roadmap §11, 0.2).
- `Basis`: coordinate conversion for a vector space, with linear-independence
  validation.
- Property tests for `LinearMap`/`Matrix` covering the algebraic laws the
  specification requires (additivity, homogeneity, composition, transpose
  involution, associativity, NumPy equivalence).
- Property tests for `Tensor` (outer/contract bilinearity and associativity,
  trace identities).
- Regression test layer (`tests/regression/`) pinning the numerical edge cases
  fixed so far (norm under/overflow, defensive copies, read-only views,
  non-finite rejection, type separation).
- Public API reference (`docs/api.md`), development guide
  (`docs/development.md`) and the formal Phase 1 acceptance report
  (`docs/phase1-acceptance.md`).
- Examples `03_tensor_operations.py` and `04_bases_and_coordinates.py`.
- Micro-benchmarks (`benchmarks/`) comparing SCW against raw NumPy.
- `scripts/verify_phase1.sh` to replay every acceptance check.

### Changed

- Property comparisons are scale-aware (`rtol=1e-9, atol=1e-6`) to keep the
  suite deterministic across machines.

## [0.1.0] - 2026-11-16

### Added

- Project skeleton: `src/` layout, packaging, Ruff, pytest, mypy, pre-commit
  and GitHub Actions CI.
- Mathematical core: `Vector`, `Covector`, `Matrix`, `LinearMap` and
  `VectorSpace`, with dimension/shape validation and read-only data access.
- Numerical services: `solve`, `inverse` and `det` backed by SciPy.
- CLI entry point with `version` and `doctor` commands.
- Unit, property-based (Hypothesis) and integration tests.
- Documentation (MkDocs Material), examples and a quickstart notebook.

[Unreleased]: https://github.com/twobox77/scientific-computing-workbench/compare/v0.8.0...HEAD
[0.8.0]: https://github.com/twobox77/scientific-computing-workbench/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/twobox77/scientific-computing-workbench/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/twobox77/scientific-computing-workbench/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/twobox77/scientific-computing-workbench/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/twobox77/scientific-computing-workbench/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/twobox77/scientific-computing-workbench/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/twobox77/scientific-computing-workbench/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/twobox77/scientific-computing-workbench/releases/tag/v0.1.0
