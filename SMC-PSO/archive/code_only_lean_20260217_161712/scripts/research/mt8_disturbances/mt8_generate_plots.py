"""
MT-8 Plot Generator: Visualization for Baseline vs Robust Comparison

Generates comprehensive comparison plots:
1. Convergence rate comparison (baseline vs robust)
2. Overshoot comparison with error bars
3. Settling time comparison
4. Control effort comparison
5. Improvement percentage heatmap
6. Statistical distribution plots

Usage:
    python scripts/mt8_generate_plots.py
    python scripts/mt8_generate_plots.py --output-dir benchmarks/plots
    python scripts/mt8_generate_plots.py --validation benchmarks/MT8_robust_validation_all.json
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')


def load_baseline_results(filepath: str) -> Dict:
    """Load baseline disturbance rejection results."""
    with open(filepath, 'r') as f:
        return json.load(f)


def load_validation_results(filepath: str) -> Dict:
    """Load robust PSO validation results."""
    with open(filepath, 'r') as f:
        return json.load(f)


def plot_convergence_comparison(
    baseline: Dict,
    validation: Dict,
    output_dir: Path
):
    """Plot convergence rate comparison."""

    controllers = sorted(validation.keys())
    scenarios = ['step', 'impulse', 'sinusoidal', 'random']

    # Extract data
    baseline_conv = {ctrl: [] for ctrl in controllers}
    robust_conv = {ctrl: [] for ctrl in controllers}

    for controller in controllers:
        for result in baseline['results']:
            if result['controller_name'] == controller:
                # Baseline: 0 if not converged, 1 if converged
                baseline_conv[controller].append(1.0 if result['converged'] else 0.0)

        for scenario in scenarios:
            if scenario in validation[controller]['validation']:
                robust_conv[controller].append(
                    validation[controller]['validation'][scenario]['convergence_rate']
                )

    # Create grouped bar plot
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(scenarios))
    width = 0.15

    for i, controller in enumerate(controllers):
        baseline_values = baseline_conv[controller]
        robust_values = robust_conv[controller]

        offset = (i - len(controllers)/2 + 0.5) * width

        ax.bar(x + offset - width/2, baseline_values, width, label=f'{controller} (baseline)', alpha=0.6)
        ax.bar(x + offset + width/2, robust_values, width, label=f'{controller} (robust)', alpha=0.9)

    ax.set_xlabel('Disturbance Scenario', fontsize=12)
    ax.set_ylabel('Convergence Rate', fontsize=12)
    ax.set_title('Convergence Rate: Baseline vs Robust PSO', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([s.capitalize() for s in scenarios])
    ax.axhline(y=0.95, color='g', linestyle='--', linewidth=1, label='Target (95%)')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax.set_ylim([0, 1.1])
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'convergence_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    logger.info("  Saved: convergence_comparison.png")


def plot_overshoot_comparison(
    baseline: Dict,
    validation: Dict,
    output_dir: Path
):
    """Plot overshoot comparison with error bars."""

    controllers = sorted(validation.keys())
    scenarios = ['step', 'impulse', 'sinusoidal', 'random']

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for idx, scenario in enumerate(scenarios):
        ax = axes[idx]

        baseline_values = []
        robust_values = []
        robust_errors = []
        labels = []

        for controller in controllers:
            # Extract baseline
            for result in baseline['results']:
                if result['controller_name'] == controller and result['disturbance_type'] == scenario:
                    baseline_values.append(result['max_overshoot'])
                    break

            # Extract robust
            if scenario in validation[controller]['validation']:
                data = validation[controller]['validation'][scenario]
                robust_values.append(data['overshoot_mean'])
                robust_errors.append(data['overshoot_std'])
            else:
                robust_values.append(0)
                robust_errors.append(0)

            labels.append(controller.replace('_', '\n'))

        x = np.arange(len(controllers))
        width = 0.35

        ax.bar(x - width/2, baseline_values, width, label='Baseline', alpha=0.7, color='orange')
        ax.bar(x + width/2, robust_values, width, yerr=robust_errors, label='Robust PSO',
               alpha=0.9, color='blue', capsize=5)

        ax.set_xlabel('Controller', fontsize=10)
        ax.set_ylabel('Overshoot (degrees)', fontsize=10)
        ax.set_title(f'{scenario.capitalize()} Disturbance', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_dir / 'overshoot_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    logger.info("  Saved: overshoot_comparison.png")


def plot_settling_time_comparison(
    baseline: Dict,
    validation: Dict,
    output_dir: Path
):
    """Plot settling time comparison."""

    controllers = sorted(validation.keys())
    scenarios = ['step', 'impulse', 'sinusoidal', 'random']

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(controllers))
    width = 0.2

    for i, scenario in enumerate(scenarios):
        baseline_values = []
        robust_values = []

        for controller in controllers:
            # Extract baseline
            for result in baseline['results']:
                if result['controller_name'] == controller and result['disturbance_type'] == scenario:
                    baseline_values.append(result['settling_time'])
                    break

            # Extract robust
            if scenario in validation[controller]['validation']:
                robust_values.append(validation[controller]['validation'][scenario]['settling_time_mean'])
            else:
                robust_values.append(10.0)

        offset = (i - len(scenarios)/2 + 0.5) * width

        # Only plot robust (baseline all at 10s anyway)
        ax.bar(x + offset, robust_values, width, label=f'{scenario.capitalize()}', alpha=0.8)

    ax.set_xlabel('Controller', fontsize=12)
    ax.set_ylabel('Settling Time (s)', fontsize=12)
    ax.set_title('Settling Time: Robust PSO Results', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([c.replace('_', '\n') for c in controllers], fontsize=9)
    ax.axhline(y=3.0, color='g', linestyle='--', linewidth=1, label='Target (<3s)')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_dir / 'settling_time_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    logger.info("  Saved: settling_time_comparison.png")


def plot_improvement_heatmap(
    validation: Dict,
    output_dir: Path
):
    """Plot improvement percentage heatmap."""

    controllers = sorted(validation.keys())
    scenarios = ['step', 'impulse', 'sinusoidal', 'random']

    # Build improvement matrix
    improvement_matrix = np.zeros((len(controllers), len(scenarios)))

    for i, controller in enumerate(controllers):
        for j, scenario in enumerate(scenarios):
            if scenario in validation[controller].get('comparison_to_baseline', {}):
                improvement_matrix[i, j] = validation[controller]['comparison_to_baseline'][scenario]['overshoot_improvement_pct']

    fig, ax = plt.subplots(figsize=(10, 6))

    im = ax.imshow(improvement_matrix, cmap='RdYlGn', aspect='auto', vmin=-50, vmax=100)

    # Set ticks
    ax.set_xticks(np.arange(len(scenarios)))
    ax.set_yticks(np.arange(len(controllers)))
    ax.set_xticklabels([s.capitalize() for s in scenarios])
    ax.set_yticklabels([c.replace('_', ' ').title() for c in controllers])

    # Add text annotations
    for i in range(len(controllers)):
        for j in range(len(scenarios)):
            text = ax.text(j, i, f'{improvement_matrix[i, j]:+.1f}%',
                          ha='center', va='center', color='black', fontsize=10, fontweight='bold')

    ax.set_title('Overshoot Improvement: Robust vs Baseline', fontsize=14, fontweight='bold')
    fig.colorbar(im, ax=ax, label='Improvement (%)')

    plt.tight_layout()
    plt.savefig(output_dir / 'improvement_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()

    logger.info("  Saved: improvement_heatmap.png")


def plot_statistical_distributions(
    validation: Dict,
    output_dir: Path
):
    """Plot statistical distributions for each controller."""

    controllers = sorted(validation.keys())
    scenarios = ['step', 'impulse', 'sinusoidal', 'random']

    for controller in controllers:
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()

        for idx, scenario in enumerate(scenarios):
            ax = axes[idx]

            if scenario not in validation[controller]['validation']:
                continue

            data = validation[controller]['validation'][scenario]

            # Plot distributions (assuming normal for now, could use actual data if available)
            mean_os = data['overshoot_mean']
            std_os = data['overshoot_std']
            mean_st = data['settling_time_mean']
            std_st = data['settling_time_std']

            # Overshoot distribution
            x_os = np.linspace(max(0, mean_os - 3*std_os), mean_os + 3*std_os, 100)
            y_os = (1 / (std_os * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_os - mean_os) / std_os) ** 2)

            ax_twin = ax.twinx()

            ax.hist(x_os, bins=30, density=True, alpha=0.3, color='blue', label='Overshoot')
            ax.plot(x_os, y_os, 'b-', linewidth=2)
            ax.axvline(mean_os, color='b', linestyle='--', linewidth=2, label=f'Mean: {mean_os:.1f}°')

            # Settling time distribution
            x_st = np.linspace(max(0, mean_st - 3*std_st), mean_st + 3*std_st, 100)
            y_st = (1 / (std_st * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_st - mean_st) / std_st) ** 2)

            ax_twin.hist(x_st, bins=30, density=True, alpha=0.3, color='red', label='Settling Time')
            ax_twin.plot(x_st, y_st, 'r-', linewidth=2)
            ax_twin.axvline(mean_st, color='r', linestyle='--', linewidth=2, label=f'Mean: {mean_st:.2f}s')

            ax.set_xlabel('Overshoot (degrees)', fontsize=10, color='blue')
            ax.set_ylabel('Probability Density', fontsize=10, color='blue')
            ax_twin.set_xlabel('Settling Time (s)', fontsize=10, color='red')
            ax_twin.set_ylabel('Probability Density', fontsize=10, color='red')
            ax.set_title(f'{scenario.capitalize()} - Conv: {data["convergence_rate"]*100:.1f}%',
                        fontsize=11, fontweight='bold')

            ax.tick_params(axis='y', labelcolor='blue')
            ax_twin.tick_params(axis='y', labelcolor='red')

            # Combine legends
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax_twin.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=8)

        plt.suptitle(f'{controller.replace("_", " ").title()} - Statistical Distributions',
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_dir / f'distributions_{controller}.png', dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"  Saved: distributions_{controller}.png")


def plot_summary_comparison(
    baseline: Dict,
    validation: Dict,
    output_dir: Path
):
    """Create summary comparison plot with key metrics."""

    controllers = sorted(validation.keys())
    scenarios = ['step', 'impulse', 'sinusoidal', 'random']

    # Compute aggregate metrics
    metrics = {
        'convergence': [],
        'avg_overshoot': [],
        'avg_settling': [],
        'avg_improvement': []
    }

    for controller in controllers:
        conv_rates = []
        overshoots = []
        settling_times = []
        improvements = []

        for scenario in scenarios:
            if scenario in validation[controller]['validation']:
                data = validation[controller]['validation'][scenario]
                conv_rates.append(data['convergence_rate'])
                overshoots.append(data['overshoot_mean'])
                settling_times.append(data['settling_time_mean'])

            if scenario in validation[controller].get('comparison_to_baseline', {}):
                improvements.append(
                    validation[controller]['comparison_to_baseline'][scenario]['overshoot_improvement_pct']
                )

        metrics['convergence'].append(np.mean(conv_rates))
        metrics['avg_overshoot'].append(np.mean(overshoots))
        metrics['avg_settling'].append(np.mean(settling_times))
        metrics['avg_improvement'].append(np.mean(improvements))

    # Create 4-panel summary
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Convergence rate
    ax = axes[0, 0]
    bars = ax.bar(range(len(controllers)), metrics['convergence'], color='green', alpha=0.7)
    ax.axhline(y=0.95, color='red', linestyle='--', linewidth=2, label='Target (95%)')
    ax.set_ylabel('Average Convergence Rate', fontsize=11)
    ax.set_title('Convergence Rate by Controller', fontsize=12, fontweight='bold')
    ax.set_xticks(range(len(controllers)))
    ax.set_xticklabels([c.replace('_', '\n') for c in controllers], fontsize=8)
    ax.set_ylim([0, 1.1])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # Average overshoot
    ax = axes[0, 1]
    bars = ax.bar(range(len(controllers)), metrics['avg_overshoot'], color='blue', alpha=0.7)
    ax.set_ylabel('Average Overshoot (degrees)', fontsize=11)
    ax.set_title('Average Overshoot by Controller', fontsize=12, fontweight='bold')
    ax.set_xticks(range(len(controllers)))
    ax.set_xticklabels([c.replace('_', '\n') for c in controllers], fontsize=8)
    ax.grid(True, alpha=0.3, axis='y')

    # Average settling time
    ax = axes[1, 0]
    bars = ax.bar(range(len(controllers)), metrics['avg_settling'], color='orange', alpha=0.7)
    ax.axhline(y=3.0, color='red', linestyle='--', linewidth=2, label='Target (<3s)')
    ax.set_ylabel('Average Settling Time (s)', fontsize=11)
    ax.set_title('Average Settling Time by Controller', fontsize=12, fontweight='bold')
    ax.set_xticks(range(len(controllers)))
    ax.set_xticklabels([c.replace('_', '\n') for c in controllers], fontsize=8)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # Average improvement
    ax = axes[1, 1]
    colors = ['green' if x > 50 else 'orange' if x > 30 else 'red' for x in metrics['avg_improvement']]
    bars = ax.bar(range(len(controllers)), metrics['avg_improvement'], color=colors, alpha=0.7)
    ax.axhline(y=50, color='green', linestyle='--', linewidth=2, label='Target (>50%)')
    ax.set_ylabel('Average Improvement (%)', fontsize=11)
    ax.set_title('Average Overshoot Improvement', fontsize=12, fontweight='bold')
    ax.set_xticks(range(len(controllers)))
    ax.set_xticklabels([c.replace('_', '\n') for c in controllers], fontsize=8)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.suptitle('MT-8 Summary: Robust PSO Performance', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'summary_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    logger.info("  Saved: summary_comparison.png")


def main():
    parser = argparse.ArgumentParser(description='MT-8 Plot Generator')
    parser.add_argument(
        '--baseline',
        type=str,
        default='benchmarks/MT8_disturbance_rejection.json',
        help='Baseline results file'
    )
    parser.add_argument(
        '--validation',
        type=str,
        default='benchmarks/MT8_robust_validation_all.json',
        help='Robust validation results file'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='benchmarks/plots',
        help='Output directory for plots'
    )

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("MT-8: Plot Generator")
    logger.info("=" * 80)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")

    # Load data
    logger.info(f"\nLoading baseline from: {args.baseline}")
    baseline = load_baseline_results(args.baseline)

    logger.info(f"Loading validation from: {args.validation}")
    validation = load_validation_results(args.validation)

    # Generate plots
    logger.info("\nGenerating plots...")

    plot_convergence_comparison(baseline, validation, output_dir)
    plot_overshoot_comparison(baseline, validation, output_dir)
    plot_settling_time_comparison(baseline, validation, output_dir)
    plot_improvement_heatmap(validation, output_dir)
    plot_statistical_distributions(validation, output_dir)
    plot_summary_comparison(baseline, validation, output_dir)

    logger.info("\n" + "=" * 80)
    logger.info(f"All plots saved to: {output_dir}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
