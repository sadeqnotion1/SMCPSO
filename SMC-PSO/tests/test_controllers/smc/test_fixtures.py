#======================================================================================\\\
#==================== tests/test_controllers/smc/test_fixtures.py =====================\\\
#======================================================================================\\\

"""
Shared test fixtures and utilities for SMC testing.

This module provides common test utilities, mock objects, and fixtures
used across all SMC test modules to ensure consistency and reduce duplication.
"""

from __future__ import annotations

import numpy as np
import pytest
from typing import Tuple
from dataclasses import dataclass

# Test imports for modular controllers
from src.controllers.smc.algorithms import (
    # Classical SMC
    ClassicalSMCConfig,

    # Adaptive SMC
    AdaptiveSMCConfig,
    SuperTwistingSMCConfig,
    HybridSMCConfig
)


@dataclass
class SystemStateFixture:
    """Test system state for SMC testing."""
    position: np.ndarray
    velocity: np.ndarray
    time: float = 0.0


class MockDynamics:
    """Mock dynamics model for testing SMC controllers."""

    def __init__(self, n_dof: int = 3):
        self.n_dof = n_dof

    def _compute_physics_matrices(self, state: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute test physics matrices."""
        # Simple diagonal inertia matrix
        M = np.eye(self.n_dof)
        # Small damping
        C = 0.1 * np.eye(self.n_dof)
        # Zero gravity for simplicity
        G = np.zeros(self.n_dof)
        return M, C, G


@pytest.fixture
def mock_dynamics():
    """Fixture providing mock dynamics for testing."""
    return MockDynamics()


@pytest.fixture
def test_state():
    """Fixture providing test system state."""
    return SystemStateFixture(
        position=np.array([0.1, 0.05, 0.02]),
        velocity=np.array([0.2, -0.1, 0.15])
    )


@pytest.fixture
def classical_smc_config():
    """Fixture providing classical SMC configuration."""
    return ClassicalSMCConfig(
        gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],  # [k1, k2, lam1, lam2, K, kd]
        max_force=100.0,
        dt=0.01,
        boundary_layer=0.1
    )


@pytest.fixture
def adaptive_smc_config():
    """Fixture providing adaptive SMC configuration."""
    return AdaptiveSMCConfig(
        gains=[5.0, 3.0, 4.0, 2.0, 0.5],  # [k1, k2, lam1, lam2, gamma]
        max_force=100.0,
        dt=0.01,
        K_init=10.0,
        K_min=0.1,
        K_max=100.0
    )


@pytest.fixture
def super_twisting_config():
    """Fixture providing super-twisting SMC configuration."""
    return SuperTwistingSMCConfig(
        gains=[2.5, 1.5, 5.0, 3.0, 4.0, 2.0],  # [K1, K2, k1, k2, lam1, lam2] with K1 > K2
        max_force=100.0,
        dt=0.01
    )


@pytest.fixture
def hybrid_smc_config():
    """Fixture providing hybrid SMC configuration."""
    classical_config = ClassicalSMCConfig(
        gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
        max_force=100.0,
        dt=0.01,
        boundary_layer=0.01
    )
    adaptive_config = AdaptiveSMCConfig(
        gains=[5.0, 3.0, 4.0, 2.0, 0.5],
        max_force=100.0,
        dt=0.01
    )

    from src.controllers.smc.algorithms.hybrid.config import HybridMode

    return HybridSMCConfig(
        hybrid_mode=HybridMode.CLASSICAL_ADAPTIVE,
        dt=0.01,
        max_force=100.0,
        classical_config=classical_config,
        adaptive_config=adaptive_config
    )


def create_test_reference(t: float) -> np.ndarray:
    """Create test reference trajectory."""
    return np.array([
        0.5 * np.sin(t),
        0.3 * np.cos(t),
        0.2 * np.sin(0.5 * t)
    ])


def validate_control_output(control: np.ndarray, max_force: float = 50.0) -> bool:
    """Validate control output is within reasonable bounds."""
    return np.all(np.abs(control) <= max_force)


def compute_tracking_error(state: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """Compute tracking error for test validation."""
    pos = state[:3]  # Assuming first 3 elements are positions
    return pos - reference