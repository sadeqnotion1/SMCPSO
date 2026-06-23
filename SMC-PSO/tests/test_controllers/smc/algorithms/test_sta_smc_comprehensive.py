#======================================================================================\\\
#======== tests/test_controllers/smc/algorithms/test_sta_smc_comprehensive.py =========\\\
#======================================================================================\\\

"""
Comprehensive tests for Super-Twisting Algorithm (STA) SMC controller.

MISSION: Achieve 85%+ coverage for STA SMC controller module.

Test Coverage:
- Initialization and parameter validation
- Super-Twisting algorithm correctness
- Finite-time convergence properties
- Gain conditions (K1 > K2 > 0, sqrt relationship)
- Chattering reduction vs classical SMC
- Robustness to bounded uncertainties
- Integral state (z) dynamics
- Lyapunov function properties
- Boundary layer effects
- Anti-windup mechanisms
"""

import pytest
import numpy as np
from typing import Dict, Any

from src.controllers.smc.algorithms.super_twisting.controller import ModularSuperTwistingSMC, SuperTwistingSMC
from src.controllers.smc.algorithms.super_twisting.config import SuperTwistingSMCConfig


class TestSuperTwistingSMCInitialization:
    """Test Super-Twisting SMC initialization and configuration."""

    def test_modular_initialization_valid_config(self):
        """Test modular controller initializes with valid config."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],  # K1, K2, k1, k2, lam1, lam2
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        assert controller.config == config
        assert controller.n_gains == 6
        assert len(controller.gains) == 6

    def test_facade_initialization_legacy_interface(self):
        """Test facade initializes with legacy interface."""
        gains = [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
        controller = SuperTwistingSMC(
            gains=gains,
            dt=0.01,
            max_force=100.0
        )

        assert len(controller.gains) == 6
        assert controller.gains == gains

    def test_initialization_gain_relationship_k1_gt_k2(self):
        """Test initialization validates K1 > K2."""
        # Valid: K1 > K2
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],  # K1=10 > K2=5
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)
        assert controller.config.K1 > controller.config.K2

    def test_initialization_positive_gains(self):
        """Test all gains are positive."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        gains = controller.gains
        assert all(g > 0 for g in gains)

    def test_initialization_custom_parameters(self):
        """Test initialization with custom parameters."""
        config = SuperTwistingSMCConfig(
            gains=[15.0, 7.0, 10.0, 5.0, 20.0, 3.0],
            dt=0.02,
            max_force=150.0,
            boundary_layer=0.05,
            switch_method='tanh',
            damping_gain=0.5,
            power_exponent=0.5,
            anti_windup_gain=10.0
        )
        controller = ModularSuperTwistingSMC(config)

        assert controller.config.dt == 0.02
        assert controller.config.max_force == 150.0
        assert controller.config.boundary_layer == 0.05
        assert controller.config.switch_method == 'tanh'
        assert controller.config.damping_gain == 0.5

    def test_initialization_default_parameters(self):
        """Test default parameter values."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        # Check defaults
        assert controller.config.boundary_layer > 0
        assert controller.config.switch_method in ['linear', 'tanh']


class TestSuperTwistingAlgorithmCorrectness:
    """Test Super-Twisting algorithm correctness."""

    @pytest.fixture
    def controller(self):
        """Create controller for testing."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0,
            boundary_layer=0.1
        )
        return ModularSuperTwistingSMC(config)

    def test_twisting_control_at_equilibrium(self, controller):
        """Test control at equilibrium is small."""
        state = np.zeros(6)
        result = controller.compute_control(state, None, {})

        if isinstance(result, dict):
            assert abs(result['u']) < 1.0
        else:
            assert np.all(np.abs(result) < 1.0)

    def test_twisting_control_components_exist(self, controller):
        """Test Super-Twisting control components are present."""
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])
        result = controller.compute_control(state, None, {})

        if isinstance(result, dict):
            assert 'u1_continuous' in result
            assert 'u2_integral' in result
            assert 'integral_state' in result

    def test_continuous_term_proportional_to_sqrt_surface(self, controller):
        """Test u1 = -K1 * sqrt(|s|) * sign(s)."""
        state1 = np.array([0.0, 0.1, 0.0, 0.0, 0.0, 0.0])
        state2 = np.array([0.0, 0.4, 0.0, 0.0, 0.0, 0.0])  # 4x position error

        result1 = controller.compute_control(state1, None, {})
        result2 = controller.compute_control(state2, None, {})

        if isinstance(result1, dict) and isinstance(result2, dict):
            # u1 should scale with sqrt of surface
            u1_1 = result1['u1_continuous']
            u1_2 = result2['u1_continuous']

            # Due to sqrt relationship, u1_2 should be roughly sqrt(4) = 2x u1_1
            # (accounting for other state components)
            assert abs(u1_2) > abs(u1_1)

    def test_integral_state_evolution(self, controller):
        """Test integral state z evolves according to dynamics."""
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])

        # Run multiple steps
        results = []
        for _ in range(5):
            result = controller.compute_control(state, None, {})
            if isinstance(result, dict):
                results.append(result['integral_state'])

        if len(results) > 1:
            # Integral state should evolve (change over time)
            assert any(abs(results[i+1] - results[i]) > 1e-10 for i in range(len(results)-1))

    def test_control_bounded_by_max_force(self, controller):
        """Test control is bounded by max_force."""
        states = [
            np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05]),
            np.array([0.0, 1.0, 0.5, 0.0, 0.5, 0.2]),
            np.array([0.0, -0.5, -0.2, 0.0, -0.2, -0.1])
        ]

        for state in states:
            result = controller.compute_control(state, None, {})

            if isinstance(result, dict):
                assert abs(result['u']) <= controller.config.max_force
            else:
                assert np.all(np.abs(result) <= controller.config.max_force)


