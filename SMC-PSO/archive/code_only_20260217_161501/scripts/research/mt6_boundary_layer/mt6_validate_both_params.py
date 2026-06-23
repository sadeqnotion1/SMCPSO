"""
MT-6 Parameter Set Validation Script

Compares both reported parameter sets side-by-side with corrected unbiased metrics:
- Set A (CORRECTED): epsilon_min=0.0135, alpha=0.171 (claimed 352% worse)
- Set B (COMPLETE): epsilon_min=0.0025, alpha=1.21 (claimed 66.5% better)

Uses frequency-domain method only (unbiased against adaptive boundary layers).
"""

import numpy as np
import json
from pathlib import Path
from typing import Dict, Tuple
from dataclasses import dataclass

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.dynamics import DIPDynamics
from src.controllers.factory import create_controller
from src.controllers.smc.algorithms.classical.boundary_layer import BoundaryLayer
from src.core.simulation_runner import run_simulation
from src.config import load_config


@dataclass
class ValidationResult:
    """Results from validation run."""
    epsilon_min: float
    alpha: float
    chattering_freq: float      # Frequency-domain (unbiased)
    chattering_zero: float      # Zero-crossing rate (unbiased)
    chattering_legacy: float    # Combined legacy (biased) for comparison
    settling_time: float
    overshoot: float
    control_energy: float
    rms_control: float


def run_single_validation(
    epsilon_min: float,
    alpha: float,
    gains: list,
    n_runs: int = 100,
    seed: int = 42
) -> Tuple[ValidationResult, Dict]:
    """Run validation for one parameter set."""

    np.random.seed(seed)

    # Storage for metrics
    chatter_freq_list = []
    chatter_zero_list = []
    chatter_legacy_list = []
    settling_list = []
    overshoot_list = []
    energy_list = []
    rms_list = []

    # Load config once for all runs
    project_root = Path(__file__).resolve().parent.parent
    config = load_config(project_root / "config.yaml")
    dynamics = DIPDynamics(config.physics)

    for run_idx in range(n_runs):
        # Varied initial conditions
        theta1_init = np.random.uniform(-0.1, 0.1)
        theta2_init = np.random.uniform(-0.1, 0.1)
        initial_state = np.array([0.0, theta1_init, theta2_init, 0.0, 0.0, 0.0])

        # Create controller with adaptive boundary layer parameters
        from src.controllers.smc.classic_smc import ClassicalSMC
        controller = ClassicalSMC(
            gains=gains,
            max_force=150.0,
            boundary_layer=epsilon_min,         # Base thickness
            boundary_layer_slope=alpha,         # Adaptive slope
            switch_method="tanh"
        )

        # Run simulation
        t, states, controls = run_simulation(
            controller=controller,
            dynamics_model=dynamics,
            sim_time=10.0,
            dt=0.01,
            initial_state=initial_state,
            u_max=150.0
        )

        # Create BoundaryLayer object for chattering metrics
        boundary_layer = BoundaryLayer(
            thickness=epsilon_min,
            slope=alpha,
            switch_method="tanh"
        )

        # Compute chattering with ALL three methods for comparison
        chatter_freq = boundary_layer.get_chattering_index(
            controls, dt=0.01, method="frequency", cutoff_hz=20.0
        )
        chatter_zero = boundary_layer.get_chattering_index(
            controls, dt=0.01, method="zero_crossing"
        )
        chatter_legacy = boundary_layer.get_chattering_index(
            controls, dt=0.01, method="combined_legacy"
        )

        chatter_freq_list.append(chatter_freq)
        chatter_zero_list.append(chatter_zero)
        chatter_legacy_list.append(chatter_legacy)

        # Secondary metrics
        # Settling time (check if |theta1| < 0.05 rad in last 20% of trajectory)
        settling_idx = int(0.8 * len(t))
        settled = np.all(np.abs(states[settling_idx:, 1]) < 0.05)
        settling_time = 10.0 if not settled else t[settling_idx]
        settling_list.append(settling_time)

        # Overshoot (max absolute deviation)
        overshoot = np.max(np.abs(states[:, 1]))
        overshoot_list.append(overshoot)

        # Control energy (integral of u^2)
        dt = 0.01
        energy = np.sum(controls**2) * dt
        energy_list.append(energy)

        # RMS control
        rms = np.sqrt(np.mean(controls**2))
        rms_list.append(rms)

    # Aggregate results
    result = ValidationResult(
        epsilon_min=epsilon_min,
        alpha=alpha,
        chattering_freq=float(np.mean(chatter_freq_list)),
        chattering_zero=float(np.mean(chatter_zero_list)),
        chattering_legacy=float(np.mean(chatter_legacy_list)),
        settling_time=float(np.mean(settling_list)),
        overshoot=float(np.mean(overshoot_list)),
        control_energy=float(np.mean(energy_list)),
        rms_control=float(np.mean(rms_list))
    )

    # Statistical details
    stats = {
        "chattering_freq": {
            "mean": float(np.mean(chatter_freq_list)),
            "std": float(np.std(chatter_freq_list)),
            "ci95": [
                float(np.mean(chatter_freq_list) - 1.96 * np.std(chatter_freq_list) / np.sqrt(n_runs)),
                float(np.mean(chatter_freq_list) + 1.96 * np.std(chatter_freq_list) / np.sqrt(n_runs))
            ]
        },
        "chattering_zero": {
            "mean": float(np.mean(chatter_zero_list)),
            "std": float(np.std(chatter_zero_list))
        },
        "chattering_legacy": {
            "mean": float(np.mean(chatter_legacy_list)),
            "std": float(np.std(chatter_legacy_list))
        }
    }

    return result, stats


