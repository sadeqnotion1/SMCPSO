"""
Generate PSO Theory Diagrams for Chapter 7

Creates pedagogical visualizations of PSO algorithm mechanics:
1. Particle swarm movement in 2D parameter space
2. Velocity update components (inertia, cognitive, social)
3. Exploration vs exploitation with varying inertia weights
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
from matplotlib.colors import LinearSegmentedColormap
import os

# Configure matplotlib for publication-quality figures
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

# Output directory
output_dir = "figures/ch07_pso_theory"
os.makedirs(output_dir, exist_ok=True)

# ============================================================================
# Figure 1: PSO Particle Swarm Movement in 2D Parameter Space
# ============================================================================

def sphere_function(x, y):
    """Simple 2D sphere function for demonstration"""
    return x**2 + y**2

def create_pso_swarm_visualization():
    """Show particles moving toward global best in 2D parameter space"""
    fig, ax = plt.subplots(figsize=(8, 6))

    # Create fitness landscape (sphere function)
    x = np.linspace(-5, 5, 100)
    y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x, y)
    Z = sphere_function(X, Y)

    # Plot contours
    contour = ax.contour(X, Y, Z, levels=15, cmap='viridis', alpha=0.3)
    ax.clabel(contour, inline=True, fontsize=8, fmt='%1.0f')

    # Define particles at two time steps
    np.random.seed(42)
    n_particles = 8

    # Initial positions (scattered)
    particles_t0 = np.random.uniform(-4, 4, (n_particles, 2))

    # Velocities pointing toward global optimum (0, 0)
    global_best = np.array([0.3, -0.2])  # Slightly offset for visualization
    velocities = (global_best - particles_t0) * 0.3 + np.random.normal(0, 0.2, (n_particles, 2))

    # Next positions
    particles_t1 = particles_t0 + velocities

    # Plot particles at t=0
    ax.scatter(particles_t0[:, 0], particles_t0[:, 1], c='blue', s=80,
               marker='o', label='Particles at $t$', zorder=5, edgecolors='black', linewidths=1.5)

    # Plot particles at t=1 (lighter color)
    ax.scatter(particles_t1[:, 0], particles_t1[:, 1], c='lightblue', s=60,
               marker='o', label='Particles at $t+1$', zorder=4, edgecolors='gray', linewidths=1)

    # Plot velocity vectors
    for i in range(n_particles):
        arrow = FancyArrowPatch(particles_t0[i], particles_t1[i],
                               arrowstyle='->', mutation_scale=15,
                               linewidth=1.5, color='red', alpha=0.7, zorder=3)
        ax.add_patch(arrow)

    # Mark global best
    ax.scatter([global_best[0]], [global_best[1]], c='gold', s=200,
               marker='*', label='Global Best $\\mathbf{g}$', zorder=6,
               edgecolors='orange', linewidths=2)

    # Personal bests (scattered near particles)
    personal_bests = particles_t0 + np.random.normal(0, 0.5, (n_particles, 2))
    ax.scatter(personal_bests[:, 0], personal_bests[:, 1], c='green', s=60,
               marker='s', label='Personal Bests $\\mathbf{p}_i$', zorder=4,
               edgecolors='darkgreen', linewidths=1)

    ax.set_xlabel('Gain $k_1$')
    ax.set_ylabel('Gain $k_2$')
    ax.set_title('PSO Particle Swarm Movement in 2D Parameter Space')
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/pso_swarm_movement.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Created {output_dir}/pso_swarm_movement.png")

# ============================================================================
# Figure 2: PSO Velocity Update Components
# ============================================================================

def create_velocity_update_diagram():
    """Visualize the three components of PSO velocity update"""
    fig, ax = plt.subplots(figsize=(9, 7))

    # Current particle position
    x_i = np.array([2.0, 1.5])

    # Personal best
    p_i = np.array([3.5, 3.0])

    # Global best
    g = np.array([4.5, 2.5])

    # Current velocity (inertia component)
    v_i = np.array([0.8, 0.4])

    # Cognitive component: toward personal best
    cognitive = 0.6 * (p_i - x_i)

    # Social component: toward global best
    social = 0.5 * (g - x_i)

    # Inertia component: scaled current velocity
    inertia = 0.7 * v_i

    # New velocity: sum of components
    v_new = inertia + cognitive + social

    # Plot components
    origin = x_i

    # Inertia (blue)
    ax.arrow(origin[0], origin[1], inertia[0], inertia[1],
             head_width=0.15, head_length=0.12, fc='blue', ec='blue',
             linewidth=2, label='Inertia: $w \\mathbf{v}_i(t)$', zorder=3)

    # Cognitive (green) - start from end of inertia
    cog_start = origin + inertia
    ax.arrow(cog_start[0], cog_start[1], cognitive[0], cognitive[1],
             head_width=0.15, head_length=0.12, fc='green', ec='green',
             linewidth=2, label='Cognitive: $c_1 r_1 (\\mathbf{p}_i - \\mathbf{x}_i)$', zorder=3)

    # Social (red) - start from end of cognitive
    soc_start = cog_start + cognitive
    ax.arrow(soc_start[0], soc_start[1], social[0], social[1],
             head_width=0.15, head_length=0.12, fc='red', ec='red',
             linewidth=2, label='Social: $c_2 r_2 (\\mathbf{g} - \\mathbf{x}_i)$', zorder=3)

    # Resultant velocity (black dashed)
    ax.arrow(origin[0], origin[1], v_new[0], v_new[1],
             head_width=0.18, head_length=0.15, fc='black', ec='black',
             linewidth=2.5, linestyle='--', alpha=0.7,
             label='New Velocity: $\\mathbf{v}_i(t+1)$', zorder=4)

    # Mark key points
    ax.scatter([x_i[0]], [x_i[1]], c='blue', s=150, marker='o',
               edgecolors='black', linewidths=2, zorder=5, label='Current Position $\\mathbf{x}_i(t)$')
    ax.scatter([p_i[0]], [p_i[1]], c='green', s=150, marker='s',
               edgecolors='darkgreen', linewidths=2, zorder=5, label='Personal Best $\\mathbf{p}_i$')
    ax.scatter([g[0]], [g[1]], c='gold', s=250, marker='*',
               edgecolors='orange', linewidths=2, zorder=6, label='Global Best $\\mathbf{g}$')

    # Annotations
    ax.annotate('$\\mathbf{x}_i(t)$', xy=x_i, xytext=(x_i[0]-0.7, x_i[1]-0.5),
                fontsize=12, fontweight='bold')
    ax.annotate('$\\mathbf{p}_i$', xy=p_i, xytext=(p_i[0]+0.2, p_i[1]+0.3),
                fontsize=12, fontweight='bold', color='darkgreen')
    ax.annotate('$\\mathbf{g}$', xy=g, xytext=(g[0]+0.2, g[1]+0.3),
                fontsize=12, fontweight='bold', color='orange')

    ax.set_xlabel('Parameter Dimension 1')
    ax.set_ylabel('Parameter Dimension 2')
    ax.set_title('PSO Velocity Update: Three-Component Decomposition')
    ax.legend(loc='upper left', framealpha=0.95, fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0.5, 6.5)
    ax.set_ylim(0, 5)
    ax.set_aspect('equal')

    plt.tight_layout()
    plt.savefig(f"{output_dir}/pso_velocity_components.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Created {output_dir}/pso_velocity_components.png")

# ============================================================================
# Figure 3: Exploration vs Exploitation (Inertia Weight Effect)
# ============================================================================

def create_exploration_exploitation_diagram():
    """Show how inertia weight affects exploration vs exploitation"""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    # Define fitness landscape
    x = np.linspace(-5, 5, 100)
    y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x, y)
    Z = sphere_function(X, Y)

    # Three scenarios: high, medium, low inertia
    inertia_weights = [0.9, 0.6, 0.3]
    titles = ['High Inertia ($w=0.9$): Exploration',
              'Medium Inertia ($w=0.6$): Balance',
              'Low Inertia ($w=0.3$): Exploitation']

    global_best = np.array([0.5, -0.3])

    for idx, (w, title) in enumerate(zip(inertia_weights, titles)):
        ax = axes[idx]

        # Plot contours
        contour = ax.contour(X, Y, Z, levels=12, cmap='viridis', alpha=0.3)

        # Simulate particle trajectories with different inertia
        np.random.seed(42 + idx)
        n_particles = 6
        particles = np.random.uniform(-4, 4, (n_particles, 2))
        velocities = np.random.normal(0, 1, (n_particles, 2))

        # Run 10 steps
        trajectory = [particles.copy()]
        for _ in range(10):
            # PSO update
            cognitive = 1.5 * np.random.rand(n_particles, 2) * (global_best - particles)
            social = 1.5 * np.random.rand(n_particles, 2) * (global_best - particles)
            velocities = w * velocities + cognitive + social
            particles = particles + velocities * 0.3  # Scale down for visualization
            trajectory.append(particles.copy())

        # Plot trajectories
        trajectory = np.array(trajectory)
        for i in range(n_particles):
            ax.plot(trajectory[:, i, 0], trajectory[:, i, 1],
                   'o-', alpha=0.6, linewidth=1.5, markersize=4)

        # Mark start and end
        ax.scatter(trajectory[0, :, 0], trajectory[0, :, 1],
                  c='blue', s=80, marker='o', edgecolors='black',
                  linewidths=1.5, zorder=5, label='Start')
        ax.scatter(trajectory[-1, :, 0], trajectory[-1, :, 1],
                  c='red', s=80, marker='s', edgecolors='darkred',
                  linewidths=1.5, zorder=5, label='End')

        # Mark global best
        ax.scatter([global_best[0]], [global_best[1]], c='gold', s=200,
                  marker='*', zorder=6, edgecolors='orange', linewidths=2)

        ax.set_xlabel('Gain $k_1$')
        ax.set_ylabel('Gain $k_2$')
        ax.set_title(title, fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        if idx == 0:
            ax.legend(loc='upper right', fontsize=8)

    fig.suptitle('Effect of Inertia Weight on PSO Search Behavior',
                fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/pso_inertia_effect.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Created {output_dir}/pso_inertia_effect.png")

# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    print("[INFO] Generating PSO theory diagrams for Chapter 7...")
    print()

    create_pso_swarm_visualization()
    create_velocity_update_diagram()
    create_exploration_exploitation_diagram()

    print()
    print("[OK] All 3 PSO theory diagrams created successfully!")
    print(f"[INFO] Output directory: {output_dir}/")
    print()
    print("Files created:")
    print("  1. pso_swarm_movement.png - Particle swarm in 2D parameter space")
    print("  2. pso_velocity_components.png - Three-component velocity update")
    print("  3. pso_inertia_effect.png - Exploration vs exploitation")
