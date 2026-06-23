"""
MT-8 Validation: Test Robust PSO Gains with Full Disturbance Suite

Validates optimized robust gains from MT-8 PSO optimization by running:
1. Monte Carlo validation (100 trials per scenario)
2. Statistical analysis (mean, std, 95% CI)
3. Convergence rate analysis
4. Comparison against baseline performance

Usage:
    python scripts/mt8_validate_robust_gains.py --controller classical_smc
    python scripts/mt8_validate_robust_gains.py --controller all --trials 100
    python scripts/mt8_validate_robust_gains.py --gains-file optimization_results/mt8_robust_classical_smc.json
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy import stats

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.controllers.factory import create_controller
from src.plant.core.dynamics import DIPDynamics
from scripts.research.mt8_disturbances.mt8_disturbance_rejection import (
    create_step_scenario,
    create_impulse_scenario,
    create_sinusoidal_scenario,
    create_random_scenario,
    run_simulation_with_disturbance,
    compute_metrics,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_robust_gains(controller_name: str, gains_file: str = None) -> np.ndarray:
    """
    Load robust PSO gains for a controller.

    Args:
        controller_name: Name of controller (e.g., 'classical_smc')
        gains_file: Optional path to gains file. If None, uses default location.

    Returns:
        Array of optimized gains
    """
    if gains_file is None:
        gains_file = f"optimization_results/mt8_robust_{controller_name}.json"

    gains_path = Path(gains_file)
    if not gains_path.exists():
        raise FileNotFoundError(f"Robust gains not found: {gains_file}")

    with open(gains_path, 'r') as f:
        data = json.load(f)

    gains = np.array(data['best_gains'])
    logger.info(f"Loaded robust gains from {gains_file}")
    logger.info(f"  Gains: {gains}")
    logger.info(f"  Robust fitness: {data['best_fitness']:.4f}")

    return gains


def validate_controller_monte_carlo(
    controller_name: str,
    gains: np.ndarray,
    dynamics: DIPDynamics,
    num_trials: int = 100,
    seed: int = 42
) -> Dict:
    """
    Run Monte Carlo validation on a controller with robust gains.

    Args:
        controller_name: Name of controller
        gains: Optimized gains to test
        dynamics: Dynamics model
        num_trials: Number of Monte Carlo trials per scenario
        seed: Random seed for reproducibility

    Returns:
        Dictionary with validation results
    """
    logger.info(f"\nValidating {controller_name} with {num_trials} trials per scenario...")

    np.random.seed(seed)

    # Disturbance scenarios
    scenarios = {
        'step': create_step_scenario(magnitude=10.0, start_time=2.0),
        'impulse': create_impulse_scenario(magnitude=30.0, start_time=2.0, duration=0.1),
        'sinusoidal': create_sinusoidal_scenario(amplitude=8.0, frequency=2.0, start_time=1.0),
        'random': create_random_scenario(std_dev=3.0, seed=seed),
    }

    results = {}

    for scenario_name, dist_gen in scenarios.items():
        logger.info(f"  Testing {scenario_name} disturbance...")

        trial_metrics = {
            'settling_time': [],
            'max_overshoot': [],
            'recovery_time': [],
            'control_effort': [],
            'converged': []
        }

        for trial in range(num_trials):
            # Reseed for this trial
            trial_seed = seed + trial
            np.random.seed(trial_seed)

            # Create fresh controller and disturbance
            controller = create_controller(controller_name, gains=list(gains))
            if scenario_name == 'random':
                dist_gen = create_random_scenario(std_dev=3.0, seed=trial_seed)

            try:
                t, x, u = run_simulation_with_disturbance(
                    controller=controller,
                    dynamics=dynamics,
                    disturbance_gen=dist_gen,
                    sim_time=10.0,
                    dt=0.01
                )

                metrics = compute_metrics(t, x, u, disturbance_start_time=2.0)

                trial_metrics['settling_time'].append(metrics['settling_time'])
                trial_metrics['max_overshoot'].append(metrics['max_overshoot'])
                trial_metrics['recovery_time'].append(metrics['recovery_time'])
                trial_metrics['control_effort'].append(metrics['control_effort'])
                trial_metrics['converged'].append(metrics['converged'])

            except Exception as e:
                logger.warning(f"    Trial {trial+1} failed: {e}")
                trial_metrics['settling_time'].append(10.0)
                trial_metrics['max_overshoot'].append(999.0)
                trial_metrics['recovery_time'].append(10.0)
                trial_metrics['control_effort'].append(999.0)
                trial_metrics['converged'].append(False)

        # Compute statistics
        settling_times = np.array(trial_metrics['settling_time'])
        overshoots = np.array(trial_metrics['max_overshoot'])
        recovery_times = np.array(trial_metrics['recovery_time'])
        control_efforts = np.array(trial_metrics['control_effort'])
        convergence_rate = np.mean(trial_metrics['converged'])

        # 95% confidence intervals
        settling_ci = stats.t.interval(
            0.95, len(settling_times)-1,
            loc=np.mean(settling_times),
            scale=stats.sem(settling_times)
        )

        overshoot_ci = stats.t.interval(
            0.95, len(overshoots)-1,
            loc=np.mean(overshoots),
            scale=stats.sem(overshoots)
        )

        results[scenario_name] = {
            'settling_time_mean': float(np.mean(settling_times)),
            'settling_time_std': float(np.std(settling_times)),
            'settling_time_ci': [float(settling_ci[0]), float(settling_ci[1])],
            'overshoot_mean': float(np.mean(overshoots)),
            'overshoot_std': float(np.std(overshoots)),
            'overshoot_ci': [float(overshoot_ci[0]), float(overshoot_ci[1])],
            'recovery_time_mean': float(np.mean(recovery_times)),
            'recovery_time_std': float(np.std(recovery_times)),
            'control_effort_mean': float(np.mean(control_efforts)),
            'control_effort_std': float(np.std(control_efforts)),
            'convergence_rate': float(convergence_rate),
            'num_trials': num_trials,
        }

        logger.info(f"    Settling time: {results[scenario_name]['settling_time_mean']:.2f} ± {results[scenario_name]['settling_time_std']:.2f} s")
        logger.info(f"    Overshoot: {results[scenario_name]['overshoot_mean']:.2f} ± {results[scenario_name]['overshoot_std']:.2f} deg")
        logger.info(f"    Convergence rate: {convergence_rate*100:.1f}%")

    return results


def compare_to_baseline(
    controller_name: str,
    robust_results: Dict,
    baseline_file: str = "benchmarks/MT8_disturbance_rejection.json"
) -> Dict:
    """
    Compare robust validation results to baseline performance.

    Args:
        controller_name: Name of controller
        robust_results: Validation results from robust gains
        baseline_file: Path to baseline results file

    Returns:
        Dictionary with comparison metrics
    """
    baseline_path = Path(baseline_file)
    if not baseline_path.exists():
        logger.warning(f"Baseline file not found: {baseline_file}")
        return {}

    with open(baseline_path, 'r') as f:
        baseline_data = json.load(f)

    # Extract baseline results for this controller
    baseline_results = {}
    for result in baseline_data['results']:
        if result['controller_name'] == controller_name:
            scenario = result['disturbance_type']
            baseline_results[scenario] = result

    # Compute improvements
    comparisons = {}
    for scenario in robust_results.keys():
        if scenario not in baseline_results:
            continue

        baseline = baseline_results[scenario]
        robust = robust_results[scenario]

        settling_improvement = (
            (baseline['settling_time'] - robust['settling_time_mean']) / baseline['settling_time'] * 100
        )
        overshoot_improvement = (
            (baseline['max_overshoot'] - robust['overshoot_mean']) / baseline['max_overshoot'] * 100
        )

        comparisons[scenario] = {
            'baseline_settling': baseline['settling_time'],
            'robust_settling': robust['settling_time_mean'],
            'settling_improvement_pct': float(settling_improvement),
            'baseline_overshoot': baseline['max_overshoot'],
            'robust_overshoot': robust['overshoot_mean'],
            'overshoot_improvement_pct': float(overshoot_improvement),
            'baseline_converged': baseline['converged'],
            'robust_convergence_rate': robust['convergence_rate'],
        }

    return comparisons


def main():
    parser = argparse.ArgumentParser(description='MT-8 Robust Gains Validation')
    parser.add_argument(
        '--controller',
        type=str,
        default='classical_smc',
        choices=['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc', 'all'],
        help='Controller to validate'
    )
    parser.add_argument(
        '--trials',
        type=int,
        default=100,
        help='Number of Monte Carlo trials per scenario'
    )
    parser.add_argument(
        '--gains-file',
        type=str,
        default=None,
        help='Path to gains file (default: optimization_results/mt8_robust_{controller}.json)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file for validation results (default: benchmarks/MT8_robust_validation_{controller}.json)'
    )

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("MT-8: Robust Gains Validation")
    logger.info(f"Trials per scenario: {args.trials}")
    logger.info("=" * 80)

    # Load configuration and dynamics
    config = load_config("config.yaml")
    dynamics = DIPDynamics(config.simulation)
    logger.info("Configuration loaded")
    logger.info("Dynamics model initialized")

    # Determine controllers to validate
    if args.controller == 'all':
        controllers = ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']
    else:
        controllers = [args.controller]

    # Validate each controller
    all_results = {}

    for controller_name in controllers:
        logger.info(f"\n{'='*80}")
        logger.info(f"Validating: {controller_name}")
        logger.info(f"{'='*80}")

        try:
            # Load robust gains
            gains = load_robust_gains(controller_name, args.gains_file)

            # Run Monte Carlo validation
            validation_results = validate_controller_monte_carlo(
                controller_name=controller_name,
                gains=gains,
                dynamics=dynamics,
                num_trials=args.trials,
                seed=args.seed
            )

            # Compare to baseline
            comparisons = compare_to_baseline(controller_name, validation_results)

            # Store results
            all_results[controller_name] = {
                'gains': gains.tolist(),
                'validation': validation_results,
                'comparison_to_baseline': comparisons,
                'num_trials': args.trials,
                'seed': args.seed,
            }

            # Print summary
            logger.info(f"\n{controller_name} Summary:")
            for scenario, comp in comparisons.items():
                logger.info(f"  {scenario}:")
                logger.info(f"    Settling: {comp['baseline_settling']:.2f}s -> {comp['robust_settling']:.2f}s ({comp['settling_improvement_pct']:+.1f}%)")
                logger.info(f"    Overshoot: {comp['baseline_overshoot']:.1f}° -> {comp['robust_overshoot']:.1f}° ({comp['overshoot_improvement_pct']:+.1f}%)")
                logger.info(f"    Convergence: {comp['baseline_converged']} -> {comp['robust_convergence_rate']*100:.1f}%")

        except Exception as e:
            logger.error(f"Validation failed for {controller_name}: {e}")
            continue

    # Save results
    if args.output is None:
        if len(controllers) == 1:
            output_file = f"benchmarks/MT8_robust_validation_{controllers[0]}.json"
        else:
            output_file = "benchmarks/MT8_robust_validation_all.json"
    else:
        output_file = args.output

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)

    logger.info(f"\n{'='*80}")
    logger.info(f"Validation results saved to: {output_file}")
    logger.info(f"{'='*80}")


if __name__ == "__main__":
    main()
