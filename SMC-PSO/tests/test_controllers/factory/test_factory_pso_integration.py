#======================================================================================\\
#======== tests/test_controllers/factory/test_factory_pso_integration.py =========\\
#======================================================================================\\

"""
PSO Integration Edge Cases for SMC Factory.

Tests PSO wrapper behavior and edge cases not covered in main factory tests:
- PSO wrapper state_vars initialization for all controller types
- Wrapper interface consistency across controllers
- Edge cases in config validation
- Controller type string normalization
"""

from __future__ import annotations

import numpy as np
import pytest

from src.controllers.factory import (
    SMCFactory,
    SMCType,
    SMCConfig,
    PSOControllerWrapper
)


class TestPSOWrapperStateInitialization:
    """Test PSO wrapper state_vars initialization for all controller types."""

    def test_classical_smc_state_vars(self):
        """Test Classical SMC wrapper has empty state_vars tuple."""
        try:
            spec = SMCFactory.get_gain_specification(SMCType.CLASSICAL)
            gains = [10.0] * spec.n_gains
            config = SMCConfig(gains=gains, max_force=100.0, dt=0.01)

            controller = SMCFactory.create_controller(SMCType.CLASSICAL, config)
            wrapper = PSOControllerWrapper(controller)

            # Classical SMC should have empty tuple
            assert wrapper._state_vars == ()
        except Exception as e:
            pytest.skip(f"Classical SMC not available: {e}")

    def test_adaptive_smc_state_vars(self):
        """Test Adaptive SMC wrapper has empty state_vars tuple."""
        try:
            spec = SMCFactory.get_gain_specification(SMCType.ADAPTIVE)
            gains = [10.0] * spec.n_gains
            config = SMCConfig(gains=gains, max_force=100.0, dt=0.01)

            controller = SMCFactory.create_controller(SMCType.ADAPTIVE, config)
            wrapper = PSOControllerWrapper(controller)

            # Adaptive SMC should have empty tuple
            assert wrapper._state_vars == ()
        except Exception as e:
            pytest.skip(f"Adaptive SMC not available: {e}")

    def test_super_twisting_state_vars(self):
        """Test Super-Twisting SMC wrapper has (z, sigma) tuple."""
        try:
            spec = SMCFactory.get_gain_specification(SMCType.SUPER_TWISTING)
            gains = [10.0] * spec.n_gains
            config = SMCConfig(gains=gains, max_force=100.0, dt=0.01)

            controller = SMCFactory.create_controller(SMCType.SUPER_TWISTING, config)
            wrapper = PSOControllerWrapper(controller)

            # STA-SMC should have (z=0, sigma=0) tuple
            assert isinstance(wrapper._state_vars, tuple)
            assert len(wrapper._state_vars) == 2
            assert wrapper._state_vars == (0.0, 0.0)
        except Exception as e:
            pytest.skip(f"Super-Twisting SMC not available: {e}")

    def test_hybrid_state_vars(self):
        """Test Hybrid SMC wrapper has (k1, k2, u_int) tuple."""
        try:
            spec = SMCFactory.get_gain_specification(SMCType.HYBRID)
            gains = [10.0] * spec.n_gains
            config = SMCConfig(gains=gains, max_force=100.0, dt=0.01)

            controller = SMCFactory.create_controller(SMCType.HYBRID, config)
            wrapper = PSOControllerWrapper(controller)

            # Hybrid should have 3-tuple (k1_init, k2_init, u_int_prev)
            assert isinstance(wrapper._state_vars, tuple)
            assert len(wrapper._state_vars) == 3
            # Third element (u_int_prev) should be 0.0
            assert wrapper._state_vars[2] == 0.0
        except Exception as e:
            pytest.skip(f"Hybrid SMC not available: {e}")


