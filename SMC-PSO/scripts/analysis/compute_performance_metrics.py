#======================================================================================\\\
#==================== compute_performance_metrics.py ==================================\\\
#======================================================================================\\\

"""
Performance Metrics Computation for DIP SMC Simulations.

Computes standard control performance metrics from simulation output arrays,
matching the metrics documented in Tutorial 01.

Usage:
    from scripts.analysis.compute_performance_metrics import compute_all_metrics

    # After simulation
    metrics = compute_all_metrics(t, x, u)
    print(f"Settling Time: {metrics['settling_time']:.2f} s")
    print(f"Max Overshoot: {metrics['max_overshoot']:.2f} %")
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, Optional


@dataclass
class PerformanceMetrics:
    """Container for DIP SMC performance metrics."""
    settling_time: float  # seconds
    max_overshoot: float  # percentage
    steady_state_error: float  # radians
    rms_control: float  # Newtons
    peak_control: float  # Newtons
    saturation_percentage: float  # percentage

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for JSON export."""
        return {
            'settling_time': self.settling_time,
            'max_overshoot': self.max_overshoot,
            'steady_state_error': self.steady_state_error,
            'rms_control': self.rms_control,
            'peak_control': self.peak_control,
            'saturation_percentage': self.saturation_percentage
        }

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"""Performance Metrics:
  Settling Time:       {self.settling_time:.2f} s
  Max Overshoot:       {self.max_overshoot:.2f} %
  Steady-State Error:  {self.steady_state_error:.4f} rad ({np.degrees(self.steady_state_error):.2f}°)
  RMS Control Effort:  {self.rms_control:.2f} N
  Peak Control:        {self.peak_control:.2f} N
  Control Saturation:  {self.saturation_percentage:.1f}%"""


def compute_settling_time(
    t: np.ndarray,
    x: np.ndarray,
    threshold: float = 0.02
) -> float:
    """
    Compute settling time for all state variables.

    Settling time is defined as the time after which all state variables
    remain within threshold% of their final values.

    Parameters
    ----------
    t : np.ndarray, shape (N,)
        Time array.
    x : np.ndarray, shape (N, 6)
        State trajectory [x, dx, θ₁, dθ₁, θ₂, dθ₂].
    threshold : float, default=0.02
        Settling threshold as fraction of final value (0.02 = 2%).

    Returns
    -------
    settling_time : float
        Time in seconds when all states settle.
    """
    # Consider last 20% of simulation as steady state
    steady_state_idx = int(0.8 * len(t))

    # Compute final values (average of last 20%)
    final_values = np.mean(x[steady_state_idx:], axis=0)

    # Find last time any state exceeds threshold
    max_settling_idx = 0

    for i in range(x.shape[1]):  # For each state variable
        state = x[:, i]
        final_val = final_values[i]

        # Compute threshold band
        if abs(final_val) < 1e-6:
            # For near-zero final values, use absolute threshold
            threshold_val = 0.01  # 0.01 rad or 0.01 m
        else:
            threshold_val = threshold * abs(final_val)

        # Find indices where state exceeds threshold
        exceed_indices = np.where(np.abs(state - final_val) > threshold_val)[0]

        if len(exceed_indices) > 0:
            max_settling_idx = max(max_settling_idx, exceed_indices[-1])

    # Settling time is the time at max_settling_idx
    if max_settling_idx < len(t) - 1:
        return t[max_settling_idx + 1]
    else:
        return t[-1]


def compute_max_overshoot(
    t: np.ndarray,
    x: np.ndarray
) -> float:
    """
    Compute maximum overshoot for pendulum angles.

    Overshoot is the maximum deviation beyond the final value,
    expressed as a percentage of the final value.

    Parameters
    ----------
    t : np.ndarray, shape (N,)
        Time array.
    x : np.ndarray, shape (N, 6)
        State trajectory [x, dx, θ₁, dθ₁, θ₂, dθ₂].

    Returns
    -------
    max_overshoot : float
        Maximum overshoot percentage across both pendulum angles.
    """
    # Consider last 20% as steady state
    steady_state_idx = int(0.8 * len(t))

    # Pendulum angles are indices 2 and 4
    theta1 = x[:, 2]
    theta2 = x[:, 4]

    # Compute final angles
    final_theta1 = np.mean(theta1[steady_state_idx:])
    final_theta2 = np.mean(theta2[steady_state_idx:])

    # Compute overshoots
    overshoots = []

    for theta, final in [(theta1, final_theta1), (theta2, final_theta2)]:
        peak = np.max(np.abs(theta))

        if abs(final) < 1e-6:
            # For near-zero final values, overshoot is peak angle in radians
            # Convert to percentage relative to 1 radian reference
            overshoot_pct = (peak / 1.0) * 100
        else:
            overshoot_pct = ((peak - abs(final)) / abs(final)) * 100

        overshoots.append(overshoot_pct)

    return max(overshoots)


def compute_steady_state_error(
    t: np.ndarray,
    x: np.ndarray
) -> float:
    """
    Compute steady-state error for pendulum angles.

    Steady-state error is the average absolute deviation from the
    desired upright position (θ₁=θ₂=0) during the final 20% of simulation.

    Parameters
    ----------
    t : np.ndarray, shape (N,)
        Time array.
    x : np.ndarray, shape (N, 6)
        State trajectory [x, dx, θ₁, dθ₁, θ₂, dθ₂].

    Returns
    -------
    steady_state_error : float
        Average absolute error in radians.
    """
    # Consider last 20% as steady state
    steady_state_idx = int(0.8 * len(t))

    # Pendulum angles are indices 2 and 4
    theta1 = x[steady_state_idx:, 2]
    theta2 = x[steady_state_idx:, 4]

    # Desired angles are zero (upright)
    error1 = np.mean(np.abs(theta1))
    error2 = np.mean(np.abs(theta2))

    # Return maximum error
    return max(error1, error2)


