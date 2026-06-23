"""
Phase 3.1: Selective c1/c2 Scheduling Strategy Testing

Tests different c1/c2 scheduling configurations to identify which component
causes the feedback instability observed in Phase 2.3.

Background:
    Phase 2.3 showed that full c1/c2 adaptive scheduling causes:
    - 2.27x increase in |s| variance (p<0.001, d=1.33)
    - +176% chattering increase
    - Strong feedback loop instability

Hypothesis:
    Selective scheduling (c1 only OR c2 only) may reduce feedback instability
    compared to full scheduling (both c1 AND c2).

Test Design:
    - Condition 1: Baseline (no scheduling, fixed gains)
    - Condition 2: c1 only scheduling (c2 fixed)
    - Condition 3: c2 only scheduling (c1 fixed)
    - Condition 4: Full scheduling (both c1 and c2) - replicates Phase 2.3
    - IC: +-0.05 rad (worst-case from Phase 1.3)
    - Trials: 25 per condition = 100 total
    - Metrics: |s| variance, chattering, control effort, scheduler activity

Expected Results:
    1. Full scheduling (c1+c2) shows largest variance increase
    2. c1-only scheduling shows moderate variance increase
    3. c2-only scheduling shows smaller variance increase
    4. Baseline shows lowest variance (reference)

Usage:
    python scripts/research/phase3_1_test_selective_c1c2_scheduling.py
    python scripts/research/phase3_1_test_selective_c1c2_scheduling.py --trials 100
    python scripts/research/phase3_1_test_selective_c1c2_scheduling.py --quick  # 10 trials
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

# Enable DEBUG logging when verification mode is active
VERIFICATION_MODE = False  # Set to True for detailed verification logging

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
    robust_gains: List[float],
    scheduler_mode: str = "none",
    duration: float = 5.0,
    dt: float = 0.01,
    window_duration: float = 1.0
) -> Dict:
    """
    Run a single simulation trial with sliding surface variance logging.

    Args:
        controller: Controller instance (Hybrid or wrapped with scheduler)
        dynamics: DIP dynamics model
        initial_state: Initial state [4]
        scheduler_mode: "none", "c1_only", "c2_only", "full"
        duration: Simulation duration in seconds
        dt: Time step
        window_duration: Window size for variance computation (seconds)

    Returns:
        Dictionary with metrics and logged data
    """
    steps = int(duration / dt)
    window_size = int(window_duration / dt)

    # Storage for trajectory
    state = initial_state.copy()
    trajectory_s = np.zeros(steps)
    trajectory_u = np.zeros(steps)

    # Control history
    last_control = 0.0

    # Reset controller state and initialize history
    if hasattr(controller, 'cleanup'):
        controller.cleanup()

    # Initialize state and history
    state_vars = controller.initialize_state() if hasattr(controller, 'initialize_state') else None
    history = controller.initialize_history() if hasattr(controller, 'initialize_history') else None

    # Run simulation
    for i in range(steps):
        # Compute control
        if history is not None:
            u = controller.compute_control(state, state_vars, history)
            # Handle both direct float return and NamedTuple return
            if hasattr(u, 'u'):
                u = u.u
        else:
            u = controller.compute_control(state, last_control)

        # Log trajectories
        # State is [x, theta1, theta2, xdot, th1dot, th2dot]
        c1, c2 = robust_gains[0], robust_gains[2]  # c1, c2 from robust gains
        s = c1 * state[1] + c2 * state[4]  # theta1 and theta1_dot components
        trajectory_s[i] = abs(s)
        trajectory_u[i] = u

        # Update state
        state = dynamics.step(state, u, dt)

        # Update last control
        last_control = u

    # Compute metrics
    # Windowed variance
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
        "mean_s": mean_s,
        "std_s": std_s,
    }


def create_selective_scheduler(
    base_controller,
    config,
    mode: str,
    robust_gains: List[float]
) -> object:
    """
    Create a selective scheduler wrapper.

    Args:
        base_controller: Hybrid controller instance
        config: Configuration object
        mode: "none", "c1_only", "c2_only", "full"
        robust_gains: [c1, lambda1, c2, lambda2]

    Returns:
        Controller with selective scheduling applied
    """
    if mode == "none":
        # No scheduling - return controller as-is
        return base_controller

    if mode == "full":
        # Full scheduling - use AdaptiveGainScheduler
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

    # For selective modes, create custom wrapper
    class SelectiveScheduler:
        """Wrapper that applies selective gain scheduling (c1 or c2 only)"""

        def __init__(self, controller, mode, robust_gains):
            self.controller = controller
            self.mode = mode
            self.robust_gains = np.array(robust_gains)
            self.base_gains = robust_gains.copy()

            # Scheduler parameters
            self.small_threshold = 0.1
            self.large_threshold = 0.2
            self.conservative_scale = 0.5
            self.hysteresis_width = 0.01

            # State tracking
            self.current_mode = "conservative"  # Start in conservative mode
            self.last_theta_mag = 0.0

        def _compute_theta_magnitude(self, state):
            """Compute angle magnitude for scheduling decision"""
            # State is [x, theta1, theta2, xdot, th1dot, th2dot]
            theta1 = state[1]
            theta2 = state[2]
            return np.sqrt(theta1**2 + theta2**2)

        def _schedule_gains(self, state):
            """Apply selective scheduling based on mode"""
            theta_mag = self._compute_theta_magnitude(state)

            # Determine mode with hysteresis
            old_mode = self.current_mode
            if self.current_mode == "aggressive":
                # In aggressive mode, switch to conservative if theta exceeds large threshold
                if theta_mag > self.large_threshold + self.hysteresis_width:
                    self.current_mode = "conservative"
            else:  # conservative mode
                # In conservative mode, switch to aggressive if theta below small threshold
                if theta_mag < self.small_threshold - self.hysteresis_width:
                    self.current_mode = "aggressive"

            # Log mode transitions if verification mode enabled
            if VERIFICATION_MODE and old_mode != self.current_mode:
                logger.debug(f"  [SCHEDULER] Mode transition: {old_mode} -> {self.current_mode} (theta_mag={theta_mag:.4f})")

            self.last_theta_mag = theta_mag

            # Apply scaling based on mode
            if self.current_mode == "conservative":
                scale = self.conservative_scale
            else:
                scale = 1.0

            # Create scheduled gains based on selective mode
            scheduled_gains = self.robust_gains.copy()

            if self.mode == "c1_only":
                # Only scale c1 and lambda1 (indices 0, 1)
                scheduled_gains[0] = self.robust_gains[0] * scale  # c1
                scheduled_gains[1] = self.robust_gains[1] * scale  # lambda1
                # c2 and lambda2 remain at robust values
                if VERIFICATION_MODE:
                    logger.debug(f"  [c1_only] c1: {scheduled_gains[0]:.4f} (scale={scale:.2f}), c2: {scheduled_gains[2]:.4f} (FIXED)")
            elif self.mode == "c2_only":
                # Only scale c2 and lambda2 (indices 2, 3)
                scheduled_gains[2] = self.robust_gains[2] * scale  # c2
                scheduled_gains[3] = self.robust_gains[3] * scale  # lambda2
                # c1 and lambda1 remain at robust values
                if VERIFICATION_MODE:
                    logger.debug(f"  [c2_only] c1: {scheduled_gains[0]:.4f} (FIXED), c2: {scheduled_gains[2]:.4f} (scale={scale:.2f})")

            return scheduled_gains

        def compute_control(self, state, state_vars, history):
            """Compute control with selective gain scheduling"""
            # Schedule gains
            scheduled_gains = self._schedule_gains(state)

            # Update controller gains temporarily
            original_gains = self.controller._gains if hasattr(self.controller, '_gains') else None
            self.controller._gains = scheduled_gains

            # Compute control
            output = self.controller.compute_control(state, state_vars, history)

            # Restore original gains if needed
            if original_gains is not None:
                self.controller._gains = original_gains

            return output

        def initialize_state(self):
            if hasattr(self.controller, 'initialize_state'):
                return self.controller.initialize_state()
            return None

        def initialize_history(self):
            if hasattr(self.controller, 'initialize_history'):
                return self.controller.initialize_history()
            return None

        def cleanup(self):
            if hasattr(self.controller, 'cleanup'):
                self.controller.cleanup()

    return SelectiveScheduler(base_controller, mode, robust_gains)


def run_monte_carlo_condition(
    config,
    dynamics: DIPDynamics,
    robust_gains: List[float],
    mode: str,
    num_trials: int,
    ic_range: float = 0.05,
    seed: int = 42
) -> List[Dict]:
    """
    Run Monte Carlo trials for a single scheduling condition.

    Args:
        config: Configuration object
        dynamics: DIP dynamics model
        robust_gains: [c1, c2, lambda1, lambda2]
        mode: "none", "c1_only", "c2_only", "full"
        num_trials: Number of trials to run
        ic_range: Initial condition range (+-rad)
        seed: Random seed

    Returns:
        List of trial results
    """
    np.random.seed(seed)
    results = []

    logger.info(f"{ASCII_INFO} Running {num_trials} trials for mode={mode}")

    for trial in range(num_trials):
        # Random initial condition (6-element state: x, theta1, theta2, xdot, th1dot, th2dot)
        # Random sign for theta1 and theta2
        theta1_init = np.random.uniform(-ic_range, ic_range)
        theta2_init = np.random.uniform(-ic_range, ic_range)
        ic_variation = np.random.uniform(-0.01, 0.01, size=6)
        initial_state = np.array([0.0, theta1_init, theta2_init, 0.0, 0.0, 0.0]) + ic_variation

        # Create controller
        base_controller = create_controller(
            'hybrid_adaptive_sta_smc',
            config=config,
            gains=robust_gains,
            k1_init=0.2,
            k2_init=0.02
        )

        # Wrap with selective scheduler
        controller = create_selective_scheduler(
            base_controller,
            config,
            mode,
            robust_gains
        )

        # Run trial
        trial_result = run_single_trial_with_variance_logging(
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
        "mean_s_variance",
        "max_s_variance",
        "std_s_variance",
        "chattering",
        "chattering_std",
        "control_effort",
        "mean_s",
        "std_s"
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


def compare_conditions(
    results_dict: Dict[str, List[Dict]]
) -> Dict:
    """
    Compare scheduling conditions statistically.

    Args:
        results_dict: {"none": [...], "c1_only": [...], "c2_only": [...], "full": [...]}

    Returns:
        Statistical comparison results
    """
    metrics = [
        "mean_s_variance",
        "max_s_variance",
        "chattering",
        "chattering_std",
        "control_effort"
    ]

    comparison = {}
    baseline = results_dict["none"]

    for mode in ["c1_only", "c2_only", "full"]:
        test_data = results_dict[mode]
        mode_comparison = {}

        for metric in metrics:
            baseline_values = [r[metric] for r in baseline]
            test_values = [r[metric] for r in test_data]

            # Welch's t-test
            t_stat, p_value = stats.ttest_ind(
                baseline_values,
                test_values,
                equal_var=False
            )

            # Cohen's d
            mean_diff = np.mean(test_values) - np.mean(baseline_values)
            pooled_std = np.sqrt(
                (np.std(baseline_values)**2 + np.std(test_values)**2) / 2
            )
            cohen_d = mean_diff / pooled_std if pooled_std > 0 else 0.0

            # Percent change
            baseline_mean = np.mean(baseline_values)
            test_mean = np.mean(test_values)
            pct_change = ((test_mean - baseline_mean) / baseline_mean * 100) if baseline_mean > 0 else 0.0

            # Variance ratio
            variance_ratio = test_mean / baseline_mean if baseline_mean > 0 else 0.0

            mode_comparison[metric] = {
                "baseline_mean": float(baseline_mean),
                "test_mean": float(test_mean),
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "cohen_d": float(cohen_d),
                "percent_change": float(pct_change),
                "variance_ratio": float(variance_ratio),
                "significant": bool(p_value < 0.05)
            }

        comparison[mode] = mode_comparison

    return comparison


def create_comparison_plots(
    results_dict: Dict[str, List[Dict]],
    comparison: Dict,
    output_dir: Path
):
    """Create comparison plots for all scheduling modes."""

    modes = ["none", "c1_only", "c2_only", "full"]
    mode_labels = {
        "none": "Baseline\n(No Scheduling)",
        "c1_only": "c1 Only\nScheduling",
        "c2_only": "c2 Only\nScheduling",
        "full": "Full\n(c1+c2)"
    }

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle("Phase 3.1: Selective c1/c2 Scheduling Comparison", fontsize=14, fontweight='bold')

    metrics_to_plot = [
        ("mean_s_variance", "|s| Mean Variance", "Variance"),
        ("max_s_variance", "|s| Max Variance", "Variance"),
        ("chattering", "Chattering", "rad/s^2"),
        ("chattering_std", "Chattering Std", "rad/s^2"),
        ("control_effort", "Control Effort", "N"),
        ("mean_s", "Mean |s|", "")
    ]

    for idx, (metric, title, ylabel) in enumerate(metrics_to_plot):
        ax = axes[idx // 3, idx % 3]

        # Extract data
        data_to_plot = []
        labels_to_plot = []
        colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']  # green, blue, orange, red

        for mode in modes:
            values = [r[metric] for r in results_dict[mode]]
            data_to_plot.append(values)
            labels_to_plot.append(mode_labels[mode])

        # Box plot
        bp = ax.boxplot(data_to_plot, labels=labels_to_plot, patch_artist=True)

        # Color boxes
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)

        # Add significance markers
        if idx < 5:  # Only for metrics in comparison
            baseline_mean = np.mean(data_to_plot[0])
            for i, mode in enumerate(["c1_only", "c2_only", "full"]):
                if mode in comparison and metric in comparison[mode]:
                    stats_result = comparison[mode][metric]
                    if stats_result['significant']:
                        # Add asterisk for significance
                        test_mean = stats_result['test_mean']
                        y_pos = max(test_mean, baseline_mean) * 1.1
                        ax.text(i+2, y_pos, '*' if stats_result['p_value'] < 0.05 else '**',
                               ha='center', fontsize=16, color='red')

        ax.set_title(title, fontweight='bold')
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', labelsize=8)

    plt.tight_layout()

    # Save plot
    output_path = output_dir / "phase3_1_selective_scheduling_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logger.info(f"{ASCII_OK} Saved comparison plot: {output_path}")
    plt.close()

    # Create variance ratio bar plot
    fig, ax = plt.subplots(figsize=(10, 6))

    modes_test = ["c1_only", "c2_only", "full"]
    variance_ratios = [comparison[mode]["mean_s_variance"]["variance_ratio"] for mode in modes_test]
    colors_test = ['#3498db', '#f39c12', '#e74c3c']

    bars = ax.bar(range(len(modes_test)), variance_ratios, color=colors_test, alpha=0.7, edgecolor='black')
    ax.axhline(y=1.0, color='green', linestyle='--', linewidth=2, label='Baseline (No Scheduling)')

    # Add value labels on bars
    for i, (bar, ratio) in enumerate(zip(bars, variance_ratios)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{ratio:.2f}x',
               ha='center', va='bottom', fontweight='bold', fontsize=11)

    ax.set_xticks(range(len(modes_test)))
    ax.set_xticklabels([mode_labels[m] for m in modes_test])
    ax.set_ylabel("|s| Variance Ratio vs Baseline", fontsize=12, fontweight='bold')
    ax.set_title("Phase 3.1: Variance Increase by Scheduling Mode", fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_path = output_dir / "phase3_1_variance_ratio_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logger.info(f"{ASCII_OK} Saved variance ratio plot: {output_path}")
    plt.close()


def main():
    global VERIFICATION_MODE  # Allow modifying global verification flag

    parser = argparse.ArgumentParser(description="Phase 3.1: Selective c1/c2 Scheduling Testing")
    parser.add_argument("--trials", type=int, default=25,
                       help="Number of trials per condition (default: 25)")
    parser.add_argument("--quick", action="store_true",
                       help="Quick test with 10 trials per condition")
    parser.add_argument("--verify", action="store_true",
                       help="Enable verification mode with detailed DEBUG logging")
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed (default: 42)")

    args = parser.parse_args()

    # Enable verification mode if requested
    if args.verify:
        VERIFICATION_MODE = True
        logger.setLevel(logging.DEBUG)
        logger.info(f"{ASCII_INFO} Verification mode ENABLED - detailed logging active")

    if args.quick:
        num_trials = 10
        logger.info(f"{ASCII_INFO} Running quick test with {num_trials} trials per condition")
    else:
        num_trials = args.trials

    # Load configuration
    config = load_config("config.yaml")

    # Create dynamics
    dynamics = DIPDynamics(config.physics)

    # MT-8 robust PSO gains (from Phase 2.3)
    robust_gains = [10.149, 12.839, 6.815, 2.750]

    # Output directory
    output_dir = Path("benchmarks/research/phase3_1")
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 70)
    logger.info("Phase 3.1: Selective c1/c2 Scheduling Strategy Testing")
    logger.info("=" * 70)
    logger.info(f"{ASCII_INFO} Configuration:")
    logger.info(f"  - Trials per condition: {num_trials}")
    logger.info(f"  - Total trials: {num_trials * 4}")
    logger.info(f"  - IC range: +-0.05 rad")
    logger.info(f"  - Robust gains: {robust_gains}")
    logger.info(f"  - Random seed: {args.seed}")

    # Run all conditions
    modes = ["none", "c1_only", "c2_only", "full"]
    results_dict = {}

    for mode in modes:
        logger.info(f"\n{ASCII_INFO} Testing mode: {mode}")
        results = run_monte_carlo_condition(
            config,
            dynamics,
            robust_gains,
            mode,
            num_trials,
            ic_range=0.05,
            seed=args.seed
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
        logger.info(f"  Control Effort: {aggregated[mode]['control_effort']['mean']:.2f} +- {aggregated[mode]['control_effort']['std']:.2f} N")

    logger.info("\n" + "=" * 70)
    logger.info("COMPARISON VS BASELINE (none)")
    logger.info("=" * 70)

    for mode in ["c1_only", "c2_only", "full"]:
        logger.info(f"\n{mode.upper()}:")
        var_stats = comparison[mode]["mean_s_variance"]
        chatter_stats = comparison[mode]["chattering"]

        logger.info(f"  |s| Variance: {var_stats['variance_ratio']:.2f}x ({var_stats['percent_change']:+.1f}%)")
        logger.info(f"    p={var_stats['p_value']:.4f}, d={var_stats['cohen_d']:.2f}")
        logger.info(f"  Chattering: {chatter_stats['variance_ratio']:.2f}x ({chatter_stats['percent_change']:+.1f}%)")
        logger.info(f"    p={chatter_stats['p_value']:.4f}, d={chatter_stats['cohen_d']:.2f}")

    # Save results
    output_data = {
        "test_parameters": {
            "trials_per_condition": num_trials,
            "total_trials": num_trials * 4,
            "ic_range": 0.05,
            "robust_gains": robust_gains,
            "random_seed": args.seed,
            "modes_tested": modes
        },
        "aggregated_results": aggregated,
        "statistical_comparison": comparison
    }

    output_json = output_dir / "phase3_1_selective_scheduling_report.json"
    with open(output_json, 'w') as f:
        json.dump(output_data, f, indent=2)
    logger.info(f"\n{ASCII_OK} Saved results: {output_json}")

    # Create plots
    logger.info(f"{ASCII_INFO} Creating comparison plots...")
    create_comparison_plots(results_dict, comparison, output_dir)

    logger.info(f"\n{ASCII_OK} Phase 3.1 testing complete!")
    logger.info(f"{ASCII_INFO} Results saved to: {output_dir}")


if __name__ == "__main__":
    main()