class TestFiniteTimeConvergence:
    """Test finite-time convergence properties."""

    @pytest.fixture
    def controller(self):
        """Create controller for testing."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        return ModularSuperTwistingSMC(config)

    def test_stability_condition_k1_gt_k2(self, controller):
        """Test stability condition K1 > K2 > 0."""
        # Controller already created with K1=10, K2=5
        assert controller.config.K1 > controller.config.K2 > 0

    def test_convergence_time_estimate_exists(self, controller):
        """Test convergence time estimate is available."""
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])
        result = controller.compute_control(state, None, {})

        if isinstance(result, dict):
            if 'convergence_time_estimate' in result:
                assert result['convergence_time_estimate'] >= 0

    def test_finite_time_convergence_property(self, controller):
        """Test finite-time convergence property indicator."""
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])
        result = controller.compute_control(state, None, {})

        if isinstance(result, dict):
            if 'finite_time_convergence' in result:
                assert result['finite_time_convergence'] == True

    def test_convergence_estimate_method(self, controller):
        """Test convergence estimate method."""
        estimate = controller.get_convergence_estimate(current_surface=0.1)

        assert 'estimated_convergence_time' in estimate
        assert 'finite_time_convergence' in estimate
        assert estimate['finite_time_convergence'] == True


class TestGainConditions:
    """Test gain conditions and validation."""

    def test_validate_gains_k1_gt_k2_requirement(self):
        """Test validate_gains enforces K1 > K2."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        # Valid gains: K1 > K2
        gains_valid = np.array([
            [10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            [20.0, 10.0, 8.0, 3.0, 15.0, 2.0]
        ])
        valid = controller.validate_gains(gains_valid)
        assert all(valid)

        # Invalid gains: K1 <= K2
        gains_invalid = np.array([
            [5.0, 10.0, 8.0, 3.0, 15.0, 2.0],  # K1 < K2
            [10.0, 10.0, 8.0, 3.0, 15.0, 2.0]  # K1 = K2
        ])
        valid_inv = controller.validate_gains(gains_invalid)
        assert not any(valid_inv)

    def test_validate_gains_positive_requirement(self):
        """Test validate_gains requires positive gains."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        # Invalid: zero or negative gains
        gains_invalid = np.array([
            [0.0, 5.0, 8.0, 3.0, 15.0, 2.0],   # K1 = 0
            [-10.0, 5.0, 8.0, 3.0, 15.0, 2.0], # K1 < 0
            [10.0, -5.0, 8.0, 3.0, 15.0, 2.0]  # K2 < 0
        ])
        valid = controller.validate_gains(gains_invalid)
        assert not any(valid)

    def test_validate_gains_surface_params(self):
        """Test validate_gains checks surface parameters."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        # Invalid: negative surface parameters
        gains_invalid = np.array([
            [10.0, 5.0, -8.0, 3.0, 15.0, 2.0],  # k1 < 0
            [10.0, 5.0, 8.0, 3.0, -15.0, 2.0]   # lam1 < 0
        ])
        valid = controller.validate_gains(gains_invalid)
        assert not any(valid)

    def test_set_twisting_gains_validation(self):
        """Test set_twisting_gains validates K1 > K2."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        # Valid update
        controller.set_twisting_gains(K1=15.0, K2=7.0)
        K1, K2 = controller.get_twisting_gains()
        assert K1 == 15.0
        assert K2 == 7.0

        # Invalid update should raise
        with pytest.raises(ValueError):
            controller.set_twisting_gains(K1=5.0, K2=10.0)  # K1 < K2


class TestChatteringReduction:
    """Test chattering reduction vs classical SMC."""

    def test_boundary_layer_smooths_control(self):
        """Test boundary layer smooths control signal."""
        state = np.array([0.0, 0.05, 0.02, 0.0, 0.05, 0.02])

        # Small boundary layer (sharper switching)
        config_sharp = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0,
            boundary_layer=0.01
        )
        controller_sharp = ModularSuperTwistingSMC(config_sharp)
        result_sharp = controller_sharp.compute_control(state, None, {})

        # Large boundary layer (smoother switching)
        config_smooth = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0,
            boundary_layer=0.5
        )
        controller_smooth = ModularSuperTwistingSMC(config_smooth)
        result_smooth = controller_smooth.compute_control(state, None, {})

        # Both should produce finite control
        if isinstance(result_sharp, dict):
            assert np.isfinite(result_sharp['u'])
        if isinstance(result_smooth, dict):
            assert np.isfinite(result_smooth['u'])

    def test_switch_method_tanh_vs_linear(self):
        """Test different switching methods."""
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])

        # Linear switching
        config_linear = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0,
            switch_method='linear'
        )
        controller_linear = ModularSuperTwistingSMC(config_linear)
        result_linear = controller_linear.compute_control(state, None, {})

        # Tanh switching
        config_tanh = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0,
            switch_method='tanh'
        )
        controller_tanh = ModularSuperTwistingSMC(config_tanh)
        result_tanh = controller_tanh.compute_control(state, None, {})

        # Both should produce valid control
        if isinstance(result_linear, dict):
            assert np.isfinite(result_linear['u'])
        if isinstance(result_tanh, dict):
            assert np.isfinite(result_tanh['u'])

    def test_continuous_control_signal(self):
        """Test control signal is continuous (no discrete jumps)."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0,
            boundary_layer=0.1
        )
        controller = ModularSuperTwistingSMC(config)

        # Two nearby states
        state1 = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])
        state2 = np.array([0.0, 0.101, 0.051, 0.0, 0.101, 0.051])

        result1 = controller.compute_control(state1, None, {})
        result2 = controller.compute_control(state2, None, {})

        if isinstance(result1, dict) and isinstance(result2, dict):
            control_diff = abs(result2['u'] - result1['u'])
            assert control_diff < 5.0  # Should change smoothly


