# PSO Optimization Scripts - Issue #12

Comprehensive automation toolkit for PSO-based controller optimization and validation.

---

## Quick Start

### Monitor PSO and Auto-Validate
```bash
# Check every 60 seconds, auto-validate when done
python scripts/optimization/monitor_and_validate.py

# With auto-config-update
python scripts/optimization/monitor_and_validate.py --auto-update-config

# Check every 2 minutes, max wait 3 hours
python scripts/optimization/monitor_and_validate.py --interval 120 --max-wait 180
```

### Manual Workflow
```bash
# 1. Check PSO status
python scripts/optimization/check_pso_completion.py

# 2. When complete, validate
python scripts/optimization/validate_and_summarize.py

# 3. If validation passes, update config
python scripts/optimization/update_config_with_gains.py --dry-run  # preview
python scripts/optimization/update_config_with_gains.py            # actually update
```

---

## Scripts Overview

### 1. PSO Optimization Scripts

#### `optimize_chattering_direct.py`
**Original PSO optimizer** (tracking-focused fitness)

```bash
python scripts/optimization/optimize_chattering_direct.py --controller classical_smc --iters 150
```

**Fitness Function:**
```python
fitness = tracking_error_rms + chattering_penalty + tracking_penalty + effort_penalty
# Where: chattering_penalty = max(0, chattering - 2.0) * 10.0
# Issue: Penalty is ZERO when chattering < 2.0, so fitness dominated by tracking!
```

**Usage:** ~~Not recommended for chattering reduction~~ Use `optimize_chattering_focused.py` instead

#### `optimize_chattering_focused.py` ✨
**Corrected PSO optimizer** (direct chattering minimization)

```bash
python scripts/optimization/optimize_chattering_focused.py --controller classical_smc --iters 150
python scripts/optimization/optimize_chattering_focused.py --controller adaptive_smc --iters 150
python scripts/optimization/optimize_chattering_focused.py --controller sta_smc --iters 150
```

**Fitness Function:**
```python
fitness = chattering_index  # Direct minimization!
# + tracking_constraint_penalty if tracking > 0.1 rad
```

**Recommended:** Use this for true chattering reduction

---

### 2. Monitoring and Validation

#### `check_pso_completion.py`
Check PSO completion status

```bash
python scripts/optimization/check_pso_completion.py

# Auto-validate when complete
python scripts/optimization/check_pso_completion.py --auto-validate
```

**Output:**
```
================================================================================
PSO COMPLETION CHECKER - Issue #12
================================================================================
Time: 2025-09-30 18:34:00

classical_smc       : [DONE] 150/150, cost=5.33e+02
adaptive_smc        : [DONE] 150/150, cost=1.61e+03
sta_smc             : [RUNNING] 142/150 (94.7%)

Overall: 2/3 controllers complete

Estimated Progress:
  sta_smc             : 8 iterations remaining
```

#### `validate_and_summarize.py` ✨
**Comprehensive validation** by re-simulation with exact PSO metrics

```bash
python scripts/optimization/validate_and_summarize.py
```

**What it does:**
1. Loads optimized gains from `gains_*_chattering.json`
2. Re-simulates each controller
3. Computes exact same metrics as PSO:
   - Chattering index (time + freq domain)
   - Tracking error RMS
   - Control effort RMS
4. Checks acceptance criteria (chattering < 2.0, tracking < 0.1 rad)
5. Generates JSON summary: `docs/issue_12_validation_summary_YYYYMMDD_HHMMSS.json`

**Output:**
```
================================================================================
SUMMARY
================================================================================

Controllers optimized: 3/4
Chattering target met: 2/3

Individual Results:
  classical_smc               : chattering= 533.000 [FAIL]
  adaptive_smc                : chattering=   1.523 [PASS]
  sta_smc                     : chattering=   1.874 [PASS]
```

#### `monitor_and_validate.py` ✨
**Automated end-to-end workflow** - monitor PSO and auto-validate

```bash
# Basic monitoring (check every 60 seconds)
python scripts/optimization/monitor_and_validate.py

# With auto-config-update
python scripts/optimization/monitor_and_validate.py --auto-update-config

# Custom settings
python scripts/optimization/monitor_and_validate.py --interval 120 --max-wait 180
```

**Features:**
- Polls PSO logs at specified interval
- Auto-triggers validation when all complete
- Optionally updates config.yaml if validation passes
- Timeout protection (default: 4 hours)
- Keyboard interrupt handling

---

### 3. Configuration Management

#### `update_config_with_gains.py`
Update `config.yaml` with optimized gains

```bash
# Dry run (preview changes)
python scripts/optimization/update_config_with_gains.py --dry-run

# Actually update
python scripts/optimization/update_config_with_gains.py
```

**What it does:**
1. Loads gains from `gains_*_chattering.json`
2. Creates backup: `.archive/config_backup_YYYYMMDD_HHMMSS.yaml`
3. Updates both `controllers` and `controller_defaults` sections
4. Prints old vs new gains comparison

**Safety:** Always creates backup before modifying config.yaml

---

### 4. Analysis and Diagnostics

#### `analyze_pso_convergence.py`
Generate convergence curves and analysis

```bash
python scripts/optimization/analyze_pso_convergence.py --controller classical_smc
```

**Output:**
- Convergence curve plot
- Best cost history
- Convergence statistics

#### `diagnose_classical_chattering.py`
Diagnostic tool to compare fitness vs actual chattering

```bash
python scripts/optimization/diagnose_classical_chattering.py
```

**Purpose:** Discovered the fitness function confusion bug

