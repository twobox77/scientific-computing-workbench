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


class SymbolicError(SCWError, ValueError):
    """A symbolic value cannot be turned into a numeric one, or vice versa."""


class NumericalError(SCWError, ValueError):
    """A numerical routine cannot proceed with the given input."""


class ConvergenceError(SCWError, RuntimeError):
    """An iterative numerical method failed to converge."""


class ExperimentError(SCWError, ValueError):
    """An experiment configuration, run record or result store is invalid."""


__all__ = [
    "SCWError",
    "ConvergenceError",
    "DimensionError",
    "ExperimentError",
    "NonFiniteError",
    "NumericalError",
    "ShapeError",
    "SymbolicError",
]