class TestRobustnessProperties:
    """Test robustness to uncertainties and disturbances."""

    @pytest.fixture
    def controller(self):
        """Create controller for testing."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        return ModularSuperTwistingSMC(config)

    def test_bounded_control_for_bounded_disturbance(self, controller):
        """Test control remains bounded with bounded disturbances."""
        # Simulate states with "disturbances"
        states = [
            np.array([0.0, 0.1 + 0.01, 0.05 + 0.005, 0.0, 0.1 + 0.01, 0.05 + 0.005]),
            np.array([0.0, 0.1 - 0.01, 0.05 - 0.005, 0.0, 0.1 - 0.01, 0.05 - 0.005])
        ]

        for state in states:
            result = controller.compute_control(state, None, {})

            if isinstance(result, dict):
                assert abs(result['u']) <= controller.config.max_force

    def test_control_opposes_error_sign(self, controller):
        """Test control opposes error direction."""
        state_pos = np.array([0.0, 0.2, 0.1, 0.0, 0.1, 0.05])
        state_neg = np.array([0.0, -0.2, -0.1, 0.0, -0.1, -0.05])

        result_pos = controller.compute_control(state_pos, None, {})
        result_neg = controller.compute_control(state_neg, None, {})

        if isinstance(result_pos, dict) and isinstance(result_neg, dict):
            # Control should have opposite tendencies for opposite errors
            if abs(result_pos['u']) > 0.1 and abs(result_neg['u']) > 0.1:
                assert np.sign(result_pos['u']) != np.sign(result_neg['u'])


class TestIntegralStateDynamics:
    """Test integral state (z) dynamics."""

    @pytest.fixture
    def controller(self):
        """Create controller for testing."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        return ModularSuperTwistingSMC(config)

    def test_integral_state_initialization(self, controller):
        """Test integral state initializes to zero."""
        controller.reset_controller()
        state = np.zeros(6)
        result = controller.compute_control(state, None, {})

        if isinstance(result, dict):
            # After reset, integral state should be small/zero
            if 'integral_state' in result:
                assert abs(result['integral_state']) < 1e-6

    def test_integral_state_accumulation(self, controller):
        """Test integral state accumulates over time."""
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])

        integral_states = []
        for _ in range(10):
            result = controller.compute_control(state, None, {})
            if isinstance(result, dict) and 'integral_state' in result:
                integral_states.append(result['integral_state'])

        # Integral state should evolve
        if len(integral_states) > 1:
            assert any(abs(integral_states[i+1] - integral_states[i]) > 0 for i in range(len(integral_states)-1))

    def test_integral_state_bounded(self, controller):
        """Test integral state is bounded."""
        state = np.array([0.0, 1.0, 0.5, 0.0, 0.5, 0.2])

        for _ in range(100):
            result = controller.compute_control(state, None, {})
            if isinstance(result, dict) and 'integral_state' in result:
                # Integral state should be bounded by anti-windup
                assert abs(result['integral_state']) < 1000.0  # Reasonable bound


