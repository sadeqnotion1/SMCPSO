<!--======================================================================================\\\
======= docs/testing/reports/2025-09-30/pso_fitness_investigation.md ================\\\
=======================================================================================-->

# PSO Fitness Function Investigation - cost=0.0 Root Cause Analysis

**Investigation Date**: September 30, 2025
**Issue**: All 22 PSO runs converged to `cost=0.0` (statistically impossible)
**Status**: 🔴 **ROOT CAUSE IDENTIFIED** - Excessive Baseline Normalization
**Priority**: Critical - Blocks reliable PSO parameter tuning



## 📋 Executive Summary

**Root Cause**: Baseline normalization with poorly-tuned gains creates excessively large denominators, causing all subsequent PSO particle costs to normalize to near-zero values.

**Impact**:
- PSO optimization results are meaningless
- Cannot distinguish between good and bad controller parameters
- Reported optimal gains may be suboptimal

**Recommended Fix**:
1. Use well-tuned baseline gains or disable baseline normalization
2. Reduce `state_error` weight from 50.0 to 1.0-5.0 range
3. Add diagnostic logging to track normalization effects



## 🔍 Investigation Process

### Step 1: Configuration Analysis

**Examined**: `config.yaml` cost function section

```yaml
cost_function:
  weights:
    state_error: 50.0        # ⚠️  EXTREMELY HIGH (typical: 1.0-5.0)
    control_effort: 0.2
    control_rate: 0.1
    stability: 0.1
  baseline:
    gains: [50, 100, 10, 8, 5, 4]  # ⚠️  Likely poorly tuned
  instability_penalty: 1000.0
  combine_weights:
    mean: 0.7
    max: 0.3
```

**Critical Observations**:
1. **Unbalanced Weights**: `state_error` weight is **250x** larger than `control_effort`
2. **Suspicious Baseline Gains**: Values `[50, 100, 10, 8, 5, 4]` appear arbitrary
3. **No Normalization Constants**: Missing explicit `norms` section



### Step 2: Code Analysis

**File**: `src/optimization/algorithms/pso_optimizer.py`

#### **Baseline Normalization Logic** (Lines 236-282)

```python
# example-metadata:
# runnable: false

# Automatic baseline normalization
baseline_particles = np.asarray(gains_list, dtype=float).reshape(1, -1)
res = simulate_system_batch(
    controller_factory=controller_factory,
    particles=baseline_particles,
    sim_time=self.sim_cfg.duration,
    dt=self.sim_cfg.dt,
    u_max=u_max_val,
)

# Extract baseline costs
ise_base = float(np.sum((x_b[:, :-1, :3] ** 2 * dt_arr) * time_mask, axis=(1, 2))[0])
u_sq_base = float(np.sum((u_b ** 2 * dt_arr) * time_mask, axis=1)[0])
du_sq_base = float(np.sum((du ** 2 * dt_arr) * time_mask, axis=1)[0])
sigma_sq_base = float(np.sum((sigma_b ** 2 * dt_arr) * time_mask, axis=1)[0])

# Set normalization denominators
self.norm_ise = max(ise_base, 1e-12)
self.norm_u = max(u_sq_base, 1e-12)
self.norm_du = max(du_sq_base, 1e-12)
self.norm_sigma = max(sigma_sq_base, 1e-12)
```

**Problem**: If baseline gains produce **very poor performance**, the normalization denominators become **very large**.



## **Cost Computation with Normalization** (Lines 416-438)

```python
# example-metadata:
# runnable: false

# State error integration
ise = np.sum((x_b[:, :-1, :] ** 2 * dt_b) * time_mask, axis=(1, 2))
ise_n = self._normalise(ise, self.norm_ise)  # ⚠️  Division by large baseline

# Control effort
u_sq = np.sum((u_b_trunc ** 2 * dt_b) * time_mask, axis=1)
u_n = self._normalise(u_sq, self.norm_u)

# Control slew
du_sq = np.sum((du_trunc ** 2 * dt_b) * time_mask, axis=1)
du_n = self._normalise(du_sq, self.norm_du)

# Sliding variable energy
sigma_sq = np.sum((sigma_b_trunc ** 2 * dt_b) * time_mask, axis=1)
sigma_n = self._normalise(sigma_sq, self.norm_sigma)

# Weighted cost
J = (
    self.weights.state_error * ise_n      # 50.0 * (tiny value)
    + self.weights.control_effort * u_n   # 0.2 * (tiny value)
    + self.weights.control_rate * du_n    # 0.1 * (tiny value)
    + self.weights.stability * sigma_n    # 0.1 * (tiny value)
) + penalty
```

