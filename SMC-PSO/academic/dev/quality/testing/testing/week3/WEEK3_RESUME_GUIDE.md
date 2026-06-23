# Week 3 Coverage Improvement - Resume Guide

**Status**: PAUSED (pending factory API fix)
**Pause Date**: December 20, 2025 (Session 3 complete)
**Resume Trigger**: Factory API bug resolved
**Estimated Resume Time**: 30 seconds (with this guide)

---

## Quick Status Check

**Before resuming**, verify the factory fix is complete:

```bash
# 1. Check factory bug status
cat .project/ai/issues/FACTORY_API_BUG.md | grep "Status:"

# 2. Run integration tests to verify fix
python -m pytest tests/test_integration/test_factory_integration.py::TestFactoryControllerCreation::test_create_controller_from_config -v

# Expected: 5/5 controllers PASSING (not 1/5)
```

**If tests still fail**: Factory fix incomplete, DO NOT resume Week 3.

---

## Prerequisites Checklist

Before resuming Week 3, ensure:

- [ ] Factory API bug fixed (FACTORY-001)
- [ ] All 5 controllers passing integration tests
- [ ] No regressions in factory unit tests
- [ ] Factory code updated at `src/controllers/factory/base.py:656`
- [ ] Controller constructors standardized: `(config, dynamics_model, **kwargs)`

**Validation Commands**:
```bash
# All controllers should pass
python -m pytest tests/test_integration/test_factory_integration.py -v

# Factory unit tests should still pass
python -m pytest tests/test_controllers/factory/ -v

# No new test errors
python -m pytest tests/ --maxfail=1 -x
```

---

## Resume Workflow (30 seconds)

### Step 1: Quick Recovery

```bash
# Load project state
bash .project/tools/recovery/recover_project.sh

# Check Week 3 progress
cat .project/ai/planning/WEEK3_PROGRESS.md | head -20

# Verify baseline coverage
python -m pytest tests/ --cov=src --cov-report=term-missing | grep "TOTAL"
```

**Expected Baseline**:
- Coverage: ~9-15% overall
- Factory: ~15-20% partial
- Tests passing: 16+ (after factory fix)

### Step 2: Update Status

```bash
# Mark Week 3 as RESUMED in progress tracker
# Update .project/ai/planning/WEEK3_PROGRESS.md:
# - Change "Status: PAUSED" → "Status: RESUMED"
# - Add Session 4 header
# - Update baseline metrics after factory fix
```

### Step 3: Measure New Baseline

```bash
# Get coverage after factory fix
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

# Check what improved
# Compare to pre-fix baseline (9.14% overall)
```

---

## Session 4 Plan (First Session After Resume)

**Duration**: 1-2 hours
**Goal**: Validate factory fix + continue integration tests

### Tasks

1. **Validate Factory Fix** (15 min)
   - Re-run all integration tests
   - Verify 5/5 controllers passing
   - Check coverage delta from fix

2. **Complete Integration Test Suite** (30-45 min)
   - Expand Controller → Control Computation tests
   - Add PSO Integration tests (4 controllers)
   - Add End-to-End Workflow tests (6 tests)

3. **Measure Coverage Improvement** (15 min)
   - Run coverage report
   - Compare to baseline (9.14%)
   - Document gains in WEEK3_PROGRESS.md

4. **Plan Next Phase** (15 min)
   - Decide: continue integration tests OR switch to focused unit tests
   - Update Week 3 roadmap based on coverage gains

---

## Expected Outcomes (Session 4)

**If factory fix is good**:
- Integration tests: 40-48 tests passing (90%+ pass rate)
- Coverage: 15-25% overall (factory: 30-40%)
- Ready to continue Week 3 with confidence

**If factory fix is incomplete**:
- Integration tests: still failing
- **Action**: Document new issues, pause again
- DO NOT continue Week 3 until factory is fully working

---

## Recovery Commands Reference

### Quick Status
```bash
# View progress tracker
cat .project/ai/planning/WEEK3_PROGRESS.md

# View Session 3 findings
cat .project/ai/planning/WEEK3_SESSION3_FINDINGS.md

# View factory bug details
cat .project/ai/issues/FACTORY_API_BUG.md

# Check current coverage
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
```

### Run Tests
```bash
# Integration tests (should be 5/5 passing)
python -m pytest tests/test_integration/test_factory_integration.py -v

# Factory unit tests
python -m pytest tests/test_controllers/factory/ -v

# All tests
python -m pytest tests/ -v --tb=short
```

### Coverage Analysis
```bash
# Overall coverage
python -m pytest tests/ --cov=src --cov-report=html

# Factory coverage specifically
python -m pytest tests/ --cov=src/controllers/factory --cov-report=term-missing

# Open HTML report
start coverage_html/index.html  # Windows
# OR
open coverage_html/index.html   # Mac/Linux
```

