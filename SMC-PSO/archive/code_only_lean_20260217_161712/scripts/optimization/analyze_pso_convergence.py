#==========================================================================================\\\
#=================== scripts/optimization/analyze_pso_convergence.py =====================\\\
#==========================================================================================\\\

"""
Analyze PSO convergence behavior from log files.
Extracts convergence curves, identifies convergence points, and generates diagnostic plots.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import re  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from typing import Dict, List, Tuple  # noqa: E402
import argparse  # noqa: E402

# Centralized log paths
from src.utils.infrastructure.logging.paths import PSO_LOG_DIR  # noqa: E402


def extract_convergence_data(log_file: Path) -> Tuple[List[int], List[float]]:
    """
    Extract PSO iteration and cost data from log file.

    Returns:
        (iterations, costs) - Lists of iteration numbers and corresponding best costs
    """
    with open(log_file) as f:
        log_content = f.read()

    # Find all best_cost updates in format: "X/150, best_cost=Y"
    pattern = r'(\d+)/150[^=]*best_cost=(\d+\.?\d*)'
    matches = re.findall(pattern, log_content)

    if not matches:
        return [], []

    iterations = []
    costs = []

    for iter_str, cost_str in matches:
        iteration = int(iter_str)
        cost = float(cost_str)

        # Filter out penalty values
        if cost < 10000:
            iterations.append(iteration)
            costs.append(cost)

    return iterations, costs


def detect_convergence_point(iterations: List[int], costs: List[float],
                              window_size: int = 20, threshold: float = 1.0) -> int:
    """
    Detect the iteration where PSO converged.

    Convergence is detected when the standard deviation of costs in a sliding window
    falls below the threshold.

    Returns:
        Iteration number where convergence occurred, or -1 if not converged
    """
    if len(costs) < window_size:
        return -1

    for i in range(len(costs) - window_size + 1):
        window = costs[i:i + window_size]
        std = np.std(window)

        if std < threshold:
            return iterations[i + window_size // 2]  # Return middle of convergence window

    return -1


def analyze_controller(controller_name: str, log_file: Path) -> Dict:
    """Analyze single controller's PSO convergence."""

    iterations, costs = extract_convergence_data(log_file)

    if not iterations:
        return {
            'controller': controller_name,
            'status': 'NO_DATA',
            'iterations': [],
            'costs': []
        }

    # Statistics
    initial_cost = costs[0] if costs else None
    final_cost = costs[-1] if costs else None
    min_cost = min(costs) if costs else None
    max_cost = max(costs) if costs else None
    converged_at = detect_convergence_point(iterations, costs)

    # Improvement metrics
    if initial_cost and final_cost and initial_cost > 0:
        improvement_pct = (initial_cost - final_cost) / initial_cost * 100
    else:
        improvement_pct = 0.0

    # Convergence rate (iterations to reach 95% of final improvement)
    target_cost = initial_cost - 0.95 * (initial_cost - final_cost)
    conv_rate = -1
    for i, cost in enumerate(costs):
        if cost <= target_cost:
            conv_rate = iterations[i]
            break

    return {
        'controller': controller_name,
        'status': 'CONVERGED' if converged_at > 0 else 'RUNNING',
        'iterations': iterations,
        'costs': costs,
        'initial_cost': initial_cost,
        'final_cost': final_cost,
        'min_cost': min_cost,
        'max_cost': max_cost,
        'converged_at': converged_at,
        'improvement_pct': improvement_pct,
        'conv_rate_95': conv_rate
    }