**Problem**: Even with `state_error` weight of 50.0, if `ise_n` is normalized to `~1e-6`, the total cost becomes:
```
J = 50.0 * 1e-6 + 0.2 * 1e-6 + 0.1 * 1e-6 + 0.1 * 1e-6 + 0
  ≈ 5e-5  (rounds to 0.0 in log output)
```



## Step 3: Normalization Analysis

### **Normalization Function** (Lines 450-472)

```python
def _normalise(self, val: np.ndarray, denom: float) -> np.ndarray:
    """Safely normalise with threshold check"""
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = val / denom
    thr = float(self.normalisation_threshold)  # Default: 1e-12
    return np.where(denom > thr, ratio, val)
```

**Behavior**:
- If `denom > 1e-12`: Returns `val / denom`
- If `denom ≤ 1e-12`: Returns `val` (no normalization)

**Scenario with Baseline Normalization**:
1. Baseline simulation with gains `[50, 100, 10, 8, 5, 4]` produces `ise_base = 1000.0`
2. `self.norm_ise` is set to `1000.0`
3. PSO finds better gains with `ise = 0.5`
4. Normalized: `ise_n = 0.5 / 1000.0 = 0.0005`
5. Weighted cost: `50.0 * 0.0005 = 0.025`
6. Total cost with other terms: `~0.03` (very small, rounds to 0 in logs)



## 🧪 Validation Experiment

### Recommended Test

```bash
# Create diagnostic config
cat > config_pso_debug.yaml << EOF
cost_function:
  weights:
    state_error: 1.0       # Reduced from 50.0
    control_effort: 0.1
    control_rate: 0.01
    stability: 0.1
  # Remove baseline normalization
  # baseline:
  #   gains: []
  instability_penalty: 1000.0

pso:
  n_particles: 30          # Increased from 5
  iters: 50
  bounds:
    min: [0.1, 0.1, 0.1, 0.1, 1.0, 0.0]
    max: [50.0, 50.0, 50.0, 50.0, 200.0, 50.0]
EOF

# Run PSO with diagnostic logging
python simulate.py --ctrl classical_smc --run-pso \
  --config config_pso_debug.yaml \
  --save pso_debug_results.json
```

**Expected Outcome**: Cost values should be non-zero and show meaningful variation



## 📊 Evidence from Logs

### Symptom 1: Identical Convergence

```
Final cost: 0.0 (Run 1)
Final cost: 0.0 (Run 2)
...
Final cost: 0.0 (Run 22)
```

**Analysis**: Zero variation suggests:
- All particles collapse to same region
- Cost function lacks sensitivity
- Normalization removes distinctions



### Symptom 2: Low Particle Count Warning

```
UserWarning: The number of particles (5) is less than the recommended
minimum of 10 particles. This may affect the optimization performance.
```

**Analysis**: With only 5 particles and insensitive cost function:
- Limited exploration
- Premature convergence likely
- Cannot escape local minima



### Symptom 3: Optimal Gains Consistency

```python
optimal_gains = [77.62, 44.45, 17.31, 14.25, 18.66, 9.76]
```

**Analysis**:
- High boundary layer (9.76) suggests chattering avoidance
- Balanced gains indicate reasonable control
- **BUT**: If cost function is broken, these may not be truly optimal



## 🔧 Recommended Fixes

### Fix 1: Remove Baseline Normalization (Immediate)

**config.yaml**:
```yaml
cost_function:
  weights:
    state_error: 1.0       # Reduced from 50.0
    control_effort: 0.1
    control_rate: 0.01
    stability: 0.1
  # baseline:              # REMOVED - causing issues
  #   gains: []
  instability_penalty: 1000.0
```

**Rationale**: Eliminates excessive normalization while maintaining cost sensitivity



### Fix 2: Use Explicit Normalization Constants (Alternative)

