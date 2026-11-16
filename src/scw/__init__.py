"""SCW — Scientific Computing Workbench.

Public entry point. The stable public surface for the first release is
:mod:`scw.math_core`; import domain objects from there.
"""

from __future__ import annotations

from scw.math_core import (
    Basis,
    Covector,
    LinearMap,
    Matrix,
    Tensor,
    Vector,
    VectorSpace,
    einsum,
)

__version__ = "0.5.0"

__all__ = [
    "Basis",
    "Covector",
    "LinearMap",
    "Matrix",
    "Tensor",
    "Vector",
    "VectorSpace",
    "__version__",
    "einsum",
]
