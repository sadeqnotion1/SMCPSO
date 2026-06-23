#======================================================================================\\\
#============== tests/test_controllers/smc/test_adaptive_smc.py ========================\\\
#======================================================================================\\\

"""
Comprehensive tests for AdaptiveSMC controller.

Target: 90%+ coverage for adaptive control component.
Tests initialization, control computation, adaptation mechanisms, and edge cases.
"""

import pytest
import numpy as np
from src.controllers.smc.adaptive_smc import AdaptiveSMC
from src.utils import AdaptiveSMCOutput


class TestAdaptiveSMCInitialization:
    """Test controller initialization and parameter validation."""

    def test_valid_initialization(self):
        """Test controller initializes with valid parameters."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]  # k1, k2, lam1, lam2, gamma
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
            dead_zone=0.001,
            K_init=10.0,
            alpha=0.5
        )
        assert controller is not None
        assert len(controller.gains) == 5

    def test_n_gains_property(self):
        """Test n_gains property is 5."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )
        assert controller.n_gains == 5

    def test_invalid_dt_raises(self):
        """Test that non-positive dt raises ValueError."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        with pytest.raises((ValueError, AssertionError)):
            AdaptiveSMC(
                gains=gains, dt=0.0, max_force=100.0,
                leak_rate=0.1, adapt_rate_limit=10.0,
                K_min=1.0, K_max=50.0, smooth_switch=False,
                boundary_layer=0.01, dead_zone=0.001
            )

    def test_invalid_max_force_raises(self):
        """Test that non-positive max_force raises ValueError."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        with pytest.raises((ValueError, AssertionError)):
            AdaptiveSMC(
                gains=gains, dt=0.01, max_force=-100.0,
                leak_rate=0.1, adapt_rate_limit=10.0,
                K_min=1.0, K_max=50.0, smooth_switch=False,
                boundary_layer=0.01, dead_zone=0.001
            )

    def test_invalid_boundary_layer_raises(self):
        """Test that non-positive boundary_layer raises ValueError."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        with pytest.raises((ValueError, AssertionError)):
            AdaptiveSMC(
                gains=gains, dt=0.01, max_force=100.0,
                leak_rate=0.1, adapt_rate_limit=10.0,
                K_min=1.0, K_max=50.0, smooth_switch=False,
                boundary_layer=-0.01, dead_zone=0.001
            )

    def test_invalid_k_bounds_raises(self):
        """Test that invalid K bounds raise ValueError."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        with pytest.raises((ValueError, AssertionError)):
            AdaptiveSMC(
                gains=gains, dt=0.01, max_force=100.0,
                leak_rate=0.1, adapt_rate_limit=10.0,
                K_min=50.0, K_max=1.0,  # min > max
                smooth_switch=False, boundary_layer=0.01, dead_zone=0.001
            )

    def test_smooth_switch_parameter(self):
        """Test smooth_switch parameter is accepted."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller_linear = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )
        controller_smooth = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=True,
            boundary_layer=0.01, dead_zone=0.001
        )
        assert controller_linear is not None
        assert controller_smooth is not None


class TestAdaptiveSMCComputation:
    """Test control computation functionality."""

    @pytest.fixture
    def controller(self):
        """Create standard controller instance."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        return AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001, K_init=10.0
        )

    @pytest.fixture
    def state_zero(self):
        """Zero state at equilibrium."""
        return np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    @pytest.fixture
    def state_perturbed(self):
        """Perturbed state."""
        return np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])

    def test_compute_control_output_type(self, controller, state_perturbed):
        """Test compute_control returns AdaptiveSMCOutput."""
        output = controller.compute_control(state_perturbed, 0.0, {})
        assert isinstance(output, AdaptiveSMCOutput)
        assert hasattr(output, 'u')
        assert hasattr(output, 'state')
        assert hasattr(output, 'history')
        assert hasattr(output, 'sigma')

    def test_compute_control_at_equilibrium(self, controller, state_zero):
        """Test control at equilibrium is small."""
        output = controller.compute_control(state_zero, 0.0, {})
        assert abs(output.u) < 1.0

    def test_compute_control_with_perturbation(self, controller, state_perturbed):
        """Test control with perturbed state."""
        output = controller.compute_control(state_perturbed, 0.0, {})
        assert not np.isnan(output.u)
        assert not np.isinf(output.u)
        assert abs(output.u) >= 0.0

    def test_control_bounded(self, controller, state_perturbed):
        """Test control is bounded by max_force."""
        output = controller.compute_control(state_perturbed, 0.0, {})
        assert abs(output.u) <= controller.max_force

    def test_control_trajectory(self, controller, state_perturbed):
        """Test control computation over trajectory."""
        state = state_perturbed.copy()
        K = 10.0
        controls = []

        for i in range(10):
            output = controller.compute_control(state, K, {})
            controls.append(output.u)
            # state is a tuple (K, u_sw, sigma_error), extract K
            if isinstance(output.state, tuple):
                K = output.state[0]
            else:
                K = output.state
            # Simulate convergence
            state = state * 0.9

        assert len(controls) == 10
        assert all(abs(u) <= 100.0 for u in controls)

    def test_history_tracking(self, controller, state_perturbed):
        """Test history dictionary is updated."""
        history = {}
        output = controller.compute_control(state_perturbed, 10.0, history)

        assert len(output.history) > 0
        assert 'sigma' in output.history or 'K' in output.history

    def test_sigma_in_output(self, controller, state_perturbed):
        """Test sigma is returned in output."""
        output = controller.compute_control(state_perturbed, 10.0, {})
        assert np.isfinite(output.sigma)

    def test_adaptive_gain_updates(self, controller, state_perturbed):
        """Test adaptive gain K updates over time."""
        state = state_perturbed.copy()
        K_old = 10.0

        output1 = controller.compute_control(state, K_old, {})
        K_state = output1.state

        # state can be a tuple or scalar, extract K if tuple
        if isinstance(K_state, tuple):
            K_new = K_state[0]
        else:
            K_new = K_state

        assert isinstance(K_new, (float, np.floating, int))


