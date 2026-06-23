"""
Unit tests for saturation functions (src/utils/control/primitives/saturation.py).

Tests cover:
- Normal operation for saturate(), smooth_sign(), dead_zone()
- Edge cases (boundary values, large inputs, overflow prevention)
- Error handling (invalid epsilon, threshold)
- Method variations (tanh vs linear)
- Scalar vs array inputs
"""

import numpy as np
import pytest
import warnings

from src.utils.control.primitives.saturation import saturate, smooth_sign, dead_zone


# ======================================================================================
# saturate() Tests
# ======================================================================================

class TestSaturateBasicOperation:
    """Test basic saturate() functionality."""

    def test_saturate_tanh_zero_input(self):
        """Should return 0 for sigma=0."""
        result = saturate(sigma=0.0, epsilon=0.1, method="tanh")
        assert result == pytest.approx(0.0, abs=1e-10)

    def test_saturate_tanh_positive_input(self):
        """Should return positive value for positive sigma."""
        result = saturate(sigma=0.05, epsilon=0.1, method="tanh")
        assert 0.0 < result < 1.0

    def test_saturate_tanh_negative_input(self):
        """Should return negative value for negative sigma."""
        result = saturate(sigma=-0.05, epsilon=0.1, method="tanh")
        assert -1.0 < result < 0.0

    def test_saturate_tanh_large_positive(self):
        """Should saturate to ~1.0 for large positive sigma."""
        result = saturate(sigma=10.0, epsilon=0.1, method="tanh")
        assert result == pytest.approx(1.0, abs=0.01)

    def test_saturate_tanh_large_negative(self):
        """Should saturate to ~-1.0 for large negative sigma."""
        result = saturate(sigma=-10.0, epsilon=0.1, method="tanh")
        assert result == pytest.approx(-1.0, abs=0.01)


class TestSaturateLinearMethod:
    """Test saturate() with linear method."""

    def test_saturate_linear_zero(self):
        """Should return 0 for sigma=0."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            result = saturate(sigma=0.0, epsilon=0.1, method="linear")
        assert result == 0.0

    def test_saturate_linear_within_boundary(self):
        """Should return sigma/epsilon within boundary."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            result = saturate(sigma=0.05, epsilon=0.1, method="linear")
        assert result == pytest.approx(0.5, abs=1e-10)

    def test_saturate_linear_clips_large_positive(self):
        """Should clip to 1.0 for large positive sigma."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            result = saturate(sigma=10.0, epsilon=0.1, method="linear")
        assert result == 1.0

    def test_saturate_linear_clips_large_negative(self):
        """Should clip to -1.0 for large negative sigma."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            result = saturate(sigma=-10.0, epsilon=0.1, method="linear")
        assert result == -1.0

    def test_saturate_linear_emits_warning(self):
        """Should emit RuntimeWarning for linear method."""
        with pytest.warns(RuntimeWarning, match="piecewise‑linear saturation"):
            saturate(sigma=0.1, epsilon=0.1, method="linear")


class TestSaturateArrayInputs:
    """Test saturate() with array inputs."""

    def test_saturate_array_tanh(self):
        """Should handle array inputs correctly."""
        sigma = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])
        result = saturate(sigma, epsilon=0.1, method="tanh")

        assert isinstance(result, np.ndarray)
        assert result.shape == sigma.shape
        assert result[2] == pytest.approx(0.0, abs=1e-10)  # sigma=0
        assert result[3] > 0.0  # sigma=0.5
        assert result[1] < 0.0  # sigma=-0.5

    def test_saturate_array_linear(self):
        """Should handle array inputs with linear method."""
        sigma = np.array([-10.0, -0.05, 0.0, 0.05, 10.0])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            result = saturate(sigma, epsilon=0.1, method="linear")

        assert isinstance(result, np.ndarray)
        assert result[0] == -1.0  # clipped
        assert result[1] == pytest.approx(-0.5, abs=1e-10)
        assert result[2] == 0.0
        assert result[3] == pytest.approx(0.5, abs=1e-10)
        assert result[4] == 1.0  # clipped


