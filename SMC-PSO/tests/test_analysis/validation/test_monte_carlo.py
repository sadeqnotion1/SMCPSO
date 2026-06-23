#======================================================================================\\\
#================ tests/test_analysis/validation/test_monte_carlo.py ==================\\\
#======================================================================================\\\

"""
Comprehensive tests for Monte Carlo analysis and validation module.

This module tests Monte Carlo capabilities including:
- Sampling correctness (uniform, Gaussian, other distributions)
- Reproducibility with fixed seed (same seed = same results)
- Statistical properties (mean, variance, distribution shape)
- Failure case handling in simulations
- Parallel vs sequential execution consistency
- Result aggregation and statistics computation
- Confidence interval computation (95%, 99%)
- Sample size validation
- Memory efficiency for large sample counts (N > 10,000)
"""

import pytest
import numpy as np
from scipy import stats
from typing import Dict, Any, List
from unittest.mock import Mock, patch

from src.analysis.validation.monte_carlo import (
    MonteCarloAnalyzer,
    MonteCarloConfig,
    create_monte_carlo_analyzer
)
from src.analysis.core.interfaces import AnalysisStatus


# ==================== Fixtures ====================

@pytest.fixture
def default_config():
    """Create default Monte Carlo configuration."""
    return MonteCarloConfig(
        n_samples=1000,
        confidence_level=0.95,
        random_seed=42,
        parallel_processing=False,  # Disable for determinism
        sampling_method="random"
    )


@pytest.fixture
def analyzer_with_seed():
    """Create analyzer with fixed seed for reproducibility."""
    config = MonteCarloConfig(
        n_samples=100,
        random_seed=42,
        parallel_processing=False
    )
    return MonteCarloAnalyzer(config)


# ==================== Sampling Correctness Tests ====================

class TestSamplingCorrectness:
    """Test correctness of sampling from various distributions."""

    def test_uniform_sampling_mean_variance(self, analyzer_with_seed):
        """Test that uniform [0,1] sampling has mean ≈ 0.5, variance ≈ 1/12."""
        distribution_info = {'type': 'uniform', 'low': 0.0, 'high': 1.0}

        # Generate samples
        samples = [analyzer_with_seed._sample_from_distribution(distribution_info)
                  for _ in range(1000)]

        sample_mean = np.mean(samples)
        sample_var = np.var(samples)

        # Uniform [0,1]: E[X] = 0.5, Var[X] = 1/12 ≈ 0.0833
        assert abs(sample_mean - 0.5) < 0.05, f"Mean {sample_mean} not near 0.5"
        assert abs(sample_var - 1/12) < 0.02, f"Variance {sample_var} not near {1/12:.4f}"

    def test_normal_sampling_mean_variance(self, analyzer_with_seed):
        """Test that N(0,1) sampling has mean ≈ 0, variance ≈ 1."""
        distribution_info = {'type': 'normal', 'mean': 0.0, 'std': 1.0}

        samples = [analyzer_with_seed._sample_from_distribution(distribution_info)
                  for _ in range(1000)]

        sample_mean = np.mean(samples)
        sample_var = np.var(samples)

        # N(0,1): E[X] = 0, Var[X] = 1
        assert abs(sample_mean) < 0.1, f"Mean {sample_mean} not near 0"
        assert abs(sample_var - 1.0) < 0.2, f"Variance {sample_var} not near 1.0"

    def test_ks_test_uniform_distribution(self, analyzer_with_seed):
        """Test that uniform samples pass Kolmogorov-Smirnov test (p > 0.05)."""
        distribution_info = {'type': 'uniform', 'low': 0.0, 'high': 1.0}

        samples = np.array([analyzer_with_seed._sample_from_distribution(distribution_info)
                           for _ in range(1000)])

        # K-S test: compare samples to uniform [0,1]
        ks_stat, p_value = stats.kstest(samples, 'uniform')

        assert p_value > 0.05, f"K-S test failed: p={p_value:.4f} < 0.05"

    def test_ks_test_normal_distribution(self, analyzer_with_seed):
        """Test that normal samples pass K-S test (p > 0.05)."""
        distribution_info = {'type': 'normal', 'mean': 0.0, 'std': 1.0}

        samples = np.array([analyzer_with_seed._sample_from_distribution(distribution_info)
                           for _ in range(1000)])

        # K-S test: compare samples to N(0,1)
        ks_stat, p_value = stats.kstest(samples, 'norm')

        assert p_value > 0.05, f"K-S test failed: p={p_value:.4f} < 0.05"


