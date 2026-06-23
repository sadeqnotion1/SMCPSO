# Section 6 Enhancement Plan: Experimental Setup and Benchmarking Protocol

**Date:** December 25, 2025
**Status:** PLANNING
**Target Completion:** 1.5 hours (time-constrained, selective enhancements)

---

## Current State Analysis

**Section 6 Structure (493 lines, ~3,500 words):**
- 6.1 Simulation Platform (software/hardware specs, reproducibility measures)
- 6.2 Performance Metrics (12 metrics across 5 categories with mathematical definitions)
- 6.3 Benchmarking Scenarios (4 scenarios, Monte Carlo framework, sample size justification)
- 6.4 Validation Methodology (statistical tests, effect sizes, confidence intervals, data archival)
- 6.5 Disturbance Rejection Protocol (8 disturbance types, robust PSO validation)

**Strengths:**
- ✅ Extremely comprehensive and methodical
- ✅ All metrics mathematically defined with physical interpretation
- ✅ Statistical methodology rigorous (Welch's t-test, Cohen's d, bootstrap CI)
- ✅ Reproducibility measures specified (seeds, version pinning, SHA256 checksums)
- ✅ Practical implementation details (Python code, file paths)
- ✅ Sample size justified via power analysis

**Gaps/Opportunities (minimal, section is strong):**
- ⚠️ No step-by-step reproducibility checklist (readers must synthesize from prose)
- ⚠️ Quick reference table missing (specs scattered across subsections)
- ⚠️ Common experimental pitfalls not discussed (what can go wrong?)
- ⚠️ Pre-flight validation procedure missing (how to verify setup before benchmarking?)

---

## Enhancement Strategy

### Goal
Add **practical reproducibility aids** to complement the existing comprehensive methodology.

### Target Metrics
- **Words:** +400-500 words (~12-14% increase, time-constrained)
- **Lines:** +60-80 lines
- **New subsections:** +1-2
- **Tables:** +1 quick reference card

### Effort Allocation (1.5-hour constraint)
1. **Section 6.6 Reproducibility Checklist (50%):** Step-by-step replication guide
2. **Quick Reference Table (30%):** Condensed setup specs
3. **Common Pitfalls (20%, optional):** Troubleshooting guide if time permits

---

## Proposed Enhancements

### Enhancement 1: Add Section 6.6 "Reproducibility Checklist" (+250 words, +40 lines)
**Location:** After Section 6.5 (before Section 7)

**Content:**
- **Step-by-Step Replication Guide**
  - Environment setup (5 steps: Python 3.9+, pip install -r requirements.txt, verify versions)
  - Configuration validation (3 steps: copy config.yaml, check seed=42, verify paths)
  - Baseline test (2 steps: run single simulation, compare to reference output)
  - Full benchmark execution (3 steps: run QW-2, MT-7, check runtime estimates)
  - Statistical analysis (2 steps: run validation scripts, generate figures)

