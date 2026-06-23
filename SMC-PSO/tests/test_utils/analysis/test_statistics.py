"""
================================================================================
Tests for Statistical Analysis Module
================================================================================

Unit tests for src/utils/analysis/statistics.py

Tests cover:
1. Confidence intervals (Student's t and bootstrap)
2. Hypothesis testing (Welch's t-test, one-way ANOVA)
3. Monte Carlo analysis
4. Performance comparison utilities
5. Sample size calculations

Author: DIP_SMC_PSO Team
Created: December 21, 2025 (Week 3 Session 13)
"""

import numpy as np
import pytest
from scipy.stats import t, f, norm
from src.utils.analysis.statistics import (
    confidence_interval,
    bootstrap_confidence_interval,
    welch_t_test,
    one_way_anova,
    monte_carlo_analysis,
    performance_comparison_summary,
    sample_size_calculation,
)


# =============================================================================
# Test Confidence Interval (Student's t)
# =============================================================================

class TestConfidenceInterval:
    """Tests for confidence_interval function."""

    def test_normal_data_95_ci(self):
        """Test CI with normal distributed data at 95% confidence."""
        np.random.seed(42)
        data = np.random.normal(100, 10, 100)  # mean=100, std=10, n=100

        mean, half_width = confidence_interval(data, confidence=0.95)

        # Mean should be close to 100
        assert abs(mean - 100) < 5, f"Mean should be ~100, got {mean}"

        # Half-width should be positive
        assert half_width > 0, "Half-width should be positive"

        # Half-width should be reasonable (t * s / sqrt(n))
        # For n=100, s~10, t_95~2, half_width ~ 2
        assert 0.5 < half_width < 5, f"Half-width should be ~2, got {half_width}"

    def test_small_sample_wider_ci(self):
        """Small samples should have wider confidence intervals."""
        np.random.seed(42)

        # Small sample (n=5)
        small_data = np.random.normal(50, 10, 5)
        _, hw_small = confidence_interval(small_data, 0.95)

        # Large sample (n=100)
        large_data = np.random.normal(50, 10, 100)
        _, hw_large = confidence_interval(large_data, 0.95)

        # Small sample should have wider CI
        assert hw_small > hw_large, \
            f"Small sample CI ({hw_small}) should be wider than large ({hw_large})"

    def test_different_confidence_levels(self):
        """Higher confidence level should produce wider intervals."""
        np.random.seed(42)
        data = np.random.normal(100, 10, 50)

        # 90% CI
        _, hw_90 = confidence_interval(data, 0.90)

        # 95% CI
        _, hw_95 = confidence_interval(data, 0.95)

        # 99% CI
        _, hw_99 = confidence_interval(data, 0.99)

        # CI width should increase with confidence level
        assert hw_90 < hw_95 < hw_99, \
            f"CI width should increase: {hw_90} < {hw_95} < {hw_99}"

    def test_single_value_returns_nan_halfwidth(self):
        """Single value should return NaN for half-width."""
        data = np.array([42.0])

        mean, half_width = confidence_interval(data)

        assert mean == 42.0, "Mean should be the single value"
        assert np.isnan(half_width), "Half-width should be NaN for single value"

    def test_empty_array_returns_nan(self):
        """Empty array should return NaN for both mean and half-width."""
        data = np.array([])

        mean, half_width = confidence_interval(data)

        assert np.isnan(mean), "Mean should be NaN for empty array"
        assert np.isnan(half_width), "Half-width should be NaN for empty array"

    def test_constant_data_zero_halfwidth(self):
        """Constant data should have zero half-width (no variance)."""
        data = np.ones(100) * 5.0

        mean, half_width = confidence_interval(data)

        assert mean == 5.0, "Mean should be 5.0"
        assert half_width == 0.0, f"Half-width should be 0 for constant data, got {half_width}"

    def test_two_samples_valid_ci(self):
        """Two samples should produce valid CI."""
        data = np.array([10.0, 20.0])

        mean, half_width = confidence_interval(data, 0.95)

        assert mean == 15.0, "Mean should be 15.0"
        assert half_width > 0, "Half-width should be positive"
        # For n=2, df=1, t_95 ~ 12.7, s=7.07, hw ~ 63.5
        assert half_width > 10, "Half-width should be large for n=2"

    def test_return_types_are_floats(self):
        """Return values should be Python floats."""
        data = np.array([1, 2, 3, 4, 5])

        mean, half_width = confidence_interval(data)

        assert isinstance(mean, float), "Mean should be float"
        assert isinstance(half_width, float) or np.isnan(half_width), "Half-width should be float"


