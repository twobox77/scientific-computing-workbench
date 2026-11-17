"""Point masses: the objects a physics simulation moves.

A :class:`Particle` is a point mass carrying a position and a velocity, both
:class:`~scw.math_core.vector.Vector` objects, so the whole linear-algebra core
applies to them unchanged.  The only physics this class adds is the mass and
the two derived quantities that use it: momentum and kinetic energy.

This module depends only on :mod:`scw.math_core` and :mod:`scw.exceptions`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from scw.exceptions import DimensionError
from scw.math_core.vector import Vector

_REAL = (int, float, np.integer, np.floating)


def validate_mass(mass: Any) -> float:
    """Return ``mass`` as a positive finite float, or raise.

    A non-number raises :class:`TypeError`; a non-finite or non-positive value
    raises :class:`ValueError`.
    """
    if isinstance(mass, bool) or not isinstance(mass, _REAL):
        raise TypeError("mass must be a real number")
    value = float(mass)
    if not np.isfinite(value):
        raise ValueError("mass must be finite")
    if value <= 0.0:
        raise ValueError("mass must be positive")
    return value


@dataclass(frozen=True)
class Particle:
    """A point mass with a position and a velocity in a common space.

    ``position`` and ``velocity`` must be :class:`Vector` objects of the same
    dimension; ``mass`` must be positive and finite.  Equality is field-wise,
    so two particles are equal exactly when their mass, position, velocity and
    name match.
    """

    mass: float
    position: Vector
    velocity: Vector
    name: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "mass", validate_mass(self.mass))
        if not isinstance(self.position, Vector):
            raise TypeError("position must be a Vector")
        if not isinstance(self.velocity, Vector):
            raise TypeError("velocity must be a Vector")
        if self.position.dimension != self.velocity.dimension:
            raise DimensionError(
                "position and velocity must have the same dimension, got "
                f"{self.position.dimension} and {self.velocity.dimension}"
            )

    @property
    def dimension(self) -> int:
        """Dimension of the space the particle moves in."""
        return self.position.dimension

    @property
    def momentum(self) -> Vector:
        """Linear momentum ``m v``."""
        return self.mass * self.velocity

    @property
    def kinetic_energy(self) -> float:
        """Kinetic energy ``(1/2) m |v|^2``."""
        return 0.5 * self.mass * self.velocity.dot(self.velocity)

    def with_state(self, position: Vector, velocity: Vector) -> Particle:
        """A copy of this particle at a new ``position`` and ``velocity``."""
        return Particle(self.mass, position, velocity, self.name)

    def __repr__(self) -> str:
        label = f", name={self.name!r}" if self.name is not None else ""
        return (
            f"Particle(mass={self.mass!r}, position={self.position!r}, "
            f"velocity={self.velocity!r}{label})"
        )
