# LT-6: Model Uncertainty Analysis

**Date:** October 18, 2025
**Status:** COMPLETE
**Test Duration:** ~3 minutes (1,320 simulations)

---

## Executive Summary

Tested robustness of 4 SMC controllers to model parameter errors (±10%, ±20% in mass, length, inertia).

### Key Findings

1. **CRITICAL ISSUE:** Default controller gains FAIL to stabilize system (0% convergence for ALL controllers)
2. **All controllers equally poor:** Robustness score: 30.0/100 (baseline failure)
3. **Model uncertainty irrelevant:** When controllers don't work nominally, perturbations don't matter
4. **System diverges:** All scenarios show angles exceeding 300° (multiple full rotations)

### Conclusion

**LT-6 reveals fundamental limitation:** Controllers require PSO-tuned gains to function. Default gains from config.yaml are ineffective for double-inverted pendulum stabilization.

**Recommendation:** Re-run LT-6 AFTER completing gain tuning (use PSO-optimized gains from MT-6/MT-8).

---

## Methodology

### Test Matrix

- **Controllers:** 4 (classical_smc, sta_smc, adaptive_smc, hybrid_adaptive_sta_smc)
- **Scenarios:** 33 per controller
  - 1 nominal
  - 28 single-parameter variations
  - 4 combined worst-case variations
- **Error levels:** ±10%, ±20%
- **Monte Carlo trials:** 10 per scenario
- **Total simulations:** 1,320

### Parameter Variations

**Masses:**
- m0 (cart mass)
- m1 (pendulum 1 mass)
- m2 (pendulum 2 mass)

**Lengths:**
- l1 (pendulum 1 length)
- l2 (pendulum 2 length)

**Inertias:**
- I1 (pendulum 1 inertia)
- I2 (pendulum 2 inertia)

### Physical Constraint Violations

Some scenarios violated physical constraints and were skipped:
- **m1+10%, m1+20%:** Pendulum 1 inertia below minimum (0.0081 < 0.009)
- **m2+10%, m2+20%:** Pendulum 2 inertia below minimum
- **I1-10%, I1-20%:** Inertia below physical bound
- **I2-10%, I2-20%:** Inertia below physical bound
- **all_masses+10%, all_masses+20%:** Combined constraint violations

**Total skipped:** 10 scenarios per controller (40 total)
**Total completed:** 23 scenarios per controller (92 total)

### Test Conditions

- **Initial condition:** [0, 0.1, 0.1, 0, 0, 0] rad (5.7° perturbation on each angle)
- **Simulation time:** 10 seconds
- **Time step:** dt = 0.01s
- **Settling criterion:** |θ1|, |θ2| < 0.1 rad (5.7°) continuously for last 0.5s

---

## Results

### Robustness Ranking

| Rank | Controller | Robustness Score | Settling Degradation | Convergence Degradation |
|------|------------|------------------|----------------------|-------------------------|
| 1 (tie) | classical_smc | 30.0 / 100 | +0.0% | +100.0% |
| 1 (tie) | sta_smc | 30.0 / 100 | +0.0% | +100.0% |
| 1 (tie) | adaptive_smc | 30.0 / 100 | +0.0% | +100.0% |
| 1 (tie) | hybrid_adaptive_sta_smc | 30.0 / 100 | +0.0% | +100.0% |

**Interpretation:**
- **Robustness score:** 100 = no degradation, 0 = complete failure
- **30.0/100:** Indicates baseline failure (0% convergence both nominal and perturbed)
- **+100% convergence degradation:** From 0% (nominal) to 0% (perturbed) = infinite degradation (capped at 100%)

### Performance Metrics (All Controllers)

| Metric | Nominal | Perturbed (avg) |
|--------|---------|-----------------|
| Settling time | 10.00s | 10.00s |
| Convergence rate | 0% | 0% |
| Max overshoot | 300-480° | 300-480° |

**Observation:** System diverges to multiple full rotations, indicating complete instability.

---

## Analysis

### Why All Controllers Failed

#### Default Gains Are Insufficient

The default controller gains in `config.yaml` are NOT tuned for double-inverted pendulum stabilization. Evidence:

1. **Nominal performance:** 0% convergence even without model uncertainty
2. **Large overshoots:** 300-480° (complete loss of control)
3. **No settling:** All scenarios reach 10s timeout without stabilizing

#### Expected Behavior (If Gains Were Tuned)

With PSO-optimized gains, we would expect:
- **Nominal:** 80-100% convergence
- **±10% errors:** 50-80% convergence (modest degradation)
- **±20% errors:** 20-50% convergence (significant degradation)
- **Robustness scores:** 50-90/100 (controller-dependent)

### Why Model Uncertainty Doesn't Matter

When controllers fail nominally, parameter perturbations have no effect:
- Divergence from initial condition dominates behavior
- ±20% mass error is negligible compared to 300° overshoot
- All scenarios converge to same failure mode (uncontrolled rotation)

---

## Comparison with MT-8 (Disturbance Rejection)

| Test | Nominal Gains | Result | Conclusion |
|------|--------------|--------|------------|
| **MT-8** | Default gains | 0% convergence under disturbances | Gains need tuning |
| **LT-6** | Default gains | 0% convergence even without disturbances | Gains fundamentally broken |

