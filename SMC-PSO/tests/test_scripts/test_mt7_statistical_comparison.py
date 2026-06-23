import json
import math
from pathlib import Path

import numpy as np
import pytest

# Ensure scripts directory is importable
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
import sys

sys.path.insert(0, str(SCRIPTS_DIR))

import mt7_statistical_comparison as mt7_stat


# 1.1 Data Loading Tests -------------------------------------------------------
def test_load_summary_data_valid(tmp_path):
    payload = {
        "statistics": {"chattering_index": {"mean": 2.14, "std": 0.13}},
        "configuration": {"n_success": 100},
    }
    file_path = tmp_path / "summary.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = mt7_stat.load_summary_data(file_path)

    assert loaded == payload
    assert loaded["statistics"]["chattering_index"]["mean"] == pytest.approx(2.14)


def test_load_summary_data_missing_file():
    with pytest.raises(FileNotFoundError):
        mt7_stat.load_summary_data(Path("/nonexistent/path.json"))


def test_load_summary_data_invalid_json(tmp_path):
    bad_file = tmp_path / "broken.json"
    bad_file.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        mt7_stat.load_summary_data(bad_file)


# 1.2 Degradation Calculation Tests --------------------------------------------
def test_compute_degradation_50x_worse():
    ratio, percent = mt7_stat.compute_degradation(2.14, 107.61)

    assert ratio == pytest.approx(50.3, rel=0.1)
    assert percent == pytest.approx(4929.9, rel=1.0)


def test_compute_degradation_zero_baseline():
    ratio, percent = mt7_stat.compute_degradation(0.0, 107.61)

    assert ratio == float("inf")
    assert percent == float("inf")


def test_compute_degradation_improvement():
    ratio, percent = mt7_stat.compute_degradation(10.0, 7.0)

    assert ratio == pytest.approx(0.7)
    assert percent == pytest.approx(-30.0)


def test_compute_degradation_no_change():
    ratio, percent = mt7_stat.compute_degradation(5.0, 5.0)

    assert ratio == pytest.approx(1.0)
    assert percent == pytest.approx(0.0)


# 1.3 Statistical Test Execution -----------------------------------------------
def test_compare_metric_welch_t_test(monkeypatch):
    def fake_welch(mt6_vals, mt7_vals, alpha=0.05):
        # Verify the generated sample sizes match the requested counts
        assert len(mt6_vals) == 100
        assert len(mt7_vals) == 49
        return {
            "t_statistic": -131.22,
            "p_value": 0.0,
            "effect_size": -26.51,
            "reject_null_hypothesis": True,
        }

    monkeypatch.setattr(mt7_stat, "welch_t_test", fake_welch)

    mt6_stats = {"mean": 2.14, "std": 0.13}
    mt7_stats = {"mean": 107.61, "std": 5.48}

    result = mt7_stat.compare_metric("chattering_index", mt6_stats, mt7_stats, 100, 49)

    assert result.metric_name == "chattering_index"
    assert result.mt6_mean == pytest.approx(2.14)
    assert result.mt7_mean == pytest.approx(107.61)
    assert result.degradation_ratio == pytest.approx(50.3, rel=0.1)
    assert result.t_statistic == pytest.approx(-131.22)
    assert result.p_value < 1e-6
    assert result.cohens_d == pytest.approx(-26.51)
    assert result.significant is True


def test_compare_metric_confidence_intervals(monkeypatch):
    mock_result = {
        "t_statistic": -131.22,
        "p_value": 0.0,
        "effect_size": -26.51,
        "reject_null_hypothesis": True,
    }

    monkeypatch.setattr(mt7_stat, "welch_t_test", lambda *_args, **_kwargs: mock_result)

    mt6_stats = {"mean": 2.14, "std": 0.13}
    mt7_stats = {"mean": 107.61, "std": 5.48}

    result = mt7_stat.compare_metric("chattering_index", mt6_stats, mt7_stats, 100, 49)

    assert result.mt6_ci_lower == pytest.approx(2.14 - 1.96 * 0.13 / np.sqrt(100), rel=0.01)
    assert result.mt6_ci_upper == pytest.approx(2.14 + 1.96 * 0.13 / np.sqrt(100), rel=0.01)
    assert result.mt7_ci_lower == pytest.approx(107.61 - 1.96 * 5.48 / np.sqrt(49), rel=0.1)
    assert result.mt7_ci_upper == pytest.approx(107.61 + 1.96 * 5.48 / np.sqrt(49), rel=0.1)


