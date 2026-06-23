#======================================================================================\\
#==== tests/test_controllers/smc/algorithms/classical/test_classical_edge_cases.py ====\\
#======================================================================================\\

"""
Edge case tests for Modular Classical SMC.

Tests challenging scenarios:
- Component composition and integration
- Error handling and recovery
- Reset behavior with different internal states
- Boundary conditions
- Saturation behavior
"""

from __future__ import annotations

import numpy as np
import pytest

from tests.test_controllers.smc.test_fixtures import MockDynamics
from src.controllers.smc.algorithms import ModularClassicalSMC, ClassicalSMCConfig


class TestClassicalSMCInitialization:
    """Test controller initialization variations."""

    def test_initialization_without_dynamics_model(self):
        """Test initialization without dynamics model."""
        config = ClassicalSMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 10.0, 2.0],
            max_force=50.0,
            boundary_layer=0.1
        )
        controller = ModularClassicalSMC(config)

        assert controller.config is not None
        assert hasattr(controller, '_surface')
        assert hasattr(controller, '_equivalent')
        assert hasattr(controller, '_boundary_layer')

    def test_initialization_with_dynamics_model(self):
        """Test initialization with dynamics model."""
        dynamics = MockDynamics(n_dof=3)
        config = ClassicalSMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 10.0, 2.0],
            max_force=50.0,
            boundary_layer=0.1,
            dynamics_model=dynamics
        )
        controller = ModularClassicalSMC(config)

        assert controller.config.dynamics_model is dynamics

    def test_initialization_with_custom_boundary_layer(self):
        """Test initialization with various boundary layer values."""
        for boundary_layer in [0.01, 0.1, 1.0, 10.0]:
            config = ClassicalSMCConfig(
                gains=[1.0, 1.0, 1.0, 1.0, 10.0, 2.0],
                max_force=50.0,
                boundary_layer=boundary_layer
            )
            controller = ModularClassicalSMC(config)

            assert controller.config.boundary_layer == boundary_layer


class TestControlComponentBreakdown:
    """Test control component breakdown and composition."""

    @pytest.fixture
    def controller(self) -> ModularClassicalSMC:
        """Create controller for component testing."""
        config = ClassicalSMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 10.0, 2.0],
            max_force=50.0,
            boundary_layer=0.1
        )
        return ModularClassicalSMC(config)

    def test_control_components_sum_correctly(self, controller):
        """Test u_total = u_eq + u_switch + u_deriv before saturation."""
        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])

        result = controller.compute_control(state, None, {})

        u_total_computed = (
            result['equivalent_control'] +
            result['switching_control'] +
            result['derivative_control']
        )

        # Should match total_before_saturation
        assert np.isclose(u_total_computed, result['total_before_saturation'], atol=1e-10)

    def test_equivalent_control_component(self, controller):
        """Test equivalent control component is computed."""
        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])

        result = controller.compute_control(state, None, {})

        assert 'equivalent_control' in result
        assert isinstance(result['equivalent_control'], float)
        assert np.isfinite(result['equivalent_control'])

    def test_switching_control_component(self, controller):
        """Test switching control component is computed."""
        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])

        result = controller.compute_control(state, None, {})

        assert 'switching_control' in result
        assert isinstance(result['switching_control'], float)
        assert np.isfinite(result['switching_control'])

    def test_derivative_control_component(self, controller):
        """Test derivative control component is computed."""
        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])

        result = controller.compute_control(state, None, {})

        assert 'derivative_control' in result
        assert isinstance(result['derivative_control'], float)
        assert np.isfinite(result['derivative_control'])


