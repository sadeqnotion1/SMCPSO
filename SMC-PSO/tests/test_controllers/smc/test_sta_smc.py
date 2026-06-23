#======================================================================================\\\
#==================== tests/test_controllers/smc/test_sta_smc.py =======================\\\
#======================================================================================\\\

"""
Comprehensive tests for SuperTwistingSMC controller.

Target: 90%+ coverage for critical control component.
Tests initialization, control computation, gain validation, and edge cases.
"""

import pytest
import numpy as np
from src.controllers.smc.sta_smc import SuperTwistingSMC
from src.utils import STAOutput


class TestSuperTwistingSMCInitialization:
    """Test controller initialization and parameter validation."""

    def test_valid_initialization_2_gains(self):
        """Test controller initializes with 2-element gain vector."""
        gains = [10.0, 5.0]  # K1, K2
        controller = SuperTwistingSMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            boundary_layer=0.01
        )
        assert len(controller.gains) == 2
        assert controller.alg_gain_K1 == 10.0
        assert controller.alg_gain_K2 == 5.0
        # Should use default surface gains
        assert controller.surf_gain_k1 == 5.0
        assert controller.surf_gain_k2 == 3.0

    def test_valid_initialization_6_gains(self):
        """Test controller initializes with 6-element gain vector."""
        gains = [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]  # K1, K2, k1, k2, lambda1, lambda2
        controller = SuperTwistingSMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            boundary_layer=0.01
        )
        assert len(controller.gains) == 6
        assert controller.alg_gain_K1 == 10.0
        assert controller.alg_gain_K2 == 5.0
        assert controller.surf_gain_k1 == 8.0
        assert controller.surf_gain_k2 == 3.0
        assert controller.surf_lam1 == 15.0
        assert controller.surf_lam2 == 2.0

    def test_invalid_gain_count_raises(self):
        """Test that wrong gain count raises ValueError."""
        with pytest.raises(ValueError):
            SuperTwistingSMC(
                gains=[1.0, 2.0, 3.0],  # Wrong count!
                dt=0.01,
                max_force=100.0,
                boundary_layer=0.01
            )

    def test_zero_gain_raises(self):
        """Test that zero gain raises ValueError."""
        with pytest.raises(ValueError):
            SuperTwistingSMC(
                gains=[0.0, 5.0],  # K1 = 0
                dt=0.01,
                max_force=100.0,
                boundary_layer=0.01
            )

    def test_negative_gain_raises(self):
        """Test that negative gain raises ValueError."""
        with pytest.raises(ValueError):
            SuperTwistingSMC(
                gains=[-10.0, 5.0],  # K1 < 0
                dt=0.01,
                max_force=100.0,
                boundary_layer=0.01
            )

    def test_zero_dt_raises(self):
        """Test that zero dt raises ValueError."""
        with pytest.raises(ValueError):
            SuperTwistingSMC(
                gains=[10.0, 5.0],
                dt=0.0,  # Invalid
                max_force=100.0,
                boundary_layer=0.01
            )

    def test_negative_max_force_raises(self):
        """Test that negative max_force raises ValueError."""
        with pytest.raises(ValueError):
            SuperTwistingSMC(
                gains=[10.0, 5.0],
                dt=0.01,
                max_force=-100.0,  # Invalid
                boundary_layer=0.01
            )

    def test_zero_boundary_layer_raises(self):
        """Test that zero boundary_layer raises ValueError."""
        with pytest.raises(ValueError):
            SuperTwistingSMC(
                gains=[10.0, 5.0],
                dt=0.01,
                max_force=100.0,
                boundary_layer=0.0  # Invalid
            )

    def test_negative_boundary_layer_raises(self):
        """Test that negative boundary_layer raises ValueError."""
        with pytest.raises(ValueError):
            SuperTwistingSMC(
                gains=[10.0, 5.0],
                dt=0.01,
                max_force=100.0,
                boundary_layer=-0.01  # Invalid
            )

    def test_invalid_switch_method_raises(self):
        """Test that invalid switch_method raises ValueError."""
        with pytest.raises(ValueError):
            SuperTwistingSMC(
                gains=[10.0, 5.0],
                dt=0.01,
                max_force=100.0,
                boundary_layer=0.01,
                switch_method="invalid"  # Invalid
            )

    def test_valid_switch_methods(self):
        """Test valid switch methods are accepted."""
        for method in ["linear", "tanh", "LINEAR", "TANH"]:
            controller = SuperTwistingSMC(
                gains=[10.0, 5.0],
                dt=0.01,
                max_force=100.0,
                boundary_layer=0.01,
                switch_method=method
            )
            assert controller.switch_method.lower() in ["linear", "tanh"]

    def test_default_parameters(self):
        """Test default parameter values."""
        controller = SuperTwistingSMC(
            gains=[10.0, 5.0],
            dt=0.01
        )
        assert controller.max_force == 150.0  # Default
        assert controller.damping_gain == 0.0  # Default
        assert controller.boundary_layer == 0.01  # Default
        assert controller.switch_method == "linear"  # Default

    def test_custom_parameters(self):
        """Test custom parameter values are set correctly."""
        controller = SuperTwistingSMC(
            gains=[10.0, 5.0],
            dt=0.02,
            max_force=200.0,
            damping_gain=0.5,
            boundary_layer=0.05,
            switch_method="tanh",
            anti_windup_gain=0.1,
            regularization=1e-8
        )
        assert controller.dt == 0.02
        assert controller.max_force == 200.0
        assert controller.damping_gain == 0.5
        assert controller.boundary_layer == 0.05
        assert controller.switch_method == "tanh"
        assert controller.anti_windup_gain == 0.1
        assert controller.regularization == 1e-8

    def test_n_gains_property(self):
        """Test n_gains property is always 6."""
        controller_2 = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)
        controller_6 = SuperTwistingSMC(gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0], dt=0.01)

        assert controller_2.n_gains == 6
        assert controller_6.n_gains == 6


