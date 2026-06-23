#==========================================================================================\\\
#====================== scripts/optimization/validate_optimized_gains.py =================\\\
#==========================================================================================\\\

"""
Validate optimized controller gains from PSO optimization.

Loads optimized gains from JSON files and runs validation tests to ensure
chattering reduction targets are met.

Usage:
    python scripts/optimization/validate_optimized_gains.py --controller classical_smc
    python scripts/optimization/validate_optimized_gains.py --all
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import load_config  # noqa: E402
from src.controllers.factory import create_controller  # noqa: E402
from src.plant.models.simplified.dynamics import DoubleInvertedPendulum  # noqa: E402


def load_optimized_gains(controller: str) -> Optional[Dict]:
    """Load optimized gains from JSON file."""
    gain_file = Path(f"gains_{controller}_chattering.json")

    if not gain_file.exists():
        print(f"✗ Gains file not found: {gain_file}")
        return None

    with open(gain_file) as f:
        data = json.load(f)

    return data


def simulate_with_gains(controller_type: str, gains: List[float],
                       config, dt: float = 0.01, t_final: float = 15.0) -> Dict:
    """Simulate controller with given gains and compute metrics."""
    # Create controller
    controller_config = config['controllers'].get(controller_type, {})
    controller = create_controller(
        controller_type=controller_type,
        config=controller_config,
        gains=gains
    )

    # Create dynamics
    dynamics = DoubleInvertedPendulum(config['physics'])

    # Initial state: small disturbance
    state = np.array([0.0, 0.02, 0.02, 0.0, 0.0, 0.0])
    n_steps = int(t_final / dt)

    # Simulation
    control_output = 0.0
    control_history = []

    for step in range(n_steps):
        # Compute control
        control_output = controller.compute_control(state, control_output, control_history)
        control_history.append(control_output)

        # Update dynamics
        state = dynamics.sanitize_state(state)
        result = dynamics.compute_dynamics(state, np.array([control_output]))

        if not result.success:
            return {
                'success': False,
                'reason': 'Dynamics failed',
                'step': step
            }

        state = state + result.state_derivative * dt

    # Compute metrics
    control_array = np.array(control_history)

    # Chattering index (total variation)
    control_changes = np.abs(np.diff(control_array))
    total_variation = np.sum(control_changes) / len(control_changes)
    chattering_index = total_variation / dt

    # Tracking error
    angles = state[1:3]  # theta1, theta2
    tracking_error_rms = np.sqrt(np.mean(angles**2))

    return {
        'success': True,
        'chattering_index': float(chattering_index),
        'tracking_error_rms': float(tracking_error_rms),
        'final_state': state.tolist(),
        'control_range': [float(control_array.min()), float(control_array.max())]
    }


def validate_controller(controller_type: str, target_chattering: float = 2.0) -> bool:
    """Validate optimized gains for a controller."""
    print(f"\n{'='*60}")
    print(f"Validating: {controller_type}")
    print(f"{'='*60}")

    # Load optimized gains
    data = load_optimized_gains(controller_type)
    if data is None:
        return False

    optimized_gains = data.get('optimized_gains')
    reported_chattering = data.get('chattering_index')

    print(f"Optimized gains: {optimized_gains}")
    print(f"Reported chattering: {reported_chattering:.3f}")
    print()

    # Load config
    config = load_config('config.yaml', allow_unknown=False)

    # Run validation simulation
    print("Running validation simulation...")
    result = simulate_with_gains(controller_type, optimized_gains, config)

    if not result['success']:
        print(f"✗ Validation FAILED: {result['reason']} at step {result['step']}")
        return False

    # Check results
    chattering = result['chattering_index']
    tracking_error = result['tracking_error_rms']

    print("Validation results:")
    print(f"  Chattering index:    {chattering:.3f}")
    print(f"  Tracking error RMS:  {tracking_error:.4f} rad")
    print(f"  Control range:       [{result['control_range'][0]:.2f}, {result['control_range'][1]:.2f}] N")
    print()

    # Acceptance criteria
    passed = True
    if chattering >= target_chattering:
        print(f"✗ FAIL: Chattering {chattering:.3f} >= target {target_chattering}")
        passed = False
    else:
        print(f"✓ PASS: Chattering {chattering:.3f} < target {target_chattering}")

    if tracking_error > 0.1:
        print(f"✗ FAIL: Tracking error {tracking_error:.4f} > 0.1 rad")
        passed = False
    else:
        print(f"✓ PASS: Tracking error {tracking_error:.4f} <= 0.1 rad")

    return passed


def main():
    parser = argparse.ArgumentParser(
        description="Validate optimized controller gains"
    )
    parser.add_argument(
        '--controller',
        choices=['classical_smc', 'adaptive_smc', 'sta_smc', 'hybrid_adaptive_sta_smc'],
        help='Controller to validate'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Validate all controllers'
    )
    parser.add_argument(
        '--target-chattering',
        type=float,
        default=2.0,
        help='Target chattering threshold (default: 2.0)'
    )

    args = parser.parse_args()

    if args.all:
        controllers = ['classical_smc', 'adaptive_smc', 'sta_smc', 'hybrid_adaptive_sta_smc']
    elif args.controller:
        controllers = [args.controller]
    else:
        parser.error("Must specify --controller or --all")

    print("="*60)
    print("PSO Optimization Validation Suite")
    print("="*60)
    print(f"Target chattering: < {args.target_chattering}")
    print(f"Controllers: {', '.join(controllers)}")

    results = {}
    for ctrl in controllers:
        passed = validate_controller(ctrl, args.target_chattering)
        results[ctrl] = passed

    # Summary
    print(f"\n{'='*60}")
    print("Validation Summary")
    print(f"{'='*60}")

    for ctrl, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{ctrl:30s}: {status}")

    total = len(results)
    passed_count = sum(results.values())

    print(f"\nTotal: {passed_count}/{total} controllers passed")

    if passed_count == total:
        print("\n✓✓✓ ALL CONTROLLERS PASSED ✓✓✓")
        sys.exit(0)
    else:
        print(f"\n✗✗✗ {total - passed_count} CONTROLLERS FAILED ✗✗✗")
        sys.exit(1)


if __name__ == '__main__':
    main()