---

## Week 3 Roadmap (After Resume)

### Completed (Sessions 1-3)
- [x] Session 1: 48 factory base tests (mock-based)
- [x] Session 2: 27 thread-safety tests (mock-based)
- [x] Session 3: 48 integration tests (real config) **FOUND CRITICAL BUG**

### Remaining Work (4-14 hours)

**Session 4** (1-2h): Validate factory fix + complete integration tests
- [ ] Re-run integration tests (verify 5/5 passing)
- [ ] Expand control computation tests
- [ ] Add PSO integration tests
- [ ] Add end-to-end workflow tests

**Session 5+** (3-12h): Focused unit tests for pure functions
- [ ] Validation module tests (120 tests)
- [ ] Registry tests (80 tests)
- [ ] PSO integration tests (80 tests)
- [ ] Utils critical coverage (130 tests)

**Target**: 45-50% coverage overall, 90% factory coverage

---

## Files to Review Before Resume

1. **Progress Tracker**: `.project/ai/planning/WEEK3_PROGRESS.md`
   - Current status, metrics, phases

2. **Session 3 Findings**: `.project/ai/planning/WEEK3_SESSION3_FINDINGS.md`
   - What we discovered, why it matters

3. **Factory Bug**: `.project/ai/issues/FACTORY_API_BUG.md`
   - Bug details, fix requirements

4. **Integration Tests**: `tests/test_integration/test_factory_integration.py`
   - 390 lines, 48 tests, 4 test suites

5. **Current Status**: `.project/ai/planning/CURRENT_STATUS.md`
   - Overall project status (will update)

---

## What Changed During Pause

**Code**:
- Created: `tests/test_integration/test_factory_integration.py` (390 lines)
- No other code changes (work paused)

**Documentation**:
- Created: `WEEK3_SESSION3_FINDINGS.md` (comprehensive analysis)
- Created: `FACTORY_API_BUG.md` (this bug report)
- Created: `WEEK3_RESUME_GUIDE.md` (this file)
- Updated: `WEEK3_PROGRESS.md` (Session 3 metrics)

**Tests**:
- Total: 123 tests (75 unit + 48 integration)
- Passing: 16/123 (13% - due to factory bug)
- After fix: expect 60-80/123 passing (50-65%)

---

## Common Issues After Resume

### Issue 1: Integration tests still failing

**Symptom**: 1/5 or 0/5 controllers passing
**Cause**: Factory fix incomplete
**Solution**: Review factory fix, check constructor signatures

### Issue 2: New test errors

**Symptom**: Tests that passed before now fail
**Cause**: Factory fix introduced regressions
**Solution**: Run unit tests, check for breaking changes

### Issue 3: Coverage dropped

**Symptom**: Coverage <9% (lower than baseline)
**Cause**: Factory fix removed tested code
**Solution**: Review coverage report, add tests for new code paths

---

## Success Criteria for Resume

**Minimum Requirements**:
- Integration tests: 5/5 controllers passing
- Factory unit tests: no new failures
- Coverage: ≥9.14% (no regression)

**Target Goals**:
- Integration tests: 40+ tests passing (85%+)
- Coverage: 15-25% overall, 30-40% factory
- Ready to continue Week 3 phases 4-7

**If Not Met**:
- Document new issues
- Pause again if critical bugs found
- Do NOT force coverage work with broken tests

---

## Contact Information

**Week 3 Owner**: Claude Code (AI Assistant)
**Factory Fix Owner**: Factory team (TBD)
**Issue Tracking**: `.project/ai/issues/FACTORY_API_BUG.md`

---

## Timeline

**Pause Date**: December 20, 2025, 9:00pm
**Pause Reason**: Critical factory API bug (FACTORY-001)
**Expected Resume**: After factory fix (2-4 hours estimated)
**Sessions Completed**: 3/10+ (4 hours spent)
**Time Remaining**: 8-14 hours (after resume)

---

## One-Command Resume

```bash
# When factory fix is complete, run this:
bash .project/tools/recovery/recover_project.sh && \
  python -m pytest tests/test_integration/test_factory_integration.py -v && \
  echo "[OK] Week 3 ready to resume!" || \
  echo "[ERROR] Factory fix incomplete - see integration test failures"
```

**Expected Output**: `[OK] Week 3 ready to resume!`

---

**Resume Checklist**:
- [ ] Factory bug fixed (FACTORY-001)
- [ ] Integration tests passing (5/5 controllers)
- [ ] Factory unit tests passing (no regressions)
- [ ] Coverage baseline measured
- [ ] Week 3 progress tracker updated
- [ ] Ready for Session 4!

**Status**: READY TO RESUME (after factory fix)
**Last Updated**: December 20, 2025, 9:00pm
