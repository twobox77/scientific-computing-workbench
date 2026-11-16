"""Covector: an element of the dual space, i.e. a linear functional."""

from __future__ import annotations

from typing import Any

import numpy as np

from scw.config import DEFAULT_DTYPE
from scw.exceptions import DimensionError, NonFiniteError
from scw.math_core.spaces import VectorSpace
from scw.math_core.vector import Vector, _as_scalar


class Covector:
    """A linear functional ``alpha: V -> R`` given by its coefficients.

    A covector is deliberately a distinct type from :class:`Vector` even
    though, in a chosen basis, both hold a one-dimensional array of the same
    length.  The distinction is the whole point: pairing and vector addition
    are different operations.
    """

    __slots__ = ("_data", "_dual_space")

    def __init__(self, data: Any, *, dual_space: VectorSpace | None = None) -> None:
        arr = np.array(data, dtype=DEFAULT_DTYPE, copy=True)
        if arr.ndim != 1:
            raise DimensionError(
                f"Covector requires a one-dimensional array, got shape {arr.shape}"
            )
        if arr.size == 0:
            raise DimensionError("Covector must have at least one component")
        if not np.all(np.isfinite(arr)):
            raise NonFiniteError("Covector data contains NaN or infinite values")
        if dual_space is not None and dual_space.dimension != arr.size:
            raise DimensionError(
                f"dual space has dimension {dual_space.dimension} but data has "
                f"{arr.size}"
            )
        self._data = arr
        self._dual_space = (
            dual_space if dual_space is not None else VectorSpace(int(arr.size))
        )

    @property
    def dual_space(self) -> VectorSpace:
        """The space of vectors this covector acts on."""
        return self._dual_space

    @property
    def dimension(self) -> int:
        """Number of components."""
        return int(self._data.size)

    @property
    def data(self) -> np.ndarray:
        """Read-only view of the underlying coefficients."""
        view = self._data.view()
        view.flags.writeable = False
        return view

    def to_numpy(self, *, copy: bool = True) -> np.ndarray:
        """Return the coefficients as a NumPy array (a copy by default)."""
        return self._data.copy() if copy else self.data

    def evaluate(self, vector: Vector) -> float:
        """Natural pairing ``alpha(v)``."""
        if not isinstance(vector, Vector):
            raise TypeError("evaluate expects a Vector")
        if self.dimension != vector.dimension:
            raise DimensionError(
                f"pairing requires equal dimensions, got {self.dimension} and "
                f"{vector.dimension}"
            )
        return float(np.dot(self._data, vector.data))

    __call__ = evaluate

    def _check_compatible(self, other: Covector, op: str) -> None:
        if self.dimension != other.dimension:
            raise DimensionError(
                f"{op} requires equal dimensions, got {self.dimension} and "
                f"{other.dimension}"
            )

    def __add__(self, other: Any) -> Covector:
        if not isinstance(other, Covector):
            return NotImplemented
        self._check_compatible(other, "addition")
        return Covector(self._data + other._data, dual_space=self._dual_space)

    def __sub__(self, other: Any) -> Covector:
        if not isinstance(other, Covector):
            return NotImplemented
        self._check_compatible(other, "subtraction")
        return Covector(self._data - other._data, dual_space=self._dual_space)

    def __neg__(self) -> Covector:
        return Covector(-self._data, dual_space=self._dual_space)

    def __mul__(self, scalar: Any) -> Covector:
        if isinstance(scalar, Covector):
            raise TypeError("covectors cannot be multiplied together")
        factor = _as_scalar(scalar)
        if factor is None:
            return NotImplemented
        return Covector(self._data * factor, dual_space=self._dual_space)

    __rmul__ = __mul__

    def __truediv__(self, scalar: Any) -> Covector:
        factor = _as_scalar(scalar)
        if factor is None:
            return NotImplemented
        if factor == 0.0:
            raise ZeroDivisionError("cannot divide a covector by zero")
        return Covector(self._data / factor, dual_space=self._dual_space)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Covector):
            return NotImplemented
        return self._dual_space == other._dual_space and bool(
            np.array_equal(self._data, other._data)
        )

    def __hash__(self) -> int:
        return hash((self._dual_space, tuple(self._data.tolist())))

    def __repr__(self) -> str:
        body = ", ".join(repr(float(x)) for x in self._data)
        return f"Covector([{body}], dual_space={self._dual_space})"
