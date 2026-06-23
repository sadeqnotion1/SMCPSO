# Phase 4 Research Roadmap: Fixing Adaptive Gain Scheduling

**Date:** November 2025
**Objective:** Design and validate safe adaptive gain scheduling mechanisms
**Related:** MT-6 (Boundary Layer Optimization), Phase 3.3 Statistical Analysis

---

## 1. Phase 3 Recap: What We Learned

Phase 3 statistical analysis (100 trials across 4 phases) revealed critical findings:

| Finding | Impact | Recommendation |
|---------|--------|----------------|
| **Full gain scheduling** | +125% to +208% chattering | [WARNING] DO NOT USE in production |
| **Selective scheduling** (c1/c2/lambda1/lambda2) | ZERO effect (0% change) | Ineffective - try alternative mechanisms |
| **Feedback loop instability** | Cohen's d = 1.47 (large effect) | Need non-circular scheduling metric |
| **Gain coupling** | Phase 3.1 = Phase 3.2 (identical results) | Cannot distinguish c1/c2 vs lambda1/lambda2 |

**Key Insight:** Angle-based thresholds (`|theta| > threshold`) create feedback loop because:
1. Large angle triggers aggressive gains
2. Aggressive gains cause chattering
3. Chattering increases measured angle
4. Cycle repeats - unstable positive feedback

**Solution Direction:** Use **sliding surface magnitude** (`|s|`) instead of angle for scheduling decisions.

---

## 2. Phase 4 Overview: Three-Phase Approach

Phase 4 tests alternative gain scheduling mechanisms to break the feedback loop:

| Phase | Mechanism | Hypothesis | Expected Time |
|-------|-----------|------------|---------------|
| **4.1** | \|s\|-based thresholds | Break feedback loop with non-circular metric | 1-2 hours |
| **4.2** | Dynamic conservative scaling | Adaptive scaling prevents chattering | 2-3 hours |
| **4.3** | HybridGainScheduler class | Unified scheduler for all controllers | 3-4 hours |

**Total Estimate:** 6-9 hours for complete Phase 4 research

---

## 3. Phase 4.1: Sliding Surface-Based Thresholds

### 3.1 Hypothesis

Using `|s|` (sliding surface magnitude) for scheduling breaks the feedback loop because:

1. **Direct control relationship:** `|s|` is directly controlled by the controller (not a side effect)
2. **Semantic clarity:** Large `|s|` means system is far from sliding surface
3. **No circular dependency:** Reducing gains when `|s|` is large helps reach the surface (negative feedback)
4. **Physical interpretation:** `|s|` measures tracking error, not just angle

### 3.2 Approach

Use PSO to optimize two thresholds:
- `s_aggressive`: Switch to aggressive gains when `|s| > s_aggressive`
- `s_conservative`: Switch to conservative gains when `|s| < s_conservative`

**Gain Scaling:**
- Aggressive mode: `gains = nominal_gains * 1.5`
- Conservative mode: `gains = nominal_gains * 0.5`
- Nominal mode: `gains = nominal_gains` (when `s_conservative < |s| < s_aggressive`)

### 3.3 Implementation Status

**Files Created:**
- `scripts/research/phase4_1_optimize_s_based_thresholds.py` - PSO optimization script
- `scripts/research/phase4_1_validate_s_based_scheduler.py` - Validation script
- `src/controllers/sliding_surface_scheduler.py` - SlidingSurfaceAdaptiveScheduler class

**Known Bugs (MUST FIX BEFORE RUNNING):**

Both Phase 4.1 scripts use old config field names. Replace the following:

| Old Field | New Field | Occurrences |
|-----------|-----------|-------------|
| `config.physics.m1` | `config.physics.pendulum1_mass` | ~2 |
| `config.physics.m2` | `config.physics.pendulum2_mass` | ~2 |
| `config.physics.l1` | `config.physics.pendulum1_length` | ~2 |
| `config.physics.l2` | `config.physics.pendulum2_length` | ~2 |
| `config.physics.M` | `config.physics.cart_mass` | ~2 |
| `config.physics.g` | `config.physics.gravity` | ~2 |

