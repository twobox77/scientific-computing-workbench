"""Unit tests for the optional Matplotlib adapter (:mod:`scw.visualization`).

The whole module is skipped when the optional ``visualization`` extra is not
installed, so the core test suite still passes on a minimal install.  A
non-interactive backend is selected before importing ``pyplot`` so the tests
run headless (no display, no GUI windows).
"""

from __future__ import annotations

import numpy as np
import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from mpl_toolkits.mplot3d.axes3d import Axes3D  # noqa: E402

from scw.exceptions import DimensionError, NumericalError  # noqa: E402
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
    plot_vectors,
    plot_vectors_3d,
)


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")


def test_new_figure_returns_figure_and_axes() -> None:
    fig, ax = new_figure()
    assert isinstance(ax, Axes)
    assert ax.figure is fig


def test_new_3d_figure_returns_3d_axes() -> None:
    fig, ax = new_3d_figure()
    assert isinstance(ax, Axes3D)
    assert ax.figure is fig


def test_plot_vector_draws_one_arrow() -> None:
    ax = plot_vector(Vector([1.0, 2.0]))
    assert len(ax.collections) == 1


def test_plot_vector_uses_supplied_axes() -> None:
    _, ax = new_figure()
    returned = plot_vector(Vector([1.0, 0.0]), ax=ax, label="v")
    assert returned is ax
    assert ax.get_legend() is not None


def test_plot_vector_rejects_wrong_dimension() -> None:
    with pytest.raises(DimensionError):
        plot_vector(Vector([1.0, 2.0, 3.0]))


def test_plot_vector_rejects_non_vector() -> None:
    with pytest.raises(TypeError):
        plot_vector([1.0, 2.0])  # type: ignore[arg-type]


def test_plot_vectors_colors_and_labels() -> None:
    vectors = [Vector([1.0, 0.0]), Vector([0.0, 1.0])]
    ax = plot_vectors(vectors, colors=["r", "g"], labels=["e1", "e2"])
    assert len(ax.collections) == 2
    assert ax.get_legend() is not None


def test_plot_vectors_single_quiver_without_styling() -> None:
    vectors = [Vector([1.0, 0.0]), Vector([0.0, 1.0])]
    ax = plot_vectors(vectors)
    assert len(ax.collections) == 1


def test_plot_vectors_origins() -> None:
    vectors = [Vector([1.0, 0.0])]
    ax = plot_vectors(vectors, origins=[[2.0, 3.0]])
    assert len(ax.collections) == 1


def test_plot_vectors_rejects_bad_origins_shape() -> None:
    with pytest.raises(DimensionError):
        plot_vectors([Vector([1.0, 0.0])], origins=[[1.0, 2.0, 3.0]])


def test_plot_vectors_rejects_mixed_dimensions() -> None:
    with pytest.raises(DimensionError):
        plot_vectors([Vector([1.0, 0.0]), Vector([1.0, 0.0, 0.0])])


def test_plot_vectors_rejects_empty() -> None:
    with pytest.raises(DimensionError):
        plot_vectors([])


def test_plot_function_samples_and_labels() -> None:
    ax = plot_function(np.sin, (0.0, float(np.pi)), samples=32, label="sin")
    line = ax.lines[0]
    assert line.get_label() == "sin"
    xs = line.get_xdata()
    assert xs[0] == pytest.approx(0.0)
    assert xs[-1] == pytest.approx(np.pi)
    assert line.get_ydata()[-1] == pytest.approx(np.sin(np.pi), abs=1e-9)


def test_plot_function_rejects_non_callable() -> None:
    with pytest.raises(TypeError):
        plot_function(3, (0.0, 1.0))  # type: ignore[arg-type]


def test_plot_function_rejects_bad_range() -> None:
    with pytest.raises(NumericalError):
        plot_function(np.sin, (1.0, 1.0))
    with pytest.raises(NumericalError):
        plot_function(np.sin, (0.0,))  # type: ignore[arg-type]


def test_plot_function_rejects_too_few_samples() -> None:
    with pytest.raises(NumericalError):
        plot_function(np.sin, (0.0, 1.0), samples=1)


def test_plot_function_rejects_wrong_output_shape() -> None:
    with pytest.raises(DimensionError):
        plot_function(lambda x: np.zeros(x.shape + (2,)), (0.0, 1.0))


def test_plot_vector_field_draws_arrows() -> None:
    ax = plot_vector_field(lambda x, y: (-y, x), (-1.0, 1.0), (-1.0, 1.0), samples=8)
    assert len(ax.collections) == 1


def test_plot_vector_field_normalize() -> None:
    ax = plot_vector_field(
        lambda x, y: (x * 100.0, y * 100.0), (-1.0, 1.0), (-1.0, 1.0), normalize=True
    )
    quiver = ax.collections[0]
    u = np.asarray(quiver.U)
    v = np.asarray(quiver.V)
    assert np.all(np.hypot(u, v) <= 1.0 + 1e-9)


def test_plot_vector_field_rejects_non_callable() -> None:
    with pytest.raises(TypeError):
        plot_vector_field(1, (0.0, 1.0), (0.0, 1.0))  # type: ignore[arg-type]


