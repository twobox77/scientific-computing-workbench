"""Matrix factorizations backed by SciPy.

Each routine validates its input, delegates the arithmetic to SciPy, and
returns a small immutable result object holding :class:`~scw.math_core.Matrix`
factors.  Every result exposes ``reconstruct`` so a factorization can be
checked by rebuilding the original matrix::

    lu(a).reconstruct()      # == a
    qr(a).reconstruct()      # == a
    svd(a).reconstruct()     # == a
    cholesky(a)              # == a  (L L^T)
    eigh(a).reconstruct()    # == a  (symmetric input)
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import scipy.linalg

from scw.config import DEFAULT_ATOL, DEFAULT_RTOL
from scw.exceptions import NumericalError, ShapeError
from scw.math_core.matrix import Matrix
from scw.math_core.vector import Vector


def _as_matrix(a: Matrix, name: str) -> Matrix:
    if not isinstance(a, Matrix):
        raise TypeError(f"{name} expects a Matrix")
    return a


def _require_square(a: Matrix, op: str) -> None:
    if a.rows != a.columns:
        raise ShapeError(f"{op} requires a square matrix, got shape {a.shape}")


def _translate_lin_alg_error(exc: np.linalg.LinAlgError, op: str) -> NumericalError:
    return NumericalError(f"{op} failed: {exc}")


@dataclass(frozen=True)
class LUResult:
    """The ``P L U`` factorization of a square matrix, ``A = P L U``.

    ``lower`` is unit lower-triangular and ``upper`` is upper-triangular;
    ``p`` is a permutation matrix.
    """

    p: Matrix
    lower: Matrix
    upper: Matrix

    def reconstruct(self) -> Matrix:
        """Rebuild ``A`` from the factors."""
        return self.p @ self.lower @ self.upper


@dataclass(frozen=True)
class QRResult:
    """The ``Q R`` factorization of a matrix, ``A = Q R``.

    ``q`` has orthonormal columns and ``r`` is upper-triangular.
    """

    q: Matrix
    r: Matrix

    def reconstruct(self) -> Matrix:
        """Rebuild ``A`` from the factors."""
        return self.q @ self.r


@dataclass(frozen=True)
class SVDResult:
    """The singular value decomposition, ``A = U diag(s) Vh``.

    ``s`` holds the singular values in descending order.
    """

    u: Matrix
    s: Vector
    vh: Matrix

    def reconstruct(self) -> Matrix:
        """Rebuild ``A`` from the factors."""
        k = self.s.dimension
        return Matrix(self.u.data[:, :k] @ np.diag(self.s.data) @ self.vh.data[:k, :])

    def rank(self, *, atol: float | None = None, rtol: float | None = None) -> int:
        """Numerical rank: the count of singular values above a tolerance."""
        limit = (atol if atol is not None else DEFAULT_ATOL) + (
            rtol if rtol is not None else DEFAULT_RTOL
        ) * float(np.max(self.s.data))
        return int(np.count_nonzero(self.s.data > limit))


@dataclass(frozen=True)
class EighResult:
    """The symmetric eigendecomposition, ``A = V diag(w) V^T``.

    ``eigenvalues`` are in ascending order; the columns of ``eigenvectors`` are
    the matching orthonormal eigenvectors.
    """

    eigenvalues: Vector
    eigenvectors: Matrix

    def reconstruct(self) -> Matrix:
        """Rebuild the symmetric matrix from the factors."""
        v = self.eigenvectors.data
        return Matrix(v @ np.diag(self.eigenvalues.data) @ v.T)


def lu(a: Matrix) -> LUResult:
    """Factor a square matrix as ``A = P L U``."""
    _as_matrix(a, "lu")
    _require_square(a, "lu")
    p, lower, upper = scipy.linalg.lu(a.data)
    return LUResult(Matrix(p), Matrix(lower), Matrix(upper))


def qr(a: Matrix, *, mode: str = "full") -> QRResult:
    """Factor a matrix as ``A = Q R``.

    ``mode`` is ``"full"`` (``q`` is ``m x m``) or ``"economic"`` (``q`` is
    ``m x n`` with ``n = min(m, n)``).
    """
    _as_matrix(a, "qr")
    if mode not in {"full", "economic"}:
        raise NumericalError("qr mode must be 'full' or 'economic'")
    q, r = scipy.linalg.qr(a.data, mode=mode)
    return QRResult(Matrix(q), Matrix(r))


def svd(a: Matrix, *, full_matrices: bool = True) -> SVDResult:
    """Return the singular value decomposition ``A = U diag(s) Vh``."""
    _as_matrix(a, "svd")
    u, s, vh = scipy.linalg.svd(a.data, full_matrices=full_matrices)
    return SVDResult(Matrix(u), Vector(s), Matrix(vh))


def cholesky(a: Matrix, *, lower: bool = True) -> Matrix:
    """Return the Cholesky factor ``L`` of a symmetric positive-definite ``A``.

    With ``lower=True`` (the default) ``A = L L^T``; otherwise ``A = R^T R``.
    """
    _as_matrix(a, "cholesky")
    _require_square(a, "cholesky")
    if not np.allclose(a.data, a.data.T, rtol=DEFAULT_RTOL, atol=DEFAULT_ATOL):
        raise NumericalError("cholesky requires a symmetric matrix")
    try:
        factor = scipy.linalg.cholesky(a.data, lower=lower)
    except np.linalg.LinAlgError as exc:
        raise _translate_lin_alg_error(exc, "cholesky") from exc
    return Matrix(factor)


def eigh(a: Matrix) -> EighResult:
    """Eigendecompose a symmetric matrix, returning real eigenvalues.

    Eigenvalues are ascending and the eigenvectors are orthonormal.
    """
    _as_matrix(a, "eigh")
    _require_square(a, "eigh")
    if not np.allclose(a.data, a.data.T, rtol=DEFAULT_RTOL, atol=DEFAULT_ATOL):
        raise NumericalError("eigh requires a symmetric matrix")
    try:
        w, v = scipy.linalg.eigh(a.data)
    except np.linalg.LinAlgError as exc:
        raise _translate_lin_alg_error(exc, "eigh") from exc
    return EighResult(Vector(w), Matrix(v))
