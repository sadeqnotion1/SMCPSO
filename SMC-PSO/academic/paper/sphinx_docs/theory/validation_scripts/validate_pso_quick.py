#!/usr/bin/env python3
"""
Quick PSO Algorithm Validation - Key Concepts Only.

Validates core mathematical claims from pso_algorithm_foundations.md
with minimal computation time.

Author: Documentation Expert Agent
Date: 2025-10-07
"""

import numpy as np
import json


def test_velocity_position_update():
    """Test basic PSO update equations."""
    print("Test 1: PSO Velocity and Position Update Equations")

    # Simple 2D case
    x = np.array([5.0, 5.0])
    v = np.array([0.0, 0.0])
    p_best = np.array([3.0, 3.0])
    g_best = np.array([0.0, 0.0])

    w, c1, c2 = 0.7, 2.0, 2.0
    r1, r2 = np.array([0.5, 0.5]), np.array([0.5, 0.5])

    # Apply PSO equations
    v_new = w * v + c1 * r1 * (p_best - x) + c2 * r2 * (g_best - x)
    x_new = x + v_new

    # Expected: particle moves toward global best
    dist_before = np.linalg.norm(x - g_best)
    dist_after = np.linalg.norm(x_new - g_best)

    passed = dist_after < dist_before
    print(f"  Distance before: {dist_before:.4f}")
    print(f"  Distance after: {dist_after:.4f}")
    print(f"  Status: {'PASS' if passed else 'FAIL'}")
    print()

    return passed


def test_eigenvalue_stability():
    """Test eigenvalue stability analysis."""
    print("Test 2: Eigenvalue Stability Analysis")

    w, c1, c2 = 0.5, 1.5, 1.5
    phi = c1 + c2

    # 1D system matrix
    A = np.array([[1 - phi, 1], [-phi, w]])
    eigenvalues = np.linalg.eigvals(A)
    max_eig_mag = np.max(np.abs(eigenvalues))

    # Stability condition
    stable_empirical = max_eig_mag < 1.0
    stable_theoretical = (0 < w < 1) and (0 < phi < 2 * (1 + w))

    passed = stable_empirical == stable_theoretical
    print(f"  w={w}, c1={c1}, c2={c2}, phi={phi}")
    print(f"  Max eigenvalue magnitude: {max_eig_mag:.4f}")
    print(f"  Theoretical stable: {stable_theoretical}")
    print(f"  Empirical stable: {stable_empirical}")
    print(f"  Status: {'PASS' if passed else 'FAIL'}")
    print()

    return passed


def test_pareto_dominance():
    """Test Pareto dominance relationship."""
    print("Test 3: Pareto Dominance")

    # Two objectives
    obj1 = np.array([1.0, 2.0])
    obj2 = np.array([2.0, 1.0])

    # obj1 dominates obj2 in objective 1, obj2 dominates obj1 in objective 2
    # Neither dominates the other (both are Pareto optimal)
    dominates_12 = np.all(obj1 <= obj2) and np.any(obj1 < obj2)
    dominates_21 = np.all(obj2 <= obj1) and np.any(obj2 < obj1)

    passed = not dominates_12 and not dominates_21
    print(f"  obj1: {obj1}")
    print(f"  obj2: {obj2}")
    print(f"  obj1 dominates obj2: {dominates_12}")
    print(f"  obj2 dominates obj1: {dominates_21}")
    print(f"  Both Pareto optimal: {passed}")
    print(f"  Status: {'PASS' if passed else 'FAIL'}")
    print()

    return passed


def test_convergence_trend():
    """Test that higher inertia leads to slower convergence."""
    print("Test 4: Inertia Weight Convergence Trend")

    # Quick convergence test
    w_low, w_high = 0.4, 0.9
    n_iters = 20

    # Test with low inertia
    x_low = np.array([10.0])
    v_low = np.array([0.0])
    for _ in range(n_iters):
        v_low = w_low * v_low + 2.0 * 0.5 * (0.0 - x_low)
        x_low = x_low + v_low

    # Test with high inertia
    x_high = np.array([10.0])
    v_high = np.array([0.0])
    for _ in range(n_iters):
        v_high = w_high * v_high + 2.0 * 0.5 * (0.0 - x_high)
        x_high = x_high + v_high

    # Low inertia should converge faster (be closer to origin)
    dist_low = abs(x_low[0])
    dist_high = abs(x_high[0])

    passed = dist_low < dist_high
    print(f"  Low inertia (w={w_low}): distance = {dist_low:.4f}")
    print(f"  High inertia (w={w_high}): distance = {dist_high:.4f}")
    print(f"  Low inertia converges faster: {passed}")
    print(f"  Status: {'PASS' if passed else 'FAIL'}")
    print()

    return passed


def main():
    """Run quick validation suite."""
    print("=" * 80)
    print("PSO ALGORITHM FOUNDATIONS - QUICK VALIDATION")
    print("Documentation: docs/theory/pso_algorithm_foundations.md")
    print("=" * 80)
    print()

    results = []
    results.append(test_velocity_position_update())
    results.append(test_eigenvalue_stability())
    results.append(test_pareto_dominance())
    results.append(test_convergence_trend())

    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    all_passed = all(results)
    print(f"Overall: {'[PASS] ALL TESTS PASSED' if all_passed else '[FAIL] SOME TESTS FAILED'}")
    print(f"Passed: {sum(results)}/{len(results)} tests")
    print()

    validation_results = {
        "validation_suite": "PSO Algorithm Foundations - Quick Validation",
        "document": "docs/theory/pso_algorithm_foundations.md",
        "timestamp": "2025-10-07",
        "all_tests_passed": bool(all_passed),
        "tests_passed": int(sum(results)),
        "tests_total": int(len(results))
    }

    # Save results
    with open("docs/theory/validation_scripts/pso_validation_quick.json", 'w') as f:
        json.dump(validation_results, f, indent=2)

    print(f"Results saved to: docs/theory/validation_scripts/pso_validation_quick.json")
    print("=" * 80)

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
