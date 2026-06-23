#======================================================================================\\\
#========== tests/test_controllers/specialized/test_swing_up_smc_expanded.py ==========\\\
#======================================================================================\\\

"""
Expanded tests for SwingUpSMC energy-based controller.

This module provides comprehensive coverage of:
- Parameter validation and initialization
- Energy-based control law
- Mode switching logic and hysteresis
- Force saturation
- State and history management
- Edge cases and boundary conditions
"""

import pytest
import numpy as np
from unittest.mock import Mock

from src.controllers.specialized.swing_up_smc import SwingUpSMC


class SimpleDynamics:
    """Simple dynamics with configurable energy."""

    def __init__(self, energy_value=0.0):
        self.energy_value = energy_value

    def total_energy(self, state: np.ndarray) -> float:
        return self.energy_value


class SimpleStabilizer:
    """Simple stabilizer for testing mode handoff."""

    max_force = 15.0

    def initialize_state(self):
        return {"integral": 0.0}

    def initialize_history(self):
        return {"controls": []}

    def compute_control(self, state, svars, hist):
        # Simple proportional control on first angle
        control = -2.0 * state[1]
        hist["controls"].append(control)
        return control, svars, hist


# =====================================================================================
# Initialization and Parameter Validation
# =====================================================================================

class TestSwingUpSMCInitialization:
    """Test controller initialization and parameter validation."""

    def test_basic_initialization(self):
        """Test basic controller initialization with default parameters."""
        dyn = SimpleDynamics()
        stabilizer = SimpleStabilizer()

        ctrl = SwingUpSMC(
            dynamics_model=dyn,
            stabilizing_controller=stabilizer,
            energy_gain=10.0,
            dt=0.01,
            max_force=20.0
        )

        assert ctrl.dyn == dyn
        assert ctrl.stabilizer == stabilizer
        assert ctrl.energy_gain == 10.0
        assert ctrl.dt == 0.01
        assert ctrl.max_force == 20.0
        assert ctrl._mode == "swing"
        assert not ctrl._stabilizer_initialized

    def test_custom_parameters(self):
        """Test initialization with custom switching parameters."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=15.0,
            switch_energy_factor=0.6,
            exit_energy_factor=0.3,
            switch_angle_tolerance=0.4,
            reentry_angle_tolerance=0.5,
            dt=0.02,
            max_force=25.0
        )

        assert ctrl.switch_energy_factor == 0.6
        assert ctrl.exit_energy_factor == 0.3
        assert ctrl.switch_angle_tolerance == 0.4
        assert ctrl.reentry_angle_tolerance == 0.5

    def test_max_force_attribute(self):
        """Test that max_force attribute is accessible."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            dt=0.01,
            max_force=30.0
        )

        assert hasattr(ctrl, 'max_force')
        assert ctrl.max_force == 30.0


# =====================================================================================
# State and History Initialization
# =====================================================================================

class TestStateHistoryInitialization:
    """Test state and history initialization methods."""

    @pytest.fixture
    def controller(self):
        return SwingUpSMC(
            dynamics_model=SimpleDynamics(),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            dt=0.01,
            max_force=20.0
        )

    def test_initialize_state(self, controller):
        """Test state initialization."""
        state = controller.initialize_state()

        assert isinstance(state, dict)
        assert "integral" in state
        assert state["integral"] == 0.0

    def test_initialize_history(self, controller):
        """Test history initialization."""
        history = controller.initialize_history()

        assert isinstance(history, dict)
        assert "mode" in history
        assert history["mode"] == "swing"
        assert "t" in history
        assert history["t"] == 0.0


# =====================================================================================
# Energy-Based Control Law (Swing Mode)
# =====================================================================================

