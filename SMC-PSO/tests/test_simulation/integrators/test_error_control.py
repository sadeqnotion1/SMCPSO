# ==============================================================================
# tests/test_simulation/integrators/test_error_control.py
#
# Comprehensive tests for adaptive step size error controllers
#
# Tests error-based step size adaptation, acceptance/rejection logic,
# and safety bounds for ErrorController, PIController, and DeadBeatController.
# ==============================================================================

import pytest
import numpy as np

from src.simulation.integrators.adaptive.error_control import (
    ErrorController,
    PIController,
    DeadBeatController
)


# ==============================================================================
# Test ErrorController (Basic)
# ==============================================================================

class TestErrorController:
    """Tests for basic ErrorController."""

    def test_initialization_default(self):
        """Test default initialization."""
        controller = ErrorController()
        assert controller.safety_factor == 0.9

    def test_initialization_custom(self):
        """Test custom safety factor."""
        controller = ErrorController(safety_factor=0.85)
        assert controller.safety_factor == 0.85

    def test_accept_step_small_error(self):
        """Test step acceptance when error is below tolerance."""
        controller = ErrorController(safety_factor=0.9)

        error_norm = 0.5  # Below tolerance of 1.0
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 0.1
        order = 4

        new_dt, accept = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order
        )

        assert accept is True
        assert new_dt > current_dt  # Should grow step size
        assert min_dt <= new_dt <= max_dt

    def test_reject_step_large_error(self):
        """Test step rejection when error exceeds tolerance."""
        controller = ErrorController(safety_factor=0.9)

        error_norm = 2.0  # Above tolerance of 1.0
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 0.1
        order = 4

        new_dt, accept = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order
        )

        assert accept is False
        assert new_dt < current_dt  # Should shrink step size
        assert min_dt <= new_dt <= max_dt

    def test_zero_error_handling(self):
        """Test handling of perfect accuracy (zero error)."""
        controller = ErrorController()

        error_norm = 0.0  # Perfect accuracy
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 0.1
        order = 4

        new_dt, accept = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order
        )

        assert accept is True
        # Should use factor of 2.0 for zero error
        assert new_dt == pytest.approx(min(current_dt * 2.0, max_dt))

    def test_safety_factor_application_accept(self):
        """Test safety factor is applied correctly on acceptance."""
        safety = 0.8
        controller = ErrorController(safety_factor=safety)

        error_norm = 0.5
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 1.0
        order = 4

        new_dt, accept = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order
        )

        # Expected factor: safety * (1.0/error_norm)^(1/order)
        expected_factor = min(safety * (1.0 / error_norm) ** (1.0 / order), 5.0)
        expected_dt = current_dt * expected_factor

        assert accept is True
        assert new_dt == pytest.approx(min(expected_dt, max_dt))

    def test_safety_factor_application_reject(self):
        """Test safety factor is applied correctly on rejection."""
        safety = 0.8
        controller = ErrorController(safety_factor=safety)

        error_norm = 3.0
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 1.0
        order = 4

        new_dt, accept = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order
        )

        # Expected factor: max(safety * (1.0/error_norm)^(1/(order+1)), 0.1)
        expected_factor = max(safety * (1.0 / error_norm) ** (1.0 / (order + 1)), 0.1)
        expected_dt = current_dt * expected_factor

        assert accept is False
        assert new_dt == pytest.approx(max(expected_dt, min_dt))

    def test_growth_factor_limit(self):
        """Test that growth factor is limited to 5.0."""
        controller = ErrorController(safety_factor=0.9)

        error_norm = 0.001  # Very small error
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 10.0
        order = 1  # Low order to maximize growth

        new_dt, accept = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order
        )

        assert accept is True
        # Factor should be capped at 5.0
        assert new_dt <= current_dt * 5.0

    def test_shrinkage_factor_limit(self):
        """Test that shrinkage factor is limited to 0.1."""
        controller = ErrorController(safety_factor=0.9)

        error_norm = 100.0  # Very large error
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 10.0
        order = 1

        new_dt, accept = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order
        )

        assert accept is False
        # Factor should be capped at 0.1
        assert new_dt >= current_dt * 0.1

    def test_min_dt_enforcement(self):
        """Test that new dt respects min_dt bound."""
        controller = ErrorController(safety_factor=0.9)

        error_norm = 100.0  # Large error to trigger shrinkage
        current_dt = 1e-5
        min_dt = 1e-6
        max_dt = 1.0
        order = 4

        new_dt, accept = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order
        )

        assert accept is False
        assert new_dt >= min_dt

    def test_max_dt_enforcement(self):
        """Test that new dt respects max_dt bound."""
        controller = ErrorController(safety_factor=0.9)

        error_norm = 0.01  # Small error to trigger growth
        current_dt = 0.05
        min_dt = 1e-6
        max_dt = 0.1
        order = 4

        new_dt, accept = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order
        )

        assert accept is True
        assert new_dt <= max_dt

    def test_order_dependency_accept(self):
        """Test that higher order gives more aggressive growth."""
        controller = ErrorController(safety_factor=0.9)

        error_norm = 0.5
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 1.0

        # Compare order 2 vs order 4
        new_dt_order2, _ = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order=2
        )
        new_dt_order4, _ = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order=4
        )

        # Higher order should give smaller exponent, thus less growth
        # (1/order) is smaller for larger order
        assert new_dt_order2 > new_dt_order4

    def test_order_dependency_reject(self):
        """Test that higher order gives more conservative shrinkage on rejection."""
        controller = ErrorController(safety_factor=0.9)

        error_norm = 3.0
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 1.0

        # Compare order 2 vs order 4
        new_dt_order2, _ = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order=2
        )
        new_dt_order4, _ = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order=4
        )

        # Higher order uses 1/(order+1) exponent for rejection
        # Smaller exponent means less aggressive shrinkage
        assert new_dt_order4 > new_dt_order2


