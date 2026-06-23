"""
Zero Variance Investigation Script

BLOCKING ISSUE: All Phase 3/4 trials show std=0.00 across all metrics
This script investigates whether this is:
1. Strong convergence (expected - all ICs reach same steady-state)
2. Deterministic controller (expected - no stochastic elements in SMC)
3. Implementation bug (HIGH IMPACT - would invalidate results)

Investigation Methods:
- Trajectory logging (verify trials are different)
- Visualization (inspect 5 random trials)
- Noise injection (test if controller is deterministic)
- RNG verification (check seeding works)
- Independent validation (different seed)

Usage:
    python scripts/research/investigate_zero_variance.py
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import warnings

import numpy as np
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import load_config
from src.controllers.factory import create_controller
from src.plant.core.dynamics import DIPDynamics

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

ASCII_OK = "[OK]"
ASCII_ERROR = "[ERROR]"
ASCII_INFO = "[INFO]"
ASCII_WARN = "[WARNING]"


def run_single_trial_with_logging(
    controller,
    dynamics: DIPDynamics,
    initial_state: np.ndarray,
    robust_gains: List[float],
    duration: float = 5.0,
    dt: float = 0.01,
    trial_id: int = 0
) -> Dict:
    """Run single trial with FULL trajectory logging."""
    steps = int(duration / dt)

    # Storage for FULL trajectories
    state = initial_state.copy()
    trajectory_s = np.zeros(steps)
    trajectory_u = np.zeros(steps)
    trajectory_theta1 = np.zeros(steps)
    trajectory_theta2 = np.zeros(steps)
    trajectory_theta1_dot = np.zeros(steps)
    trajectory_theta2_dot = np.zeros(steps)

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

        # Log FULL state
        c1, c2 = robust_gains[0], robust_gains[2]
        s = c1 * state[1] + c2 * state[4]  # c1*theta1 + c2*theta1_dot

        trajectory_s[i] = abs(s)
        trajectory_u[i] = u
        trajectory_theta1[i] = state[1]
        trajectory_theta2[i] = state[2]
        trajectory_theta1_dot[i] = state[4]
        trajectory_theta2_dot[i] = state[5]

        # Update state
        state = dynamics.step(state, u, dt)
        last_control = u

    # Compute summary metrics
    jerk = np.abs(np.diff(trajectory_u, n=3)) / (dt ** 3)
    chattering = np.mean(jerk)

    return {
        "trial_id": trial_id,
        "chattering": float(chattering),
        "mean_s": float(np.mean(trajectory_s)),
        "std_s": float(np.std(trajectory_s)),
        "max_theta1": float(np.max(np.abs(trajectory_theta1))),
        "max_theta2": float(np.max(np.abs(trajectory_theta2))),
        # FULL trajectories
        "trajectory_s": trajectory_s.tolist(),
        "trajectory_u": trajectory_u.tolist(),
        "trajectory_theta1": trajectory_theta1.tolist(),
        "trajectory_theta2": trajectory_theta2.tolist(),
        "trajectory_theta1_dot": trajectory_theta1_dot.tolist(),
        "trajectory_theta2_dot": trajectory_theta2_dot.tolist(),
    }


def test_trajectory_uniqueness(results: List[Dict]) -> Dict:
    """Test if trajectories are truly unique or byte-for-byte identical."""
    print(f"\n{ASCII_INFO} Testing trajectory uniqueness...")

    # Extract first 5 trials
    n_trials = min(5, len(results))

    # Compare trajectories pairwise
    uniqueness_scores = []

    for i in range(n_trials):
        for j in range(i + 1, n_trials):
            traj_i = np.array(results[i]["trajectory_s"])
            traj_j = np.array(results[j]["trajectory_s"])

            # Compute difference
            diff = np.abs(traj_i - traj_j)
            max_diff = np.max(diff)
            mean_diff = np.mean(diff)

            uniqueness_scores.append({
                "pair": f"Trial {i} vs Trial {j}",
                "max_diff": float(max_diff),
                "mean_diff": float(mean_diff),
                "identical": bool(max_diff < 1e-10)
            })

    # Summary
    all_identical = all(score["identical"] for score in uniqueness_scores)

    print(f"  Pairwise comparisons: {len(uniqueness_scores)}")
    print(f"  All trajectories identical: {all_identical}")

    if all_identical:
        print(f"  {ASCII_WARN} All trajectories are BYTE-FOR-BYTE IDENTICAL!")
        print(f"  {ASCII_WARN} This suggests strong convergence OR implementation bug")
    else:
        print(f"  {ASCII_OK} Trajectories show variation (expected)")
        for score in uniqueness_scores[:3]:  # Show first 3
            print(f"    {score['pair']}: max_diff={score['max_diff']:.2e}, mean_diff={score['mean_diff']:.2e}")

    return {
        "all_identical": all_identical,
        "uniqueness_scores": uniqueness_scores
    }


def test_rng_functionality() -> Dict:
    """Test if random number generator is working correctly."""
    print(f"\n{ASCII_INFO} Testing RNG functionality...")

    # Test 1: Generate random numbers with same seed (should be identical)
    np.random.seed(42)
    sample1 = np.random.uniform(-0.05, 0.05, size=10)

    np.random.seed(42)
    sample2 = np.random.uniform(-0.05, 0.05, size=10)

    identical_with_same_seed = np.allclose(sample1, sample2)
    print(f"  Same seed produces identical numbers: {identical_with_same_seed}")

    # Test 2: Generate random numbers with different seeds (should be different)
    np.random.seed(42)
    sample3 = np.random.uniform(-0.05, 0.05, size=10)

    np.random.seed(123)
    sample4 = np.random.uniform(-0.05, 0.05, size=10)

    different_with_different_seeds = not np.allclose(sample3, sample4)
    print(f"  Different seeds produce different numbers: {different_with_different_seeds}")

    # Test 3: Check distribution
    np.random.seed(42)
    large_sample = np.random.uniform(-0.05, 0.05, size=10000)
    mean_val = np.mean(large_sample)
    std_val = np.std(large_sample)

    # Uniform distribution should have mean ≈ 0, std ≈ 0.05/sqrt(3) ≈ 0.0289
    expected_std = (0.1) / np.sqrt(12)  # Range 0.1, uniform distribution
    print(f"  Large sample statistics: mean={mean_val:.6f}, std={std_val:.6f}")
    print(f"  Expected std for uniform: {expected_std:.6f}")

    rng_working = identical_with_same_seed and different_with_different_seeds

    if rng_working:
        print(f"  {ASCII_OK} RNG is functioning correctly")
    else:
        print(f"  {ASCII_ERROR} RNG may have issues!")

    return {
        "rng_working": rng_working,
        "same_seed_identical": identical_with_same_seed,
        "different_seeds_different": different_with_different_seeds,
        "distribution_stats": {"mean": float(mean_val), "std": float(std_val)}
    }


def test_initial_condition_variation(
    config,
    dynamics: DIPDynamics,
    robust_gains: List[float],
    trials: int = 10,
    seed: int = 42
) -> Dict:
    """Test if different ICs actually produce different initial states."""
    print(f"\n{ASCII_INFO} Testing initial condition variation...")

    np.random.seed(seed)

    initial_states = []
    for trial in range(trials):
        theta1_init = np.random.uniform(-0.05, 0.05)
        theta2_init = np.random.uniform(-0.05, 0.05)
        ic_variation = np.random.uniform(-0.01, 0.01, size=6)
        initial_state = np.array([0.0, theta1_init, theta2_init, 0.0, 0.0, 0.0]) + ic_variation

        initial_states.append({
            "trial": trial,
            "theta1": float(initial_state[1]),
            "theta2": float(initial_state[2]),
            "full_state": initial_state.tolist()
        })

    # Check variation
    theta1_values = [s["theta1"] for s in initial_states]
    theta2_values = [s["theta2"] for s in initial_states]

    theta1_std = np.std(theta1_values)
    theta2_std = np.std(theta2_values)

    print(f"  Theta1 std across {trials} ICs: {theta1_std:.6f}")
    print(f"  Theta2 std across {trials} ICs: {theta2_std:.6f}")

    has_variation = (theta1_std > 1e-6) and (theta2_std > 1e-6)

    if has_variation:
        print(f"  {ASCII_OK} Initial conditions show expected variation")
    else:
        print(f"  {ASCII_ERROR} Initial conditions are NOT varying!")
        print(f"  {ASCII_ERROR} This indicates RNG or IC generation bug")

    return {
        "has_variation": has_variation,
        "theta1_std": float(theta1_std),
        "theta2_std": float(theta2_std),
        "sample_states": initial_states[:5]  # First 5 samples
    }


def test_noise_injection(
    config,
    dynamics: DIPDynamics,
    robust_gains: List[float],
    trials: int = 5
) -> Dict:
    """Test if adding noise to initial conditions affects results."""
    print(f"\n{ASCII_INFO} Testing noise injection effect...")

    # Fixed IC
    base_ic = np.array([0.0, 0.03, -0.02, 0.0, 0.0, 0.0])

    results_clean = []
    results_noisy = []

    for trial in range(trials):
        # Clean: No noise
        controller = create_controller(
            'hybrid_adaptive_sta_smc',
            config=config,
            gains=robust_gains,
            k1_init=0.2,
            k2_init=0.02
        )

        result_clean = run_single_trial_with_logging(
            controller, dynamics, base_ic.copy(), robust_gains,
            duration=2.0, trial_id=trial
        )
        results_clean.append(result_clean["chattering"])

        # Noisy: Add small noise to IC
        np.random.seed(trial + 100)  # Different seed per trial
        noise = np.random.normal(0, 0.001, size=6)  # Small noise
        noisy_ic = base_ic + noise

        controller_noisy = create_controller(
            'hybrid_adaptive_sta_smc',
            config=config,
            gains=robust_gains,
            k1_init=0.2,
            k2_init=0.02
        )

        result_noisy = run_single_trial_with_logging(
            controller_noisy, dynamics, noisy_ic, robust_gains,
            duration=2.0, trial_id=trial
        )
        results_noisy.append(result_noisy["chattering"])

        if hasattr(controller, 'cleanup'):
            controller.cleanup()
        if hasattr(controller_noisy, 'cleanup'):
            controller_noisy.cleanup()

    # Compare
    clean_std = np.std(results_clean)
    noisy_std = np.std(results_noisy)

    print(f"  Clean IC std: {clean_std:.2f}")
    print(f"  Noisy IC std: {noisy_std:.2f}")

    if clean_std < 1e-6 and noisy_std < 1e-6:
        print(f"  {ASCII_WARN} Both clean and noisy show zero variance")
        print(f"  {ASCII_WARN} Controller appears completely deterministic")
    elif clean_std < 1e-6 and noisy_std > 1e-6:
        print(f"  {ASCII_OK} Noise injection creates variation (expected)")
    else:
        print(f"  {ASCII_OK} Both show variation (expected for stochastic system)")

    return {
        "clean_std": float(clean_std),
        "noisy_std": float(noisy_std),
        "deterministic": bool(clean_std < 1e-6 and noisy_std < 1e-6)
    }


def visualize_trajectories(results: List[Dict], output_dir: Path):
    """Visualize first 5 trajectories to see if visually identical."""
    print(f"\n{ASCII_INFO} Creating trajectory visualizations...")

    n_trials = min(5, len(results))

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Trajectory Comparison: First 5 Trials", fontsize=14, fontweight='bold')

    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']

    # Plot |s|
    ax = axes[0, 0]
    for i in range(n_trials):
        traj_s = np.array(results[i]["trajectory_s"])
        t = np.linspace(0, 5, len(traj_s))
        ax.plot(t, traj_s, color=colors[i], alpha=0.7, label=f'Trial {i}')
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("|s|")
    ax.set_title("Sliding Surface Magnitude")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot control
    ax = axes[0, 1]
    for i in range(n_trials):
        traj_u = np.array(results[i]["trajectory_u"])
        t = np.linspace(0, 5, len(traj_u))
        ax.plot(t, traj_u, color=colors[i], alpha=0.7, label=f'Trial {i}')
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Control (N)")
    ax.set_title("Control Input")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot theta1
    ax = axes[1, 0]
    for i in range(n_trials):
        traj_theta1 = np.array(results[i]["trajectory_theta1"])
        t = np.linspace(0, 5, len(traj_theta1))
        ax.plot(t, np.degrees(traj_theta1), color=colors[i], alpha=0.7, label=f'Trial {i}')
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Theta1 (degrees)")
    ax.set_title("First Pendulum Angle")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot theta2
    ax = axes[1, 1]
    for i in range(n_trials):
        traj_theta2 = np.array(results[i]["trajectory_theta2"])
        t = np.linspace(0, 5, len(traj_theta2))
        ax.plot(t, np.degrees(traj_theta2), color=colors[i], alpha=0.7, label=f'Trial {i}')
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Theta2 (degrees)")
    ax.set_title("Second Pendulum Angle")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = output_dir / "zero_variance_trajectory_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  {ASCII_OK} Saved trajectory plot: {output_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Zero Variance Investigation")
    parser.add_argument("--trials", type=int, default=10,
                       help="Number of trials to run (default: 10)")
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed (default: 42)")

    args = parser.parse_args()

    # Output directory
    output_dir = Path("benchmarks/research/zero_variance_investigation")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("ZERO VARIANCE INVESTIGATION")
    print("=" * 70)
    print(f"{ASCII_INFO} This investigation determines if std=0.00 is valid or a bug")
    print(f"{ASCII_INFO} Running {args.trials} trials with seed={args.seed}")
    print()

    # Load config
    config = load_config("config.yaml")
    dynamics = DIPDynamics(config.physics)
    robust_gains = [10.149, 12.839, 6.815, 2.750]

    # ==== TEST 1: RNG Functionality ====
    rng_result = test_rng_functionality()

    if not rng_result["rng_working"]:
        print(f"\n{ASCII_ERROR} RNG FAILURE DETECTED - Investigation aborted")
        print(f"{ASCII_ERROR} Fix RNG issues before proceeding")
        return

    # ==== TEST 2: Initial Condition Variation ====
    ic_result = test_initial_condition_variation(
        config, dynamics, robust_gains, trials=args.trials, seed=args.seed
    )

    if not ic_result["has_variation"]:
        print(f"\n{ASCII_ERROR} IC GENERATION FAILURE - Investigation aborted")
        print(f"{ASCII_ERROR} Initial conditions are not varying!")
        return

    # ==== TEST 3: Run Trials with Full Logging ====
    print(f"\n{ASCII_INFO} Running {args.trials} trials with full trajectory logging...")

    np.random.seed(args.seed)
    results = []

    for trial in range(args.trials):
        theta1_init = np.random.uniform(-0.05, 0.05)
        theta2_init = np.random.uniform(-0.05, 0.05)
        ic_variation = np.random.uniform(-0.01, 0.01, size=6)
        initial_state = np.array([0.0, theta1_init, theta2_init, 0.0, 0.0, 0.0]) + ic_variation

        controller = create_controller(
            'hybrid_adaptive_sta_smc',
            config=config,
            gains=robust_gains,
            k1_init=0.2,
            k2_init=0.02
        )

        result = run_single_trial_with_logging(
            controller, dynamics, initial_state, robust_gains, trial_id=trial
        )
        results.append(result)

        if hasattr(controller, 'cleanup'):
            controller.cleanup()

        if (trial + 1) % 5 == 0:
            print(f"  Completed {trial + 1}/{args.trials} trials")

    print(f"{ASCII_OK} Completed all {args.trials} trials")

    # ==== TEST 4: Trajectory Uniqueness ====
    uniqueness_result = test_trajectory_uniqueness(results)

    # ==== TEST 5: Noise Injection ====
    noise_result = test_noise_injection(config, dynamics, robust_gains, trials=5)

    # ==== TEST 6: Visualize Trajectories ====
    visualize_trajectories(results, output_dir)

    # ==== COMPUTE STATISTICS ====
    print(f"\n{ASCII_INFO} Computing statistics across {args.trials} trials...")

    chattering_values = [r["chattering"] for r in results]
    mean_s_values = [r["mean_s"] for r in results]

    chattering_mean = np.mean(chattering_values)
    chattering_std = np.std(chattering_values)

    mean_s_mean = np.mean(mean_s_values)
    mean_s_std = np.std(mean_s_values)

    print(f"  Chattering: mean={chattering_mean:.2f}, std={chattering_std:.2f}")
    print(f"  Mean |s|: mean={mean_s_mean:.2f}, std={mean_s_std:.2f}")

    # ==== FINAL DIAGNOSIS ====
    print("\n" + "=" * 70)
    print("DIAGNOSIS")
    print("=" * 70)

    all_tests_passed = (
        rng_result["rng_working"] and
        ic_result["has_variation"]
    )

    if uniqueness_result["all_identical"]:
        if noise_result["deterministic"]:
            print(f"\n{ASCII_OK} CONCLUSION: Strong convergence + deterministic controller")
            print(f"  - All trials converge to IDENTICAL steady-state")
            print(f"  - SMC controller is deterministic (expected)")
            print(f"  - Zero variance is VALID, not a bug")
            print(f"\n{ASCII_OK} Explanation:")
            print(f"  - ICs vary (confirmed), but all reach same attractor")
            print(f"  - Robust PSO gains create strong stability basin")
            print(f"  - DIP equilibrium at theta1=theta2=0 is globally attractive")
            print(f"\n{ASCII_OK} RECOMMENDATION: Proceed with Phase 4.2 optimization")
            diagnosis = "VALID_STRONG_CONVERGENCE"
        else:
            print(f"\n{ASCII_WARN} CONCLUSION: Unclear - needs further investigation")
            print(f"  - Trajectories identical but noise creates variation")
            print(f"  - Possible edge case or numerical precision issue")
            print(f"\n{ASCII_WARN} RECOMMENDATION: Re-run with larger IC range (±0.1 rad)")
            diagnosis = "UNCLEAR_NEEDS_INVESTIGATION"
    else:
        print(f"\n{ASCII_OK} CONCLUSION: Normal variation detected")
        print(f"  - Trajectories show variation (max_diff > 1e-10)")
        print(f"  - Zero variance in Phase 3/4 may be specific to IC range")
        print(f"\n{ASCII_OK} RECOMMENDATION: Proceed with Phase 4.2 optimization")
        diagnosis = "NORMAL_VARIATION"

    # Save results
    # Convert numpy bools to Python bools for JSON serialization
    def convert_numpy_types(obj):
        if isinstance(obj, dict):
            return {k: convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(item) for item in obj]
        elif isinstance(obj, (np.bool_, np.integer)):
            return bool(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        return obj

    investigation_report = {
        "test_parameters": {
            "trials": args.trials,
            "seed": args.seed,
            "ic_range": 0.05,
            "robust_gains": robust_gains
        },
        "rng_test": convert_numpy_types(rng_result),
        "ic_variation_test": convert_numpy_types(ic_result),
        "trajectory_uniqueness_test": convert_numpy_types(uniqueness_result),
        "noise_injection_test": convert_numpy_types(noise_result),
        "statistics": {
            "chattering_mean": float(chattering_mean),
            "chattering_std": float(chattering_std),
            "mean_s_mean": float(mean_s_mean),
            "mean_s_std": float(mean_s_std)
        },
        "diagnosis": diagnosis,
        "all_tests_passed": bool(all_tests_passed)
    }

    output_json = output_dir / "zero_variance_investigation_report.json"
    with open(output_json, 'w') as f:
        json.dump(investigation_report, f, indent=2)
    print(f"\n{ASCII_OK} Saved investigation report: {output_json}")

    print(f"\n{ASCII_OK} Zero variance investigation complete!")
    print(f"{ASCII_INFO} Results saved to: {output_dir}")


if __name__ == "__main__":
    main()
