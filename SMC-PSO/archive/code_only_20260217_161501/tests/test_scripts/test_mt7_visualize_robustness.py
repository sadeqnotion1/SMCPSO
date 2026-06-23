from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import sys

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import mt7_visualize_robustness as mt7_viz  # noqa: E402
from matplotlib import axes as mpl_axes  # noqa: E402
from matplotlib._api.deprecation import MatplotlibDeprecationWarning  # noqa: E402


def create_mock_seed_dataframe(
    total_runs: int = 50,
    successful_runs: int | None = None,
    success_rate: float | None = 0.1,
    rng_seed: int = 0,
) -> pd.DataFrame:
    rng = np.random.default_rng(rng_seed)
    seeds = list(range(42, 52))
    rows = []

    if successful_runs is not None:
        base = successful_runs // len(seeds)
        remainder = successful_runs % len(seeds)
        counts = [min(total_runs, base + (1 if i < remainder else 0)) for i in range(len(seeds))]
    elif success_rate is not None:
        counts = []
        for i in range(len(seeds)):
            count = int(round(total_runs * success_rate))
            counts.append(min(total_runs, max(0, count)))
    else:
        counts = [total_runs for _ in seeds]

    for seed, count in zip(seeds, counts):
        for run in range(count):
            rows.append(
                {
                    "seed": seed,
                    "run": run,
                    "chattering_index": float(rng.normal(100 + seed, 5)),
                    "success": True,
                }
            )

    return pd.DataFrame(rows, columns=["seed", "run", "chattering_index", "success"])


# 2.1 Figure 1: Chattering Distribution ----------------------------------------
def test_plot_chattering_distribution_creates_image(tmp_path, monkeypatch):
    def fake_savefig(path, *args, **kwargs):
        path = Path(path)
        path.write_bytes(b"0" * 60000)

    monkeypatch.setattr(mt7_viz.plt, "savefig", fake_savefig)

    mt6_stats = {"chattering_index": {"mean": 2.14, "std": 0.13}}
    mt7_stats = {"mean": 107.61, "std": 5.48, "p95": 114.57, "p99": 115.73}
    output_path = tmp_path / "fig1.png"

    mt7_viz.plot_chattering_distribution(mt6_stats, mt7_stats, output_path, show=False)

    assert output_path.exists()
    assert output_path.stat().st_size > 50000


def test_plot_chattering_distribution_marks_percentiles(monkeypatch):
    captured = []
    original = mpl_axes.Axes.axvline

    def capture_axvline(self, x=0, *args, **kwargs):
        captured.append(x)
        return original(self, x, *args, **kwargs)

    monkeypatch.setattr(mpl_axes.Axes, "axvline", capture_axvline)
    monkeypatch.setattr(mt7_viz.plt, "savefig", lambda *args, **kwargs: None)

    mt6_stats = {"chattering_index": {"mean": 2.14, "std": 0.13}}
    mt7_stats = {"mean": 107.61, "std": 5.48, "p95": 114.57, "p99": 115.73}

    mt7_viz.plot_chattering_distribution(mt6_stats, mt7_stats, Path("/dev/null"), show=False)

    assert any(pytest.approx(114.57, rel=1e-3) == value for value in captured)
    assert any(pytest.approx(115.73, rel=1e-3) == value for value in captured)


def test_plot_chattering_distribution_includes_degradation_text(monkeypatch):
    texts = []
    original = mpl_axes.Axes.text

    def capture_text(self, x, y, s, *args, **kwargs):
        texts.append(str(s))
        return original(self, x, y, s, *args, **kwargs)

    monkeypatch.setattr(mpl_axes.Axes, "text", capture_text)
    monkeypatch.setattr(mt7_viz.plt, "savefig", lambda *args, **kwargs: None)

    mt6_stats = {"chattering_index": {"mean": 2.14, "std": 0.13}}
    mt7_stats = {"mean": 107.61, "std": 5.48, "p95": 114.57, "p99": 115.73}

    mt7_viz.plot_chattering_distribution(mt6_stats, mt7_stats, Path("/dev/null"), show=False)

    assert any("worse" in text for text in texts)


