"""
Phase 2.3: Feedback Loop Instability Hypothesis Testing

Tests whether adaptive scheduling creates a positive feedback loop that destabilizes
the Hybrid controller's sliding surface dynamics.

Hypothesis:
    Adaptive scheduling creates positive feedback:
    chattering → large |θ| → conservative gains → weaker sliding mode → MORE chattering → repeat

    This should manifest as increased variance in |s|(t) when scheduler is active.

Test Design:
    - Baseline: Hybrid with FIXED MT-8 robust gains
    - Test: Hybrid with ADAPTIVE SCHEDULER (50% conservative scaling)
    - IC: +-0.05 rad (worst-case from Phase 1.3)
    - Trials: 50 per condition = 100 total
    - Logging: |s|(t) at 100Hz, compute variance over 1-second windows
    - Metrics: Mean variance, max variance, variance explosion ratio

Expected Results:
    1. |s| variance increases 3-10x with adaptive scheduling
    2. Chattering std increases 3-4x (0.108 → 0.405 from Phase 1.3)
    3. Positive correlation: variance spikes correlate with scheduler mode switches
    4. Validates feedback loop instability mechanism

Usage:
    python scripts/research/phase2_3_test_feedback_instability.py
    python scripts/research/phase2_3_test_feedback_instability.py --trials 100
    python scripts/research/phase2_3_test_feedback_instability.py --quick  # 10 trials for testing
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import warnings

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import load_config
from src.controllers.factory import create_controller
from src.controllers.adaptive_gain_scheduler import AdaptiveGainScheduler, GainScheduleConfig
from src.plant.core.dynamics import DIPDynamics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ASCII-only output (Windows terminal compatibility)
ASCII_OK = "[OK]"
ASCII_ERROR = "[ERROR]"
ASCII_INFO = "[INFO]"
ASCII_WARN = "[WARNING]"


def compute_windowed_variance(trajectory: np.ndarray, window_size: int) -> np.ndarray:
    """
    Compute variance over sliding windows.

    Args:
        trajectory: Time series data [steps]
        window_size: Window size in samples

    Returns:
        Array of variance values (one per window)
    """
    num_windows = len(trajectory) - window_size + 1
    variances = np.zeros(num_windows)

    for i in range(num_windows):
        window = trajectory[i:i+window_size]
        variances[i] = np.var(window)

    return variances


def run_single_trial_with_variance_logging(
    controller,
    dynamics: DIPDynamics,
    initial_state: np.ndarray,
    is_scheduler: bool = False,
    duration: float = 5.0,
    dt: float = 0.01,
    window_duration: float = 1.0
) -> Dict:
    """
    Run a single simulation trial with sliding surface variance logging.

    Args:
        controller: Controller instance (Hybrid or wrapped with scheduler)
        dynamics: Dynamics model
        initial_state: Initial condition [x, th1, th2, xdot, th1dot, th2dot]
        is_scheduler: Whether controller is wrapped with scheduler
        duration: Simulation duration (seconds)
        dt: Timestep (seconds)
        window_duration: Variance window duration (seconds)

    Returns:
        Dictionary with trajectories and variance metrics
    """
    steps = int(duration / dt)
    window_size = int(window_duration / dt)
    state = initial_state.copy()

    # Trajectory storage
    time_vec = np.zeros(steps)
    states = np.zeros((steps, 6))
    controls = np.zeros(steps)
    s_trajectory = np.zeros(steps)
    theta_mag_trajectory = np.zeros(steps)

    # Initialize
    last_u = 0.0
    if is_scheduler:
        state_vars = controller.initialize_state()
        history = controller.initialize_history()
    else:
        state_vars = controller.initialize_state() if hasattr(controller, 'initialize_state') else None
        history = controller.initialize_history() if hasattr(controller, 'initialize_history') else None

    # Simulation loop
    for i in range(steps):
        time_vec[i] = i * dt
        states[i] = state

        # Compute control
        try:
            if history is not None:
                output = controller.compute_control(state, state_vars, history)
            else:
                output = controller.compute_control(state, last_u)

            # Handle both direct float return and NamedTuple return
            if hasattr(output, 'u'):
                u = output.u
                # Extract s from output
                s = output.sigma if hasattr(output, 'sigma') else 0.0
            else:
                u = output
                # Access internal state
                if is_scheduler:
                    s = controller.base_controller.s if hasattr(controller.base_controller, 's') else 0.0
                else:
                    s = controller.s if hasattr(controller, 's') else 0.0
        except Exception as e:
            logger.warning(f"Control computation failed at step {i}: {e}")
            u = 0.0
            s = 0.0

        # Apply saturation
        u = float(np.clip(u, -50.0, 50.0))
        controls[i] = u

        # Log sliding surface magnitude
        s_trajectory[i] = abs(s)

        # Track theta magnitude
        theta_mag_trajectory[i] = np.sqrt(state[1]**2 + state[2]**2)

        # Step dynamics
        state = dynamics.step(state, u, dt)
        last_u = u

    # Compute windowed variance of |s|
    s_variances = compute_windowed_variance(s_trajectory, window_size)

    # Compute chattering (mean absolute jerk)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=RuntimeWarning)
        accel = np.gradient(controls, dt)
        jerk = np.gradient(accel, dt)
        chattering = np.mean(np.abs(jerk))
        chattering_std = np.std(np.abs(jerk))
        if np.isnan(chattering) or np.isinf(chattering):
            chattering = 0.0
            chattering_std = 0.0

    # Compute control effort
    control_effort = np.trapz(np.abs(controls), dx=dt)

    return {
        "time": time_vec,
        "states": states,
        "controls": controls,
        "s_trajectory": s_trajectory,
        "theta_mag_trajectory": theta_mag_trajectory,
        "s_variances": s_variances,
        "chattering": chattering,
        "chattering_std": chattering_std,
        "control_effort": control_effort,
        "mean_s": np.mean(s_trajectory),
        "std_s": np.std(s_trajectory),
        "mean_s_variance": np.mean(s_variances),
        "max_s_variance": np.max(s_variances),
        "std_s_variance": np.std(s_variances)
    }


def run_monte_carlo_phase2_3(
    config,
    ic_magnitude: float = 0.05,
    trials_per_condition: int = 50,
    seed: int = 42
) -> Dict:
    """
    Run Phase 2.3 Monte Carlo trials comparing fixed gains vs adaptive scheduler.

    Args:
        config: Configuration object
        ic_magnitude: Initial condition magnitude (rad)
        trials_per_condition: Number of trials per condition
        seed: Random seed

    Returns:
        Dictionary with aggregated results
    """
    logger.info("="*80)
    logger.info(f"{ASCII_INFO} PHASE 2.3: FEEDBACK LOOP INSTABILITY HYPOTHESIS TESTING")
    logger.info("="*80)
    logger.info(f"{ASCII_INFO} IC: +-{ic_magnitude} rad (worst-case from Phase 1.3)")
    logger.info(f"{ASCII_INFO} Baseline: Hybrid with FIXED MT-8 robust gains")
    logger.info(f"{ASCII_INFO} Test: Hybrid with ADAPTIVE SCHEDULER (50% conservative scaling)")
    logger.info(f"{ASCII_INFO} Trials per condition: {trials_per_condition}")
    logger.info(f"{ASCII_INFO} Total trials: {trials_per_condition * 2}")
    logger.info("="*80)

    # Initialize dynamics
    dynamics = DIPDynamics(config.physics)

    # MT-8 robust gains for Hybrid Adaptive STA SMC
    mt8_gains = [10.149, 12.839, 6.815, 2.750]  # c1, lambda1, c2, lambda2

    # Scheduler configuration
    scheduler_config = GainScheduleConfig(
        small_error_threshold=0.1,
        large_error_threshold=0.2,
        conservative_scale=0.5,
        hysteresis_width=0.01,
        use_angles_only=True
    )

    # Storage for results
    results = {
        "fixed_gains": [],
        "adaptive_scheduler": []
    }

    # Run FIXED GAINS trials (baseline)
    logger.info(f"\n{ASCII_INFO} Running FIXED GAINS trials (baseline)...")
    for trial in range(trials_per_condition):
        # Create controller (fresh instance per trial)
        controller = create_controller(
            'hybrid_adaptive_sta_smc',
            config=config,
            gains=mt8_gains
        )

        # Random IC with unique seed
        np.random.seed(seed + trial)
        ic_variation = np.random.uniform(-0.01, 0.01, size=6)
        initial_state = np.array([0.0, ic_magnitude, ic_magnitude, 0.0, 0.0, 0.0]) + ic_variation

        # Run trial
        result = run_single_trial_with_variance_logging(
            controller, dynamics, initial_state, is_scheduler=False
        )
        results["fixed_gains"].append(result)

        if (trial + 1) % 10 == 0:
            logger.info(f"{ASCII_OK} Completed {trial + 1}/{trials_per_condition} fixed gains trials")

    # Run ADAPTIVE SCHEDULER trials (test)
    logger.info(f"\n{ASCII_INFO} Running ADAPTIVE SCHEDULER trials (test)...")
    for trial in range(trials_per_condition):
        # Create base controller (fresh instance per trial)
        base_controller = create_controller(
            'hybrid_adaptive_sta_smc',
            config=config,
            gains=mt8_gains
        )

        # Wrap with adaptive scheduler
        controller = AdaptiveGainScheduler(
            base_controller=base_controller,
            config=scheduler_config
        )

        # Random IC with unique seed (offset to avoid same ICs as baseline)
        np.random.seed(seed + trials_per_condition + trial)
        ic_variation = np.random.uniform(-0.01, 0.01, size=6)
        initial_state = np.array([0.0, ic_magnitude, ic_magnitude, 0.0, 0.0, 0.0]) + ic_variation

        # Run trial
        result = run_single_trial_with_variance_logging(
            controller, dynamics, initial_state, is_scheduler=True
        )
        results["adaptive_scheduler"].append(result)

        if (trial + 1) % 10 == 0:
            logger.info(f"{ASCII_OK} Completed {trial + 1}/{trials_per_condition} scheduler trials")

    logger.info(f"\n{ASCII_OK} All trials complete!")
    return results


def aggregate_and_analyze(results: Dict) -> Dict:
    """
    Aggregate results and perform statistical analysis.

    Args:
        results: Dictionary with fixed_gains and adaptive_scheduler trial lists

    Returns:
        Dictionary with aggregated metrics and statistics
    """
    logger.info(f"\n{ASCII_INFO} Aggregating results...")

    # Extract metrics for each condition
    fixed_metrics = {
        "chattering": [r["chattering"] for r in results["fixed_gains"]],
        "chattering_std": [r["chattering_std"] for r in results["fixed_gains"]],
        "control_effort": [r["control_effort"] for r in results["fixed_gains"]],
        "mean_s": [r["mean_s"] for r in results["fixed_gains"]],
        "std_s": [r["std_s"] for r in results["fixed_gains"]],
        "mean_s_variance": [r["mean_s_variance"] for r in results["fixed_gains"]],
        "max_s_variance": [r["max_s_variance"] for r in results["fixed_gains"]],
        "std_s_variance": [r["std_s_variance"] for r in results["fixed_gains"]]
    }

    scheduler_metrics = {
        "chattering": [r["chattering"] for r in results["adaptive_scheduler"]],
        "chattering_std": [r["chattering_std"] for r in results["adaptive_scheduler"]],
        "control_effort": [r["control_effort"] for r in results["adaptive_scheduler"]],
        "mean_s": [r["mean_s"] for r in results["adaptive_scheduler"]],
        "std_s": [r["std_s"] for r in results["adaptive_scheduler"]],
        "mean_s_variance": [r["mean_s_variance"] for r in results["adaptive_scheduler"]],
        "max_s_variance": [r["max_s_variance"] for r in results["adaptive_scheduler"]],
        "std_s_variance": [r["std_s_variance"] for r in results["adaptive_scheduler"]]
    }

    # Compute statistics
    summary = {}
    for key in fixed_metrics:
        # Numerical metrics
        fixed_arr = np.array(fixed_metrics[key])
        scheduler_arr = np.array(scheduler_metrics[key])

        # Handle NaN/Inf
        fixed_arr = fixed_arr[np.isfinite(fixed_arr)]
        scheduler_arr = scheduler_arr[np.isfinite(scheduler_arr)]

        fixed_mean = np.mean(fixed_arr)
        fixed_std = np.std(fixed_arr)
        scheduler_mean = np.mean(scheduler_arr)
        scheduler_std = np.std(scheduler_arr)

        # Statistical test
        if len(fixed_arr) > 0 and len(scheduler_arr) > 0 and fixed_std > 0 and scheduler_std > 0:
            t_stat, p_value = stats.ttest_ind(fixed_arr, scheduler_arr, equal_var=False)

            # Cohen's d
            pooled_std = np.sqrt((fixed_std**2 + scheduler_std**2) / 2)
            cohen_d = (scheduler_mean - fixed_mean) / pooled_std if pooled_std > 0 else 0.0
        else:
            t_stat, p_value, cohen_d = np.nan, np.nan, np.nan

        # Variance explosion ratio
        variance_ratio = scheduler_mean / fixed_mean if fixed_mean > 0 else 0.0

        summary[key] = {
            "fixed": {"mean": fixed_mean, "std": fixed_std},
            "scheduler": {"mean": scheduler_mean, "std": scheduler_std},
            "t_statistic": t_stat,
            "p_value": p_value,
            "cohen_d": cohen_d,
            "percent_change": ((scheduler_mean - fixed_mean) / fixed_mean * 100) if fixed_mean != 0 else 0.0,
            "variance_ratio": variance_ratio
        }

    return summary


def print_summary_report(summary: Dict):
    """
    Print human-readable summary report.

    Args:
        summary: Aggregated statistics dictionary
    """
    logger.info("\n" + "="*80)
    logger.info(f"{ASCII_OK} PHASE 2.3 RESULTS SUMMARY")
    logger.info("="*80)

    # |s| mean variance (KEY METRIC)
    logger.info(f"\n{ASCII_INFO} |s| Mean Variance (KEY METRIC - Feedback Instability Indicator):")
    logger.info(f"  Fixed Gains: {summary['mean_s_variance']['fixed']['mean']:.6f} +- {summary['mean_s_variance']['fixed']['std']:.6f}")
    logger.info(f"  Scheduler: {summary['mean_s_variance']['scheduler']['mean']:.6f} +- {summary['mean_s_variance']['scheduler']['std']:.6f}")
    logger.info(f"  Variance Ratio: {summary['mean_s_variance']['variance_ratio']:.2f}x (expected 3-10x)")
    logger.info(f"  Change: {summary['mean_s_variance']['percent_change']:+.1f}% (p={summary['mean_s_variance']['p_value']:.3f}, d={summary['mean_s_variance']['cohen_d']:.2f})")

    # |s| max variance
    logger.info(f"\n{ASCII_INFO} |s| Max Variance:")
    logger.info(f"  Fixed Gains: {summary['max_s_variance']['fixed']['mean']:.6f} +- {summary['max_s_variance']['fixed']['std']:.6f}")
    logger.info(f"  Scheduler: {summary['max_s_variance']['scheduler']['mean']:.6f} +- {summary['max_s_variance']['scheduler']['std']:.6f}")
    logger.info(f"  Variance Ratio: {summary['max_s_variance']['variance_ratio']:.2f}x")

    # Chattering std (Supporting Evidence)
    logger.info(f"\n{ASCII_INFO} Chattering Std (Supporting Evidence):")
    logger.info(f"  Fixed Gains: {summary['chattering_std']['fixed']['mean']:.4f} +- {summary['chattering_std']['fixed']['std']:.4f}")
    logger.info(f"  Scheduler: {summary['chattering_std']['scheduler']['mean']:.4f} +- {summary['chattering_std']['scheduler']['std']:.4f}")
    logger.info(f"  Variance Ratio: {summary['chattering_std']['variance_ratio']:.2f}x (Phase 1.3 showed 3.7x)")

    # Chattering mean
    logger.info(f"\n{ASCII_INFO} Chattering (rad/s^2):")
    logger.info(f"  Fixed Gains: {summary['chattering']['fixed']['mean']:.1f} +- {summary['chattering']['fixed']['std']:.1f}")
    logger.info(f"  Scheduler: {summary['chattering']['scheduler']['mean']:.1f} +- {summary['chattering']['scheduler']['std']:.1f}")
    logger.info(f"  Change: {summary['chattering']['percent_change']:+.1f}% (p={summary['chattering']['p_value']:.3f})")

    logger.info("\n" + "="*80)


def save_results(results: Dict, summary: Dict, output_dir: Path):
    """
    Save results to JSON and generate plots.

    Args:
        results: Raw trial results
        summary: Aggregated statistics
        output_dir: Output directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save summary JSON
    summary_path = output_dir / "phase2_3_feedback_instability_report.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2, default=lambda x: str(x))
    logger.info(f"{ASCII_OK} Saved summary report: {summary_path}")

    # Create visualization
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # Plot 1: |s| mean variance comparison
    ax = axes[0, 0]
    fixed_var = [r["mean_s_variance"] for r in results["fixed_gains"]]
    sched_var = [r["mean_s_variance"] for r in results["adaptive_scheduler"]]
    ax.boxplot([fixed_var, sched_var], tick_labels=['Fixed Gains', 'Scheduler'])
    ax.set_ylabel('|s| Mean Variance')
    ax.set_title('Sliding Surface Variance: Fixed vs Scheduler')
    ax.grid(True, alpha=0.3)

    # Plot 2: |s| max variance comparison
    ax = axes[0, 1]
    fixed_max = [r["max_s_variance"] for r in results["fixed_gains"]]
    sched_max = [r["max_s_variance"] for r in results["adaptive_scheduler"]]
    ax.boxplot([fixed_max, sched_max], tick_labels=['Fixed Gains', 'Scheduler'])
    ax.set_ylabel('|s| Max Variance')
    ax.set_title('Peak Variance: Fixed vs Scheduler')
    ax.grid(True, alpha=0.3)

    # Plot 3: Chattering std comparison
    ax = axes[0, 2]
    fixed_chat_std = [r["chattering_std"] for r in results["fixed_gains"]]
    sched_chat_std = [r["chattering_std"] for r in results["adaptive_scheduler"]]
    ax.boxplot([fixed_chat_std, sched_chat_std], tick_labels=['Fixed Gains', 'Scheduler'])
    ax.set_ylabel('Chattering Std')
    ax.set_title('Chattering Variability: Fixed vs Scheduler')
    ax.grid(True, alpha=0.3)

    # Plot 4: Chattering mean comparison
    ax = axes[1, 0]
    fixed_chat = [r["chattering"] for r in results["fixed_gains"]]
    sched_chat = [r["chattering"] for r in results["adaptive_scheduler"]]
    ax.boxplot([fixed_chat, sched_chat], tick_labels=['Fixed Gains', 'Scheduler'])
    ax.set_ylabel('Chattering (rad/s^2)')
    ax.set_title('Chattering: Fixed vs Scheduler')
    ax.grid(True, alpha=0.3)

    # Plot 5: |s| std comparison
    ax = axes[1, 1]
    fixed_s_std = [r["std_s"] for r in results["fixed_gains"]]
    sched_s_std = [r["std_s"] for r in results["adaptive_scheduler"]]
    ax.boxplot([fixed_s_std, sched_s_std], tick_labels=['Fixed Gains', 'Scheduler'])
    ax.set_ylabel('|s| Std')
    ax.set_title('|s| Variability: Fixed vs Scheduler')
    ax.grid(True, alpha=0.3)

    # Plot 6: Control effort comparison
    ax = axes[1, 2]
    fixed_effort = [r["control_effort"] for r in results["fixed_gains"]]
    sched_effort = [r["control_effort"] for r in results["adaptive_scheduler"]]
    ax.boxplot([fixed_effort, sched_effort], tick_labels=['Fixed Gains', 'Scheduler'])
    ax.set_ylabel('Control Effort')
    ax.set_title('Control Effort: Fixed vs Scheduler')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plot_path = output_dir / "phase2_3_feedback_instability_comparison.png"
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"{ASCII_OK} Saved plot: {plot_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Phase 2.3: Feedback Loop Instability Hypothesis Testing")
    parser.add_argument('--trials', type=int, default=50, help='Trials per condition (default: 50)')
    parser.add_argument('--quick', action='store_true', help='Quick test with 10 trials per condition')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--output', type=str, default='benchmarks/research/phase2_3', help='Output directory')
    args = parser.parse_args()

    # Determine trial count
    trials_per_condition = 10 if args.quick else args.trials

    # Load config
    config = load_config("config.yaml")

    # Run Monte Carlo
    results = run_monte_carlo_phase2_3(
        config,
        ic_magnitude=0.05,
        trials_per_condition=trials_per_condition,
        seed=args.seed
    )

    # Aggregate and analyze
    summary = aggregate_and_analyze(results)

    # Print summary
    print_summary_report(summary)

    # Save results
    output_dir = Path(args.output)
    save_results(results, summary, output_dir)

    logger.info(f"\n{ASCII_OK} Phase 2.3 complete!")
    logger.info(f"{ASCII_INFO} Results saved to: {output_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
