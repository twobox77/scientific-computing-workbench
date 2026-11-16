"""Symbolic linear algebra: exact results, then collapse to numbers.

Requires the optional ``symbolic`` extra::

    uv sync --extra symbolic
    uv run python examples/05_symbolic_algebra.py
"""

from __future__ import annotations

import numpy as np
from sympy import symbols

from scw.math_core import Matrix
from scw.symbolic import SymbolicMatrix, SymbolicVector, to_symbolic


def main() -> None:
    a, b = symbols("a b")

    # An exact, symbolic 2x2 inverse -- no floating point anywhere.
    m = SymbolicMatrix([[a, 1], [2, b]])
    det = m.to_sympy().det()
    inv = m.to_sympy().inv()
    print("det(M) =", det)
    print("M^-1   =", inv)

    # Substituting concrete values yields an exact matrix, then floats.
    resolved = m.subs({a: 4, b: 3})
    print("M(a=4, b=3) ->", resolved.to_numpy().tolist())
    assert np.allclose(resolved.to_numpy(), np.array([[4.0, 1.0], [2.0, 3.0]]))

    # Lift a numeric object, compute symbolically, come back to numbers.
    numeric = Matrix([[2.0, 0.0], [0.0, 5.0]])
    scaled = to_symbolic(numeric).to_sympy() * a
    print(
        "a * diag(2,5) with a=2 ->",
        SymbolicMatrix(scaled).subs({a: 2}).to_numpy().tolist(),
    )

    # Vectors work the same way.
    v = SymbolicVector([a, 2]).subs({a: 7})
    print("vector ->", v.to_numeric().to_numpy().tolist())


if __name__ == "__main__":
    main()
