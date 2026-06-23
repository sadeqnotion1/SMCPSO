# Live Python Code Execution

**Revolutionary Feature**: Run Python code directly in your browser with NumPy, Matplotlib, and zero installation required.

This page demonstrates Pyodide - Python compiled to WebAssembly. Edit code, click Run, and see results instantly. Perfect for learning, experimentation, and interactive documentation.

---

## Quick Start Guide

**How to Use:**
1. **Click "Run Code"** - Executes Python in your browser
2. **Edit Inline** - Modify code directly in the block
3. **See Results** - stdout, figures, and errors display below
4. **Reset Anytime** - Restore original code

**Keyboard Shortcut:** Press `Ctrl+Enter` (or `Cmd+Enter` on Mac) to run code

```{admonition} First Run Notice
:class: warning
**First execution takes 15-30 seconds** to download Python runtime + packages (~60MB).
Subsequent runs are instant (cached in browser). Please be patient!
```

---

## System Requirements

```{eval-rst}
.. pyodide-info::
   :show-requirements:
   :show-packages:
   :show-limitations:
```

---

## Example 1: Hello World + NumPy Verification

Let's verify Python and NumPy are working correctly:

```{eval-rst}
.. runnable-code::
   :language: python
   :caption: Example 1 - Hello World with NumPy
   :preload: numpy

   print("🐍 Python running in your browser!")
   print("=" * 50)

   import numpy as np
   print(f"NumPy version: {np.__version__}")
   print(f"NumPy loaded successfully!")

   # Create array and perform operations
   arr = np.array([1, 2, 3, 4, 5])
   print(f"\nArray: {arr}")
   print(f"Sum: {arr.sum()}")
   print(f"Mean: {arr.mean()}")
   print(f"Std Dev: {arr.std():.3f}")

   # Matrix operations
   matrix = np.array([[1, 2], [3, 4]])
   print(f"\nMatrix:\n{matrix}")
   print(f"Determinant: {np.linalg.det(matrix):.1f}")
```

**What's Happening:**
- Python 3.11 executes in a Web Worker (non-blocking)
- NumPy loads on-demand (~25MB, cached after first load)
- stdout captured and displayed in output panel
- All standard NumPy functions available

---

## Example 2: Matplotlib Visualization

Generate interactive plots with Matplotlib:

```{eval-rst}
.. runnable-code::
   :language: python
   :caption: Example 2 - Matplotlib Sine Wave Visualization
   :preload: numpy,matplotlib
   :timeout: 15000

   import numpy as np
   import matplotlib.pyplot as plt

   # Generate data
   t = np.linspace(0, 10, 200)
   y1 = np.sin(t)
   y2 = np.sin(2 * t)
   y3 = np.sin(3 * t)

   # Create figure with subplots
   fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

   # Plot 1: Multiple sine waves
   ax1.plot(t, y1, 'b-', linewidth=2, label='sin(t)')
   ax1.plot(t, y2, 'r--', linewidth=2, label='sin(2t)')
   ax1.plot(t, y3, 'g:', linewidth=2, label='sin(3t)')
   ax1.set_xlabel('Time (s)')
   ax1.set_ylabel('Amplitude')
   ax1.set_title('Multiple Frequency Sine Waves')
   ax1.legend()
   ax1.grid(True, alpha=0.3)

   # Plot 2: Amplitude envelope
   envelope = np.abs(y1) + np.abs(y2) + np.abs(y3)
   ax2.fill_between(t, 0, envelope, alpha=0.3, color='purple')
   ax2.plot(t, envelope, 'purple', linewidth=2)
   ax2.set_xlabel('Time (s)')
   ax2.set_ylabel('Combined Amplitude')
   ax2.set_title('Amplitude Envelope')
   ax2.grid(True, alpha=0.3)

   plt.tight_layout()
   plt.show()

   print(f"✓ Figure generated with {len(t)} data points")
   print(f"✓ Peak amplitude: {envelope.max():.2f}")
```

