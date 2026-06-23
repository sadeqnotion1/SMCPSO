#!/usr/bin/env python3
"""
MT-8 Robust PSO Optimization: Disturbance-Aware Controller Tuning
================================================================================

Optimizes SMC controller gains for BOTH nominal performance AND disturbance
rejection. Uses a robust fitness function:

    fitness = 0.5 * cost_nominal + 0.5 * cost_disturbed

This ensures controllers are tuned to handle external disturbances, not just
perfect conditions.

Author: MT-8 Optimization Team
Created: November 8, 2025
"""

import numpy as np
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.config import load_config
from src.core.dynamics import DIPDynamics
from src.controllers.factory import create_controller
from src.utils.disturbances import create_step_scenario, create_impulse_scenario

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.logs/benchmarks/mt8_robust_pso.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class RobustPSOResult:
    """Results from robust PSO optimization."""
    controller_name: str
    original_gains: List[float]
    optimized_gains: List[float]
    nominal_cost_before: float
    nominal_cost_after: float
    disturbed_cost_before: float
    disturbed_cost_after: float
    robust_cost_before: float
    robust_cost_after: float
    improvement_pct: float
    n_iterations: int
    n_particles: int
    converged: bool


def simulate_with_controller(
    controller,
    dynamics: DIPDynamics,
    disturbance_gen=None,
    sim_time: float = 10.0,
    dt: float = 0.01,
    u_max: float = 150.0,
    initial_state: np.ndarray = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulate system with a controller.

    Args:
        controller: Controller instance
        dynamics: Dynamics model
        disturbance_gen: Optional disturbance generator
        sim_time: Simulation duration (s)
        dt: Timestep (s)
        u_max: Maximum control force (N)
        initial_state: Initial state (if None, use small perturbation)

    Returns:
        Tuple of (time_array, state_array, control_array)
    """
    n_steps = int(round(sim_time / dt))
    if initial_state is None:
        initial_state = np.array([0, 0.1, 0.1, 0, 0, 0])  # Small angle perturbation

    t_arr = np.zeros(n_steps + 1)
    x_arr = np.zeros((n_steps + 1, 6))
    u_arr = np.zeros(n_steps)

    x_arr[0] = initial_state
    t_arr[0] = 0.0

    # Initialize controller state
    if hasattr(controller, 'initialize_state'):
        ctrl_state = controller.initialize_state()
    else:
        ctrl_state = None

    if hasattr(controller, 'initialize_history'):
        history = controller.initialize_history()
    else:
        history = None

    # Simulation loop
    x_curr = initial_state.copy()
    for i in range(n_steps):
        t_now = i * dt
        t_arr[i] = t_now

        # Compute nominal control
        try:
            if ctrl_state is not None and history is not None:
                result = controller.compute_control(x_curr, ctrl_state, history)
                if hasattr(result, 'u'):
                    u_nominal = float(result.u)
                    ctrl_state = result.state if hasattr(result, 'state') else ctrl_state
                    history = result.history if hasattr(result, 'history') else history
                else:
                    u_nominal = float(result)
            else:
                result = controller.compute_control(x_curr)
                u_nominal = float(result.u) if hasattr(result, 'u') else float(result)
        except Exception as e:
            logger.warning(f"Control computation failed at t={t_now:.2f}s: {e}")
            u_nominal = 0.0

        # Add disturbance if provided
        if disturbance_gen is not None:
            d_cart = disturbance_gen.get_disturbance_force_only(t_now)
            u_total = u_nominal + d_cart
        else:
            u_total = u_nominal

        # Saturate
        u_total = np.clip(u_total, -u_max, u_max)
        u_arr[i] = u_total

        # Step dynamics
        try:
            x_next = dynamics.step(x_curr, u_total, dt)
        except Exception as e:
            logger.error(f"Dynamics step failed at t={t_now:.2f}s: {e}")
            break

        # Check for divergence
        if not np.all(np.isfinite(x_next)):
            logger.warning(f"Simulation diverged at t={t_now:.2f}s")
            break

        x_curr = x_next
        x_arr[i + 1] = x_curr

    t_arr[-1] = n_steps * dt
    return t_arr, x_arr, u_arr


def compute_cost(
    t_arr: np.ndarray,
    x_arr: np.ndarray,
    u_arr: np.ndarray,
    settling_threshold: float = np.radians(5)  # 5 degrees
) -> float:
    """
    Compute control cost from trajectory.

    Cost combines:
    - Settling time (70%)
    - Peak overshoot (20%)
    - Energy consumption (10%)

    Args:
        t_arr: Time array
        x_arr: State array
        u_arr: Control array
        settling_threshold: Angle threshold for "settled" (rad)

    Returns:
        Scalar cost (lower is better)
    """
    # Extract angles
    theta1 = x_arr[:, 1]
    theta2 = x_arr[:, 2]

    # 1. Settling time (time when angles stay within threshold for 0.5s)
    settled_mask = (np.abs(theta1) < settling_threshold) & (np.abs(theta2) < settling_threshold)
    settling_time = 10.0  # Default: didn't settle
    for i in range(len(settled_mask) - 50):
        if np.all(settled_mask[i:i + 50]):  # 0.5s = 50 samples at dt=0.01
            settling_time = t_arr[i]
            break

    # 2. Peak overshoot
    theta_max = np.max(np.abs(np.concatenate([theta1, theta2])))
    overshoot = np.degrees(theta_max)

    # 3. Energy consumption (RMS control effort)
    energy = np.sqrt(np.mean(u_arr**2))

    # Weighted combination
    cost = 0.7 * settling_time + 0.2 * (overshoot / 30.0) + 0.1 * (energy / 50.0)

    return float(cost)


def evaluate_robust_fitness(
    gains: np.ndarray,
    controller_name: str,
    dynamics: DIPDynamics,
    nominal_weight: float = 0.5,
    disturbed_weight: float = 0.5
) -> float:
    """
    Evaluate robust fitness for a set of gains.

    Fitness = nominal_weight * cost_nominal + disturbed_weight * cost_disturbed

    Args:
        gains: Controller gains
        controller_name: Name of controller
        dynamics: Dynamics model
        nominal_weight: Weight for nominal performance (default: 0.5)
        disturbed_weight: Weight for disturbed performance (default: 0.5)

    Returns:
        Scalar fitness (lower is better)
    """
    # Create controller
    try:
        controller = create_controller(controller_name, gains=list(gains))
    except Exception as e:
        logger.warning(f"Failed to create controller with gains {gains}: {e}")
        return 1e6  # Penalty for invalid gains

    # 1. Evaluate nominal performance
    try:
        t_nom, x_nom, u_nom = simulate_with_controller(controller, dynamics)
        cost_nominal = compute_cost(t_nom, x_nom, u_nom)
    except Exception as e:
        logger.warning(f"Nominal simulation failed: {e}")
        return 1e6

    # 2. Evaluate disturbed performance (average over 2 scenarios)
    disturbance_scenarios = [
        create_step_scenario(magnitude=10.0, start_time=2.0),
        create_impulse_scenario(magnitude=30.0, start_time=2.0, duration=0.1),
    ]

    disturbed_costs = []
    for dist_gen in disturbance_scenarios:
        try:
            # Create fresh controller for each trial
            controller = create_controller(controller_name, gains=list(gains))
            t_dist, x_dist, u_dist = simulate_with_controller(controller, dynamics, dist_gen)
            cost_dist = compute_cost(t_dist, x_dist, u_dist)
            disturbed_costs.append(cost_dist)
        except Exception as e:
            logger.warning(f"Disturbed simulation failed: {e}")
            disturbed_costs.append(1e6)

    cost_disturbed = np.mean(disturbed_costs)

    # 3. Combine
    robust_fitness = nominal_weight * cost_nominal + disturbed_weight * cost_disturbed

    return float(robust_fitness)


def optimize_controller_robust_pso(
    controller_name: str,
    dynamics: DIPDynamics,
    config: Any,
    n_particles: int = 30,
    n_iterations: int = 50,
    bounds_min: List[float] = None,
    bounds_max: List[float] = None
) -> RobustPSOResult:
    """
    Optimize controller gains using robust PSO.

    Args:
        controller_name: Name of controller to optimize
        dynamics: Dynamics model
        config: Configuration object
        n_particles: Number of PSO particles
        n_iterations: Number of PSO iterations
        bounds_min: Lower bounds for gains
        bounds_max: Upper bounds for gains

    Returns:
        RobustPSOResult with optimization results
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"Optimizing: {controller_name} (Robust PSO)")
    logger.info(f"{'='*80}")
    logger.info(f"  Particles: {n_particles}, Iterations: {n_iterations}")

    # Get original gains
    original_gains = list(getattr(config.controller_defaults, controller_name).gains)
    n_gains = len(original_gains)

    # Get bounds
    if bounds_min is None or bounds_max is None:
        pso_bounds = getattr(config.pso.bounds, controller_name, None)
        if pso_bounds is not None:
            bounds_min = pso_bounds.min
            bounds_max = pso_bounds.max
        else:
            # Fallback to default bounds
            bounds_min = [0.1] * n_gains
            bounds_max = [30.0] * n_gains

    logger.info(f"  Gain bounds: [{bounds_min[0]:.1f}, {bounds_max[0]:.1f}] (×{n_gains})")

    # Evaluate original gains
    logger.info("  Evaluating original gains...")
    original_fitness = evaluate_robust_fitness(
        np.array(original_gains), controller_name, dynamics
    )
    logger.info(f"    Original robust fitness: {original_fitness:.4f}")

    # PSO optimization using pyswarms
    try:
        import pyswarms as ps
    except ImportError:
        logger.error("PySwarms not installed! Run: pip install pyswarms")
        raise

    # Define fitness function for swarm
    def fitness_func(particles: np.ndarray) -> np.ndarray:
        """Vectorized fitness evaluation for swarm."""
        costs = []
        for i, particle in enumerate(particles):
            cost = evaluate_robust_fitness(particle, controller_name, dynamics)
            costs.append(cost)
            if (i + 1) % 5 == 0:
                logger.info(f"    Evaluated {i+1}/{len(particles)} particles...")
        return np.array(costs)

    # Setup PSO
    bounds = (np.array(bounds_min), np.array(bounds_max))
    options = {'c1': 2.0, 'c2': 2.0, 'w': 0.7}  # Cognitive, social, inertia

    logger.info(f"  Starting PSO optimization...")
    optimizer = ps.single.GlobalBestPSO(
        n_particles=n_particles,
        dimensions=n_gains,
        options=options,
        bounds=bounds
    )

    # Run optimization
    best_cost, best_gains = optimizer.optimize(
        fitness_func,
        iters=n_iterations,
        verbose=False
    )

    logger.info(f"  [OK] PSO complete!")
    logger.info(f"    Best robust fitness: {best_cost:.4f}")
    logger.info(f"    Improvement: {100*(original_fitness - best_cost)/original_fitness:.1f}%")
    logger.info(f"    Optimized gains: {[f'{g:.3f}' for g in best_gains]}")

    # Compute detailed costs for result
    # Original performance
    ctrl_orig = create_controller(controller_name, gains=original_gains)
    t_nom_o, x_nom_o, u_nom_o = simulate_with_controller(ctrl_orig, dynamics)
    nominal_cost_before = compute_cost(t_nom_o, x_nom_o, u_nom_o)

    dist_step_o = create_step_scenario(magnitude=10.0, start_time=2.0)
    ctrl_orig_d = create_controller(controller_name, gains=original_gains)
    t_dist_o, x_dist_o, u_dist_o = simulate_with_controller(ctrl_orig_d, dynamics, dist_step_o)
    disturbed_cost_before = compute_cost(t_dist_o, x_dist_o, u_dist_o)

    # Optimized performance
    ctrl_opt = create_controller(controller_name, gains=list(best_gains))
    t_nom_n, x_nom_n, u_nom_n = simulate_with_controller(ctrl_opt, dynamics)
    nominal_cost_after = compute_cost(t_nom_n, x_nom_n, u_nom_n)

    dist_step_n = create_step_scenario(magnitude=10.0, start_time=2.0)
    ctrl_opt_d = create_controller(controller_name, gains=list(best_gains))
    t_dist_n, x_dist_n, u_dist_n = simulate_with_controller(ctrl_opt_d, dynamics, dist_step_n)
    disturbed_cost_after = compute_cost(t_dist_n, x_dist_n, u_dist_n)

    result = RobustPSOResult(
        controller_name=controller_name,
        original_gains=original_gains,
        optimized_gains=list(best_gains),
        nominal_cost_before=nominal_cost_before,
        nominal_cost_after=nominal_cost_after,
        disturbed_cost_before=disturbed_cost_before,
        disturbed_cost_after=disturbed_cost_after,
        robust_cost_before=original_fitness,
        robust_cost_after=best_cost,
        improvement_pct=100.0 * (original_fitness - best_cost) / original_fitness,
        n_iterations=n_iterations,
        n_particles=n_particles,
        converged=True
    )

    return result


