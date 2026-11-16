"""Vectors, covectors and the natural pairing.

Run with::

    uv run python examples/01_vectors_and_covectors.py
"""

from __future__ import annotations

from scw.math_core import Covector, Vector


def main() -> None:
    v = Vector([1.0, 2.0, 3.0])
    w = Vector([4.0, 5.0, 6.0])

    print("v =", v)
    print("dimension:", v.dimension)
    print("norm(v):", v.norm())
    print("v . w:", v.dot(w))
    print("v + w:", (v + w).to_numpy().tolist())
    print("2 * v:", (2 * v).to_numpy().tolist())

    alpha = Covector([2.0, 0.0, -1.0])
    print("alpha(v):", alpha.evaluate(v))


if __name__ == "__main__":
    main()
