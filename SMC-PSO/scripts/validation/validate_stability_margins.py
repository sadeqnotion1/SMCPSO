#!/usr/bin/env python3
"""
Lyapunov Function Validation Script

Loads simulation results and computes:
1. V(t) for each controller
2. dV/dt numerically
3. Verifies V̇ < 0 (or ISS bound)
4. Plots Lyapunov function evolution

Usage:
    python scripts/validate_stability_margins.py --controller classical_smc --csv benchmarks/results.csv
    python scripts/validate_stability_margins.py --controller adaptive_smc --csv benchmarks/MT6_adaptive_validation.csv
    python scripts/validate_stability_margins.py --all  # Validate all available benchmarks

Author: Agent 2 (Implementation Validator)
Date: 2025-10-18
Reference: docs/theory/lyapunov_stability_proofs.md, .artifacts/lt4_validation_report_FINAL.md
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate Lyapunov stability margins from simulation data"
    )
    parser.add_argument(
        "--controller",
        type=str,
        choices=["classical_smc", "sta_smc", "adaptive_smc", "hybrid_adaptive_sta_smc", "swing_up_smc"],
        help="Controller type",
    )
    parser.add_argument(
        "--csv",
        type=str,
        help="Path to simulation results CSV",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all available benchmarks in benchmarks/ directory",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        default=True,
        help="Generate Lyapunov evolution plots (default: True)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.95,
        help="Fraction of time V̇ < 0 required for validation (default: 0.95 = 95%%)",
    )
    return parser.parse_args()


def load_simulation_data(csv_path: str) -> pd.DataFrame:
    """Load simulation results from CSV.

    Expected columns (vary by controller):
    - time, x, theta1, theta2, x_dot, theta1_dot, theta2_dot
    - u (control input)
    - sigma (sliding surface) or s
    - K (adaptive gain, for adaptive/hybrid controllers)
    - z (integral state, for STA/hybrid controllers)
    """
    df = pd.DataFrame(pd.read_csv(csv_path))
    print(f"Loaded {len(df)} timesteps from {csv_path}")
    print(f"Columns: {list(df.columns)}")
    return df


def compute_lyapunov_classical(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """Compute V(t) = 0.5 * s^2 for Classical SMC.

    Args:
        df: DataFrame with 'sigma' or 's' column (sliding surface)

    Returns:
        V: Lyapunov function values V(t)
        dV_dt: Time derivative dV/dt
    """
    # Extract sliding surface (try 'sigma' then 's')
    if 'sigma' in df.columns:
        s = df['sigma'].values
    elif 's' in df.columns:
        s = df['s'].values
    else:
        raise ValueError("No sliding surface column found ('sigma' or 's')")

    # Compute V(t) = 0.5 * s^2
    V = 0.5 * s**2

    # Compute dV/dt ≈ (V[i+1] - V[i]) / dt
    dt = df['time'].diff().mean()  # Average timestep
    dV_dt = np.diff(V) / dt
    dV_dt = np.append(dV_dt, dV_dt[-1])  # Pad to match length

    return V, dV_dt


def compute_lyapunov_sta(df: pd.DataFrame, K2: float = 4.0) -> Tuple[np.ndarray, np.ndarray]:
    """Compute V(t) = |s| + (1/(2*K2)) * z^2 for STA SMC.

    Args:
        df: DataFrame with 'sigma' (or 's') and 'z' columns
        K2: Algorithmic gain K2 (from config, default 4.0)

    Returns:
        V: Lyapunov function values V(t)
        dV_dt: Time derivative dV/dt
    """
    # Extract sliding surface and integral state
    if 'sigma' in df.columns:
        s = df['sigma'].values
    elif 's' in df.columns:
        s = df['s'].values
    else:
        raise ValueError("No sliding surface column found")

    if 'z' not in df.columns:
        raise ValueError("No integral state column 'z' found for STA controller")

    z = df['z'].values

    # Compute V(t) = |s| + (1/(2*K2)) * z^2
    V = np.abs(s) + (1.0 / (2.0 * K2)) * z**2

    # Compute dV/dt
    dt = df['time'].diff().mean()
    dV_dt = np.diff(V) / dt
    dV_dt = np.append(dV_dt, dV_dt[-1])

    return V, dV_dt


def compute_lyapunov_adaptive(df: pd.DataFrame, gamma: float = 10.0) -> Tuple[np.ndarray, np.ndarray]:
    """Compute V(t) = 0.5*s^2 + (1/(2*gamma))*(K - K*)^2 for Adaptive SMC.

    Args:
        df: DataFrame with 'sigma' (or 's') and 'K' columns
        gamma: Adaptation rate (from config, default 10.0)

    Returns:
        V: Lyapunov function values V(t)
        dV_dt: Time derivative dV/dt
    """
    # Extract sliding surface and adaptive gain
    if 'sigma' in df.columns:
        s = df['sigma'].values
    elif 's' in df.columns:
        s = df['s'].values
    else:
        raise ValueError("No sliding surface column found")

    if 'K' not in df.columns:
        raise ValueError("No adaptive gain column 'K' found")

    K = df['K'].values

    # Estimate K* as the converged value (last 10% of simulation)
    K_star = np.mean(K[int(0.9 * len(K)):])
    K_tilde = K - K_star

    # Compute composite Lyapunov V(t) = 0.5*s^2 + (1/(2*gamma))*(K - K*)^2
    V = 0.5 * s**2 + (1.0 / (2.0 * gamma)) * K_tilde**2

    # Compute dV/dt
    dt = df['time'].diff().mean()
    dV_dt = np.diff(V) / dt
    dV_dt = np.append(dV_dt, dV_dt[-1])

    return V, dV_dt


def compute_lyapunov_hybrid(df: pd.DataFrame, gamma1: float = 2.0, gamma2: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
    """Compute V(t) for Hybrid Adaptive STA-SMC (ISS framework).

    Args:
        df: DataFrame with 's', 'k1', 'k2', 'u_int' columns
        gamma1, gamma2: Adaptation rates

    Returns:
        V: Lyapunov function values V(t)
        dV_dt: Time derivative dV/dt
    """
    # Extract states
    if 'sigma' in df.columns:
        s = df['sigma'].values
    elif 's' in df.columns:
        s = df['s'].values
    else:
        raise ValueError("No sliding surface column found")

    if 'k1' not in df.columns or 'k2' not in df.columns:
        raise ValueError("No adaptive gains 'k1', 'k2' found")

    k1 = df['k1'].values
    k2 = df['k2'].values

    # u_int may be named differently
    if 'u_int' in df.columns:
        u_int = df['u_int'].values
    elif 'u_integral' in df.columns:
        u_int = df['u_integral'].values
    else:
        # If not available, approximate as zero (degrades validation)
        print("WARNING: No integral state 'u_int' found, using 0.0")
        u_int = np.zeros_like(s)

    # Estimate ideal gains (converged values)
    k1_star = np.mean(k1[int(0.9 * len(k1)):])
    k2_star = np.mean(k2[int(0.9 * len(k2)):])
    k1_tilde = k1 - k1_star
    k2_tilde = k2 - k2_star

    # Compute composite Lyapunov
    V = 0.5 * s**2 + (1.0 / (2.0 * gamma1)) * k1_tilde**2 + (1.0 / (2.0 * gamma2)) * k2_tilde**2 + 0.5 * u_int**2

    # Compute dV/dt
    dt = df['time'].diff().mean()
    dV_dt = np.diff(V) / dt
    dV_dt = np.append(dV_dt, dV_dt[-1])

    return V, dV_dt


def compute_lyapunov_swingup(df: pd.DataFrame, mode_col: str = 'mode') -> Tuple[np.ndarray, np.ndarray]:
    """Compute V(t) for Swing-Up SMC (mode-dependent).

    Args:
        df: DataFrame with 'mode', 'E_total', 'E_bottom', 'sigma' columns
        mode_col: Column name for mode ('swing' or 'stabilize')

    Returns:
        V: Lyapunov function values V(t) (mode-dependent)
        dV_dt: Time derivative dV/dt
    """
    # This is simplified: real implementation would require energy computation
    # For now, delegate to classical SMC when in stabilize mode
    raise NotImplementedError("Swing-Up Lyapunov validation requires energy computation (TODO)")


def validate_lyapunov_decrease(
    V: np.ndarray,
    dV_dt: np.ndarray,
    threshold: float = 0.95,
    transient_time: float = 1.0,
    dt_avg: float = 0.01
) -> Dict:
    """Validate that V̇ < 0 for at least `threshold` fraction of time.

    Args:
        V: Lyapunov function values V(t)
        dV_dt: Time derivative dV/dt
        threshold: Minimum fraction of time with V̇ < 0 (default: 0.95 = 95%)
        transient_time: Ignore first `transient_time` seconds (default: 1.0s)
        dt_avg: Average timestep (default: 0.01s)

    Returns:
        Dictionary with validation results
    """
    # Ignore transient (first transient_time seconds)
    transient_steps = int(transient_time / dt_avg)
    dV_dt_steady = dV_dt[transient_steps:]

    # Count negative derivatives
    negative_count = np.sum(dV_dt_steady < 0)
    total_count = len(dV_dt_steady)
    fraction_negative = negative_count / total_count if total_count > 0 else 0.0

    # Validation result
    passed = fraction_negative >= threshold

    return {
        'passed': passed,
        'fraction_negative': fraction_negative,
        'threshold': threshold,
        'negative_count': negative_count,
        'total_count': total_count,
        'transient_steps_ignored': transient_steps,
        'V_initial': V[0],
        'V_final': V[-1],
        'V_max': np.max(V),
        'mean_dV_dt': np.mean(dV_dt_steady),
    }


def plot_lyapunov_evolution(
    time: np.ndarray,
    V: np.ndarray,
    dV_dt: np.ndarray,
    controller: str,
    validation_result: Dict,
    output_path: Optional[str] = None
):
    """Plot Lyapunov function V(t) and its derivative dV/dt.

    Args:
        time: Time vector
        V: Lyapunov function values
        dV_dt: Time derivative dV/dt
        controller: Controller name (for title)
        validation_result: Dict from validate_lyapunov_decrease()
        output_path: Optional path to save figure
    """
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Plot V(t)
    axes[0].plot(time, V, 'b-', linewidth=1.5, label='V(t)')
    axes[0].axhline(y=validation_result['V_final'], color='r', linestyle='--', alpha=0.5, label=f"V(final) = {validation_result['V_final']:.4f}")
    axes[0].set_ylabel('Lyapunov Function V(t)', fontsize=12)
    axes[0].set_title(f"{controller.upper()} Lyapunov Evolution", fontsize=14, fontweight='bold')
    axes[0].legend(loc='upper right')
    axes[0].grid(True, alpha=0.3)

    # Plot dV/dt
    axes[1].plot(time, dV_dt, 'r-', linewidth=1.0, label='dV/dt', alpha=0.7)
    axes[1].axhline(y=0, color='k', linestyle='-', linewidth=1.5, label='Zero line')
    axes[1].fill_between(time, 0, dV_dt, where=(dV_dt < 0), color='g', alpha=0.3, label='V̇ < 0 (stable)')
    axes[1].fill_between(time, 0, dV_dt, where=(dV_dt >= 0), color='r', alpha=0.3, label='V̇ ≥ 0 (unstable)')
    axes[1].set_xlabel('Time [s]', fontsize=12)
    axes[1].set_ylabel('dV/dt', fontsize=12)
    axes[1].legend(loc='upper right')
    axes[1].grid(True, alpha=0.3)

    # Add validation result text
    result_text = f"Validation: {'PASS' if validation_result['passed'] else 'FAIL'}\n"
    result_text += f"V̇ < 0: {validation_result['fraction_negative']*100:.1f}% (threshold: {validation_result['threshold']*100:.0f}%)"
    axes[1].text(0.05, 0.95, result_text, transform=axes[1].transAxes,
                 fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {output_path}")

    plt.show()


def validate_controller(controller: str, csv_path: str, threshold: float = 0.95, plot: bool = True):
    """Main validation workflow for a single controller.

    Args:
        controller: Controller type
        csv_path: Path to simulation CSV
        threshold: Validation threshold (fraction of time with V̇ < 0)
        plot: Whether to generate plots
    """
    print(f"\n{'='*60}")
    print(f"Validating {controller.upper()}")
    print(f"{'='*60}")

    # Load simulation data
    df = load_simulation_data(csv_path)
    time = df['time'].values
    dt_avg = df['time'].diff().mean()

    # Compute Lyapunov function based on controller type
    if controller == "classical_smc":
        V, dV_dt = compute_lyapunov_classical(df)
    elif controller == "sta_smc":
        V, dV_dt = compute_lyapunov_sta(df, K2=4.0)  # TODO: Extract K2 from config
    elif controller == "adaptive_smc":
        V, dV_dt = compute_lyapunov_adaptive(df, gamma=10.0)  # TODO: Extract gamma from config
    elif controller == "hybrid_adaptive_sta_smc":
        V, dV_dt = compute_lyapunov_hybrid(df, gamma1=2.0, gamma2=0.5)  # TODO: Extract from config
    elif controller == "swing_up_smc":
        V, dV_dt = compute_lyapunov_swingup(df)
    else:
        raise ValueError(f"Unknown controller type: {controller}")

    # Validate V̇ < 0
    validation_result = validate_lyapunov_decrease(V, dV_dt, threshold=threshold, dt_avg=dt_avg)

    # Print validation results
    print(f"\nValidation Results:")
    print(f"  V̇ < 0 for {validation_result['fraction_negative']*100:.1f}% of time (threshold: {threshold*100:.0f}%)")
    print(f"  V(0) = {validation_result['V_initial']:.6f}")
    print(f"  V(final) = {validation_result['V_final']:.6f}")
    print(f"  V(max) = {validation_result['V_max']:.6f}")
    print(f"  Mean(dV/dt) = {validation_result['mean_dV_dt']:.6f}")
    print(f"  Status: {'✅ PASS' if validation_result['passed'] else '❌ FAIL'}")

    # Plot
    if plot:
        output_path = f"benchmarks/{controller}_lyapunov_validation.png"
        plot_lyapunov_evolution(time, V, dV_dt, controller, validation_result, output_path)

    return validation_result


def main():
    args = parse_args()

    if args.all:
        # Auto-detect benchmarks and validate all
        print("Auto-validation mode: Scanning benchmarks/ directory...")
        benchmarks_dir = Path("benchmarks")
        if not benchmarks_dir.exists():
            print("ERROR: benchmarks/ directory not found")
            sys.exit(1)

        # Known mappings (CSV filename → controller type)
        mappings = {
            "classical": "classical_smc",
            "sta": "sta_smc",
            "adaptive": "adaptive_smc",
            "MT6": "adaptive_smc",  # MT6 = Adaptive SMC task
            "hybrid": "hybrid_adaptive_sta_smc",
            "swing": "swing_up_smc",
        }

        csv_files = list(benchmarks_dir.glob("*.csv"))
        print(f"Found {len(csv_files)} CSV files")

        for csv_file in csv_files:
            # Detect controller type from filename
            controller = None
            for key, ctrl in mappings.items():
                if key.lower() in csv_file.stem.lower():
                    controller = ctrl
                    break

            if controller:
                try:
                    validate_controller(controller, str(csv_file), args.threshold, args.plot)
                except Exception as e:
                    print(f"ERROR validating {csv_file.name}: {e}")
            else:
                print(f"Skipping {csv_file.name} (controller type unknown)")

    elif args.controller and args.csv:
        # Single controller validation
        validate_controller(args.controller, args.csv, args.threshold, args.plot)

    else:
        print("ERROR: Must specify --controller and --csv, or use --all")
        sys.exit(1)


if __name__ == "__main__":
    main()
