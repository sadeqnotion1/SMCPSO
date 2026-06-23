"""
MT-6 Chattering Investigation: Control Signal Extraction (Simplified)
================================================================================

Extracts control signals u(t) from fixed and adaptive boundary layer simulations
using the standard run_simulation() function. Computes epsilon_eff post-hoc.

Author: MT-6 Investigation Team
Created: October 18, 2025
"""

import numpy as np
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.controllers.smc.classic_smc import ClassicalSMC
from src.core.dynamics import DIPDynamics
from src.core.simulation_runner import run_simulation
from src.config import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Main extraction routine: run fixed and adaptive simulations, save time series.
    """
    logger.info("=" * 80)
    logger.info("MT-6 Control Signal Extraction (Simplified)")
    logger.info("=" * 80)

    # Load configuration
    config = load_config("config.yaml")
    logger.info("Configuration loaded")

    # Create dynamics model
    dynamics = DIPDynamics(config.physics)
    logger.info("Dynamics model initialized")

    # Simulation parameters
    sim_time = 10.0  # seconds
    dt = 0.01  # 100 Hz sampling
    num_runs = 3  # Reduced for speed
    gains = [5.0, 5.0, 5.0, 0.5, 0.5, 0.5]

    # Initial state (6D: [x, theta1, theta2, x_dot, theta1_dot, theta2_dot])
    initial_state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])  # Small angle perturbation

    # -------------------------------------------------------------------------
    # FIXED BOUNDARY LAYER
    # -------------------------------------------------------------------------
    logger.info("\n" + "-" * 80)
    logger.info("FIXED BOUNDARY LAYER (epsilon=0.02, alpha=0.0)")
    logger.info("-" * 80)

    fixed_results = []
    for run_id in range(num_runs):
        seed = 42 + run_id
        logger.info(f"  Run {run_id+1}/{num_runs} (seed={seed})")

        # Create controller
        controller = ClassicalSMC(
            gains=gains,
            max_force=150.0,
            boundary_layer=0.02,
            boundary_layer_slope=0.0,
            switch_method='tanh'
        )

        # Run simulation
        try:
            t_arr, x_arr, u_arr = run_simulation(
                controller=controller,
                dynamics_model=dynamics,
                sim_time=sim_time,
                dt=dt,
                initial_state=initial_state,
                u_max=150.0,
                seed=seed
            )

            logger.info(f"    Simulation returned: t={len(t_arr)}, x={x_arr.shape}, u={len(u_arr)}")

            if len(u_arr) == 0:
                logger.error(f"    ERROR: Simulation produced zero control steps!")
                continue

            fixed_results.append((t_arr, x_arr, u_arr))
            logger.info(f"    Completed: {len(t_arr)} timesteps, control range [{u_arr.min():.1f}, {u_arr.max():.1f}] N")

        except Exception as e:
            logger.error(f"    Simulation failed: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Average fixed results
    t_fixed = fixed_results[0][0]
    x_fixed = np.mean([r[1] for r in fixed_results], axis=0)
    u_fixed = np.mean([r[2] for r in fixed_results], axis=0)

    # Compute sliding surface and epsilon_eff for fixed
    c1 = 5.0  # From gains
    # State is [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
    s_fixed = c1 * x_fixed[:-1, 1] + x_fixed[:-1, 4]  # s = c1*theta1 + theta1_dot
    epsilon_fixed = np.full_like(s_fixed, 0.02)  # Constant

    # Save fixed results
    fixed_file = Path("benchmarks/MT6_fixed_timeseries.npz")
    np.savez(
        fixed_file,
        t=t_fixed,
        u=u_fixed,
        state=x_fixed,
        s=s_fixed,
        epsilon_eff=epsilon_fixed
    )
    logger.info(f"\n✓ Saved: {fixed_file} ({fixed_file.stat().st_size / 1024:.1f} KB)")

    # -------------------------------------------------------------------------
    # ADAPTIVE BOUNDARY LAYER
    # -------------------------------------------------------------------------
    logger.info("\n" + "-" * 80)
    logger.info("ADAPTIVE BOUNDARY LAYER (epsilon_min=0.0206, alpha=0.2829)")
    logger.info("-" * 80)

    adaptive_results = []
    for run_id in range(num_runs):
        seed = 42 + run_id
        logger.info(f"  Run {run_id+1}/{num_runs} (seed={seed})")

        # Create controller
        controller = ClassicalSMC(
            gains=gains,
            max_force=150.0,
            boundary_layer=0.0206,
            boundary_layer_slope=0.2829,
            switch_method='tanh'
        )

        # Run simulation
        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=dynamics,
            sim_time=sim_time,
            dt=dt,
            initial_state=initial_state,
            u_max=150.0,
            seed=seed
        )

        adaptive_results.append((t_arr, x_arr, u_arr))
        logger.info(f"    Completed: {len(t_arr)} timesteps, control range [{u_arr.min():.1f}, {u_arr.max():.1f}] N")

    # Average adaptive results
    t_adaptive = adaptive_results[0][0]
    x_adaptive = np.mean([r[1] for r in adaptive_results], axis=0)
    u_adaptive = np.mean([r[2] for r in adaptive_results], axis=0)

    # Compute sliding surface and epsilon_eff for adaptive
    # State is [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
    s_adaptive = c1 * x_adaptive[:-1, 1] + x_adaptive[:-1, 4]  # s = c1*theta1 + theta1_dot
    s_dot = np.gradient(s_adaptive, dt)  # Approximate derivative
    epsilon_adaptive = 0.0206 + 0.2829 * np.abs(s_dot)  # ε_eff = ε_min + α|ṡ|

    # Save adaptive results
    adaptive_file = Path("benchmarks/MT6_adaptive_timeseries.npz")
    np.savez(
        adaptive_file,
        t=t_adaptive,
        u=u_adaptive,
        state=x_adaptive,
        s=s_adaptive,
        epsilon_eff=epsilon_adaptive
    )
    logger.info(f"\n✓ Saved: {adaptive_file} ({adaptive_file.stat().st_size / 1024:.1f} KB)")
    logger.info(f"  epsilon_eff range: [{epsilon_adaptive.min():.4f}, {epsilon_adaptive.max():.4f}]")

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------
    logger.info("\n" + "=" * 80)
    logger.info("EXTRACTION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Files generated:")
    logger.info(f"  1. {fixed_file}")
    logger.info(f"  2. {adaptive_file}")
    logger.info(f"\nNext: Run scripts/mt6_visualize_chattering.py to generate plots")


if __name__ == "__main__":
    main()
