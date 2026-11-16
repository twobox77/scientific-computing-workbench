"""Micro-benchmarks for the SCW core operations.

Run with::

    uv run python benchmarks/bench_core.py
    uv run python benchmarks/bench_core.py --json results.json

The benchmarks are deliberately simple and dependency-free (only the standard
library ``timeit``), so they run anywhere the package is installed.  They
measure the overhead SCW adds on top of the underlying NumPy/SciPy calls, which
is the number that matters for the workbench: SCW defines semantics, NumPy does
the arithmetic.
"""

from __future__ import annotations

import argparse
import json
import timeit
from collections.abc import Callable

import numpy as np

from scw.math_core import LinearMap, Matrix, Tensor, Vector
from scw.numerical import det, lu, solve, solve_ivp, svd

RNG = np.random.default_rng(20260101)


def _time(fn: Callable[[], object], *, number: int, repeat: int = 5) -> float:
    """Return the best (minimum) per-call time in microseconds."""
    best = min(timeit.repeat(fn, number=number, repeat=repeat))
    return best / number * 1e6


def build_benchmarks() -> dict[str, Callable[[], object]]:
    v3 = Vector([1.0, 2.0, 3.0])
    w3 = Vector([4.0, 5.0, 6.0])
    a8 = Matrix(RNG.standard_normal((8, 8)))
    b8 = Matrix(RNG.standard_normal((8, 8)))
    t8 = Tensor(a8.data)
    rhs8 = Vector(RNG.standard_normal(8))
    map8 = LinearMap.from_matrix(a8)

    def bench_vector_add() -> object:
        return v3 + w3

    def bench_vector_norm() -> object:
        return v3.norm()

    def bench_vector_dot() -> object:
        return v3.dot(w3)

    def bench_matrix_product() -> object:
        return a8 @ b8

    def bench_matrix_transpose() -> object:
        return a8.transpose()

    def bench_linear_map_apply() -> object:
        return map8.apply(rhs8)

    def bench_tensor_contract() -> object:
        return t8.contract(t8)

    def bench_solve_8x8() -> object:
        return solve(a8, rhs8)

    def bench_det_8x8() -> object:
        return det(a8)

    def bench_lu_8x8() -> object:
        return lu(a8)

    def bench_svd_8x8() -> object:
        return svd(a8)

    def bench_ode_decay() -> object:
        return solve_ivp(lambda t, y: -1.0 * y, (0.0, 1.0), Vector([1.0]))

    return {
        "vector_add": bench_vector_add,
        "vector_norm": bench_vector_norm,
        "vector_dot": bench_vector_dot,
        "matrix_product_8x8": bench_matrix_product,
        "matrix_transpose_8x8": bench_matrix_transpose,
        "linear_map_apply_8x8": bench_linear_map_apply,
        "tensor_contract_8x8": bench_tensor_contract,
        "solve_8x8": bench_solve_8x8,
        "det_8x8": bench_det_8x8,
        "lu_8x8": bench_lu_8x8,
        "svd_8x8": bench_svd_8x8,
        "ode_decay_1d": bench_ode_decay,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="SCW core micro-benchmarks")
    parser.add_argument("--json", metavar="PATH", help="write results as JSON")
    parser.add_argument(
        "--number", type=int, default=2000, help="iterations per timing (default 2000)"
    )
    args = parser.parse_args()

    results: dict[str, float] = {}
    print(f"{'benchmark':<26}{'us/call':>10}")
    print("-" * 36)
    for name, fn in build_benchmarks().items():
        # Warm up so the first call's import/allocation cost is not measured.
        fn()
        micros = _time(fn, number=args.number)
        results[name] = round(micros, 3)
        print(f"{name:<26}{micros:>10.3f}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(results, handle, indent=2, sort_keys=True)
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