def test_plot_vector_field_rejects_bad_shape() -> None:
    with pytest.raises(DimensionError):
        plot_vector_field(
            lambda x, y: (np.zeros(3), np.zeros(3)), (-1.0, 1.0), (-1.0, 1.0), samples=8
        )


def test_plot_vector_field_rejects_bad_range() -> None:
    with pytest.raises(NumericalError):
        plot_vector_field(lambda x, y: (x, y), (1.0, 0.0), (0.0, 1.0))
    with pytest.raises(NumericalError):
        plot_vector_field(lambda x, y: (x, y), (0.0, 1.0), (0.0, 1.0), samples=1)


def test_plot_matrix_heatmap_and_colorbar() -> None:
    matrix = Matrix([[1.0, 2.0], [3.0, 4.0]])
    fig, ax = new_figure()
    plot_matrix(matrix, ax=ax)
    assert len(ax.images) == 1
    # a colorbar adds a second axes to the figure
    assert len(fig.axes) == 2
    np.testing.assert_allclose(ax.images[0].get_array(), matrix.data)


def test_plot_matrix_without_colorbar_and_annotated() -> None:
    matrix = Matrix([[1.0, 2.0], [3.0, 4.0]])
    fig, ax = new_figure()
    plot_matrix(matrix, ax=ax, colorbar=False, annotate=True)
    assert len(fig.axes) == 1
    assert len(ax.texts) == 4


def test_plot_matrix_rejects_non_matrix() -> None:
    with pytest.raises(TypeError):
        plot_matrix([[1.0, 2.0]])  # type: ignore[arg-type]


def _decay(t: float, y: Vector) -> Vector:
    return Vector(-1.0 * y.data)


def test_plot_ode_solution_all_components() -> None:
    solution = solve_ivp(
        _decay, (0.0, 1.0), Vector([1.0, 2.0]), t_eval=np.linspace(0.0, 1.0, 11)
    )
    ax = plot_ode_solution(solution)
    assert len(ax.lines) == 2
    assert ax.get_xlabel() == "t"


def test_plot_ode_solution_selected_component_with_label() -> None:
    solution = solve_ivp(
        _decay, (0.0, 1.0), Vector([1.0, 2.0]), t_eval=np.linspace(0.0, 1.0, 11)
    )
    ax = plot_ode_solution(solution, components=[0], labels=["y0"])
    assert len(ax.lines) == 1
    assert ax.get_legend() is not None
    np.testing.assert_allclose(ax.lines[0].get_ydata(), solution.y[:, 0])


def test_plot_ode_solution_rejects_bad_component() -> None:
    solution = solve_ivp(_decay, (0.0, 1.0), Vector([1.0]))
    with pytest.raises(DimensionError):
        plot_ode_solution(solution, components=[5])


def test_plot_ode_solution_rejects_non_solution() -> None:
    with pytest.raises(TypeError):
        plot_ode_solution(object())  # type: ignore[arg-type]


def test_plot_vectors_3d_draws_arrows() -> None:
    vectors = [Vector([1.0, 0.0, 0.0]), Vector([0.0, 1.0, 1.0])]
    ax = plot_vectors_3d(vectors)
    assert isinstance(ax, Axes3D)
    assert len(ax.collections) == 1


def test_plot_vectors_3d_with_origins_and_labels() -> None:
    vectors = [Vector([1.0, 0.0, 0.0]), Vector([0.0, 1.0, 0.0])]
    ax = plot_vectors_3d(
        vectors, origins=[[1.0, 1.0, 1.0], [0.0, 0.0, 0.0]], labels=["a", "b"]
    )
    assert len(ax.collections) == 2


def test_plot_vectors_3d_rejects_2d() -> None:
    with pytest.raises(DimensionError):
        plot_vectors_3d([Vector([1.0, 2.0])])


def test_plot_vectors_3d_rejects_bad_origins() -> None:
    with pytest.raises(DimensionError):
        plot_vectors_3d([Vector([1.0, 0.0, 0.0])], origins=[[1.0, 2.0]])


def test_plot_surface_draws_surface() -> None:
    ax = plot_surface(lambda x, y: np.sin(x) * np.cos(y), (-1.0, 1.0), (-1.0, 1.0))
    assert isinstance(ax, Axes3D)
    assert len(ax.collections) == 1


def test_plot_surface_rejects_non_callable() -> None:
    with pytest.raises(TypeError):
        plot_surface(0, (0.0, 1.0), (0.0, 1.0))  # type: ignore[arg-type]


def test_plot_surface_rejects_bad_shape() -> None:
    with pytest.raises(DimensionError):
        plot_surface(lambda x, y: np.zeros((3, 3)), (-1.0, 1.0), (-1.0, 1.0))


def test_plot_surface_rejects_bad_range() -> None:
    with pytest.raises(NumericalError):
        plot_surface(lambda x, y: x + y, (1.0, 1.0), (0.0, 1.0))


def test_plot_surface_rejects_too_few_samples() -> None:
    with pytest.raises(NumericalError):
        plot_surface(lambda x, y: x + y, (0.0, 1.0), (0.0, 1.0), samples=1)
