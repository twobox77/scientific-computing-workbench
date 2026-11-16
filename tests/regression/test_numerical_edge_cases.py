"""Regression tests: specific cases that once failed or are numerically
delicate, kept to stop them from silently breaking again (specification §7.1).
"""

from __future__ import annotations

import numpy as np
import pytest

from scw.exceptions import ConvergenceError, NumericalError
from scw.math_core import Covector, LinearMap, Matrix, Vector
from scw.numerical import cholesky, lstsq, lu, solve_ivp, svd


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


def test_lu_uses_permutation_so_pivoting_survives_zero_leading_entry() -> None:
    # Regression: an LU without pivoting would divide by the zero pivot here.
    # The permutation factor must absorb the row swap and reconstruct A.
    a = Matrix([[0.0, 1.0], [1.0, 0.0]])
    result = lu(a)
    assert not np.allclose(result.p.data, np.eye(2))
    np.testing.assert_allclose(result.reconstruct().data, a.data, atol=1e-12)


def test_cholesky_rejects_symmetric_indefinite_matrix() -> None:
    # Regression: symmetry alone is not enough; an indefinite matrix has no
    # real Cholesky factor and must fail with an SCW error, not a bare one.
    with pytest.raises(NumericalError):
        cholesky(Matrix([[1.0, 0.0], [0.0, -1.0]]))


def test_svd_rank_threshold_is_scale_aware() -> None:
    # Regression: a fixed absolute threshold would call this large-but-rank-1
    # matrix full rank.  The rank test scales with the largest singular value.
    huge = Matrix([[1e6, 2e6], [2e6, 4e6]])
    assert svd(huge).rank() == 1


def test_lstsq_residual_norm_zero_for_consistent_overdetermined_system() -> None:
    # Regression: a consistent overdetermined system must solve exactly.
    a = Matrix([[1.0, 1.0], [1.0, 2.0], [1.0, 3.0]])
    b = Vector([1.0, 2.0, 3.0])
    result = lstsq(a, b)
    assert result.residual_norm == pytest.approx(0.0, abs=1e-9)


def test_ode_failure_is_a_convergence_error_not_a_value_error() -> None:
    # Regression: a failed integration is a runtime condition, so it must be
    # catchable as RuntimeError (ConvergenceError), not as a shape/dimension
    # ValueError.  ``SCWError`` is the common base either way.
    def blowup(t, y):
        return Vector(y.data**2)

    with pytest.raises(ConvergenceError):
        solve_ivp(blowup, (0.0, 2.0), Vector([1.0]))


def test_ode_solution_arrays_are_read_only_views() -> None:
    # Regression: callers must not be able to mutate the stored trajectory.
    sol = solve_ivp(lambda t, y: -1.0 * y, (0.0, 1.0), Vector([1.0]))
    with pytest.raises(ValueError):
        sol.y[0, 0] = 123.0
