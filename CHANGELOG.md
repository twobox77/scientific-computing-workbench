# Changelog

All notable changes to this project are documented here.  The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/twobox77/scientific-computing-workbench/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/twobox77/scientific-computing-workbench/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/twobox77/scientific-computing-workbench/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/twobox77/scientific-computing-workbench/releases/tag/v0.1.0
