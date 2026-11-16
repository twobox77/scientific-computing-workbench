"""Initial-value ODE solving backed by :func:`scipy.integrate.solve_ivp`.

The right-hand side is written in the domain's terms: it takes a scalar time
and a :class:`~scw.math_core.Vector` state and returns a ``Vector`` (or any
array-like of the same dimension).  The solution is returned as an
:class:`ODESolution` carrying the time grid and the state at each time.

    def rhs(t, y):                 # y' = -y,  y(0) = 1
        return -1.0 * y

    sol = solve_ivp(rhs, (0.0, 5.0), Vector([1.0]), t_eval=[0.0, 5.0])
    sol.final_state                # approx exp(-5) * e_1
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp as _scipy_solve_ivp

from scw.config import DEFAULT_DTYPE
from scw.exceptions import ConvergenceError, DimensionError, NumericalError
from scw.math_core.vector import Vector

#: ODE methods accepted by :func:`solve_ivp` (SciPy's ``solve_ivp`` set).
METHODS = (
    "RK45",
    "RK23",
    "DOP853",
    "Radau",
    "BDF",
    "LSODA",
)


class ODESolution:
    """The result of :func:`solve_ivp`.

    ``t`` holds the time grid and ``y`` the state at each time as an array of
    shape ``(n_points, dimension)``; row ``i`` is the state at ``t[i]``.
    """

    __slots__ = ("_t", "_y", "_status", "_message", "_success", "_method", "_dense")

    def __init__(
        self,
        t: np.ndarray,
        y: np.ndarray,
        *,
        status: int,
        message: str,
        success: bool,
        method: str,
        dense: Callable[[float], np.ndarray] | None = None,
    ) -> None:
        self._t = t
        self._y = y
        self._status = status
        self._message = message
        self._success = success
        self._method = method
        self._dense = dense

    @property
    def t(self) -> np.ndarray:
        """Read-only view of the time grid, shape ``(n_points,)``."""
        view = self._t.view()
        view.flags.writeable = False
        return view

    @property
    def y(self) -> np.ndarray:
        """Read-only view of the states, shape ``(n_points, dimension)``."""
        view = self._y.view()
        view.flags.writeable = False
        return view

    @property
    def dimension(self) -> int:
        """Dimension of the state space."""
        return int(self._y.shape[1])

    @property
    def success(self) -> bool:
        """Whether the integrator reached the end of the interval."""
        return self._success

    @property
    def status(self) -> int:
        """SciPy's status code (0 means success)."""
        return self._status

    @property
    def message(self) -> str:
        """Human-readable status message."""
        return self._message

    @property
    def method(self) -> str:
        """The integration method that was used."""
        return self._method

    @property
    def final_state(self) -> Vector:
        """The state at the last time in the grid."""
        return Vector(self._y[-1])

    def state_at(self, index: int) -> Vector:
        """The state at grid point ``index``."""
        if not -len(self) <= index < len(self):
            raise IndexError(f"grid index {index} out of range for {len(self)} points")
        return Vector(self._y[index])

    def interpolate(self, t: float) -> Vector:
        """The state at an arbitrary time ``t``.

        Requires the solver to have been called with ``dense_output=True``.
        """
        if self._dense is None:
            raise NumericalError(
                "interpolation requires dense_output=True when calling solve_ivp"
            )
        return Vector(np.asarray(self._dense(float(t)), dtype=DEFAULT_DTYPE))

    def __len__(self) -> int:
        return int(self._y.shape[0])

    def __repr__(self) -> str:
        return (
            f"ODESolution(method={self._method!r}, points={len(self)}, "
            f"dimension={self.dimension}, success={self._success})"
        )


def _coerce_y0(y0: Any) -> Vector:
    if isinstance(y0, Vector):
        return y0
    return Vector(y0)


def _validate_t_span(t_span: Any) -> tuple[float, float]:
    try:
        t0, t1 = t_span
    except (TypeError, ValueError) as exc:
        raise NumericalError("t_span must be a (t0, t1) pair") from exc
    t0 = float(t0)
    t1 = float(t1)
    if not (np.isfinite(t0) and np.isfinite(t1)):
        raise NumericalError("t_span bounds must be finite")
    if t0 == t1:
        raise NumericalError("t_span bounds must differ")
    return t0, t1


def _wrap_rhs(
    fun: Callable[[float, Vector], Any], dimension: int
) -> Callable[[float, np.ndarray], np.ndarray]:
    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        value = fun(float(t), Vector(y))
        if isinstance(value, Vector):
            if value.dimension != dimension:
                raise DimensionError(
                    f"rhs returned a vector of dimension {value.dimension}, "
                    f"expected {dimension}"
                )
            arr = value.to_numpy()
        else:
            arr = np.asarray(value, dtype=DEFAULT_DTYPE)
            if arr.shape != (dimension,):
                raise DimensionError(
                    f"rhs returned shape {arr.shape}, expected ({dimension},)"
                )
        if not np.all(np.isfinite(arr)):
            raise NumericalError("rhs returned a non-finite derivative")
        return arr

    return rhs


def solve_ivp(
    fun: Callable[[float, Vector], Any],
    t_span: Sequence[float],
    y0: Vector | Any,
    *,
    method: str = "RK45",
    t_eval: Sequence[float] | None = None,
    rtol: float | None = None,
    atol: float | None = None,
    max_step: float | None = None,
    first_step: float | None = None,
    dense_output: bool = False,
    raise_on_failure: bool = True,
) -> ODESolution:
    """Integrate ``y' = fun(t, y)`` from ``t_span[0]`` to ``t_span[1]``.

    ``fun`` maps ``(t, Vector)`` to the derivative, returned as a ``Vector``
    (or an array-like of the same dimension).  ``y0`` is the initial state.
    The remaining keyword arguments mirror :func:`scipy.integrate.solve_ivp`;
    ``method`` must be one of :data:`METHODS`.

    Raises :class:`~scw.exceptions.ConvergenceError` when the integrator fails
    and ``raise_on_failure`` is true (the default); otherwise the returned
    :class:`ODESolution` reports ``success == False``.
    """
    if not callable(fun):
        raise TypeError("fun must be callable")
    if method not in METHODS:
        raise NumericalError(f"unknown ODE method {method!r}; choose from {METHODS}")
    t0, t1 = _validate_t_span(t_span)
    initial = _coerce_y0(y0)
    rhs = _wrap_rhs(fun, initial.dimension)

    t_eval_array = None if t_eval is None else np.asarray(t_eval, dtype=DEFAULT_DTYPE)

    options: dict[str, Any] = {}
    if rtol is not None:
        options["rtol"] = rtol
    if atol is not None:
        options["atol"] = atol
    if max_step is not None:
        options["max_step"] = max_step
    if first_step is not None:
        options["first_step"] = first_step

    result = _scipy_solve_ivp(
        rhs,
        (t0, t1),
        initial.data,
        method=method,
        t_eval=t_eval_array,
        dense_output=dense_output,
        **options,
    )

    dense = result.sol if dense_output else None
    solution = ODESolution(
        np.asarray(result.t, dtype=DEFAULT_DTYPE),
        np.asarray(result.y, dtype=DEFAULT_DTYPE).T.copy(),
        status=int(result.status),
        message=str(result.message),
        success=bool(result.success),
        method=method,
        dense=dense,
    )
    if raise_on_failure and not solution.success:
        raise ConvergenceError(
            f"ODE integration failed with {method}: {solution.message}"
        )
    return solution
