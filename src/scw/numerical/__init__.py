"""Numerical algorithms built on NumPy / SciPy.

This layer accepts the objects defined in :mod:`scw.math_core` but must not
leak its own concerns back into the domain model.
"""

from __future__ import annotations

from scw.numerical.decomposition import (
    EighResult,
    LUResult,
    QRResult,
    SVDResult,
    cholesky,
    eigh,
    lu,
    qr,
    svd,
)
from scw.numerical.linalg import LeastSquaresResult, det, inverse, lstsq, solve
from scw.numerical.ode import METHODS, ODESolution, solve_ivp

__all__ = [
    "METHODS",
    "EighResult",
    "LUResult",
    "LeastSquaresResult",
    "ODESolution",
    "QRResult",
    "SVDResult",
    "cholesky",
    "det",
    "eigh",
    "inverse",
    "lstsq",
    "lu",
    "qr",
    "solve",
    "solve_ivp",
    "svd",
]
