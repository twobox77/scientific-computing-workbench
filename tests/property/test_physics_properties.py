"""Property-based tests for :mod:`scw.physics`.

The laws checked here are the ones mechanics must satisfy: that a conservative
force is the negative gradient of its potential (checked numerically), that a
spring's force is exactly Hooke's law, that a constant field's potential is
linear in position, and that simulating a conservative system conserves energy.
Comparisons between differently-rounded computations use a scale-aware
tolerance (``rtol=1e-9, atol=1e-6``); see
``tests/property/test_vector_properties.py``.
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from scw.math_core import Vector
from scw.physics import (
    CentralGravity,
    ConstantForce,
    Particle,
    SpringForce,
    System,
    simulate,
)

_ATOL = 1e-6
_RTOL = 1e-9

_coord = st.floats(-1e2, 1e2, allow_nan=False, allow_infinity=False)
_offset = st.floats(-5.0, 5.0, allow_nan=False, allow_infinity=False)
_positive = st.floats(0.1, 1e2, allow_nan=False, allow_infinity=False)


def _gradient(force, particle, *, step: float = 1e-5) -> np.ndarray:
    """Central-difference gradient of ``U`` at the particle's position."""
    x = particle.position.data
    grad = np.empty_like(x)
    # complexity: fixed-dimension finite differences, O(dimension) not O(data)
    for i in range(x.size):
        e = np.zeros_like(x)
        e[i] = step
        plus = particle.with_state(Vector(x + e), particle.velocity)
        minus = particle.with_state(Vector(x - e), particle.velocity)
        grad[i] = (
            force.potential_energy(plus, 0.0) - force.potential_energy(minus, 0.0)
        ) / (2.0 * step)
    return grad


@settings(max_examples=100, deadline=None)
@given(
    anchor=st.lists(_coord, min_size=2, max_size=2),
    stiffness=_positive,
    x=st.lists(_coord, min_size=2, max_size=2),
    v=st.lists(_coord, min_size=2, max_size=2),
)
def test_spring_force_is_hookes_law(anchor, stiffness, x, v) -> None:
    force = SpringForce(anchor, stiffness=stiffness)
    particle = Particle(1.0, Vector(x), Vector(v))
    expected = -stiffness * (np.asarray(x) - np.asarray(anchor))
    np.testing.assert_allclose(
        force.force(particle, 0.0).data, expected, rtol=_RTOL, atol=_ATOL
    )


@settings(max_examples=100, deadline=None)
@given(
    field=st.lists(_coord, min_size=2, max_size=2),
    x=st.lists(_coord, min_size=2, max_size=2),
)
def test_constant_force_potential_is_linear(field, x) -> None:
    force = ConstantForce(field)
    particle = Particle(1.0, Vector(x), Vector([0.0, 0.0]))
    assert force.potential_energy(particle, 0.0) == pytest.approx(
        -float(np.dot(field, x)), rel=_RTOL, abs=_ATOL
    )


@settings(max_examples=50, deadline=None)
@given(
    anchor=st.lists(_offset, min_size=2, max_size=2),
    stiffness=_positive,
    x=st.lists(_offset, min_size=2, max_size=2),
)
def test_spring_force_is_minus_gradient_of_potential(anchor, stiffness, x) -> None:
    force = SpringForce(anchor, stiffness=stiffness)
    particle = Particle(1.0, Vector(x), Vector([0.0, 0.0]))
    np.testing.assert_allclose(
        force.force(particle, 0.0).data,
        -_gradient(force, particle),
        rtol=1e-4,
        atol=1e-4,
    )


@settings(max_examples=50, deadline=None)
@given(
    mu=_positive,
    x=st.lists(st.floats(0.5, 5.0, allow_nan=False), min_size=2, max_size=2),
)
def test_gravity_force_is_minus_gradient_of_potential(mu, x) -> None:
    force = CentralGravity([0.0, 0.0], mu=mu)
    particle = Particle(2.0, Vector(x), Vector([0.0, 0.0]))
    np.testing.assert_allclose(
        force.force(particle, 0.0).data,
        -_gradient(force, particle),
        rtol=1e-4,
        atol=1e-4,
    )


@settings(max_examples=30, deadline=None)
@given(
    stiffness=_positive,
    x0=st.floats(-3.0, 3.0, allow_nan=False),
    v0=st.floats(-3.0, 3.0, allow_nan=False),
)
def test_conservative_simulation_conserves_energy(stiffness, x0, v0) -> None:
    system = System(
        [Particle(1.0, Vector([x0]), Vector([v0]))],
        SpringForce([0.0], stiffness=stiffness),
    )
    traj = simulate(
        system,
        (0.0, 5.0),
        t_eval=np.linspace(0.0, 5.0, 101),
        method="DOP853",
        rtol=1e-10,
        atol=1e-12,
    )
    energy = traj.total_energy()
    np.testing.assert_allclose(energy, energy[0], atol=1e-6)


@settings(max_examples=30, deadline=None)
@given(
    mass=st.floats(0.5, 5.0, allow_nan=False),
    v=st.lists(st.floats(-2.0, 2.0, allow_nan=False), min_size=2, max_size=2),
)
def test_free_particle_moves_in_a_straight_line(mass, v) -> None:
    # No forces: x(t) = x0 + v t, exactly (up to integration error).
    system = System([Particle(mass, Vector([0.0, 0.0]), Vector(v))])
    t = np.linspace(0.0, 2.0, 21)
    traj = simulate(system, (0.0, 2.0), t_eval=t, rtol=1e-11, atol=1e-13)
    expected = np.outer(t, np.asarray(v))
    np.testing.assert_allclose(traj.positions(0), expected, rtol=_RTOL, atol=1e-7)
