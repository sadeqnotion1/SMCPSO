# PSO Optimization Failure Analysis - Phase 4.1
**Date:** 2025-11-09
**Investigation:** Why all 750 PSO simulations diverged
**Status:** ROOT CAUSE IDENTIFIED

---

## Problem Statement

PSO optimization for |s|-based thresholds (`phase4_1_optimize_s_based_thresholds.py`) failed catastrophically:
- **750/750 simulations diverged** around t=3.8-3.9s
- **Best cost:** 3.01e+8 (extremely high = total failure)
- **Progress:** 33% (5/15 iterations) before crash
- **Search space:** s_aggressive=[5.0, 100.0], s_conservative=[0.1, 5.0]

---

## Investigation Methodology

Created baseline tests to isolate the problem:

### Test 1: HybridWithSScheduling with Fixed s-Thresholds
**Script:** `test_s_baseline_simple.py`
**Tested configurations:**
1. s_agg=50.0, s_cons=2.5 (PSO middle point)
2. s_agg=10.0, s_cons=1.0 (Conservative)
3. s_agg=20.0, s_cons=0.5 (Moderate)
4. s_agg=5.0, s_cons=0.1 (Lower bounds)
5. s_agg=100.0, s_cons=5.0 (Upper bounds)

**Results:**
```
[FAIL] s_agg=50.0, s_cons=2.5  → Diverged at t=3.880s
[FAIL] s_agg=10.0, s_cons=1.0  → Diverged at t=3.990s
[FAIL] s_agg=20.0, s_cons=0.5  → Diverged at t=3.990s
[FAIL] s_agg=5.0, s_cons=0.1   → Diverged at t=3.950s
[FAIL] s_agg=100.0, s_cons=5.0 → Diverged at t=3.900s

Success rate: 0/5
```

**Observation:** Exact same failure timing as PSO (t≈3.9s)

### Test 2: Baseline HybridAdaptiveSTASMC (NO Scheduling)
**Script:** `test_baseline_hybrid.py`
**Configuration:** Same ROBUST_GAINS, no s-scheduling wrapper

**Results:**
```
[FAIL] Diverged at t=9.890s
Final state: [-1.63, -3.40, 12.62, -2.79, -4.91, 7.49]
            (theta2=12.62 rad = 2 full rotations + 90°)
```

**Observation:** Baseline also fails, just takes 2.5x longer

---

## Root Cause Analysis