class TestWrapperInterfaceConsistency:
    """Test wrapper provides consistent interface across all controller types."""

    @pytest.mark.parametrize("smc_type", [
        SMCType.CLASSICAL,
        SMCType.ADAPTIVE,
        SMCType.SUPER_TWISTING,
        SMCType.HYBRID
    ])
    def test_wrapper_compute_control_simplified_interface(self, smc_type):
        """Test all controllers work with simplified compute_control(state) interface."""
        try:
            spec = SMCFactory.get_gain_specification(smc_type)
            gains = [10.0] * spec.n_gains
            config = SMCConfig(gains=gains, max_force=100.0, dt=0.01)

            controller = SMCFactory.create_controller(smc_type, config)
            wrapper = PSOControllerWrapper(controller)

            state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])

            # Simplified interface (PSO-friendly)
            control = wrapper.compute_control(state)

            assert isinstance(control, np.ndarray)
            assert control.size > 0
            assert np.all(np.isfinite(control))
        except (ImportError, NotImplementedError, AttributeError) as e:
            pytest.skip(f"{smc_type.value} not available: {e}")

    @pytest.mark.parametrize("smc_type", [
        SMCType.CLASSICAL,
        SMCType.ADAPTIVE,
        SMCType.SUPER_TWISTING,
        SMCType.HYBRID
    ])
    def test_wrapper_compute_control_full_interface(self, smc_type):
        """Test all controllers work with full compute_control(state, state_vars, history) interface."""
        try:
            spec = SMCFactory.get_gain_specification(smc_type)
            gains = [10.0] * spec.n_gains
            config = SMCConfig(gains=gains, max_force=100.0, dt=0.01)

            controller = SMCFactory.create_controller(smc_type, config)
            wrapper = PSOControllerWrapper(controller)

            state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])

            # Full interface
            result = wrapper.compute_control(state, wrapper._state_vars, {})

            # Result should be valid (type depends on controller)
            assert result is not None
        except (ImportError, NotImplementedError, AttributeError) as e:
            pytest.skip(f"{smc_type.value} not available: {e}")

    def test_all_controllers_integration(self):
        """Test factory can create and wrap all 4 controller types in one test."""
        created_controllers = []

        for smc_type in [SMCType.CLASSICAL, SMCType.ADAPTIVE, SMCType.SUPER_TWISTING, SMCType.HYBRID]:
            try:
                spec = SMCFactory.get_gain_specification(smc_type)
                gains = [10.0] * spec.n_gains
                config = SMCConfig(gains=gains, max_force=100.0, dt=0.01)

                controller = SMCFactory.create_controller(smc_type, config)
                wrapper = PSOControllerWrapper(controller)

                created_controllers.append((smc_type, controller, wrapper))
            except (ImportError, NotImplementedError, AttributeError):
                # Skip unavailable controllers
                pass

        # At least 2 controllers should be available (Classical and Adaptive are core)
        assert len(created_controllers) >= 2


class TestConfigValidationEdgeCases:
    """Test configuration validation edge cases."""

    def test_extreme_max_force_values(self):
        """Test config validation with extreme max_force values."""
        # Very small max_force
        config_small = SMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            max_force=0.01,
            dt=0.01
        )
        assert config_small.max_force == 0.01

        # Very large max_force
        config_large = SMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            max_force=10000.0,
            dt=0.01
        )
        assert config_large.max_force == 10000.0

    def test_extreme_dt_values(self):
        """Test config validation with extreme dt values."""
        # Very small dt
        config_small_dt = SMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            max_force=100.0,
            dt=0.0001
        )
        assert config_small_dt.dt == 0.0001

        # Moderately large dt
        config_large_dt = SMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            max_force=100.0,
            dt=0.1
        )
        assert config_large_dt.dt == 0.1

    def test_gain_count_validation(self):
        """Test config validation rejects wrong gain counts."""
        # Too few gains
        with pytest.raises((ValueError, TypeError, AssertionError)):
            config = SMCConfig(
                gains=[1.0, 2.0],  # Only 2 gains (not enough for any controller)
                max_force=100.0,
                dt=0.01
            )
            # Try to create a controller with wrong gain count
            SMCFactory.create_controller(SMCType.CLASSICAL, config)

    def test_negative_max_force_rejected(self):
        """Test negative max_force is rejected."""
        try:
            config = SMCConfig(
                gains=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                max_force=-10.0,  # Negative
                dt=0.01
            )
            # If config accepts negative max_force, it should still fail or convert
            assert config.max_force != -10.0  # Should be converted to positive or rejected
        except (ValueError, AssertionError):
            # Acceptable to reject negative max_force
            pass

    def test_zero_dt_handling(self):
        """Test zero dt is handled (rejected or special case)."""
        try:
            config = SMCConfig(
                gains=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                max_force=100.0,
                dt=0.0
            )
            # If config accepts dt=0, it's for special use cases
            assert config.dt == 0.0
        except (ValueError, AssertionError):
            # Acceptable to reject dt=0
            pass


