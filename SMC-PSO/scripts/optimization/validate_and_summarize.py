#==========================================================================================\\\
#=================== scripts/optimization/validate_and_summarize.py ======================\\\
#==========================================================================================\\\

"""
Comprehensive validation and summary generation for Issue #12 PSO results.
Validates all completed PSO optimizations and generates final summary.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import json  # noqa: E402
import numpy as np  # noqa: E402
from datetime import datetime  # noqa: E402
from typing import Dict, List  # noqa: E402
from scipy.fft import fft, fftfreq  # noqa: E402

from src.config import load_config  # noqa: E402
from src.controllers.factory import create_controller  # noqa: E402
from src.plant.models.dynamics import DoubleInvertedPendulum  # noqa: E402


def load_pso_results(controller: str) -> Dict:
    """Load PSO results from JSON file."""
    json_file = Path(f'gains_{controller}_chattering.json')

    if not json_file.exists():
        return {'exists': False, 'controller': controller}

    with open(json_file) as f:
        data = json.load(f)

    data['exists'] = True
    return data


def validate_gains(controller_type: str, gains: List[float]) -> Dict:
    """Validate gains by simulation and compute all metrics."""

    config = load_config('config.yaml')
    dynamics = DoubleInvertedPendulum(config=config.physics)

    # Create controller with these gains
    temp_config = config.model_copy(deep=True)

    if hasattr(temp_config.controller_defaults, controller_type):
        default_ctrl = getattr(temp_config.controller_defaults, controller_type)
        updated = default_ctrl.model_copy(update={'gains': gains})
        setattr(temp_config.controller_defaults, controller_type, updated)

    if hasattr(temp_config.controllers, controller_type):
        ctrl = getattr(temp_config.controllers, controller_type)
        updated = ctrl.model_copy(update={'gains': gains})
        setattr(temp_config.controllers, controller_type, updated)

    controller = create_controller(controller_type=controller_type, config=temp_config)

    # Initialize
    state_vars = controller.initialize_state() if hasattr(controller, 'initialize_state') else ()
    history = controller.initialize_history() if hasattr(controller, 'initialize_history') else {}

    # Simulate
    dt = 0.01
    t_sim = 15.0
    n_steps = int(t_sim / dt)

    state = np.array([0.0, 0.02, 0.02, 0.0, 0.0, 0.0])
    control_hist = []
    state_hist = []

    for i in range(n_steps):
        state_hist.append(state.copy())

        # Compute control
        try:
            result = controller.compute_control(state, state_vars, history)

            # Extract control
            if hasattr(result, 'u'):
                control = result.u
                state_vars = getattr(result, 'state', state_vars)
                history = getattr(result, 'history', history)
            elif isinstance(result, np.ndarray):
                control = float(result.flat[0])
            elif isinstance(result, tuple):
                control = float(result[0])
                if len(result) > 1:
                    state_vars = result[1]
                if len(result) > 2:
                    history = result[2]
            else:
                control = float(result)
        except Exception as e:
            return {'success': False, 'error': str(e), 'step': i}

        control_hist.append(control)

        # Update dynamics
        state = dynamics.sanitize_state(state)
        dyn_result = dynamics.compute_dynamics(state, np.array([control]))

        if not dyn_result.success:
            return {'success': False, 'error': 'Dynamics failed', 'step': i}

        state = state + dyn_result.state_derivative * dt

        if not np.all(np.isfinite(state)) or np.any(np.abs(state) > 1e3):
            return {'success': False, 'error': 'State diverged', 'step': i}

    # Compute metrics (exactly matching PSO)
    control_array = np.array(control_hist)
    state_array = np.array(state_hist)

    # Tracking error
    tracking_rms = float(np.sqrt(np.mean(state_array[:, 1:3]**2)))

    # Chattering index
    control_deriv = np.gradient(control_array, dt)
    time_domain = float(np.sqrt(np.mean(control_deriv**2)))

    spectrum = np.abs(fft(control_array))
    freqs = fftfreq(len(control_array), d=dt)
    hf_mask = np.abs(freqs) > 10.0
    hf_power = np.sum(spectrum[hf_mask]) if np.any(hf_mask) else 0.0
    total_power = np.sum(spectrum) + 1e-12
    freq_domain = float(hf_power / total_power)

    chattering_index = 0.7 * time_domain + 0.3 * freq_domain

    # Control effort
    control_rms = float(np.sqrt(np.mean(control_array**2)))

    return {
        'success': True,
        'tracking_error_rms': tracking_rms,
        'chattering_index': chattering_index,
        'time_domain_index': time_domain,
        'freq_domain_index': freq_domain,
        'control_effort_rms': control_rms
    }


def main():
    print("="*80)
    print("ISSUE #12 - PSO OPTIMIZATION VALIDATION & SUMMARY")
    print("="*80)
    print()

    controllers = ['classical_smc', 'adaptive_smc', 'sta_smc', 'hybrid_adaptive_sta_smc']

    results = {}

    for ctrl in controllers:
        print(f"Validating {ctrl}...")

        # Load PSO results
        pso_data = load_pso_results(ctrl)

        if not pso_data['exists']:
            print("  [SKIP] No results file found\n")
            results[ctrl] = {'status': 'NO_RESULTS'}
            continue

        gains = pso_data['gains']
        print(f"  Gains: {gains}")

        # Validate by simulation
        validation = validate_gains(ctrl, gains)

        if not validation['success']:
            print(f"  [FAIL] Validation failed: {validation.get('error', 'Unknown')}")
            print(f"         at step {validation.get('step', '?')}\n")
            results[ctrl] = {'status': 'VALIDATION_FAILED', 'validation': validation}
            continue

        # Check criteria
        chat = validation['chattering_index']
        track = validation['tracking_error_rms']

        chat_pass = chat < 2.0
        track_pass = track < 0.1

        print(f"  Chattering: {chat:.3f} {'[PASS]' if chat_pass else '[FAIL]'} (target < 2.0)")
        print(f"  Tracking:   {track:.4f} {'[PASS]' if track_pass else '[FAIL]'} (target < 0.1)")
        print(f"  Control RMS: {validation['control_effort_rms']:.2f} N")
        print()

        results[ctrl] = {
            'status': 'VALIDATED',
            'gains': gains,
            'metrics': validation,
            'chat_pass': chat_pass,
            'track_pass': track_pass,
            'pso_data': pso_data
        }

    # Generate summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()

    passed = sum(1 for r in results.values() if r.get('status') == 'VALIDATED' and r.get('chat_pass'))
    total = len([r for r in results.values() if r.get('status') != 'NO_RESULTS'])

    print(f"Controllers optimized: {total}/4")
    print(f"Chattering target met: {passed}/{total}")
    print()

    print("Individual Results:")
    for ctrl, data in results.items():
        if data['status'] == 'NO_RESULTS':
            print(f"  {ctrl:30s}: NO RESULTS")
        elif data['status'] == 'VALIDATION_FAILED':
            print(f"  {ctrl:30s}: VALIDATION FAILED")
        else:
            chat = data['metrics']['chattering_index']
            status = 'PASS' if data['chat_pass'] else 'FAIL'
            print(f"  {ctrl:30s}: chattering={chat:7.3f} [{status}]")

    print()
    print("="*80)

    # Save summary
    summary_file = f"docs/issue_12_validation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Detailed results saved to: {summary_file}")

    return results


if __name__ == '__main__':
    main()