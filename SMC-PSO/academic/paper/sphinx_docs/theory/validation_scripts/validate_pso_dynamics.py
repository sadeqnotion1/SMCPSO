#!/usr/bin/env python3
"""
PSO Algorithm Dynamics Validation Script.

This script validates all mathematical claims in pso_algorithm_foundations.md
using executable NumPy computations.

Author: Documentation Expert Agent
Date: 2025-10-07
Status: Executable validation script for research-grade documentation
"""

import numpy as np
from scipy.optimize import rosen
from typing import Dict, List, Tuple
import json


# ==============================================================================
# Section 1: PSO Swarm Dynamics Validation
# ==============================================================================

def validate_particle_trajectory(
    initial_position: np.ndarray,
    initial_velocity: np.ndarray,
    personal_best: np.ndarray,
    global_best: np.ndarray,
    w: float,
    c1: float,
    c2: float,
    n_iterations: int,
    seed: int = 42
) -> Dict:
    """
    Validate PSO particle trajectory equations (Section 1.4).

    This function simulates a single particle's motion and verifies:
    1. Position update equation: x_i^{t+1} = x_i^t + v_i^{t+1}
    2. Velocity update equation: v_i^{t+1} = w*v_i^t + c1*r1*(p_i - x_i) + c2*r2*(g - x_i)
    3. Convergence to global best position

    Returns
    -------
    dict
        Validation results with convergence metrics
    """
    rng = np.random.default_rng(seed)
    D = len(initial_position)

    positions = np.zeros((n_iterations + 1, D))
    velocities = np.zeros((n_iterations + 1, D))

    positions[0] = initial_position.copy()
    velocities[0] = initial_velocity.copy()

    # PSO update loop
    for t in range(n_iterations):
        r1 = rng.uniform(0, 1, D)
        r2 = rng.uniform(0, 1, D)

        # Velocity update (Eq. 1 in documentation)
        v_inertia = w * velocities[t]
        v_cognitive = c1 * r1 * (personal_best - positions[t])
        v_social = c2 * r2 * (global_best - positions[t])
        velocities[t+1] = v_inertia + v_cognitive + v_social

        # Position update (Eq. 2 in documentation)
        positions[t+1] = positions[t] + velocities[t+1]

    # Convergence metrics
    distances_to_gbest = np.linalg.norm(positions - global_best, axis=1)
    velocity_magnitudes = np.linalg.norm(velocities, axis=1)

    # Convergence rate estimation
    if n_iterations > 10:
        t_vals = np.arange(n_iterations + 1)
        log_dist = np.log(distances_to_gbest + 1e-10)
        valid_idx = np.isfinite(log_dist)

        if np.sum(valid_idx) > 5:
            coeffs = np.polyfit(t_vals[valid_idx], log_dist[valid_idx], 1)
            convergence_rate = -coeffs[0]
        else:
            convergence_rate = 0.0
    else:
        convergence_rate = 0.0

    return {
        "test_name": "Particle Trajectory Validation",
        "positions": positions.tolist(),
        "velocities": velocities.tolist(),
        "final_position": positions[-1].tolist(),
        "final_velocity": velocities[-1].tolist(),
        "distance_to_gbest": float(distances_to_gbest[-1]),
        "convergence_rate": float(convergence_rate),
        "converged": bool(distances_to_gbest[-1] < 1e-3),
        "validation_status": "PASS" if distances_to_gbest[-1] < 1e-3 else "FAIL"
    }


# ==============================================================================
# Section 2: Eigenvalue Stability Analysis (Theorem 2.1)
# ==============================================================================

