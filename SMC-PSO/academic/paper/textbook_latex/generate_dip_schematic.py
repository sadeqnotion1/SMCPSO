"""
Generate Double-Inverted Pendulum Schematic Diagram

Creates a professional technical schematic showing:
- Cart on horizontal rail
- Two pendulum links (L1, L2) with masses (m1, m2)
- Angles (theta1, theta2) from vertical
- Control force (u) on cart
- Coordinate system and labels
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Arc
from matplotlib.lines import Line2D
import os

# Configure matplotlib for publication-quality figures
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13

# Output file
output_file = "figures/placeholder_dip_schematic.png"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Create figure
fig, ax = plt.subplots(figsize=(10, 8))

# ============================================================================
# Parameters
# ============================================================================
cart_width = 1.2
cart_height = 0.6
cart_x = 0  # Center of cart
cart_y = 0  # Bottom of cart on rail

L1 = 2.0  # Length of first pendulum
L2 = 1.5  # Length of second pendulum

# Angles (from vertical upward = 0)
theta1 = np.radians(25)  # First link tilted 25 degrees
theta2 = np.radians(-15)  # Second link tilted -15 degrees

# ============================================================================
# Draw rail
# ============================================================================
rail_y = cart_y - 0.1
ax.plot([-3, 3], [rail_y, rail_y], 'k-', linewidth=3, solid_capstyle='butt')

# Rail support hatching
for x in np.linspace(-3, 3, 20):
    ax.plot([x, x - 0.15], [rail_y, rail_y - 0.3], 'k-', linewidth=0.8)

# ============================================================================
# Draw cart
# ============================================================================
cart_rect = Rectangle((cart_x - cart_width/2, cart_y), cart_width, cart_height,
                       facecolor='lightgray', edgecolor='black', linewidth=2)
ax.add_patch(cart_rect)

# Cart label
ax.text(cart_x, cart_y + cart_height/2, '$M$', fontsize=16, fontweight='bold',
        ha='center', va='center')

# Cart wheels
wheel_radius = 0.15
wheel1 = Circle((cart_x - cart_width/3, cart_y), wheel_radius,
                facecolor='white', edgecolor='black', linewidth=1.5, zorder=5)
wheel2 = Circle((cart_x + cart_width/3, cart_y), wheel_radius,
                facecolor='white', edgecolor='black', linewidth=1.5, zorder=5)
ax.add_patch(wheel1)
ax.add_patch(wheel2)

# ============================================================================
# Draw pendulum links
# ============================================================================

# Joint 0 (cart pivot) - at top center of cart
joint0_x = cart_x
joint0_y = cart_y + cart_height

# Joint 1 (between link 1 and link 2)
joint1_x = joint0_x + L1 * np.sin(theta1)
joint1_y = joint0_y + L1 * np.cos(theta1)

# End of link 2
joint2_x = joint1_x + L2 * np.sin(theta2)
joint2_y = joint1_y + L2 * np.cos(theta2)

# Draw link 1 (as thick gray line)
ax.plot([joint0_x, joint1_x], [joint0_y, joint1_y], 'gray', linewidth=8, solid_capstyle='butt')

# Draw link 2 (as thick gray line)
ax.plot([joint1_x, joint2_x], [joint1_y, joint2_y], 'gray', linewidth=8, solid_capstyle='butt')

# Draw joints as circles
joint0 = Circle((joint0_x, joint0_y), 0.12, facecolor='black', edgecolor='black', zorder=10)
joint1 = Circle((joint1_x, joint1_y), 0.12, facecolor='black', edgecolor='black', zorder=10)
joint2 = Circle((joint2_x, joint2_y), 0.12, facecolor='darkred', edgecolor='black', linewidth=2, zorder=10)
ax.add_patch(joint0)
ax.add_patch(joint1)
ax.add_patch(joint2)

# ============================================================================
# Add masses (circles at center of each link)
# ============================================================================
mass1_x = joint0_x + (L1/2) * np.sin(theta1)
mass1_y = joint0_y + (L1/2) * np.cos(theta1)

mass2_x = joint1_x + (L2/2) * np.sin(theta2)
mass2_y = joint1_y + (L2/2) * np.cos(theta2)

mass1 = Circle((mass1_x, mass1_y), 0.25, facecolor='lightblue', edgecolor='blue', linewidth=2, zorder=8)
mass2 = Circle((mass2_x, mass2_y), 0.22, facecolor='lightcoral', edgecolor='red', linewidth=2, zorder=8)
ax.add_patch(mass1)
ax.add_patch(mass2)

# Mass labels
ax.text(mass1_x, mass1_y, '$m_1$', fontsize=14, fontweight='bold', ha='center', va='center')
ax.text(mass2_x, mass2_y, '$m_2$', fontsize=14, fontweight='bold', ha='center', va='center')

# ============================================================================
# Add length labels
# ============================================================================
# L1 label (midpoint of link 1)
mid1_x = joint0_x + (L1 * 0.6) * np.sin(theta1)
mid1_y = joint0_y + (L1 * 0.6) * np.cos(theta1)
ax.text(mid1_x + 0.3, mid1_y, '$L_1$', fontsize=13, fontweight='bold', style='italic')

# L2 label (midpoint of link 2)
mid2_x = joint1_x + (L2 * 0.6) * np.sin(theta2)
mid2_y = joint1_y + (L2 * 0.6) * np.cos(theta2)
ax.text(mid2_x - 0.4, mid2_y, '$L_2$', fontsize=13, fontweight='bold', style='italic')

# ============================================================================
# Add angle indicators
# ============================================================================

# Vertical reference line from joint 0 (dashed)
vert_line_length = 1.5
ax.plot([joint0_x, joint0_x], [joint0_y, joint0_y + vert_line_length],
        'k--', linewidth=1.5, alpha=0.6)

# Theta1 arc
arc1 = Arc((joint0_x, joint0_y), 0.8, 0.8, angle=0, theta1=90-np.degrees(theta1), theta2=90,
           color='blue', linewidth=2)
ax.add_patch(arc1)
ax.text(joint0_x + 0.5, joint0_y + 1.0, r'$\theta_1$', fontsize=13, color='blue', fontweight='bold')

# Vertical reference line from joint 1 (dashed)
ax.plot([joint1_x, joint1_x], [joint1_y, joint1_y + vert_line_length],
        'k--', linewidth=1.5, alpha=0.6)

# Theta2 arc
arc2 = Arc((joint1_x, joint1_y), 0.8, 0.8, angle=0, theta1=90, theta2=90-np.degrees(theta2),
           color='red', linewidth=2)
ax.add_patch(arc2)
ax.text(joint1_x - 0.6, joint1_y + 0.9, r'$\theta_2$', fontsize=13, color='red', fontweight='bold')

# ============================================================================
# Add control force arrow (u)
# ============================================================================
force_arrow = FancyArrowPatch((cart_x - cart_width/2 - 0.8, cart_y + cart_height/2),
                              (cart_x - cart_width/2 - 0.2, cart_y + cart_height/2),
                              arrowstyle='->', mutation_scale=25, linewidth=3,
                              color='green', zorder=15)
ax.add_patch(force_arrow)
ax.text(cart_x - cart_width/2 - 1.0, cart_y + cart_height/2 + 0.3, '$u$',
        fontsize=16, fontweight='bold', color='green')

# ============================================================================
# Add coordinate system (x-axis)
# ============================================================================
coord_y = rail_y - 0.6
ax.arrow(-2.5, coord_y, 1.5, 0, head_width=0.15, head_length=0.15,
         fc='black', ec='black', linewidth=1.5)
ax.text(-1.5, coord_y - 0.4, '$x$ (cart position)', fontsize=12, ha='center')

# ============================================================================
# Add gravity indicator
# ============================================================================
gravity_x = -2.5
gravity_y = 3.0
ax.arrow(gravity_x, gravity_y, 0, -0.8, head_width=0.15, head_length=0.15,
         fc='purple', ec='purple', linewidth=2)
ax.text(gravity_x, gravity_y + 0.3, '$g$', fontsize=14, fontweight='bold', color='purple')

# ============================================================================
# Add title and annotations
# ============================================================================
ax.text(0, -2.5, 'Double-Inverted Pendulum (DIP) Configuration',
        fontsize=14, fontweight='bold', ha='center')

# Add degrees of freedom annotation
ax.text(2.5, -1.8, '3 DOF: $x_{cart}, \\theta_1, \\theta_2$',
        fontsize=11, ha='right', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
ax.text(2.5, -2.2, '1 Actuator: $u$ (horizontal force)',
        fontsize=11, ha='right', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

# ============================================================================
# Formatting
# ============================================================================
ax.set_xlim(-3, 3.5)
ax.set_ylim(-3, 5)
ax.set_aspect('equal')
ax.axis('off')

plt.tight_layout()
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print(f"[OK] Created {output_file}")
print(f"[INFO] DIP schematic diagram generated successfully")
print(f"[INFO] Shows cart (M), two pendulum links (L1, L2), masses (m1, m2),")
print(f"[INFO] angles (theta1, theta2), control force (u), and coordinate system")
