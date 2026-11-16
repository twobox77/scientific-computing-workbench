"""Mathematical domain core.

Semantic, typed objects for finite-dimensional real linear algebra.  This
layer depends only on NumPy and the SCW configuration/exceptions; it must not
import the CLI, Jupyter, plotting, or file-system code.
"""

from __future__ import annotations

from scw.math_core.covector import Covector
from scw.math_core.linear_map import LinearMap
from scw.math_core.matrix import Matrix
from scw.math_core.spaces import VectorSpace
from scw.math_core.vector import Vector

__all__ = ["Covector", "LinearMap", "Matrix", "Vector", "VectorSpace"]