def plot_convergence_curves(results: Dict[str, Dict], output_dir: Path):
    """Create convergence curve plots."""

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('PSO Convergence Analysis - Issue #12', fontsize=16, fontweight='bold')

    controllers = ['classical_smc', 'adaptive_smc', 'sta_smc', 'hybrid_adaptive_sta_smc']
    colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c']

    for idx, ctrl_name in enumerate(controllers):
        if ctrl_name not in results:
            continue

        data = results[ctrl_name]
        if data['status'] == 'NO_DATA':
            continue

        ax = axes[idx // 2, idx % 2]

        iterations = data['iterations']
        costs = data['costs']

        # Plot convergence curve
        ax.plot(iterations, costs, 'o-', color=colors[idx], linewidth=2, markersize=4, alpha=0.7)

        # Mark convergence point
        if data['converged_at'] > 0:
            conv_cost = costs[iterations.index(data['converged_at'])]
            ax.axvline(data['converged_at'], color='red', linestyle='--', linewidth=2, alpha=0.5, label='Converged')
            ax.plot(data['converged_at'], conv_cost, 'r*', markersize=15)

        # Horizontal line at final cost
        if data['final_cost']:
            ax.axhline(data['final_cost'], color='green', linestyle=':', linewidth=1.5, alpha=0.7, label=f'Final: {data["final_cost"]:.1f}')

        # Target line
        ax.axhline(2.0, color='orange', linestyle='--', linewidth=2, alpha=0.5, label='Target (2.0)')

        ax.set_xlabel('Iteration', fontsize=11, fontweight='bold')
        ax.set_ylabel('Best Cost', fontsize=11, fontweight='bold')
        ax.set_title(f'{ctrl_name}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)

        # Log scale for better visualization if costs vary widely
        if data['max_cost'] and data['min_cost'] and data['max_cost'] / data['min_cost'] > 10:
            ax.set_yscale('log')

    plt.tight_layout()

    output_file = output_dir / 'pso_convergence_curves.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"[OK] Saved convergence curves: {output_file}")
    plt.close()


def generate_convergence_report(results: Dict[str, Dict], output_dir: Path):
    """Generate markdown convergence analysis report."""

    md_content = "# PSO Convergence Analysis - Issue #12\n\n"
    md_content += f"Generated: {Path().absolute()}\n\n"

    md_content += "## Summary Table\n\n"
    md_content += "| Controller | Status | Initial Cost | Final Cost | Improvement | Converged At |\n"
    md_content += "|------------|--------|--------------|------------|-------------|-------------|\n"

    for ctrl_name, data in results.items():
        if data['status'] == 'NO_DATA':
            md_content += f"| {ctrl_name} | NO_DATA | - | - | - | - |\n"
            continue

        status = data['status']
        initial = f"{data['initial_cost']:.1f}" if data['initial_cost'] else "?"
        final = f"{data['final_cost']:.1f}" if data['final_cost'] else "?"
        improvement = f"{data['improvement_pct']:.1f}%" if data['improvement_pct'] else "?"
        converged = f"Iter {data['converged_at']}" if data['converged_at'] > 0 else "Not yet"

        md_content += f"| {ctrl_name} | {status} | {initial} | {final} | {improvement} | {converged} |\n"

    md_content += "\n## Detailed Analysis\n\n"

    for ctrl_name, data in results.items():
        if data['status'] == 'NO_DATA':
            continue

        md_content += f"### {ctrl_name}\n\n"
        md_content += f"- **Status**: {data['status']}\n"
        md_content += f"- **Initial Cost**: {data['initial_cost']:.2f}\n"
        md_content += f"- **Final Cost**: {data['final_cost']:.2f}\n"
        md_content += f"- **Min Cost**: {data['min_cost']:.2f}\n"
        md_content += f"- **Improvement**: {data['improvement_pct']:.2f}%\n"

        if data['converged_at'] > 0:
            md_content += f"- **Converged At**: Iteration {data['converged_at']}\n"
        else:
            md_content += "- **Converged At**: Not yet converged\n"

        if data['conv_rate_95'] > 0:
            md_content += f"- **95% Convergence Rate**: Iteration {data['conv_rate_95']}\n"

        md_content += f"- **Total Iterations Logged**: {len(data['iterations'])}\n"

        # Pass/fail assessment
        if data['final_cost'] and data['final_cost'] < 2.0:
            md_content += "- **Assessment**: ✅ **PASS** (chattering target < 2.0 met)\n"
        else:
            md_content += "- **Assessment**: ❌ **FAIL** (chattering target < 2.0 not met)\n"

        md_content += "\n"

    md_content += "## Observations\n\n"
    md_content += "- **Target**: Chattering index < 2.0\n"
    md_content += "- **Convergence Criterion**: Standard deviation < 1.0 over 20-iteration window\n"
    md_content += "- **PSO Configuration**: 30 particles, 150 iterations, seed=42\n\n"

    output_file = output_dir / 'pso_convergence_report.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"[OK] Saved convergence report: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Analyze PSO convergence from log files')
    parser.add_argument('--logs-dir', type=Path, default=Path('.'),
                        help='Directory containing PSO log files')
    parser.add_argument('--output-dir', type=Path, default=Path('docs/analysis'),
                        help='Directory for output files')
    args = parser.parse_args()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("Analyzing PSO convergence...")

    # Analyze each controller
    controllers = {
        'classical_smc': args.logs_dir / 'pso_classical.log',
        'adaptive_smc': args.logs_dir / 'pso_adaptive_smc.log',
        'sta_smc': args.logs_dir / 'pso_sta_smc.log',
        'hybrid_adaptive_sta_smc': args.logs_dir / 'pso_hybrid_adaptive_sta_smc.log'
    }

    results = {}
    for ctrl_name, log_file in controllers.items():
        if log_file.exists():
            print(f"  Analyzing {ctrl_name}...")
            results[ctrl_name] = analyze_controller(ctrl_name, log_file)
        else:
            print(f"  Warning: {log_file} not found")
            results[ctrl_name] = {'controller': ctrl_name, 'status': 'NO_DATA', 'iterations': [], 'costs': []}

    # Generate outputs
    print("\nGenerating convergence analysis...")
    plot_convergence_curves(results, args.output_dir)
    generate_convergence_report(results, args.output_dir)

    print(f"\n[SUCCESS] Convergence analysis complete! Output saved to: {args.output_dir}")

    # Print summary to terminal
    print("\n" + "="*70)
    print("CONVERGENCE SUMMARY")
    print("="*70)
    for ctrl_name, data in results.items():
        if data['status'] != 'NO_DATA':
            status_icon = "[PASS]" if data['final_cost'] and data['final_cost'] < 2.0 else "[FAIL]"
            print(f"{status_icon} {ctrl_name:25s}: final_cost={data['final_cost']:.2f}, converged_at={data['converged_at']}")


if __name__ == '__main__':
    main()