**Fix Command (run from project root):**
```bash
# Fix phase4_1_optimize_s_based_thresholds.py
sed -i 's/config\.physics\.m1/config.physics.pendulum1_mass/g' scripts/research/phase4_1_optimize_s_based_thresholds.py
sed -i 's/config\.physics\.m2/config.physics.pendulum2_mass/g' scripts/research/phase4_1_optimize_s_based_thresholds.py
sed -i 's/config\.physics\.l1/config.physics.pendulum1_length/g' scripts/research/phase4_1_optimize_s_based_thresholds.py
sed -i 's/config\.physics\.l2/config.physics.pendulum2_length/g' scripts/research/phase4_1_optimize_s_based_thresholds.py
sed -i 's/config\.physics\.M/config.physics.cart_mass/g' scripts/research/phase4_1_optimize_s_based_thresholds.py
sed -i 's/config\.physics\.g/config.physics.gravity/g' scripts/research/phase4_1_optimize_s_based_thresholds.py

# Fix phase4_1_validate_s_based_scheduler.py
sed -i 's/config\.physics\.m1/config.physics.pendulum1_mass/g' scripts/research/phase4_1_validate_s_based_scheduler.py
sed -i 's/config\.physics\.m2/config.physics.pendulum2_mass/g' scripts/research/phase4_1_validate_s_based_scheduler.py
sed -i 's/config\.physics\.l1/config.physics.pendulum1_length/g' scripts/research/phase4_1_validate_s_based_scheduler.py
sed -i 's/config\.physics\.l2/config.physics.pendulum2_length/g' scripts/research/phase4_1_validate_s_based_scheduler.py
sed -i 's/config\.physics\.M/config.physics.cart_mass/g' scripts/research/phase4_1_validate_s_based_scheduler.py
sed -i 's/config\.physics\.g/config.physics.gravity/g' scripts/research/phase4_1_validate_s_based_scheduler.py
```

**Windows PowerShell Alternative:**
```powershell
# Fix phase4_1_optimize_s_based_thresholds.py
(Get-Content scripts\research\phase4_1_optimize_s_based_thresholds.py) -replace 'config\.physics\.m1', 'config.physics.pendulum1_mass' | Set-Content scripts\research\phase4_1_optimize_s_based_thresholds.py
(Get-Content scripts\research\phase4_1_optimize_s_based_thresholds.py) -replace 'config\.physics\.m2', 'config.physics.pendulum2_mass' | Set-Content scripts\research\phase4_1_optimize_s_based_thresholds.py
(Get-Content scripts\research\phase4_1_optimize_s_based_thresholds.py) -replace 'config\.physics\.l1', 'config.physics.pendulum1_length' | Set-Content scripts\research\phase4_1_optimize_s_based_thresholds.py
(Get-Content scripts\research\phase4_1_optimize_s_based_thresholds.py) -replace 'config\.physics\.l2', 'config.physics.pendulum2_length' | Set-Content scripts\research\phase4_1_optimize_s_based_thresholds.py
(Get-Content scripts\research\phase4_1_optimize_s_based_thresholds.py) -replace 'config\.physics\.M', 'config.physics.cart_mass' | Set-Content scripts\research\phase4_1_optimize_s_based_thresholds.py
(Get-Content scripts\research\phase4_1_optimize_s_based_thresholds.py) -replace 'config\.physics\.g', 'config.physics.gravity' | Set-Content scripts\research\phase4_1_optimize_s_based_thresholds.py

# Repeat for phase4_1_validate_s_based_scheduler.py
```

### 3.4 PSO Parameters

**Search Space:**
- `s_aggressive`: [0.1, 10.0] (sliding surface threshold for aggressive mode)
- `s_conservative`: [0.01, 1.0] (sliding surface threshold for conservative mode)

**PSO Configuration:**
- Particles: 30
- Iterations: 50
- Inertia: 0.7
- Cognitive coefficient: 1.5
- Social coefficient: 1.5

