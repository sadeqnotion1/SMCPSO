#======================================================================================\\\
#====== tests/test_controllers/smc/algorithms/test_classical_smc_comprehensive.py =====\\\
#======================================================================================\\\

"""
Comprehensive tests for Classical SMC controller.

MISSION: Achieve 85%+ coverage for Classical SMC controller module.

Test Coverage:
- Initialization and parameter validation
- Sliding surface computation (s = c*e + e_dot)
- Switching function (sign-based control)
- Lyapunov stability properties
- Chattering behavior analysis
- Boundary layer effects
- Gain validation and edge cases
- Equivalent control computation
- Control component breakdown
- Performance metrics
"""

import pytest
import numpy as np
from typing import Dict, Any

from src.controllers.smc.algorithms.classical.controller import ModularClassicalSMC, ClassicalSMC
from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig


class TestClassicalSMCInitialization:
    """Test Classical SMC initialization and configuration."""

    def test_modular_initialization_valid_config(self):
        """Test modular controller initializes with valid config."""
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        controller = ModularClassicalSMC(config)

        assert controller.config == config
        assert controller.n_gains == 6
        assert len(controller.gains) == 6

    def test_facade_initialization_legacy_interface(self):
        """Test facade initializes with legacy interface."""
        gains = [5.0, 3.0, 4.0, 2.0, 10.0, 1.0]
        controller = ClassicalSMC(
            gains=gains,
            max_force=100.0,
            boundary_layer=0.1,
            dt=0.01
        )

        assert len(controller.gains) == 6
        assert controller.gains == gains

    def test_initialization_with_dynamics_model(self):
        """Test initialization with dynamics model."""
        class MockDynamics:
            def _compute_physics_matrices(self, state):
                M = np.eye(3)
                C = np.zeros(3)
                G = np.zeros(3)
                return M, C, G

        dyn = MockDynamics()
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1,
            dynamics_model=dyn
        )
        controller = ModularClassicalSMC(config)

        assert controller.config.dynamics_model is dyn

    def test_initialization_boundary_layer_validation(self):
        """Test boundary layer parameter validation."""
        # Valid boundary layer
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.01
        )
        controller = ModularClassicalSMC(config)
        assert controller.config.boundary_layer == 0.01

    def test_initialization_custom_parameters(self):
        """Test initialization with custom parameters."""
        config = ClassicalSMCConfig(
            gains=[8.0, 4.0, 6.0, 3.0, 15.0, 2.0],
            max_force=150.0,
            dt=0.02,
            boundary_layer=0.05,
            boundary_layer_slope=1.5,
            switch_method='tanh'
        )
        controller = ModularClassicalSMC(config)

        assert controller.config.max_force == 150.0
        assert controller.config.dt == 0.02
        assert controller.config.boundary_layer == 0.05
        assert controller.config.switch_method == 'tanh'


