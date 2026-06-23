"""
Generate Chattering Illustration

Creates a time-series plot showing:
- Ideal sliding mode control (infinite switching frequency)
- Practical SMC with chattering (finite switching frequency)
- Comparison of control signals and sliding surface dynamics
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# Configure matplotlib
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'serif'

# Output file
output_file = "figures/placeholder_chattering_illustration.png"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# ============================================================================
# Generate signals
# ============================================================================

# Time vector
t = np.linspace(0, 2, 2000)
dt = t[1] - t[0]

# Ideal sliding surface (smooth convergence to zero)
s_ideal = 0.5 * np.exp(-3*t)

# Practical sliding surface with chattering
s_practical = 0.5 * np.exp(-3*t) * (1 + 0.15 * np.sin(100*np.pi*t))

# Ideal control signal (smooth)
u_ideal = -10 * np.sign(s_ideal) * np.abs(s_ideal)**0.5

# Practical control signal with chattering (high-frequency switching)
u_practical = np.zeros_like(t)
for i in range(len(t)):
    if i == 0:
        u_practical[i] = -10 * np.sign(s_practical[i])
    else:
        # Simulate switching with delay
        if abs(s_practical[i]) > 0.01:
            u_practical[i] = -10 * np.sign(s_practical[i])
        else:
            # Chattering zone - rapid switching
            u_practical[i] = -10 * np.sign(s_practical[i]) + 5 * np.sin(200*np.pi*t[i])

# ============================================================================
# Create figure
# ============================================================================

fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# ============================================================================
# Subplot 1: Sliding surface
# ============================================================================

ax1 = axes[0]

# Plot ideal
ax1.plot(t, s_ideal, 'b-', linewidth=2.5, label='Ideal SMC (infinite switching)', alpha=0.8)

# Plot practical with chattering
ax1.plot(t, s_practical, 'r-', linewidth=1.8, label='Practical SMC (chattering)', alpha=0.9)

# Zero line
ax1.axhline(y=0, color='k', linestyle='--', linewidth=1, alpha=0.5)

# Shade chattering region
chattering_zone = 0.02
ax1.axhspan(-chattering_zone, chattering_zone, alpha=0.2, color='yellow',
            label='Chattering zone')

ax1.set_ylabel('Sliding Surface $s(t)$', fontsize=13, fontweight='bold')
ax1.set_title('Chattering in Sliding Mode Control: Sliding Surface Dynamics',
              fontsize=14, fontweight='bold')
ax1.legend(loc='upper right', fontsize=10, framealpha=0.9)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(0, 2)
ax1.set_ylim(-0.1, 0.6)

# Add annotation showing chattering
ax1.annotate('High-frequency\noscillations\n(chattering)',
            xy=(1.5, s_practical[1500]), xytext=(1.2, 0.35),
            arrowprops=dict(arrowstyle='->', lw=2, color='red'),
            fontsize=11, fontweight='bold', color='red',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

# ============================================================================
# Subplot 2: Control signal
# ============================================================================

ax2 = axes[1]

# Plot ideal control
ax2.plot(t, u_ideal, 'b-', linewidth=2.5, label='Ideal control', alpha=0.7)

# Plot practical control with chattering
ax2.plot(t, u_practical, 'r-', linewidth=0.8, label='Practical control (chattering)', alpha=0.9)

# Zero line
ax2.axhline(y=0, color='k', linestyle='--', linewidth=1, alpha=0.5)

ax2.set_xlabel('Time $t$ (s)', fontsize=13, fontweight='bold')
ax2.set_ylabel('Control Input $u(t)$ (N)', fontsize=13, fontweight='bold')
ax2.set_title('Control Signal: Ideal vs. Chattering',
              fontsize=14, fontweight='bold')
ax2.legend(loc='upper right', fontsize=10, framealpha=0.9)
ax2.grid(True, alpha=0.3)
ax2.set_xlim(0, 2)
ax2.set_ylim(-18, 18)

# Add zoomed inset showing rapid switching
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset

axins = zoomed_inset_axes(ax2, zoom=4, loc='center right',
                          bbox_to_anchor=(0.95, 0.45),
                          bbox_transform=ax2.transAxes)
t_zoom_start, t_zoom_end = 1.48, 1.52
zoom_indices = (t >= t_zoom_start) & (t <= t_zoom_end)
axins.plot(t[zoom_indices], u_practical[zoom_indices], 'r-', linewidth=1.5)
axins.axhline(y=0, color='k', linestyle='--', linewidth=0.8)
axins.set_xlim(t_zoom_start, t_zoom_end)
axins.set_ylim(-18, 18)
axins.grid(True, alpha=0.4)
axins.set_title('Rapid switching\n(~100 Hz)', fontsize=9)

# Draw box around zoomed region
mark_inset(ax2, axins, loc1=2, loc2=4, fc="none", ec="gray", linestyle='--', linewidth=1.5)

# Add annotation pointing to chatter
ax2.annotate('Rapid control switching\ncauses mechanical wear\nand energy waste',
            xy=(1.3, 8), xytext=(0.5, 12),
            arrowprops=dict(arrowstyle='->', lw=2, color='darkred'),
            fontsize=10, fontweight='bold', color='darkred',
            bbox=dict(boxstyle='round', facecolor='mistyrose', alpha=0.9))

# ============================================================================
# Add summary text box
# ============================================================================

summary_text = (
    'Chattering Causes:\n'
    '  1. Finite switching frequency (vs. ideal infinite frequency)\n'
    '  2. Sensor measurement noise\n'
    '  3. Actuator bandwidth limitations\n'
    '  4. Time discretization in digital implementation\n\n'
    'Mitigation Strategies:\n'
    '  - Boundary layer (smooth approximation)\n'
    '  - Higher-order SMC (e.g., Super-Twisting)\n'
    '  - Adaptive gain scheduling\n'
    '  - Observer-based filtering'
)

fig.text(0.02, 0.02, summary_text, fontsize=9,
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85),
         verticalalignment='bottom', family='monospace')

plt.tight_layout(rect=[0, 0.15, 1, 1])
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print(f"[OK] Created {output_file}")
print(f"[INFO] Chattering illustration generated successfully")
print(f"[INFO] Shows comparison between ideal SMC and practical SMC with chattering")
print(f"[INFO] Includes sliding surface dynamics, control signals, and zoomed inset")
