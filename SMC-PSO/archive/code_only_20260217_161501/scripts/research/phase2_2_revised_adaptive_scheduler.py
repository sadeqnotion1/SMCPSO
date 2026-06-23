"""
Phase 2.2 Revision: Mode Confusion Hypothesis Testing WITH Adaptive Scheduler

Tests whether rapid scheduler mode switching (at small IC) prevents the Hybrid
controller's k1/k2 from adapting properly, whereas slow mode switching (at large IC)
allows stable adaptation.

REVISION: This version enables the AdaptiveGainScheduler to test actual dynamic
gain modulation, not just inferred mode switching.

Hypothesis:
    Small IC (+-0.05 rad) causes rapid scheduler mode switching (10-50 Hz) near the
    0.1 rad threshold, preventing k1/k2 from tracking effectively (gamma1=0.5 is too slow).
    Large IC (+-0.30 rad) causes stable conservative mode (1-5 Hz switching), allowing
    k1/k2 to adapt consistently.

Test Design:
    - Small IC: +-0.05 rad (25 trials)
    - Large IC: +-0.30 rad (25 trials)
    - Controller: Hybrid Adaptive STA SMC WRAPPED with AdaptiveGainScheduler
    - Scheduler Config: Thresholds 0.1/0.2 rad, 50% conservative scaling
    - Logging: ACTUAL mode switches, k1(t), k2(t), |theta|(t), |s|(t) at 100Hz
    - Metrics: Mode switch frequency, k1/k2 adaptation rate, correlation

Expected Results:
    1. Small IC: 10-50 mode switches/second → k1/k2 stagnation → +217% chattering
    2. Large IC: 1-5 mode switches/second → k1/k2 stable adaptation → +24% chattering
    3. Strong negative correlation: mode switch freq vs k1/k2 adaptation rate
    4. Validates chattering degradation trend from Phase 1.3

Usage:
    python scripts/research/phase2_2_revised_adaptive_scheduler.py
    python scripts/research/phase2_2_revised_adaptive_scheduler.py --trials 50
    python scripts/research/phase2_2_revised_adaptive_scheduler.py --quick  # 5 trials for testing
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


def run_single_trial_with_scheduler_logging(
    scheduler: AdaptiveGainScheduler,
    dynamics: DIPDynamics,
    initial_state: np.ndarray,
    duration: float = 5.0,
    dt: float = 0.01
) -> Dict:
    """
    Run a single simulation trial with scheduler mode and adaptation logging.

    Args:
        scheduler: AdaptiveGainScheduler wrapping Hybrid controller
        dynamics: Dynamics model
        initial_state: Initial condition [x, th1, th2, xdot, th1dot, th2dot]
        duration: Simulation duration (seconds)
        dt: Timestep (seconds)

    Returns:
        Dictionary with trajectories and metrics
    """
    steps = int(duration / dt)
    state = initial_state.copy()

    # Trajectory storage
    time_vec = np.zeros(steps)
    states = np.zeros((steps, 6))
    controls = np.zeros(steps)
    k1_trajectory = np.zeros(steps)
    k2_trajectory = np.zeros(steps)
    s_trajectory = np.zeros(steps)
    mode_trajectory = []  # String list of actual scheduler modes
    theta_mag_trajectory = np.zeros(steps)
    scheduled_gains_history = []  # List of gain arrays

    # Initialize
    last_u = 0.0
    state_vars = scheduler.initialize_state()
    history = scheduler.initialize_history()

    # Simulation loop
    for i in range(steps):
        time_vec[i] = i * dt
        states[i] = state

        # BEFORE control computation: log current scheduler mode
        current_mode = scheduler.get_gain_mode_history()
        mode_trajectory.append(current_mode)

        # Compute scheduled gains (this happens inside compute_control, but we want to see it)
        scheduled_gains = scheduler.schedule_gains(state)
        scheduled_gains_history.append(scheduled_gains.copy())

        # Compute control
        try:
            output = scheduler.compute_control(state, state_vars, history)

            # Handle both direct float return and NamedTuple return
            if hasattr(output, 'u'):
                u = output.u
                # Extract k1, k2, s from output
                k1, k2, u_int = output.state
                s = output.sigma
            else:
                u = output
                # Hybrid doesn't return NamedTuple, need to access internal state
                k1 = scheduler.base_controller.k1 if hasattr(scheduler.base_controller, 'k1') else 0.0
                k2 = scheduler.base_controller.k2 if hasattr(scheduler.base_controller, 'k2') else 0.0
                s = scheduler.base_controller.s if hasattr(scheduler.base_controller, 's') else 0.0
        except Exception as e:
            logger.warning(f"Control computation failed at step {i}: {e}")
            u = 0.0
            k1, k2, s = 0.0, 0.0, 0.0

        # Apply saturation
        u = float(np.clip(u, -50.0, 50.0))
        controls[i] = u

        # Log k1/k2
        k1_trajectory[i] = k1
        k2_trajectory[i] = k2

        # Log sliding surface magnitude
        s_trajectory[i] = abs(s)

        # Track theta magnitude
        theta_mag_trajectory[i] = np.sqrt(state[1]**2 + state[2]**2)

        # Step dynamics
        state = dynamics.step(state, u, dt)
        last_u = u

    # Compute chattering (mean absolute jerk)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=RuntimeWarning)
        accel = np.gradient(controls, dt)
        jerk = np.gradient(accel, dt)
        chattering = np.mean(np.abs(jerk))
        if np.isnan(chattering) or np.isinf(chattering):
            chattering = 0.0

    # Compute control effort
    control_effort = np.trapz(np.abs(controls), dx=dt)

    # Analyze mode switching
    mode_metrics = detect_mode_switches(mode_trajectory, dt)

    # Analyze k1/k2 adaptation
    k1_metrics = compute_k_adaptation_rate(k1_trajectory, dt)
    k2_metrics = compute_k_adaptation_rate(k2_trajectory, dt)

    # Analyze scheduled gains variance
    scheduled_gains_array = np.array(scheduled_gains_history)
    c1_variance = np.var(scheduled_gains_array[:, 0])
    lambda1_variance = np.var(scheduled_gains_array[:, 1])

    return {
        "time": time_vec,
        "states": states,
        "controls": controls,
        "k1_trajectory": k1_trajectory,
        "k2_trajectory": k2_trajectory,
        "s_trajectory": s_trajectory,
        "mode_trajectory": mode_trajectory,
        "theta_mag_trajectory": theta_mag_trajectory,
        "scheduled_gains_history": scheduled_gains_array,
        "chattering": chattering,
        "control_effort": control_effort,
        "mean_s": np.mean(s_trajectory),
        "k1_final": k1_trajectory[-1],
        "k2_final": k2_trajectory[-1],
        "mode_metrics": mode_metrics,
        "k1_adaptation": k1_metrics,
        "k2_adaptation": k2_metrics,
        "c1_variance": c1_variance,
        "lambda1_variance": lambda1_variance
    }


def detect_mode_switches(mode_trajectory: List[str], dt: float) -> Dict:
    """
    Analyze scheduler mode switching behavior from ACTUAL mode log.

    Args:
        mode_trajectory: List of mode strings over time ("aggressive", "conservative", etc.)
        dt: Timestep (seconds)

    Returns:
        Dictionary with mode switch metrics
    """
    # Count total switches
    total_switches = 0
    for i in range(1, len(mode_trajectory)):
        if mode_trajectory[i] != mode_trajectory[i-1]:
            total_switches += 1

    # Count time in each mode
    from collections import Counter
    mode_counts = Counter(mode_trajectory)

    # Calculate mode fractions
    total_steps = len(mode_trajectory)
    mode_fractions = {k: v / total_steps for k, v in mode_counts.items()}

    # Calculate switch frequency
    duration = total_steps * dt
    switch_frequency_hz = total_switches / duration if duration > 0 else 0.0

    return {
        "total_switches": total_switches,
        "switch_frequency_hz": switch_frequency_hz,
        "mode_counts": dict(mode_counts),
        "mode_fractions": mode_fractions,
        "dominant_mode": mode_counts.most_common(1)[0][0] if mode_counts else "unknown"
    }


def compute_k_adaptation_rate(k_trajectory: np.ndarray, dt: float = 0.01) -> Dict:
    """
    Compute k1/k2 adaptation rate metrics.

    Args:
        k_trajectory: Array of k values over time [steps]
        dt: Timestep

    Returns:
        Dictionary with adaptation metrics
    """
    # Compute derivative (adaptation rate)
    k_dot = np.gradient(k_trajectory, dt)

    # Metrics
    mean_rate = np.mean(np.abs(k_dot))
    std_rate = np.std(np.abs(k_dot))
    max_rate = np.max(np.abs(k_dot))

    # Detect "freeze" events (adaptation rate < 0.01 threshold)
    freeze_threshold = 0.01
    freeze_events = np.sum(np.abs(k_dot) < freeze_threshold)
    freeze_fraction = freeze_events / len(k_dot)

    return {
        "mean_adaptation_rate": mean_rate,
        "std_adaptation_rate": std_rate,
        "max_adaptation_rate": max_rate,
        "freeze_events": freeze_events,
        "freeze_fraction": freeze_fraction
    }


def run_monte_carlo_phase2_2_revised(
    config,
    ic_small: float = 0.05,
    ic_large: float = 0.30,
    trials_per_condition: int = 25,
    seed: int = 42
) -> Dict:
    """
    Run Phase 2.2 REVISED Monte Carlo trials comparing small IC vs large IC WITH scheduler.

    Args:
        config: Configuration object
        ic_small: Small IC magnitude (rad)
        ic_large: Large IC magnitude (rad)
        trials_per_condition: Number of trials per IC condition
        seed: Random seed

    Returns:
        Dictionary with aggregated results
    """
    logger.info("="*80)
    logger.info(f"{ASCII_INFO} PHASE 2.2 REVISED: MODE CONFUSION WITH ADAPTIVE SCHEDULER")
    logger.info("="*80)
    logger.info(f"{ASCII_INFO} Small IC: +-{ic_small} rad (rapid mode switching expected)")
    logger.info(f"{ASCII_INFO} Large IC: +-{ic_large} rad (stable conservative mode expected)")
    logger.info(f"{ASCII_INFO} Trials per condition: {trials_per_condition}")
    logger.info(f"{ASCII_INFO} Total trials: {trials_per_condition * 2}")
    logger.info(f"{ASCII_INFO} Adaptive scheduler: ENABLED (50% conservative scaling)")
    logger.info("="*80)

    # Initialize dynamics
    dynamics = DIPDynamics(config.physics)

    # MT-8 robust gains for Hybrid Adaptive STA SMC
    mt8_gains = [10.149, 12.839, 6.815, 2.750]  # c1, lambda1, c2, lambda2

    # Scheduler configuration (matching MT-8 thresholds)
    scheduler_config = GainScheduleConfig(
        small_error_threshold=0.1,  # rad
        large_error_threshold=0.2,  # rad
        conservative_scale=0.5,     # 50% gain reduction
        hysteresis_width=0.01,      # 0.01 rad hysteresis
        use_angles_only=True        # Use ||[θ1, θ2]|| for threshold
    )

    # Storage for results
    results = {
        "small_ic": [],
        "large_ic": []
    }

    # Run small IC trials
    logger.info(f"\n{ASCII_INFO} Running small IC trials (+-{ic_small} rad)...")
    for trial in range(trials_per_condition):
        # Create base controller (fresh instance per trial)
        base_controller = create_controller(
            'hybrid_adaptive_sta_smc',
            config=config,
            gains=mt8_gains
        )

        # Wrap with adaptive scheduler
        scheduler = AdaptiveGainScheduler(
            base_controller=base_controller,
            config=scheduler_config
        )

        # Random IC with unique seed
        np.random.seed(seed + trial)
        ic_variation = np.random.uniform(-0.01, 0.01, size=6)
        initial_state = np.array([0.0, ic_small, ic_small, 0.0, 0.0, 0.0]) + ic_variation

        # Run trial
        result = run_single_trial_with_scheduler_logging(
            scheduler, dynamics, initial_state
        )
        results["small_ic"].append(result)

        if (trial + 1) % 5 == 0:
            logger.info(f"{ASCII_OK} Completed {trial + 1}/{trials_per_condition} small IC trials")

    # Run large IC trials
    logger.info(f"\n{ASCII_INFO} Running large IC trials (+-{ic_large} rad)...")
    for trial in range(trials_per_condition):
        # Create base controller (fresh instance per trial)
        base_controller = create_controller(
            'hybrid_adaptive_sta_smc',
            config=config,
            gains=mt8_gains
        )

        # Wrap with adaptive scheduler
        scheduler = AdaptiveGainScheduler(
            base_controller=base_controller,
            config=scheduler_config
        )

        # Random IC with unique seed
        np.random.seed(seed + trials_per_condition + trial)
        ic_variation = np.random.uniform(-0.01, 0.01, size=6)
        initial_state = np.array([0.0, ic_large, ic_large, 0.0, 0.0, 0.0]) + ic_variation

        # Run trial
        result = run_single_trial_with_scheduler_logging(
            scheduler, dynamics, initial_state
        )
        results["large_ic"].append(result)

        if (trial + 1) % 5 == 0:
            logger.info(f"{ASCII_OK} Completed {trial + 1}/{trials_per_condition} large IC trials")

    logger.info(f"\n{ASCII_OK} All trials complete!")
    return results


def aggregate_and_analyze(results: Dict) -> Dict:
    """
    Aggregate results and perform statistical analysis.

    Args:
        results: Dictionary with small_ic and large_ic trial lists

    Returns:
        Dictionary with aggregated metrics and statistics
    """
    logger.info(f"\n{ASCII_INFO} Aggregating results...")

    # Extract metrics for each condition
    small_metrics = {
        "chattering": [r["chattering"] for r in results["small_ic"]],
        "control_effort": [r["control_effort"] for r in results["small_ic"]],
        "mean_s": [r["mean_s"] for r in results["small_ic"]],
        "mode_switch_freq": [r["mode_metrics"]["switch_frequency_hz"] for r in results["small_ic"]],
        "k1_adaptation_rate": [r["k1_adaptation"]["mean_adaptation_rate"] for r in results["small_ic"]],
        "k2_adaptation_rate": [r["k2_adaptation"]["mean_adaptation_rate"] for r in results["small_ic"]],
        "k1_freeze_fraction": [r["k1_adaptation"]["freeze_fraction"] for r in results["small_ic"]],
        "k2_freeze_fraction": [r["k2_adaptation"]["freeze_fraction"] for r in results["small_ic"]],
        "c1_variance": [r["c1_variance"] for r in results["small_ic"]],
        "lambda1_variance": [r["lambda1_variance"] for r in results["small_ic"]],
        "dominant_mode": [r["mode_metrics"]["dominant_mode"] for r in results["small_ic"]]
    }

    large_metrics = {
        "chattering": [r["chattering"] for r in results["large_ic"]],
        "control_effort": [r["control_effort"] for r in results["large_ic"]],
        "mean_s": [r["mean_s"] for r in results["large_ic"]],
        "mode_switch_freq": [r["mode_metrics"]["switch_frequency_hz"] for r in results["large_ic"]],
        "k1_adaptation_rate": [r["k1_adaptation"]["mean_adaptation_rate"] for r in results["large_ic"]],
        "k2_adaptation_rate": [r["k2_adaptation"]["mean_adaptation_rate"] for r in results["large_ic"]],
        "k1_freeze_fraction": [r["k1_adaptation"]["freeze_fraction"] for r in results["large_ic"]],
        "k2_freeze_fraction": [r["k2_adaptation"]["freeze_fraction"] for r in results["large_ic"]],
        "c1_variance": [r["c1_variance"] for r in results["large_ic"]],
        "lambda1_variance": [r["lambda1_variance"] for r in results["large_ic"]],
        "dominant_mode": [r["mode_metrics"]["dominant_mode"] for r in results["large_ic"]]
    }

    # Compute statistics
    summary = {}
    for key in small_metrics:
        if key == "dominant_mode":
            # Mode analysis
            from collections import Counter
            small_mode_counts = Counter(small_metrics[key])
            large_mode_counts = Counter(large_metrics[key])
            summary[key] = {
                "small_ic": small_mode_counts,
                "large_ic": large_mode_counts
            }
        else:
            # Numerical metrics
            small_arr = np.array(small_metrics[key])
            large_arr = np.array(large_metrics[key])

            # Handle NaN/Inf
            small_arr = small_arr[np.isfinite(small_arr)]
            large_arr = large_arr[np.isfinite(large_arr)]

            small_mean = np.mean(small_arr)
            small_std = np.std(small_arr)
            large_mean = np.mean(large_arr)
            large_std = np.std(large_arr)

            # Statistical test
            if len(small_arr) > 0 and len(large_arr) > 0 and small_std > 0 and large_std > 0:
                t_stat, p_value = stats.ttest_ind(small_arr, large_arr, equal_var=False)

                # Cohen's d
                pooled_std = np.sqrt((small_std**2 + large_std**2) / 2)
                cohen_d = (small_mean - large_mean) / pooled_std if pooled_std > 0 else 0.0
            else:
                t_stat, p_value, cohen_d = np.nan, np.nan, np.nan

            summary[key] = {
                "small_ic": {"mean": small_mean, "std": small_std},
                "large_ic": {"mean": large_mean, "std": large_std},
                "t_statistic": t_stat,
                "p_value": p_value,
                "cohen_d": cohen_d,
                "percent_change": ((small_mean - large_mean) / large_mean * 100) if large_mean != 0 else 0.0
            }

    return summary


def print_summary_report(summary: Dict):
    """
    Print human-readable summary report.

    Args:
        summary: Aggregated statistics dictionary
    """
    logger.info("\n" + "="*80)
    logger.info(f"{ASCII_OK} PHASE 2.2 REVISED RESULTS SUMMARY")
    logger.info("="*80)

    # Chattering
    logger.info(f"\n{ASCII_INFO} Chattering (rad/s^2):")
    logger.info(f"  Small IC: {summary['chattering']['small_ic']['mean']:.1f} +- {summary['chattering']['small_ic']['std']:.1f}")
    logger.info(f"  Large IC: {summary['chattering']['large_ic']['mean']:.1f} +- {summary['chattering']['large_ic']['std']:.1f}")
    logger.info(f"  Change: {summary['chattering']['percent_change']:+.1f}% (p={summary['chattering']['p_value']:.3f}, d={summary['chattering']['cohen_d']:.2f})")

    # Mode switching
    logger.info(f"\n{ASCII_INFO} Mode Switch Frequency (Hz):")
    logger.info(f"  Small IC: {summary['mode_switch_freq']['small_ic']['mean']:.2f} +- {summary['mode_switch_freq']['small_ic']['std']:.2f}")
    logger.info(f"  Large IC: {summary['mode_switch_freq']['large_ic']['mean']:.2f} +- {summary['mode_switch_freq']['large_ic']['std']:.2f}")
    if summary['mode_switch_freq']['large_ic']['mean'] > 0:
        logger.info(f"  Ratio: {summary['mode_switch_freq']['small_ic']['mean'] / summary['mode_switch_freq']['large_ic']['mean']:.1f}x faster")
    else:
        logger.info(f"  Ratio: inf (large IC has no switching)")

    # k1 adaptation
    logger.info(f"\n{ASCII_INFO} k1 Adaptation Rate:")
    logger.info(f"  Small IC: {summary['k1_adaptation_rate']['small_ic']['mean']:.4f} +- {summary['k1_adaptation_rate']['small_ic']['std']:.4f}")
    logger.info(f"  Large IC: {summary['k1_adaptation_rate']['large_ic']['mean']:.4f} +- {summary['k1_adaptation_rate']['large_ic']['std']:.4f}")
    logger.info(f"  Change: {summary['k1_adaptation_rate']['percent_change']:+.1f}%")

    # k1 freeze fraction
    logger.info(f"\n{ASCII_INFO} k1 Freeze Fraction:")
    logger.info(f"  Small IC: {summary['k1_freeze_fraction']['small_ic']['mean']:.2%} +- {summary['k1_freeze_fraction']['small_ic']['std']:.2%}")
    logger.info(f"  Large IC: {summary['k1_freeze_fraction']['large_ic']['mean']:.2%} +- {summary['k1_freeze_fraction']['large_ic']['std']:.2%}")

    # c1 variance (gain modulation)
    logger.info(f"\n{ASCII_INFO} c1 Gain Variance (scheduler activity):")
    logger.info(f"  Small IC: {summary['c1_variance']['small_ic']['mean']:.4f} +- {summary['c1_variance']['small_ic']['std']:.4f}")
    logger.info(f"  Large IC: {summary['c1_variance']['large_ic']['mean']:.4f} +- {summary['c1_variance']['large_ic']['std']:.4f}")

    # Dominant mode
    logger.info(f"\n{ASCII_INFO} Dominant Mode Distribution:")
    logger.info(f"  Small IC: {dict(summary['dominant_mode']['small_ic'])}")
    logger.info(f"  Large IC: {dict(summary['dominant_mode']['large_ic'])}")

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
    summary_path = output_dir / "phase2_2_revised_scheduler_report.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2, default=lambda x: str(x))
    logger.info(f"{ASCII_OK} Saved summary report: {summary_path}")

    # Create visualization
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # Plot 1: Mode switch frequency comparison
    ax = axes[0, 0]
    small_freq = [r["mode_metrics"]["switch_frequency_hz"] for r in results["small_ic"]]
    large_freq = [r["mode_metrics"]["switch_frequency_hz"] for r in results["large_ic"]]
    ax.boxplot([small_freq, large_freq], tick_labels=['Small IC\n(0.05 rad)', 'Large IC\n(0.30 rad)'])
    ax.set_ylabel('Mode Switch Frequency (Hz)')
    ax.set_title('Mode Switching: Small vs Large IC')
    ax.grid(True, alpha=0.3)

    # Plot 2: k1 adaptation rate comparison
    ax = axes[0, 1]
    small_k1 = [r["k1_adaptation"]["mean_adaptation_rate"] for r in results["small_ic"]]
    large_k1 = [r["k1_adaptation"]["mean_adaptation_rate"] for r in results["large_ic"]]
    ax.boxplot([small_k1, large_k1], tick_labels=['Small IC', 'Large IC'])
    ax.set_ylabel('k1 Adaptation Rate')
    ax.set_title('k1 Adaptation: Small vs Large IC')
    ax.grid(True, alpha=0.3)

    # Plot 3: k1 freeze fraction comparison
    ax = axes[0, 2]
    small_freeze = [r["k1_adaptation"]["freeze_fraction"] for r in results["small_ic"]]
    large_freeze = [r["k1_adaptation"]["freeze_fraction"] for r in results["large_ic"]]
    ax.boxplot([small_freeze, large_freeze], tick_labels=['Small IC', 'Large IC'])
    ax.set_ylabel('k1 Freeze Fraction')
    ax.set_title('k1 Freeze Events: Small vs Large IC')
    ax.grid(True, alpha=0.3)

    # Plot 4: Chattering comparison
    ax = axes[1, 0]
    small_chat = [r["chattering"] for r in results["small_ic"]]
    large_chat = [r["chattering"] for r in results["large_ic"]]
    ax.boxplot([small_chat, large_chat], tick_labels=['Small IC', 'Large IC'])
    ax.set_ylabel('Chattering (rad/s^2)')
    ax.set_title('Chattering: Small vs Large IC')
    ax.grid(True, alpha=0.3)

    # Plot 5: c1 variance (scheduler activity)
    ax = axes[1, 1]
    small_c1var = [r["c1_variance"] for r in results["small_ic"]]
    large_c1var = [r["c1_variance"] for r in results["large_ic"]]
    ax.boxplot([small_c1var, large_c1var], tick_labels=['Small IC', 'Large IC'])
    ax.set_ylabel('c1 Variance')
    ax.set_title('Scheduler Activity (c1 Modulation)')
    ax.grid(True, alpha=0.3)

    # Plot 6: Control effort
    ax = axes[1, 2]
    small_effort = [r["control_effort"] for r in results["small_ic"]]
    large_effort = [r["control_effort"] for r in results["large_ic"]]
    ax.boxplot([small_effort, large_effort], tick_labels=['Small IC', 'Large IC'])
    ax.set_ylabel('Control Effort')
    ax.set_title('Control Effort: Small vs Large IC')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plot_path = output_dir / "phase2_2_revised_scheduler_comparison.png"
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"{ASCII_OK} Saved plot: {plot_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Phase 2.2 Revised: Mode Confusion with Adaptive Scheduler")
    parser.add_argument('--trials', type=int, default=25, help='Trials per condition (default: 25)')
    parser.add_argument('--quick', action='store_true', help='Quick test with 5 trials per condition')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--output', type=str, default='benchmarks/research/phase2_2_revised', help='Output directory')
    args = parser.parse_args()

    # Determine trial count
    trials_per_condition = 5 if args.quick else args.trials

    # Load config
    config = load_config("config.yaml")

    # Run Monte Carlo
    results = run_monte_carlo_phase2_2_revised(
        config,
        ic_small=0.05,
        ic_large=0.30,
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

    logger.info(f"\n{ASCII_OK} Phase 2.2 REVISED complete!")
    logger.info(f"{ASCII_INFO} Results saved to: {output_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