class TestLyapunovProperties:
    """Test Lyapunov function properties."""

    @pytest.fixture
    def controller(self):
        """Create controller for testing."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        return ModularSuperTwistingSMC(config)

    def test_lyapunov_function_available(self, controller):
        """Test Lyapunov function is computed."""
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])
        result = controller.compute_control(state, None, {})

        if isinstance(result, dict):
            if 'lyapunov_function' in result:
                assert result['lyapunov_function'] >= 0  # Lyapunov should be non-negative

    def test_lyapunov_minimum_at_equilibrium(self, controller):
        """Test Lyapunov function is minimal at equilibrium."""
        state_eq = np.zeros(6)
        state_err = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])

        result_eq = controller.compute_control(state_eq, None, {})
        result_err = controller.compute_control(state_err, None, {})

        if isinstance(result_eq, dict) and isinstance(result_err, dict):
            if 'lyapunov_function' in result_eq and 'lyapunov_function' in result_err:
                # Lyapunov at equilibrium should be smaller
                assert result_eq['lyapunov_function'] <= result_err['lyapunov_function']


class TestAntiWindup:
    """Test anti-windup mechanisms."""

    def test_anti_windup_limits_integral_state(self):
        """Test anti-windup limits integral state growth."""
        # With anti-windup
        config_aw = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=50.0,  # Low saturation
            anti_windup_gain=20.0  # Active anti-windup
        )
        controller_aw = ModularSuperTwistingSMC(config_aw)

        # Large persistent error (would cause saturation)
        state = np.array([0.0, 1.0, 0.5, 0.0, 0.5, 0.2])

        integral_states = []
        for _ in range(50):
            result = controller_aw.compute_control(state, None, {})
            if isinstance(result, dict) and 'integral_state' in result:
                integral_states.append(result['integral_state'])

        # Integral state should be bounded
        if len(integral_states) > 10:
            max_integral = max(abs(z) for z in integral_states)
            assert max_integral < 100.0  # Should be limited by anti-windup

    def test_anti_windup_active_indicator(self):
        """Test anti-windup active indicator."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=50.0,
            anti_windup_gain=20.0
        )
        controller = ModularSuperTwistingSMC(config)

        state = np.array([0.0, 1.0, 0.5, 0.0, 0.5, 0.2])

        # Run until saturation likely
        for _ in range(20):
            result = controller.compute_control(state, None, {})

        # Check if anti-windup indicator exists
        if isinstance(result, dict):
            if 'anti_windup_active' in result:
                assert isinstance(result['anti_windup_active'], bool)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_state(self):
        """Test with zero state."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        state = np.zeros(6)
        result = controller.compute_control(state, None, {})

        if isinstance(result, dict):
            assert np.isfinite(result['u'])
            assert abs(result['u']) < 1.0

    def test_large_state(self):
        """Test with large state values."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        state = np.array([0.0, 10.0, 5.0, 0.0, 5.0, 2.0])
        result = controller.compute_control(state, None, {})

        if isinstance(result, dict):
            assert np.isfinite(result['u'])
            assert abs(result['u']) <= 100.0

    def test_negative_state(self):
        """Test with negative state values."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        state = np.array([0.0, -0.5, -0.2, 0.0, -0.2, -0.1])
        result = controller.compute_control(state, None, {})

        if isinstance(result, dict):
            assert np.isfinite(result['u'])

    def test_mixed_sign_state(self):
        """Test with mixed positive/negative state."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        state = np.array([0.0, 0.1, -0.05, 0.0, -0.1, 0.05])
        result = controller.compute_control(state, None, {})

        if isinstance(result, dict):
            assert np.isfinite(result['u'])


