"""
================================================================================
Phase 4.1: Optimize |s|-Based Thresholds with PSO
================================================================================

Instead of using angle-based thresholds (|theta| > threshold), use sliding
surface magnitude thresholds (|s| > threshold) for adaptive gain scheduling.

Hypothesis: |s|-based thresholds break the feedback loop because:
1. |s| is directly controlled by the controller
2. Large |s| indicates system is far from sliding surface
3. Reducing gains when |s| is large helps reach the surface
4. No circular dependency between scheduling decision and control outcome

This script uses PSO to find optimal |s| thresholds for:
- s_aggressive_threshold: Switch to aggressive gains when |s| > this
- s_conservative_threshold: Switch to conservative gains when |s| < this

Author: Research Team
Date: November 2025
Related: MT-6 (Boundary Layer Optimization), Phase 2.3 (Feedback Instability)
================================================================================
"""

import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.controllers.smc.hybrid_adaptive_sta_smc import HybridAdaptiveSTASMC
from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics
from src.plant.models.simplified.config import SimplifiedDIPConfig
from src.config import load_config

try:
    import pyswarms as ps
    from pyswarms.utils.functions import single_obj as fx
except ImportError:
    print("[ERROR] PySwarms not installed. Install with: pip install pyswarms")
    sys.exit(1)


# ============================================================================
# Configuration
# ============================================================================

# Robust gains from MT-8 Enhancement #3
ROBUST_GAINS = [10.149, 12.839, 6.815, 2.75]  # [c1, lambda1, c2, lambda2]

# Simulation parameters
SIM_DURATION = 10.0  # seconds
DT = 0.01  # time step

# Initial conditions (small perturbation)
IC_RANGE = 0.05

# PSO Parameters (reduced for faster execution)
N_PARTICLES = 10
N_ITERATIONS = 15
PSO_OPTIONS = {'c1': 1.5, 'c2': 1.5, 'w': 0.7}  # Cognitive, social, inertia

# Search bounds for thresholds
# [s_aggressive, s_conservative]
BOUNDS_LOW = [5.0, 0.1]
BOUNDS_HIGH = [100.0, 5.0]

# Number of trials per PSO evaluation
N_TRIALS_PER_EVAL = 5

# Random seed for reproducibility
RANDOM_SEED = 42

# Output directory
OUTPUT_DIR = Path("benchmarks/research/phase4_1")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Modified Adaptive Scheduler (|s|-Based)
# ============================================================================

class SlidingSurfaceAdaptiveScheduler:
    """
    Adaptive gain scheduler based on sliding surface magnitude |s|.

    This breaks the feedback loop by using |s| instead of |theta| for
    scheduling decisions.
    """

    def __init__(self, s_aggressive: float, s_conservative: float,
                 aggressive_scale: float = 1.5, conservative_scale: float = 0.5):
        """
        Initialize scheduler.

        Args:
            s_aggressive: |s| threshold for aggressive mode (|s| > this → aggressive)
            s_conservative: |s| threshold for conservative mode (|s| < this → conservative)
            aggressive_scale: Gain multiplier in aggressive mode
            conservative_scale: Gain multiplier in conservative mode
        """
        self.s_aggressive = s_aggressive
        self.s_conservative = s_conservative
        self.aggressive_scale = aggressive_scale
        self.conservative_scale = conservative_scale

        self.current_mode = "nominal"
        self.mode_history = []

    def update(self, s: np.ndarray, gains: np.ndarray) -> np.ndarray:
        """
        Update gains based on |s| magnitude.

        Args:
            s: Sliding surface vector [s1, s2]
            gains: Base gains [c1, lambda1, c2, lambda2]

        Returns:
            Scheduled gains
        """
        # Compute |s| magnitude
        s_magnitude = np.linalg.norm(s)

        # Determine mode
        if s_magnitude > self.s_aggressive:
            mode = "aggressive"
            scale = self.aggressive_scale
        elif s_magnitude < self.s_conservative:
            mode = "conservative"
            scale = self.conservative_scale
        else:
            mode = "nominal"
            scale = 1.0

        self.current_mode = mode
        self.mode_history.append(mode)

        # Scale gains
        return np.array(gains) * scale


