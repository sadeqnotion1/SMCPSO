# ==============================================================================
# tests/test_simulation/integrators/test_base_integrator.py
#
# Tests for BaseIntegrator abstract class and IntegrationResult
#
# Tests initialization, statistics tracking, input validation, error norm
# computation, and integration result container.
# ==============================================================================

import pytest
import numpy as np

from src.simulation.integrators.base import BaseIntegrator, IntegrationResult
from src.simulation.integrators.fixed_step.euler import ForwardEuler  # Concrete implementation


# ==============================================================================
# Test BaseIntegrator
# ==============================================================================

class TestBaseIntegrator:
    """Tests for BaseIntegrator abstract base class."""

    def test_initialization_default(self):
        """Test default initialization."""
        integrator = ForwardEuler()  # Use concrete implementation
        assert integrator.rtol == 1e-6
        assert integrator.atol == 1e-9

    def test_initialization_custom(self):
        """Test custom tolerances."""
        integrator = ForwardEuler(rtol=1e-5, atol=1e-8)
        assert integrator.rtol == 1e-5
        assert integrator.atol == 1e-8

    def test_statistics_initialization(self):
        """Test statistics are initialized to zero."""
        integrator = ForwardEuler()
        stats = integrator.get_statistics()

        assert stats["total_steps"] == 0
        assert stats["accepted_steps"] == 0
        assert stats["rejected_steps"] == 0
        assert stats["function_evaluations"] == 0

    def test_statistics_are_independent_copy(self):
        """Test get_statistics returns a copy, not reference."""
        integrator = ForwardEuler()
        stats1 = integrator.get_statistics()
        stats1["total_steps"] = 999  # Modify copy

        stats2 = integrator.get_statistics()
        assert stats2["total_steps"] == 0  # Original unchanged

    def test_reset_statistics(self):
        """Test reset_statistics clears all counters."""
        integrator = ForwardEuler()

        # Manually set some statistics
        integrator._stats["total_steps"] = 10
        integrator._stats["accepted_steps"] = 8
        integrator._stats["rejected_steps"] = 2
        integrator._stats["function_evaluations"] = 40

        # Reset
        integrator.reset_statistics()

        # Verify all zero
        stats = integrator.get_statistics()
        assert stats["total_steps"] == 0
        assert stats["accepted_steps"] == 0
        assert stats["rejected_steps"] == 0
        assert stats["function_evaluations"] == 0

    def test_update_stats_accepted(self):
        """Test _update_stats for accepted step."""
        integrator = ForwardEuler()
        integrator._update_stats(accepted=True, func_evals=4)

        stats = integrator.get_statistics()
        assert stats["total_steps"] == 1
        assert stats["accepted_steps"] == 1
        assert stats["rejected_steps"] == 0
        assert stats["function_evaluations"] == 4

    def test_update_stats_rejected(self):
        """Test _update_stats for rejected step."""
        integrator = ForwardEuler()
        integrator._update_stats(accepted=False, func_evals=7)

        stats = integrator.get_statistics()
        assert stats["total_steps"] == 1
        assert stats["accepted_steps"] == 0
        assert stats["rejected_steps"] == 1
        assert stats["function_evaluations"] == 7

    def test_update_stats_accumulation(self):
        """Test _update_stats accumulates over multiple calls."""
        integrator = ForwardEuler()

        integrator._update_stats(accepted=True, func_evals=1)
        integrator._update_stats(accepted=True, func_evals=1)
        integrator._update_stats(accepted=False, func_evals=2)

        stats = integrator.get_statistics()
        assert stats["total_steps"] == 3
        assert stats["accepted_steps"] == 2
        assert stats["rejected_steps"] == 1
        assert stats["function_evaluations"] == 4

    # ==============================================================================
    # Input Validation Tests
    # ==============================================================================

    def test_validate_inputs_non_callable_dynamics(self):
        """Test validation rejects non-callable dynamics."""
        integrator = ForwardEuler()

        with pytest.raises(TypeError, match="dynamics_fn must be callable"):
            integrator._validate_inputs(
                "not_callable",  # Invalid
                np.array([1.0]),
                np.array([0.0]),
                0.01
            )

    def test_validate_inputs_non_array_state(self):
        """Test validation rejects non-array state."""
        integrator = ForwardEuler()

        def dynamics(t, x, u):
            return x

        with pytest.raises(TypeError, match="state must be numpy array"):
            integrator._validate_inputs(
                dynamics,
                [1.0, 2.0],  # List, not ndarray
                np.array([0.0]),
                0.01
            )

    def test_validate_inputs_non_array_control(self):
        """Test validation rejects non-array control."""
        integrator = ForwardEuler()

        def dynamics(t, x, u):
            return x

        with pytest.raises(TypeError, match="control must be numpy array"):
            integrator._validate_inputs(
                dynamics,
                np.array([1.0]),
                0.5,  # Scalar, not ndarray
                0.01
            )

    def test_validate_inputs_negative_dt(self):
        """Test validation rejects negative dt."""
        integrator = ForwardEuler()

        def dynamics(t, x, u):
            return x

        with pytest.raises(ValueError, match="dt must be positive"):
            integrator._validate_inputs(
                dynamics,
                np.array([1.0]),
                np.array([0.0]),
                -0.01  # Negative
            )

    def test_validate_inputs_zero_dt(self):
        """Test validation rejects zero dt."""
        integrator = ForwardEuler()

        def dynamics(t, x, u):
            return x

        with pytest.raises(ValueError, match="dt must be positive"):
            integrator._validate_inputs(
                dynamics,
                np.array([1.0]),
                np.array([0.0]),
                0.0  # Zero
            )

    def test_validate_inputs_nan_state(self):
        """Test validation rejects NaN in state."""
        integrator = ForwardEuler()

        def dynamics(t, x, u):
            return x

        with pytest.raises(ValueError, match="state contains non-finite values"):
            integrator._validate_inputs(
                dynamics,
                np.array([1.0, np.nan, 0.5]),  # Contains NaN
                np.array([0.0]),
                0.01
            )

    def test_validate_inputs_inf_state(self):
        """Test validation rejects Inf in state."""
        integrator = ForwardEuler()

        def dynamics(t, x, u):
            return x

        with pytest.raises(ValueError, match="state contains non-finite values"):
            integrator._validate_inputs(
                dynamics,
                np.array([1.0, np.inf]),  # Contains Inf
                np.array([0.0]),
                0.01
            )

    def test_validate_inputs_nan_control(self):
        """Test validation rejects NaN in control."""
        integrator = ForwardEuler()

        def dynamics(t, x, u):
            return x

        with pytest.raises(ValueError, match="control contains non-finite values"):
            integrator._validate_inputs(
                dynamics,
                np.array([1.0]),
                np.array([np.nan]),  # Contains NaN
                0.01
            )

    def test_validate_inputs_valid(self):
        """Test validation passes for valid inputs."""
        integrator = ForwardEuler()

        def dynamics(t, x, u):
            return x

        # Should not raise
        integrator._validate_inputs(
            dynamics,
            np.array([1.0, 0.5]),
            np.array([0.2]),
            0.01
        )

    # ==============================================================================
    # Error Norm Computation Tests
    # ==============================================================================

    def test_compute_error_norm_basic(self):
        """Test error norm computation with simple values."""
        integrator = ForwardEuler(rtol=1e-6, atol=1e-9)

        error = np.array([1e-8, 2e-8])
        state = np.array([1.0, 2.0])

        # Scale = atol + rtol * |state|
        # Scale = [1e-9 + 1e-6*1.0, 1e-9 + 1e-6*2.0]
        #       = [1.001e-6, 2.001e-6]
        # Normalized error = error / scale
        # RMS = sqrt(mean((error/scale)^2))

        expected_scale = 1e-9 + 1e-6 * np.abs(state)
        expected_normalized = error / expected_scale
        expected_rms = np.sqrt(np.mean(expected_normalized**2))

        error_norm = integrator._compute_error_norm(error, state)

        assert error_norm == pytest.approx(expected_rms, rel=1e-10)

    def test_compute_error_norm_zero_state(self):
        """Test error norm when state is zero (uses absolute tolerance)."""
        integrator = ForwardEuler(rtol=1e-6, atol=1e-9)

        error = np.array([1e-10, 1e-10])
        state = np.array([0.0, 0.0])

        # Scale should be atol when state is zero
        expected_scale = 1e-9
        expected_normalized = error / expected_scale
        expected_rms = np.sqrt(np.mean(expected_normalized**2))

        error_norm = integrator._compute_error_norm(error, state)

        assert error_norm == pytest.approx(expected_rms, rel=1e-10)

    def test_compute_error_norm_large_state(self):
        """Test error norm scaling with large state values."""
        integrator = ForwardEuler(rtol=1e-6, atol=1e-9)

        error = np.array([1e-4])
        state = np.array([1e6])  # Large state

        # Scale dominated by rtol * |state| = 1e-6 * 1e6 = 1.0
        # Normalized error = 1e-4 / 1.0 = 1e-4
        error_norm = integrator._compute_error_norm(error, state)

        # Approximately 1e-4 (RMS of single element)
        assert error_norm == pytest.approx(1e-4, rel=1e-8)

    def test_compute_error_norm_custom_tolerances(self):
        """Test error norm with custom tolerances."""
        integrator = ForwardEuler(rtol=1e-3, atol=1e-6)

        error = np.array([1e-5])
        state = np.array([1.0])

        # Scale = 1e-6 + 1e-3 * 1.0 = 1.001e-3
        # Normalized = 1e-5 / 1.001e-3 ≈ 0.00999
        expected_scale = 1e-6 + 1e-3
        expected_norm = error[0] / expected_scale

        error_norm = integrator._compute_error_norm(error, state)

        assert error_norm == pytest.approx(expected_norm, rel=1e-8)


