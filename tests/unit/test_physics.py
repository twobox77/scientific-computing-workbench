"""Unit tests for :mod:`scw.physics` (particles, forces, systems, simulation)."""

from __future__ import annotations

import numpy as np
import pytest

from scw.exceptions import DimensionError, NumericalError
from scw.math_core import Vector
from scw.physics import (
    CentralGravity,
    ConservativeForce,
    ConstantForce,
    Drag,
    Force,
    Particle,
    SpringForce,
    System,
    Trajectory,
    simulate,
)


# --------------------------------------------------------------------------- #
# Particle
# --------------------------------------------------------------------------- #
def test_particle_basic_quantities() -> None:
    p = Particle(2.0, Vector([1.0, 0.0]), Vector([0.0, 3.0]))
    assert p.mass == 2.0
    assert p.dimension == 2
    np.testing.assert_allclose(p.momentum.data, [0.0, 6.0])
    assert p.kinetic_energy == pytest.approx(0.5 * 2.0 * 9.0)


def test_particle_rejects_bad_mass() -> None:
    with pytest.raises(TypeError):
        Particle(True, Vector([0.0]), Vector([0.0]))  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        Particle(0.0, Vector([0.0]), Vector([0.0]))
    with pytest.raises(ValueError):
        Particle(-1.0, Vector([0.0]), Vector([0.0]))
    with pytest.raises(ValueError):
        Particle(float("inf"), Vector([0.0]), Vector([0.0]))


def test_particle_rejects_mismatched_state_dimensions() -> None:
    with pytest.raises(DimensionError):
        Particle(1.0, Vector([0.0, 0.0]), Vector([0.0]))


def test_particle_rejects_non_vectors() -> None:
    with pytest.raises(TypeError):
        Particle(1.0, [0.0], Vector([0.0]))  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        Particle(1.0, Vector([0.0]), [0.0])  # type: ignore[arg-type]


def test_particle_with_state_keeps_mass_and_name() -> None:
    p = Particle(3.0, Vector([0.0]), Vector([1.0]), name="moon")
    q = p.with_state(Vector([5.0]), Vector([-1.0]))
    assert q.mass == 3.0 and q.name == "moon"
    np.testing.assert_allclose(q.position.data, [5.0])


def test_particle_repr_mentions_name() -> None:
    p = Particle(1.0, Vector([0.0]), Vector([0.0]), name="p")
    assert "name='p'" in repr(p)


# --------------------------------------------------------------------------- #
# Forces
# --------------------------------------------------------------------------- #
def test_constant_force_value_and_potential() -> None:
    f = ConstantForce([0.0, -9.81])
    p = Particle(2.0, Vector([0.0, 5.0]), Vector([0.0, 0.0]))
    np.testing.assert_allclose(f.force(p, 0.0).data, [0.0, -9.81])
    # U = -F . x = -(0*0 + (-9.81)*5) = 49.05
    assert f.potential_energy(p, 0.0) == pytest.approx(49.05)
    assert f.conservative is True
    assert isinstance(f, ConservativeForce)


def test_constant_force_read_only_view() -> None:
    f = ConstantForce([1.0, 2.0])
    with pytest.raises(ValueError):
        f.vector[0] = 9.0


def test_constant_force_dimension_mismatch() -> None:
    f = ConstantForce([1.0, 2.0, 3.0])
    p = Particle(1.0, Vector([0.0, 0.0]), Vector([0.0, 0.0]))
    with pytest.raises(DimensionError):
        f.force(p, 0.0)


def test_spring_force_is_hooke_law() -> None:
    f = SpringForce([0.0], stiffness=4.0)
    p = Particle(1.0, Vector([3.0]), Vector([0.0]))
    np.testing.assert_allclose(f.force(p, 0.0).data, [-12.0])
    assert f.potential_energy(p, 0.0) == pytest.approx(0.5 * 4.0 * 9.0)
    assert f.stiffness == 4.0


def test_spring_force_rejects_bad_stiffness() -> None:
    with pytest.raises(TypeError):
        SpringForce([0.0], stiffness="x")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        SpringForce([0.0], stiffness=0.0)
    with pytest.raises(ValueError):
        SpringForce([0.0], stiffness=-1.0)


def test_gravity_is_inverse_square() -> None:
    mu = 3.0
    f = CentralGravity([0.0, 0.0], mu=mu)
    p = Particle(2.0, Vector([2.0, 0.0]), Vector([0.0, 0.0]))
    # F = -mu m (x-c)/|x-c|^3 = -3*2*[2,0]/8 = [-1.5, 0]
    np.testing.assert_allclose(f.force(p, 0.0).data, [-1.5, 0.0])
    # U = -mu m / r = -6/2 = -3
    assert f.potential_energy(p, 0.0) == pytest.approx(-3.0)
    assert f.mu == mu


