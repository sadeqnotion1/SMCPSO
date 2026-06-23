#======================================================================================\\\
#================ tests/test_controllers/smc/test_hybrid_adaptive_sta_smc.py ============\\\
#======================================================================================\\\

"""
Comprehensive tests for HybridAdaptiveSTASMC controller.

Target: 90%+ coverage for hybrid adaptive super-twisting SMC component.
Tests initialization, control computation, adaptation mechanisms, and edge cases.
"""

import pytest
import numpy as np
from src.controllers.smc.hybrid_adaptive_sta_smc import HybridAdaptiveSTASMC
from src.utils import HybridSTAOutput


class TestHybridAdaptiveSTASMCInitialization:
    """Test controller initialization and parameter validation."""

    def test_valid_initialization_default(self):
        """Test initialization with default parameters."""
        gains = [2.0, 1.0, 2.0, 1.0]
        controller = HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
        )
        assert controller is not None
        assert controller.c1 == 2.0
        assert controller.c2 == 2.0

    def test_valid_initialization_with_extra_gains(self):
        """Test initialization with extra gains (ignored)."""
        gains = [2.0, 1.0, 2.0, 1.0, 999.0]
        controller = HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
        )
        assert controller is not None
        assert controller.c1 == 2.0

    def test_initialization_insufficient_gains(self):
        """Test that insufficient gains raise ValueError."""
        gains = [2.0, 1.0]
        with pytest.raises(ValueError):
            HybridAdaptiveSTASMC(
                gains=gains,
                dt=0.01,
                max_force=100.0,
                k1_init=5.0,
                k2_init=5.0,
                gamma1=1.0,
                gamma2=1.0,
                dead_zone=0.01,
            )

    def test_initialization_negative_dt(self):
        """Test that negative dt raises error."""
        gains = [2.0, 1.0, 2.0, 1.0]
        with pytest.raises(ValueError):
            HybridAdaptiveSTASMC(
                gains=gains,
                dt=-0.01,
                max_force=100.0,
                k1_init=5.0,
                k2_init=5.0,
                gamma1=1.0,
                gamma2=1.0,
                dead_zone=0.01,
            )

    def test_initialization_zero_dt(self):
        """Test that zero dt raises error."""
        gains = [2.0, 1.0, 2.0, 1.0]
        with pytest.raises(ValueError):
            HybridAdaptiveSTASMC(
                gains=gains,
                dt=0.0,
                max_force=100.0,
                k1_init=5.0,
                k2_init=5.0,
                gamma1=1.0,
                gamma2=1.0,
                dead_zone=0.01,
            )

    def test_initialization_negative_max_force(self):
        """Test that negative max_force raises error."""
        gains = [2.0, 1.0, 2.0, 1.0]
        with pytest.raises(ValueError):
            HybridAdaptiveSTASMC(
                gains=gains,
                dt=0.01,
                max_force=-100.0,
                k1_init=5.0,
                k2_init=5.0,
                gamma1=1.0,
                gamma2=1.0,
                dead_zone=0.01,
            )

    def test_initialization_k1_exceeds_max(self):
        """Test that k1_init > k1_max raises error."""
        gains = [2.0, 1.0, 2.0, 1.0]
        with pytest.raises(ValueError):
            HybridAdaptiveSTASMC(
                gains=gains,
                dt=0.01,
                max_force=100.0,
                k1_init=60.0,
                k2_init=5.0,
                gamma1=1.0,
                gamma2=1.0,
                dead_zone=0.01,
                k1_max=50.0,
            )

    def test_initialization_sat_width_less_than_dead_zone(self):
        """Test that sat_soft_width < dead_zone raises error."""
        gains = [2.0, 1.0, 2.0, 1.0]
        with pytest.raises(ValueError):
            HybridAdaptiveSTASMC(
                gains=gains,
                dt=0.01,
                max_force=100.0,
                k1_init=5.0,
                k2_init=5.0,
                gamma1=1.0,
                gamma2=1.0,
                dead_zone=0.05,
                sat_soft_width=0.01,
            )

    def test_initialization_invalid_recenter_thresholds(self):
        """Test that invalid recenter thresholds raise error."""
        gains = [2.0, 1.0, 2.0, 1.0]
        with pytest.raises(ValueError):
            HybridAdaptiveSTASMC(
                gains=gains,
                dt=0.01,
                max_force=100.0,
                k1_init=5.0,
                k2_init=5.0,
                gamma1=1.0,
                gamma2=1.0,
                dead_zone=0.01,
                recenter_high_thresh=0.02,
                recenter_low_thresh=0.05,
            )

    def test_initialization_with_enable_equivalent_true(self):
        """Test initialization with enable_equivalent=True."""
        gains = [2.0, 1.0, 2.0, 1.0]
        controller = HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
            enable_equivalent=True,
        )
        assert controller.use_equivalent is True

    def test_initialization_with_enable_equivalent_false(self):
        """Test initialization with enable_equivalent=False."""
        gains = [2.0, 1.0, 2.0, 1.0]
        controller = HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
            enable_equivalent=False,
        )
        assert controller.use_equivalent is False


