# Visualization

Plotting lives in `scw.visualization`, an **optional adapter** over
[Matplotlib](https://matplotlib.org/). The mathematical core never imports
Matplotlib and never returns a figure: domain objects stay pure data, and this
adapter *reads* them to build artists.

Install the extra:

```bash
uv sync --extra visualization      # or: pip install 'scw[visualization]'
```

Importing `scw.visualization` without the extra raises an actionable
`ImportError`.

## Headless use

Every function returns the Matplotlib `Axes` it drew on (or a `(Figure, Axes)`
pair from `new_figure`), so you keep full control of styling and saving. In a
non-interactive environment pick the `Agg` backend *before* importing `pyplot`:

```python
import matplotlib
matplotlib.use("Agg")

from scw.math_core import Vector
from scw.visualization import new_figure, plot_vector

fig, ax = new_figure(figsize=(4, 4))
plot_vector(Vector([2.0, 1.0]), ax=ax, label="v")
ax.set_aspect("equal")
fig.savefig("vector.png", dpi=120)
```

Passing an existing `ax` lets several plots share one axes.

## 2D helpers

| Function | Draws |
|---|---|
| `plot_vector(v)` | one 2D vector as an arrow |
| `plot_vectors([v, ...])` | several 2D vectors (per-vector `colors`/`labels`) |
| `plot_function(f, x_range)` | the curve `y = f(x)` sampled over `x_range` |
| `plot_vector_field(field, x_range, y_range)` | the planar field `(u, v) = field(x, y)` on a grid |
| `plot_matrix(m)` | a matrix as a heat map (optional colorbar and cell annotations) |
| `plot_ode_solution(sol)` | an `ODESolution` component by component |

## 3D helpers

| Function | Draws |
|---|---|
| `new_3d_figure()` | a figure with a 3D axes |
| `plot_vectors_3d([v, ...])` | 3D vectors as arrows |
| `plot_surface(f, x_range, y_range)` | the surface `z = f(x, y)` |

```python
import numpy as np
from scw.visualization import new_3d_figure, plot_surface

fig, ax = new_3d_figure()
plot_surface(lambda x, y: np.sin(x) * np.cos(y), (-3.0, 3.0), (-3.0, 3.0), ax=ax)
```

## Vector fields

`plot_vector_field` samples `field(x, y)` on a `samples x samples` grid
(`samples=20` by default). With `normalize=True` each arrow is scaled to unit
length, which makes the *direction* of a field with widely varying magnitude
readable. `plot_surface` and `plot_function` take a `samples` argument too.

## Errors

The adapter validates its inputs and raises the usual SCW exceptions:

- `TypeError` — a non-`Vector`/`Matrix`, or a non-callable field;
- `DimensionError` — a vector of the wrong dimension, mismatched vector
  dimensions, or a field returning an unexpected shape;
- `NumericalError` — an invalid range (`low >= high`, non-finite) or too few
  samples.

See the runnable [example](https://github.com/twobox77/scientific-computing-workbench/blob/main/examples/08_visualization.py)
for a full tour.