**What's Happening:**
- Matplotlib uses 'Agg' backend (non-interactive, renders to PNG)
- Figures converted to base64 PNG (~100-500KB each)
- Multiple figures supported (all displayed inline)
- All Matplotlib features work: subplots, styling, annotations, legends

---

## Example 3: Array Broadcasting & Linear Algebra

Explore NumPy's powerful array operations:

```{eval-rst}
.. runnable-code::
   :language: python
   :caption: Example 3 - Advanced NumPy Operations
   :preload: numpy

   import numpy as np

   # Broadcasting example
   print("=== Array Broadcasting ===")
   x = np.array([[1], [2], [3]])  # Shape: (3, 1)
   y = np.array([10, 20, 30])     # Shape: (3,)

   result = x + y  # Broadcasting
   print(f"x shape: {x.shape}")
   print(f"y shape: {y.shape}")
   print(f"Result shape: {result.shape}")
   print(f"Result:\n{result}")

   # Linear algebra
   print("\n=== Linear Algebra ===")
   A = np.array([[4, 2], [3, 1]])
   b = np.array([8, 5])

   # Solve Ax = b
   x_solution = np.linalg.solve(A, b)
   print(f"Matrix A:\n{A}")
   print(f"Vector b: {b}")
   print(f"Solution x: {x_solution}")
   print(f"Verification Ax: {A @ x_solution}")

   # Eigenvalues
   eigenvalues, eigenvectors = np.linalg.eig(A)
   print(f"\nEigenvalues: {eigenvalues}")
   print(f"Eigenvectors:\n{eigenvectors}")

   # Matrix properties
   print(f"\nDeterminant: {np.linalg.det(A):.2f}")
   print(f"Trace: {np.trace(A)}")
   print(f"Condition number: {np.linalg.cond(A):.2f}")
```

**Try This:**
- Change matrix A to be singular (det=0) and see what happens
- Try larger matrices (10x10, 100x100)
- Experiment with different broadcasting shapes

---

## Example 4: Random Number Generation & Statistics

NumPy's random module for statistical analysis:

```{eval-rst}
.. runnable-code::
   :language: python
   :caption: Example 4 - Statistical Analysis with NumPy
   :preload: numpy,matplotlib

   import numpy as np
   import matplotlib.pyplot as plt

   # Set random seed for reproducibility
   np.random.seed(42)

   # Generate random data
   normal_data = np.random.normal(loc=0, scale=1, size=1000)
   uniform_data = np.random.uniform(low=-2, high=2, size=1000)

   # Statistical analysis
   print("=== Normal Distribution ===")
   print(f"Mean: {normal_data.mean():.3f}")
   print(f"Std Dev: {normal_data.std():.3f}")
   print(f"Min: {normal_data.min():.3f}")
   print(f"Max: {normal_data.max():.3f}")
   print(f"Median: {np.median(normal_data):.3f}")
   print(f"25th percentile: {np.percentile(normal_data, 25):.3f}")
   print(f"75th percentile: {np.percentile(normal_data, 75):.3f}")

   # Visualization
   fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

   # Histogram
   ax1.hist(normal_data, bins=30, alpha=0.7, color='blue', edgecolor='black')
   ax1.set_xlabel('Value')
   ax1.set_ylabel('Frequency')
   ax1.set_title('Normal Distribution (μ=0, σ=1)')
   ax1.grid(True, alpha=0.3)

   # Comparison
   ax2.hist(normal_data, bins=30, alpha=0.5, color='blue', label='Normal')
   ax2.hist(uniform_data, bins=30, alpha=0.5, color='red', label='Uniform')
   ax2.set_xlabel('Value')
   ax2.set_ylabel('Frequency')
   ax2.set_title('Distribution Comparison')
   ax2.legend()
   ax2.grid(True, alpha=0.3)

   plt.tight_layout()
   plt.show()

   print(f"\n✓ Generated {len(normal_data)} samples")
```

