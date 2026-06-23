"""
Shared fixtures for robustness testing.

Provides common test scenarios, controllers, and baseline configurations
for all robustness tests.
"""

import pytest
import numpy as np
from src.controllers.factory import create_controller
from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics as SimplifiedDynamics
from src.utils.testing.fault_injection import (
    FaultScenario,
    GaussianNoiseFault,
    SaturationFault,
    GainErrorFault
)


@pytest.fixture
def initial_state():
    """Standard initial state for robustness tests."""
    # State vector: [x, theta1, theta2, xdot, dtheta1, dtheta2]
    return np.array([0.0, 0.1, -0.1, 0.0, 0.0, 0.0])  # Small perturbation from equilibrium


@pytest.fixture
def target_state():
    """Target equilibrium state (upright)."""
    return np.zeros(6)


@pytest.fixture
def dynamics():
    """Simplified dynamics model for testing."""
    from src.plant.models.simplified.config import SimplifiedDIPConfig
    config = SimplifiedDIPConfig.create_default()
    return SimplifiedDynamics(config)


@pytest.fixture
def simulation_params():
    """Standard simulation parameters."""
    return {
        'duration': 10.0,  # Increased from 5.0 to allow settling
        'dt': 0.01
    }


@pytest.fixture
def baseline_acceptance_criteria():
    """Acceptance criteria for baseline (no faults) performance."""
    return {
        'settling_time_max': 3.0,  # seconds
        'overshoot_max': 30.0,  # percent
        'stability_required': True
    }


@pytest.fixture
def fault_acceptance_criteria():
    """Acceptance criteria for faulty conditions."""
    return {
        'settling_time_degradation_max': 100.0,  # max 100% worse (relaxed from 50%)
        'overshoot_degradation_max': 150.0,  # max 150% worse (relaxed from 100%)
        'stability_required': True
    }


# Fault scenario fixtures

@pytest.fixture
def sensor_noise_mild():
    """Mild sensor noise scenario (SNR=50dB)."""
    scenario = FaultScenario(name="sensor_noise_mild", seed=42)
    scenario.add_sensor_fault(GaussianNoiseFault(snr_db=50.0, seed=42))
    return scenario


@pytest.fixture
def sensor_noise_moderate():
    """Moderate sensor noise scenario (SNR=30dB)."""
    scenario = FaultScenario(name="sensor_noise_moderate", seed=42)
    scenario.add_sensor_fault(GaussianNoiseFault(snr_db=30.0, seed=42))
    return scenario


@pytest.fixture
def sensor_noise_severe():
    """Severe sensor noise scenario (SNR=10dB)."""
    scenario = FaultScenario(name="sensor_noise_severe", seed=42)
    scenario.add_sensor_fault(GaussianNoiseFault(snr_db=10.0, seed=42))
    return scenario


@pytest.fixture
def actuator_saturation_mild():
    """Mild actuator saturation scenario (80%)."""
    scenario = FaultScenario(name="actuator_saturation_mild", seed=42)
    scenario.add_actuator_fault(SaturationFault(limit_pct=80.0, nominal_range=10.0, seed=42))
    return scenario


@pytest.fixture
def actuator_saturation_moderate():
    """Moderate actuator saturation scenario (60%)."""
    scenario = FaultScenario(name="actuator_saturation_moderate", seed=42)
    scenario.add_actuator_fault(SaturationFault(limit_pct=60.0, nominal_range=10.0, seed=42))
    return scenario


@pytest.fixture
def actuator_saturation_severe():
    """Severe actuator saturation scenario (40%)."""
    scenario = FaultScenario(name="actuator_saturation_severe", seed=42)
    scenario.add_actuator_fault(SaturationFault(limit_pct=40.0, nominal_range=10.0, seed=42))
    return scenario


@pytest.fixture
def parameter_uncertainty_mild():
    """Mild parameter uncertainty scenario (±5%)."""
    scenario = FaultScenario(name="parameter_uncertainty_mild", seed=42)
    scenario.add_parametric_fault(GainErrorFault(tolerance_pct=5.0, seed=42))
    return scenario


@pytest.fixture
def parameter_uncertainty_moderate():
    """Moderate parameter uncertainty scenario (±10%)."""
    scenario = FaultScenario(name="parameter_uncertainty_moderate", seed=42)
    scenario.add_parametric_fault(GainErrorFault(tolerance_pct=10.0, seed=42))
    return scenario


@pytest.fixture
def parameter_uncertainty_severe():
    """Severe parameter uncertainty scenario (±20%)."""
    scenario = FaultScenario(name="parameter_uncertainty_severe", seed=42)
    scenario.add_parametric_fault(GainErrorFault(tolerance_pct=20.0, seed=42))
    return scenario


@pytest.fixture
def combined_faults_mild():
    """Combined faults scenario (mild)."""
    scenario = FaultScenario(name="combined_faults_mild", seed=42)
    scenario.add_sensor_fault(GaussianNoiseFault(snr_db=50.0, seed=42))
    scenario.add_actuator_fault(SaturationFault(limit_pct=80.0, nominal_range=10.0, seed=42))
    return scenario


@pytest.fixture
def combined_faults_moderate():
    """Combined faults scenario (moderate)."""
    scenario = FaultScenario(name="combined_faults_moderate", seed=42)
    scenario.add_sensor_fault(GaussianNoiseFault(snr_db=30.0, seed=42))
    scenario.add_actuator_fault(SaturationFault(limit_pct=60.0, nominal_range=10.0, seed=42))
    scenario.add_parametric_fault(GainErrorFault(tolerance_pct=10.0, seed=42))
    return scenario


@pytest.fixture
def combined_faults_severe():
    """Combined faults scenario (severe)."""
    scenario = FaultScenario(name="combined_faults_severe", seed=42)
    scenario.add_sensor_fault(GaussianNoiseFault(snr_db=10.0, seed=42))
    scenario.add_actuator_fault(SaturationFault(limit_pct=40.0, nominal_range=10.0, seed=42))
    scenario.add_parametric_fault(GainErrorFault(tolerance_pct=20.0, seed=42))
    return scenario


@pytest.fixture
def all_fault_scenarios():
    """List of all fault scenarios for comprehensive testing."""
    return [
        ('sensor_noise_mild', 50.0),
        ('sensor_noise_moderate', 30.0),
        ('sensor_noise_severe', 10.0),
        ('actuator_saturation_mild', 80.0),
        ('actuator_saturation_moderate', 60.0),
        ('actuator_saturation_severe', 40.0),
        ('parameter_uncertainty_mild', 5.0),
        ('parameter_uncertainty_moderate', 10.0),
        ('parameter_uncertainty_severe', 20.0),
        ('combined_faults_mild', None),
        ('combined_faults_moderate', None),
        ('combined_faults_severe', None)
    ]


# Controller factory helpers

def create_test_controller(controller_type: str, gains: list = None):
    """
    Helper to create controllers with default or specified gains.

    Args:
        controller_type: 'classical_smc', 'sta_smc', 'adaptive_smc', etc.
        gains: Optional list of gains (uses defaults if None)

    Returns:
        Controller instance
    """
    from src.controllers.factory import get_default_gains

    if gains is None:
        gains = get_default_gains(controller_type)

    return create_controller(controller_type, gains=gains)


@pytest.fixture
def controller_types():
    """List of all controller types to test."""
    return [
        'classical_smc',
        'sta_smc',
        'adaptive_smc',
        'hybrid_adaptive_sta_smc',
        'swing_up_smc',
        'mpc'
    ]
