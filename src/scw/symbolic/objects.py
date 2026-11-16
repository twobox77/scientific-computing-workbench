"""Symbolic domain objects backed by SymPy.

These are the symbolic counterparts of :class:`~scw.math_core.Matrix` and
:class:`~scw.math_core.Vector`.  They stay in the domain layer: the numeric
types never import this module, and this module never imports the CLI, Jupyter
or plotting code.  SymPy is optional, so this module is only imported when a
caller asks for it (see :mod:`scw.symbolic._backend`).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from scw.config import DEFAULT_DTYPE
from scw.exceptions import DimensionError, SymbolicError
from scw.math_core import Matrix, Vector
from scw.symbolic._backend import SympyMatrix, sympy


def _to_sympy(value: Any) -> Any:
    """Convert a scalar, list or SymPy object into a SymPy expression/array."""
    if isinstance(value, sympy.Basic):
        return value
    return sympy.sympify(value)


class SymbolicVector:
    """A vector whose components are SymPy expressions.

    Values may be numbers, symbols or expressions; the input is copied, so
    later mutation of the caller's list never changes the vector.
    """

    __slots__ = ("_entries",)

    def __init__(self, entries: Any) -> None:
        items = [_to_sympy(e) for e in entries]
        if not items:
            raise DimensionError("SymbolicVector must have at least one component")
        self._entries = tuple(items)

    @property
    def dimension(self) -> int:
        """Number of components."""
        return len(self._entries)

    @property
    def entries(self) -> tuple[Any, ...]:
        """The component expressions, as a tuple."""
        return self._entries

    @property
    def free_symbols(self) -> set[Any]:
        """The set of free symbols appearing in the components."""
        result: set[Any] = set()
        # complexity: SymPy expressions are scalar; this loop is the only way
        for entry in self._entries:
            result |= entry.free_symbols
        return result

    def subs(self, mapping: dict[Any, Any]) -> SymbolicVector:
        """Substitute symbols/expressions, returning a new vector."""
        return SymbolicVector([entry.subs(mapping) for entry in self._entries])

    def to_numeric(self) -> Vector:
        """Return the numeric :class:`Vector`, if every component is a number."""
        if self.free_symbols:
            names = ", ".join(sorted(str(s) for s in self.free_symbols))
            raise SymbolicError(
                f"cannot convert a symbolic vector with free symbols ({names}) "
                "to a numeric Vector; substitute concrete values first"
            )
        data = np.array([float(entry) for entry in self._entries], dtype=DEFAULT_DTYPE)
        return Vector(data)

    @classmethod
    def from_numeric(cls, vector: Vector) -> SymbolicVector:
        """Lift a numeric :class:`Vector` into a symbolic vector."""
        if not isinstance(vector, Vector):
            raise TypeError("from_numeric expects a Vector")
        return cls([sympy.Float(x) for x in vector.data])

    def __len__(self) -> int:
        return self.dimension

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SymbolicVector):
            return NotImplemented
        return self._entries == other._entries

    def __hash__(self) -> int:
        return hash(self._entries)

    def __repr__(self) -> str:
        return f"SymbolicVector({list(self._entries)!r})"


class SymbolicMatrix:
    """A matrix whose entries are SymPy expressions."""

    __slots__ = ("_matrix",)

    def __init__(self, entries: Any) -> None:
        if isinstance(entries, SympyMatrix):
            matrix = sympy.Matrix(entries)
        elif isinstance(entries, (Matrix, SymbolicMatrix)):
            matrix = sympy.Matrix(entries.to_numpy().tolist())
        else:
            matrix = sympy.Matrix(entries)
        if matrix.rows == 0 or matrix.cols == 0:
            raise DimensionError("SymbolicMatrix must be non-empty")
        self._matrix = matrix

    @property
    def rows(self) -> int:
        """Number of rows."""
        return int(self._matrix.rows)

    @property
    def columns(self) -> int:
        """Number of columns."""
        return int(self._matrix.cols)

    @property
    def shape(self) -> tuple[int, int]:
        """The ``(rows, columns)`` shape."""
        return (self.rows, self.columns)

    @property
    def free_symbols(self) -> set[Any]:
        """The set of free symbols appearing in the entries."""
        return set(self._matrix.free_symbols)

    def to_sympy(self) -> Any:
        """Return the underlying SymPy matrix (a copy)."""
        return self._matrix.copy()

    def to_numpy(self) -> np.ndarray:
        """Return the entries as a numeric array (requires no free symbols)."""
        if self.free_symbols:
            names = ", ".join(sorted(str(s) for s in self.free_symbols))
            raise SymbolicError(
                f"cannot convert a symbolic matrix with free symbols ({names}) "
                "to a numeric array; substitute concrete values first"
            )
        return np.array(self._matrix, dtype=DEFAULT_DTYPE)

    def subs(self, mapping: dict[Any, Any]) -> SymbolicMatrix:
        """Substitute symbols/expressions, returning a new matrix."""
        return SymbolicMatrix(self._matrix.subs(mapping))

    def to_numeric(self) -> Matrix:
        """Return the numeric :class:`Matrix`, if every entry is a number."""
        return Matrix(self.to_numpy())

    @classmethod
    def from_numeric(cls, matrix: Matrix) -> SymbolicMatrix:
        """Lift a numeric :class:`Matrix` into a symbolic matrix."""
        if not isinstance(matrix, Matrix):
            raise TypeError("from_numeric expects a Matrix")
        return cls(sympy.Matrix(matrix.data.tolist()))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SymbolicMatrix):
            return NotImplemented
        return bool(self._matrix == other._matrix)

    def __hash__(self) -> int:
        flat = tuple(
            self._matrix[i] for i in range(self._matrix.rows * self._matrix.cols)
        )
        return hash((self.shape, flat))

    def __repr__(self) -> str:
        return f"SymbolicMatrix(shape={self.shape}, entries={self._matrix!r})"


def to_symbolic(value: Any) -> SymbolicVector | SymbolicMatrix:
    """Lift a numeric :class:`Vector`/:class:`Matrix` into its symbolic form."""
    if isinstance(value, Vector):
        return SymbolicVector.from_numeric(value)
    if isinstance(value, Matrix):
        return SymbolicMatrix.from_numeric(value)
    raise TypeError("to_symbolic expects a Vector or a Matrix")


__all__ = ["SymbolicMatrix", "SymbolicVector", "to_symbolic"]