# =============================================================================
# Test Bootstrap Confidence Interval
# =============================================================================

class TestBootstrapConfidenceInterval:
    """Tests for bootstrap_confidence_interval function."""

    def test_bootstrap_mean_ci(self):
        """Bootstrap CI for mean should be reasonable."""
        np.random.seed(42)
        data = np.random.normal(100, 10, 50)

        stat, (lower, upper) = bootstrap_confidence_interval(
            data, statistic_func=np.mean, confidence=0.95, n_bootstrap=1000
        )

        # Statistic should be close to 100
        assert abs(stat - 100) < 5, f"Mean should be ~100, got {stat}"

        # CI should contain the statistic
        assert lower < stat < upper, "CI should contain the statistic"

        # CI should be reasonable width
        assert (upper - lower) < 20, f"CI width should be reasonable, got {upper - lower}"

    def test_bootstrap_median_ci(self):
        """Bootstrap CI for median."""
        np.random.seed(42)
        data = np.random.normal(100, 10, 50)

        stat, (lower, upper) = bootstrap_confidence_interval(
            data, statistic_func=np.median, confidence=0.95, n_bootstrap=1000
        )

        assert abs(stat - 100) < 5, f"Median should be ~100, got {stat}"
        assert lower < stat < upper, "CI should contain median"

    def test_bootstrap_reproducible_with_seed(self):
        """Bootstrap should be reproducible with seed."""
        data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        np.random.seed(123)
        stat1, (lower1, upper1) = bootstrap_confidence_interval(
            data, n_bootstrap=100
        )

        np.random.seed(123)
        stat2, (lower2, upper2) = bootstrap_confidence_interval(
            data, n_bootstrap=100
        )

        assert stat1 == stat2, "Statistics should match with same seed"
        assert abs(lower1 - lower2) < 0.01, "CI bounds should match with same seed"

    def test_bootstrap_90_narrower_than_99(self):
        """90% bootstrap CI should be narrower than 99% CI."""
        np.random.seed(42)
        data = np.random.normal(100, 10, 50)

        _, (lower_90, upper_90) = bootstrap_confidence_interval(
            data, confidence=0.90, n_bootstrap=1000
        )
        width_90 = upper_90 - lower_90

        _, (lower_99, upper_99) = bootstrap_confidence_interval(
            data, confidence=0.99, n_bootstrap=1000
        )
        width_99 = upper_99 - lower_99

        assert width_90 < width_99, \
            f"90% CI ({width_90}) should be narrower than 99% CI ({width_99})"


# =============================================================================
# Test Welch's T-Test
# =============================================================================

