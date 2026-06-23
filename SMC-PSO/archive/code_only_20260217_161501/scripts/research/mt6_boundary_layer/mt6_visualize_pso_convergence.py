"""Visualisations for MT-6 particle swarm optimisation convergence data.

This script produces publication-friendly convergence plots that highlight how
the adaptive boundary layer parameters evolve during the PSO search.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.visualization.pso_plots import plot_convergence


def load_pso_history(csv_path: Path) -> pd.DataFrame:
    """Load MT-6 PSO optimisation history from a CSV file.

    Args:
        csv_path (Path): Location of the CSV file containing PSO iterations.

    Returns:
        pd.DataFrame: DataFrame with at least the columns ``iteration``,
        ``epsilon_min``, ``alpha``, and ``best_fitness``. Optional columns such
        as ``mean_fitness`` or ``std_fitness`` are preserved when present.
    """
    df = pd.read_csv(csv_path)
    return df


def plot_mt6_pso_convergence(
    pso_history: pd.DataFrame,
    save_path: Optional[Path] = None,
    show: bool = True
) -> None:
    """Create a two-panel PSO convergence plot for MT-6 experiments.

    Args:
        pso_history (pd.DataFrame): PSO iteration history containing convergence
            metrics.
        save_path (Path | None, optional): Location to write the PNG artifact.
            When None the figure is not written to disk.
        show (bool, optional): When True display the figure interactively;
            otherwise the figure is closed after saving. Defaults to True.

    Example:
        >>> plot_mt6_pso_convergence(history_df, Path("mt6.png"), show=False)
    """

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), dpi=300)

    iterations = pso_history['iteration'].values
    best_fitness = pso_history['best_fitness'].values
    epsilon_min = pso_history['epsilon_min'].values
    alpha = pso_history['alpha'].values

    # ----- Plot 1: Fitness Convergence -----
    ax1.plot(iterations, best_fitness, 'b-', linewidth=2.5, label='Best Fitness')

    # Highlight best iteration
    best_idx = np.argmin(best_fitness)
    best_iter = iterations[best_idx]
    best_fit = best_fitness[best_idx]
    best_eps = epsilon_min[best_idx]
    best_alpha = alpha[best_idx]

    ax1.scatter([best_iter], [best_fit], c='red', s=200, zorder=5,
                marker='*', edgecolors='black', linewidths=1.5,
                label=f'Best (iter {best_iter})')

    # Annotate best point
    annotation_text = (
        f"Best: epsilon={best_eps:.4f}, alpha={best_alpha:.2f}\n"
        f"Fitness={best_fit:.4f}"
    )
    ax1.annotate(
        annotation_text,
        xy=(best_iter, best_fit),
        xytext=(best_iter + 3, best_fit + 0.05 * (np.max(best_fitness) - np.min(best_fitness))),
        fontsize=10,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
        arrowprops=dict(arrowstyle='->', lw=1.5, color='red')
    )

    # Optional: Add mean fitness if available
    if 'mean_fitness' in pso_history.columns:
        mean_fitness = pso_history['mean_fitness'].values
        ax1.plot(iterations, mean_fitness, 'g--', linewidth=1.5,
                alpha=0.6, label='Mean Fitness (Swarm)')

    ax1.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Fitness', fontsize=12, fontweight='bold')
    ax1.set_title('MT-6 Adaptive Boundary Layer PSO Convergence',
                  fontsize=14, fontweight='bold', pad=15)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='upper right', fontsize=10, framealpha=0.9)

    # ----- Plot 2: Parameter Evolution -----
    ax2_twin = ax2.twinx()  # Dual y-axis for epsilon_min and alpha

    # Plot epsilon_min on left y-axis
    line1 = ax2.plot(iterations, epsilon_min, 'b-', linewidth=2,
                     marker='o', markersize=4, markevery=max(1, len(iterations)//10),
                     label='epsilon_min (Boundary Layer Base)')

    # Plot alpha on right y-axis
    line2 = ax2_twin.plot(iterations, alpha, 'r-', linewidth=2,
                          marker='s', markersize=4, markevery=max(1, len(iterations)//10),
                          label='alpha (Adaptive Slope)')

    # Highlight best parameters
    ax2.scatter([best_iter], [best_eps], c='blue', s=150, zorder=5,
                marker='*', edgecolors='black', linewidths=1.5)
    ax2_twin.scatter([best_iter], [best_alpha], c='red', s=150, zorder=5,
                     marker='*', edgecolors='black', linewidths=1.5)

    # Labels and formatting
    ax2.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax2.set_ylabel('epsilon_min (Boundary Layer Base)', fontsize=11,
                   fontweight='bold', color='blue')
    ax2_twin.set_ylabel('alpha (Adaptive Slope)', fontsize=11,
                        fontweight='bold', color='red')
    ax2.set_title('Best Parameter Evolution Over PSO Iterations',
                  fontsize=12, fontweight='bold', pad=10)

    ax2.tick_params(axis='y', labelcolor='blue')
    ax2_twin.tick_params(axis='y', labelcolor='red')
    ax2.grid(True, alpha=0.3, linestyle='--')

    # Combined legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc='upper right', fontsize=10, framealpha=0.9)

    # Tight layout
    plt.tight_layout()

    # Save
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"PSO convergence plot saved to: {save_path}")

    # Show
    if show:
        plt.show()
    else:
        plt.close()


def main():
    """Generate the MT-6 PSO convergence visualisation from disk artifacts.

    Returns:
        int: Zero on success, non-zero when required inputs are missing.
    """

    print("="*80)
    print("MT-6 PSO Convergence Visualization")
    print("="*80)

    # Paths
    benchmarks_dir = Path(__file__).parent.parent / "benchmarks"
    pso_csv = benchmarks_dir / "MT6_adaptive_optimization.csv"
    figures_dir = benchmarks_dir / "figures"
    figures_dir.mkdir(exist_ok=True)
    output_png = figures_dir / "MT6_pso_convergence.png"

    # Check if PSO results exist
    if not pso_csv.exists():
        print(f"WARNING: PSO results not found: {pso_csv}")
        print("Waiting for adaptive PSO to complete...")
        return 0

    # Load data
    print(f"\nLoading PSO history from: {pso_csv}")
    pso_history = load_pso_history(pso_csv)

    print(f"  Iterations: {len(pso_history)}")
    print(f"  Best fitness: {pso_history['best_fitness'].min():.6f}")

    # Generate plot
    print(f"\nGenerating convergence plot...")
    plot_mt6_pso_convergence(pso_history, save_path=output_png, show=False)

    print("="*80)
    print(f"PSO convergence visualization complete!")
    print(f"Output: {output_png}")
    print("="*80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
