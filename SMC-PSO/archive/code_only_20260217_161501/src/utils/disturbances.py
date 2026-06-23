"""
Disturbance Generation for Robustness Testing
================================================================================

Provides various disturbance models for testing controller robustness:
- Step disturbances (sudden force/torque)
- Impulse disturbances (brief spike)
- Sinusoidal disturbances (periodic)
- Random disturbances (Gaussian noise)
- Combined disturbances (multiple types)

Used for MT-8: Disturbance Rejection Analysis.

Author: MT-8 Investigation Team
Created: October 18, 2025
"""

from typing import Callable, List, Tuple, Optional, Union
import numpy as np
from dataclasses import dataclass
from enum import Enum


class DisturbanceType(Enum):
    """Disturbance type enumeration."""
    STEP = "step"
    IMPULSE = "impulse"
    SINUSOIDAL = "sinusoidal"
    RANDOM = "random"
    COMBINED = "combined"


@dataclass
class DisturbanceConfig:
    """
    Configuration for a single disturbance.

    Attributes:
        type: Disturbance type
        magnitude: Disturbance magnitude (N for force, N·m for torque)
        start_time: When disturbance starts (seconds)
        duration: How long disturbance lasts (seconds, inf for step)
        frequency: Frequency for sinusoidal disturbances (Hz)
        std_dev: Standard deviation for random disturbances
        axis: Which state to disturb:
            - 0: Cart force (x-direction)
            - 1: Pendulum 1 torque
            - 2: Pendulum 2 torque
    """
    type: DisturbanceType
    magnitude: float
    start_time: float = 0.0
    duration: float = float('inf')
    frequency: float = 1.0
    std_dev: float = 0.1
    axis: int = 0  # 0=cart, 1=link1, 2=link2

    def __post_init__(self):
        """Validate configuration."""
        if self.magnitude < 0:
            raise ValueError("Disturbance magnitude must be non-negative")
        if self.start_time < 0:
            raise ValueError("Start time must be non-negative")
        if self.duration <= 0 and self.duration != float('inf'):
            raise ValueError("Duration must be positive or infinite")
        if self.axis not in [0, 1, 2]:
            raise ValueError("Axis must be 0 (cart), 1 (link1), or 2 (link2)")


class DisturbanceGenerator:
    """
    Generates disturbances for robustness testing.

    Examples:
        # Step disturbance on cart at t=2s
        gen = DisturbanceGenerator()
        gen.add_step_disturbance(magnitude=10.0, start_time=2.0, axis=0)

        # Get disturbance at current time
        d_cart, d_link1, d_link2 = gen.get_disturbance(t=3.0)

        # Inject into control: u_total = u_nominal + d_cart
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize disturbance generator.

        Args:
            seed: Random seed for reproducibility
        """
        self.disturbances: List[DisturbanceConfig] = []
        self.rng = np.random.default_rng(seed)

    def add_step_disturbance(
        self,
        magnitude: float,
        start_time: float = 0.0,
        axis: int = 0
    ) -> None:
        """
        Add step disturbance (constant after start_time).

        Args:
            magnitude: Disturbance magnitude
            start_time: When disturbance starts
            axis: 0=cart force, 1=link1 torque, 2=link2 torque
        """
        config = DisturbanceConfig(
            type=DisturbanceType.STEP,
            magnitude=magnitude,
            start_time=start_time,
            duration=float('inf'),
            axis=axis
        )
        self.disturbances.append(config)

    def add_impulse_disturbance(
        self,
        magnitude: float,
        start_time: float,
        duration: float = 0.1,
        axis: int = 0
    ) -> None:
        """
        Add impulse disturbance (brief spike).

        Args:
            magnitude: Peak disturbance magnitude
            start_time: When impulse starts
            duration: Impulse duration (seconds)
            axis: 0=cart force, 1=link1 torque, 2=link2 torque
        """
        config = DisturbanceConfig(
            type=DisturbanceType.IMPULSE,
            magnitude=magnitude,
            start_time=start_time,
            duration=duration,
            axis=axis
        )
        self.disturbances.append(config)

    def add_sinusoidal_disturbance(
        self,
        magnitude: float,
        frequency: float = 1.0,
        start_time: float = 0.0,
        duration: float = float('inf'),
        axis: int = 0
    ) -> None:
        """
        Add sinusoidal disturbance (periodic).

        Args:
            magnitude: Amplitude of sinusoid
            frequency: Frequency (Hz)
            start_time: When disturbance starts
            duration: How long disturbance lasts
            axis: 0=cart force, 1=link1 torque, 2=link2 torque
        """
        config = DisturbanceConfig(
            type=DisturbanceType.SINUSOIDAL,
            magnitude=magnitude,
            frequency=frequency,
            start_time=start_time,
            duration=duration,
            axis=axis
        )
        self.disturbances.append(config)

    def add_random_disturbance(
        self,
        std_dev: float,
        start_time: float = 0.0,
        duration: float = float('inf'),
        axis: int = 0
    ) -> None:
        """
        Add random Gaussian noise disturbance.

        Args:
            std_dev: Standard deviation of noise
            start_time: When disturbance starts
            duration: How long disturbance lasts
            axis: 0=cart force, 1=link1 torque, 2=link2 torque
        """
        config = DisturbanceConfig(
            type=DisturbanceType.RANDOM,
            magnitude=std_dev,  # Use magnitude field for std_dev
            std_dev=std_dev,
            start_time=start_time,
            duration=duration,
            axis=axis
        )
        self.disturbances.append(config)

    def clear_disturbances(self) -> None:
        """Remove all disturbances."""
        self.disturbances = []

    def get_disturbance(self, t: float) -> Tuple[float, float, float]:
        """
        Compute total disturbance at time t.

        Args:
            t: Current time (seconds)

        Returns:
            Tuple of (cart_force, link1_torque, link2_torque)
        """
        # Initialize disturbances
        d_cart = 0.0
        d_link1 = 0.0
        d_link2 = 0.0

        # Sum all active disturbances
        for config in self.disturbances:
            # Check if disturbance is active at time t
            if t < config.start_time:
                continue
            if t > config.start_time + config.duration:
                continue

            # Compute disturbance value
            if config.type == DisturbanceType.STEP:
                value = config.magnitude

            elif config.type == DisturbanceType.IMPULSE:
                value = config.magnitude

            elif config.type == DisturbanceType.SINUSOIDAL:
                # d(t) = A * sin(2π * f * (t - t_start))
                t_rel = t - config.start_time
                value = config.magnitude * np.sin(2 * np.pi * config.frequency * t_rel)

            elif config.type == DisturbanceType.RANDOM:
                value = self.rng.normal(0, config.std_dev)

            else:
                value = 0.0

            # Add to appropriate axis
            if config.axis == 0:
                d_cart += value
            elif config.axis == 1:
                d_link1 += value
            elif config.axis == 2:
                d_link2 += value

        return d_cart, d_link1, d_link2

    def get_disturbance_force_only(self, t: float) -> float:
        """
        Get disturbance force on cart only (for simplified dynamics).

        Args:
            t: Current time (seconds)

        Returns:
            Cart force disturbance
        """
        d_cart, _, _ = self.get_disturbance(t)
        return d_cart


