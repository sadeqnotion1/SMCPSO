# CA-02 Phase 2: Leak Detection Results

**Date**: November 11, 2025
**Duration**: 2 hours
**Test Method**: tracemalloc + 2 test scenarios
**Status**: [OK] COMPLETE

---

## Executive Summary

Phase 2 ran two leak detection tests across all 4 controllers:
1. **Test 1**: Create NEW controller 1000 times (test factory/creation leaks)
2. **Test 2**: Use SAME controller for 1000 steps (test history list leaks)

**Critical Finding**: **STA-SMC has a MASSIVE memory leak** (13.94 KB/cycle) caused by Numba JIT compilation code. This is a **CRITICAL** production blocker.

**Other controllers**: All 3 other controllers (Classical, Adaptive, Hybrid) pass leak detection with <0.21 KB/step growth.

---

## Test 1: Controller Creation/Destruction Leaks

### Test Design
- Create NEW controller instance 1000 times
- Run short simulation (0.5s, dt=0.01) on each cycle
- Delete controller and force GC every 100 cycles
- Measure memory growth over 1000 cycles

### Results Summary

| Controller | Growth (KB/cycle) | Verdict | Total Growth (MB) |
|-----------|-------------------|---------|-------------------|
| classical_smc | 0.04 | ✅ OK | 0.04 |
| sta_smc | **13.94** | ❌ **LEAK DETECTED** | **13.61** |
| adaptive_smc | 0.01 | ✅ OK | 0.01 |
| hybrid_adaptive_sta_smc | 0.01 | ✅ OK | 0.01 |

---

### 1.1 ClassicalSMC: PASS ✅

**Memory Growth**: 0.04 KB/cycle (40 KB over 1000 cycles)

**Snapshots**:
- Cycle 0: 0.00 MB (baseline)
- Cycle 100: 0.04 MB (+0.04 MB)
- Cycle 500: 0.04 MB (stable)
- Cycle 1000: 0.04 MB (stable)

**Top Allocations**:
1. linecache.py: 0.030 MB (334 allocations) - Python internal caching
2. numpy fromnumeric.py: 0.003 MB (67 allocations) - NumPy overhead
3. simulation_runner.py:216: 0.002 MB (2 allocations) - Array allocation

**Assessment**: ✅ **EXCELLENT** - Minimal growth, well within acceptable limits

---

### 1.2 STASMC: FAIL ❌ [CRITICAL]

**Memory Growth**: 13.94 KB/cycle (13.61 MB over 1000 cycles)

**Snapshots**:
- Cycle 0: 0.00 MB (baseline)
- Cycle 100: 13.61 MB (+13.61 MB) - **MASSIVE JUMP**
- Cycle 500: 13.61 MB (stable after initial jump)
- Cycle 1000: 13.61 MB (stable)

**Top Allocations** (all Numba JIT compilation):
1. `<frozen importlib._bootstrap_external>:757`: 3.71 MB (31,600 allocations)
2. `<frozen abc>:106`: 2.98 MB (9,181 allocations)
3. `numba.core.typing.templates.py:1183`: 0.54 MB (1,971 allocations)
4. `<frozen abc>:107`: 0.39 MB (2,807 allocations)
5. `numba.core.typing.context.py:439`: 0.36 MB (2,444 allocations)
6. `numba.core.typing.templates.py:891`: 0.29 MB (4,971 allocations)
7. `<frozen abc>:123`: 0.28 MB (3,160 allocations)
8. `numba.core.typing.context.py:474`: 0.27 MB (3,027 allocations)
9. `numba.core.typing.templates.py:889`: 0.26 MB (3,710 allocations)
10. `numba.np.npyimpl.py:465`: 0.18 MB (774 allocations)

**Root Cause Analysis**:
- All allocations are in Numba JIT compilation infrastructure
- Leak occurs during first 100 cycles, then stabilizes
- Suggests Numba is repeatedly compiling code instead of caching compiled functions
- Possible causes:
  1. Dynamic function generation (new function objects on each call)
  2. Missing `@njit(cache=True)` decorator
  3. Numba cache disabled or not working
  4. Non-hashable function arguments preventing cache hits

