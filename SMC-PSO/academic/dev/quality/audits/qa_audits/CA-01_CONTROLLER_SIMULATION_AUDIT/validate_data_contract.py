"""
CA-01 Audit: Data Contract Validation Script

Validates the data contract between Controller Factory and Simulation Runner.
Tests all 4 controller types for interface compliance.
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
from src.controllers.factory.smc_factory import SMCFactory, SMCType


def validate_data_contract():
    """Validate data contract between factory and simulation."""
    results = {}

    print("[INFO] Starting data contract validation for all 4 SMC controllers...")
    print("=" * 80)

    for ctrl_type in SMCType:
        print(f"\n[TESTING] {ctrl_type.value}")
        print("-" * 80)

        try:
            # Get gain specification
            spec = SMCFactory.get_gain_specification(ctrl_type)
            print(f"  Required gains: {spec.n_gains}")
            print(f"  Gain names: {spec.gain_names}")

            # Create controller with valid gains
            gains = [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]  # 6 gains (enough for all types)
            controller = SMCFactory.create_from_gains(ctrl_type.value, gains=gains)

            # Test protocol compliance
            has_compute_control = hasattr(controller, 'compute_control')
            has_initialize_state = hasattr(controller, 'initialize_state')
            has_initialize_history = hasattr(controller, 'initialize_history')
            has_gains = hasattr(controller, 'gains')
            has_max_force = hasattr(controller, 'max_force')

            print(f"  Protocol compliance:")
            print(f"    - compute_control: {has_compute_control}")
            print(f"    - initialize_state: {has_initialize_state}")
            print(f"    - initialize_history: {has_initialize_history}")
            print(f"    - gains property: {has_gains}")
            print(f"    - max_force property: {has_max_force}")

            # Test state initialization
            state_vars = controller.initialize_state()
            history = controller.initialize_history()

            print(f"  Initialized state:")
            print(f"    - state_vars type: {type(state_vars).__name__}")
            print(f"    - state_vars value: {state_vars}")
            print(f"    - history type: {type(history).__name__}")
            print(f"    - history keys: {list(history.keys()) if isinstance(history, dict) else 'N/A'}")

            # Test control computation with standard state vector
            state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])  # [x, θ1, θ2, ẋ, θ̇1, θ̇2]
            control_output = controller.compute_control(state, state_vars, history)

            # Extract control value from output
            if hasattr(control_output, 'u'):
                control_value = control_output.u
            elif hasattr(control_output, 'control'):
                control_value = control_output.control
            elif isinstance(control_output, dict) and 'u' in control_output:
                control_value = control_output['u']
            elif isinstance(control_output, dict) and 'control' in control_output:
                control_value = control_output['control']
            elif isinstance(control_output, tuple):
                control_value = control_output[0]
            else:
                control_value = control_output

            print(f"  Control computation:")
            print(f"    - Output type: {type(control_output).__name__}")
            print(f"    - Control value: {control_value}")
            print(f"    - Control dtype: {type(control_value).__name__}")
            print(f"    - Is scalar: {np.isscalar(control_value)}")
            print(f"    - Is finite: {np.isfinite(float(control_value))}")

            # Type checking
            state_vars_valid = state_vars is not None
            history_valid = isinstance(history, dict)
            control_valid = np.isfinite(float(control_value))

            print(f"  Validation:")
            print(f"    - state_vars valid: {state_vars_valid}")
            print(f"    - history valid: {history_valid}")
            print(f"    - control valid: {control_valid}")

            # Check max_force
            max_force_value = getattr(controller, 'max_force', None)
            print(f"    - max_force: {max_force_value}")

            # Store results
            results[ctrl_type.value] = {
                'status': 'PASS',
                'protocol_compliance': {
                    'compute_control': has_compute_control,
                    'initialize_state': has_initialize_state,
                    'initialize_history': has_initialize_history,
                    'gains': has_gains,
                    'max_force': has_max_force
                },
                'state_vars_type': type(state_vars).__name__,
                'state_vars_value': str(state_vars),
                'history_type': type(history).__name__,
                'history_keys': list(history.keys()) if isinstance(history, dict) else [],
                'control_output_type': type(control_output).__name__,
                'control_value': float(control_value),
                'control_dtype': type(control_value).__name__,
                'is_scalar': bool(np.isscalar(control_value)),
                'is_finite': bool(np.isfinite(float(control_value))),
                'max_force': max_force_value,
                'validation': {
                    'state_vars_valid': state_vars_valid,
                    'history_valid': history_valid,
                    'control_valid': control_valid
                }
            }

            print(f"  [OK] {ctrl_type.value} validation PASSED")

        except Exception as e:
            print(f"  [ERROR] {ctrl_type.value} validation FAILED: {e}")
            results[ctrl_type.value] = {
                'status': 'FAIL',
                'error': str(e)
            }

    print("\n" + "=" * 80)
    print("[INFO] Data contract validation complete")

    # Summary
    passed = sum(1 for r in results.values() if r.get('status') == 'PASS')
    failed = len(results) - passed
    print(f"\n[SUMMARY] {passed}/{len(results)} controllers passed, {failed} failed")

    return results


def test_simulation_runner_interface():
    """Test that simulation runner accepts all controller types."""
    from src.simulation.engines.simulation_runner import run_simulation
    from src.plant.models.lowrank.dynamics import LowRankDIPDynamics
    from src.plant.models.lowrank.config import LowRankDIPConfig

    print("\n" + "=" * 80)
    print("[INFO] Testing Simulation Runner Interface")
    print("=" * 80)

    # Create dynamics with default config
    config = LowRankDIPConfig()
    dynamics = LowRankDIPDynamics(config=config)
    results = {}

    for ctrl_type in SMCType:
        print(f"\n[TESTING] {ctrl_type.value} with simulation runner")
        try:
            controller = SMCFactory.create_from_gains(
                ctrl_type.value,
                gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
            )

            t, x, u = run_simulation(
                controller=controller,
                dynamics_model=dynamics,
                sim_time=1.0,
                dt=0.01,
                initial_state=np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])
            )

            steps = len(t)
            final_state_norm = np.linalg.norm(x[-1])
            control_effort = np.sqrt(np.mean(u**2))

            print(f"  [OK] Simulation successful")
            print(f"    - Steps completed: {steps}")
            print(f"    - Final state norm: {final_state_norm:.4f}")
            print(f"    - Control effort (RMS): {control_effort:.4f}")

            results[ctrl_type.value] = {
                'status': 'PASS',
                'steps': int(steps),
                'final_state_norm': float(final_state_norm),
                'control_effort': float(control_effort)
            }

        except Exception as e:
            print(f"  [ERROR] Simulation failed: {e}")
            results[ctrl_type.value] = {
                'status': 'FAIL',
                'error': str(e)
            }

    passed = sum(1 for r in results.values() if r.get('status') == 'PASS')
    print(f"\n[SUMMARY] {passed}/{len(results)} simulations passed")

    return results


if __name__ == '__main__':
    # Run data contract validation
    contract_results = validate_data_contract()

    # Run simulation runner interface test
    simulation_results = test_simulation_runner_interface()

    # Save results
    output_dir = Path(__file__).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    all_results = {
        'data_contract': contract_results,
        'simulation_integration': simulation_results
    }

    # Convert numpy types to native Python types for JSON serialization
    def convert_numpy_types(obj):
        if isinstance(obj, dict):
            return {k: convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(v) for v in obj]
        elif isinstance(obj, (np.bool_, np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj

    all_results_serializable = convert_numpy_types(all_results)

    output_file = output_dir / 'data_contract_validation_results.json'
    with open(output_file, 'w') as f:
        json.dump(all_results_serializable, f, indent=2)

    print(f"\n[INFO] Results saved to: {output_file}")

    # Exit with error code if any failures
    all_passed = all(
        r.get('status') == 'PASS'
        for r in list(contract_results.values()) + list(simulation_results.values())
    )

    if all_passed:
        print("\n[OK] All validations PASSED")
        sys.exit(0)
    else:
        print("\n[ERROR] Some validations FAILED")
        sys.exit(1)