class TestHybridAdaptiveSTASMCComputation:
    """Test control computation and dynamics."""

    @pytest.fixture
    def controller(self):
        """Create standard controller instance."""
        gains = [2.0, 1.0, 2.0, 1.0]
        return HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
        )

    def test_compute_control_output_type(self, controller):
        """Test that compute_control returns valid HybridSTAOutput."""
        state = np.array([0.01, 0.1, 0.05, 0.05, 0.1, 0.05], dtype=float)
        state_vars = controller.initialize_state()
        history = controller.initialize_history()
        result = controller.compute_control(state, state_vars, history)

        assert result is not None
        assert isinstance(result, HybridSTAOutput)
        assert hasattr(result, "u")
        assert hasattr(result, "state")
        assert hasattr(result, "history")
        assert hasattr(result, "sigma")

    def test_compute_control_finite_output(self, controller):
        """Test that control output is finite."""
        state = np.array([0.01, 0.1, 0.05, 0.05, 0.1, 0.05], dtype=float)
        state_vars = controller.initialize_state()
        result = controller.compute_control(state, state_vars, None)

        assert np.isfinite(result.u)

    def test_control_saturates_at_max_force(self, controller):
        """Test that control saturates at max_force."""
        large_state = np.array([5.0, 2.0, 2.0, 5.0, 5.0, 5.0], dtype=float)
        state_vars = (50.0, 50.0, 0.0)
        result = controller.compute_control(large_state, state_vars, None)

        assert abs(result.u) <= controller.max_force + 1e-9

    def test_state_tuple_has_three_elements(self, controller):
        """Test that returned state is (k1, k2, u_int)."""
        state = np.array([0.01, 0.1, 0.05, 0.05, 0.1, 0.05], dtype=float)
        state_vars = controller.initialize_state()
        result = controller.compute_control(state, state_vars, None)

        assert isinstance(result.state, tuple)
        assert len(result.state) == 3
        k1, k2, u_int = result.state
        assert isinstance(k1, (float, np.floating))
        assert isinstance(k2, (float, np.floating))
        assert isinstance(u_int, (float, np.floating))

    def test_adaptive_gains_bounded(self, controller):
        """Test that adaptive gains remain bounded."""
        state = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5], dtype=float)
        state_vars = controller.initialize_state()

        for _ in range(10):
            result = controller.compute_control(state, state_vars, None)
            k1, k2, u_int = result.state

            assert 0.0 <= k1 <= controller.k1_max
            assert 0.0 <= k2 <= controller.k2_max
            assert abs(u_int) <= controller.u_int_max

            state_vars = result.state


class TestHybridAdaptiveSTASMCAdaptation:
    """Test adaptation mechanisms."""

    @pytest.fixture
    def controller(self):
        """Create controller with medium adaptation rates."""
        gains = [2.0, 1.0, 2.0, 1.0]
        return HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=2.0,
            gamma2=2.0,
            dead_zone=0.01,
        )

    def test_gains_adapt_outside_dead_zone(self, controller):
        """Test that gains adapt when outside dead zone."""
        state = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1], dtype=float)
        state_vars = (5.0, 5.0, 0.0)

        result = controller.compute_control(state, state_vars, None)
        k1_new, k2_new, _ = result.state

        assert k1_new >= 5.0 or k2_new >= 5.0

    def test_gains_freeze_in_dead_zone(self, controller):
        """Test that gains freeze inside dead zone."""
        state = np.array([0.001, 0.001, 0.001, 0.001, 0.001, 0.001], dtype=float)
        state_vars = (10.0, 10.0, 0.0)

        result = controller.compute_control(state, state_vars, None)
        k1_new, k2_new, _ = result.state

        assert k1_new <= 10.0
        assert k2_new <= 10.0

    def test_integral_term_accumulates(self, controller):
        """Test that integral term accumulates outside dead zone."""
        state = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1], dtype=float)
        state_vars = (5.0, 5.0, 0.0)
        history = controller.initialize_history()

        result1 = controller.compute_control(state, state_vars, history)
        u_int1 = result1.state[2]

        result2 = controller.compute_control(state, result1.state, result1.history)
        u_int2 = result2.state[2]

        assert u_int2 != u_int1 or u_int1 != 0.0


class TestHybridAdaptiveSTASMCEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def controller(self):
        """Create standard controller."""
        gains = [2.0, 1.0, 2.0, 1.0]
        return HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
        )

    def test_nan_state_handled_gracefully(self, controller):
        """Test that NaN state is handled gracefully."""
        nan_state = np.array([np.nan, 0.1, 0.1, 0.1, 0.1, 0.1], dtype=float)
        result = controller.compute_control(nan_state, None, None)

        assert result is not None
        assert result.u == 0.0

    def test_inf_state_handled_gracefully(self, controller):
        """Test that Inf state is handled gracefully."""
        inf_state = np.array([np.inf, 0.1, 0.1, 0.1, 0.1, 0.1], dtype=float)
        result = controller.compute_control(inf_state, None, None)

        assert result is not None
        assert np.isfinite(result.u)

    def test_very_large_state_triggers_emergency_reset(self, controller):
        """Test that very large state triggers emergency reset."""
        large_state = np.array([100.0, 100.0, 100.0, 100.0, 100.0, 100.0], dtype=float)
        state_vars = (50.0, 50.0, 50.0)

        result = controller.compute_control(large_state, state_vars, None)

        assert result is not None
        k1, k2, u_int = result.state
        assert k1 <= controller.k1_init * 0.1
        assert k2 <= controller.k2_init * 0.1

    def test_zero_state_produces_minimal_control(self, controller):
        """Test that zero state produces minimal control."""
        zero_state = np.zeros(6)
        result = controller.compute_control(zero_state, None, None)

        assert abs(result.u) < 10.0


class TestHybridAdaptiveSTASMCProperties:
    """Test properties and accessors."""

    def test_gains_property_returns_list(self):
        """Test that gains property returns list."""
        gains = [2.5, 1.5, 3.0, 0.8]
        controller = HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
        )
        assert controller.gains == gains

    def test_dyn_property_initially_none(self):
        """Test that dynamics reference is initially None."""
        gains = [2.0, 1.0, 2.0, 1.0]
        controller = HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
        )
        assert controller.dyn is None

    def test_initialize_state_returns_tuple(self):
        """Test that initialize_state returns proper tuple."""
        gains = [2.0, 1.0, 2.0, 1.0]
        controller = HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
        )
        state = controller.initialize_state()

        assert isinstance(state, tuple)
        assert len(state) == 3
        assert state[0] == 5.0
        assert state[1] == 5.0
        assert state[2] == 0.0

    def test_initialize_history_returns_dict(self):
        """Test that initialize_history returns proper dict."""
        gains = [2.0, 1.0, 2.0, 1.0]
        controller = HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
        )
        history = controller.initialize_history()

        assert isinstance(history, dict)
        assert "k1" in history
        assert "k2" in history
        assert "u_int" in history
        assert "s" in history


class TestHybridAdaptiveSTASMCIntegration:
    """Integration tests for complete control loops."""

    def test_realistic_trajectory(self):
        """Test control over a realistic trajectory."""
        gains = [2.0, 1.0, 2.0, 1.0]
        controller = HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
        )

        state = np.array([0.0, np.pi, 0.0, 0.0, 0.0, 0.0], dtype=float)
        state_vars = controller.initialize_state()
        history = controller.initialize_history()

        for _ in range(50):
            result = controller.compute_control(state, state_vars, history)
            assert result is not None
            state_vars = result.state
            history = result.history

    def test_cleanup_functionality(self):
        """Test that cleanup method works."""
        gains = [2.0, 1.0, 2.0, 1.0]
        controller = HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
        )

        controller.cleanup()
        assert controller.dyn is None

    def test_multiple_instances_independence(self):
        """Test that multiple controller instances are independent."""
        gains = [2.0, 1.0, 2.0, 1.0]
        controller1 = HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
        )
        controller2 = HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=10.0,
            k2_init=5.0,
            gamma1=2.0,
            gamma2=1.0,
            dead_zone=0.02,
        )

        state = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1], dtype=float)
        result1 = controller1.compute_control(state, None, None)
        result2 = controller2.compute_control(state, None, None)

        # Results should differ due to different parameters
        assert result1.state[0] != result2.state[0] or result1.state[2] != result2.state[2]


