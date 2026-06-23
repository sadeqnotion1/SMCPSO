#======================================================================================\\\
#=============== tests/test_controllers/factory/core/test_validation.py ===============\\\
#======================================================================================\\\

"""
Comprehensive tests for factory validation framework.

Tests the validation system for controller gains, configurations, and parameters
with edge cases, error conditions, and performance validation.
"""

import pytest
import numpy as np
from typing import List

from src.controllers.factory.validation import (
    ValidationResult,
    validate_controller_gains,
    validate_configuration,
    validate_state_vector,
    validate_control_output
)


class TestValidationResult:
    """Test the ValidationResult class."""

    def test_initial_state(self):
        """Test initial validation result state."""
        result = ValidationResult()
        assert result.valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.info == []
        assert result.metadata == {}

    def test_add_error(self):
        """Test adding errors invalidates result."""
        result = ValidationResult()
        result.add_error("Test error")
        assert result.valid is False
        assert "Test error" in result.errors

    def test_add_warning(self):
        """Test adding warnings doesn't invalidate result."""
        result = ValidationResult()
        result.add_warning("Test warning")
        assert result.valid is True
        assert "Test warning" in result.warnings

    def test_has_issues(self):
        """Test issue detection."""
        result = ValidationResult()
        assert not result.has_issues()

        result.add_warning("Warning")
        assert result.has_issues()

        result = ValidationResult()
        result.add_error("Error")
        assert result.has_issues()

    def test_get_summary(self):
        """Test summary generation."""
        result = ValidationResult()
        assert "no issues" in result.get_summary()

        result.add_error("Error")
        result.add_warning("Warning")
        summary = result.get_summary()
        assert "1 error(s)" in summary
        assert "1 warning(s)" in summary


class TestValidateControllerGains:
    """Test controller gains validation."""

    def test_valid_classical_smc_gains(self):
        """Test validation of valid classical SMC gains."""
        gains = [10.0, 8.0, 5.0, 4.0, 20.0, 2.0]  # [k1, k2, λ1, λ2, K, kd]
        result = validate_controller_gains(gains, 'classical_smc')
        assert result.valid

    def test_invalid_gain_count(self):
        """Test validation fails with wrong number of gains."""
        gains = [10.0, 8.0, 5.0]  # Too few gains
        result = validate_controller_gains(gains, 'classical_smc')
        assert not result.valid
        assert any("requires exactly 6 gains" in error for error in result.errors)

    def test_non_finite_gains(self):
        """Test validation fails with non-finite gains."""
        gains = [10.0, np.inf, 5.0, 4.0, 20.0, 2.0]
        result = validate_controller_gains(gains, 'classical_smc')
        assert not result.valid
        assert any("not finite" in error for error in result.errors)

    def test_negative_gains(self):
        """Test validation fails with negative gains."""
        gains = [10.0, -8.0, 5.0, 4.0, 20.0, 2.0]
        result = validate_controller_gains(gains, 'classical_smc')
        assert not result.valid
        assert any("must be positive" in error for error in result.errors)

    def test_zero_gains(self):
        """Test validation fails with zero gains."""
        gains = [10.0, 0.0, 5.0, 4.0, 20.0, 2.0]
        result = validate_controller_gains(gains, 'classical_smc')
        assert not result.valid

    def test_numpy_array_gains(self):
        """Test validation works with numpy arrays."""
        gains = np.array([10.0, 8.0, 5.0, 4.0, 20.0, 2.0])
        result = validate_controller_gains(gains, 'classical_smc')
        assert result.valid

    def test_bounds_checking(self):
        """Test gain bounds checking generates warnings."""
        gains = [100.0, 8.0, 5.0, 4.0, 20.0, 2.0]  # k1 too high
        result = validate_controller_gains(gains, 'classical_smc', check_bounds=True)
        # Should be valid but with warnings
        assert result.valid
        assert len(result.warnings) > 0

    def test_classical_smc_specific_validation(self):
        """Test Classical SMC specific validation rules."""
        # High damping ratio
        gains = [1.0, 1.0, 25.0, 25.0, 20.0, 2.0]  # λ/k = 25
        result = validate_controller_gains(gains, 'classical_smc')
        assert result.valid
        assert any("damping ratio" in warning for warning in result.warnings)

        # Very high switching gain
        gains = [10.0, 8.0, 5.0, 4.0, 150.0, 2.0]  # K = 150
        result = validate_controller_gains(gains, 'classical_smc')
        assert result.valid
        assert any("switching gain" in warning for warning in result.warnings)

    def test_adaptive_smc_validation(self):
        """Test Adaptive SMC specific validation."""
        # Valid gains
        gains = [10.0, 8.0, 5.0, 4.0, 2.0]  # [k1, k2, λ1, λ2, γ]
        result = validate_controller_gains(gains, 'adaptive_smc')
        assert result.valid

        # High adaptation gain
        gains = [10.0, 8.0, 5.0, 4.0, 15.0]  # γ = 15
        result = validate_controller_gains(gains, 'adaptive_smc')
        assert result.valid
        assert any("adaptation gain" in warning for warning in result.warnings)

    def test_sta_smc_validation(self):
        """Test Super-Twisting SMC specific validation."""
        gains = [20.0, 15.0, 10.0, 8.0, 5.0, 4.0]  # [K1, K2, k1, k2, λ1, λ2]
        result = validate_controller_gains(gains, 'sta_smc')
        assert result.valid

        # Test ratio warnings
        gains = [10.0, 25.0, 10.0, 8.0, 5.0, 4.0]  # K2 > K1
        result = validate_controller_gains(gains, 'sta_smc')
        assert result.valid
        assert len(result.warnings) > 0

    def test_hybrid_smc_validation(self):
        """Test Hybrid SMC specific validation."""
        gains = [10.0, 8.0, 5.0, 4.0]  # [k1, k2, λ1, λ2]
        result = validate_controller_gains(gains, 'hybrid_adaptive_sta_smc')
        assert result.valid

        # Test imbalance warnings
        gains = [50.0, 2.0, 5.0, 4.0]  # Large k1/k2 ratio
        result = validate_controller_gains(gains, 'hybrid_adaptive_sta_smc')
        assert result.valid
        assert any("imbalance" in warning for warning in result.warnings)

    def test_invalid_controller_type(self):
        """Test validation fails with invalid controller type."""
        gains = [10.0, 8.0, 5.0, 4.0, 20.0, 2.0]
        result = validate_controller_gains(gains, 'invalid_controller')
        assert not result.valid
        assert any("Invalid controller type" in error for error in result.errors)

    def test_stability_checking_disabled(self):
        """Test validation with stability checking disabled."""
        gains = [10.0, 8.0, 5.0, 4.0, 20.0, 2.0]
        result = validate_controller_gains(gains, 'classical_smc', check_stability=False)
        assert result.valid
        # Should not have stability-related metadata
        assert 'stability_margin' not in result.metadata


