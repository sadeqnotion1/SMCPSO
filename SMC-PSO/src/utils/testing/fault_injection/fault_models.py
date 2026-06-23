"""
Concrete implementations of fault models.

Provides ready-to-use fault injectors for sensor noise, actuator limitations,
parameter variations, and environmental disturbances.
"""

import numpy as np
from typing import Optional, Union, Dict
from .fault_injector import (
    SensorFaultInjector,
    ActuatorFaultInjector,
    ParametricFaultInjector,
    EnvironmentalFaultInjector
)


# ============================================================================
# SENSOR FAULTS
# ============================================================================

class GaussianNoiseFault(SensorFaultInjector):
    """Additive white Gaussian noise (AWGN) fault."""

    def __init__(self, snr_db: float = 30.0, target: Union[str, list] = 'all_states',
                 enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize Gaussian noise fault.

        Args:
            snr_db: Signal-to-noise ratio in decibels (50=mild, 30=moderate, 10=severe)
            target: States to affect ('all_states' or list of indices)
            enabled: Whether fault is active
            seed: Random seed for reproducibility
        """
        super().__init__(name=f"GaussianNoise_SNR{snr_db}dB", target=target,
                         enabled=enabled, seed=seed)
        self.snr_db = snr_db

    def inject(self, signal: np.ndarray, **kwargs) -> np.ndarray:
        """Add Gaussian noise to signal."""
        # Calculate noise power from SNR
        signal_power = np.mean(signal ** 2)
        signal_power = max(signal_power, 1e-10)  # Avoid division by zero
        snr_linear = 10 ** (self.snr_db / 10.0)
        noise_power = signal_power / snr_linear
        noise_std = np.sqrt(noise_power)

        # Generate noise
        noise = self._rng.normal(0, noise_std, size=signal.shape)
        corrupted = signal + noise

        return self._apply_to_target(signal, corrupted)


class BiasFault(SensorFaultInjector):
    """Constant bias (offset) fault."""

    def __init__(self, bias_magnitude: float = 0.05, target: Union[str, list] = 'all_states',
                 enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize bias fault.

        Args:
            bias_magnitude: Magnitude of bias (absolute or % of signal range)
            target: States to affect
            enabled: Whether fault is active
            seed: Random seed
        """
        super().__init__(name=f"Bias_{bias_magnitude}", target=target,
                         enabled=enabled, seed=seed)
        self.bias_magnitude = bias_magnitude

    def inject(self, signal: np.ndarray, **kwargs) -> np.ndarray:
        """Add constant bias to signal."""
        corrupted = signal + self.bias_magnitude
        return self._apply_to_target(signal, corrupted)


class DropoutFault(SensorFaultInjector):
    """Data dropout (packet loss) fault."""

    def __init__(self, dropout_rate: float = 0.05, target: Union[str, list] = 'all_states',
                 enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize dropout fault.

        Args:
            dropout_rate: Probability of data loss per sample (0.01-0.2)
            target: States to affect
            enabled: Whether fault is active
            seed: Random seed
        """
        super().__init__(name=f"Dropout_{dropout_rate}", target=target,
                         enabled=enabled, seed=seed)
        self.dropout_rate = dropout_rate
        self._last_valid = None

    def inject(self, signal: np.ndarray, **kwargs) -> np.ndarray:
        """Drop data with specified probability, hold last valid value."""
        if self._last_valid is None:
            self._last_valid = signal.copy()

        # Decide if this sample drops out
        if self._rng.rand() < self.dropout_rate:
            corrupted = self._last_valid  # Hold last valid
        else:
            corrupted = signal
            self._last_valid = signal.copy()

        return self._apply_to_target(signal, corrupted)

    def reset_state(self):
        """Reset last valid value."""
        self._last_valid = None


class QuantizationFault(SensorFaultInjector):
    """Finite resolution (quantization) fault."""

    def __init__(self, bit_depth: int = 12, signal_range: float = 2.0,
                 target: Union[str, list] = 'all_states',
                 enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize quantization fault.

        Args:
            bit_depth: Number of bits (8, 10, 12, 16)
            signal_range: Full-scale range for quantization
            target: States to affect
            enabled: Whether fault is active
            seed: Random seed
        """
        super().__init__(name=f"Quantization_{bit_depth}bit", target=target,
                         enabled=enabled, seed=seed)
        self.bit_depth = bit_depth
        self.signal_range = signal_range
        self.num_levels = 2 ** bit_depth
        self.quantum = signal_range / (self.num_levels - 1)

    def inject(self, signal: np.ndarray, **kwargs) -> np.ndarray:
        """Quantize signal to finite resolution."""
        # Quantize: round to nearest quantum level
        corrupted = np.round(signal / self.quantum) * self.quantum
        return self._apply_to_target(signal, corrupted)


# ============================================================================
# ACTUATOR FAULTS
# ============================================================================

class SaturationFault(ActuatorFaultInjector):
    """Actuator saturation (clipping) fault."""

    def __init__(self, limit_pct: float = 80.0, nominal_range: float = 10.0,
                 enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize saturation fault.

        Args:
            limit_pct: Percentage of nominal range (40%, 60%, 80%)
            nominal_range: Nominal control range (±value)
            enabled: Whether fault is active
            seed: Random seed
        """
        super().__init__(name=f"Saturation_{limit_pct}pct", enabled=enabled, seed=seed)
        self.limit_pct = limit_pct
        self.nominal_range = nominal_range
        self.actual_limit = nominal_range * (limit_pct / 100.0)

    def inject(self, signal: np.ndarray, **kwargs) -> np.ndarray:
        """Clip signal to saturation limits."""
        return np.clip(signal, -self.actual_limit, self.actual_limit)


class DeadZoneFault(ActuatorFaultInjector):
    """Dead zone (unresponsive region) fault."""

    def __init__(self, dead_zone_width: float = 0.1, center: float = 0.0,
                 enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize dead zone fault.

        Args:
            dead_zone_width: Width of dead zone (5%, 10%, 20% of range)
            center: Center of dead zone
            enabled: Whether fault is active
            seed: Random seed
        """
        super().__init__(name=f"DeadZone_{dead_zone_width}", enabled=enabled, seed=seed)
        self.dead_zone_width = dead_zone_width
        self.center = center

    def inject(self, signal: np.ndarray, **kwargs) -> np.ndarray:
        """Zero out signal in dead zone."""
        signal_centered = signal - self.center
        mask = np.abs(signal_centered) <= self.dead_zone_width
        corrupted = np.where(mask, 0.0, signal)
        return corrupted


class LagFault(ActuatorFaultInjector):
    """First-order lag (delay) fault."""

    def __init__(self, time_constant: float = 0.02, dt: float = 0.01,
                 enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize lag fault.

        Args:
            time_constant: Lag time constant in seconds (0.01, 0.05, 0.1)
            dt: Simulation timestep
            enabled: Whether fault is active
            seed: Random seed
        """
        super().__init__(name=f"Lag_{time_constant}s", enabled=enabled, seed=seed)
        self.time_constant = time_constant
        self.dt = dt
        self.alpha = dt / (time_constant + dt)  # Filter coefficient
        self._state['output'] = None

    def inject(self, signal: np.ndarray, **kwargs) -> np.ndarray:
        """Apply first-order lag filter."""
        if self._state['output'] is None:
            self._state['output'] = signal.copy()

        # First-order filter: y[k] = alpha * u[k] + (1-alpha) * y[k-1]
        self._state['output'] = self.alpha * signal + (1 - self.alpha) * self._state['output']
        return self._state['output']

    def reset_state(self):
        """Reset lag filter."""
        self._state['output'] = None


class JitterFault(ActuatorFaultInjector):
    """High-frequency jitter (noise) fault."""

    def __init__(self, jitter_amplitude: float = 0.05, jitter_frequency: float = 50.0,
                 enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize jitter fault.

        Args:
            jitter_amplitude: Peak-to-peak amplitude (% of command)
            jitter_frequency: Dominant frequency in Hz
            enabled: Whether fault is active
            seed: Random seed
        """
        super().__init__(name=f"Jitter_{jitter_amplitude}", enabled=enabled, seed=seed)
        self.jitter_amplitude = jitter_amplitude
        self.jitter_frequency = jitter_frequency
        self._state['time'] = 0.0

    def inject(self, signal: np.ndarray, dt: float = 0.01, **kwargs) -> np.ndarray:
        """Add high-frequency sinusoidal jitter."""
        # Sinusoidal jitter with random phase
        phase = self._rng.rand() * 2 * np.pi
        jitter = self.jitter_amplitude * np.sin(2 * np.pi * self.jitter_frequency * self._state['time'] + phase)
        self._state['time'] += dt
        return signal + jitter * np.abs(signal)  # Jitter proportional to command magnitude


# ============================================================================
# PARAMETER VARIATIONS
# ============================================================================

class GainErrorFault(ParametricFaultInjector):
    """Controller gain error fault."""

    def __init__(self, tolerance_pct: float = 10.0, distribution: str = 'uniform',
                 enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize gain error fault.

        Args:
            tolerance_pct: Percentage deviation (±5%, ±10%, ±20%)
            distribution: 'uniform' or 'normal'
            enabled: Whether fault is active
            seed: Random seed
        """
        super().__init__(name=f"GainError_{tolerance_pct}pct", enabled=enabled, seed=seed)
        self.tolerance_pct = tolerance_pct
        self.distribution = distribution

    def inject(self, signal: np.ndarray, **kwargs) -> np.ndarray:
        """
        Apply gain errors to controller gains.

        Args:
            signal: Array of nominal gains

        Returns:
            Array of corrupted gains
        """
        tolerance_frac = self.tolerance_pct / 100.0

        if self.distribution == 'uniform':
            # Uniform distribution in [-tolerance, +tolerance]
            errors = self._rng.uniform(-tolerance_frac, tolerance_frac, size=signal.shape)
        elif self.distribution == 'normal':
            # Normal distribution with std = tolerance/3 (99.7% within ±tolerance)
            errors = self._rng.normal(0, tolerance_frac / 3.0, size=signal.shape)
        else:
            errors = np.zeros_like(signal)

        return signal * (1.0 + errors)

    def inject_parameters(self, params: Dict[str, float], **kwargs) -> Dict[str, float]:
        """Apply gain errors to parameter dictionary."""
        corrupted = {}
        for key, value in params.items():
            if isinstance(value, (int, float)):
                tolerance_frac = self.tolerance_pct / 100.0
                if self.distribution == 'uniform':
                    error = self._rng.uniform(-tolerance_frac, tolerance_frac)
                else:
                    error = self._rng.normal(0, tolerance_frac / 3.0)
                corrupted[key] = value * (1.0 + error)
            else:
                corrupted[key] = value
        return corrupted


class SystemUncertaintyFault(ParametricFaultInjector):
    """System parameter uncertainty fault."""

    def __init__(self, param_variations: Dict[str, float],
                 enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize system uncertainty fault.

        Args:
            param_variations: Dictionary of {param_name: variation_pct}
                Example: {'mass_cart': 10.0, 'inertia_pole1': 15.0}
            enabled: Whether fault is active
            seed: Random seed
        """
        super().__init__(name="SystemUncertainty", enabled=enabled, seed=seed)
        self.param_variations = param_variations

    def inject_parameters(self, params: Dict[str, float], **kwargs) -> Dict[str, float]:
        """Apply parameter variations."""
        corrupted = params.copy()
        for param_name, variation_pct in self.param_variations.items():
            if param_name in corrupted:
                tolerance_frac = variation_pct / 100.0
                error = self._rng.uniform(-tolerance_frac, tolerance_frac)
                corrupted[param_name] = corrupted[param_name] * (1.0 + error)
        return corrupted


class DriftFault(ParametricFaultInjector):
    """Time-varying parameter drift fault."""

    def __init__(self, drift_rate: float = 0.01, drift_pattern: str = 'linear',
                 enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize drift fault.

        Args:
            drift_rate: Rate of change per second (% per second)
            drift_pattern: 'linear', 'exponential', 'random_walk'
            enabled: Whether fault is active
            seed: Random seed
        """
        super().__init__(name=f"Drift_{drift_rate}", enabled=enabled, seed=seed)
        self.drift_rate = drift_rate
        self.drift_pattern = drift_pattern
        self._state['time'] = 0.0
        self._state['cumulative_drift'] = 0.0

    def inject(self, signal: np.ndarray, dt: float = 0.01, **kwargs) -> np.ndarray:
        """Apply time-varying drift to parameters."""
        if self.drift_pattern == 'linear':
            drift = self.drift_rate * self._state['time']
        elif self.drift_pattern == 'exponential':
            drift = np.exp(self.drift_rate * self._state['time']) - 1.0
        elif self.drift_pattern == 'random_walk':
            step = self._rng.normal(0, self.drift_rate * dt)
            self._state['cumulative_drift'] += step
            drift = self._state['cumulative_drift']
        else:
            drift = 0.0

        self._state['time'] += dt
        return signal * (1.0 + drift)


# ============================================================================
# ENVIRONMENTAL FAULTS
# ============================================================================

class DisturbanceFault(EnvironmentalFaultInjector):
    """External disturbance fault."""

    def __init__(self, disturbance_type: str = 'step', magnitude: float = 0.5,
                 frequency: float = 2.0, start_time: float = 1.0, end_time: float = 5.0,
                 enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize disturbance fault.

        Args:
            disturbance_type: 'step', 'periodic', 'random', 'impulse'
            magnitude: Disturbance amplitude (N or Nm)
            frequency: For periodic disturbances (Hz)
            start_time: When disturbance starts (seconds)
            end_time: When disturbance ends (seconds)
            enabled: Whether fault is active
            seed: Random seed
        """
        super().__init__(name=f"Disturbance_{disturbance_type}", enabled=enabled, seed=seed)
        self.disturbance_type = disturbance_type
        self.magnitude = magnitude
        self.frequency = frequency
        self.start_time = start_time
        self.end_time = end_time

    def inject(self, signal: np.ndarray, time: float = 0.0, **kwargs) -> np.ndarray:
        """Add disturbance to signal (control or force)."""
        self._time = time

        # Check if disturbance is active
        if time < self.start_time or time > self.end_time:
            return signal

        # Generate disturbance based on type
        if self.disturbance_type == 'step':
            disturbance = self.magnitude
        elif self.disturbance_type == 'periodic':
            disturbance = self.magnitude * np.sin(2 * np.pi * self.frequency * time)
        elif self.disturbance_type == 'random':
            disturbance = self.magnitude * self._rng.randn()
        elif self.disturbance_type == 'impulse':
            # Impulse at start_time only
            disturbance = self.magnitude if abs(time - self.start_time) < 0.01 else 0.0
        else:
            disturbance = 0.0

        return signal + disturbance
