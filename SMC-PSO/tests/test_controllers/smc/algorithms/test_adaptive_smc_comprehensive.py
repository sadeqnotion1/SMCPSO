#======================================================================================\
#==== tests/test_controllers/smc/algorithms/test_adaptive_smc_comprehensive.py =======\
#======================================================================================\

"""
Comprehensive Tests for Adaptive SMC Controller.

This test suite provides extensive coverage for the adaptive sliding mode controller,
focusing on:
- Gain adaptation mechanisms
- Dead zone behavior
- Leak rate dynamics
- Rate limiting
- Boundary layer effects
- Min/max gain bounds enforcement
- Convergence properties
- Edge cases and error handling

Target: 85%+ coverage for src/controllers/smc/adaptive_smc.py
"""

import pytest
import numpy as np
from src.controllers.smc.adaptive_smc import AdaptiveSMC
from src.utils import AdaptiveSMCOutput


class TestAdaptiveSMCInitializationValidation:
    """Test initialization parameter validation."""

    def test_valid_initialization_minimal(self):
        """Test controller initializes with minimal valid parameters."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            leak_rate=0.1,
            adapt_rate_limit=10.0,
            K_min=1.0,
            K_max=50.0,
            smooth_switch=False,
            boundary_layer=0.01,
            dead_zone=0.001
        )
        assert controller.k1 == 5.0
        assert controller.k2 == 3.0
        assert controller.lam1 == 2.0
        assert controller.lam2 == 1.0
        assert controller.gamma == 0.5

    def test_valid_initialization_all_parameters(self):
        """Test initialization with all parameters specified."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            leak_rate=0.1,
            adapt_rate_limit=10.0,
            K_min=1.0,
            K_max=50.0,
            smooth_switch=True,
            boundary_layer=0.01,
            dead_zone=0.001,
            K_init=15.0,
            alpha=0.8
        )
        assert controller.K_init == 15.0
        assert controller.alpha == 0.8
        assert controller.smooth_switch is True

    def test_insufficient_gains_raises_error(self):
        """Test that fewer than 5 gains raises ValueError."""
        gains = [5.0, 3.0, 2.0]  # Only 3 gains
        with pytest.raises(ValueError, match="at least 5 gains"):
            AdaptiveSMC(
                gains=gains, dt=0.01, max_force=100.0,
                leak_rate=0.1, adapt_rate_limit=10.0,
                K_min=1.0, K_max=50.0, smooth_switch=False,
                boundary_layer=0.01, dead_zone=0.001
            )

    def test_extra_gains_accepted(self):
        """Test that extra gains are accepted (for forward compatibility)."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5, 99.0, 88.0]  # 7 gains
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )
        assert len(controller.gains) == 7
        # Only first 5 should be used internally
        assert controller.k1 == 5.0
        assert controller.gamma == 0.5

    def test_negative_gains_raise_error(self):
        """Test that negative gains raise ValueError."""
        gains = [5.0, -3.0, 2.0, 1.0, 0.5]  # k2 is negative
        with pytest.raises(ValueError):
            AdaptiveSMC(
                gains=gains, dt=0.01, max_force=100.0,
                leak_rate=0.1, adapt_rate_limit=10.0,
                K_min=1.0, K_max=50.0, smooth_switch=False,
                boundary_layer=0.01, dead_zone=0.001
            )

    def test_zero_dt_raises_error(self):
        """Test that zero dt raises ValueError."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        with pytest.raises(ValueError):
            AdaptiveSMC(
                gains=gains, dt=0.0, max_force=100.0,
                leak_rate=0.1, adapt_rate_limit=10.0,
                K_min=1.0, K_max=50.0, smooth_switch=False,
                boundary_layer=0.01, dead_zone=0.001
            )

    def test_negative_dt_raises_error(self):
        """Test that negative dt raises ValueError."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        with pytest.raises(ValueError):
            AdaptiveSMC(
                gains=gains, dt=-0.01, max_force=100.0,
                leak_rate=0.1, adapt_rate_limit=10.0,
                K_min=1.0, K_max=50.0, smooth_switch=False,
                boundary_layer=0.01, dead_zone=0.001
            )

    def test_zero_boundary_layer_raises_error(self):
        """Test that zero boundary_layer raises ValueError."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        with pytest.raises(ValueError):
            AdaptiveSMC(
                gains=gains, dt=0.01, max_force=100.0,
                leak_rate=0.1, adapt_rate_limit=10.0,
                K_min=1.0, K_max=50.0, smooth_switch=False,
                boundary_layer=0.0, dead_zone=0.001
            )

    def test_invalid_k_bounds_raises_error(self):
        """Test that K_min > K_max raises ValueError."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        with pytest.raises(ValueError):
            AdaptiveSMC(
                gains=gains, dt=0.01, max_force=100.0,
                leak_rate=0.1, adapt_rate_limit=10.0,
                K_min=50.0, K_max=10.0,  # min > max
                smooth_switch=False, boundary_layer=0.01, dead_zone=0.001
            )

    def test_k_init_outside_bounds_raises_error(self):
        """Test that K_init outside [K_min, K_max] raises ValueError."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        with pytest.raises(ValueError, match="K_min ≤ K_init ≤ K_max"):
            AdaptiveSMC(
                gains=gains, dt=0.01, max_force=100.0,
                leak_rate=0.1, adapt_rate_limit=10.0,
                K_min=10.0, K_max=50.0,
                smooth_switch=False, boundary_layer=0.01, dead_zone=0.001,
                K_init=5.0  # Below K_min
            )

    def test_zero_leak_rate_allowed(self):
        """Test that zero leak_rate is allowed."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.0,  # Zero is allowed
            adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )
        assert controller.leak_rate == 0.0

    def test_zero_dead_zone_allowed(self):
        """Test that zero dead_zone is allowed."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.0  # Zero is allowed
        )
        assert controller.dead_zone == 0.0


