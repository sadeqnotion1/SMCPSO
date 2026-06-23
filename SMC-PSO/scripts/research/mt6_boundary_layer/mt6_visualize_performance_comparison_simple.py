"""Simplified MT-6 performance comparison visualisations.

These plots operate purely on the JSON summary statistics produced by the
MT-6 analysis pipeline, making it possible to produce consistent visuals
without the raw Monte Carlo traces.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json


def load_json_summary(json_path: Path) -> dict:
    """Load MT-6 summary statistics from a JSON file.

    Args:
        json_path (Path): Path to the JSON artifact produced by MT-6.

    Returns:
        dict: Parsed summary statistics.
    """
    with open(json_path, 'r') as f:
        return json.load(f)


def add_significance_annotation(ax, x1, x2, y, p_value, improvement_pct):
    """Draw a bracket annotation with significance stars and improvement text.

    Args:
        ax (matplotlib.axes.Axes): Target axis that receives the annotation.
        x1 (float): X-coordinate of the first bar in the pair.
        x2 (float): X-coordinate of the second bar in the pair.
        y (float): Baseline height for the bracket.
        p_value (float): P-value associated with the comparison.
        improvement_pct (float): Percent improvement to display alongside the stars.
    """
    # Determine significance level
    if p_value < 0.001:
        sig_text = '***'
    elif p_value < 0.01:
        sig_text = '**'
    elif p_value < 0.05:
        sig_text = '*'
    else:
        sig_text = 'ns'

    # Draw bracket
    h = y * 0.03
    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c='black')

    # Add text
    annotation = f'{sig_text}\n{improvement_pct:+.1f}%'
    ax.text((x1+x2)*0.5, y+h, annotation, ha='center', va='bottom',
            fontsize=10, fontweight='bold')


def plot_comparison_from_summary(
    statistical_json_path: Path,
    output_path: Path,
    show: bool = False
):
    """Render a bar-chart comparison using MT-6 summary statistics.

    Args:
        statistical_json_path (Path): Path to the statistical comparison JSON artifact.
        output_path (Path): Destination path for the rendered PNG figure.
        show (bool, optional): Display the figure interactively when True. Defaults to False.
    """

    # Load statistical comparison
    stats = load_json_summary(statistical_json_path)
    comparisons = stats['comparisons']

    # Set style
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['font.family'] = 'DejaVu Sans'

    # Create 2x2 subplot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=300)
    fig.suptitle('MT-6 Performance Comparison: Fixed vs Adaptive Boundary Layer',
                 fontsize=16, fontweight='bold', y=0.98)

    # Colors
    color_fixed = '#FF6B6B'
    color_adaptive = '#4ECDC4'

    # Metrics to plot
    metrics = [
        ('chattering_index', 'Chattering Index', 'Chattering Mitigation'),
        ('overshoot_theta1', 'Overshoot theta1 [rad]', 'Transient Overshoot'),
        ('overshoot_theta2', 'Overshoot theta2 [rad]', 'Second Link Overshoot'),
        ('control_energy', 'Control Energy [N^2*s]', 'Control Efficiency')
    ]

    for idx, (metric_key, ylabel, title) in enumerate(metrics):
        ax = axes[idx // 2, idx % 2]

        # Get data
        comp = comparisons.get(metric_key, {})
        if not comp or not comp.get('significant', False):
            # Skip if not available or not significant
            if not comp:
                ax.text(0.5, 0.5, f'{metric_key}\nData not available',
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color='gray')
                ax.set_title(title, fontsize=12, fontweight='bold')
                continue

        fixed_mean = comp['fixed_mean']
        fixed_ci_lower = comp['fixed_ci_lower']
        fixed_ci_upper = comp['fixed_ci_upper']
        adaptive_mean = comp['adaptive_mean']
        adaptive_ci_lower = comp['adaptive_ci_lower']
        adaptive_ci_upper = comp['adaptive_ci_upper']

        # Compute error bars (CI width) - format: [[lower_errors], [upper_errors]]
        yerr = np.array([
            [fixed_mean - fixed_ci_lower, adaptive_mean - adaptive_ci_lower],
            [fixed_ci_upper - fixed_mean, adaptive_ci_upper - adaptive_mean]
        ])

        # Plot bars
        x_pos = [1, 2]
        bars = ax.bar(x_pos, [fixed_mean, adaptive_mean],
                     color=[color_fixed, color_adaptive],
                     edgecolor='black', linewidth=1.5, width=0.6,
                     yerr=yerr,
                     capsize=8, error_kw={'linewidth': 2, 'ecolor': 'black'})

        # Add value labels on bars
        for bar, val in zip(bars, [fixed_mean, adaptive_mean]):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.2f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Add significance annotation
        p_val = comp['p_value']
        improvement = comp['improvement_percent']
        y_max = max(fixed_ci_upper, adaptive_ci_upper)
        add_significance_annotation(ax, 1, 2, y_max * 1.1, p_val, improvement)

        # Styling
        ax.set_ylabel(ylabel, fontsize=11, fontweight='bold')
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(['Fixed', 'Adaptive'], fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim(bottom=0, top=y_max * 1.25)

        # Add improvement text box
        textstr = f'Improvement: {improvement:+.1f}%\np < {p_val:.4f}'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=9,
               verticalalignment='top', bbox=props)

    # Add summary statistics box
    summary_text = stats.get('summary', 'Statistical analysis complete')
    fig.text(0.5, 0.02, summary_text, ha='center', fontsize=11,
            style='italic', bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))

    plt.tight_layout(rect=[0, 0.04, 1, 0.96])

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Performance comparison plot saved to: {output_path}")

    if show:
        plt.show()

    plt.close()


def main():
    """Generate the simplified MT-6 performance comparison figure from summaries.

    Returns:
        int: Zero on success, non-zero when prerequisites are missing.
    """
    print("=" * 80)
    print("MT-6 Performance Comparison Visualization (Simplified)")
    print("=" * 80)
    print()

    # Paths
    project_root = Path(__file__).parent.parent
    statistical_json = project_root / "benchmarks" / "MT6_statistical_comparison.json"
    output_path = project_root / "benchmarks" / "figures" / "MT6_performance_comparison.png"

    # Verify inputs
    if not statistical_json.exists():
        print(f"ERROR: Statistical comparison not found: {statistical_json}")
        return 1

    print(f"Loading statistical comparison: {statistical_json}")
    print()

    # Generate plot
    print("Generating performance comparison plot...")
    plot_comparison_from_summary(statistical_json, output_path, show=False)

    print("=" * 80)
    print("Performance comparison visualization complete!")
    print(f"Output: {output_path}")
    print("=" * 80)

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