class TestSwingModeControl:
    """Test energy-based control law in swing mode."""

    def test_swing_mode_nonzero_control(self):
        """Test that swing mode produces non-zero control."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=1.0),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            dt=0.01,
            max_force=20.0
        )

        # Hanging state with velocity
        state = np.array([0.0, np.pi, np.pi, 0.0, 0.5, 0.0])
        u, _, _ = ctrl.compute_control(state, ctrl.initialize_state(), ctrl.initialize_history())

        assert u != 0.0
        assert isinstance(u, float)

    def test_energy_gain_scaling(self):
        """Test that energy gain scales the control output."""
        dyn = SimpleDynamics(energy_value=1.0)
        stabilizer = SimpleStabilizer()
        state = np.array([0.0, np.pi, np.pi, 0.0, 0.5, 0.0])

        # Low gain
        ctrl1 = SwingUpSMC(
            dynamics_model=dyn,
            stabilizing_controller=stabilizer,
            energy_gain=5.0,
            dt=0.01,
            max_force=100.0  # High limit to avoid saturation
        )
        u1, _, _ = ctrl1.compute_control(state, ctrl1.initialize_state(), ctrl1.initialize_history())

        # High gain
        ctrl2 = SwingUpSMC(
            dynamics_model=dyn,
            stabilizing_controller=stabilizer,
            energy_gain=15.0,
            dt=0.01,
            max_force=100.0
        )
        u2, _, _ = ctrl2.compute_control(state, ctrl2.initialize_state(), ctrl2.initialize_history())

        # Higher gain should produce larger control (in magnitude)
        assert abs(u2) > abs(u1)

    def test_swing_mode_force_saturation(self):
        """Test that swing mode respects max_force limits."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=10.0),  # High energy
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=100.0,  # High gain to trigger saturation
            dt=0.01,
            max_force=5.0  # Low limit
        )

        state = np.array([0.0, np.pi, np.pi, 0.0, 2.0, 0.0])
        u, _, _ = ctrl.compute_control(state, ctrl.initialize_state(), ctrl.initialize_history())

        # Should be saturated
        assert abs(u) <= ctrl.max_force

    def test_swing_mode_different_velocities(self):
        """Test swing mode control with different velocity directions."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=1.0),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            dt=0.01,
            max_force=20.0
        )

        # Positive velocity
        state_pos = np.array([0.0, np.pi, np.pi, 0.0, 1.0, 0.0])
        u_pos, _, _ = ctrl.compute_control(state_pos, ctrl.initialize_state(), ctrl.initialize_history())

        # Negative velocity
        state_neg = np.array([0.0, np.pi, np.pi, 0.0, -1.0, 0.0])
        u_neg, _, _ = ctrl.compute_control(state_neg, ctrl.initialize_state(), ctrl.initialize_history())

        # Controls should have opposite signs (energy-based control)
        assert np.sign(u_pos) != np.sign(u_neg)


# =====================================================================================
# Mode Switching Logic
# =====================================================================================

class TestModeSwitching:
    """Test mode switching between swing and stabilize."""

    def test_switch_to_stabilize_upright(self):
        """Test switch to stabilize mode when upright."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=0.5),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            switch_energy_factor=0.6,
            switch_angle_tolerance=0.3,
            dt=0.01,
            max_force=20.0
        )

        # Near-upright with sufficient energy
        state = np.array([0.0, 0.1, -0.1, 0.0, 0.0, 0.0])
        svars = ctrl.initialize_state()
        hist = ctrl.initialize_history()

        u, svars, hist = ctrl.compute_control(state, svars, hist)

        # Should switch to stabilize
        assert ctrl._mode == "stabilize"
        assert hist["mode"] == "stabilize"

    def test_stay_in_swing_mode_large_angles(self):
        """Test that controller stays in swing mode with large angles."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=1.0),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            switch_energy_factor=0.5,
            switch_angle_tolerance=0.2,
            dt=0.01,
            max_force=20.0
        )

        # Large angles (far from upright)
        state = np.array([0.0, 1.0, -1.0, 0.0, 0.0, 0.0])
        u, _, _ = ctrl.compute_control(state, ctrl.initialize_state(), ctrl.initialize_history())

        # Should stay in swing mode
        assert ctrl._mode == "swing"

    def test_reentry_to_swing_mode(self):
        """Test reentry to swing mode when angles become too large."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=0.2),  # Low energy
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            exit_energy_factor=0.3,
            reentry_angle_tolerance=0.4,
            dt=0.01,
            max_force=20.0
        )

        # Force into stabilize mode
        ctrl._mode = "stabilize"
        ctrl._stabilizer_initialized = True

        # Large angle deviation
        state = np.array([0.0, 0.5, -0.5, 0.0, 0.0, 0.0])
        svars = ctrl.initialize_state()
        hist = {"mode": "stabilize", "t": 0.0}

        u, svars, hist = ctrl.compute_control(state, svars, hist)

        # Should return to swing mode
        assert ctrl._mode == "swing"
        assert hist["mode"] == "swing"

    def test_hysteresis_behavior(self):
        """Test hysteresis prevents rapid mode switching."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=0.5),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            switch_energy_factor=0.6,
            exit_energy_factor=0.4,
            switch_angle_tolerance=0.3,
            reentry_angle_tolerance=0.35,
            dt=0.01,
            max_force=20.0
        )

        # State in the hysteresis zone
        state = np.array([0.0, 0.32, -0.32, 0.0, 0.0, 0.0])

        # Start in swing mode
        ctrl._mode = "swing"
        u1, _, _ = ctrl.compute_control(state, ctrl.initialize_state(), ctrl.initialize_history())
        mode1 = ctrl._mode

        # Switch to stabilize
        state_upright = np.array([0.0, 0.1, -0.1, 0.0, 0.0, 0.0])
        u2, _, _ = ctrl.compute_control(state_upright, ctrl.initialize_state(), ctrl.initialize_history())
        assert ctrl._mode == "stabilize"

        # Return to hysteresis zone - should stay in stabilize
        ctrl._stabilizer_initialized = True
        hist = {"mode": "stabilize", "t": 0.0}
        u3, _, _ = ctrl.compute_control(state, ctrl.initialize_state(), hist)

        # Due to hysteresis, should stay in stabilize
        # (reentry_angle_tolerance = 0.35 < angle = 0.32)
        assert ctrl._mode == "stabilize"


# =====================================================================================
# Stabilize Mode Delegation
# =====================================================================================

class TestStabilizeMode:
    """Test delegation to stabilizing controller."""

    def test_stabilizer_control_output(self):
        """Test that stabilizer control is used in stabilize mode."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=0.5),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            switch_energy_factor=0.6,
            switch_angle_tolerance=0.5,
            dt=0.01,
            max_force=20.0
        )

        # Force into stabilize mode
        state = np.array([0.0, 0.1, -0.1, 0.0, 0.0, 0.0])
        svars = ctrl.initialize_state()
        hist = ctrl.initialize_history()

        u, svars, hist = ctrl.compute_control(state, svars, hist)

        # Should be in stabilize mode
        assert ctrl._mode == "stabilize"

        # Control should come from stabilizer (proportional to angle)
        # SimpleStabilizer returns -2.0 * state[1]
        expected_control = -2.0 * state[1]
        np.testing.assert_almost_equal(u, expected_control)

    def test_stabilizer_initialization(self):
        """Test that stabilizer is initialized on first entry."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=0.5),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            switch_energy_factor=0.6,
            switch_angle_tolerance=0.5,
            dt=0.01,
            max_force=20.0
        )

        state = np.array([0.0, 0.1, -0.1, 0.0, 0.0, 0.0])
        svars = ctrl.initialize_state()
        hist = ctrl.initialize_history()

        # First call should initialize stabilizer
        u1, svars, hist = ctrl.compute_control(state, svars, hist)
        assert ctrl._stabilizer_initialized

        # Second call should not re-initialize
        u2, svars, hist = ctrl.compute_control(state, svars, hist)
        assert ctrl._stabilizer_initialized

    def test_stabilizer_force_saturation(self):
        """Test that stabilizer control respects max_force."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=0.5),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            switch_energy_factor=0.6,
            switch_angle_tolerance=0.5,
            dt=0.01,
            max_force=1.0  # Very low limit
        )

        # Large angle to trigger large stabilizer control
        state = np.array([0.0, 0.3, -0.3, 0.0, 0.0, 0.0])
        svars = ctrl.initialize_state()
        hist = ctrl.initialize_history()

        u, svars, hist = ctrl.compute_control(state, svars, hist)

        # Should be saturated
        assert abs(u) <= ctrl.max_force


