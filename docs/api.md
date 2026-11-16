# Public API

SCW exposes a small, deliberately stable surface. Everything documented here is
importable from the top-level ``scw`` package or from ``scw.math_core`` /
``scw.numerical``.

## Design rules

- **Typed mathematical objects.** A `Vector` is not a raw array; a `Covector`
  is a distinct type with different operations; a `LinearMap` carries its
  domain and codomain explicitly.
- **Explicit failure.** Dimension, shape and finiteness problems raise
  `scw.exceptions.SCWError` subclasses (which also derive from `ValueError`),
  never silent garbage.
- **Defensive copies.** Constructors copy their input; mutating the array you
  passed in never changes an SCW object. Accessors return read-only views.
- **One dtype policy.** Everything is `float64` (`scw.config.DEFAULT_DTYPE`).

## `scw.math_core`

### `VectorSpace`

```python
VectorSpace(3)                 # R^3
VectorSpace(3, name="V")       # a named space; equality includes the name
```

A named space is *not* equal to an unnamed space of the same dimension, so
mixing them raises `DimensionError`. Use names to make units or bases explicit.

### `Vector`

```python
v = Vector([1.0, 2.0, 3.0])
v + w, v - w, 2.0 * v, v / 2.0     # arithmetic
v.dot(w)                            # inner product
v.norm()                            # Euclidean norm (scale-aware)
v.norm(p=1)                         # p-norm
v.is_zero()                         # exact-zero test
v.to_numpy()                        # copy (default) or read-only view
```

`v.data` is a read-only NumPy view. The Euclidean norm is computed with a
scale factor so it neither underflows (all-subnormal inputs) nor overflows
(large inputs).

### `Covector`

```python
alpha = Covector([2.0, 0.0, -1.0])
alpha(v)             # natural pairing alpha(v)  ==  alpha.evaluate(v)
alpha + beta         # covectors add
3.0 * alpha          # scalar scaling
```

A covector pairs with a vector of the same dimension; mismatched dimensions
raise `DimensionError`. `Covector` is intentionally **not** a `Vector`: the two
do not substitute for one another anywhere in the API.

### `Matrix`

```python
m = Matrix([[1.0, 2.0], [3.0, 4.0]])
m.shape, m.rows, m.columns
m + n, m - n, 2.0 * m
m @ n                # matrix product (validates inner dimensions)
m.apply(v)           # ==  m @ v, returns a Vector
m.transpose(), m.T
```

`Matrix @ Matrix` is matrix multiplication; `Matrix * scalar` is scaling.
Using `*` between two matrices raises `TypeError` to avoid the classic
element-wise-vs-matrix-product mistake.

### `LinearMap`

```python
t = LinearMap.from_matrix(Matrix([[1.0, 2.0], [3.0, 4.0]]))
t.domain, t.codomain          # inferred from the matrix shape
t.apply(v)                    # ==  t(v); validates the input dimension
t.compose(s)                  # t . s  (apply s first)
t @ s                         # operator form of compose
```

The representing matrix has `codomain.dimension` rows and
`domain.dimension` columns. Passing explicit `domain=` / `codomain=` spaces
whose dimensions disagree with the matrix raises `DimensionError`.

### `Tensor`

An order-`r` array of components. A scalar has order 0, a vector order 1, a
matrix order 2.

```python
t = Tensor([[1.0, 2.0], [3.0, 4.0]])
t.order, t.shape, t.size       # 2, (2, 2), 4
t + u, t - u, -t, 2.0 * t      # same-shape arithmetic
t.outer(u)                     # tensor product; order adds
t.contract(u)                  # contract t's last axis with u's first
t.contract(u, axis=0, other_axis=1)   # explicit axes
t.trace()                      # contract axis 0 with axis 1
t.trace(axis1=1, axis2=3)      # explicit axes for higher order
Tensor.zeros((2, 3))           # zero tensor of a shape
Tensor.eye(3)                  # order-2 identity
```