def test_plot_chattering_distribution_uses_300dpi(monkeypatch, tmp_path):
    call_args = {}

    def capture_savefig(path, *args, **kwargs):
        call_args.update(kwargs)
        Path(path).write_bytes(b"")

    monkeypatch.setattr(mt7_viz.plt, "savefig", capture_savefig)

    mt6_stats = {"chattering_index": {"mean": 2.14, "std": 0.13}}
    mt7_stats = {"mean": 107.61, "std": 5.48, "p95": 114.57, "p99": 115.73}

    mt7_viz.plot_chattering_distribution(mt6_stats, mt7_stats, tmp_path / "fig1.png", show=False)

    assert call_args.get("dpi") == 300


def test_plot_chattering_distribution_missing_p99_raises():
    mt6_stats = {"chattering_index": {"mean": 2.14, "std": 0.13}}
    mt7_stats = {"mean": 107.61, "std": 5.48, "p95": 114.57}

    with pytest.raises(KeyError):
        mt7_viz.plot_chattering_distribution(mt6_stats, mt7_stats, Path("/dev/null"), show=False)


# 2.2 Figure 2: Per-Seed Variance ----------------------------------------------
def _build_mt7_per_seed_data():
    per_seed = {str(i): {"mean": 100 + i, "std": 5.0, "n": 5} for i in range(42, 52)}
    return {
        "per_seed_statistics": per_seed,
        "global_statistics": {"mean": 107.61, "cv": 0.051},
    }


def test_plot_per_seed_variance_creates_image(tmp_path, monkeypatch):
    def fake_savefig(path, *args, **kwargs):
        Path(path).write_bytes(b"0" * 60000)

    monkeypatch.setattr(mt7_viz.plt, "savefig", fake_savefig)
    captured = {}

    def fake_boxplot(self, data, *args, **kwargs):
        captured["labels"] = kwargs.get("labels")
        return {}

    monkeypatch.setattr(mpl_axes.Axes, "boxplot", fake_boxplot)

    mt7_data = _build_mt7_per_seed_data()
    seed_df = create_mock_seed_dataframe(success_rate=0.3)
    output_path = tmp_path / "fig2.png"

    mt7_viz.plot_per_seed_variance(mt7_data, seed_df, output_path, show=False)

    assert output_path.exists()
    assert output_path.stat().st_size > 50000
    assert captured["labels"] == [str(seed) for seed in range(42, 52)]


def test_plot_per_seed_variance_global_mean_line(monkeypatch):
    captured = []
    original = mpl_axes.Axes.axhline

    def capture_axhline(self, y=0, *args, **kwargs):
        captured.append(y)
        return original(self, y, *args, **kwargs)

    monkeypatch.setattr(mpl_axes.Axes, "boxplot", lambda *args, **kwargs: {})
    monkeypatch.setattr(mpl_axes.Axes, "axhline", capture_axhline)
    monkeypatch.setattr(mt7_viz.plt, "savefig", lambda *args, **kwargs: None)

    mt7_data = _build_mt7_per_seed_data()
    seed_df = create_mock_seed_dataframe(success_rate=0.2)

    mt7_viz.plot_per_seed_variance(mt7_data, seed_df, Path("/dev/null"), show=False)

    assert any(pytest.approx(107.61, rel=1e-3) == value for value in captured)


def test_plot_per_seed_variance_cv_annotation(monkeypatch):
    texts = []
    original = mpl_axes.Axes.text

    def capture_text(self, x, y, s, *args, **kwargs):
        texts.append(str(s))
        return original(self, x, y, s, *args, **kwargs)

    monkeypatch.setattr(mpl_axes.Axes, "boxplot", lambda *args, **kwargs: {})
    monkeypatch.setattr(mpl_axes.Axes, "text", capture_text)
    monkeypatch.setattr(mt7_viz.plt, "savefig", lambda *args, **kwargs: None)

    mt7_data = _build_mt7_per_seed_data()
    seed_df = create_mock_seed_dataframe(success_rate=0.25)

    mt7_viz.plot_per_seed_variance(mt7_data, seed_df, Path("/dev/null"), show=False)

    assert any("CV = 5.1%" in text or "CV = 5.0%" in text for text in texts)