def test_gravity_singularity_at_centre() -> None:
    f = CentralGravity([0.0], mu=1.0)
    p = Particle(1.0, Vector([0.0]), Vector([0.0]))
    with pytest.raises(ZeroDivisionError):
        f.force(p, 0.0)


def test_gravity_rejects_bad_mu() -> None:
    with pytest.raises(ValueError):
        CentralGravity([0.0], mu=0.0)
    with pytest.raises(TypeError):
        CentralGravity([0.0], mu=None)  # type: ignore[arg-type]


def test_drag_opposes_velocity_and_is_not_conservative() -> None:
    f = Drag(coefficient=0.5)
    p = Particle(1.0, Vector([0.0, 0.0]), Vector([2.0, -4.0]))
    np.testing.assert_allclose(f.force(p, 0.0).data, [-1.0, 2.0])
    assert f.conservative is False
    assert not isinstance(f, ConservativeForce)
    with pytest.raises(ValueError):
        Drag(coefficient=-1.0)


def test_force_is_abstract() -> None:
    with pytest.raises(TypeError):
        Force()  # type: ignore[abstract]
    with pytest.raises(TypeError):
        ConservativeForce()  # type: ignore[abstract]


# --------------------------------------------------------------------------- #
# System
# --------------------------------------------------------------------------- #
def test_system_rejects_empty_and_mixed_dimensions() -> None:
    with pytest.raises(ValueError):
        System([])
    a = Particle(1.0, Vector([0.0, 0.0]), Vector([0.0, 0.0]))
    b = Particle(1.0, Vector([0.0]), Vector([0.0]))
    with pytest.raises(DimensionError):
        System([a, b])


def test_system_rejects_duplicate_names() -> None:
    a = Particle(1.0, Vector([0.0]), Vector([0.0]), name="x")
    b = Particle(1.0, Vector([1.0]), Vector([0.0]), name="x")
    with pytest.raises(ValueError):
        System([a, b])


def test_system_rejects_non_particle_and_non_force() -> None:
    with pytest.raises(TypeError):
        System([Vector([0.0])])  # type: ignore[list-item]
    a = Particle(1.0, Vector([0.0]), Vector([0.0]))
    with pytest.raises(TypeError):
        System([a], forces=[object()])  # type: ignore[list-item]


def test_system_single_force_or_iterable() -> None:
    a = Particle(1.0, Vector([0.0]), Vector([0.0]))
    single = System([a], ConstantForce([1.0]))
    many = System([a], [ConstantForce([1.0]), Drag(coefficient=1.0)])
    assert len(single.forces) == 1
    assert len(many.forces) == 2


def test_system_particle_lookup() -> None:
    a = Particle(1.0, Vector([0.0]), Vector([0.0]), name="a")
    b = Particle(2.0, Vector([1.0]), Vector([0.0]), name="b")
    s = System([a, b])
    assert s.particle("b") is b
    assert s.particle(0) is a
    with pytest.raises(KeyError):
        s.particle("c")


def test_system_net_force_sums_contributions() -> None:
    a = Particle(2.0, Vector([0.0]), Vector([1.0]))
    s = System([a], [ConstantForce([4.0]), Drag(coefficient=1.0)])
    # 4 - 1*1 = 3
    np.testing.assert_allclose(s.net_force(a, 0.0).data, [3.0])
    np.testing.assert_allclose(s.acceleration(a, 0.0).data, [1.5])


def test_system_total_momentum_and_energy() -> None:
    a = Particle(2.0, Vector([0.0]), Vector([1.0]))
    b = Particle(3.0, Vector([10.0]), Vector([-1.0]))
    s = System([a, b])
    np.testing.assert_allclose(s.total_momentum().data, [2.0 - 3.0])
    assert s.kinetic_energy() == pytest.approx(0.5 * 2.0 + 0.5 * 3.0)


def test_system_potential_energy_requires_conservative_forces() -> None:
    a = Particle(1.0, Vector([0.0]), Vector([0.0]))
    s = System([a], Drag(coefficient=1.0))
    assert s.conservative is False
    with pytest.raises(NumericalError):
        s.potential_energy()
    with pytest.raises(NumericalError):
        s.total_energy()


def test_system_repr_and_properties() -> None:
    a = Particle(1.0, Vector([0.0]), Vector([0.0]))
    s = System([a], ConstantForce([1.0]), name="sys")
    assert s.name == "sys"
    assert s.num_particles == 1
    assert s.dimension == 1
    assert "particles=1" in repr(s)