class TestWelchTTest:
    """Tests for welch_t_test function."""

    def test_identical_groups_no_difference(self):
        """Identical groups should not reject null hypothesis."""
        np.random.seed(42)
        group1 = np.random.normal(100, 10, 50)
        group2 = group1.copy()  # Identical

        result = welch_t_test(group1, group2, alpha=0.05)

        assert result['t_statistic'] == 0.0, "t-statistic should be 0 for identical groups"
        assert result['p_value'] > 0.05, "p-value should be >0.05 (fail to reject)"
        assert result['reject_null_hypothesis'] == False, "Should not reject null"
        assert result['mean_difference'] == 0.0, "Mean difference should be 0"

    def test_different_groups_reject_null(self):
        """Groups with different means should reject null hypothesis."""
        np.random.seed(42)
        group1 = np.random.normal(100, 10, 50)  # mean=100
        group2 = np.random.normal(120, 10, 50)  # mean=120 (large difference)

        result = welch_t_test(group1, group2, alpha=0.05)

        assert result['p_value'] < 0.05, "p-value should be <0.05 (reject null)"
        assert result['reject_null_hypothesis'] == True, "Should reject null"
        assert result['mean_difference'] < 0, "Group1 mean < Group2 mean"

    def test_unequal_variances_handled(self):
        """Welch's t-test should handle unequal variances."""
        np.random.seed(42)
        group1 = np.random.normal(100, 5, 50)   # std=5 (low variance)
        group2 = np.random.normal(100, 20, 50)  # std=20 (high variance)

        result = welch_t_test(group1, group2, alpha=0.05)

        # Same means, so should not reject (despite different variances)
        assert result['p_value'] > 0.05, "Should not reject with same means"
        assert result['reject_null_hypothesis'] == False

    def test_small_samples_error(self):
        """Groups with <2 samples should raise ValueError."""
        group1 = np.array([5.0])  # n=1
        group2 = np.array([6.0, 7.0])

        with pytest.raises(ValueError, match="at least 2 observations"):
            welch_t_test(group1, group2)

    def test_effect_size_calculation(self):
        """Effect size (Cohen's d) should be calculated."""
        np.random.seed(42)
        group1 = np.random.normal(100, 10, 50)
        group2 = np.random.normal(120, 10, 50)  # 2 std difference

        result = welch_t_test(group1, group2)

        # Effect size should be ~2.0 (20 / 10)
        assert 'effect_size' in result
        assert abs(result['effect_size']) > 1.5, "Effect size should be large"

    def test_result_keys_present(self):
        """Result should contain all expected keys."""
        group1 = np.array([1, 2, 3, 4, 5])
        group2 = np.array([6, 7, 8, 9, 10])

        result = welch_t_test(group1, group2)

        expected_keys = {
            't_statistic', 'p_value', 'degrees_of_freedom', 'alpha',
            'reject_null_hypothesis', 'mean_difference', 'effect_size'
        }
        assert set(result.keys()) == expected_keys


# =============================================================================
# Test One-Way ANOVA
# =============================================================================

