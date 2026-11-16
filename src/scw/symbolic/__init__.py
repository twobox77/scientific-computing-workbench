"""SymPy adapter (optional; not required by the mathematical core).

Symbolic counterparts of the numeric domain objects.  Importing this package
requires the optional ``symbolic`` extra (``uv sync --extra symbolic``); the
core never depends on it.  The numeric types and the symbolic types convert in
both directions:

    from scw.math_core import Matrix
    from scw.symbolic import SymbolicMatrix, to_symbolic

    SymbolicMatrix([[a, 1], [2, b]])   # symbolic construction
    to_symbolic(Matrix([[1.0, 2.0]]))  # lift a numeric matrix
    sym.to_numeric()                   # collapse back, if free of symbols
"""

from __future__ import annotations

from scw.symbolic.objects import SymbolicMatrix, SymbolicVector, to_symbolic

__all__ = ["SymbolicMatrix", "SymbolicVector", "to_symbolic"]