`outer` stacks indices (`a.outer(b)` has order `a.order + b.order`). `contract`
requires the two contracted axes to have equal size and keeps the remaining
indices in order (self first, then other); `Matrix @ Matrix` is the order-2
case. `trace` requires two distinct, equally sized axes and a tensor of order
at least 2. `*` between a tensor and another tensor/array raises `TypeError` —
use `outer`.

For readability, `einsum("ij,jk->ik", a, b)` performs the same contraction as
`a.contract(b)` using Einstein-summation subscripts. It validates the
subscript string and operand orders, then delegates to `numpy.einsum`; a
repeated index not appearing in the output is summed, an index appearing only
in the output is broadcast.

### `Basis`

An ordered basis of a vector space, for converting between vectors and
coordinates.

```python
b = Basis([Vector([1.0, 0.0]), Vector([1.0, 1.0])])
b.dimension, len(b)            # 2
b.vectors                      # the basis vectors, in order
b.to_matrix()                  # columns are the basis vectors
b.to_coordinates(v)            # coefficients of v in this basis
b.from_coordinates([1.0, 2.0]) # rebuild the vector
```

Construction validates that the vectors share one space, that there are exactly
`space.dimension` of them, and that they are linearly independent; violations
raise `DimensionError`.

## `scw.numerical`

SciPy-backed linear algebra and ODE integration on `Matrix` / `Vector` inputs.

### Linear systems

```python
from scw.numerical import solve, inverse, det, lstsq

solve(a, b)      # a x = b (square a)
inverse(a)       # a^-1
det(a)           # determinant
lstsq(a, b)      # least-squares solution for any shape
```

`solve`, `inverse` and `det` require square (and, where relevant, consistently
shaped) inputs. `lstsq` works for over- and under-determined systems and returns
a `LeastSquaresResult`:

```python
r = lstsq(a, b)
r.solution         # minimum-norm solution, a Vector
r.rank             # numerical rank of a
r.residual_norm    # ||a x - b||  (0.0 for a consistent/underdetermined system)
r.singular_values  # singular values of a, a Vector
```

### Decompositions

```python
from scw.numerical import lu, qr, svd, cholesky, eigh

lu(a)                 # A = P L U;  factors .p, .lower, .upper
qr(a)                 # A = Q R;    factors .q, .r  (mode="full"|"economic")
svd(a)                # A = U diag(s) Vh;  .u, .s, .vh, plus .rank()
cholesky(a)           # A = L L^T  (symmetric positive-definite), returns L
eigh(a)               # A = V diag(w) V^T;  .eigenvalues, .eigenvectors
```

Each factorization result exposes `reconstruct()`, so a factor can be checked by
rebuilding the original matrix:

```python
import numpy as np
np.allclose(lu(a).reconstruct().data, a.data)   # True
svd(a).rank()                                    # scale-aware numerical rank
```

`cholesky` and `eigh` require a symmetric input and raise `NumericalError`
otherwise (or when the matrix is not positive-definite); `lu` requires a square
matrix. `eigh` returns real eigenvalues in ascending order and orthonormal
eigenvectors.

### ODE integration

```python
from scw.math_core import Vector
from scw.numerical import solve_ivp, METHODS

def rhs(t, y):          # y' = -y
    return -1.0 * y

sol = solve_ivp(rhs, (0.0, 5.0), Vector([1.0]), t_eval=[0.0, 5.0])
sol.t               # time grid
sol.y               # states, shape (n_points, dimension)
sol.final_state     # Vector at the last time
sol.state_at(i)     # Vector at grid point i
sol.success, sol.message, sol.method
```

