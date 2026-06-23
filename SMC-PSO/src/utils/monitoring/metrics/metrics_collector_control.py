#======================================================================================\
#================ src/utils/monitoring/metrics_collector_control.py ================\
#======================================================================================\

"""
Real-time metrics collection for control system simulations.

This module provides efficient, non-blocking metrics collection during
simulation runs. It integrates with the data model to capture snapshots
and compute performance summaries.
"""

import time
import numpy as np
from typing import Dict, List, Optional, Any, Callable
from collections import deque
import logging

from .data_model import (
    MetricsSnapshot,
    PerformanceSummary,
    DashboardData,
    RunStatus,
    compute_settling_time,
    compute_overshoot,
    compute_chattering_index
)


class ControlMetricsCollector:
    """
    Real-time metrics collector for control system simulations.

    Features:
    - Non-blocking per-step collection (minimal overhead)
    - Configurable sampling rate (collect every N steps)
    - Memory-efficient circular buffers
    - Automatic summary computation
    - Export to multiple formats (CSV, JSON)
    """

    def __init__(self,
                 config: Optional[Dict[str, Any]] = None,
                 sampling_interval: int = 1,
                 max_snapshots: int = 10000):
        """
        Initialize metrics collector.

        Args:
            config: Configuration dictionary
            sampling_interval: Collect every N steps (1 = every step)
            max_snapshots: Maximum snapshots to keep in memory
        """
        self.config = config or {}
        self.sampling_interval = sampling_interval
        self.max_snapshots = max_snapshots

        # Current run data
        self.current_run: Optional[DashboardData] = None
        self.step_counter = 0

        # Temporary storage for efficiency
        self._control_history = deque(maxlen=1000)
        self._error_history = deque(maxlen=1000)

        # Performance tracking
        self._computation_times = []
        self._start_time = None

        # Logger
        self.logger = logging.getLogger("ControlMetricsCollector")

        # Callbacks for real-time updates
        self._update_callbacks: List[Callable[[MetricsSnapshot], None]] = []

    def start_run(self,
                  run_id: str,
                  controller_type: str,
                  scenario: str,
                  config: Optional[Dict[str, Any]] = None) -> None:
        """
        Start a new simulation run.

        Args:
            run_id: Unique identifier for this run
            controller_type: Type of controller being used
            scenario: Scenario name (e.g., "stabilization", "tracking")
            config: Run-specific configuration
        """
        self.current_run = DashboardData(
            run_id=run_id,
            controller=controller_type,
            scenario=scenario,
            config=config or {},
            status=RunStatus.RUNNING,
            start_time=time.time()
        )

        self.step_counter = 0
        self._control_history.clear()
        self._error_history.clear()
        self._computation_times.clear()
        self._start_time = time.time()

        self.logger.info(f"Started run: {run_id} ({controller_type} on {scenario})")

    def add_snapshot(self,
                    state: np.ndarray,
                    control_output: float,
                    time_step: int,
                    timestamp_s: float,
                    computation_time_ms: Optional[float] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a metrics snapshot for the current time step.

        This is the main collection point called during simulation loops.

        Args:
            state: State vector [theta1, theta2, theta1_dot, theta2_dot]
            control_output: Control signal u
            time_step: Current simulation step
            timestamp_s: Current simulation time (seconds)
            computation_time_ms: Controller computation time
            metadata: Additional metadata
        """
        if self.current_run is None:
            raise RuntimeError("No active run. Call start_run() first.")

        self.step_counter += 1

        # Sample at specified interval to reduce memory usage
        if self.step_counter % self.sampling_interval != 0:
            # Still track control signal for chattering metrics
            self._control_history.append(control_output)
            return

        # Extract state components
        theta1 = state[0]
        theta2 = state[1]
        theta1_dot = state[2] if len(state) > 2 else 0.0
        theta2_dot = state[3] if len(state) > 3 else 0.0

        # Compute error norm (distance from upright equilibrium)
        # Upright: theta1 = 0, theta2 = 0, velocities = 0
        error = np.array([theta1, theta2, theta1_dot, theta2_dot])
        error_norm = np.linalg.norm(error)

        # Detect settling (within 2% = 0.02 rad for angles)
        settling_threshold = 0.02
        settling_detected = (abs(theta1) < settling_threshold and
                           abs(theta2) < settling_threshold and
                           abs(theta1_dot) < settling_threshold and
                           abs(theta2_dot) < settling_threshold)

        # Compute instantaneous chattering index
        chattering_idx = 0.0
        if len(self._control_history) > 1:
            recent_controls = list(self._control_history)[-10:]  # Last 10 steps
            variations = np.abs(np.diff(recent_controls))
            chattering_idx = np.mean(variations) if len(variations) > 0 else 0.0

        # Create snapshot
        snapshot = MetricsSnapshot(
            timestamp_s=timestamp_s,
            time_step=time_step,
            controller_type=self.current_run.controller,
            state=state.copy(),
            control_output=control_output,
            error_norm=error_norm,
            angle1_rad=theta1,
            angle2_rad=theta2,
            velocity1_rad_s=theta1_dot,
            velocity2_rad_s=theta2_dot,
            settling_detected=settling_detected,
            chattering_index=chattering_idx,
            control_effort=abs(control_output),
            metadata=metadata or {}
        )

        # Store snapshot
        self.current_run.add_snapshot(snapshot)

        # Track for summary computation
        self._control_history.append(control_output)
        self._error_history.append(error_norm)

        if computation_time_ms is not None:
            self._computation_times.append(computation_time_ms)

        # Notify callbacks
        for callback in self._update_callbacks:
            try:
                callback(snapshot)
            except Exception as e:
                self.logger.error(f"Error in update callback: {e}")

        # Memory management: limit snapshot count
        if len(self.current_run.snapshots) > self.max_snapshots:
            # Keep first and last half
            half = self.max_snapshots // 2
            self.current_run.snapshots = (
                self.current_run.snapshots[:half] +
                self.current_run.snapshots[-half:]
            )
            self.current_run.warnings.append(
                f"Snapshot limit reached. Decimated to {self.max_snapshots} samples."
            )

    def end_run(self, success: bool = True, error_msg: str = "") -> DashboardData:
        """
        End the current run and compute summary metrics.

        Args:
            success: Whether run completed successfully
            error_msg: Error message if failed

        Returns:
            Complete DashboardData with summary
        """
        if self.current_run is None:
            raise RuntimeError("No active run to end.")

        if not success:
            self.current_run.mark_failed(error_msg)
            self.logger.error(f"Run {self.current_run.run_id} failed: {error_msg}")
            return self.current_run

        # Compute performance summary
        summary = self.compute_metrics()

        # Finalize run
        self.current_run.finalize(summary)

        self.logger.info(
            f"Run {self.current_run.run_id} complete. "
            f"Settling time: {summary.settling_time_s:.2f}s, "
            f"Overshoot: {summary.overshoot_pct:.1f}%, "
            f"Score: {summary.get_score():.1f}/100"
        )

        # Return completed run
        completed_run = self.current_run
        self.current_run = None

        return completed_run

    def compute_metrics(self) -> PerformanceSummary:
        """
        Compute aggregate performance metrics from collected snapshots.

        Returns:
            PerformanceSummary with all computed metrics
        """
        if self.current_run is None or len(self.current_run.snapshots) == 0:
            return PerformanceSummary()

        snapshots = self.current_run.snapshots

        # Extract time series
        timestamps, errors = self.current_run.get_time_series('error_norm')
        _, controls = self.current_run.get_time_series('control')
        _, angle1 = self.current_run.get_time_series('angle1')
        _, angle2 = self.current_run.get_time_series('angle2')

        # Time step
        dt = timestamps[1] - timestamps[0] if len(timestamps) > 1 else 0.01

        # Settling time
        settling_time = compute_settling_time(timestamps, errors, threshold=0.02, min_duration=0.5)

        # Rise time (time to reach 90% of final value, approximated)
        rise_time = self._compute_rise_time(timestamps, errors)

        # Overshoot (maximum deviation from equilibrium)
        overshoot_angle1 = compute_overshoot(angle1, setpoint=0.0)
        overshoot_angle2 = compute_overshoot(angle2, setpoint=0.0)
        overshoot_pct = max(overshoot_angle1, overshoot_angle2)

        # Steady-state error (average error in last 10% of simulation)
        steady_state_idx = int(len(errors) * 0.9)
        steady_state_error = np.mean(errors[steady_state_idx:]) if len(errors) > 10 else errors[-1]

        # Energy (integral of u^2)
        energy = np.sum(controls ** 2) * dt

        # Total variation (sum of |u[k+1] - u[k]|)
        total_variation = np.sum(np.abs(np.diff(controls)))

        # Peak control
        peak_control = np.max(np.abs(controls))

        # Stability: check if all states remained bounded
        max_angle = max(np.max(np.abs(angle1)), np.max(np.abs(angle2)))
        bounded_states = max_angle < 2.0  # Consider unstable if > 2 rad (~114 deg)

        # Lyapunov decrease rate (simplified: -d(error^2)/dt)
        lyapunov_proxy = errors ** 2
        lyapunov_decrease_rate = np.mean(np.diff(lyapunov_proxy)) / dt if len(lyapunov_proxy) > 1 else 0.0

        # Chattering metrics
        chattering_idx = compute_chattering_index(controls, dt)
        chattering_amplitude = np.std(np.diff(controls)) if len(controls) > 1 else 0.0
        chattering_total_variation = total_variation

        # Chattering frequency (dominant frequency via FFT)
        chattering_freq = self._estimate_chattering_frequency(controls, dt)

        # Robustness (placeholder - would need disturbance data)
        disturbance_rejection_db = 0.0
        recovery_time_s = 0.0

        # Computational metrics
        avg_comp_time = np.mean(self._computation_times) if self._computation_times else 0.0
        max_comp_time = np.max(self._computation_times) if self._computation_times else 0.0
        deadline_misses = sum(1 for t in self._computation_times if t > dt * 1000)  # Missed if > dt

        # Stability margin (simplified: minimum distance from instability)
        stability_margin = 2.0 - max_angle  # Distance from 2 rad limit

        return PerformanceSummary(
            settling_time_s=settling_time,
            rise_time_s=rise_time,
            overshoot_pct=overshoot_pct,
            steady_state_error=steady_state_error,
            energy_j=energy,
            total_variation=total_variation,
            peak_control=peak_control,
            stability_margin=stability_margin,
            lyapunov_decrease_rate=lyapunov_decrease_rate,
            bounded_states=bounded_states,
            chattering_frequency_hz=chattering_freq,
            chattering_amplitude=chattering_amplitude,
            chattering_total_variation=chattering_total_variation,
            disturbance_rejection_db=disturbance_rejection_db,
            recovery_time_s=recovery_time_s,
            avg_computation_time_ms=avg_comp_time,
            max_computation_time_ms=max_comp_time,
            deadline_misses=deadline_misses
        )

    def get_summary(self) -> Optional[PerformanceSummary]:
        """
        Get current performance summary (without ending run).

        Returns:
            Current PerformanceSummary or None if no run active
        """
        if self.current_run is None:
            return None

        return self.compute_metrics()

    def export_to_csv(self, filepath: str) -> None:
        """
        Export current run snapshots to CSV.

        Args:
            filepath: Output CSV file path
        """
        if self.current_run is None or len(self.current_run.snapshots) == 0:
            raise RuntimeError("No data to export")

        import csv

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'timestamp_s', 'time_step', 'controller',
                'theta1_rad', 'theta2_rad', 'theta1_dot_rad_s', 'theta2_dot_rad_s',
                'control_output', 'error_norm', 'chattering_index', 'settling_detected'
            ])

            # Data rows
            for snap in self.current_run.snapshots:
                writer.writerow([
                    snap.timestamp_s,
                    snap.time_step,
                    snap.controller_type,
                    snap.angle1_rad,
                    snap.angle2_rad,
                    snap.velocity1_rad_s,
                    snap.velocity2_rad_s,
                    snap.control_output,
                    snap.error_norm,
                    snap.chattering_index,
                    snap.settling_detected
                ])

        self.logger.info(f"Exported {len(self.current_run.snapshots)} snapshots to {filepath}")

    def export_to_json(self, filepath: str) -> None:
        """
        Export current run to JSON.

        Args:
            filepath: Output JSON file path
        """
        if self.current_run is None:
            raise RuntimeError("No data to export")

        self.current_run.to_json(filepath)
        self.logger.info(f"Exported run to {filepath}")

    def register_update_callback(self, callback: Callable[[MetricsSnapshot], None]) -> None:
        """
        Register callback for real-time updates.

        Callback will be called after each snapshot is added.

        Args:
            callback: Function accepting MetricsSnapshot
        """
        self._update_callbacks.append(callback)

    def _compute_rise_time(self, timestamps: np.ndarray, errors: np.ndarray) -> float:
        """
        Compute rise time (time to reach 10% of final value).

        Args:
            timestamps: Time array
            errors: Error array

        Returns:
            Rise time in seconds
        """
        if len(errors) == 0:
            return float('inf')

        # Target is 10% of initial error
        initial_error = errors[0]
        target_error = initial_error * 0.1

        # Find first crossing
        crossed_mask = errors < target_error
        if not np.any(crossed_mask):
            return float('inf')

        first_cross_idx = np.argmax(crossed_mask)
        return timestamps[first_cross_idx]

    def _estimate_chattering_frequency(self, control_signal: np.ndarray, dt: float) -> float:
        """
        Estimate dominant chattering frequency using FFT.

        Args:
            control_signal: Control signal array
            dt: Time step

        Returns:
            Dominant frequency in Hz
        """
        if len(control_signal) < 10:
            return 0.0

        try:
            # Compute FFT
            fft_vals = np.fft.fft(control_signal - np.mean(control_signal))
            fft_freq = np.fft.fftfreq(len(control_signal), dt)

            # Find peak frequency (positive frequencies only)
            positive_freq_mask = fft_freq > 0
            magnitudes = np.abs(fft_vals[positive_freq_mask])
            frequencies = fft_freq[positive_freq_mask]

            if len(magnitudes) == 0:
                return 0.0

            peak_idx = np.argmax(magnitudes)
            return frequencies[peak_idx]

        except Exception as e:
            self.logger.warning(f"Failed to estimate chattering frequency: {e}")
            return 0.0


# Export
__all__ = ['ControlMetricsCollector']
