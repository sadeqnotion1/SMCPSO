#======================================================================================\\\
#==================== src/controllers/factory/fallback_configs.py =====================\\\
#======================================================================================\\\

"""
Fallback configuration classes for SMC controllers.

Provides minimal working configuration classes when the full implementation
config classes are not available. These ensure graceful degradation of the factory.
"""

from dataclasses import dataclass
from typing import Any, List


@dataclass
class ClassicalSMCConfig:
    """Fallback minimal configuration for Classical SMC controller."""

    gains: List[float]
    max_force: float = 150.0
    boundary_layer: float = 0.02
    boundary_layer_slope: float = 1.0
    switch_method: str = "tanh"
    regularization: float = 1e-6
    dt: float = 0.001
    dynamics_model: Any = None

    def get_surface_gains(self) -> List[float]:
        """Get sliding surface gains [k1, k2, λ1, λ2]."""
        return self.gains[:4] if len(self.gains) >= 4 else self.gains

    def get_effective_controllability_threshold(self) -> float:
        """Get effective controllability threshold."""
        return self.regularization


@dataclass
class STASMCConfig:
    """Fallback minimal configuration for Super-Twisting SMC controller."""

    gains: List[float]
    max_force: float = 150.0
    damping_gain: float = 0.0
    dt: float = 0.001
    switch_method: str = "tanh"
    dynamics_model: Any = None
    K1: float = 4.0
    K2: float = 0.4
    power_exponent: float = 0.5
    regularization: float = 1e-6

    def get_surface_gains(self) -> List[float]:
        """Get sliding surface gains [k1, k2, λ1, λ2]."""
        return self.gains[:4] if len(self.gains) >= 4 else self.gains

    def get_effective_anti_windup_gain(self) -> float:
        """Get effective anti-windup gain."""
        return self.damping_gain


@dataclass
class AdaptiveSMCConfig:
    """Fallback minimal configuration for Adaptive SMC controller."""

    gains: List[float]
    max_force: float = 150.0
    leak_rate: float = 0.01
    dead_zone: float = 0.05
    adapt_rate_limit: float = 10.0
    K_min: float = 0.1
    K_max: float = 100.0
    dt: float = 0.001
    smooth_switch: bool = True
    boundary_layer: float = 0.1
    gamma: float = 2.0
    dynamics_model: Any = None

    def get_surface_gains(self) -> List[float]:
        """Get sliding surface gains [k1, k2, λ1, λ2]."""
        return self.gains[:4] if len(self.gains) >= 4 else self.gains

    def get_adaptation_bounds(self) -> tuple:
        """Get adaptation bounds (K_min, K_max)."""
        return (self.K_min, self.K_max)


@dataclass
class HybridAdaptiveSTASMCConfig:
    """Fallback minimal configuration for Hybrid Adaptive STA-SMC controller."""

    gains: List[float]
    max_force: float = 150.0
    dt: float = 0.001
    k1_init: float = 4.0
    k2_init: float = 0.4
    gamma1: float = 2.0
    gamma2: float = 0.5
    dead_zone: float = 0.05
    dynamics_model: Any = None

    def get_surface_gains(self) -> List[float]:
        """Get sliding surface gains [k1, k2, λ1, λ2]."""
        return self.gains[:4] if len(self.gains) >= 4 else self.gains