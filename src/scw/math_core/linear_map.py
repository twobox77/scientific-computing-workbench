"""LinearMap: a linear map between two finite-dimensional spaces."""

from __future__ import annotations

from typing import Any

import numpy as np

from scw.exceptions import DimensionError
from scw.math_core.matrix import Matrix
from scw.math_core.spaces import VectorSpace
from scw.math_core.vector import Vector


class LinearMap:
    """A linear map ``T: domain -> codomain`` represented by a matrix.

    The domain (input) and codomain (output) are explicit.  The stored matrix
    has ``codomain.dimension`` rows and ``domain.dimension`` columns.
    """

    __slots__ = ("_matrix", "_domain", "_codomain")

    def __init__(
        self,
        matrix: Matrix | Any,
        *,
        domain: VectorSpace | None = None,
        codomain: VectorSpace | None = None,
    ) -> None:
        mat = matrix if isinstance(matrix, Matrix) else Matrix(matrix)
        rows, cols = mat.shape
        if codomain is None:
            codomain = VectorSpace(rows)
        if domain is None:
            domain = VectorSpace(cols)
        if codomain.dimension != rows:
            raise DimensionError(
                f"codomain has dimension {codomain.dimension} but matrix has "
                f"{rows} rows"
            )
        if domain.dimension != cols:
            raise DimensionError(
                f"domain has dimension {domain.dimension} but matrix has {cols} columns"
            )
        self._matrix = mat
        self._domain = domain
        self._codomain = codomain

    @classmethod
    def from_matrix(
        cls,
        matrix: Matrix | Any,
        *,
        domain: VectorSpace | None = None,
        codomain: VectorSpace | None = None,
    ) -> LinearMap:
        """Build a map from a matrix (mirrors the plain constructor)."""
        return cls(matrix, domain=domain, codomain=codomain)

    @property
    def matrix(self) -> Matrix:
        """The representing matrix."""
        return self._matrix

    @property
    def domain(self) -> VectorSpace:
        """The input space."""
        return self._domain

    @property
    def codomain(self) -> VectorSpace:
        """The output space."""
        return self._codomain

    def apply(self, vector: Vector) -> Vector:
        """Apply the map, validating the input dimension."""
        if not isinstance(vector, Vector):
            raise TypeError("apply expects a Vector")
        if vector.dimension != self._domain.dimension:
            raise DimensionError(
                f"map expects input dimension {self._domain.dimension}, got "
                f"{vector.dimension}"
            )
        out = self._matrix.data @ vector.data
        return Vector(out, space=self._codomain)

    __call__ = apply

    def compose(self, other: LinearMap) -> LinearMap:
        """Return ``self . other`` (apply ``other`` first, then ``self``)."""
        if not isinstance(other, LinearMap):
            raise TypeError("compose expects a LinearMap")
        if other.codomain.dimension != self.domain.dimension:
            raise DimensionError(
                f"cannot compose: inner dimensions {other.codomain.dimension} "
                f"and {self.domain.dimension} differ"
            )
        composed = self._matrix.data @ other.matrix.data
        return LinearMap(Matrix(composed), domain=other.domain, codomain=self.codomain)

    def __matmul__(self, other: Any) -> LinearMap:
        if not isinstance(other, LinearMap):
            return NotImplemented
        return self.compose(other)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, LinearMap):
            return NotImplemented
        return (
            self._domain == other._domain
            and self._codomain == other._codomain
            and bool(np.array_equal(self._matrix.data, other._matrix.data))
        )

    def __hash__(self) -> int:
        return hash(
            (
                self._domain,
                self._codomain,
                self._matrix.data.shape,
                tuple(self._matrix.data.ravel().tolist()),
            )
        )

    def __repr__(self) -> str:
        return (
            f"LinearMap(domain={self._domain}, codomain={self._codomain}, "
            f"matrix={self._matrix!r})"
        )