class TestSaturateSlopeParameter:
    """Test saturate() slope parameter effects."""

    def test_saturate_slope_affects_smoothness(self):
        """Higher slope should give gentler transition."""
        sigma = 0.1
        epsilon = 0.1

        result_steep = saturate(sigma, epsilon, method="tanh", slope=1.0)
        result_gentle = saturate(sigma, epsilon, method="tanh", slope=3.0)

        # With slope=3.0, transition should be gentler (closer to 0)
        assert abs(result_gentle) < abs(result_steep)

    def test_saturate_default_slope(self):
        """Should use slope=3.0 by default."""
        result_default = saturate(sigma=0.1, epsilon=0.1, method="tanh")
        result_explicit = saturate(sigma=0.1, epsilon=0.1, method="tanh", slope=3.0)

        assert result_default == pytest.approx(result_explicit, abs=1e-10)


class TestSaturateEdgeCases:
    """Test saturate() edge cases and numerical stability."""

    def test_saturate_very_large_sigma_no_overflow(self):
        """Should handle very large sigma without overflow."""
        result = saturate(sigma=1000.0, epsilon=0.01, method="tanh")
        assert np.isfinite(result)
        assert result == pytest.approx(1.0, abs=0.01)

    def test_saturate_very_small_epsilon(self):
        """Should handle very small epsilon."""
        result = saturate(sigma=0.001, epsilon=1e-6, method="tanh")
        assert np.isfinite(result)
        assert result == pytest.approx(1.0, abs=0.1)

    def test_saturate_extreme_slope(self):
        """Should handle extreme slope values."""
        # Very steep slope
        result_steep = saturate(sigma=0.1, epsilon=0.1, method="tanh", slope=0.1)
        assert np.isfinite(result_steep)

        # Very gentle slope
        result_gentle = saturate(sigma=0.1, epsilon=0.1, method="tanh", slope=10.0)
        assert np.isfinite(result_gentle)


class TestSaturateErrorHandling:
    """Test saturate() error handling."""

    def test_saturate_zero_epsilon_raises_error(self):
        """Should raise ValueError for epsilon=0."""
        with pytest.raises(ValueError, match="boundary layer epsilon must be positive"):
            saturate(sigma=0.1, epsilon=0.0, method="tanh")

    def test_saturate_negative_epsilon_raises_error(self):
        """Should raise ValueError for negative epsilon."""
        with pytest.raises(ValueError, match="boundary layer epsilon must be positive"):
            saturate(sigma=0.1, epsilon=-0.1, method="tanh")

    def test_saturate_invalid_method_raises_error(self):
        """Should raise ValueError for unknown method."""
        with pytest.raises(ValueError, match="unknown saturation method"):
            saturate(sigma=0.1, epsilon=0.1, method="invalid")


# ======================================================================================
# smooth_sign() Tests
# ======================================================================================

class TestSmoothSign:
    """Test smooth_sign() function."""

    def test_smooth_sign_zero(self):
        """Should return 0 for x=0."""
        result = smooth_sign(0.0)
        assert result == pytest.approx(0.0, abs=1e-10)

    def test_smooth_sign_positive(self):
        """Should return positive value for positive x."""
        result = smooth_sign(0.5)
        assert 0.0 < result < 1.0

    def test_smooth_sign_negative(self):
        """Should return negative value for negative x."""
        result = smooth_sign(-0.5)
        assert -1.0 < result < 0.0

    def test_smooth_sign_large_positive(self):
        """Should saturate to ~1.0 for large positive x."""
        result = smooth_sign(10.0)
        assert result == pytest.approx(1.0, abs=0.01)

    def test_smooth_sign_large_negative(self):
        """Should saturate to ~-1.0 for large negative x."""
        result = smooth_sign(-10.0)
        assert result == pytest.approx(-1.0, abs=0.01)

    def test_smooth_sign_custom_epsilon(self):
        """Should accept custom epsilon parameter."""
        result_small = smooth_sign(0.1, epsilon=0.01)
        result_large = smooth_sign(0.1, epsilon=0.1)

        # Smaller epsilon → steeper transition (larger result)
        assert abs(result_small) > abs(result_large)

    def test_smooth_sign_array_input(self):
        """Should handle array inputs."""
        x = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])
        result = smooth_sign(x, epsilon=0.1)

        assert isinstance(result, np.ndarray)
        assert result.shape == x.shape
        assert result[2] == pytest.approx(0.0, abs=1e-10)


# ======================================================================================
# dead_zone() Tests
# ======================================================================================

