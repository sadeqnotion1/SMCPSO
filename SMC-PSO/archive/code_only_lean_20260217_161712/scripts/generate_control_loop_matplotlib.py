"""
Generate Control Loop Schematic using Matplotlib
Creates publication-quality PDF showing detailed SMC control flow.

Usage:
    python scripts/generate_control_loop_matplotlib.py

Output:
    academic/paper/thesis/figures/schematics/control_loop.pdf
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import os

def create_control_loop_schematic():
    """Generate control loop schematic using matplotlib."""

    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Define colors
    color_measurement = '#E8F4F8'
    color_surface = '#E8F8E8'
    color_control = '#FFF8DC'
    color_sat = '#FFE8CC'
    color_plant = '#FFE8F0'
    color_integration = '#E8E8FF'

    # Helper functions
    def add_block(x, y, width, height, text, color, fontsize=9):
        """Add a rounded box with text."""
        box = FancyBboxPatch((x, y), width, height,
                            boxstyle='round,pad=0.05',
                            facecolor=color,
                            edgecolor='black',
                            linewidth=2,
                            zorder=2)
        ax.add_patch(box)

        # Add text - handle multiline
        lines = text.split('\n')
        y_text = y + height/2 + (len(lines)-1)*0.12
        for i, line in enumerate(lines):
            # Check if line contains math ($ symbols)
            if '$' in line:
                ax.text(x + width/2, y_text, line,
                       ha='center', va='center',
                       fontsize=fontsize-1,
                       math_fontfamily='cm',
                       zorder=3)
            else:
                weight = 'bold' if i == 0 else 'normal'
                ax.text(x + width/2, y_text, line,
                       ha='center', va='center',
                       fontsize=fontsize, fontweight=weight,
                       zorder=3)
            y_text -= 0.24

    def add_circle(x, y, radius, label, color):
        """Add a circle (summing junction)."""
        circle = Circle((x, y), radius,
                       facecolor=color,
                       edgecolor='black',
                       linewidth=2,
                       zorder=2)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center',
               fontsize=11, fontweight='bold', zorder=3)

    def add_arrow(x1, y1, x2, y2, label='', style='->'):
        """Add arrow with optional label."""
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle=style,
                               color='black',
                               linewidth=2,
                               mutation_scale=25,
                               zorder=1)
        ax.add_patch(arrow)
        if label:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mid_x, mid_y + 0.15, label,
                   ha='center', va='bottom',
                   fontsize=8, style='italic',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

    # Title
    ax.text(8, 9.5, 'Sliding Mode Control Loop - Double-Inverted Pendulum',
           ha='center', va='center', fontsize=16, fontweight='bold')

    # Reference Input
    ax.text(0.5, 7, r'$\theta_1^d=0$', ha='center', va='center', fontsize=10)
    ax.text(0.5, 6.7, r'$\theta_2^d=0$', ha='center', va='center', fontsize=10)
    ax.text(0.5, 6.35, r'Reference', ha='center', va='center', fontsize=8, style='italic')

    # State Measurement Block
    add_block(1.5, 6.2, 2.2, 1.2,
             'State\nMeasurement\n$\\mathbf{x} = [x, \\theta_1, \\theta_2,$\n$\\dot{x}, \\dot{\\theta}_1, \\dot{\\theta}_2]^T$',
             color_measurement, 8)

    # Summing Junction
    add_circle(5, 6.8, 0.25, '−', '#FFE8E8')

    # Sliding Surface Block
    add_block(6.2, 6.2, 2.2, 1.2,
             'Sliding Surface\n$s_1 = \\lambda_1\\theta_1 + \\dot{\\theta}_1$\n$s_2 = \\lambda_2\\theta_2 + \\dot{\\theta}_2$',
             color_surface, 8)

    # Controller Block (with variants)
    add_block(9.5, 5.8, 3.2, 2.0,
             'Control Law\nClassical: $u=-K\\,\\mathrm{sign}(s)$\nSTA: $u=-K_1|s|^{1/2}\\mathrm{sgn}(s)-K_2\\int\\mathrm{sgn}(s)dt$\nAdaptive: $\\hat{K}(t)=\\gamma\\int|s|dt$\nHybrid: Combines STA + Adaptive',
             color_control, 7)

    # Saturation & Boundary Layer
    add_block(13.5, 6.2, 1.8, 1.2,
             'Saturation\n$u=\\mathrm{sat}(u_r,F_{max})$\n$F_{max}=150$ N',
             color_sat, 8)

    # Plant Dynamics Block
    add_block(10.5, 2.5, 4, 1.8,
             'DIP Dynamics\n$M(\\mathbf{q})\\ddot{\\mathbf{q}}+C(\\mathbf{q},\\dot{\\mathbf{q}})\\dot{\\mathbf{q}}+G(\\mathbf{q})=Bu$\nwhere $\\mathbf{q}=[x,\\theta_1,\\theta_2]^T$\nIntegration: RK45, $\\Delta t=0.001$ s',
             color_plant, 8)

    # Integration Block
    add_block(10.5, 0.5, 4, 1.2,
             'Numerical Integration\n$\\dot{\\mathbf{x}}=f(\\mathbf{x},u,t)$\nRunge-Kutta 4th order',
             color_integration, 8)

    # Arrows - Forward path
    add_arrow(0.8, 6.8, 1.5, 6.8, r'$\theta_d$')
    add_arrow(3.7, 6.8, 4.75, 6.8, r'$\mathbf{x}$')
    add_arrow(5.25, 6.8, 6.2, 6.8, r'$e$')
    add_arrow(8.4, 6.8, 9.5, 6.8, r'$s$')
    add_arrow(12.7, 6.8, 13.5, 6.8, r'$u_r$')

    # Arrow from saturation to plant (vertical then horizontal)
    add_arrow(14.4, 6.2, 14.4, 4.3, r'$u$')
    add_arrow(14.4, 3.4, 14.5, 3.4)

    # Arrow from plant to integration
    add_arrow(12.5, 2.5, 12.5, 1.7, r'$\ddot{\mathbf{q}}$')

    # Arrow from integration downward
    ax.arrow(12.5, 0.5, 0, -0.3, head_width=0.15, head_length=0.1,
             fc='black', ec='black', linewidth=2, zorder=1)
    ax.text(12.5, -0.05, r'$\mathbf{x}(t)$', ha='center', va='top', fontsize=9, style='italic')

    # Feedback path (bottom to left)
    # Horizontal line from integration output
    add_arrow(10.5, 1.1, 1, 1.1, '', '->')
    # Vertical line up to measurement
    add_arrow(1.5, 1.1, 1.5, 6.2, '', '->')
    ax.text(0.7, 3.5, 'Feedback', ha='center', va='center', fontsize=9,
           rotation=90, style='italic',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.6))

    # PSO Optimization Annotation (side)
    pso_box = FancyBboxPatch((5, 8.5), 3, 0.9,
                            boxstyle='round,pad=0.05',
                            facecolor='#FFFFCC',
                            edgecolor='blue',
                            linewidth=1.5,
                            linestyle='dashed',
                            zorder=2)
    ax.add_patch(pso_box)
    ax.text(6.5, 9.15, 'PSO Optimization (Offline)', ha='center', va='center',
           fontsize=9, fontweight='bold')
    ax.text(6.5, 8.85, r'Tunes: $K, \lambda, k_d$ gains', ha='center', va='center',
           fontsize=7.5)
    ax.text(6.5, 8.6, '30 particles × 50 iterations', ha='center', va='center',
           fontsize=7)

    # Arrow from PSO to controller
    add_arrow(7.5, 8.5, 11, 7.8, '', '->')
    ax.text(9, 8.3, 'Optimized\ngains', ha='center', va='center',
           fontsize=7, style='italic')

    # Key Parameters Box
    param_box = FancyBboxPatch((0.2, 0.2), 4.5, 1.8,
                              boxstyle='round,pad=0.05',
                              facecolor='#F5F5F5',
                              edgecolor='gray',
                              linewidth=1.5,
                              zorder=2)
    ax.add_patch(param_box)
    ax.text(2.45, 1.85, 'Key Parameters', ha='center', va='center',
           fontsize=10, fontweight='bold')
    params_text = r'''$\lambda_1, \lambda_2$: Surface slopes
$K, K_1, K_2$: Control gains
$\gamma$: Adaptation rate
$\varepsilon$: Boundary layer thickness
$\Delta t = 0.001$ s: Sample time
$F_{max} = 150$ N: Force saturation'''
    ax.text(2.45, 1.0, params_text, ha='center', va='center',
           fontsize=7.5, family='monospace')

    # Legend
    ax.text(0.3, 4.8, 'Legend:', fontsize=9, fontweight='bold')
    legend_items = [
        ('Measurement', color_measurement),
        ('Sliding Surface', color_surface),
        ('Controller', color_control),
        ('Saturation', color_sat),
        ('Plant Dynamics', color_plant),
        ('Integration', color_integration)
    ]
    for i, (label, color) in enumerate(legend_items):
        y = 4.5 - i*0.3
        rect = mpatches.Rectangle((0.3, y-0.1), 0.4, 0.18,
                                  facecolor=color, edgecolor='black', linewidth=1)
        ax.add_patch(rect)
        ax.text(0.85, y, label, fontsize=7, va='center')

    plt.tight_layout()

    # Save
    output_dir = 'academic/paper/thesis/figures/schematics'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'control_loop.pdf')

    plt.savefig(output_path, format='pdf', dpi=300, bbox_inches='tight')
    print(f"[OK] Control loop schematic saved to: {output_path}")

    # Also save PNG preview
    png_path = output_path.replace('.pdf', '.png')
    plt.savefig(png_path, format='png', dpi=150, bbox_inches='tight')
    print(f"[INFO] Preview PNG saved to: {png_path}")

    plt.close()

    return output_path

if __name__ == '__main__':
    print("[INFO] Generating control loop schematic...")
    output = create_control_loop_schematic()
    print(f"[OK] Schematic generation complete: {output}")

    # Verify file size
    size_kb = os.path.getsize(output) / 1024
    print(f"[INFO] File size: {size_kb:.1f} KB")

    if size_kb > 500:
        print(f"[WARNING] File size exceeds 500 KB target ({size_kb:.1f} KB)")
    else:
        print("[OK] File size within target (<500 KB)")
