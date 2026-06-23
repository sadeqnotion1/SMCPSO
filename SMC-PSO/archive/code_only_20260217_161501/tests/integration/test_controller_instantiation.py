#======================================================================================\\\
#========================== test_controller_instantiation.py ==========================\\\
#======================================================================================\\\

"""
Integration Validation Script - Controller Instantiation Test

This script validates that all 4 SMC controllers can be properly instantiated
and integrated with the factory system. It performs comprehensive testing of:
- Controller factory instantiation
- Basic functionality validation
- Configuration compatibility
- PSO wrapper integration
"""

import traceback
from typing import Any, Dict
import numpy as np

def test_controller_instantiation() -> Dict[str, Any]:
    """Test instantiation of all 4 SMC controllers."""

    print("=" * 80)
    print("INTEGRATION VALIDATION: Controller Factory Instantiation Test")
    print("=" * 80)

    results = {
        'controllers_tested': [],
        'successful': [],
        'failed': [],
        'error_details': {},
        'total_score': 0,
        'max_score': 4
    }

    # Test all 4 controllers
    controllers_to_test = [
        'classical_smc',
        'adaptive_smc',
        'sta_smc',
        'hybrid_adaptive_sta_smc'
    ]

    try:
        from src.controllers.factory import create_controller
        print("[OK] Factory import successful")
    except Exception as e:
        print(f"[FAIL] CRITICAL: Factory import failed: {e}")
        return results

    for controller_type in controllers_to_test:
        print(f"\n--- Testing {controller_type} ---")
        results['controllers_tested'].append(controller_type)

        try:
            # Test basic instantiation
            controller = create_controller(controller_type)
            print(f"[OK] {controller_type}: Basic instantiation SUCCESS")

            # Test controller has required methods
            if hasattr(controller, 'compute_control'):
                print(f"[OK] {controller_type}: Has compute_control method")
            else:
                print(f"[WARN] {controller_type}: Missing compute_control method")

            if hasattr(controller, 'reset'):
                print(f"[OK] {controller_type}: Has reset method")
            else:
                print(f"[WARN] {controller_type}: Missing reset method")

            # Test with sample state
            test_state = np.array([0.1, 0.05, 0.02, 0.01, 0.0, 0.0])  # [x, x_dot, theta1, theta1_dot, theta2, theta2_dot]

            try:
                result = controller.compute_control(test_state, 0.0, {})
                print(f"[OK] {controller_type}: Control computation SUCCESS")

                # Extract control value for validation
                if hasattr(result, 'u'):
                    u = result.u
                elif isinstance(result, dict) and 'u' in result:
                    u = result['u']
                else:
                    u = result

                print(f"[OK] {controller_type}: Control output = {u}")

            except Exception as e:
                print(f"[FAIL] {controller_type}: Control computation FAILED: {e}")
                results['failed'].append(controller_type)
                results['error_details'][controller_type] = str(e)
                continue

            # If we get here, the controller is working
            results['successful'].append(controller_type)
            results['total_score'] += 1
            print(f"[OK] {controller_type}: COMPLETE SUCCESS")

        except Exception as e:
            print(f"[FAIL] {controller_type}: INSTANTIATION FAILED")
            print(f"   Error: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            results['failed'].append(controller_type)
            results['error_details'][controller_type] = str(e)

    # Summary
    print("\n" + "=" * 80)
    print("CONTROLLER INSTANTIATION SUMMARY")
    print("=" * 80)
    print(f"Controllers Tested: {len(results['controllers_tested'])}")
    print(f"Successful: {len(results['successful'])} - {results['successful']}")
    print(f"Failed: {len(results['failed'])} - {results['failed']}")
    print(f"Integration Score: {results['total_score']}/{results['max_score']}")

    if results['failed']:
        print("\nFAILED CONTROLLERS:")
        for controller in results['failed']:
            print(f"  [FAIL] {controller}: {results['error_details'][controller]}")

    return results

def test_pso_integration() -> Dict[str, Any]:
    """Test PSO wrapper integration for all controllers."""

    print("\n" + "=" * 80)
    print("PSO INTEGRATION VALIDATION TEST")
    print("=" * 80)

    results = {
        'controllers_tested': [],
        'successful': [],
        'failed': [],
        'error_details': {},
        'total_score': 0,
        'max_score': 4
    }

    try:
        from src.controllers.factory import SMCType, create_smc_for_pso
        print("[OK] PSO integration imports successful")
    except Exception as e:
        print(f"[FAIL] CRITICAL: PSO integration import failed: {e}")
        return results

    # Test PSO integration for each controller
    controllers_to_test = [
        (SMCType.CLASSICAL, [20.0, 15.0, 12.0, 8.0, 35.0, 5.0]),
        (SMCType.ADAPTIVE, [25.0, 18.0, 15.0, 10.0, 4.0]),
        (SMCType.SUPER_TWISTING, [25.0, 15.0, 20.0, 12.0, 8.0, 6.0]),
        (SMCType.HYBRID, [18.0, 12.0, 10.0, 8.0])
    ]

    for smc_type, test_gains in controllers_to_test:
        controller_name = smc_type.value
        print(f"\n--- Testing PSO integration for {controller_name} ---")
        results['controllers_tested'].append(controller_name)

        try:
            # Create PSO wrapper
            pso_controller = create_smc_for_pso(smc_type, test_gains)
            print(f"[OK] {controller_name}: PSO wrapper creation SUCCESS")

            # Test PSO interface methods
            if hasattr(pso_controller, 'compute_control'):
                print(f"[OK] {controller_name}: Has PSO compute_control method")
            else:
                print(f"[FAIL] {controller_name}: Missing PSO compute_control method")
                results['failed'].append(controller_name)
                continue

            if hasattr(pso_controller, 'validate_gains'):
                print(f"[OK] {controller_name}: Has validate_gains method")
            else:
                print(f"[WARN] {controller_name}: Missing validate_gains method")

            # Test control computation with PSO interface
            test_state = np.array([0.1, 0.05, 0.02, 0.01, 0.0, 0.0])

            try:
                control_output = pso_controller.compute_control(test_state)
                print(f"[OK] {controller_name}: PSO control computation SUCCESS")
                print(f"   Control output: {control_output}")

                # Validate output format
                if isinstance(control_output, np.ndarray) and len(control_output) == 1:
                    print(f"[OK] {controller_name}: PSO output format correct")
                else:
                    print(f"[WARN] {controller_name}: PSO output format unexpected: {type(control_output)}")

            except Exception as e:
                print(f"[FAIL] {controller_name}: PSO control computation FAILED: {e}")
                results['failed'].append(controller_name)
                results['error_details'][controller_name] = str(e)
                continue

            # Test gain validation if available
            if hasattr(pso_controller, 'validate_gains'):
                try:
                    valid_gains = np.array([test_gains])
                    validation_result = pso_controller.validate_gains(valid_gains)
                    print(f"[OK] {controller_name}: Gain validation SUCCESS: {validation_result}")
                except Exception as e:
                    print(f"[WARN] {controller_name}: Gain validation failed: {e}")

            # If we get here, PSO integration is working
            results['successful'].append(controller_name)
            results['total_score'] += 1
            print(f"[OK] {controller_name}: PSO INTEGRATION SUCCESS")

        except Exception as e:
            print(f"[FAIL] {controller_name}: PSO INTEGRATION FAILED")
            print(f"   Error: {e}")
            results['failed'].append(controller_name)
            results['error_details'][controller_name] = str(e)

    # Summary
    print("\n" + "=" * 80)
    print("PSO INTEGRATION SUMMARY")
    print("=" * 80)
    print(f"Controllers Tested: {len(results['controllers_tested'])}")
    print(f"Successful: {len(results['successful'])} - {results['successful']}")
    print(f"Failed: {len(results['failed'])} - {results['failed']}")
    print(f"PSO Integration Score: {results['total_score']}/{results['max_score']}")

    return results

def main():
    """Main integration validation function."""

    print("STARTING COMPREHENSIVE CONTROLLER INTEGRATION VALIDATION")
    print("=" * 80)

    # Test 1: Controller Instantiation
    instantiation_results = test_controller_instantiation()

    # Test 2: PSO Integration
    pso_results = test_pso_integration()

    # Overall Summary
    print("\n" + "=" * 80)
    print("OVERALL INTEGRATION VALIDATION SUMMARY")
    print("=" * 80)

    total_score = instantiation_results['total_score'] + pso_results['total_score']
    max_total_score = instantiation_results['max_score'] + pso_results['max_score']

    print(f"Controller Instantiation: {instantiation_results['total_score']}/{instantiation_results['max_score']}")
    print(f"PSO Integration: {pso_results['total_score']}/{pso_results['max_score']}")
    print(f"TOTAL INTEGRATION SCORE: {total_score}/{max_total_score}")

    # Determine integration health level
    if total_score == max_total_score:
        print("[PERFECT] INTEGRATION STATUS: PERFECT (100%)")
    elif total_score >= max_total_score * 0.75:
        print(f"[EXCELLENT] INTEGRATION STATUS: EXCELLENT ({total_score/max_total_score*100:.1f}%)")
    elif total_score >= max_total_score * 0.5:
        print(f"[PARTIAL] INTEGRATION STATUS: PARTIAL ({total_score/max_total_score*100:.1f}%)")
    else:
        print(f"[CRITICAL] INTEGRATION STATUS: CRITICAL ({total_score/max_total_score*100:.1f}%)")

    # Recommendations
    print("\nRECOMMENDations:")
    all_failed = set(instantiation_results['failed'] + pso_results['failed'])
    if not all_failed:
        print("[OK] All controllers are fully integrated and functional")
        print("[OK] System ready for production deployment")
    else:
        print(f"[FIX] Controllers requiring attention: {list(all_failed)}")
        print("[FIX] Focus on fixing failed controllers for complete integration")

    return {
        'instantiation': instantiation_results,
        'pso_integration': pso_results,
        'total_score': total_score,
        'max_score': max_total_score,
        'integration_percentage': total_score/max_total_score*100
    }

if __name__ == "__main__":
    results = main()