# Predefined disturbance scenarios for testing

def create_step_scenario(magnitude: float = 20.0, start_time: float = 2.0) -> DisturbanceGenerator:
    """
    Create step disturbance scenario (constant force after t=2s).

    Args:
        magnitude: Step magnitude (N)
        start_time: When step occurs

    Returns:
        Configured disturbance generator
    """
    gen = DisturbanceGenerator()
    gen.add_step_disturbance(magnitude=magnitude, start_time=start_time, axis=0)
    return gen


def create_impulse_scenario(magnitude: float = 50.0, start_time: float = 2.0, duration: float = 0.1) -> DisturbanceGenerator:
    """
    Create impulse disturbance scenario (brief spike).

    Args:
        magnitude: Impulse peak (N)
        start_time: When impulse occurs
        duration: Impulse duration (s)

    Returns:
        Configured disturbance generator
    """
    gen = DisturbanceGenerator()
    gen.add_impulse_disturbance(magnitude=magnitude, start_time=start_time, duration=duration, axis=0)
    return gen


def create_sinusoidal_scenario(magnitude: float = 15.0, frequency: float = 2.0) -> DisturbanceGenerator:
    """
    Create sinusoidal disturbance scenario (periodic force).

    Args:
        magnitude: Amplitude (N)
        frequency: Frequency (Hz)

    Returns:
        Configured disturbance generator
    """
    gen = DisturbanceGenerator()
    gen.add_sinusoidal_disturbance(magnitude=magnitude, frequency=frequency, start_time=0.0, axis=0)
    return gen


def create_random_scenario(std_dev: float = 5.0) -> DisturbanceGenerator:
    """
    Create random noise disturbance scenario.

    Args:
        std_dev: Noise standard deviation (N)

    Returns:
        Configured disturbance generator
    """
    gen = DisturbanceGenerator()
    gen.add_random_disturbance(std_dev=std_dev, start_time=0.0, axis=0)
    return gen


def create_combined_scenario() -> DisturbanceGenerator:
    """
    Create combined disturbance scenario (multiple types).

    Returns:
        Configured disturbance generator with:
        - Step at t=2s (20 N)
        - Impulse at t=5s (50 N, 0.1s)
        - Random noise throughout (5 N std)
    """
    gen = DisturbanceGenerator()
    gen.add_step_disturbance(magnitude=20.0, start_time=2.0, axis=0)
    gen.add_impulse_disturbance(magnitude=50.0, start_time=5.0, duration=0.1, axis=0)
    gen.add_random_disturbance(std_dev=5.0, start_time=0.0, axis=0)
    return gen
