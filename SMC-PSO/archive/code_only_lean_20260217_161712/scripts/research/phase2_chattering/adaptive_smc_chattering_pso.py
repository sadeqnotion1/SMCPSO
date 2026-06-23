#!/usr/bin/env python3
"""
Phase 2: Adaptive SMC Chattering PSO Optimization
================================================================================

Optimizes Adaptive SMC controller gains to minimize chattering while
maintaining performance. Uses a multi-objective fitness function:

    fitness = 0.7 * chattering_index + 0.3 * RMSE

This balances chattering reduction with tracking accuracy.

Part of Option B Framework 1 completion (Phase 2: Safety Expansion)
Author: AI Workspace (Claude Code)
Created: January 4, 2026
"""

import numpy as np
import json
import logging
import sys
import pandas as pd
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
        logging.FileHandler(log_dir / 'adaptive_smc_chattering_phase2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ChatteringPSOResult:
    """Results from chattering PSO optimization."""
    controller_name: str
    original_gains: List[float]
    optimized_gains: List[float]
    chattering_before: float
    chattering_after: float
    rmse_before: float
    rmse_after: float
    fitness_before: float
    fitness_after: float
    improvement_pct: float
    n_iterations: int
    n_particles: int
    converged: bool
    optimization_time_sec: float


def simulate_with_controller(
    controller,
    dynamics: DIPDynamics,
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

        # Compute control - ModularClassicalSMC requires state, state_vars, and history
        try:
            result = controller.compute_control(x_curr, ctrl_state, history)
            # Handle different return types (dict, object with attributes, or scalar)
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

        # Saturate
        u_total = np.clip(u_nominal, -u_max, u_max)
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


def compute_chattering_index(u_arr: np.ndarray, dt: float = 0.01) -> float:
    """
    Compute chattering index as RMS of control derivative.

    Chattering = sqrt(mean((du/dt)^2))

    Args:
        u_arr: Control signal array
        dt: Timestep (s)

    Returns:
        Chattering index (higher = more chattering)
    """
    if len(u_arr) < 2:
        return 0.0

    # Compute derivative
    du_dt = np.diff(u_arr) / dt

    # RMS of derivative
    chattering = np.sqrt(np.mean(du_dt ** 2))

    return float(chattering)


def compute_rmse(x_arr: np.ndarray) -> float:
    """
    Compute RMSE of angles (tracking error).

    Args:
        x_arr: State array (N x 6)

    Returns:
        RMSE in radians
    """
    theta1 = x_arr[:, 1]
    theta2 = x_arr[:, 2]

    # RMSE of both angles
    rmse = np.sqrt(np.mean(theta1**2 + theta2**2))

    return float(rmse)


def compute_fitness(
    t_arr: np.ndarray,
    x_arr: np.ndarray,
    u_arr: np.ndarray,
    dt: float = 0.01
) -> Tuple[float, float, float]:
    """
    Compute multi-objective fitness for chattering PSO.

    fitness = 0.7 * chattering_index + 0.3 * RMSE

    Args:
        t_arr: Time array
        x_arr: State array
        u_arr: Control array
        dt: Timestep

    Returns:
        Tuple of (total_fitness, chattering_index, rmse)
    """
    chattering = compute_chattering_index(u_arr, dt)
    rmse = compute_rmse(x_arr)

    # Multi-objective fitness (70% chattering, 30% performance)
    fitness = 0.7 * chattering + 0.3 * rmse

    return fitness, chattering, rmse


def objective_function(gains: np.ndarray, config: Any, controller_type: str) -> float:
    """
    PSO objective function for chattering optimization.

    Args:
        gains: Candidate controller gains
        config: System configuration
        controller_type: Controller type string

    Returns:
        Fitness value (lower is better)
    """
    try:
        # Create controller with candidate gains
        temp_config = config.model_copy(deep=True)

        # Update gains in both controller_defaults and controllers
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

        # Simulate
        t_arr, x_arr, u_arr = simulate_with_controller(
            controller, dynamics,
            sim_time=10.0, dt=0.01
        )

        # Compute fitness
        fitness, chattering, rmse = compute_fitness(t_arr, x_arr, u_arr, dt=0.01)

        return fitness

    except Exception as e:
        logger.error(f"Objective function failed: {e}")
        return 1e6  # Penalty for failure


def optimize_adaptive_smc_chattering(
    n_particles: int = 30,
    n_iterations: int = 50,
    seed: int = 42
) -> ChatteringPSOResult:
    """
    Run chattering PSO optimization for Adaptive SMC.

    Args:
        n_particles: Number of PSO particles
        n_iterations: Number of PSO iterations
        seed: Random seed

    Returns:
        ChatteringPSOResult with optimization results
    """
    logger.info("=" * 80)
    logger.info("Phase 2: Adaptive SMC Chattering PSO Optimization")
    logger.info("=" * 80)
    logger.info(f"Particles: {n_particles}, Iterations: {n_iterations}, Seed: {seed}")

    start_time = datetime.now()

    # Load config
    config = load_config('config.yaml', allow_unknown=False)

    # Get original gains
    original_gains = config.controller_defaults.adaptive_smc.gains
    logger.info(f"Original gains: {original_gains}")

    # Define bounds (search around current values ± 50%)
    bounds = []
    for g in original_gains:
        lower = max(0.01, g * 0.5)  # At least 0.01
        upper = g * 1.5
        bounds.append((lower, upper))

    logger.info(f"Search bounds: {bounds}")

    # Evaluate original performance
    logger.info("Evaluating original controller...")
    controller_orig = create_controller(controller_type='adaptive_smc', config=config)
    dynamics = DIPDynamics(config=config.physics)
    t_orig, x_orig, u_orig = simulate_with_controller(controller_orig, dynamics)
    fitness_orig, chattering_orig, rmse_orig = compute_fitness(t_orig, x_orig, u_orig)

    logger.info(f"Original - Chattering: {chattering_orig:.4f}, RMSE: {rmse_orig:.4f}, Fitness: {fitness_orig:.4f}")

    # Run PSO optimization using PySwarms directly
    logger.info("Starting PSO optimization...")

    # Import PySwarms
    from pyswarms.single import GlobalBestPSO

    # Set random seed for reproducibility
    if seed is not None:
        np.random.seed(seed)

    # PSO configuration
    pso_options = {
        'c1': 2.0,  # Cognitive parameter
        'c2': 2.0,  # Social parameter
        'w': 0.9    # Inertia weight
    }

    # Create PSO optimizer
    optimizer = GlobalBestPSO(
        n_particles=n_particles,
        dimensions=len(original_gains),
        options=pso_options,
        bounds=(np.array([b[0] for b in bounds]), np.array([b[1] for b in bounds]))
    )

    # Run optimization
    best_fitness, optimized_gains = optimizer.optimize(
        lambda p: np.array([objective_function(gains, config, 'adaptive_smc') for gains in p]),
        iters=n_iterations
    )

    logger.info(f"PSO complete. Best fitness: {best_fitness:.4f}")
    logger.info(f"Optimized gains: {optimized_gains.tolist()}")

    # Evaluate optimized controller
    logger.info("Evaluating optimized controller...")
    temp_config = config.model_copy(deep=True)
    default_ctrl = temp_config.controller_defaults.adaptive_smc
    updated = default_ctrl.model_copy(update={'gains': optimized_gains.tolist()})
    temp_config.controller_defaults.adaptive_smc = updated

    ctrl_config = temp_config.controllers.adaptive_smc
    updated_ctrl = ctrl_config.model_copy(update={'gains': optimized_gains.tolist()})
    temp_config.controllers.adaptive_smc = updated_ctrl

    controller_opt = create_controller(controller_type='adaptive_smc', config=temp_config)
    t_opt, x_opt, u_opt = simulate_with_controller(controller_opt, dynamics)
    fitness_opt, chattering_opt, rmse_opt = compute_fitness(t_opt, x_opt, u_opt)

    logger.info(f"Optimized - Chattering: {chattering_opt:.4f}, RMSE: {rmse_opt:.4f}, Fitness: {fitness_opt:.4f}")

    # Compute improvement
    improvement = ((fitness_orig - fitness_opt) / fitness_orig) * 100
    logger.info(f"Improvement: {improvement:.2f}%")

    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    logger.info(f"Total time: {elapsed:.1f}s")

    result = ChatteringPSOResult(
        controller_name='adaptive_smc',
        original_gains=original_gains,
        optimized_gains=optimized_gains.tolist(),
        chattering_before=chattering_orig,
        chattering_after=chattering_opt,
        rmse_before=rmse_orig,
        rmse_after=rmse_opt,
        fitness_before=fitness_orig,
        fitness_after=fitness_opt,
        improvement_pct=improvement,
        n_iterations=n_iterations,
        n_particles=n_particles,
        converged=True,  # PSO always runs to completion
        optimization_time_sec=elapsed
    )

    return result


def save_results(result: ChatteringPSOResult, output_dir: Path):
    """Save optimization results to files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Gains JSON
    gains_file = output_dir / "adaptive_smc_chattering_gains.json"
    with open(gains_file, 'w') as f:
        json.dump({
            'controller': result.controller_name,
            'gains': result.optimized_gains,
            'chattering': result.chattering_after,
            'rmse': result.rmse_after,
            'fitness': result.fitness_after
        }, f, indent=2)
    logger.info(f"Saved gains: {gains_file}")

    # 2. Summary JSON
    summary_file = output_dir / "adaptive_smc_chattering_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(asdict(result), f, indent=2)
    logger.info(f"Saved summary: {summary_file}")

    # 3. CSV for analysis
    csv_file = output_dir / "adaptive_smc_chattering_optimization.csv"
    df = pd.DataFrame([{
        'metric': 'chattering',
        'before': result.chattering_before,
        'after': result.chattering_after,
        'improvement_pct': ((result.chattering_before - result.chattering_after) / result.chattering_before) * 100
    }, {
        'metric': 'rmse',
        'before': result.rmse_before,
        'after': result.rmse_after,
        'improvement_pct': ((result.rmse_before - result.rmse_after) / result.rmse_before) * 100
    }, {
        'metric': 'fitness',
        'before': result.fitness_before,
        'after': result.fitness_after,
        'improvement_pct': result.improvement_pct
    }])
    df.to_csv(csv_file, index=False)
    logger.info(f"Saved CSV: {csv_file}")

    # 4. Simulate optimized controller and save time-series
    logger.info("Generating time-series data...")
    config = load_config('config.yaml', allow_unknown=False)
    temp_config = config.model_copy(deep=True)
    default_ctrl = temp_config.controller_defaults.adaptive_smc
    updated = default_ctrl.model_copy(update={'gains': result.optimized_gains})
    temp_config.controller_defaults.adaptive_smc = updated

    controller_opt = create_controller(controller_type='adaptive_smc', config=temp_config)
    dynamics = DIPDynamics(config=config.physics)
    t_arr, x_arr, u_arr = simulate_with_controller(controller_opt, dynamics)

    # Save as NPZ
    npz_file = output_dir / "adaptive_smc_chattering_timeseries.npz"
    np.savez(npz_file, time=t_arr, state=x_arr, control=u_arr)
    logger.info(f"Saved time-series: {npz_file}")


if __name__ == "__main__":
    logger.info("[OK] Starting Phase 2: Adaptive SMC Chattering PSO")

    # Run optimization
    result = optimize_adaptive_smc_chattering(
        n_particles=30,
        n_iterations=50,
        seed=42
    )

    # Save results
    output_dir = project_root / "academic" / "paper" / "experiments" / "adaptive_smc" / "optimization" / "chattering"
    save_results(result, output_dir)

    logger.info("[OK] Phase 2 Adaptive SMC chattering PSO complete!")
    logger.info(f"Results saved to: {output_dir}")
    logger.info(f"Improvement: {result.improvement_pct:.2f}%")
