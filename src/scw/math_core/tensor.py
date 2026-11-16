"""Tensor: a multilinear object over a finite-dimensional real vector space.

A tensor of order ``r`` is an ``r``-way array of ``float64`` components.  The
implementation keeps the semantics that the domain layer owns: rank/shape
validation, a stable notion of equality, and the two operations that make a
tensor a tensor -- the tensor (outer) product and contraction of one index
against another.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from scw.config import DEFAULT_DTYPE
from scw.exceptions import DimensionError, NonFiniteError, ShapeError

_SCALAR_TYPES = (int, float, np.integer, np.floating)


def _as_index(value: Any, *, name: str, order: int) -> int:
    """Validate an axis index against ``order`` (negative indices allowed)."""
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise TypeError(f"{name} must be an integer axis index")
    idx = int(value)
    if not -order <= idx < order:
        raise DimensionError(
            f"{name} {idx} is out of range for a tensor of order {order}"
        )
    return idx % order


class Tensor:
    """An ``order``-way array of real components.

    The order is the number of indices; a scalar has order 0, a vector order 1
    and a matrix order 2.  Input data is copied on construction so that later
    mutation of the caller's array never changes the tensor.
    """

    __slots__ = ("_data",)

    def __init__(self, data: Any) -> None:
        arr = np.array(data, dtype=DEFAULT_DTYPE, copy=True)
        if not np.all(np.isfinite(arr)):
            raise NonFiniteError("Tensor data contains NaN or infinite values")
        self._data = arr

    @classmethod
    def zeros(cls, shape: tuple[int, ...]) -> Tensor:
        """Return the zero tensor of the given shape."""
        if not all(
            isinstance(d, (int, np.integer)) and not isinstance(d, bool) for d in shape
        ):
            raise TypeError("shape must be a sequence of integers")
        if any(int(d) < 0 for d in shape):
            raise ShapeError("shape dimensions must be non-negative")
        return cls(np.zeros(tuple(int(d) for d in shape), dtype=DEFAULT_DTYPE))

    @classmethod
    def eye(cls, n: int) -> Tensor:
        """Return the order-2 identity tensor of size ``n``."""
        if isinstance(n, bool) or not isinstance(n, (int, np.integer)):
            raise TypeError("eye expects an integer size")
        if int(n) <= 0:
            raise ShapeError("eye size must be positive")
        return cls(np.eye(int(n), dtype=DEFAULT_DTYPE))

    @property
    def shape(self) -> tuple[int, ...]:
        """The size of each index."""
        return tuple(int(d) for d in self._data.shape)

    @property
    def order(self) -> int:
        """The number of indices."""
        return int(self._data.ndim)

    @property
    def size(self) -> int:
        """Total number of components."""
        return int(self._data.size)

    @property
    def data(self) -> np.ndarray:
        """Read-only view of the underlying array."""
        view = self._data.view()
        view.flags.writeable = False
        return view

    def to_numpy(self, *, copy: bool = True) -> np.ndarray:
        """Return the components as a NumPy array (a copy by default)."""
        return self._data.copy() if copy else self.data

    def _check_compatible(self, other: Tensor, op: str) -> None:
        if self.shape != other.shape:
            raise ShapeError(
                f"{op} requires equal shapes, got {self.shape} and {other.shape}"
            )

    def __add__(self, other: Any) -> Tensor:
        if not isinstance(other, Tensor):
            return NotImplemented
        self._check_compatible(other, "addition")
        return Tensor(self._data + other._data)

    def __sub__(self, other: Any) -> Tensor:
        if not isinstance(other, Tensor):
            return NotImplemented
        self._check_compatible(other, "subtraction")
        return Tensor(self._data - other._data)

    def __neg__(self) -> Tensor:
        return Tensor(-self._data)

    def __mul__(self, scalar: Any) -> Tensor:
        if isinstance(scalar, (Tensor, np.ndarray)):
            raise TypeError("use Tensor.outer for a tensor product")
        if isinstance(scalar, bool) or not isinstance(scalar, _SCALAR_TYPES):
            return NotImplemented
        return Tensor(self._data * float(scalar))

    __rmul__ = __mul__

    def outer(self, other: Tensor) -> Tensor:
        """Tensor (outer) product, stacking indices.

        ``a.outer(b)`` has order ``a.order + b.order``; its first indices run
        over ``a`` and its last over ``b``.
        """
        if not isinstance(other, Tensor):
            raise TypeError("outer expects a Tensor")
        return Tensor(np.tensordot(self._data, other._data, axes=0))

    def contract(self, other: Tensor, *, axis: int = -1, other_axis: int = 0) -> Tensor:
        """Contract ``self``'s ``axis`` with ``other``'s ``other_axis``.

        The contracted indices must have the same size.  The result keeps the
        remaining indices in order: those of ``self`` first, then those of
        ``other``.
        """
        if not isinstance(other, Tensor):
            raise TypeError("contract expects a Tensor")
        i = _as_index(axis, name="axis", order=self.order)
        j = _as_index(other_axis, name="other_axis", order=other.order)
        if self.shape[i] != other.shape[j]:
            raise DimensionError(
                f"cannot contract axes of size {self.shape[i]} and {other.shape[j]}"
            )
        return Tensor(np.tensordot(self._data, other._data, axes=([i], [j])))

    def trace(self, *, axis1: int = 0, axis2: int = 1) -> Tensor:
        """Contract ``axis1`` with ``axis2`` within this tensor.

        The two axes must have the same size; the result keeps the remaining
        indices in order.
        """
        if self.order < 2:
            raise DimensionError("trace requires a tensor of order at least 2")
        i = _as_index(axis1, name="axis1", order=self.order)
        j = _as_index(axis2, name="axis2", order=self.order)
        if i == j:
            raise DimensionError("trace axes must be distinct")
        if self.shape[i] != self.shape[j]:
            raise DimensionError(
                f"cannot trace axes of size {self.shape[i]} and {self.shape[j]}"
            )
        return Tensor(np.trace(self._data, axis1=i, axis2=j))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Tensor):
            return NotImplemented
        return bool(np.array_equal(self._data, other._data))

    def __hash__(self) -> int:
        return hash((self._data.shape, tuple(self._data.ravel().tolist())))

    def __repr__(self) -> str:
        return f"Tensor(shape={self.shape}, data={self._data!r})"


def _parse_subscripts(subscripts: str, operands: tuple[Tensor, ...]) -> None:
    """Validate an einsum ``subscripts`` string against the operands.

    Raises :class:`ShapeError` when the spec is malformed or an operand has the
    wrong order, so callers get an SCW error rather than a bare NumPy one.
    """
    if not isinstance(subscripts, str):
        raise TypeError("subscripts must be a string")
    if "->" in subscripts:
        left, right = subscripts.split("->", 1)
        right = right.strip()
    else:
        left, right = subscripts, None
    terms = [term.strip() for term in left.split(",")]
    if len(terms) != len(operands):
        raise ShapeError(
            f"subscripts describe {len(terms)} operands but {len(operands)} were given"
        )
    for term, operand in zip(terms, operands, strict=True):
        if len(term) != operand.order:
            raise ShapeError(
                f"subscript '{term}' has {len(term)} indices but the operand has "
                f"order {operand.order}"
            )
    labels = "".join(terms) + (right or "")
    if not all(c.isalpha() for c in labels):
        raise ShapeError("subscripts may only contain alphabetic index labels")


def einsum(subscripts: str, *operands: Tensor) -> Tensor:
    """Evaluate an Einstein-summation ``subscripts`` expression over tensors.

    This is the named, readable form of :meth:`Tensor.contract`::

        einsum("ij,jk->ik", a, b)      # matrix product
        einsum("ii->i", a)             # diagonal
        einsum("ij->ji", a)            # transpose
        einsum("i,j->ij", u, v)        # outer product

    The result is always a :class:`Tensor` (a scalar expression yields an
    order-0 tensor).  The subscripts string and operand orders are validated
    first; the arithmetic is delegated to :func:`numpy.einsum`.
    """
    if not operands:
        raise ShapeError("einsum needs at least one operand")
    if not all(isinstance(op, Tensor) for op in operands):
        raise TypeError("einsum operands must be Tensor objects")
    _parse_subscripts(subscripts, operands)
    result = np.einsum(subscripts, *(op.data for op in operands))
    return Tensor(np.asarray(result, dtype=DEFAULT_DTYPE))