#### `visualize_optimization_results.py`
Visualize PSO results across all controllers

```bash
python scripts/optimization/visualize_optimization_results.py
```

---

## Workflows

### Workflow 1: Initial PSO Optimization
```bash
# Run PSO for all 3 controllers
python scripts/optimization/optimize_chattering_direct.py --controller classical_smc --iters 150 &
python scripts/optimization/optimize_chattering_direct.py --controller adaptive_smc --iters 150 &
python scripts/optimization/optimize_chattering_direct.py --controller sta_smc --iters 150 &

# Wait for completion (or use monitor)
python scripts/optimization/monitor_and_validate.py --auto-update-config
```

### Workflow 2: Validation and Config Update
```bash
# 1. Check status
python scripts/optimization/check_pso_completion.py

# 2. Validate results
python scripts/optimization/validate_and_summarize.py

# 3. If PASS: update config
python scripts/optimization/update_config_with_gains.py

# 4. Test updated config
python simulate.py --ctrl classical_smc --plot

# 5. Commit changes
git add config.yaml docs/issue_12_validation_summary_*.json
git commit -m "RESOLVED: Issue #12 - Chattering reduction complete"
```

### Workflow 3: Re-optimization (if validation fails)
```bash
# Re-run with corrected fitness function
python scripts/optimization/optimize_chattering_focused.py --controller classical_smc --iters 150
python scripts/optimization/optimize_chattering_focused.py --controller adaptive_smc --iters 150
python scripts/optimization/optimize_chattering_focused.py --controller sta_smc --iters 150

# Validate again
python scripts/optimization/validate_and_summarize.py
```

---

## Expected Results

### Baseline (Before Optimization)
- Chattering Index: ~69
- Tracking Error: ~0.02 rad
- Control Effort: ~50 N

### Target (After Optimization)
- Chattering Index: **< 2.0** ✅
- Tracking Error: < 0.1 rad ✅
- Control Effort: < 100 N RMS ✅

### Likely Outcome (Current PSO Runs)
Based on fitness function analysis:
- **classical_smc:** FAIL (fitness=533, not optimized for chattering)
- **adaptive_smc:** UNKNOWN (fitness=1610, need validation)
- **sta_smc:** UNKNOWN (fitness=1970, need validation)

**Recommendation:** Be prepared to re-run with `optimize_chattering_focused.py`

---

## File Naming Convention

### Input Files
- `config.yaml` - Main configuration
- `logs/pso_*_smc.log` - PSO optimization logs

### Output Files
- `gains_*_chattering.json` - Optimized gains with metrics
- `docs/issue_12_validation_summary_*.json` - Validation results
- `.archive/config_backup_*.yaml` - Config backups

### Output Format (gains_*_chattering.json)
```json
{
  "controller": "classical_smc",
  "gains": [16.11, 2.79, 2.72, 4.52, 16.94, 2.96],
  "metrics": {
    "chattering_index": 1.523,
    "tracking_error_rms": 0.0234,
    "control_effort_rms": 45.67
  },
  "pso_config": {
    "n_particles": 30,
    "iters": 150,
    "seed": 42
  }
}
```

---

## Troubleshooting

### PSO not converging
**Problem:** Best cost not improving
**Solutions:**
- Increase `--iters` (e.g., 200 or 300)
- Increase `--n-particles` (e.g., 50)
- Adjust PSO parameters in config.yaml
- Check if fitness function is appropriate

### Validation failing
**Problem:** Chattering still > 2.0 after optimization
**Root Cause:** Fitness function prioritizes tracking, not chattering
**Solution:** Re-run with `optimize_chattering_focused.py`

### Config update failing
**Problem:** JSON files not found
**Check:**
```bash
ls -la gains_*_chattering.json
```
Ensure PSO generated output files

### Simulation diverging
**Problem:** Controller unstable with optimized gains
**Possible Causes:**
- Gains outside safe bounds
- Numerical instability
- Control saturation too aggressive
**Solution:** Review gain bounds in config.yaml PSO section

---

## Architecture

### Fitness Functions Comparison

| Aspect | `optimize_chattering_direct.py` | `optimize_chattering_focused.py` |
|--------|----------------------------------|-----------------------------------|
| Primary Objective | Tracking performance | Chattering reduction |
| Fitness Formula | `tracking + penalties` | `chattering + constraint` |
| Chattering Weight | Low (only penalized if >2.0) | High (direct minimization) |
| Recommended Use | Balanced performance | True chattering reduction |

### Validation Metrics

**Exact same metrics as PSO:**
1. **Chattering Index:**
   ```python
   time_domain = sqrt(mean(gradient(control, dt)^2))
   freq_domain = sum(spectrum[f>10Hz]) / sum(spectrum)
   chattering_index = 0.7 * time_domain + 0.3 * freq_domain
   ```

2. **Tracking Error RMS:**
   ```python
   tracking_rms = sqrt(mean(state[:, 1:3]^2))  # pendulum angles only
   ```

3. **Control Effort RMS:**
   ```python
   effort_rms = sqrt(mean(control^2))
   ```

---

## Contributing

When adding new optimization scripts:
1. Follow naming convention: `optimize_<objective>_<method>.py`
2. Include ASCII header (90 chars wide)
3. Add comprehensive docstring
4. Support `--controller`, `--iters`, `--n-particles`, `--seed` args
5. Generate JSON output: `gains_<controller>_<objective>.json`
6. Update this README

---

**Repository:** https://github.com/theSadeQ/dip-smc-pso.git
**Issue:** #12 - Chattering Reduction
**Created:** 2025-09-30
**Status:** PSO running, automation ready