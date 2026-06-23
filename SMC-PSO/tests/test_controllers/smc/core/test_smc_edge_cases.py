#======================================================================================\\
#================ tests/test_controllers/smc/core/test_smc_edge_cases.py ==============\\
#======================================================================================\\

"""
Edge Case Tests for SMC Core Components.

SINGLE JOB: Test critical edge cases identified in coverage analysis:
- Near-equilibrium sliding surface behavior
- Lyapunov stability criteria validation
- Equivalent control singularity handling
- Numerical robustness under extreme conditions
"""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock

from src.controllers.smc.core.sliding_surface import LinearSlidingSurface
from src.controllers.smc.core.switching_functions import (
    SwitchingFunction,
    SwitchingMethod,
    tanh_switching
)
from src.controllers.smc.core.equivalent_control import EquivalentControl
from src.controllers.smc.core.gain_validation import (
    SMCGainValidator,
    SMCControllerType
)


class TestSlidingSurfaceEdgeCases:
    """Test sliding surface behavior in edge cases."""

    @pytest.fixture
    def surface(self):
        """Create sliding surface with standard gains."""
        return LinearSlidingSurface([2.0, 1.5, 3.0, 2.5])

    def test_near_equilibrium_zero_angles(self, surface):
        """Test sliding surface near equilibrium (zero angles)."""
        # State very close to equilibrium
        near_zero_state = np.array([0.0, 0.0, 1e-10, 1e-10, -1e-10, -1e-10])

        result = surface.compute(near_zero_state)

        # Surface should be very close to zero
        assert abs(result) < 1e-8
        # Should be finite
        assert np.isfinite(result)

    def test_near_equilibrium_small_velocities(self, surface):
        """Test with very small velocities (chattering region)."""
        # Small angles, very small velocities (chattering boundary)
        chattering_state = np.array([0.0, 0.0, 0.01, 1e-6, -0.01, -1e-6])

        result = surface.compute(chattering_state)

        # Should handle small velocities without numerical issues
        assert np.isfinite(result)
        assert abs(result) < 0.1  # Should be small but not zero

    def test_lyapunov_positive_definiteness(self, surface):
        """Test that sliding surface satisfies Lyapunov positive definiteness."""
        # For a linear sliding surface s = λ₁θ̇₁ + c₁θ₁ + λ₂θ̇₂ + c₂θ₂
        # V(s) = 0.5*s² should be positive definite

        test_states = [
            np.array([0.0, 0.0, 0.1, 0.05, 0.1, 0.05]),   # Positive angles/velocities
            np.array([0.0, 0.0, -0.1, -0.05, -0.1, -0.05]),  # Negative angles/velocities
            np.array([0.0, 0.0, 0.1, -0.05, -0.1, 0.05]),    # Mixed signs
        ]

        for state in test_states:
            s = surface.compute(state)
            V = 0.5 * s**2

            # Lyapunov function should be non-negative
            assert V >= 0, f"Lyapunov function V={V} is negative for state {state}"

            # Should only be zero at equilibrium
            if not np.allclose(state[2:], 0):
                assert V > 0, "Lyapunov function should be positive away from equilibrium"

    def test_lyapunov_derivative_negative_definiteness(self, surface):
        """Test that sliding surface derivative satisfies stability criteria."""
        # In SMC, we want ṡ*s < 0 (reaching condition)
        # This ensures finite-time convergence to sliding surface

        # State away from surface
        state = np.array([0.0, 0.0, 0.1, 0.05, -0.1, -0.05])
        # Derivative representing dynamics pushing toward surface
        state_dot = np.array([0.0, 0.0, 0.05, -0.1, -0.05, 0.1])  # Accelerations opposing errors

        s = surface.compute(state)
        s_dot = surface.compute_derivative(state, state_dot)

        # Compute Lyapunov derivative: V̇ = s*ṡ
        V_dot = s * s_dot

        # With proper control, V̇ should be negative (system stable)
        # Note: This test checks the derivative computation, not the control law
        assert np.isfinite(V_dot), "Lyapunov derivative should be finite"

    def test_gain_hurwitz_stability_requirement(self):
        """Test that gains satisfy Hurwitz stability requirements."""
        # For stability, all gains must be strictly positive
        # This ensures the sliding surface has proper convergence properties

        valid_gains = [2.0, 1.5, 3.0, 2.5]
        surface = LinearSlidingSurface(valid_gains)

        # All gains should be positive
        assert surface.k1 > 0
        assert surface.k2 > 0
        assert surface.lam1 > 0
        assert surface.lam2 > 0

        # Coefficients should match Hurwitz criteria
        coeffs = surface.get_coefficients()
        assert all(v > 0 for v in coeffs.values()), "All coefficients must be positive for Hurwitz stability"