def main():
    """Run validation comparison."""

    print("[INFO] MT-6 Parameter Set Validation")
    print("=" * 80)

    # Default gains (same for both sets for fair comparison)
    gains = [5.0, 5.0, 5.0, 0.5, 0.5, 0.5]

    # Set A: From MT6_CORRECTED_ANALYSIS.md (claimed 352% worse with biased metric)
    print("\n[1/2] Validating Set A (CORRECTED_ANALYSIS: epsilon_min=0.0135, alpha=0.171)...")
    result_a, stats_a = run_single_validation(
        epsilon_min=0.0135,
        alpha=0.171,
        gains=gains,
        n_runs=100,
        seed=42
    )

    # Set B: From MT6_COMPLETE_REPORT.md (claimed 66.5% better)
    print("\n[2/2] Validating Set B (COMPLETE_REPORT: epsilon_min=0.0025, alpha=1.21)...")
    result_b, stats_b = run_single_validation(
        epsilon_min=0.0025,
        alpha=1.21,
        gains=gains,
        n_runs=100,
        seed=42
    )

    # Fixed baseline reference (epsilon=0.02, alpha=0.0)
    print("\n[BASELINE] Validating Fixed Boundary Layer (epsilon=0.02, alpha=0.0)...")
    result_fixed, stats_fixed = run_single_validation(
        epsilon_min=0.02,
        alpha=0.0,
        gains=gains,
        n_runs=100,
        seed=42
    )

    # Print comparison
    print("\n" + "=" * 80)
    print("RESULTS COMPARISON")
    print("=" * 80)

    print(f"\n{'Metric':<30} {'Fixed (Baseline)':<20} {'Set A (0.0135/0.171)':<20} {'Set B (0.0025/1.21)':<20}")
    print("-" * 90)

    # Chattering (frequency-domain, UNBIASED)
    print(f"{'Chattering (freq-domain)':<30} {result_fixed.chattering_freq:<20.6f} {result_a.chattering_freq:<20.6f} {result_b.chattering_freq:<20.6f}")

    # Calculate reduction percentages vs baseline
    reduction_a = (result_fixed.chattering_freq - result_a.chattering_freq) / result_fixed.chattering_freq * 100
    reduction_b = (result_fixed.chattering_freq - result_b.chattering_freq) / result_fixed.chattering_freq * 100

    print(f"{'  Reduction vs Fixed':<30} {'0.0%':<20} {reduction_a:<20.1f}% {reduction_b:<20.1f}%")

    # Chattering (zero-crossing, UNBIASED alternative)
    print(f"{'Chattering (zero-cross Hz)':<30} {result_fixed.chattering_zero:<20.2f} {result_a.chattering_zero:<20.2f} {result_b.chattering_zero:<20.2f}")

    # Chattering (legacy biased method for comparison)
    print(f"{'Chattering (legacy BIASED)':<30} {result_fixed.chattering_legacy:<20.6f} {result_a.chattering_legacy:<20.6f} {result_b.chattering_legacy:<20.6f}")

    # Secondary metrics
    print(f"{'Overshoot (rad)':<30} {result_fixed.overshoot:<20.3f} {result_a.overshoot:<20.3f} {result_b.overshoot:<20.3f}")
    print(f"{'Control Energy (N^2*s)':<30} {result_fixed.control_energy:<20.1f} {result_a.control_energy:<20.1f} {result_b.control_energy:<20.1f}")
    print(f"{'RMS Control (N)':<30} {result_fixed.rms_control:<20.2f} {result_a.rms_control:<20.2f} {result_b.rms_control:<20.2f}")

    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)

    if reduction_b > reduction_a and reduction_b > 30:
        print(f"\n[OK] Set B (0.0025/1.21) WINS: {reduction_b:.1f}% chattering reduction (>30% target)")
        print(f"[WARNING] Set A (0.0135/0.171) achieved only {reduction_a:.1f}% reduction")
    elif reduction_a > reduction_b and reduction_a > 30:
        print(f"\n[OK] Set A (0.0135/0.171) WINS: {reduction_a:.1f}% chattering reduction (>30% target)")
        print(f"[WARNING] Set B (0.0025/1.21) achieved only {reduction_b:.1f}% reduction")
    elif reduction_a < 0 and reduction_b < 0:
        print(f"\n[ERROR] BOTH SETS FAILED: Chattering increased instead of decreased")
        print(f"  Set A: {reduction_a:.1f}% (worse)")
        print(f"  Set B: {reduction_b:.1f}% (worse)")
    else:
        print(f"\n[WARNING] Neither set achieved >30% reduction target")
        print(f"  Set A: {reduction_a:.1f}%")
        print(f"  Set B: {reduction_b:.1f}%")

    # Save results
    output_dir = Path(__file__).parent.parent / "benchmarks"
    output_file = output_dir / "MT6_VALIDATION_COMPARISON.json"

    output_data = {
        "fixed_baseline": {
            "params": {"epsilon": 0.02, "alpha": 0.0},
            "results": result_fixed.__dict__,
            "stats": stats_fixed
        },
        "set_a_corrected": {
            "params": {"epsilon_min": 0.0135, "alpha": 0.171},
            "results": result_a.__dict__,
            "stats": stats_a,
            "reduction_pct": reduction_a
        },
        "set_b_complete": {
            "params": {"epsilon_min": 0.0025, "alpha": 1.21},
            "results": result_b.__dict__,
            "stats": stats_b,
            "reduction_pct": reduction_b
        },
        "gains_used": gains,
        "n_runs": 100,
        "seed": 42,
        "notes": "Uses frequency-domain chattering metric (unbiased) with cutoff=20Hz"
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n[INFO] Results saved to: {output_file}")


if __name__ == "__main__":
    main()