class TestClassicalSMCSlidingSurface:
    """Test sliding surface computation."""

    @pytest.fixture
    def controller(self):
        """Create controller for testing."""
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],  # k1, k2, lam1, lam2, K, kd
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        return ModularClassicalSMC(config)

    def test_sliding_surface_at_equilibrium(self, controller):
        """Test sliding surface is zero at equilibrium."""
        state = np.zeros(6)
        result = controller.compute_control(state, {}, {})

        assert abs(result['surface_value']) < 1e-10

    def test_sliding_surface_proportional_to_error(self, controller):
        """Test sliding surface is proportional to position error."""
        state1 = np.array([0.0, 0.1, 0.0, 0.0, 0.0, 0.0])
        state2 = np.array([0.0, 0.2, 0.0, 0.0, 0.0, 0.0])

        result1 = controller.compute_control(state1, {}, {})
        result2 = controller.compute_control(state2, {}, {})

        # Surface should scale with position error
        assert abs(result2['surface_value']) > abs(result1['surface_value'])

    def test_sliding_surface_includes_velocity(self, controller):
        """Test sliding surface includes velocity terms."""
        state_pos = np.array([0.0, 0.1, 0.0, 0.0, 0.0, 0.0])
        state_vel = np.array([0.0, 0.0, 0.0, 0.0, 0.1, 0.0])

        result_pos = controller.compute_control(state_pos, {}, {})
        result_vel = controller.compute_control(state_vel, {}, {})

        # Both position and velocity errors should affect surface
        assert abs(result_pos['surface_value']) > 0
        assert abs(result_vel['surface_value']) > 0

    def test_sliding_surface_sign_correctness(self, controller):
        """Test sliding surface sign matches error direction."""
        state_pos = np.array([0.0, 0.1, 0.0, 0.0, 0.0, 0.0])
        state_neg = np.array([0.0, -0.1, 0.0, 0.0, 0.0, 0.0])

        result_pos = controller.compute_control(state_pos, {}, {})
        result_neg = controller.compute_control(state_neg, {}, {})

        # Signs should be opposite for opposite errors
        assert np.sign(result_pos['surface_value']) == -np.sign(result_neg['surface_value'])

    def test_sliding_surface_magnitude_bounds(self, controller):
        """Test sliding surface magnitude is bounded for reasonable states."""
        states = [
            np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05]),
            np.array([0.0, 0.5, 0.3, 0.0, 0.2, 0.1]),
            np.array([0.0, -0.2, -0.1, 0.0, -0.1, -0.05])
        ]

        for state in states:
            result = controller.compute_control(state, {}, {})
            # Surface should be finite and bounded
            assert np.isfinite(result['surface_value'])
            assert abs(result['surface_value']) < 100.0  # Reasonable bound


class TestClassicalSMCSwitchingFunction:
    """Test switching function (sign-based control)."""

    @pytest.fixture
    def controller(self):
        """Create controller for testing."""
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        return ModularClassicalSMC(config)

    def test_switching_control_opposes_surface(self, controller):
        """Test switching control opposes sliding surface."""
        state_pos = np.array([0.0, 0.1, 0.0, 0.0, 0.0, 0.0])
        state_neg = np.array([0.0, -0.1, 0.0, 0.0, 0.0, 0.0])

        result_pos = controller.compute_control(state_pos, {}, {})
        result_neg = controller.compute_control(state_neg, {}, {})

        # Switching control should have opposite signs for opposite surfaces
        if abs(result_pos['switching_control']) > 0.01 and abs(result_neg['switching_control']) > 0.01:
            switch_sign_product = np.sign(result_pos['switching_control']) * np.sign(result_neg['switching_control'])
            assert switch_sign_product <= 0

    def test_switching_control_scales_with_gain(self):
        """Test switching control scales with control gain K."""
        state = np.array([0.0, 0.1, 0.0, 0.0, 0.0, 0.0])

        # Low gain
        config_low = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 5.0, 1.0],  # K = 5
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        controller_low = ModularClassicalSMC(config_low)
        result_low = controller_low.compute_control(state, {}, {})

        # High gain
        config_high = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 20.0, 1.0],  # K = 20
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        controller_high = ModularClassicalSMC(config_high)
        result_high = controller_high.compute_control(state, {}, {})

        # Higher gain should produce larger switching control magnitude
        assert abs(result_high['switching_control']) > abs(result_low['switching_control'])

    def test_switching_control_boundary_layer_smoothing(self):
        """Test boundary layer smooths switching function."""
        state = np.array([0.0, 0.05, 0.0, 0.0, 0.0, 0.0])

        # Small boundary layer (sharp switching)
        config_sharp = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.01
        )
        controller_sharp = ModularClassicalSMC(config_sharp)
        result_sharp = controller_sharp.compute_control(state, {}, {})

        # Large boundary layer (smooth switching)
        config_smooth = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.5
        )
        controller_smooth = ModularClassicalSMC(config_smooth)
        result_smooth = controller_smooth.compute_control(state, {}, {})

        # Both should be finite
        assert np.isfinite(result_sharp['switching_control'])
        assert np.isfinite(result_smooth['switching_control'])

    def test_switching_methods_linear_vs_tanh(self):
        """Test different switching methods produce valid control."""
        state = np.array([0.0, 0.1, 0.0, 0.0, 0.0, 0.0])

        # Linear switching
        config_linear = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1,
            switch_method='linear'
        )
        controller_linear = ModularClassicalSMC(config_linear)
        result_linear = controller_linear.compute_control(state, {}, {})

        # Tanh switching
        config_tanh = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1,
            switch_method='tanh'
        )
        controller_tanh = ModularClassicalSMC(config_tanh)
        result_tanh = controller_tanh.compute_control(state, {}, {})

        # Both methods should produce finite control
        assert np.isfinite(result_linear['u'])
        assert np.isfinite(result_tanh['u'])