# ==============================================================================
# Test IntegrationResult
# ==============================================================================

class TestIntegrationResult:
    """Tests for IntegrationResult container."""

    def test_initialization_minimal(self):
        """Test initialization with only required arguments."""
        state = np.array([1.0, 2.0])
        result = IntegrationResult(state=state)

        assert np.array_equal(result.state, state)
        assert result.accepted is True
        assert result.error_estimate is None
        assert result.suggested_dt is None
        assert result.function_evaluations == 1

    def test_initialization_full(self):
        """Test initialization with all arguments."""
        state = np.array([1.0, 2.0])
        result = IntegrationResult(
            state=state,
            accepted=False,
            error_estimate=0.005,
            suggested_dt=0.001,
            function_evaluations=7
        )

        assert np.array_equal(result.state, state)
        assert result.accepted is False
        assert result.error_estimate == 0.005
        assert result.suggested_dt == 0.001
        assert result.function_evaluations == 7

    def test_state_reference(self):
        """Test that state is stored as reference (not copy)."""
        state = np.array([1.0, 2.0])
        result = IntegrationResult(state=state)

        # Modify original
        state[0] = 999.0

        # Result should reflect change (shares reference)
        assert result.state[0] == 999.0

    def test_fields_accessible(self):
        """Test all fields are accessible."""
        result = IntegrationResult(
            state=np.array([1.0]),
            accepted=True,
            error_estimate=0.1,
            suggested_dt=0.05,
            function_evaluations=4
        )

        # Should not raise AttributeError
        _ = result.state
        _ = result.accepted
        _ = result.error_estimate
        _ = result.suggested_dt
        _ = result.function_evaluations
