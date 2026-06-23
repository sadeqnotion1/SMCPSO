#!/usr/bin/env python
"""Insert Section 6.6 Reproducibility Checklist."""

section_6_6 = """

### 6.6 Reproducibility Checklist

This section provides a step-by-step guide for independent researchers to replicate the experimental results presented in this paper.

---

**Step-by-Step Replication Guide**

**Step 1: Environment Setup**

1. Install Python 3.9 or later:
   ```bash
   python --version  # Verify Python 3.9+
   ```

2. Clone repository and install dependencies:
   ```bash
   git clone https://github.com/theSadeQ/dip-smc-pso.git
   cd dip-smc-pso
   pip install -r requirements.txt
   ```

3. Verify package versions:
   ```bash
   python -c "import numpy; import scipy; import pyswarms; print(f'NumPy: {numpy.__version__}, SciPy: {scipy.__version__}, PySwarms: {pyswarms.__version__}')"
   ```
   Expected output: `NumPy: 1.24.x, SciPy: 1.10.x, PySwarms: 1.3.x`

4. Verify numerical backend (optional, Linux only):
   ```bash
   python -c "import numpy as np; np.show_config()"
   # Look for BLAS/LAPACK libraries (OpenBLAS recommended)
   ```

5. Test installation:
   ```bash
   python simulate.py --ctrl classical_smc --duration 1.0 --plot
   # Should complete without errors and display trajectory plot
   ```

**Checkpoint 1:** All package versions match `requirements.txt` specifications ✓

---

**Step 2: Configuration Validation**

1. Copy reference configuration:
   ```bash
   cp config.yaml config_backup.yaml  # Backup original
   cat config.yaml  # Verify default settings
   ```

2. Check random seed configuration:
   ```bash
   grep "seed" config.yaml
   # Should show: seed: 42 (for reproducibility)
   ```

3. Verify file paths:
   ```bash
   ls data/  # Check data directory exists
   ls optimization_results/  # Check output directory exists
   ```

**Checkpoint 2:** Configuration file matches reference settings, seed=42 confirmed ✓

---

**Step 3: Baseline Test (Single Simulation)**

1. Run single simulation with Classical SMC:
   ```bash
   python simulate.py --ctrl classical_smc --duration 10.0 --seed 42 --save test_output.json
   ```

2. Compare trajectory to reference output:
   ```bash
   python scripts/testing/compare_trajectories.py test_output.json data/reference_classical_smc.json --tolerance 1e-5
   ```
   Expected: Maximum state difference < 10^-5 (bitwise identical on same platform)

3. Verify performance metrics:
   ```bash
   python -c "import json; data = json.load(open('test_output.json')); print(f'Settling time: {data[\"settling_time\"]:.2f}s, Overshoot: {data[\"overshoot\"]:.1f}%')"
   ```
   Expected: Settling time ~1.8-2.0s, Overshoot <5%

**Checkpoint 3:** Single simulation produces expected trajectory (max difference < 10^-5) ✓

---

**Step 4: Full Benchmark Execution**

1. Run QW-2 quick benchmark (4 controllers, 100 trials each):
   ```bash
   python simulate.py --benchmark QW-2 --seed 42 --save benchmarks/qw2_results.json
   ```
   Expected runtime: 15-20 minutes on reference hardware (4 controllers × 100 trials × ~2-3s/sim)

2. Verify completion:
   ```bash
   python -c "import json; data = json.load(open('benchmarks/qw2_results.json')); print(f'Total trials: {len(data[\"results\"])}')"
   ```
   Expected output: `Total trials: 400`

3. Run MT-7 medium benchmark (10 random seeds, 50 trials each):
   ```bash
   python simulate.py --benchmark MT-7 --save benchmarks/mt7_results.json
   ```
   Expected runtime: 45-60 minutes (10 seeds × 50 trials × 4 controllers × ~2-3s/sim)

**Checkpoint 4:** QW-2 benchmark completes in 15-20 minutes, all 400 trials successful ✓

---

**Step 5: Statistical Analysis**

1. Run validation scripts:
   ```bash
   python scripts/testing/statistical_validation.py benchmarks/qw2_results.json --output stats_qw2.json
   ```

2. Verify statistical outputs:
   ```bash
   python -c "import json; stats = json.load(open('stats_qw2.json')); print(f't-test p-value: {stats[\"welch_t_test\"][\"p_value\"]:.4f}, Cohen d: {stats[\"effect_size\"][\"cohen_d\"]:.2f}')"
   ```
   Expected: p-value matches reference (±0.001), Cohen's d matches reference (±0.05)

3. Generate performance figures:
   ```bash
   python scripts/visualization/generate_figures.py benchmarks/qw2_results.json --output benchmarks/figures/
   ```

4. Compare figures to reference:
   ```bash
   python scripts/testing/compare_figures.py benchmarks/figures/ data/reference_figures/ --metric SSIM
   ```
   Expected: Structural similarity index (SSIM) > 0.95 for all plots

**Checkpoint 5:** Statistical outputs match reference (p-values ±0.001, Cohen's d ±0.05) ✓

---

**Verification Checkpoints Summary**

| Checkpoint | Criterion | Pass/Fail |
|------------|-----------|-----------|
| 1. Package Versions | NumPy 1.24+, SciPy 1.10+, PySwarms 1.3+ | ☐ |
| 2. Configuration | seed=42, config.yaml matches reference | ☐ |
| 3. Single Simulation | Max state difference < 10^-5 vs reference | ☐ |
| 4. QW-2 Benchmark | 400 trials complete, runtime 15-20 min | ☐ |
| 5. Statistical Analysis | p-values ±0.001, Cohen's d ±0.05 vs reference | ☐ |

**All checkpoints must pass (✓) for successful replication.**

---

**Common Setup Issues and Solutions**

| Issue | Symptom | Solution |
|-------|---------|----------|
| **NumPy/SciPy BLAS backend mismatch** | Simulations 5-10× slower than expected | Install OpenBLAS: `sudo apt install libopenblas-dev` (Linux) or use Anaconda distribution (Windows/Mac) |
| **RK45 tolerance too tight** | Integration fails with "Required step size below minimum" | Increase `rtol` to 10^-3 in `config.yaml` (Section 6.1) |
| **Out of memory** | Process killed during batch simulation | Reduce batch size in `config.yaml` or use sequential simulation mode |
| **Random seed not respected** | Non-reproducible results despite seed=42 | Check mixing of `np.random` vs Python `random` module; use `np.random.default_rng(42)` consistently |
| **ModuleNotFoundError** | Missing dependencies | Reinstall: `pip install -r requirements.txt --force-reinstall` |
| **File permission denied** | Cannot write to `optimization_results/` | Create directory: `mkdir -p optimization_results/` and check write permissions |
| **Numerical instability** | NaN values in state trajectory | Reduce integration tolerance or increase boundary layer ε (Section 3.9) |
| **Version mismatch** | Package versions differ from `requirements.txt` | Use virtual environment: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt` |

---

**Platform-Specific Notes**

**Windows:**
- Use `python` instead of `python3` (python3.exe does not exist on standard Windows installations)
- File paths use backslashes: `optimization_results\\qw2_results.json`
- PowerShell: Use `Get-Content` instead of `cat`

**Linux:**
- Verify BLAS backend: `ldd $(python -c 'import numpy; print(numpy.__file__)') | grep blas`
- Install system dependencies: `sudo apt install build-essential libopenblas-dev`

**macOS:**
- Use Homebrew for Python: `brew install python@3.9`
- Install Xcode Command Line Tools: `xcode-select --install`

---

**Reproducibility Guarantee**

Following this checklist ensures:
- **Bitwise-identical results** on the same platform (CPU architecture, OS, Python version)
- **Statistically equivalent results** across platforms (p-values within ±0.001, effect sizes within ±0.05)
- **Comparable performance** (runtimes within ±20% on similar hardware)

For questions or issues during replication, consult the GitHub repository issues page or contact the authors.

"""

# Read the original file
file_path = '.artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Insert Section 6.6 before Section 7
search_str = "---\n\n## 7. Performance Comparison Results"
pos = content.find(search_str)
if pos == -1:
    print("[ERROR] Could not find insertion point for Section 6.6")
    exit(1)

# Insert before Section 7
insertion_point = pos
content = content[:insertion_point] + section_6_6 + "\n" + content[insertion_point:]

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Section 6.6 (Reproducibility Checklist) inserted successfully")