class TestOneWayANOVA:
    """Tests for one_way_anova function."""

    def test_identical_groups_no_difference(self):
        """Identical groups should not reject null hypothesis."""
        np.random.seed(42)
        group1 = np.random.normal(100, 10, 20)
        group2 = group1.copy()
        group3 = group1.copy()

        result = one_way_anova([group1, group2, group3], alpha=0.05)

        assert result['F_statistic'] < 0.01, "F-statistic should be near 0"
        assert result['p_value'] > 0.05, "p-value should be >0.05"
        assert result['reject_null_hypothesis'] == False

    def test_different_groups_reject_null(self):
        """Groups with different means should reject null."""
        np.random.seed(42)
        group1 = np.random.normal(100, 10, 20)  # mean=100
        group2 = np.random.normal(120, 10, 20)  # mean=120
        group3 = np.random.normal(140, 10, 20)  # mean=140

        result = one_way_anova([group1, group2, group3], alpha=0.05)

        assert result['F_statistic'] > 1.0, "F-statistic should be large"
        assert result['p_value'] < 0.05, "p-value should be <0.05"
        assert result['reject_null_hypothesis'] == True

    def test_eta_squared_effect_size(self):
        """Eta-squared should be between 0 and 1."""
        np.random.seed(42)
        group1 = np.random.normal(100, 10, 20)
        group2 = np.random.normal(110, 10, 20)
        group3 = np.random.normal(120, 10, 20)

        result = one_way_anova([group1, group2, group3])

        assert 0 <= result['eta_squared'] <= 1, "Eta-squared should be in [0,1]"
        assert result['eta_squared'] > 0.1, "Eta-squared should be substantial"

    def test_degrees_of_freedom_calculation(self):
        """Degrees of freedom should be calculated correctly."""
        group1 = np.array([1, 2, 3, 4, 5])      # n=5
        group2 = np.array([6, 7, 8, 9, 10])     # n=5
        group3 = np.array([11, 12, 13, 14, 15]) # n=5

        result = one_way_anova([group1, group2, group3])

        # df_between = k-1 = 3-1 = 2
        assert result['df_between'] == 2

        # df_within = N-k = 15-3 = 12
        assert result['df_within'] == 12

    def test_single_group_error(self):
        """Single group should raise ValueError."""
        group1 = np.array([1, 2, 3, 4, 5])

        with pytest.raises(ValueError, match="at least 2 groups"):
            one_way_anova([group1])

    def test_small_group_error(self):
        """Group with <2 samples should raise ValueError."""
        group1 = np.array([1])  # n=1
        group2 = np.array([2, 3])

        with pytest.raises(ValueError, match="at least 2 observations"):
            one_way_anova([group1, group2])

    def test_result_keys_present(self):
        """Result should contain all expected keys."""
        group1 = np.array([1, 2, 3])
        group2 = np.array([4, 5, 6])

        result = one_way_anova([group1, group2])

        expected_keys = {
            'F_statistic', 'p_value', 'df_between', 'df_within', 'alpha',
            'reject_null_hypothesis', 'eta_squared', 'sum_squares_between',
            'sum_squares_within', 'mean_square_between', 'mean_square_within'
        }
        assert set(result.keys()) == expected_keys


# =============================================================================
# Test Monte Carlo Analysis
# =============================================================================

class TestMonteCarloAnalysis:
    """Tests for monte_carlo_analysis function."""

    def test_simple_simulation(self):
        """Monte Carlo with simple simulation function."""
        def sim_func(a, b):
            return a + b

        param_dists = {
            'a': lambda: np.random.uniform(0, 10),
            'b': lambda: np.random.uniform(0, 10),
        }

        result = monte_carlo_analysis(sim_func, param_dists, n_trials=100)

        # Mean should be around 10 (5 + 5)
        assert 8 < result['mean'] < 12, f"Mean should be ~10, got {result['mean']}"
        assert result['n_successful_trials'] == 100
        assert result['n_failed_trials'] == 0

    def test_failing_trials_handled(self):
        """Monte Carlo should handle failing trials."""
        call_count = [0]

        def failing_sim(x):
            call_count[0] += 1
            if call_count[0] % 3 == 0:  # Fail every 3rd trial
                raise RuntimeError("Simulated failure")
            return x ** 2

        param_dists = {'x': lambda: 5.0}

        with pytest.warns(UserWarning):
            result = monte_carlo_analysis(failing_sim, param_dists, n_trials=30)

        # Should have ~20 successful trials
        assert result['n_successful_trials'] < 30
        assert result['n_failed_trials'] > 0
        assert result['mean'] > 0

    def test_confidence_interval_in_results(self):
        """Result should contain confidence interval."""
        def sim_func(x):
            return x * 2

        param_dists = {'x': lambda: np.random.normal(10, 1)}

        result = monte_carlo_analysis(sim_func, param_dists, n_trials=100, confidence_level=0.95)

        assert 'confidence_interval' in result
        ci = result['confidence_interval']
        assert 'lower' in ci and 'upper' in ci
        assert ci['lower'] < result['mean'] < ci['upper']

    def test_percentiles_computed(self):
        """Result should contain percentiles."""
        def sim_func(x):
            return x

        param_dists = {'x': lambda: np.random.uniform(0, 100)}

        result = monte_carlo_analysis(sim_func, param_dists, n_trials=1000)

        assert 'percentiles' in result
        percs = result['percentiles']

        # Percentiles should be ordered
        assert percs[5] < percs[25] < percs[75] < percs[95]

        # For uniform[0, 100], p50 should be ~50
        median = result['median']
        assert 40 < median < 60