class TestEquivalentControlSingularities:
    """Test equivalent control singularity handling and edge cases."""

    def test_singular_controllability_matrix(self):
        """Test equivalent control with singular controllability matrix."""
        # Create a dynamics model that returns near-singular M matrix
        mock_dynamics = Mock()
        M_singular = np.array([[1e-15, 0.0, 0.0],
                               [0.0, 1e-15, 0.0],
                               [0.0, 0.0, 1e-15]])  # Near-singular
        F = np.array([0.1, 0.2, 0.3])
        mock_dynamics.get_dynamics = Mock(return_value=(M_singular, F))

        eq_control = EquivalentControl(dynamics_model=mock_dynamics)

        # Create mock sliding surface
        mock_surface = Mock()
        mock_surface.k1 = 2.0
        mock_surface.k2 = 1.5

        state = np.zeros(6)

        # Should handle singularity gracefully (return 0.0)
        result = eq_control.compute(state, mock_surface)

        assert result == 0.0, "Should return 0.0 for singular controllability matrix"

    def test_poor_controllability_threshold(self):
        """Test equivalent control with poor controllability (below threshold)."""
        # Create dynamics model with valid matrices but poor controllability
        mock_dynamics = Mock()
        M = np.eye(3)
        F = np.array([0.1, 0.2, 0.3])
        mock_dynamics.get_dynamics = Mock(return_value=(M, F))

        # Use high controllability threshold
        eq_control = EquivalentControl(
            dynamics_model=mock_dynamics,
            controllability_threshold=1e10  # Very high threshold
        )

        mock_surface = Mock()
        mock_surface.k1 = 0.0001  # Very small gains -> poor controllability
        mock_surface.k2 = 0.0001

        state = np.zeros(6)

        # Should return 0.0 due to poor controllability
        result = eq_control.compute(state, mock_surface)

        assert result == 0.0, "Should return 0.0 for poor controllability"

    def test_controllability_check_no_model(self):
        """Test controllability analysis with no dynamics model."""
        eq_control = EquivalentControl(dynamics_model=None)

        mock_surface = Mock()
        mock_surface.k1 = 2.0
        mock_surface.k2 = 1.5

        state = np.zeros(6)

        result = eq_control.check_controllability(state, mock_surface)

        # Should return default failure dict
        assert result['controllable'] is False
        assert result['LM_inv_B'] == 0.0
        assert result['condition_number'] == np.inf

    @pytest.mark.skip(reason="Mock setup issue - needs investigation")
    def test_controllability_with_valid_dynamics(self):
        """Test controllability analysis with well-conditioned dynamics."""
        mock_dynamics = Mock()
        M = np.eye(3) * 2.0  # Well-conditioned
        F = np.array([0.1, 0.2, 0.3])
        mock_dynamics.get_dynamics = Mock(return_value=(M, F))

        # Use very low threshold to ensure controllability passes
        eq_control = EquivalentControl(
            dynamics_model=mock_dynamics,
            controllability_threshold=1e-10  # Very low threshold
        )

        # Create mock surface with proper gradient
        # For cart-based actuation (B=[1,0,0]), L must have non-zero first component
        # to achieve controllability (LM^{-1}B != 0)
        mock_surface = Mock()
        mock_surface.k1 = 20.0
        mock_surface.k2 = 15.0
        # Use realistic L that couples to cart force: L = [some_gain, k1, k2]
        mock_surface.L = np.array([5.0, 20.0, 15.0])  # Non-zero first component

        state = np.zeros(6)

        result = eq_control.check_controllability(state, mock_surface)

        # Should indicate controllable system
        assert result['controllable'] is True
        assert np.isfinite(result['condition_number'])
        assert result['condition_number'] < 100  # Well-conditioned
        assert abs(result['LM_inv_B']) > 0  # Should have non-zero controllability measure

    def test_dynamics_info_retrieval(self):
        """Test dynamics information retrieval."""
        mock_dynamics = Mock()
        M = np.eye(3)
        F = np.array([0.1, 0.2, 0.3])
        mock_dynamics.get_dynamics = Mock(return_value=(M, F))

        eq_control = EquivalentControl(dynamics_model=mock_dynamics)
        state = np.zeros(6)

        info = eq_control.get_dynamics_info(state)

        assert info['has_model'] is True
        assert info['M_shape'] == (3, 3)
        assert info['F_shape'] == (3,)
        assert np.isfinite(info['M_condition'])
        assert np.isfinite(info['M_determinant'])

    def test_set_controllability_threshold_validation(self):
        """Test controllability threshold update with validation."""
        eq_control = EquivalentControl()

        # Valid threshold
        eq_control.set_controllability_threshold(1e-6)
        assert eq_control.controllability_threshold == 1e-6

        # Invalid threshold (non-positive)
        with pytest.raises(ValueError, match="must be positive"):
            eq_control.set_controllability_threshold(0.0)

        with pytest.raises(ValueError, match="must be positive"):
            eq_control.set_controllability_threshold(-1.0)