def compute_rms_control(
    u: np.ndarray
) -> float:
    """
    Compute RMS (root-mean-square) control effort.

    Parameters
    ----------
    u : np.ndarray, shape (N,)
        Control input array in Newtons.

    Returns
    -------
    rms_control : float
        RMS control effort in Newtons.
    """
    return np.sqrt(np.mean(u**2))


def compute_peak_control(
    u: np.ndarray
) -> float:
    """
    Compute peak control effort.

    Parameters
    ----------
    u : np.ndarray, shape (N,)
        Control input array in Newtons.

    Returns
    -------
    peak_control : float
        Peak absolute control in Newtons.
    """
    return np.max(np.abs(u))


def compute_saturation_percentage(
    u: np.ndarray,
    saturation_limit: float = 150.0
) -> float:
    """
    Compute percentage of time control is saturated.

    Parameters
    ----------
    u : np.ndarray, shape (N,)
        Control input array in Newtons.
    saturation_limit : float, default=150.0
        Saturation limit in Newtons.

    Returns
    -------
    saturation_percentage : float
        Percentage of time control is at saturation limits.
    """
    saturated = np.abs(u) >= (saturation_limit - 1e-3)
    return 100.0 * np.sum(saturated) / len(u)


def compute_all_metrics(
    t: np.ndarray,
    x: np.ndarray,
    u: np.ndarray,
    saturation_limit: float = 150.0
) -> PerformanceMetrics:
    """
    Compute all performance metrics from simulation output.

    Parameters
    ----------
    t : np.ndarray, shape (N,)
        Time array in seconds.
    x : np.ndarray, shape (N, 6)
        State trajectory [x, dx, θ₁, dθ₁, θ₂, dθ₂].
    u : np.ndarray, shape (N,)
        Control input array in Newtons.
    saturation_limit : float, default=150.0
        Control saturation limit in Newtons.

    Returns
    -------
    metrics : PerformanceMetrics
        Container with all computed metrics.

    Examples
    --------
    >>> from src.core.simulation_runner import run_simulation
    >>> from src.controllers.factory import create_controller
    >>> from src.plant.models.lowrank.dynamics import LowRankDIPDynamics
    >>>
    >>> controller = create_controller('classical_smc')
    >>> dynamics = LowRankDIPDynamics()
    >>>
    >>> t, x, u = run_simulation(
    ...     controller=controller,
    ...     dynamics_model=dynamics,
    ...     sim_time=5.0,
    ...     dt=0.001,
    ...     initial_state=np.array([0.1, 0.0, 0.0, 0.0, 0.0, 0.0])
    ... )
    >>>
    >>> metrics = compute_all_metrics(t, x, u)
    >>> print(metrics)
    Performance Metrics:
      Settling Time:       2.45 s
      Max Overshoot:       3.2 %
      Steady-State Error:  0.008 rad (0.46°)
      RMS Control Effort:  12.4 N
      Peak Control:        45.3 N
      Control Saturation:  0.0%
    """
    return PerformanceMetrics(
        settling_time=compute_settling_time(t, x),
        max_overshoot=compute_max_overshoot(t, x),
        steady_state_error=compute_steady_state_error(t, x),
        rms_control=compute_rms_control(u),
        peak_control=compute_peak_control(u),
        saturation_percentage=compute_saturation_percentage(u, saturation_limit)
    )


def validate_against_expected(
    metrics: PerformanceMetrics,
    expected_ranges: Optional[Dict[str, Tuple[float, float]]] = None
) -> Dict[str, bool]:
    """
    Validate metrics against expected ranges from Tutorial 01.

    Parameters
    ----------
    metrics : PerformanceMetrics
        Computed metrics.
    expected_ranges : dict, optional
        Dictionary mapping metric names to (min, max) tuples.
        If None, uses default ranges from Tutorial 01 (lines 391-398).

    Returns
    -------
    validation : dict
        Dictionary mapping metric names to pass/fail booleans.

    Examples
    --------
    >>> metrics = compute_all_metrics(t, x, u)
    >>> validation = validate_against_expected(metrics)
    >>> if all(validation.values()):
    ...     print("All metrics within expected ranges!")
    """
    if expected_ranges is None:
        # Default ranges from Tutorial 01 (lines 391-398)
        expected_ranges = {
            'settling_time': (2.0, 3.0),
            'max_overshoot': (2.0, 5.0),
            'steady_state_error': (0.005, 0.01),
            'rms_control': (10.0, 15.0),
            'peak_control': (40.0, 60.0),
            'saturation_percentage': (0.0, 2.0)
        }

    validation = {}
    metrics_dict = metrics.to_dict()

    for metric_name, (min_val, max_val) in expected_ranges.items():
        value = metrics_dict[metric_name]
        validation[metric_name] = min_val <= value <= max_val

    return validation


if __name__ == "__main__":
    # Example usage
    import sys

    print("Performance Metrics Computation Script")
    print("=" * 50)
    print()
    print("This script provides functions to compute performance metrics")
    print("from DIP SMC simulation output arrays (t, x, u).")
    print()
    print("Usage:")
    print("  from scripts.analysis.compute_performance_metrics import compute_all_metrics")
    print("  metrics = compute_all_metrics(t, x, u)")
    print("  print(metrics)")
    print()
    print("See module docstring for examples.")
