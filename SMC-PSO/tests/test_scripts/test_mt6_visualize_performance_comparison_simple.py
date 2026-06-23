import json

import numpy as np
import matplotlib.pyplot as plt

import mt6_visualize_performance_comparison_simple as viz_compare


def test_load_json_summary(tmp_path):
    payload = {"comparisons": {"metric": {}}}
    json_path = tmp_path / "stats.json"
    json_path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = viz_compare.load_json_summary(json_path)

    assert loaded == payload


def test_plot_comparison_from_summary_generates_png(tmp_path):
    comparison_payload = {
        "summary": "Adaptive boundary layer reduces chattering.",
        "comparisons": {
            "chattering_index": {
                "fixed_mean": 1.0,
                "fixed_ci_lower": 0.9,
                "fixed_ci_upper": 1.1,
                "adaptive_mean": 0.6,
                "adaptive_ci_lower": 0.5,
                "adaptive_ci_upper": 0.7,
                "improvement_percent": 40.0,
                "p_value": 0.002,
                "significant": True,
            },
            "overshoot_theta1": {
                "fixed_mean": 0.3,
                "fixed_ci_lower": 0.25,
                "fixed_ci_upper": 0.35,
                "adaptive_mean": 0.2,
                "adaptive_ci_lower": 0.18,
                "adaptive_ci_upper": 0.22,
                "improvement_percent": 33.3,
                "p_value": 0.01,
                "significant": True,
            },
            "overshoot_theta2": {
                "fixed_mean": 0.28,
                "fixed_ci_lower": 0.24,
                "fixed_ci_upper": 0.32,
                "adaptive_mean": 0.19,
                "adaptive_ci_lower": 0.16,
                "adaptive_ci_upper": 0.22,
                "improvement_percent": 32.0,
                "p_value": 0.015,
                "significant": True,
            },
            "control_energy": {
                "fixed_mean": 12.0,
                "fixed_ci_lower": 11.0,
                "fixed_ci_upper": 13.0,
                "adaptive_mean": 9.0,
                "adaptive_ci_lower": 8.5,
                "adaptive_ci_upper": 9.5,
                "improvement_percent": 25.0,
                "p_value": 0.03,
                "significant": True,
            },
        },
    }

    statistics_path = tmp_path / "comparison.json"
    statistics_path.write_text(json.dumps(comparison_payload), encoding="utf-8")
    output_path = tmp_path / "figure.png"

    viz_compare.plot_comparison_from_summary(statistics_path, output_path, show=False)

    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert plt.get_fignums() == []
