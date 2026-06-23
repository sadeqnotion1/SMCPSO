import io
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import sys

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import mt7_robust_pso_tuning as mt7_tuning  # noqa: E402


def make_metric(seed, run_id, chattering, success=True):
    value = float(chattering)
    return mt7_tuning.MT7Metrics(
        seed=seed,
        run_id=run_id,
        chattering_index=value,
        settling_time=5.0 if success else np.inf,
        overshoot_theta1=0.1,
        overshoot_theta2=0.2,
        control_energy=10.0,
        rms_control=3.0,
        success=success,
    )


def build_results(success_counts):
    all_results = {}
    success_values = []
    for seed, count in success_counts.items():
        metrics = []
        for idx in range(count):
            chattering = 100.0 + seed + idx
            metrics.append(make_metric(seed, idx + 1, chattering, success=True))
            success_values.append(chattering)
        # Add a failed run to ensure filtering works
        metrics.append(
            mt7_tuning.MT7Metrics(
                seed=seed,
                run_id=count + 1,
                chattering_index=np.inf,
                settling_time=np.inf,
                overshoot_theta1=np.inf,
                overshoot_theta2=np.inf,
                control_energy=np.inf,
                rms_control=np.inf,
                success=False,
            )
        )
        all_results[seed] = metrics
    return all_results, success_values


# 4.1 Initialization Tests -----------------------------------------------------
def test_mt7_script_imports():
    assert hasattr(mt7_tuning, "main")


def test_mt6_optimal_params_values():
    params = mt7_tuning.MT6_OPTIMAL_PARAMS
    assert params["epsilon_min"] == pytest.approx(0.00250336, rel=1e-6)
    assert params["alpha"] == pytest.approx(1.21441504, rel=1e-6)


def test_mt7_config_structure():
    config = mt7_tuning.MT7_CONFIG
    assert config["seeds"] == list(range(42, 52))
    assert config["n_runs_per_seed"] == 50
    assert config["dt"] == pytest.approx(0.01)
    assert config["sim_time"] == pytest.approx(10.0)


# 4.2 Initial Condition & Metric Utilities ------------------------------------
def test_generate_initial_conditions_shape():
    ic = mt7_tuning.generate_initial_conditions_mt7(25, seed=42)
    assert ic.shape == (25, 6)
    assert np.all(ic[:, 0] == 0.0)
    assert np.all(np.abs(ic[:, 1:3]) <= 0.3 + 1e-9)


def test_generate_initial_conditions_seed_variation():
    ic_a = mt7_tuning.generate_initial_conditions_mt7(10, seed=42)
    ic_b = mt7_tuning.generate_initial_conditions_mt7(10, seed=43)
    assert not np.array_equal(ic_a, ic_b)


def test_compute_chattering_index_fft_high_freq():
    dt = 0.01
    t = np.arange(0, 1.0, dt)
    control = np.sin(2 * np.pi * 20 * t)  # 20 Hz component
    index = mt7_tuning.compute_chattering_index_fft(control, dt)
    assert index > 0.0


def test_compute_mt7_metrics_success_flag():
    t_arr = np.linspace(0, 1, 11)
    x_arr = np.zeros((11, 6))
    x_arr[:, 1] = np.linspace(0.2, 0.0, 11)
    x_arr[:, 2] = np.linspace(0.1, 0.0, 11)
    u_arr = np.sin(np.linspace(0, 10, 10))

    metrics = mt7_tuning.compute_mt7_metrics(t_arr, x_arr, u_arr, seed=42, run_id=1)

    assert metrics.success
    assert metrics.chattering_index >= 0.0


def test_compute_mt7_metrics_failure_flag():
    t_arr = np.linspace(0, 1, 11)
    x_arr = np.zeros((11, 6))
    x_arr[:, 1] = 0.5  # never within tolerance
    x_arr[:, 2] = 0.5
    u_arr = np.zeros(10)

    metrics = mt7_tuning.compute_mt7_metrics(t_arr, x_arr, u_arr, seed=42, run_id=1)

    assert not metrics.success
    assert metrics.settling_time == pytest.approx(t_arr[-1])