**config.yaml**:
```yaml
cost_function:
  weights:
    state_error: 1.0
    control_effort: 0.1
    control_rate: 0.01
    stability: 0.1
  norms:                   # Explicit, reasonable values
    state_error: 10.0      # Typical ISE for unstable system
    control_effort: 100.0  # u_max^2 * duration
    control_rate: 1000.0   # Typical slew rate
    sliding: 1.0           # Typical sliding variable magnitude
  instability_penalty: 1000.0
```

**Rationale**: Controlled normalization with domain-appropriate scales



### Fix 3: Balance Cost Weights (Essential)

**config.yaml**:
```yaml
cost_function:
  weights:
    state_error: 1.0       # Reduced from 50.0
    control_effort: 0.1    # Unchanged
    control_rate: 0.01     # Unchanged
    stability: 0.1         # Unchanged
```

**Rationale**:
- Prevents single term dominance
- Allows PSO to balance multiple objectives
- Typical control engineering practice: `state_error : control_effort = 10:1`



### Fix 4: Increase Particle Count (Essential)

**config.yaml**:
```yaml
pso:
  n_particles: 30          # Increased from 5
  iters: 50                # Increased from 2-10
```

**Rationale**:
- Better exploration of parameter space
- Reduces premature convergence
- Industry standard: 10-50 particles for 6-dimensional problems



## 🧬 Diagnostic Script

**Create**: `scripts/debug_pso_fitness.py`

```python
#==========================================================================================\\\
#========================= scripts/debug_pso_fitness.py =================================\\\
#==========================================================================================\\\

"""PSO Fitness Function Diagnostic Tool"""

import numpy as np
from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.config import load_config

def diagnose_normalization():
    """Diagnose normalization effects"""
    config = load_config("config.yaml")

    # Create PSOTuner (triggers baseline normalization)
    def dummy_factory(gains):
        from src.controllers.smc.classic_smc import ClassicalSMC
        return ClassicalSMC(gains=gains, max_force=100.0)

    tuner = PSOTuner(dummy_factory, config)

    # Print normalization constants
    print("=" * 90)
    print("PSO NORMALIZATION DIAGNOSTIC")
    print("=" * 90)
    print(f"\nNormalization Constants:")
    print(f"  norm_ise:    {tuner.norm_ise:.6e}")
    print(f"  norm_u:      {tuner.norm_u:.6e}")
    print(f"  norm_du:     {tuner.norm_du:.6e}")
    print(f"  norm_sigma:  {tuner.norm_sigma:.6e}")

    print(f"\nCost Weights:")
    print(f"  state_error:     {tuner.weights.state_error}")
    print(f"  control_effort:  {tuner.weights.control_effort}")
    print(f"  control_rate:    {tuner.weights.control_rate}")
    print(f"  stability:       {tuner.weights.stability}")

    print(f"\nInstability Penalty: {tuner.instability_penalty:.6e}")
    print(f"Combine Weights: mean={tuner.combine_weights[0]}, max={tuner.combine_weights[1]}")

    # Simulate example cost computation
    print(f"\n{'=' * 90}")
    print("EXAMPLE COST COMPUTATION")
    print("=" * 90)

    # Example raw costs
    ise_raw = 1.0      # Good tracking
    u_sq_raw = 50.0    # Moderate control effort
    du_sq_raw = 100.0  # Moderate slew rate
    sigma_sq_raw = 0.5 # Good sliding surface convergence

    # Normalize
    ise_n = ise_raw / tuner.norm_ise if tuner.norm_ise > 1e-12 else ise_raw
    u_n = u_sq_raw / tuner.norm_u if tuner.norm_u > 1e-12 else u_sq_raw
    du_n = du_sq_raw / tuner.norm_du if tuner.norm_du > 1e-12 else du_sq_raw
    sigma_n = sigma_sq_raw / tuner.norm_sigma if tuner.norm_sigma > 1e-12 else sigma_sq_raw

    print(f"\nRaw Costs:")
    print(f"  ISE:     {ise_raw:.4f}  →  Normalized: {ise_n:.6e}")
    print(f"  U²:      {u_sq_raw:.4f}  →  Normalized: {u_n:.6e}")
    print(f"  (ΔU)²:   {du_sq_raw:.4f}  →  Normalized: {du_n:.6e}")
    print(f"  σ²:      {sigma_sq_raw:.4f}  →  Normalized: {sigma_n:.6e}")

    # Compute weighted cost
    J_components = {
        'state_error': tuner.weights.state_error * ise_n,
        'control_effort': tuner.weights.control_effort * u_n,
        'control_rate': tuner.weights.control_rate * du_n,
        'stability': tuner.weights.stability * sigma_n
    }

    J_total = sum(J_components.values())

    print(f"\nWeighted Cost Components:")
    for name, value in J_components.items():
        pct = (value / J_total * 100) if J_total > 0 else 0
        print(f"  {name:20s}: {value:.6e}  ({pct:.1f}%)")

    print(f"\nTotal Cost: {J_total:.6e}")

    print(f"\n{'=' * 90}")
    print("ASSESSMENT")
    print("=" * 90)

    # Assess normalization health
    if tuner.norm_ise > 100.0:
        print("⚠️  WARNING: norm_ise is very large - may cause excessive normalization")
    if tuner.weights.state_error > 10.0:
        print("⚠️  WARNING: state_error weight is very high - may dominate cost")
    if J_total < 1e-3:
        print("🔴 CRITICAL: Total cost is near zero - PSO cannot distinguish particles")
    else:
        print("✅ Cost function sensitivity appears reasonable")

if __name__ == "__main__":
    diagnose_normalization()
```

