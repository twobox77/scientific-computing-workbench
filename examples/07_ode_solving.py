"""Solving initial-value ODEs: exponential decay and a harmonic oscillator.

Run with::

    uv run python examples/07_ode_solving.py
"""

from __future__ import annotations

import numpy as np

from scw.math_core import Vector
from scw.numerical import solve_ivp


def decay(t: float, y: Vector) -> Vector:
    """y' = -y, the simplest linear decay."""
    return -1.0 * y


def oscillator(t: float, y: Vector) -> Vector:
    """y = (position, velocity); y' = (velocity, -position)."""
    return Vector([y.data[1], -y.data[0]])


def main() -> None:
    # Exponential decay: y(t) = exp(-t) from y(0) = 1.
    sol = solve_ivp(
        decay,
        (0.0, 5.0),
        Vector([1.0]),
        t_eval=np.linspace(0.0, 5.0, 6),
        rtol=1e-10,
        atol=1e-12,
    )
    print("decay: success =", sol.success, " method =", sol.method)
    print("  t =", sol.t)
    print("  y =", sol.y.ravel())
    print("  max |y - exp(-t)| =", np.max(np.abs(sol.y.ravel() - np.exp(-sol.t))))

    # Harmonic oscillator: the energy 0.5*(q^2 + v^2) is conserved.
    orbit = solve_ivp(
        oscillator,
        (0.0, 20.0),
        Vector([1.0, 0.0]),
        method="DOP853",
        rtol=1e-10,
        atol=1e-12,
    )
    energy = orbit.y[:, 0] ** 2 + orbit.y[:, 1] ** 2
    print(
        "\noscillator: points =", len(orbit), " final state =", orbit.final_state.data
    )
    print("  energy drift =", np.max(np.abs(energy - 1.0)))


if __name__ == "__main__":
    main()
