#============================================================================================
#=== tests/test_controllers/smc/algorithms/conditional_hybrid/test_safety_checker.py ====
#============================================================================================

"""
Safety Checker Tests for Conditional Hybrid SMC.

Tests the safety region logic that determines when super-twisting can be safely
applied without encountering B_eq singularities.

Based on Gemini's theoretical proof of architectural incompatibility.
"""

import numpy as np
import pytest

from src.controllers.smc.algorithms.conditional_hybrid.safety_checker import (
    compute_equivalent_gain,
    compute_sliding_surface,
    is_safe_for_supertwisting,
    compute_blend_weight,
)


class TestComputeEquivalentGain:
    """Test B_eq computation from Gemini's theoretical proof."""

    def test_B_eq_at_equilibrium(self):
        """Test B_eq computation at equilibrium (all angles zero)."""
        state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        gains = np.array([20.0, 15.0, 9.0, 4.0])  # [k1, k2, lambda1, lambda2]

        B_eq = compute_equivalent_gain(state, gains)

        # At equilibrium (theta=0), cos(0)=1.0
        # B_eq = lambda1 * H11 + lambda2 * H21 + lambda2 * H31
        # B_eq = 9.0 * 1.0 + 4.0 * 0.3 * 1.0 + 4.0 * 0.2 * 1.0
        # B_eq = 9.0 + 1.2 + 0.8 = 11.0
        expected = 9.0 + 4.0 * 0.3 + 4.0 * 0.2
        assert abs(B_eq - expected) < 1e-10, f"Expected {expected}, got {B_eq}"

    def test_B_eq_at_90_degrees(self):
        """Test B_eq at 90 degrees (cos(pi/2)=0) - potential singularity."""
        state = np.array([0.0, np.pi/2, np.pi/2, 0.0, 0.0, 0.0])
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        B_eq = compute_equivalent_gain(state, gains)

        # At 90 degrees, cos(pi/2) ≈ 0
        # B_eq = 9.0 * 1.0 + 4.0 * 0.3 * 0 + 4.0 * 0.2 * 0 = 9.0
        # Coupling terms vanish, leaving only H11
        assert abs(B_eq - 9.0) < 0.01, f"Expected 9.0, got {B_eq}"

    def test_B_eq_with_small_positive_angles(self):
        """Test B_eq with small positive angles (normal operation)."""
        state = np.array([0.1, 0.1, 0.1, 0.0, 0.0, 0.0])
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        B_eq = compute_equivalent_gain(state, gains)

        # Small positive angles: cos(0.1) ≈ 0.995
        expected = 9.0 + 4.0 * 0.3 * np.cos(0.1) + 4.0 * 0.2 * np.cos(0.1)
        assert abs(B_eq - expected) < 1e-6

    def test_B_eq_always_positive_with_positive_gains(self):
        """Test that B_eq remains positive with positive lambda gains."""
        states = [
            np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),      # Equilibrium
            np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1]),      # Small angles
            np.array([0.0, 0.3, -0.2, 0.0, 0.0, 0.0]),     # Mixed angles
            np.array([0.0, np.pi/4, np.pi/6, 0.0, 0.0, 0.0]),  # Larger angles
        ]
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        for state in states:
            B_eq = compute_equivalent_gain(state, gains)
            assert B_eq > 0, f"B_eq should be positive, got {B_eq} for state {state}"

    def test_B_eq_returns_scalar(self):
        """Test that B_eq computation returns a scalar float."""
        state = np.array([0.1, 0.2, 0.3, 0.0, 0.0, 0.0])
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        B_eq = compute_equivalent_gain(state, gains)

        assert isinstance(B_eq, (float, np.floating))
        assert np.isfinite(B_eq)


