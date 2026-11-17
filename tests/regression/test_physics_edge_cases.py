"""Regression tests for :mod:`scw.physics`.

These pin the physics edge cases that are easy to get subtly wrong: that force
constructors copy their input and expose read-only views, that the trajectory
arrays are read-only, that energy and angular momentum are conserved over a
long orbit, and that the singular centre of attraction is rejected rather than
producing inf/nan.
"""

from __future__ import annotations

import numpy as np
import pytest

from scw.exceptions import NonFiniteError
from scw.math_core import Vector
from scw.physics import (
    CentralGravity,
    ConstantForce,
    Drag,
    Particle,
    SpringForce,
    System,
    simulate,
)


def test_constant_force_copies_input() -> None:
    raw = np.array([1.0, 2.0])
    force = ConstantForce(raw)
    raw[0] = 99.0
    np.testing.assert_allclose(force.vector, [1.0, 2.0])


def test_spring_and_gravity_views_are_read_only() -> None:
    spring = SpringForce([0.0, 0.0], stiffness=1.0)
    gravity = CentralGravity([0.0, 0.0], mu=1.0)
    with pytest.raises(ValueError):
        spring.anchor[0] = 5.0
    with pytest.raises(ValueError):
        gravity.centre[0] = 5.0


def test_trajectory_arrays_are_read_only() -> None:
    system = System([Particle(1.0, Vector([0.0]), Vector([1.0]))])
    traj = simulate(system, (0.0, 1.0), t_eval=[0.0, 1.0])
    with pytest.raises(ValueError):
        traj.positions(0)[0, 0] = 5.0


def test_non_finite_inputs_are_rejected() -> None:
    with pytest.raises(NonFiniteError):
        Vector([float("nan")])
    with pytest.raises(ValueError):
        ConstantForce([float("inf")])
    with pytest.raises(ValueError):
        SpringForce([float("nan")], stiffness=1.0)


def test_energy_is_conserved_over_a_long_orbit() -> None:
    # Regression: a circular orbit integrated for many periods must not drift
    # in energy; the integrator tolerance is set tight enough for that.
    mu = 1.0
    satellite = Particle(1.0, Vector([1.0, 0.0]), Vector([0.0, 1.0]))
    system = System([satellite], CentralGravity([0.0, 0.0], mu=mu))
    t = np.linspace(0.0, 20.0 * np.pi, 2001)
    traj = simulate(
        system,
        (0.0, 20.0 * np.pi),
        method="DOP853",
        t_eval=t,
        rtol=1e-11,
        atol=1e-13,
    )
    energy = traj.total_energy()
    assert np.max(np.abs(energy - energy[0])) < 1e-7


def test_angular_momentum_is_conserved_for_a_central_force() -> None:
    # A central force exerts no torque, so r x v is constant.
    mu = 1.0
    satellite = Particle(1.0, Vector([1.0, 0.0]), Vector([0.0, 1.2]))
    system = System([satellite], CentralGravity([0.0, 0.0], mu=mu))
    t = np.linspace(0.0, 10.0, 1001)
    traj = simulate(
        system, (0.0, 10.0), method="DOP853", t_eval=t, rtol=1e-11, atol=1e-13
    )
    positions = traj.positions(0)
    velocities = traj.velocities(0)
    angular = positions[:, 0] * velocities[:, 1] - positions[:, 1] * velocities[:, 0]
    np.testing.assert_allclose(angular, angular[0], atol=1e-8)


def test_gravity_singularity_is_rejected_not_nan() -> None:
    # Regression: evaluating the force exactly at the centre must raise, not
    # return inf/nan that would poison the integrator.
    gravity = CentralGravity([0.0, 0.0], mu=1.0)
    at_centre = Particle(1.0, Vector([0.0, 0.0]), Vector([0.0, 0.0]))
    with pytest.raises(ZeroDivisionError):
        gravity.force(at_centre, 0.0)
    with pytest.raises(ZeroDivisionError):
        gravity.potential_energy(at_centre, 0.0)


def test_drag_removes_energy() -> None:
    # Regression: drag is non-conservative.  Compared with the same projectile
    # under gravity alone, the dragged one must have strictly less mechanical
    # energy at the end (gravity adds energy, drag removes more of it).
    gravity = ConstantForce([0.0, -9.81])
    ball = Particle(1.0, Vector([0.0, 10.0]), Vector([5.0, 0.0]))
    t = np.linspace(0.0, 3.0, 301)

    free = simulate(System([ball], gravity), (0.0, 3.0), t_eval=t)
    dragged = simulate(
        System([ball], [gravity, Drag(coefficient=0.5)]), (0.0, 3.0), t_eval=t
    )
    free_energy = free.kinetic_energy() + (-9.81) * free.positions(0)[:, 1]
    dragged_energy = dragged.kinetic_energy() + (-9.81) * dragged.positions(0)[:, 1]
    assert dragged_energy[-1] < free_energy[-1]