# ==============================================================================
# Test PIController
# ==============================================================================

class TestPIController:
    """Tests for PI (Proportional-Integral) controller."""

    def test_initialization_default(self):
        """Test default initialization."""
        controller = PIController()
        assert controller.safety_factor == 0.9
        assert controller.alpha == 0.7
        assert controller.beta == 0.4
        assert controller._previous_error is None

    def test_initialization_custom(self):
        """Test custom parameters."""
        controller = PIController(safety_factor=0.85, alpha=0.6, beta=0.3)
        assert controller.safety_factor == 0.85
        assert controller.alpha == 0.6
        assert controller.beta == 0.3

    def test_first_step_uses_basic_controller(self):
        """Test that first step uses basic controller (no error history)."""
        controller = PIController(safety_factor=0.9, alpha=0.7, beta=0.4)

        error_norm = 0.5
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 1.0
        order = 4

        new_dt, accept = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order
        )

        # First step should use basic formula (no PI yet)
        expected_factor = min(0.9 * (1.0 / error_norm) ** (1.0 / order), 5.0)
        expected_dt = current_dt * expected_factor

        assert accept is True
        assert new_dt == pytest.approx(min(expected_dt, max_dt), rel=1e-10)

    def test_second_step_uses_pi_formula(self):
        """Test that second step uses PI formula with error history."""
        controller = PIController(safety_factor=0.9, alpha=0.7, beta=0.4)

        error_norm_1 = 0.8
        error_norm_2 = 0.5
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 1.0
        order = 4

        # First step
        controller.update_step_size(error_norm_1, current_dt, min_dt, max_dt, order)

        # Second step (should use PI)
        new_dt, accept = controller.update_step_size(
            error_norm_2, current_dt, min_dt, max_dt, order
        )

        # PI formula: safety * (tol/err)^alpha * (prev_err/err)^beta
        proportional = (1.0 / error_norm_2) ** 0.7
        integral = (error_norm_1 / error_norm_2) ** 0.4
        expected_factor = np.clip(0.9 * proportional * integral, 0.1, 5.0)
        expected_dt = np.clip(current_dt * expected_factor, min_dt, max_dt)

        assert accept is True
        assert new_dt == pytest.approx(expected_dt, rel=1e-10)

    def test_error_history_tracking(self):
        """Test that error history is tracked correctly."""
        controller = PIController()

        error_norms = [0.8, 0.5, 0.3]
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 1.0
        order = 4

        for error_norm in error_norms:
            controller.update_step_size(error_norm, current_dt, min_dt, max_dt, order)
            # Previous error should be updated
            assert controller._previous_error == error_norm

    def test_reset_clears_history(self):
        """Test that reset() clears error history."""
        controller = PIController()

        # Take some steps to build history
        error_norm = 0.5
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 1.0
        order = 4

        controller.update_step_size(error_norm, current_dt, min_dt, max_dt, order)
        assert controller._previous_error is not None

        # Reset should clear history
        controller.reset()
        assert controller._previous_error is None

    def test_zero_error_first_step(self):
        """Test zero error handling on first step."""
        controller = PIController()

        error_norm = 0.0
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 1.0
        order = 4

        new_dt, accept = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order
        )

        assert accept is True
        assert new_dt == pytest.approx(min(current_dt * 2.0, max_dt))

    def test_zero_error_with_history(self):
        """Test zero error handling when error history exists."""
        controller = PIController()

        # First step
        controller.update_step_size(0.5, 0.01, 1e-6, 1.0, 4)

        # Second step with zero error
        new_dt, accept = controller.update_step_size(
            0.0, 0.01, 1e-6, 1.0, 4
        )

        assert accept is True
        # Should use factor of 2.0 even with history
        assert new_dt == pytest.approx(min(0.01 * 2.0, 1.0))

    def test_pi_smoother_than_basic(self):
        """Test that PI controller uses error history (behavioral test)."""
        basic = ErrorController(safety_factor=0.9)
        pi = PIController(safety_factor=0.9, alpha=0.7, beta=0.4)

        error_sequence = [0.8, 0.3, 0.7, 0.4]  # Varying errors
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 1.0
        order = 4

        basic_dts = []
        pi_dts = []

        for error in error_sequence:
            dt_basic, _ = basic.update_step_size(error, current_dt, min_dt, max_dt, order)
            dt_pi, _ = pi.update_step_size(error, current_dt, min_dt, max_dt, order)

            basic_dts.append(dt_basic)
            pi_dts.append(dt_pi)

        # After first step, PI and basic should give different results
        # (due to integral term in PI)
        # This is a behavioral check, not a strict guarantee of smoothness
        assert basic_dts[0] == pi_dts[0]  # First step should be identical
        assert basic_dts[1] != pi_dts[1]  # Second step should differ (PI uses history)

    def test_accept_reject_behavior(self):
        """Test step acceptance/rejection follows same rules as basic controller."""
        controller = PIController()

        # Accept case
        new_dt_accept, accept = controller.update_step_size(
            0.5, 0.01, 1e-6, 1.0, 4
        )
        assert accept is True

        # Reject case
        new_dt_reject, reject = controller.update_step_size(
            2.0, 0.01, 1e-6, 1.0, 4
        )
        assert reject is False


