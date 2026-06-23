import re
from pathlib import Path

import pandas as pd
import pytest

import sys

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts" / "research" / "mt7_robustness"
sys.path.insert(0, str(SCRIPTS_DIR))

import mt7_generate_report as mt7_report  # noqa: E402


def create_mock_mt6_data():
    return {
        "statistics": {"chattering_index": {"mean": 2.14, "std": 0.13}},
        "configuration": {"n_success": 100},
    }


def _distribute_counts(total, buckets, max_per_bucket):
    if buckets == 0:
        return []
    base = total // buckets
    remainder = total % buckets
    counts = [min(max_per_bucket, base) for _ in range(buckets)]
    for idx in range(remainder):
        counts[idx] = min(max_per_bucket, counts[idx] + 1)
    return counts


def create_mock_mt7_data(n_total: int = 49):
    seeds = list(range(42, 52))
    counts = _distribute_counts(n_total, len(seeds), 50)
    per_seed_stats = {}
    for idx, seed in enumerate(seeds):
        per_seed_stats[str(seed)] = {
            "mean": 100 + seed,
            "std": 5.0,
            "n": counts[idx],
        }

    return {
        "configuration": {
            "seeds": seeds,
            "n_runs_per_seed": 50,
            "total_runs": 500,
            "epsilon_min": 0.00250336,
            "alpha": 1.21441504,
        },
        "global_statistics": {
            "mean": 107.61,
            "std": 5.48,
            "p95": 114.57,
            "p99": 115.73,
            "cv": 0.051,
            "n_total": n_total,
        },
        "per_seed_statistics": per_seed_stats,
    }


def create_mock_comparison_data():
    return {
        "summary": {
            "degradation_ratio": 50.4,
            "degradation_percent": 4929.9,
            "p_value": 0.0,
            "cohens_d": -26.51,
            "significant": True,
        },
        "comparison": {
            "t_statistic": -131.22,
            "p_value": 0.0,
            "effect_size": -26.51,
            "reject_null_hypothesis": True,
        },
    }


def create_mock_seed_dataframe():
    data = []
    for seed in range(42, 52):
        for run in range(5):
            data.append(
                {
                    "seed": seed,
                    "run": run,
                    "chattering_index": 100 + seed + run * 0.1,
                }
            )
    return pd.DataFrame(data)


def generate_mock_report(tmp_path: Path, n_total: int = 49):
    output_path = tmp_path / "MT7_COMPLETE_REPORT.md"
    mt6_data = create_mock_mt6_data()
    mt7_data = create_mock_mt7_data(n_total=n_total)
    comparison_data = create_mock_comparison_data()
    seed_df = create_mock_seed_dataframe()

    mt7_report.generate_mt7_report(mt6_data, mt7_data, comparison_data, seed_df, output_path)
    return output_path.read_text(encoding="utf-8")


# 3.1 Report Structure Tests ---------------------------------------------------
def test_report_generation_creates_file(tmp_path):
    output_path = tmp_path / "report.md"
    mt7_report.generate_mt7_report(
        create_mock_mt6_data(),
        create_mock_mt7_data(),
        create_mock_comparison_data(),
        create_mock_seed_dataframe(),
        output_path,
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 5000


def test_report_contains_all_sections(tmp_path):
    report_content = generate_mock_report(tmp_path)

    required_sections = [
        "# MT-7 Robust PSO Tuning Validation Report",
        "## Executive Summary",
        "## 1. Methodology",
        "## 2. Results",
        "## 3. Visualizations",
        "## 4. Discussion",
        "## 5. Conclusions",
        "## 6. Data Artifacts",
        "## 7. Reproducibility",
    ]

    for section in required_sections:
        assert section in report_content, f"Missing section: {section}"


def test_report_markdown_syntax_valid(tmp_path):
    report_content = generate_mock_report(tmp_path)

    assert report_content.count("```") % 2 == 0
    table_pattern = r"\|.*\|\n\|[-:]+\|"
    assert re.search(table_pattern, report_content)


def test_report_size_reasonable(tmp_path):
    report_content = generate_mock_report(tmp_path)
    size_bytes = len(report_content.encode("utf-8"))

    assert 5000 < size_bytes < 50000


# 3.2 Content Validation Tests -------------------------------------------------
def test_degradation_metrics_in_report(tmp_path):
    report_content = generate_mock_report(tmp_path)

    assert "50.4x" in report_content
    assert "4930" in report_content or "4929" in report_content
    assert "p < 0.001" in report_content or "p<0.001" in report_content
    assert "Cohen's d" in report_content
    assert "-26.5" in report_content


def test_figure_embeds_present(tmp_path):
    report_content = generate_mock_report(tmp_path)

    expected_figures = [
        "MT7_robustness_chattering_distribution.png",
        "MT7_robustness_per_seed_variance.png",
        "MT7_robustness_success_rate.png",
        "MT7_robustness_worst_case.png",
    ]

    for fig in expected_figures:
        assert fig in report_content


def test_per_seed_table_complete(tmp_path):
    report_content = generate_mock_report(tmp_path)

    seed_rows = [seed for seed in range(42, 52) if f"| {seed} |" in report_content]
    assert len(seed_rows) == 10


def test_recommendations_section_present(tmp_path):
    report_content = generate_mock_report(tmp_path)

    assert "## 4.3 Recommendations for MT-8+" in report_content
    assert "Multi-Scenario PSO" in report_content or "Multi-Scenario" in report_content
    assert "Expand PSO training set" in report_content


# 3.3 Data Formatting Tests ----------------------------------------------------
def test_format_number_precision():
    assert mt7_report.format_number(107.6070097, 2) == "107.61"
    assert mt7_report.format_number(2.1354, 4) == "2.1354"
    assert mt7_report.format_number(float("nan"), 2) == "N/A"


def test_timestamp_format(tmp_path):
    report_content = generate_mock_report(tmp_path)

    timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
    assert re.search(timestamp_pattern, report_content)


# 3.4 Edge Cases ---------------------------------------------------------------
def test_edge_case_incomplete_mt7_data(tmp_path):
    mt6_data = create_mock_mt6_data()
    mt7_data = {
        "configuration": {
            "seeds": list(range(42, 52)),
            "n_runs_per_seed": 50,
            "total_runs": 500,
            "epsilon_min": 0.00250336,
            "alpha": 1.21441504,
        },
        "global_statistics": {"mean": 107.61},
        "per_seed_statistics": {},
    }
    comparison_data = create_mock_comparison_data()

    with pytest.raises(KeyError):
        mt7_report.generate_mt7_report(mt6_data, mt7_data, comparison_data, pd.DataFrame(), tmp_path / "out.md")


def test_edge_case_empty_seed_dataframe(tmp_path):
    output_path = tmp_path / "report.md"
    mt6_data = create_mock_mt6_data()
    mt7_data = create_mock_mt7_data(n_total=0)
    comparison_data = create_mock_comparison_data()
    empty_seed_df = pd.DataFrame(columns=["seed", "run", "chattering_index"])

    mt7_report.generate_mt7_report(mt6_data, mt7_data, comparison_data, empty_seed_df, output_path)
    content = output_path.read_text(encoding="utf-8")

    assert "0/500" in content or "0 successful runs" in content.lower()
