# Gallery

Every figure below is produced by the SCW plotting adapter
(`scw.visualization`) from ordinary domain objects (`Vector`, `Matrix`,
`ODESolution`, `Manifold`).  They are regenerated deterministically by

```bash
uv sync --extra visualization
uv run python scripts/build_gallery.py
```

which writes the PNG files into `docs/assets/gallery/`.

## Vectors

![Vectors drawn as arrows](assets/gallery/vectors.png)

From `examples/08_visualization.py`: `plot_vector` / `plot_vectors`.

## Scalar functions

![sin(x) and cos(x) over one period](assets/gallery/function.png)

`plot_function` samples a callable over an interval.

## Vector field

![The rotation field (-y, x)](assets/gallery/vector_field.png)

`plot_vector_field` draws a planar field on a grid; pass `normalize=True` when
the magnitude varies widely.

## Matrix heat map

![A 3x3 matrix as a heat map](assets/gallery/matrix.png)

`plot_matrix` renders a `Matrix`; `annotate=True` labels each cell.

## ODE solution

![Exponential decay from the solver](assets/gallery/ode.png)

`plot_ode_solution` plots an `ODESolution` straight from `scw.numerical`.

## 3D surface

![z = sin(x) cos(y)](assets/gallery/surface.png)

`plot_surface` draws `z = f(x, y)` on a 3D axes from `new_3d_figure`.

## Sphere tangent basis (0.6)

![Tangent basis on the round 2-sphere](assets/gallery/sphere_tangent.png)

The milestone 0.6 figure: a point on the round sphere with its coordinate
tangent basis `e_theta`, `e_phi`.  The metric `g = diag(r^2, r^2 sin^2 theta)`
gives `|e_theta| = r` and `|e_phi| = r sin(theta)`; see
[Manifolds](mathematics/manifolds.md).  Also available in the interactive
notebook `notebooks/03_manifolds_interactive.ipynb`.