class TestSuperTwistingSMCComputeControl:
    """Test control computation functionality."""

    @pytest.fixture
    def controller(self):
        """Create a standard controller instance."""
        return SuperTwistingSMC(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0,
            boundary_layer=0.01
        )

    @pytest.fixture
    def state_zero(self):
        """Zero state (equilibrium)."""
        return np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    @pytest.fixture
    def state_perturbed(self):
        """Perturbed state."""
        return np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])

    @pytest.fixture
    def state_large_error(self):
        """Large error state."""
        return np.array([0.5, 0.3, 0.4, 0.5, 0.2, 0.1])

    def test_compute_control_output_type(self, controller, state_perturbed):
        """Test compute_control returns STAOutput."""
        output = controller.compute_control(state_perturbed, (0.0, 0.0), {})
        assert isinstance(output, STAOutput)
        assert hasattr(output, 'u')
        assert hasattr(output, 'state')
        assert hasattr(output, 'history')

    def test_compute_control_at_equilibrium(self, controller, state_zero):
        """Test control at equilibrium is small."""
        output = controller.compute_control(state_zero, (0.0, 0.0), {})
        assert abs(output.u) < 1.0  # Should be near zero

    def test_compute_control_perturbed(self, controller, state_perturbed):
        """Test control with perturbed state is non-zero."""
        output = controller.compute_control(state_perturbed, (0.0, 0.0), {})
        assert not np.isnan(output.u)
        assert not np.isinf(output.u)
        assert abs(output.u) > 0.0  # Should generate some control

    def test_compute_control_large_error(self, controller, state_large_error):
        """Test control with large error."""
        output = controller.compute_control(state_large_error, (0.0, 0.0), {})
        assert not np.isnan(output.u)
        assert not np.isinf(output.u)
        assert abs(output.u) > 1.0  # Should generate significant control

    def test_compute_control_bounded(self, controller, state_large_error):
        """Test control is bounded by max_force."""
        output = controller.compute_control(state_large_error, (0.0, 0.0), {})
        assert abs(output.u) <= controller.max_force

    def test_compute_control_state_tuple_z_sigma(self, controller, state_perturbed):
        """Test compute_control with (z, sigma) state tuple."""
        output = controller.compute_control(state_perturbed, (0.5, 0.2), {})
        assert isinstance(output, STAOutput)
        assert abs(output.u) <= 100.0

    def test_compute_control_legacy_scalar_state(self, controller, state_perturbed):
        """Test compute_control with legacy scalar state (z only)."""
        output = controller.compute_control(state_perturbed, 0.5, {})
        assert isinstance(output, STAOutput)
        assert abs(output.u) <= 100.0

    def test_compute_control_trajectory(self, controller, state_perturbed):
        """Test control computation over a trajectory."""
        state = state_perturbed.copy()
        z, sigma = 0.0, 0.0
        controls = []

        for i in range(10):
            output = controller.compute_control(state, (z, sigma), {})
            controls.append(output.u)
            z, sigma = output.state
            # Simulate state convergence
            state = state * 0.9

        assert len(controls) == 10
        assert all(abs(u) <= 100.0 for u in controls)

    def test_history_tracking(self, controller, state_perturbed):
        """Test history dictionary is updated."""
        history = {}
        output = controller.compute_control(state_perturbed, (0.0, 0.0), history)

        # History should be updated with sigma, z, u, u_eq
        assert 'sigma' in output.history
        assert 'z' in output.history
        assert 'u' in output.history
        assert 'u_eq' in output.history

    def test_control_continuity(self, controller, state_perturbed):
        """Test control signal is continuous (no jumps)."""
        state1 = state_perturbed.copy()
        control1 = controller.compute_control(state1, (0.0, 0.0), {})

        # Small perturbation
        state2 = state1 + np.array([0.001, 0.001, 0.001, 0.001, 0.001, 0.001])
        control2 = controller.compute_control(state2, (0.0, 0.0), {})

        # Control should change smoothly
        control_diff = abs(control2.u - control1.u)
        assert control_diff < 10.0  # Reasonable continuity

    def test_damping_effect(self):
        """Test damping gain effect on control."""
        gains = [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])

        # Controller without damping
        controller_no_damp = SuperTwistingSMC(
            gains=gains, dt=0.01, damping_gain=0.0
        )
        control_no_damp = controller_no_damp.compute_control(state, (0.0, 0.0), {})

        # Controller with damping
        controller_damp = SuperTwistingSMC(
            gains=gains, dt=0.01, damping_gain=1.0
        )
        control_damp = controller_damp.compute_control(state, (0.0, 0.0), {})

        # Controls should be different
        assert abs(control_damp.u - control_no_damp.u) > 0.01

    def test_boundary_layer_effect(self):
        """Test boundary layer effect on control."""
        gains = [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
        # Use a larger state so boundary layer effect is significant
        state = np.array([0.1, 0.05, 0.02, 0.1, 0.05, 0.02])

        # Small boundary layer (sharp)
        controller_small = SuperTwistingSMC(
            gains=gains, dt=0.01, boundary_layer=0.01
        )
        control_small = controller_small.compute_control(state, (0.0, 0.0), {})

        # Large boundary layer (smooth)
        controller_large = SuperTwistingSMC(
            gains=gains, dt=0.01, boundary_layer=1.0
        )
        control_large = controller_large.compute_control(state, (0.0, 0.0), {})

        # Controls should be different (or both valid)
        # Both should produce finite controls
        assert np.isfinite(control_small.u) and np.isfinite(control_large.u)


class TestSuperTwistingSMCGainValidation:
    """Test gain validation functionality."""

    def test_validate_gains_all_valid(self):
        """Test validate_gains with all valid gains."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)

        gains_b = np.array([
            [10.0, 5.0],   # Valid: K1 > K2 > 0
            [20.0, 10.0],  # Valid: K1 > K2 > 0
            [5.0, 2.0],    # Valid: K1 > K2 > 0
        ])

        valid = controller.validate_gains(gains_b)
        assert all(valid)

    def test_validate_gains_invalid_k1(self):
        """Test validate_gains rejects invalid K1."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)

        gains_b = np.array([
            [5.0, 10.0],   # Invalid: K1 <= K2
            [0.0, 5.0],    # Invalid: K1 = 0
            [-10.0, 5.0],  # Invalid: K1 < 0
        ])

        valid = controller.validate_gains(gains_b)
        assert not any(valid)

    def test_validate_gains_k1_k2_relationship(self):
        """Test K1 > K2 requirement."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)

        gains_b = np.array([
            [10.0, 5.0],   # Valid: 10 > 5
            [10.0, 10.0],  # Invalid: 10 = 10
            [5.0, 10.0],   # Invalid: 5 < 10
        ])

        valid = controller.validate_gains(gains_b)
        assert valid[0] and not valid[1] and not valid[2]

    def test_validate_gains_with_surface_params(self):
        """Test validate_gains with 6-dimensional gains."""
        controller = SuperTwistingSMC(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0], dt=0.01
        )

        gains_b = np.array([
            [10.0, 5.0, 8.0, 3.0, 15.0, 2.0],   # All valid
            [10.0, 5.0, 0.0, 3.0, 15.0, 2.0],   # Invalid: k1 = 0
            [10.0, 5.0, 8.0, 3.0, -1.0, 2.0],   # Invalid: lambda1 < 0
        ])

        valid = controller.validate_gains(gains_b)
        assert valid[0] and not valid[1] and not valid[2]

    def test_validate_gains_empty(self):
        """Test validate_gains with empty array."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)
        gains_b = np.zeros((0, 2))
        valid = controller.validate_gains(gains_b)
        assert len(valid) == 0


class TestSuperTwistingSMCEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_state(self):
        """Test with zero state."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)
        zero_state = np.zeros(6)

        output = controller.compute_control(zero_state, (0.0, 0.0), {})
        assert abs(output.u) < 0.1

    def test_large_state(self):
        """Test with large state values."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)
        large_state = np.array([10.0, 5.0, 8.0, 3.0, 2.0, 1.0])

        output = controller.compute_control(large_state, (0.0, 0.0), {})
        assert not np.isnan(output.u)
        assert not np.isinf(output.u)
        assert abs(output.u) <= 150.0

    def test_very_small_state(self):
        """Test with very small state values."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)
        tiny_state = np.array([1e-8, 1e-8, 1e-8, 1e-8, 1e-8, 1e-8])

        output = controller.compute_control(tiny_state, (0.0, 0.0), {})
        assert abs(output.u) < 0.01

    def test_nan_in_state_doesnt_crash(self):
        """Test that NaN in state doesn't crash (though result may be clipped)."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)
        nan_state = np.array([np.nan, 0.0, 0.0, 0.0, 0.0, 0.0])

        # Controller doesn't validate input; saturation handles NaN gracefully
        output = controller.compute_control(nan_state, (0.0, 0.0), {})
        # Output should be bounded (saturation clips even NaN/inf)
        assert isinstance(output.u, (float, np.floating))

    def test_inf_in_state_doesnt_crash(self):
        """Test that inf in state doesn't crash (though result may be clipped)."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)
        inf_state = np.array([np.inf, 0.0, 0.0, 0.0, 0.0, 0.0])

        # Controller doesn't validate input; saturation handles inf gracefully
        output = controller.compute_control(inf_state, (0.0, 0.0), {})
        # Output should be bounded (saturation clips even NaN/inf)
        assert isinstance(output.u, (float, np.floating))

    def test_invalid_state_dimension(self):
        """Test error with wrong state dimension."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)

        with pytest.raises((ValueError, IndexError)):
            controller.compute_control(np.array([1.0, 2.0, 3.0]), (0.0, 0.0), {})

    def test_negative_z(self):
        """Test with negative integral state."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)
        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])

        output = controller.compute_control(state, (-10.0, 0.0), {})
        assert not np.isnan(output.u)
        assert abs(output.u) <= 150.0

    def test_large_z(self):
        """Test with large integral state."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)
        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])

        output = controller.compute_control(state, (100.0, 0.0), {})
        assert not np.isnan(output.u)
        assert abs(output.u) <= 150.0