def test_compare_metric_interpretation(monkeypatch):
    mock_result = {
        "t_statistic": -10.0,
        "p_value": 0.2,
        "effect_size": 0.1,
        "reject_null_hypothesis": False,
    }
    monkeypatch.setattr(mt7_stat, "welch_t_test", lambda *_args, **_kwargs: mock_result)

    mt6_stats = {"mean": 5.0, "std": 1.0}
    mt7_stats = {"mean": 5.5, "std": 1.2}

    result = mt7_stat.compare_metric("settling_time", mt6_stats, mt7_stats, 50, 50)

    assert "settling_time" in result.interpretation
    assert "not significant" in result.interpretation


# 1.4 Output Validation & Utilities -------------------------------------------
def test_interpret_comparison_highly_significant():
    interpretation = mt7_stat.interpret_comparison("chattering_index", 50.4, 0.0, -26.51)

    assert "chattering_index" in interpretation
    assert "50.4x worse" in interpretation
    assert "highly significant" in interpretation
    assert "very large effect" in interpretation


def test_interpret_comparison_not_significant():
    interpretation = mt7_stat.interpret_comparison("chattering_index", 1.5, 0.12, 0.15)

    assert "not significant" in interpretation
    assert "negligible effect" in interpretation


def test_convert_numpy_types():
    obj = {
        "scalar": np.float64(3.14),
        "bool": np.bool_(True),
        "array": np.array([1, 2, 3]),
        "nested": {"value": np.int32(42)},
    }

    converted = mt7_stat.convert_numpy_types(obj)

    assert isinstance(converted["scalar"], float)
    assert isinstance(converted["bool"], bool)
    assert isinstance(converted["array"], list)
    assert isinstance(converted["nested"]["value"], int)


# 1.5 Edge Cases ---------------------------------------------------------------
def test_compare_metric_missing_required_fields():
    mt6_stats = {"mean": 2.14}
    mt7_stats = {"mean": 107.61, "std": 5.48}

    with pytest.raises(KeyError):
        mt7_stat.compare_metric("chattering_index", mt6_stats, mt7_stats, 100, 49)


def test_compare_metric_zero_sample_size_handles(monkeypatch):
    mock_result = {
        "t_statistic": 0.0,
        "p_value": 1.0,
        "effect_size": 0.0,
        "reject_null_hypothesis": False,
    }
    monkeypatch.setattr(mt7_stat, "welch_t_test", lambda *_args, **_kwargs: mock_result)

    mt6_stats = {"mean": 2.14, "std": 0.13}
    mt7_stats = {"mean": 107.61, "std": 5.48}

    result = mt7_stat.compare_metric("chattering_index", mt6_stats, mt7_stats, 100, 0)

    assert math.isinf(result.mt7_ci_lower)
    assert math.isinf(result.mt7_ci_upper)
    assert result.significant is False


def test_compare_metric_sample_sizes_passed(monkeypatch):
    calls = {}

    def capturing_welch(mt6_vals, mt7_vals, alpha=0.05):
        calls["len_mt6"] = len(mt6_vals)
        calls["len_mt7"] = len(mt7_vals)
        return {
            "t_statistic": 1.0,
            "p_value": 0.04,
            "effect_size": 0.6,
            "reject_null_hypothesis": True,
        }

    monkeypatch.setattr(mt7_stat, "welch_t_test", capturing_welch)

    mt6_stats = {"mean": 10.0, "std": 2.0}
    mt7_stats = {"mean": 12.0, "std": 3.0}

    result = mt7_stat.compare_metric("overshoot", mt6_stats, mt7_stats, 80, 40)

    assert result.significant is True
    assert calls["len_mt6"] == 80
    assert calls["len_mt7"] == 40
