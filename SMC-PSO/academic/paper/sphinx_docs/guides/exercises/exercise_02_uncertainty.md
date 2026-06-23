# Exercise 2: Model Uncertainty Analysis

**Level:** Intermediate (Level 2)
**Estimated Time:** 40 minutes
**Prerequisites:** Tutorial 02, Tutorial 06 (Section 3-4)

---

## Objective

Test **STA SMC** under ±30% cart mass variation using Monte Carlo analysis (N=50 runs). Compute mean performance, standard deviation, and 95% confidence intervals.

---

## Your Task

1. Run 50 Monte Carlo simulations with cart mass sampled from uniform distribution [0.7×nominal, 1.3×nominal]
2. Compute statistics: mean, std, 5th/50th/95th percentiles for settling time
3. Plot histogram and boxplot of settling time distribution
4. Assess: Is performance degradation <15% at 95% CI upper bound?

**Expected Results:**
- Mean settling time: ~3.0s (±0.4s std)
- 95% CI: [2.3s, 3.8s]
- Degradation: ~12% (EXCELLENT)
- Convergence rate: 98-100%

**Success Criteria:**
- [x] 95% CI upper bound < 4.0s
- [x] Convergence rate >95%
- [x] Mean degradation <15%

See [solution](solutions/exercise_02_solution.py).