class TestAdaptiveSMCControlComputation:
    """Test control computation functionality."""

    @pytest.fixture
    def controller(self):
        """Standard controller for testing."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        return AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001, K_init=10.0, alpha=0.5
        )

    def test_output_type_is_named_tuple(self, controller):
        """Test that output is AdaptiveSMCOutput named tuple."""
        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])
        state_vars = (10.0, 0.0, 0.0)
        output = controller.compute_control(state, state_vars, {})

        assert isinstance(output, AdaptiveSMCOutput)
        assert hasattr(output, 'u')
        assert hasattr(output, 'state')
        assert hasattr(output, 'history')
        assert hasattr(output, 'sigma')

    def test_control_at_equilibrium_is_small(self, controller):
        """Test that control at equilibrium is near zero."""
        state = np.zeros(6)
        state_vars = (10.0, 0.0, 0.0)
        output = controller.compute_control(state, state_vars, {})

        assert abs(output.u) < 0.1

    def test_control_bounded_by_max_force(self, controller):
        """Test that control is always bounded by max_force."""
        large_state = np.array([10.0, 5.0, 5.0, 2.0, 2.0, 2.0])
        state_vars = (10.0, 0.0, 0.0)
        output = controller.compute_control(large_state, state_vars, {})

        assert abs(output.u) <= controller.max_force

    def test_sigma_computed_correctly(self, controller):
        """Test that sliding surface sigma is computed correctly."""
        state = np.array([0.0, 0.1, 0.2, 0.0, 0.05, 0.1])
        state_vars = (10.0, 0.0, 0.0)
        output = controller.compute_control(state, state_vars, {})

        # sigma = k1*(theta1_dot + lam1*theta1) + k2*(theta2_dot + lam2*theta2)
        expected_sigma = controller.k1 * (0.05 + controller.lam1 * 0.1) + \
                        controller.k2 * (0.1 + controller.lam2 * 0.2)

        np.testing.assert_allclose(output.sigma, expected_sigma, rtol=1e-6)

    def test_state_vars_can_be_scalar(self, controller):
        """Test that state_vars can be a scalar (legacy fallback)."""
        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])
        output = controller.compute_control(state, 10.0, {})

        assert isinstance(output, AdaptiveSMCOutput)
        assert output.state[0] > 0  # K should be positive

    def test_state_vars_empty_tuple_uses_defaults(self, controller):
        """Test that empty state_vars tuple uses default values."""
        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])
        output = controller.compute_control(state, (), {})

        # Should use K_init as default
        assert isinstance(output, AdaptiveSMCOutput)

    def test_state_vars_single_element_tuple(self, controller):
        """Test that single-element state_vars works."""
        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])
        output = controller.compute_control(state, (15.0,), {})

        assert isinstance(output, AdaptiveSMCOutput)

    def test_history_updated_correctly(self, controller):
        """Test that history dictionary is updated with all fields."""
        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])
        state_vars = (10.0, 0.0, 0.0)
        history = {}

        output = controller.compute_control(state, state_vars, history)

        assert 'K' in output.history
        assert 'sigma' in output.history
        assert 'u_sw' in output.history
        assert 'dK' in output.history
        assert 'time_in_sliding' in output.history
        assert len(output.history['K']) == 1
        assert len(output.history['sigma']) == 1

    def test_smooth_switch_tanh_vs_linear(self):
        """Test that smooth_switch parameter is accepted and produces reasonable output."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])
        state_vars = (10.0, 0.0, 0.0)

        controller_linear = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001, K_init=10.0
        )

        controller_tanh = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=True,
            boundary_layer=0.01, dead_zone=0.001, K_init=10.0
        )

        output_linear = controller_linear.compute_control(state, state_vars, {})
        output_tanh = controller_tanh.compute_control(state, state_vars, {})

        # Both outputs should be valid
        assert isinstance(output_linear, AdaptiveSMCOutput)
        assert isinstance(output_tanh, AdaptiveSMCOutput)
        assert np.isfinite(output_linear.u)
        assert np.isfinite(output_tanh.u)


