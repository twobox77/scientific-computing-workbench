"""Vector: an element of a finite-dimensional real vector space."""

from __future__ import annotations

from typing import Any

import numpy as np

from scw.config import DEFAULT_DTYPE
from scw.exceptions import DimensionError, NonFiniteError
from scw.math_core.spaces import VectorSpace


def _as_scalar(value: Any) -> float | None:
    """Return ``value`` as a float if it is a real scalar, else ``None``."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)
    return None


class Vector:
    """A vector in a finite-dimensional real vector space.

    The vector stores its coordinates in an implicit basis as a one-dimensional
    ``float64`` array.  Input data is copied on construction, so later mutation
    of the caller's array never changes the vector.
    """

    __slots__ = ("_data", "_space")

    def __init__(self, data: Any, *, space: VectorSpace | None = None) -> None:
        arr = np.array(data, dtype=DEFAULT_DTYPE, copy=True)
        if arr.ndim != 1:
            raise DimensionError(
                f"Vector requires a one-dimensional array, got shape {arr.shape}"
            )
        if arr.size == 0:
            raise DimensionError("Vector must have at least one component")
        if not np.all(np.isfinite(arr)):
            raise NonFiniteError("Vector data contains NaN or infinite values")
        if space is not None and space.dimension != arr.size:
            raise DimensionError(
                f"space has dimension {space.dimension} but data has {arr.size}"
            )
        self._data = arr
        self._space = space if space is not None else VectorSpace(int(arr.size))

    @property
    def space(self) -> VectorSpace:
        """The space this vector belongs to."""
        return self._space

    @property
    def dimension(self) -> int:
        """Number of components."""
        return int(self._data.size)

    @property
    def data(self) -> np.ndarray:
        """Read-only view of the underlying coordinates."""
        view = self._data.view()
        view.flags.writeable = False
        return view

    def to_numpy(self, *, copy: bool = True) -> np.ndarray:
        """Return the coordinates as a NumPy array (a copy by default)."""
        return self._data.copy() if copy else self.data

    def _check_compatible(self, other: Vector, op: str) -> None:
        if self.dimension != other.dimension:
            raise DimensionError(
                f"{op} requires equal dimensions, got {self.dimension} and "
                f"{other.dimension}"
            )
        if self._space != other._space:
            raise DimensionError(
                f"{op} requires vectors in the same space: {self._space} vs "
                f"{other._space}"
            )

    def __add__(self, other: Any) -> Vector:
        if not isinstance(other, Vector):
            return NotImplemented
        self._check_compatible(other, "addition")
        return Vector(self._data + other._data, space=self._space)

    def __sub__(self, other: Any) -> Vector:
        if not isinstance(other, Vector):
            return NotImplemented
        self._check_compatible(other, "subtraction")
        return Vector(self._data - other._data, space=self._space)

    def __neg__(self) -> Vector:
        return Vector(-self._data, space=self._space)

    def __mul__(self, scalar: Any) -> Vector:
        if isinstance(scalar, Vector):
            raise TypeError("use Vector.dot(other) for an inner product")
        factor = _as_scalar(scalar)
        if factor is None:
            return NotImplemented
        return Vector(self._data * factor, space=self._space)

    __rmul__ = __mul__

    def __truediv__(self, scalar: Any) -> Vector:
        factor = _as_scalar(scalar)
        if factor is None:
            return NotImplemented
        if factor == 0.0:
            raise ZeroDivisionError("cannot divide a vector by zero")
        return Vector(self._data / factor, space=self._space)

    def dot(self, other: Vector) -> float:
        """Euclidean inner product with ``other``."""
        if not isinstance(other, Vector):
            raise TypeError("dot expects a Vector")
        self._check_compatible(other, "dot product")
        return float(np.dot(self._data, other._data))

    def norm(self, *, p: float = 2) -> float:
        """Return the ``p``-norm (Euclidean by default).

        The Euclidean norm is computed with a scale factor so that very small
        or very large components do not underflow or overflow the sum of
        squares.
        """
        if p <= 0:
            raise ValueError("norm order p must be positive")
        if p == 2:
            scale = float(np.max(np.abs(self._data)))
            if scale == 0.0:
                return 0.0
            return float(scale * np.linalg.norm(self._data / scale))
        return float(np.linalg.norm(self._data, ord=p))

    def is_zero(self, *, atol: float = 0.0) -> bool:
        """True when every component is zero within ``atol``."""
        return bool(np.all(np.abs(self._data) <= atol))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self._space == other._space and bool(
            np.array_equal(self._data, other._data)
        )

    def __hash__(self) -> int:
        return hash((self._space, tuple(self._data.tolist())))

    def __repr__(self) -> str:
        body = ", ".join(repr(float(x)) for x in self._data)
        return f"Vector([{body}], space={self._space})"
