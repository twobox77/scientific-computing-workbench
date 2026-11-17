"""Particle systems: several particles, the forces on them, and their energies.

A :class:`System` groups the particles of one simulation together with the
forces that act on *all* of them (a uniform field, drag, a spring, a central
attraction).  It is the place where the bookkeeping lives — total momentum and
total (kinetic, potential, mechanical) energy — so that a simulation only has
to supply a time span.

This module depends on :mod:`scw.math_core`, :mod:`scw.exceptions` and the
sibling physics modules; it imports neither the CLI, plotting, nor the file
system.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

import numpy as np

from scw.exceptions import DimensionError, NumericalError
from scw.math_core.vector import Vector
from scw.physics.forces import ConservativeForce, Force
from scw.physics.particles import Particle


def _as_force_sequence(forces: Any) -> tuple[Force, ...]:
    if isinstance(forces, Force):
        return (forces,)
    if not isinstance(forces, Iterable):
        raise TypeError("forces must be a Force or an iterable of Force objects")
    result = tuple(forces)
    # complexity: validates the handful of forces registered on the system
    for item in result:
        if not isinstance(item, Force):
            raise TypeError("every force must be a Force")
    return result


class System:
    """A set of particles and the forces that act on all of them.

    ``particles`` must be non-empty and share one dimension.  When names are
    given they must be unique, so a particle can be looked up by name.
    ``forces`` may be a single :class:`~scw.physics.forces.Force` or an iterable
    of them; each force is applied to every particle.
    """

    __slots__ = ("_particles", "_forces", "_name", "_index")

    def __init__(
        self,
        particles: Sequence[Particle],
        forces: Any = (),
        *,
        name: str | None = None,
    ) -> None:
        items = tuple(particles)
        if not items:
            raise ValueError("a system needs at least one particle")
        # complexity: validates the handful of particles in the system
        for particle in items:
            if not isinstance(particle, Particle):
                raise TypeError("every element of particles must be a Particle")
        dimension = items[0].dimension
        # complexity: validates the handful of particles in the system
        for particle in items[1:]:
            if particle.dimension != dimension:
                raise DimensionError(
                    "all particles must move in the same dimension, got "
                    f"{dimension} and {particle.dimension}"
                )
        index: dict[str, int] = {}
        # complexity: builds the name index over the handful of particles
        for position, particle in enumerate(items):
            if particle.name is not None:
                if particle.name in index:
                    raise ValueError(f"duplicate particle name {particle.name!r}")
                index[particle.name] = position
        self._particles = items
        self._forces = _as_force_sequence(forces)
        self._name = name
        self._index = index

    @property
    def name(self) -> str | None:
        """An optional human-readable name."""
        return self._name

    @property
    def particles(self) -> tuple[Particle, ...]:
        """The particles, in order."""
        return self._particles

    @property
    def forces(self) -> tuple[Force, ...]:
        """The forces acting on every particle, in order."""
        return self._forces

    @property
    def dimension(self) -> int:
        """Dimension of the space the particles move in."""
        return self._particles[0].dimension

    @property
    def num_particles(self) -> int:
        """Number of particles."""
        return len(self._particles)

    @property
    def conservative(self) -> bool:
        """True when every force is conservative (so total energy is defined)."""
        return all(force.conservative for force in self._forces)

    def particle(self, key: int | str) -> Particle:
        """The particle at ``key`` (an index or a unique name)."""
        if isinstance(key, str):
            try:
                return self._particles[self._index[key]]
            except KeyError as exc:
                raise KeyError(f"no particle named {key!r}") from exc
        return self._particles[key]

    def net_force(self, particle: Particle, t: float) -> Vector:
        """The vector sum of every force acting on ``particle`` at time ``t``."""
        total = np.zeros(self.dimension)
        # complexity: iterates the handful of forces registered on the system
        for force in self._forces:
            total = total + force.force(particle, t).data
        return Vector(total, space=particle.position.space)

    def acceleration(self, particle: Particle, t: float) -> Vector:
        """The acceleration ``F / m`` of ``particle`` at time ``t``."""
        return (1.0 / particle.mass) * self.net_force(particle, t)

    def with_particles(self, particles: Sequence[Particle]) -> System:
        """A copy of this system at a new set of particle states."""
        return System(particles, self._forces, name=self._name)

    def total_momentum(self) -> Vector:
        """The total linear momentum ``sum_i m_i v_i``."""
        space = self._particles[0].velocity.space
        total = np.zeros(self.dimension)
        # complexity: iterates the handful of particles in the system
        for particle in self._particles:
            total = total + particle.momentum.data
        return Vector(total, space=space)

    def kinetic_energy(self) -> float:
        """The total kinetic energy ``sum_i (1/2) m_i |v_i|^2``."""
        masses = np.array([p.mass for p in self._particles])
        speeds2 = np.array([p.velocity.dot(p.velocity) for p in self._particles])
        return float(0.5 * np.dot(masses, speeds2))

    def potential_energy(self, t: float = 0.0) -> float:
        """The total potential energy, or raise if some force is not conservative."""
        total = 0.0
        # complexity: iterates the handful of forces registered on the system
        for force in self._forces:
            if not isinstance(force, ConservativeForce):
                raise NumericalError(
                    f"potential energy is undefined: {force!r} is not conservative"
                )
            # complexity: iterates the handful of particles in the system
            for particle in self._particles:
                total += force.potential_energy(particle, t)
        return float(total)

    def total_energy(self, t: float = 0.0) -> float:
        """The mechanical energy ``K + U`` (requires conservative forces)."""
        return self.kinetic_energy() + self.potential_energy(t)

    def __repr__(self) -> str:
        label = f", name={self._name!r}" if self._name is not None else ""
        return (
            f"System(particles={self.num_particles}, forces={len(self._forces)}{label})"
        )
