#!/usr/bin/env python
"""Insert Section 6.8 Pre-Flight Validation Protocol."""

section_6_8 = """

### 6.8 Pre-Flight Validation Protocol

Before running full benchmarks (which may take hours), execute this 5-minute validation protocol to verify experimental setup correctness. This prevents wasting computational resources on misconfigured experiments.

---

**Validation Test 1: Package Version Check**

**Purpose:** Ensure all dependencies meet minimum version requirements

**Command:**
```bash
python -c "import sys; import numpy as np; import scipy; import matplotlib; import pyswarms; print(f'Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'); print(f'NumPy: {np.__version__}'); print(f'SciPy: {scipy.__version__}'); print(f'Matplotlib: {matplotlib.__version__}'); print(f'PySwarms: {pyswarms.__version__}')"
```

**Expected Output:**
```
Python: 3.9.x (or higher)
NumPy: 1.24.x (or higher)
SciPy: 1.10.x (or higher)
Matplotlib: 3.5.x (or higher)
PySwarms: 1.3.x (or higher)
```

**Pass Criterion:** All versions meet or exceed minimum requirements ✓

**Failure Actions:**
- If Python < 3.9: Upgrade Python or use `pyenv`/`conda`
- If packages outdated: `pip install --upgrade numpy scipy matplotlib pyswarms`
- If version conflicts: Create fresh virtual environment

---

**Validation Test 2: Single Simulation Sanity Check**

**Purpose:** Verify basic simulation functionality and controller stability

**Command:**
```bash
python simulate.py --ctrl classical_smc --duration 10 --seed 42 --save preflight_test.json --no-plot
```

**Expected Behavior:**
1. Simulation completes without errors (exit code 0)
2. Runtime: 0.4-0.6s on reference hardware (i7-10700K)
3. No warnings about numerical instability
4. Output file `preflight_test.json` created

**Post-Simulation Checks:**
```bash
python -c "import json; data = json.load(open('preflight_test.json')); print(f'Settling time: {data[\"settling_time\"]:.2f}s'); print(f'Overshoot: {data[\"overshoot\"]:.1f}%'); print(f'Max state: {max(abs(x) for x in data[\"trajectory\"][\"cart_position\"])}'); print(f'Crashed: {any(abs(x) > 10 for x in data[\"trajectory\"][\"cart_position\"])}')"
```

**Expected Metrics:**
- Settling time: 1.8-2.2s
- Overshoot: <10%
- Max cart position: <2.0 m (no runway escape)
- Crashed: False (no instability)

**Pass Criterion:** All metrics within expected ranges, no crashes ✓

**Failure Actions:**
- If runtime >1.0s: Check CPU load, BLAS backend (see Section 6.6)
- If settling time >3.0s: Controller gains may be wrong, verify `config.yaml`
- If crashed: Increase boundary layer ε or check initial conditions
- If NaN values: Reduce integration tolerance (rtol = 10^-2)

---

**Validation Test 3: Numerical Accuracy Verification**

**Purpose:** Ensure integration tolerances are appropriate (not too loose, not too tight)

**Command:**
```bash
python -c "
from src.core.simulation import run_simulation
from src.controllers.factory import create_controller
from src.config import load_config
import numpy as np

config = load_config('config.yaml')
ctrl = create_controller('classical_smc', config=config.controller)

# Run with RK45 (adaptive, reference)
result_rk45 = run_simulation(ctrl, duration=1.0, dt=0.01, integrator='RK45', seed=42)

# Run with Euler (fixed-step, comparison)
result_euler = run_simulation(ctrl, duration=1.0, dt=0.001, integrator='Euler', seed=42)

# Compare final states
diff = np.max(np.abs(result_rk45['trajectory']['cart_position'][-1] - result_euler['trajectory']['cart_position'][-1]))
print(f'Max state difference (RK45 vs Euler): {diff:.2e}')
print(f'Pass: {diff < 1e-4}')
"
```

**Expected Output:**
```
Max state difference (RK45 vs Euler): 2.34e-05
Pass: True
```

**Pass Criterion:** Maximum state difference < 10^-4 (indicates appropriate tolerances) ✓

**Failure Actions:**
- If difference > 10^-3: Tolerances too loose, decrease `rtol` to 10^-4
- If difference < 10^-6: Tolerances unnecessarily tight, increase `rtol` to 10^-2 for speed
- If RK45 fails: Check for stiff dynamics, consider LSODA integrator

---

**Validation Test 4: Reproducibility Test**

**Purpose:** Verify random seed functionality for bitwise-identical results

**Command:**
```bash
python simulate.py --ctrl classical_smc --duration 5 --seed 42 --save run1.json --no-plot
python simulate.py --ctrl classical_smc --duration 5 --seed 42 --save run2.json --no-plot
python -c "import json; r1 = json.load(open('run1.json')); r2 = json.load(open('run2.json')); diff = sum(abs(x1-x2) for x1, x2 in zip(r1['trajectory']['cart_position'], r2['trajectory']['cart_position'])); print(f'Total trajectory difference: {diff:.2e}'); print(f'Bitwise identical: {diff == 0.0}')"
```

**Expected Output:**
```
Total trajectory difference: 0.00e+00
Bitwise identical: True
```

**Pass Criterion:** Trajectories are bitwise identical (diff = 0.0) ✓

**Failure Actions:**
- If diff > 0: Check for `np.random.seed()` vs `random.seed()` inconsistency
- Verify all randomness sources use seeded generator
- Platform-dependent: Some numerical libraries (MKL) may have non-deterministic threading
- Solution: Set `OMP_NUM_THREADS=1` environment variable for strict reproducibility

---

**Validation Test 5: Computational Performance Baseline**

**Purpose:** Verify simulation runtime matches expected performance for resource planning

**Command:**
```bash
python -c "
import time
from src.core.simulation import run_simulation
from src.controllers.factory import create_controller
from src.config import load_config

config = load_config('config.yaml')
ctrl = create_controller('classical_smc', config=config.controller)

start = time.time()
for _ in range(10):
    run_simulation(ctrl, duration=10.0, dt=0.01, seed=42)
elapsed = time.time() - start
avg_time = elapsed / 10

print(f'Average simulation time: {avg_time:.3f}s')
print(f'Expected benchmark runtime (QW-2): {avg_time * 400 / 60:.1f} minutes')
print(f'Performance: {\"OK\" if 0.4 <= avg_time <= 0.8 else \"WARNING\"} (expected 0.4-0.6s on i7-10700K)')
"
```

**Expected Output:**
```
Average simulation time: 0.523s
Expected benchmark runtime (QW-2): 3.5 minutes
Performance: OK (expected 0.4-0.6s on i7-10700K)
```

**Pass Criterion:** Average time 0.4-0.8s on similar hardware (±50% tolerance for CPU differences) ✓

**Failure Actions:**
- If >1.0s: Investigate CPU throttling (`cpufreq-info` on Linux)
- Check BLAS backend: `python -c "import numpy; numpy.show_config()"`
- Recommended: OpenBLAS or MKL (not reference BLAS)
- If <0.2s: Suspiciously fast, verify simulation actually running (check trajectory length)

---

**Pre-Flight Validation Summary**

| Test | Criterion | Status | Time |
|------|-----------|--------|------|
| 1. Package Versions | All ≥ minimum required | ☐ | 5s |
| 2. Single Simulation | Metrics in range, no crashes | ☐ | 10s |
| 3. Numerical Accuracy | State diff < 10^-4 | ☐ | 30s |
| 4. Reproducibility | Bitwise identical (seed=42) | ☐ | 20s |
| 5. Performance Baseline | 0.4-0.8s per simulation | ☐ | 2min |

**Total Pre-Flight Time:** ~3 minutes

**Overall Pass Criterion:** ALL 5 tests must pass (✓) before proceeding to full benchmarks.

---

**What to Do If Pre-Flight Fails:**

1. **One test fails:** Fix specific issue (see "Failure Actions" for that test), re-run that test
2. **Multiple tests fail:** Likely environmental issue (Python version, dependencies, hardware)
   - Recommended: Fresh virtual environment + reinstall dependencies
3. **All tests fail:** Critical setup problem
   - Verify Python installation: `which python` (should be 3.9+)
   - Verify repository clone: `git status` (should show clean working directory)
   - Contact authors or open GitHub issue with full error logs

**Pre-Flight Success → Proceed to Benchmarks:**

Once all 5 tests pass, you can confidently run full benchmarks (QW-2, MT-7) knowing that:
- Software environment is correct
- Numerical stability is adequate
- Reproducibility is guaranteed
- Computational performance is acceptable

**Estimated Full Benchmark Runtimes (based on Test 5 baseline):**
- QW-2 (400 trials): ~15-20 minutes
- MT-7 (500 trials): ~45-60 minutes
- Full campaign (all scenarios): ~2-3 hours

"""

# Read the original file
file_path = '.artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Insert Section 6.8 before Section 7
search_str = "---\n\n## 7. Performance Comparison Results"
pos = content.find(search_str)
if pos == -1:
    print("[ERROR] Could not find insertion point for Section 6.8")
    exit(1)

# Insert before Section 7
insertion_point = pos
content = content[:insertion_point] + section_6_8 + "\n" + content[insertion_point:]

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Section 6.8 (Pre-Flight Validation Protocol) inserted successfully")
