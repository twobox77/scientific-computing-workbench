"""Numerical algorithms built on NumPy / SciPy.

This layer accepts the objects defined in :mod:`scw.math_core` but must not
leak its own concerns back into the domain model.
"""

from __future__ import annotations

from scw.numerical.linalg import det, inverse, solve

__all__ = ["det", "inverse", "solve"]
