#======================================================================================
#==================== tests/test_simulation/test_results.py ===========================
#======================================================================================

"""Unit tests for the simulation results subpackage (M4 Slice 5)."""

import os
import csv
import tempfile

import numpy as np
import pytest

from src.simulation.results import (
    StandardResultContainer,
    BatchResultContainer,
    ResultProcessor,
    CSVExporter,
    HDF5Exporter,
    ResultValidator,
)
from src.simulation.core.interfaces import ResultContainer


def _traj(n=5, dim=4):
    times = np.linspace(0.0, (n - 1) * 0.1, n)
    states = np.arange(n * dim, dtype=float).reshape(n, dim)
    controls = np.arange(n, dtype=float)
    return states, times, controls


def test_results_package_exports():
    import src.simulation.results as r
    for name in ("StandardResultContainer", "BatchResultContainer", "ResultProcessor",
                 "CSVExporter", "HDF5Exporter", "ResultValidator"):
        assert name in r.__all__
        assert hasattr(r, name)


def test_standard_container_roundtrip_and_isolation():
    states, times, controls = _traj()
    c = StandardResultContainer()
    assert isinstance(c, ResultContainer)
    c.add_trajectory(states, times, controls=controls, run="a")
    assert np.array_equal(c.get_states(), states)
    assert np.array_equal(c.get_times(), times)
    assert np.array_equal(c.controls, controls)
    assert c.metadata["run"] == "a"
    states[0, 0] = -999.0
    assert c.get_states()[0, 0] != -999.0


def test_standard_container_empty_defaults():
    c = StandardResultContainer()
    assert c.get_states().size == 0
    assert c.get_times().size == 0


def test_standard_container_export_dispatch_and_bad_format():
    states, times, controls = _traj()
    c = StandardResultContainer()
    c.add_trajectory(states, times, controls=controls)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.csv")
        c.export("CSV", path)
        assert os.path.exists(path)
    with pytest.raises(ValueError):
        c.export("bogus", "x")


def test_batch_container_indexing_and_count():
    b = BatchResultContainer()
    for i in range(3):
        states = np.full((4, 2), float(i))
        times = np.linspace(0, 0.3, 4)
        b.add_trajectory(states, times, controls=np.zeros(3), batch_index=i)
    assert b.get_batch_count() == 3
    assert np.array_equal(b.get_states(0), np.full((4, 2), 0.0))
    assert np.array_equal(b.get_states(2), np.full((4, 2), 2.0))
    agg = b.get_states()
    assert agg.shape == (3, 4, 2)
    assert np.array_equal(b.get_times(), np.linspace(0, 0.3, 4))


def test_batch_container_auto_index():
    b = BatchResultContainer()
    b.add_trajectory(np.zeros((2, 2)), np.zeros(2))
    b.add_trajectory(np.ones((2, 2)), np.zeros(2))
    assert b.get_batch_count() == 2


def test_processor_statistics_and_metrics():
    states, times, controls = _traj()
    p = ResultProcessor()
    stats = p.compute_statistics(states)
    assert np.array_equal(stats["mean"], np.mean(states, axis=0))
    assert stats["trajectory_length"] == len(states)
    assert np.array_equal(stats["final_state"], states[-1])
    energy = p.compute_energy_metrics(states)
    assert set(energy) == {"avg_kinetic", "avg_potential", "avg_total", "energy_variation"}
    ctrl = p.compute_control_metrics(controls)
    assert ctrl["max_control"] == float(np.max(np.abs(controls)))


def test_processor_analyze_trajectory():
    states, times, controls = _traj()
    c = StandardResultContainer()
    c.add_trajectory(states, times, controls=controls)
    analysis = ResultProcessor().analyze_trajectory(c)
    assert "state_statistics" in analysis
    assert "energy_metrics" in analysis
    assert "control_metrics" in analysis
    assert analysis["time_step"] == pytest.approx(0.1)


def test_processor_empty_inputs():
    p = ResultProcessor()
    assert p.compute_energy_metrics(np.array([])) == {}
    assert p.compute_control_metrics(np.array([])) == {}


def test_validator_basic_structure_good_and_bad():
    states, times, _ = _traj()
    c = StandardResultContainer()
    c.add_trajectory(states, times)
    ok, errors = ResultValidator().validate_basic_structure(c)
    assert ok and errors == []
    bad = StandardResultContainer()
    bad.add_trajectory(np.array([[np.nan, 1.0]]), np.array([0.0]))
    ok2, errors2 = ResultValidator().validate_basic_structure(bad)
    assert not ok2
    assert any("Non-finite" in e for e in errors2)


def test_validator_time_consistency():
    v = ResultValidator()
    ok, _ = v.validate_time_consistency(np.linspace(0, 1, 11))
    assert ok
    bad_ok, errs = v.validate_time_consistency(np.array([0.0, 0.0, 1.0]))
    assert not bad_ok


def test_validator_comprehensive():
    states, times, _ = _traj()
    c = StandardResultContainer()
    c.add_trajectory(states, times)
    report = ResultValidator().comprehensive_validation(c)
    assert report["valid"] is True
    assert report["basic_structure"]["valid"] is True


def test_csv_exporter_roundtrip():
    states, times, controls = _traj(n=4, dim=3)
    c = StandardResultContainer()
    c.add_trajectory(states, times, controls=controls)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "r.csv")
        CSVExporter().export(c, path)
        with open(path, newline="") as f:
            rows = list(csv.reader(f))
    assert rows[0] == ["time", "state_0", "state_1", "state_2", "control"]
    assert len(rows) == 1 + len(times)
    assert float(rows[1][0]) == pytest.approx(times[0])
    assert float(rows[1][1]) == pytest.approx(states[0, 0])


def test_hdf5_exporter_requires_h5py():
    try:
        import h5py  # noqa: F401
    except ImportError:
        states, times, _ = _traj()
        c = StandardResultContainer()
        c.add_trajectory(states, times)
        with tempfile.TemporaryDirectory() as d:
            with pytest.raises(ImportError):
                HDF5Exporter().export(c, os.path.join(d, "r.h5"))
    else:
        pytest.skip("h5py installed; ImportError path not exercised")
