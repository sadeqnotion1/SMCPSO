# [DEPRECATED - METRIC BIAS] MT-6: Corrected Boundary Layer Optimization Analysis

**[WARNING] This report contains INCORRECT results due to biased chattering metric**

**See:** `benchmarks/MT6_DEEP_DIVE_FINAL_ANALYSIS.md` for corrected analysis (November 7, 2025)

**Reality:** Adaptive boundary layer is only **1.3% worse** than fixed baseline (not 352.5% worse)

**Root Cause:** "combined_legacy" chattering metric penalizes dε/dt, artificially inflating the perceived degradation of adaptive boundary layers. Unbiased frequency-domain validation (300 Monte Carlo simulations) revealed minimal difference.

**Conclusion:** Both fixed and adaptive boundary layers perform similarly (~±4%). Fixed boundary layer (ε=0.02) is recommended due to simplicity.

---

## [ORIGINAL REPORT FOLLOWS - RESULTS INCORRECT]

---

**Date:** October 18, 2025
**Task:** MT-6 - Boundary Layer Optimization (Classical/STA SMC)
**Status:** Completed with unexpected results

---

## Executive Summary

**CRITICAL FINDING (INCORRECT - BIASED METRIC):** Adaptive boundary layer optimization INCREASED chattering by 352.5% compared to fixed baseline (28.83 vs 6.37), opposite of hypothesis. [INCORRECT - METRIC BIAS]

**Root Cause of Previous Discrepancy:** Agent A and Agent B used different controller gains, making comparison invalid. This was corrected by using identical default gains `[5.0, 5.0, 5.0, 0.5, 0.5, 0.5]` for both approaches.

**Current Status:** Fair comparison achieved, but adaptive approach underperformed fixed baseline. Requires investigation into PSO objective function, parameter bounds, and chattering metric calculation.

---

## Corrected Methodology (October 18)

### Issue Fixed
**Problem:** Agent A used config.yaml defaults `[5.0, 5.0, 5.0, 0.5, 0.5, 0.5]`, while Agent B used phase53 optimized gains `[23.67, 14.29, 8.87, 3.55, 6.52, 2.93]`, causing 23x chattering difference due to gain mismatch, not boundary layer strategy.

**Solution:** Updated `scripts/mt6_adaptive_boundary_layer_pso.py` line 537 to use default gains for fair comparison:
```python
# CRITICAL FIX: Previously used phase53 gains [23.67, 14.29, ...]
# which caused 23x higher chattering. Now using same defaults as Agent A.
optimized_gains = [5.0, 5.0, 5.0, 0.5, 0.5, 0.5]  # [k1, k2, lam1, lam2, K, kd]
```

---

## Results Comparison

### Agent A: Fixed Boundary Layer (Baseline)

| Metric | Mean | Std Dev | 95% CI | Notes |
|--------|------|---------|--------|-------|
| **Chattering Index** | **6.37** | 1.20 | [6.13, 6.61] | **Baseline** |
| Settling Time | 10.0s | 0.0s | N/A | None converged |
| Overshoot θ1 | 5.36 rad | 0.32 rad | [5.30, 5.42] | 307° |
| Overshoot θ2 | 9.87 rad | 3.05 rad | [9.27, 10.48] | 565° |
| Control Energy | 5,232 N²·s | 2,888 N²·s | [4,659, 5,805] | Moderate |
| RMS Control | 21.5 N | 7.85 N | [19.9, 23.1] | 14% of max |

**Configuration:**
- Boundary layer: ε = 0.02 (fixed)
- Adaptive slope: α = 0.0 (no adaptation)
- Gains: [5.0, 5.0, 5.0, 0.5, 0.5, 0.5]
- Sample size: N = 100, seed = 42

### Agent B: Adaptive Boundary Layer (PSO Optimized)

| Metric | Mean | Std Dev | 95% CI | Notes |
|--------|------|---------|--------|-------|
| **Chattering Index** | **28.83** | 7.17 | [27.42, 30.23] | **352% WORSE** |
| Settling Time | 10.0s | 0.0s | N/A | None converged |
| Overshoot | 6.94 rad | 1.47 rad | [6.65, 7.23] | Combined θ1+θ2 |
| Control Energy | 7,090 N²·s | 6,631 N²·s | N/A | 35% higher |

**Optimized Parameters (PSO Result):**
- Base boundary layer: ε_min = 0.0135
- Adaptive slope: α = 0.171
- Effective boundary layer: ε_eff = ε_min + α|ṡ|
- Gains: [5.0, 5.0, 5.0, 0.5, 0.5, 0.5] (same as Agent A)

**PSO Configuration:**
- Swarm: 15 particles, 20 iterations
- Parameter bounds: ε_min ∈ [0.005, 0.03], α ∈ [0.0, 1.0]
- Fitness function: 70% chattering + 15% settling penalty + 15% overshoot penalty
- Monte Carlo samples per particle: 5
- Validation: 100 runs

