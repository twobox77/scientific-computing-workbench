# Symbolic algebra

SCW's numeric core is exact about *semantics* but approximate about *numbers*:
everything is `float64`.  When you want an exact answer -- a determinant as a
polynomial, an inverse with symbolic entries, a formula to inspect before
plugging in values -- use the symbolic adapter in `scw.symbolic`.

The adapter is **optional**.  It wraps [SymPy](https://www.sympy.org/) and is
installed with the `symbolic` extra:

```bash
uv sync --extra symbolic      # or: pip install 'scw[symbolic]'
```

The numeric core never imports it, so a minimal install stays lean.  Importing
`scw.symbolic` without the extra raises an `ImportError` that tells you how to
install it.

## The two objects

`SymbolicMatrix` and `SymbolicVector` mirror their numeric counterparts.  Entries
may be numbers, symbols or expressions:

```python
from sympy import symbols
from scw.symbolic import SymbolicMatrix

a, b = symbols("a b")
m = SymbolicMatrix([[a, 1], [2, b]])

m.shape           # (2, 2)
m.free_symbols    # {a, b}
m.subs({a: 4})    # SymbolicMatrix([[4, 1], [2, b]])
```

`to_sympy()` hands back a plain SymPy matrix when you need SymPy's own algebra
(`det`, `inv`, `eigenvals`, ...):

```python
m.to_sympy().det()   # a*b - 2
m.to_sympy().inv()   # Matrix([[b/(a*b - 2), -1/(a*b - 2)], ...])
```

## Crossing the numeric boundary

Conversion is explicit in both directions, so a symbolic value never silently
becomes a float:

```python
from scw.math_core import Matrix
from scw.symbolic import to_symbolic

to_symbolic(Matrix([[2.0, 0.0], [0.0, 5.0]]))   # lift a numeric matrix
m.subs({a: 4, b: 3}).to_numeric()               # collapse to Matrix
```

`to_numeric()` / `to_numpy()` refuse to run while any free symbol remains and
raise `SymbolicError`, which (like every SCW error) is also a `ValueError`.

## Where this sits

`scw.symbolic` depends on `scw.math_core` and SymPy.  It is never a dependency
of the numeric core, and it imports no interface code (no CLI, Jupyter or
plotting), preserving the layering rule from the specification.
