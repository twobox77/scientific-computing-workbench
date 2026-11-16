"""Vector spaces used to give domain objects their semantics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VectorSpace:
    """A finite-dimensional real vector space.

    The space carries a dimension and an optional human-readable name.  Two
    spaces are equal when their dimension and name match, which is what lets
    :class:`~scw.math_core.vector.Vector` reject operations between vectors
    from different (named) spaces.
    """

    dimension: int
    name: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.dimension, int):
            raise TypeError("dimension must be an int")
        if self.dimension <= 0:
            raise ValueError("dimension must be positive")

    def __str__(self) -> str:
        if self.name is None:
            return f"R^{self.dimension}"
        return f"{self.name} (R^{self.dimension})"