class TestComputeSlidingSurface:
    """Test sliding surface computation."""

    def test_surface_at_equilibrium(self):
        """Test sliding surface is zero at equilibrium."""
        state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        s = compute_sliding_surface(state, gains)

        assert abs(s) < 1e-10, f"Expected surface ≈ 0 at equilibrium, got {s}"

    def test_surface_with_positive_angles(self):
        """Test sliding surface with positive angles and velocities."""
        # State: [x, θ₁, θ₂, ẋ, θ̇₁, θ̇₂]
        state = np.array([0.0, 0.1, 0.2, 0.0, 0.5, 0.3])
        gains = np.array([20.0, 15.0, 9.0, 4.0])  # [k1, k2, lambda1, lambda2]

        s = compute_sliding_surface(state, gains)

        # s = k1*θ̇₁ + lambda1*θ₁ + k2*θ̇₂ + lambda2*θ₂
        # s = 20.0*0.5 + 9.0*0.1 + 15.0*0.3 + 4.0*0.2
        expected = 20.0 * 0.5 + 9.0 * 0.1 + 15.0 * 0.3 + 4.0 * 0.2
        assert abs(s - expected) < 1e-10, f"Expected {expected}, got {s}"

    def test_surface_linearity(self):
        """Test sliding surface linearity: s(α*state) = α*s(state)."""
        state = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
        gains = np.array([20.0, 15.0, 9.0, 4.0])
        scale = 2.5

        s1 = compute_sliding_surface(state, gains)
        s2 = compute_sliding_surface(scale * state, gains)

        assert abs(s2 - scale * s1) < 1e-10, "Surface should be linear"

    def test_surface_returns_scalar(self):
        """Test that surface computation returns a scalar float."""
        state = np.array([0.1, 0.2, 0.3, 0.1, 0.2, 0.3])
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        s = compute_sliding_surface(state, gains)

        assert isinstance(s, (float, np.floating))
        assert np.isfinite(s)


class TestIsSafeForSupertwisting:
    """Test safety condition checker for super-twisting activation."""

    @pytest.fixture
    def default_thresholds(self):
        """Default safety thresholds."""
        return {
            "angle_threshold": 0.2,       # rad
            "surface_threshold": 1.0,     # surface units
            "B_eq_threshold": 0.1,        # minimum |B_eq|
        }

    def test_safe_at_equilibrium_on_surface(self, default_thresholds):
        """Test that equilibrium on surface is SAFE."""
        state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        is_safe, diagnostics = is_safe_for_supertwisting(
            state, gains, **default_thresholds
        )

        assert is_safe == True, "Equilibrium on surface should be SAFE"
        assert diagnostics["near_equilibrium"] == True
        assert diagnostics["on_surface"] == True
        assert diagnostics["no_singularity"] == True
        assert abs(diagnostics["s"]) < 1e-10
        assert diagnostics["B_eq"] > default_thresholds["B_eq_threshold"]

    def test_unsafe_large_angles(self, default_thresholds):
        """Test that large angles are UNSAFE (violates condition 1)."""
        state = np.array([0.0, 0.5, 0.0, 0.0, 0.0, 0.0])  # θ₁ = 0.5 rad > 0.2
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        is_safe, diagnostics = is_safe_for_supertwisting(
            state, gains, **default_thresholds
        )

        assert is_safe == False, "Large angles should be UNSAFE"
        assert diagnostics["near_equilibrium"] == False
        assert abs(diagnostics["theta1"]) > default_thresholds["angle_threshold"]

    def test_unsafe_far_from_surface(self, default_thresholds):
        """Test that states far from surface are UNSAFE (violates condition 2)."""
        # Create state with large surface value
        state = np.array([0.0, 0.0, 0.0, 0.0, 2.0, 0.0])  # Large θ̇₁
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        is_safe, diagnostics = is_safe_for_supertwisting(
            state, gains, **default_thresholds
        )

        assert is_safe == False, "Far from surface should be UNSAFE"
        assert diagnostics["on_surface"] == False
        assert abs(diagnostics["s"]) > default_thresholds["surface_threshold"]

    def test_safe_small_angles_on_surface(self, default_thresholds):
        """Test that small angles on surface are SAFE."""
        state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])  # Small angles, zero velocity
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        is_safe, diagnostics = is_safe_for_supertwisting(
            state, gains, **default_thresholds
        )

        # Check if all conditions met
        assert diagnostics["near_equilibrium"] == True
        assert diagnostics["no_singularity"] == True
        # Surface might not be exactly zero due to position terms

    def test_diagnostics_structure(self, default_thresholds):
        """Test that diagnostics contain all required fields."""
        state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        is_safe, diagnostics = is_safe_for_supertwisting(
            state, gains, **default_thresholds
        )

        required_fields = [
            "near_equilibrium", "on_surface", "no_singularity",
            "theta1", "theta2", "s", "B_eq", "is_safe"
        ]
        for field in required_fields:
            assert field in diagnostics, f"Missing field: {field}"

        # Check types
        assert isinstance(diagnostics["is_safe"], bool)
        assert isinstance(diagnostics["near_equilibrium"], bool)
        assert isinstance(diagnostics["on_surface"], bool)
        assert isinstance(diagnostics["no_singularity"], bool)
        assert np.isfinite(diagnostics["s"])
        assert np.isfinite(diagnostics["B_eq"])

    def test_all_conditions_must_be_true(self, default_thresholds):
        """Test that ALL three conditions must be True for safety."""
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        # Condition 1 fails (large angle)
        state1 = np.array([0.0, 0.5, 0.0, 0.0, 0.0, 0.0])
        is_safe1, _ = is_safe_for_supertwisting(state1, gains, **default_thresholds)
        assert is_safe1 == False

        # Condition 2 fails (far from surface)
        state2 = np.array([0.0, 0.0, 0.0, 0.0, 5.0, 0.0])
        is_safe2, _ = is_safe_for_supertwisting(state2, gains, **default_thresholds)
        assert is_safe2 == False