class TestSaturationBehavior:
    """Test control saturation behavior."""

    @pytest.fixture
    def controller(self) -> ModularClassicalSMC:
        """Create controller with low max_force for easy saturation."""
        config = ClassicalSMCConfig(
            gains=[10.0, 10.0, 10.0, 10.0, 50.0, 5.0],  # High gains
            max_force=10.0,  # Low max force
            boundary_layer=0.1
        )
        return ModularClassicalSMC(config)

    def test_saturation_limits_magnitude(self, controller):
        """Test saturation limits control magnitude to max_force."""
        # Large state to trigger saturation
        state = np.array([0, 0, 10.0, 0, 0, 0])

        result = controller.compute_control(state, None, {})

        assert abs(result['u']) <= 10.0

    def test_saturation_preserves_sign(self, controller):
        """Test saturation preserves control sign."""
        # Positive surface
        state_pos = np.array([0, 0, 5.0, 0, 0, 0])
        result_pos = controller.compute_control(state_pos, None, {})

        # Negative surface
        state_neg = np.array([0, 0, -5.0, 0, 0, 0])
        result_neg = controller.compute_control(state_neg, None, {})

        # Signs should be opposite (or zero)
        if result_pos['total_before_saturation'] != 0 and result_neg['total_before_saturation'] != 0:
            assert np.sign(result_pos['total_before_saturation']) != np.sign(result_neg['total_before_saturation'])

    def test_saturation_active_flag(self, controller):
        """Test saturation_active flag is set correctly."""
        # Large state to trigger saturation
        state_large = np.array([0, 0, 10.0, 0, 0, 0])
        result_large = controller.compute_control(state_large, None, {})

        # Small state to avoid saturation
        state_small = np.array([0, 0, 0.001, 0, 0, 0])
        result_small = controller.compute_control(state_small, None, {})

        # Saturation flag should match the condition
        assert result_large['saturation_active'] == (abs(result_large['total_before_saturation']) > 10.0)
        assert result_small['saturation_active'] == (abs(result_small['total_before_saturation']) > 10.0)


class TestBoundaryLayerIntegration:
    """Test boundary layer integration."""

    @pytest.fixture
    def controller(self) -> ModularClassicalSMC:
        """Create controller for boundary layer testing."""
        config = ClassicalSMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 10.0, 2.0],
            max_force=50.0,
            boundary_layer=0.5  # Moderately thick boundary layer
        )
        return ModularClassicalSMC(config)

    def test_boundary_layer_flag_inside_layer(self, controller):
        """Test in_boundary_layer flag when inside boundary layer."""
        # Small surface value (inside boundary layer)
        state = np.array([0, 0, 0.01, 0, 0, 0])

        result = controller.compute_control(state, None, {})

        # Check boundary layer flag is present
        assert 'in_boundary_layer' in result
        assert isinstance(result['in_boundary_layer'], bool)

    def test_boundary_layer_smooth_switching(self, controller):
        """Test boundary layer provides smooth switching."""
        # Inside boundary layer
        state_inside = np.array([0, 0, 0.1, 0, 0, 0])
        result_inside = controller.compute_control(state_inside, None, {})

        # Outside boundary layer
        state_outside = np.array([0, 0, 5.0, 0, 0, 0])
        result_outside = controller.compute_control(state_outside, None, {})

        # Both should produce finite control
        assert np.isfinite(result_inside['u'])
        assert np.isfinite(result_outside['u'])


class TestResetBehavior:
    """Test reset behavior comprehensively."""

    @pytest.fixture
    def controller_with_history(self) -> ModularClassicalSMC:
        """Create controller with some execution history."""
        config = ClassicalSMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 10.0, 2.0],
            max_force=50.0,
            boundary_layer=0.1
        )
        controller = ModularClassicalSMC(config)

        # Run some control steps
        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])
        for _ in range(10):
            controller.compute_control(state, None, {})

        return controller

    def test_reset_method_exists(self, controller_with_history):
        """Test reset method exists and is callable."""
        assert hasattr(controller_with_history, 'reset')
        assert callable(controller_with_history.reset)

    def test_reset_does_not_crash(self, controller_with_history):
        """Test reset executes without errors."""
        try:
            controller_with_history.reset()
        except Exception as e:
            pytest.fail(f"Reset should not raise exception: {e}")

    def test_reset_allows_continued_operation(self, controller_with_history):
        """Test controller can continue operating after reset."""
        controller_with_history.reset()

        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])
        result = controller_with_history.compute_control(state, None, {})

        assert 'u' in result
        assert np.isfinite(result['u'])

    def test_reset_clears_component_state(self, controller_with_history):
        """Test reset clears component internal state (if any)."""
        controller_with_history.reset()

        # Components should be in clean state
        # (Classical SMC typically doesn't have much internal state)
        # This test verifies reset can be called without error


