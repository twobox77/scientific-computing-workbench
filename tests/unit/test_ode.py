"""Unit tests for :mod:`scw.numerical.ode`."""

from __future__ import annotations

import numpy as np
import pytest

from scw.exceptions import ConvergenceError, DimensionError, NumericalError
from scw.math_core import Vector
from scw.numerical import METHODS, ODESolution, solve_ivp


def decay(t: float, y: Vector) -> Vector:
    return -1.0 * y


def oscillator(t: float, y: Vector) -> Vector:
    # y = (position, velocity); y' = (velocity, -position)
    return Vector([y.data[1], -y.data[0]])


def test_exponential_decay_matches_analytic_solution() -> None:
    sol = solve_ivp(
        decay,
        (0.0, 5.0),
        Vector([1.0]),
        t_eval=[0.0, 1.0, 5.0],
        rtol=1e-10,
        atol=1e-12,
    )
    assert isinstance(sol, ODESolution)
    assert sol.success
    assert sol.dimension == 1
    np.testing.assert_allclose(sol.y.ravel(), np.exp(-sol.t), rtol=1e-6, atol=1e-9)


def test_rhs_may_return_a_plain_array() -> None:
    sol = solve_ivp(
        lambda t, y: [-1.0 * v for v in y.data],
        (0.0, 1.0),
        Vector([1.0]),
        rtol=1e-10,
        atol=1e-12,
    )
    assert sol.success
    assert sol.final_state.data[0] == pytest.approx(np.exp(-1.0), rel=1e-6)


def test_harmonic_oscillator_preserves_energy() -> None:
    y0 = Vector([1.0, 0.0])
    sol = solve_ivp(
        oscillator, (0.0, 10.0), y0, method="DOP853", rtol=1e-10, atol=1e-12
    )
    energy = sol.y[:, 0] ** 2 + sol.y[:, 1] ** 2
    np.testing.assert_allclose(energy, np.ones_like(energy), rtol=1e-6, atol=1e-9)


def test_final_state_and_state_at() -> None:
    sol = solve_ivp(decay, (0.0, 1.0), Vector([2.0]), t_eval=[0.0, 0.5, 1.0])
    assert sol.final_state.data[0] == pytest.approx(sol.y[-1, 0])
    assert sol.state_at(1).data[0] == pytest.approx(sol.y[1, 0])
    assert sol.state_at(-1).data[0] == pytest.approx(sol.y[-1, 0])
    with pytest.raises(IndexError):
        sol.state_at(99)


def test_views_are_read_only() -> None:
    sol = solve_ivp(decay, (0.0, 1.0), Vector([1.0]))
    with pytest.raises(ValueError):
        sol.t[0] = 5.0
    with pytest.raises(ValueError):
        sol.y[0, 0] = 5.0


def test_dense_output_interpolation() -> None:
    sol = solve_ivp(
        decay,
        (0.0, 2.0),
        Vector([1.0]),
        dense_output=True,
        rtol=1e-10,
        atol=1e-12,
    )
    midpoint = sol.interpolate(1.0).data[0]
    assert midpoint == pytest.approx(np.exp(-1.0), rel=1e-6)


def test_interpolation_requires_dense_output() -> None:
    sol = solve_ivp(decay, (0.0, 1.0), Vector([1.0]))
    with pytest.raises(NumericalError):
        sol.interpolate(0.5)


def test_repr_reports_metadata() -> None:
    sol = solve_ivp(decay, (0.0, 1.0), Vector([1.0]), method="RK23")
    assert "RK23" in repr(sol)
    assert "dimension=1" in repr(sol)


def test_every_method_runs() -> None:
    for method in METHODS:
        sol = solve_ivp(
            decay,
            (0.0, 1.0),
            Vector([1.0]),
            method=method,
            rtol=1e-10,
            atol=1e-12,
        )
        assert sol.success
        assert sol.final_state.data[0] == pytest.approx(np.exp(-1.0), rel=1e-4)


def test_unknown_method_rejected() -> None:
    with pytest.raises(NumericalError):
        solve_ivp(decay, (0.0, 1.0), Vector([1.0]), method="EULER")


def test_bad_t_span_rejected() -> None:
    with pytest.raises(NumericalError):
        solve_ivp(decay, (0.0, 0.0), Vector([1.0]))
    with pytest.raises(NumericalError):
        solve_ivp(decay, (0.0,), Vector([1.0]))  # type: ignore[arg-type]


def test_non_finite_t_span_rejected() -> None:
    with pytest.raises(NumericalError):
        solve_ivp(decay, (0.0, float("inf")), Vector([1.0]))


def test_rhs_wrong_dimension_is_rejected() -> None:
    def bad(t: float, y: Vector) -> Vector:
        return Vector([1.0, 2.0])

    with pytest.raises(DimensionError):
        solve_ivp(bad, (0.0, 1.0), Vector([1.0]))


def test_rhs_non_finite_is_rejected() -> None:
    def bad(t: float, y: Vector) -> list[float]:
        return [float("nan")]

    with pytest.raises(NumericalError):
        solve_ivp(bad, (0.0, 1.0), Vector([1.0]))


def test_rhs_array_of_wrong_shape_is_rejected() -> None:
    def bad(t: float, y: Vector) -> list[float]:
        return [1.0, 2.0]

    with pytest.raises(DimensionError):
        solve_ivp(bad, (0.0, 1.0), Vector([1.0]))


def test_initial_state_may_be_a_plain_sequence() -> None:
    sol = solve_ivp(decay, (0.0, 1.0), [1.0], rtol=1e-10, atol=1e-12)
    assert sol.final_state.data[0] == pytest.approx(np.exp(-1.0), rel=1e-6)


def test_step_control_options_are_forwarded() -> None:
    sol = solve_ivp(
        decay,
        (0.0, 1.0),
        Vector([1.0]),
        max_step=0.1,
        first_step=0.05,
        rtol=1e-10,
        atol=1e-12,
    )
    assert sol.success
    assert sol.final_state.data[0] == pytest.approx(np.exp(-1.0), rel=1e-6)


def test_non_callable_rhs_rejected() -> None:
    with pytest.raises(TypeError):
        solve_ivp(42, (0.0, 1.0), Vector([1.0]))  # type: ignore[arg-type]


def test_divergent_problem_reports_failure() -> None:
    # y' = y**2 blows up in finite time; the integrator cannot reach t=2.
    def blowup(t: float, y: Vector) -> Vector:
        return Vector(y.data**2)

    with pytest.raises(ConvergenceError):
        solve_ivp(blowup, (0.0, 2.0), Vector([1.0]), method="RK45")

    sol = solve_ivp(
        blowup, (0.0, 2.0), Vector([1.0]), raise_on_failure=False, method="RK45"
    )
    assert not sol.success
    assert sol.status != 0
    assert isinstance(sol.message, str)
