#======================================================================================\\\
#============== tests/test_utils/monitoring/test_stability_monitoring.py ==============\\\
#======================================================================================\\\

"""
Test script for the stability monitoring system implementation.

Tests the Issue #1 resolution components:
- LDR monitoring
- Saturation monitoring
- Dynamics conditioning
- Diagnostic checklist
"""

import numpy as np
from src.utils.monitoring import (
    StabilityMonitoringSystem,
    DiagnosticChecklist,
    InstabilityType
)


def test_stability_monitoring_basic():
    """Test basic functionality of stability monitoring system."""
    print("Testing Stability Monitoring System...")

    # Create monitoring system with test configuration
    config = {
        'dt': 0.01,
        'max_force': 150.0,
        'ldr_threshold': 0.95,
        'duty_threshold': 0.2,
        'condition_threshold': 1e7
    }

    monitor = StabilityMonitoringSystem(config)

    # Simulate a test trajectory
    time_steps = 1000
    results = []

    print(f"Simulating {time_steps} time steps...")

    for t in range(time_steps):
        # Generate test data
        time_val = t * config['dt']

        # Create sliding surface that starts unstable then stabilizes
        if t < 100:  # Transient period
            sigma = np.array([0.5 * np.sin(0.1 * t), 0.3 * np.cos(0.1 * t)])
        elif t < 500:  # Unstable period (LDR violation)
            sigma = np.array([0.2 + 0.01 * t, 0.1 + 0.005 * t])  # Growing
        else:  # Stable period
            decay = np.exp(-(t - 500) * 0.01)
            sigma = np.array([0.1 * decay, 0.05 * decay])

        # Control force with saturation issues in middle period
        if 200 < t < 400:
            control_force = config['max_force'] * 0.95  # Near saturation
        else:
            control_force = 50.0 * np.sin(0.05 * t)

        # Mass matrix with occasional conditioning issues
        if 300 < t < 350:
            # Poor conditioning
            mass_matrix = np.array([[1.0, 0.999], [0.999, 1.0]])  # Nearly singular
        else:
            # Good conditioning
            mass_matrix = np.array([[2.0, 0.1], [0.1, 1.5]])

        # Update monitoring system
        result = monitor.update(
            sigma=sigma,
            control_force=control_force,
            mass_matrix=mass_matrix,
            used_fallback=(300 < t < 350)
        )

        results.append(result)

        # Print alerts (only first few and key transitions)
        if result['alert'] and (t < 105 or t % 100 == 0 or (300 < t < 355)):
            alert_types = []
            if result['ldr']['alert']:
                alert_types.append(f"LDR={result['ldr']['ldr']:.3f}")
            if result['saturation']['alert']:
                alert_types.append(f"SAT={result['saturation']['duty']:.3f}")
            if result['conditioning']['alert']:
                alert_types.append(f"COND={result['conditioning']['current_condition']:.2e}")

            print(f"  ALERT at t={time_val:.2f}s: {', '.join(alert_types)}")

    # Generate summary report
    report = monitor.get_stability_report()

    print("\n" + "="*60)
    print("STABILITY MONITORING REPORT")
    print("="*60)
    print(f"Total violations: {report['total_violations']}")
    print(f"Violation rate: {report['violation_rate']:.4f}")
    print(f"LDR alerts: {report['ldr_alert_count']}")
    print(f"Saturation violations: {report['saturation_violations']}")
    print(f"Conditioning violations: {report['conditioning_violations']}")
    print(f"Stability score: {report['stability_score']:.3f}")

    # Assert that the test ran successfully
    assert len(results) > 0, "Should have processed time steps"
    assert report['total_violations'] > 0, "Should have detected violations"


