"""Matrices, linear maps and solving linear systems.

Run with::

    uv run python examples/02_matrix_operations.py
"""

from __future__ import annotations

import numpy as np

from scw.math_core import LinearMap, Matrix, Vector
from scw.numerical import det, solve


def main() -> None:
    a = Matrix([[3.0, 1.0], [1.0, 2.0]])
    b = Matrix([[1.0, 0.0], [0.0, 1.0]])

    print("A =", a.data.tolist())
    print("A @ I =", (a @ b).data.tolist())
    print("A^T =", a.T.data.tolist())
    print("det(A):", det(a))

    t = LinearMap.from_matrix(a)
    print("T applied to [1, 1]:", t.apply(Vector([1.0, 1.0])).to_numpy().tolist())

    rhs = Vector([9.0, 8.0])
    x = solve(a, rhs)
    print("solve(A, b):", x.to_numpy().tolist())
    assert np.allclose(a.data @ x.data, rhs.data)


if __name__ == "__main__":
    main()