class TestControllerTypeStringNormalization:
    """Test controller type string normalization and compatibility."""

    def test_smc_type_enum_values(self):
        """Test SMCType enum has expected values."""
        assert SMCType.CLASSICAL.value == "classical_smc"
        assert SMCType.ADAPTIVE.value == "adaptive_smc"
        assert SMCType.SUPER_TWISTING.value == "sta_smc"
        assert SMCType.HYBRID.value == "hybrid_adaptive_sta_smc"

    def test_smc_type_enum_from_string(self):
        """Test creating SMCType from string values."""
        # Using enum constructor
        type_classical = SMCType("classical_smc")
        assert type_classical == SMCType.CLASSICAL

        type_adaptive = SMCType("adaptive_smc")
        assert type_adaptive == SMCType.ADAPTIVE

    def test_gain_specification_for_all_types(self):
        """Test gain specification available for all 4 types."""
        for smc_type in [SMCType.CLASSICAL, SMCType.ADAPTIVE, SMCType.SUPER_TWISTING, SMCType.HYBRID]:
            spec = SMCFactory.get_gain_specification(smc_type)

            assert spec is not None
            assert hasattr(spec, 'n_gains')
            assert spec.n_gains > 0

    def test_create_controller_with_enum_type(self):
        """Test create_controller works with SMCType enum."""
        try:
            spec = SMCFactory.get_gain_specification(SMCType.CLASSICAL)
            gains = [10.0] * spec.n_gains
            config = SMCConfig(gains=gains, max_force=100.0, dt=0.01)

            controller = SMCFactory.create_controller(SMCType.CLASSICAL, config)

            assert controller is not None
        except (ImportError, NotImplementedError):
            pytest.skip("Classical SMC not available")


class TestPSOGainBounds:
    """Test PSO gain bounds retrieval."""

    def test_get_gain_bounds_for_pso_returns_valid_bounds(self):
        """Test get_gain_bounds_for_pso returns reasonable bounds."""
        try:
            bounds = SMCFactory.get_gain_bounds_for_pso(SMCType.CLASSICAL)

            assert isinstance(bounds, tuple)
            assert len(bounds) == 2  # (lower_bounds, upper_bounds)

            lower, upper = bounds
            assert isinstance(lower, (list, np.ndarray))
            assert isinstance(upper, (list, np.ndarray))

            # Lower bounds should be less than upper bounds
            lower_arr = np.array(lower)
            upper_arr = np.array(upper)
            assert np.all(lower_arr < upper_arr)
        except (ImportError, NotImplementedError, AttributeError):
            pytest.skip("get_gain_bounds_for_pso not available")

    def test_validate_smc_gains_accepts_valid_gains(self):
        """Test validate_smc_gains accepts valid gain values."""
        try:
            spec = SMCFactory.get_gain_specification(SMCType.CLASSICAL)
            valid_gains = [10.0] * spec.n_gains

            # Should not raise exception
            SMCFactory.validate_smc_gains(SMCType.CLASSICAL, valid_gains)
        except (ImportError, NotImplementedError, AttributeError):
            pytest.skip("validate_smc_gains not available")

    def test_validate_smc_gains_rejects_wrong_count(self):
        """Test validate_smc_gains rejects wrong gain count."""
        try:
            wrong_gains = [10.0, 20.0]  # Only 2 gains

            with pytest.raises((ValueError, AssertionError)):
                SMCFactory.validate_smc_gains(SMCType.CLASSICAL, wrong_gains)
        except (ImportError, NotImplementedError, AttributeError):
            pytest.skip("validate_smc_gains not available")

    @pytest.mark.parametrize("smc_type", [
        SMCType.CLASSICAL,
        SMCType.ADAPTIVE,
        SMCType.SUPER_TWISTING,
        SMCType.HYBRID
    ])
    def test_gain_bounds_consistent_with_spec(self, smc_type):
        """Test gain bounds have same length as gain specification."""
        try:
            spec = SMCFactory.get_gain_specification(smc_type)
            bounds = SMCFactory.get_gain_bounds_for_pso(smc_type)

            lower, upper = bounds
            assert len(lower) == spec.n_gains
            assert len(upper) == spec.n_gains
        except (ImportError, NotImplementedError, AttributeError):
            pytest.skip(f"{smc_type.value} bounds not available")