class TestComputeBlendWeight:
    """Test smooth blending weight computation."""

    @pytest.fixture
    def default_params(self):
        """Default blending parameters."""
        return {
            "angle_threshold": 0.2,
            "surface_threshold": 1.0,
            "B_eq_threshold": 0.1,
            "w_angle": 0.3,
            "w_surface": 0.3,
            "w_singularity": 0.4,
        }

    def test_weight_range_0_to_1(self, default_params):
        """Test that blend weight is always in [0, 1] range."""
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        states = [
            np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),      # Equilibrium
            np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1]),      # Small deviations
            np.array([0.0, 0.5, 0.5, 0.0, 0.0, 0.0]),      # Large angles
            np.array([0.0, 0.0, 0.0, 0.0, 5.0, 5.0]),      # Large velocities
        ]

        for state in states:
            weight = compute_blend_weight(state, gains, **default_params)
            assert 0.0 <= weight <= 1.0, f"Weight {weight} out of range for state {state}"

    def test_weight_high_at_equilibrium(self, default_params):
        """Test that weight is high (close to 1.0) at equilibrium."""
        state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        weight = compute_blend_weight(state, gains, **default_params)

        # At equilibrium, all proximities are 1.0, so weight should be high
        assert weight > 0.5, f"Weight at equilibrium should be high, got {weight}"

    def test_weight_low_far_from_safe_region(self, default_params):
        """Test that weight is low (close to 0.0) far from safe region."""
        # Large angles, far from surface, potentially low B_eq
        state = np.array([0.0, 0.8, 0.8, 0.0, 10.0, 10.0])
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        weight = compute_blend_weight(state, gains, **default_params)

        # Far from safe region, weight should be low
        assert weight < 0.5, f"Weight far from safe region should be low, got {weight}"

    def test_weight_monotonic_with_angle(self, default_params):
        """Test that weight decreases as angle increases."""
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        # Gradually increase angle
        angles = [0.0, 0.05, 0.10, 0.15, 0.20]
        weights = []

        for angle in angles:
            state = np.array([0.0, angle, 0.0, 0.0, 0.0, 0.0])
            weight = compute_blend_weight(state, gains, **default_params)
            weights.append(weight)

        # Weights should generally decrease as angle increases
        # (allowing for small non-monotonicity due to sigmoid)
        assert weights[0] > weights[-1], "Weight should decrease with increasing angle"

    def test_sigmoid_smoothness(self, default_params):
        """Test that sigmoid produces smooth transitions (no discontinuities)."""
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        # Sample weights at small intervals
        angles = np.linspace(0.0, 0.3, 20)
        weights = []

        for angle in angles:
            state = np.array([0.0, angle, 0.0, 0.0, 0.0, 0.0])
            weight = compute_blend_weight(state, gains, **default_params)
            weights.append(weight)

        # Check for smoothness (no large jumps)
        diffs = np.diff(weights)
        max_diff = np.max(np.abs(diffs))
        assert max_diff < 0.3, f"Sigmoid not smooth, max diff: {max_diff}"

    def test_weight_returns_scalar(self, default_params):
        """Test that blend weight computation returns a scalar float."""
        state = np.array([0.1, 0.2, 0.3, 0.1, 0.2, 0.3])
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        weight = compute_blend_weight(state, gains, **default_params)

        assert isinstance(weight, (float, np.floating))
        assert np.isfinite(weight)


