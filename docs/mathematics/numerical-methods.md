# Numerical methods: linear algebra and ODEs

`scw.numerical` holds the algorithms.  It accepts the domain objects from
`scw.math_core` (`Matrix`, `Vector`) and wraps SciPy; it never pushes its own
types back into the domain model.  Every routine validates its input and raises
an SCW exception, so callers never see a bare `numpy.linalg` error.

## Linear systems

- `solve(a, b)` solves a square `a x = b` with a stable factorization
  (`scipy.linalg.solve`), not by forming an explicit inverse.
- `lstsq(a, b)` solves `a x ~ b` in the least-squares sense for any shape,
  returning the minimum-norm solution, the numerical rank and the singular
  values of `a`.  The residual norm is zero for a consistent or
  under-determined system.

## Factorizations

Each factorization returns an immutable result that can rebuild the original
matrix with `reconstruct()`, which is how the property tests check it.

| Routine | Factorization | Notes |
|---|---|---|
| `lu(a)` | `A = P L U` | square `a`; `P` absorbs the pivoting |
| `qr(a)` | `A = Q R` | `Q` orthonormal; `mode="full"` or `"economic"` |
| `svd(a)` | `A = U diag(s) Vh` | `s` descending; `rank()` is scale-aware |
| `cholesky(a)` | `A = L L^T` | symmetric positive-definite |
| `eigh(a)` | `A = V diag(w) V^T` | symmetric `a`; real, ascending `w` |

`cholesky` and `eigh` check symmetry first and raise `NumericalError` when it
does not hold (or when `cholesky` meets a non-positive-definite matrix).  The
rank test in `SVDResult.rank` uses a tolerance that scales with the largest
singular value, so a large but rank-deficient matrix is not mistaken for a
full-rank one.

## Initial-value ODEs

`solve_ivp(fun, t_span, y0, ...)` integrates `y' = fun(t, y)` over `t_span`.
The right-hand side is written in the domain's terms: it takes a scalar time and
a `Vector` state and returns a `Vector` (or any array-like of the same
dimension).  The call mirrors `scipy.integrate.solve_ivp`: choose `method` from
`METHODS`, set `rtol`/`atol`/`max_step`/`first_step`, and request specific
output times with `t_eval`.

The returned `ODESolution` exposes the time grid `t`, the states `y` (shape
`(n_points, dimension)`), `final_state`, `state_at(i)`, and — when the solver is
called with `dense_output=True` — `interpolate(t)`.  A failed integration raises
`ConvergenceError` (a `RuntimeError`), or reports `success == False` when
`raise_on_failure=False`.

### Accuracy

The property tests pin two exact references:

- linear decay `y' = -rate * y` against `exp(-rate * t)`;
- a constant-coefficient system `y' = A y` against `expm(A t) y0`.

The harmonic oscillator is checked by energy conservation
(`q^2 + v^2` is constant), which a method with the wrong order cannot satisfy
over a long interval.
