"""Plotting adapters (optional).

Matplotlib lives behind this adapter; the mathematical core never imports it
and never returns a figure.  Importing this package requires the optional
``visualization`` extra (``uv sync --extra visualization``); in a headless
environment pick a non-interactive backend first::

    import matplotlib
    matplotlib.use("Agg")

    from scw.visualization import plot_vector_field
"""

from __future__ import annotations

from scw.visualization.plots import (
    new_3d_figure,
    new_figure,
    plot_function,
    plot_matrix,
    plot_ode_solution,
    plot_surface,
    plot_vector,
    plot_vector_field,
    plot_vectors,
    plot_vectors_3d,
)

__all__ = [
    "new_3d_figure",
    "new_figure",
    "plot_function",
    "plot_matrix",
    "plot_ode_solution",
    "plot_surface",
    "plot_vector",
    "plot_vector_field",
    "plot_vectors",
    "plot_vectors_3d",
]