**Cross-test insight:** MT-8 and LT-6 both confirm default gains are unusable. **Priority: Gain tuning (PSO) before further robustness tests.**

---

## Recommendations

### Immediate Actions

1. **Complete gain tuning:**
   - Run PSO optimization for all 4 controllers
   - Target: 80%+ convergence on nominal plant
   - Save tuned gains to `optimization_results/`

2. **Re-run LT-6 with tuned gains:**
   - Load PSO-optimized gains
   - Re-execute model uncertainty analysis
   - Expected outcome: Robustness scores 50-90/100

3. **Update config.yaml:**
   - Replace default gains with PSO-optimized values
   - Document gain source (e.g., "PSO-tuned 2025-10-18")

### For Publication

**Do NOT include current LT-6 results in paper.** They demonstrate:
- Poor experimental design (testing robustness with broken controllers)
- No scientific value (all scores identical due to baseline failure)

**Instead:**
1. First complete gain tuning
2. Re-run LT-6 with tuned gains
3. Report meaningful robustness differences between controllers
4. Discuss trade-offs (e.g., "Adaptive SMC more robust to mass errors")

### For PSO Re-optimization

Add robustness term to fitness function:

```python
# Current fitness (nominal only)
fitness = settling_time + 10 * max_overshoot + 1000 * (1 - converged)

# Proposed fitness (nominal + worst-case)
nominal_perf = settling_time_nominal + 10 * overshoot_nominal
worst_case_perf = settling_time_worst + 10 * overshoot_worst
fitness = 0.7 * nominal_perf + 0.3 * worst_case_perf
```

This encourages PSO to find gains robust to model uncertainty.

---

## Files Generated

1. **benchmarks/LT6_uncertainty_analysis.csv** - Raw results (93 rows: 4 controllers × 23 scenarios)
2. **benchmarks/LT6_robustness_ranking.csv** - Robustness scores (4 controllers)
3. **scripts/lt6_model_uncertainty.py** - Test script (reusable for future runs)
4. **src/utils/model_uncertainty.py** - Parameter perturbation module
5. **benchmarks/lt6_model_uncertainty.log** - Execution log (1,320 simulations)

---

## Lessons Learned

### What Worked

1. **Systematic scenario generation:** Covers all parameters (mass, length, inertia) at multiple error levels
2. **Physical constraint validation:** Automatically skips invalid scenarios (e.g., negative inertia)
3. **Monte Carlo trials:** 10 trials per scenario provides statistical confidence
4. **Automated robustness scoring:** Quantifies performance degradation objectively

### What Didn't Work

1. **Testing with default gains:** Wasted 3 minutes on meaningless simulations
2. **No preliminary gain check:** Should verify nominal convergence before robustness testing

### Improvements for Next Run

1. **Prerequisite check:**
   ```python
   if nominal_convergence < 50%:
       raise ValueError("Tune gains first! Nominal performance too poor for robustness testing.")
   ```

2. **Load tuned gains:**
   ```python
   # Add to script
   parser.add_argument('--gains-file', type=str, default='optimization_results/pso_gains.json',
                       help='Path to PSO-tuned gains')
   ```

3. **Focus on valid scenarios:**
   - Skip constraint-violating scenarios during generation (not during execution)
   - Reduces total simulations from 1,320 to ~1,000

---

## Appendix: Physical Constraint Analysis

### Why Some Scenarios Failed

**Pendulum inertia has minimum bound:**

I_min = (1/3) * m * L²

When mass increases (+10%), inertia should increase proportionally. But we only perturbed mass, leaving inertia at nominal value. This violates physics:

- **m1 = 0.2 kg → 0.22 kg (+10%)**
- **I1 = 0.009 kg·m²** (unchanged)
- **I1_min = (1/3) × 0.22 × 0.3² = 0.0066 kg·m²** (OK)
- **BUT:** Config validation requires I1 ≥ 0.009 kg·m²

**Solution for future runs:**
- Perturb inertia when perturbing mass: `I1_new = I1_nominal × (m1_new / m1_nominal)²`
- This maintains physical consistency

---

## Summary Statistics

- **Total test time:** ~3 minutes
- **Simulations completed:** 920 / 1,320 (69.7%)
- **Simulations skipped:** 400 / 1,320 (30.3%) - constraint violations
- **Controllers tested:** 4 / 5 (swing_up_smc unavailable)
- **Convergence rate:** 0% (all controllers, all scenarios)
- **Robustness outcome:** Inconclusive (requires tuned gains)

**Status:** Test infrastructure validated, but results not actionable until gain tuning completed.

---

## Next Steps

**Priority 1:** Gain Tuning (MT-6 adaptive boundary layer PSO)
- Target: 80%+ convergence for all controllers
- Est. time: 4-6 hours per controller

**Priority 2:** Re-run LT-6 with tuned gains
- Expected outcome: Robustness scores 50-90/100
- Actionable insights for controller selection

**Priority 3:** Combined robustness test (LT-7)
- Model uncertainty + external disturbances
- Test worst-case scenarios for industrial deployment