# =====================================================================================
# History and State Management
# =====================================================================================

class TestHistoryManagement:
    """Test history tracking and state propagation."""

    def test_history_mode_tracking(self):
        """Test that history tracks current mode."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=0.5),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            switch_energy_factor=0.6,
            switch_angle_tolerance=0.5,
            dt=0.01,
            max_force=20.0
        )

        state = np.array([0.0, 0.1, -0.1, 0.0, 0.0, 0.0])
        svars = ctrl.initialize_state()
        hist = ctrl.initialize_history()

        # Initial history
        assert hist["mode"] == "swing"

        # Switch to stabilize
        u, svars, hist = ctrl.compute_control(state, svars, hist)
        assert hist["mode"] == "stabilize"

    def test_state_propagation(self):
        """Test that state variables are properly propagated."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=0.5),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            dt=0.01,
            max_force=20.0
        )

        state = np.array([0.0, 0.1, -0.1, 0.0, 0.0, 0.0])
        svars = ctrl.initialize_state()
        hist = ctrl.initialize_history()

        # Multiple calls should update state
        u1, svars1, hist1 = ctrl.compute_control(state, svars, hist)
        u2, svars2, hist2 = ctrl.compute_control(state, svars1, hist1)

        assert isinstance(svars2, dict)
        assert "integral" in svars2


