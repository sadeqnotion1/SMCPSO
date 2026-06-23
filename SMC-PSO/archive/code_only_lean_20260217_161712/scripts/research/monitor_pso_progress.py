"""
Phase 4.2 PSO Optimization Progress Monitor

Monitors the running PSO optimization and reports progress.

Usage:
    python scripts/research/monitor_pso_progress.py

Author: Phase 4.2 Research Team
Created: November 9, 2025
"""

import time
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

ASCII_INFO = "[INFO]"
ASCII_OK = "[OK]"
ASCII_WARN = "[WARNING]"
ASCII_ERROR = "[ERROR]"

# Paths
LOG_FILE = Path(".logs/benchmarks/research/phase4_2/pso_optimization.log")
RESULTS_FILE = Path("benchmarks/research/phase4_2/phase4_2_pso_results.json")
BASELINE_FILE = Path("benchmarks/research/phase4_2/phase4_2_baseline.json")

# Expected configuration
TOTAL_ITERATIONS = 50
TOTAL_PARTICLES = 20


def parse_log_file():
    """
    Parse the PSO optimization log file to extract progress.

    Returns:
        Dictionary with progress metrics
    """
    if not LOG_FILE.exists():
        return {
            "status": "not_started",
            "message": "Log file not found - optimization may not have started yet"
        }

    with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        log_content = f.read()

    # Check if baseline computed
    baseline_computed = "Baseline computed:" in log_content
    pso_started = "Starting PSO optimization" in log_content

    if not baseline_computed:
        return {
            "status": "computing_baseline",
            "message": "Computing baseline metrics (100 trials)..."
        }

    if not pso_started:
        return {
            "status": "baseline_complete",
            "message": "Baseline complete, preparing PSO optimization..."
        }

    # Extract iteration progress from PySwarms progress bar
    # Look for patterns like "pyswarms.single.global_best:   2%|█"
    import re
    progress_pattern = r'pyswarms\.single\.global_best:\s+(\d+)%'
    matches = re.findall(progress_pattern, log_content)

    if matches:
        latest_progress = int(matches[-1])
        current_iteration = int(latest_progress * TOTAL_ITERATIONS / 100)
    else:
        current_iteration = 0

    # Extract best fitness so far from particle evaluation logs
    fitness_pattern = r'Particle \d+/\d+: chattering_ratio=([\d.]+), fitness=([\d.]+)'
    fitness_matches = re.findall(fitness_pattern, log_content)

    best_chattering_ratio = None
    best_fitness = None
    if fitness_matches:
        chattering_ratios = [float(m[0]) for m in fitness_matches]
        fitness_values = [float(m[1]) for m in fitness_matches]
        best_chattering_ratio = min(chattering_ratios)
        best_fitness = min(fitness_values)

    # Estimate completion time
    # Each iteration takes roughly 7-8 minutes (based on 50 iterations in 6 hours)
    minutes_per_iteration = 360 / TOTAL_ITERATIONS  # 6 hours = 360 minutes
    remaining_iterations = TOTAL_ITERATIONS - current_iteration
    estimated_minutes_remaining = remaining_iterations * minutes_per_iteration

    return {
        "status": "running",
        "current_iteration": current_iteration,
        "total_iterations": TOTAL_ITERATIONS,
        "progress_percent": latest_progress if matches else 0,
        "best_chattering_ratio": best_chattering_ratio,
        "best_fitness": best_fitness,
        "estimated_minutes_remaining": int(estimated_minutes_remaining),
        "particles_evaluated": len(fitness_matches)
    }


def check_completion():
    """
    Check if optimization has completed and results are available.

    Returns:
        Boolean indicating completion status
    """
    if not RESULTS_FILE.exists():
        return False

    try:
        with open(RESULTS_FILE, 'r') as f:
            results = json.load(f)

        # Check if results contain optimized parameters
        if "optimal_parameters" in results and "best_cost" in results:
            return True
    except (json.JSONDecodeError, KeyError):
        return False

    return False


def print_status():
    """Print current optimization status."""
    print("=" * 80)
    print("Phase 4.2 PSO Threshold Optimization - Progress Monitor")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check if completed
    if check_completion():
        print(f"{ASCII_OK} OPTIMIZATION COMPLETE!")
        print()
        with open(RESULTS_FILE, 'r') as f:
            results = json.load(f)

        print("Final Results:")
        print(f"  Best Cost: {results['best_cost']:.4f}")
        print(f"  Optimal Parameters:")
        opt_params = results['optimal_parameters']
        print(f"    s_small: {opt_params['s_small']:.4f}")
        print(f"    s_large: {opt_params['s_large']:.4f}")
        print(f"    scale_aggressive: {opt_params['scale_aggressive']:.4f}")
        print(f"    scale_conservative: {opt_params['scale_conservative']:.4f}")
        print()
        print(f"{ASCII_INFO} Results saved to: {RESULTS_FILE}")
        return

    # Parse log for progress
    status = parse_log_file()

    if status["status"] == "not_started":
        print(f"{ASCII_INFO} {status['message']}")
    elif status["status"] == "computing_baseline":
        print(f"{ASCII_INFO} {status['message']}")
    elif status["status"] == "baseline_complete":
        print(f"{ASCII_OK} {status['message']}")
    elif status["status"] == "running":
        print(f"{ASCII_INFO} PSO Optimization In Progress")
        print()
        print(f"Progress: {status['current_iteration']}/{status['total_iterations']} iterations ({status['progress_percent']}%)")
        print(f"Particles Evaluated: {status['particles_evaluated']}")
        print()
        if status['best_chattering_ratio'] is not None:
            print("Current Best Results:")
            print(f"  Chattering Ratio: {status['best_chattering_ratio']:.3f} ({(1-status['best_chattering_ratio'])*100:+.1f}%)")
            print(f"  Best Fitness: {status['best_fitness']:.4f}")
            print()
        print(f"Estimated Time Remaining: {status['estimated_minutes_remaining']} minutes ({status['estimated_minutes_remaining']//60}h {status['estimated_minutes_remaining']%60}m)")
        eta = datetime.now() + timedelta(minutes=status['estimated_minutes_remaining'])
        print(f"Estimated Completion: {eta.strftime('%Y-%m-%d %H:%M:%S')}")

    print()
    print("=" * 80)


def continuous_monitor(interval_minutes=10):
    """
    Continuously monitor optimization progress.

    Args:
        interval_minutes: Minutes between status updates
    """
    print(f"{ASCII_INFO} Starting continuous monitoring (updates every {interval_minutes} minutes)")
    print(f"{ASCII_INFO} Press Ctrl+C to stop monitoring")
    print()

    try:
        while True:
            print_status()

            if check_completion():
                print(f"{ASCII_OK} Optimization complete! Monitoring stopped.")
                break

            print(f"\n{ASCII_INFO} Next update in {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)

    except KeyboardInterrupt:
        print(f"\n{ASCII_WARN} Monitoring stopped by user")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Monitor Phase 4.2 PSO optimization progress")
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Continuously monitor with periodic updates'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Minutes between updates in continuous mode (default: 10)'
    )

    args = parser.parse_args()

    if args.continuous:
        continuous_monitor(interval_minutes=args.interval)
    else:
        print_status()