# =============================================================================
# Test Performance Comparison Summary
# =============================================================================

class TestPerformanceComparisonSummary:
    """Tests for performance_comparison_summary function."""

    def test_two_controllers_comparison(self):
        """Compare two controllers."""
        np.random.seed(42)
        results = {
            'Controller_A': np.random.normal(100, 10, 50),
            'Controller_B': np.random.normal(110, 10, 50),
        }

        summary = performance_comparison_summary(results)

        assert 'Controller_A' in summary['controllers']
        assert 'Controller_B' in summary['controllers']
        assert 'Controller_A_vs_Controller_B' in summary['pairwise_comparisons']
        assert summary['anova'] is None  # Only 2 controllers, no ANOVA

    def test_three_controllers_includes_anova(self):
        """Three controllers should trigger ANOVA."""
        np.random.seed(42)
        results = {
            'A': np.random.normal(100, 10, 30),
            'B': np.random.normal(110, 10, 30),
            'C': np.random.normal(120, 10, 30),
        }

        summary = performance_comparison_summary(results)

        assert summary['anova'] is not None, "ANOVA should be performed"
        assert 'F_statistic' in summary['anova']

    def test_pairwise_comparisons_count(self):
        """Number of pairwise comparisons should be C(n, 2)."""
        np.random.seed(42)
        results = {
            'A': np.random.normal(100, 10, 20),
            'B': np.random.normal(105, 10, 20),
            'C': np.random.normal(110, 10, 20),
            'D': np.random.normal(115, 10, 20),
        }

        summary = performance_comparison_summary(results)

        # 4 controllers → C(4,2) = 6 pairwise comparisons
        assert len(summary['pairwise_comparisons']) == 6

    def test_controller_statistics_present(self):
        """Each controller should have comprehensive statistics."""
        np.random.seed(42)
        results = {'Test': np.random.normal(100, 10, 50)}

        summary = performance_comparison_summary(results)

        stats = summary['controllers']['Test']
        expected_keys = {'n_samples', 'mean', 'std', 'median', 'confidence_interval', 'min', 'max'}
        assert set(stats.keys()) == expected_keys


# =============================================================================
# Test Sample Size Calculation
# =============================================================================

