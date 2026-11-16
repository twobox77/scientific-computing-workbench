"""Linear-algebra services backed by SciPy.

Prefer :func:`solve` over forming an explicit inverse when solving a linear
system; :func:`inverse` exists for the cases where the inverse itself is the
object of interest.  For over- or under-determined systems use :func:`lstsq`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import scipy.linalg

from scw.exceptions import DimensionError, ShapeError
from scw.math_core.matrix import Matrix
from scw.math_core.vector import Vector


@dataclass(frozen=True)
class LeastSquaresResult:
    """The minimum-norm least-squares solution of ``A x ~ b``.

    ``residuals`` holds the squared residual norm per column (empty when the
    system is exactly determined or under-determined).
    """

    solution: Vector
    residuals: np.ndarray
    rank: int
    singular_values: Vector

    @property
    def residual_norm(self) -> float:
        """Euclidean norm of the residual ``A x - b`` (0.0 if underdetermined)."""
        if self.residuals.size == 0:
            return 0.0
        return float(np.sqrt(np.sum(self.residuals)))


def solve(matrix: Matrix, rhs: Vector) -> Vector:
    """Solve ``A x = b`` for ``x`` using a stable factorization."""
    if not isinstance(matrix, Matrix):
        raise TypeError("solve expects a Matrix")
    if not isinstance(rhs, Vector):
        raise TypeError("solve expects a Vector right-hand side")
    if matrix.rows != matrix.columns:
        raise ShapeError("solve requires a square matrix")
    if matrix.rows != rhs.dimension:
        raise DimensionError(
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
        raise ShapeError("inverse requires a square matrix")
    return Matrix(scipy.linalg.inv(matrix.data))


def det(matrix: Matrix) -> float:
    """Return the determinant of a square matrix."""
    if not isinstance(matrix, Matrix):
        raise TypeError("det expects a Matrix")
    if matrix.rows != matrix.columns:
        raise ShapeError("det requires a square matrix")
    return float(np.linalg.det(matrix.data))


def lstsq(matrix: Matrix, rhs: Vector) -> LeastSquaresResult:
    """Solve ``A x ~ b`` in the least-squares sense (minimum-norm solution).

    Works for over- and under-determined systems.  ``A`` has ``m`` rows and
    ``n`` columns; ``b`` must have ``m`` components.  The returned
    :class:`LeastSquaresResult` carries the solution, the rank and the
    singular values of ``A``.
    """
    if not isinstance(matrix, Matrix):
        raise TypeError("lstsq expects a Matrix")
    if not isinstance(rhs, Vector):
        raise TypeError("lstsq expects a Vector right-hand side")
    if matrix.rows != rhs.dimension:
        raise DimensionError(
            f"matrix is {matrix.rows}x{matrix.columns} but vector has "
            f"{rhs.dimension} components"
        )
    x, residuals, rank, singular_values = scipy.linalg.lstsq(matrix.data, rhs.data)
    return LeastSquaresResult(
        solution=Vector(x),
        residuals=np.asarray(residuals, dtype=float),
        rank=int(rank),
        singular_values=Vector(singular_values),
    )
