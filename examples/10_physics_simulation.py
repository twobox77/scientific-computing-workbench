"""Newtonian mechanics: projectiles, a spring, and a planetary orbit.

Roadmap §11, milestone 0.7.  Run with::

    uv run python examples/10_physics_simulation.py
"""

from __future__ import annotations

import numpy as np

from scw.math_core import Vector
from scw.physics import (
    CentralGravity,
    ConstantForce,
    Particle,
    SpringForce,
    System,
    simulate,
)


def projectile() -> None:
    """A ball under uniform gravity: compare with the analytic parabola."""
    g = 9.81
    ball = Particle(mass=1.0, position=Vector([0.0, 0.0]), velocity=Vector([3.0, 4.0]))
    system = System([ball], ConstantForce([0.0, -g]))
    t = np.linspace(0.0, 1.0, 101)
    traj = simulate(system, (0.0, 1.0), t_eval=t, rtol=1e-10, atol=1e-12)

    x, y = traj.positions(0).T
    error = np.max(np.abs(y - (4.0 * t - 0.5 * g * t**2)))
    print("projectile (constant gravity)")
    print("  t_end =", t[-1], " final position =", traj.positions(0)[-1])
    print("  max |y - analytic| =", error)


def harmonic_oscillator() -> None:
    """A mass on a spring: total energy is conserved and x(t) = cos(omega t)."""
    stiffness, mass = 4.0, 1.0
    omega = np.sqrt(stiffness / mass)
    block = Particle(mass=mass, position=Vector([1.0]), velocity=Vector([0.0]))
    system = System([block], SpringForce([0.0], stiffness=stiffness))
    t = np.linspace(0.0, 10.0, 501)
    traj = simulate(system, (0.0, 10.0), t_eval=t, rtol=1e-11, atol=1e-13)

    energy = traj.total_energy()
    x_error = np.max(np.abs(traj.positions(0)[:, 0] - np.cos(omega * t)))
    print("\nharmonic oscillator (spring)")
    print("  omega =", omega)
    print("  max |x - cos(omega t)| =", x_error)
    print("  energy drift =", np.max(np.abs(energy - energy[0])))


def planetary_orbit() -> None:
    """A satellite in a circular orbit: radius, energy and angular momentum hold."""
    mu = 1.0
    satellite = Particle(
        mass=1.0, position=Vector([1.0, 0.0]), velocity=Vector([0.0, 1.0])
    )
    system = System([satellite], CentralGravity([0.0, 0.0], mu=mu))
    period = 2.0 * np.pi
    t = np.linspace(0.0, period, 401)
    traj = simulate(
        system, (0.0, period), method="DOP853", t_eval=t, rtol=1e-11, atol=1e-13
    )

    positions = traj.positions(0)
    velocities = traj.velocities(0)
    radius = np.linalg.norm(positions, axis=1)
    angular = positions[:, 0] * velocities[:, 1] - positions[:, 1] * velocities[:, 0]
    energy = traj.total_energy()
    print("\nplanetary orbit (inverse-square gravity)")
    print("  radius min/max =", radius.min(), radius.max())
    print("  energy drift =", np.max(np.abs(energy - energy[0])))
    print("  angular momentum drift =", np.max(np.abs(angular - angular[0])))
    print("  returns to start:", np.allclose(positions[-1], positions[0], atol=1e-6))


def main() -> None:
    projectile()
    harmonic_oscillator()
    planetary_orbit()


if __name__ == "__main__":
    main()
