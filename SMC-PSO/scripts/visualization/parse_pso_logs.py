#!/usr/bin/env python3
"""
PSO Convergence Log Parser with Pandas Integration

This script parses PSO optimization logs and generates Chart.js-compatible JSON
data files for interactive visualization of convergence behavior.

Features:
- Pandas-based data extraction and transformation
- Statistical convergence analysis
- Chart.js JSON generation
- Multi-controller comparative analysis

Usage:
    python parse_pso_logs.py

Outputs:
    - docs/visualization/data/pso_*_convergence.json (individual controllers)
    - docs/visualization/data/pso_comparison.json (combined analysis)
    - docs/visualization/data/convergence_statistics.json (metrics)

Author: Documentation Expert Agent
Date: 2025-10-07
"""

import re
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Centralized log paths
from src.utils.infrastructure.logging.paths import PSO_LOG_DIR


@dataclass
class ConvergenceMetrics:
    """Statistical metrics for PSO convergence analysis."""

    controller_name: str
    initial_cost: float
    final_cost: float
    best_cost: float
    total_iterations: int
    iterations_to_90_percent: Optional[int]
    iterations_to_95_percent: Optional[int]
    iterations_to_99_percent: Optional[int]
    convergence_rate: float  # Cost reduction per iteration
    mean_improvement_per_iter: float
    std_improvement: float
    stagnation_iterations: int  # Iterations with <1% improvement
    total_time_seconds: float
    iterations_per_second: float
    final_gains: List[float]

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class PSOLogParser:
    """Parse PSO optimization logs and extract convergence data."""

    # Regular expressions for log parsing
    ITERATION_PATTERN = r'(\d+)/(\d+),\s*best_cost=([\d.e+\-]+)(?:\s|$)'
    TIMESTAMP_PATTERN = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}),\d+'
    FINAL_COST_PATTERN = r'Optimization finished.*best cost:\s*([\d.]+),\s*best pos:\s*\[([\d.,\s]+)\]'
    TOTAL_TIME_PATTERN = r'Optimization completed in\s*([\d.]+)s'
    CONFIG_PATTERN = r"n_particles=(\d+),\s*iters=(\d+)"

    # Controller color scheme for Chart.js
    CONTROLLER_COLORS = {
        'classical_smc': 'rgb(75, 192, 192)',
        'sta_smc': 'rgb(255, 99, 132)',
        'adaptive_smc': 'rgb(54, 162, 235)',
        'hybrid_adaptive_sta_smc': 'rgb(255, 206, 86)'
    }

    def __init__(self, logs_dir: Path = PSO_LOG_DIR):
        """Initialize parser with log directory (defaults to centralized PSO log dir)."""
        self.logs_dir = logs_dir
        self.convergence_data: Dict[str, pd.DataFrame] = {}
        self.metrics: Dict[str, ConvergenceMetrics] = {}

    def parse_log_file(self, log_path: Path, controller_name: str) -> pd.DataFrame:
        """
        Parse a single PSO log file and extract convergence data.

        Parameters
        ----------
        log_path : Path
            Path to the PSO log file
        controller_name : str
            Name of the controller (e.g., 'classical_smc')

        Returns
        -------
        pd.DataFrame
            Convergence data with columns: iteration, cost, timestamp
        """
        print(f"\nParsing {controller_name} log: {log_path.name}")

        data_rows = []
        timestamps = []

        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Find ALL matches in the line (multiple per line possible)
                matches = list(re.finditer(self.ITERATION_PATTERN, line))
                for match in matches:
                    iteration = int(match.group(1))
                    total_iters = int(match.group(2))
                    cost_str = match.group(3)

                    try:
                        cost = float(cost_str)
                    except ValueError:
                        # Skip malformed entries
                        continue

                    # Extract timestamp (same for all entries in line)
                    ts_match = re.search(self.TIMESTAMP_PATTERN, line)
                    timestamp = None
                    if ts_match:
                        try:
                            timestamp = datetime.strptime(ts_match.group(1), '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            timestamp = None

                    data_rows.append({
                        'iteration': iteration,
                        'cost': cost,
                        'timestamp': timestamp
                    })

        if not data_rows:
            print(f"WARNING: No convergence data found in {log_path.name}")
            return pd.DataFrame()

        df = pd.DataFrame(data_rows)

        # Sort by iteration to ensure proper ordering
        df = df.sort_values('iteration').reset_index(drop=True)

        # Calculate time deltas if timestamps are available
        if df['timestamp'].notna().all():
            df['elapsed_seconds'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()
        else:
            df['elapsed_seconds'] = np.nan

        print(f"  Extracted {len(df)} data points")
        print(f"  Iteration range: {df['iteration'].min()} - {df['iteration'].max()}")
        print(f"  Cost range: {df['cost'].min():.2f} - {df['cost'].max():.2f}")

        return df

    def extract_final_results(self, log_path: Path) -> Tuple[float, List[float], float]:
        """
        Extract final optimization results from log file.

        Returns
        -------
        Tuple[float, List[float], float]
            (final_cost, final_gains, total_time_seconds)
        """
        final_cost = None
        final_gains = []
        total_time = None

        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Extract final cost and gains
            match = re.search(self.FINAL_COST_PATTERN, content)
            if match:
                final_cost = float(match.group(1))
                gains_str = match.group(2)
                # Parse gains - they are space-separated, not comma-separated
                final_gains = [float(x.strip()) for x in gains_str.split() if x.strip()]

            # Extract total time
            match = re.search(self.TOTAL_TIME_PATTERN, content)
            if match:
                total_time = float(match.group(1))

        return final_cost, final_gains, total_time

    def calculate_convergence_metrics(self, df: pd.DataFrame, controller_name: str,
                                     log_path: Path) -> ConvergenceMetrics:
        """
        Calculate comprehensive convergence metrics from parsed data.

        Parameters
        ----------
        df : pd.DataFrame
            Convergence data from parse_log_file()
        controller_name : str
            Controller name
        log_path : Path
            Path to log file (for extracting final results)

        Returns
        -------
        ConvergenceMetrics
            Statistical metrics for convergence analysis
        """
        if df.empty:
            return None

        # Extract final results from log
        final_cost, final_gains, total_time = self.extract_final_results(log_path)

        # Basic metrics
        initial_cost = df['cost'].iloc[0]
        best_cost = df['cost'].min()
        total_iterations = df['iteration'].max() + 1

        # Convergence thresholds (percentage of initial improvement)
        target_90 = initial_cost - 0.90 * (initial_cost - best_cost)
        target_95 = initial_cost - 0.95 * (initial_cost - best_cost)
        target_99 = initial_cost - 0.99 * (initial_cost - best_cost)

        # Find iterations to reach thresholds
        iters_90 = df[df['cost'] <= target_90]['iteration'].min() if (df['cost'] <= target_90).any() else None
        iters_95 = df[df['cost'] <= target_95]['iteration'].min() if (df['cost'] <= target_95).any() else None
        iters_99 = df[df['cost'] <= target_99]['iteration'].min() if (df['cost'] <= target_99).any() else None

        # Convergence rate (overall)
        convergence_rate = (initial_cost - best_cost) / total_iterations

        # Per-iteration improvement statistics
        df['improvement'] = df['cost'].shift(1) - df['cost']
        df['improvement'] = df['improvement'].fillna(0)
        mean_improvement = df['improvement'].mean()
        std_improvement = df['improvement'].std()

        # Stagnation detection (iterations with <1% improvement from previous)
        threshold = 0.01 * initial_cost
        stagnation_iters = (df['improvement'].abs() < threshold).sum()

        # Time metrics
        if total_time:
            iters_per_second = total_iterations / total_time
        else:
            iters_per_second = 0.0

        metrics = ConvergenceMetrics(
            controller_name=controller_name,
            initial_cost=float(initial_cost),
            final_cost=float(final_cost) if final_cost else float(best_cost),
            best_cost=float(best_cost),
            total_iterations=int(total_iterations),
            iterations_to_90_percent=int(iters_90) if pd.notna(iters_90) else None,
            iterations_to_95_percent=int(iters_95) if pd.notna(iters_95) else None,
            iterations_to_99_percent=int(iters_99) if pd.notna(iters_99) else None,
            convergence_rate=float(convergence_rate),
            mean_improvement_per_iter=float(mean_improvement),
            std_improvement=float(std_improvement),
            stagnation_iterations=int(stagnation_iters),
            total_time_seconds=float(total_time) if total_time else 0.0,
            iterations_per_second=float(iters_per_second),
            final_gains=final_gains if final_gains else []
        )

        return metrics

    def generate_chartjs_data(self, df: pd.DataFrame, controller_name: str,
                             include_linear: bool = True) -> Dict:
        """
        Generate Chart.js-compatible JSON data structure.

        Parameters
        ----------
        df : pd.DataFrame
            Convergence data
        controller_name : str
            Controller name
        include_linear : bool
            Whether to include linear scale data (default: True)

        Returns
        -------
        Dict
            Chart.js data structure
        """
        if df.empty:
            return {}

        # Get color for this controller
        color = self.CONTROLLER_COLORS.get(controller_name, 'rgb(128, 128, 128)')

        chart_data = {
            'labels': df['iteration'].tolist(),
            'datasets': [
                {
                    'label': controller_name.replace('_', ' ').title(),
                    'data': df['cost'].tolist(),
                    'borderColor': color,
                    'backgroundColor': color.replace('rgb', 'rgba').replace(')', ', 0.1)'),
                    'tension': 0.1,
                    'pointRadius': 0,  # Hide points for cleaner visualization
                    'borderWidth': 2
                }
            ]
        }

        return chart_data

    def generate_comparison_data(self) -> Dict:
        """
        Generate Chart.js data for multi-controller comparison.

        Returns
        -------
        Dict
            Chart.js data with all controllers on same axes
        """
        all_iterations = set()
        for df in self.convergence_data.values():
            if not df.empty:
                all_iterations.update(df['iteration'].tolist())

        labels = sorted(list(all_iterations))

        datasets = []
        for controller_name, df in self.convergence_data.items():
            if df.empty:
                continue

            color = self.CONTROLLER_COLORS.get(controller_name, 'rgb(128, 128, 128)')

            # Create aligned data series
            cost_series = []
            for iter_num in labels:
                matching = df[df['iteration'] == iter_num]
                if not matching.empty:
                    cost_series.append(float(matching['cost'].iloc[0]))
                else:
                    # Interpolate or use previous value
                    prev_data = df[df['iteration'] < iter_num]
                    if not prev_data.empty:
                        cost_series.append(float(prev_data['cost'].iloc[-1]))
                    else:
                        cost_series.append(None)

            datasets.append({
                'label': controller_name.replace('_', ' ').title(),
                'data': cost_series,
                'borderColor': color,
                'backgroundColor': color.replace('rgb', 'rgba').replace(')', ', 0.1)'),
                'tension': 0.1,
                'pointRadius': 0,
                'borderWidth': 2
            })

        return {
            'labels': labels,
            'datasets': datasets
        }

    def parse_all_logs(self) -> None:
        """Parse all PSO log files in the logs directory."""
        log_files = {
            'classical_smc': 'pso_classical.log',
            'sta_smc': 'pso_sta_smc.log',
            'adaptive_smc': 'pso_adaptive_smc.log',
            'hybrid_adaptive_sta_smc': 'pso_hybrid_adaptive_sta_smc.log'
        }

        for controller_name, log_file in log_files.items():
            log_path = self.logs_dir / log_file

            if not log_path.exists():
                print(f"WARNING: Log file not found: {log_path}")
                continue

            # Parse log file
            df = self.parse_log_file(log_path, controller_name)
            self.convergence_data[controller_name] = df

            # Calculate metrics
            if not df.empty:
                metrics = self.calculate_convergence_metrics(df, controller_name, log_path)
                self.metrics[controller_name] = metrics

    def save_chartjs_files(self, output_dir: Path = Path("D:/Projects/main/docs/visualization/data")) -> None:
        """
        Save Chart.js JSON files for all controllers.

        Parameters
        ----------
        output_dir : Path
            Directory to save JSON files
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save individual controller data
        for controller_name, df in self.convergence_data.items():
            if df.empty:
                continue

            chart_data = self.generate_chartjs_data(df, controller_name)
            output_file = output_dir / f"pso_{controller_name}_convergence.json"

            with open(output_file, 'w') as f:
                json.dump(chart_data, f, indent=2)

            print(f"Saved: {output_file}")

        # Save comparison data
        comparison_data = self.generate_comparison_data()
        comparison_file = output_dir / "pso_comparison.json"

        with open(comparison_file, 'w') as f:
            json.dump(comparison_data, f, indent=2)

        print(f"Saved: {comparison_file}")

        # Save convergence metrics
        metrics_dict = {name: metrics.to_dict() for name, metrics in self.metrics.items()}
        metrics_file = output_dir / "convergence_statistics.json"

        with open(metrics_file, 'w') as f:
            json.dump(metrics_dict, f, indent=2)

        print(f"Saved: {metrics_file}")

    def print_summary(self) -> None:
        """Print summary of convergence analysis."""
        print("\n" + "="*80)
        print("PSO CONVERGENCE ANALYSIS SUMMARY")
        print("="*80)

        for controller_name, metrics in self.metrics.items():
            print(f"\n{controller_name.upper()}")
            print("-" * 80)
            print(f"  Initial Cost:          {metrics.initial_cost:12.2f}")
            print(f"  Final Cost:            {metrics.final_cost:12.2f}")
            print(f"  Best Cost:             {metrics.best_cost:12.2f}")
            print(f"  Total Improvement:     {metrics.initial_cost - metrics.best_cost:12.2f} ({100*(metrics.initial_cost - metrics.best_cost)/metrics.initial_cost:.1f}%)")
            print(f"  Total Iterations:      {metrics.total_iterations:12d}")
            print(f"  Iters to 90% conv:     {metrics.iterations_to_90_percent if metrics.iterations_to_90_percent else 'N/A':>12}")
            print(f"  Iters to 95% conv:     {metrics.iterations_to_95_percent if metrics.iterations_to_95_percent else 'N/A':>12}")
            print(f"  Convergence Rate:      {metrics.convergence_rate:12.4f} cost/iter")
            print(f"  Mean Improvement:      {metrics.mean_improvement_per_iter:12.4f} ± {metrics.std_improvement:.4f}")
            print(f"  Stagnation Iterations: {metrics.stagnation_iterations:12d} ({100*metrics.stagnation_iterations/metrics.total_iterations:.1f}%)")
            print(f"  Total Time:            {metrics.total_time_seconds:12.1f} seconds")
            print(f"  Iterations/Second:     {metrics.iterations_per_second:12.4f}")
            if metrics.final_gains:
                print(f"  Final Gains:           {metrics.final_gains}")


def main():
    """Main execution function."""
    print("PSO Convergence Log Parser")
    print("=" * 80)

    # Initialize parser
    parser = PSOLogParser()

    # Parse all logs
    parser.parse_all_logs()

    # Save Chart.js JSON files
    parser.save_chartjs_files()

    # Print summary
    parser.print_summary()

    print("\n" + "="*80)
    print("PARSING COMPLETE")
    print("="*80)
    print(f"\nOutput files saved to: D:/Projects/main/docs/visualization/data/")
    print("\nGenerated files:")
    print("  - pso_classical_smc_convergence.json")
    print("  - pso_sta_smc_convergence.json")
    print("  - pso_adaptive_smc_convergence.json")
    print("  - pso_hybrid_adaptive_sta_smc_convergence.json")
    print("  - pso_comparison.json")
    print("  - convergence_statistics.json")


if __name__ == "__main__":
    main()
