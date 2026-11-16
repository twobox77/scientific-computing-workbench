"""Guarded import of the optional Matplotlib backend.

Matplotlib is an *optional* dependency: the mathematical core must work without
it, and the domain layer must never import it.  This module is the only place in
:mod:`scw.visualization` that touches Matplotlib, and it fails with an
actionable message when the ``visualization`` extra is not installed.
"""

from __future__ import annotations

try:  # pragma: no cover - exercised only when the extra is absent
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from mpl_toolkits.mplot3d.axes3d import Axes3D
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "scw.visualization requires the optional 'visualization' extra; install "
        "it with `uv sync --extra visualization` (or "
        "`pip install 'scw[visualization]'`)."
    ) from exc

__all__ = ["Axes", "Axes3D", "Figure", "matplotlib", "plt"]