# --------------------------------------------------------------------------- #
# Simulation / Trajectory
# --------------------------------------------------------------------------- #
def test_projectile_matches_analytic_solution() -> None:
    g = 9.81
    ball = Particle(1.0, Vector([0.0, 0.0]), Vector([3.0, 4.0]))
    system = System([ball], ConstantForce([0.0, -g]))
    t = np.linspace(0.0, 1.0, 51)
    traj = simulate(system, (0.0, 1.0), t_eval=t, rtol=1e-10, atol=1e-12)
    pos = traj.positions(0)
    np.testing.assert_allclose(pos[:, 0], 3.0 * t, atol=1e-9)
    np.testing.assert_allclose(pos[:, 1], 4.0 * t - 0.5 * g * t**2, atol=1e-9)


def test_simple_harmonic_motion_is_cosine() -> None:
    system = System(
        [Particle(1.0, Vector([1.0]), Vector([0.0]))], SpringForce([0.0], stiffness=4.0)
    )
    t = np.linspace(0.0, 10.0, 501)
    traj = simulate(system, (0.0, 10.0), t_eval=t, rtol=1e-11, atol=1e-13)
    np.testing.assert_allclose(traj.positions(0)[:, 0], np.cos(2.0 * t), atol=1e-7)


def test_trajectory_reports_energy_and_momentum() -> None:
    system = System(
        [Particle(1.0, Vector([1.0]), Vector([0.0]))], SpringForce([0.0], stiffness=4.0)
    )
    t = np.linspace(0.0, 6.0, 121)
    traj = simulate(system, (0.0, 6.0), t_eval=t, rtol=1e-10, atol=1e-12)
    energy = traj.total_energy()
    np.testing.assert_allclose(energy, energy[0], atol=1e-7)
    # Momentum is m * v; for a single particle it oscillates rather than being
    # conserved (the spring is an external force), so check it against m v.
    np.testing.assert_allclose(
        traj.momentum().ravel(), traj.velocities(0)[:, 0], atol=1e-9
    )


def test_trajectory_shapes_and_accessors() -> None:
    system = System([Particle(1.0, Vector([0.0, 0.0]), Vector([1.0, 0.0]))])
    traj = simulate(system, (0.0, 1.0), t_eval=[0.0, 0.5, 1.0])
    assert isinstance(traj, Trajectory)
    assert traj.positions(0).shape == (3, 2)
    assert traj.velocities(0).shape == (3, 2)
    assert len(traj) == 3
    assert traj.num_particles == 1
    assert traj.dimension == 2
    assert len(traj.states(0)) == 3
    final_position = traj.final_system().particles[0].position.data
    np.testing.assert_allclose(final_position, [1.0, 0.0])


def test_trajectory_negative_index_and_bounds() -> None:
    system = System([Particle(1.0, Vector([0.0]), Vector([1.0]))])
    traj = simulate(system, (0.0, 1.0), t_eval=[0.0, 1.0])
    np.testing.assert_allclose(traj.positions(-1), traj.positions(0))
    with pytest.raises(IndexError):
        traj.positions(1)


def test_simulate_rejects_non_system() -> None:
    with pytest.raises(TypeError):
        simulate([], (0.0, 1.0))  # type: ignore[arg-type]


def test_simulate_passes_method_and_dense_output() -> None:
    system = System(
        [Particle(1.0, Vector([1.0]), Vector([0.0]))], SpringForce([0.0], stiffness=1.0)
    )
    traj = simulate(
        system,
        (0.0, 1.0),
        method="DOP853",
        dense_output=True,
        t_eval=[0.0, 1.0],
        rtol=1e-11,
        atol=1e-13,
    )
    assert traj.solution.method == "DOP853"
    # interpolate returns the flat [position, velocity] state; the position
    # component follows cos(t) for a unit mass on a unit spring.
    state = traj.solution.interpolate(0.5)
    assert state.dimension == 2
    assert state.data[0] == pytest.approx(np.cos(0.5), abs=1e-8)


def test_two_particle_gravity_conserves_energy() -> None:
    # Two particles falling toward a fixed central mass: the central force is
    # conservative, so the total mechanical energy is conserved.
    mu = 1.0
    a = Particle(1.0, Vector([1.0, 0.0]), Vector([0.0, 0.5]))
    b = Particle(1.0, Vector([-1.0, 0.0]), Vector([0.0, -0.5]))
    system = System([a, b], CentralGravity([0.0, 0.0], mu=mu))
    t = np.linspace(0.0, 3.0, 301)
    traj = simulate(
        system, (0.0, 3.0), method="DOP853", t_eval=t, rtol=1e-11, atol=1e-13
    )
    energy = traj.total_energy()
    np.testing.assert_allclose(energy, energy[0], atol=1e-7)