**Objective Function:**
Minimize weighted sum:
```
cost = w1 * chattering + w2 * tracking_error + w3 * control_effort
```
Where:
- `w1 = 1.0` (chattering weight)
- `w2 = 0.5` (tracking error weight)
- `w3 = 0.1` (control effort weight)

### 3.5 Execution Steps

1. **Fix bugs** (5-10 minutes):
   ```bash
   # Run fix commands above
   ```

2. **Validate scheduler** (5-10 minutes):
   ```bash
   python scripts/research/phase4_1_validate_s_based_scheduler.py
   ```
   Expected output: Scheduler switches modes correctly based on |s| values

3. **Run PSO optimization** (30-60 minutes):
   ```bash
   python scripts/research/phase4_1_optimize_s_based_thresholds.py
   ```
   Expected output:
   - Optimal thresholds: `s_aggressive_opt`, `s_conservative_opt`
   - Performance comparison: baseline vs scheduled
   - JSON report: `benchmarks/research/phase4_1/phase4_1_results.json`

4. **Analyze results** (10-15 minutes):
   - Compare chattering: scheduled vs baseline
   - Check for feedback instability (like Phase 2.3)
   - Validate hypothesis: |s|-based scheduling safer than angle-based

### 3.6 Success Criteria

- [ ] PSO converges (cost decreases over iterations)
- [ ] Chattering reduction: scheduled <= baseline (no increase)
- [ ] Tracking error maintained: <= 5% degradation
- [ ] Scheduler stability: no oscillations between modes
- [ ] Hypothesis validated: |s|-based scheduling breaks feedback loop

### 3.7 Deliverables

- [ ] `phase4_1_results.json` - PSO optimization results
- [ ] `phase4_1_chattering_comparison.png` - Chattering plot
- [ ] `phase4_1_scheduling_timeline.png` - Mode switching over time
- [ ] `PHASE4_1_SUMMARY.md` - Analysis report

---

## 4. Phase 4.2: Dynamic Conservative Scaling

### 4.1 Motivation

Phase 4.1 uses fixed scaling factors (1.5x aggressive, 0.5x conservative). Phase 4.2 makes scaling **adaptive** based on system state.

### 4.2 Hypothesis

Dynamic scaling prevents chattering by:
1. **Gradual transitions:** Smooth scaling reduces mode-switching shocks
2. **State-aware adaptation:** Scale factor follows system dynamics
3. **Chattering suppression:** Conservative scaling activates during high-frequency oscillations

### 4.3 Approach

Replace fixed `conservative_scale = 0.5` with adaptive function:

```python
def compute_conservative_scale(s_magnitude: float, s_rate: float, chattering: float) -> float:
    """
    Compute adaptive conservative scaling factor.

    Args:
        s_magnitude: Current |s| value
        s_rate: Rate of change of |s| (d|s|/dt)
        chattering: Recent chattering metric

    Returns:
        scale: Conservative gain multiplier in [0.1, 1.0]
    """
    # Base scaling on sliding surface magnitude
    base_scale = np.clip(0.5 - 0.4 * (s_magnitude / 10.0), 0.1, 0.5)

    # Increase conservatism if chattering detected
    if chattering > threshold:
        base_scale *= 0.5  # More conservative

    # Adjust for sliding surface rate
    if s_rate > 0:  # Moving away from surface
        base_scale *= 1.2  # Less conservative
    else:  # Approaching surface
        base_scale *= 0.8  # More conservative

    return np.clip(base_scale, 0.1, 1.0)
```

### 4.4 Implementation Tasks

1. **Create DynamicConservativeScheduler class** (1 hour):
   - Inherit from SlidingSurfaceAdaptiveScheduler
   - Add `compute_conservative_scale()` method
   - Track `s_rate` using finite differences
   - Monitor chattering with sliding window

2. **Integration testing** (30 minutes):
   - Test with HybridAdaptiveSTASMC controller
   - Verify smooth transitions (no discontinuities)
   - Validate chattering suppression

3. **Comparative analysis** (30-60 minutes):
   - Compare vs Phase 4.1 fixed scaling
   - Compare vs baseline (no scheduling)
   - Statistical testing (Welch's t-test, Cohen's d)

