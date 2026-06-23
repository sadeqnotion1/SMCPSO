# utils.visualization.__init__

**Source:** `src\utils\visualization\__init__.py`

## Module Overview visualization

package for control engineering

. This package provides complete visualization features including:


- Real-time and recorded animations
- Static analysis plots
- Controller comparison visualizations
- Complete project documentation movies
- Professional presentation materials ## Complete Source Code ```{literalinclude} ../../../src/utils/visualization/__init__.py
:language: python
:linenos:
```

---

## Dependencies This module imports: - `from .animation import DIPAnimator, MultiSystemAnimator`
- `from .static_plots import ControlPlotter, SystemVisualization`
- `from .movie_generator import ProjectMovieGenerator, MovieScene`
- `from .legacy_visualizer import Visualizer` ## Advanced Mathematical Theory ### Visualization Theory Scientific visualization transforms numerical data into perceptual representations using mathematical principles. #### Frame Interpolation **Linear interpolation** for smooth animation:
$$
x(t) = x_i + \frac{t - t_i}{t_{i+1} - t_i} (x_{i+1} - x_i)
$$ **Cubic spline interpolation** (C² continuous):
$$
s(t) = a_i + b_i(t - t_i) + c_i(t - t_i)^2 + d_i(t - t_i)^3
$$ **Animation frame rate:**
$$
\Delta t_{\text{frame}} = \frac{1}{\text{fps}}
$$ For 30 FPS: $\Delta t = 33.33$ ms #### Color Theory **RGB color space** (device-dependent):
$$
C_{\text{RGB}} = (R, G, B), \quad R, G, B \in [0, 1]
$$ **HSV color space** (perceptually intuitive):
$$
C_{\text{HSV}} = (H, S, V), \quad H \in [0, 360°), \, S, V \in [0, 1]
$$ **Perceptual color distance** (CIE LAB):
$$
\Delta E = \sqrt{(\Delta L^*)^2 + (\Delta a^*)^2 + (\Delta b^*)^2}
$$ Just-noticeable difference: $\Delta E < 2.3$ #### Plot Composition **Aspect ratio** for physical accuracy:
$$
\text{Aspect} = \frac{\text{width}}{\text{height}}
$$ **Grid layout** for subplots:
$$
\text{Grid} = (n_{\text{rows}}, n_{\text{cols}}), \quad n_{\text{total}} = n_{\text{rows}} \times n_{\text{cols}}
$$ **Margin calculation:**
$$
\text{Plot Area} = (W - 2m_x) \times (H - 2m_y)
$$ where $m_x, m_y$ are horizontal and vertical margins. #### Information Density **Data-ink ratio** (Tufte's principle):
$$
\text{Data-Ink Ratio} = \frac{\text{Ink used for data}}{\text{Total ink used}}
$$ Target: > 0.5 (prefer data over decoration) **Pixels per data point:**
$$
\text{Resolution} = \frac{\text{Total pixels}}{\text{Number of data points}}
$$ ## Architecture Diagram ```{mermaid}
graph TD A[Visualization System] --> B[Animation] A --> C[Static Plots] A --> D[Movie Generator] B --> E[Frame Interpolation] E --> F{Interpolation Method} F -->|Linear| G[Fast, C⁰] F -->|Spline| H[Smooth, C²] C --> I[Plot Composition] I --> J{Layout} J -->|Single| K[Full Figure] J -->|Grid| L[Subplots] D --> M[Scene Management] M --> N[Intro Scene] M --> O[Animation Scenes] M --> P[Comparison Scene] N --> Q[Video Encoder] O --> Q P --> Q Q --> R[Output MP4/GIF] style F fill:#fff4e1 style J fill:#fff4e1 style R fill:#e8f5e9
``` ## Usage Examples ### Example 1: Real-Time Animation ```python

from src.utils.visualization import DIPAnimator
import numpy as np # Create animator
animator = DIPAnimator( L1=0.3, L2=0.25, # Pendulum lengths fps=30, # 30 frames per second trail_length=50 # Show last 50 positions
) # Animate simulation results
animator.animate( t=t, # Time vector x=x, # State trajectories save_path="simulation.mp4", dpi=120
) print(f"Animation created at 30 FPS")
print(f"Frame interval: {1000/30:.2f} ms")
``` ### Example 2: Static Performance Plots ```python
from src.utils.visualization import ControlPlotter
import matplotlib.pyplot as plt # Create plotter
plotter = ControlPlotter() # Create plot layout
fig, axes = plotter.plot_comprehensive( t=t, x=x, u=u, reference=np.zeros_like(x), title="Classical SMC Performance"
) # Customize appearance
plotter.set_style('seaborn-v0_8-paper')
plotter.add_grid(axes, alpha=0.3) plt.savefig('performance.png', dpi=300, bbox_inches='tight')
``` ### Example 3: Multi-System Comparison ```python

from src.utils.visualization import MultiSystemAnimator # Create comparison animator
animator = MultiSystemAnimator( systems=['Classical SMC', 'Adaptive SMC', 'STA SMC'], L1=0.3, L2=0.25, layout='horizontal' # Side-by-side comparison
) # Animate multiple controllers
animator.animate_comparison( t=t, states=[x_classical, x_adaptive, x_sta], save_path="comparison.mp4", fps=30
)
``` ### Example 4: Project Movie Generation ```python
from src.utils.visualization import ProjectMovieGenerator, MovieScene # Create movie generator
generator = ProjectMovieGenerator( title="DIP SMC PSO Project", output_path="project_overview.mp4", fps=30, resolution=(1920, 1080)
) # Define scenes
scenes = [ MovieScene('intro', duration=5.0, content="Title and overview"), MovieScene('simulation', duration=10.0, content=simulation_results), MovieScene('comparison', duration=8.0, content=comparison_data), MovieScene('conclusion', duration=3.0, content="Summary")
] # Generate complete movie
generator.create_movie(scenes)
``` ### Example 5: Custom Color Schemes ```python

from src.utils.visualization import ControlPlotter
import numpy as np # Define perceptually uniform color scheme
colors = { 'state': '#1f77b4', # Blue 'control': '#ff7f0e', # Orange 'reference': '#2ca02c', # Green 'error': '#d62728' # Red
} plotter = ControlPlotter(color_scheme=colors) # Plot with consistent colors
fig, axes = plt.subplots(2, 1, figsize=(10, 8)) axes[0].plot(t, x[:, 1], color=colors['state'], label='θ₁')
axes[0].plot(t, ref, color=colors['reference'], linestyle='--', label='Reference') axes[1].plot(t, u, color=colors['control'], label='Control')
axes[1].axhline(0, color='gray', linestyle=':', alpha=0.5) for ax in axes: ax.legend() ax.grid(alpha=0.3) plt.tight_layout()
```
