#======================================================================================
#======================== tests/test_utils/test_analysis.py ===========================
#======================================================================================

"""Tests for utils.analysis.statistics (M3 slice 5).

These tests exercise the real ship code, which imports scipy.stats. In the
project environment that is real SciPy; in the offline sandbox a minimal but
accurate scipy.stats shim is placed on sys.path by the test driver. Assertions
use textbook-known statistical values so the test validates the ship code
wiring (and, in the sandbox, the shim) independently.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from utils.analysis import (
    confidence_interval,
    bootstrap_confidence_interval,
    welch_t_test,
    one_way_anova,
    monte_carlo_analysis,
    performance_comparison_summary,
    sample_size_calculation,
)
import utils.analysis as analysis

# Textbook two-sided t critical value for 95% CI, df=9.
T_CRIT_975_DF9 = 2.2621571627409915


def test_confidence_interval_basic():
    data = np.arange(1.0, 11.0)  # 1..10, mean 5.5
    mean, half = confidence_interval(data, 0.95)
    assert np.isclose(mean, 5.5)
    s = float(np.std(data, ddof=1))
    expected_half = T_CRIT_975_DF9 * s / math.sqrt(10)
    assert np.isclose(half, expected_half, rtol=1e-3)


def test_confidence_interval_small_sample_nan():
    mean, half = confidence_interval(np.array([42.0]), 0.95)
    assert mean == 42.0
    assert math.isnan(half)


def test_bootstrap_confidence_interval_brackets_mean():
    np.random.seed(0)
    data = np.arange(1.0, 11.0)
    stat, (lo, hi) = bootstrap_confidence_interval(data, n_bootstrap=2000)
    assert np.isclose(stat, 5.5)
    assert lo < 5.5 < hi


def test_welch_t_test_no_reject_for_similar_groups():
    g1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    g2 = np.array([2.0, 3.0, 4.0, 5.0, 6.0])
    res = welch_t_test(g1, g2, alpha=0.05)
    assert np.isclose(res["mean_difference"], -1.0)
    assert res["reject_null_hypothesis"] is False
    assert 0.0 <= res["p_value"] <= 1.0


def test_welch_t_test_rejects_for_separated_groups():
    g1 = np.array([1.0, 1.0, 1.0, 2.0, 1.0])
    g2 = np.array([10.0, 11.0, 10.0, 12.0, 11.0])
    res = welch_t_test(g1, g2, alpha=0.05)
    assert res["reject_null_hypothesis"] is True
    assert res["p_value"] < 0.05
    assert res["t_statistic"] < 0


def test_welch_t_test_too_few_raises():
    with pytest.raises(ValueError):
        welch_t_test(np.array([1.0]), np.array([1.0, 2.0]))


def test_one_way_anova_rejects_separated_groups():
    groups = [
        np.array([1.0, 2.0, 3.0]),
        np.array([10.0, 11.0, 12.0]),
        np.array([20.0, 21.0, 22.0]),
    ]
    res = one_way_anova(groups, alpha=0.05)
    assert res["df_between"] == 2
    assert res["df_within"] == 6
    assert res["reject_null_hypothesis"] is True
    assert res["p_value"] < 0.05
    assert 0.0 <= res["eta_squared"] <= 1.0


def test_one_way_anova_requires_two_groups():
    with pytest.raises(ValueError):
        one_way_anova([np.array([1.0, 2.0])])


def test_one_way_anova_requires_min_two_obs():
    with pytest.raises(ValueError):
        one_way_anova([np.array([1.0]), np.array([2.0, 3.0])])


def test_monte_carlo_analysis_deterministic():
    res = monte_carlo_analysis(
        simulation_func=lambda x: x * 2.0,
        parameter_distributions={"x": lambda: 1.0},
        n_trials=10,
    )
    assert res["n_successful_trials"] == 10
    assert res["n_failed_trials"] == 0
    assert np.isclose(res["mean"], 2.0)
    assert np.isclose(res["std"], 0.0)
    assert np.isclose(res["confidence_interval"]["half_width"], 0.0)
    assert set(res["percentiles"].keys()) == {5, 25, 75, 95}


def test_monte_carlo_analysis_all_fail_raises():
    def boom(**kwargs):
        raise RuntimeError("nope")

    with pytest.raises(RuntimeError):
        monte_carlo_analysis(
            simulation_func=boom,
            parameter_distributions={"x": lambda: 1.0},
            n_trials=5,
        )


def test_performance_comparison_summary_three_controllers():
    np.random.seed(1)
    data = {
        "A": np.array([1.0, 2.0, 3.0, 2.5, 1.5]),
        "B": np.array([5.0, 6.0, 5.5, 4.5, 5.0]),
        "C": np.array([9.0, 10.0, 9.5, 8.5, 10.5]),
    }
    summary = performance_comparison_summary(data, metric_name="ISE")
    assert summary["metric_name"] == "ISE"
    assert set(summary["controllers"].keys()) == {"A", "B", "C"}
    assert len(summary["pairwise_comparisons"]) == 3
    assert summary["anova"] is not None
    assert summary["controllers"]["A"]["n_samples"] == 5


def test_performance_comparison_summary_two_controllers_no_anova():
    data = {
        "A": np.array([1.0, 2.0, 3.0]),
        "B": np.array([4.0, 5.0, 6.0]),
    }
    summary = performance_comparison_summary(data)
    assert len(summary["pairwise_comparisons"]) == 1
    assert summary["anova"] is None


def test_sample_size_t_test():
    n = sample_size_calculation(effect_size=0.5, power=0.8, alpha=0.05, test_type="t_test")
    assert n == 63


def test_sample_size_anova():
    n = sample_size_calculation(effect_size=0.5, power=0.8, alpha=0.05, test_type="anova")
    assert n == 76


def test_sample_size_unknown_type_raises():
    with pytest.raises(ValueError):
        sample_size_calculation(effect_size=0.5, test_type="chi_square")


def test_package_namespace_exposes_all():
    for name in (
        "confidence_interval",
        "bootstrap_confidence_interval",
        "welch_t_test",
        "one_way_anova",
        "monte_carlo_analysis",
        "performance_comparison_summary",
        "sample_size_calculation",
    ):
        assert hasattr(analysis, name)
