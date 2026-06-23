"""
Phase 4.1: Validate |s|-Based Threshold Scheduler

Tests whether the new SlidingSurfaceScheduler (|s|-based) fixes the feedback loop
instability caused by the angle-based AdaptiveGainScheduler (Phase 2.3 issue).

Background:
    Phase 2.3 showed that angle-based adaptive scheduling creates positive feedback:
    - Chattering → large |θ| → conservative gains → MORE chattering
    - Result: +176% chattering increase, +2.27x |s| variance
    - Root cause: Monitoring angles creates indirect feedback through control performance

Hypothesis:
    The new |s|-based scheduler will break the feedback loop by:
    1. Monitoring |s| directly (control performance metric)
    2. Inverted logic: HIGH |s| → INCREASE gains (not decrease)
    3. Result: Chattering → large |s| → aggressive gains → LESS chattering

Test Design:
    - Condition 1: Baseline (no scheduling, fixed robust gains)
    - Condition 2: Angle-based (AdaptiveGainScheduler - Phase 2.3 implementation)
    - Condition 3: |s|-based (SlidingSurfaceScheduler - NEW implementation)
    - IC: ±0.05 rad (worst-case from Phase 1.3)
    - Trials: 25 per condition = 75 total
    - Metrics: |s| variance, chattering, control effort, overshoot

Expected Results:
    1. Baseline: Low chattering, low variance (reference)
    2. Angle-based: +176% chattering (replicates Phase 2.3 finding)
    3. |s|-based: ≤10% chattering increase (SUCCESS if breaks feedback loop)

Success Criteria:
    - |s|-based shows <50% chattering increase vs baseline
    - |s|-based shows significant reduction vs angle-based (p<0.05)
    - |s|-based |s| variance ratio <1.5x baseline

Usage:
    python scripts/research/phase4_1_validate_s_based_scheduler.py
    python scripts/research/phase4_1_validate_s_based_scheduler.py --trials 100
    python scripts/research/phase4_1_validate_s_based_scheduler.py --quick  # 10 trials
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List
import warnings

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import load_config
from src.controllers.factory import create_controller
from src.controllers.adaptive_gain_scheduler import AdaptiveGainScheduler, GainScheduleConfig
from src.controllers.sliding_surface_scheduler import SlidingSurfaceScheduler, SlidingSurfaceScheduleConfig
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
    """Compute variance over sliding windows."""
    num_windows = len(trajectory) - window_size + 1
    variances = np.zeros(num_windows)
    for i in range(num_windows):
        window = trajectory[i:i+window_size]
        variances[i] = np.var(window)
    return variances


def run_single_trial(
    controller,
    dynamics: DIPDynamics,
    initial_state: np.ndarray,
    robust_gains: List[float],
    scheduler_mode: str = "none",
    duration: float = 5.0,
    dt: float = 0.01,
    window_duration: float = 1.0
) -> Dict:
    """Run a single simulation trial with comprehensive metrics."""
    steps = int(duration / dt)
    window_size = int(window_duration / dt)

    # Storage
    state = initial_state.copy()
    trajectory_s = np.zeros(steps)
    trajectory_u = np.zeros(steps)
    trajectory_theta1 = np.zeros(steps)
    trajectory_theta2 = np.zeros(steps)

    last_control = 0.0

    # Reset controller
    if hasattr(controller, 'cleanup'):
        controller.cleanup()

    state_vars = controller.initialize_state() if hasattr(controller, 'initialize_state') else None
    history = controller.initialize_history() if hasattr(controller, 'initialize_history') else None

    # Run simulation
    for i in range(steps):
        # Compute control
        if history is not None:
            u = controller.compute_control(state, state_vars, history)
            if hasattr(u, 'u'):
                u = u.u
        else:
            u = controller.compute_control(state, last_control)

        # Log trajectories
        c1, c2 = robust_gains[0], robust_gains[2]
        s = c1 * state[1] + c2 * state[4]  # c1*theta1 + c2*theta1_dot
        trajectory_s[i] = abs(s)
        trajectory_u[i] = u
        trajectory_theta1[i] = state[1]
        trajectory_theta2[i] = state[2]

        # Update state
        state = dynamics.step(state, u, dt)
        last_control = u

    # Compute metrics
    # Sliding surface variance
    variances = compute_windowed_variance(trajectory_s, window_size)
    mean_variance = np.mean(variances)
    max_variance = np.max(variances)
    std_variance = np.std(variances)

    # Chattering (jerk)
    jerk = np.abs(np.diff(trajectory_u, n=3)) / (dt ** 3)
    chattering = np.mean(jerk)
    chattering_std = np.std(jerk)

    # Control effort
    control_effort = np.mean(np.abs(trajectory_u))

    # Overshoot (max angle)
    max_theta1 = np.max(np.abs(trajectory_theta1))
    max_theta2 = np.max(np.abs(trajectory_theta2))
    max_overshoot = max(max_theta1, max_theta2)

    # Settling time (time to reach and stay within 5 degrees)
    threshold = np.radians(5)
    settled_mask = (np.abs(trajectory_theta1) < threshold) & (np.abs(trajectory_theta2) < threshold)
    if np.any(settled_mask):
        settling_idx = np.where(settled_mask)[0][0]
        settling_time = settling_idx * dt
    else:
        settling_time = duration  # Did not settle

    # Sliding surface stats
    mean_s = np.mean(trajectory_s)
    std_s = np.std(trajectory_s)

    return {
        "mean_s_variance": mean_variance,
        "max_s_variance": max_variance,
        "std_s_variance": std_variance,
        "chattering": chattering,
        "chattering_std": chattering_std,
        "control_effort": control_effort,
        "max_overshoot": max_overshoot,
        "settling_time": settling_time,
        "mean_s": mean_s,
        "std_s": std_s,
    }


def create_scheduled_controller(
    config,
    mode: str,
    robust_gains: List[float]
):
    """
    Create controller with specified scheduling mode.

    Args:
        config: Configuration object
        mode: "none", "angle_based", "s_based"
        robust_gains: [c1, lambda1, c2, lambda2]

    Returns:
        Controller instance
    """
    # Create base Hybrid controller
    base_controller = create_controller(
        'hybrid_adaptive_sta_smc',
        config=config,
        gains=robust_gains,
        k1_init=0.2,
        k2_init=0.02
    )

    if mode == "none":
        # No scheduling - return as-is
        return base_controller

    elif mode == "angle_based":
        # Angle-based scheduling (Phase 2.3 implementation)
        scheduler_config = GainScheduleConfig(
            small_error_threshold=0.1,
            large_error_threshold=0.2,
            conservative_scale=0.5,
            hysteresis_width=0.01,
            use_angles_only=True
        )
        return AdaptiveGainScheduler(
            base_controller=base_controller,
            config=scheduler_config
        )

    elif mode == "s_based":
        # |s|-based scheduling (NEW implementation)
        scheduler_config = SlidingSurfaceScheduleConfig(
            small_s_threshold=0.1,
            large_s_threshold=0.5,
            aggressive_scale=1.0,
            conservative_scale=0.5,
            hysteresis_width=0.05,
            c1=robust_gains[0],
            c2=robust_gains[2]
        )
        return SlidingSurfaceScheduler(
            base_controller=base_controller,
            config=scheduler_config,
            robust_gains=robust_gains
        )

    else:
        raise ValueError(f"Unknown mode: {mode}")


def run_monte_carlo_condition(
    config,
    dynamics: DIPDynamics,
    robust_gains: List[float],
    mode: str,
    num_trials: int,
    ic_range: float = 0.05,
    seed: int = 42
) -> List[Dict]:
    """Run Monte Carlo trials for a single scheduling condition."""
    np.random.seed(seed)
    results = []

    logger.info(f"{ASCII_INFO} Running {num_trials} trials for mode={mode}")

    for trial in range(num_trials):
        # Random IC
        theta1_init = np.random.uniform(-ic_range, ic_range)
        theta2_init = np.random.uniform(-ic_range, ic_range)
        ic_variation = np.random.uniform(-0.01, 0.01, size=6)
        initial_state = np.array([0.0, theta1_init, theta2_init, 0.0, 0.0, 0.0]) + ic_variation

        # Create controller
        controller = create_scheduled_controller(config, mode, robust_gains)

        # Run trial
        trial_result = run_single_trial(
            controller,
            dynamics,
            initial_state,
            robust_gains,
            scheduler_mode=mode
        )

        results.append(trial_result)

        # Cleanup
        if hasattr(controller, 'cleanup'):
            controller.cleanup()

        if (trial + 1) % 10 == 0:
            logger.info(f"  Completed {trial + 1}/{num_trials} trials")

    logger.info(f"{ASCII_OK} Completed all {num_trials} trials for mode={mode}")
    return results


def aggregate_results(results: List[Dict]) -> Dict:
    """Aggregate Monte Carlo results."""
    metrics = [
        "mean_s_variance", "max_s_variance", "std_s_variance",
        "chattering", "chattering_std", "control_effort",
        "max_overshoot", "settling_time", "mean_s", "std_s"
    ]

    aggregated = {}
    for metric in metrics:
        values = [r[metric] for r in results]
        aggregated[metric] = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "median": float(np.median(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values))
        }

    return aggregated


def compare_conditions(results_dict: Dict[str, List[Dict]]) -> Dict:
    """Compare scheduling conditions statistically."""
    metrics = [
        "mean_s_variance", "max_s_variance", "chattering",
        "chattering_std", "control_effort", "max_overshoot", "settling_time"
    ]

    comparison = {}
    baseline = results_dict["none"]

    for mode in ["angle_based", "s_based"]:
        test_data = results_dict[mode]
        mode_comparison = {}

        for metric in metrics:
            baseline_values = [r[metric] for r in baseline]
            test_values = [r[metric] for r in test_data]

            # Welch's t-test
            t_stat, p_value = stats.ttest_ind(baseline_values, test_values, equal_var=False)

            # Cohen's d
            mean_diff = np.mean(test_values) - np.mean(baseline_values)
            pooled_std = np.sqrt((np.std(baseline_values)**2 + np.std(test_values)**2) / 2)
            cohen_d = mean_diff / pooled_std if pooled_std > 0 else 0.0

            # Percent change
            baseline_mean = np.mean(baseline_values)
            test_mean = np.mean(test_values)
            pct_change = ((test_mean - baseline_mean) / baseline_mean * 100) if baseline_mean > 0 else 0.0

            # Ratio
            ratio = test_mean / baseline_mean if baseline_mean > 0 else 0.0

            mode_comparison[metric] = {
                "baseline_mean": float(baseline_mean),
                "test_mean": float(test_mean),
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "cohen_d": float(cohen_d),
                "percent_change": float(pct_change),
                "ratio": float(ratio),
                "significant": bool(p_value < 0.05)
            }

        comparison[mode] = mode_comparison

    return comparison


def create_comparison_plots(
    results_dict: Dict[str, List[Dict]],
    comparison: Dict,
    output_dir: Path
):
    """Create comparison plots."""
    modes = ["none", "angle_based", "s_based"]
    mode_labels = {
        "none": "Baseline\n(No Scheduling)",
        "angle_based": "Angle-Based\n(Phase 2.3)",
        "s_based": "|s|-Based\n(NEW)"
    }

    fig, axes = plt.subplots(2, 4, figsize=(16, 10))
    fig.suptitle("Phase 4.1: |s|-Based Scheduler Validation", fontsize=14, fontweight='bold')

    metrics_to_plot = [
        ("mean_s_variance", "|s| Mean Variance", "Variance"),
        ("max_s_variance", "|s| Max Variance", "Variance"),
        ("chattering", "Chattering", "rad/s^2"),
        ("chattering_std", "Chattering Std", "rad/s^2"),
        ("control_effort", "Control Effort", "N"),
        ("max_overshoot", "Max Overshoot", "rad"),
        ("settling_time", "Settling Time", "s"),
        ("mean_s", "Mean |s|", "")
    ]

    for idx, (metric, title, ylabel) in enumerate(metrics_to_plot):
        ax = axes[idx // 4, idx % 4]

        data_to_plot = []
        labels_to_plot = []
        colors = ['#2ecc71', '#e74c3c', '#3498db']  # green, red, blue

        for mode in modes:
            values = [r[metric] for r in results_dict[mode]]
            data_to_plot.append(values)
            labels_to_plot.append(mode_labels[mode])

        bp = ax.boxplot(data_to_plot, labels=labels_to_plot, patch_artist=True)

        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)

        # Add significance markers
        if idx < 7:
            baseline_mean = np.mean(data_to_plot[0])
            for i, mode in enumerate(["angle_based", "s_based"]):
                if mode in comparison and metric in comparison[mode]:
                    stats_result = comparison[mode][metric]
                    if stats_result['significant']:
                        test_mean = stats_result['test_mean']
                        y_pos = max(test_mean, baseline_mean) * 1.1
                        ax.text(i+2, y_pos, '*' if stats_result['p_value'] < 0.05 else '**',
                               ha='center', fontsize=16, color='red')

        ax.set_title(title, fontweight='bold')
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', labelsize=8)

    plt.tight_layout()
    output_path = output_dir / "phase4_1_s_based_scheduler_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logger.info(f"{ASCII_OK} Saved comparison plot: {output_path}")
    plt.close()

    # Chattering ratio bar plot
    fig, ax = plt.subplots(figsize=(10, 6))

    modes_test = ["angle_based", "s_based"]
    chattering_ratios = [comparison[mode]["chattering"]["ratio"] for mode in modes_test]
    colors_test = ['#e74c3c', '#3498db']

    bars = ax.bar(range(len(modes_test)), chattering_ratios, color=colors_test, alpha=0.7, edgecolor='black')
    ax.axhline(y=1.0, color='green', linestyle='--', linewidth=2, label='Baseline (No Scheduling)')

    for i, (bar, ratio) in enumerate(zip(bars, chattering_ratios)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{ratio:.2f}x\n({comparison[modes_test[i]]["chattering"]["percent_change"]:+.0f}%)',
               ha='center', va='bottom', fontweight='bold', fontsize=11)

    ax.set_xticks(range(len(modes_test)))
    ax.set_xticklabels([mode_labels[m] for m in modes_test])
    ax.set_ylabel("Chattering Ratio vs Baseline", fontsize=12, fontweight='bold')
    ax.set_title("Phase 4.1: Chattering Comparison - |s|-Based vs Angle-Based", fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_path = output_dir / "phase4_1_chattering_ratio_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logger.info(f"{ASCII_OK} Saved chattering ratio plot: {output_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Phase 4.1: |s|-Based Scheduler Validation")
    parser.add_argument("--trials", type=int, default=25,
                       help="Number of trials per condition (default: 25)")
    parser.add_argument("--quick", action="store_true",
                       help="Quick test with 10 trials per condition")
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed (default: 42)")

    args = parser.parse_args()

    if args.quick:
        num_trials = 10
        logger.info(f"{ASCII_INFO} Running quick test with {num_trials} trials per condition")
    else:
        num_trials = args.trials

    # Load configuration
    config = load_config("config.yaml")
    dynamics = DIPDynamics(config.physics)

    # MT-8 robust PSO gains
    robust_gains = [10.149, 12.839, 6.815, 2.750]

    # Output directory
    output_dir = Path("benchmarks/research/phase4_1")
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 70)
    logger.info("Phase 4.1: |s|-Based Threshold Scheduler Validation")
    logger.info("=" * 70)
    logger.info(f"{ASCII_INFO} Configuration:")
    logger.info(f"  - Trials per condition: {num_trials}")
    logger.info(f"  - Total trials: {num_trials * 3}")
    logger.info(f"  - IC range: +-0.05 rad")
    logger.info(f"  - Robust gains: {robust_gains}")
    logger.info(f"  - Random seed: {args.seed}")

    # Run all conditions
    modes = ["none", "angle_based", "s_based"]
    results_dict = {}

    for mode in modes:
        logger.info(f"\n{ASCII_INFO} Testing mode: {mode}")
        results = run_monte_carlo_condition(
            config, dynamics, robust_gains, mode, num_trials,
            ic_range=0.05, seed=args.seed
        )
        results_dict[mode] = results

    # Aggregate results
    logger.info(f"\n{ASCII_INFO} Aggregating results...")
    aggregated = {}
    for mode in modes:
        aggregated[mode] = aggregate_results(results_dict[mode])

    # Statistical comparison
    logger.info(f"{ASCII_INFO} Performing statistical comparisons...")
    comparison = compare_conditions(results_dict)

    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("RESULTS SUMMARY")
    logger.info("=" * 70)

    for mode in modes:
        logger.info(f"\n{mode.upper()}:")
        logger.info(f"  |s| Mean Variance: {aggregated[mode]['mean_s_variance']['mean']:.2f} +- {aggregated[mode]['mean_s_variance']['std']:.2f}")
        logger.info(f"  Chattering: {aggregated[mode]['chattering']['mean']:.2f} +- {aggregated[mode]['chattering']['std']:.2f} rad/s^2")
        logger.info(f"  Max Overshoot: {np.degrees(aggregated[mode]['max_overshoot']['mean']):.1f} +- {np.degrees(aggregated[mode]['max_overshoot']['std']):.1f} degrees")
        logger.info(f"  Control Effort: {aggregated[mode]['control_effort']['mean']:.2f} +- {aggregated[mode]['control_effort']['std']:.2f} N")

    logger.info("\n" + "=" * 70)
    logger.info("COMPARISON VS BASELINE (none)")
    logger.info("=" * 70)

    for mode in ["angle_based", "s_based"]:
        logger.info(f"\n{mode.upper()}:")
        var_stats = comparison[mode]["mean_s_variance"]
        chatter_stats = comparison[mode]["chattering"]

        logger.info(f"  |s| Variance: {var_stats['ratio']:.2f}x ({var_stats['percent_change']:+.1f}%)")
        logger.info(f"    p={var_stats['p_value']:.4f}, d={var_stats['cohen_d']:.2f}")
        logger.info(f"  Chattering: {chatter_stats['ratio']:.2f}x ({chatter_stats['percent_change']:+.1f}%)")
        logger.info(f"    p={chatter_stats['p_value']:.4f}, d={chatter_stats['cohen_d']:.2f}")

    # Success criteria check
    logger.info("\n" + "=" * 70)
    logger.info("SUCCESS CRITERIA CHECK")
    logger.info("=" * 70)

    s_based_chatter_ratio = comparison["s_based"]["chattering"]["ratio"]
    s_based_var_ratio = comparison["s_based"]["mean_s_variance"]["ratio"]

    criteria_1 = s_based_chatter_ratio < 1.5  # <50% increase
    criteria_2 = s_based_var_ratio < 1.5      # <50% variance increase
    criteria_3 = comparison["s_based"]["chattering"]["p_value"] < 0.05  # Significant improvement

    logger.info(f"\n1. Chattering ratio <1.5x: {s_based_chatter_ratio:.2f}x - {'PASS' if criteria_1 else 'FAIL'}")
    logger.info(f"2. Variance ratio <1.5x: {s_based_var_ratio:.2f}x - {'PASS' if criteria_2 else 'FAIL'}")
    logger.info(f"3. Statistically significant: p={comparison['s_based']['chattering']['p_value']:.4f} - {'PASS' if criteria_3 else 'FAIL'}")

    all_pass = criteria_1 and criteria_2
    logger.info(f"\nOVERALL: {'SUCCESS' if all_pass else 'NEEDS TUNING'}")

    # Save results
    output_data = {
        "test_parameters": {
            "trials_per_condition": num_trials,
            "total_trials": num_trials * 3,
            "ic_range": 0.05,
            "robust_gains": robust_gains,
            "random_seed": args.seed,
            "modes_tested": modes
        },
        "aggregated_results": aggregated,
        "statistical_comparison": comparison,
        "success_criteria": {
            "chattering_ratio_threshold": 1.5,
            "variance_ratio_threshold": 1.5,
            "s_based_chattering_ratio": float(s_based_chatter_ratio),
            "s_based_variance_ratio": float(s_based_var_ratio),
            "criteria_1_pass": bool(criteria_1),
            "criteria_2_pass": bool(criteria_2),
            "criteria_3_pass": bool(criteria_3),
            "overall_pass": bool(all_pass)
        }
    }

    output_json = output_dir / "phase4_1_s_based_scheduler_report.json"
    with open(output_json, 'w') as f:
        json.dump(output_data, f, indent=2)
    logger.info(f"\n{ASCII_OK} Saved results: {output_json}")

    # Create plots
    logger.info(f"{ASCII_INFO} Creating comparison plots...")
    create_comparison_plots(results_dict, comparison, output_dir)

    logger.info(f"\n{ASCII_OK} Phase 4.1 validation complete!")
    logger.info(f"{ASCII_INFO} Results saved to: {output_dir}")


if __name__ == "__main__":
    main()
