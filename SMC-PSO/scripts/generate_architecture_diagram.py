"""
Generate System Architecture Diagram for Thesis
Creates publication-quality PDF figure showing DIP-SMC-PSO system components.

Usage:
    python scripts/generate_architecture_diagram.py

Output:
    academic/paper/thesis/figures/architecture/system_overview.pdf
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

def create_architecture_diagram():
    """Generate system architecture block diagram."""

    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Define colors (professional academic palette)
    color_interface = '#E8F4F8'  # Light blue
    color_controller = '#E8F8E8'  # Light green
    color_plant = '#FFF8E8'      # Light yellow
    color_engine = '#FFE8E8'     # Light red
    color_optimization = '#F8E8FF'  # Light purple
    color_infra = '#F0F0F0'      # Light gray

    # Define box style
    box_style = dict(boxstyle='round,pad=0.3', facecolor='white',
                     edgecolor='black', linewidth=1.5)

    # Helper function to create boxes
    def add_box(x, y, width, height, text, color, fontsize=9):
        """Add a rounded box with text."""
        box = FancyBboxPatch((x, y), width, height,
                            boxstyle='round,pad=0.05',
                            facecolor=color,
                            edgecolor='black',
                            linewidth=1.5,
                            zorder=2)
        ax.add_patch(box)

        # Add text
        lines = text.split('\n')
        y_text = y + height/2 + (len(lines)-1)*0.08
        for line in lines:
            ax.text(x + width/2, y_text, line,
                   ha='center', va='center',
                   fontsize=fontsize, fontweight='bold' if lines.index(line)==0 else 'normal',
                   zorder=3)
            y_text -= 0.16

    def add_arrow(x1, y1, x2, y2, style='->'):
        """Add arrow between boxes."""
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle=style,
                               color='black',
                               linewidth=1.5,
                               mutation_scale=20,
                               zorder=1)
        ax.add_patch(arrow)

    # Title
    ax.text(7, 9.5, 'DIP-SMC-PSO System Architecture',
           ha='center', va='center', fontsize=16, fontweight='bold')

    # Layer 1: User Interfaces (top)
    ax.text(7, 8.8, 'User Interfaces', ha='center', va='center',
           fontsize=11, fontweight='bold', style='italic')
    add_box(1, 8.0, 2.5, 0.6, 'Command Line\nsimulate.py', color_interface, 8)
    add_box(10.5, 8.0, 2.5, 0.6, 'Web Dashboard\nStreamlit App', color_interface, 8)

    # Layer 2: Controller Factory
    ax.text(7, 7.3, 'Controller Layer', ha='center', va='center',
           fontsize=11, fontweight='bold', style='italic')
    add_box(5.5, 6.5, 3, 0.6, 'Controller Factory\nType-safe instantiation', color_controller, 8)

    # Layer 3: SMC Controllers
    add_box(0.5, 5.2, 2.5, 0.6, 'Classical SMC\nBoundary layer', color_controller, 8)
    add_box(4, 5.2, 2.5, 0.6, 'Super-Twisting\nContinuous control', color_controller, 8)
    add_box(7.5, 5.2, 2.5, 0.6, 'Adaptive SMC\nOnline tuning', color_controller, 8)
    add_box(11, 5.2, 2.5, 0.6, 'Hybrid STA-SMC\nBest of both', color_controller, 8)

    # Layer 4: Core Simulation Engine
    ax.text(7, 4.5, 'Core Simulation Engine', ha='center', va='center',
           fontsize=11, fontweight='bold', style='italic')
    add_box(4.5, 3.5, 5, 0.7, 'Simulation Runner\nOrchestration & Context Management', color_engine, 8)

    # Layer 5: Plant Models
    ax.text(2, 2.8, 'Plant Models', ha='center', va='center',
           fontsize=10, fontweight='bold', style='italic')
    add_box(0.3, 1.8, 2, 0.6, 'Simplified\nLinearized', color_plant, 7)
    add_box(2.5, 1.8, 2, 0.6, 'Full Nonlinear\nHigh-fidelity', color_plant, 7)
    add_box(4.7, 1.8, 2, 0.6, 'Low-Rank\nEfficient', color_plant, 7)

    # Layer 6: Supporting Components
    ax.text(10.5, 2.8, 'Optimization & Analysis', ha='center', va='center',
           fontsize=10, fontweight='bold', style='italic')
    add_box(8.5, 2.2, 2, 0.5, 'PSO Tuner\nGain optimization', color_optimization, 7)
    add_box(10.8, 2.2, 2, 0.5, 'Visualization\nPlots & animation', color_optimization, 7)
    add_box(8.5, 1.5, 2, 0.5, 'Cost Functions\nMulti-objective', color_optimization, 7)
    add_box(10.8, 1.5, 2, 0.5, 'Statistics\nMonte Carlo', color_optimization, 7)

    # Layer 7: Infrastructure
    ax.text(7, 0.9, 'Infrastructure', ha='center', va='center',
           fontsize=10, fontweight='bold', style='italic')
    add_box(2, 0.2, 2, 0.5, 'Configuration\nYAML validation', color_infra, 7)
    add_box(5, 0.2, 2, 0.5, 'Monitoring\nPerformance', color_infra, 7)
    add_box(8, 0.2, 2, 0.5, 'Safety Guards\nConstraints', color_infra, 7)
    add_box(11, 0.2, 2, 0.5, 'HIL Interface\nHardware', color_infra, 7)

    # Arrows - Data Flow
    # Interfaces to Factory
    add_arrow(2.5, 8.0, 6.5, 7.1)
    add_arrow(11.5, 8.0, 8.0, 7.1)

    # Factory to Controllers
    add_arrow(6.2, 6.5, 1.8, 5.8)
    add_arrow(6.8, 6.5, 5.2, 5.8)
    add_arrow(7.4, 6.5, 8.7, 5.8)
    add_arrow(8.0, 6.5, 12.2, 5.8)

    # Controllers to Runner
    add_arrow(1.75, 5.2, 5.5, 4.2)
    add_arrow(5.25, 5.2, 6.5, 4.2)
    add_arrow(8.75, 5.2, 7.5, 4.2)
    add_arrow(12.25, 5.2, 8.5, 4.2)

    # Runner to Plant Models
    add_arrow(5.5, 3.5, 1.5, 2.4)
    add_arrow(6.5, 3.5, 3.5, 2.4)
    add_arrow(7.5, 3.5, 5.7, 2.4)

    # Runner to Optimization/Analysis
    add_arrow(9.5, 3.7, 9.5, 2.7)
    add_arrow(9.5, 3.7, 11.8, 2.7)

    # Factory to PSO
    add_arrow(8.5, 6.7, 9.3, 2.7)

    # Infrastructure to Runner
    add_arrow(3.0, 0.7, 5.5, 3.5)
    add_arrow(6.0, 0.7, 6.5, 3.5)
    add_arrow(9.0, 0.7, 7.5, 3.5)
    add_arrow(12.0, 0.7, 8.5, 3.5)

    # Legend
    legend_y = 9.2
    legend_x = 0.3
    legend_items = [
        ('User Interfaces', color_interface),
        ('Controllers', color_controller),
        ('Plant Models', color_plant),
        ('Core Engine', color_engine),
        ('Optimization', color_optimization),
        ('Infrastructure', color_infra)
    ]

    ax.text(legend_x, legend_y + 0.3, 'Legend:', fontsize=9, fontweight='bold')
    for i, (label, color) in enumerate(legend_items):
        y = legend_y - i*0.25
        rect = mpatches.Rectangle((legend_x, y-0.08), 0.3, 0.15,
                                  facecolor=color, edgecolor='black', linewidth=1)
        ax.add_patch(rect)
        ax.text(legend_x + 0.4, y, label, fontsize=7, va='center')

    # Add annotations
    ax.text(7, -0.4, 'System Features: 4 SMC variants, PSO optimization, 3 plant models, Numba acceleration',
           ha='center', va='center', fontsize=8, style='italic', color='gray')

    plt.tight_layout()

    # Save to thesis directory
    output_dir = 'academic/paper/thesis/figures/architecture'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'system_overview.pdf')

    plt.savefig(output_path, format='pdf', dpi=300, bbox_inches='tight')
    print(f"[OK] System architecture diagram saved to: {output_path}")

    # Also save PNG for preview
    png_path = output_path.replace('.pdf', '.png')
    plt.savefig(png_path, format='png', dpi=150, bbox_inches='tight')
    print(f"[INFO] Preview PNG saved to: {png_path}")

    plt.close()

    return output_path

if __name__ == '__main__':
    print("[INFO] Generating system architecture diagram...")
    output = create_architecture_diagram()
    print(f"[OK] Diagram generation complete: {output}")

    # Verify file size
    import os
    size_kb = os.path.getsize(output) / 1024
    print(f"[INFO] File size: {size_kb:.1f} KB")

    if size_kb > 500:
        print(f"[WARNING] File size exceeds 500 KB target ({size_kb:.1f} KB)")
    else:
        print("[OK] File size within target (<500 KB)")