# ==============================================================================
# Test DeadBeatController
# ==============================================================================

class TestDeadBeatController:
    """Tests for DeadBeatController (aggressive adaptation)."""

    def test_initialization_default(self):
        """Test default initialization."""
        controller = DeadBeatController()
        assert controller.safety_factor == 0.9
        assert controller.target_error == 0.1

    def test_initialization_custom(self):
        """Test custom parameters."""
        controller = DeadBeatController(safety_factor=0.85, target_error=0.05)
        assert controller.safety_factor == 0.85
        assert controller.target_error == 0.05

    def test_targets_specific_error_level(self):
        """Test that controller targets specified error level."""
        target = 0.2
        controller = DeadBeatController(safety_factor=0.9, target_error=target)

        error_norm = 0.8
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 10.0
        order = 4

        new_dt, accept = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order
        )

        # Expected factor: safety * (target/error)^(1/order)
        expected_factor = np.clip(0.9 * (target / error_norm) ** (1.0 / order), 0.05, 10.0)
        expected_dt = np.clip(current_dt * expected_factor, min_dt, max_dt)

        assert accept is True
        assert new_dt == pytest.approx(expected_dt, rel=1e-10)

    def test_aggressive_bounds(self):
        """Test that DeadBeat uses more aggressive bounds (0.05, 10.0)."""
        controller = DeadBeatController()

        # Very large error should use lower bound of 0.05
        error_norm = 1000.0
        current_dt = 0.01
        min_dt, max_dt = 1e-8, 10.0
        order = 4

        new_dt, _ = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order
        )

        # Factor should be at lower bound of 0.05
        assert new_dt >= current_dt * 0.05
        assert new_dt >= min_dt

    def test_aggressive_growth(self):
        """Test that DeadBeat has higher factor bounds (10.0 vs 5.0)."""
        basic = ErrorController(safety_factor=0.9)
        deadbeat = DeadBeatController(safety_factor=0.9, target_error=0.05)

        # Use extremely small error to hit the upper factor bound
        error_norm = 1e-10  # Extremely small error
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 10.0
        order = 1  # Low order to maximize growth factor

        dt_basic, _ = basic.update_step_size(error_norm, current_dt, min_dt, max_dt, order)
        dt_deadbeat, _ = deadbeat.update_step_size(error_norm, current_dt, min_dt, max_dt, order)

        # Basic is capped at factor 5.0, DeadBeat at factor 10.0
        # With extremely small error, both should hit their caps
        assert dt_basic <= current_dt * 5.0  # Basic cap
        assert dt_deadbeat <= current_dt * 10.0  # DeadBeat cap
        # DeadBeat should be able to grow more
        assert dt_deadbeat >= dt_basic

    def test_zero_error_handling(self):
        """Test zero error handling."""
        controller = DeadBeatController()

        error_norm = 0.0
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 10.0
        order = 4

        new_dt, accept = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order
        )

        assert accept is True
        # Should use factor of 2.0 for zero error
        assert new_dt == pytest.approx(min(current_dt * 2.0, max_dt))

    def test_accept_reject_behavior(self):
        """Test step acceptance/rejection follows same tolerance."""
        controller = DeadBeatController()

        # Accept case (error <= 1.0)
        new_dt_accept, accept = controller.update_step_size(
            0.5, 0.01, 1e-6, 1.0, 4
        )
        assert accept is True

        # Reject case (error > 1.0)
        new_dt_reject, reject = controller.update_step_size(
            2.0, 0.01, 1e-6, 1.0, 4
        )
        assert reject is False

    def test_factor_bounds_enforcement(self):
        """Test that factor is clipped to [0.05, 10.0]."""
        controller = DeadBeatController()

        # Very small error to test upper bound
        error_norm = 0.00001
        current_dt = 0.01
        min_dt, max_dt = 1e-6, 100.0
        order = 1  # Low order to maximize growth

        new_dt, _ = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order
        )

        # Factor should be capped at 10.0
        assert new_dt <= current_dt * 10.0

        # Very large error to test lower bound
        error_norm = 10000.0
        new_dt, _ = controller.update_step_size(
            error_norm, current_dt, min_dt, max_dt, order
        )

        # Factor should be capped at 0.05
        assert new_dt >= current_dt * 0.05