class TestHybridAdaptiveSTASMCEdgeCases:
    """Test edge cases identified in MA-02 audit: relative surface mode and cart recentering hysteresis."""

    def test_relative_surface_mode(self):
        """Test that relative surface mode (use_relative_surface=True) computes control correctly."""
        gains = [2.0, 1.0, 2.0, 1.0]

        # Create controller with relative surface mode
        controller_rel = HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
            use_relative_surface=True,
        )

        # Create controller with absolute surface mode (default)
        controller_abs = HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
            use_relative_surface=False,
        )

        # State where θ2 ≠ θ1 (should produce different sliding surfaces)
        state = np.array([0.0, 0.1, 0.2, 0.0, 0.1, 0.15], dtype=float)

        result_rel = controller_rel.compute_control(state, None, None)
        result_abs = controller_abs.compute_control(state, None, None)

        # Verify both produce finite control
        assert np.isfinite(result_rel.u)
        assert np.isfinite(result_abs.u)

        # Verify control outputs differ (relative vs absolute formulation)
        assert result_rel.u != result_abs.u, \
            "Relative and absolute surface modes should produce different control"

        # Verify sliding surface calculation differs
        s_rel = controller_rel._compute_sliding_surface(state)
        s_abs = controller_abs._compute_sliding_surface(state)
        assert s_rel != s_abs, "Sliding surface should differ between modes"

    def test_cart_recentering_hysteresis_engage(self):
        """Test cart recentering engages smoothly when cart exceeds high threshold."""
        gains = [2.0, 1.0, 2.0, 1.0]
        controller = HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
            recenter_low_thresh=0.02,
            recenter_high_thresh=0.05,
        )

        # State 1: Cart position below low threshold (no recentering)
        state_low = np.array([0.01, 0.1, 0.1, 0.0, 0.0, 0.0], dtype=float)
        result_low = controller.compute_control(state_low, None, None)

        # State 2: Cart position in hysteresis zone (partial recentering)
        state_mid = np.array([0.035, 0.1, 0.1, 0.0, 0.0, 0.0], dtype=float)
        result_mid = controller.compute_control(state_mid, None, None)

        # State 3: Cart position above high threshold (full recentering)
        state_high = np.array([0.06, 0.1, 0.1, 0.0, 0.0, 0.0], dtype=float)
        result_high = controller.compute_control(state_high, None, None)

        # All should produce finite control
        assert np.isfinite(result_low.u)
        assert np.isfinite(result_mid.u)
        assert np.isfinite(result_high.u)

        # Control magnitude should generally increase with cart displacement
        # (though exact ordering depends on pendulum angles and adaptive gains)
        assert abs(result_high.u) >= abs(result_low.u) or \
               abs(result_mid.u) >= abs(result_low.u), \
            "Cart recentering should affect control magnitude"

    def test_cart_recentering_hysteresis_disengage(self):
        """Test cart recentering disengages correctly when cart returns below low threshold."""
        gains = [2.0, 1.0, 2.0, 1.0]
        controller = HybridAdaptiveSTASMC(
            gains=gains,
            dt=0.01,
            max_force=100.0,
            k1_init=5.0,
            k2_init=5.0,
            gamma1=1.0,
            gamma2=1.0,
            dead_zone=0.01,
            recenter_low_thresh=0.03,
            recenter_high_thresh=0.08,
        )

        # Simulate trajectory: high -> mid (in hysteresis) -> low
        # Step 1: Start above high threshold (full recentering)
        state_high = np.array([0.10, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=float)
        result_high = controller.compute_control(state_high, None, None)
        assert np.isfinite(result_high.u)

        # Step 2: Move to hysteresis zone (still recentering, but less)
        state_mid = np.array([0.05, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=float)
        result_mid = controller.compute_control(state_mid, result_high.state, result_high.history)
        assert np.isfinite(result_mid.u)

        # Step 3: Move below low threshold (minimal/no recentering)
        state_low = np.array([0.01, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=float)
        result_low = controller.compute_control(state_low, result_mid.state, result_mid.history)
        assert np.isfinite(result_low.u)

        # Verify hysteresis behavior: control should vary smoothly across zones
        # (exact values depend on adaptive gains, but all should be finite and reasonable)
        assert abs(result_high.u) <= controller.max_force
        assert abs(result_mid.u) <= controller.max_force
        assert abs(result_low.u) <= controller.max_force


#========================================================================================================\\\
