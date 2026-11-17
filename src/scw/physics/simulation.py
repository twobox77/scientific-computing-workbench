"""Newtonian simulation: integrate a :class:`~scw.physics.system.System` in time.

The equations of motion are the first-order system ``dx/dt = v`` and
``dv/dt = F(x, t) / m``.  They are handed to
:func:`scw.numerical.solve_ivp`, so the integrators and their options are the
numerical layer's, and the physics layer only packs and unpacks the state
vector.  The result is a :class:`Trajectory`.

This module depends on :mod:`scw.math_core`, :mod:`scw.numerical` and the
sibling physics modules; it imports neither the CLI, plotting, nor the file
system.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from scw.config import DEFAULT_DTYPE
from scw.math_core.vector import Vector
from scw.numerical.ode import ODESolution, solve_ivp
from scw.physics.particles import Particle
from scw.physics.system import System


def _pack(particles: Sequence[Particle]) -> np.ndarray:
    """Flatten particles into ``[positions..., velocities...]``."""
    positions = np.concatenate([p.position.data for p in particles])
    velocities = np.concatenate([p.velocity.data for p in particles])
    return np.concatenate([positions, velocities])


def _particles_from_state(state: np.ndarray, system: System) -> tuple[Particle, ...]:
    """Rebuild the particles from a flat ``[positions..., velocities...]`` state."""
    dimension = system.dimension
    count = system.num_particles
    block = count * dimension
    positions = state[:block].reshape(count, dimension)
    velocities = state[block:].reshape(count, dimension)
    rebuilt = []
    # complexity: rebuilds the handful of particles in the system
    for i, template in enumerate(system.particles):
        rebuilt.append(
            template.with_state(
                Vector(positions[i], space=template.position.space),
                Vector(velocities[i], space=template.velocity.space),
            )
        )
    return tuple(rebuilt)


def _make_rhs(system: System):
    """Build the ``(t, Vector) -> Vector`` right-hand side for :func:`solve_ivp`."""
    dimension = system.dimension
    count = system.num_particles
    block = count * dimension

    def rhs(t: float, y: Vector) -> Vector:
        particles = _particles_from_state(y.data, system)
        current = system.with_particles(particles)
        deriv = np.empty(2 * block, dtype=DEFAULT_DTYPE)
        # complexity: iterates the handful of particles in the system
        for i, particle in enumerate(particles):
            start = i * dimension
            deriv[start : start + dimension] = particle.velocity.data
            deriv[block + start : block + start + dimension] = current.acceleration(
                particle, t
            ).data
        return Vector(deriv)

    return rhs


class Trajectory:
    """The time history of a simulated :class:`~scw.physics.system.System`.

    ``t`` is the time grid.  The state at each time is stored as a flat
    ``[positions..., velocities...]`` vector; :meth:`positions` and
    :meth:`velocities` return particle ``i``'s coordinates as arrays of shape
    ``(n_points, dimension)``, and :meth:`states` returns :class:`Particle`
    objects.  The conserved quantities are available directly through
    :meth:`kinetic_energy`, :meth:`potential_energy`, :meth:`total_energy` and
    :meth:`momentum`.
    """

    __slots__ = ("_system", "_solution", "_dimension", "_count")

    def __init__(self, system: System, solution: ODESolution) -> None:
        self._system = system
        self._solution = solution
        self._dimension = system.dimension
        self._count = system.num_particles

    @property
    def system(self) -> System:
        """The system that was simulated (carrying its initial state)."""
        return self._system

    @property
    def solution(self) -> ODESolution:
        """The underlying :class:`~scw.numerical.ode.ODESolution`."""
        return self._solution

    @property
    def t(self) -> np.ndarray:
        """Read-only view of the time grid, shape ``(n_points,)``."""
        return self._solution.t

    @property
    def dimension(self) -> int:
        """Dimension of the space the particles move in."""
        return self._dimension

    @property
    def num_particles(self) -> int:
        """Number of particles."""
        return self._count

    def __len__(self) -> int:
        return len(self._solution)

    def _slice(self, index: int) -> tuple[int, int]:
        if not -self._count <= index < self._count:
            raise IndexError(
                f"particle index {index} out of range for {self._count} particles"
            )
        i = index % self._count
        return i * self._dimension, (i + 1) * self._dimension

    def positions(self, index: int = 0) -> np.ndarray:
        """Particle ``index``'s positions over time, shape ``(n_points, dim)``."""
        start, stop = self._slice(index)
        return self._solution.y[:, start:stop]

    def velocities(self, index: int = 0) -> np.ndarray:
        """Particle ``index``'s velocities over time, shape ``(n_points, dim)``."""
        start, stop = self._slice(index)
        offset = self._dimension * self._count
        return self._solution.y[:, offset + start : offset + stop]

    def states(self, index: int = 0) -> list[Particle]:
        """Particle ``index`` at each time in the grid, as ``Particle`` objects."""
        template = self._system.particles[index % self._count]
        positions = self.positions(index)
        velocities = self.velocities(index)
        return [
            template.with_state(
                Vector(positions[k], space=template.position.space),
                Vector(velocities[k], space=template.velocity.space),
            )
            for k in range(len(self))
        ]

    def final_system(self) -> System:
        """The system at the last time in the grid."""
        return self._system.with_particles(
            tuple(self.states(i)[-1] for i in range(self._count))
        )

    def _masses(self) -> np.ndarray:
        return np.array([p.mass for p in self._system.particles])

    def kinetic_energy(self) -> np.ndarray:
        """Kinetic energy at each time, shape ``(n_points,)``."""
        block = self._count * self._dimension
        velocities = self._solution.y[:, block:].reshape(
            len(self), self._count, self._dimension
        )
        speeds2 = np.sum(velocities**2, axis=2)
        return np.asarray(0.5 * (speeds2 @ self._masses()))

    def momentum(self) -> np.ndarray:
        """Total momentum at each time, shape ``(n_points, dimension)``."""
        block = self._count * self._dimension
        velocities = self._solution.y[:, block:].reshape(
            len(self), self._count, self._dimension
        )
        return np.asarray(np.einsum("ncd,c->nd", velocities, self._masses()))

    def _particles_at(self, k: int) -> tuple[Particle, ...]:
        block = self._count * self._dimension
        state = self._solution.y[k]
        positions = state[:block].reshape(self._count, self._dimension)
        velocities = state[block:].reshape(self._count, self._dimension)
        return tuple(
            template.with_state(Vector(positions[i]), Vector(velocities[i]))
            for i, template in enumerate(self._system.particles)
        )

    def potential_energy(self) -> np.ndarray:
        """Potential energy at each time (requires conservative forces)."""
        result = np.empty(len(self), dtype=DEFAULT_DTYPE)
        # complexity: one energy evaluation per output time, O(#forces) each
        for k in range(len(self)):
            system_k = self._system.with_particles(self._particles_at(k))
            result[k] = system_k.potential_energy(float(self.t[k]))
        return result

    def total_energy(self) -> np.ndarray:
        """Mechanical energy at each time (requires conservative forces)."""
        return np.asarray(self.kinetic_energy() + self.potential_energy())

    def __repr__(self) -> str:
        return (
            f"Trajectory(particles={self._count}, points={len(self)}, "
            f"dimension={self._dimension})"
        )


def simulate(
    system: System,
    t_span: Sequence[float],
    *,
    method: str = "RK45",
    t_eval: Sequence[float] | None = None,
    rtol: float | None = None,
    atol: float | None = None,
    max_step: float | None = None,
    first_step: float | None = None,
    dense_output: bool = False,
) -> Trajectory:
    """Integrate ``system`` from ``t_span[0]`` to ``t_span[1]``.

    ``system`` supplies the particles (initial positions and velocities), their
    masses and the forces acting on them.  The remaining keyword arguments
    mirror :func:`scw.numerical.solve_ivp` (``method`` is one of
    :data:`scw.numerical.METHODS`).  Returns a :class:`Trajectory`.

    A failed integration raises :class:`~scw.exceptions.ConvergenceError` (via
    :func:`solve_ivp`).
    """
    if not isinstance(system, System):
        raise TypeError("simulate expects a System")
    solution = solve_ivp(
        _make_rhs(system),
        t_span,
        Vector(_pack(system.particles)),
        method=method,
        t_eval=t_eval,
        rtol=rtol,
        atol=atol,
        max_step=max_step,
        first_step=first_step,
        dense_output=dense_output,
    )
    return Trajectory(system, solution)
