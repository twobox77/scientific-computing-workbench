"""Plotting domain objects with the optional Matplotlib adapter.

Requires the optional ``visualization`` extra::

    uv sync --extra visualization
    uv run python examples/08_visualization.py

Saves PNG files into ``scw_plots/`` (gitignored).  A non-interactive backend
is selected so the example runs headless; drop the ``matplotlib.use("Agg")``
line and call ``plt.show()`` to view the figures interactively instead.
"""

from __future__ import annotations

import pathlib

import matplotlib

matplotlib.use("Agg")

import numpy as np  # noqa: E402

from scw.math_core import Matrix, Vector  # noqa: E402
from scw.numerical import solve_ivp  # noqa: E402
from scw.visualization import (  # noqa: E402
    new_3d_figure,
    new_figure,
    plot_function,
    plot_matrix,
    plot_ode_solution,
    plot_surface,
    plot_vector,
    plot_vector_field,
)


def main() -> None:
    output = pathlib.Path("scw_plots")
    output.mkdir(exist_ok=True)

    # A single vector and a small basis, drawn as arrows.
    fig, ax = new_figure(figsize=(4, 4))
    plot_vector(Vector([2.0, 1.0]), ax=ax, label="v = (2, 1)")
    plot_vector(Vector([1.0, 0.0]), ax=ax, color="gray", label="e1")
    ax.set_aspect("equal")
    ax.set_title("Vectors")
    fig.savefig(output / "scw_vectors.png", dpi=120)
    print(f"wrote {output / 'scw_vectors.png'}")

    # A scalar function sampled over an interval.
    fig, ax = new_figure()
    plot_function(np.sin, (0.0, 2.0 * np.pi), ax=ax, label="sin(x)")
    ax.set_title("Function plot")
    fig.savefig(output / "scw_function.png", dpi=120)
    print(f"wrote {output / 'scw_function.png'}")

    # The rotation field (u, v) = (-y, x), normalised for readability.
    fig, ax = new_figure()
    plot_vector_field(lambda x, y: (-y, x), (-2.0, 2.0), (-2.0, 2.0), ax=ax, samples=16)
    ax.set_title("Vector field (-y, x)")
    fig.savefig(output / "scw_vector_field.png", dpi=120)
    print(f"wrote {output / 'scw_vector_field.png'}")

    # A matrix as a heat map.
    fig, ax = new_figure()
    plot_matrix(Matrix([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]), ax=ax)
    ax.set_title("Matrix heat map")
    fig.savefig(output / "scw_matrix.png", dpi=120)
    print(f"wrote {output / 'scw_matrix.png'}")

    # An ODE solution, plotted straight from the solver result.
    solution = solve_ivp(
        lambda t, y: Vector(-0.5 * y.data),
        (0.0, 6.0),
        Vector([1.0]),
        t_eval=np.linspace(0.0, 6.0, 61),
    )
    fig, ax = new_figure()
    plot_ode_solution(solution, ax=ax, labels=["y(t)"])
    ax.set_title("dy/dt = -0.5 y")
    fig.savefig(output / "scw_ode.png", dpi=120)
    print(f"wrote {output / 'scw_ode.png'}")

    # A 3D surface.
    fig, ax = new_3d_figure()
    plot_surface(lambda x, y: np.sin(x) * np.cos(y), (-3.0, 3.0), (-3.0, 3.0), ax=ax)
    ax.set_title("z = sin(x) cos(y)")
    fig.savefig(output / "scw_surface.png", dpi=120)
    print(f"wrote {output / 'scw_surface.png'}")


if __name__ == "__main__":
    main()
