import json
from pathlib import Path

import pytest

import mt6_statistical_comparison as mt6_stat


def test_load_summary_data(tmp_path):
    payload = {"metric": {"mean": 1.23}}
    file_path = tmp_path / "summary.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = mt6_stat.load_summary_data(file_path)

    assert loaded == payload


def test_compute_improvement_lower_is_better():
    percent, absolute = mt6_stat.compute_improvement(10.0, 7.0, lower_is_better=True)

    assert percent == pytest.approx(30.0)
    assert absolute == pytest.approx(3.0)


def test_compute_improvement_higher_is_better():
    percent, absolute = mt6_stat.compute_improvement(10.0, 12.0, lower_is_better=False)

    assert percent == pytest.approx(20.0)
    assert absolute == pytest.approx(-2.0)


def test_interpret_comparison_includes_context():
    message = mt6_stat.interpret_comparison(
        "chattering_index",
        improvement_pct=35.0,
        p_value=0.004,
        cohens_d=-0.9,
    )

    assert "chattering_index" in message
    assert "35.0% reduction" in message
    assert "large effect" in message
    assert "significant (p<0.01)" in message


def test_compare_metric_uses_welch_results(monkeypatch):
    def fake_welch(_fixed, _adaptive, alpha=0.05):
        return {
            "t_statistic": 2.5,
            "p_value": 0.012,
            "effect_size": 0.65,
            "reject_null_hypothesis": True,
        }

    monkeypatch.setattr(mt6_stat, "welch_t_test", fake_welch)

    fixed_stats = {"mean": 5.0, "std": 0.8, "ci_lower": 4.5, "ci_upper": 5.5}
    adaptive_stats = {"mean": 3.0, "std": 0.6, "ci_lower": 2.8, "ci_upper": 3.3}

    result = mt6_stat.compare_metric(
        "chattering_index",
        fixed_stats,
        adaptive_stats,
        lower_is_better=True,
    )

    assert result.metric_name == "chattering_index"
    assert result.improvement_percent == pytest.approx(40.0)
    assert result.improvement_absolute == pytest.approx(2.0)
    assert result.significant is True
    assert "chattering_index" in result.interpretation
