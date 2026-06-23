# Integration Testing Guide

**Document Version:** 1.0
**Date:** November 12, 2025
**Status:** OPERATIONAL
**Test Suite:** `tests/test_integration/test_cross_component.py`

---

## Table of Contents

1. [Overview](#overview)
2. [Test Matrix](#test-matrix)
3. [Quick Start](#quick-start)
4. [Performance Metrics](#performance-metrics)
5. [Regression Detection](#regression-detection)
6. [Baseline Benchmarks](#baseline-benchmarks)
7. [Troubleshooting](#troubleshooting)
8. [Continuous Integration](#continuous-integration)

---

## Overview

The integration testing framework validates the interaction between controllers, dynamics models, and PSO configurations to ensure:

- **System stability**: No crashes during execution
- **Performance bounds**: Metrics within acceptable limits
- **Regression prevention**: No performance degradation over time
- **Cross-component compatibility**: All combinations work together

**Test Coverage:**
- **Controllers:** 7 types (Classical SMC, STA, Adaptive, Hybrid, Swing-Up, MPC)
- **Dynamics:** 2 types (Simplified, Full)
- **PSO Configs:** 3 variants (Default, Aggressive, Conservative)
- **Total Test Cases:** 7 × 2 × 3 = 42 test cases (excluding known incompatibilities)

---

## Test Matrix

### Controllers (7 types)

1. **Classical SMC** (`classical_smc`)
   - Traditional sliding mode control
   - Fast response, moderate chattering

2. **Super-Twisting Algorithm** (`sta_smc`)
   - Second-order SMC
   - Reduced chattering, smooth control

3. **Adaptive SMC** (`adaptive_smc`)
   - Parameter adaptation
   - Robust to model uncertainty

4. **Hybrid Adaptive STA-SMC** (`hybrid_adaptive_sta_smc`)
   - Combined adaptive + super-twisting
   - Best robustness and smoothness

5. **Swing-Up SMC** (`swing_up_smc`)
   - Energy-based swing-up + SMC stabilization
   - For large initial angles

6. **MPC Controller** (`mpc_controller`)
   - Model Predictive Control (experimental)
   - Constraint handling, optimal trajectories

### Dynamics Models (2 types)

1. **Simplified** (`simplified`)
   - Linearized dynamics
   - Fast simulation (~10ms per run)
   - Suitable for controller tuning

2. **Full** (`full`)
   - Nonlinear dynamics
   - Accurate physics (~50ms per run)
   - Suitable for validation

### PSO Configurations (3 variants)

1. **Default** (`default`)
   - Balanced exploration/exploitation
   - c1=2.0, c2=2.0, w=0.7

2. **Aggressive** (`aggressive`)
   - High velocity, fast convergence
   - c1=2.5, c2=2.5, w=0.9

3. **Conservative** (`conservative`)
   - Low velocity, robust convergence
   - c1=1.5, c2=1.5, w=0.4

---

## Quick Start

### Run All Integration Tests

```bash
# Run full test suite (42 test cases)
pytest tests/test_integration/test_cross_component.py -v

# Expected output:
# test_cross_component_integration[classical_smc-simplified-default] PASSED
# test_cross_component_integration[classical_smc-simplified-aggressive] PASSED
# ...
# ====== 42 passed in 120.00s (2 minutes) ======
```

### Run Specific Test Case

```bash
# Test Classical SMC + Simplified + Default
pytest tests/test_integration/test_cross_component.py::test_cross_component_integration[classical_smc-simplified-default] -v

# Test all variants of STA-SMC
pytest tests/test_integration/test_cross_component.py -k "sta_smc" -v

# Test all Aggressive PSO configurations
pytest tests/test_integration/test_cross_component.py -k "aggressive" -v
```

### Generate Baseline Benchmarks

```bash
# Generate baseline benchmarks (run once)
pytest tests/test_integration/test_cross_component.py::test_generate_baseline_benchmarks -v

# Output: benchmarks/baseline_integration.csv
```

### View Test Summary

```bash
# Print test matrix information
pytest tests/test_integration/test_cross_component.py::test_print_integration_summary -v -s

# Output:
# ================================================================================
#  Cross-Component Integration Test Matrix
# ================================================================================
#  Controllers: 7
#  Dynamics: 2
#  PSO Configs: 3
#  Total Test Cases: 42
# ...
```

---

## Performance Metrics

The integration tests measure four key performance metrics:

### 1. Settling Time

**Definition:** Time for system to reach ±2% of final value

**Threshold:** <10.0 seconds

**Typical Values:**
- Classical SMC: 3.0-3.5s
- STA-SMC: 2.8-3.0s
- Adaptive SMC: 2.9-3.1s
- Hybrid: 2.7-2.9s (best)
- Swing-Up: 4.5-5.0s (large initial angle)
- MPC: 3.5-3.8s

**Calculation:**
```python
# Find first time cart position reaches ±2% of final value
final_pos = cart_pos[-1]
threshold = 0.02 * abs(final_pos)
settled_idx = np.where(np.abs(cart_pos - final_pos) < threshold)[0]
settling_time = time_vector[settled_idx[0]]
```

### 2. Overshoot

**Definition:** Maximum deviation from final value (percentage)

**Threshold:** <20.0%

**Typical Values:**
- Classical SMC: 5-6%
- STA-SMC: 4-5%
- Adaptive SMC: 3-4%
- Hybrid: 3-4% (best)
- Swing-Up: 8-9%
- MPC: 5-6%

**Calculation:**
```python
# Max deviation from final value
overshoot = np.max(np.abs(cart_pos - final_pos)) / (abs(final_pos) + 1e-6) * 100
```

### 3. Energy

**Definition:** Integral of control effort squared (∫u²dt)

**Threshold:** <1000.0

**Typical Values:**
- Classical SMC: 120-140
- STA-SMC: 105-120
- Adaptive SMC: 95-110
- Hybrid: 88-100 (best)
- Swing-Up: 180-200 (high initial energy)
- MPC: 140-155

**Calculation:**
```python
# Integrate control signal squared
dt = time_vector[1] - time_vector[0]
energy = np.sum(control_history**2) * dt
```

### 4. Chattering Frequency

**Definition:** Control signal oscillation frequency (Hz)

**Threshold:** (informational only, no hard limit)

**Typical Values:**
- Classical SMC: 15-18Hz (high)
- STA-SMC: 8-10Hz (reduced)
- Adaptive SMC: 6-7Hz (low)
- Hybrid: 5-6Hz (lowest)
- Swing-Up: 22-26Hz
- MPC: 18-22Hz

**Calculation:**
```python
# Count zero-crossings in control signal
control_diff = np.diff(np.sign(control_history.flatten()))
chattering_freq = np.sum(np.abs(control_diff)) / (2 * time_vector[-1])
```

---

## Regression Detection

The integration tests include automatic regression detection by comparing current performance against baseline benchmarks.

### Regression Thresholds

| Metric | Threshold | Interpretation |
|--------|-----------|----------------|
| Settling Time | ±10% | Small improvements/degradations acceptable |
| Overshoot | ±15% | Moderate variations acceptable |
| Energy | ±20% | Higher variations acceptable (less critical) |
| Chattering Frequency | ±25% | High variance expected, informational |

### How Regression Detection Works

1. **Load baseline benchmarks** from `benchmarks/baseline_integration.csv`
2. **Run current test** and calculate metrics
3. **Compare metrics** against baseline:
   - Calculate percentage difference: `|current - baseline| / baseline`
   - Check if difference exceeds threshold
4. **Report regressions** as warnings (not failures)

**Example:**
```
[WARNING] Performance regression detected:
  Settling time regressed: 3.52s vs baseline 3.20s (10.0% change)
```

### When to Update Baselines

**Update baselines when:**
- Intentional algorithm improvements made
- Performance validated across multiple runs
- Regressions false positives (temporary variations)

**How to update:**
```bash
# Delete old baseline
rm benchmarks/baseline_integration.csv

# Regenerate baseline
pytest tests/test_integration/test_cross_component.py::test_generate_baseline_benchmarks -v

# Commit new baseline
git add benchmarks/baseline_integration.csv
git commit -m "chore: Update integration test baselines"
```

---

## Baseline Benchmarks

### File Format

**Location:** `benchmarks/baseline_integration.csv`

**Format:**
```csv
controller_type,dynamics_type,pso_config,settling_time,overshoot,energy,chattering_freq
classical_smc,simplified,default,3.2,5.1,120.5,15.3
classical_smc,simplified,aggressive,2.8,6.2,135.2,18.1
...
```

**Columns:**
- `controller_type`: Controller name (e.g., "classical_smc")
- `dynamics_type`: Dynamics model (e.g., "simplified")
- `pso_config`: PSO configuration (e.g., "default")
- `settling_time`: Settling time in seconds
- `overshoot`: Overshoot in percent
- `energy`: Control effort (∫u²dt)
- `chattering_freq`: Chattering frequency in Hz

### Template

A template with typical values is provided:
```
benchmarks/baseline_integration_template.csv
```

Copy this to `baseline_integration.csv` and customize as needed.

---

## Troubleshooting

### Issue: Tests Failing Due to Missing Config

**Symptoms:**
```
pytest.skip: Configuration not available
```

**Solution:**
```bash
# Verify config.yaml exists
ls -l config.yaml

# If missing, copy from template
cp config.yaml.template config.yaml

# Edit parameters as needed
nano config.yaml
```

### Issue: Tests Failing Due to Import Errors

**Symptoms:**
```
ImportError: No module named 'src.controllers.factory'
```

**Solution:**
```bash
# Install project in editable mode
pip install -e .

# Or add src/ to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Windows
set PYTHONPATH=%PYTHONPATH%;%CD%\src
```

### Issue: Tests Taking Too Long

**Symptoms:**
- 42 tests taking >5 minutes

**Solution:**
```bash
# Run subset of tests
pytest tests/test_integration/test_cross_component.py -k "simplified" -v

# Run with parallelization (requires pytest-xdist)
pip install pytest-xdist
pytest tests/test_integration/test_cross_component.py -n auto -v
```

### Issue: Baseline Benchmarks Not Loading

**Symptoms:**
```
[WARNING] Baseline benchmarks not found: benchmarks/baseline_integration.csv
```

**Solution:**
```bash
# Generate baseline benchmarks
pytest tests/test_integration/test_cross_component.py::test_generate_baseline_benchmarks -v

# Or copy template
cp benchmarks/baseline_integration_template.csv benchmarks/baseline_integration.csv
```

### Issue: Regression Warnings

**Symptoms:**
```
[WARNING] Performance regression detected:
  Settling time regressed: 3.52s vs baseline 3.20s (10.0% change)
```

**Solution:**
1. **Verify regression is real:**
   - Run test multiple times (5-10 runs)
   - Check if regression consistent

2. **Investigate cause:**
   - Recent code changes affecting performance
   - Different hardware (CPU speed, memory)
   - PSO randomness (different random seed)

3. **Update baseline if false positive:**
   ```bash
   rm benchmarks/baseline_integration.csv
   pytest tests/test_integration/test_cross_component.py::test_generate_baseline_benchmarks -v
   ```

---

## Continuous Integration

### GitHub Actions Integration

Add to `.github/workflows/tests.yml`:

```yaml
name: Integration Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.9'
      - run: |
          pip install -r requirements.txt
          pytest tests/test_integration/test_cross_component.py -v
```

### Pre-Commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Run integration tests before commit
pytest tests/test_integration/test_cross_component.py -v --tb=short

if [ $? -ne 0 ]; then
  echo "[ERROR] Integration tests failed. Fix issues before committing."
  exit 1
fi

echo "[OK] Integration tests passed"
```

### Weekly Regression Check

Run weekly to catch performance regressions:

```bash
# Weekly cron job (e.g., every Monday at 9am)
0 9 * * 1 cd /path/to/project && pytest tests/test_integration/test_cross_component.py -v | tee integration_tests_$(date +\%Y\%m\%d).log
```

---

## References

### Related Documentation

- **Test Standards:** `.ai/config/testing_standards.md`
- **Controller Documentation:** `docs/api/controllers/`
- **Dynamics Documentation:** `docs/api/dynamics/`
- **PSO Configuration:** `docs/guides/optimization/pso_tuning.md`

### Related Test Suites

- **Unit Tests:** `tests/test_controllers/`, `tests/test_optimization/`
- **End-to-End Tests:** `tests/test_integration/test_end_to_end_validation.py`
- **Regression Tests:** `tests/test_integration/test_integration_regression_detection.py`
- **Thread Safety:** `tests/test_integration/test_thread_safety/`

---

**End of Integration Testing Guide**

**Document Version:** 1.0
**Last Updated:** November 12, 2025
**Status:** OPERATIONAL
**Maintenance:** Update baselines after major algorithm changes