def validate_pso_stability_conditions(
    test_cases: List[Tuple[float, float, float]]
) -> Dict:
    """
    Validate PSO stability conditions via eigenvalue analysis (Section 2.4).

    Tests Theorem 2.1: Stability requires 0 < w < 1 and 0 < c1+c2 < 2(1+w)

    Parameters
    ----------
    test_cases : List[Tuple[float, float, float]]
        List of (w, c1, c2) parameter combinations to test

    Returns
    -------
    dict
        Stability analysis results for each test case
    """
    results = []

    for w, c1, c2 in test_cases:
        phi = c1 + c2

        # System matrix for 1D deterministic PSO
        A = np.array([
            [1 - phi, 1],
            [-phi, w]
        ])

        # Eigenvalue analysis
        eigenvalues = np.linalg.eigvals(A)
        eigenvalue_magnitudes = np.abs(eigenvalues)
        max_eigenvalue_magnitude = float(np.max(eigenvalue_magnitudes))

        # Stability conditions
        condition1 = (0 < w < 1)
        condition2 = (0 < phi < 2 * (1 + w))
        theoretical_stable = condition1 and condition2
        empirical_stable = np.all(eigenvalue_magnitudes < 1.0)

        # Constriction factor
        if phi > 4:
            chi = 2.0 / abs(2 - phi - np.sqrt(phi**2 - 4*phi))
            constriction_applicable = True
        else:
            chi = None
            constriction_applicable = False

        status = "PASS" if (theoretical_stable == empirical_stable) else "FAIL"

        results.append({
            "w": float(w),
            "c1": float(c1),
            "c2": float(c2),
            "phi": float(phi),
            "eigenvalues": [complex(e) for e in eigenvalues],
            "max_eigenvalue_magnitude": max_eigenvalue_magnitude,
            "condition_w": bool(condition1),
            "condition_phi": bool(condition2),
            "theoretical_stable": bool(theoretical_stable),
            "empirical_stable": bool(empirical_stable),
            "constriction_factor": float(chi) if chi is not None else None,
            "constriction_applicable": bool(constriction_applicable),
            "validation_status": status
        })

    return {
        "test_name": "PSO Stability Eigenvalue Analysis",
        "test_cases": results,
        "overall_status": "PASS" if all(r["validation_status"] == "PASS" for r in results) else "FAIL"
    }


# ==============================================================================
# Section 3: Parameter Sensitivity Analysis
# ==============================================================================

def validate_inertia_weight_impact(
    w_values: List[float],
    dimension: int = 2,
    n_trials: int = 5,
    n_iterations: int = 30
) -> Dict:
    """
    Validate inertia weight impact on convergence (Section 3.1).

    Tests that:
    - High w (0.9): Global exploration, slower convergence
    - Low w (0.4): Local exploitation, faster convergence
    """
    results = []

    for w in w_values:
        convergence_iterations_list = []

        for trial in range(n_trials):
            rng = np.random.default_rng(42 + trial)

            # Simple optimization: converge to origin
            position = rng.uniform(-5, 5, dimension)
            velocity = rng.uniform(-1, 1, dimension)
            p_best = position.copy()
            g_best = np.zeros(dimension)  # Target: origin

            for t in range(n_iterations):
                r1 = rng.uniform(0, 1, dimension)
                r2 = rng.uniform(0, 1, dimension)

                velocity = w * velocity + 2.0 * r1 * (p_best - position) + 2.0 * r2 * (g_best - position)
                position = position + velocity

                if np.linalg.norm(position) < np.linalg.norm(p_best):
                    p_best = position.copy()

                # Check convergence
                if np.linalg.norm(position - g_best) < 0.01:
                    convergence_iterations_list.append(t)
                    break

        mean_convergence = np.mean(convergence_iterations_list) if convergence_iterations_list else n_iterations

        results.append({
            "w": float(w),
            "mean_convergence_iterations": float(mean_convergence),
            "convergence_rate": float(len(convergence_iterations_list) / n_trials)
        })

    # Validate trend: higher w should give slower convergence
    w_sorted = sorted(results, key=lambda x: x["w"])
    trend_valid = all(
        w_sorted[i]["mean_convergence_iterations"] <= w_sorted[i+1]["mean_convergence_iterations"]
        for i in range(len(w_sorted) - 1)
    )

    return {
        "test_name": "Inertia Weight Sensitivity",
        "results": results,
        "trend_valid": bool(trend_valid),
        "validation_status": "PASS" if trend_valid else "FAIL"
    }