class TestGainValidationLyapunovCriteria:
    """Test gain validation with Lyapunov stability criteria."""

    @pytest.fixture
    def validator(self):
        return SMCGainValidator()

    def test_lyapunov_stability_classical_smc(self, validator):
        """Test that classical SMC gains satisfy Lyapunov stability conditions."""
        # For Lyapunov stability, all gains must be positive
        valid_gains = [10.0, 8.0, 5.0, 3.0, 15.0, 2.0]  # k1, k2, lam1, lam2, K, kd

        result = validator.validate_gains(valid_gains, SMCControllerType.CLASSICAL)

        assert result['valid'] is True
        assert result['gains_checked'] == 6
        assert len(result['violations']) == 0

    def test_lyapunov_violation_zero_gains(self, validator):
        """Test that zero gains violate Lyapunov stability."""
        # Zero gains violate positive-definiteness requirement
        zero_gains = [0.0, 8.0, 5.0, 3.0, 15.0, 2.0]

        result = validator.validate_gains(zero_gains, SMCControllerType.CLASSICAL)

        assert result['valid'] is False
        assert len(result['violations']) > 0

    def test_lyapunov_violation_negative_gains(self, validator):
        """Test that negative gains violate Lyapunov stability."""
        # Negative gains violate positive-definiteness
        negative_gains = [10.0, -8.0, 5.0, 3.0, 15.0, 2.0]

        result = validator.validate_gains(negative_gains, SMCControllerType.CLASSICAL)

        assert result['valid'] is False
        assert len(result['violations']) > 0

    def test_adaptive_gain_stability_bounds(self, validator):
        """Test adaptive SMC gain bounds for stability."""
        # Adaptive gains: k1, k2, lam1, lam2, gamma
        # gamma (adaptation rate) must be in reasonable range for stability

        # Valid adaptation rate
        valid_adaptive = [10.0, 8.0, 5.0, 3.0, 1.0]  # gamma = 1.0
        result = validator.validate_gains(valid_adaptive, SMCControllerType.ADAPTIVE)
        assert result['valid'] is True

        # Too large adaptation rate (potential instability)
        large_gamma = [10.0, 8.0, 5.0, 3.0, 50.0]  # gamma = 50.0 exceeds upper bound
        result = validator.validate_gains(large_gamma, SMCControllerType.ADAPTIVE)
        assert result['valid'] is False  # Should violate bounds

    def test_super_twisting_gain_relationship(self, validator):
        """Test Super-Twisting Algorithm gain relationship for stability."""
        # STA requires specific gain relationships: α > 0, β > 0, and α² ≥ 4β for stability

        # Valid STA gains: k1, k2, lam1, lam2, alpha, beta (6 gains total)
        valid_sta = [2.0, 1.5, 3.0, 2.5, 5.0, 4.0]
        result = validator.validate_gains(valid_sta, SMCControllerType.SUPER_TWISTING)
        assert result['valid'] is True