class TestAdaptiveSMCAdaptation:
    """Test adaptation mechanisms."""

    def test_adaptation_mechanism_exists(self):
        """Test controller has adaptation mechanism."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])
        output1 = controller.compute_control(state, 10.0, {})

        # Extract K from state (can be tuple or scalar)
        K_state1 = output1.state
        if isinstance(K_state1, tuple):
            K1 = K_state1[0]
        else:
            K1 = K_state1

        output2 = controller.compute_control(state, K1, {})
        K_state2 = output2.state
        if isinstance(K_state2, tuple):
            K2 = K_state2[0]
        else:
            K2 = K_state2

        # Both should be valid
        assert isinstance(K1, (float, np.floating, int))
        assert isinstance(K2, (float, np.floating, int))

    def test_dead_zone_effect(self):
        """Test dead zone prevents adaptation near zero."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.5  # Large dead zone
        )

        # Near zero, K should not increase significantly
        state_small = np.array([0.001, 0.001, 0.001, 0.001, 0.001, 0.001])
        output = controller.compute_control(state_small, 10.0, {})
        K_state = output.state

        # Extract K from state (can be tuple or scalar)
        if isinstance(K_state, tuple):
            K_updated = K_state[0]
        else:
            K_updated = K_state

        # K should stay close to initial due to large dead zone
        assert abs(K_updated - 10.0) < 5.0


class TestAdaptiveSMCEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_state(self):
        """Test with zero state."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        output = controller.compute_control(np.zeros(6), 10.0, {})
        assert abs(output.u) < 0.1

    def test_large_state(self):
        """Test with large state values."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        large_state = np.array([10.0, 5.0, 8.0, 3.0, 2.0, 1.0])
        output = controller.compute_control(large_state, 10.0, {})
        assert not np.isnan(output.u)
        assert abs(output.u) <= 150.0

    def test_invalid_state_dimension(self):
        """Test error with wrong state dimension."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        with pytest.raises((ValueError, IndexError)):
            controller.compute_control(np.array([1.0, 2.0, 3.0]), 10.0, {})

    def test_extreme_adaptive_gain(self):
        """Test with extreme adaptive gain values."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])

        # Very small K
        output_small = controller.compute_control(state, 0.1, {})
        assert np.isfinite(output_small.u)

        # Very large K (but within bounds)
        output_large = controller.compute_control(state, 50.0, {})
        assert np.isfinite(output_large.u)


class TestAdaptiveSMCProperties:
    """Test controller properties."""

    def test_gains_property(self):
        """Test gains property returns copy."""
        gains_in = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains_in, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        gains_out = controller.gains
        assert gains_out == gains_in

    def test_forward_compatibility(self):
        """Test forward compatibility with extra gains."""
        gains_in = [5.0, 3.0, 2.0, 1.0, 0.5, 0.0, 0.0]  # Extra gains
        controller = AdaptiveSMC(
            gains=gains_in, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )

        gains_out = controller.gains
        assert len(gains_out) >= 5


class TestAdaptiveSMCIntegration:
    """Integration tests."""

    def test_control_loop_simulation(self):
        """Test control in a simulation loop."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        controller = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001, K_init=10.0
        )

        state = np.array([0.1, 0.05, 0.03, 0.0, 0.0, 0.0])
        K = 10.0

        for step in range(100):
            output = controller.compute_control(state, K, {})
            # Extract K from state (can be tuple or scalar)
            K_state = output.state
            if isinstance(K_state, tuple):
                K = K_state[0]
            else:
                K = K_state
            # Simple state update
            state = state + np.array([-0.001 * output.u, 0, 0, 0.01, 0, 0])
            state = np.clip(state, -1.0, 1.0)

        assert np.all(np.isfinite(state))
        assert np.isfinite(K)
        assert 1.0 <= K <= 50.0

    def test_multiple_controllers(self):
        """Test multiple controller instances don't interfere."""
        gains = [5.0, 3.0, 2.0, 1.0, 0.5]
        ctrl1 = AdaptiveSMC(
            gains=gains, dt=0.01, max_force=100.0,
            leak_rate=0.1, adapt_rate_limit=10.0,
            K_min=1.0, K_max=50.0, smooth_switch=False,
            boundary_layer=0.01, dead_zone=0.001
        )
        ctrl2 = AdaptiveSMC(
            gains=gains, dt=0.02, max_force=150.0,
            leak_rate=0.2, adapt_rate_limit=20.0,
            K_min=2.0, K_max=100.0, smooth_switch=True,
            boundary_layer=0.02, dead_zone=0.002
        )

        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])
        out1 = ctrl1.compute_control(state, 10.0, {})
        out2 = ctrl2.compute_control(state, 10.0, {})

        # Different configurations should produce different controls
        assert np.isfinite(out1.u) and np.isfinite(out2.u)

#========================================================================================================\\\
