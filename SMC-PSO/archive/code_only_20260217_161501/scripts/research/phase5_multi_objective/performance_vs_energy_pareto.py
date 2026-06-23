#!/usr/bin/env python3
"""
Phase 5: Multi-Objective PSO - Performance vs Energy Pareto Front
================================================================================

Generates Pareto-optimal solutions for the trade-off between tracking performance
(RMSE) and energy efficiency (RMS control effort) using weighted-sum multi-objective PSO.

Strategy:
- Run PSO with multiple weight combinations: w1*RMSE + w2*energy
- Weight combinations: [(0.9, 0.1), (0.7, 0.3), (0.5, 0.5), (0.3, 0.7), (0.1, 0.9)]
- Collect all optimized solutions
- Filter for non-dominated solutions (Pareto front)
- Visualize trade-off frontier

Part of Option B Framework 1 completion (Phase 5: Multi-Objective Expansion)
Author: AI Workspace (Claude Code)
Created: January 5, 2026
"""

import numpy as np
import json
import logging
import sys
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config import load_config
from src.core.dynamics import DIPDynamics
from src.controllers.factory import create_controller

# Configure logging
log_dir = project_root / "academic" / "logs" / "pso"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'phase5_performance_vs_energy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ParetoSolution:
    """Single solution on Pareto front."""
    controller: str
    gains: List[float]
    rmse: float
    energy: float
    fitness: float
    weight_rmse: float
    weight_energy: float
    is_dominated: bool = False


