"""Unit tests for the optional SymPy adapter (:mod:`scw.symbolic`).

The whole module is skipped when the optional ``symbolic`` extra is not
installed, so the core test suite still passes on a minimal install.
"""

from __future__ import annotations

import numpy as np
import pytest

sympy = pytest.importorskip("sympy")

from sympy import symbols  # noqa: E402

from scw.exceptions import DimensionError, SymbolicError  # noqa: E402
from scw.math_core import Matrix, Vector  # noqa: E402
from scw.symbolic import SymbolicMatrix, SymbolicVector, to_symbolic  # noqa: E402


def test_matrix_shape_and_free_symbols() -> None:
    a, b = symbols("a b")
    m = SymbolicMatrix([[a, 1], [2, b]])
    assert m.shape == (2, 2)
    assert m.rows == 2
    assert m.columns == 2
    assert m.free_symbols == {a, b}


def test_matrix_subs_then_numeric() -> None:
    a, b = symbols("a b")
    m = SymbolicMatrix([[a, 1], [2, b]])
    resolved = m.subs({a: 3, b: 4})
    assert np.array_equal(resolved.to_numpy(), np.array([[3.0, 1.0], [2.0, 4.0]]))
    assert resolved.to_numeric() == Matrix([[3.0, 1.0], [2.0, 4.0]])


def test_matrix_to_numeric_rejects_free_symbols() -> None:
    a = symbols("a")
    with pytest.raises(SymbolicError):
        SymbolicMatrix([[a, 1], [2, 3]]).to_numeric()


def test_matrix_accepts_numeric_matrix_and_sympy_matrix() -> None:
    assert SymbolicMatrix(Matrix([[1.0, 2.0]])).to_numeric() == Matrix([[1.0, 2.0]])
    assert SymbolicMatrix(sympy.Matrix([[1, 2]])).to_numeric() == Matrix([[1.0, 2.0]])


def test_matrix_from_numeric_round_trip() -> None:
    m = Matrix([[1.5, -2.0], [0.0, 3.0]])
    assert SymbolicMatrix.from_numeric(m).to_numeric() == m


def test_matrix_empty_rejected() -> None:
    with pytest.raises(DimensionError):
        SymbolicMatrix([])


def test_matrix_from_numeric_type_error() -> None:
    with pytest.raises(TypeError):
        SymbolicMatrix.from_numeric([[1.0]])  # type: ignore[arg-type]


def test_matrix_equality_and_hash() -> None:
    a = symbols("a")
    assert SymbolicMatrix([[a]]) == SymbolicMatrix([[a]])
    assert hash(SymbolicMatrix([[a]])) == hash(SymbolicMatrix([[a]]))
    assert SymbolicMatrix([[a]]) != SymbolicMatrix([[1]])


def test_matrix_to_sympy_is_a_copy() -> None:
    m = SymbolicMatrix([[1, 2]])
    raw = m.to_sympy()
    raw[0, 0] = 99
    assert m.to_sympy()[0, 0] == 1


def test_vector_basics() -> None:
    a = symbols("a")
    v = SymbolicVector([a, 2])
    assert v.dimension == 2
    assert len(v) == 2
    assert v.entries == (a, sympy.Integer(2))
    assert v.free_symbols == {a}


def test_vector_subs_and_numeric() -> None:
    a = symbols("a")
    v = SymbolicVector([a, 2]).subs({a: 7})
    assert np.array_equal(v.to_numeric().data, np.array([7.0, 2.0]))


def test_vector_to_numeric_rejects_free_symbols() -> None:
    a = symbols("a")
    with pytest.raises(SymbolicError):
        SymbolicVector([a, 1]).to_numeric()


def test_vector_from_numeric_round_trip() -> None:
    v = Vector([1.0, -2.5])
    assert SymbolicVector.from_numeric(v).to_numeric() == v


def test_vector_from_numeric_type_error() -> None:
    with pytest.raises(TypeError):
        SymbolicVector.from_numeric([1.0, 2.0])  # type: ignore[arg-type]


def test_vector_empty_rejected() -> None:
    with pytest.raises(DimensionError):
        SymbolicVector([])


def test_to_symbolic_dispatch() -> None:
    assert isinstance(to_symbolic(Vector([1.0])), SymbolicVector)
    assert isinstance(to_symbolic(Matrix([[1.0]])), SymbolicMatrix)
    with pytest.raises(TypeError):
        to_symbolic([1.0, 2.0])  # type: ignore[arg-type]


def test_missing_sympy_raises_actionable_error(monkeypatch) -> None:
    """Without the optional extra, importing the backend explains how to fix it."""
    import builtins
    import importlib
    import sys

    real_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "sympy" or name.startswith("sympy."):
            raise ImportError("simulated missing sympy")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.delitem(sys.modules, "scw.symbolic._backend", raising=False)
    with pytest.raises(ImportError, match="symbolic"):
        importlib.import_module("scw.symbolic._backend")
