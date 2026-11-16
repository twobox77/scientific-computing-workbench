"""Compare SCW operations against their raw NumPy equivalents.

Run with::

    uv run python benchmarks/compare_numpy.py

The ratio column is the SCW time divided by the NumPy time; a value close to
1.0 means SCW adds little beyond validation and copying.  This is the overhead
the workbench deliberately pays for typed, validated semantics.
"""

from __future__ import annotations

import timeit
from collections.abc import Callable

import numpy as np

from scw.math_core import Matrix, Vector

RNG = np.random.default_rng(20260101)


def _time(fn: Callable[[], object], *, number: int, repeat: int = 5) -> float:
    return min(timeit.repeat(fn, number=number, repeat=repeat)) / number * 1e6


def main() -> None:
    raw_a = RNG.standard_normal((8, 8))
    raw_b = RNG.standard_normal((8, 8))
    raw_v = RNG.standard_normal(8)
    raw_w = RNG.standard_normal(8)

    a = Matrix(raw_a)
    b = Matrix(raw_b)
    v = Vector(raw_v)
    w = Vector(raw_w)

    number = 2000
    cases = [
        ("vector add", lambda: v + w, lambda: raw_v + raw_w),
        ("vector dot", lambda: v.dot(w), lambda: float(np.dot(raw_v, raw_w))),
        ("matrix product", lambda: a @ b, lambda: raw_a @ raw_b),
        ("matrix transpose", lambda: a.transpose(), lambda: raw_a.T),
    ]

    print(f"{'operation':<20}{'scw us':>10}{'numpy us':>10}{'ratio':>8}")
    print("-" * 48)
    for name, scw_fn, np_fn in cases:
        scw_fn()
        np_fn()
        scw_us = _time(scw_fn, number=number)
        np_us = _time(np_fn, number=number)
        ratio = scw_us / np_us if np_us else float("inf")
        print(f"{name:<20}{scw_us:>10.3f}{np_us:>10.3f}{ratio:>8.2f}")


if __name__ == "__main__":
    main()
