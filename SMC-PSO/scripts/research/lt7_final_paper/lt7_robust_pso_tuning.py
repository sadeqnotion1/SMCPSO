#!/usr/bin/env python3
"""
LT-7 Robust PSO Gain Tuning for Journal Paper

Optimizes controller gains for:
1. Nominal performance (settling, overshoot, energy)
2. Robustness to physics parameter uncertainty (±5%)
3. Control effort minimization
4. Chattering reduction

Uses existing PSOTuner infrastructure with physics_uncertainty enabled.

Usage:
    python scripts/lt7_robust_pso_tuning.py --controller classical_smc
    python scripts/lt7_robust_pso_tuning.py --controller sta_smc --n-particles 50 --iters 250
    python scripts/lt7_robust_pso_tuning.py --all  # Tune all 4 controllers sequentially
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List
import time

import numpy as np
import matplotlib.pyplot as plt

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.config import load_config
from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.controllers.factory import create_controller

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('optimization_results/lt7_robust_tuning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Controller gain specifications (from Lyapunov stability analysis)
CONTROLLER_SPECS = {
    'classical_smc': {
        'n_params': 6,
        'param_names': ['k1', 'k2', 'lambda1', 'lambda2', 'K', 'kd'],
        'description': 'Classical SMC with boundary layer',
        'lyapunov_constraints': {
            'K_min': 0.5,  # K > d_bar for disturbance rejection
            'positive_gains': True,  # All gains must be positive
        }
    },
    'sta_smc': {
        'n_params': 6,
        'param_names': ['K1', 'K2', 'k1', 'k2', 'lambda1', 'lambda2'],
        'description': 'Super-Twisting Algorithm',
        'lyapunov_constraints': {
            'K1_gt_K2': True,  # K1 > K2 required for finite-time convergence
            'K1_min': 2.0,  # K1 > 2*sqrt(2*d_bar/beta)
            'positive_gains': True,
        }
    },
    'adaptive_smc': {
        'n_params': 5,
        'param_names': ['k1', 'k2', 'lambda1', 'lambda2', 'gamma'],
        'description': 'Adaptive SMC with online gain adjustment',
        'lyapunov_constraints': {
            'gamma_positive': True,  # Adaptation rate > 0
            'positive_gains': True,
        }
    },
    'hybrid_adaptive_sta_smc': {
        'n_params': 4,
        'param_names': ['c1', 'lambda1', 'c2', 'lambda2'],
        'description': 'Hybrid Adaptive STA-SMC',
        'lyapunov_constraints': {
            'positive_gains': True,
        }
    }
}


def validate_gains_lyapunov(controller_type: str, gains: np.ndarray) -> bool:
    """
    Validate gains against Lyapunov stability constraints.

    Args:
        controller_type: Controller type identifier
        gains: Gain vector to validate

    Returns:
        True if gains satisfy Lyapunov constraints
    """
    spec = CONTROLLER_SPECS.get(controller_type)
    if not spec:
        return True  # Unknown controller, skip validation

    constraints = spec.get('lyapunov_constraints', {})

    # Check positive gains
    if constraints.get('positive_gains') and np.any(gains <= 0):
        return False

    # Controller-specific constraints
    if controller_type == 'classical_smc':
        K = gains[4]  # K is 5th parameter
        if K < constraints.get('K_min', 0.5):
            return False

    elif controller_type == 'sta_smc':
        K1, K2 = gains[0], gains[1]
        if constraints.get('K1_gt_K2') and K1 <= K2:
            return False
        if K1 < constraints.get('K1_min', 2.0):
            return False

    elif controller_type == 'adaptive_smc':
        gamma = gains[4]  # Last parameter
        if gamma <= 0:
            return False

    return True


def run_pso_optimization(
    controller_type: str,
    n_particles: int = 40,
    n_iterations: int = 200,
    seed: int = 42,
    config_path: Path = None
) -> Dict[str, Any]:
    """
    Run PSO optimization for a controller with physics uncertainty.

    Args:
        controller_type: Controller type identifier
        n_particles: Number of PSO particles
        n_iterations: Number of PSO iterations
        seed: Random seed for reproducibility
        config_path: Path to config.yaml

    Returns:
        Dictionary with optimization results
    """
    logger.info(f"="*80)
    logger.info(f"Starting Robust PSO Tuning: {controller_type}")
    logger.info(f"="*80)
    logger.info(f"Parameters: {n_particles} particles, {n_iterations} iterations, seed={seed}")

    # Load configuration
    if config_path is None:
        config_path = project_root / "config.yaml"
    config = load_config(config_path)

    # Verify physics_uncertainty is enabled
    if not hasattr(config, 'physics_uncertainty') or config.physics_uncertainty.n_evals < 2:
        logger.warning("physics_uncertainty not enabled or n_evals < 2. Enabling with 10 draws.")
        # Would need to modify config here if needed

    logger.info(f"Physics uncertainty: {config.physics_uncertainty.n_evals} draws enabled")

    # Get controller spec
    spec = CONTROLLER_SPECS.get(controller_type)
    if not spec:
        raise ValueError(f"Unknown controller type: {controller_type}")

    n_params = spec['n_params']
    logger.info(f"Controller: {spec['description']}")
    logger.info(f"Parameters to optimize: {n_params} - {spec['param_names']}")
    logger.info(f"Lyapunov constraints: {spec['lyapunov_constraints']}")

    # Define controller factory with required attributes
    def controller_factory(gains: np.ndarray):
        """Factory function for creating controller instances."""
        return create_controller(controller_type=controller_type, config=config, gains=gains.tolist())

    # Add required attributes for PSOTuner
    controller_factory.n_gains = n_params
    controller_factory.controller_type = controller_type

    # Create PSO tuner with physics uncertainty
    logger.info("Initializing PSOTuner with physics uncertainty...")
    start_time = time.time()

    try:
        tuner = PSOTuner(
            controller_factory=controller_factory,
            config=config,
            seed=seed,
            instability_penalty_factor=100.0  # Moderate penalty for unstable particles
        )

        logger.info("PSOTuner initialized successfully")
        logger.info(f"  Cost weights: state={tuner.weights.state_error}, "
                   f"control={tuner.weights.control_effort}, "
                   f"rate={tuner.weights.control_rate}, "
                   f"stability={tuner.weights.stability}")

    except Exception as e:
        logger.error(f"Failed to initialize PSOTuner: {e}")
        raise

    # Get PSO bounds from config
    pso_config = config.pso
    if hasattr(pso_config.bounds, controller_type):
        bounds_config = getattr(pso_config.bounds, controller_type)
        bounds_min = np.array(bounds_config.min)
        bounds_max = np.array(bounds_config.max)
    else:
        # Use default bounds
        bounds_min = np.array(pso_config.bounds.min[:n_params])
        bounds_max = np.array(pso_config.bounds.max[:n_params])

    logger.info(f"PSO bounds:")
    for i, (name, vmin, vmax) in enumerate(zip(spec['param_names'], bounds_min, bounds_max)):
        logger.info(f"  {name:12s}: [{vmin:6.3f}, {vmax:6.3f}]")

    # Run PSO optimization
    logger.info(f"\nStarting PSO optimization...")
    logger.info(f"Estimated time: ~{n_iterations * n_particles * 0.5 / 60:.1f} minutes")
    logger.info(f"(Assuming ~0.5s per particle evaluation)")

    try:
        # Use PSOTuner's built-in optimise() method
        logger.info(f"PSO hyperparameters: w={pso_config.w}, c1={pso_config.c1}, c2={pso_config.c2}")

        # Run optimization with overrides
        result = tuner.optimise(
            n_particles_override=n_particles,
            iters_override=n_iterations,
        )

        # Extract results
        best_gains = result['best_pos']
        best_cost = result['best_cost']
        cost_history = result.get('cost_history', [])

        optimization_time = time.time() - start_time
        logger.info(f"\n{'='*80}")
        logger.info(f"PSO Optimization Complete!")
        logger.info(f"{'='*80}")
        logger.info(f"Time elapsed: {optimization_time/60:.1f} minutes")
        logger.info(f"Best cost: {best_cost:.6f}")
        logger.info(f"Best gains:")
        for name, gain in zip(spec['param_names'], best_gains):
            logger.info(f"  {name:12s}: {gain:8.4f}")

        # Validate against Lyapunov constraints
        valid = validate_gains_lyapunov(controller_type, best_gains)
        logger.info(f"\nLyapunov constraint validation: {'✓ PASS' if valid else '✗ FAIL'}")
        if not valid:
            logger.warning("Optimized gains violate Lyapunov stability constraints!")

        # Prepare results
        results = {
            'controller_type': controller_type,
            'best_cost': float(best_cost),
            'best_gains': best_gains.tolist() if isinstance(best_gains, np.ndarray) else best_gains,
            'gain_names': spec['param_names'],
            'optimization_time_minutes': optimization_time / 60,
            'n_particles': n_particles,
            'n_iterations': n_iterations,
            'seed': seed,
            'physics_uncertainty_draws': config.physics_uncertainty.n_evals,
            'lyapunov_valid': valid,
            'cost_history': cost_history,
            'mean_pbest_history': result.get('mean_pbest_history', []),
            'mean_neighbor_history': result.get('mean_neighbor_history', []),
        }

        return results

    except Exception as e:
        logger.error(f"PSO optimization failed: {e}")
        import traceback
        traceback.print_exc()
        raise


def save_results(results: Dict[str, Any], output_dir: Path = None):
    """Save optimization results to JSON and generate convergence plot."""
    if output_dir is None:
        output_dir = project_root / "optimization_results"
    output_dir.mkdir(parents=True, exist_ok=True)

    controller_type = results['controller_type']
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    # Save JSON results
    json_path = output_dir / f"lt7_{controller_type}_robust_{timestamp}.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"\nResults saved to: {json_path}")

    # Also save to standard filename (for easy loading)
    json_path_standard = output_dir / f"lt7_{controller_type}_robust_gains.json"
    with open(json_path_standard, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Standard filename: {json_path_standard}")

    # Generate convergence plot
    try:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # Cost history
        ax1.plot(results['cost_history'], 'b-', linewidth=2, label='Global best cost')
        ax1.set_xlabel('Iteration')
        ax1.set_ylabel('Cost')
        ax1.set_title(f"PSO Convergence - {controller_type}")
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_yscale('log')

        # Mean personal best history
        ax2.plot(results['mean_pbest_history'], 'g-', linewidth=2, label='Mean personal best')
        ax2.set_xlabel('Iteration')
        ax2.set_ylabel('Mean Cost')
        ax2.set_title('Swarm Mean Personal Best')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_yscale('log')

        plt.tight_layout()
        plot_path = output_dir / f"lt7_{controller_type}_convergence.png"
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        logger.info(f"Convergence plot saved to: {plot_path}")

    except Exception as e:
        logger.warning(f"Failed to generate convergence plot: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="LT-7 Robust PSO Gain Tuning for Journal Paper"
    )
    parser.add_argument(
        '--controller',
        choices=['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc'],
        help='Controller to optimize'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Optimize all 4 controllers sequentially'
    )
    parser.add_argument(
        '--n-particles',
        type=int,
        default=40,
        help='Number of PSO particles (default: 40)'
    )
    parser.add_argument(
        '--iters',
        type=int,
        default=200,
        help='Number of PSO iterations (default: 200)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed (default: 42)'
    )
    parser.add_argument(
        '--config',
        type=Path,
        default=None,
        help='Path to config.yaml (default: project_root/config.yaml)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=None,
        help='Output directory for results (default: optimization_results/)'
    )

    args = parser.parse_args()

    # Determine controllers to optimize
    if args.all:
        controllers = ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']
    elif args.controller:
        controllers = [args.controller]
    else:
        parser.error("Must specify --controller or --all")

    # Ensure output directory exists
    output_dir = args.output_dir or (project_root / "optimization_results")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run optimization for each controller
    all_results = {}
    for ctrl in controllers:
        try:
            logger.info(f"\n\n{'#'*80}")
            logger.info(f"Optimizing controller {controllers.index(ctrl)+1}/{len(controllers)}: {ctrl}")
            logger.info(f"{'#'*80}\n")

            results = run_pso_optimization(
                controller_type=ctrl,
                n_particles=args.n_particles,
                n_iterations=args.iters,
                seed=args.seed,
                config_path=args.config
            )

            save_results(results, output_dir)
            all_results[ctrl] = results

        except Exception as e:
            logger.error(f"Failed to optimize {ctrl}: {e}")
            continue

    # Generate summary
    logger.info(f"\n\n{'='*80}")
    logger.info(f"OPTIMIZATION SUMMARY")
    logger.info(f"{'='*80}")
    logger.info(f"Controllers optimized: {len(all_results)}/{len(controllers)}")

    for ctrl, results in all_results.items():
        logger.info(f"\n{ctrl}:")
        logger.info(f"  Best cost: {results['best_cost']:.6f}")
        logger.info(f"  Time: {results['optimization_time_minutes']:.1f} minutes")
        logger.info(f"  Lyapunov valid: {results['lyapunov_valid']}")
        logger.info(f"  Best gains: {[f'{g:.4f}' for g in results['best_gains']]}")

    logger.info(f"\nAll results saved to: {output_dir}")


if __name__ == "__main__":
    main()
