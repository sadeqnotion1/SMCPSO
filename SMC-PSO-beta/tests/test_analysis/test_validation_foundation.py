#======================================================================================
#======== tests/test_analysis/test_validation_foundation.py (M8-S3a) ==================
#======================================================================================

"""Regression tests for the analysis.validation foundation (M8-S3a).

Covers the public surface (StatisticalBenchmarks) plus the foundation modules
core / metrics / statistics that statistical_benchmarks delegates to.

Scope note: the heavier standalone modules (benchmarking, cross_validation,
monte_carlo, statistical_tests) are ported in M8-S3b and tested separately.

Finding M8-S3a-1 (documented below): the convenience wrappers
`run_trials_with_advanced_statistics` and `compare_controllers` perform a
function-local import of names that do not exist in `.statistics`
(perform_statistical_tests, compute_t_confidence_intervals,
compute_bootstrap_confidence_intervals, compare_metric_distributions) and
therefore raise ImportError when called. This is a pre-existing latent defect
ported faithfully; the test below pins that behaviour so it cannot regress
silently.
"""

import numpy as np
import pytest

from src.analysis.validation import StatisticalBenchmarks
from src.analysis.validation.core import (
    TrialConfiguration,
    TrialResult,
    TrialBatch,
    validate_trial_configuration,
    run_multiple_trials,
    compare_trial_batches,
    mock_trial_function,
)
from src.analysis.validation.metrics import compute_basic_metrics
from src.analysis.validation.statistics import (
    compute_basic_confidence_intervals,
    statistical_summary,
)
from src.analysis.validation import statistical_benchmarks as sb


def test_surface_export_is_class():
    assert isinstance(StatisticalBenchmarks, type)
    # Instantiable with an optional seed.
    inst = StatisticalBenchmarks(random_seed=123)
    assert inst is not None


def test_foundation_symbols_importable():
    for fn in (validate_trial_configuration, run_multiple_trials,
               compare_trial_batches, mock_trial_function,
               compute_basic_metrics, compute_basic_confidence_intervals,
               statistical_summary):
        assert callable(fn)


def test_compute_basic_metrics_known_values():
    data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    m = compute_basic_metrics(data)
    assert m['mean'] == pytest.approx(3.0)
    assert m['std'] == pytest.approx(np.std(data))
    assert m['min'] == pytest.approx(1.0)
    assert m['max'] == pytest.approx(5.0)
    assert m['median'] == pytest.approx(3.0)
    assert m['count'] == 5


def test_compute_basic_metrics_empty():
    m = compute_basic_metrics(np.array([]))
    assert m['count'] == 0
    assert m['mean'] == 0.0 and m['std'] == 0.0


def test_confidence_intervals_bracket_mean():
    data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    ci = compute_basic_confidence_intervals(data, confidence_level=0.95)
    assert ci['mean'] == pytest.approx(3.0)
    assert ci['sample_size'] == 5
    assert ci['lower_bound'] < ci['mean'] < ci['upper_bound']
    assert ci['confidence_level'] == 0.95


def test_confidence_intervals_empty():
    ci = compute_basic_confidence_intervals(np.array([]))
    assert ci['mean'] == 0.0
    assert ci['lower_bound'] == 0.0 and ci['upper_bound'] == 0.0


def test_statistical_summary_keys():
    data = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    s = statistical_summary(data)
    for k in ('count', 'mean', 'std', 'min', 'max', 'median',
              'q25', 'q75', 'skewness', 'kurtosis',
              'confidence_interval', 'normality', 'outliers'):
        assert k in s
    assert s['count'] == 6
    assert s['mean'] == pytest.approx(3.5)


def test_validate_trial_configuration_valid():
    cfg = TrialConfiguration(name='ok', parameters={'a': 1}, repetitions=5)
    assert validate_trial_configuration(cfg) == []


def test_validate_trial_configuration_invalid():
    cfg = TrialConfiguration(name='   ', parameters={'a': 1},
                             repetitions=0, timeout=-1.0)
    errors = validate_trial_configuration(cfg)
    joined = ' | '.join(errors)
    assert 'name cannot be empty' in joined
    assert 'at least 1' in joined
    assert 'Timeout must be positive' in joined


def test_run_multiple_trials_with_mock_produces_batch():
    cfg = TrialConfiguration(name='mock', parameters={'duration': 1.0, 'tolerance': 0.1},
                             repetitions=6, parallel=False, random_seed=42)
    batch = run_multiple_trials(mock_trial_function, cfg)
    assert isinstance(batch, TrialBatch)
    assert len(batch.results) == 6
    assert all(isinstance(r, TrialResult) for r in batch.results)
    assert batch.success_rate == pytest.approx(1.0)
    vals = batch.get_metric_values('performance')
    assert len(vals) == 6
    summ = batch.get_summary_statistics('performance')
    assert 'mean' in summ


def test_run_multiple_trials_deterministic_with_seed():
    def make():
        cfg = TrialConfiguration(name='det', parameters={'duration': 1.0, 'tolerance': 0.1},
                                 repetitions=5, parallel=False, random_seed=7)
        return run_multiple_trials(mock_trial_function, cfg).get_metric_values('performance')
    a = make()
    b = make()
    assert np.allclose(a, b)


def test_compare_trial_batches():
    cfg1 = TrialConfiguration(name='b1', parameters={'duration': 1.0, 'tolerance': 0.1},
                              repetitions=5, parallel=False, random_seed=1)
    cfg2 = TrialConfiguration(name='b2', parameters={'duration': 1.0, 'tolerance': 0.1},
                              repetitions=5, parallel=False, random_seed=2)
    b1 = run_multiple_trials(mock_trial_function, cfg1)
    b2 = run_multiple_trials(mock_trial_function, cfg2)
    cmp = compare_trial_batches(b1, b2, 'performance')
    assert cmp['comparison_possible'] is True
    assert 'mean_difference' in cmp and 'relative_change' in cmp


def test_latent_advanced_wrappers_raise_importerror():
    # Documents finding M8-S3a-1: deferred import of undefined .statistics names.
    with pytest.raises(ImportError):
        sb.run_trials_with_advanced_statistics(lambda g: None, object())
    with pytest.raises(ImportError):
        sb.compare_controllers(lambda g: None, lambda g: None, object())
