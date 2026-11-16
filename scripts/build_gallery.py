"""Render the figure gallery shown in ``docs/gallery.md``.

Run with::

    uv sync --extra visualization
    uv run python scripts/build_gallery.py

Writes deterministic PNG files into ``docs/assets/gallery/`` (committed, so the
documentation site shows them without a plotting dependency at build time).
"""

from __future__ import annotations

import pathlib

import matplotlib

matplotlib.use("Agg")

import numpy as np  # noqa: E402

from scw.manifold import Sphere  # noqa: E402
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
    plot_vectors_3d,
)

OUTPUT = pathlib.Path("docs/assets/gallery")
DPI = 110


def _save(fig: object, name: str) -> None:
    path = OUTPUT / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight")  # type: ignore[attr-defined]
    print(f"wrote {path}")


def gallery_vectors() -> None:
    fig, ax = new_figure(figsize=(4, 4))
    plot_vector(Vector([2.0, 1.0]), ax=ax, label="v = (2, 1)")
    plot_vector(Vector([1.0, 0.0]), ax=ax, color="gray", label="e1")
    plot_vector(Vector([0.0, 1.0]), ax=ax, color="gray", label="e2")
    ax.set_aspect("equal")
    ax.set_title("Vectors")
    _save(fig, "vectors.png")


def gallery_function() -> None:
    fig, ax = new_figure()
    plot_function(np.sin, (0.0, 2.0 * np.pi), ax=ax, label="sin(x)")
    plot_function(np.cos, (0.0, 2.0 * np.pi), ax=ax, label="cos(x)")
    ax.set_title("Scalar functions")
    _save(fig, "function.png")


def gallery_vector_field() -> None:
    fig, ax = new_figure()
    plot_vector_field(lambda x, y: (-y, x), (-2.0, 2.0), (-2.0, 2.0), ax=ax, samples=18)
    ax.set_title("Vector field (-y, x)")
    _save(fig, "vector_field.png")


def gallery_matrix() -> None:
    fig, ax = new_figure()
    plot_matrix(
        Matrix([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]),
        ax=ax,
        annotate=True,
    )
    ax.set_title("Matrix heat map")
    _save(fig, "matrix.png")


def gallery_ode() -> None:
    solution = solve_ivp(
        lambda t, y: Vector(-0.5 * y.data),
        (0.0, 6.0),
        Vector([1.0]),
        t_eval=np.linspace(0.0, 6.0, 61),
    )
    fig, ax = new_figure()
    plot_ode_solution(solution, ax=ax, labels=["y(t)"])
    ax.set_title("dy/dt = -0.5 y")
    _save(fig, "ode.png")


def gallery_surface() -> None:
    fig, ax = new_3d_figure(figsize=(5, 4))
    plot_surface(lambda x, y: np.sin(x) * np.cos(y), (-3.0, 3.0), (-3.0, 3.0), ax=ax)
    ax.set_title("z = sin(x) cos(y)")
    _save(fig, "surface.png")


def gallery_sphere_tangent() -> None:
    """The round 2-sphere with its tangent basis -- the 0.6 figure."""
    radius = 2.0
    theta0, phi0 = np.pi / 3, np.pi / 6
    point = np.array(
        [
            radius * np.sin(theta0) * np.cos(phi0),
            radius * np.sin(theta0) * np.sin(phi0),
            radius * np.cos(theta0),
        ]
    )
    e_theta = np.array(
        [
            radius * np.cos(theta0) * np.cos(phi0),
            radius * np.cos(theta0) * np.sin(phi0),
            -radius * np.sin(theta0),
        ]
    )
    e_phi = np.array(
        [
            -radius * np.sin(theta0) * np.sin(phi0),
            radius * np.sin(theta0) * np.cos(phi0),
            0.0,
        ]
    )
    # Confirm the metric really does give these lengths (r^2 and r^2 sin^2 theta).
    sphere = Sphere(radius=radius)
    metric = sphere.metric((theta0, phi0))
    e_theta_vec = sphere.tangent_vector([1.0, 0.0], point=(theta0, phi0))
    e_phi_vec = sphere.tangent_vector([0.0, 1.0], point=(theta0, phi0))
    assert np.isclose(metric.norm(e_theta_vec), radius)
    assert np.isclose(metric.norm(e_phi_vec), radius * np.sin(theta0))

    fig, ax = new_3d_figure(figsize=(6, 6))
    theta, phi = np.meshgrid(np.linspace(0, np.pi, 80), np.linspace(0, 2 * np.pi, 80))
    ax.plot_surface(
        radius * np.sin(theta) * np.cos(phi),
        radius * np.sin(theta) * np.sin(phi),
        radius * np.cos(theta),
        alpha=0.2,
        color="tab:blue",
        linewidth=0,
    )
    ax.scatter(*point, color="k", s=25, label="p")
    plot_vectors_3d(
        [Vector(e_theta), Vector(e_phi)],
        origins=[point, point],
        colors=["tab:red", "tab:green"],
        labels=["e_theta", "e_phi"],
        ax=ax,
    )
    ax.set_title("S^2 tangent basis, g = diag(r^2, r^2 sin^2 theta)")
    ax.legend(loc="upper right")
    _save(fig, "sphere_tangent.png")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    gallery_vectors()
    gallery_function()
    gallery_vector_field()
    gallery_matrix()
    gallery_ode()
    gallery_surface()
    gallery_sphere_tangent()


if __name__ == "__main__":
    main()