- **Verification Checkpoints:**
  - Checkpoint 1: Package versions match requirements.txt
  - Checkpoint 2: Single simulation produces expected trajectory (compare to reference CSV)
  - Checkpoint 3: QW-2 benchmark completes in 15-20 minutes (4 controllers × 100 trials × ~2-3s/sim)
  - Checkpoint 4: Statistical outputs match reference (t-test p-values, Cohen's d)

- **Common Setup Issues:**
  - NumPy/SciPy BLAS backend mismatch → install openblas-dev
  - RK45 tolerance too tight → increase rtol to 10^-3
  - Out of memory → reduce batch size or use sequential simulation
  - Random seed not respected → check np.random vs random module usage

**Value:** Enables independent researchers to replicate experiments step-by-step

---

### Enhancement 2: Add "Quick Reference Card" Table (+120 words, +20 lines)
**Location:** After Section 6.6

**Content:**
**Table 6.1: Experimental Setup Quick Reference**

| Category | Specification | Value | Purpose |
|----------|--------------|-------|---------|
| **Software** | Python | 3.9+ | Primary language |
| | NumPy | 1.24+ | Numerical arrays |
| | SciPy | 1.10+ | ODE integration |
| | PySwarms | 1.3+ | PSO optimization |
| **Hardware** | CPU | i7-10700K (8 cores) | Simulation compute |
| | RAM | 16 GB | Batch storage |
| | Storage | NVMe SSD | Fast I/O |
| **Simulation** | Time step | dt = 0.01s | 100 Hz rate |
| | Duration | T = 10s | Full transient |
| | Integration | RK45 (adaptive) | Scipy solve_ivp |
| | Tolerance | abs=10^-6, rel=10^-3 | Accuracy |
| **Benchmarks** | QW-2 trials | 400 (100/controller) | Nominal |
| | MT-7 trials | 500 (50/controller × 10 seeds) | Large perturbation |
| | Random seed | 42 | Reproducibility |
| **Statistics** | Significance | α = 0.05 | 95% confidence |
| | Effect size | Cohen's d | Practical significance |
| | CI method | Bootstrap BCa (B=10,000) | Non-parametric |
| | Correction | Bonferroni (α/6 = 0.0083) | Multiple comparisons |
| **Metrics** | Computational | t_compute, M_peak | Section 7.1 |
| | Transient | t_s, OS, t_r | Section 7.2 |
| | Chattering | CI, f_chatter, E_HF | Section 7.3 |
| | Energy | E_ctrl, P_peak | Section 7.4 |
| | Robustness | Δ_tol, A_dist | Section 8 |

**Value:** One-page reference for quick lookup of all setup parameters

---

### Enhancement 3: Add Section 6.7 "Pre-Flight Validation Protocol" (Optional, +150 words, +25 lines)
**Location:** After Section 6.6

**Content:**
- **Purpose:** Verify experimental setup before running full benchmarks

- **Validation Tests (5-minute runtime):**

1. **Package Version Check:**
   ```bash
   python -c "import numpy; import scipy; import matplotlib; print(f'NumPy: {numpy.__version__}, SciPy: {scipy.__version__}')"
   # Expected: NumPy: 1.24.x, SciPy: 1.10.x
   ```

2. **Single Simulation Sanity Check:**
   ```bash
   python simulate.py --ctrl classical_smc --duration 10 --seed 42 --save test_output.json
   # Verify: Settling time ~2.0-2.5s, overshoot <10%, no crashes
   ```

3. **Numerical Accuracy Validation:**
   - Compare RK45 vs Euler integration (same initial condition)
   - Maximum state difference should be <10^-5
   - Indicates integration tolerance appropriate

4. **Reproducibility Test:**
   - Run same simulation twice with seed=42
   - Outputs must be bitwise identical (diff test_run1.json test_run2.json → no difference)

5. **Computational Performance Baseline:**
   - Measure single simulation time: should be 0.4-0.6s on reference hardware
   - If >1.0s → investigate CPU throttling, BLAS backend

- **Pass Criteria:**
  - All version checks pass ✓
  - Sanity check produces stable trajectory ✓
  - Numerical accuracy <10^-5 ✓
  - Reproducibility exact match ✓
  - Runtime 0.4-0.6s ✓

**Value:** Catches configuration issues before wasting hours on invalid benchmarks

---

## Implementation Plan (1.5-hour time constraint)

### Phase 1: Reproducibility Checklist (40 min)
1. Write Section 6.6 with 5-step replication guide
2. Add 4 verification checkpoints
3. Include common setup issues table

### Phase 2: Quick Reference Table (25 min)
1. Create Table 6.1 with all setup specifications
2. Organize into 6 categories (Software, Hardware, Simulation, Benchmarks, Statistics, Metrics)
3. Add cross-references to relevant sections

### Phase 3: Pre-Flight Validation (25 min, optional)
1. Write Section 6.7 with 5 validation tests
2. Include bash/python code snippets
3. Add pass criteria checklist

**Total Estimated Time:** 1.5 hours

---

## Success Criteria

- ✅ Section 6 word count increases by 400-500 words (12-14%)
- ✅ Reproducibility checklist added (step-by-step guide)
- ✅ Quick reference table added (one-page lookup)
- ✅ Optional: Pre-flight validation protocol if time permits
- ✅ Cross-references to existing subsections maintained
- ✅ Code snippets executable and tested

---

## Risk Mitigation

**Risk 1:** Time overrun (1.5-hour constraint tight)
- **Mitigation:** Focus on Phases 1-2 (highest value), defer Phase 3 if needed

**Risk 2:** Reproducibility checklist too verbose
- **Mitigation:** Keep to 5 main steps with sub-bullets, ~250 words max

**Risk 3:** Quick reference table too large
- **Mitigation:** Limit to 20 rows, most critical specs only

---

## Post-Enhancement Metrics (Estimated)

| Metric | Before | After | Change | Target |
|--------|--------|-------|--------|--------|
| **Section 6 lines** | 493 | ~568 | +75 (+15%) | +60-80 |
| **Section 6 words** | ~3,500 | ~3,950 | +450 (+13%) | +400-500 |
| **Subsections** | 5 | 7 | +2 | +1-2 |
| **Tables** | 1 (inline) | 2 | +1 | +1 |
| **Code snippets** | 2 | 5 | +3 | +2-3 |

**Overall Paper Progress:**
- Total words: 34,800 → ~35,250 (+450, +1.3%)
- Total lines: 4,932 → ~5,007 (+75, +1.5%)
- Sections enhanced: 5/10 → 6/10 (60% complete)

---

## Notes

- Section 6 is already exceptionally strong - enhancements add **practical reproducibility aids**, not fill gaps
- Reproducibility checklist critical for independent replication
- Quick reference table enables fast lookup without re-reading subsections
- Pre-flight validation prevents wasted time on misconfigured setups
- Time constraint (1.5 hours) means focused additions, not exhaustive coverage
- Section 6 likely lowest enhancement potential of all sections (already comprehensive)