def main():
    """Main MT-8 robust PSO execution."""
    import argparse
    parser = argparse.ArgumentParser(description='MT-8: Robust PSO Optimization')
    parser.add_argument('--controller', type=str, default='all',
                        help='Controller to optimize (classical_smc, sta_smc, adaptive_smc, hybrid_adaptive_sta_smc, or all)')
    parser.add_argument('--particles', type=int, default=30, help='Number of PSO particles')
    parser.add_argument('--iterations', type=int, default=50, help='Number of PSO iterations')
    args = parser.parse_args()

    logger.info("="*80)
    logger.info("MT-8: Robust PSO Optimization")
    logger.info(f"Particles: {args.particles}, Iterations: {args.iterations}")
    logger.info("="*80)

    # Load config
    config = load_config("config.yaml")
    logger.info("Configuration loaded")

    # Create dynamics
    dynamics = DIPDynamics(config.physics)
    logger.info("Dynamics model initialized")

    # Define controllers to optimize
    if args.controller == 'all':
        controllers = ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']
    else:
        controllers = [args.controller]

    logger.info(f"\nOptimizing {len(controllers)} controller(s):")
    for name in controllers:
        logger.info(f"  - {name}")

    # Run optimization
    all_results = []
    for controller_name in controllers:
        try:
            result = optimize_controller_robust_pso(
                controller_name=controller_name,
                dynamics=dynamics,
                config=config,
                n_particles=args.particles,
                n_iterations=args.iterations
            )
            all_results.append(result)

            # Save gains immediately
            gains_file = Path(f"optimization_results/mt8_robust_{controller_name}.json")
            gains_file.parent.mkdir(exist_ok=True)
            with open(gains_file, 'w') as f:
                json.dump({
                    'controller': controller_name,
                    'gains': result.optimized_gains,
                    'robust_cost': result.robust_cost_after,
                    'improvement_pct': result.improvement_pct
                }, f, indent=2)
            logger.info(f"  [OK] Saved gains: {gains_file}")

        except Exception as e:
            logger.error(f"ERROR optimizing {controller_name}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Save summary
    logger.info(f"\n{'='*80}")
    logger.info("Saving optimization summary...")
    logger.info(f"{'='*80}")

    summary_file = Path("optimization_results/mt8_robust_pso_summary.json")
    with open(summary_file, 'w') as f:
        json.dump({
            'controllers_optimized': [r.controller_name for r in all_results],
            'n_particles': args.particles,
            'n_iterations': args.iterations,
            'results': [asdict(r) for r in all_results]
        }, f, indent=2)
    logger.info(f"[OK] Saved summary: {summary_file}")

    # Print summary
    logger.info(f"\n{'='*80}")
    logger.info("OPTIMIZATION SUMMARY")
    logger.info(f"{'='*80}")
    logger.info(f"\n{'Controller':<30} {'Original Cost':<15} {'Optimized Cost':<15} {'Improvement'}")
    logger.info('-'*80)
    for result in all_results:
        logger.info(
            f"{result.controller_name:<30} {result.robust_cost_before:<15.4f} "
            f"{result.robust_cost_after:<15.4f} {result.improvement_pct:>6.1f}%"
        )

    logger.info(f"\n{'='*80}")
    logger.info("MT-8 ROBUST PSO COMPLETE!")
    logger.info(f"{'='*80}")


if __name__ == "__main__":
    main()
