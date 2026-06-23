#======================================================================================\
#===================== src/utils/monitoring/data_model.py =====================\
#======================================================================================\

"""
Data models for performance monitoring dashboard.

This module defines data structures for capturing, storing, and analyzing
control system performance metrics across simulation runs.
"""

import time
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json


class RunStatus(Enum):
    """Simulation run status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    PAUSED = "paused"


class ControllerType(Enum):
    """Supported controller types."""
    CLASSICAL_SMC = "classical_smc"
    STA_SMC = "sta_smc"
    ADAPTIVE_SMC = "adaptive_smc"
    HYBRID_ADAPTIVE_STA = "hybrid_adaptive_sta_smc"
    SWING_UP_SMC = "swing_up_smc"
    MPC = "mpc_controller"
    PID = "pid_controller"


@dataclass
class MetricsSnapshot:
    """
    Single time-step metrics snapshot.

    Captures instantaneous state of the control system at one time step.
    Used for real-time monitoring and detailed time-series analysis.
    """
    # Timestamp
    timestamp_s: float
    time_step: int

    # Controller info
    controller_type: str

    # State vector [theta1, theta2, theta1_dot, theta2_dot]
    state: np.ndarray

    # Control output
    control_output: float

    # Instantaneous metrics
    error_norm: float  # ||e|| = sqrt(sum(e_i^2))
    angle1_rad: float  # theta1
    angle2_rad: float  # theta2
    velocity1_rad_s: float  # theta1_dot
    velocity2_rad_s: float  # theta2_dot

    # Performance indicators
    settling_detected: bool = False  # Within settling band?
    chattering_index: float = 0.0  # Instantaneous chattering metric
    control_effort: float = 0.0  # |u|

    # Optional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'timestamp_s': self.timestamp_s,
            'time_step': self.time_step,
            'controller_type': self.controller_type,
            'state': self.state.tolist() if isinstance(self.state, np.ndarray) else self.state,
            'control_output': self.control_output,
            'error_norm': self.error_norm,
            'angle1_rad': self.angle1_rad,
            'angle2_rad': self.angle2_rad,
            'velocity1_rad_s': self.velocity1_rad_s,
            'velocity2_rad_s': self.velocity2_rad_s,
            'settling_detected': self.settling_detected,
            'chattering_index': self.chattering_index,
            'control_effort': self.control_effort,
            'metadata': self.metadata
        }


@dataclass
class PerformanceSummary:
    """
    Aggregated performance metrics for a complete simulation run.

    These metrics are computed after simulation completes and provide
    a comprehensive assessment of controller performance.
    """
    # Time-domain metrics
    settling_time_s: float = float('inf')  # Time to reach and stay in 2% band
    rise_time_s: float = float('inf')  # Time to reach 90% of setpoint
    overshoot_pct: float = 0.0  # Maximum overshoot percentage
    steady_state_error: float = 0.0  # Final error magnitude

    # Energy and effort
    energy_j: float = 0.0  # Integral of u^2 over time
    total_variation: float = 0.0  # Sum of |u[k+1] - u[k]|
    peak_control: float = 0.0  # max|u|

    # Stability metrics
    stability_margin: float = 0.0  # Minimum distance to instability
    lyapunov_decrease_rate: float = 0.0  # Average dV/dt (should be negative)
    bounded_states: bool = True  # All states remained bounded?

    # Chattering metrics
    chattering_frequency_hz: float = 0.0  # Dominant chattering frequency
    chattering_amplitude: float = 0.0  # Average chattering magnitude
    chattering_total_variation: float = 0.0  # Total variation metric

    # Robustness (if disturbances applied)
    disturbance_rejection_db: float = 0.0  # Attenuation in dB
    recovery_time_s: float = 0.0  # Time to recover after disturbance

    # Computational metrics
    avg_computation_time_ms: float = 0.0
    max_computation_time_ms: float = 0.0
    deadline_misses: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def get_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        """
        Compute weighted performance score (0-100).

        Higher is better. Default weights emphasize settling time,
        overshoot, and steady-state error.
        """
        if weights is None:
            weights = {
                'settling_time': 0.25,
                'overshoot': 0.20,
                'steady_state_error': 0.20,
                'energy': 0.15,
                'chattering': 0.10,
                'stability': 0.10
            }

        # Normalize each metric to 0-100 (lower is better, so invert)
        score = 0.0

        # Settling time (penalize > 5s heavily)
        if self.settling_time_s < float('inf'):
            settling_score = max(0, 100 - (self.settling_time_s / 5.0) * 100)
            score += weights.get('settling_time', 0.25) * settling_score

        # Overshoot (penalize > 20% heavily)
        overshoot_score = max(0, 100 - (self.overshoot_pct / 20.0) * 100)
        score += weights.get('overshoot', 0.20) * overshoot_score

        # Steady-state error (penalize > 0.1 rad)
        ss_error_score = max(0, 100 - (self.steady_state_error / 0.1) * 100)
        score += weights.get('steady_state_error', 0.20) * ss_error_score

        # Energy (penalize high energy use)
        energy_score = max(0, 100 - min(100, self.energy_j / 100.0 * 100))
        score += weights.get('energy', 0.15) * energy_score

        # Chattering (penalize amplitude > 1.0)
        chattering_score = max(0, 100 - min(100, self.chattering_amplitude * 100))
        score += weights.get('chattering', 0.10) * chattering_score

        # Stability (binary: bounded or not)
        stability_score = 100.0 if self.bounded_states else 0.0
        score += weights.get('stability', 0.10) * stability_score

        return score


@dataclass
class DashboardData:
    """
    Complete dataset for a single simulation run.

    Contains all snapshots plus summary statistics. This is the primary
    data structure passed to the dashboard for visualization.
    """
    # Run identification
    run_id: str
    controller: str
    scenario: str

    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)

    # Time-series data
    snapshots: List[MetricsSnapshot] = field(default_factory=list)

    # Summary statistics
    summary: Optional[PerformanceSummary] = None

    # Run metadata
    status: RunStatus = RunStatus.PENDING
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_s: float = 0.0

    # Errors and warnings
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_snapshot(self, snapshot: MetricsSnapshot) -> None:
        """Add a new metrics snapshot."""
        self.snapshots.append(snapshot)

    def finalize(self, summary: PerformanceSummary) -> None:
        """Finalize the run with summary statistics."""
        self.summary = summary
        self.end_time = time.time()
        self.duration_s = self.end_time - self.start_time
        self.status = RunStatus.COMPLETE

    def mark_failed(self, error_msg: str) -> None:
        """Mark run as failed."""
        self.status = RunStatus.FAILED
        self.errors.append(error_msg)
        self.end_time = time.time()
        self.duration_s = self.end_time - self.start_time

    def get_time_series(self, metric: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract time series for a specific metric.

        Returns:
            (timestamps, values) as numpy arrays
        """
        if not self.snapshots:
            return np.array([]), np.array([])

        timestamps = np.array([s.timestamp_s for s in self.snapshots])

        if metric == 'angle1':
            values = np.array([s.angle1_rad for s in self.snapshots])
        elif metric == 'angle2':
            values = np.array([s.angle2_rad for s in self.snapshots])
        elif metric == 'velocity1':
            values = np.array([s.velocity1_rad_s for s in self.snapshots])
        elif metric == 'velocity2':
            values = np.array([s.velocity2_rad_s for s in self.snapshots])
        elif metric == 'control':
            values = np.array([s.control_output for s in self.snapshots])
        elif metric == 'error_norm':
            values = np.array([s.error_norm for s in self.snapshots])
        elif metric == 'chattering':
            values = np.array([s.chattering_index for s in self.snapshots])
        else:
            raise ValueError(f"Unknown metric: {metric}")

        return timestamps, values

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'run_id': self.run_id,
            'controller': self.controller,
            'scenario': self.scenario,
            'config': self.config,
            'snapshots': [s.to_dict() for s in self.snapshots],
            'summary': self.summary.to_dict() if self.summary else None,
            'status': self.status.value,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_s': self.duration_s,
            'errors': self.errors,
            'warnings': self.warnings
        }

    def to_json(self, filepath: str) -> None:
        """Save to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_json(cls, filepath: str) -> 'DashboardData':
        """Load from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Reconstruct snapshots
        snapshots = []
        for s_dict in data.get('snapshots', []):
            snapshot = MetricsSnapshot(
                timestamp_s=s_dict['timestamp_s'],
                time_step=s_dict['time_step'],
                controller_type=s_dict['controller_type'],
                state=np.array(s_dict['state']),
                control_output=s_dict['control_output'],
                error_norm=s_dict['error_norm'],
                angle1_rad=s_dict['angle1_rad'],
                angle2_rad=s_dict['angle2_rad'],
                velocity1_rad_s=s_dict['velocity1_rad_s'],
                velocity2_rad_s=s_dict['velocity2_rad_s'],
                settling_detected=s_dict.get('settling_detected', False),
                chattering_index=s_dict.get('chattering_index', 0.0),
                control_effort=s_dict.get('control_effort', 0.0),
                metadata=s_dict.get('metadata', {})
            )
            snapshots.append(snapshot)

        # Reconstruct summary
        summary = None
        if data.get('summary'):
            summary = PerformanceSummary(**data['summary'])

        return cls(
            run_id=data['run_id'],
            controller=data['controller'],
            scenario=data['scenario'],
            config=data.get('config', {}),
            snapshots=snapshots,
            summary=summary,
            status=RunStatus(data['status']),
            start_time=data['start_time'],
            end_time=data.get('end_time'),
            duration_s=data.get('duration_s', 0.0),
            errors=data.get('errors', []),
            warnings=data.get('warnings', [])
        )


