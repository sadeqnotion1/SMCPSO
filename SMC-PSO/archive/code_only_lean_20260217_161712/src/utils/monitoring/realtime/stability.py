#======================================================================================\\\
#========================= src/utils/monitoring/stability.py ==========================\\\
#======================================================================================\\\

"""
Lyapunov Decrease Ratio (LDR) and stability monitoring for control systems.

Implements the stability monitoring solution from Issue #1 resolution plan,
including LDR monitoring, saturation tracking, and dynamics conditioning.

Thread Safety: All counters use AtomicCounter for race-free increments.
"""

from __future__ import annotations
import time
from typing import List, Dict, Any, Optional
import numpy as np
from collections import deque

from src.utils.infrastructure.threading import AtomicCounter


class LyapunovDecreaseMonitor:
    """Monitor Lyapunov Decrease Ratio for stability assessment.

    Implements LDR monitoring as specified in Issue #1 resolution:
    - Alert when LDR < 95% over 200-500ms rolling window (post-transient)
    - Track sigma*sigma_dot for sliding surface analysis
    """

    def __init__(self, window_size_ms: float = 300.0, dt: float = 0.01,
                 ldr_threshold: float = 0.95, transient_time: float = 1.0):
        """Initialize LDR monitor.

        Parameters
        ----------
        window_size_ms : float
            Rolling window size in milliseconds (200-500ms recommended)
        dt : float
            Simulation timestep in seconds
        ldr_threshold : float
            LDR threshold below which to trigger alert (0.95 = 95%)
        transient_time : float
            Transient period to ignore in seconds
        """
        self.window_size_ms = window_size_ms
        self.dt = dt
        self.ldr_threshold = ldr_threshold
        self.transient_time = transient_time

        # Convert window size to number of samples
        self.window_samples = max(1, int(window_size_ms / 1000.0 / dt))
        self.transient_samples = int(transient_time / dt)

        # Sliding surface and derivative history
        self.sigma_history: deque = deque(maxlen=self.window_samples + 1)
        self.sigma_dot_history: deque = deque(maxlen=self.window_samples)

        # Lyapunov function history (V = 0.5 * sigma^2)
        self.lyapunov_history: deque = deque(maxlen=self.window_samples)

        # Monitoring state (thread-safe atomic counters)
        self.sample_count = AtomicCounter(0)
        self.alert_count = AtomicCounter(0)
        self.last_ldr = 1.0
        self.alert_active = False

    def update(self, sigma: np.ndarray) -> Dict[str, Any]:
        """Update monitor with new sliding surface values.

        Parameters
        ----------
        sigma : np.ndarray
            Current sliding surface vector

        Returns
        -------
        dict
            Monitoring results with LDR, alert status, and metrics
        """
        current_count = self.sample_count.increment()

        # Store sigma values
        self.sigma_history.append(sigma.copy())

        # Compute sigma_dot if we have previous sample
        if len(self.sigma_history) >= 2:
            sigma_prev = self.sigma_history[-2]
            sigma_dot = (sigma - sigma_prev) / self.dt
            self.sigma_dot_history.append(sigma_dot)

            # Compute Lyapunov function V = 0.5 * ||sigma||^2
            lyapunov_val = 0.5 * np.sum(sigma**2)
            self.lyapunov_history.append(lyapunov_val)

        # Skip analysis during transient period
        if current_count <= self.transient_samples:
            return {
                'ldr': 1.0,
                'alert': False,
                'status': 'transient',
                'sample_count': current_count,
                'sigma_dot_sigma': 0.0
            }

        # Compute LDR if we have enough samples
        if len(self.lyapunov_history) >= self.window_samples:
            self.last_ldr = self._compute_ldr()

            # Check for alert condition
            self.alert_active = self.last_ldr < self.ldr_threshold
            if self.alert_active:
                self.alert_count.increment()

        # Compute sigma*sigma_dot for reachability analysis
        sigma_dot_sigma = 0.0
        if len(self.sigma_dot_history) > 0:
            sigma_dot = self.sigma_dot_history[-1]
            sigma_dot_sigma = np.sum(sigma * sigma_dot)

        return {
            'ldr': self.last_ldr,
            'alert': self.alert_active,
            'status': 'monitoring',
            'sample_count': self.sample_count.get(),
            'alert_count': self.alert_count.get(),
            'sigma_dot_sigma': sigma_dot_sigma,
            'lyapunov_value': self.lyapunov_history[-1] if self.lyapunov_history else 0.0
        }

    def _compute_ldr(self) -> float:
        """Compute Lyapunov Decrease Ratio over the rolling window."""
        if len(self.lyapunov_history) < 2:
            return 1.0

        lyapunov_vals = np.array(list(self.lyapunov_history))
        lyapunov_decreases = np.diff(lyapunov_vals)

        # Count decreasing samples
        decreasing_count = np.sum(lyapunov_decreases < 0)
        total_count = len(lyapunov_decreases)

        return decreasing_count / total_count if total_count > 0 else 1.0

    def reset(self) -> None:
        """Reset all monitoring state."""
        self.sigma_history.clear()
        self.sigma_dot_history.clear()
        self.lyapunov_history.clear()
        self.sample_count.reset()
        self.alert_count.reset()
        self.last_ldr = 1.0
        self.alert_active = False


