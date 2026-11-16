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
