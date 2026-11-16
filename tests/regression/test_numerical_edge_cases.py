"""Regression tests: specific cases that once failed or are numerically
delicate, kept to stop them from silently breaking again (specification §7.1).
"""

from __future__ import annotations

import numpy as np
import pytest

from scw.math_core import Covector, LinearMap, Matrix, Vector


def test_norm_underflow_does_not_report_zero_for_nonzero_vector() -> None:
    # Regression: naive ``sqrt(sum(v**2))`` underflows to 0.0 when every
    # component is subnormal, violating the ``|v| == 0  iff  v == 0`` law.
    v = Vector([0.0, 0.0, 0.0, 2.2250738585072014e-308])
    assert not v.is_zero()
    assert v.norm() > 0.0


def test_norm_overflow_stays_finite() -> None:
    # Regression: the naive sum of squares overflows for large components.
    v = Vector([1e200, 1e200, 1e200])
    assert np.isfinite(v.norm())
    assert v.norm() == pytest.approx(1e200 * np.sqrt(3.0))


def test_norm_scaling_is_exact_for_simple_pythagorean_triple() -> None:
    # 3-4-5 is exactly representable, so the scale-aware norm must reproduce
    # the analytic result with no rounding error.
    v = Vector([3.0, 4.0])
    assert v.norm() == 5.0


def test_to_numpy_copy_false_shares_memory_with_data() -> None:
    # Regression: ``.data`` returns a fresh view each call, so identity
    # comparison (``is``) is wrong; the contract is shared memory.
    v = Vector([1.0, 2.0])
    assert np.shares_memory(v.to_numpy(copy=False), v.data)


def test_construction_copies_external_array() -> None:
    # Regression: later mutation of the caller's array must not leak in.
    source = np.array([1.0, 2.0, 3.0])
    v = Vector(source)
    source[0] = 99.0
    assert v.data[0] == 1.0


def test_read_only_view_rejects_mutation() -> None:
    v = Vector([1.0, 2.0])
    with pytest.raises(ValueError):
        v.data[0] = 5.0


def test_zero_length_vectors_and_matrices_are_rejected() -> None:
    with pytest.raises(ValueError):
        Vector([])
    with pytest.raises(ValueError):
        Matrix([])


def test_non_finite_input_is_rejected_at_the_boundary() -> None:
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError):
            Vector([1.0, bad])
        with pytest.raises(ValueError):
            Covector([1.0, bad])
        with pytest.raises(ValueError):
            Matrix([[1.0, bad]])


def test_covector_and_vector_are_distinct_types() -> None:
    # Regression: a covector must never be usable where a vector is expected.
    alpha = Covector([1.0, 2.0])
    with pytest.raises(TypeError):
        Vector([1.0, 2.0]).dot(alpha)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        LinearMap(Matrix([[1.0, 0.0], [0.0, 1.0]])).apply(alpha)  # type: ignore[arg-type]