class TestValidateConfiguration:
    """Test configuration validation."""

    class MockConfig:
        """Mock configuration for testing."""
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    def test_none_configuration(self):
        """Test validation of None configuration."""
        result = validate_configuration(None, 'classical_smc')
        assert result.valid
        assert any("None" in warning for warning in result.warnings)

    def test_valid_configuration(self):
        """Test validation of valid configuration."""
        config = self.MockConfig(
            gains=[10.0, 8.0, 5.0, 4.0, 20.0, 2.0],
            max_force=150.0,
            dt=0.001,
            boundary_layer=0.02
        )
        result = validate_configuration(config, 'classical_smc')
        assert result.valid

    def test_missing_required_parameters(self):
        """Test validation fails with missing required parameters."""
        config = self.MockConfig(gains=[10.0, 8.0, 5.0, 4.0, 20.0, 2.0])
        result = validate_configuration(config, 'classical_smc', check_completeness=True)
        assert not result.valid
        assert any("Missing required parameter" in error for error in result.errors)

    def test_invalid_max_force(self):
        """Test validation fails with invalid max_force."""
        config = self.MockConfig(
            gains=[10.0, 8.0, 5.0, 4.0, 20.0, 2.0],
            max_force=-150.0  # Negative max force
        )
        result = validate_configuration(config, 'classical_smc')
        assert not result.valid
        assert any("max_force must be" in error for error in result.errors)

    def test_invalid_dt(self):
        """Test validation fails with invalid dt."""
        config = self.MockConfig(
            gains=[10.0, 8.0, 5.0, 4.0, 20.0, 2.0],
            dt=0.0  # Zero timestep
        )
        result = validate_configuration(config, 'classical_smc', check_completeness=False)
        assert not result.valid

        # Large timestep should generate warning but still be valid
        config = self.MockConfig(
            gains=[10.0, 8.0, 5.0, 4.0, 20.0, 2.0],
            max_force=150.0,
            boundary_layer=0.02,
            dt=0.2  # Large timestep
        )
        result = validate_configuration(config, 'classical_smc', check_completeness=False)
        assert result.valid
        assert any("Large timestep" in warning for warning in result.warnings)

    def test_classical_smc_boundary_layer(self):
        """Test Classical SMC boundary layer validation."""
        config = self.MockConfig(
            gains=[10.0, 8.0, 5.0, 4.0, 20.0, 2.0],
            boundary_layer=-0.01  # Negative boundary layer
        )
        result = validate_configuration(config, 'classical_smc')
        assert not result.valid
        assert any("boundary_layer must be" in error for error in result.errors)


