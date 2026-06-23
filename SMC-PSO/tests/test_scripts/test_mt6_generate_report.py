import sys
from pathlib import Path

import pandas as pd

# Add scripts/research/mt6_boundary_layer to path for import
scripts_path = Path(__file__).parents[2] / "scripts" / "research" / "mt6_boundary_layer"
sys.path.insert(0, str(scripts_path))

import mt6_generate_report as mt6_report


def test_format_number_handles_nan_and_precision():
    assert mt6_report.format_number(float("nan")) == "N/A"
    assert mt6_report.format_number(1.2345, decimals=3) == "1.234"


def test_get_significance_stars_thresholds():
    assert mt6_report.get_significance_stars(0.0009) == "***"
    assert mt6_report.get_significance_stars(0.005) == "**"
    assert mt6_report.get_significance_stars(0.03) == "*"
    assert mt6_report.get_significance_stars(0.2) == "ns"


def _stat_block(mean, std, ci_lower, ci_upper):
    return {
        "mean": mean,
        "std": std,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
    }


def test_generate_report_populates_template(tmp_path):
    template_path = tmp_path / "template.md"
    template_path.write_text(
        "# MT-6 Report\n"
        "Improvement: {{chattering_improvement}}%\n"
        "Best fitness: {{best_fitness}}\n"
        "Summary: {{conclusion_summary}}\n",
        encoding="utf-8",
    )
    output_path = tmp_path / "report.md"

    fixed_summary = {
        "statistics": {
            "chattering_index": _stat_block(1.0, 0.1, 0.9, 1.1),
            "settling_time": _stat_block(4.5, 0.2, 4.3, 4.7),
            "overshoot_theta1": _stat_block(0.35, 0.05, 0.3, 0.4),
            "control_energy": _stat_block(12.0, 0.5, 11.5, 12.5),
            "rms_control": _stat_block(3.0, 0.2, 2.8, 3.2),
        },
        "configuration": {"n_runs": 50},
    }

    adaptive_summary = {
        "statistics": {
            "chattering_index": _stat_block(0.6, 0.08, 0.55, 0.65),
            "settling_time": _stat_block(3.2, 0.15, 3.0, 3.4),
            "overshoot_theta1": _stat_block(0.2, 0.03, 0.17, 0.23),
            "control_energy": _stat_block(8.8, 0.4, 8.4, 9.2),
            "rms_control": _stat_block(2.2, 0.15, 2.0, 2.4),
        },
        "configuration": {"n_runs": 50},
    }

    comparison = {
        "summary": "Adaptive boundary layer reduces chattering by 40%.",
        "comparisons": {
            "chattering_index": {
                "improvement_percent": 40.0,
                "p_value": 0.004,
                "cohens_d": -0.9,
                "adaptive_mean": 0.6,
                "significant": True,
            },
            "settling_time": {
                "improvement_percent": 28.9,
                "p_value": 0.01,
                "significant": True,
            },
            "overshoot_theta1": {
                "improvement_percent": 42.9,
                "p_value": 0.02,
                "significant": True,
            },
            "control_energy": {
                "improvement_percent": 26.7,
                "p_value": 0.03,
                "significant": True,
            },
            "rms_control": {
                "improvement_percent": 26.7,
                "p_value": 0.025,
                "significant": True,
            },
        },
    }

    pso_csv = pd.DataFrame(
        {
            "iteration": [0, 1, 2],
            "epsilon_min": [0.02, 0.018, 0.015],
            "alpha": [0.5, 0.55, 0.6],
            "best_fitness": [1.0, 0.7, 0.3],
            "mean_fitness": [1.1, 0.8, 0.4],
            "std_fitness": [0.1, 0.08, 0.05],
        }
    )

    mt6_report.generate_report(
        template_path,
        output_path,
        fixed_summary,
        adaptive_summary,
        comparison,
        pso_csv,
    )

    report_text = output_path.read_text(encoding="utf-8")

    assert "Improvement: 40.0%" in report_text
    assert "Best fitness: 0.3000" in report_text
    assert "Adaptive boundary layer achieves" in report_text
    assert "{{" not in report_text and "}}" not in report_text
