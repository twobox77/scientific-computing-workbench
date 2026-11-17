"""Physics models and simulation (roadmap §11, 0.7).

This layer turns the mathematical core into mechanics: point masses
(:class:`Particle`), the forces that act on them (:class:`Force` and friends),
a :class:`System` that groups particles with their forces and reports the
conserved quantities, and a :func:`simulate` driver that integrates the
equations of motion with :func:`scw.numerical.solve_ivp`.

It uses the math and numerical APIs and must not import the CLI, plotting or
file-system code.
"""

from __future__ import annotations

from scw.physics.forces import (
    CentralGravity,
    ConservativeForce,
    ConstantForce,
    Drag,
    Force,
    SpringForce,
)
from scw.physics.particles import Particle
from scw.physics.simulation import Trajectory, simulate
from scw.physics.system import System

__all__ = [
    "CentralGravity",
    "ConservativeForce",
    "ConstantForce",
    "Drag",
    "Force",
    "Particle",
    "SpringForce",
    "System",
    "Trajectory",
    "simulate",
]
