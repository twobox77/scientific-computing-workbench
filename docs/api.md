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

## Command line

```bash
scw version     # show scw / Python / NumPy / SciPy versions
scw doctor      # verify required dependencies import correctly
scw --help
```