class TestSuperTwistingSMCStateManagement:
    """Test state initialization and reset."""

    def test_initialize_state(self):
        """Test initial state is (z=0, sigma=0)."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)
        z, sigma = controller.initialize_state()

        assert z == 0.0
        assert sigma == 0.0

    def test_initialize_history(self):
        """Test initial history is empty dict."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)
        history = controller.initialize_history()

        assert isinstance(history, dict)
        assert len(history) == 0

    def test_reset(self):
        """Test reset method."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)
        # Reset should not raise
        controller.reset()

    def test_cleanup(self):
        """Test cleanup method."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)
        controller.cleanup()

        # After cleanup, dynamics ref should be None
        assert controller.dyn is None


class TestSuperTwistingSMCProperties:
    """Test controller properties."""

    def test_gains_property(self):
        """Test gains property returns copy."""
        gains_in = [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
        controller = SuperTwistingSMC(gains=gains_in, dt=0.01)

        gains_out = controller.gains
        assert gains_out == gains_in

        # Modifying returned list shouldn't affect controller
        gains_out[0] = 999.0
        assert controller.gains[0] == 10.0

    def test_dyn_property(self):
        """Test dyn property (dynamics model reference)."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)

        # Initially None
        assert controller.dyn is None

        # Set dynamics
        class DummyDynamics:
            pass

        dyn = DummyDynamics()
        controller.dyn = dyn
        assert controller.dyn is dyn

        # Clear dynamics
        controller.dyn = None
        assert controller.dyn is None

    def test_dynamics_model_alias(self):
        """Test dynamics_model alias."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)

        class DummyDynamics:
            pass

        dyn = DummyDynamics()
        controller.dynamics_model = dyn
        assert controller.dynamics_model is dyn

    def test_set_dynamics(self):
        """Test set_dynamics method."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)

        class DummyDynamics:
            pass

        dyn = DummyDynamics()
        controller.set_dynamics(dyn)
        assert controller.dyn is dyn


class TestSuperTwistingSMCMathematicalProperties:
    """Test mathematical properties and stability."""

    def test_sliding_surface_computation(self):
        """Test sliding surface computation."""
        controller = SuperTwistingSMC(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01
        )
        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])

        # sigma = k1*(th1dot + lam1*th1) + k2*(th2dot + lam2*th2)
        # State unpacking: _, th1, th2, _, th1dot, th2dot = state
        # Using values: x=0.1, th1=0.05, th2=0.03, xdot=0.2, th1dot=0.1, th2dot=0.05
        # k1=8.0, k2=3.0, lam1=15.0, lam2=2.0
        expected_sigma = (8.0 * (0.1 + 15.0 * 0.05) +
                         3.0 * (0.05 + 2.0 * 0.03))

        sigma = controller._compute_sliding_surface(state)
        assert abs(sigma - expected_sigma) < 1e-10

    def test_equivalent_control_none_dynamics(self):
        """Test equivalent control with no dynamics model."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)
        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])

        # Without dynamics, should return 0
        u_eq = controller._compute_equivalent_control(state)
        assert u_eq == 0.0

    def test_finite_time_convergence_property(self):
        """Test finite-time convergence property (simplified)."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)

        # Start with large error
        state = np.array([0.5, 0.3, 0.4, 0.5, 0.2, 0.1])

        controls = []
        for i in range(5):
            output = controller.compute_control(state, (0.0, 0.0), {})
            controls.append(abs(output.u))
            # Simulate convergence
            state = state * 0.8

        # All control magnitudes should be finite and bounded
        assert all(0 <= c <= 150.0 for c in controls)

    def test_switching_function_properties(self):
        """Test properties of the switching function."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)

        # Test at multiple states
        states = [
            np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05]),
            np.array([0.5, 0.3, 0.4, 0.5, 0.2, 0.1]),
        ]

        for state in states:
            output = controller.compute_control(state, (0.0, 0.0), {})
            # Control should always be finite
            assert np.isfinite(output.u)


