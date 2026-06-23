# Figure Style Guide - DIP-SMC-PSO Textbook

**Version:** 1.0
**Author:** Agent 3 - Figure Integration and Caption Writing
**Date:** 2026-01-05
**Purpose:** Ensure visual consistency across all 50+ figures in the textbook

---

## 1. Overview

This style guide defines mandatory formatting standards for all figures in the DIP-SMC-PSO textbook. Consistency in fonts, colors, sizes, and layouts improves readability and professional presentation.

**Scope:** Applies to:
- All NEW figures generated via `scripts/textbook/generate_figures.py`
- Any EXISTING figures modified or regenerated
- Figures created by other agents (e.g., Algorithm Agent's pseudocode diagrams)

**Non-scope:** Does not apply to:
- Third-party figures (cited with permission)
- Screenshots from external tools (preserve original appearance)

---

## 2. Mandatory Matplotlib Style Configuration

All Python-generated figures **MUST** apply this style configuration before plotting:

```python
import matplotlib.pyplot as plt

STYLE_CONFIG = {
    "figure.dpi": 300,                    # High resolution for print quality
    "savefig.dpi": 300,                   # Match figure DPI
    "font.family": "serif",               # Serif fonts for academic style
    "font.serif": ["Times New Roman", "DejaVu Serif"],  # Fallback to DejaVu if Times unavailable
    "font.size": 12,                      # Base font size
    "axes.titlesize": 14,                 # Plot titles
    "axes.labelsize": 12,                 # Axis labels (x, y, z)
    "xtick.labelsize": 10,                # X-axis tick labels
    "ytick.labelsize": 10,                # Y-axis tick labels
    "legend.fontsize": 10,                # Legend entries
    "figure.titlesize": 14,               # Figure suptitle
    "lines.linewidth": 2,                 # Default line width
    "lines.markersize": 8,                # Default marker size
    "axes.grid": True,                    # Enable grid by default
    "grid.alpha": 0.3,                    # Light grid lines
    "axes.axisbelow": True,               # Grid behind data
}

plt.rcParams.update(STYLE_CONFIG)
```

**Rationale:**
- **300 DPI:** Required for print quality (textbooks, journals, posters)
- **Times New Roman:** Standard academic serif font, widely available
- **Consistent sizes:** 14pt titles, 12pt labels, 10pt ticks ensures hierarchy
- **Serif fonts:** Better readability in printed text than sans-serif

---

## 3. Color Palette: 7-Controller Standard

All controller comparisons **MUST** use these exact colors for consistency across chapters:

| Controller | Hex Color | RGB | Color Name | Usage |
|------------|-----------|-----|------------|-------|
| Classical SMC | `#1f77b4` | (31, 119, 180) | Blue | Baseline controller |
| STA-SMC | `#ff7f0e` | (255, 127, 14) | Orange | Continuous control |
| Adaptive SMC | `#2ca02c` | (44, 160, 44) | Green | Gain scheduling |
| Hybrid Adaptive STA | `#d62728` | (214, 39, 40) | Red | Best overall performance |
| Swing-Up | `#9467bd` | (148, 103, 189) | Purple | Large-angle maneuvers |
| MPC | `#8c564b` | (140, 86, 75) | Brown | Optimal control |
| HOSM (3rd order) | `#e377c2` | (227, 119, 194) | Pink | Advanced SMC |

**Python implementation:**

```python
CONTROLLER_COLORS = {
    "classical_smc": "#1f77b4",
    "sta_smc": "#ff7f0e",
    "adaptive_smc": "#2ca02c",
    "hybrid_adaptive_sta": "#d62728",
    "swing_up": "#9467bd",
    "mpc": "#8c564b",
    "hosm": "#e377c2",
}

# Usage
plt.plot(t, theta1, color=CONTROLLER_COLORS["classical_smc"], label="Classical SMC")
```

**Accessibility:**
- All colors are distinguishable in grayscale (tested via simulated color blindness)
- Line styles should differentiate controllers when printing in B&W: solid, dashed, dotted

---

## 4. Figure Dimensions and Layouts

### 4.1 Single-Column Figures

**Width:** `0.8\textwidth` in LaTeX (approximately 5.5 inches for standard textbook)

**Python:**
```python
fig, ax = plt.subplots(figsize=(10, 6))  # 10 inches wide, 6 inches tall
```

**Aspect ratio:** 5:3 (golden ratio approximation)

**Use cases:**
- Time-series plots (angle vs time, control vs time)
- Single phase portraits
- Bar charts with 5-7 items
- Heatmaps

### 4.2 Two-Column (Side-by-Side) Figures

**Width:** `0.45\textwidth` per subfigure in LaTeX (approximately 2.5 inches each)

**Python:**
```python
fig, axes = plt.subplots(1, 2, figsize=(14, 6))  # Total 14 inches wide
# Left subplot: axes[0]
# Right subplot: axes[1]
```

**Use cases:**
- Comparing two controllers
- Dual phase portraits (theta1 vs theta1_dot, theta2 vs theta2_dot)
- Before/after comparisons

### 4.3 Multi-Panel Figures (2x2 Grid)

**Python:**
```python
fig, axes = plt.subplots(2, 2, figsize=(14, 10))  # 2 rows, 2 columns
# Access: axes[row, col]
```

**Use cases:**
- Comprehensive analysis (e.g., Figure 4.4: sigma1 time, sigma2 time, phase portrait, Lyapunov)
- Multi-metric comparisons

### 4.4 3D Plots

**Python:**
```python
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
ax.view_init(elev=25, azim=45)  # Standard viewing angle
```

**Viewing angles:**
- **Elevation:** 25 degrees (slightly above horizontal)
- **Azimuth:** 45 degrees (northeast perspective)

---

## 5. Line Styles and Markers

### 5.1 Line Styles for Controller Differentiation

When plotting multiple controllers, use **both color AND line style**:

| Controller | Color | Line Style | Marker |
|------------|-------|------------|--------|
| Classical | Blue | Solid `-` | Circle `o` |
| STA | Orange | Solid `-` | Triangle `^` |
| Adaptive | Green | Solid `-` | Square `s` |
| Hybrid | Red | Solid `-` | Diamond `D` |
| Swing-Up | Purple | Solid `-` | Star `*` |

**For before/after comparisons:**
- **Before (heuristic gains):** Dashed `--` line
- **After (PSO-optimized):** Solid `-` line

**For nominal vs perturbed:**
- **Nominal:** Solid `-` line
- **Perturbed:** Dotted `:` or dash-dot `-.` line

### 5.2 Line Widths

- **Primary data:** `linewidth=2` (default, readable)
- **Secondary/reference:** `linewidth=1.5` (slightly thinner)
- **Grid lines:** `linewidth=0.5` (subtle)
- **Annotations:** `linewidth=1` (arrows, boxes)

### 5.3 Marker Sizes

- **Scatter plots:** `s=100` (moderate size)
- **Line plots with markers:** `markersize=8`
- **Emphasis (start/end points):** `s=200` or `markersize=12`

---

## 6. Axis Labels and Titles

### 6.1 Axis Label Format

**Template:** `Variable Symbol (units)`

**Examples:**
- `Time (s)`
- `$\theta_1$ (rad)` (use LaTeX math mode for symbols)
- `Control Force $F$ (N)`
- `Energy $E$ (J)`
- `Settling Time $t_s$ (s)`

**Python:**
```python
ax.set_xlabel("Time (s)", fontsize=12)
ax.set_ylabel(r"$\theta_1$ (rad)", fontsize=12)  # Note the raw string r"..." for LaTeX
```

### 6.2 Title Format

**Single-panel:** Descriptive title summarizing the plot

```python
ax.set_title("Transient Response: Classical SMC", fontsize=14, weight="bold")
```

**Multi-panel:** Use subplot labels (a), (b), (c), (d)

```python
axes[0, 0].set_title("(a) Sliding Variable $\sigma_1$", fontsize=14, weight="bold", loc="left")
axes[0, 1].set_title("(b) Sliding Variable $\sigma_2$", fontsize=14, weight="bold", loc="left")
```

### 6.3 Mathematical Notation

Use LaTeX math mode for all variables:
- Angles: `$\theta_1$`, `$\theta_2$`
- Derivatives: `$\dot{\theta}_1$`, `$\ddot{x}$`
- Sliding variables: `$s_1 = \lambda_1 \theta_1 + \dot{\theta}_1$`
- Control: `$F$`, `$u$`, `$\tau$`
- Gains: `$k_1$`, `$K_1$`, `$\lambda_1$`

**Avoid:**
- Plain text: ~~theta1~~, ~~sigma~~
- Inconsistent notation: ~~th1~~, ~~angle1~~

---

## 7. Legends

### 7.1 Legend Placement

**Preferred locations (in order):**
1. `loc="best"` (Matplotlib auto-selects least-obstructive location)
2. `loc="upper right"` (for bottom-left data concentration)
3. `loc="upper left"` (for bottom-right data concentration)
4. `loc="lower right"` (for top-left data concentration)

**Avoid:**
- `loc="center"` (obscures data)
- Outside plot area (wastes space in textbook layout)

### 7.2 Legend Formatting

```python
ax.legend(
    loc="best",
    frameon=True,        # Draw border
    shadow=True,         # Add shadow for depth
    fontsize=10,         # Readable size
    ncol=1,              # Single column (use ncol=2 for 5+ items)
)
```

### 7.3 Legend Entry Format

**Template:** `Label: Description (Key Parameter)`

**Examples:**
- `Classical SMC` (simple, for well-known controllers)
- `$\epsilon = 0.05$` (for parameter sweeps)
- `PSO-Optimized` (for before/after)
- `Nominal` vs `+20% Uncertainty`

---

## 8. Grids and Axes

### 8.1 Grid Lines

**Always enable grids** for quantitative plots:

```python
ax.grid(True, alpha=0.3, linewidth=0.5, color="gray")
ax.set_axisbelow(True)  # Grid behind data
```

**Exceptions:**
- Schematic diagrams (free body diagrams, UML)
- Photos/screenshots
- Artistic visualizations

### 8.2 Axis Limits

**Auto-scaling:** Use Matplotlib defaults for most cases

**Manual limits:** Set when emphasizing specific regions

```python
ax.set_xlim(0, 5)      # Time from 0 to 5 seconds
ax.set_ylim(-0.3, 0.3) # Angle range ±0.3 rad
```

**Padding:** Include 5-10% margin around data

```python
ax.margins(0.05)  # 5% padding on all sides
```

### 8.3 Log Scales

Use log scale for:
- Chattering amplitude (spans 3 orders of magnitude)
- PSO fitness evolution (exponential decay)
- Computational cost (10 µs to 1000 µs)

```python
ax.set_yscale("log")
```

**Label format:**
```python
ax.set_ylabel("Chattering $\sigma(\dot{F})$ (N/s, log scale)", fontsize=12)
```

---

## 9. Annotations and Highlights

### 9.1 Arrows and Text

**Pointing to key features:**

```python
ax.annotate(
    "Switching point",
    xy=(3.5, 0.5),          # Point location
    xytext=(4.0, 0.8),      # Text location
    arrowprops=dict(
        arrowstyle="->",
        lw=1.5,
        color="black"
    ),
    fontsize=10,
    bbox=dict(
        boxstyle="round,pad=0.3",
        facecolor="yellow",
        alpha=0.3
    )
)
```

### 9.2 Vertical/Horizontal Lines

**Marking events:**

```python
ax.axvline(x=2.0, color="gray", linestyle="--", linewidth=1.5, alpha=0.7, label="Disturbance onset")
ax.axhline(y=0.0, color="black", linestyle="-", linewidth=0.5, alpha=0.3)  # Zero reference
```

### 9.3 Shaded Regions

**Highlighting phases:**

```python
ax.fill_between(
    t[swing_up_phase],
    -0.5, 0.5,
    alpha=0.2,
    color="purple",
    label="Swing-up region"
)
```

---

## 10. Saving Figures

### 10.1 File Formats

**MANDATORY:** Save **BOTH** PNG and PDF for each figure

```python
def save_figure(fig, filename, chapter_dir):
    output_dir = FIGURES_DIR / chapter_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    png_path = output_dir / f"{filename}.png"
    pdf_path = output_dir / f"{filename}.pdf"

    fig.savefig(png_path, dpi=300, bbox_inches="tight", format="png")
    fig.savefig(pdf_path, bbox_inches="tight", format="pdf")

    print(f"[OK] Saved {png_path}")
    print(f"[OK] Saved {pdf_path}")
```

**Rationale:**
- **PNG (300 DPI):** Web viewing, Markdown previews, quick checks
- **PDF (vector):** LaTeX inclusion, scalable quality, print-ready

### 10.2 File Naming Convention

**Template:** `{chapter_prefix}_{descriptive_name}.{ext}`

**Examples:**
- `ch03_classical_smc/transient_response_classical.png`
- `ch04_super_twisting/NEW_finite_time_trajectory.pdf`
- `ch08_pso/pso_convergence_LT7.png`

**Rules:**
- Lowercase with underscores (no spaces, no camelCase)
- Descriptive names (not `fig1.png`, `plot2.png`)
- Prefix `NEW_` for newly generated figures (vs copied existing)

### 10.3 DPI Requirements

| Use Case | DPI | File Size (est.) |
|----------|-----|------------------|
| Web preview | 72-96 | 50-100 KB |
| Screen presentation | 150 | 200-400 KB |
| **Textbook print (REQUIRED)** | **300** | **500 KB - 2 MB** |
| High-quality poster | 600 | 2-5 MB |

**Guideline:** Always use **300 DPI minimum** for textbook figures.

---

## 11. Special Figure Types

### 11.1 Heatmaps

**Style:**
```python
import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
im = ax.imshow(
    data,
    cmap="RdYlGn",        # Red (bad) to Yellow to Green (good)
    aspect="auto",
    vmin=0, vmax=100,     # Explicit range for consistency
    interpolation="nearest"  # No smoothing for discrete data
)

# Colorbar
cbar = plt.colorbar(im, ax=ax, shrink=0.8)
cbar.set_label("Success Rate (%)", rotation=270, labelpad=20, fontsize=12)

# Cell annotations
for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        text = ax.text(j, i, f"{data[i, j]:.1f}",
                      ha="center", va="center", color="black", fontsize=10, weight="bold")
```

**Color maps:**
- **Performance (higher is better):** `RdYlGn` (red-yellow-green)
- **Error (lower is better):** `RdYlGn_r` (reversed, green-yellow-red)
- **Sequential:** `viridis`, `plasma`, `cividis` (colorblind-friendly)
- **Diverging:** `RdBu` (red-blue), `coolwarm`

### 11.2 Bar Charts

**Style:**
```python
fig, ax = plt.subplots(figsize=(10, 6))

x = np.arange(len(controllers))
width = 0.35

bars1 = ax.bar(x - width/2, values_before, width, label="Before PSO", color="lightblue", edgecolor="black", linewidth=1.5)
bars2 = ax.bar(x + width/2, values_after, width, label="After PSO", color="darkblue", edgecolor="black", linewidth=1.5)

ax.set_xlabel("Controller", fontsize=12)
ax.set_ylabel("Chattering $\sigma(\dot{F})$ (N/s)", fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(controllers, fontsize=10, rotation=15, ha="right")
ax.legend(loc="upper right", frameon=True, shadow=True)
ax.grid(True, alpha=0.3, axis="y")
```

**Guidelines:**
- **Edge colors:** Always add black edges to bars for clarity
- **Width:** 0.7-0.8 for single series, 0.35 for grouped bars
- **Rotation:** 15-45 degrees for long labels

### 11.3 Radar Charts (Spider Plots)

**Style:**
```python
from math import pi

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, polar=True)

categories = ["Settling", "Overshoot", "Energy", "Chattering", "Robustness", "Compute"]
N = len(categories)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]  # Close the loop

values = [0.82, 0.80, 0.82, 0.92, 0.95, 0.48]  # Hybrid controller scores
values += values[:1]

ax.plot(angles, values, "o-", linewidth=2, label="Hybrid", color=CONTROLLER_COLORS["hybrid_adaptive_sta"])
ax.fill(angles, values, alpha=0.15, color=CONTROLLER_COLORS["hybrid_adaptive_sta"])

ax.set_theta_offset(pi / 2)
ax.set_theta_direction(-1)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=11)
ax.set_ylim(0, 1)
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.grid(True, alpha=0.3)
ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
```

### 11.4 Phase Portraits

**Style:**
```python
fig, ax = plt.subplots(figsize=(8, 8))

# Plot trajectories
for initial_condition in initial_conditions:
    theta, theta_dot = simulate(initial_condition)
    ax.plot(theta, theta_dot, alpha=0.7, linewidth=1.5, color="blue")

# Sliding surface
theta_range = np.linspace(-0.3, 0.3, 100)
sliding_surface = -lambda1 * theta_range
ax.plot(theta_range, sliding_surface, "r--", linewidth=3, label=f"Sliding surface: $s = {lambda1:.2f}\\theta + \\dot{{\\theta}} = 0$")

# Equilibrium point
ax.scatter([0], [0], color="green", s=300, marker="*", label="Equilibrium", zorder=5, edgecolors="black", linewidths=2)

ax.set_xlabel(r"$\theta$ (rad)", fontsize=12)
ax.set_ylabel(r"$\dot{\theta}$ (rad/s)", fontsize=12)
ax.set_title("Phase Portrait: Classical SMC", fontsize=14, weight="bold")
ax.axhline(0, color="k", linewidth=0.5, alpha=0.3)
ax.axvline(0, color="k", linewidth=0.5, alpha=0.3)
ax.set_aspect("equal")  # Equal scaling for phase space
ax.legend(loc="best", frameon=True, shadow=True)
ax.grid(True, alpha=0.3)
```

**Key feature:** `ax.set_aspect("equal")` ensures circular orbits appear circular (not elliptical)

---

## 12. LaTeX Integration

### 12.1 Including Figures in LaTeX

**Template:**
```latex
\begin{figure}[htbp]  % h=here, t=top, b=bottom, p=page
  \centering
  \includegraphics[width=0.8\textwidth]{figures/ch03_classical_smc/transient_response_classical.png}
  \caption{\captionClassicalTransient}  % From figure_captions.tex
  \label{fig:ch03:classical_transient}
\end{figure}
```

**Side-by-side subfigures:**
```latex
\begin{figure}[htbp]
  \centering
  \begin{subfigure}[b]{0.45\textwidth}
    \includegraphics[width=\textwidth]{figures/ch03_classical_smc/phase_portrait_theta1.png}
    \caption{Pendulum 1}
    \label{fig:ch03:phase_theta1}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.45\textwidth}
    \includegraphics[width=\textwidth]{figures/ch03_classical_smc/phase_portrait_theta2.png}
    \caption{Pendulum 2}
    \label{fig:ch03:phase_theta2}
  \end{subfigure}
  \caption{Phase portraits for both pendulum angles.}
  \label{fig:ch03:phase_portraits}
\end{figure}
```

### 12.2 Cross-Referencing

**In text:**
```latex
The transient response (Figure~\ref{fig:ch03:classical_transient}) shows settling time $t_s = 1.82$ s.
```

**Label naming convention:**
- `fig:{chapter}:{descriptor}`
- Examples: `fig:ch02:stability_regions`, `fig:ch08:pso_convergence`

---

## 13. Quality Checklist

Before finalizing any figure, verify:

**Resolution:**
- [ ] PNG saved at 300 DPI minimum
- [ ] PDF saved as vector (no rasterization)
- [ ] File size reasonable (< 5 MB per figure)

**Fonts:**
- [ ] All text uses Times New Roman (or DejaVu Serif fallback)
- [ ] Title 14pt, axis labels 12pt, ticks 10pt
- [ ] Mathematical symbols in LaTeX math mode (`$\theta_1$`)

**Colors:**
- [ ] Controllers use standard 7-color palette
- [ ] Colors distinguishable in grayscale
- [ ] Colorblind-friendly palettes for heatmaps

**Layout:**
- [ ] Figure dimensions appropriate (10x6 for single-column)
- [ ] Grid lines enabled and subtle (alpha=0.3)
- [ ] Legend visible and non-obstructive
- [ ] Axis labels include units

**Data:**
- [ ] Line widths readable (2.0 for primary data)
- [ ] Markers distinguish multiple series
- [ ] No overlapping text/annotations

**Saving:**
- [ ] Both PNG and PDF formats saved
- [ ] Filename follows convention (lowercase, underscores, descriptive)
- [ ] Saved to correct chapter directory

**LaTeX:**
- [ ] Caption defined in `figure_captions.tex`
- [ ] Figure label follows `fig:{chapter}:{name}` convention
- [ ] Cross-references use `\ref{}` command

---

## 14. Example: Complete Figure Generation Workflow

**Step-by-step example for generating Figure 3.2 (Transient Response):**

```python
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# 1. Apply style configuration
STYLE_CONFIG = {
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
}
plt.rcParams.update(STYLE_CONFIG)

# 2. Load color palette
CONTROLLER_COLORS = {
    "classical_smc": "#1f77b4",
    "sta_smc": "#ff7f0e",
    "adaptive_smc": "#2ca02c",
    "hybrid_adaptive_sta": "#d62728",
}

# 3. Create figure
fig, ax = plt.subplots(figsize=(10, 6))

# 4. Plot data for each controller
for ctrl_name, color in CONTROLLER_COLORS.items():
    t, theta1 = simulate_controller(ctrl_name)  # Your simulation function
    ax.plot(t, theta1, color=color, linewidth=2, label=ctrl_name.replace("_", " ").title())

# 5. Format axes
ax.set_xlabel("Time (s)", fontsize=12)
ax.set_ylabel(r"$\theta_1$ (rad)", fontsize=12)
ax.set_title("Transient Response: All Controllers", fontsize=14, weight="bold")
ax.grid(True, alpha=0.3)
ax.axhline(0, color="k", linewidth=0.5, alpha=0.3)  # Zero reference
ax.legend(loc="upper right", frameon=True, shadow=True, fontsize=10)

# 6. Save figure
output_dir = Path("academic/paper/textbook_latex/figures/ch03_classical_smc")
output_dir.mkdir(parents=True, exist_ok=True)

fig.savefig(output_dir / "transient_response_all.png", dpi=300, bbox_inches="tight")
fig.savefig(output_dir / "transient_response_all.pdf", bbox_inches="tight")
plt.close(fig)

print("[OK] Figure saved: transient_response_all.png and .pdf")
```

**Corresponding LaTeX:**
```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.8\textwidth]{figures/ch03_classical_smc/transient_response_all.png}
  \caption{\captionClassicalTransient}
  \label{fig:ch03:classical_transient}
\end{figure}
```

**Caption from `figure_captions.tex`:**
```latex
\newcommand{\captionClassicalTransient}{%
Transient response of all seven controllers...
[3-5 sentence detailed description]
}
```

---

## 15. Common Pitfalls and Solutions

### Problem 1: Fonts Revert to Default Sans-Serif

**Symptom:** Matplotlib uses DejaVu Sans instead of Times New Roman

**Solution:**
```python
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif"]
```

**Alternative:** Specify font for each text element
```python
ax.set_xlabel("Time (s)", fontsize=12, fontfamily="serif")
```

### Problem 2: Low-Resolution PNG Output

**Symptom:** PNG appears pixelated at 100% zoom

**Solution:**
```python
fig.savefig("output.png", dpi=300)  # NOT dpi=100 (default)
```

**Verification:** Open PNG in image viewer, check properties for 300 DPI

### Problem 3: Legend Obscures Data

**Symptom:** Legend box covers critical data points

**Solutions:**
1. Try `loc="best"` first (auto-placement)
2. Manually specify: `loc="upper left"`, `loc="lower right"`, etc.
3. Reduce legend font size: `fontsize=9`
4. Use semi-transparent background: `framealpha=0.8`
5. Last resort: Place outside plot (reduces plot area)

```python
ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))  # Right side outside
```

### Problem 4: Overlapping Tick Labels

**Symptom:** X-axis labels overlap when many categories

**Solutions:**
1. Rotate labels:
```python
ax.set_xticklabels(labels, rotation=45, ha="right")
```
2. Reduce font size:
```python
ax.tick_params(axis="x", labelsize=8)
```
3. Use fewer ticks:
```python
ax.set_xticks(x[::2])  # Every other tick
```

### Problem 5: LaTeX Math Not Rendering

**Symptom:** `$\theta_1$` appears as literal text, not math symbol

**Solution:** Use raw string prefix `r"..."`
```python
ax.set_ylabel(r"$\theta_1$ (rad)")  # Correct
# NOT: ax.set_ylabel("$\theta_1$ (rad)")  # Backslash interpreted as escape
```

---

## 16. Contact and Updates

**Maintainer:** Agent 3 - Figure Integration and Caption Writing
**Last Updated:** 2026-01-05
**Version:** 1.0

**Updates:** This guide may be revised based on:
- Feedback from Agent 1 (Planning) on consistency requirements
- LaTeX rendering issues discovered during textbook compilation
- Accessibility recommendations from peer review

**Questions:** For clarification on specific figure types, consult `scripts/textbook/generate_figures.py` for reference implementations.

---

**END OF FIGURE STYLE GUIDE**
