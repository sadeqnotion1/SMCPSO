#==========================================================================================\\\
#================= scripts/optimization/visualize_optimization_results.py ================\\\
#==========================================================================================\\\

"""
Visualization tool for PSO optimization results from Issue #12.
Generates comprehensive comparison plots for all optimized controllers.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import json  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from typing import Dict  # noqa: E402
import argparse  # noqa: E402


def load_optimization_results(results_dir: Path) -> Dict:
    """Load all optimization result JSON files."""
    results = {}

    controllers = ['classical_smc', 'adaptive_smc', 'sta_smc', 'hybrid_adaptive_sta_smc']

    for ctrl in controllers:
        json_file = results_dir / f'gains_{ctrl}_chattering.json'
        if json_file.exists():
            with open(json_file) as f:
                results[ctrl] = json.load(f)
        else:
            print(f"Warning: {json_file} not found")

    return results


def create_comparison_plots(results: Dict, output_dir: Path):
    """Create comprehensive comparison plots."""

    # Extract metrics
    controllers = list(results.keys())
    chattering = [results[c]['metrics']['chattering_index'] for c in controllers]
    tracking = [results[c]['metrics']['tracking_error_rms'] for c in controllers]
    control_effort = [results[c]['metrics']['control_effort_rms'] for c in controllers]
    smoothness = [results[c]['metrics']['smoothness_index'] for c in controllers]

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('PSO Optimization Results - Issue #12 Chattering Reduction', fontsize=16, fontweight='bold')

    # 1. Chattering Index
    ax = axes[0, 0]
    bars = ax.bar(controllers, chattering, color=['#2ecc71' if c < 2.0 else '#e74c3c' for c in chattering])
    ax.axhline(y=2.0, color='red', linestyle='--', linewidth=2, label='Target (<2.0)')
    ax.set_ylabel('Chattering Index', fontsize=12, fontweight='bold')
    ax.set_title('Chattering Reduction (Lower is Better)', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xticklabels(controllers, rotation=15, ha='right')

    # Add value labels on bars
    for bar, value in zip(bars, chattering):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.2f}',
                ha='center', va='bottom', fontweight='bold')

    # 2. Tracking Error
    ax = axes[0, 1]
    bars = ax.bar(controllers, tracking, color='#3498db')
    ax.axhline(y=0.1, color='orange', linestyle='--', linewidth=2, label='Target (<0.1 rad)')
    ax.set_ylabel('Tracking Error RMS (rad)', fontsize=12, fontweight='bold')
    ax.set_title('Tracking Accuracy (Lower is Better)', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xticklabels(controllers, rotation=15, ha='right')

    # Add value labels
    for bar, value in zip(bars, tracking):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.4f}',
                ha='center', va='bottom', fontweight='bold')

    # 3. Control Effort
    ax = axes[1, 0]
    bars = ax.bar(controllers, control_effort, color='#9b59b6')
    ax.axhline(y=100.0, color='green', linestyle='--', linewidth=2, label='Target (<100 N)')
    ax.set_ylabel('Control Effort RMS (N)', fontsize=12, fontweight='bold')
    ax.set_title('Control Effort (Lower is Better)', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xticklabels(controllers, rotation=15, ha='right')

    # Add value labels
    for bar, value in zip(bars, control_effort):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.1f}',
                ha='center', va='bottom', fontweight='bold')

    # 4. Smoothness Index
    ax = axes[1, 1]
    bars = ax.bar(controllers, smoothness, color='#e67e22')
    ax.set_ylabel('Smoothness Index', fontsize=12, fontweight='bold')
    ax.set_title('Control Smoothness (Higher is Better)', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_xticklabels(controllers, rotation=15, ha='right')

    # Add value labels
    for bar, value in zip(bars, smoothness):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.4f}',
                ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()

    # Save
    output_file = output_dir / 'optimization_results_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved comparison plot: {output_file}")
    plt.close()


def create_gains_comparison(results: Dict, output_dir: Path):
    """Create gains comparison visualization."""

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Optimized Controller Gains Comparison', fontsize=16, fontweight='bold')

    for idx, (ctrl_name, data) in enumerate(results.items()):
        ax = axes[idx // 2, idx % 2]

        gains = data['gains']
        gain_labels = [f'g{i+1}' for i in range(len(gains))]

        bars = ax.bar(gain_labels, gains, color='#16a085')
        ax.set_ylabel('Gain Value', fontsize=11, fontweight='bold')
        ax.set_title(f'{ctrl_name}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for bar, value in zip(bars, gains):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.2f}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()

    output_file = output_dir / 'optimized_gains_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved gains plot: {output_file}")
    plt.close()


def generate_summary_table(results: Dict, output_dir: Path):
    """Generate markdown summary table."""

    md_content = "# PSO Optimization Results - Issue #12 Chattering Reduction\n\n"
    md_content += "## Summary Table\n\n"
    md_content += "| Controller | Chattering | Tracking (rad) | Control (N) | Smoothness | Status |\n"
    md_content += "|------------|------------|----------------|-------------|------------|--------|\n"

    for ctrl_name, data in results.items():
        metrics = data['metrics']
        chat = metrics['chattering_index']
        track = metrics['tracking_error_rms']
        effort = metrics['control_effort_rms']
        smooth = metrics['smoothness_index']

        # Determine pass/fail
        pass_chat = "✓" if chat < 2.0 else "✗"
        pass_track = "✓" if track < 0.1 else "✗"
        pass_effort = "✓" if effort < 100.0 else "✗"
        pass_smooth = "✓" if smooth > 0.001 else "✗"

        status = f"{pass_chat}{pass_track}{pass_effort}{pass_smooth}"

        md_content += f"| {ctrl_name} | {chat:.3f} | {track:.4f} | {effort:.2f} | {smooth:.4f} | {status} |\n"

    md_content += "\n## Criteria\n\n"
    md_content += "- ✓ = Pass, ✗ = Fail\n"
    md_content += "- Order: Chattering | Tracking | Control | Smoothness\n"
    md_content += "- Targets: <2.0 | <0.1 rad | <100 N | >0.001\n\n"

    md_content += "## Optimized Gains\n\n"
    for ctrl_name, data in results.items():
        gains = data['gains']
        md_content += f"### {ctrl_name}\n"
        md_content += f"```python\n{gains}\n```\n\n"

    output_file = output_dir / 'optimization_summary.md'
    with open(output_file, 'w') as f:
        f.write(md_content)

    print(f"✓ Saved summary: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Visualize PSO optimization results')
    parser.add_argument('--results-dir', type=Path, default=Path('.'),
                        help='Directory containing gains_*_chattering.json files')
    parser.add_argument('--output-dir', type=Path, default=Path('docs/analysis'),
                        help='Directory for output plots')
    args = parser.parse_args()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load results
    print("Loading optimization results...")
    results = load_optimization_results(args.results_dir)

    if not results:
        print("Error: No optimization results found!")
        return

    print(f"Found results for {len(results)} controllers")

    # Generate visualizations
    print("\nGenerating visualizations...")
    create_comparison_plots(results, args.output_dir)
    create_gains_comparison(results, args.output_dir)
    generate_summary_table(results, args.output_dir)

    print(f"\n✅ All visualizations saved to: {args.output_dir}")


if __name__ == '__main__':
    main()