class TestDeadZoneBasicOperation:
    """Test basic dead_zone() functionality."""

    def test_dead_zone_below_threshold(self):
        """Should return 0 for signal below threshold."""
        result = dead_zone(x=0.05, threshold=0.1)
        assert result == 0.0

    def test_dead_zone_at_threshold(self):
        """Should return 0 at threshold boundary."""
        result = dead_zone(x=0.1, threshold=0.1)
        assert result == 0.0

    def test_dead_zone_above_threshold_positive(self):
        """Should return x - threshold for positive x > threshold."""
        result = dead_zone(x=0.5, threshold=0.1)
        assert result == pytest.approx(0.4, abs=1e-10)

    def test_dead_zone_above_threshold_negative(self):
        """Should return x + threshold for negative x < -threshold."""
        result = dead_zone(x=-0.5, threshold=0.1)
        assert result == pytest.approx(-0.4, abs=1e-10)

    def test_dead_zone_zero_input(self):
        """Should return 0 for x=0."""
        result = dead_zone(x=0.0, threshold=0.1)
        assert result == 0.0


class TestDeadZoneArrayInputs:
    """Test dead_zone() with array inputs."""

    def test_dead_zone_array(self):
        """Should handle array inputs correctly."""
        x = np.array([-0.5, -0.05, 0.0, 0.05, 0.5])
        result = dead_zone(x, threshold=0.1)

        assert isinstance(result, np.ndarray)
        assert result.shape == x.shape

        # Below threshold → 0
        assert result[1] == 0.0  # x=-0.05
        assert result[2] == 0.0  # x=0.0
        assert result[3] == 0.0  # x=0.05

        # Above threshold → x - threshold * sign(x)
        assert result[0] == pytest.approx(-0.4, abs=1e-10)  # x=-0.5
        assert result[4] == pytest.approx(0.4, abs=1e-10)   # x=0.5

    def test_dead_zone_preserves_scalar_type(self):
        """Should return scalar for scalar input."""
        result = dead_zone(x=0.5, threshold=0.1)
        assert np.isscalar(result) or isinstance(result, float)


class TestDeadZoneEdgeCases:
    """Test dead_zone() edge cases."""

    def test_dead_zone_very_small_threshold(self):
        """Should work with very small threshold."""
        result = dead_zone(x=0.001, threshold=1e-6)
        assert result == pytest.approx(0.001 - 1e-6, abs=1e-10)

    def test_dead_zone_large_signal(self):
        """Should handle large signals correctly."""
        result = dead_zone(x=100.0, threshold=0.1)
        assert result == pytest.approx(99.9, abs=1e-10)


class TestDeadZoneErrorHandling:
    """Test dead_zone() error handling."""

    def test_dead_zone_zero_threshold_raises_error(self):
        """Should raise ValueError for threshold=0."""
        with pytest.raises(ValueError, match="Dead zone threshold must be positive"):
            dead_zone(x=0.5, threshold=0.0)

    def test_dead_zone_negative_threshold_raises_error(self):
        """Should raise ValueError for negative threshold."""
        with pytest.raises(ValueError, match="Dead zone threshold must be positive"):
            dead_zone(x=0.5, threshold=-0.1)


# ======================================================================================
# Integration Tests
# ======================================================================================

class TestSaturationIntegration:
    """Integration tests across saturation functions."""

    def test_smooth_sign_uses_saturate(self):
        """smooth_sign should delegate to saturate with tanh method."""
        x = 0.5
        epsilon = 0.01

        result_smooth = smooth_sign(x, epsilon=epsilon)
        result_saturate = saturate(x, epsilon=epsilon, method="tanh")

        assert result_smooth == pytest.approx(result_saturate, abs=1e-10)

    def test_all_functions_handle_arrays(self):
        """All functions should handle array inputs consistently."""
        x = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])

        result_saturate = saturate(x, epsilon=0.1, method="tanh")
        result_smooth = smooth_sign(x, epsilon=0.1)
        result_deadzone = dead_zone(x, threshold=0.1)

        # All should return arrays
        assert isinstance(result_saturate, np.ndarray)
        assert isinstance(result_smooth, np.ndarray)
        assert isinstance(result_deadzone, np.ndarray)

        # All should have correct shape
        assert result_saturate.shape == x.shape
        assert result_smooth.shape == x.shape
        assert result_deadzone.shape == x.shape
