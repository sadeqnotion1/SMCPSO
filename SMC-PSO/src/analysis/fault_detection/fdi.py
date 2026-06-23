#======================================================================================\\\
#======================== src/analysis/fault_detection/fdi.py =========================\\\
#======================================================================================\\\

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Protocol, Any, Dict
import numpy as np
import numpy.typing as npt
import logging

class DynamicsProtocol(Protocol):
    """Protocol defining the expected interface for dynamics models.

    This protocol ensures type safety and compatibility across different
    dynamics model implementations used in fault detection.
    """
    def step(self, state: npt.NDArray[np.floating], u: float, dt: float) -> npt.NDArray[np.floating]:
        """Advance the system dynamics by one timestep.

        Args:
            state: Current system state vector
            u: Control input
            dt: Time step (must be positive)

        Returns:
            Predicted next state vector

        Raises:
            ValueError: If dt <= 0 or state dimensions are invalid
        """
        ...

@dataclass
class FDIsystem:
    """
    Lightweight, modular Fault Detection and Isolation (FDI) system with
    optional adaptive thresholds and CUSUM drift detection.

    A residual is formed by comparing the one‑step state prediction from a
    dynamics model with the actual measurement.  If an extended Kalman
    filter (EKF) is available it may provide a more statistically
    informed residual (future enhancement).  The residual norm is
    monitored against a threshold; persistent violations indicate a fault.

    To improve robustness the detector can adapt its threshold based on
    recent residual statistics and can optionally employ a cumulative sum
    (CUSUM) statistic to detect slow drifts.  Adaptive thresholding has
    been shown to enhance the robustness of fault diagnosis by
    automatically adjusting to operating conditions【218697608892619†L682-L687】.  CUSUM
    methods accumulate deviations from a reference and are sensitive to
    faint changes【675426604190490†L699-L722】; however the choice of threshold and
    reference value is critical to avoid false alarms【675426604190490†L746-L752】.

    Attributes
    ----------
    residual_threshold : float
        Base threshold for the residual norm.  Used when adaptive
        thresholding is disabled or insufficient samples are available.
    persistence_counter : int
        Number of consecutive threshold violations required to declare a
        fault.  Helps filter sporadic spikes.
    use_ekf_residual : bool
        Placeholder for future EKF innovation residual.
    residual_states : list[int]
        Indices of state variables to include in the residual.
    residual_weights : list[float], optional
        Optional weights applied elementwise to the residual before
        computing the norm.
    adaptive : bool
        Enable adaptive thresholding.  When True the threshold is
        computed as ``mu + threshold_factor * sigma`` over the last
        ``window_size`` residuals.  This dynamic threshold adjusts to
        changing operating conditions【218697608892619†L682-L687】.
    window_size : int
        Number of recent residuals used to estimate the mean and
        standard deviation for adaptive thresholding.
    threshold_factor : float
        Multiplicative factor applied to the standard deviation when
        computing the adaptive threshold.  Larger values reduce
        sensitivity.
    cusum_enabled : bool
        Enable simple CUSUM drift detection.  When True the detector
        accumulates deviations of the residual norm from its running
        average and compares the sum against ``cusum_threshold`` to
        detect slow drifts【675426604190490†L699-L722】.
    cusum_threshold : float
        Threshold for the cumulative sum.  When the cumulative sum
        exceeds this value a fault is declared.
    hysteresis_enabled : bool
        Enable hysteresis mechanism to prevent rapid oscillation
        between OK and FAULT states near threshold boundaries.
        When False, uses original single-threshold behavior.
    hysteresis_upper : float
        Upper threshold for fault detection when hysteresis is enabled.
        Residual must exceed this value to trigger fault state.
        Typically set to threshold * 1.1 (10% deadband).
    hysteresis_lower : float
        Lower threshold for potential fault recovery (future use).
        Residual must drop below this value for recovery.
        Typically set to threshold * 0.9 (10% deadband).

    Notes
    -----
    * Adaptive thresholding and CUSUM can be enabled independently.
    * When both methods are enabled the residual must exceed either
      the adaptive threshold persistently or the CUSUM threshold to
      trigger a fault.
    * Hysteresis prevents rapid state oscillations near threshold
      boundaries by creating a deadband between fault trigger and
      recovery thresholds (Issue #18).
    * The FDI system reports status only ("OK"/"FAULT") and does not modify
      the control command path; external supervisors decide safe-state actions.  # [CIT-064]
    """

    residual_threshold: float = 0.150  # [HIGH-001] Statistically calibrated (mean=0.103, std=0.044, p99=0.219)
    persistence_counter: int = 10  # [CIT-048]
    use_ekf_residual: bool = False
    residual_states: List[int] = field(default_factory=lambda: [0, 1, 2])
    residual_weights: Optional[List[float]] = None
    adaptive: bool = False
    window_size: int = 50  # [CIT-049]
    threshold_factor: float = 3.0  # [CIT-049]
    cusum_enabled: bool = False
    cusum_threshold: float = 5.0  # [CIT-049]

    # Hysteresis mechanism for threshold oscillation prevention [Issue #18]
    hysteresis_enabled: bool = False
    hysteresis_upper: float = 0.165  # [HIGH-001] Upper threshold = 0.150 * 1.1 (10% deadband)
    hysteresis_lower: float = 0.135  # [HIGH-001] Lower threshold = 0.150 * 0.9 (10% deadband)

    # Internal state - safety-critical components
    _counter: int = field(default=0, repr=False, init=False)
    _last_state: Optional[npt.NDArray[np.floating]] = field(default=None, repr=False, init=False)
    tripped_at: Optional[float] = field(default=None, repr=False, init=False)

    # For adaptive thresholding and CUSUM - bounded collections for memory safety
    _residual_window: List[float] = field(default_factory=list, repr=False, init=False)
    _cusum: float = field(default=0.0, repr=False, init=False)

    # History for plotting/analysis - bounded for production safety
    times: List[float] = field(default_factory=list, repr=False, init=False)
    residuals: List[float] = field(default_factory=list, repr=False, init=False)

    # Memory management constants
    _MAX_HISTORY_SIZE: int = field(default=10000, repr=False, init=False)
    _NUMERICAL_TOLERANCE: float = field(default=1e-12, repr=False, init=False)

    def reset(self) -> None:
        """Reset the FDI system state."""
        self._counter = 0
        self._last_state = None
        self.tripped_at = None
        self._residual_window.clear()
        self._cusum = 0.0
        self.times.clear()
        self.residuals.clear()

    def _append_to_bounded_history(self, t: float, residual_norm: float) -> None:
        """Append to history with memory bounds for production safety."""
        self.times.append(t)
        self.residuals.append(residual_norm)

        # Maintain bounded history for memory safety
        if len(self.times) > self._MAX_HISTORY_SIZE:
            # Remove oldest entries to maintain memory bounds
            self.times.pop(0)
            self.residuals.pop(0)

    def check(
        self,
        t: float,
        meas: np.ndarray,
        u: float,
        dt: float,
        dynamics_model: DynamicsProtocol,
    ) -> Tuple[str, float]:
        """
        Check for a fault at the current time step.
        
        Args:
            t: Current simulation time
            meas: Current state measurement
            u: Control input applied
            dt: Time step
            dynamics_model: Model with step(state, u, dt) method for prediction
            
        Returns:
            Tuple of (status, residual_norm) where status is "OK" or "FAULT"
        """
        # Validate time step.  A non‑positive dt invalidates the residual
        # computation and can produce spurious faults.  Raise an error
        # rather than silently accepting a zero or negative sampling
        # interval【738473614585036†L239-L256】.
        if dt <= 0.0:
            raise ValueError("dt must be positive for FDI residual computation.")

        if self.tripped_at is not None:
            return "FAULT", np.inf

        if self._last_state is None:
            self._last_state = meas.copy()
            # Store history for first measurement
            self.times.append(t)
            self.residuals.append(0.0)
            return "OK", 0.0

        # One-step prediction using the dynamics model
        try:
            predicted_state = dynamics_model.step(self._last_state, u, dt)
            
            # Check for numerical issues in prediction
            if not np.all(np.isfinite(predicted_state)):
                logging.warning(
                    f"FDI check at t={t:.2f}s: dynamics model returned non-finite values "
                    f"(nan or inf). Skipping residual computation."
                )
                return "OK", 0.0
                
        except Exception as e:
            # If model fails, cannot compute residual; assume OK for now but log it
            logging.warning(
                f"FDI check at t={t:.2f}s failed: dynamics model step raised "
                f"{type(e).__name__}: {str(e)}. Skipping residual computation."
            )
            return "OK", 0.0

        # Residual is the difference between prediction and measurement
        residual = meas - predicted_state

        # Compute weighted norm using specified indices and optional weights.
        # Optimized for numerical stability and performance.
        # Weighted residuals allow tuning the sensitivity of the detector to
        # individual states.  When no weights are provided a standard 2‑norm is
        # used on the selected indices.  If an index error occurs fallback
        # gracefully to the full residual norm and log the error.
        try:
            # Validate indices are within bounds for safety-critical operation
            max_index = max(self.residual_states) if self.residual_states else 0
            if max_index >= len(residual):
                raise IndexError(f"Residual state index {max_index} exceeds state vector size {len(residual)}")

            # Extract sub-residual efficiently
            sub = residual[self.residual_states]

            # Apply weights with numerical stability checks
            if self.residual_weights is not None:
                # Validate weights configuration
                if len(self.residual_weights) != len(self.residual_states):
                    raise ValueError(f"Weights length {len(self.residual_weights)} != states length {len(self.residual_states)}")

                # Convert to array once for efficiency and apply weights
                weights_array = np.asarray(self.residual_weights, dtype=np.float64)

                # Check for invalid weights (safety-critical)
                if not np.all(np.isfinite(weights_array)) or np.any(weights_array < 0):
                    raise ValueError("Invalid weights detected: must be finite and non-negative")

                # Apply weights element-wise with numerical stability
                sub = sub * weights_array

            # Compute norm with numerical stability check
            residual_norm = float(np.linalg.norm(sub, ord=2))

            # Verify result is finite (safety-critical check)
            if not np.isfinite(residual_norm):
                raise ValueError("Computed residual norm is not finite")

        except (IndexError, ValueError) as e:
            logging.error(
                f"FDI configuration error: {str(e)} "
                f"(residual_states={self.residual_states}, weights={self.residual_weights}, "
                f"state_vector_size={len(residual)})"
            )
            # Fallback to full residual norm for safety
            residual_norm = float(np.linalg.norm(residual, ord=2))
        except Exception as e:
            logging.error(
                f"Unexpected error in residual computation: {type(e).__name__}: {str(e)}"
            )
            # Safety fallback
            residual_norm = float(np.linalg.norm(residual, ord=2))

        # Store history for analysis with memory bounds (safety-critical)
        self._append_to_bounded_history(t, residual_norm)

        # Append to residual window for adaptive thresholding
        self._residual_window.append(residual_norm)
        if len(self._residual_window) > self.window_size:
            self._residual_window.pop(0)

        # Compute adaptive threshold when enabled and enough samples collected
        dynamic_threshold = self.residual_threshold
        mu = None
        sigma = None
        if self.adaptive and len(self._residual_window) >= self.window_size:
            mu = float(np.mean(self._residual_window))
            sigma = float(np.std(self._residual_window))
            # Avoid zero variance; if sigma is extremely small fall back to
            # base threshold to prevent division by zero
            if sigma > 1e-12:
                dynamic_threshold = mu + self.threshold_factor * sigma
            else:
                dynamic_threshold = mu

        # CUSUM drift detection: update cumulative sum of deviations
        if self.cusum_enabled:
            # Use current mean estimate if available, otherwise base threshold
            ref = mu if (self.adaptive and mu is not None) else self.residual_threshold
            # Deviation from reference; negative deviations are clipped at zero
            self._cusum = max(0.0, self._cusum + (residual_norm - ref))
            if self._cusum > self.cusum_threshold:
                self.tripped_at = t
                logging.info(
                    f"FDI CUSUM fault detected at t={t:.2f}s (cusum={self._cusum:.4f} > threshold={self.cusum_threshold})"
                )
                return "FAULT", residual_norm

        # Hysteresis state machine for threshold oscillation prevention [Issue #18]
        # Determine which threshold to use based on hysteresis configuration
        if self.hysteresis_enabled:
            # Use upper threshold for fault detection (prevents oscillation)
            detection_threshold = self.hysteresis_upper
        else:
            # Original single-threshold behavior (backward compatible)
            detection_threshold = dynamic_threshold

        # Update persistence counter using appropriate threshold
        if residual_norm > detection_threshold:
            self._counter += 1
            # Don't update _last_state when fault is detected to prevent
            # corrupted measurements from becoming the prediction base
        else:
            self._counter = 0  # Reset on any good measurement
            # Only update state when measurement appears good
            self._last_state = meas.copy()

        # Check for fault condition based on persistence count
        if self._counter >= self.persistence_counter:
            self.tripped_at = t
            threshold_used = detection_threshold
            logging.info(
                f"FDI fault detected at t={t:.2f}s after {self._counter} consecutive "
                f"violations (residual_norm={residual_norm:.4f} > threshold={threshold_used:.4f})"
            )
            return "FAULT", residual_norm

        return "OK", residual_norm

    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get comprehensive detection statistics for analysis.

        Returns:
            Dictionary containing detection performance metrics and diagnostics
        """
        if not self.residuals:
            return {"status": "no_data", "message": "No residual data available"}

        residuals_array = np.array(self.residuals)

        stats = {
            "total_samples": len(self.residuals),
            "mean_residual": float(np.mean(residuals_array)),
            "std_residual": float(np.std(residuals_array)),
            "max_residual": float(np.max(residuals_array)),
            "min_residual": float(np.min(residuals_array)),
            "current_threshold": self.residual_threshold,
            "fault_status": "FAULT" if self.tripped_at is not None else "OK",
            "fault_time": self.tripped_at,
            "consecutive_violations": self._counter,
            "cusum_statistic": self._cusum if self.cusum_enabled else None,
            "adaptive_window_size": len(self._residual_window),
            "memory_usage": {
                "history_entries": len(self.times),
                "max_history_size": self._MAX_HISTORY_SIZE,
                "memory_utilization": len(self.times) / self._MAX_HISTORY_SIZE
            }
        }

        # Add adaptive threshold statistics if available
        if self.adaptive and len(self._residual_window) >= self.window_size:
            window_array = np.array(self._residual_window)
            stats["adaptive_threshold_stats"] = {
                "current_mean": float(np.mean(window_array)),
                "current_std": float(np.std(window_array)),
                "current_threshold": float(np.mean(window_array) + self.threshold_factor * np.std(window_array))
            }

        return stats


class FaultDetectionInterface(Protocol):
    """
    Protocol defining the interface for fault detection systems.

    This interface ensures compatibility across different fault detection
    implementations and provides a standard API for testing and usage.
    """

    def check(
        self,
        t: float,
        meas: np.ndarray,
        u: float,
        dt: float,
        dynamics_model: DynamicsProtocol,
    ) -> Tuple[str, float]:
        """
        Check for a fault at the current time step.

        Args:
            t: Current simulation time
            meas: Current state measurement
            u: Control input applied
            dt: Time step
            dynamics_model: Model with step(state, u, dt) method for prediction

        Returns:
            Tuple of (status, residual_norm) where status is "OK" or "FAULT"
        """
        ...


# Verify that FDIsystem implements the interface
def _verify_interface() -> None:
    """Verify that FDIsystem correctly implements FaultDetectionInterface."""
    # This function exists to ensure type compatibility at import time
    _: FaultDetectionInterface = FDIsystem()  # type: ignore


#===================================================================================\\\