def test_plot_per_seed_variance_single_seed(tmp_path, monkeypatch):
    monkeypatch.setattr(mt7_viz.plt, "savefig", lambda *args, **kwargs: None)
    monkeypatch.setattr(mpl_axes.Axes, "boxplot", lambda *args, **kwargs: {})

    mt7_data = {
        "per_seed_statistics": {"42": {"mean": 107.61, "std": 5.48, "n": 49}},
        "global_statistics": {"mean": 107.61, "cv": 0.051},
    }
    rng = np.random.default_rng(42)
    seed_df = pd.DataFrame(
        {
            "seed": [42] * 49,
            "run": list(range(49)),
            "chattering_index": rng.normal(107.61, 5.48, 49),
            "success": True,
        }
    )

    mt7_viz.plot_per_seed_variance(mt7_data, seed_df, tmp_path / "fig2.png", show=False)


def test_plot_per_seed_variance_no_seed_data_raises():
    mt7_data = {"per_seed_statistics": {}, "global_statistics": {"mean": 0.0, "cv": 0.0}}
    seed_df = pd.DataFrame(columns=["seed", "run", "chattering_index", "success"])

    with pytest.raises(MatplotlibDeprecationWarning):
        mt7_viz.plot_per_seed_variance(mt7_data, seed_df, Path("/dev/null"), show=False)


# 2.3 Figure 3: Success Rate Analysis ------------------------------------------
def test_plot_success_rate_analysis_creates_image(tmp_path, monkeypatch):
    def fake_savefig(path, *args, **kwargs):
        Path(path).write_bytes(b"0" * 20000)

    monkeypatch.setattr(mt7_viz.plt, "savefig", fake_savefig)

    seed_df = create_mock_seed_dataframe(successful_runs=60)

    output_path = tmp_path / "fig3.png"
    mt7_viz.plot_success_rate_analysis(seed_df, output_path, show=False)

    assert output_path.exists()
    assert output_path.stat().st_size > 10000


def test_plot_success_rate_analysis_shows_success_rate(monkeypatch):
    texts = []
    original = mpl_axes.Axes.text

    def capture_text(self, x, y, s, *args, **kwargs):
        texts.append(str(s))
        return original(self, x, y, s, *args, **kwargs)

    monkeypatch.setattr(mpl_axes.Axes, "text", capture_text)
    monkeypatch.setattr(mt7_viz.plt, "savefig", lambda *args, **kwargs: None)

    seed_df = create_mock_seed_dataframe(total_runs=50, successful_runs=49)

    mt7_viz.plot_success_rate_analysis(seed_df, Path("/dev/null"), show=False)

    assert any("Success Rate" in text and "%" in text for text in texts)


def test_plot_success_rate_analysis_reference_line(monkeypatch):
    captured = []
    original = mpl_axes.Axes.axhline

    def capture_axhline(self, y=0, *args, **kwargs):
        captured.append(y)
        return original(self, y, *args, **kwargs)

    monkeypatch.setattr(mpl_axes.Axes, "axhline", capture_axhline)
    monkeypatch.setattr(mt7_viz.plt, "savefig", lambda *args, **kwargs: None)

    seed_df = create_mock_seed_dataframe(success_rate=0.4)

    mt7_viz.plot_success_rate_analysis(seed_df, Path("/dev/null"), show=False)

    assert any(pytest.approx(50, rel=1e-3) == value for value in captured)