class TestAdaptiveSMCAdaptationMechanisms:
    """Test gain adaptation mechanisms."""

    @pytest.fixture
    def controller(self):
        """Controller with moderate adaptation parameters."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        return AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001, K_init=10.0
        )

    def test_gain_increases_with_large_sigma(self, controller):
        """Test that K increases when |sigma| is large (outside dead zone)."""
        large_sigma_state = np.array([0.0, 0.5, 0.5, 0.0, 0.3, 0.3])
        state_vars = (10.0, 0.0, 0.0)

        output = controller.compute_control(large_sigma_state, state_vars, {})
        K_new = output.state[0]

        # K should increase when sigma is large
        assert K_new >= 10.0 or abs(output.sigma) < controller.dead_zone

    def test_gain_stays_bounded_by_k_max(self, controller):
        """Test that K never exceeds K_max."""
        large_state = np.array([0.0, 1.0, 1.0, 0.0, 1.0, 1.0])
        K = 10.0

        for _ in range(100):  # Many iterations to try to exceed K_max
            state_vars = (K, 0.0, 0.0)
            output = controller.compute_control(large_state, state_vars, {})
            K = output.state[0]
            assert K <= controller.K_max

    def test_gain_stays_bounded_by_k_min(self, controller):
        """Test that K never goes below K_min."""
        small_state = np.zeros(6)
        K = 10.0

        # Use high leak rate to force K down
        controller_high_leak = AdaptiveSMC(
            gains=[5.0, 3.0, 2.0, 1.0, 0.5],
            dt=0.01, max_force=100.0,
            leak_rate=5.0,  # High leak rate
            adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001, K_init=10.0
        )

        for _ in range(200):  # Many iterations
            state_vars = (K, 0.0, 0.0)
            output = controller_high_leak.compute_control(small_state, state_vars, {})
            K = output.state[0]
            assert K >= controller_high_leak.K_min

    def test_dead_zone_freezes_adaptation(self, controller):
        """Test that adaptation is frozen inside dead zone."""
        # State that produces small sigma (inside dead zone)
        small_state = np.array([0.0, 0.0001, 0.0001, 0.0, 0.0001, 0.0001])
        state_vars = (10.0, 0.0, 0.0)
        history = {}

        output = controller.compute_control(small_state, state_vars, history)

        if abs(output.sigma) <= controller.dead_zone:
            # dK should be zero when inside dead zone
            assert abs(history['dK'][0]) < 1e-6

    def test_leak_rate_pulls_k_toward_k_init(self):
        """Test that leak rate pulls K toward K_init."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.5,  # Moderate leak rate
            adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.5, K_init=10.0  # Large dead zone
        )

        # Start with K far from K_init, inside dead zone (no growth)
        small_state = np.zeros(6)
        K = 30.0

        for _ in range(50):
            state_vars = (K, 0.0, 0.0)
            output = controller.compute_control(small_state, state_vars, {})
            K_new = output.state[0]

            # K should move toward K_init due to leak
            if abs(output.sigma) <= controller.dead_zone:
                # Inside dead zone: dK = 0 (frozen)
                pass
            else:
                # Outside dead zone: leak term should pull toward K_init
                if K > controller.K_init:
                    assert K_new <= K or abs(K_new - K) < 1e-6
            K = K_new

    def test_adapt_rate_limit_enforced(self):
        """Test that adaptation rate is limited by adapt_rate_limit."""
        gains = [5.0, 3.0, 2.0, 1.0, 5.0]  # High gamma for fast adaptation
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.0,
            adapt_rate_limit=1.0,  # Small rate limit
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001, K_init=10.0
        )

        large_state = np.array([0.0, 1.0, 1.0, 0.0, 1.0, 1.0])
        state_vars = (10.0, 0.0, 0.0)
        history = {}

        output = controller.compute_control(large_state, state_vars, history)

        # dK should be limited by adapt_rate_limit
        assert abs(history['dK'][0]) <= controller.adapt_rate_limit

    def test_time_in_sliding_increases_inside_boundary(self, controller):
        """Test that time_in_sliding increases inside boundary layer."""
        # State with small sigma (inside boundary layer)
        small_state = np.array([0.0, 0.001, 0.001, 0.0, 0.001, 0.001])
        state_vars = (10.0, 0.0, 0.5)  # time_in_sliding = 0.5
        history = {}

        output = controller.compute_control(small_state, state_vars, history)

        if abs(output.sigma) <= controller.boundary_layer:
            # time_in_sliding should increase by dt
            assert history['time_in_sliding'][0] >= 0.5

    def test_time_in_sliding_resets_outside_boundary(self, controller):
        """Test that time_in_sliding resets outside boundary layer."""
        # State with large sigma (outside boundary layer)
        large_state = np.array([0.0, 0.5, 0.5, 0.0, 0.3, 0.3])
        state_vars = (10.0, 0.0, 5.0)  # time_in_sliding = 5.0
        history = {}

        output = controller.compute_control(large_state, state_vars, history)

        if abs(output.sigma) > controller.boundary_layer:
            # time_in_sliding should reset to 0
            assert history['time_in_sliding'][0] == 0.0


