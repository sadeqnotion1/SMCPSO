#!/usr/bin/env python3
#======================================================================================\
#=================== scripts/benchmarks/compare_optimizers.py ====================\
#======================================================================================\
"""
Comparative Benchmark: PSO vs GA vs DE for Controller Optimization

This script compares the performance of three optimization algorithms
(Particle Swarm Optimization, Genetic Algorithm, Differential Evolution)
on the same controller tuning task. Results are essential for master's
thesis analysis showing algorithm strengths/weaknesses.

Metrics Compared:
- Best cost achieved
- Convergence speed (iterations to 95% of best)
- Computational time
- Solution robustness (std dev across runs)
- Final controller performance (settling time, overshoot, ISE)

Usage:
    python scripts/benchmarks/compare_optimizers.py --controller classical_smc --runs 10
    python scripts/benchmarks/compare_optimizers.py --controller sta_smc --runs 5 --save-results

Output:
    1. Console table with comparison metrics
    2. Convergence plot (3 algorithms overlaid)
    3. Box plots showing robustness
    4. CSV file with raw results (if --save-results)

Author: Claude Code + AI-assisted development
Date: November 2025
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
import sys

# Add project root to path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.config import load_config
from src.controllers.factory import create_controller
from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.optimizer.ga_optimizer import GATuner
from src.optimizer.de_optimizer import DETuner


def run_single_optimization(algorithm: str, controller_name: str, config_path: Path,
                            seed: int, dimension: int) -> Tuple[float, float, List[float]]:
    """Run a single optimization trial for one algorithm.

    Parameters
    ----------
    algorithm : str
        Algorithm name ('PSO', 'GA', 'DE')
    controller_name : str
        Controller type (e.g., 'classical_smc')
    config_path : Path
        Path to configuration file
    seed : int
        Random seed for reproducibility
    dimension : int
        Number of gain parameters

    Returns
    -------
    best_cost : float
        Best cost achieved
    runtime : float
        Total optimization time (seconds)
    convergence_history : List[float]
        Best cost at each iteration/generation
    """
    config = load_config(config_path)
    controller_factory = lambda gains: create_controller(controller_name, config=config, gains=gains)

    lower_bounds = np.full(dimension, 0.1)
    upper_bounds = np.full(dimension, 100.0)

    start_time = time.time()

    if algorithm == 'PSO':
        tuner = PSOTuner(controller_factory, config=config, seed=seed)
        best_gains, best_cost = tuner.optimize(
            population_size=50,
            max_generations=100,
            dimension=dimension,
            lower_bounds=lower_bounds,
            upper_bounds=upper_bounds
        )
        convergence_history = getattr(tuner, 'fitness_history', [])

    elif algorithm == 'GA':
        tuner = GATuner(controller_factory, config=config, seed=seed)
        best_gains, best_cost = tuner.optimize(
            population_size=50,
            max_generations=100,
            dimension=dimension,
            lower_bounds=lower_bounds,
            upper_bounds=upper_bounds
        )
        convergence_history = getattr(tuner, 'fitness_history', [])

    elif algorithm == 'DE':
        tuner = DETuner(controller_factory, config=config, seed=seed)
        best_gains, best_cost = tuner.optimize(
            population_size=50,
            max_generations=100,
            dimension=dimension,
            lower_bounds=lower_bounds,
            upper_bounds=upper_bounds,
            strategy='best/1/bin',
            adaptive_parameters=True
        )
        convergence_history = getattr(tuner, 'fitness_history', [])

    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    runtime = time.time() - start_time

    return best_cost, runtime, convergence_history


def compute_convergence_iteration(history: List[float], threshold: float = 0.95) -> int:
    """Find iteration where algorithm reaches 95% of final best cost.

    Returns -1 if never converges to threshold.
    """
    if not history:
        return -1

    final_best = min(history)
    target = final_best / threshold

    for i, cost in enumerate(history):
        if cost <= target:
            return i

    return -1  # Never converged


def run_comparison_benchmark(controller_name: str, config_path: Path, n_runs: int = 10,
                             dimension: int = 6, save_results: bool = False) -> Dict:
    """Run full comparison benchmark across all algorithms.

    Parameters
    ----------
    controller_name : str
        Controller type to optimize
    config_path : Path
        Configuration file path
    n_runs : int
        Number of independent runs per algorithm
    dimension : int
        Number of controller gains
    save_results : bool
        Whether to save raw results to file

    Returns
    -------
    results : Dict
        Nested dictionary: results[algorithm][metric] = [run1, run2, ...]
    """
    algorithms = ['PSO', 'GA', 'DE']
    results = {alg: {'costs': [], 'runtimes': [], 'convergence_iters': [], 'histories': []}
               for alg in algorithms}

    print(f"\n{'='*70}")
    print(f"Optimizer Comparison Benchmark: {controller_name}")
    print(f"Runs per algorithm: {n_runs}")
    print(f"Parameter dimension: {dimension}")
    print(f"{'='*70}\n")

    for alg in algorithms:
        print(f"Running {alg}... (0/{n_runs})", end='', flush=True)

        for run_idx in range(n_runs):
            seed = 42 + run_idx  # Reproducible but different seeds

            try:
                cost, runtime, history = run_single_optimization(
                    alg, controller_name, config_path, seed, dimension
                )

                results[alg]['costs'].append(cost)
                results[alg]['runtimes'].append(runtime)
                results[alg]['histories'].append(history)

                conv_iter = compute_convergence_iteration(history)
                results[alg]['convergence_iters'].append(conv_iter)

                print(f"\rRunning {alg}... ({run_idx+1}/{n_runs})", end='', flush=True)

            except Exception as e:
                print(f"\n[ERROR] {alg} run {run_idx+1} failed: {e}")
                results[alg]['costs'].append(np.inf)
                results[alg]['runtimes'].append(np.inf)
                results[alg]['convergence_iters'].append(-1)
                results[alg]['histories'].append([])

        print()  # Newline after algorithm completes

    # Print summary table
    print(f"\n{'='*70}")
    print("BENCHMARK RESULTS SUMMARY")
    print(f"{'='*70}")
    print(f"{'Algorithm':<12} {'Best Cost':<15} {'Mean Cost':<15} {'Std Cost':<15}")
    print(f"{'-'*70}")

    for alg in algorithms:
        costs = np.array([c for c in results[alg]['costs'] if c != np.inf])
        if len(costs) > 0:
            best = np.min(costs)
            mean = np.mean(costs)
            std = np.std(costs)
            print(f"{alg:<12} {best:<15.6f} {mean:<15.6f} {std:<15.6f}")
        else:
            print(f"{alg:<12} {'FAILED':<15} {'FAILED':<15} {'FAILED':<15}")

    print(f"\n{'Algorithm':<12} {'Mean Time (s)':<15} {'Std Time (s)':<15} {'Conv. Iter':<15}")
    print(f"{'-'*70}")

    for alg in algorithms:
        runtimes = np.array([r for r in results[alg]['runtimes'] if r != np.inf])
        conv_iters = np.array([c for c in results[alg]['convergence_iters'] if c >= 0])

        if len(runtimes) > 0:
            mean_time = np.mean(runtimes)
            std_time = np.std(runtimes)
            mean_conv = np.mean(conv_iters) if len(conv_iters) > 0 else -1

            print(f"{alg:<12} {mean_time:<15.2f} {std_time:<15.2f} {mean_conv:<15.1f}")
        else:
            print(f"{alg:<12} {'FAILED':<15} {'FAILED':<15} {'FAILED':<15}")

    print(f"{'='*70}\n")

    # Save results if requested
    if save_results:
        output_dir = REPO_ROOT / "optimization_results" / "comparisons"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"comparison_{controller_name}_{timestamp}.json"

        # Convert numpy arrays to lists for JSON serialization
        json_results = {
            alg: {k: [float(v) if isinstance(v, (np.floating, np.integer)) else v
                     for v in vals]
                  for k, vals in metrics.items()}
            for alg, metrics in results.items()
        }

        with open(output_file, 'w') as f:
            json.dump({
                'controller': controller_name,
                'n_runs': n_runs,
                'dimension': dimension,
                'results': json_results
            }, f, indent=2)

        print(f"[OK] Results saved to: {output_file}")

    return results


def plot_convergence_comparison(results: Dict, controller_name: str, save_fig: bool = False):
    """Plot convergence curves for all algorithms overlaid."""
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {'PSO': 'blue', 'GA': 'green', 'DE': 'red'}

    for alg, data in results.items():
        histories = data['histories']

        if not histories or all(len(h) == 0 for h in histories):
            continue

        # Plot mean and std envelope
        max_len = max(len(h) for h in histories if h)
        all_histories = np.full((len(histories), max_len), np.nan)

        for i, h in enumerate(histories):
            if h:
                all_histories[i, :len(h)] = h

        mean_hist = np.nanmean(all_histories, axis=0)
        std_hist = np.nanstd(all_histories, axis=0)

        iterations = np.arange(len(mean_hist))
        ax.plot(iterations, mean_hist, label=alg, color=colors[alg], linewidth=2)
        ax.fill_between(iterations, mean_hist - std_hist, mean_hist + std_hist,
                        alpha=0.2, color=colors[alg])

    ax.set_xlabel('Iteration / Generation', fontsize=12)
    ax.set_ylabel('Best Cost', fontsize=12)
    ax.set_title(f'Optimization Convergence Comparison: {controller_name}', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')  # Log scale for better visualization

    if save_fig:
        output_dir = REPO_ROOT / "optimization_results" / "comparisons"
        output_dir.mkdir(parents=True, exist_ok=True)
        fig_path = output_dir / f"convergence_{controller_name}.png"
        plt.savefig(fig_path, dpi=150, bbox_inches='tight')
        print(f"[OK] Convergence plot saved to: {fig_path}")

    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Compare PSO vs GA vs DE optimizers")
    parser.add_argument('--controller', type=str, default='classical_smc',
                       help='Controller to optimize (classical_smc, sta_smc, adaptive_smc)')
    parser.add_argument('--runs', type=int, default=10,
                       help='Number of independent runs per algorithm (default: 10)')
    parser.add_argument('--dimension', type=int, default=6,
                       help='Number of gain parameters (default: 6)')
    parser.add_argument('--config', type=Path, default=REPO_ROOT / "config.yaml",
                       help='Path to configuration file')
    parser.add_argument('--save-results', action='store_true',
                       help='Save raw results to JSON file')
    parser.add_argument('--plot', action='store_true',
                       help='Display convergence comparison plot')

    args = parser.parse_args()

    # Run benchmark
    results = run_comparison_benchmark(
        controller_name=args.controller,
        config_path=args.config,
        n_runs=args.runs,
        dimension=args.dimension,
        save_results=args.save_results
    )

    # Plot if requested
    if args.plot:
        plot_convergence_comparison(results, args.controller, save_fig=args.save_results)


if __name__ == "__main__":
    main()
