"""
================================================================================
PSO Convergence Visualization Module
================================================================================

Provides plotting utilities for analyzing Particle Swarm Optimization (PSO)
convergence behavior, including:
- Best cost history over iterations
- Swarm diversity (position spread) over time
- Combined summary plots

Author: DIP_SMC_PSO Team
Created: October 2025 (Week 1, Task QW-3)
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple
from pathlib import Path


def plot_convergence(
    fitness_history: np.ndarray,
    save_path: Optional[str] = None,
    show: bool = True,
    title: str = "PSO Convergence"
) -> None:
    """
    Plot PSO best cost convergence over iterations.

    Parameters
    ----------
    fitness_history : np.ndarray
        Array of best costs per iteration, shape (n_iters,)
    save_path : str, optional
        Path to save plot (PNG). If None, plot not saved.
    show : bool, optional
        Whether to display plot interactively (default: True)
    title : str, optional
        Plot title

    Examples
    --------
    >>> fitness = np.array([100.0, 50.0, 25.0, 10.0, 5.0, 2.5, 1.0, 0.5, 0.1, 0.01])
    >>> plot_convergence(fitness, save_path="convergence.png", show=False)
    """
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    iterations = np.arange(len(fitness_history))

    # Plot convergence curve
    ax.plot(iterations, fitness_history, 'b-', linewidth=2, label='Best Cost')
    ax.scatter(iterations[::max(1, len(iterations)//20)],
               fitness_history[::max(1, len(iterations)//20)],
               c='red', s=50, zorder=5, alpha=0.6, label='Sampled Points')

    # Formatting
    ax.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax.set_ylabel('Best Cost', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', fontsize=10)

    # Log scale if cost spans multiple orders of magnitude
    if len(fitness_history) > 0:
        cost_range = np.max(fitness_history) / (np.min(fitness_history) + 1e-12)
        if cost_range > 100:
            ax.set_yscale('log')
            ax.set_ylabel('Best Cost (log scale)', fontsize=12, fontweight='bold')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Convergence plot saved to: {save_path}")

    if show:
        plt.show()
    else:
        plt.close()


def plot_diversity(
    position_history: np.ndarray,
    save_path: Optional[str] = None,
    show: bool = True,
    title: str = "PSO Swarm Diversity"
) -> None:
    """
    Plot swarm diversity (position spread) over iterations.

    Diversity is measured as the average standard deviation of particle
    positions across all dimensions. High diversity indicates exploration,
    low diversity indicates exploitation/convergence.

    Parameters
    ----------
    position_history : np.ndarray
        Array of particle positions over iterations, shape (n_iters, n_particles, n_dims)
        OR (n_iters, n_dims) for best position history only
    save_path : str, optional
        Path to save plot (PNG). If None, plot not saved.
    show : bool, optional
        Whether to display plot interactively (default: True)
    title : str, optional
        Plot title

    Examples
    --------
    >>> positions = np.random.randn(100, 30, 6)  # 100 iters, 30 particles, 6 dims
    >>> plot_diversity(positions, save_path="diversity.png", show=False)
    """
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    # Handle both full swarm history and best position history
    if position_history.ndim == 3:
        # Full swarm: (n_iters, n_particles, n_dims)
        # Compute diversity as mean standard deviation across dimensions
        diversity = np.mean(np.std(position_history, axis=1), axis=1)
        ylabel = 'Mean Std Dev (All Dimensions)'
    elif position_history.ndim == 2:
        # Best position only: (n_iters, n_dims)
        # Compute diversity as std dev of best position movement
        diversity = np.std(position_history, axis=1)
        ylabel = 'Std Dev of Best Position'
    else:
        raise ValueError(f"position_history must be 2D or 3D, got shape {position_history.shape}")

    iterations = np.arange(len(diversity))

    # Plot diversity curve
    ax.plot(iterations, diversity, 'g-', linewidth=2, label='Swarm Diversity')
    ax.fill_between(iterations, 0, diversity, alpha=0.3, color='green')

    # Formatting
    ax.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', fontsize=10)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Diversity plot saved to: {save_path}")

    if show:
        plt.show()
    else:
        plt.close()


def plot_pso_summary(
    fitness_history: np.ndarray,
    position_history: Optional[np.ndarray] = None,
    save_path: Optional[str] = None,
    show: bool = True
) -> None:
    """
    Generate combined PSO summary plot with convergence and diversity.

    Creates a 2-subplot figure with:
    - Top: Best cost convergence over iterations
    - Bottom: Swarm diversity over iterations (if position_history provided)

    Parameters
    ----------
    fitness_history : np.ndarray
        Array of best costs per iteration, shape (n_iters,)
    position_history : np.ndarray, optional
        Array of particle positions, shape (n_iters, n_particles, n_dims) or (n_iters, n_dims)
        If None, only convergence plot is shown
    save_path : str, optional
        Path to save plot (PNG). If None, plot not saved.
    show : bool, optional
        Whether to display plot interactively (default: True)

    Examples
    --------
    >>> fitness = np.logspace(2, -2, 100)  # 100 iterations, cost 100 → 0.01
    >>> positions = np.random.randn(100, 30, 6)  # 30 particles, 6 dims
    >>> plot_pso_summary(fitness, positions, save_path="pso_summary.png", show=False)
    """
    if position_history is not None:
        # Two subplots: convergence + diversity
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), dpi=300)
    else:
        # Single subplot: convergence only
        fig, ax1 = plt.subplots(1, 1, figsize=(10, 6), dpi=300)

    iterations = np.arange(len(fitness_history))

    # ==================== Convergence Plot ====================
    ax1.plot(iterations, fitness_history, 'b-', linewidth=2, label='Best Cost')
    ax1.scatter(iterations[::max(1, len(iterations)//20)],
                fitness_history[::max(1, len(iterations)//20)],
                c='red', s=50, zorder=5, alpha=0.6, label='Sampled Points')

    ax1.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Best Cost', fontsize=12, fontweight='bold')
    ax1.set_title('PSO Convergence', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='upper right', fontsize=10)

    # Log scale if needed
    if len(fitness_history) > 0:
        cost_range = np.max(fitness_history) / (np.min(fitness_history) + 1e-12)
        if cost_range > 100:
            ax1.set_yscale('log')
            ax1.set_ylabel('Best Cost (log scale)', fontsize=12, fontweight='bold')

    # ==================== Diversity Plot ====================
    if position_history is not None:
        # Compute diversity
        if position_history.ndim == 3:
            diversity = np.mean(np.std(position_history, axis=1), axis=1)
            ylabel = 'Mean Std Dev (All Dimensions)'
        elif position_history.ndim == 2:
            diversity = np.std(position_history, axis=1)
            ylabel = 'Std Dev of Best Position'
        else:
            raise ValueError(f"position_history must be 2D or 3D, got shape {position_history.shape}")

        ax2.plot(iterations, diversity, 'g-', linewidth=2, label='Swarm Diversity')
        ax2.fill_between(iterations, 0, diversity, alpha=0.3, color='green')

        ax2.set_xlabel('Iteration', fontsize=12, fontweight='bold')
        ax2.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax2.set_title('Swarm Diversity Over Time', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.legend(loc='upper right', fontsize=10)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"PSO summary plot saved to: {save_path}")

    if show:
        plt.show()
    else:
        plt.close()