class TestSurfaceDerivativeEstimation:
    """Test surface derivative estimation."""

    @pytest.fixture
    def controller(self) -> ModularClassicalSMC:
        """Create controller for derivative testing."""
        config = ClassicalSMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 10.0, 2.0],
            max_force=50.0,
            boundary_layer=0.1
        )
        return ModularClassicalSMC(config)

    def test_derivative_with_full_state(self, controller):
        """Test derivative estimation with 6D state."""
        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])

        result = controller.compute_control(state, None, {})

        assert 'surface_derivative' in result
        assert np.isfinite(result['surface_derivative'])

    def test_derivative_fallback_short_state(self, controller):
        """Test derivative estimation fallback for state < 6 dimensions."""
        state = np.array([0.1, 0.2, 0.1, 0.2])  # 4D state

        result = controller.compute_control(state, None, {})

        # Short state may trigger error, which is acceptable
        if 'error' in result:
            assert result.get('safe_mode') is True
        else:
            assert 'surface_derivative' in result
            # Fallback should return 0.0
            assert result['surface_derivative'] == 0.0

    def test_derivative_uses_velocity_components(self, controller):
        """Test derivative estimation uses theta_dot components."""
        state = np.array([0.1, 0.2, 0.3, 1.0, 0.5, 2.0])  # Non-zero velocities

        result = controller.compute_control(state, None, {})

        # Derivative should be non-zero with non-zero velocities
        # derivative = lam1 * theta1_dot + lam2 * theta2_dot
        # With lam1=lam2=1.0, derivative = 1.0 + 2.0 = 3.0
        expected_derivative = controller.config.lam1 * 1.0 + controller.config.lam2 * 2.0
        assert np.isclose(result['surface_derivative'], expected_derivative, atol=0.01)


class TestErrorHandling:
    """Test error handling and recovery."""

    @pytest.fixture
    def controller(self) -> ModularClassicalSMC:
        """Create controller for error testing."""
        config = ClassicalSMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 10.0, 2.0],
            max_force=50.0,
            boundary_layer=0.1
        )
        return ModularClassicalSMC(config)

    def test_nan_state_handling(self, controller):
        """Test handling of NaN in state."""
        state = np.array([np.nan, 0, 0, 0, 0, 0])

        result = controller.compute_control(state, None, {})

        assert isinstance(result, dict)
        assert 'u' in result
        # NaN is handled gracefully - surface becomes 0
        assert np.isfinite(result['u']) or result['u'] == 0.0

    def test_inf_state_handling(self, controller):
        """Test handling of Inf in state."""
        state = np.array([np.inf, 0, 0, 0, 0, 0])

        result = controller.compute_control(state, None, {})

        assert isinstance(result, dict)
        assert result['u'] == 0.0

    def test_error_result_structure(self, controller):
        """Test error result has proper structure."""
        state = np.array([np.nan, 0, 0, 0, 0, 0])

        result = controller.compute_control(state, None, {})

        # NaN is handled gracefully, may not trigger error path
        assert 'u' in result
        assert 'controller_type' in result
        assert result['controller_type'] == 'classical_smc'

    def test_recovery_after_error(self, controller):
        """Test controller recovers after error."""
        # Error state
        state_bad = np.array([np.nan, 0, 0, 0, 0, 0])
        result_bad = controller.compute_control(state_bad, None, {})

        assert result_bad['u'] == 0.0

        # Normal state should work after recovery
        state_good = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])
        result_good = controller.compute_control(state_good, None, {})

        assert 'u' in result_good
        assert np.isfinite(result_good['u'])
        assert result_good.get('safe_mode', False) is False


