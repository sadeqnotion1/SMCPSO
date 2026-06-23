#======================================================================================\\
#========= tests/test_controllers/smc/core/test_property_based_invariants.py =========\\
#======================================================================================\\

"""
Property-Based Tests for SMC Core Invariants using Hypothesis.

SINGLE JOB: Validate mathematical invariants and properties that MUST hold
for ALL valid inputs, using property-based testing to explore edge cases.

Tests cover:
- Sliding surface: Finiteness, linearity, scaling properties
- Switching functions: Bounds, monotonicity, antisymmetry
- Gain validation: Positive-definiteness, stability criteria
- Equivalent control: Numerical stability, controllability
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, assume, settings
from hypothesis import HealthCheck

from src.controllers.smc.core.sliding_surface import LinearSlidingSurface
from src.controllers.smc.core.switching_functions import (
    SwitchingFunction,
    SwitchingMethod,
    tanh_switching,
    linear_switching
)
from src.controllers.smc.core.gain_validation import (
    SMCGainValidator,
    SMCControllerType
)


# Custom strategies for SMC testing
@st.composite
def positive_gains(draw, min_val=0.1, max_val=100.0, num_gains=4):
    """Generate strictly positive gains for SMC."""
    return [draw(st.floats(min_value=min_val, max_value=max_val)) for _ in range(num_gains)]


@st.composite
def bounded_state_vector(draw, min_angle=np.radians(-30), max_angle=np.radians(30),
                        min_vel=-5.0, max_vel=5.0):
    """Generate realistic state vectors for double-inverted pendulum."""
    # Use simpler strategy to avoid slow generation
    x = draw(st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False))
    x_dot = draw(st.floats(min_value=-3.0, max_value=3.0, allow_nan=False, allow_infinity=False))
    theta1 = draw(st.floats(min_value=min_angle, max_value=max_angle, allow_nan=False, allow_infinity=False))
    theta1_dot = draw(st.floats(min_value=min_vel, max_value=max_vel, allow_nan=False, allow_infinity=False))
    theta2 = draw(st.floats(min_value=min_angle, max_value=max_angle, allow_nan=False, allow_infinity=False))
    theta2_dot = draw(st.floats(min_value=min_vel, max_value=max_vel, allow_nan=False, allow_infinity=False))

    return np.array([x, x_dot, theta1, theta1_dot, theta2, theta2_dot])


@st.composite
def surface_value_and_epsilon(draw):
    """Generate sliding surface value and boundary layer thickness."""
    surface_value = draw(st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    epsilon = draw(st.floats(min_value=1e-6, max_value=10.0, allow_nan=False, allow_infinity=False))
    return surface_value, epsilon


@pytest.mark.property_based
class TestSlidingSurfaceInvariants:
    """Property-based tests for sliding surface mathematical invariants."""

    @given(
        gains=positive_gains(min_val=0.1, max_val=50.0, num_gains=4),
        state=bounded_state_vector()
    )
    @settings(max_examples=100, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_sliding_surface_always_finite(self, gains, state):
        """Property: Sliding surface must ALWAYS be finite for bounded states."""
        surface = LinearSlidingSurface(gains)

        s = surface.compute(state)

        # INVARIANT: s must be finite for any bounded state
        assert np.isfinite(s), f"Surface value {s} is not finite for state {state}"

    @given(
        gains=positive_gains(min_val=0.1, max_val=50.0, num_gains=4),
        state=bounded_state_vector(),
        scale=st.floats(min_value=0.1, max_value=10.0)
    )
    @settings(max_examples=50, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_sliding_surface_linearity(self, gains, state, scale):
        """Property: Sliding surface is LINEAR - s(α*x) = α*s(x)."""
        surface = LinearSlidingSurface(gains)

        s_original = surface.compute(state)
        s_scaled = surface.compute(scale * state)

        # INVARIANT: Linearity property s(α*x) = α*s(x)
        expected = scale * s_original

        # Allow small numerical tolerance
        if np.isfinite(s_original) and np.isfinite(s_scaled):
            assert np.isclose(s_scaled, expected, rtol=1e-5, atol=1e-8), \
                f"Linearity violated: s({scale}*x) = {s_scaled} != {scale}*s(x) = {expected}"

    @given(
        gains=positive_gains(min_val=0.1, max_val=50.0, num_gains=4),
        state1=bounded_state_vector(),
        state2=bounded_state_vector()
    )
    @settings(max_examples=50, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_sliding_surface_additivity(self, gains, state1, state2):
        """Property: Sliding surface is ADDITIVE - s(x1 + x2) = s(x1) + s(x2)."""
        surface = LinearSlidingSurface(gains)

        s1 = surface.compute(state1)
        s2 = surface.compute(state2)
        s_sum = surface.compute(state1 + state2)

        # INVARIANT: Additivity property s(x1 + x2) = s(x1) + s(x2)
        expected = s1 + s2

        if np.isfinite(s1) and np.isfinite(s2) and np.isfinite(s_sum):
            assert np.isclose(s_sum, expected, rtol=1e-5, atol=1e-8), \
                f"Additivity violated: s(x1+x2) = {s_sum} != s(x1)+s(x2) = {expected}"

    @given(
        gains=positive_gains(min_val=0.1, max_val=50.0, num_gains=4)
    )
    @settings(max_examples=50, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_sliding_surface_zero_at_equilibrium(self, gains):
        """Property: Sliding surface MUST be zero at equilibrium (all states zero)."""
        surface = LinearSlidingSurface(gains)

        equilibrium_state = np.zeros(6)
        s = surface.compute(equilibrium_state)

        # INVARIANT: s(0) = 0 (equilibrium property)
        assert np.isclose(s, 0.0, atol=1e-10), \
            f"Surface at equilibrium is {s}, expected 0.0"

    @given(
        gains=positive_gains(min_val=0.1, max_val=50.0, num_gains=4),
        state=bounded_state_vector()
    )
    @settings(max_examples=50, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_gains_positive_definiteness(self, gains, state):
        """Property: All gains MUST be strictly positive for stability."""
        # This is enforced at construction, but verify invariant holds
        surface = LinearSlidingSurface(gains)

        # INVARIANT: All gains > 0 (positive-definiteness for Lyapunov stability)
        assert surface.k1 > 0, f"k1 = {surface.k1} is not positive"
        assert surface.k2 > 0, f"k2 = {surface.k2} is not positive"
        assert surface.lam1 > 0, f"lambda1 = {surface.lam1} is not positive"
        assert surface.lam2 > 0, f"lambda2 = {surface.lam2} is not positive"


@pytest.mark.property_based
class TestSwitchingFunctionInvariants:
    """Property-based tests for switching function invariants."""

    @given(data=surface_value_and_epsilon())
    @settings(max_examples=200, deadline=1000, suppress_health_check=[HealthCheck.filter_too_much])
    def test_tanh_switching_bounded(self, data):
        """Property: Tanh switching function MUST be bounded in [-1, 1]."""
        surface_value, epsilon = data

        switch_func = SwitchingFunction(SwitchingMethod.TANH)
        result = switch_func.compute(surface_value, epsilon)

        # INVARIANT: Output ∈ [-1, 1]
        assert -1.0 <= result <= 1.0, \
            f"Tanh switching output {result} is outside [-1, 1] for s={surface_value}, ε={epsilon}"

    @given(data=surface_value_and_epsilon())
    @settings(max_examples=100, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_linear_switching_bounded(self, data):
        """Property: Linear switching function MUST be bounded in [-1, 1]."""
        surface_value, epsilon = data

        switch_func = SwitchingFunction(SwitchingMethod.LINEAR)
        result = switch_func.compute(surface_value, epsilon)

        # INVARIANT: Output ∈ [-1, 1]
        assert -1.0 <= result <= 1.0, \
            f"Linear switching output {result} is outside [-1, 1] for s={surface_value}, ε={epsilon}"

    @given(
        epsilon=st.floats(min_value=1e-6, max_value=10.0),
        s1=st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        s2=st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=50, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_switching_function_monotonicity(self, epsilon, s1, s2):
        """Property: Switching functions MUST be monotonically increasing."""
        assume(s1 < s2)  # Only test when s1 < s2

        switch_func = SwitchingFunction(SwitchingMethod.TANH)

        result1 = switch_func.compute(s1, epsilon)
        result2 = switch_func.compute(s2, epsilon)

        # INVARIANT: If s1 < s2, then switch(s1) <= switch(s2) (monotonicity)
        assert result1 <= result2, \
            f"Monotonicity violated: switch({s1}) = {result1} > switch({s2}) = {result2}"

    @given(
        surface_value=st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        epsilon=st.floats(min_value=1e-6, max_value=10.0)
    )
    @settings(max_examples=100, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_switching_function_antisymmetry(self, surface_value, epsilon):
        """Property: Switching functions MUST be antisymmetric - switch(-s) = -switch(s)."""
        switch_func = SwitchingFunction(SwitchingMethod.TANH)

        result_pos = switch_func.compute(surface_value, epsilon)
        result_neg = switch_func.compute(-surface_value, epsilon)

        # INVARIANT: Antisymmetry switch(-s) = -switch(s)
        assert np.isclose(result_neg, -result_pos, rtol=1e-6, atol=1e-8), \
            f"Antisymmetry violated: switch(-{surface_value}) = {result_neg} != -switch({surface_value}) = {-result_pos}"

    @given(
        epsilon=st.floats(min_value=1e-6, max_value=10.0)
    )
    @settings(max_examples=50, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_switching_function_zero_at_origin(self, epsilon):
        """Property: Switching function MUST be zero at s=0."""
        switch_func = SwitchingFunction(SwitchingMethod.TANH)

        result = switch_func.compute(0.0, epsilon)

        # INVARIANT: switch(0) = 0
        assert np.isclose(result, 0.0, atol=1e-10), \
            f"Switching function at origin is {result}, expected 0.0"

    @given(
        surface_value=st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        epsilon=st.floats(min_value=1e-3, max_value=10.0)  # Avoid very small epsilon
    )
    @settings(max_examples=100, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_switching_function_continuity(self, surface_value, epsilon):
        """Property: Switching functions MUST be continuous (no jumps)."""
        switch_func = SwitchingFunction(SwitchingMethod.TANH)

        # Sample nearby points - use adaptive delta based on epsilon
        # Use larger delta to avoid numerical precision issues
        delta = epsilon / 100.0  # 1% of epsilon
        s_left = surface_value - delta
        s_right = surface_value + delta

        result_center = switch_func.compute(surface_value, epsilon)
        result_left = switch_func.compute(s_left, epsilon)
        result_right = switch_func.compute(s_right, epsilon)

        # INVARIANT: Continuity - no large jumps
        # For tanh(3s/ε), max derivative is ~3/ε at s=0
        # Max change over distance delta is approximately (3/ε) * delta
        # Add 2x safety factor for numerical stability
        max_expected_change = (3.0 / epsilon) * delta * 2.0

        # Check for discontinuity (change much larger than expected from derivative)
        left_diff = abs(result_left - result_center)
        right_diff = abs(result_right - result_center)

        # Use tolerance to account for floating point precision
        tolerance = 1e-10
        assert left_diff <= max_expected_change + tolerance, \
            f"Discontinuity detected at s={surface_value}: " \
            f"left={result_left}, center={result_center}"
        assert right_diff <= max_expected_change + tolerance, \
            f"Discontinuity detected at s={surface_value}: " \
            f"right={result_right}, center={result_center}"


@pytest.mark.property_based
class TestGainValidationInvariants:
    """Property-based tests for gain validation invariants."""

    @given(
        k1=st.floats(min_value=0.1, max_value=50.0),
        k2=st.floats(min_value=0.1, max_value=50.0),
        lam1=st.floats(min_value=0.1, max_value=50.0),
        lam2=st.floats(min_value=0.1, max_value=50.0),
        K=st.floats(min_value=0.1, max_value=50.0),
        kd=st.floats(min_value=0.01, max_value=5.0)
    )
    @settings(max_examples=100, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_positive_gains_always_valid_classical(self, k1, k2, lam1, lam2, K, kd):
        """Property: Strictly positive gains MUST always be valid for classical SMC."""
        validator = SMCGainValidator()
        gains = [k1, k2, lam1, lam2, K, kd]

        result = validator.validate_gains(gains, SMCControllerType.CLASSICAL)

        # INVARIANT: All positive gains should pass validation
        assert result['valid'] is True, \
            f"Positive gains {gains} failed validation: {result}"

    @given(
        k1=st.floats(min_value=0.1, max_value=50.0),
        k2=st.floats(min_value=0.1, max_value=50.0),
        lam1=st.floats(min_value=0.1, max_value=50.0),
        lam2=st.floats(min_value=0.1, max_value=50.0),
        gamma=st.floats(min_value=0.01, max_value=10.0)  # Within adapter bounds
    )
    @settings(max_examples=100, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_positive_gains_always_valid_adaptive(self, k1, k2, lam1, lam2, gamma):
        """Property: Positive gains within bounds MUST always be valid for adaptive SMC."""
        validator = SMCGainValidator()
        gains = [k1, k2, lam1, lam2, gamma]

        result = validator.validate_gains(gains, SMCControllerType.ADAPTIVE)

        # INVARIANT: Positive gains within recommended range should pass
        assert result['valid'] is True, \
            f"Valid adaptive gains {gains} failed validation: {result}"

    @given(
        gains=st.lists(
            st.floats(min_value=-100.0, max_value=-0.01),  # Negative gains
            min_size=6,
            max_size=6
        )
    )
    @settings(max_examples=50, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_negative_gains_always_invalid(self, gains):
        """Property: Any negative gain MUST cause validation failure."""
        validator = SMCGainValidator()

        result = validator.validate_gains(gains, SMCControllerType.CLASSICAL)

        # INVARIANT: Negative gains violate Lyapunov stability
        assert result['valid'] is False, \
            f"Negative gains {gains} passed validation (should fail)"

    @given(
        num_gains=st.integers(min_value=1, max_value=5)  # Wrong number of gains
    )
    @settings(max_examples=30, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_wrong_length_always_invalid(self, num_gains):
        """Property: Wrong number of gains MUST cause validation failure."""
        validator = SMCGainValidator()
        gains = [1.0] * num_gains  # Classical needs exactly 6 gains

        result = validator.validate_gains(gains, SMCControllerType.CLASSICAL)

        # INVARIANT: Wrong length should always fail
        assert result['valid'] is False, \
            f"Wrong-length gains (n={num_gains}) passed validation (should fail)"


@pytest.mark.property_based
class TestControlOutputBounds:
    """Property-based tests for control output boundedness."""

    @given(
        gains=positive_gains(min_val=0.1, max_val=50.0, num_gains=4),
        state=bounded_state_vector(),
        K=st.floats(min_value=1.0, max_value=100.0),
        epsilon=st.floats(min_value=0.01, max_value=5.0)
    )
    @settings(max_examples=100, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_switching_control_bounded(self, gains, state, K, epsilon):
        """Property: Switching control component MUST be bounded by K."""
        surface = LinearSlidingSurface(gains)
        switch_func = SwitchingFunction(SwitchingMethod.TANH)

        # Compute sliding surface
        s = surface.compute(state)

        # Compute switching control: u_switch = K * switch(s/ε)
        switch_value = switch_func.compute(s, epsilon)
        u_switch = K * switch_value

        # INVARIANT: |u_switch| ≤ K (since |switch(·)| ≤ 1)
        assert abs(u_switch) <= K + 1e-10, \
            f"Switching control {u_switch} exceeds bound K={K} for s={s}, ε={epsilon}"

    @given(
        gains=positive_gains(min_val=0.1, max_val=50.0, num_gains=4),
        state=bounded_state_vector()
    )
    @settings(max_examples=50, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_lyapunov_function_nonnegative(self, gains, state):
        """Property: Lyapunov function V = 0.5*s² MUST be non-negative."""
        surface = LinearSlidingSurface(gains)

        s = surface.compute(state)
        V = 0.5 * s**2

        # INVARIANT: V ≥ 0 (positive semi-definiteness)
        assert V >= 0, f"Lyapunov function V = {V} is negative for state {state}"

    @given(
        gains=positive_gains(min_val=0.1, max_val=50.0, num_gains=4),
        state=bounded_state_vector()
    )
    @settings(max_examples=50, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_lyapunov_function_zero_only_at_equilibrium(self, gains, state):
        """Property: Lyapunov function V = 0 IFF at equilibrium."""
        surface = LinearSlidingSurface(gains)

        s = surface.compute(state)
        V = 0.5 * s**2

        # Extract relevant state components (angles and velocities)
        relevant_state = state[2:]  # [theta1, theta1_dot, theta2, theta2_dot]

        # INVARIANT: V = 0 iff state is at equilibrium
        # Use consistent tolerance for both checks to avoid edge cases
        equilibrium_tol = 1e-6  # Tolerance for state being at equilibrium
        V_zero_tol = 1e-12      # Tolerance for V being zero (much stricter)

        at_equilibrium = np.allclose(relevant_state, 0, atol=equilibrium_tol)
        V_is_zero = V < V_zero_tol

        if at_equilibrium:
            assert V_is_zero, f"At equilibrium but V = {V} != 0"
        else:
            # Away from equilibrium, V should be strictly positive
            # Allow for numerical precision: V might be very small but not exactly zero
            if V_is_zero:
                # Check if state is VERY close to equilibrium (stricter tolerance)
                very_close = np.allclose(relevant_state, 0, atol=1e-8)
                assert very_close, \
                    f"Away from equilibrium but V = {V} ≈ 0 (state: {relevant_state})"


@pytest.mark.property_based
class TestNumericalStabilityInvariants:
    """Property-based tests for numerical stability invariants."""

    @given(
        gains=positive_gains(min_val=1e-3, max_val=1e6, num_gains=4),  # Wide range
        state=bounded_state_vector()
    )
    @settings(max_examples=200, deadline=1000, suppress_health_check=[HealthCheck.filter_too_much])
    def test_sliding_surface_no_overflow(self, gains, state):
        """Property: Sliding surface MUST NOT overflow for reasonable inputs."""
        # Filter out extreme gain combinations that might cause issues
        assume(max(gains) / min(gains) < 1e4)  # Avoid extreme gain ratios

        surface = LinearSlidingSurface(gains)
        s = surface.compute(state)

        # INVARIANT: No overflow or underflow
        assert np.isfinite(s), \
            f"Sliding surface overflowed: s={s} for gains={gains}, state={state}"

    @given(
        surface_value=st.floats(min_value=1e-100, max_value=1e100, allow_nan=False, allow_infinity=False),
        epsilon=st.floats(min_value=1e-10, max_value=1e10, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=200, deadline=1000, suppress_health_check=[HealthCheck.filter_too_much])
    def test_switching_function_no_overflow(self, surface_value, epsilon):
        """Property: Switching functions MUST NOT overflow for extreme inputs."""
        switch_func = SwitchingFunction(SwitchingMethod.TANH)

        result = switch_func.compute(surface_value, epsilon)

        # INVARIANT: No overflow, result is finite and bounded
        assert np.isfinite(result), \
            f"Switching function overflowed: result={result} for s={surface_value}, ε={epsilon}"
        assert -1.0 <= result <= 1.0, \
            f"Switching function out of bounds: result={result}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