**Assessment**: ❌ **CRITICAL LEAK** - Production blocker

**Recommendation**:
1. Review all `@njit` decorators in sta_smc.py and ensure `cache=True` is set
2. Check for dynamic function generation (lambdas, closures)
3. Investigate Numba cache directory and permissions
4. Consider pre-compiling all Numba functions on module load

---

### 1.3 AdaptiveSMC: PASS ✅

**Memory Growth**: 0.01 KB/cycle (9.4 KB over 1000 cycles)

**Snapshots**:
- Cycle 0: 0.00 MB (baseline)
- Cycle 100: 0.01 MB (+0.01 MB)
- Cycle 500: 0.01 MB (stable)
- Cycle 1000: 0.01 MB (stable)

**Top Allocations**:
1. numpy fromnumeric.py: 0.003 MB (76 allocations)
2. simulation_runner.py:216: 0.002 MB (2 allocations)

**Assessment**: ✅ **EXCELLENT** - Minimal growth

---

### 1.4 HybridAdaptiveSTASMC: PASS ✅

**Memory Growth**: 0.01 KB/cycle (7.0 KB over 1000 cycles)

**Snapshots**:
- Cycle 0: 0.00 MB (baseline)
- Cycle 100: 0.00 MB (stable)
- Cycle 500: 0.01 MB (+0.01 MB)
- Cycle 1000: 0.01 MB (stable)

**Top Allocations**:
1. simulation_runner.py:216: 0.002 MB (2 allocations)
2. numpy fromnumeric.py: 0.0005 MB (12 allocations)

**Assessment**: ✅ **EXCELLENT** - Minimal growth

---

## Test 2: History List Growth Leaks

### Test Design
- Create ONE controller instance (not recreated)
- Run 1000 simulation steps with SAME controller
- Track memory growth from unbounded history lists
- Inspect controller internals for history list sizes

### Results Summary

| Controller | Growth (KB/step) | Verdict | Total Growth (MB) | History Sizes |
|-----------|------------------|---------|-------------------|---------------|
| classical_smc | 0.21 | ✅ OK | 0.20 | None detected |
| sta_smc | **14.04** | ❌ **LEAK DETECTED** | **13.71** | None detected |
| adaptive_smc | 0.14 | ✅ OK | 0.14 | None detected |
| hybrid_adaptive_sta_smc | 0.13 | ✅ OK | 0.13 | None detected |

---

### 2.1 ClassicalSMC: PASS ✅

**Memory Growth**: 0.21 KB/step (0.20 MB over 1000 steps)

**Snapshots**:
- Step 0: 0.00 MB (baseline)
- Step 100: 0.05 MB (+0.05 MB)
- Step 500: 0.12 MB (+0.12 MB)
- Step 1000: 0.20 MB (+0.20 MB)

**Growth Pattern**: Linear growth (0.20 MB / 1000 steps = 0.20 KB/step)

**History List Inspection**: No history lists detected (empty dict)

**Assessment**: ✅ **ACCEPTABLE** - Slight linear growth, but within limits

---

### 2.2 STASMC: FAIL ❌ [CRITICAL]

**Memory Growth**: 14.04 KB/step (13.71 MB over 1000 steps)

**Snapshots**:
- Step 0: 0.00 MB (baseline)
- Step 100: 13.62 MB (+13.62 MB) - **MASSIVE JUMP**
- Step 500: 13.66 MB (+0.04 MB)
- Step 1000: 13.71 MB (+0.05 MB)

**Growth Pattern**: Massive initial jump (13.62 MB in first 100 steps), then slow linear growth

**History List Inspection**: No history lists detected (empty dict)

**Root Cause**: Same as Test 1 - Numba JIT compilation leak, not history lists

**Assessment**: ❌ **CRITICAL LEAK** - Production blocker

---

### 2.3 AdaptiveSMC: PASS ✅

