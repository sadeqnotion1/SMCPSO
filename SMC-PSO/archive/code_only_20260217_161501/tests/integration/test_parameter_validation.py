#======================================================================================\\\
#============================ test_parameter_validation.py ============================\\\
#======================================================================================\\\

"""
Quick parameter validation for Issue #2 PSO optimization reality check.
Compares theoretical overshoot predictions for original vs current parameters.
"""

import numpy as np

def compute_damping_ratio(k, lam):
    """Compute damping ratio: ζ = λ/(2√k)"""
    return lam / (2 * np.sqrt(k))

def estimate_overshoot(zeta):
    """Estimate overshoot for second-order system: %OS ≈ exp(-ζπ/√(1-ζ²)) × 100"""
    if zeta >= 1.0:
        return 0.0  # Overdamped, no overshoot
    elif zeta <= 0.0:
        return 100.0  # Underdamped, high overshoot
    else:
        return np.exp(-zeta * np.pi / np.sqrt(1 - zeta**2)) * 100

def analyze_gains(gains, label):
    """Analyze gain set and compute performance metrics."""
    K1, K2, k1, k2, lam1, lam2 = gains

    # Compute damping ratios
    zeta1 = compute_damping_ratio(k1, lam1)
    zeta2 = compute_damping_ratio(k2, lam2)

    # Estimate overshoot
    overshoot1 = estimate_overshoot(zeta1)
    overshoot2 = estimate_overshoot(zeta2)
    overshoot_max = max(overshoot1, overshoot2)

    # Natural frequencies
    omega_n1 = np.sqrt(k1 * lam1)
    omega_n2 = np.sqrt(k2 * lam2)

    # Settling time estimate: t_s ≈ 4/(ζωn)
    settling_time1 = 4 / (zeta1 * omega_n1) if zeta1 > 0 else float('inf')
    settling_time2 = 4 / (zeta2 * omega_n2) if zeta2 > 0 else float('inf')
    settling_time_max = max(settling_time1, settling_time2)

    results = {
        'gains': gains,
        'zeta1': zeta1,
        'zeta2': zeta2,
        'overshoot1': overshoot1,
        'overshoot2': overshoot2,
        'overshoot_max': overshoot_max,
        'settling_time_max': settling_time_max,
        'control_effort': K1 + K2
    }

    print(f"\n{label} Analysis:")
    print(f"  Gains: {gains}")
    print(f"  Damping ratios: zeta1={zeta1:.3f}, zeta2={zeta2:.3f}")
    print(f"  Estimated overshoot: {overshoot_max:.1f}% (zeta1: {overshoot1:.1f}%, zeta2: {overshoot2:.1f}%)")
    print(f"  Settling time: {settling_time_max:.2f}s")
    print(f"  Control effort: {K1 + K2:.1f}")

    return results

def main():
    """Compare original vs current parameter sets."""
    print("PSO OPTIMIZATION REALITY CHECK - Parameter Validation")
    print("=" * 60)

    # Original problematic parameters from Issue #2
    original_gains = [15.0, 8.0, 12.0, 6.0, 20.0, 4.0]

    # Current optimized parameters from config.yaml
    current_gains = [8.0, 5.0, 12.0, 6.0, 4.85, 3.43]

    # Analyze both sets
    original_results = analyze_gains(original_gains, "ORIGINAL (Problematic)")
    current_results = analyze_gains(current_gains, "CURRENT (Optimized)")

    # Compute improvements
    overshoot_improvement = original_results['overshoot_max'] - current_results['overshoot_max']
    settling_improvement = original_results['settling_time_max'] - current_results['settling_time_max']
    effort_reduction = original_results['control_effort'] - current_results['control_effort']

    print(f"\n{'='*60}")
    print("IMPROVEMENT ANALYSIS:")
    print(f"{'='*60}")
    print(f"Overshoot reduction: {overshoot_improvement:+.1f}% ({original_results['overshoot_max']:.1f}% -> {current_results['overshoot_max']:.1f}%)")
    print(f"Settling time change: {settling_improvement:+.2f}s")
    print(f"Control effort reduction: {effort_reduction:+.1f}")

    # Theoretical validation
    target_zeta = 0.7
    zeta1_target_error = abs(current_results['zeta1'] - target_zeta)
    zeta2_target_error = abs(current_results['zeta2'] - target_zeta)

    print("\nTHEORETICAL VALIDATION:")
    print(f"Target damping ratio: {target_zeta}")
    print(f"zeta1 error from target: {zeta1_target_error:.3f} ({'OK' if zeta1_target_error < 0.1 else 'FAIL'})")
    print(f"zeta2 error from target: {zeta2_target_error:.3f} ({'OK' if zeta2_target_error < 0.1 else 'FAIL'})")

    # Overall assessment
    print("\nOVERALL ASSESSMENT:")
    if current_results['overshoot_max'] < 15.0 and overshoot_improvement > 0:
        print("OK OVERSHOOT TARGET ACHIEVED: <15% overshoot target met")
    else:
        print("FAIL OVERSHOOT TARGET NOT MET")

    if zeta1_target_error < 0.1 and zeta2_target_error < 0.1:
        print("OK DAMPING RATIO TARGET ACHIEVED: Both zeta within +/-0.1 of target")
    else:
        print("FAIL DAMPING RATIO TARGET NOT MET")

    if effort_reduction > 0:
        print("OK CONTROL EFFORT REDUCED: Lower control effort")
    else:
        print("FAIL CONTROL EFFORT INCREASED")

    print("\nCONCLUSION:")
    if (current_results['overshoot_max'] < original_results['overshoot_max'] and
        current_results['overshoot_max'] < 15.0):
        print("SUCCESS PARAMETER OPTIMIZATION SUCCESSFUL")
        print("   Current parameters show significant improvement over original")
        print("   Theoretical predictions indicate Issue #2 resolution")
    else:
        print("WARNING PARAMETER OPTIMIZATION INCONCLUSIVE")
        print("   Further validation needed")

if __name__ == "__main__":
    main()