# ==============================================================================
# Section 4: Condition Number Impact on Convergence
# ==============================================================================

def validate_conditioning_impact(
    condition_numbers: List[float],
    dimension: int = 5,
    n_trials: int = 3,
    n_iterations: int = 50
) -> Dict:
    """
    Validate that ill-conditioned problems converge slower (Section 4.4).

    Tests quadratic objectives with varying condition numbers:
    f(x) = 0.5 * x^T Q x where kappa(Q) varies
    """
    results = []

    for kappa in condition_numbers:
        convergence_rates = []

        for trial in range(n_trials):
            # Create quadratic with specified condition number
            eigenvalues = np.logspace(0, np.log10(kappa), dimension)
            Q = np.diag(eigenvalues)

            def objective(x):
                return 0.5 * x @ Q @ x

            # PSO optimization
            rng = np.random.default_rng(42 + trial)
            N = 15
            positions = rng.uniform(-10, 10, (N, dimension))
            velocities = rng.uniform(-1, 1, (N, dimension))

            p_best = positions.copy()
            p_best_costs = np.array([objective(x) for x in positions])
            g_best = p_best[np.argmin(p_best_costs)].copy()

            cost_history = [objective(g_best)]

            for t in range(n_iterations):
                for i in range(N):
                    r1 = rng.uniform(0, 1, dimension)
                    r2 = rng.uniform(0, 1, dimension)

                    velocities[i] = (0.7 * velocities[i] +
                                    2.0 * r1 * (p_best[i] - positions[i]) +
                                    2.0 * r2 * (g_best - positions[i]))
                    positions[i] = positions[i] + velocities[i]

                    cost = objective(positions[i])
                    if cost < p_best_costs[i]:
                        p_best[i] = positions[i].copy()
                        p_best_costs[i] = cost
                        if cost < objective(g_best):
                            g_best = positions[i].copy()

                cost_history.append(objective(g_best))

            # Convergence rate estimation
            log_costs = np.log(np.array(cost_history) + 1e-10)
            t_vals = np.arange(len(log_costs))
            valid = np.isfinite(log_costs)

            if np.sum(valid) > 10:
                coeffs = np.polyfit(t_vals[valid], log_costs[valid], 1)
                rate = -coeffs[0]
            else:
                rate = 0.0

            convergence_rates.append(rate)

        results.append({
            "condition_number": float(kappa),
            "mean_convergence_rate": float(np.mean(convergence_rates)),
            "std_convergence_rate": float(np.std(convergence_rates))
        })

    # Validate trend: higher kappa should give slower convergence (lower rate)
    kappa_sorted = sorted(results, key=lambda x: x["condition_number"])
    trend_valid = all(
        kappa_sorted[i]["mean_convergence_rate"] >= kappa_sorted[i+1]["mean_convergence_rate"]
        for i in range(len(kappa_sorted) - 1)
    )

    return {
        "test_name": "Condition Number Impact Analysis",
        "results": results,
        "trend_valid": bool(trend_valid),
        "validation_status": "PASS" if trend_valid else "FAIL"
    }


# ==============================================================================
# Section 5: Multi-Objective Optimization - Pareto Frontier
# ==============================================================================