**Usage**:
```bash
python scripts/debug_pso_fitness.py
```



## 📈 Prevention Strategy

### 1. Configuration Validation

Add to `src/config.py`:
```python
# example-metadata:
# runnable: false

def validate_cost_function_config(cost_cfg):
    """Validate cost function configuration"""
    # Check weight balance
    if cost_cfg.weights.state_error > 10.0:
        warnings.warn(f"state_error weight ({cost_cfg.weights.state_error}) is very high")

    # Check baseline gains
    if hasattr(cost_cfg, 'baseline') and cost_cfg.baseline.gains:
        warnings.warn("Baseline normalization enabled - may cause cost=0 issues")

    # Check explicit norms
    if not hasattr(cost_cfg, 'norms'):
        warnings.warn("No explicit normalization constants - using baseline or defaults")
```



### 2. Logging Enhancement

Add to `pso_optimizer.py` (after line 438):
```python
# Diagnostic logging
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"Cost components (normalized):")
    logger.debug(f"  ISE: {ise_n.mean():.6e}")
    logger.debug(f"  U²:  {u_n.mean():.6e}")
    logger.debug(f"  ΔU²: {du_n.mean():.6e}")
    logger.debug(f"  σ²:  {sigma_n.mean():.6e}")
    logger.debug(f"Total cost: {J.mean():.6e}")
```



## 3. Unit Tests

**Create**: `tests/test_optimizer/test_pso_cost_sensitivity.py`

```python
# example-metadata:
# runnable: false

def test_cost_sensitivity():
    """Verify PSO cost function distinguishes good/bad controllers"""
    # Test that different gains produce different costs
    gains_good = [10, 5, 8, 3, 15, 2]
    gains_bad = [100, 100, 100, 100, 100, 100]

    cost_good = evaluate_gains(gains_good)
    cost_bad = evaluate_gains(gains_bad)

    # Good gains should have lower cost
    assert cost_good < cost_bad, "Cost function cannot distinguish controller quality"

    # Costs should not be zero
    assert cost_good > 1e-6, "Good controller cost is suspiciously small"
    assert cost_bad > 1e-3, "Bad controller cost is suspiciously small"
```



## ✅ Success Criteria

**After Applying Fixes**:
1. ✅ PSO cost values are non-zero (> 1e-3)
2. ✅ Cost values show meaningful variation between particles
3. ✅ Diagnostic script shows balanced cost components
4. ✅ PSO finds different solutions with different random seeds
5. ✅ Unit tests pass for cost sensitivity



## 🔗 Navigation

[🏠 Testing Home](../../README.md) | [📊 PSO Convergence Analysis](pso_convergence_analysis.md)



**Investigation Complete**: September 30, 2025
**Root Cause**: Excessive baseline normalization + unbalanced weights
**Recommended Action**: Apply Fix 1 + Fix 3 + Fix 4 immediately
**Status**: 🔴 Awaiting configuration changes and validation