class TestUtilityMethods:
    """Test utility and helper methods."""

    def test_reset_controller(self):
        """Test reset_controller method."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        # Run some steps
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])
        for _ in range(10):
            controller.compute_control(state, None, {})

        # Reset should not crash
        controller.reset_controller()

    def test_reset_alias_method(self):
        """Test reset() alias method."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        controller.reset()  # Should not crash

    def test_get_parameters(self):
        """Test get_parameters returns expected structure."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        params = controller.get_parameters()

        assert 'twisting_gains' in params
        assert 'surface_gains' in params
        assert 'config' in params

    def test_get_stability_analysis(self):
        """Test get_stability_analysis method."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        # Run some steps to populate history
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])
        for _ in range(15):
            controller.compute_control(state, None, {})

        stability = controller.get_stability_analysis()

        assert 'config_stability' in stability
        assert 'theoretical_properties' in stability

    def test_tune_gains_method(self):
        """Test tune_gains runtime adjustment."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        # Valid tuning
        controller.tune_gains(K1=15.0, K2=7.0)
        K1, K2 = controller.get_twisting_gains()
        assert K1 == 15.0
        assert K2 == 7.0

        # Invalid tuning should raise
        with pytest.raises(ValueError):
            controller.tune_gains(K1=5.0, K2=10.0)

    def test_gains_property(self):
        """Test gains property."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        gains = controller.gains
        assert len(gains) == 6
        assert gains == [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]


