"""
Base classes for fault injection.

Defines abstract interfaces for different fault types (sensor, actuator,
parametric, environmental) and provides common functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
import numpy as np


class FaultInjector(ABC):
    """Abstract base class for all fault injectors."""

    def __init__(self, name: str, enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize fault injector.

        Args:
            name: Human-readable fault name
            enabled: Whether fault is active
            seed: Random seed for reproducibility
        """
        self.name = name
        self.enabled = enabled
        self.seed = seed
        self._rng = np.random.RandomState(seed)

    @abstractmethod
    def inject(self, signal: np.ndarray, **kwargs) -> np.ndarray:
        """
        Inject fault into signal.

        Args:
            signal: Input signal (state, control, etc.)
            **kwargs: Fault-specific parameters

        Returns:
            Corrupted signal
        """
        pass

    def __call__(self, signal: np.ndarray, **kwargs) -> np.ndarray:
        """Allow injector to be called like a function."""
        if not self.enabled:
            return signal
        return self.inject(signal, **kwargs)

    def enable(self):
        """Enable this fault."""
        self.enabled = True

    def disable(self):
        """Disable this fault."""
        self.enabled = False

    def reset_rng(self, seed: Optional[int] = None):
        """Reset random number generator."""
        self.seed = seed if seed is not None else self.seed
        self._rng = np.random.RandomState(self.seed)


class SensorFaultInjector(FaultInjector):
    """Base class for sensor faults (noise, bias, dropout, quantization)."""

    def __init__(self, name: str, target: Union[str, list] = 'all_states',
                 enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize sensor fault injector.

        Args:
            name: Fault name
            target: 'all_states' or list of state indices to affect
            enabled: Whether fault is active
            seed: Random seed
        """
        super().__init__(name, enabled, seed)
        self.target = target

    def _apply_to_target(self, signal: np.ndarray, corrupted: np.ndarray) -> np.ndarray:
        """
        Apply corrupted signal only to targeted states.

        Args:
            signal: Original signal
            corrupted: Fully corrupted signal

        Returns:
            Signal with faults applied to target states only
        """
        if self.target == 'all_states':
            return corrupted

        # Apply only to specific indices
        result = signal.copy()
        if isinstance(self.target, list):
            for idx in self.target:
                if isinstance(idx, int) and 0 <= idx < len(signal):
                    result[idx] = corrupted[idx]
        return result


class ActuatorFaultInjector(FaultInjector):
    """Base class for actuator faults (saturation, dead zone, lag, jitter)."""

    def __init__(self, name: str, enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize actuator fault injector.

        Args:
            name: Fault name
            enabled: Whether fault is active
            seed: Random seed
        """
        super().__init__(name, enabled, seed)
        self._state = {}  # For stateful faults (lag, etc.)

    def reset_state(self):
        """Reset internal state (e.g., lag filter)."""
        self._state = {}


class ParametricFaultInjector(FaultInjector):
    """Base class for parametric faults (gain errors, system uncertainty)."""

    def __init__(self, name: str, enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize parametric fault injector.

        Args:
            name: Fault name
            enabled: Whether fault is active
            seed: Random seed
        """
        super().__init__(name, enabled, seed)

    def inject_parameters(self, params: Dict[str, float], **kwargs) -> Dict[str, float]:
        """
        Inject faults into system/controller parameters.

        Args:
            params: Original parameters
            **kwargs: Fault-specific parameters

        Returns:
            Corrupted parameters
        """
        # Subclasses implement specific parameter corruption
        return params


class EnvironmentalFaultInjector(FaultInjector):
    """Base class for environmental faults (disturbances, model mismatch)."""

    def __init__(self, name: str, enabled: bool = True, seed: Optional[int] = None):
        """
        Initialize environmental fault injector.

        Args:
            name: Fault name
            enabled: Whether fault is active
            seed: Random seed
        """
        super().__init__(name, enabled, seed)
        self._time = 0.0  # Track simulation time for time-varying disturbances

    def inject(self, signal: np.ndarray, time: float = 0.0, **kwargs) -> np.ndarray:
        """
        Inject environmental fault (disturbance).

        Args:
            signal: Input signal (usually control or force)
            time: Current simulation time
            **kwargs: Fault-specific parameters

        Returns:
            Signal with disturbance added
        """
        self._time = time
        return signal

    def reset_time(self):
        """Reset internal time tracker."""
        self._time = 0.0