class TestValidateStateVector:
    """Test state vector validation."""

    def test_valid_state_vector(self):
        """Test validation of valid state vector."""
        state = np.array([0.1, 0.05, 0.02, 0.0, 0.0, 0.0])
        result = validate_state_vector(state)
        assert result.valid

    def test_invalid_state_type(self):
        """Test validation fails with non-numpy array."""
        state = [0.1, 0.05, 0.02, 0.0, 0.0, 0.0]  # List instead of array
        result = validate_state_vector(state)
        assert not result.valid

    def test_invalid_state_shape(self):
        """Test validation fails with wrong shape."""
        state = np.array([0.1, 0.05, 0.02])  # Only 3 elements
        result = validate_state_vector(state)
        assert not result.valid

    def test_non_finite_state(self):
        """Test validation fails with non-finite values."""
        state = np.array([0.1, np.inf, 0.02, 0.0, 0.0, 0.0])
        result = validate_state_vector(state)
        assert not result.valid

    def test_large_values_warning(self):
        """Test warnings for physically unreasonable values."""
        # Large cart position
        state = np.array([15.0, 0.05, 0.02, 0.0, 0.0, 0.0])
        result = validate_state_vector(state)
        assert result.valid
        assert any("Large cart position" in warning for warning in result.warnings)

        # Large velocities
        state = np.array([0.1, 0.05, 0.02, 25.0, 0.0, 0.0])
        result = validate_state_vector(state)
        assert result.valid
        assert any("velocity" in warning for warning in result.warnings)

        # Large angular velocities
        state = np.array([0.1, 0.05, 0.02, 0.0, 60.0, 0.0])
        result = validate_state_vector(state)
        assert result.valid
        assert any("angular velocities" in warning for warning in result.warnings)


class TestValidateControlOutput:
    """Test control output validation."""

    def test_valid_scalar_output(self):
        """Test validation of valid scalar control output."""
        result = validate_control_output(50.0, max_force=150.0)
        assert result.valid
        assert result.metadata['control_value'] == 50.0

    def test_valid_array_output(self):
        """Test validation of valid array control output."""
        control = np.array([50.0])
        result = validate_control_output(control, max_force=150.0)
        assert result.valid

    def test_scalar_array_output(self):
        """Test validation of scalar numpy array."""
        control = np.array(50.0)  # 0-d array
        result = validate_control_output(control, max_force=150.0)
        assert result.valid

    def test_invalid_array_shape(self):
        """Test validation fails with invalid array shape."""
        control = np.array([50.0, 60.0])  # Multi-element array
        result = validate_control_output(control, max_force=150.0)
        assert not result.valid

    def test_non_finite_output(self):
        """Test validation fails with non-finite output."""
        result = validate_control_output(np.inf, max_force=150.0)
        assert not result.valid

    def test_saturation_warning(self):
        """Test warning for outputs requiring saturation."""
        result = validate_control_output(200.0, max_force=150.0)
        assert result.valid
        assert any("exceeds max_force" in warning for warning in result.warnings)
        assert result.metadata['saturation_required'] is True

    def test_severe_violation_error(self):
        """Test error for severely excessive outputs."""
        result = validate_control_output(500.0, max_force=150.0)
        assert not result.valid
        assert any("severely exceeds" in error for error in result.errors)


@pytest.mark.parametrize("controller_type,gains", [
    ('classical_smc', [10.0, 8.0, 5.0, 4.0, 20.0, 2.0]),
    ('adaptive_smc', [10.0, 8.0, 5.0, 4.0, 2.0]),
    ('sta_smc', [20.0, 15.0, 10.0, 8.0, 5.0, 4.0]),
    ('hybrid_adaptive_sta_smc', [10.0, 8.0, 5.0, 4.0])
])
def test_all_controller_types_validation(controller_type: str, gains: List[float]):
    """Test validation works for all supported controller types."""
    result = validate_controller_gains(gains, controller_type)
    assert result.valid
    assert result.metadata['controller_type'] == controller_type
    assert result.metadata['gain_count'] == len(gains)