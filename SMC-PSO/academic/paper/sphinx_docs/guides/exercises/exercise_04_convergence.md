# Exercise 4: PSO Convergence Diagnostics

**Level:** Advanced (Level 3)
**Estimated Time:** 45 minutes
**Prerequisites:** Tutorial 03, Tutorial 07 (Section 4)

## Objective
Diagnose and fix premature convergence in PSO optimization. Identify issues from convergence plots (diversity, improvement rate) and recommend fixes.

## Your Task
1. Run PSO with poor parameters: N=10, iters=30, w=0.3 (fixed)
2. Track metrics: gbest cost, diversity, improvement rate
3. Diagnose: Premature convergence? Stagnation?
4. Fix: Increase N to 30, iters to 60, use adaptive w (0.9→0.4)
5. Compare: Before vs after convergence plots

**Expected Diagnosis:**
- Diversity drops to <1% by iteration 10 (PREMATURE)
- Improvement rate <0.01% after iteration 15 (STAGNANT)
- Final cost 2x worse than expected

**Fix Results:**
- Diversity maintained at 5-10% until iteration 40
- Steady improvement until iteration 50
- Final cost 50% better

See [solution](solutions/exercise_04_solution.py).
