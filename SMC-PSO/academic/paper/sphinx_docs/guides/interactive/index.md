# Interactive Features

**Revolutionary Documentation Experience**: Run Python code, manipulate 3D visualizations, and explore control systems directly in your browser.

This section showcases cutting-edge interactive documentation features that transform passive reading into active experimentation.

---

## Available Interactive Features

### Live Python Code Execution

**Run real Python code in your browser** - no installation required. Powered by Pyodide (Python compiled to WebAssembly).

**Features:**
- Full Python 3.11 with NumPy, Matplotlib, SciPy
- Edit code inline and re-run instantly
- Interactive examples throughout documentation
- 15-30s first load, instant after caching

**[Start Experimenting →](live-python-demo.md)**

---

### Plotly Interactive Charts

**Professional data visualization** with zoom, pan, and interactive exploration. Transform static plots into dynamic, explorable visualizations.

**Features:**
- Multiple chart types (line, scatter, bar, heatmap, radar)
- Controller performance comparison matrices
- PSO convergence animations with particle tracking
- Parameter space exploration (scatter matrices)
- Export charts as high-resolution images

**[Explore Charts →](plotly-charts-demo.md)**

---

### Jupyter Notebooks Integration

**Execute complete Jupyter notebooks** directly in documentation with full Python environment, interactive widgets, and execution caching.

**Features:**
- Full notebook embedding with selective cell display
- Inline code cells for quick demonstrations
- Interactive widgets (sliders, dropdowns, buttons, checkboxes)
- Execution caching for instant rebuilds
- Native Python performance (100% speed)

**[Try Notebooks →](jupyter-notebooks-demo.md)**

---

### Mathematical Visualizations

**Interactive control theory visualizations** with 6 custom directives for exploring phase portraits, Lyapunov functions, stability regions, and sliding surfaces.

**Features:**
- Phase portraits with vector fields and trajectory tracking
- 3D Lyapunov energy surfaces with rotation/zoom controls
- Parameter space stability heatmaps with metric selection
- Sliding mode surfaces with adjustable boundary layers
- Control signal time-series with switching function overlays
- Multi-parameter sweep optimization visualizations

**[Explore Visualizations →](mathematical-visualizations-demo.md)**

---

### 3D Interactive Pendulum Visualization

**Immersive 3D simulation** with Three.js WebGL rendering. Rotate, zoom, and watch the double inverted pendulum in real-time.

**Features:**
- Realistic physics simulation
- Orbit controls (mouse drag to rotate)
- Real-time state visualization
- Mobile-friendly touch controls

**[Launch 3D Demo →](3d-pendulum-demo.md)** (Coming soon)

---

## Quick Start Guide

### System Requirements

**Browser Compatibility:**
- Chrome 90+ (recommended)
- Firefox 88+
- Safari 14+
- Edge 90+

**Requirements:**
- JavaScript enabled
- WebAssembly support (automatic in modern browsers)
- 2GB+ RAM recommended
- Stable internet connection (first load only)

### First-Time Setup

**No setup required!** Interactive features work immediately in supported browsers:

1. **Click "Run Code"** on any Python example
2. **First execution**: 15-30 seconds to download Python runtime (~60MB)
3. **Subsequent runs**: Instant (cached in browser)

---

## Interactive Example Gallery

Explore these enhanced pages with live, executable examples:

### Tutorials with Live Code

**[Tutorial 01: First Simulation](../tutorials/tutorial-01-first-simulation.md)**
- Interactive sliding surface calculator
- Live gain tuning experiments
- Real-time control response visualization

**[Tutorial 02: Controller Comparison](../tutorials/tutorial-02-controller-comparison.md)** (Coming in Phase 3)
- Side-by-side controller performance
- Interactive Plotly charts
- Live parameter sweeps

### Theory with Visualization

**[SMC Theory](../theory/smc-theory.md)**
- Phase portrait visualization
- Stability region calculator
- Lyapunov function plotter

**[PSO Theory](../theory/pso-theory.md)** (Coming in Phase 3)
- Particle swarm animation
- Convergence visualization
- Interactive hyperparameter tuning

---

## Technical Details

### Architecture

```
[Browser]
  └─ [Main Thread]
       ├─ pyodide-runner.js (UI controller)
       └─ [Web Worker]
            ├─ Pyodide Runtime (Python 3.11 WASM)
            ├─ NumPy Package (~25MB)
            └─ Matplotlib Package (~22MB)
```

### Performance

- **Execution Speed:** 50-70% of native Python
- **Memory Limit:** ~2GB (browser constraint)
- **Timeout:** 10 seconds per execution
- **Cache Size:** ~60MB total

### Security

All code executes in a sandboxed Web Worker:
- No access to local filesystem
- No system calls
- No network access (CORS restricted)
- Isolated from main browser context

---

## Troubleshooting

### "Loading Python runtime..." takes forever

**Solution:** First load requires downloading ~60MB. Wait 30-60 seconds. Check internet connection.

### Code execution timeout

**Solution:** Reduce array sizes or simplify algorithm. Pyodide is 50-70% speed of native Python.

### Figures not displaying

**Solution:** Ensure `plt.show()` is called. Try simpler plot first. Check browser console for errors.

### Reset to defaults

**Solution:** Click "Reset" button or clear browser LocalStorage.

---

## Browser Testing Status

Tested and verified on:
- ✅ Chrome 120+ (Windows/macOS/Linux)
- ✅ Firefox 121+ (Windows/macOS/Linux)
- ✅ Safari 17+ (macOS/iOS)
- ✅ Edge 120+ (Windows)

---

## Feedback and Support

Found a bug or have suggestions? [Open an issue on GitHub](https://github.com/theSadeQ/dip-smc-pso/issues)

---

**Ready to experiment?** Start with **[Live Python Demo →](live-python-demo.md)**

---

**[AI] Generated with Claude Code**
**Phase 2**: Live Python Code Execution
**Phase 3**: Plotly Interactive Charts
**Phase 4**: Jupyter Notebooks Integration
**Phase 5**: Mathematical Visualizations


```{toctree}
:hidden:

3d-pendulum-demo
jupyter-notebooks-demo
live-python-demo
mathematical-visualizations-demo
plotly-charts-demo
```
---

**Navigation**: Return to [Master Navigation Hub](../../NAVIGATION.md) | Browse all [Documentation Categories](../../index.md)
