"""Linear-algebra services backed by SciPy.

Prefer :func:`solve` over forming an explicit inverse when solving a linear
system; :func:`inverse` exists for the cases where the inverse itself is the
object of interest.
"""

from __future__ import annotations

import numpy as np
import scipy.linalg

from scw.math_core.matrix import Matrix
from scw.math_core.vector import Vector


def solve(matrix: Matrix, rhs: Vector) -> Vector:
    """Solve ``A x = b`` for ``x`` using a stable factorization."""
    if not isinstance(matrix, Matrix):
        raise TypeError("solve expects a Matrix")
    if not isinstance(rhs, Vector):
        raise TypeError("solve expects a Vector right-hand side")
    if matrix.rows != matrix.columns:
        raise ValueError("solve requires a square matrix")
    if matrix.rows != rhs.dimension:
        raise ValueError(
            f"matrix is {matrix.rows}x{matrix.columns} but vector has "
            f"{rhs.dimension} components"
        )
    x = scipy.linalg.solve(matrix.data, rhs.data)
    return Vector(x)


def inverse(matrix: Matrix) -> Matrix:
    """Return the inverse of a square matrix."""
    if not isinstance(matrix, Matrix):
        raise TypeError("inverse expects a Matrix")
    if matrix.rows != matrix.columns:
        raise ValueError("inverse requires a square matrix")
    return Matrix(scipy.linalg.inv(matrix.data))


def det(matrix: Matrix) -> float:
    """Return the determinant of a square matrix."""
    if not isinstance(matrix, Matrix):
        raise TypeError("det expects a Matrix")
    if matrix.rows != matrix.columns:
        raise ValueError("det requires a square matrix")
    return float(np.linalg.det(matrix.data))
