"""M4 Slice 6 - simulation/strategies (MonteCarloStrategy) behavioral tests."""
import numpy as np
import pytest

from src.simulation.strategies import MonteCarloStrategy
from src.simulation.core.interfaces import SimulationStrategy


class _FakeResult:
    """Mimics a result container exposing get_states() -> ndarray (T, n)."""
    def __init__(self, states):
        self._states = np.asarray(states, dtype=float)
    def get_states(self):
        return self._states


def _sim_ok(params, **kwargs):
    # deterministic: final state encodes a parameter so stats are checkable
    g = params.get("gain", 1.0)
    return _FakeResult([[0.0, 0.0], [g, 2.0 * g]])


def test_is_simulation_strategy_subclass():
    assert issubclass(MonteCarloStrategy, SimulationStrategy)
    assert isinstance(MonteCarloStrategy(), SimulationStrategy)


def test_init_stores_config():
    s = MonteCarloStrategy(n_samples=42, parallel=False, max_workers=3)
    assert s.n_samples == 42 and s.parallel is False and s.max_workers == 3


def test_generate_samples_count_and_constant():
    s = MonteCarloStrategy(n_samples=7)
    samples = s._generate_samples({"k": {"type": "constant", "value": 5.0}})
    assert len(samples) == 7
    assert all(smp["k"] == 5.0 for smp in samples)


def test_generate_samples_uniform_within_bounds():
    np.random.seed(0)
    s = MonteCarloStrategy(n_samples=200)
    samples = s._generate_samples({"k": {"type": "uniform", "low": -1.0, "high": 1.0}})
    vals = [smp["k"] for smp in samples]
    assert all(-1.0 <= v <= 1.0 for v in vals)


def test_generate_samples_normal_stats():
    np.random.seed(1)
    s = MonteCarloStrategy(n_samples=5000)
    samples = s._generate_samples({"k": {"type": "normal", "mean": 10.0, "std": 2.0}})
    vals = np.array([smp["k"] for smp in samples])
    assert abs(vals.mean() - 10.0) < 0.3
    assert abs(vals.std() - 2.0) < 0.3


def test_generate_samples_unknown_type_raises():
    s = MonteCarloStrategy(n_samples=1)
    with pytest.raises(ValueError):
        s._generate_samples({"k": {"type": "weibull"}})


def test_analyze_sequential_success_and_statistics():
    np.random.seed(2)
    s = MonteCarloStrategy(n_samples=20, parallel=False)
    out = s.analyze(_sim_ok, {"distributions": {"gain": {"type": "constant", "value": 3.0}}})
    assert out["success_rate"] == 1.0
    assert out["n_successful"] == 20 and out["n_total"] == 20
    stats = out["statistics"]
    # final_state_0 == gain == 3.0 deterministically
    assert abs(stats["final_state_0"]["mean"] - 3.0) < 1e-9
    assert abs(stats["final_state_1"]["mean"] - 6.0) < 1e-9
    assert set(stats["final_state_0"]["percentiles"].keys()) == {"5", "25", "50", "75", "95"}
    # max_deviation == max|states| == 6.0
    assert abs(stats["max_deviation"]["max"] - 6.0) < 1e-9


def test_analyze_parallel_flag_runs_same_path():
    s = MonteCarloStrategy(n_samples=5, parallel=True)
    out = s.analyze(_sim_ok, {"distributions": {"gain": {"type": "constant", "value": 1.0}}})
    assert out["success_rate"] == 1.0 and out["n_successful"] == 5


def test_analyze_counts_failures():
    calls = {"i": 0}
    def flaky(params, **kwargs):
        calls["i"] += 1
        if calls["i"] % 2 == 0:
            raise RuntimeError("boom")
        return _FakeResult([[0.0], [1.0]])
    s = MonteCarloStrategy(n_samples=10, parallel=False)
    out = s.analyze(flaky, {"distributions": {"g": {"type": "constant", "value": 1.0}}})
    assert out["n_total"] == 10
    assert 0.0 < out["success_rate"] < 1.0
    assert out["n_successful"] == 5


def test_analyze_no_success_returns_error():
    def always_fail(params, **kwargs):
        raise RuntimeError("nope")
    s = MonteCarloStrategy(n_samples=4, parallel=False)
    out = s.analyze(always_fail, {"distributions": {"g": {"type": "constant", "value": 1.0}}})
    assert out["success_rate"] == 0.0
    assert "error" in out


def test_fixed_params_merge():
    seen = {}
    def capture(params, **kwargs):
        seen.update(params)
        return _FakeResult([[0.0], [1.0]])
    s = MonteCarloStrategy(n_samples=1, parallel=False)
    s.analyze(capture, {"fixed": {"dt": 0.01}, "distributions": {"g": {"type": "constant", "value": 9.0}}})
    assert seen["dt"] == 0.01 and seen["g"] == 9.0
