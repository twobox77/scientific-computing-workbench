"""SCW — Scientific Computing Workbench.

Public entry point. The stable public surface for the first release is
:mod:`scw.math_core`; import domain objects from there.
"""

from __future__ import annotations

from scw.math_core import Covector, LinearMap, Matrix, Vector, VectorSpace

__version__ = "0.1.0"

__all__ = [
    "Covector",
    "LinearMap",
    "Matrix",
    "Vector",
    "VectorSpace",
    "__version__",
]
