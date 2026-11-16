# Changelog

All notable changes to this project are documented here.  The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Property tests for `LinearMap`/`Matrix` covering the algebraic laws the
  specification requires (additivity, homogeneity, composition, transpose
  involution, associativity, NumPy equivalence).
- Regression test layer (`tests/regression/`) pinning the numerical edge cases
  fixed so far (norm under/overflow, defensive copies, read-only views,
  non-finite rejection, type separation).
- Public API reference (`docs/api.md`) and development guide
  (`docs/development.md`).

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

[Unreleased]: https://github.com/twobox77/scientific-computing-workbench/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/twobox77/scientific-computing-workbench/releases/tag/v0.1.0