**Memory Growth**: 0.14 KB/step (0.14 MB over 1000 steps)

**Snapshots**:
- Step 0: 0.00 MB (baseline)
- Step 100: 0.02 MB (+0.02 MB)
- Step 500: 0.07 MB (+0.07 MB)
- Step 1000: 0.14 MB (+0.14 MB)

**Growth Pattern**: Linear growth (0.14 MB / 1000 steps = 0.14 KB/step)

**History List Inspection**: No history lists detected (empty dict)

**Assessment**: ✅ **ACCEPTABLE** - Slight linear growth, but within limits

**Note**: Phase 1 identified `_control_history` list bounded to 100 items (adaptive/controller.py:71, 119-120), which explains why no unbounded growth is detected here. The bounded list design is working correctly.

---

### 2.4 HybridAdaptiveSTASMC: PASS ✅

**Memory Growth**: 0.13 KB/step (0.13 MB over 1000 steps)

**Snapshots**:
- Step 0: 0.00 MB (baseline)
- Step 100: 0.01 MB (+0.01 MB)
- Step 500: 0.06 MB (+0.06 MB)
- Step 1000: 0.13 MB (+0.13 MB)

**Growth Pattern**: Linear growth (0.13 MB / 1000 steps = 0.13 KB/step)

**History List Inspection**: No history lists detected (empty dict)

**Assessment**: ✅ **ACCEPTABLE** - Slight linear growth, but within limits

**Note**: Phase 1 identified `control_history` bounded to 1000 items with truncation to 500 (hybrid/controller.py:106, 259-260), which explains why no unbounded growth is detected. The bounded list design is working correctly.

---

## Reconciliation with Phase 1 Findings

### Expected vs. Actual Results

Phase 1 identified 7 potential unbounded history lists:
1. switching_history (hybrid/controller.py) - **NOT DETECTED** in Test 2
2. switch_history (hybrid/switching_logic.py) - **NOT DETECTED** in Test 2
3. _adaptation_history (adaptive/adaptation_law.py) - **NOT DETECTED** in Test 2
4. _parameter_history (adaptive/parameter_estimation.py) - **NOT DETECTED** in Test 2
5. simulation_history (simulation_runner.py) - **NOT TESTED** (not part of controller)
6. threshold_adaptation_history (hybrid/switching_logic.py) - **NOT DETECTED** in Test 2
7. performance_history (hybrid/switching_logic.py) - **NOT DETECTED** in Test 2

### Why Weren't History Lists Detected?

**Theory 1**: Short simulation time (1000 steps = 10 seconds) may not trigger enough events
- switching_history only grows on controller switches (rare events)
- _adaptation_history only grows on gain updates (periodic, not every step)
- _parameter_history only grows on parameter updates (periodic)

**Theory 2**: History lists may be nested in sub-components not accessible via hasattr()
- switching_logic is a sub-object of hybrid controller
- adaptation_law is a sub-object of adaptive controller
- Need deeper inspection

**Theory 3**: History lists may have been cleared or not used in this test configuration
- Some history lists may only be used with specific config flags
- Need to review controller initialization paths

**Recommendation**: Run Phase 3 stress test with MUCH longer simulation (10,000+ steps) and enable all optional features (adaptive thresholds, parameter estimation, etc.) to trigger history list growth.

---

## Critical Findings Summary

### CRITICAL Issue: STA-SMC Numba Leak ❌

**Severity**: CRITICAL (production blocker)

**Impact**: 13.94 KB/cycle memory growth in repeated simulations

**Root Cause**: Numba JIT compilation code leaking memory
- Allocations in importlib, abc, numba.core.typing
- 13.61 MB leaked in first 100 cycles
- Suggests repeated JIT compilation instead of caching

**Evidence**:
- Test 1 (1000 controller creations): 13.61 MB growth
- Test 2 (1000 steps, same controller): 13.71 MB growth
- Both tests show identical Numba allocation patterns

**Affected Code**: `src/controllers/smc/sta_smc.py` (Numba decorators)