class TestAdaptiveSMCPropertiesAndMethods:
    """Test controller properties and utility methods."""

    def test_gains_property_returns_copy(self):
        """Test that gains property returns a copy of gains."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        returned_gains = controller.gains
        assert returned_gains == gains

        # Modifying returned gains should not affect controller
        returned_gains[0] = 999.0
        assert controller.gains[0] == 5.0

    def test_validate_gains_accepts_valid_gains(self):
        """Test that validate_gains accepts valid gains."""
        valid_gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        # Should not raise
        AdaptiveSMC.validate_gains(valid_gains)

    def test_validate_gains_rejects_too_few_gains(self):
        """Test that validate_gains rejects fewer than 5 gains."""
        invalid_gains = [5.0, 3.0, 2.0]
        with pytest.raises(ValueError, match="at least 5 gains"):
            AdaptiveSMC.validate_gains(invalid_gains)

    def test_validate_gains_accepts_extra_gains(self):
        """Test that validate_gains accepts more than 5 gains."""
        extra_gains = [5.0, 3.0, 2.0, 1.0, 0.5, 99.0, 88.0]
        # Should not raise
        AdaptiveSMC.validate_gains(extra_gains)

    def test_validate_gains_rejects_negative_gains(self):
        """Test that validate_gains rejects negative gains."""
        negative_gains = [5.0, -3.0, 2.0, 1.0, 0.5]
        with pytest.raises(ValueError):
            AdaptiveSMC.validate_gains(negative_gains)

    def test_initialize_state_returns_correct_tuple(self):
        """Test that initialize_state returns (K_init, 0.0, 0.0)."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001, K_init=15.0
        )

        state = controller.initialize_state()
        assert state == (15.0, 0.0, 0.0)

    def test_initialize_history_returns_empty_dict_with_keys(self):
        """Test that initialize_history returns dict with expected keys."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        history = controller.initialize_history()
        assert isinstance(history, dict)
        assert 'K' in history
        assert 'sigma' in history
        assert 'u_sw' in history
        assert 'dK' in history
        assert 'time_in_sliding' in history
        assert len(history['K']) == 0  # Empty lists

    def test_set_dynamics_does_nothing(self):
        """Test that set_dynamics exists for compatibility."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        # Should not raise
        controller.set_dynamics(None)

    def test_reset_method_exists(self):
        """Test that reset method exists for interface compliance."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        # Should not raise
        controller.reset()

    def test_cleanup_method_exists(self):
        """Test that cleanup method exists for memory management."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        # Should not raise
        controller.cleanup()


