# ============================================================================
# Factory Pattern: Unified Controller Creation
# ============================================================================
# Demonstrates the factory pattern for creating different controller types
# with a unified interface

from typing import Dict, Any, List
import numpy as np


class ControllerFactory:
    """
    Factory for creating sliding mode controllers.

    Supports:
        - classical_smc: Classical SMC with boundary layer
        - sta_smc: Super-Twisting Algorithm (second-order SMC)
        - adaptive_smc: Adaptive SMC with online parameter estimation
        - hybrid_adaptive_sta_smc: Hybrid adaptive + super-twisting
    """

    _registry: Dict[str, type] = {}

    @classmethod
    def register(cls, name: str, controller_class: type):
        """Register a controller type."""
        cls._registry[name] = controller_class

    @classmethod
    def create(cls, controller_type: str, config: Dict[str, Any], gains: List[float]):
        """
        Create a controller instance.

        Parameters:
            controller_type: Name of controller ('classical_smc', 'sta_smc', etc.)
            config: Configuration dictionary (physics params, max_force, etc.)
            gains: Controller gain vector

        Returns:
            Controller instance with compute_control() method
        """
        if controller_type not in cls._registry:
            raise ValueError(
                f"Unknown controller type: {controller_type}. "
                f"Available: {list(cls._registry.keys())}"
            )

        controller_class = cls._registry[controller_type]
        return controller_class(config=config, gains=gains)


# Example controller classes (simplified)
class ClassicalSMC:
    """Classical SMC implementation."""

    def __init__(self, config: Dict[str, Any], gains: List[float]):
        self.max_force = config.get('max_force', 20.0)
        self.k1, self.k2, self.lambda1, self.lambda2, self.K, self.epsilon = gains

    def compute_control(self, state: np.ndarray, last_control: float, history):
        """Compute control force."""
        theta1, theta1_dot, theta2, theta2_dot = state

        # Sliding surface
        s = (self.k1 * theta1 + self.k2 * theta1_dot +
             self.lambda1 * theta2 + self.lambda2 * theta2_dot)

        # Control law
        u = -self.K * np.tanh(s / self.epsilon)

        # Saturation
        return np.clip(u, -self.max_force, self.max_force)


class STASMC:
    """Super-Twisting Algorithm SMC implementation."""

    def __init__(self, config: Dict[str, Any], gains: List[float]):
        self.max_force = config.get('max_force', 20.0)
        self.k1, self.k2, self.lambda1, self.lambda2, self.alpha, self.beta = gains
        self.u2_integral = 0.0  # Integral term for STA

    def compute_control(self, state: np.ndarray, last_control: float, history):
        """Compute control force using STA."""
        theta1, theta1_dot, theta2, theta2_dot = state

        # Sliding surface
        s = (self.k1 * theta1 + self.k2 * theta1_dot +
             self.lambda1 * theta2 + self.lambda2 * theta2_dot)

        # Super-twisting control law
        u1 = -self.alpha * np.abs(s) ** 0.5 * np.sign(s)
        self.u2_integral += -self.beta * np.sign(s) * 0.01  # dt=0.01

        u = u1 + self.u2_integral

        # Saturation
        return np.clip(u, -self.max_force, self.max_force)


# Register controllers
ControllerFactory.register('classical_smc', ClassicalSMC)
ControllerFactory.register('sta_smc', STASMC)


# Example usage
if __name__ == "__main__":
    # Configuration
    config = {
        'max_force': 20.0,
        'dt': 0.01
    }

    # Create classical SMC
    classical = ControllerFactory.create(
        controller_type='classical_smc',
        config=config,
        gains=[10.0, 5.0, 8.0, 3.0, 15.0, 0.05]
    )

    # Create STA-SMC
    sta = ControllerFactory.create(
        controller_type='sta_smc',
        config=config,
        gains=[10.0, 5.0, 8.0, 3.0, 5.0, 10.0]  # Different gain structure
    )

    # Test state
    state = np.array([0.1, 0.0, 0.05, 0.0])

    # Compute controls
    u_classical = classical.compute_control(state, 0.0, None)
    u_sta = sta.compute_control(state, 0.0, None)

    print(f"[INFO] Classical SMC control: {u_classical:.3f} N")
    print(f"[INFO] STA-SMC control: {u_sta:.3f} N")
