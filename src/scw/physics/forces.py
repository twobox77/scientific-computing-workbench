"""Force models: what pushes a particle around.

A :class:`Force` answers one question: given a particle and a time, what force
(vector) acts on it?  This module ships the forces that cover the classic
introductory problems:

* :class:`ConstantForce` — a uniform field, ``F = const`` (e.g. weight near the
  ground);
* :class:`SpringForce` — Hooke's law, ``F = -k (x - anchor)``;
* :class:`CentralGravity` — an inverse-square attraction to a fixed centre,
  ``F = -mu m (x - c) / |x - c|^3``.

Those three are **conservative**: the work they do is path-independent, so each
provides a potential energy ``U`` with ``F = -grad U`` and they subclass
:class:`ConservativeForce`.  :class:`Drag` is deliberately not conservative:
``F = -c v`` (linear drag) removes energy from the system.

The layer uses the domain and numerical APIs only; it imports neither the CLI,
plotting, nor the file system.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from scw.exceptions import DimensionError
from scw.math_core.vector import Vector
from scw.physics.particles import Particle

_REAL = (int, float, np.integer, np.floating)


def _real(value: Any, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, _REAL):
        raise TypeError(f"{name} must be a real number")
    result = float(value)
    if not np.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(value: Any, *, name: str) -> float:
    result = _real(value, name=name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def _non_negative(value: Any, *, name: str) -> float:
    result = _real(value, name=name)
    if result < 0.0:
        raise ValueError(f"{name} must be non-negative")
    return result


def _point(value: Any, *, name: str) -> np.ndarray:
    """Validate ``value`` as a non-empty finite 1-D point and return it."""
    arr = np.array(value, dtype=float)
    if arr.ndim != 1 or arr.size == 0:
        raise DimensionError(f"{name} must be a non-empty one-dimensional vector")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} coordinates must be finite")
    return arr


def _match_dimension(point: np.ndarray, particle: Particle, *, name: str) -> None:
    if particle.dimension != point.size:
        raise DimensionError(
            f"{name} has dimension {point.size} but the particle moves in "
            f"dimension {particle.dimension}"
        )


class Force(ABC):
    """A force acting on a particle, possibly time-dependent."""

    #: Whether this force is conservative (i.e. has a potential energy).
    conservative: bool = False

    @abstractmethod
    def force(self, particle: Particle, t: float) -> Vector:
        """The force vector on ``particle`` at time ``t``."""

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class ConservativeForce(Force):
    """A force that derives from a potential ``U`` via ``F = -grad U``."""

    conservative = True

    @abstractmethod
    def potential_energy(self, particle: Particle, t: float) -> float:
        """The potential energy ``U`` of ``particle`` at time ``t``."""


class ConstantForce(ConservativeForce):
    """A uniform (position- and time-independent) force field ``F``.

    The potential is ``U(x) = -F . x``.
    """

    __slots__ = ("_force",)

    def __init__(self, force: Any) -> None:
        self._force = _point(force, name="force")

    @property
    def vector(self) -> np.ndarray:
        """Read-only view of the constant force vector."""
        view = self._force.view()
        view.flags.writeable = False
        return view

    def force(self, particle: Particle, t: float) -> Vector:
        _match_dimension(self._force, particle, name="force")
        return Vector(self._force, space=particle.position.space)

    def potential_energy(self, particle: Particle, t: float) -> float:
        _match_dimension(self._force, particle, name="force")
        return float(-np.dot(self._force, particle.position.data))

    def __repr__(self) -> str:
        return f"ConstantForce({self._force.tolist()})"


class SpringForce(ConservativeForce):
    """Hooke's law ``F = -k (x - anchor)``, potential ``(1/2) k |x - anchor|^2``."""

    __slots__ = ("_anchor", "_stiffness")

    def __init__(self, anchor: Any, *, stiffness: Any) -> None:
        self._anchor = _point(anchor, name="anchor")
        self._stiffness = _positive(stiffness, name="stiffness")

    @property
    def anchor(self) -> np.ndarray:
        """Read-only view of the anchor point."""
        view = self._anchor.view()
        view.flags.writeable = False
        return view

    @property
    def stiffness(self) -> float:
        """The spring constant ``k``."""
        return self._stiffness

    def _displacement(self, particle: Particle) -> np.ndarray:
        _match_dimension(self._anchor, particle, name="anchor")
        return np.asarray(particle.position.data - self._anchor)

    def force(self, particle: Particle, t: float) -> Vector:
        return Vector(
            -self._stiffness * self._displacement(particle),
            space=particle.position.space,
        )

    def potential_energy(self, particle: Particle, t: float) -> float:
        r = self._displacement(particle)
        return float(0.5 * self._stiffness * np.dot(r, r))

    def __repr__(self) -> str:
        return (
            f"SpringForce(anchor={self._anchor.tolist()}, stiffness={self._stiffness})"
        )


class CentralGravity(ConservativeForce):
    """Inverse-square attraction to a fixed centre.

    With standard gravitational parameter ``mu = G M`` and centre ``c``, the
    force on a particle of mass ``m`` at ``x`` is
    ``F = -mu m (x - c) / |x - c|^3`` and the potential is ``U = -mu m / |x - c|``.
    """

    __slots__ = ("_centre", "_mu")

    def __init__(self, centre: Any, *, mu: Any) -> None:
        self._centre = _point(centre, name="centre")
        self._mu = _positive(mu, name="mu")

    @property
    def centre(self) -> np.ndarray:
        """Read-only view of the centre of attraction."""
        view = self._centre.view()
        view.flags.writeable = False
        return view

    @property
    def mu(self) -> float:
        """The standard gravitational parameter ``G M``."""
        return self._mu

    def _separation(self, particle: Particle) -> tuple[np.ndarray, float]:
        _match_dimension(self._centre, particle, name="centre")
        r = particle.position.data - self._centre
        distance = float(np.linalg.norm(r))
        if distance == 0.0:
            raise ZeroDivisionError(
                "the particle is at the centre of attraction; the force is singular"
            )
        return r, distance

    def force(self, particle: Particle, t: float) -> Vector:
        r, distance = self._separation(particle)
        magnitude = -self._mu * particle.mass / distance**3
        return Vector(magnitude * r, space=particle.position.space)

    def potential_energy(self, particle: Particle, t: float) -> float:
        _, distance = self._separation(particle)
        return float(-self._mu * particle.mass / distance)

    def __repr__(self) -> str:
        return f"CentralGravity(centre={self._centre.tolist()}, mu={self._mu})"


class Drag(Force):
    """Linear drag ``F = -c v`` — a non-conservative force that dissipates energy."""

    __slots__ = ("_coefficient",)

    def __init__(self, *, coefficient: Any) -> None:
        self._coefficient = _non_negative(coefficient, name="coefficient")

    @property
    def coefficient(self) -> float:
        """The drag coefficient ``c``."""
        return self._coefficient

    def force(self, particle: Particle, t: float) -> Vector:
        return Vector(
            -self._coefficient * particle.velocity.data,
            space=particle.position.space,
        )

    def __repr__(self) -> str:
        return f"Drag(coefficient={self._coefficient})"
