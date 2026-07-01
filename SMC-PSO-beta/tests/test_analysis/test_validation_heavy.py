"""M8-S3b regression tests for src/analysis/validation heavy-analysis modules.

Covers the honest-degrade contract (M8-S3b): the three fabricated hardcoded
p-values in ``statistical_tests.py`` (Anderson-Darling, ADF, KPSS) must now
report ``p_value = None`` and be flagged ``method == 'simplified'`` while their
real statistics/critical values are preserved. Also smoke/functional coverage
for benchmarking, cross_validation, and monte_carlo entry points.
"""
import numpy as np
import pytest

from src.analysis.validation.statistical_tests import (
    StatisticalTestSuite,
    StatisticalTestConfig,
    create_statistical_test_suite,
)
from src.analysis.validation.benchmarking import (
    BenchmarkSuite,
    create_benchmark_suite,
)
from src.analysis.validation.cross_validation import (
    CrossValidator,
    create_cross_validator,
    KFold,
    mean_squared_error,
    mean_absolute_error,
)
from src.analysis.validation.monte_carlo import (
    MonteCarloAnalyzer,
    create_monte_carlo_analyzer,
)


# --------------------------------------------------------------------------- #
# Honest-degrade contract (M8-S3b): fabricated p-values are nulled + flagged   #
# --------------------------------------------------------------------------- #
def test_adf_test_honest_degrade():
    """ADF returns real statistic/critical value but no fabricated p-value."""
    suite = StatisticalTestSuite()
    rng = np.random.RandomState(0)
    series = np.cumsum(rng.randn(120))  # random walk, non-constant
    result = suite._adf_test(series)
    assert "error" not in result, result
    assert result["p_value"] is None
    assert result["method"] == "simplified"
    assert isinstance(result["test_statistic"], float)
    assert "critical_value" in result
    assert result["conclusion"] in ("Stationary", "Non-stationary")


def test_kpss_test_honest_degrade():
    """KPSS returns real statistic/critical value but no fabricated p-value."""
    suite = StatisticalTestSuite()
    rng = np.random.RandomState(1)
    series = np.cumsum(rng.randn(120))
    result = suite._kpss_test(series)
    assert "error" not in result, result
    assert result["p_value"] is None
    assert result["method"] == "simplified"
    assert isinstance(result["test_statistic"], float)
    assert "critical_value" in result
    assert result["conclusion"] in ("Stationary", "Non-stationary")


def test_anderson_darling_honest_degrade():
    """Anderson-Darling keeps real statistic/critical value, nulls fake p-value."""
    suite = StatisticalTestSuite()
    rng = np.random.RandomState(2)
    data = rng.normal(0.0, 1.0, size=80)
    results = suite._perform_normality_tests(data)
    ad = results["anderson_darling"]
    assert "error" not in ad, ad
    assert ad["p_value"] is None
    assert ad["method"] == "simplified"
    assert isinstance(ad["statistic"], float)
    assert ad["critical_value"] is not None


def test_normality_real_pvalues_preserved():
    """Positive control: scipy-backed normality tests still report real p-values."""
    suite = StatisticalTestSuite()
    rng = np.random.RandomState(3)
    data = rng.normal(0.0, 1.0, size=80)
    results = suite._perform_normality_tests(data)
    sw = results["shapiro_wilk"]
    assert "error" not in sw, sw
    # Real scipy p-value: a float, never nulled, and NOT flagged simplified.
    assert isinstance(sw["p_value"], float)
    assert "method" not in sw


def test_only_the_three_sites_are_flagged_simplified():
    """Normality dict: exactly the Anderson-Darling entry is simplified-flagged."""
    suite = StatisticalTestSuite()
    rng = np.random.RandomState(4)
    data = rng.normal(0.0, 1.0, size=60)
    results = suite._perform_normality_tests(data)
    flagged = [k for k, v in results.items()
               if isinstance(v, dict) and v.get("method") == "simplified"]
    assert flagged == ["anderson_darling"], flagged


# --------------------------------------------------------------------------- #
# statistical_tests.py: factory + surface                                      #
# --------------------------------------------------------------------------- #
def test_statistical_suite_factory_and_methods():
    suite = create_statistical_test_suite()
    assert isinstance(suite, StatisticalTestSuite)
    assert "normality_tests" in suite.validation_methods
    assert "anderson" in StatisticalTestConfig().normality_tests


# --------------------------------------------------------------------------- #
# cross_validation.py                                                          #
# --------------------------------------------------------------------------- #
def test_kfold_split_partitions_all_indices():
    kf = KFold(n_splits=5, shuffle=False)
    X = np.arange(50)
    folds = list(kf.split(X))
    assert len(folds) == 5
    covered = np.concatenate([test_idx for _, test_idx in folds])
    assert sorted(covered.tolist()) == list(range(50))
    for train_idx, test_idx in folds:
        assert set(train_idx).isdisjoint(set(test_idx))


def test_mse_mae_basic():
    y_true = np.array([1.0, 2.0, 3.0])
    y_pred = np.array([1.0, 2.0, 5.0])
    assert mean_squared_error(y_true, y_pred) == pytest.approx(4.0 / 3.0)
    assert mean_absolute_error(y_true, y_pred) == pytest.approx(2.0 / 3.0)


def test_cross_validator_factory():
    cv = create_cross_validator()
    assert isinstance(cv, CrossValidator)
    assert isinstance(cv.validation_methods, list)


# --------------------------------------------------------------------------- #
# benchmarking.py                                                              #
# --------------------------------------------------------------------------- #
def test_benchmark_suite_factory():
    suite = create_benchmark_suite()
    assert isinstance(suite, BenchmarkSuite)
    assert isinstance(suite.validation_methods, list)


# --------------------------------------------------------------------------- #
# monte_carlo.py                                                               #
# --------------------------------------------------------------------------- #
def test_monte_carlo_factory_and_seed():
    analyzer = create_monte_carlo_analyzer()
    assert isinstance(analyzer, MonteCarloAnalyzer)
    assert isinstance(analyzer.validation_methods, list)


def test_monte_carlo_seed_is_reproducible():
    from src.analysis.validation.monte_carlo import MonteCarloConfig
    MonteCarloAnalyzer(MonteCarloConfig(random_seed=123))
    a = np.random.random(5)
    MonteCarloAnalyzer(MonteCarloConfig(random_seed=123))
    b = np.random.random(5)
    assert np.allclose(a, b)
