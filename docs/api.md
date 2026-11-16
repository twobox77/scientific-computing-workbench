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

SciPy-backed linear algebra on `Matrix` / `Vector` inputs:

```python
from scw.numerical import solve, inverse, det

solve(a, b)      # a x = b
inverse(a)       # a^-1
det(a)           # determinant
```

All three require square (and, where relevant, consistently shaped) inputs and
raise the SCW exceptions on violation.

## Exceptions

```python
from scw.exceptions import SCWError, DimensionError, ShapeError, NonFiniteError
```

Every SCW error is a subclass of `SCWError`; the value-like ones
(`DimensionError`, `ShapeError`, `NonFiniteError`) also subclass `ValueError`,
so `except ValueError` catches them too.

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
