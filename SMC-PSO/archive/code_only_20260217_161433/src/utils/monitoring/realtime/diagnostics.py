#======================================================================================\\\
#======================== src/utils/monitoring/diagnostics.py =========================\\\
#======================================================================================\\\

"""
Diagnostic checklist instrumentation for stability analysis.

Implements the 9-step diagnostic checklist from Issue #1 resolution plan
to systematically classify instability causes and provide actionable diagnosis.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import time
from dataclasses import dataclass


class InstabilityType(Enum):
    """Classification of instability root causes."""
    NUMERICAL = "numerical"
    AUTHORITY = "authority"
    SLIDING_REACHABILITY = "sliding/reachability"
    TIMING_NOISE = "timing/noise"
    MISMATCH_TUNING = "mismatch/tuning"
    ADAPTATION = "adaptation"
    PSO_OBJECTIVE = "pso_objective"
    MODE_HANDOFF = "mode_handoff"
    UNKNOWN = "unknown"


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check."""
    step: int
    name: str
    passed: bool
    primary_cause: Optional[InstabilityType]
    details: Dict[str, Any]
    timestamp: float
    fail_rule_triggered: bool = False


class DiagnosticChecklist:
    """9-step diagnostic checklist for systematic instability classification.

    Implements the priority-ranked diagnostic checklist from Issue #1 resolution:
    "Run top-down, stop at first fail"
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize diagnostic checklist.

        Parameters
        ----------
        config : dict, optional
            Diagnostic configuration parameters
        """
        if config is None:
            config = {}

        self.config = config
        self.history: List[DiagnosticResult] = []
        self.current_diagnosis: Optional[InstabilityType] = None
        self.episode_data: Dict[str, Any] = {}

        # Diagnostic thresholds
        self.thresholds = {
            'condition_spike_ratio': config.get('condition_spike_ratio', 100.0),
            'frequent_fallback_rate': config.get('frequent_fallback_rate', 0.1),
            'authority_duty_threshold': config.get('authority_duty_threshold', 0.25),
            'rate_limit_threshold': config.get('rate_limit_threshold', 0.1),
            'ldr_threshold': config.get('ldr_threshold', 0.95),
            'sigma_dot_sigma_threshold': config.get('sigma_dot_sigma_threshold', 0.0),
            'envelope_violation_correlation': config.get('envelope_violation_correlation', 0.7),
            'adaptation_bounds_check': config.get('adaptation_bounds_check', True),
            'pso_score_inconsistency': config.get('pso_score_inconsistency', 0.3)
        }

    def run_full_diagnostic(self, episode_data: Dict[str, Any]) -> Tuple[InstabilityType, List[DiagnosticResult]]:
        """Run complete diagnostic checklist on episode data.

        Parameters
        ----------
        episode_data : dict
            Complete episode simulation data including:
            - states, controls, sigma values
            - condition numbers, fallback events
            - timing data, noise levels
            - model comparison results
            - adaptation parameters, PSO scores

        Returns
        -------
        tuple
            (primary_cause, diagnostic_results)
        """
        self.episode_data = episode_data
        self.history.clear()
        self.current_diagnosis = None

        # Run diagnostic steps in priority order
        diagnostic_steps = [
            self._step1_reproduce_classify,
            self._step2_numerical_conditioning,
            self._step3_actuator_authority,
            self._step4_sliding_reachability,
            self._step5_timing_noise,
            self._step6_model_mismatch,
            self._step7_adaptation_safeguards,
            self._step8_pso_objective,
            self._step9_mode_handoff
        ]

        for step_num, diagnostic_func in enumerate(diagnostic_steps, 1):
            result = diagnostic_func(step_num)
            self.history.append(result)

            # Stop at first fail rule as specified in resolution plan
            if result.fail_rule_triggered:
                self.current_diagnosis = result.primary_cause
                break

        # If no fail rule triggered, mark as unknown
        if self.current_diagnosis is None:
            self.current_diagnosis = InstabilityType.UNKNOWN

        return self.current_diagnosis, self.history

    def _step1_reproduce_classify(self, step: int) -> DiagnosticResult:
        """Step 1: Reproduce & classify (baseline triage)."""

        # Extract episode symptoms
        has_nan_inf = self.episode_data.get('has_nan_inf', False)
        has_inversion_alert = self.episode_data.get('has_inversion_alert', False)
        has_saturation = self.episode_data.get('has_saturation', False)
        sigma_growth = self.episode_data.get('sigma_growth', False)
        timing_spikes = self.episode_data.get('timing_spikes', False)

        symptoms = {
            'nan_inf_events': has_nan_inf,
            'inversion_alerts': has_inversion_alert,
            'saturation_events': has_saturation,
            'sigma_growth': sigma_growth,
            'timing_spikes': timing_spikes
        }

        # Baseline triage passes if we can categorize symptoms
        anomalous_symptoms = sum(symptoms.values())
        passed = anomalous_symptoms > 0  # Should have at least one symptom to diagnose

        return DiagnosticResult(
            step=step,
            name="Reproduce & classify (baseline triage)",
            passed=passed,
            primary_cause=None,  # This step doesn't determine cause
            details=symptoms,
            timestamp=time.time(),
            fail_rule_triggered=False
        )

    def _step2_numerical_conditioning(self, step: int) -> DiagnosticResult:
        """Step 2: Numerical conditioning gate."""

        condition_numbers = self.episode_data.get('condition_numbers', [])
        fallback_events = self.episode_data.get('fallback_events', [])
        sigma_values = self.episode_data.get('sigma_values', [])

        # Check for condition number spikes before sigma growth
        condition_spike_before_sigma = False
        frequent_fallbacks = False

        if condition_numbers and sigma_values:
            # Find first significant sigma growth
            sigma_norms = [np.linalg.norm(s) for s in sigma_values]
            sigma_growth_idx = self._find_growth_onset(sigma_norms)

            if sigma_growth_idx is not None and sigma_growth_idx < len(condition_numbers):
                # Check if condition number spiked before sigma growth
                pre_growth_conditions = condition_numbers[:sigma_growth_idx]
                if pre_growth_conditions:
                    max_pre_condition = max(pre_growth_conditions)
                    mean_condition = np.mean(condition_numbers)
                    condition_spike_before_sigma = max_pre_condition > mean_condition * self.thresholds['condition_spike_ratio']

        # Check for frequent fallbacks
        if fallback_events:
            fallback_rate = len(fallback_events) / len(condition_numbers) if condition_numbers else 0
            frequent_fallbacks = fallback_rate > self.thresholds['frequent_fallback_rate']

        # Fail rule: κ spikes before σ growth OR frequent fallbacks → Primary: Numerical
        fail_rule = condition_spike_before_sigma or frequent_fallbacks

        details = {
            'condition_spike_before_sigma': condition_spike_before_sigma,
            'frequent_fallbacks': frequent_fallbacks,
            'fallback_rate': len(fallback_events) / max(1, len(condition_numbers)),
            'max_condition_number': max(condition_numbers) if condition_numbers else 0,
            'mean_condition_number': np.mean(condition_numbers) if condition_numbers else 0
        }

        return DiagnosticResult(
            step=step,
            name="Numerical conditioning gate",
            passed=not fail_rule,
            primary_cause=InstabilityType.NUMERICAL if fail_rule else None,
            details=details,
            timestamp=time.time(),
            fail_rule_triggered=fail_rule
        )

    def _step3_actuator_authority(self, step: int) -> DiagnosticResult:
        """Step 3: Actuator authority & rate limits."""

        control_forces = self.episode_data.get('control_forces', [])
        max_force = self.episode_data.get('max_force', 150.0)
        dt = self.episode_data.get('dt', 0.01)

        # Compute saturation duty and rate limit hits
        saturation_duty = 0.0
        rate_limit_hits = 0.0

        if control_forces:
            # Calculate saturation duty (post-transient)
            transient_samples = int(1.0 / dt)  # 1 second transient
            post_transient_forces = control_forces[transient_samples:] if len(control_forces) > transient_samples else control_forces

            if post_transient_forces:
                saturated_samples = sum(1 for f in post_transient_forces if abs(f) >= max_force * 0.99)
                saturation_duty = saturated_samples / len(post_transient_forces)

                # Calculate rate limit hits
                force_rates = [abs((control_forces[i] - control_forces[i-1]) / dt)
                             for i in range(1, len(control_forces))]
                max_rate = max_force / dt
                rate_hits = sum(1 for r in force_rates if r >= max_rate * 0.99)
                rate_limit_hits = rate_hits / len(force_rates) if force_rates else 0

        # Fail rule: duty persistently > 20–30% or frequent rate-limit clips → Primary: Authority
        persistent_saturation = saturation_duty > self.thresholds['authority_duty_threshold']
        frequent_rate_clips = rate_limit_hits > self.thresholds['rate_limit_threshold']
        fail_rule = persistent_saturation or frequent_rate_clips

        details = {
            'saturation_duty': saturation_duty,
            'rate_limit_hits': rate_limit_hits,
            'persistent_saturation': persistent_saturation,
            'frequent_rate_clips': frequent_rate_clips,
            'max_force': max_force
        }

        return DiagnosticResult(
            step=step,
            name="Actuator authority & rate limits",
            passed=not fail_rule,
            primary_cause=InstabilityType.AUTHORITY if fail_rule else None,
            details=details,
            timestamp=time.time(),
            fail_rule_triggered=fail_rule
        )

    def _step4_sliding_reachability(self, step: int) -> DiagnosticResult:
        """Step 4: Sliding reachability (Lyapunov trend)."""

        sigma_values = self.episode_data.get('sigma_values', [])
        sigma_dot_values = self.episode_data.get('sigma_dot_values', [])
        dt = self.episode_data.get('dt', 0.01)

        # Compute LDR and average (σ·σ̇) over rolling windows post-transient
        ldr = 1.0
        avg_sigma_dot_sigma = 0.0

        if sigma_values and sigma_dot_values:
            transient_samples = int(1.0 / dt)  # 1 second transient
            post_transient_sigma = sigma_values[transient_samples:] if len(sigma_values) > transient_samples else sigma_values
            post_transient_sigma_dot = sigma_dot_values[transient_samples:] if len(sigma_dot_values) > transient_samples else sigma_dot_values

            if len(post_transient_sigma) >= 2:
                # Compute LDR
                lyapunov_vals = [0.5 * np.sum(s**2) for s in post_transient_sigma]
                decreases = np.diff(lyapunov_vals)
                decreasing_count = np.sum(decreases < 0)
                ldr = decreasing_count / len(decreases) if decreases.size > 0 else 1.0

                # Compute average σ·σ̇
                if len(post_transient_sigma_dot) > 0:
                    min_len = min(len(post_transient_sigma), len(post_transient_sigma_dot))
                    sigma_dot_sigma_products = [
                        np.sum(post_transient_sigma[i] * post_transient_sigma_dot[i])
                        for i in range(min_len)
                    ]
                    avg_sigma_dot_sigma = np.mean(sigma_dot_sigma_products)

        # Fail rule: LDR falls or ⟨σ·σ̇⟩ > 0 → Primary: surface/gains/sampling
        ldr_fails = ldr < self.thresholds['ldr_threshold']
        sigma_dot_sigma_positive = avg_sigma_dot_sigma > self.thresholds['sigma_dot_sigma_threshold']
        fail_rule = ldr_fails or sigma_dot_sigma_positive

        details = {
            'ldr': ldr,
            'avg_sigma_dot_sigma': avg_sigma_dot_sigma,
            'ldr_fails': ldr_fails,
            'sigma_dot_sigma_positive': sigma_dot_sigma_positive,
            'ldr_threshold': self.thresholds['ldr_threshold']
        }

        return DiagnosticResult(
            step=step,
            name="Sliding reachability (Lyapunov trend)",
            passed=not fail_rule,
            primary_cause=InstabilityType.SLIDING_REACHABILITY if fail_rule else None,
            details=details,
            timestamp=time.time(),
            fail_rule_triggered=fail_rule
        )

    def _step5_timing_noise(self, step: int) -> DiagnosticResult:
        """Step 5: Timing/latency/noise envelope."""

        timing_data = self.episode_data.get('timing_data', [])
        noise_levels = self.episode_data.get('noise_levels', [])
        ldr_dips = self.episode_data.get('ldr_dips', [])
        chattering_events = self.episode_data.get('chattering_events', [])

        # Correlate jitter/latency spikes and noise RMS with LDR dips/chattering
        envelope_violations = self.episode_data.get('envelope_violations', [])
        instability_events = len(ldr_dips) + len(chattering_events)

        correlation = 0.0
        if envelope_violations and instability_events > 0:
            # Simple correlation: ratio of aligned events
            aligned_events = self.episode_data.get('aligned_timing_instability_events', 0)
            correlation = aligned_events / max(len(envelope_violations), instability_events)

        # Fail rule: envelope violations align with instability → Primary: timing/noise
        fail_rule = correlation > self.thresholds['envelope_violation_correlation']

        details = {
            'envelope_violations': len(envelope_violations),
            'instability_events': instability_events,
            'correlation': correlation,
            'timing_spikes': len([t for t in timing_data if t > 2 * np.mean(timing_data)]) if timing_data else 0,
            'noise_rms': np.sqrt(np.mean(np.array(noise_levels)**2)) if noise_levels else 0
        }

        return DiagnosticResult(
            step=step,
            name="Timing/latency/noise envelope",
            passed=not fail_rule,
            primary_cause=InstabilityType.TIMING_NOISE if fail_rule else None,
            details=details,
            timestamp=time.time(),
            fail_rule_triggered=fail_rule
        )

    def _step6_model_mismatch(self, step: int) -> DiagnosticResult:
        """Step 6: Model-mismatch A/B."""

        # A/B test results: (a) simplified, (b) full, (c) full w/o noise/latency
        simplified_stable = self.episode_data.get('simplified_stable', True)
        full_stable = self.episode_data.get('full_stable', True)
        full_no_noise_stable = self.episode_data.get('full_no_noise_stable', True)

        # Fail rule: stable (a) but not (b)/(c) → Primary: mismatch
        fail_rule = simplified_stable and (not full_stable or not full_no_noise_stable)

        details = {
            'simplified_stable': simplified_stable,
            'full_stable': full_stable,
            'full_no_noise_stable': full_no_noise_stable,
            'model_mismatch_detected': fail_rule
        }

        return DiagnosticResult(
            step=step,
            name="Model-mismatch A/B",
            passed=not fail_rule,
            primary_cause=InstabilityType.MISMATCH_TUNING if fail_rule else None,
            details=details,
            timestamp=time.time(),
            fail_rule_triggered=fail_rule
        )

    def _step7_adaptation_safeguards(self, step: int) -> DiagnosticResult:
        """Step 7: Adaptation safeguards sanity."""

        adaptive_gains = self.episode_data.get('adaptive_gains', [])
        gain_bounds = self.episode_data.get('gain_bounds', {})

        # Check for pinning/ratcheting/freezing in adaptive gains
        pinning_detected = False
        ratcheting_detected = False
        freezing_detected = False

        if adaptive_gains and gain_bounds:
            for gain_history in adaptive_gains:
                if len(gain_history) > 10:
                    # Check for pinning (stuck at bounds)
                    min_bound = gain_bounds.get('min', 0)
                    max_bound = gain_bounds.get('max', 100)
                    at_min = sum(1 for g in gain_history[-10:] if abs(g - min_bound) < 0.01)
                    at_max = sum(1 for g in gain_history[-10:] if abs(g - max_bound) < 0.01)
                    if at_min > 8 or at_max > 8:  # 80% of recent samples at bound
                        pinning_detected = True

                    # Check for ratcheting (monotonic increase/decrease)
                    recent_gains = gain_history[-10:]
                    monotonic_inc = all(recent_gains[i] <= recent_gains[i+1] for i in range(len(recent_gains)-1))
                    monotonic_dec = all(recent_gains[i] >= recent_gains[i+1] for i in range(len(recent_gains)-1))
                    if monotonic_inc or monotonic_dec:
                        ratcheting_detected = True

                    # Check for freezing (no change)
                    if np.std(recent_gains) < 0.001:  # Very small variation
                        freezing_detected = True

        # Fail rule: pinning/ratcheting/freezing → Primary: adaptation config
        fail_rule = pinning_detected or ratcheting_detected or freezing_detected

        details = {
            'pinning_detected': pinning_detected,
            'ratcheting_detected': ratcheting_detected,
            'freezing_detected': freezing_detected,
            'gain_histories_analyzed': len(adaptive_gains)
        }

        return DiagnosticResult(
            step=step,
            name="Adaptation safeguards sanity",
            passed=not fail_rule,
            primary_cause=InstabilityType.ADAPTATION if fail_rule else None,
            details=details,
            timestamp=time.time(),
            fail_rule_triggered=fail_rule
        )

    def _step8_pso_objective(self, step: int) -> DiagnosticResult:
        """Step 8: PSO objective / distribution audit."""

        failing_trajectory_score = self.episode_data.get('failing_trajectory_score', 0)
        good_trajectory_scores = self.episode_data.get('good_trajectory_scores', [])
        ranking_consistency = self.episode_data.get('ranking_consistency', True)

        # Re-score failing trajectory; check if bad runs still score well
        bad_scores_well = False
        ranking_flips = False

        if good_trajectory_scores:
            avg_good_score = np.mean(good_trajectory_scores)
            # Bad run scores well if it's within threshold of good runs
            bad_scores_well = failing_trajectory_score > avg_good_score * (1 - self.thresholds['pso_score_inconsistency'])

        ranking_flips = not ranking_consistency

        # Fail rule: bad runs still score well OR ranking flips under mild broadening → Primary: objective mis-spec
        fail_rule = bad_scores_well or ranking_flips

        details = {
            'failing_trajectory_score': failing_trajectory_score,
            'avg_good_score': np.mean(good_trajectory_scores) if good_trajectory_scores else 0,
            'bad_scores_well': bad_scores_well,
            'ranking_flips': ranking_flips,
            'score_inconsistency_threshold': self.thresholds['pso_score_inconsistency']
        }

        return DiagnosticResult(
            step=step,
            name="PSO objective / distribution audit",
            passed=not fail_rule,
            primary_cause=InstabilityType.PSO_OBJECTIVE if fail_rule else None,
            details=details,
            timestamp=time.time(),
            fail_rule_triggered=fail_rule
        )

    def _step9_mode_handoff(self, step: int) -> DiagnosticResult:
        """Step 9: Mode-handoff checks (if still unexplained)."""

        mode_transitions = self.episode_data.get('mode_transitions', [])
        state_discontinuities = self.episode_data.get('state_discontinuities', [])
        sigma_discontinuities = self.episode_data.get('sigma_discontinuities', [])

        # Verify phase-aligned state/σ across swing-up → stabilize
        handoff_issues = False
        if mode_transitions:
            # Check for discontinuities at transition points
            for transition_idx in mode_transitions:
                # Look for discontinuities around transition
                if any(abs(idx - transition_idx) < 10 for idx in state_discontinuities):
                    handoff_issues = True
                if any(abs(idx - transition_idx) < 10 for idx in sigma_discontinuities):
                    handoff_issues = True

        # This step only triggers if we reach it (no previous fail rules)
        fail_rule = handoff_issues

        details = {
            'mode_transitions': len(mode_transitions),
            'state_discontinuities': len(state_discontinuities),
            'sigma_discontinuities': len(sigma_discontinuities),
            'handoff_issues': handoff_issues
        }

        return DiagnosticResult(
            step=step,
            name="Mode-handoff checks",
            passed=not fail_rule,
            primary_cause=InstabilityType.MODE_HANDOFF if fail_rule else None,
            details=details,
            timestamp=time.time(),
            fail_rule_triggered=fail_rule
        )

    def _find_growth_onset(self, values: List[float], threshold_factor: float = 2.0) -> Optional[int]:
        """Find the index where significant growth begins."""
        if len(values) < 10:
            return None

        # Use moving average to find growth onset
        window = 5
        baseline = np.mean(values[:window])

        for i in range(window, len(values)):
            current_avg = np.mean(values[i-window:i])
            if current_avg > baseline * threshold_factor:
                return i

        return None

    def get_diagnostic_summary(self) -> Dict[str, Any]:
        """Get summary of diagnostic results."""
        if not self.history:
            return {'status': 'no_diagnosis', 'primary_cause': None}

        passed_steps = [r for r in self.history if r.passed]
        failed_steps = [r for r in self.history if not r.passed]

        return {
            'primary_cause': self.current_diagnosis.value if self.current_diagnosis else 'unknown',
            'total_steps': len(self.history),
            'passed_steps': len(passed_steps),
            'failed_steps': len(failed_steps),
            'first_failure_step': failed_steps[0].step if failed_steps else None,
            'diagnosis_confidence': len(passed_steps) / len(self.history),
            'timestamp': time.time()
        }