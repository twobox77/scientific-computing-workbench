"""Tensors: outer product, contraction and trace.

Run with::

    uv run python examples/03_tensor_operations.py
"""

from __future__ import annotations

import numpy as np

from scw.math_core import Tensor


def main() -> None:
    a = Tensor([[1.0, 2.0], [3.0, 4.0]])
    b = Tensor([[5.0, 6.0], [7.0, 8.0]])

    print("a.order:", a.order, "a.shape:", a.shape)
    print("a + b:", (a + b).data.tolist())
    print("2 * a:", (2 * a).data.tolist())

    outer = a.outer(b)
    print("a (x) b shape:", outer.shape)

    # Contracting the last index of a with the first of b is the matrix product.
    print("a . b (contract):", a.contract(b).data.tolist())
    assert np.allclose(a.contract(b).data, a.data @ b.data)

    print("trace(a):", float(a.trace().data))
    print("Tensor.eye(3):", Tensor.eye(3).data.tolist())


if __name__ == "__main__":
    main()
