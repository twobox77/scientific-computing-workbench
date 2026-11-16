# Quickstart

## Install

```bash
uv sync --all-extras
```

## Use the Python API

```python
from scw.math_core import Covector, LinearMap, Matrix, Vector

v = Vector([1.0, 2.0, 3.0])
w = Vector([4.0, 5.0, 6.0])
print(v.norm(), v.dot(w))

alpha = Covector([2.0, 0.0, -1.0])
print(alpha.evaluate(v))

a = Matrix([[1.0, 2.0], [3.0, 4.0]])
t = LinearMap.from_matrix(a)
print(t.apply(Vector([1.0, 1.0])))
```

## Numerical work

```python
from scw.math_core import Matrix, Vector
from scw.numerical import lu, solve, solve_ivp

a = Matrix([[4.0, 7.0], [2.0, 6.0]])
x = solve(a, Vector([1.0, 0.0]))   # solve a x = b
print(x.data)
print(lu(a).reconstruct().data)   # factorizations rebuild the matrix

# Integrate y' = -y from y(0) = 1, sampling at a few times.
sol = solve_ivp(lambda t, y: -1.0 * y, (0.0, 2.0), Vector([1.0]), t_eval=[0.0, 2.0])
print(sol.final_state.data)       # ~ exp(-2)
```

## Command line

```bash
uv run scw version
uv run scw doctor
```

## Develop

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src/scw
```