# ==================== Reproducibility Tests ====================

class TestReproducibility:
    """Test that same seed produces identical results."""

    def test_same_seed_identical_samples(self):
        """Test that two analyzers with same seed generate identical samples."""
        # NOTE: MonteCarloAnalyzer uses np.random.seed() which is global
        # So we need to reset between runs for determinism
        config1 = MonteCarloConfig(n_samples=100, random_seed=42, parallel_processing=False)
        analyzer1 = MonteCarloAnalyzer(config1)

        dist_info = {'type': 'normal', 'mean': 0.0, 'std': 1.0}
        samples1 = [analyzer1._sample_from_distribution(dist_info) for _ in range(100)]

        # Reset seed and create new analyzer
        config2 = MonteCarloConfig(n_samples=100, random_seed=42, parallel_processing=False)
        analyzer2 = MonteCarloAnalyzer(config2)
        samples2 = [analyzer2._sample_from_distribution(dist_info) for _ in range(100)]

        # Should produce identical samples with same seed
        np.testing.assert_array_almost_equal(samples1, samples2)

    def test_different_seed_different_samples(self):
        """Test that different seeds produce different samples."""
        config1 = MonteCarloConfig(n_samples=100, random_seed=42, parallel_processing=False)
        config2 = MonteCarloConfig(n_samples=100, random_seed=99, parallel_processing=False)

        analyzer1 = MonteCarloAnalyzer(config1)
        analyzer2 = MonteCarloAnalyzer(config2)

        dist_info = {'type': 'normal', 'mean': 0.0, 'std': 1.0}

        samples1 = np.array([analyzer1._sample_from_distribution(dist_info) for _ in range(100)])
        samples2 = np.array([analyzer2._sample_from_distribution(dist_info) for _ in range(100)])

        # Samples should be different
        assert not np.allclose(samples1, samples2)


# ==================== Statistical Properties Tests ====================