class SaturationMonitor:
    """Monitor actuator saturation duty and rate-limit violations.

    Implements saturation monitoring as specified in Issue #1 resolution:
    - Alert when duty > 20-30% or rate hits > 1% beyond transient
    """

    def __init__(self, max_force: float = 150.0, dt: float = 0.01,
                 duty_threshold: float = 0.2, rate_hit_threshold: float = 0.01,
                 transient_time: float = 1.0, window_size_ms: float = 1000.0):
        """Initialize saturation monitor.

        Parameters
        ----------
        max_force : float
            Maximum actuator force limit
        dt : float
            Simulation timestep
        duty_threshold : float
            Saturation duty threshold (0.2 = 20%)
        rate_hit_threshold : float
            Rate limit hit threshold (0.01 = 1%)
        transient_time : float
            Transient period to ignore
        window_size_ms : float
            Rolling window for statistics
        """
        self.max_force = max_force
        self.dt = dt
        self.duty_threshold = duty_threshold
        self.rate_hit_threshold = rate_hit_threshold
        self.transient_time = transient_time

        self.window_samples = max(1, int(window_size_ms / 1000.0 / dt))
        self.transient_samples = int(transient_time / dt)

        # Force and rate history
        self.force_history: deque = deque(maxlen=self.window_samples)
        self.rate_history: deque = deque(maxlen=self.window_samples)

        # Monitoring state (thread-safe atomic counters)
        self.sample_count = AtomicCounter(0)
        self.saturation_count = AtomicCounter(0)
        self.rate_hit_count = AtomicCounter(0)
        self.continuous_saturation_time = 0.0
        self.max_continuous_saturation = 0.0
        self.last_force = 0.0

    def update(self, force: float) -> Dict[str, Any]:
        """Update monitor with new control force.

        Parameters
        ----------
        force : float
            Current control force

        Returns
        -------
        dict
            Saturation monitoring results
        """
        current_count = self.sample_count.increment()

        # Store force
        self.force_history.append(force)

        # Compute rate if we have previous sample
        rate = 0.0
        if current_count > 1:
            rate = abs(force - self.last_force) / self.dt
            self.rate_history.append(rate)

        self.last_force = force

        # Check saturation
        is_saturated = abs(force) >= self.max_force * 0.99  # 99% of max
        if is_saturated:
            self.saturation_count.increment()
            self.continuous_saturation_time += self.dt
        else:
            if self.continuous_saturation_time > self.max_continuous_saturation:
                self.max_continuous_saturation = self.continuous_saturation_time
            self.continuous_saturation_time = 0.0

        # Check rate limiting (assuming max rate = max_force / dt)
        max_rate = self.max_force / self.dt
        is_rate_limited = rate >= max_rate * 0.99
        if is_rate_limited:
            self.rate_hit_count.increment()

        # Skip analysis during transient
        if current_count <= self.transient_samples:
            return {
                'duty': 0.0,
                'rate_hit_rate': 0.0,
                'alert': False,
                'status': 'transient',
                'continuous_saturation_ms': 0.0
            }

        # Compute metrics over rolling window
        window_samples = min(self.window_samples, len(self.force_history))
        if window_samples == 0:
            return {'duty': 0.0, 'rate_hit_rate': 0.0, 'alert': False, 'status': 'no_data'}

        # Saturation duty in window
        recent_forces = list(self.force_history)[-window_samples:]
        saturated_samples = sum(1 for f in recent_forces if abs(f) >= self.max_force * 0.99)
        duty = saturated_samples / window_samples

        # Rate hit rate in window
        window_rate_samples = min(window_samples, len(self.rate_history))
        rate_hit_rate = 0.0
        if window_rate_samples > 0:
            max_rate = self.max_force / self.dt
            recent_rates = list(self.rate_history)[-window_rate_samples:]
            rate_hits = sum(1 for r in recent_rates if r >= max_rate * 0.99)
            rate_hit_rate = rate_hits / window_rate_samples

        # Alert conditions
        duty_alert = duty > self.duty_threshold
        rate_alert = rate_hit_rate > self.rate_hit_threshold
        continuous_alert = self.continuous_saturation_time > 0.2  # 200ms

        alert = duty_alert or rate_alert or continuous_alert

        return {
            'duty': duty,
            'rate_hit_rate': rate_hit_rate,
            'alert': alert,
            'status': 'monitoring',
            'continuous_saturation_ms': self.continuous_saturation_time * 1000,
            'max_continuous_saturation_ms': self.max_continuous_saturation * 1000,
            'force': force,
            'rate': rate
        }

    def reset(self) -> None:
        """Reset monitoring state."""
        self.force_history.clear()
        self.rate_history.clear()
        self.sample_count.reset()
        self.saturation_count.reset()
        self.rate_hit_count.reset()
        self.continuous_saturation_time = 0.0
        self.max_continuous_saturation = 0.0
        self.last_force = 0.0