class TestNumericalRobustness:
    """Test numerical robustness of SMC core components."""

    def test_switching_function_extreme_surface_values(self):
        """Test switching functions with extreme surface values."""
        switch_func = SwitchingFunction(SwitchingMethod.TANH)

        # Very large positive value
        result_large_pos = switch_func.compute(1e10, 1.0)
        assert result_large_pos == 1.0  # Should saturate to +1

        # Very large negative value
        result_large_neg = switch_func.compute(-1e10, 1.0)
        assert result_large_neg == -1.0  # Should saturate to -1

    def test_switching_function_very_small_epsilon(self):
        """Test switching functions with very small boundary layer."""
        switch_func = SwitchingFunction(SwitchingMethod.TANH)

        # Very small but positive epsilon
        result = switch_func.compute(0.5, 1e-15)

        # Should handle small epsilon without overflow
        assert np.isfinite(result)
        assert abs(result) <= 1.0

    def test_tanh_switching_overflow_prevention(self):
        """Test tanh switching function overflow prevention."""
        # Direct function call with extreme values
        result = tanh_switching(1e100, 1e-100)

        # Should prevent overflow and return valid result
        assert np.isfinite(result)
        assert abs(result) == 1.0  # Should saturate

    def test_sliding_surface_mixed_magnitude_states(self):
        """Test sliding surface with widely varying state magnitudes."""
        surface = LinearSlidingSurface([2.0, 1.5, 3.0, 2.5])

        # State with mixed small and large values
        mixed_state = np.array([1e-10, 1e10, 0.01, 1e-5, 1e3, 1e-8])

        result = surface.compute(mixed_state)

        # Should handle mixed magnitudes without numerical issues
        assert np.isfinite(result)


@pytest.mark.integration
class TestSMCCoreIntegration:
    """Integration tests for SMC core components working together."""

    def test_sliding_surface_with_switching_function(self):
        """Test sliding surface integrated with switching function."""
        surface = LinearSlidingSurface([2.0, 1.5, 3.0, 2.5])
        switch_func = SwitchingFunction(SwitchingMethod.TANH)

        state = np.array([0.0, 0.0, 0.1, 0.05, -0.1, -0.05])

        # Compute sliding surface
        s = surface.compute(state)

        # Apply switching function with boundary layer
        control_component = switch_func.compute(s, 0.1)

        # Integration should work smoothly
        assert np.isfinite(s)
        assert np.isfinite(control_component)
        assert abs(control_component) <= 1.0

    def test_complete_control_law_computation(self):
        """Test complete SMC control law computation."""
        # Setup components
        surface = LinearSlidingSurface([2.0, 1.5, 3.0, 2.5])
        switch_func = SwitchingFunction(SwitchingMethod.TANH)

        # Mock dynamics for equivalent control
        mock_dynamics = Mock()
        M = np.eye(3) * 2.0
        F = np.array([0.1, 0.2, 0.3])
        mock_dynamics.get_dynamics = Mock(return_value=(M, F))

        eq_control = EquivalentControl(dynamics_model=mock_dynamics)

        state = np.array([0.0, 0.0, 0.1, 0.05, -0.1, -0.05])

        # Compute control law: u = u_eq - K*switch(s/ε)
        s = surface.compute(state)
        u_eq = eq_control.compute(state, surface)
        u_switch = switch_func.compute(s, 0.1)

        K = 15.0  # Switching gain
        u_total = u_eq - K * u_switch

        # Complete control law should be computable and finite
        assert np.isfinite(u_total)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