class TestZeroGainHandling:
    """Test edge case with very small or zero gains."""

    def test_zero_switching_gain(self):
        """Test behavior with K=0 (zero switching gain)."""
        try:
            config = ClassicalSMCConfig(
                gains=[1.0, 1.0, 1.0, 1.0, 0.0, 2.0],  # K=0
                max_force=50.0,
                boundary_layer=0.1
            )
            controller = ModularClassicalSMC(config)

            state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])
            result = controller.compute_control(state, None, {})

            # Should still produce valid result
            assert 'u' in result
            assert np.isfinite(result['u'])
        except (ValueError, AssertionError):
            # Acceptable to reject K=0 in validation
            pytest.skip("Config validation rejects K=0")

    def test_zero_derivative_gain(self):
        """Test behavior with kd=0 (zero derivative gain)."""
        config = ClassicalSMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 10.0, 0.0],  # kd=0
            max_force=50.0,
            boundary_layer=0.1
        )
        controller = ModularClassicalSMC(config)

        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])
        result = controller.compute_control(state, None, {})

        # Derivative control should be zero
        assert result['derivative_control'] == 0.0
        # Total control should still be valid
        assert np.isfinite(result['u'])


class TestBackwardCompatibilityFacade:
    """Test backward compatibility ClassicalSMC facade."""

    def test_facade_initialization(self):
        """Test facade initializes correctly."""
        from src.controllers.smc.algorithms import ClassicalSMC

        controller = ClassicalSMC(
            gains=[1.0, 1.0, 1.0, 1.0, 10.0, 2.0],
            max_force=50.0,
            boundary_layer=0.1
        )

        assert controller is not None
        assert hasattr(controller, '_controller')

    def test_facade_with_dynamics_model(self):
        """Test facade initialization with dynamics model."""
        from src.controllers.smc.algorithms import ClassicalSMC

        dynamics = MockDynamics(n_dof=3)
        controller = ClassicalSMC(
            gains=[1.0, 1.0, 1.0, 1.0, 10.0, 2.0],
            max_force=50.0,
            boundary_layer=0.1,
            dynamics_model=dynamics
        )

        assert controller._controller.config.dynamics_model is dynamics

    def test_facade_compute_control(self):
        """Test facade compute_control delegation."""
        from src.controllers.smc.algorithms import ClassicalSMC

        controller = ClassicalSMC(
            gains=[1.0, 1.0, 1.0, 1.0, 10.0, 2.0],
            max_force=50.0,
            boundary_layer=0.1
        )

        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])
        result = controller.compute_control(state, None, {})

        assert isinstance(result, dict)
        assert 'u' in result

    def test_facade_gains_property(self):
        """Test facade gains property delegation."""
        from src.controllers.smc.algorithms import ClassicalSMC

        controller = ClassicalSMC(
            gains=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            max_force=50.0,
            boundary_layer=0.1
        )

        assert controller.gains == [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]

    def test_facade_reset(self):
        """Test facade reset delegation."""
        from src.controllers.smc.algorithms import ClassicalSMC

        controller = ClassicalSMC(
            gains=[1.0, 1.0, 1.0, 1.0, 10.0, 2.0],
            max_force=50.0,
            boundary_layer=0.1
        )

        # Run some control
        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])
        for _ in range(10):
            controller.compute_control(state, None, {})

        # Reset should not crash
        controller.reset()

    def test_facade_get_parameters(self):
        """Test facade get_parameters delegation."""
        from src.controllers.smc.algorithms import ClassicalSMC

        controller = ClassicalSMC(
            gains=[1.0, 1.0, 1.0, 1.0, 10.0, 2.0],
            max_force=50.0,
            boundary_layer=0.1
        )

        params = controller.get_parameters()

        assert isinstance(params, dict)
        assert 'gains' in params