@dataclass
class ComparisonData:
    """
    Data structure for comparing multiple simulation runs.

    Used for controller benchmarking and parameter sweep analysis.
    """
    runs: List[DashboardData] = field(default_factory=list)
    comparison_id: str = ""
    created_at: float = field(default_factory=time.time)

    def add_run(self, run: DashboardData) -> None:
        """Add a run to the comparison."""
        self.runs.append(run)

    def get_ranking(self, metric: str = 'score') -> List[Tuple[str, float]]:
        """
        Rank runs by performance metric.

        Returns:
            List of (controller_name, metric_value) sorted best to worst
        """
        rankings = []

        for run in self.runs:
            if run.summary is None:
                continue

            if metric == 'score':
                value = run.summary.get_score()
            elif hasattr(run.summary, metric):
                value = getattr(run.summary, metric)
            else:
                continue

            rankings.append((run.controller, value))

        # Sort based on metric (lower is better for most metrics except score)
        if metric == 'score':
            rankings.sort(key=lambda x: x[1], reverse=True)  # Higher score is better
        else:
            rankings.sort(key=lambda x: x[1])  # Lower is better

        return rankings

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'comparison_id': self.comparison_id,
            'created_at': self.created_at,
            'runs': [run.to_dict() for run in self.runs]
        }


