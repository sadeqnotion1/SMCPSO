"""
Phase 4.2: PSO Threshold Optimization for |s|-Based Scheduler

Optimizes 4 parameters to reduce chattering from +36.9% to <20% vs baseline:
- s_small: Lower threshold for conservative -> aggressive transition
- s_large: Upper threshold for aggressive -> conservative transition
- scale_aggressive: Multiplier for robust gains in aggressive mode
- scale_conservative: Multiplier for robust gains in conservative mode

Fitness Function (ULTRATHINK Spec):
- 60% chattering reduction (primary objective)
- 20% variance minimization (secondary)
- 10% effort minimization (tertiary)
- 10% penalty for >20% degradation

PSO Configuration:
- 20 particles, 50 iterations
- 25 trials per particle evaluation
- Expected runtime: ~6 hours

References:
- ULTRATHINK Plan: .project/ai/planning/ULTRATHINK_PHASE4_STRATEGIC_PLAN.md
- Phase 4.1 Validation: benchmarks/research/phase4_1/PHASE4_1_SUMMARY.md
- SlidingSurfaceScheduler: src/controllers/sliding_surface_scheduler.py

Author: Phase 4.2 Research Team
Created: November 9, 2025
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import load_config
from src.controllers.factory import create_controller
from src.controllers.sliding_surface_scheduler import (
    SlidingSurfaceScheduler,
    SlidingSurfaceScheduleConfig
)
from src.plant.core.dynamics import DIPDynamics

try:
    import pyswarms as ps
except ImportError:
    print("[ERROR] PySwarms not installed. Install with: pip install pyswarms")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ASCII_INFO = "[INFO]"
ASCII_OK = "[OK]"
ASCII_WARN = "[WARNING]"
ASCII_ERROR = "[ERROR]"

# =============================================================================
# Configuration
# =============================================================================

# MT-8 robust PSO gains (baseline)
ROBUST_GAINS = [10.149, 12.839, 6.815, 2.750]  # [c1, lambda1, c2, lambda2]

# PSO parameters (ULTRATHINK spec)
N_PARTICLES = 20
N_ITERATIONS = 50
N_TRIALS_PER_EVAL = 25
PSO_OPTIONS = {'c1': 0.5, 'c2': 0.3, 'w': 0.9}  # Robust PSO settings from MT-7

# Optimization bounds (ULTRATHINK spec)
# [s_small, s_large, scale_aggressive, scale_conservative]
BOUNDS_LOW = [0.01, 0.5, 0.8, 0.3]
BOUNDS_HIGH = [0.5, 2.0, 1.2, 0.7]

# Constraints
HYSTERESIS_WIDTH = 0.05  # Fixed (prevents rapid switching)

# Simulation parameters
SIM_DURATION = 5.0  # seconds
DT = 0.01  # time step
IC_RANGE = 0.05  # ±0.05 rad (Phase 4.1 validation range)

# Random seed
RANDOM_SEED = 42

# Output directory
OUTPUT_DIR = Path("benchmarks/research/phase4_2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Baseline Performance (for comparison)
# =============================================================================

def compute_baseline_metrics(n_trials: int = 100) -> Dict:
    """
    Compute baseline performance metrics (no scheduling, fixed robust gains).

    This establishes the reference for chattering ratio calculations.

    Returns:
        Dictionary with baseline statistics
    """
    logger.info(f"{ASCII_INFO} Computing baseline metrics ({n_trials} trials)...")

    config = load_config("config.yaml")
    dynamics = DIPDynamics(config.physics)

    chattering_values = []
    variance_values = []
    effort_values = []

    for trial in range(n_trials):
        np.random.seed(RANDOM_SEED + trial)

        # Random IC
        theta1_init = np.random.uniform(-IC_RANGE, IC_RANGE)
        theta2_init = np.random.uniform(-IC_RANGE, IC_RANGE)
        ic_variation = np.random.uniform(-0.01, 0.01, size=6)
        initial_state = np.array([0.0, theta1_init, theta2_init, 0.0, 0.0, 0.0]) + ic_variation

        # Create controller (no scheduling)
        controller = create_controller(
            'hybrid_adaptive_sta_smc',
            config=config,
            gains=ROBUST_GAINS,
            k1_init=0.2,
            k2_init=0.02
        )

        # Run simulation
        state = initial_state.copy()
        u_history = []
        s_history = []
        last_control = 0.0

        for step in range(int(SIM_DURATION / DT)):
            u_raw = controller.compute_control(state, last_control)
            # Extract scalar value from output
            if hasattr(u_raw, 'u'):
                u = float(u_raw.u)
            elif isinstance(u_raw, (list, tuple, np.ndarray)):
                u = float(u_raw[0]) if len(u_raw) > 0 else float(u_raw)
            else:
                u = float(u_raw)
            u_history.append(u)

            # Compute |s|
            c1, c2 = ROBUST_GAINS[0], ROBUST_GAINS[2]
            s = c1 * state[1] + c2 * state[4]
            s_history.append(abs(s))

            state = dynamics.step(state, u, DT)
            last_control = u

        # Metrics
        u_array = np.array(u_history)
        jerk = np.abs(np.diff(u_array, n=3)) / (DT ** 3)
        chattering = np.mean(jerk)

        s_array = np.array(s_history)
        window_size = int(1.0 / DT)  # 1 second window
        variances = []
        for i in range(len(s_array) - window_size + 1):
            window = s_array[i:i+window_size]
            variances.append(np.var(window))
        variance = np.mean(variances)

        effort = np.mean(np.abs(u_array))

        chattering_values.append(chattering)
        variance_values.append(variance)
        effort_values.append(effort)

        if hasattr(controller, 'cleanup'):
            controller.cleanup()

    baseline = {
        "chattering": {
            "mean": float(np.mean(chattering_values)),
            "std": float(np.std(chattering_values))
        },
        "variance": {
            "mean": float(np.mean(variance_values)),
            "std": float(np.std(variance_values))
        },
        "effort": {
            "mean": float(np.mean(effort_values)),
            "std": float(np.std(effort_values))
        }
    }

    logger.info(f"{ASCII_OK} Baseline computed:")
    logger.info(f"  Chattering: {baseline['chattering']['mean']:.2f} +- {baseline['chattering']['std']:.2f}")
    logger.info(f"  Variance: {baseline['variance']['mean']:.6f} +- {baseline['variance']['std']:.6f}")
    logger.info(f"  Effort: {baseline['effort']['mean']:.2f} +- {baseline['effort']['std']:.2f}")

    return baseline


# =============================================================================
# Single Trial Simulation
# =============================================================================

def run_single_trial_with_scheduling(
    s_small: float,
    s_large: float,
    scale_aggressive: float,
    scale_conservative: float,
    seed: int
) -> Dict:
    """
    Run single trial with |s|-based gain scheduling.

    Args:
        s_small: Lower threshold (conservative -> aggressive)
        s_large: Upper threshold (aggressive -> conservative)
        scale_aggressive: Gain multiplier for aggressive mode
        scale_conservative: Gain multiplier for conservative mode
        seed: Random seed for IC generation

    Returns:
        Dictionary with performance metrics
    """
    np.random.seed(seed)

    config = load_config("config.yaml")
    dynamics = DIPDynamics(config.physics)

    # Random IC
    theta1_init = np.random.uniform(-IC_RANGE, IC_RANGE)
    theta2_init = np.random.uniform(-IC_RANGE, IC_RANGE)
    ic_variation = np.random.uniform(-0.01, 0.01, size=6)
    initial_state = np.array([0.0, theta1_init, theta2_init, 0.0, 0.0, 0.0]) + ic_variation

    # Create base controller
    base_controller = create_controller(
        'hybrid_adaptive_sta_smc',
        config=config,
        gains=ROBUST_GAINS,
        k1_init=0.2,
        k2_init=0.02
    )

    # Wrap with scheduler
    scheduler_config = SlidingSurfaceScheduleConfig(
        small_s_threshold=s_small,
        large_s_threshold=s_large,
        aggressive_scale=scale_aggressive,
        conservative_scale=scale_conservative,
        hysteresis_width=HYSTERESIS_WIDTH,
        c1=ROBUST_GAINS[0],
        c2=ROBUST_GAINS[2]
    )

    controller = SlidingSurfaceScheduler(
        base_controller=base_controller,
        config=scheduler_config,
        robust_gains=ROBUST_GAINS
    )

    # Run simulation
    state = initial_state.copy()
    u_history = []
    s_history = []
    last_control = 0.0

    for step in range(int(SIM_DURATION / DT)):
        # Check for divergence
        if np.any(np.abs(state) > 100):
            return {
                "chattering": 1e8,  # Penalty for divergence
                "variance": 1e8,
                "effort": 1e8,
                "diverged": True
            }

        u_raw = controller.compute_control(state, last_control)
        # Extract scalar value from output
        if hasattr(u_raw, 'u'):
            u = float(u_raw.u)
        elif isinstance(u_raw, (list, tuple, np.ndarray)):
            u = float(u_raw[0]) if len(u_raw) > 0 else float(u_raw)
        else:
            u = float(u_raw)
        u_history.append(u)

        # Compute |s|
        c1, c2 = ROBUST_GAINS[0], ROBUST_GAINS[2]
        s = c1 * state[1] + c2 * state[4]
        s_history.append(abs(s))

        state = dynamics.step(state, u, DT)
        last_control = u

    # Compute metrics
    u_array = np.array(u_history)
    jerk = np.abs(np.diff(u_array, n=3)) / (DT ** 3)
    chattering = np.mean(jerk)

    s_array = np.array(s_history)
    window_size = int(1.0 / DT)
    variances = []
    for i in range(len(s_array) - window_size + 1):
        window = s_array[i:i+window_size]
        variances.append(np.var(window))
    variance = np.mean(variances)

    effort = np.mean(np.abs(u_array))

    if hasattr(controller, 'cleanup'):
        controller.cleanup()

    return {
        "chattering": float(chattering),
        "variance": float(variance),
        "effort": float(effort),
        "diverged": False
    }


# =============================================================================
# PSO Fitness Function
# =============================================================================

def fitness_function(params: np.ndarray, baseline: Dict) -> np.ndarray:
    """
    PSO fitness function (ULTRATHINK spec).

    Weighted multi-objective:
    - 60% chattering ratio (primary)
    - 20% variance ratio (secondary)
    - 10% effort ratio (tertiary)
    - 10% penalty if chattering ratio > 1.2 (>20% degradation)

    Args:
        params: [s_small, s_large, scale_aggressive, scale_conservative] for each particle
        baseline: Baseline metrics for ratio computation

    Returns:
        Fitness values (lower is better)
    """
    n_particles = params.shape[0]
    fitness_values = np.zeros(n_particles)

    for i in range(n_particles):
        s_small, s_large, scale_agg, scale_cons = params[i]

        # Constraint 1: s_small < s_large
        if s_small >= s_large:
            fitness_values[i] = 1e6
            continue

        # Constraint 2: scale_cons < scale_agg
        if scale_cons >= scale_agg:
            fitness_values[i] = 1e6
            continue

        # Run N_TRIALS_PER_EVAL trials
        chattering_vals = []
        variance_vals = []
        effort_vals = []

        for trial in range(N_TRIALS_PER_EVAL):
            trial_seed = RANDOM_SEED + i * 1000 + trial
            result = run_single_trial_with_scheduling(
                s_small, s_large, scale_agg, scale_cons, trial_seed
            )

            chattering_vals.append(result["chattering"])
            variance_vals.append(result["variance"])
            effort_vals.append(result["effort"])

        # Compute ratios vs baseline
        chattering_ratio = np.mean(chattering_vals) / baseline["chattering"]["mean"]
        variance_ratio = np.mean(variance_vals) / baseline["variance"]["mean"]
        effort_ratio = np.mean(effort_vals) / baseline["effort"]["mean"]

        # Weighted fitness
        fitness = (
            0.6 * chattering_ratio +
            0.2 * variance_ratio +
            0.1 * effort_ratio
        )

        # Penalty for >20% chattering degradation
        if chattering_ratio > 1.2:
            penalty = 0.1 * (chattering_ratio - 1.2) * 10
            fitness += penalty

        fitness_values[i] = fitness

        # Log progress
        if i % 5 == 0:
            logger.info(
                f"  Particle {i}/{n_particles}: "
                f"chattering_ratio={chattering_ratio:.3f}, "
                f"fitness={fitness:.3f}"
            )

    return fitness_values


# =============================================================================
# Main PSO Optimization
# =============================================================================

def main():
    logger.info("=" * 80)
    logger.info("Phase 4.2: PSO Threshold Optimization")
    logger.info("=" * 80)
    logger.info(f"{ASCII_INFO} Configuration:")
    logger.info(f"  Particles: {N_PARTICLES}")
    logger.info(f"  Iterations: {N_ITERATIONS}")
    logger.info(f"  Trials per particle: {N_TRIALS_PER_EVAL}")
    logger.info(f"  Total simulations: {N_PARTICLES * N_ITERATIONS * N_TRIALS_PER_EVAL}")
    logger.info(f"  Expected runtime: ~6 hours")
    logger.info(f"  Bounds:")
    logger.info(f"    s_small: [{BOUNDS_LOW[0]}, {BOUNDS_HIGH[0]}]")
    logger.info(f"    s_large: [{BOUNDS_LOW[1]}, {BOUNDS_HIGH[1]}]")
    logger.info(f"    scale_aggressive: [{BOUNDS_LOW[2]}, {BOUNDS_HIGH[2]}]")
    logger.info(f"    scale_conservative: [{BOUNDS_LOW[3]}, {BOUNDS_HIGH[3]}]")

    # Step 1: Compute baseline
    baseline = compute_baseline_metrics(n_trials=100)

    # Save baseline
    with open(OUTPUT_DIR / "phase4_2_baseline.json", 'w') as f:
        json.dump(baseline, f, indent=2)
    logger.info(f"{ASCII_OK} Saved baseline: {OUTPUT_DIR}/phase4_2_baseline.json")

    # Step 2: Run PSO optimization
    logger.info(f"\n{ASCII_INFO} Starting PSO optimization...")

    bounds = (np.array(BOUNDS_LOW), np.array(BOUNDS_HIGH))

    optimizer = ps.single.GlobalBestPSO(
        n_particles=N_PARTICLES,
        dimensions=4,  # s_small, s_large, scale_aggressive, scale_conservative
        options=PSO_OPTIONS,
        bounds=bounds
    )

    # Wrapper to pass baseline to fitness function
    def fitness_with_baseline(params):
        return fitness_function(params, baseline)

    best_cost, best_params = optimizer.optimize(
        fitness_with_baseline,
        iters=N_ITERATIONS,
        verbose=True
    )

    s_small_opt, s_large_opt, scale_agg_opt, scale_cons_opt = best_params

    logger.info(f"\n{ASCII_OK} Optimization complete!")
    logger.info(f"  Best fitness: {best_cost:.4f}")
    logger.info(f"  Optimal s_small: {s_small_opt:.4f}")
    logger.info(f"  Optimal s_large: {s_large_opt:.4f}")
    logger.info(f"  Optimal scale_aggressive: {scale_agg_opt:.4f}")
    logger.info(f"  Optimal scale_conservative: {scale_cons_opt:.4f}")

    # Step 3: Save results
    pso_results = {
        "best_cost": float(best_cost),
        "optimal_parameters": {
            "s_small": float(s_small_opt),
            "s_large": float(s_large_opt),
            "scale_aggressive": float(scale_agg_opt),
            "scale_conservative": float(scale_cons_opt),
            "hysteresis_width": HYSTERESIS_WIDTH
        },
        "cost_history": optimizer.cost_history.tolist(),
        "pso_config": {
            "n_particles": N_PARTICLES,
            "n_iterations": N_ITERATIONS,
            "n_trials_per_eval": N_TRIALS_PER_EVAL,
            "bounds": {"low": BOUNDS_LOW, "high": BOUNDS_HIGH},
            "options": PSO_OPTIONS
        },
        "baseline_metrics": baseline
    }

    output_file = OUTPUT_DIR / "phase4_2_pso_results.json"
    with open(output_file, 'w') as f:
        json.dump(pso_results, f, indent=2)
    logger.info(f"{ASCII_OK} Saved PSO results: {output_file}")

    logger.info(f"\n{ASCII_INFO} Next steps:")
    logger.info("  1. Run validation trials with optimized parameters (100 trials, 4 IC ranges)")
    logger.info("  2. Analyze chattering reduction vs Phase 4.1 (target: <20% increase)")
    logger.info("  3. Update LT-7 Section 8.5 with results")
    logger.info("  4. Submit LT-7 v2.2 with optimized scheduler")


if __name__ == "__main__":
    main()
