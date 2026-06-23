"""
Generate DIP System Overview Diagram

Creates a high-level system architecture diagram showing:
- Physical DIP plant
- Sensors (encoders for angles, position)
- Controller (SMC/STA/Adaptive/Hybrid)
- Actuator (motor applying force u)
- Feedback loop with signal flow
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import os

# Configure matplotlib
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'serif'

# Output file
output_file = "figures/ch01_introduction/system_overview.png"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Create figure
fig, ax = plt.subplots(figsize=(12, 8))

# ============================================================================
# Define component positions
# ============================================================================

# Reference position (desired state)
ref_x, ref_y = 1, 6

# Controller
ctrl_x, ctrl_y = 3, 6
ctrl_w, ctrl_h = 2.5, 1.2

# Actuator
act_x, act_y = 7, 6
act_w, act_h = 1.8, 1.0

# Plant (DIP system)
plant_x, plant_y = 10, 4
plant_w, plant_h = 2.5, 4

# Sensors
sens_x, sens_y = 7, 2
sens_w, sens_h = 1.8, 1.0

# ============================================================================
# Draw components
# ============================================================================

# Reference input (circle)
ref_circle = Circle((ref_x, ref_y), 0.4, facecolor='lightgreen',
                    edgecolor='darkgreen', linewidth=2.5)
ax.add_patch(ref_circle)
ax.text(ref_x, ref_y, r'$\mathbf{r}$', fontsize=14, fontweight='bold',
        ha='center', va='center')
ax.text(ref_x, ref_y - 0.9, 'Reference\n(upright)', fontsize=10,
        ha='center', style='italic')

# Controller box
ctrl_box = FancyBboxPatch((ctrl_x, ctrl_y), ctrl_w, ctrl_h,
                         boxstyle="round,pad=0.1",
                         facecolor='lightblue', edgecolor='blue', linewidth=2.5)
ax.add_patch(ctrl_box)
ax.text(ctrl_x + ctrl_w/2, ctrl_y + ctrl_h/2 + 0.25, 'Controller',
        fontsize=12, fontweight='bold', ha='center')
ax.text(ctrl_x + ctrl_w/2, ctrl_y + ctrl_h/2 - 0.25, 'SMC/STA/Adaptive',
        fontsize=9, ha='center', style='italic')

# Actuator box
act_box = FancyBboxPatch((act_x, act_y), act_w, act_h,
                        boxstyle="round,pad=0.08",
                        facecolor='lightyellow', edgecolor='orange', linewidth=2.5)
ax.add_patch(act_box)
ax.text(act_x + act_w/2, act_y + act_h/2 + 0.2, 'Actuator',
        fontsize=12, fontweight='bold', ha='center')
ax.text(act_x + act_w/2, act_y + act_h/2 - 0.2, 'Motor',
        fontsize=9, ha='center', style='italic')

# Plant box (larger, with internal DIP sketch)
plant_box = FancyBboxPatch((plant_x, plant_y), plant_w, plant_h,
                          boxstyle="round,pad=0.1",
                          facecolor='lightcoral', edgecolor='darkred', linewidth=3)
ax.add_patch(plant_box)
ax.text(plant_x + plant_w/2, plant_y + plant_h - 0.5, 'Plant',
        fontsize=13, fontweight='bold', ha='center')
ax.text(plant_x + plant_w/2, plant_y + plant_h - 1.0, 'Double-Inverted',
        fontsize=10, ha='center')
ax.text(plant_x + plant_w/2, plant_y + plant_h - 1.4, 'Pendulum',
        fontsize=10, ha='center')

# Simple DIP sketch inside plant box
dip_base_x = plant_x + plant_w/2
dip_base_y = plant_y + 0.8
dip_h1 = 1.2
dip_h2 = 0.9
# Cart
ax.add_patch(Rectangle((dip_base_x - 0.3, dip_base_y), 0.6, 0.3,
                       facecolor='gray', edgecolor='black', linewidth=1))
# Link 1
ax.plot([dip_base_x, dip_base_x + 0.3], [dip_base_y + 0.3, dip_base_y + 0.3 + dip_h1],
        'k-', linewidth=4)
# Link 2
ax.plot([dip_base_x + 0.3, dip_base_x + 0.5],
        [dip_base_y + 0.3 + dip_h1, dip_base_y + 0.3 + dip_h1 + dip_h2],
        'k-', linewidth=4)
# Joints
ax.plot([dip_base_x, dip_base_x + 0.3, dip_base_x + 0.5],
        [dip_base_y + 0.3, dip_base_y + 0.3 + dip_h1, dip_base_y + 0.3 + dip_h1 + dip_h2],
        'ko', markersize=6)

# State annotation in plant
ax.text(plant_x + plant_w/2, plant_y + 0.3,
        r'$\mathbf{x} = [x, \theta_1, \theta_2, \dot{x}, \dot{\theta}_1, \dot{\theta}_2]^T$',
        fontsize=8, ha='center', style='italic')

# Sensors box
sens_box = FancyBboxPatch((sens_x, sens_y), sens_w, sens_h,
                         boxstyle="round,pad=0.08",
                         facecolor='lightgray', edgecolor='gray', linewidth=2.5)
ax.add_patch(sens_box)
ax.text(sens_x + sens_w/2, sens_y + sens_h/2 + 0.2, 'Sensors',
        fontsize=12, fontweight='bold', ha='center')
ax.text(sens_x + sens_w/2, sens_y + sens_h/2 - 0.2, 'Encoders',
        fontsize=9, ha='center', style='italic')

# ============================================================================
# Draw signal flow arrows
# ============================================================================

# Reference to controller (error signal)
arrow1 = FancyArrowPatch((ref_x + 0.5, ref_y), (ctrl_x, ctrl_y + ctrl_h/2),
                        arrowstyle='->', mutation_scale=25, linewidth=2.5,
                        color='green')
ax.add_patch(arrow1)
ax.text(2.2, ref_y + 0.3, r'$e = \mathbf{r} - \mathbf{x}$',
        fontsize=10, fontweight='bold', color='green')

# Controller to actuator (control signal)
arrow2 = FancyArrowPatch((ctrl_x + ctrl_w, ctrl_y + ctrl_h/2),
                        (act_x, act_y + act_h/2),
                        arrowstyle='->', mutation_scale=25, linewidth=2.5,
                        color='blue')
ax.add_patch(arrow2)
ax.text(6.2, act_y + act_h/2 + 0.4, r'$u(t)$',
        fontsize=11, fontweight='bold', color='blue')

# Actuator to plant (force)
arrow3 = FancyArrowPatch((act_x + act_w, act_y + act_h/2),
                        (plant_x, plant_y + plant_h/2 + 0.5),
                        arrowstyle='->', mutation_scale=25, linewidth=2.5,
                        color='orange')
ax.add_patch(arrow3)
ax.text(9.0, plant_y + plant_h/2 + 1.0, 'Force',
        fontsize=10, fontweight='bold', color='orange')

# Plant to sensors (state)
arrow4 = FancyArrowPatch((plant_x + plant_w/2, plant_y),
                        (sens_x + sens_w/2, sens_y + sens_h),
                        arrowstyle='->', mutation_scale=25, linewidth=2.5,
                        color='purple')
ax.add_patch(arrow4)
ax.text(plant_x + 0.8, plant_y - 0.4, r'$\mathbf{x}_{meas}$',
        fontsize=10, fontweight='bold', color='purple')

# Sensors to controller (feedback)
# Draw curved feedback arrow
from matplotlib.patches import ConnectionPatch
feedback_arrow = ConnectionPatch((sens_x, sens_y + sens_h/2),
                                (ctrl_x + ctrl_w/2, ctrl_y),
                                "data", "data",
                                arrowstyle="->", shrinkA=5, shrinkB=5,
                                mutation_scale=25, linewidth=2.5,
                                color='red',
                                connectionstyle="arc3,rad=-0.3")
ax.add_patch(feedback_arrow)
ax.text(4.5, 3.5, 'Feedback', fontsize=10, fontweight='bold',
        color='red', rotation=0)

# ============================================================================
# Add disturbances
# ============================================================================

# External disturbance arrow
dist_arrow = FancyArrowPatch((plant_x + plant_w/2 + 1.5, plant_y + plant_h + 1.2),
                            (plant_x + plant_w/2 + 0.5, plant_y + plant_h + 0.2),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color='brown', linestyle='--')
ax.add_patch(dist_arrow)
ax.text(plant_x + plant_w/2 + 1.8, plant_y + plant_h + 1.5,
        'Disturbances\n$d(t)$', fontsize=9, color='brown',
        ha='center', style='italic')

# ============================================================================
# Add title and labels
# ============================================================================

ax.text(6.5, 8.5, 'Closed-Loop Control System for Double-Inverted Pendulum',
        fontsize=15, fontweight='bold', ha='center')

# Add performance objectives box
perf_text = (
    'Control Objectives:\n'
    '  1. Stabilize upright equilibrium\n'
    '  2. Minimize settling time\n'
    '  3. Reduce chattering\n'
    '  4. Reject disturbances'
)
ax.text(1.5, 3.5, perf_text, fontsize=9,
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
        verticalalignment='top')

# Add system properties box
props_text = (
    'System Properties:\n'
    '  - 3 DOF, 1 control input\n'
    '  - Nonlinear dynamics\n'
    '  - Underactuated (67%)\n'
    '  - Real-time constraints'
)
ax.text(11.5, 1.2, props_text, fontsize=9,
        bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8),
        verticalalignment='bottom')

# ============================================================================
# Formatting
# ============================================================================

ax.set_xlim(0, 13)
ax.set_ylim(0, 9)
ax.set_aspect('equal')
ax.axis('off')

plt.tight_layout()
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print(f"[OK] Created {output_file}")
print(f"[INFO] System overview diagram generated successfully")
print(f"[INFO] Shows complete control loop: Reference -> Controller -> Actuator -> Plant -> Sensors -> Feedback")