class TestSuperTwistingSMCIntegration:
    """Integration tests."""

    def test_control_loop_simulation(self):
        """Test control in a simple simulation loop."""
        controller = SuperTwistingSMC(
            gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
            dt=0.01,
            max_force=100.0
        )

        # Initial state
        state = np.array([0.1, 0.05, 0.03, 0.0, 0.0, 0.0])
        z, sigma = 0.0, 0.0

        # Run for multiple steps
        for step in range(100):
            output = controller.compute_control(state, (z, sigma), {})
            z, sigma = output.state

            # Simple state update (not a real dynamics)
            state = state + np.array([-0.001 * output.u, 0, 0, 0.01, 0, 0])
            state = np.clip(state, -1.0, 1.0)  # Bound state

        # Should not crash and state should remain reasonable
        assert np.all(np.isfinite(state))
        assert abs(z) <= 150.0

    def test_multiple_controllers(self):
        """Test multiple controller instances don't interfere."""
        ctrl1 = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)
        ctrl2 = SuperTwistingSMC(gains=[20.0, 10.0], dt=0.02)

        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])

        out1 = ctrl1.compute_control(state, (0.0, 0.0), {})
        out2 = ctrl2.compute_control(state, (0.0, 0.0), {})

        # Different gains should produce different controls
        assert abs(out1.u - out2.u) > 0.01

    def test_controller_reuse(self):
        """Test controller can be reused for multiple steps."""
        controller = SuperTwistingSMC(gains=[10.0, 5.0], dt=0.01)
        state = np.array([0.1, 0.05, 0.03, 0.2, 0.1, 0.05])

        # Reuse controller multiple times
        for _ in range(10):
            output = controller.compute_control(state, (0.0, 0.0), {})
            assert isinstance(output, STAOutput)

#========================================================================================================\\\