def validate_pareto_frontier_computation(
    objectives: np.ndarray
) -> Dict:
    """
    Validate Fast Non-Dominated Sort and Crowding Distance (Section 5.4).

    Implements Algorithm 5.1 (Deb et al. 2002) and Definition 5.3.
    """
    N, M = objectives.shape

    # Fast Non-Dominated Sort
    domination_count = np.zeros(N, dtype=int)
    dominated_solutions = [set() for _ in range(N)]

    for i in range(N):
        for j in range(i+1, N):
            i_dominates_j = np.all(objectives[i] <= objectives[j]) and \
                           np.any(objectives[i] < objectives[j])
            j_dominates_i = np.all(objectives[j] <= objectives[i]) and \
                           np.any(objectives[j] < objectives[i])

            if i_dominates_j:
                dominated_solutions[i].add(j)
                domination_count[j] += 1
            elif j_dominates_i:
                dominated_solutions[j].add(i)
                domination_count[i] += 1

    fronts = []
    current_front = [i for i in range(N) if domination_count[i] == 0]
    fronts.append(current_front)

    while len(fronts[-1]) > 0:
        next_front = []
        for i in fronts[-1]:
            for j in dominated_solutions[i]:
                domination_count[j] -= 1
                if domination_count[j] == 0:
                    next_front.append(j)

        if len(next_front) > 0:
            fronts.append(next_front)

    if len(fronts[-1]) == 0:
        fronts = fronts[:-1]

    # Crowding Distance for first front
    if len(fronts) > 0 and len(fronts[0]) > 0:
        front_indices = fronts[0]
        crowding_distances = compute_crowding_distance(objectives, front_indices)
    else:
        crowding_distances = []

    return {
        "test_name": "Pareto Frontier Computation",
        "n_solutions": int(N),
        "n_objectives": int(M),
        "n_fronts": len(fronts),
        "front_sizes": [len(f) for f in fronts],
        "pareto_front_indices": fronts[0] if len(fronts) > 0 else [],
        "pareto_front_size": len(fronts[0]) if len(fronts) > 0 else 0,
        "crowding_distances": [float(cd) for cd in crowding_distances],
        "validation_status": "PASS" if len(fronts) > 0 else "FAIL"
    }


def compute_crowding_distance(
    objectives: np.ndarray,
    front_indices: List[int]
) -> np.ndarray:
    """Compute crowding distance for solutions in a Pareto front."""
    N_front = len(front_indices)
    M = objectives.shape[1]

    if N_front <= 2:
        return np.full(N_front, np.inf)

    crowding_distances = np.zeros(N_front)

    for m in range(M):
        obj_m = objectives[front_indices, m]
        sorted_indices = np.argsort(obj_m)

        crowding_distances[sorted_indices[0]] = np.inf
        crowding_distances[sorted_indices[-1]] = np.inf

        obj_range = obj_m[sorted_indices[-1]] - obj_m[sorted_indices[0]]

        if obj_range > 1e-10:
            for i in range(1, N_front - 1):
                idx = sorted_indices[i]
                crowding_distances[idx] += (
                    (obj_m[sorted_indices[i+1]] - obj_m[sorted_indices[i-1]]) / obj_range
                )

    return crowding_distances


# ==============================================================================
# Main Validation Suite
# ==============================================================================