# =====================================================================================
# Edge Cases and Boundary Conditions
# =====================================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_velocity_state(self):
        """Test control with zero velocity."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=1.0),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            dt=0.01,
            max_force=20.0
        )

        state = np.array([0.0, np.pi, np.pi, 0.0, 0.0, 0.0])
        u, _, _ = ctrl.compute_control(state, ctrl.initialize_state(), ctrl.initialize_history())

        # Should produce control even with zero velocity
        assert isinstance(u, float)

    def test_exact_upright_state(self):
        """Test with exactly upright state (zero angles)."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=0.5),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            switch_energy_factor=0.6,
            switch_angle_tolerance=0.5,
            dt=0.01,
            max_force=20.0
        )

        state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        u, _, _ = ctrl.compute_control(state, ctrl.initialize_state(), ctrl.initialize_history())

        # Should switch to stabilize (zero angles are within tolerance)
        assert ctrl._mode == "stabilize"

    def test_consecutive_mode_switches(self):
        """Test multiple consecutive mode switches."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=0.5),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            switch_energy_factor=0.6,
            exit_energy_factor=0.3,
            switch_angle_tolerance=0.3,
            reentry_angle_tolerance=0.4,
            dt=0.01,
            max_force=20.0
        )

        svars = ctrl.initialize_state()
        hist = ctrl.initialize_history()

        # Swing -> Stabilize
        state_upright = np.array([0.0, 0.1, -0.1, 0.0, 0.0, 0.0])
        u1, svars, hist = ctrl.compute_control(state_upright, svars, hist)
        assert ctrl._mode == "stabilize"

        # Stabilize -> Swing
        ctrl._stabilizer_initialized = True
        state_large_angle = np.array([0.0, 0.5, -0.5, 0.0, 0.0, 0.0])
        u2, svars, hist = ctrl.compute_control(state_large_angle, svars, hist)
        assert ctrl._mode == "swing"

        # Swing -> Stabilize again
        u3, svars, hist = ctrl.compute_control(state_upright, svars, hist)
        assert ctrl._mode == "stabilize"

    def test_very_small_dt(self):
        """Test controller with very small timestep."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=1.0),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=10.0,
            dt=1e-6,  # Very small
            max_force=20.0
        )

        state = np.array([0.0, np.pi, np.pi, 0.0, 0.5, 0.0])
        u, _, _ = ctrl.compute_control(state, ctrl.initialize_state(), ctrl.initialize_history())

        assert isinstance(u, float)
        assert np.isfinite(u)

    def test_very_large_energy_gain(self):
        """Test controller with very large energy gain."""
        ctrl = SwingUpSMC(
            dynamics_model=SimpleDynamics(energy_value=10.0),
            stabilizing_controller=SimpleStabilizer(),
            energy_gain=1000.0,  # Very large
            dt=0.01,
            max_force=20.0
        )

        state = np.array([0.0, np.pi, np.pi, 0.0, 0.5, 0.0])
        u, _, _ = ctrl.compute_control(state, ctrl.initialize_state(), ctrl.initialize_history())

        # Should be saturated
        assert abs(u) <= ctrl.max_force