# ============================================================================
# Modified Hybrid Controller (|s|-Based Scheduling)
# ============================================================================

class HybridWithSScheduling(HybridAdaptiveSTASMC):
    """
    Hybrid controller with |s|-based adaptive gain scheduling.
    """

    def __init__(self, scheduler: SlidingSurfaceAdaptiveScheduler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scheduler = scheduler
        self.s_history = []

    def compute_control(self, state: np.ndarray, last_control: float = 0.0,
                       history: List[np.ndarray] = None) -> float:
        """
        Compute control with |s|-based adaptive scheduling.
        """
        # State format: [x, theta1, theta2, xdot, theta1dot, theta2dot]
        x, theta1, theta2, xdot, theta1dot, theta2dot = state

        # Sliding surface for each pendulum
        s1 = self.c1 * theta1 + theta1dot
        s2 = self.c2 * theta2 + theta2dot
        s = np.array([s1, s2])

        self.s_history.append(np.linalg.norm(s))

        # Get scheduled gains
        base_gains = [self.c1, self.lambda1, self.c2, self.lambda2]
        scheduled_gains = self.scheduler.update(s, base_gains)

        # Temporarily override gains
        original_gains = (self.c1, self.lambda1, self.c2, self.lambda2)
        self.c1, self.lambda1, self.c2, self.lambda2 = scheduled_gains

        # Compute control with scheduled gains
        # Parent expects (state, state_vars, history) and returns HybridSTAOutput
        output = super().compute_control(state, state_vars=None, history=None)

        # Restore original gains
        self.c1, self.lambda1, self.c2, self.lambda2 = original_gains

        # Extract control value from output
        return float(output.u)


# ============================================================================
# Simulation & Evaluation Functions
# ============================================================================

def run_single_trial(s_aggressive: float, s_conservative: float,
                    aggressive_scale: float = 1.5,
                    conservative_scale: float = 0.5,
                    seed: int = None) -> Dict:
    """
    Run a single trial with given |s| thresholds.

    Returns:
        Dictionary with performance metrics
    """
    # Set random seed if provided
    if seed is not None:
        np.random.seed(seed)

    # Load config
    config = load_config()

    # Create dynamics using simplified model (same as other research scripts)
    dip_config = SimplifiedDIPConfig.create_default()
    dynamics = SimplifiedDIPDynamics(dip_config)

    # Create scheduler
    scheduler = SlidingSurfaceAdaptiveScheduler(
        s_aggressive=s_aggressive,
        s_conservative=s_conservative,
        aggressive_scale=aggressive_scale,
        conservative_scale=conservative_scale
    )

    # Create controller with proper HybridAdaptiveSTASMC parameters
    controller = HybridWithSScheduling(
        scheduler=scheduler,
        gains=ROBUST_GAINS,  # [c1, lambda1, c2, lambda2]
        dt=DT,
        max_force=20.0,
        k1_init=15.0,
        k2_init=8.0,
        gamma1=1.0,
        gamma2=1.0,
        dead_zone=0.01,
        dynamics_model=dynamics
    )

    # Random initial condition - state format: [x, theta1, theta2, xdot, theta1dot, theta2dot]
    ic = np.array([
        0.0,  # cart_pos (x)
        np.random.uniform(-IC_RANGE, IC_RANGE),  # theta1
        np.random.uniform(-IC_RANGE, IC_RANGE),  # theta2
        0.0,  # cart_vel (xdot)
        0.0,  # theta1dot (omega1)
        0.0   # theta2dot (omega2)
    ])

    # Simulation
    t = 0.0
    state = ic.copy()
    u_last = 0.0

    control_history = []
    state_history = [state.copy()]

    while t < SIM_DURATION:
        # Compute control
        u = controller.compute_control(state, u_last, None)
        u = np.clip(u, -20.0, 20.0)  # Actuator limits
        control_history.append(u)

        # Dynamics (expects control as array, returns DynamicsResult)
        result = dynamics.compute_dynamics(state, np.array([u]))

        # Check if dynamics computation succeeded
        if not result.success or len(result.state_derivative) == 0:
            # System became unstable - return high penalty for PSO
            print(f"[WARN] Simulation failed at t={t:.3f} (state diverged)")
            return {
                'chattering': 1e6,  # High penalty
                'control_effort': 1e6,
                'tracking_error': 1e6,
                'final_error': 1e6,  # High error for PSO objective
                's_magnitude_mean': 1e6,
                'failed': True,
                'failure_time': t
            }

        state = state + result.state_derivative * DT
        state_history.append(state.copy())

        u_last = u
        t += DT

    # Compute metrics
    control_history = np.array(control_history)
    state_history = np.array(state_history)

    # Chattering (mean absolute control derivative)
    chattering = np.mean(np.abs(np.diff(control_history))) / DT

    # Control effort (RMS)
    control_effort = np.sqrt(np.mean(control_history**2))

    # Stabilization error (final state magnitude)
    final_error = np.linalg.norm(state_history[-1, :4])  # theta1, omega1, theta2, omega2

    # Mode distribution
    mode_counts = {
        "aggressive": controller.scheduler.mode_history.count("aggressive"),
        "nominal": controller.scheduler.mode_history.count("nominal"),
        "conservative": controller.scheduler.mode_history.count("conservative")
    }

    return {
        "chattering": chattering,
        "control_effort": control_effort,
        "final_error": final_error,
        "mode_counts": mode_counts,
        "s_history": controller.s_history
    }


def objective_function(params: np.ndarray) -> np.ndarray:
    """
    PSO objective function: minimize weighted sum of chattering and error.

    Args:
        params: [s_aggressive, s_conservative] for each particle

    Returns:
        Objective values (lower is better)
    """
    n_particles = params.shape[0]
    objectives = np.zeros(n_particles)

    for i in range(n_particles):
        s_aggressive, s_conservative = params[i]

        # Ensure s_aggressive > s_conservative (constraint)
        if s_aggressive <= s_conservative:
            objectives[i] = 1e6  # Penalty
            continue

        # Run multiple trials and average
        chattering_vals = []
        error_vals = []

        for trial in range(N_TRIALS_PER_EVAL):
            trial_seed = RANDOM_SEED + i * N_TRIALS_PER_EVAL + trial
            result = run_single_trial(
                s_aggressive=s_aggressive,
                s_conservative=s_conservative,
                seed=trial_seed
            )
            chattering_vals.append(result["chattering"])
            error_vals.append(result["final_error"])

        # Weighted objective: 70% chattering, 30% error
        mean_chattering = np.mean(chattering_vals)
        mean_error = np.mean(error_vals)

        objectives[i] = 0.7 * mean_chattering + 0.3 * mean_error * 1000  # Scale error

    return objectives


# ============================================================================
# PSO Optimization
# ============================================================================

def run_pso_optimization() -> Dict:
    """
    Run PSO optimization to find optimal |s| thresholds.

    Returns:
        Dictionary with optimization results
    """
    print("[INFO] Starting PSO optimization for |s|-based thresholds...")
    print(f"  Particles: {N_PARTICLES}")
    print(f"  Iterations: {N_ITERATIONS}")
    print(f"  Trials per evaluation: {N_TRIALS_PER_EVAL}")
    print(f"  Search bounds: {list(zip(BOUNDS_LOW, BOUNDS_HIGH))}")

    # Create PSO optimizer
    bounds = (np.array(BOUNDS_LOW), np.array(BOUNDS_HIGH))

    optimizer = ps.single.GlobalBestPSO(
        n_particles=N_PARTICLES,
        dimensions=2,  # s_aggressive, s_conservative
        options=PSO_OPTIONS,
        bounds=bounds
    )

    # Run optimization
    print("\n[INFO] Running PSO...")
    best_cost, best_params = optimizer.optimize(
        objective_function,
        iters=N_ITERATIONS,
        verbose=True
    )

    s_aggressive_opt, s_conservative_opt = best_params

    print(f"\n[OK] Optimization complete!")
    print(f"  Best cost: {best_cost:.4f}")
    print(f"  Optimal s_aggressive: {s_aggressive_opt:.4f}")
    print(f"  Optimal s_conservative: {s_conservative_opt:.4f}")

    return {
        "best_cost": float(best_cost),
        "s_aggressive": float(s_aggressive_opt),
        "s_conservative": float(s_conservative_opt),
        "cost_history": optimizer.cost_history.tolist(),
        "pos_history": optimizer.pos_history.tolist() if hasattr(optimizer, 'pos_history') else []
    }


# ============================================================================
# Validation Testing
# ============================================================================

def run_validation_test(s_aggressive: float, s_conservative: float,
                       n_trials: int = 100) -> Dict:
    """
    Run validation test with optimized thresholds.

    Args:
        s_aggressive: Optimized aggressive threshold
        s_conservative: Optimized conservative threshold
        n_trials: Number of validation trials

    Returns:
        Validation results
    """
    print(f"\n[INFO] Running validation test ({n_trials} trials)...")

    results = {
        "chattering": [],
        "control_effort": [],
        "final_error": [],
        "mode_distributions": []
    }

    for trial in range(n_trials):
        trial_result = run_single_trial(
            s_aggressive=s_aggressive,
            s_conservative=s_conservative,
            seed=RANDOM_SEED + 1000 + trial  # Different seeds than PSO
        )

        results["chattering"].append(trial_result["chattering"])
        results["control_effort"].append(trial_result["control_effort"])
        results["final_error"].append(trial_result["final_error"])
        results["mode_distributions"].append(trial_result["mode_counts"])

    # Compute statistics
    summary = {
        "chattering": {
            "mean": float(np.mean(results["chattering"])),
            "std": float(np.std(results["chattering"])),
            "median": float(np.median(results["chattering"])),
            "min": float(np.min(results["chattering"])),
            "max": float(np.max(results["chattering"]))
        },
        "control_effort": {
            "mean": float(np.mean(results["control_effort"])),
            "std": float(np.std(results["control_effort"]))
        },
        "final_error": {
            "mean": float(np.mean(results["final_error"])),
            "std": float(np.std(results["final_error"]))
        },
        "mode_distribution": {
            "aggressive_pct": float(np.mean([d["aggressive"] / sum(d.values()) * 100
                                            for d in results["mode_distributions"]])),
            "nominal_pct": float(np.mean([d["nominal"] / sum(d.values()) * 100
                                         for d in results["mode_distributions"]])),
            "conservative_pct": float(np.mean([d["conservative"] / sum(d.values()) * 100
                                              for d in results["mode_distributions"]]))
        }
    }

    print(f"  Mean chattering: {summary['chattering']['mean']:.1f} +/- {summary['chattering']['std']:.1f}")
    print(f"  Mean control effort: {summary['control_effort']['mean']:.2f}")
    print(f"  Mean final error: {summary['final_error']['mean']:.4f}")
    print(f"  Mode distribution: {summary['mode_distribution']}")

    return summary


# ============================================================================
# Baseline Comparison
# ============================================================================

def run_baseline_comparison(s_aggressive: float, s_conservative: float,
                           n_trials: int = 100) -> Dict:
    """
    Compare |s|-based scheduling against baseline (no scheduling).

    Returns:
        Comparison results
    """
    print(f"\n[INFO] Running baseline comparison...")

    # Run baseline (no scheduling = nominal mode always)
    print("  Testing baseline (no scheduling)...")
    baseline_results = []

    for trial in range(n_trials):
        # Use very high thresholds so it never switches modes
        trial_result = run_single_trial(
            s_aggressive=1e10,  # Never aggressive
            s_conservative=-1e10,  # Never conservative
            seed=RANDOM_SEED + 2000 + trial
        )
        baseline_results.append(trial_result["chattering"])

    # Run |s|-based scheduling
    print("  Testing |s|-based scheduling...")
    scheduled_results = []

    for trial in range(n_trials):
        trial_result = run_single_trial(
            s_aggressive=s_aggressive,
            s_conservative=s_conservative,
            seed=RANDOM_SEED + 2000 + trial  # Same seeds as baseline
        )
        scheduled_results.append(trial_result["chattering"])

    # Statistical comparison
    baseline_mean = np.mean(baseline_results)
    scheduled_mean = np.mean(scheduled_results)
    percent_change = ((scheduled_mean - baseline_mean) / baseline_mean) * 100

    # Welch's t-test
    from scipy import stats as sp_stats
    t_stat, p_value = sp_stats.ttest_ind(
        baseline_results,
        scheduled_results,
        equal_var=False
    )

    comparison = {
        "baseline": {
            "mean": float(baseline_mean),
            "std": float(np.std(baseline_results)),
            "median": float(np.median(baseline_results))
        },
        "scheduled": {
            "mean": float(scheduled_mean),
            "std": float(np.std(scheduled_results)),
            "median": float(np.median(scheduled_results))
        },
        "comparison": {
            "percent_change": float(percent_change),
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "significant": bool(p_value < 0.05)
        }
    }

    print(f"\n  Baseline: {comparison['baseline']['mean']:.1f} +/- {comparison['baseline']['std']:.1f}")
    print(f"  Scheduled: {comparison['scheduled']['mean']:.1f} +/- {comparison['scheduled']['std']:.1f}")
    print(f"  Change: {comparison['comparison']['percent_change']:+.1f}%")
    print(f"  p-value: {comparison['comparison']['p_value']:.2e}")

    if comparison['comparison']['significant']:
        if percent_change < 0:
            print("  [OK] Significant improvement!")
        else:
            print("  [WARNING] Significant degradation!")
    else:
        print("  [INFO] No significant difference")

    return comparison


# ============================================================================
# Main Execution
# ============================================================================

def main():
    print("=" * 80)
    print("Phase 4.1: Optimize |s|-Based Thresholds with PSO")
    print("=" * 80)

    # Run PSO optimization
    pso_results = run_pso_optimization()

    # Save PSO results
    with open(OUTPUT_DIR / "phase4_1_pso_results.json", 'w') as f:
        json.dump(pso_results, f, indent=2)
    print(f"\n[OK] Saved: {OUTPUT_DIR / 'phase4_1_pso_results.json'}")

    # Run validation test (reduced trials for faster execution)
    validation_results = run_validation_test(
        s_aggressive=pso_results["s_aggressive"],
        s_conservative=pso_results["s_conservative"],
        n_trials=20
    )

    # Run baseline comparison (reduced trials for faster execution)
    comparison_results = run_baseline_comparison(
        s_aggressive=pso_results["s_aggressive"],
        s_conservative=pso_results["s_conservative"],
        n_trials=20
    )

    # Combine all results
    final_results = {
        "pso_optimization": pso_results,
        "validation": validation_results,
        "baseline_comparison": comparison_results,
        "parameters": {
            "robust_gains": ROBUST_GAINS,
            "sim_duration": SIM_DURATION,
            "dt": DT,
            "ic_range": IC_RANGE,
            "n_particles": N_PARTICLES,
            "n_iterations": N_ITERATIONS,
            "n_trials_per_eval": N_TRIALS_PER_EVAL,
            "bounds": {"low": BOUNDS_LOW, "high": BOUNDS_HIGH}
        }
    }

    # Save final results
    with open(OUTPUT_DIR / "phase4_1_complete_results.json", 'w') as f:
        json.dump(final_results, f, indent=2)
    print(f"\n[OK] Saved: {OUTPUT_DIR / 'phase4_1_complete_results.json'}")

    print("\n" + "=" * 80)
    print("[COMPLETE] Phase 4.1: |s|-based threshold optimization finished!")
    print("=" * 80)
    print("\n[INFO] Next steps:")
    print("  1. Analyze if |s|-based scheduling reduces chattering vs baseline")
    print("  2. Compare with Phase 2/3 results (angle-based scheduling)")
    print("  3. Proceed to Phase 4.2 (dynamic conservative scaling)")


if __name__ == "__main__":
    main()