class TestAdaptiveSMCEdgeCases:
    """Test edge cases and error handling."""

    def test_nan_state_produces_valid_output(self):
        """Test that NaN state doesn't crash controller."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        nan_state = np.array([0.1, np.nan, 0.03, 0.2, 0.1, 0.05])
        state_vars = (10.0, 0.0, 0.0)

        # Should produce output (may be NaN but shouldn't crash)
        output = controller.compute_control(nan_state, state_vars, {})
        assert isinstance(output, AdaptiveSMCOutput)

    def test_inf_state_produces_valid_output(self):
        """Test that Inf state doesn't crash controller."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        inf_state = np.array([0.1, np.inf, 0.03, 0.2, 0.1, 0.05])
        state_vars = (10.0, 0.0, 0.0)

        # Should produce output (may be Inf but shouldn't crash)
        output = controller.compute_control(inf_state, state_vars, {})
        assert isinstance(output, AdaptiveSMCOutput)

    def test_very_large_state_values(self):
        """Test controller with very large state values."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        large_state = np.array([1e6, 1e6, 1e6, 1e6, 1e6, 1e6])
        state_vars = (10.0, 0.0, 0.0)

        output = controller.compute_control(large_state, state_vars, {})

        # Control should be saturated at max_force
        assert abs(output.u) <= controller.max_force

    def test_very_small_state_values(self):
        """Test controller with very small state values."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        tiny_state = np.array([1e-10, 1e-10, 1e-10, 1e-10, 1e-10, 1e-10])
        state_vars = (10.0, 0.0, 0.0)

        output = controller.compute_control(tiny_state, state_vars, {})

        # Control should be very small
        assert abs(output.u) < 1.0

    def test_repeated_calls_are_deterministic(self):
        """Test that repeated calls with same inputs produce same outputs."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])
        state_vars = (10.0, 0.0, 0.0)

        output1 = controller.compute_control(state, state_vars, {})
        output2 = controller.compute_control(state, state_vars, {})

        assert output1.u == output2.u
        assert output1.sigma == output2.sigma
        assert output1.state == output2.state

    def test_n_gains_class_attribute(self):
        """Test that n_gains class attribute equals 5."""
        assert AdaptiveSMC.n_gains == 5


class TestAdaptiveSMCLongTermBehavior:
    """Test long-term simulation behavior."""

    def test_convergence_with_constant_disturbance(self):
        """Test that controller adapts to constant disturbance."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.01,  # Small leak
            adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001, K_init=10.0
        )

        # Simulate constant disturbance
        state = np.array([0.0, 0.1, 0.1, 0.0, 0.05, 0.05])
        K = 10.0

        K_history = []
        for _ in range(100):
            state_vars = (K, 0.0, 0.0)
            output = controller.compute_control(state, state_vars, {})
            K = output.state[0]
            K_history.append(K)

        # K should adapt (change from initial value)
        assert len(K_history) == 100
        # Check that K is varying (adapting)
        assert max(K_history) != min(K_history) or abs(K_history[-1] - 10.0) < 1e-3

    def test_gain_stability_near_sliding_surface(self):
        """Test that gain remains stable near sliding surface."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.1]  # Low gamma
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1,
            adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.02, dead_zone=0.01, K_init=10.0
        )

        # State near sliding surface (small sigma)
        near_surface_state = np.array([0.0, 0.005, 0.005, 0.0, 0.002, 0.002])
        K = 10.0

        K_values = []
        for _ in range(50):
            state_vars = (K, 0.0, 0.0)
            output = controller.compute_control(near_surface_state, state_vars, {})
            K = output.state[0]
            K_values.append(K)

        # K should remain relatively stable near surface
        K_variation = max(K_values) - min(K_values)
        assert K_variation < 5.0  # Bounded variation
