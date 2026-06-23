#!/usr/bin/env python3
#======================================================================================\
#================= scripts/benchmarks/run_all_comparisons.py ====================\
#======================================================================================\
"""
Run optimizer comparisons for ALL controllers (Classical, STA, Adaptive, Hybrid).

This script automates running complete benchmarks across all 4 controllers:
1. classical_smc (6 gains)
2. sta_smc (6 gains)
3. adaptive_smc (5 gains)
4. hybrid_adaptive_sta_smc (4 gains)

Each controller is tested with PSO, GA, and DE optimizers.

Usage:
    # Quick test (3 runs per controller)
    python scripts/benchmarks/run_all_comparisons.py --runs 3

    # Publication-quality (50 runs per controller, ~2-3 hours)
    python scripts/benchmarks/run_all_comparisons.py --runs 50 --save-results --plot

    # Custom subset
    python scripts/benchmarks/run_all_comparisons.py --controllers classical_smc hybrid_adaptive_sta_smc --runs 10

Output:
    - Console summary for each controller
    - JSON results files (if --save-results)
    - Convergence plots (if --plot)
    - Combined summary table at the end

Author: Claude Code + AI-assisted development
Date: November 2025
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Dict
import json
import time

# Add project root to path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


# Controller configurations (name, dimension)
CONTROLLERS = {
    'classical_smc': 6,
    'sta_smc': 6,
    'adaptive_smc': 5,
    'hybrid_adaptive_sta_smc': 4,
}


def run_single_controller_benchmark(controller_name: str, dimension: int, n_runs: int,
                                     save_results: bool = False, plot: bool = False) -> Dict:
    """Run benchmark for a single controller.

    Parameters
    ----------
    controller_name : str
        Controller name (e.g., 'classical_smc')
    dimension : int
        Number of gain parameters
    n_runs : int
        Number of independent runs per optimizer
    save_results : bool
        Whether to save JSON results
    plot : bool
        Whether to display plots

    Returns
    -------
    results : Dict
        Benchmark results dictionary
    """
    print(f"\n{'='*80}")
    print(f"RUNNING: {controller_name} ({dimension} gains)")
    print(f"{'='*80}\n")

    # Build command
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "benchmarks" / "compare_optimizers.py"),
        "--controller", controller_name,
        "--dimension", str(dimension),
        "--runs", str(n_runs),
    ]

    if save_results:
        cmd.append("--save-results")
    if plot:
        cmd.append("--plot")

    # Run benchmark
    start_time = time.time()
    try:
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        elapsed = time.time() - start_time

        print(f"\n[OK] {controller_name} completed in {elapsed/60:.1f} minutes")
        return {"status": "success", "elapsed_seconds": elapsed}

    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"\n[ERROR] {controller_name} failed after {elapsed/60:.1f} minutes: {e}")
        return {"status": "failed", "elapsed_seconds": elapsed, "error": str(e)}


def print_summary_table(results: Dict):
    """Print summary table of all benchmarks."""
    print(f"\n\n{'='*80}")
    print("OVERALL SUMMARY: All Controllers")
    print(f"{'='*80}")
    print(f"{'Controller':<30} {'Status':<15} {'Time (min)':<15}")
    print(f"{'-'*80}")

    total_time = 0
    for ctrl_name, result in results.items():
        status = result.get('status', 'unknown')
        elapsed = result.get('elapsed_seconds', 0) / 60.0
        total_time += result.get('elapsed_seconds', 0)

        status_symbol = "[OK]" if status == "success" else "[FAIL]"
        print(f"{ctrl_name:<30} {status_symbol:<15} {elapsed:<15.1f}")

    print(f"{'-'*80}")
    print(f"{'Total Time':<30} {'':<15} {total_time/60:.1f}")
    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(description="Run optimizer comparisons for all controllers")
    parser.add_argument('--runs', type=int, default=10,
                       help='Number of runs per optimizer per controller (default: 10)')
    parser.add_argument('--controllers', nargs='+', default=None,
                       help='Subset of controllers to test (default: all)')
    parser.add_argument('--save-results', action='store_true',
                       help='Save JSON results for each controller')
    parser.add_argument('--plot', action='store_true',
                       help='Display convergence plots for each controller')

    args = parser.parse_args()

    # Determine which controllers to run
    if args.controllers:
        controllers_to_run = {k: v for k, v in CONTROLLERS.items() if k in args.controllers}
        if not controllers_to_run:
            print(f"[ERROR] No valid controllers specified. Available: {list(CONTROLLERS.keys())}")
            return 1
    else:
        controllers_to_run = CONTROLLERS

    print(f"\n{'='*80}")
    print("OPTIMIZER COMPARISON: All Controllers")
    print(f"{'='*80}")
    print(f"Controllers to test: {len(controllers_to_run)}")
    for ctrl, dim in controllers_to_run.items():
        print(f"  - {ctrl} ({dim} gains)")
    print(f"Runs per optimizer: {args.runs}")
    print(f"Total trials: {len(controllers_to_run)} controllers × 3 optimizers × {args.runs} runs = {len(controllers_to_run) * 3 * args.runs}")
    print(f"Estimated time: {len(controllers_to_run) * args.runs * 0.5:.1f} - {len(controllers_to_run) * args.runs * 1.5:.1f} minutes")
    print(f"{'='*80}\n")

    # Run benchmarks
    results = {}
    for ctrl_name, dimension in controllers_to_run.items():
        result = run_single_controller_benchmark(
            ctrl_name, dimension, args.runs,
            save_results=args.save_results,
            plot=args.plot
        )
        results[ctrl_name] = result

    # Print summary
    print_summary_table(results)

    # Check if all succeeded
    all_success = all(r.get('status') == 'success' for r in results.values())
    if all_success:
        print("\n[OK] All benchmarks completed successfully!")
        print(f"\nResults saved to: {REPO_ROOT / 'optimization_results' / 'comparisons'}")
        return 0
    else:
        print("\n[WARNING] Some benchmarks failed. Check logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