def simulate_with_controller(
    controller,
    dynamics: DIPDynamics,
    sim_time: float = 10.0,
    dt: float = 0.01,
    u_max: float = 150.0,
    initial_state: np.ndarray = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Simulate system with a controller."""
    n_steps = int(round(sim_time / dt))
    if initial_state is None:
        initial_state = np.array([0, 0.1, 0.1, 0, 0, 0])

    t_arr = np.zeros(n_steps + 1)
    x_arr = np.zeros((n_steps + 1, 6))
    u_arr = np.zeros(n_steps)

    x_arr[0] = initial_state
    t_arr[0] = 0.0

    if hasattr(controller, 'initialize_state'):
        ctrl_state = controller.initialize_state()
    else:
        ctrl_state = None

    if hasattr(controller, 'initialize_history'):
        history = controller.initialize_history()
    else:
        history = None

    x_curr = initial_state.copy()
    for i in range(n_steps):
        t_now = i * dt
        t_arr[i] = t_now

        try:
            result = controller.compute_control(x_curr, ctrl_state, history)
            if isinstance(result, dict):
                u_nominal = float(result['u'])
                ctrl_state = result.get('state', ctrl_state)
                history = result.get('history', history)
            elif hasattr(result, 'u'):
                u_nominal = float(result.u)
                ctrl_state = result.state if hasattr(result, 'state') else ctrl_state
                history = result.history if hasattr(result, 'history') else history
            else:
                u_nominal = float(result)
        except Exception as e:
            logger.warning(f"Control computation failed at t={t_now:.2f}s: {e}")
            u_nominal = 0.0

        u_total = np.clip(u_nominal, -u_max, u_max)
        u_arr[i] = u_total

        try:
            x_next = dynamics.step(x_curr, u_total, dt)
        except Exception as e:
            logger.error(f"Dynamics step failed at t={t_now:.2f}s: {e}")
            break

        if not np.all(np.isfinite(x_next)):
            logger.warning(f"Simulation diverged at t={t_now:.2f}s")
            break

        x_curr = x_next
        x_arr[i + 1] = x_curr

    t_arr[-1] = n_steps * dt
    return t_arr, x_arr, u_arr


def compute_energy_index(u_arr: np.ndarray, dt: float = 0.01) -> float:
    """Compute energy index as RMS of control effort."""
    if len(u_arr) == 0:
        return 0.0

    energy = np.sqrt(np.mean(u_arr ** 2))
    return float(energy)


def compute_rmse(x_arr: np.ndarray) -> float:
    """Compute RMSE of angles (tracking error)."""
    theta1 = x_arr[:, 1]
    theta2 = x_arr[:, 2]
    rmse = np.sqrt(np.mean(theta1**2 + theta2**2))
    return float(rmse)


def compute_objectives(
    t_arr: np.ndarray,
    x_arr: np.ndarray,
    u_arr: np.ndarray,
    dt: float = 0.01
) -> Tuple[float, float]:
    """Compute both objectives: RMSE and energy."""
    rmse = compute_rmse(x_arr)
    energy = compute_energy_index(u_arr, dt)
    return rmse, energy


def objective_function(
    gains: np.ndarray,
    config: Any,
    controller_type: str,
    weight_rmse: float,
    weight_energy: float
) -> float:
    """Multi-objective fitness function with weighted sum."""
    try:
        temp_config = config.model_copy(deep=True)

        if hasattr(temp_config.controller_defaults, controller_type):
            default_ctrl = getattr(temp_config.controller_defaults, controller_type)
            updated = default_ctrl.model_copy(update={'gains': gains.tolist()})
            setattr(temp_config.controller_defaults, controller_type, updated)

        if hasattr(temp_config.controllers, controller_type):
            ctrl = getattr(temp_config.controllers, controller_type)
            updated = ctrl.model_copy(update={'gains': gains.tolist()})
            setattr(temp_config.controllers, controller_type, updated)

        controller = create_controller(controller_type=controller_type, config=temp_config)
        dynamics = DIPDynamics(config=config.physics)

        t_arr, x_arr, u_arr = simulate_with_controller(
            controller, dynamics,
            sim_time=10.0, dt=0.01
        )

        rmse, energy = compute_objectives(t_arr, x_arr, u_arr, dt=0.01)

        # Weighted sum fitness
        fitness = weight_rmse * rmse + weight_energy * energy

        return fitness

    except Exception as e:
        logger.error(f"Objective function failed: {e}")
        return 1e6


def is_dominated(solution1: ParetoSolution, solution2: ParetoSolution) -> bool:
    """Check if solution1 is dominated by solution2 (minimization)."""
    rmse_worse = solution1.rmse >= solution2.rmse
    energy_worse = solution1.energy >= solution2.energy
    at_least_one_strictly_worse = (solution1.rmse > solution2.rmse) or (solution1.energy > solution2.energy)

    return rmse_worse and energy_worse and at_least_one_strictly_worse


def filter_pareto_front(solutions: List[ParetoSolution]) -> List[ParetoSolution]:
    """Filter solutions to keep only non-dominated (Pareto-optimal) ones."""
    pareto_front = []

    for sol in solutions:
        dominated = False
        for other in solutions:
            if is_dominated(sol, other):
                dominated = True
                break

        if not dominated:
            sol.is_dominated = False
            pareto_front.append(sol)
        else:
            sol.is_dominated = True

    return pareto_front


def run_mopso_controller(
    controller_type: str,
    n_particles: int = 30,
    n_iterations: int = 50,
    seed: int = 42
) -> List[ParetoSolution]:
    """Run multi-objective PSO with multiple weight combinations."""
    logger.info("=" * 80)
    logger.info(f"Phase 5: Performance vs Energy MOPSO - {controller_type}")
    logger.info("=" * 80)

    config = load_config('config.yaml', allow_unknown=False)

    # Get original gains
    if controller_type == 'classical_smc':
        original_gains = config.controller_defaults.classical_smc.gains
    elif controller_type == 'adaptive_smc':
        original_gains = config.controller_defaults.adaptive_smc.gains
    elif controller_type == 'hybrid_adaptive_sta_smc':
        original_gains = config.controller_defaults.hybrid_adaptive_sta_smc.gains
    else:
        raise ValueError(f"Unknown controller: {controller_type}")

    logger.info(f"Original gains: {original_gains}")

    # Define bounds
    bounds = []
    for g in original_gains:
        lower = max(0.01, g * 0.5)
        upper = g * 1.5
        bounds.append((lower, upper))

    # Weight combinations for Pareto front approximation
    weight_combinations = [
        (0.9, 0.1),   # Performance-focused
        (0.7, 0.3),   # Phase 4 default
        (0.5, 0.5),   # Balanced
        (0.3, 0.7),   # Energy-focused
        (0.1, 0.9)    # Maximum energy reduction
    ]

    from pyswarms.single import GlobalBestPSO

    solutions = []

    for w_rmse, w_energy in weight_combinations:
        logger.info(f"\nRunning PSO with weights: RMSE={w_rmse:.1f}, Energy={w_energy:.1f}")

        if seed is not None:
            np.random.seed(seed)

        pso_options = {
            'c1': 2.0,
            'c2': 2.0,
            'w': 0.9
        }

        optimizer = GlobalBestPSO(
            n_particles=n_particles,
            dimensions=len(original_gains),
            options=pso_options,
            bounds=(np.array([b[0] for b in bounds]), np.array([b[1] for b in bounds]))
        )

        best_fitness, optimized_gains = optimizer.optimize(
            lambda p: np.array([objective_function(gains, config, controller_type, w_rmse, w_energy) for gains in p]),
            iters=n_iterations
        )

        # Evaluate optimized solution
        temp_config = config.model_copy(deep=True)
        if hasattr(temp_config.controller_defaults, controller_type):
            default_ctrl = getattr(temp_config.controller_defaults, controller_type)
            updated = default_ctrl.model_copy(update={'gains': optimized_gains.tolist()})
            setattr(temp_config.controller_defaults, controller_type, updated)

        controller = create_controller(controller_type=controller_type, config=temp_config)
        dynamics = DIPDynamics(config=config.physics)
        t_arr, x_arr, u_arr = simulate_with_controller(controller, dynamics)
        rmse, energy = compute_objectives(t_arr, x_arr, u_arr)

        solution = ParetoSolution(
            controller=controller_type,
            gains=optimized_gains.tolist(),
            rmse=rmse,
            energy=energy,
            fitness=best_fitness,
            weight_rmse=w_rmse,
            weight_energy=w_energy
        )

        solutions.append(solution)
        logger.info(f"  Result: RMSE={rmse:.4f}, Energy={energy:.4f}, Fitness={best_fitness:.4f}")

    # Filter Pareto front
    pareto_front = filter_pareto_front(solutions)
    logger.info(f"\nPareto front: {len(pareto_front)}/{len(solutions)} non-dominated solutions")

    return solutions


def save_pareto_results(
    solutions: List[ParetoSolution],
    controller_type: str,
    output_dir: Path
):
    """Save Pareto front results."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save all solutions CSV
    df = pd.DataFrame([{
        'controller': sol.controller,
        'rmse': sol.rmse,
        'energy': sol.energy,
        'fitness': sol.fitness,
        'weight_rmse': sol.weight_rmse,
        'weight_energy': sol.weight_energy,
        'is_dominated': sol.is_dominated,
        'gains': json.dumps(sol.gains)
    } for sol in solutions])

    csv_file = output_dir / f"{controller_type}_performance_vs_energy_all.csv"
    df.to_csv(csv_file, index=False)
    logger.info(f"Saved all solutions: {csv_file}")

    # Save Pareto front only
    pareto_df = df[df['is_dominated'] == False]
    pareto_csv = output_dir / f"{controller_type}_performance_vs_energy_pareto.csv"
    pareto_df.to_csv(pareto_csv, index=False)
    logger.info(f"Saved Pareto front: {pareto_csv}")

    # Create visualization
    plt.figure(figsize=(10, 8))

    # Plot all solutions
    dominated = df[df['is_dominated'] == True]
    non_dominated = df[df['is_dominated'] == False]

    plt.scatter(dominated['rmse'], dominated['energy'],
                alpha=0.3, s=50, color='gray', label='Dominated')
    plt.scatter(non_dominated['rmse'], non_dominated['energy'],
                alpha=0.8, s=100, color='blue', marker='*',
                label='Pareto Front', edgecolors='black', linewidths=1.5)

    # Sort Pareto front for line connection
    pareto_sorted = non_dominated.sort_values('rmse')
    plt.plot(pareto_sorted['rmse'], pareto_sorted['energy'],
             'b--', alpha=0.5, linewidth=2)

    plt.xlabel('RMSE (rad)', fontweight='bold', fontsize=12)
    plt.ylabel('Energy Index (RMS u)', fontweight='bold', fontsize=12)
    plt.title(f'Performance vs Energy Pareto Front\n{controller_type.replace("_", " ").title()}',
              fontweight='bold', fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plot_file = output_dir / f"{controller_type}_performance_vs_energy_pareto.png"
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    logger.info(f"Saved Pareto plot: {plot_file}")
    plt.close()


def main():
    """Run Pareto front generation for all controllers."""
    logger.info("=" * 80)
    logger.info("Phase 5: Performance vs Energy Multi-Objective PSO")
    logger.info("=" * 80)

    controllers = ['classical_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']

    for ctrl in controllers:
        solutions = run_mopso_controller(
            controller_type=ctrl,
            n_particles=30,
            n_iterations=50,
            seed=42
        )

        output_dir = project_root / "academic" / "paper" / "experiments" / "comparative" / "mopso_performance_energy"
        save_pareto_results(solutions, ctrl, output_dir)

    logger.info("=" * 80)
    logger.info("[OK] Performance vs Energy MOPSO complete!")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
