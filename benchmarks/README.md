# Benchmarks

Micro-benchmarks for the SCW core operations, plus a one-line comparison
against the raw NumPy call so the SCW overhead is visible.

```bash
uv run python benchmarks/bench_core.py
uv run python benchmarks/bench_core.py --json results.json
uv run python benchmarks/compare_numpy.py
```

Notes:

- Only the standard library (`timeit`) is used, so the benchmarks run anywhere
  the package is installed.
- Timings are the **best of five** runs (minimum per-call time in microseconds),
  which is the most stable summary for CPU-bound micro-benchmarks.
- These are not correctness tests; they guard against accidental
  complexity regressions (for example, turning an O(n) operation into O(n^2)).
- Absolute numbers depend on the machine; compare relative changes, not
  cross-machine values.
