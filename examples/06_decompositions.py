"""Matrix factorizations: LU, QR, SVD, Cholesky and the symmetric eigensolver.

Run with::

    uv run python examples/06_decompositions.py
"""

from __future__ import annotations

import numpy as np

from scw.math_core import Matrix
from scw.numerical import cholesky, eigh, lu, qr, svd

# A general square matrix and a symmetric positive-definite one.
a = Matrix([[4.0, 7.0, 2.0], [3.0, 6.0, 1.0], [2.0, 5.0, 3.0]])
spd = Matrix([[4.0, 1.0, 0.0], [1.0, 3.0, 1.0], [0.0, 1.0, 2.0]])


def main() -> None:
    print("A =\n", a.data)

    lu_result = lu(a)
    print(
        "\nLU:  P L U reconstructs A:",
        np.allclose(lu_result.reconstruct().data, a.data),
    )

    qr_result = qr(a)
    q = qr_result.q.data
    print("QR:  Q has orthonormal columns:", np.allclose(q.T @ q, np.eye(q.shape[1])))
    print("     R reconstructs A:", np.allclose(qr_result.reconstruct().data, a.data))

    svd_result = svd(a)
    print("\nSVD: singular values:", svd_result.s.data)
    print("     rank:", svd_result.rank())
    print(
        "     U S V^T reconstructs A:",
        np.allclose(svd_result.reconstruct().data, a.data),
    )

    lower = cholesky(spd)
    print(
        "\nCholesky: L L^T reconstructs the SPD matrix:",
        np.allclose(lower.data @ lower.data.T, spd.data),
    )

    eigh_result = eigh(spd)
    print("Eigh: eigenvalues (ascending):", eigh_result.eigenvalues.data)
    print(
        "      V diag(w) V^T reconstructs it:",
        np.allclose(eigh_result.reconstruct().data, spd.data),
    )


if __name__ == "__main__":
    main()
