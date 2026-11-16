"""Matplotlib plotting adapters for SCW domain objects.

Every function returns a Matplotlib :class:`~matplotlib.axes.Axes` (or a
``(Figure, Axes)`` pair from :func:`new_figure`) so the caller keeps full
control over styling and saving.  The domain objects themselves never know
about plotting: this module *reads* their ``.data`` and turns it into artists.

Importing this package requires the optional ``visualization`` extra
(``uv sync --extra visualization``).  In a headless environment select a
non-interactive backend before importing, e.g.::

    import matplotlib
    matplotlib.use("Agg")

    from scw.visualization import plot_vector_field

All functions accept an existing ``ax`` so several plots can share one axes;
when ``ax`` is omitted a new figure and axes are created and returned.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import TYPE_CHECKING, Any, cast

import numpy as np

from scw.config import DEFAULT_DTYPE
from scw.exceptions import DimensionError, NumericalError
from scw.math_core import Matrix, Vector
from scw.visualization._backend import Axes, Axes3D, Figure, plt

if TYPE_CHECKING:  # pragma: no cover - typing only
    from scw.numerical.ode import ODESolution

#: A scalar field ``f(x) -> y`` accepting and returning NumPy arrays.
ScalarField = Callable[[np.ndarray], np.ndarray]
#: A planar vector field ``field(x, y) -> (u, v)`` over arrays.
PlanarField = Callable[[np.ndarray, np.ndarray], tuple[np.ndarray, np.ndarray]]


def new_figure(
    *, figsize: tuple[float, float] | None = None, projection: str | None = None
) -> tuple[Figure, Axes]:
    """Create a new figure and axes (``projection="3d"`` for a 3D axes)."""
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection=projection)
    return fig, ax


def new_3d_figure(
    *, figsize: tuple[float, float] | None = None
) -> tuple[Figure, Axes3D]:
    """Create a new figure and a 3D axes."""
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")
    return fig, cast(Axes3D, ax)


def _require_vector(obj: Any, name: str) -> Vector:
    if not isinstance(obj, Vector):
        raise TypeError(f"{name} expects a Vector")
    return obj


def _require_matrix(obj: Any, name: str) -> Matrix:
    if not isinstance(obj, Matrix):
        raise TypeError(f"{name} expects a Matrix")
    return obj


def _resolve_ax(ax: Axes | None, *, projection: str | None = None) -> Axes:
    if ax is None:
        _, ax = new_figure(projection=projection)
    return ax


def _resolve_3d_ax(ax: Axes3D | None) -> Axes3D:
    if ax is None:
        _, ax = new_3d_figure()
    return ax


def _vector_components(vectors: Iterable[Vector], name: str) -> np.ndarray:
    items = [_require_vector(v, name) for v in vectors]
    if not items:
        raise DimensionError(f"{name} needs at least one vector")
    dimensions = {v.dimension for v in items}
    if len(dimensions) != 1:
        raise DimensionError(f"{name} vectors must all have the same dimension")
    return np.asarray([v.data for v in items], dtype=DEFAULT_DTYPE)


def plot_vector(
    vector: Vector,
    *,
    ax: Axes | None = None,
    origin: Sequence[float] = (0.0, 0.0),
    scale: float = 1.0,
    color: Any = None,
    label: str | None = None,
    **quiver_kwargs: Any,
) -> Axes:
    """Draw a 2D vector as an arrow from ``origin`` (a 2-component sequence)."""
    return plot_vectors(
        [vector],
        ax=ax,
        origins=[origin],
        scale=scale,
        colors=[color] if color is not None else None,
        labels=[label] if label is not None else None,
        **quiver_kwargs,
    )


def plot_vectors(
    vectors: Iterable[Vector],
    *,
    ax: Axes | None = None,
    origins: Sequence[Sequence[float]] | None = None,
    scale: float = 1.0,
    colors: Sequence[Any] | None = None,
    labels: Sequence[str | None] | None = None,
    **quiver_kwargs: Any,
) -> Axes:
    """Draw several 2D vectors as arrows (all must have dimension 2).

    ``origins`` is an optional list of 2-component base points, one per vector
    (default: the origin).  ``colors`` and ``labels`` are forwarded per vector
    by drawing each arrow separately, so a legend can name them.
    """
    ax = _resolve_ax(ax)
    data = _vector_components(vectors, "plot_vectors")
    if data.shape[1] != 2:
        raise DimensionError(
            f"plot_vectors expects 2D vectors, got dimension {data.shape[1]}"
        )
    if origins is None:
        base = np.zeros_like(data)
    else:
        base = np.asarray(origins, dtype=DEFAULT_DTYPE)
        if base.shape != data.shape:
            raise DimensionError(
                f"origins must have shape {data.shape}, got {base.shape}"
            )
    if colors is None and labels is None:
        ax.quiver(
            base[:, 0],
            base[:, 1],
            data[:, 0],
            data[:, 1],
            angles="xy",
            scale_units="xy",
            scale=1.0 / scale,
            **quiver_kwargs,
        )
        return ax
    # complexity: per-vector styling is metadata, not element-wise math
    for index in range(data.shape[0]):
        color = None if colors is None else colors[index]
        label = None if labels is None else labels[index]
        ax.quiver(
            base[index, 0],
            base[index, 1],
            data[index, 0],
            data[index, 1],
            angles="xy",
            scale_units="xy",
            scale=1.0 / scale,
            color=color,
            label=label,
            **quiver_kwargs,
        )
    if labels is not None:
        ax.legend()
    return ax


def plot_function(
    f: ScalarField,
    x_range: tuple[float, float],
    *,
    ax: Axes | None = None,
    samples: int = 256,
    label: str | None = None,
    **plot_kwargs: Any,
) -> Axes:
    """Plot ``y = f(x)`` over ``x_range`` by sampling ``samples`` points."""
    if not callable(f):
        raise TypeError("plot_function expects a callable")
    x0, x1 = _validate_range(x_range, "x_range")
    if samples < 2:
        raise NumericalError("samples must be at least 2")
    ax = _resolve_ax(ax)
    xs = np.linspace(x0, x1, samples, dtype=DEFAULT_DTYPE)
    ys = np.asarray(f(xs), dtype=DEFAULT_DTYPE)
    if ys.shape != xs.shape:
        raise DimensionError(f"f(x) returned shape {ys.shape}, expected {xs.shape}")
    ax.plot(xs, ys, label=label, **plot_kwargs)
    if label is not None:
        ax.legend()
    return ax


def plot_vector_field(
    field: PlanarField,
    x_range: tuple[float, float],
    y_range: tuple[float, float],
    *,
    ax: Axes | None = None,
    samples: int = 20,
    normalize: bool = False,
    **quiver_kwargs: Any,
) -> Axes:
    """Draw the planar vector field ``(u, v) = field(x, y)`` on a grid.

    ``samples`` is the number of grid points along each axis; ``normalize=True``
    draws unit-length arrows so the field's direction is clearer where its
    magnitude varies widely.
    """
    if not callable(field):
        raise TypeError("plot_vector_field expects a callable")
    x0, x1 = _validate_range(x_range, "x_range")
    y0, y1 = _validate_range(y_range, "y_range")
    if samples < 2:
        raise NumericalError("samples must be at least 2")
    ax = _resolve_ax(ax)
    xs = np.linspace(x0, x1, samples, dtype=DEFAULT_DTYPE)
    ys = np.linspace(y0, y1, samples, dtype=DEFAULT_DTYPE)
    grid_x, grid_y = np.meshgrid(xs, ys)
    u, v = field(grid_x, grid_y)
    u = np.asarray(u, dtype=DEFAULT_DTYPE)
    v = np.asarray(v, dtype=DEFAULT_DTYPE)
    if u.shape != grid_x.shape or v.shape != grid_x.shape:
        raise DimensionError(
            f"field must return arrays of shape {grid_x.shape}, "
            f"got {u.shape} and {v.shape}"
        )
    if normalize:
        magnitude = np.hypot(u, v)
        magnitude[magnitude == 0.0] = 1.0
        u, v = u / magnitude, v / magnitude
    ax.quiver(grid_x, grid_y, u, v, **quiver_kwargs)
    return ax


def plot_matrix(
    matrix: Matrix,
    *,
    ax: Axes | None = None,
    cmap: str = "viridis",
    colorbar: bool = True,
    annotate: bool = False,
    **imshow_kwargs: Any,
) -> Axes:
    """Render a matrix as a heat map (rows downward, columns rightward)."""
    ax = _resolve_ax(ax)
    data = _require_matrix(matrix, "plot_matrix").data
    image = ax.imshow(data, cmap=cmap, **imshow_kwargs)
    if colorbar:
        ax.figure.colorbar(image, ax=ax)
    if annotate:
        # complexity: labelling each cell is display work, not element-wise math
        for row in range(data.shape[0]):
            for column in range(data.shape[1]):  # complexity: see note above
                ax.text(
                    column,
                    row,
                    f"{data[row, column]:.3g}",
                    ha="center",
                    va="center",
                    color="w",
                )
    return ax


def plot_ode_solution(
    solution: ODESolution,
    *,
    ax: Axes | None = None,
    components: Sequence[int] | None = None,
    labels: Sequence[str] | None = None,
    **plot_kwargs: Any,
) -> Axes:
    """Plot an :class:`~scw.numerical.ODESolution` component by component.

    ``components`` selects which state components to draw (default: all of
    them); each is plotted against the time grid ``solution.t``.
    """
    if not hasattr(solution, "t") or not hasattr(solution, "y"):
        raise TypeError("plot_ode_solution expects an ODESolution")
    ax = _resolve_ax(ax)
    times = np.asarray(solution.t)
    states = np.asarray(solution.y)
    if components is None:
        selected = list(range(states.shape[1]))
    else:
        selected = list(components)
        # complexity: validate a small list of component indices (metadata)
        for index in selected:
            if not -states.shape[1] <= index < states.shape[1]:
                raise DimensionError(
                    f"component {index} out of range for dimension {states.shape[1]}"
                )
    # complexity: one line per selected component (metadata), not per element
    for position, index in enumerate(selected):
        label = None if labels is None else labels[position]
        ax.plot(times, states[:, index], label=label, **plot_kwargs)
    if labels is not None:
        ax.legend()
    ax.set_xlabel("t")
    return ax


def plot_vectors_3d(
    vectors: Iterable[Vector],
    *,
    ax: Axes3D | None = None,
    origins: Sequence[Sequence[float]] | None = None,
    colors: Sequence[Any] | None = None,
    labels: Sequence[str | None] | None = None,
    **quiver_kwargs: Any,
) -> Axes3D:
    """Draw several 3D vectors as arrows (all must have dimension 3)."""
    ax = _resolve_3d_ax(ax)
    data = _vector_components(vectors, "plot_vectors_3d")
    if data.shape[1] != 3:
        raise DimensionError(
            f"plot_vectors_3d expects 3D vectors, got dimension {data.shape[1]}"
        )
    if origins is None:
        base = np.zeros_like(data)
    else:
        base = np.asarray(origins, dtype=DEFAULT_DTYPE)
        if base.shape != data.shape:
            raise DimensionError(
                f"origins must have shape {data.shape}, got {base.shape}"
            )
    if colors is None and labels is None:
        ax.quiver(
            base[:, 0],
            base[:, 1],
            base[:, 2],
            data[:, 0],
            data[:, 1],
            data[:, 2],
            **quiver_kwargs,
        )
        return ax
    # complexity: per-vector styling is metadata, not element-wise math
    for index in range(data.shape[0]):
        color = None if colors is None else colors[index]
        label = None if labels is None else labels[index]
        ax.quiver(
            base[index, 0],
            base[index, 1],
            base[index, 2],
            data[index, 0],
            data[index, 1],
            data[index, 2],
            color=color,
            label=label,
            **quiver_kwargs,
        )
    if labels is not None:
        ax.legend()
    return ax


def plot_surface(
    f: Callable[[np.ndarray, np.ndarray], np.ndarray],
    x_range: tuple[float, float],
    y_range: tuple[float, float],
    *,
    ax: Axes3D | None = None,
    samples: int = 40,
    cmap: str = "viridis",
    **plot_surface_kwargs: Any,
) -> Axes3D:
    """Draw the surface ``z = f(x, y)`` over the given ranges (3D axes)."""
    if not callable(f):
        raise TypeError("plot_surface expects a callable")
    x0, x1 = _validate_range(x_range, "x_range")
    y0, y1 = _validate_range(y_range, "y_range")
    if samples < 2:
        raise NumericalError("samples must be at least 2")
    ax = _resolve_3d_ax(ax)
    xs = np.linspace(x0, x1, samples, dtype=DEFAULT_DTYPE)
    ys = np.linspace(y0, y1, samples, dtype=DEFAULT_DTYPE)
    grid_x, grid_y = np.meshgrid(xs, ys)
    grid_z = np.asarray(f(grid_x, grid_y), dtype=DEFAULT_DTYPE)
    if grid_z.shape != grid_x.shape:
        raise DimensionError(
            f"f(x, y) must return shape {grid_x.shape}, got {grid_z.shape}"
        )
    ax.plot_surface(grid_x, grid_y, grid_z, cmap=cmap, **plot_surface_kwargs)
    return ax


def _validate_range(value: Any, name: str) -> tuple[float, float]:
    try:
        low, high = value
    except (TypeError, ValueError) as exc:
        raise NumericalError(f"{name} must be a (low, high) pair") from exc
    low = float(low)
    high = float(high)
    if not (np.isfinite(low) and np.isfinite(high)):
        raise NumericalError(f"{name} bounds must be finite")
    if low >= high:
        raise NumericalError(f"{name} must satisfy low < high")
    return low, high