class DynamicsConditioningMonitor:
    """Monitor dynamics matrix conditioning and inversion health.

    Implements conditioning monitoring as specified in Issue #1 resolution:
    - Alert on sustained κ(M(q)) above threshold or spike in fallback inversions
    """

    def __init__(self, condition_threshold: float = 1e7,
                 spike_threshold: float = 1e9, fallback_threshold: int = 3,
                 window_size_ms: float = 1000.0, dt: float = 0.01):
        """Initialize conditioning monitor.

        Parameters
        ----------
        condition_threshold : float
            Median condition number threshold
        spike_threshold : float
            99th percentile condition number threshold
        fallback_threshold : int
            Maximum fallback inversions per episode
        window_size_ms : float
            Rolling window size
        dt : float
            Simulation timestep
        """
        self.condition_threshold = condition_threshold
        self.spike_threshold = spike_threshold
        self.fallback_threshold = fallback_threshold

        self.window_samples = max(1, int(window_size_ms / 1000.0 / dt))

        # Condition number and fallback history
        self.condition_history: deque = deque(maxlen=self.window_samples)
        self.fallback_count = AtomicCounter(0)
        self.sample_count = AtomicCounter(0)

    def update(self, mass_matrix: np.ndarray, used_fallback: bool = False) -> Dict[str, Any]:
        """Update monitor with dynamics matrix info.

        Parameters
        ----------
        mass_matrix : np.ndarray
            Current mass matrix M(q)
        used_fallback : bool
            Whether fallback inversion was used

        Returns
        -------
        dict
            Conditioning monitoring results
        """
        self.sample_count.increment()

        # Compute condition number
        try:
            condition_num = np.linalg.cond(mass_matrix)
            if np.isfinite(condition_num):
                self.condition_history.append(condition_num)
            else:
                self.condition_history.append(1e12)  # Very high for invalid matrices
        except (np.linalg.LinAlgError, ValueError):
            # Handle singular matrices or invalid values
            self.condition_history.append(1e12)

        # Track fallback usage
        if used_fallback:
            self.fallback_count.increment()

        # Analyze conditioning
        if len(self.condition_history) == 0:
            return {'alert': False, 'status': 'no_data'}

        conditions = np.array(list(self.condition_history))
        median_cond = np.median(conditions)
        p99_cond = np.percentile(conditions, 99)

        # Alert conditions
        fallback_count_val = self.fallback_count.get()
        median_alert = median_cond > self.condition_threshold
        spike_alert = p99_cond > self.spike_threshold
        fallback_alert = fallback_count_val > self.fallback_threshold

        alert = median_alert or spike_alert or fallback_alert

        return {
            'alert': alert,
            'status': 'monitoring',
            'median_condition': median_cond,
            'p99_condition': p99_cond,
            'fallback_count': fallback_count_val,
            'current_condition': conditions[-1],
            'median_alert': median_alert,
            'spike_alert': spike_alert,
            'fallback_alert': fallback_alert
        }

    def reset(self) -> None:
        """Reset monitoring state."""
        self.condition_history.clear()
        self.fallback_count.reset()
        self.sample_count.reset()