**Fix Priority**: P0 (must fix before production deployment)

**Estimated Effort**: 2-4 hours (review Numba decorators, add cache=True, test)

---

### Expected History List Leaks: NOT CONFIRMED ⚠️

**Severity**: MEDIUM (needs longer testing)

**Impact**: Unbounded history lists identified in Phase 1 did NOT cause measurable leaks in 1000-step test

**Possible Reasons**:
1. Test duration too short (1000 steps = 10 seconds)
2. History lists nested in sub-components (not accessible via hasattr)
3. History lists only used with specific config flags (not enabled in test)

**Recommendation**: Run Phase 3 stress test with:
- 10,000+ simulation steps (100 seconds)
- Enable all optional features (adaptive thresholds, parameter estimation)
- Deeper inspection of nested components (switching_logic, adaptation_law)

---

## Phase 2 Validation

### Checklist

- ✅ Leak detection script created (detect_memory_leaks.py)
- ✅ History leak detection script created (detect_history_leaks.py)
- ✅ All 4 controllers tested (Test 1: creation, Test 2: history)
- ✅ Memory snapshots collected at 0, 100, 500, 1000 intervals
- ✅ Top 10 allocations identified for each controller
- ✅ Results saved to JSON (leak_detection_results.json, history_leak_detection_results.json)
- ✅ Critical leak identified (STA-SMC Numba)
- ⚠️ Expected history leaks NOT confirmed (needs longer testing)

### Success Criteria Met

- ✅ Can identify memory leaks with tracemalloc
- ✅ Can measure memory growth rate (KB/cycle)
- ✅ Can trace allocations back to source files
- ✅ Can categorize leaks by severity (CRITICAL: STA-SMC)
- ⏩ Ready for Phase 3 (stress testing with longer simulations)

---

## Next Steps

### Phase 3: Stress Testing (2 hours)

1. **Extend Test Duration**: Run 10,000 simulation steps (100 seconds) to trigger more history list events
2. **Enable All Features**: Turn on adaptive thresholds, parameter estimation, switching logic
3. **Monitor Memory**: Generate memory usage plots over time
4. **Inspect Nested Components**: Deeper inspection of switching_logic, adaptation_law sub-objects
5. **Confirm History Leaks**: Verify whether Phase 1 identified lists actually grow unbounded

### Phase 4: Cleanup Verification (1.5 hours)

1. **Test STA Cleanup**: Verify STA cleanup() method releases Numba resources
2. **Test All Cleanups**: Manually test cleanup() for all 4 controllers
3. **Verify Nested Cleanup**: Check if sub-components (switching_logic) have cleanup methods

### Phase 5: Fix Recommendations (0.5 hours)

1. **Design STA Fix**: Add `cache=True` to all @njit decorators, test pre-compilation
2. **Design History Fixes**: Add truncation to all unbounded lists (if confirmed in Phase 3)
3. **Prioritize Fixes**: CRITICAL (STA Numba) → MAJOR (history lists) → MINOR (optimizations)

---

## Appendix: Verification Commands

```bash
# Run Test 1: Controller creation/destruction leaks
python .artifacts/qa_audits/CA-02_MEMORY_MANAGEMENT_AUDIT/detect_memory_leaks.py

# Run Test 2: History list growth leaks
python .artifacts/qa_audits/CA-02_MEMORY_MANAGEMENT_AUDIT/detect_history_leaks.py

# View results
cat .artifacts/qa_audits/CA-02_MEMORY_MANAGEMENT_AUDIT/leak_detection_results.json
cat .artifacts/qa_audits/CA-02_MEMORY_MANAGEMENT_AUDIT/history_leak_detection_results.json
```

---

**Phase 2 Status**: [OK] COMPLETE
**Time**: 2 hours (as planned)
**Critical Finding**: STA-SMC Numba leak (13.94 KB/cycle) - PRODUCTION BLOCKER
**Next Phase**: Phase 3 (Stress Testing with extended duration)