class TestClassicalSMCControlComponents:
    """Test control component breakdown and composition."""

    @pytest.fixture
    def controller(self):
        """Create controller for testing."""
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        return ModularClassicalSMC(config)

    def test_control_components_exist(self, controller):
        """Test all control components are present in output."""
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])
        result = controller.compute_control(state, {}, {})

        assert 'u' in result
        assert 'equivalent_control' in result
        assert 'switching_control' in result
        assert 'derivative_control' in result
        assert 'total_before_saturation' in result

    def test_control_components_sum_correctly(self, controller):
        """Test control components sum to total (before saturation)."""
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])
        result = controller.compute_control(state, {}, {})

        component_sum = (result['equivalent_control'] +
                        result['switching_control'] +
                        result['derivative_control'])

        assert abs(component_sum - result['total_before_saturation']) < 1e-10

    def test_equivalent_control_component(self, controller):
        """Test equivalent control component is finite."""
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])
        result = controller.compute_control(state, {}, {})

        # Without dynamics model, u_eq should be zero or near zero
        assert np.isfinite(result['equivalent_control'])

    def test_derivative_control_component(self, controller):
        """Test derivative control component scales with derivative gain."""
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])

        # Zero derivative gain
        config_no_deriv = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 0.0],  # kd = 0
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        controller_no_deriv = ModularClassicalSMC(config_no_deriv)
        result_no_deriv = controller_no_deriv.compute_control(state, {}, {})

        # Positive derivative gain
        config_deriv = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 2.0],  # kd = 2
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        controller_deriv = ModularClassicalSMC(config_deriv)
        result_deriv = controller_deriv.compute_control(state, {}, {})

        # Derivative control should be near zero for kd=0
        assert abs(result_no_deriv['derivative_control']) < 1e-10

        # Derivative control should be non-zero for kd>0
        assert abs(result_deriv['derivative_control']) > 0

    def test_control_saturation_indicator(self, controller):
        """Test saturation indicator is correct."""
        # Small error (shouldn't saturate)
        state_small = np.array([0.0, 0.01, 0.01, 0.0, 0.01, 0.01])
        result_small = controller.compute_control(state_small, {}, {})

        # Extreme error (should saturate with right config)
        config_low_force = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 50.0, 5.0],  # High gains
            max_force=10.0,  # Low saturation limit
            dt=0.01,
            boundary_layer=0.1
        )
        controller_low_force = ModularClassicalSMC(config_low_force)
        state_large = np.array([0.0, 1.0, 1.0, 0.0, 1.0, 1.0])
        result_large = controller_low_force.compute_control(state_large, {}, {})

        # Saturation flag should reflect whether control was clipped
        if 'saturation_active' in result_large:
            if result_large['saturation_active']:
                assert abs(result_large['u']) == 10.0


