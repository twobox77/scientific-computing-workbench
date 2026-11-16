#!/usr/bin/env bash
# Reproduce every Phase 1 acceptance check (docs/phase1-acceptance.md).
#
# Usage:  bash scripts/verify_phase1.sh
#
# Exits non-zero on the first failure.  Requires `uv` on PATH.
set -euo pipefail

echo "== install =="
uv sync --all-extras --frozen

echo "== lint =="
uv run ruff check .

echo "== format =="
uv run ruff format --check .

echo "== types =="
uv run mypy src/scw

echo "== tests + coverage =="
uv run pytest --cov=scw --cov-report=term-missing

echo "== build =="
uv build

echo "== cli =="
uv run scw version
uv run scw doctor

echo "== examples =="
for example in examples/0*.py; do
  echo "  - ${example}"
  uv run python "${example}" > /dev/null
done

echo "== benchmarks (smoke) =="
uv run python benchmarks/bench_core.py --number 200 > /dev/null

echo "== docs =="
uv run mkdocs build --strict > /dev/null

echo
echo "Phase 1 acceptance: ALL CHECKS PASSED"
