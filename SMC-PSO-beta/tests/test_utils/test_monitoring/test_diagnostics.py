#======================================================================================
# tests/test_utils/test_monitoring/test_diagnostics.py
#======================================================================================
"""Unit tests for the 9-step DiagnosticChecklist (top-down, stop-at-first-fail)."""
from src.utils.monitoring.realtime.diagnostics import (
    DiagnosticChecklist, InstabilityType,
)


def test_authority_diagnosis_stops_at_step3():
    # Persistent saturation -> Authority. No condition data so step 2 passes.
    episode = {'control_forces': [200.0] * 200, 'max_force': 150.0, 'dt': 0.01}
    checklist = DiagnosticChecklist()
    cause, history = checklist.run_full_diagnostic(episode)
    assert cause == InstabilityType.AUTHORITY
    assert history[-1].step == 3
    assert history[-1].fail_rule_triggered is True
    # stop-at-first-fail: should not run steps 4..9
    assert len(history) == 3


def test_unknown_when_no_fail_rules():
    cause, history = DiagnosticChecklist().run_full_diagnostic({})
    assert cause == InstabilityType.UNKNOWN
    assert len(history) == 9
    assert all(not r.fail_rule_triggered for r in history)


def test_summary_reports_primary_cause():
    episode = {'control_forces': [200.0] * 200, 'max_force': 150.0, 'dt': 0.01}
    checklist = DiagnosticChecklist()
    checklist.run_full_diagnostic(episode)
    summary = checklist.get_diagnostic_summary()
    assert summary['primary_cause'] == InstabilityType.AUTHORITY.value
    assert summary['failed_steps'] >= 1
    assert 0.0 <= summary['diagnosis_confidence'] <= 1.0
