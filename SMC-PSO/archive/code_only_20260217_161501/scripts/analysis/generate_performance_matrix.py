"""
================================================================================
Performance Matrix Generator
================================================================================

Parse pytest-benchmark JSON results and generate a performance matrix CSV
for controller comparison. This script is part of QW-2 (Week 1) from
ROADMAP_EXISTING_PROJECT.md.

Usage:
    python scripts/generate_performance_matrix.py

Input:
    .benchmark_results.json (from pytest --benchmark-json)

Output:
    benchmarks/baseline_performance.csv (7 controllers × 4+ metrics)

Author: DIP_SMC_PSO Team
Created: October 2025 (Week 1, Task QW-2)
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any
import sys


def load_benchmark_results(json_path: str = ".benchmark_results.json") -> Dict[str, Any]:
    """Load benchmark results from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def extract_controller_metrics(benchmarks: List[Dict]) -> Dict[str, Dict[str, float]]:
    """
    Extract performance metrics for each controller from benchmarks.

    Returns:
        Dict mapping controller_name -> {metric_name: value}

    Metrics extracted:
        - compute_time_ms: Mean time to compute control (milliseconds)
        - throughput_steps_per_s: Simulation throughput (steps/second)
        - convergence_ms: Convergence time (milliseconds)
    """
    # Known controller types (filter out test parameters)
    KNOWN_CONTROLLERS = {
        'classical_smc', 'sta_smc', 'adaptive_smc',
        'hybrid_adaptive_sta_smc', 'swing_up_smc', 'mpc_controller',
        'tsmc_smc', 'ismc_smc'  # Future controllers
    }

    metrics = {}

    for bench in benchmarks:
        name = bench.get('name', '')
        params = bench.get('params') or {}  # Handle None
        stats = bench.get('stats', {})

        # Extract controller name from parameters or test name
        ctrl_name = params.get('ctrl_name') or params.get('controller')
        if not ctrl_name:
            # Try to extract from test name: test_xxx[controller_name]
            if '[' in name and ']' in name:
                ctrl_name = name.split('[')[1].split(']')[0]

        # Filter: only keep known controller names
        if not ctrl_name or ctrl_name not in KNOWN_CONTROLLERS:
            continue  # Skip if not a recognized controller

        # Initialize controller entry
        if ctrl_name not in metrics:
            metrics[ctrl_name] = {}

        # Extract metrics based on test type
        mean_time = stats.get('mean', 0)  # Benchmark time (varies by unit)

        # Controller compute speed
        # pytest-benchmark reports in microseconds for fast operations
        if 'compute_speed' in name or 'control_computation' in name:
            # Mean is in microseconds, convert to milliseconds
            metrics[ctrl_name]['compute_time_us'] = mean_time
            metrics[ctrl_name]['compute_time_ms'] = mean_time / 1000.0

        # Simulation throughput (calculate from time)
        if 'throughput' in name and ctrl_name in name:
            # Mean is typically in milliseconds for simulations
            if mean_time > 0:
                # Assume benchmark runs full simulation (1000 steps, 10s)
                sim_time_s = mean_time / 1000.0  # Convert ms to seconds
                steps = 1000
                throughput = steps / sim_time_s if sim_time_s > 0 else 0
                metrics[ctrl_name]['throughput_steps_per_s'] = throughput

        # Convergence time (milliseconds)
        if 'convergence' in name and ctrl_name in name:
            # Mean is in milliseconds for convergence tests
            metrics[ctrl_name]['convergence_ms'] = mean_time

    return metrics


def calculate_derived_metrics(metrics: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """
    Calculate additional derived metrics from raw benchmark data.

    Adds:
        - control_effort_estimate: Relative control effort (dimensionless)
    """
    for ctrl_name, ctrl_metrics in metrics.items():
        # Estimate control effort from convergence time
        # Longer convergence → higher effort (simple heuristic)
        convergence_ms = ctrl_metrics.get('convergence_ms', 0)
        if convergence_ms > 0:
            # Normalize to 0-100 range (arbitrary scaling for comparison)
            ctrl_metrics['control_effort_estimate'] = min(100.0, convergence_ms / 10.0)
        else:
            ctrl_metrics['control_effort_estimate'] = 0.0

    return metrics


def generate_performance_csv(metrics: Dict[str, Dict[str, float]], output_path: str):
    """Generate CSV file with performance matrix."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Define column order
    columns = [
        'controller',
        'compute_time_us',
        'compute_time_ms',
        'throughput_steps_per_s',
        'convergence_ms',
        'control_effort_estimate'
    ]

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()

        for ctrl_name in sorted(metrics.keys()):
            row = {'controller': ctrl_name}
            row.update(metrics[ctrl_name])

            # Fill missing values with N/A
            for col in columns[1:]:  # Skip 'controller' column
                if col not in row:
                    row[col] = 'N/A'

            writer.writerow(row)

    print(f"[OK] Performance matrix written to: {output_path}")
    print(f"   Controllers: {len(metrics)}")
    print(f"   Metrics: {len(columns) - 1}")


def main():
    """Main execution: parse benchmarks and generate CSV."""
    print("=" * 80)
    print("Performance Matrix Generator")
    print("=" * 80)

    # Load benchmark results
    print("\n[1/4] Loading benchmark results from .benchmark_results.json...")
    try:
        data = load_benchmark_results()
        benchmarks = data.get('benchmarks', [])
        print(f"   [OK] Loaded {len(benchmarks)} benchmarks")
    except FileNotFoundError:
        print("   [FAIL] ERROR: .benchmark_results.json not found!")
        print("   Run: python -m pytest tests/test_benchmarks/ --benchmark-only --benchmark-json=.benchmark_results.json")
        sys.exit(1)
    except Exception as e:
        print(f"   [FAIL] ERROR: {e}")
        sys.exit(1)

    # Extract controller metrics
    print("\n[2/4] Extracting controller metrics...")
    metrics = extract_controller_metrics(benchmarks)
    print(f"   [OK] Extracted metrics for {len(metrics)} controllers:")
    for ctrl_name in sorted(metrics.keys()):
        print(f"      - {ctrl_name}")

    # Calculate derived metrics
    print("\n[3/4] Calculating derived metrics...")
    metrics = calculate_derived_metrics(metrics)
    print(f"   [OK] Derived metrics calculated")

    # Generate CSV
    print("\n[4/4] Generating CSV...")
    output_path = "benchmarks/raw/baselines/baseline_performance.csv"
    generate_performance_csv(metrics, output_path)

    print("\n" + "=" * 80)
    print("[SUCCESS] Performance matrix generation complete!")
    print("=" * 80)
    print(f"\nNext steps:")
    print(f"1. Review: cat {output_path}")
    print(f"2. Commit: git add {output_path} scripts/generate_performance_matrix.py")
    print(f"3. Continue with Week 2: MT-5 (Comprehensive Benchmark)")


if __name__ == "__main__":
    main()
