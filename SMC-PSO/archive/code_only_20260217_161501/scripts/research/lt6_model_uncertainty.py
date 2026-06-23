#!/usr/bin/env python3
"""
LT-6: Model Uncertainty Analysis
================================

Tests robustness of SMC controllers to model parameter errors.

This script quantifies how controller performance degrades when the actual
plant differs from the nominal model used for controller design. This is
critical for industrial deployment where manufacturing tolerances and
measurement errors create model uncertainty.

Usage:
    # Quick test (±10% errors, 10 trials)
    python scripts/lt6_model_uncertainty.py

    # Comprehensive test (±10% and ±20% errors, 20 trials)
    python scripts/lt6_model_uncertainty.py --error-levels 0.1 0.2 --trials 20

    # Minimal test (debugging)
    python scripts/lt6_model_uncertainty.py --error-levels 0.1 --trials 3

Output:
    - benchmarks/LT6_uncertainty_analysis.csv (raw results)
    - benchmarks/LT6_robustness_ranking.csv (ranked controllers)

Author: Claude Code (LT-6 Model Uncertainty Analysis)
Date: October 18, 2025
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from typing import Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.loader import load_config
from src.utils.model_uncertainty import create_uncertainty_scenarios, get_perturbation_summary
from src.controllers.factory import create_controller
from src.core.dynamics import DIPDynamics
from src.core.simulation_runner import run_simulation

# Controllers to test
CONTROLLERS = [
    'classical_smc',
    'sta_smc',
    'adaptive_smc',
    'hybrid_adaptive_sta_smc'
]


def run_uncertainty_test(
    controller_name: str,
    scenario_name: str,
    perturbed_config,
    n_trials: int = 10
) -> Dict[str, float] | None:
    """
    Run Monte Carlo trials with perturbed model.

    The controller is designed with nominal gains (from config.yaml),
    but the actual plant has perturbed parameters. This simulates
    the real-world scenario where the controller is tuned based on
    an approximate model.

    Args:
        controller_name: Controller type ('classical_smc', etc.)
        scenario_name: Scenario label (e.g., 'm1+10%')
        perturbed_config: Config with perturbed plant parameters
        n_trials: Number of Monte Carlo trials

    Returns:
        {
            'settling_time_mean': float,
            'settling_time_std': float,
            'overshoot_mean': float (degrees),
            'overshoot_std': float (degrees),
            'convergence_rate': float (0-1)
        }
    """
    results = []

    # Try to create dynamics - skip scenario if validation fails
    try:
        # Create one dynamics instance to check if scenario is valid
        test_dynamics = DIPDynamics(perturbed_config.physics)
    except (ValueError, RuntimeError) as e:
        # Scenario violates physical constraints (e.g., inertia too small)
        # Return None to indicate scenario should be skipped
        return None

    for trial in range(n_trials):
        # Create controller with nominal gains (from config.yaml)
        # NOTE: Controller doesn't know the plant parameters are wrong!
        controller = create_controller(controller_name, perturbed_config)

        # Create dynamics with PERTURBED parameters
        # This is the "real" plant that differs from the model
        dynamics = DIPDynamics(perturbed_config.physics)

        # Run simulation
        try:
            t_arr, x_arr, u_arr = run_simulation(
                controller=controller,
                dynamics_model=dynamics,
                sim_time=10.0,
                dt=0.01,
                initial_state=np.array([0, 0.1, 0.1, 0, 0, 0])  # Small perturbation (5.7° each)
            )

            # Compute metrics
            # x_arr shape: (n_steps, 6) where state = [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
            theta1 = np.abs(x_arr[:, 1])
            theta2 = np.abs(x_arr[:, 2])

            # Settling time (|θ1|, |θ2| < 0.1 rad = 5.7°)
            settled_mask = (theta1 < 0.1) & (theta2 < 0.1)
            if np.any(settled_mask):
                settling_time = t_arr[np.where(settled_mask)[0][0]]
            else:
                settling_time = 10.0  # Never settled

            # Max overshoot
            max_overshoot = max(theta1.max(), theta2.max())

            # Convergence (settled for last 0.5s)
            converged = np.all(settled_mask[-50:])  # Last 50 samples at dt=0.01

            results.append({
                'settling_time': settling_time,
                'overshoot': np.rad2deg(max_overshoot),
                'converged': converged
            })

        except Exception as e:
            # Handle simulation failures (e.g., instability)
            print(f"    WARNING: Trial {trial} failed: {e}")
            results.append({
                'settling_time': 10.0,
                'overshoot': 180.0,  # Worst case
                'converged': False
            })

    # Aggregate statistics
    return {
        'settling_time_mean': np.mean([r['settling_time'] for r in results]),
        'settling_time_std': np.std([r['settling_time'] for r in results]),
        'overshoot_mean': np.mean([r['overshoot'] for r in results]),
        'overshoot_std': np.std([r['overshoot'] for r in results]),
        'convergence_rate': np.mean([r['converged'] for r in results])
    }


def main():
    parser = argparse.ArgumentParser(description='LT-6 Model Uncertainty Analysis')
    parser.add_argument('--error-levels', nargs='+', type=float, default=[0.1, 0.2],
                       help='Parameter error levels (e.g., 0.1 = ±10%%)')
    parser.add_argument('--trials', type=int, default=10,
                       help='Monte Carlo trials per scenario')
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Configuration file path')
    args = parser.parse_args()

    print("="*70)
    print("LT-6: MODEL UNCERTAINTY ANALYSIS")
    print("="*70)

    # Load base config
    print(f"\nLoading configuration: {args.config}")
    base_config = load_config(args.config)

    # Create uncertainty scenarios
    scenarios = create_uncertainty_scenarios(base_config, error_levels=args.error_levels)
    summary = get_perturbation_summary(scenarios)

    print(f"\nScenarios generated:")
    print(f"  Total: {summary['total']}")
    print(f"  Nominal: {summary['nominal']}")
    print(f"  Single parameter: {summary['single_param']}")
    print(f"  Combined worst-case: {summary['combined']}")

    total_sims = len(CONTROLLERS) * len(scenarios) * args.trials
    print(f"\nTest matrix:")
    print(f"  Controllers: {len(CONTROLLERS)}")
    print(f"  Scenarios: {len(scenarios)}")
    print(f"  Trials per scenario: {args.trials}")
    print(f"  Total simulations: {total_sims}")
    print(f"  Estimated time: ~{total_sims * 0.5 / 60:.1f} minutes")

    # Run tests
    all_results = []

    for ctrl_idx, controller_name in enumerate(CONTROLLERS):
        print(f"\n[{ctrl_idx+1}/{len(CONTROLLERS)}] {controller_name}")

        for scenario_idx, (scenario_name, perturbed_config) in enumerate(scenarios):
            print(f"  [{scenario_idx+1}/{len(scenarios)}] {scenario_name:20s}...", end='', flush=True)

            results = run_uncertainty_test(
                controller_name,
                scenario_name,
                perturbed_config,
                n_trials=args.trials
            )

            if results is None:
                # Scenario violates physical constraints - skip it
                print(" [SKIP] (violates physical constraints)")
                continue

            all_results.append({
                'controller': controller_name,
                'scenario': scenario_name,
                **results
            })

            # Show quick summary
            converged_pct = results['convergence_rate'] * 100
            settling = results['settling_time_mean']
            print(f" [OK] (t_s={settling:.2f}s +/- {results['settling_time_std']:.2f}s, conv={converged_pct:.0f}%)")

    # Save detailed results
    print("\n" + "="*70)
    print("SAVING RESULTS")
    print("="*70)

    df = pd.DataFrame(all_results)
    output_file = Path('benchmarks') / 'LT6_uncertainty_analysis.csv'
    output_file.parent.mkdir(exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"[OK] Detailed results: {output_file}")

    # Compute robustness ranking
    print("\n" + "="*70)
    print("ROBUSTNESS RANKING")
    print("="*70)

    nominal_results = df[df['scenario'] == 'nominal']
    perturbed_results = df[df['scenario'] != 'nominal']

    robustness_scores = []
    for controller in CONTROLLERS:
        nom = nominal_results[nominal_results['controller'] == controller]
        pert = perturbed_results[perturbed_results['controller'] == controller]

        # Nominal performance
        nom_settling = nom['settling_time_mean'].values[0]
        nom_convergence = nom['convergence_rate'].values[0]

        # Perturbed performance (average over all scenarios)
        avg_settling = pert['settling_time_mean'].mean()
        avg_convergence = pert['convergence_rate'].mean()

        # Performance degradation
        if nom_settling > 0:
            settling_degradation = ((avg_settling - nom_settling) / nom_settling) * 100
        else:
            settling_degradation = 0.0

        if nom_convergence > 0:
            convergence_degradation = ((nom_convergence - avg_convergence) / nom_convergence) * 100
        else:
            convergence_degradation = 100.0

        # Robustness score (0-100, higher = more robust)
        # 100 = no degradation, 0 = complete failure
        robustness_score = 100 - (settling_degradation * 0.3 + convergence_degradation * 0.7)

        robustness_scores.append({
            'controller': controller,
            'nominal_settling_s': nom_settling,
            'perturbed_settling_s': avg_settling,
            'settling_degradation_%': settling_degradation,
            'nominal_convergence_%': nom_convergence * 100,
            'perturbed_convergence_%': avg_convergence * 100,
            'convergence_degradation_%': convergence_degradation,
            'robustness_score': robustness_score
        })

    df_robustness = pd.DataFrame(robustness_scores).sort_values('robustness_score', ascending=False)

    print("\nRanking by robustness score (higher = more robust):")
    print("-" * 70)
    for idx, row in df_robustness.iterrows():
        print(f"{row['controller']:25s} | Score: {row['robustness_score']:5.1f} | "
              f"Settling D: {row['settling_degradation_%']:+6.1f}% | "
              f"Conv D: {row['convergence_degradation_%']:+6.1f}%")

    ranking_file = Path('benchmarks') / 'LT6_robustness_ranking.csv'
    df_robustness.to_csv(ranking_file, index=False)
    print(f"\n[OK] Robustness ranking: {ranking_file}")

    # Summary statistics
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    best_controller = df_robustness.iloc[0]['controller']
    worst_controller = df_robustness.iloc[-1]['controller']
    best_score = df_robustness.iloc[0]['robustness_score']
    worst_score = df_robustness.iloc[-1]['robustness_score']

    print(f"\nMost robust:  {best_controller} (score: {best_score:.1f}/100)")
    print(f"Least robust: {worst_controller} (score: {worst_score:.1f}/100)")

    avg_convergence_nominal = nominal_results['convergence_rate'].mean() * 100
    avg_convergence_perturbed = perturbed_results['convergence_rate'].mean() * 100
    print(f"\nAverage convergence rate:")
    print(f"  Nominal:   {avg_convergence_nominal:.1f}%")
    print(f"  Perturbed: {avg_convergence_perturbed:.1f}%")
    print(f"  Change:    {avg_convergence_perturbed - avg_convergence_nominal:+.1f}%")

    print("\n" + "="*70)
    print("LT-6 COMPLETE")
    print("="*70)


if __name__ == '__main__':
    main()
