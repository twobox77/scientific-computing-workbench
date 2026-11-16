"""Guarded import of the optional SymPy backend.

SymPy is an *optional* dependency: the mathematical core must work without it.
Importing :mod:`scw.symbolic` is therefore the only place that pulls SymPy in,
and it fails with an actionable message when the extra is not installed.
"""

from __future__ import annotations

try:  # pragma: no cover - exercised only when the extra is absent
    import sympy
    from sympy import Matrix as SympyMatrix
    from sympy import Symbol, symbols
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "scw.symbolic requires the optional 'symbolic' extra; install it with "
        "`uv sync --extra symbolic` (or `pip install 'scw[symbolic]'`)."
    ) from exc

__all__ = ["Symbol", "SympyMatrix", "sympy", "symbols"]