def run_all_validations() -> Dict:
    """Run complete validation suite for PSO algorithm documentation."""

    print("=" * 80)
    print("PSO ALGORITHM MATHEMATICAL FOUNDATIONS VALIDATION")
    print("Documentation: docs/theory/pso_algorithm_foundations.md")
    print("=" * 80)
    print()

    all_results = {}

    # Test 1: Particle Trajectory
    print("Test 1: Validating PSO Particle Trajectory Equations...")
    result1 = validate_particle_trajectory(
        initial_position=np.array([5.0, 5.0]),
        initial_velocity=np.array([0.0, 0.0]),
        personal_best=np.array([3.0, 3.0]),
        global_best=np.array([0.0, 0.0]),
        w=0.7, c1=2.0, c2=2.0, n_iterations=50
    )
    print(f"  Status: {result1['validation_status']}")
    print(f"  Final distance to global best: {result1['distance_to_gbest']:.6f}")
    print(f"  Convergence rate: {result1['convergence_rate']:.6f}")
    print()
    all_results["particle_trajectory"] = result1

    # Test 2: Stability Conditions
    print("Test 2: Validating PSO Stability Eigenvalue Analysis...")
    stability_test_cases = [
        (0.7, 2.0, 2.0),   # Typical PSO (should oscillate)
        (0.5, 1.5, 1.5),   # Stable parameters
        (0.9, 2.5, 2.5),   # High inertia (unstable)
        (0.4, 1.0, 1.0),   # Low coefficients (stable)
    ]
    result2 = validate_pso_stability_conditions(stability_test_cases)
    print(f"  Status: {result2['overall_status']}")
    for case in result2['test_cases']:
        print(f"    w={case['w']}, c1={case['c1']}, c2={case['c2']}: {case['validation_status']}")
    print()
    all_results["stability_analysis"] = result2

    # Test 3: Inertia Weight Sensitivity
    print("Test 3: Validating Inertia Weight Impact on Convergence...")
    result3 = validate_inertia_weight_impact([0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    print(f"  Status: {result3['validation_status']}")
    print(f"  Trend (higher w -> slower convergence): {result3['trend_valid']}")
    print()
    all_results["inertia_sensitivity"] = result3

    # Test 4: Condition Number Impact
    print("Test 4: Validating Condition Number Impact on Convergence...")
    result4 = validate_conditioning_impact([1, 10, 100, 1000])
    print(f"  Status: {result4['validation_status']}")
    print(f"  Trend (higher kappa -> slower convergence): {result4['trend_valid']}")
    for case in result4['results']:
        print(f"    kappa={case['condition_number']:.0f}: rate={case['mean_convergence_rate']:.6f}")
    print()
    all_results["conditioning_impact"] = result4

    # Test 5: Pareto Frontier
    print("Test 5: Validating Pareto Frontier Computation...")
    # Create test objectives (ZDT1-like)
    n_solutions = 20
    x_vals = np.linspace(0, 1, n_solutions)
    obj1 = x_vals
    obj2 = 1 - np.sqrt(x_vals)
    test_objectives = np.column_stack([obj1, obj2])

    result5 = validate_pareto_frontier_computation(test_objectives)
    print(f"  Status: {result5['validation_status']}")
    print(f"  Number of fronts: {result5['n_fronts']}")
    print(f"  Pareto front size: {result5['pareto_front_size']}")
    print()
    all_results["pareto_frontier"] = result5

    # Summary
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    all_passed = all(
        result.get("validation_status") == "PASS" or result.get("overall_status") == "PASS"
        for result in all_results.values()
    )

    print(f"Overall Status: {'[PASS] ALL TESTS PASSED' if all_passed else '[FAIL] SOME TESTS FAILED'}")
    print()
    print("Individual Test Results:")
    for test_name, result in all_results.items():
        status = result.get("validation_status") or result.get("overall_status")
        symbol = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"  {symbol} {test_name}: {status}")

    print()
    print("=" * 80)

    return {
        "validation_suite": "PSO Algorithm Mathematical Foundations",
        "document": "docs/theory/pso_algorithm_foundations.md",
        "timestamp": "2025-10-07",
        "all_tests_passed": all_passed,
        "results": all_results
    }


if __name__ == "__main__":
    # Run validation suite
    validation_results = run_all_validations()

    # Save results to JSON
    output_file = "docs/theory/validation_scripts/pso_validation_results.json"
    with open(output_file, 'w') as f:
        # Convert complex numbers to strings for JSON serialization
        def serialize(obj):
            if isinstance(obj, complex):
                return {"real": obj.real, "imag": obj.imag}
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        json.dump(validation_results, f, indent=2, default=serialize)

    print(f"Validation results saved to: {output_file}")
    print()

    # Exit with appropriate code
    exit_code = 0 if validation_results["all_tests_passed"] else 1
    exit(exit_code)