**Comparison with Baseline:**
- Chattering reduction: **-352.5%** (increase, not reduction!)
- Target (≥30% reduction): **NOT ACHIEVED**
- Statistical significance (Welch's t-test): p = 1.000 (adaptive significantly WORSE)

---

## Analysis: Why Did Adaptive Perform Worse?

### Hypothesis 1: Smaller Base Boundary Layer
**Observation:** ε_min (0.0135) < ε_fixed (0.02) → 32.5% smaller
**Effect:** Less smoothing of switching function → higher chattering
**Evidence:** Chattering index increased by 4.5x

### Hypothesis 2: Minimal Adaptation
**Observation:** α = 0.171 is very small (near zero)
**Interpretation:** Adaptive component barely active:
- For typical sliding surface velocity |ṡ| ≈ 0.1: ε_eff = 0.0135 + 0.171×0.1 = 0.0152
- Still smaller than fixed ε = 0.02

**Conclusion:** PSO found "pseudo-fixed" boundary layer with smaller thickness

### Hypothesis 3: PSO Got Stuck in Local Minimum
**Observation:** Best fitness = 25.12 (chattering ~22-23), but validation = 28.83
**Interpretation:**
- PSO found particle with lower chattering during optimization
- Validation with 100 runs showed higher average (stochastic variation)
- May have converged to local minimum, not global optimum

### Hypothesis 4: Wrong Parameter Bounds
**Current bounds:** ε_min ∈ [0.005, 0.03], α ∈ [0.0, 1.0]
**Issue:** Optimal ε_min might be LARGER than 0.03 (closer to fixed baseline 0.02)
**Evidence:** Best ε_min = 0.0135 is at lower end of range, suggesting search went wrong direction

### Hypothesis 5: Chattering Metric Favors Fixed Boundary Layer
**Chattering calculation:** `BoundaryLayer.get_chattering_index()`
**Formula:** 70% RMS of control derivative + 30% HF power ratio
**Potential issue:** Adaptive boundary layer changes over time → higher derivative → inflated chattering metric

---

## Recommendations

### Option 1: Re-Optimize with Adjusted Bounds (Recommended)
**Rationale:** Current bounds may be too restrictive

**New bounds:**
- ε_min ∈ [0.015, 0.05] (shift upward, include fixed baseline 0.02)
- α ∈ [0.0, 2.0] (allow stronger adaptation)

**Expected:** May find ε_min ≈ 0.02 with α > 0.5 for true adaptive benefit

### Option 2: Investigate Chattering Metric
**Rationale:** Metric may not fairly compare fixed vs adaptive

**Action:**
1. Plot control signal u(t) for fixed vs adaptive
2. Manually inspect high-frequency oscillations
3. Compute alternative metrics (zero-crossing rate, FFT peak frequency)
4. Verify metric doesn't penalize adaptive variation

### Option 3: Try Different Fitness Function
**Current:** 70% chattering + 15% settling + 15% overshoot
**Issue:** Settling never achieved (all 10.0s) → penalty doesn't differentiate

**Alternative fitness:**
```python
fitness = 0.50 * chattering_index \
        + 0.30 * rms_control \
        + 0.20 * max(0, overshoot - threshold)
```
- De-emphasize chattering (50% vs 70%)
- Add RMS control term (smoother control preferred)
- Reduce overshoot weight

### Option 4: Use Phase53 Gains (If Optimized for Chattering)
**Rationale:** If phase53 gains were optimized for settling/overshoot, not chattering

**Action:**
1. Check phase53 optimization objective
2. If it minimized chattering, use those gains as baseline
3. Re-run Agent A with phase53 gains
4. Compare adaptive vs fixed with optimized gains

---

## Deliverables

**Generated Files:**
1. `benchmarks/MT6_adaptive_optimization.csv` - PSO iteration history (20 iterations)
2. `benchmarks/MT6_adaptive_validation.csv` - Validation results (100 runs)
3. `benchmarks/MT6_adaptive_summary.json` - Summary statistics
4. `benchmarks/MT6_fixed_baseline.csv` - Agent A baseline (100 runs)
5. `benchmarks/MT6_fixed_baseline_summary.json` - Agent A summary
6. `benchmarks/MT6_FIXED_BASELINE_REPORT.md` - Agent A detailed report
7. `benchmarks/MT6_AGENT_B_STATUS.md` - Agent B progress (pre-correction)
8. `benchmarks/MT6_CORRECTED_ANALYSIS.md` - This document

---

## Conclusion

**Key Findings:**
1. ✅ **Corrected methodology:** Fair comparison achieved (identical gains)
2. ❌ **Unexpected result:** Adaptive boundary layer INCREASED chattering by 352%
3. ✅ **Data quality:** 100% success rate, reproducible (seed=42), 95% CI computed
4. ⚠️ **Root cause unclear:** Requires further investigation (see recommendations)

**Next Steps:**
1. Re-optimize with adjusted bounds (Option 1)
2. Validate chattering metric (Option 2)
3. If still fails, try alternative fitness function (Option 3)
4. Document final MT-6 results after investigation

**Time Invested:**
- Agent A (fixed baseline): ~30 min
- Agent B (initial attempt): ~30 min
- Gain correction + re-run: ~5 min (optimization) + ~2 min (validation)
- Analysis + documentation: ~15 min
- **Total:** ~1.5 hours

**Status:** MT-6 incomplete - requires follow-up optimization with corrected approach

---

**Generated by:** Claude Code
**Script (Agent A):** `scripts/mt6_fixed_baseline.py`
**Script (Agent B):** `scripts/mt6_adaptive_boundary_layer_pso.py`
**Data Files:** `benchmarks/MT6_*.csv`, `benchmarks/MT6_*.json`