# Utility functions for metrics computation

def compute_settling_time(timestamps: np.ndarray, errors: np.ndarray,
                         threshold: float = 0.02, min_duration: float = 0.5) -> float:
    """
    Compute settling time (time to reach and stay within threshold).

    Args:
        timestamps: Time array
        errors: Error norm array
        threshold: Settling threshold (2% by default)
        min_duration: Minimum time to stay settled (0.5s by default)

    Returns:
        Settling time in seconds, or inf if never settled
    """
    if len(timestamps) == 0:
        return float('inf')

    # Find first point where error < threshold
    settled_mask = errors < threshold

    if not np.any(settled_mask):
        return float('inf')

    # Find continuous settled regions
    first_settled_idx = np.argmax(settled_mask)

    # Check if it stays settled
    dt = timestamps[1] - timestamps[0] if len(timestamps) > 1 else 0.01
    min_steps = int(min_duration / dt)

    for i in range(first_settled_idx, len(errors) - min_steps):
        if np.all(errors[i:i+min_steps] < threshold):
            return timestamps[i]

    return float('inf')


def compute_overshoot(values: np.ndarray, setpoint: float = 0.0) -> float:
    """
    Compute maximum overshoot percentage.

    Args:
        values: Time series values
        setpoint: Target setpoint

    Returns:
        Overshoot percentage
    """
    if len(values) == 0:
        return 0.0

    max_val = np.max(np.abs(values - setpoint))
    return (max_val / (abs(setpoint) + 1e-9)) * 100.0


def compute_chattering_index(control_signal: np.ndarray, dt: float) -> float:
    """
    Compute chattering index from control signal variations.

    Args:
        control_signal: Control signal time series
        dt: Time step

    Returns:
        Chattering index (total variation / time)
    """
    if len(control_signal) < 2:
        return 0.0

    total_variation = np.sum(np.abs(np.diff(control_signal)))
    duration = len(control_signal) * dt

    return total_variation / duration


# Export all data models
__all__ = [
    'RunStatus',
    'ControllerType',
    'MetricsSnapshot',
    'PerformanceSummary',
    'DashboardData',
    'ComparisonData',
    'compute_settling_time',
    'compute_overshoot',
    'compute_chattering_index'
]