class StabilityMonitoringSystem:
    """Integrated stability monitoring system for Issue #1 resolution.

    Combines LDR, saturation, and conditioning monitors for comprehensive
    stability assessment as specified in the resolution plan.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize integrated monitoring system.

        Parameters
        ----------
        config : dict, optional
            Monitoring configuration parameters
        """
        if config is None:
            config = {}

        # Extract configuration parameters
        dt = config.get('dt', 0.01)
        max_force = config.get('max_force', 150.0)

        # Initialize sub-monitors
        self.ldr_monitor = LyapunovDecreaseMonitor(
            window_size_ms=config.get('ldr_window_ms', 300.0),
            dt=dt,
            ldr_threshold=config.get('ldr_threshold', 0.95),
            transient_time=config.get('transient_time', 1.0)
        )

        self.saturation_monitor = SaturationMonitor(
            max_force=max_force,
            dt=dt,
            duty_threshold=config.get('duty_threshold', 0.2),
            rate_hit_threshold=config.get('rate_hit_threshold', 0.01),
            transient_time=config.get('transient_time', 1.0)
        )

        self.conditioning_monitor = DynamicsConditioningMonitor(
            condition_threshold=config.get('condition_threshold', 1e7),
            spike_threshold=config.get('spike_threshold', 1e9),
            fallback_threshold=config.get('fallback_threshold', 3),
            dt=dt
        )

        # System-wide monitoring state (thread-safe atomic counter)
        self.episode_count = AtomicCounter(0)
        self.violation_history: List[Dict[str, Any]] = []

    def update(self, sigma: np.ndarray, control_force: float,
               mass_matrix: np.ndarray, used_fallback: bool = False) -> Dict[str, Any]:
        """Update all monitors with current simulation data.

        Parameters
        ----------
        sigma : np.ndarray
            Sliding surface vector
        control_force : float
            Control force output
        mass_matrix : np.ndarray
            Current mass matrix
        used_fallback : bool
            Whether fallback dynamics inversion was used

        Returns
        -------
        dict
            Comprehensive monitoring results
        """
        # Update individual monitors
        ldr_result = self.ldr_monitor.update(sigma)
        sat_result = self.saturation_monitor.update(control_force)
        cond_result = self.conditioning_monitor.update(mass_matrix, used_fallback)

        # Aggregate alerts
        any_alert = ldr_result['alert'] or sat_result['alert'] or cond_result['alert']

        # Record violations
        if any_alert:
            violation = {
                'timestamp': time.time(),
                'sample': ldr_result['sample_count'],
                'ldr_alert': ldr_result['alert'],
                'saturation_alert': sat_result['alert'],
                'conditioning_alert': cond_result['alert'],
                'ldr_value': ldr_result['ldr'],
                'saturation_duty': sat_result['duty'],
                'condition_number': cond_result['current_condition']
            }
            self.violation_history.append(violation)

        # Compile comprehensive results
        result = {
            'alert': any_alert,
            'ldr': ldr_result,
            'saturation': sat_result,
            'conditioning': cond_result,
            'violation_count': len(self.violation_history),
            'episode': self.episode_count.get()
        }

        return result

    def get_stability_report(self) -> Dict[str, Any]:
        """Generate comprehensive stability report."""
        recent_violations = self.violation_history[-10:] if self.violation_history else []

        # Compute stability metrics
        total_samples = max(
            self.ldr_monitor.sample_count.get(),
            self.saturation_monitor.sample_count.get(),
            self.conditioning_monitor.sample_count.get()
        )

        violation_rate = len(self.violation_history) / max(1, total_samples)

        return {
            'episode_count': self.episode_count.get(),
            'total_violations': len(self.violation_history),
            'violation_rate': violation_rate,
            'recent_violations': recent_violations,
            'ldr_alert_count': self.ldr_monitor.alert_count.get(),
            'saturation_violations': len([v for v in self.violation_history if v['saturation_alert']]),
            'conditioning_violations': len([v for v in self.violation_history if v['conditioning_alert']]),
            'stability_score': max(0.0, 1.0 - violation_rate * 10)  # 0-1 scale
        }

    def start_new_episode(self) -> None:
        """Start monitoring a new episode."""
        self.episode_count.increment()
        # Don't reset monitors - keep cumulative data for analysis

    def reset(self) -> None:
        """Reset entire monitoring system."""
        self.ldr_monitor.reset()
        self.saturation_monitor.reset()
        self.conditioning_monitor.reset()
        self.episode_count.reset()
        self.violation_history.clear()