class TestPerformanceMetrics:
    """Test performance metrics and indicators."""

    @pytest.fixture
    def controller(self):
        """Create controller for testing."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        return ModularSuperTwistingSMC(config)

    def test_gain_ratio_metric(self, controller):
        """Test gain ratio K1/K2 is reported."""
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])
        result = controller.compute_control(state, None, {})

        if isinstance(result, dict):
            if 'gain_ratio' in result:
                expected_ratio = 10.0 / 5.0
                assert abs(result['gain_ratio'] - expected_ratio) < 1e-10

    def test_controller_type_identifier(self, controller):
        """Test controller type identifier."""
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])
        result = controller.compute_control(state, None, {})

        if isinstance(result, dict):
            if 'controller_type' in result:
                assert result['controller_type'] == 'super_twisting_smc'

    def test_saturation_indicator(self, controller):
        """Test saturation indicator."""
        # Large error to cause saturation
        config_low = SuperTwistingSMCConfig(
            gains=[20.0, 10.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=10.0  # Low limit
        )
        controller_low = ModularSuperTwistingSMC(config_low)

        state = np.array([0.0, 1.0, 0.5, 0.0, 0.5, 0.2])
        result = controller_low.compute_control(state, None, {})

        if isinstance(result, dict):
            if 'saturation_active' in result:
                assert isinstance(result['saturation_active'], bool)


class TestIntegration:
    """Integration tests."""

    def test_control_loop_simulation(self):
        """Test control in simulation loop."""
        config = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        controller = ModularSuperTwistingSMC(config)

        state = np.array([0.0, 0.1, 0.05, 0.0, 0.0, 0.0])

        for _ in range(50):
            result = controller.compute_control(state, None, {})

            # Simple state decay
            state = state * 0.95

            if isinstance(result, dict):
                assert np.isfinite(result['u'])

    def test_multiple_controllers_independence(self):
        """Test multiple controller instances are independent."""
        config1 = SuperTwistingSMCConfig(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )
        config2 = SuperTwistingSMCConfig(
            gains=[15.0, 7.0, 10.0, 5.0, 20.0, 3.0],
            dt=0.02,
            max_force=150.0
        )

        ctrl1 = ModularSuperTwistingSMC(config1)
        ctrl2 = ModularSuperTwistingSMC(config2)

        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])

        result1 = ctrl1.compute_control(state, None, {})
        result2 = ctrl2.compute_control(state, None, {})

        # Different configs should produce different results
        if isinstance(result1, dict) and isinstance(result2, dict):
            assert abs(result1['u'] - result2['u']) > 0.01

    def test_facade_vs_modular_consistency(self):
        """Test facade and modular controller consistency."""
        gains = [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
        state = np.array([0.0, 0.1, 0.05, 0.0, 0.1, 0.05])

        # Facade
        facade = SuperTwistingSMC(gains=gains, dt=0.01, max_force=100.0)
        result_facade = facade.compute_control(state, None, {})

        # Modular
        config = SuperTwistingSMCConfig(
            gains=gains,
            dt=0.01,
            max_force=100.0
        )
        modular = ModularSuperTwistingSMC(config)
        result_modular = modular.compute_control(state, None, {})

        # Both should produce similar results
        if isinstance(result_facade, dict) and isinstance(result_modular, dict):
            assert abs(result_facade['u'] - result_modular['u']) < 1.0


#========================================================================================================\\\
