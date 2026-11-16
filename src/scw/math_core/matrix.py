"""Matrix: a rectangular numerical array and linear-map representation."""

from __future__ import annotations

from typing import Any

import numpy as np

from scw.config import DEFAULT_DTYPE
from scw.exceptions import DimensionError, NonFiniteError, ShapeError
from scw.math_core.vector import Vector, _as_scalar


class Matrix:
    """A rectangular ``float64`` array.

    When used as the representation of a linear map, the caller must keep the
    input (column) and output (row) dimensions straight; see
    :class:`~scw.math_core.linear_map.LinearMap`.
    """

    __slots__ = ("_data",)

    def __init__(self, data: Any) -> None:
        arr = np.array(data, dtype=DEFAULT_DTYPE, copy=True)
        if arr.ndim != 2:
            raise ShapeError(
                f"Matrix requires a two-dimensional array, got shape {arr.shape}"
            )
        if 0 in arr.shape:
            raise ShapeError("Matrix must have non-empty rows and columns")
        if not np.all(np.isfinite(arr)):
            raise NonFiniteError("Matrix data contains NaN or infinite values")
        self._data = arr

    @property
    def shape(self) -> tuple[int, int]:
        """``(rows, columns)``."""
        return (int(self._data.shape[0]), int(self._data.shape[1]))

    @property
    def rows(self) -> int:
        return int(self._data.shape[0])

    @property
    def columns(self) -> int:
        return int(self._data.shape[1])

    @property
    def data(self) -> np.ndarray:
        """Read-only view of the underlying array."""
        view = self._data.view()
        view.flags.writeable = False
        return view

    def to_numpy(self, *, copy: bool = True) -> np.ndarray:
        """Return the array as a NumPy array (a copy by default)."""
        return self._data.copy() if copy else self.data

    def _check_same_shape(self, other: Matrix, op: str) -> None:
        if self.shape != other.shape:
            raise ShapeError(
                f"{op} requires equal shapes, got {self.shape} and {other.shape}"
            )

    def __add__(self, other: Any) -> Matrix:
        if not isinstance(other, Matrix):
            return NotImplemented
        self._check_same_shape(other, "addition")
        return Matrix(self._data + other._data)

    def __sub__(self, other: Any) -> Matrix:
        if not isinstance(other, Matrix):
            return NotImplemented
        self._check_same_shape(other, "subtraction")
        return Matrix(self._data - other._data)

    def __neg__(self) -> Matrix:
        return Matrix(-self._data)

    def __mul__(self, scalar: Any) -> Matrix:
        if isinstance(scalar, Matrix):
            raise TypeError("use Matrix @ Matrix for matrix multiplication")
        factor = _as_scalar(scalar)
        if factor is None:
            return NotImplemented
        return Matrix(self._data * factor)

    __rmul__ = __mul__

    def __matmul__(self, other: Any) -> Matrix:
        if not isinstance(other, Matrix):
            return NotImplemented
        if self.columns != other.rows:
            raise DimensionError(
                f"matrix multiplication requires {self.columns} == {other.rows}, "
                f"got shapes {self.shape} and {other.shape}"
            )
        return Matrix(self._data @ other._data)

    def apply(self, vector: Vector) -> Vector:
        """Left-multiply a vector: ``M v``."""
        if not isinstance(vector, Vector):
            raise TypeError("apply expects a Vector")
        if self.columns != vector.dimension:
            raise DimensionError(
                f"matrix has {self.columns} columns but vector has "
                f"{vector.dimension} components"
            )
        return Vector(self._data @ vector.data)

    def transpose(self) -> Matrix:
        """Return the transpose."""
        return Matrix(self._data.T)

    @property
    def T(self) -> Matrix:
        """Shorthand for :meth:`transpose`."""
        return self.transpose()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Matrix):
            return NotImplemented
        return bool(np.array_equal(self._data, other._data))

    def __hash__(self) -> int:
        return hash((self._data.shape, tuple(self._data.ravel().tolist())))

    def __repr__(self) -> str:
        return f"Matrix(shape={self.shape}, data={self._data!r})"