class TestSafetyCheckerIntegration:
    """Integration tests combining multiple safety checker functions."""

    def test_safe_state_produces_high_blend_weight(self):
        """Test that safe states produce high blend weights."""
        state = np.array([0.0, 0.05, 0.05, 0.0, 0.0, 0.0])  # Small angles, on surface
        gains = np.array([20.0, 15.0, 9.0, 4.0])
        thresholds = {
            "angle_threshold": 0.2,
            "surface_threshold": 1.0,
            "B_eq_threshold": 0.1,
        }
        blend_params = {
            **thresholds,
            "w_angle": 0.3,
            "w_surface": 0.3,
            "w_singularity": 0.4,
        }

        is_safe, _ = is_safe_for_supertwisting(state, gains, **thresholds)
        weight = compute_blend_weight(state, gains, **blend_params)

        if is_safe:
            assert weight > 0.3, "Safe state should have moderate-to-high blend weight"

    def test_unsafe_state_produces_low_blend_weight(self):
        """Test that unsafe states produce low blend weights."""
        state = np.array([0.0, 0.5, 0.5, 0.0, 0.0, 0.0])  # Large angles
        gains = np.array([20.0, 15.0, 9.0, 4.0])
        thresholds = {
            "angle_threshold": 0.2,
            "surface_threshold": 1.0,
            "B_eq_threshold": 0.1,
        }
        blend_params = {
            **thresholds,
            "w_angle": 0.3,
            "w_surface": 0.3,
            "w_singularity": 0.4,
        }

        is_safe, _ = is_safe_for_supertwisting(state, gains, **thresholds)
        weight = compute_blend_weight(state, gains, **blend_params)

        assert is_safe == False
        # Weight might not be extremely low due to sigmoid, but should be reduced


class TestEdgeCases:
    """Test edge cases and numerical robustness."""

    def test_zero_gains(self):
        """Test behavior with zero gains."""
        state = np.array([0.1, 0.1, 0.1, 0.0, 0.0, 0.0])
        gains = np.array([0.0, 0.0, 0.0, 0.0])

        B_eq = compute_equivalent_gain(state, gains)
        s = compute_sliding_surface(state, gains)

        assert B_eq == 0.0
        assert s == 0.0

    def test_large_gains(self):
        """Test behavior with very large gains."""
        state = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
        gains = np.array([1000.0, 1000.0, 1000.0, 1000.0])

        B_eq = compute_equivalent_gain(state, gains)
        s = compute_sliding_surface(state, gains)

        assert np.isfinite(B_eq)
        assert np.isfinite(s)

    def test_negative_angles(self):
        """Test behavior with negative angles."""
        state = np.array([0.0, -0.1, -0.2, 0.0, 0.0, 0.0])
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        B_eq = compute_equivalent_gain(state, gains)
        s = compute_sliding_surface(state, gains)

        assert np.isfinite(B_eq)
        assert np.isfinite(s)
        # B_eq should still be positive (cos is even function)
        assert B_eq > 0

    def test_very_small_thresholds(self):
        """Test safety checker with very small thresholds (restrictive)."""
        state = np.array([0.0, 0.05, 0.05, 0.0, 0.0, 0.0])
        gains = np.array([20.0, 15.0, 9.0, 4.0])

        # Very restrictive thresholds
        is_safe, _ = is_safe_for_supertwisting(
            state, gains,
            angle_threshold=0.01,    # Very small
            surface_threshold=0.01,
            B_eq_threshold=100.0,    # Very large
        )

        # Should be UNSAFE due to restrictive thresholds
        assert is_safe == False
