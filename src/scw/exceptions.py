"""Domain exceptions for SCW.

All SCW-specific errors derive from :class:`SCWError`.  Where the failure is a
kind of value/shape problem, the exception also subclasses the matching
built-in (``ValueError``) so callers can catch either the specific or the
standard exception.
"""

from __future__ import annotations


class SCWError(Exception):
    """Base class for every SCW error."""


class DimensionError(SCWError, ValueError):
    """Operands have incompatible dimensions."""


class ShapeError(SCWError, ValueError):
    """An array does not have the expected shape."""


class NonFiniteError(SCWError, ValueError):
    """Data contains NaN or infinite values."""
