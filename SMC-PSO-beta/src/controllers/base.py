#======================================================================================
#============================== src/controllers/base.py ===============================
#======================================================================================
"""Base controller interface and shared control primitives (M4 Slice 1).

Consolidated from the source `src/controllers/base/` package
(`controller_interface.py` + `control_primitives.py`) into the single
`src/controllers/base.py` node defined in graph.json.

Audit notes applied during port:
- Removed hallucinated AI citation tokens from docstrings (M4 Trap E).
- This module is state-ORDERING-NEUTRAL: it never indexes the state vector by
  component, so it is safe regardless of convention. BUT subclasses and the
  plant are NOT neutral. The project MUST fix one canonical ordering (M4 Trap A)
  and document it here once decided. Until then this docstring states the
  controller-side convention that the source assumed:
      state = [x, x_dot, theta1, theta1_dot, theta2, theta2_dot]   (interleaved)
  NOTE: the corrected plant physics assumes the GROUPED ordering
      state = [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
  Reconcile before wiring controllers to the plant.
"""
from __future__ import annotations

import math
import warnings
from abc import ABC, abstractmethod
from typing import Any, Literal, Optional, Tuple

import numpy as np


# --------------------------------------------------------------------------
# Positivity / range validation utilities
# --------------------------------------------------------------------------
def require_positive(
    value: float | int | None, name: str, *, allow_zero: bool = False
) -> float:
    """Validate that a numeric value is positive (or non-negative).

    Many control gains and time constants must be positive to ensure stability
    in sliding-mode and adaptive control laws. Centralising the check keeps
    error messages and thresholds consistent across controllers and validators.

    Raises
    ------
    ValueError
        If ``value`` is None, not a finite number, or fails the positivity rule.
    """
    if value is None or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number; got {value!r}")
    val = float(value)
    if allow_zero:
        if val < 0.0:
            raise ValueError(f"{name} must be >= 0; got {val}")
    else:
        if val <= 0.0:
            raise ValueError(f"{name} must be > 0; got {val}")
    return val


def require_in_range(
    value: float | int | None,
    name: str,
    *,
    minimum: float,
    maximum: float,
    allow_equal: bool = True,
) -> float:
    """Validate that a numeric value lies within an interval.

    Raises
    ------
    ValueError
        If ``value`` is None, not finite, or lies outside the interval.
    """
    if value is None or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number; got {value!r}")
    val = float(value)
    if allow_equal:
        if val < minimum or val > maximum:
            raise ValueError(
                f"{name} must be in the interval [{minimum}, {maximum}]; got {val}"
            )
    else:
        if val <= minimum or val >= maximum:
            raise ValueError(
                f"{name} must satisfy {minimum} < {name} < {maximum}; got {val}"
            )
    return val


def saturate(
    sigma: float | np.ndarray,
    epsilon: float,
    method: Literal["tanh", "linear"] = "tanh",
) -> float | np.ndarray:
    """Continuous approximation of sign(sigma) within a boundary layer.

    Parameters
    ----------
    sigma : float or np.ndarray
        Sliding surface value(s).
    epsilon : float
        Boundary-layer half-width in sigma-space (must be > 0).
    method : {"tanh", "linear"}
        "tanh" (default) uses tanh(sigma/epsilon); "linear" uses
        clip(sigma/epsilon, -1, 1). tanh is preferred: the linear form
        approximates sign() poorly near zero and can worsen chattering.

    Raises
    ------
    ValueError
        If ``epsilon <= 0`` or an unknown ``method`` is given.
    """
    if epsilon <= 0:
        raise ValueError("boundary layer epsilon must be positive")
    s = np.asarray(sigma, dtype=float) / float(epsilon)
    if method == "tanh":
        return np.tanh(s)
    if method == "linear":
        warnings.warn(
            "The 'linear' switching method implements a piecewise-linear "
            "saturation, which approximates the sign function poorly near zero "
            "and can degrade chattering performance. Prefer 'tanh'.",
            RuntimeWarning,
        )
        return np.clip(s, -1.0, 1.0)
    raise ValueError(f"unknown saturation method: {method!r}")


# --------------------------------------------------------------------------
# Abstract base controller
# --------------------------------------------------------------------------
class ControllerInterface(ABC):
    """Abstract base class for all controllers in the DIP system.

    Defines the common methods every controller must implement so that
    algorithms are interchangeable across the simulation framework.
    """

    def __init__(self, max_force: float = 20.0, dt: float = 0.01):
        self.max_force = require_positive(max_force, "max_force")
        self.dt = require_positive(dt, "dt")
        self._reset_state()

    @abstractmethod
    def compute_control(
        self, state: np.ndarray, reference: Optional[np.ndarray] = None
    ) -> float:
        """Compute the control force for the given state (see ordering note above)."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset the controller internal state."""
        ...

    def _reset_state(self) -> None:
        """Reset internal controller state variables (override if stateful)."""
        pass

    def step(
        self, state: np.ndarray, reference: Optional[np.ndarray] = None
    ) -> Tuple[float, Any]:
        """Perform one control step; returns (clipped_control, info)."""
        control = self.compute_control(state, reference)
        control = float(np.clip(control, -self.max_force, self.max_force))
        info = {
            "saturated": bool(abs(control) >= self.max_force),
            "control_raw": control,
        }
        return control, info

    @property
    def parameters(self) -> dict:
        return {"max_force": self.max_force, "dt": self.dt}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(max_force={self.max_force}, dt={self.dt})"


__all__ = [
    "require_positive",
    "require_in_range",
    "saturate",
    "ControllerInterface",
]