### 4.5 Success Criteria

- [ ] Smooth scaling transitions (no discontinuities)
- [ ] Chattering reduction: dynamic <= fixed scaling
- [ ] Tracking performance maintained: <= 5% degradation
- [ ] Computational overhead: < 10% increase

### 4.6 Deliverables

- [ ] `src/controllers/dynamic_conservative_scheduler.py` - Scheduler class
- [ ] `scripts/research/phase4_2_test_dynamic_scaling.py` - Test script
- [ ] `benchmarks/research/phase4_2/phase4_2_results.json` - Results
- [ ] `PHASE4_2_SUMMARY.md` - Analysis report

---

## 5. Phase 4.3: HybridGainScheduler Integration

### 5.1 Motivation

Phases 4.1 and 4.2 create standalone schedulers. Phase 4.3 integrates them into a unified `HybridGainScheduler` class compatible with all controllers.

### 5.2 Objectives

1. **Unified interface:** Single scheduler class for all controller types
2. **Multiple strategies:** Support angle-based, |s|-based, and dynamic scaling
3. **Safe defaults:** Conservative settings prevent chattering
4. **Extensive testing:** Integration tests with all 7 controllers

### 5.3 Architecture

```python
class HybridGainScheduler:
    """
    Unified adaptive gain scheduler with multiple strategies.

    Supports:
    - Angle-based scheduling (|theta| thresholds) - UNSAFE, for research only
    - Sliding surface scheduling (|s| thresholds) - SAFE, recommended
    - Dynamic conservative scaling - SAFEST, production-ready
    """

    def __init__(self, strategy: str = "sliding_surface", **kwargs):
        """
        Initialize scheduler.

        Args:
            strategy: "angle", "sliding_surface", or "dynamic"
            **kwargs: Strategy-specific parameters
        """
        self.strategy = strategy

        if strategy == "angle":
            self._scheduler = AngleBasedScheduler(**kwargs)  # Phase 2 approach
        elif strategy == "sliding_surface":
            self._scheduler = SlidingSurfaceAdaptiveScheduler(**kwargs)  # Phase 4.1
        elif strategy == "dynamic":
            self._scheduler = DynamicConservativeScheduler(**kwargs)  # Phase 4.2
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def schedule_gains(self, state, sliding_surface, gains):
        """Delegate to strategy-specific scheduler."""
        return self._scheduler.schedule_gains(state, sliding_surface, gains)
```

### 5.4 Implementation Tasks

1. **Create HybridGainScheduler class** (1 hour):
   - Strategy pattern for multiple scheduling approaches
   - Unified API for all controllers
   - Safe defaults (dynamic strategy)

2. **Integration tests** (1-2 hours):
   - Test with all 7 controllers:
     - ClassicalSMC
     - STASMC
     - AdaptiveSMC
     - HybridAdaptiveSTASMC
     - SwingUpSMC
     - MPCController
     - LQRController (if applicable)
   - Verify no regressions in baseline performance
   - Test all 3 strategies (angle, sliding_surface, dynamic)

3. **Documentation** (30-60 minutes):
   - API reference for HybridGainScheduler
   - Usage examples for each strategy
   - Safety guidelines (when to use each strategy)

### 5.5 Success Criteria

- [ ] HybridGainScheduler works with all 7 controllers
- [ ] No performance regressions (baseline performance maintained)
- [ ] All unit tests pass (≥95% coverage)
- [ ] Integration tests pass (all 3 strategies)
- [ ] Documentation complete (API + examples + safety guidelines)

### 5.6 Deliverables

- [ ] `src/controllers/hybrid_gain_scheduler.py` - Unified scheduler class
- [ ] `tests/test_controllers/test_hybrid_gain_scheduler.py` - Unit tests
- [ ] `tests/test_integration/test_scheduler_integration.py` - Integration tests
- [ ] `docs/guides/adaptive_gain_scheduling.md` - User guide
- [ ] `PHASE4_3_SUMMARY.md` - Implementation report

