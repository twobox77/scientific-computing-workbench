"""Bases and coordinates: the numerical workflow end to end.

Run with::

    uv run python examples/04_bases_and_coordinates.py
"""

from __future__ import annotations

import numpy as np

from scw.math_core import Basis, Matrix, Vector, VectorSpace
from scw.numerical import det, inverse, solve


def main() -> None:
    space = VectorSpace(2, name="V")
    basis = Basis([Vector([1.0, 0.0], space=space), Vector([1.0, 1.0], space=space)])
    print("basis:", basis, "-> matrix", basis.to_matrix().tolist())

    v = Vector([3.0, 2.0], space=space)
    coords = basis.to_coordinates(v)
    print("v:", v.to_numpy().tolist(), "coords:", coords.tolist())
    assert basis.from_coordinates(coords) == v

    a = Matrix([[3.0, 1.0], [1.0, 2.0]])
    rhs = Vector([9.0, 8.0])
    x = solve(a, rhs)
    print("solve(A, b):", x.to_numpy().tolist())
    assert np.allclose(a.data @ x.data, rhs.data)

    print("det(A):", det(a))
    identity = a @ inverse(a)
    print("A @ A^-1:", identity.data.tolist())
    assert np.allclose(identity.data, np.eye(2))


if __name__ == "__main__":
    main()
