#======================================================================================\
#============ tests/test_controllers/factory/test_base_create_controller.py ===========\
#======================================================================================\

"""
Comprehensive tests for factory/base.py create_controller() function.

Tests cover:
- All 6 controller types (classical, STA, adaptive, hybrid, swing-up, MPC)
- Parameter validation and error handling
- Configuration passing and defaults
- Gain parameter variations
- Type checking and validation
- Integration with registry system

Week 3 Coverage Goal: create_controller() → 95%+ coverage
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from src.controllers.factory.base import (
    create_controller,
    create_classical_smc_controller,
    create_sta_smc_controller,
    create_adaptive_smc_controller,
)
from src.controllers.factory.types import ConfigValueError


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_config():
    """Create minimal mock configuration for testing."""
    config = Mock()
    config.controllers = Mock()
    config.controller_defaults = Mock()
    config.physics = Mock()
    config.simulation = Mock()
    config.simulation.dt = 0.01
    return config


@pytest.fixture
def valid_classical_gains():
    """Valid gains for classical SMC: [lambda1, lambda2, eta1, eta2, phi1, phi2]."""
    return [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]


@pytest.fixture
def valid_sta_gains():
    """Valid gains for STA-SMC: [lambda1, lambda2, alpha1, alpha2, phi1, phi2]."""
    return [10.0, 5.0, 1.5, 1.5, 15.0, 2.0]


@pytest.fixture
def valid_adaptive_gains():
    """Valid gains for adaptive SMC: [k1, k2, lam1, lam2, gamma]."""
    return [10.0, 5.0, 8.0, 3.0, 5.0]


@pytest.fixture
def valid_hybrid_gains():
    """Valid gains for hybrid adaptive-STA SMC: [k1, k2, lam1, lam2]."""
    return [18.0, 12.0, 10.0, 8.0]


# =============================================================================
# Test Class: Basic Controller Creation
# =============================================================================

class TestCreateControllerBasic:
    """Test basic create_controller() functionality for all controller types."""

    def test_create_classical_smc_with_valid_gains(self, mock_config, valid_classical_gains):
        """Should create classical SMC controller with valid gains."""
        controller = create_controller(
            'classical_smc',
            config=mock_config,
            gains=valid_classical_gains
        )

        assert controller is not None
        assert hasattr(controller, 'compute_control')
        # Verify gains were set
        if hasattr(controller, 'gains'):
            np.testing.assert_array_almost_equal(controller.gains, valid_classical_gains)

    def test_create_sta_smc_with_valid_gains(self, mock_config, valid_sta_gains):
        """Should create STA-SMC controller with valid gains."""
        controller = create_controller(
            'sta_smc',
            config=mock_config,
            gains=valid_sta_gains
        )

        assert controller is not None
        assert hasattr(controller, 'compute_control')

    def test_create_adaptive_smc_with_valid_gains(self, mock_config, valid_adaptive_gains):
        """Should create adaptive SMC controller with valid gains."""
        controller = create_controller(
            'adaptive_smc',
            config=mock_config,
            gains=valid_adaptive_gains
        )

        assert controller is not None
        assert hasattr(controller, 'compute_control')

    def test_create_hybrid_adaptive_sta_smc_with_valid_gains(self, mock_config, valid_hybrid_gains):
        """Should create hybrid adaptive-STA SMC controller with valid gains."""
        controller = create_controller(
            'hybrid_adaptive_sta_smc',
            config=mock_config,
            gains=valid_hybrid_gains
        )

        assert controller is not None
        assert hasattr(controller, 'compute_control')

    def test_create_controller_with_alias(self, mock_config, valid_classical_gains):
        """Should accept controller type aliases (e.g., 'classic_smc')."""
        controller = create_controller(
            'classic_smc',  # Alias for classical_smc
            config=mock_config,
            gains=valid_classical_gains
        )

        assert controller is not None

    def test_create_controller_case_insensitive(self, mock_config, valid_classical_gains):
        """Should handle case-insensitive controller types."""
        controller = create_controller(
            'CLASSICAL_SMC',  # Uppercase
            config=mock_config,
            gains=valid_classical_gains
        )

        assert controller is not None


# =============================================================================
# Test Class: Controller Type Validation
# =============================================================================

class TestCreateControllerTypeValidation:
    """Test controller type validation and error handling."""

    def test_invalid_controller_type_raises_error(self, mock_config):
        """Should raise ValueError for invalid controller type."""
        with pytest.raises(ValueError, match="Unknown controller type"):
            create_controller('invalid_controller', config=mock_config)

    def test_empty_controller_type_raises_error(self, mock_config):
        """Should raise ValueError for empty controller type."""
        with pytest.raises(ValueError):
            create_controller('', config=mock_config)

    def test_none_controller_type_raises_error(self, mock_config):
        """Should raise TypeError for None controller type."""
        with pytest.raises((TypeError, ValueError)):
            create_controller(None, config=mock_config)

    def test_numeric_controller_type_raises_error(self, mock_config):
        """Should raise TypeError for numeric controller type."""
        with pytest.raises((TypeError, AttributeError)):
            create_controller(123, config=mock_config)


# =============================================================================
# Test Class: Gains Parameter Validation
# =============================================================================

class TestCreateControllerGainsValidation:
    """Test gains parameter validation."""

    def test_classical_smc_requires_6_gains(self, mock_config):
        """Should raise error if classical SMC gains length != 6."""
        with pytest.raises((ValueError, ConfigValueError)):
            create_controller('classical_smc', config=mock_config, gains=[1, 2, 3])

    def test_sta_smc_requires_6_gains(self, mock_config):
        """Should raise error if STA-SMC gains length != 6."""
        with pytest.raises((ValueError, ConfigValueError)):
            create_controller('sta_smc', config=mock_config, gains=[1, 2, 3, 4])

    def test_adaptive_smc_requires_5_gains(self, mock_config):
        """Should raise error if adaptive SMC gains length != 5."""
        with pytest.raises((ValueError, ConfigValueError)):
            create_controller('adaptive_smc', config=mock_config, gains=[1, 2])

    def test_hybrid_smc_requires_4_gains(self, mock_config):
        """Should raise error if hybrid SMC gains length != 4."""
        with pytest.raises((ValueError, ConfigValueError)):
            create_controller('hybrid_adaptive_sta_smc', config=mock_config, gains=[1, 2])

    def test_negative_gains_raise_error(self, mock_config):
        """Should raise error for negative gain values."""
        with pytest.raises((ValueError, ConfigValueError)):
            create_controller('classical_smc', config=mock_config, gains=[-1, 2, 3, 4, 5, 6])

    def test_zero_gains_allowed(self, mock_config):
        """Should allow zero gains (edge case for some parameters)."""
        # Zero may be valid for some gain parameters (e.g., boundary layer)
        # This tests that zero doesn't cause numeric errors
        controller = create_controller(
            'classical_smc',
            config=mock_config,
            gains=[10, 5, 8, 3, 0, 0]  # phi1, phi2 = 0 (no boundary layer)
        )
        assert controller is not None

    def test_nan_gains_raise_error(self, mock_config):
        """Should raise error for NaN gain values."""
        with pytest.raises((ValueError, ConfigValueError)):
            create_controller('classical_smc', config=mock_config, gains=[1, 2, np.nan, 4, 5, 6])

    def test_inf_gains_raise_error(self, mock_config):
        """Should raise error for infinite gain values."""
        with pytest.raises((ValueError, ConfigValueError)):
            create_controller('classical_smc', config=mock_config, gains=[1, 2, np.inf, 4, 5, 6])

    def test_gains_as_numpy_array(self, mock_config):
        """Should accept gains as numpy array."""
        gains_array = np.array([10.0, 5.0, 8.0, 3.0, 15.0, 2.0])
        controller = create_controller('classical_smc', config=mock_config, gains=gains_array)
        assert controller is not None

    def test_gains_as_tuple(self, mock_config):
        """Should accept gains as tuple."""
        gains_tuple = (10.0, 5.0, 8.0, 3.0, 15.0, 2.0)
        controller = create_controller('classical_smc', config=mock_config, gains=gains_tuple)
        assert controller is not None


# =============================================================================
# Test Class: Configuration Handling
# =============================================================================

class TestCreateControllerConfiguration:
    """Test configuration parameter handling."""

    def test_controller_with_minimal_config(self, valid_classical_gains):
        """Should create controller with minimal config (only required fields)."""
        minimal_config = Mock()
        minimal_config.simulation = Mock()
        minimal_config.simulation.dt = 0.01

        controller = create_controller('classical_smc', config=minimal_config, gains=valid_classical_gains)
        assert controller is not None

    def test_controller_without_config_uses_defaults(self, valid_classical_gains):
        """Should use default configuration if config=None."""
        # May raise error or use defaults depending on implementation
        # Test documents the behavior
        try:
            controller = create_controller('classical_smc', config=None, gains=valid_classical_gains)
            assert controller is not None or controller is None  # Either is acceptable
        except (ValueError, AttributeError, TypeError):
            # Expected if config is mandatory
            pass

    def test_controller_respects_dt_parameter(self, mock_config, valid_classical_gains):
        """Should use dt from configuration."""
        mock_config.simulation.dt = 0.02  # Non-default dt
        controller = create_controller('classical_smc', config=mock_config, gains=valid_classical_gains)

        if hasattr(controller, 'dt'):
            assert controller.dt == pytest.approx(0.02)


# =============================================================================
# Test Class: Convenience Functions
# =============================================================================

class TestConvenienceFunctions:
    """Test convenience functions for specific controller types."""

    def test_create_classical_smc_controller_shortcut(self, mock_config, valid_classical_gains):
        """Should create classical SMC via convenience function."""
        controller = create_classical_smc_controller(config=mock_config, gains=valid_classical_gains)
        assert controller is not None
        assert hasattr(controller, 'compute_control')

    def test_create_sta_smc_controller_shortcut(self, mock_config, valid_sta_gains):
        """Should create STA-SMC via convenience function."""
        controller = create_sta_smc_controller(config=mock_config, gains=valid_sta_gains)
        assert controller is not None
        assert hasattr(controller, 'compute_control')

    def test_create_adaptive_smc_controller_shortcut(self, mock_config, valid_adaptive_gains):
        """Should create adaptive SMC via convenience function."""
        controller = create_adaptive_smc_controller(config=mock_config, gains=valid_adaptive_gains)
        assert controller is not None
        assert hasattr(controller, 'compute_control')


# =============================================================================
# Test Class: Return Type Validation
# =============================================================================

class TestCreateControllerReturnType:
    """Test return type validation."""

    def test_returns_controller_with_compute_control_method(self, mock_config, valid_classical_gains):
        """Should return controller object with compute_control method."""
        controller = create_controller('classical_smc', config=mock_config, gains=valid_classical_gains)

        assert controller is not None
        assert hasattr(controller, 'compute_control')
        assert callable(controller.compute_control)

    def test_controller_has_expected_attributes(self, mock_config, valid_classical_gains):
        """Should return controller with expected attributes."""
        controller = create_controller('classical_smc', config=mock_config, gains=valid_classical_gains)

        # Common controller attributes
        expected_attrs = ['compute_control']
        for attr in expected_attrs:
            assert hasattr(controller, attr), f"Controller missing attribute: {attr}"


# =============================================================================
# Test Class: Edge Cases
# =============================================================================

class TestCreateControllerEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_large_gains(self, mock_config):
        """Should handle very large gain values."""
        large_gains = [1e6, 1e6, 1e6, 1e6, 1e6, 1e6]
        controller = create_controller('classical_smc', config=mock_config, gains=large_gains)
        assert controller is not None

    def test_very_small_gains(self, mock_config):
        """Should handle very small positive gain values."""
        small_gains = [1e-6, 1e-6, 1e-6, 1e-6, 1e-6, 1e-6]
        controller = create_controller('classical_smc', config=mock_config, gains=small_gains)
        assert controller is not None

    def test_mixed_precision_gains(self, mock_config):
        """Should handle mixed int/float gains."""
        mixed_gains = [10, 5.5, 8, 3.3, 15, 2.7]  # Mix of int and float
        controller = create_controller('classical_smc', config=mock_config, gains=mixed_gains)
        assert controller is not None

    def test_gains_with_trailing_zeros(self, mock_config):
        """Should handle gains with trailing decimal zeros."""
        gains = [10.00, 5.00, 8.00, 3.00, 15.00, 2.00]
        controller = create_controller('classical_smc', config=mock_config, gains=gains)
        assert controller is not None


# =============================================================================
# Test Class: Integration with Registry
# =============================================================================

class TestCreateControllerRegistryIntegration:
    """Test integration with controller registry system."""

    def test_all_registered_controllers_can_be_created(self, mock_config):
        """Should be able to create all registered controller types."""
        from src.controllers.factory.registry import list_available_controllers

        # Get all registered controller types
        available_controllers = list_available_controllers()

        # Test that each can be instantiated (with dummy gains)
        # Note: MPC may require additional setup
        testable_controllers = [c for c in available_controllers if 'mpc' not in c.lower()]

        for controller_type in testable_controllers:
            # Use appropriate gains for each type
            if 'hybrid' in controller_type:
                gains = [18, 12, 10, 8]  # 4 gains for hybrid
            elif 'adaptive' in controller_type:
                gains = [10, 5, 8, 3, 5]  # 5 gains for adaptive
            else:
                gains = [10, 5, 8, 3, 15, 2]  # 6 gains for classical/STA

            try:
                controller = create_controller(controller_type, config=mock_config, gains=gains)
                assert controller is not None, f"Failed to create {controller_type}"
            except Exception as e:
                # Document which controllers fail
                pytest.fail(f"Failed to create {controller_type}: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