---

## 6. Timeline & Resources

| Phase | Tasks | Expected Time | Dependencies |
|-------|-------|---------------|--------------|
| **4.1** | Fix bugs, validate, run PSO, analyze | 1-2 hours | None |
| **4.2** | Design, implement, test dynamic scaling | 2-3 hours | Phase 4.1 complete |
| **4.3** | Create scheduler, integration tests, docs | 3-4 hours | Phase 4.2 complete |

**Total:** 6-9 hours for complete Phase 4 research

**Critical Path:**
1. Phase 4.1 (PRIORITY 1) - Validates core hypothesis
2. Phase 4.2 (PRIORITY 2) - Improves performance
3. Phase 4.3 (PRIORITY 3) - Production integration

**Parallelization Opportunities:**
- Phase 4.2 design can start while Phase 4.1 PSO runs
- Phase 4.3 documentation can start after Phase 4.2 design complete

---

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PSO fails to converge | Medium | High | Use coarse grid search first |
| \|s\|-based still has feedback loop | Low | High | Verify with logging/visualization |
| Dynamic scaling too complex | Low | Medium | Fall back to fixed scaling |
| Integration breaks existing controllers | Low | High | Extensive testing before merge |

---

## 8. Success Metrics

**Phase 4.1:**
- Chattering: scheduled <= baseline (no increase)
- Hypothesis validated: |s|-based breaks feedback loop

**Phase 4.2:**
- Chattering: dynamic <= fixed scaling
- Smooth transitions: no discontinuities

**Phase 4.3:**
- Coverage: ≥95% for HybridGainScheduler
- Integration: All 7 controllers pass tests
- Documentation: Complete API + examples

**Overall:**
- Research paper: 1 additional section on safe gain scheduling
- Production readiness: SAFE adaptive scheduling option available

---

## 9. Next Steps (Sequential)

1. **Fix Phase 4.1 bugs** (5-10 minutes)
   - Run fix commands from Section 3.3
   - Verify scripts run without AttributeError

2. **Validate |s|-based scheduler** (5-10 minutes)
   - Run `phase4_1_validate_s_based_scheduler.py`
   - Check mode switching works correctly

3. **Run Phase 4.1 PSO** (30-60 minutes)
   - Execute `phase4_1_optimize_s_based_thresholds.py`
   - Monitor convergence
   - Analyze results vs baseline

4. **Phase 4.1 Analysis** (10-15 minutes)
   - Create PHASE4_1_SUMMARY.md
   - Compare to Phase 2.3 (feedback instability)
   - Decision point: Continue to 4.2 or iterate on 4.1?

5. **Proceed to Phase 4.2** (if 4.1 successful)
   - Design dynamic scaling function
   - Implement DynamicConservativeScheduler
   - Comparative testing

6. **Proceed to Phase 4.3** (if 4.2 successful)
   - Create HybridGainScheduler
   - Integration tests (all 7 controllers)
   - Documentation

---

## 10. References

**Related Research:**
- Phase 2.1: Gain Interference (100 trials, +125% chattering)
- Phase 2.3: Feedback Instability (100 trials, +176% chattering, d=1.47)
- Phase 3.1: c1/c2 Selective Scheduling (selective=0%, full=+208%)
- Phase 3.2: lambda1/lambda2 Selective Scheduling (identical to 3.1)
- Phase 3.3: Statistical Comparison (comprehensive analysis)
- MT-6: Boundary Layer Optimization (robust PSO gains)
- MT-8: Enhanced Disturbances (validation with noise)

**Key Insight:**
Angle-based scheduling creates feedback loop:
```
Large angle → Aggressive gains → Chattering → Larger measured angle → More aggressive gains → MORE CHATTERING
```

Solution: Use |s| (sliding surface) instead of |theta| for scheduling decisions.

---

**Status:** Phase 4 scaffolding complete, awaiting bug fixes and PSO runs
**Next Action:** Fix config field names in Phase 4.1 scripts (see Section 3.3)
**Expected Completion:** 6-9 hours for full Phase 4 research