The right-hand side takes `(t, Vector)` and returns a `Vector` (or any
array-like of the same dimension). `method` must be one of `METHODS` (`RK45`,
`RK23`, `DOP853`, `Radau`, `BDF`, `LSODA`); `rtol`, `atol`, `max_step`,
`first_step` and `t_eval` mirror SciPy. Passing `dense_output=True` enables
`sol.interpolate(t)` for the state at an arbitrary time. A failed integration
raises `ConvergenceError` unless `raise_on_failure=False`.

## Exceptions

```python
from scw.exceptions import (
    SCWError,
    ConvergenceError,
    DimensionError,
    NonFiniteError,
    NumericalError,
    ShapeError,
    SymbolicError,
)
```

Every SCW error is a subclass of `SCWError`. The value-like ones
(`DimensionError`, `ShapeError`, `NonFiniteError`, `NumericalError`,
`SymbolicError`) also subclass `ValueError`, so `except ValueError` catches
them too. `ConvergenceError` (a failed ODE integration or iterative method)
also subclasses `RuntimeError`.

## `scw.visualization`

Optional Matplotlib adapter, installed with the `visualization` extra. The core
never imports Matplotlib; these helpers read domain objects and return the
Matplotlib `Axes` they drew on (or a `(Figure, Axes)` pair from `new_figure`).
Select a non-interactive backend (`matplotlib.use("Agg")`) before importing in
headless environments.

```python
import matplotlib
matplotlib.use("Agg")

import numpy as np
from scw.math_core import Matrix, Vector
from scw.numerical import solve_ivp
from scw.visualization import (
    new_figure, new_3d_figure,
    plot_vector, plot_vectors, plot_function, plot_vector_field,
    plot_matrix, plot_ode_solution, plot_vectors_3d, plot_surface,
)

fig, ax = new_figure(figsize=(4, 4))
plot_vector(Vector([2.0, 1.0]), ax=ax, label="v")

plot_function(np.sin, (0.0, 2 * np.pi), samples=256)
plot_vector_field(lambda x, y: (-y, x), (-2.0, 2.0), (-2.0, 2.0), normalize=True)
plot_matrix(Matrix([[1.0, 2.0], [3.0, 4.0]]), annotate=True)
plot_ode_solution(solve_ivp(lambda t, y: Vector(-y.data), (0.0, 5.0), Vector([1.0])))

fig, ax = new_3d_figure()
plot_vectors_3d([Vector([1.0, 0.0, 0.0]), Vector([0.0, 1.0, 1.0])], ax=ax)
plot_surface(lambda x, y: np.sin(x) * np.cos(y), (-3.0, 3.0), (-3.0, 3.0))
```

Invalid input raises `TypeError` (non-`Vector`/`Matrix`, non-callable field),
`DimensionError` (wrong vector dimension or field output shape) or
`NumericalError` (bad range or too few samples). Importing
`scw.visualization` without the extra raises an actionable `ImportError`. See
[Visualization](mathematics/visualization.md).

## `scw.symbolic`

Optional adapter over SymPy, installed with the `symbolic` extra. `SymbolicMatrix`
and `SymbolicVector` hold exact expressions and convert explicitly:

```python
from sympy import symbols
from scw.symbolic import SymbolicMatrix, to_symbolic

a, b = symbols("a b")
m = SymbolicMatrix([[a, 1], [2, b]])
m.free_symbols                 # {a, b}
m.subs({a: 4, b: 3}).to_numeric()   # -> scw Matrix([[4, 1], [2, 3]])
m.to_sympy().det()             # a*b - 2  (SymPy's own algebra)
to_symbolic(Matrix([[2.0, 0.0], [0.0, 5.0]]))   # lift a numeric matrix
```

`to_numeric()` / `to_numpy()` raise `SymbolicError` while any free symbol
remains. Importing `scw.symbolic` without the extra raises an actionable
`ImportError`; the numeric core never imports SymPy. See
[Symbolic algebra](mathematics/symbolic.md).

## Command line

```bash
scw version     # show scw / Python / NumPy / SciPy versions
scw doctor      # verify required dependencies import correctly
scw --help
```
