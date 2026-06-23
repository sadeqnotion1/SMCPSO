# Step 1: Extract Sources for Chapter 9 - Experimental Design

**Time**: 1.5 hours | **Output**: Notes for Chapter 9

---

## OBJECTIVE

Extract experimental workflow, test scenarios, parameter sweeps, Monte Carlo setup, and validation procedures.

---

## SOURCE MATERIALS (1.5 hours)

### Primary Sources
1. **Benchmark Scripts** (30 min)
   - `scripts/run_comprehensive_benchmark.py`
   - `benchmarks/*.csv` (existing results)
   - Note test scenarios, metrics collected

2. **PSO Workflows** (20 min)
   - `scripts/mt7_robust_pso.py` (seed variation)
   - `scripts/mt8_robust_pso.py` (disturbance-aware)
   - Note optimization protocols

3. **Robustness Tests** (20 min)
   - `.artifacts/LT6_*` reports (uncertainty analysis)
   - `.artifacts/MT6_*` reports (boundary layer optimization)
   - Note parameter sweep ranges

4. **Test Procedures** (20 min)
   - `tests/test_integration/` (integration test structure)
   - `run_tests.py` (test execution workflow)

---

## EXTRACTION TASKS

### Task 1: Experimental Workflow (20 min)
**Create**: `thesis/notes/chapter09_workflow.txt`
```
EXPERIMENTAL WORKFLOW

Phase 1: Baseline Testing (QW-2, MT-5)
- Run all 7 controllers with standard IC
- Collect 6 metrics per controller
- Rank by composite performance index
- Time: ~5 minutes per controller

Phase 2: PSO Optimization (MT-7, MT-8)
- Optimize gains for each controller
- Standard PSO: 30 particles × 50 iterations
- Robust PSO: Dual fitness (nominal + disturbed)
- Time: ~20 seconds per controller

Phase 3: Robustness Testing (LT-6)
- Test with 4 ICs (small/medium/large/extreme)
- Test with parameter uncertainty (±20% mass, ±10% length)
- Test with disturbances (step, impulse)
- Time: ~30 minutes total

Phase 4: Statistical Analysis (MT-7)
- Monte Carlo: 10 seeds × 7 controllers = 70 runs
- Compute mean, std, confidence intervals
- Time: ~10 minutes

Phase 5: Validation (All tasks)
- Verify Lyapunov stability conditions
- Check theoretical predictions vs simulation
- Cross-validate metrics
```

### Task 2: Test Scenarios (15 min)
**Create**: `thesis/notes/chapter09_scenarios.txt`
- Scenario 1: Baseline (nominal, no disturbance)
- Scenario 2: Step disturbance (10N @ t=2s)
- Scenario 3: Impulse disturbance (30N pulse)
- Scenario 4: Parameter uncertainty (mass +20%)
- Scenario 5: Combined (disturbance + uncertainty)

### Task 3: Parameter Sweeps (15 min)
**Create**: `thesis/notes/chapter09_sweeps.txt`
- Boundary layer: ϕ ∈ [0.01, 0.5] (20 values, MT-6)
- Adaptation rate: γ ∈ [0.01, 1.0] (adaptive SMC)
- PSO hyperparameters: w ∈ [0.4, 0.9], c1/c2 ∈ [1.0, 2.5]

---

## VALIDATION

- [ ] 5 experimental phases documented
- [ ] 5 test scenarios listed
- [ ] Parameter sweep ranges extracted
- [ ] Time estimates for each phase

---

## TIME: ~1.5 hours

## NEXT STEP: `step_02_section_9_1_intro.md`
