"""Unit tests for :mod:`scw.numerical.decomposition`."""

from __future__ import annotations

import numpy as np
import pytest

from scw.exceptions import NumericalError, ShapeError
from scw.math_core import Matrix
from scw.numerical import cholesky, eigh, lu, qr, svd

A = Matrix([[4.0, 7.0], [2.0, 6.0]])
SPD = Matrix([[4.0, 1.0], [1.0, 3.0]])


def test_lu_reconstructs() -> None:
    np.testing.assert_allclose(lu(A).reconstruct().data, A.data, rtol=1e-9, atol=1e-12)


def test_lu_factors_have_expected_structure() -> None:
    result = lu(A)
    # L is unit lower-triangular: unit diagonal, zero above.
    np.testing.assert_allclose(np.diag(result.lower.data), np.ones(2))
    assert result.lower.data[0, 1] == pytest.approx(0.0, abs=1e-12)
    # U is upper-triangular: zero below the diagonal.
    assert result.upper.data[1, 0] == pytest.approx(0.0, abs=1e-12)


def test_lu_requires_square() -> None:
    with pytest.raises(ShapeError):
        lu(Matrix([[1.0, 2.0]]))


def test_lu_type_error() -> None:
    with pytest.raises(TypeError):
        lu([[1.0]])  # type: ignore[arg-type]


def test_qr_reconstructs_full_and_economic() -> None:
    tall = Matrix([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    for mode in ("full", "economic"):
        np.testing.assert_allclose(
            qr(tall, mode=mode).reconstruct().data, tall.data, rtol=1e-9, atol=1e-12
        )


def test_qr_orthonormal_columns() -> None:
    result = qr(A)
    q = result.q.data
    np.testing.assert_allclose(q.T @ q, np.eye(q.shape[1]), rtol=1e-9, atol=1e-12)


def test_qr_bad_mode() -> None:
    with pytest.raises(ValueError):
        qr(A, mode="reduced")


def test_qr_type_error() -> None:
    with pytest.raises(TypeError):
        qr([[1.0]])  # type: ignore[arg-type]


def test_svd_reconstructs() -> None:
    np.testing.assert_allclose(svd(A).reconstruct().data, A.data, rtol=1e-9, atol=1e-12)


def test_svd_reconstructs_with_thin_factors() -> None:
    tall = Matrix([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    np.testing.assert_allclose(
        svd(tall, full_matrices=False).reconstruct().data,
        tall.data,
        rtol=1e-9,
        atol=1e-12,
    )


def test_qr_reconstructs_wide_matrix() -> None:
    wide = Matrix([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    for mode in ("full", "economic"):
        np.testing.assert_allclose(
            qr(wide, mode=mode).reconstruct().data, wide.data, rtol=1e-9, atol=1e-12
        )


def test_svd_singular_values_are_sorted_descending() -> None:
    s = svd(A).s.data
    assert np.all(np.diff(s) <= 1e-12)
    assert np.all(s >= 0.0)


def test_svd_rank_of_full_rank_matrix() -> None:
    assert svd(A).rank() == 2


def test_svd_rank_of_rank_deficient_matrix() -> None:
    deficient = Matrix([[1.0, 2.0], [2.0, 4.0]])
    assert svd(deficient).rank() == 1


def test_svd_type_error() -> None:
    with pytest.raises(TypeError):
        svd([[1.0]])  # type: ignore[arg-type]


def test_cholesky_reconstructs_lower_and_upper() -> None:
    lower = cholesky(SPD)
    np.testing.assert_allclose(
        lower.data @ lower.data.T, SPD.data, rtol=1e-9, atol=1e-12
    )
    upper = cholesky(SPD, lower=False)
    np.testing.assert_allclose(
        upper.data.T @ upper.data, SPD.data, rtol=1e-9, atol=1e-12
    )


def test_cholesky_rejects_non_symmetric() -> None:
    with pytest.raises(NumericalError):
        cholesky(Matrix([[1.0, 2.0], [0.0, 1.0]]))


def test_cholesky_rejects_non_positive_definite() -> None:
    with pytest.raises(NumericalError):
        cholesky(Matrix([[1.0, 0.0], [0.0, -1.0]]))


def test_cholesky_requires_square() -> None:
    with pytest.raises(ShapeError):
        cholesky(Matrix([[1.0, 0.0, 0.0]]))


def test_cholesky_type_error() -> None:
    with pytest.raises(TypeError):
        cholesky([[1.0]])  # type: ignore[arg-type]


def test_eigh_reconstructs_and_sorts_ascending() -> None:
    result = eigh(SPD)
    np.testing.assert_allclose(
        result.reconstruct().data, SPD.data, rtol=1e-9, atol=1e-12
    )
    w = result.eigenvalues.data
    assert np.all(np.diff(w) >= -1e-12)


def test_eigh_eigenvectors_are_orthonormal() -> None:
    v = eigh(SPD).eigenvectors.data
    np.testing.assert_allclose(v.T @ v, np.eye(2), rtol=1e-9, atol=1e-12)


def test_eigh_rejects_non_symmetric() -> None:
    with pytest.raises(NumericalError):
        eigh(Matrix([[1.0, 2.0], [0.0, 1.0]]))


def test_eigh_requires_square() -> None:
    with pytest.raises(ShapeError):
        eigh(Matrix([[1.0, 0.0, 0.0]]))


def test_eigh_type_error() -> None:
    with pytest.raises(TypeError):
        eigh([[1.0]])  # type: ignore[arg-type]


def test_svd_rank_of_zero_matrix() -> None:
    result = svd(Matrix([[0.0, 0.0], [0.0, 0.0]]))
    assert result.rank() == 0


def test_svd_rank_tolerance_can_be_overridden() -> None:
    # A tiny nonzero singular value is below the default tolerance but above an
    # explicitly lowered one, so the rank depends on the caller's threshold.
    nearly_singular = Matrix([[1.0, 1.0], [1.0, 1.0 + 1e-14]])
    assert svd(nearly_singular).rank() == 1
    assert svd(nearly_singular).rank(atol=0.0, rtol=0.0) == 2