class TestSampleSizeCalculation:
    """Tests for sample_size_calculation function."""

    def test_large_effect_smaller_sample(self):
        """Larger effect size should require smaller sample."""
        n_small_effect = sample_size_calculation(effect_size=0.2, power=0.8, alpha=0.05)
        n_large_effect = sample_size_calculation(effect_size=0.8, power=0.8, alpha=0.05)

        assert n_large_effect < n_small_effect, \
            f"Large effect ({n_large_effect}) should need smaller sample than small effect ({n_small_effect})"

    def test_higher_power_larger_sample(self):
        """Higher power should require larger sample."""
        n_power_70 = sample_size_calculation(effect_size=0.5, power=0.7, alpha=0.05)
        n_power_90 = sample_size_calculation(effect_size=0.5, power=0.9, alpha=0.05)

        assert n_power_90 > n_power_70, \
            f"Higher power ({n_power_90}) should need larger sample than lower power ({n_power_70})"

    def test_smaller_alpha_larger_sample(self):
        """Smaller alpha (stricter test) should require larger sample."""
        n_alpha_05 = sample_size_calculation(effect_size=0.5, power=0.8, alpha=0.05)
        n_alpha_01 = sample_size_calculation(effect_size=0.5, power=0.8, alpha=0.01)

        assert n_alpha_01 > n_alpha_05, \
            f"Stricter alpha ({n_alpha_01}) should need larger sample than lenient alpha ({n_alpha_05})"

    def test_anova_larger_than_ttest(self):
        """ANOVA should require larger sample than t-test."""
        n_ttest = sample_size_calculation(effect_size=0.5, test_type='t_test')
        n_anova = sample_size_calculation(effect_size=0.5, test_type='anova')

        assert n_anova > n_ttest, \
            f"ANOVA ({n_anova}) should need larger sample than t-test ({n_ttest})"

    def test_return_type_is_int(self):
        """Sample size should be integer."""
        n = sample_size_calculation(effect_size=0.5)

        assert isinstance(n, int), "Sample size should be integer"
        assert n > 0, "Sample size should be positive"

    def test_unknown_test_type_error(self):
        """Unknown test type should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown test type"):
            sample_size_calculation(effect_size=0.5, test_type='chi_square')


# =============================================================================
# Edge Cases and Integration Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_small_effect_large_sample(self):
        """Very small effect size requires very large sample."""
        n = sample_size_calculation(effect_size=0.1, power=0.8, alpha=0.05)

        assert n > 100, "Small effect should require large sample"

    def test_confidence_interval_with_negative_data(self):
        """CI should work with negative data."""
        data = np.array([-5, -3, -1, 1, 3, 5])

        mean, half_width = confidence_interval(data)

        assert mean == 0.0, "Mean should be 0"
        assert half_width > 0, "Half-width should be positive"

    def test_welch_ttest_with_zero_variance(self):
        """Welch's t-test with zero variance in one group."""
        group1 = np.ones(10) * 5.0  # Zero variance
        group2 = np.random.normal(10, 2, 10)

        # Should not crash (scipy handles this)
        result = welch_t_test(group1, group2)

        assert 't_statistic' in result

    def test_anova_with_different_group_sizes(self):
        """ANOVA should handle unequal group sizes."""
        group1 = np.random.normal(100, 10, 10)  # n=10
        group2 = np.random.normal(105, 10, 20)  # n=20
        group3 = np.random.normal(110, 10, 30)  # n=30

        result = one_way_anova([group1, group2, group3])

        assert result['df_within'] == 60 - 3  # Total N=60, k=3


# =============================================================================
# Summary Test
# =============================================================================

def test_statistics_module_summary():
    """
    Summary test demonstrating statistics module usage.

    Validates all functions work together for control system analysis.
    """
    np.random.seed(42)

    # Simulate performance data for 3 controllers
    controller_results = {
        'Classical_SMC': np.random.normal(10.5, 1.5, 30),  # settling time (s)
        'STA_SMC': np.random.normal(9.2, 1.3, 30),
        'Adaptive_SMC': np.random.normal(8.8, 1.4, 30),
    }

    # Individual confidence intervals
    for name, data in controller_results.items():
        mean, hw = confidence_interval(data)
        assert hw > 0, f"{name} should have positive CI width"

    # Comprehensive comparison
    summary = performance_comparison_summary(controller_results, metric_name="Settling Time")

    assert len(summary['controllers']) == 3, "Should have 3 controllers"
    assert len(summary['pairwise_comparisons']) == 3, "Should have 3 pairwise comparisons (C(3,2))"
    assert summary['anova'] is not None, "Should perform ANOVA for 3 groups"

    # ANOVA should detect differences
    assert summary['anova']['reject_null_hypothesis'] == True, \
        "ANOVA should detect differences between controllers"

    # Sample size calculation for future experiments
    n_required = sample_size_calculation(effect_size=0.5, power=0.8, alpha=0.05)
    assert n_required > 0, "Sample size should be positive"

    print(f"[OK] Statistics Module Summary:")
    print(f"  Controllers compared: {len(controller_results)}")
    print(f"  ANOVA F-statistic: {summary['anova']['F_statistic']:.2f}")
    print(f"  ANOVA p-value: {summary['anova']['p_value']:.4f}")
    print(f"  Recommended sample size: {n_required}")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
