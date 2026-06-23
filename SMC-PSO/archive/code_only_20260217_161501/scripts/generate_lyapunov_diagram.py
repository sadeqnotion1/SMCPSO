"""
Generate Lyapunov Stability Diagram for Thesis
Creates phase portrait showing sliding surface and trajectory convergence.

Usage:
    python scripts/generate_lyapunov_diagram.py

Output:
    academic/paper/thesis/figures/lyapunov/stability_regions.pdf
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import os

def generate_trajectory(theta0, theta_dot0, lambda1, K, dt=0.001, t_max=2.0):
    """
    Simulate a simple SMC trajectory for visualization.

    Uses simplified dynamics: theta_ddot = -K*sign(s) where s = lambda*theta + theta_dot
    """
    t = np.arange(0, t_max, dt)
    theta = np.zeros_like(t)
    theta_dot = np.zeros_like(t)

    theta[0] = theta0
    theta_dot[0] = theta_dot0

    for i in range(len(t) - 1):
        # Sliding surface
        s = lambda1 * theta[i] + theta_dot[i]

        # Control law (simplified SMC)
        u = -K * np.sign(s)

        # Simplified dynamics: theta_ddot = u (normalized)
        theta_ddot = u

        # Euler integration
        theta_dot[i+1] = theta_dot[i] + theta_ddot * dt
        theta[i+1] = theta[i] + theta_dot[i] * dt

    return theta, theta_dot

def create_lyapunov_diagram():
    """Generate phase portrait with Lyapunov function contours."""

    fig, ax = plt.subplots(figsize=(10, 8))

    # Define parameter
    lambda1 = 5.0  # Sliding surface slope
    K = 10.0       # Control gain

    # Create grid for background
    theta_range = np.linspace(-0.5, 0.5, 100)
    theta_dot_range = np.linspace(-2, 2, 100)
    Theta, Theta_dot = np.meshgrid(theta_range, theta_dot_range)

    # Sliding surface: s = lambda*theta + theta_dot = 0
    # => theta_dot = -lambda*theta
    sliding_line_theta = theta_range
    sliding_line_theta_dot = -lambda1 * theta_range

    # Lyapunov function contours: V = 0.5 * s^2
    S = lambda1 * Theta + Theta_dot
    V = 0.5 * S**2

    # Plot Lyapunov function contours
    contour_levels = [0.1, 0.5, 1.0, 2.0, 4.0, 8.0]
    contours = ax.contour(Theta, Theta_dot, V, levels=contour_levels,
                          colors='lightblue', linewidths=1.5, alpha=0.6)
    ax.clabel(contours, inline=True, fontsize=8, fmt='V=%.1f')

    # Plot sliding surface
    ax.plot(sliding_line_theta, sliding_line_theta_dot, 'g-', linewidth=3,
           label=r'Sliding Surface: $s=\lambda\theta+\dot{\theta}=0$', zorder=5)

    # Shade regions
    ax.fill_between(theta_range, -lambda1*theta_range, 2,
                    where=(theta_range>=0), alpha=0.1, color='red', label='s>0 region')
    ax.fill_between(theta_range, -lambda1*theta_range, -2,
                    where=(theta_range<=0), alpha=0.1, color='blue', label='s<0 region')

    # Generate multiple trajectories
    initial_conditions = [
        (0.4, 1.5),
        (0.3, -1.2),
        (-0.3, 1.8),
        (-0.4, -1.0),
        (0.2, 0.5),
        (-0.2, -0.5),
        (0.45, 0.2),
    ]

    for i, (theta0, theta_dot0) in enumerate(initial_conditions):
        theta, theta_dot = generate_trajectory(theta0, theta_dot0, lambda1, K)

        # Plot trajectory
        ax.plot(theta, theta_dot, 'b-', linewidth=1.5, alpha=0.7, zorder=3)

        # Mark initial point
        ax.plot(theta[0], theta_dot[0], 'ro', markersize=8, zorder=4)

        # Add arrow to show direction
        if len(theta) > 100:
            idx = len(theta) // 3
            dx = theta[idx+10] - theta[idx]
            dy = theta_dot[idx+10] - theta_dot[idx]
            ax.arrow(theta[idx], theta_dot[idx], dx*10, dy*10,
                    head_width=0.08, head_length=0.06, fc='blue', ec='blue',
                    alpha=0.7, zorder=3)

    # Add annotations
    ax.text(0.35, -0.5, 'Reaching Phase\n(trajectories approach s=0)',
           ha='center', va='center', fontsize=10, style='italic',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

    ax.text(0, 0.15, 'Sliding Phase\n(motion along s=0)',
           ha='center', va='center', fontsize=10, style='italic',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7))

    ax.text(-0.45, 1.7, r'$s>0$: $u=-K$ (pushes down)', ha='left', va='center',
           fontsize=9, color='red')
    ax.text(0.28, -1.7, r'$s<0$: $u=+K$ (pushes up)', ha='left', va='center',
           fontsize=9, color='blue')

    # Formatting
    ax.set_xlabel(r'Angle $\theta$ (rad)', fontsize=12, fontweight='bold')
    ax.set_ylabel(r'Angular Velocity $\dot{\theta}$ (rad/s)', fontsize=12, fontweight='bold')
    ax.set_title(r'Lyapunov Stability Analysis: Phase Portrait with Sliding Surface',
                fontsize=14, fontweight='bold', pad=15)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.axvline(x=0, color='k', linewidth=0.5)
    ax.set_xlim([-0.5, 0.5])
    ax.set_ylim([-2, 2])
    ax.legend(loc='upper right', fontsize=9)

    # Add parameter box
    param_text = (f'Parameters:\n'
                 f'$\\lambda = {lambda1:.1f}$\n'
                 f'$K = {K:.1f}$\n'
                 r'$V(\mathbf{x}) = \frac{1}{2}s^2$')
    ax.text(0.02, 0.98, param_text,
           transform=ax.transAxes,
           fontsize=9,
           verticalalignment='top',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='black'))

    plt.tight_layout()

    # Save
    output_dir = 'academic/paper/thesis/figures/lyapunov'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'stability_regions.pdf')

    plt.savefig(output_path, format='pdf', dpi=300, bbox_inches='tight')
    print(f"[OK] Lyapunov stability diagram saved to: {output_path}")

    # Also save PNG preview
    png_path = output_path.replace('.pdf', '.png')
    plt.savefig(png_path, format='png', dpi=150, bbox_inches='tight')
    print(f"[INFO] Preview PNG saved to: {png_path}")

    plt.close()

    return output_path

if __name__ == '__main__':
    print("[INFO] Generating Lyapunov stability diagram...")
    output = create_lyapunov_diagram()
    print(f"[OK] Diagram generation complete: {output}")

    # Verify file size
    size_kb = os.path.getsize(output) / 1024
    print(f"[INFO] File size: {size_kb:.1f} KB")

    if size_kb > 500:
        print(f"[WARNING] File size exceeds 500 KB target ({size_kb:.1f} KB)")
    else:
        print("[OK] File size within target (<500 KB)")