**Try This:**
- Change `size=1000` to `size=10000` for smoother histograms
- Try different distributions: `np.random.exponential()`, `np.random.poisson()`
- Experiment with different bin counts

---

## Troubleshooting

### Issue: "Loading Python runtime..." takes forever

**Cause:** Slow internet connection or CDN issues

**Solutions:**
1. Wait patiently (first load: 15-30s, sometimes up to 60s)
2. Check browser DevTools console for errors
3. Try refreshing page
4. Try different browser
5. Check internet connection

### Issue: Execution timeout after 10 seconds

**Cause:** Code takes too long to execute

**Solutions:**
1. Reduce data size (smaller arrays, fewer iterations)
2. Simplify algorithm
3. Check for infinite loops
4. Note: Pyodide is 50-70% speed of native Python

### Issue: "Failed to load matplotlib"

**Cause:** Package loading failed

**Solutions:**
1. Refresh page and try again
2. Check internet connection
3. Clear browser cache
4. Try different browser

### Issue: Figures not displaying

**Cause:** `plt.show()` not called or figure errors

**Solutions:**
1. Make sure to call `plt.show()` at the end
2. Check for matplotlib errors in output
3. Try simpler plot first
4. Verify NumPy arrays have correct shape

### Issue: Code persists after refresh

**Behavior:** Edited code is saved in LocalStorage

**To Reset:**
1. Click "Reset" button, OR
2. Clear browser LocalStorage, OR
3. Use incognito/private mode

---

## Limitations & Performance

### What Works
✅ Full Python 3.11 standard library
✅ NumPy (all operations)
✅ Matplotlib (all plot types)
✅ SciPy (optional, adds 30MB)
✅ Math, statistics, itertools, etc.
✅ List comprehensions, generators
✅ Classes, decorators, context managers

### What Doesn't Work
❌ File I/O (`open()`, file reading/writing)
❌ Multiprocessing/threading
❌ System calls (`os.system()`, subprocess)
❌ Network requests (limited by CORS)
❌ Native extensions (C libraries)
❌ pip install (use preloaded packages only)

### Performance
- **Speed:** 50-70% of native Python
- **Memory:** Limited to ~2GB (browser limit)
- **Timeout:** 10 seconds per execution
- **Startup:** 15-30s first load, instant after caching

---

## Related Pages

- {doc}`/guides/tutorials/tutorial-01-first-simulation` - Interactive controller gain experiments
- {doc}`/guides/tutorials/tutorial-03-pso-optimization` - PSO convergence visualization
- {doc}`/guides/theory/smc-theory` - Phase portrait visualization
- {doc}`/guides/interactive/3d-pendulum-demo` - 3D interactive pendulum

---

## Technical Details

### Architecture
```
[Browser]
  └─ [Main Thread]
       ├─ pyodide-runner.js (UI controller)
       └─ [Web Worker]
            ├─ Pyodide Runtime (Python 3.11 WASM)
            ├─ NumPy Package
            └─ Matplotlib Package
```

### Loading Sequence
1. User clicks "Run Code" (first time)
2. Worker initializes Pyodide (~8MB, 3-5s)
3. Load NumPy (~25MB, 5-8s)
4. Load Matplotlib (~22MB, 4-6s)
5. Execute user code (<1s for simple code)
6. Capture stdout + figures
7. Display results

**Total first load:** 15-30 seconds
**Subsequent runs:** <2 seconds (cached)

### Caching Strategy
- Pyodide runtime cached in browser IndexedDB
- Packages cached in Service Worker
- Persists across sessions
- ~60MB total cache size

---

**Ready to experiment?** Try modifying the examples above and click Run!

**[AI] Generated with Claude Code**
**Phase 2**: Live Python Code Execution (Revolutionary Interactive Documentation)