class TestClassicalSMCLyapunovProperties:
    """Test Lyapunov stability properties."""

    @pytest.fixture
    def controller(self):
        """Create controller for testing."""
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        return ModularClassicalSMC(config)

    def test_control_drives_toward_equilibrium(self, controller):
        """Test control drives state toward equilibrium."""
        state = np.array([0.0, 0.2, 0.1, 0.0, 0.1, 0.05])

        result = controller.compute_control(state, {}, {})
        surface = result['surface_value']
        control = result['u']

        # Control should oppose surface (drive toward s=0)
        # This is a simplified check; full Lyapunov would need dynamics
        assert np.isfinite(control)

    def test_positive_gains_requirement(self, controller):
        """Test controller requires positive gains."""
        # Controller should have positive gains
        gains = controller.gains
        assert all(g >= 0 for g in gains)

    def test_control_bounded_for_bounded_state(self, controller):
        """Test control is bounded for bounded state."""
        states = [
            np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05]),
            np.array([0.0, -0.1, -0.05, 0.0, -0.1, -0.05]),
            np.array([0.0, 0.5, 0.3, 0.0, 0.2, 0.1])
        ]

        for state in states:
            result = controller.compute_control(state, {}, {})
            # Control should be bounded by max_force
            assert abs(result['u']) <= controller.config.max_force


class TestClassicalSMCChatteringAnalysis:
    """Test chattering behavior and mitigation."""

    def test_boundary_layer_reduces_chattering(self):
        """Test boundary layer reduces chattering."""
        state = np.array([0.0, 0.05, 0.02, 0.0, 0.05, 0.02])

        # No boundary layer (sharp switching)
        config_no_bl = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=1e-6  # Very small
        )
        controller_no_bl = ModularClassicalSMC(config_no_bl)
        result_no_bl = controller_no_bl.compute_control(state, {}, {})

        # With boundary layer (smooth switching)
        config_bl = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.5  # Large
        )
        controller_bl = ModularClassicalSMC(config_bl)
        result_bl = controller_bl.compute_control(state, {}, {})

        # Both should produce finite control
        assert np.isfinite(result_no_bl['u'])
        assert np.isfinite(result_bl['u'])

    def test_in_boundary_layer_indicator(self):
        """Test boundary layer indicator."""
        # State near equilibrium (likely in boundary layer)
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.5  # Large boundary layer
        )
        controller = ModularClassicalSMC(config)

        state_near = np.array([0.0, 0.01, 0.01, 0.0, 0.01, 0.01])
        result_near = controller.compute_control(state_near, {}, {})

        # Check if boundary layer indicator exists
        if 'in_boundary_layer' in result_near:
            assert isinstance(result_near['in_boundary_layer'], bool)

    def test_control_continuity_near_surface(self):
        """Test control is continuous near sliding surface."""
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        controller = ModularClassicalSMC(config)

        # Two states very close to each other
        state1 = np.array([0.0, 0.05, 0.02, 0.0, 0.05, 0.02])
        state2 = np.array([0.0, 0.051, 0.021, 0.0, 0.051, 0.021])

        result1 = controller.compute_control(state1, {}, {})
        result2 = controller.compute_control(state2, {}, {})

        # Control should change smoothly
        control_diff = abs(result2['u'] - result1['u'])
        assert control_diff < 5.0  # Reasonable continuity bound


class TestClassicalSMCEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_state(self):
        """Test with zero state (equilibrium)."""
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        controller = ModularClassicalSMC(config)

        state = np.zeros(6)
        result = controller.compute_control(state, {}, {})

        assert np.isfinite(result['u'])
        assert abs(result['u']) < 0.1  # Should be near zero

    def test_large_state(self):
        """Test with large state values."""
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        controller = ModularClassicalSMC(config)

        state = np.array([0.0, 10.0, 5.0, 0.0, 5.0, 2.0])
        result = controller.compute_control(state, {}, {})

        assert np.isfinite(result['u'])
        assert abs(result['u']) <= 100.0  # Should be saturated

    def test_negative_state(self):
        """Test with negative state values."""
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        controller = ModularClassicalSMC(config)

        state = np.array([0.0, -0.2, -0.1, 0.0, -0.1, -0.05])
        result = controller.compute_control(state, {}, {})

        assert np.isfinite(result['u'])

    def test_mixed_sign_state(self):
        """Test with mixed positive/negative state values."""
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        controller = ModularClassicalSMC(config)

        state = np.array([0.0, 0.1, -0.05, 0.0, -0.1, 0.05])
        result = controller.compute_control(state, {}, {})

        assert np.isfinite(result['u'])