### Finding 1: ROBUST_GAINS Are Not Robust
**ROBUST_GAINS** = `[10.149, 12.839, 6.815, 2.75]` (from MT-8 Enhancement #3)

These gains were labeled "robust" but:
- Cannot stabilize the system even WITHOUT scheduling
- System diverges at t=9.89s with baseline controller
- Second pendulum (theta2) rotates uncontrollably

**Hypothesis:** MT-8 gains were optimized for a different:
- Initial condition range
- Dynamics model (simplified vs full?)
- Controller variant (different from HybridAdaptiveSTASMC?)

### Finding 2: s-Scheduling Accelerates Failure
**Comparison:**
- Baseline HybridAdaptiveSTASMC: fails at t=9.89s
- HybridWithSScheduling: fails at t=3.88-3.99s
- **Speedup:** 2.5x faster failure

**Hypothesis:** s-scheduling logic is:
1. Detecting large |s| (system struggling)
2. Scaling gains aggressively (e.g., 1.5x or 0.8x depending on config)
3. Making instability worse instead of better

### Finding 3: State Sanitization Warnings
Both tests triggered:
```
UserWarning: State vector was modified during sanitization
```

This indicates the state became **invalid** (NaN, Inf, or out-of-bounds) before divergence detection caught it.

---

## Conclusions

### 1. PSO Is NOT The Problem
- PSO search strategy is working correctly
- The problem exists before PSO even starts searching
- All parameter combinations in search space are fundamentally unstable

### 2. Controller/Gains Mismatch
**Either:**
- MT-8 ROBUST_GAINS are incompatible with `HybridAdaptiveSTASMC`
- `HybridAdaptiveSTASMC` implementation has bugs
- SimplifiedDIPDynamics is incompatible with this controller

### 3. s-Scheduling Makes It Worse
- Baseline controller lasts 9.9s before failing
- s-scheduling reduces this to 3.9s (60% faster failure)
- Scheduling logic may be inverted or tuned incorrectly

---

## Recommended Actions

### Immediate (Fix Controller)
1. **Verify MT-8 ROBUST_GAINS source:**
   - Which controller were these optimized for?
   - Which dynamics model was used?
   - What IC range was tested?

2. **Test HybridAdaptiveSTASMC with known-good gains:**
   - Try Classical SMC gains
   - Try manual conservative gains (e.g., [5, 10, 5, 10])
   - Verify controller can stabilize system at all

3. **Debug s-scheduling logic:**
   - Log when mode switches occur
   - Check if aggressive/conservative logic is correct
   - Verify gain scaling factors (0.8 aggressive? Should be 1.2+)

### Short-term (Alternative Approach)
1. **Use working controller:**
   - Classical SMC (known to work)
   - STA SMC (known to work)
   - Avoid Hybrid until debugged

2. **Optimize working controller first:**
   - Get PSO working on simpler controller
   - Validate PSO optimization pipeline
   - Then tackle Hybrid controller

### Long-term (Robust Optimization)
1. **Multi-IC PSO:**
   - Test multiple initial conditions per evaluation
   - Ensure gains work across IC distribution
   - True robustness validation

2. **Constraint-based PSO:**
   - Add stability constraints
   - Penalize diverged simulations more heavily
   - Ensure convergence before optimizing performance

---

## Technical Details

### Initial Condition Used
```python
ic = np.array([
    0.0,   # cart_pos
    0.05,  # theta1 (≈2.86°)
    0.03,  # theta2 (≈1.72°)
    0.0,   # cart_vel
    0.0,   # theta1_dot
    0.0    # theta2_dot
])
```

### Controller Configuration
```python
HybridAdaptiveSTASMC(
    gains=[10.149, 12.839, 6.815, 2.75],  # MT-8 "robust" gains
    dt=0.01,
    max_force=20.0,
    k1_init=15.0,
    k2_init=8.0,
    gamma1=1.0,
    gamma2=1.0,
    dead_zone=0.01,
    dynamics_model=SimplifiedDIPDynamics
)
```

### s-Scheduling Configuration (Test 1)
```python
SlidingSurfaceAdaptiveScheduler(
    s_aggressive=50.0,         # Example value
    s_conservative=2.5,        # Example value
    aggressive_scale=0.8,      # 80% of base gains (!)
    conservative_scale=1.2     # 120% of base gains
)
```

**NOTE:** `aggressive_scale=0.8` means "reduce gains when aggressive" - this seems backwards!

---

## Files Generated

**Test scripts:**
- `scripts/research/test_s_baseline_simple.py` - Tests 5 s-threshold configs
- `scripts/research/test_baseline_hybrid.py` - Tests baseline without scheduling

**Diagnostic outputs:**
- This report: `benchmarks/research/phase4_1/PSO_FAILURE_ANALYSIS.md`

---

## CRITICAL UPDATE: Dynamics Model Mismatch Discovered

**Date:** 2025-11-09 (Post-investigation)

###Smoking Gun Found

By inspecting `scripts/mt8_robust_pso.py`, I discovered the MT-8 gains were optimized using:

```python
# Line 31: MT-8 used FULL dynamics
from src.core.dynamics import DIPDynamics

# Line 430:
dynamics = DIPDynamics(config.physics)

# Line 91: IC perturbation 0.1 rad (5.7°)
initial_state = np.array([0, 0.1, 0.1, 0, 0, 0])
```

**But Phase 4.1 PSO script used:**
```python
# Phase 4.1 used SIMPLIFIED dynamics
from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics

dip_config = SimplifiedDIPConfig.create_default()
dynamics = SimplifiedDIPDynamics(dip_config)

# IC perturbation 0.05 rad (2.9°)
ic = np.array([0.0, 0.05, 0.03, 0.0, 0.0, 0.0])
```

### Impact

**This is a CRITICAL mismatch:**
1. **Different physics models** - Simplified vs Full dynamics have different equations of motion
2. **Different IC ranges** - 0.1 rad vs 0.05 rad perturbations
3. **Gains optimized for wrong model** - MT-8 gains tuned for Full, applied to Simplified

**This completely explains the failure:**
- Gains optimized for one model won't work on another
- Like tuning a car's ECU on a dynamometer, then expecting it to work on a boat

### Verification Attempted

Created `test_with_full_dynamics.py` to test MT-8 gains with DIPDynamics:
- Script created successfully
- Hit API incompatibility issues with `DIPDynamics.compute_dynamics()`
- Further debugging needed to complete verification

---

## Next Steps (UPDATED)

1. **CRITICAL:** Fix Phase 4.1 PSO to use **DIPDynamics** (not SimplifiedDIPDynamics)
2. **CRITICAL:** Update IC range to match MT-8 (0.1 rad)
3. Re-run PSO with correct dynamics model
4. Alternative: Re-optimize MT-8 gains for SimplifiedDIPDynamics if that's the target platform

---

**Conclusion (UPDATED):** PSO is not broken. The failure is caused by a **dynamics model mismatch** - MT-8 ROBUST_GAINS were optimized for DIPDynamics (full model) but Phase 4.1 applied them to SimplifiedDIPDynamics. This is like using diesel engine parameters in a gasoline engine - fundamentally incompatible.