def test_diagnostic_checklist():
    """Test the diagnostic checklist functionality."""
    print("\nTesting Diagnostic Checklist...")

    # Create test episode data representing a numerical instability
    episode_data = {
        'has_nan_inf': False,
        'has_inversion_alert': True,
        'has_saturation': False,
        'sigma_growth': True,
        'timing_spikes': False,

        # Numerical conditioning data (should trigger Step 2)
        'condition_numbers': [1e5, 5e6, 1e8, 1e9, 1e10, 1e11],  # Spike before sigma growth
        'fallback_events': [2, 3, 4],  # Frequent fallbacks
        'sigma_values': [
            np.array([0.1, 0.1]),
            np.array([0.15, 0.12]),  # Growth starts here (index 1)
            np.array([0.3, 0.25]),
            np.array([0.6, 0.5]),
            np.array([1.2, 1.0]),
            np.array([2.4, 2.0])
        ],
        'sigma_dot_values': [
            np.array([0.0, 0.0]),
            np.array([5.0, 2.0]),
            np.array([15.0, 13.0]),
            np.array([30.0, 25.0]),
            np.array([60.0, 50.0])
        ],

        # Other data for subsequent steps
        'control_forces': [25.0, 30.0, 35.0, 40.0, 45.0, 50.0],
        'max_force': 150.0,
        'dt': 0.01,
        'timing_data': [0.008, 0.009, 0.010, 0.008, 0.009],
        'noise_levels': [0.01, 0.01, 0.01, 0.01, 0.01],
        'ldr_dips': [],
        'chattering_events': [],
        'envelope_violations': [],
        'aligned_timing_instability_events': 0,

        # Model comparison
        'simplified_stable': True,
        'full_stable': True,
        'full_no_noise_stable': True,

        # Adaptation data
        'adaptive_gains': [],
        'gain_bounds': {},

        # PSO data
        'failing_trajectory_score': 0.5,
        'good_trajectory_scores': [0.8, 0.9, 0.85, 0.88],
        'ranking_consistency': True,

        # Mode handoff data
        'mode_transitions': [],
        'state_discontinuities': [],
        'sigma_discontinuities': []
    }

    # Run diagnostic checklist
    checklist = DiagnosticChecklist()
    primary_cause, diagnostic_results = checklist.run_full_diagnostic(episode_data)

    print(f"Diagnostic Result: {primary_cause.value}")
    print("\nDiagnostic Steps:")

    for result in diagnostic_results:
        status = "PASS" if result.passed else "FAIL"
        if result.fail_rule_triggered:
            status += " (FAIL RULE TRIGGERED)"

        print(f"  Step {result.step}: {result.name} - {status}")
        if result.primary_cause:
            print(f"    Primary Cause: {result.primary_cause.value}")

    # Get summary
    summary = checklist.get_diagnostic_summary()
    print("\nDiagnostic Summary:")
    print(f"  Primary cause: {summary['primary_cause']}")
    print(f"  Steps completed: {summary['total_steps']}")
    print(f"  Passed: {summary['passed_steps']}, Failed: {summary['failed_steps']}")
    print(f"  Confidence: {summary['diagnosis_confidence']:.3f}")

    # Assert that diagnostic correctly identified numerical instability
    assert primary_cause == InstabilityType.NUMERICAL, f"Expected NUMERICAL instability, got {primary_cause}"


def test_integration_example():
    """Test integration with simulated controller data."""
    print("\nTesting Integration Example...")

    # Load configuration
    from src.config import load_config
    try:
        config = load_config("config.yaml", allow_unknown=True)
        stability_config = config.stability_monitoring.model_dump() if hasattr(config, 'stability_monitoring') else {}

        # Extract relevant parameters
        monitor_config = {
            'dt': config.simulation.dt,
            'max_force': config.controllers.classical_smc.max_force,
            'ldr_threshold': stability_config.get('ldr', {}).get('threshold', 0.95),
            'duty_threshold': stability_config.get('saturation', {}).get('duty_threshold', 0.2),
            'condition_threshold': stability_config.get('conditioning', {}).get('median_threshold', 1e7)
        }

        print("Successfully loaded configuration:")
        print(f"  dt: {monitor_config['dt']}")
        print(f"  max_force: {monitor_config['max_force']}")
        print(f"  LDR threshold: {monitor_config['ldr_threshold']}")
        print(f"  Duty threshold: {monitor_config['duty_threshold']}")

        # Assert configuration loaded successfully
        assert True, "Configuration loaded successfully"

    except Exception as e:
        print(f"Configuration test failed: {e}")
        assert False, f"Configuration loading failed: {e}"


# Remove main function - pytest will run test functions directly