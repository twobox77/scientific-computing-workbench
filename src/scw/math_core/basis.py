"""Basis: an ordered basis of a finite-dimensional real vector space.

A basis lets a vector be written as coordinates.  The implementation keeps the
domain-layer responsibilities: validate that the supplied vectors really form a
basis of the stated space (right count, same space, linearly independent), and
convert in both directions between a vector and its coordinates.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from scw.config import DEFAULT_DTYPE
from scw.exceptions import DimensionError
from scw.math_core.spaces import VectorSpace
from scw.math_core.vector import Vector


class Basis:
    """An ordered basis ``(e_1, ..., e_n)`` of a vector space.

    The basis is given as a non-empty sequence of :class:`Vector` objects that
    share one space and are linearly independent.  Coordinates are relative to
    the given order: ``c`` means ``c_1 e_1 + ... + c_n e_n``.
    """

    __slots__ = ("_vectors", "_space", "_matrix")

    def __init__(self, vectors: Any) -> None:
        vecs: list[Vector] = list(vectors)
        if not vecs:
            raise DimensionError("a basis needs at least one vector")
        if not all(isinstance(v, Vector) for v in vecs):
            raise TypeError("a basis is built from Vector objects")
        space: VectorSpace = vecs[0].space
        for v in vecs:
            if v.space != space:
                raise DimensionError(
                    f"basis vectors must share a space: {space} vs {v.space}"
                )
        if len(vecs) != space.dimension:
            raise DimensionError(
                f"a basis of {space} needs {space.dimension} vectors, got {len(vecs)}"
            )
        matrix = np.column_stack([v.data for v in vecs]).astype(DEFAULT_DTYPE)
        if int(np.linalg.matrix_rank(matrix)) != space.dimension:
            raise DimensionError("the given vectors are linearly dependent")
        self._vectors = tuple(vecs)
        self._space = space
        self._matrix = matrix

    @property
    def space(self) -> VectorSpace:
        """The space this basis spans."""
        return self._space

    @property
    def dimension(self) -> int:
        """Number of basis vectors."""
        return len(self._vectors)

    @property
    def vectors(self) -> tuple[Vector, ...]:
        """The basis vectors, in order."""
        return self._vectors

    def to_matrix(self) -> np.ndarray:
        """Return the basis as a matrix whose columns are the basis vectors."""
        return self._matrix.copy()

    def to_coordinates(self, vector: Vector) -> np.ndarray:
        """Express ``vector`` in this basis, returning its coefficients."""
        if not isinstance(vector, Vector):
            raise TypeError("to_coordinates expects a Vector")
        if vector.space != self._space:
            raise DimensionError(
                f"vector is in {vector.space}, basis spans {self._space}"
            )
        coeffs = np.linalg.solve(self._matrix, vector.data)
        return coeffs.astype(DEFAULT_DTYPE)

    def from_coordinates(self, coefficients: Any) -> Vector:
        """Rebuild a vector from its coefficients in this basis."""
        coeffs = np.asarray(coefficients, dtype=DEFAULT_DTYPE)
        if coeffs.ndim != 1 or coeffs.size != self.dimension:
            raise DimensionError(
                f"expected {self.dimension} coefficients, got shape {coeffs.shape}"
            )
        return Vector(self._matrix @ coeffs, space=self._space)

    def __len__(self) -> int:
        return self.dimension

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Basis):
            return NotImplemented
        return self._space == other._space and all(
            a == b for a, b in zip(self._vectors, other._vectors, strict=True)
        )

    def __hash__(self) -> int:
        return hash((self._space, self._vectors))

    def __repr__(self) -> str:
        return f"Basis(dimension={self.dimension}, space={self._space})"