# 4.3 CSV Data Structure Tests -------------------------------------------------
def test_save_seed_results_columns(tmp_path):
    metrics = [make_metric(42, i + 1, 100 + i) for i in range(5)]
    mt7_tuning.save_seed_results(42, metrics, tmp_path)
    csv_path = tmp_path / "MT7_seed_42_results.csv"

    df = pd.read_csv(csv_path)
    expected_columns = [
        "seed",
        "run",
        "chattering_index",
        "settling_time",
        "overshoot_theta1",
        "overshoot_theta2",
        "control_energy",
        "rms_control",
        "success",
    ]
    assert list(df.columns) == expected_columns


def test_save_seed_results_data_types(tmp_path):
    metrics = [make_metric(42, i + 1, 100 + i) for i in range(3)]
    mt7_tuning.save_seed_results(42, metrics, tmp_path)
    csv_path = tmp_path / "MT7_seed_42_results.csv"

    df = pd.read_csv(csv_path)
    assert pd.api.types.is_integer_dtype(df["seed"])
    assert pd.api.types.is_integer_dtype(df["run"])
    assert pd.api.types.is_float_dtype(df["chattering_index"])


def test_save_seed_results_row_count(tmp_path):
    metrics = [make_metric(42, i + 1, 100 + i) for i in range(50)]
    mt7_tuning.save_seed_results(42, metrics, tmp_path)
    csv_path = tmp_path / "MT7_seed_42_results.csv"

    df = pd.read_csv(csv_path)
    assert len(df) == 50


def test_save_seed_results_success_values_finite(tmp_path):
    metrics = [make_metric(42, i + 1, 100 + i) for i in range(5)]
    mt7_tuning.save_seed_results(42, metrics, tmp_path)
    csv_path = tmp_path / "MT7_seed_42_results.csv"

    df = pd.read_csv(csv_path)
    finite_cols = ["chattering_index", "settling_time", "control_energy"]
    for col in finite_cols:
        assert np.isfinite(df[col]).all()


# 4.4 Summary JSON Structure Tests --------------------------------------------
def test_generate_summary_json_schema(tmp_path):
    success_counts = {seed: 3 for seed in range(42, 52)}
    all_results, _ = build_results(success_counts)
    mt7_tuning.generate_summary_json(all_results, tmp_path)
    summary_path = tmp_path / "MT7_robustness_summary.json"

    with open(summary_path) as f:
        data = json.load(f)

    assert "configuration" in data
    assert "per_seed_statistics" in data
    assert "global_statistics" in data


def test_generate_summary_json_statistics_values(tmp_path):
    success_counts = {seed: (seed - 41) + 1 for seed in range(42, 52)}  # 2..11 successes
    all_results, success_values = build_results(success_counts)
    mt7_tuning.generate_summary_json(all_results, tmp_path)
    summary_path = tmp_path / "MT7_robustness_summary.json"

    with open(summary_path) as f:
        data = json.load(f)

    expected_mean = np.mean(success_values)
    expected_std = np.std(success_values, ddof=1)
    assert data["global_statistics"]["mean"] == pytest.approx(expected_mean)
    assert data["global_statistics"]["std"] == pytest.approx(expected_std)
    assert data["global_statistics"]["n_total"] == len(success_values)


def test_generate_summary_json_cv(tmp_path):
    success_counts = {seed: 2 for seed in range(42, 52)}
    all_results, success_values = build_results(success_counts)
    mt7_tuning.generate_summary_json(all_results, tmp_path)
    summary_path = tmp_path / "MT7_robustness_summary.json"

    with open(summary_path) as f:
        data = json.load(f)

    expected_cv = np.std(success_values, ddof=1) / np.mean(success_values)
    assert data["global_statistics"]["cv"] == pytest.approx(expected_cv)


def test_generate_summary_json_empty_results_raises(tmp_path):
    all_results = {seed: [make_metric(seed, 1, np.inf, success=False)] for seed in range(42, 52)}

    with pytest.raises((ValueError, IndexError)):
        mt7_tuning.generate_summary_json(all_results, tmp_path)


# 4.5 Edge Case & Data Validation ---------------------------------------------
def test_corrupted_csv_raises_value_error():
    corrupted_csv = "seed,run,chattering_index\n42,1,invalid_number"

    with pytest.raises(ValueError):
        pd.read_csv(io.StringIO(corrupted_csv), dtype={"chattering_index": float})