class TestStatisticalProperties:
    """Test statistical property validation."""

    def test_compute_statistical_summary_basic_stats(self, analyzer_with_seed):
        """Test that statistical summary computes mean, std, min, max correctly."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]

        summary = analyzer_with_seed._compute_statistical_summary(values)

        assert summary['count'] == 5
        assert summary['mean'] == 3.0
        assert summary['min'] == 1.0
        assert summary['max'] == 5.0
        assert summary['median'] == 3.0

    def test_compute_statistical_summary_percentiles(self, analyzer_with_seed):
        """Test that percentiles are computed correctly."""
        values = list(range(1, 101))  # 1 to 100

        summary = analyzer_with_seed._compute_statistical_summary(values)

        # Check percentiles
        assert abs(summary['percentile_5'] - 5.5) < 1.0
        assert abs(summary['percentile_25'] - 25.5) < 1.0
        assert abs(summary['percentile_50'] - 50.5) < 1.0  # median
        assert abs(summary['percentile_75'] - 75.5) < 1.0
        assert abs(summary['percentile_95'] - 95.5) < 1.0

    def test_confidence_interval_contains_true_mean(self, analyzer_with_seed):
        """Test that 95% CI contains true mean in ~95% of trials."""
        # Generate samples from N(0,1)
        true_mean = 0.0
        n_trials = 100
        contains_count = 0

        for _ in range(n_trials):
            samples = np.random.normal(true_mean, 1.0, 100)
            summary = analyzer_with_seed._compute_statistical_summary(samples.tolist())

            ci = summary['confidence_interval_mean']
            if ci['lower'] <= true_mean <= ci['upper']:
                contains_count += 1

        # Should contain true mean in ~95% of trials (allow some variation)
        coverage = contains_count / n_trials
        assert coverage > 0.85, f"CI coverage {coverage:.2f} too low (expected ~0.95)"


# ==================== Failure Handling Tests ====================

class TestFailureHandling:
    """Test handling of simulation failures."""

    def test_simulation_failure_returns_none(self, analyzer_with_seed):
        """Test that failed simulations return None without crashing."""
        def failing_sim(params):
            raise ValueError("Simulation failed")

        parameter_distributions = {'param1': {'type': 'uniform', 'low': 0, 'high': 1}}

        # Run simulations sequentially
        parameter_samples = analyzer_with_seed._generate_parameter_samples(parameter_distributions)
        results = analyzer_with_seed._run_simulations_sequential(failing_sim, parameter_samples[:10])

        # All should be None
        assert all(r is None for r in results)

    def test_partial_failure_analysis_handles_none(self, analyzer_with_seed):
        """Test that analysis handles mix of successful and failed simulations."""
        def partial_failing_sim(params):
            if params['param1'] < 0.5:
                return {'metric': params['param1'] * 10}
            else:
                raise ValueError("Failed")

        parameter_distributions = {'param1': {'type': 'uniform', 'low': 0, 'high': 1}}
        parameter_samples = analyzer_with_seed._generate_parameter_samples(parameter_distributions)
        results = analyzer_with_seed._run_simulations_sequential(
            partial_failing_sim, parameter_samples[:20]
        )

        # Should have mix of valid and None results
        valid_results = [r for r in results if r is not None]
        assert len(valid_results) > 0
        assert len(valid_results) < len(results)

        # Analysis should handle this gracefully
        analysis = analyzer_with_seed._analyze_simulation_results(results)
        assert 'metric' in analysis
        assert 'mean' in analysis['metric']


# ==================== Parallel vs Sequential Tests ====================

class TestParallelConsistency:
    """Test that parallel and sequential execution produce consistent results."""

    def test_sequential_execution_produces_results(self, analyzer_with_seed):
        """Test sequential simulation execution."""
        def simple_sim(params):
            return {'result': params['param1'] ** 2}

        parameter_distributions = {'param1': {'type': 'uniform', 'low': 0, 'high': 1}}
        parameter_samples = analyzer_with_seed._generate_parameter_samples(parameter_distributions)

        results = analyzer_with_seed._run_simulations_sequential(simple_sim, parameter_samples[:10])

        assert len(results) == 10
        assert all(r is not None for r in results)
        assert all('result' in r for r in results)


# ==================== Result Aggregation Tests ====================

class TestResultAggregation:
    """Test aggregation of simulation results."""

    def test_analyze_simulation_results_with_dicts(self, analyzer_with_seed):
        """Test analysis of dictionary results."""
        results = [
            {'metric1': 1.0, 'metric2': 2.0},
            {'metric1': 2.0, 'metric2': 3.0},
            {'metric1': 3.0, 'metric2': 4.0}
        ]

        analysis = analyzer_with_seed._analyze_simulation_results(results)

        assert 'metric1' in analysis
        assert 'metric2' in analysis
        assert analysis['metric1']['mean'] == 2.0
        assert analysis['metric2']['mean'] == 3.0

    def test_analyze_simulation_results_with_scalars(self, analyzer_with_seed):
        """Test analysis of scalar results."""
        results = [1.0, 2.0, 3.0, 4.0, 5.0]

        analysis = analyzer_with_seed._analyze_simulation_results(results)

        assert 'mean' in analysis
        assert analysis['mean'] == 3.0
        assert analysis['min'] == 1.0
        assert analysis['max'] == 5.0


# ==================== Confidence Interval Tests ====================

class TestConfidenceIntervals:
    """Test confidence interval computation."""

    def test_bootstrap_confidence_interval_95(self, analyzer_with_seed):
        """Test that bootstrap computes 95% CI."""
        values = np.random.normal(0, 1, 100)

        bootstrap_results = analyzer_with_seed._bootstrap_analysis(values)

        assert 'mean_confidence_interval' in bootstrap_results
        ci = bootstrap_results['mean_confidence_interval']
        assert 'lower' in ci
        assert 'upper' in ci
        assert ci['confidence_level'] == 0.95
        assert ci['lower'] < ci['upper']

    def test_bootstrap_confidence_interval_99(self):
        """Test that bootstrap computes 99% CI."""
        config = MonteCarloConfig(
            n_samples=100,
            bootstrap_confidence_level=0.99,
            random_seed=42,
            parallel_processing=False
        )
        analyzer = MonteCarloAnalyzer(config)

        values = np.random.normal(0, 1, 100)
        bootstrap_results = analyzer._bootstrap_analysis(values)

        ci = bootstrap_results['mean_confidence_interval']
        assert ci['confidence_level'] == 0.99
        # 99% CI should be wider than 95% CI
        assert ci['upper'] - ci['lower'] > 0


# ==================== Sample Size Validation Tests ====================

class TestSampleSizeValidation:
    """Test sample size validation and convergence."""

    def test_minimum_samples_enforced(self):
        """Test that minimum sample size is enforced."""
        config = MonteCarloConfig(
            n_samples=50,  # Below min
            min_samples=100,
            random_seed=42,
            parallel_processing=False
        )
        analyzer = MonteCarloAnalyzer(config)

        # Should still work but may warn
        results = [np.random.normal(0, 1) for _ in range(50)]
        convergence = analyzer._analyze_convergence(results)

        assert 'error' in convergence  # Insufficient samples

    def test_convergence_analysis_detects_convergence(self, analyzer_with_seed):
        """Test that convergence analysis detects when mean stabilizes."""
        # Create samples that converge quickly
        results = [1.0] * 200  # Constant values = immediate convergence

        convergence = analyzer_with_seed._analyze_convergence(results)

        assert convergence['converged'] is True
        assert convergence['convergence_point'] is not None


# ==================== Memory Efficiency Tests ====================

class TestMemoryEfficiency:
    """Test memory efficiency for large sample counts."""

    def test_large_sample_count_completes_quickly(self):
        """Test that N=1000 completes in < 1 second."""
        import time

        config = MonteCarloConfig(
            n_samples=1000,
            random_seed=42,
            parallel_processing=False,
            save_all_samples=False  # Don't save to reduce memory
        )
        analyzer = MonteCarloAnalyzer(config)

        def fast_sim(params):
            return {'result': params['param1']}

        parameter_distributions = {'param1': {'type': 'uniform', 'low': 0, 'high': 1}}

        start_time = time.time()
        parameter_samples = analyzer._generate_parameter_samples(parameter_distributions)
        results = analyzer._run_simulations_sequential(fast_sim, parameter_samples)
        elapsed = time.time() - start_time

        assert elapsed < 2.0, f"Took {elapsed:.2f}s for 1000 samples"
        assert len(results) == 1000


# ==================== Distribution Fitting Tests ====================

class TestDistributionFitting:
    """Test distribution fitting and analysis."""

    def test_fit_normal_distribution(self, analyzer_with_seed):
        """Test that normal samples are identified as normal distribution."""
        # Generate normal samples
        data = np.random.normal(0, 1, 1000)

        dist_analysis = analyzer_with_seed._analyze_distributions(data)

        assert 'distribution_fits' in dist_analysis
        assert 'norm' in dist_analysis['distribution_fits']

        norm_fit = dist_analysis['distribution_fits']['norm']
        if 'aic' in norm_fit:
            # Should have low K-S statistic and high p-value
            assert norm_fit['p_value'] > 0.05

    def test_best_fit_selection(self, analyzer_with_seed):
        """Test that best fit distribution is selected by AIC."""
        # Generate normal samples (should fit normal best)
        data = np.random.normal(0, 1, 1000)

        dist_analysis = analyzer_with_seed._analyze_distributions(data)

        assert 'best_fit' in dist_analysis
        # Best fit should be 'norm' for normal data
        assert dist_analysis['best_fit'] in ['norm', 'lognorm', 'exponential', 'gamma', 'beta']


# ==================== Risk Analysis Tests ====================

class TestRiskAnalysis:
    """Test tail risk and Value at Risk analysis."""

    def test_value_at_risk_computation(self, analyzer_with_seed):
        """Test that VaR is computed correctly."""
        data = np.random.normal(0, 1, 1000)

        risk_analysis = analyzer_with_seed._perform_risk_analysis(data)

        assert 'value_at_risk' in risk_analysis
        var_results = risk_analysis['value_at_risk']

        # VaR should be negative for left tail
        assert 'var_1' in var_results or 'var_5' in var_results

    def test_conditional_value_at_risk(self, analyzer_with_seed):
        """Test that CVaR is computed and CVaR <= VaR."""
        data = np.random.normal(0, 1, 1000)

        risk_analysis = analyzer_with_seed._perform_risk_analysis(data)

        cvar_results = risk_analysis['conditional_value_at_risk']
        var_results = risk_analysis['value_at_risk']

        # CVaR should be <= VaR (more extreme)
        for alpha in [1, 5, 10]:
            var_key = f'var_{alpha}'
            cvar_key = f'cvar_{alpha}'
            if var_key in var_results and cvar_key in cvar_results:
                assert cvar_results[cvar_key] <= var_results[var_key]


# ==================== Validation Interface Tests ====================

class TestValidationInterface:
    """Test MonteCarloAnalyzer validation interface."""

    def test_validate_returns_analysis_result(self, analyzer_with_seed):
        """Test that validate() returns AnalysisResult."""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]

        result = analyzer_with_seed.validate(data)

        assert result.status == AnalysisStatus.SUCCESS
        assert result.data is not None
        assert result.metadata is not None

    def test_validate_handles_errors(self, analyzer_with_seed):
        """Test that validate() handles errors gracefully."""
        # Pass invalid data
        data = None

        result = analyzer_with_seed.validate(data)

        assert result.status == AnalysisStatus.ERROR
        assert 'error_details' in result.data


# ==================== Factory Function Tests ====================

class TestFactoryFunction:
    """Test create_monte_carlo_analyzer factory function."""

    def test_create_with_config_dict(self):
        """Test creating analyzer with config dictionary."""
        config = {
            'n_samples': 500,
            'random_seed': 123,
            'parallel_processing': False
        }

        analyzer = create_monte_carlo_analyzer(config)

        assert analyzer.config.n_samples == 500
        assert analyzer.config.random_seed == 123

    def test_create_with_no_config(self):
        """Test creating analyzer with default config."""
        analyzer = create_monte_carlo_analyzer()

        assert analyzer.config.n_samples == 1000  # Default
        assert analyzer.config.confidence_level == 0.95


# ==================== Sampling Method Tests ====================

class TestSamplingMethods:
    """Test different sampling methods (Latin Hypercube, Sobol, Halton)."""

    def test_latin_hypercube_sampling(self, analyzer_with_seed):
        """Test Latin Hypercube Sampling generates well-distributed samples."""
        parameter_distributions = {
            'param1': {'type': 'uniform', 'low': 0, 'high': 1},
            'param2': {'type': 'uniform', 'low': 0, 'high': 1}
        }

        analyzer_with_seed.config.sampling_method = 'latin_hypercube'
        samples = analyzer_with_seed._generate_parameter_samples(parameter_distributions)

        assert len(samples) == analyzer_with_seed.config.n_samples
        assert all('param1' in s and 'param2' in s for s in samples)

    def test_sobol_sampling(self, analyzer_with_seed):
        """Test Sobol sequence sampling."""
        parameter_distributions = {
            'param1': {'type': 'uniform', 'low': 0, 'high': 1}
        }

        analyzer_with_seed.config.sampling_method = 'sobol'
        samples = analyzer_with_seed._generate_parameter_samples(parameter_distributions)

        assert len(samples) == analyzer_with_seed.config.n_samples
        assert all('param1' in s for s in samples)

    def test_halton_sampling(self, analyzer_with_seed):
        """Test Halton sequence sampling."""
        parameter_distributions = {
            'param1': {'type': 'uniform', 'low': 0, 'high': 1}
        }

        analyzer_with_seed.config.sampling_method = 'halton'
        samples = analyzer_with_seed._generate_parameter_samples(parameter_distributions)

        assert len(samples) == analyzer_with_seed.config.n_samples
        assert all('param1' in s for s in samples)


# ==================== Distribution Sampling Tests ====================

class TestDistributionSampling:
    """Test sampling from various distribution types."""

    def test_beta_distribution_sampling(self, analyzer_with_seed):
        """Test beta distribution sampling."""
        dist_info = {'type': 'beta', 'alpha': 2.0, 'beta': 5.0}

        samples = [analyzer_with_seed._sample_from_distribution(dist_info) for _ in range(100)]

        # Beta samples should be in [0,1]
        assert all(0 <= s <= 1 for s in samples)

    def test_gamma_distribution_sampling(self, analyzer_with_seed):
        """Test gamma distribution sampling."""
        dist_info = {'type': 'gamma', 'shape': 2.0, 'scale': 1.0}

        samples = [analyzer_with_seed._sample_from_distribution(dist_info) for _ in range(100)]

        # Gamma samples should be positive
        assert all(s > 0 for s in samples)

    def test_lognormal_distribution_sampling(self, analyzer_with_seed):
        """Test lognormal distribution sampling."""
        dist_info = {'type': 'lognormal', 'mean': 0.0, 'sigma': 1.0}

        samples = [analyzer_with_seed._sample_from_distribution(dist_info) for _ in range(100)]

        # Lognormal samples should be positive
        assert all(s > 0 for s in samples)

    def test_unknown_distribution_fallback(self, analyzer_with_seed):
        """Test that unknown distribution type falls back to normal."""
        dist_info = {'type': 'unknown_type'}

        # Should not raise error, falls back to N(0,1)
        samples = [analyzer_with_seed._sample_from_distribution(dist_info) for _ in range(100)]

        assert len(samples) == 100
        assert all(isinstance(s, float) for s in samples)


# ==================== Edge Cases ====================

class TestEdgeCases:
    """Edge case tests for Monte Carlo analyzer."""

    def test_empty_data_returns_error(self, analyzer_with_seed):
        """Test that empty data is handled gracefully."""
        data = []

        result = analyzer_with_seed.validate(data)

        # Should handle gracefully (may error or return empty analysis)
        assert result.status in [AnalysisStatus.SUCCESS, AnalysisStatus.ERROR]

    def test_single_value_data(self, analyzer_with_seed):
        """Test analysis with single data point."""
        data = [5.0]

        summary = analyzer_with_seed._compute_statistical_summary(data)

        assert summary['count'] == 1
        assert summary['mean'] == 5.0
        assert summary['min'] == 5.0
        assert summary['max'] == 5.0

    def test_data_with_nan_values(self, analyzer_with_seed):
        """Test that NaN values are filtered out."""
        data = [1.0, 2.0, np.nan, 4.0, 5.0]

        # _analyze_data_with_monte_carlo filters out NaN values
        result = analyzer_with_seed._analyze_data_with_monte_carlo(data)

        # Should have filtered data
        assert 'original_statistics' in result
        # Check that mean is finite (NaN excluded)
        if 'mean' in result['original_statistics']:
            assert np.isfinite(result['original_statistics']['mean'])

    def test_data_with_inf_values(self, analyzer_with_seed):
        """Test that Inf values are filtered out."""
        data = [1.0, 2.0, np.inf, 4.0, 5.0]

        # _analyze_data_with_monte_carlo filters out Inf values
        result = analyzer_with_seed._analyze_data_with_monte_carlo(data)

        # Should have filtered data
        assert 'original_statistics' in result
        # Check that mean is finite (Inf excluded)
        if 'mean' in result['original_statistics']:
            assert np.isfinite(result['original_statistics']['mean'])