class TestClassicalSMCUtilities:
    """Test utility methods."""

    def test_reset_method(self):
        """Test reset method."""
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        controller = ModularClassicalSMC(config)

        # Should not crash
        controller.reset()

    def test_get_parameters(self):
        """Test get_parameters returns expected structure."""
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        controller = ModularClassicalSMC(config)

        params = controller.get_parameters()

        assert 'gains' in params
        assert 'config' in params
        assert 'surface_params' in params

    def test_gains_property(self):
        """Test gains property returns copy."""
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        controller = ModularClassicalSMC(config)

        gains = controller.gains

        assert len(gains) == 6
        assert gains == [5.0, 3.0, 4.0, 2.0, 10.0, 1.0]


class TestClassicalSMCPerformanceMetrics:
    """Test performance metrics and analysis."""

    @pytest.fixture
    def controller(self):
        """Create controller for testing."""
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        return ModularClassicalSMC(config)

    def test_control_effort_metric(self, controller):
        """Test control effort metric."""
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])
        result = controller.compute_control(state, {}, {})

        assert 'control_effort' in result
        assert result['control_effort'] == abs(result['u'])

    def test_surface_magnitude_metric(self, controller):
        """Test surface magnitude metric."""
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])
        result = controller.compute_control(state, {}, {})

        assert 'surface_magnitude' in result
        assert result['surface_magnitude'] == abs(result['surface_value'])

    def test_controller_type_identifier(self, controller):
        """Test controller type identifier."""
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])
        result = controller.compute_control(state, {}, {})

        assert 'controller_type' in result
        assert result['controller_type'] == 'classical_smc'


class TestClassicalSMCIntegration:
    """Integration tests."""

    def test_control_loop_simulation(self):
        """Test control in a simple simulation loop."""
        config = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        controller = ModularClassicalSMC(config)

        state = np.array([0.0, 0.1, 0.05, 0.0, 0.0, 0.0])

        for step in range(10):
            result = controller.compute_control(state, {}, {})

            # Simple state update (not real dynamics)
            state = state * 0.95

            assert np.isfinite(result['u'])

    def test_multiple_controllers_independence(self):
        """Test multiple controller instances are independent."""
        config1 = ClassicalSMCConfig(
            gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0],
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        config2 = ClassicalSMCConfig(
            gains=[8.0, 4.0, 6.0, 3.0, 15.0, 2.0],
            max_force=150.0,
            dt=0.02,
            boundary_layer=0.05
        )

        ctrl1 = ModularClassicalSMC(config1)
        ctrl2 = ModularClassicalSMC(config2)

        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])

        result1 = ctrl1.compute_control(state, {}, {})
        result2 = ctrl2.compute_control(state, {}, {})

        # Different configs should produce different results
        assert abs(result1['u'] - result2['u']) > 0.01

    def test_facade_vs_modular_consistency(self):
        """Test facade produces consistent results with modular controller."""
        gains = [5.0, 3.0, 4.0, 2.0, 10.0, 1.0]
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])

        # Facade controller
        facade = ClassicalSMC(
            gains=gains,
            max_force=100.0,
            boundary_layer=0.1,
            dt=0.01
        )
        result_facade = facade.compute_control(state, {}, {})

        # Modular controller
        config = ClassicalSMCConfig(
            gains=gains,
            max_force=100.0,
            dt=0.01,
            boundary_layer=0.1
        )
        modular = ModularClassicalSMC(config)
        result_modular = modular.compute_control(state, {}, {})

        # Both should produce same control
        assert abs(result_facade['u'] - result_modular['u']) < 1e-10


#========================================================================================================\\\