def test_plot_success_rate_analysis_zero_success(monkeypatch):
    monkeypatch.setattr(mt7_viz.plt, "savefig", lambda *args, **kwargs: None)
    seed_df = pd.DataFrame(columns=["seed", "run", "chattering_index", "success"])

    with pytest.raises(ZeroDivisionError):
        mt7_viz.plot_success_rate_analysis(seed_df, Path("/dev/null"), show=False)


def test_plot_success_rate_analysis_full_success(monkeypatch):
    monkeypatch.setattr(mt7_viz.plt, "savefig", lambda *args, **kwargs: None)
    seed_df = create_mock_seed_dataframe(success_rate=1.0)

    mt7_viz.plot_success_rate_analysis(seed_df, Path("/dev/null"), show=False)


# 2.4 Figure 4: Worst-Case Percentiles -----------------------------------------
def test_plot_worst_case_analysis_creates_image(tmp_path, monkeypatch):
    def fake_savefig(path, *args, **kwargs):
        Path(path).write_bytes(b"0" * 40000)

    monkeypatch.setattr(mt7_viz.plt, "savefig", fake_savefig)

    mt6_stats = {"chattering_index": {"mean": 2.14, "std": 0.13}}
    mt7_stats = {"mean": 107.61, "std": 5.48, "p95": 114.57, "p99": 115.73}

    output_path = tmp_path / "fig4.png"
    mt7_viz.plot_worst_case_analysis(mt6_stats, mt7_stats, output_path, show=False)

    assert output_path.exists()
    assert output_path.stat().st_size > 20000


def test_plot_worst_case_analysis_degradation_text(monkeypatch):
    texts = []
    original = mpl_axes.Axes.text

    def capture_text(self, x, y, s, *args, **kwargs):
        texts.append(str(s))
        return original(self, x, y, s, *args, **kwargs)

    monkeypatch.setattr(mpl_axes.Axes, "text", capture_text)
    monkeypatch.setattr(mt7_viz.plt, "savefig", lambda *args, **kwargs: None)

    mt6_stats = {"chattering_index": {"mean": 2.14, "std": 0.13}}
    mt7_stats = {"mean": 107.61, "std": 5.48, "p95": 114.57, "p99": 115.73}

    mt7_viz.plot_worst_case_analysis(mt6_stats, mt7_stats, Path("/dev/null"), show=False)

    assert any("P95:" in text and "x worse" in text for text in texts)


def test_plot_worst_case_analysis_plots_two_lines(monkeypatch):
    calls = []
    original = mpl_axes.Axes.plot

    def capture_plot(self, *args, **kwargs):
        calls.append(args)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(mpl_axes.Axes, "plot", capture_plot)
    monkeypatch.setattr(mt7_viz.plt, "savefig", lambda *args, **kwargs: None)

    mt6_stats = {"chattering_index": {"mean": 2.14, "std": 0.13}}
    mt7_stats = {"mean": 107.61, "std": 5.48, "p95": 114.57, "p99": 115.73}

    mt7_viz.plot_worst_case_analysis(mt6_stats, mt7_stats, Path("/dev/null"), show=False)

    assert len(calls) == 2
    for _, y_values in calls:
        assert len(y_values) == 5


def test_plot_worst_case_analysis_identical_percentiles(monkeypatch):
    monkeypatch.setattr(mt7_viz.plt, "savefig", lambda *args, **kwargs: None)

    mt6_stats = {"chattering_index": {"mean": 2.14, "std": 0.0}}
    mt7_stats = {"mean": 107.61, "std": 0.0, "p95": 107.61, "p99": 107.61}

    mt7_viz.plot_worst_case_analysis(mt6_stats, mt7_stats, Path("/dev/null"), show=False)


def test_plot_worst_case_analysis_missing_p95():
    mt6_stats = {"chattering_index": {"mean": 2.14, "std": 0.13}}
    mt7_stats = {"mean": 107.61, "std": 5.48, "p99": 115.73}

    with pytest.raises(KeyError):
        mt7_viz.plot_worst_case_analysis(mt6_stats, mt7_stats, Path("/dev/null"), show=False)
