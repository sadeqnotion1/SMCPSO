# Week 3-5: Coverage Improvement Plan
## src/ Directory Reorganization - Phase 3 (30-50 hours)

**Date**: December 20, 2025
**Prerequisites**: Weeks 1-2 complete, validation passed, test errors reduced 31→5

---

## Executive Summary

**Goal**: Improve test coverage from 10.4% to 90% overall
**Scope**: Factory (0%→90%), Utils critical modules, SMC algorithms (27%→90%), Visualization
**Estimated Effort**: 30-50 hours
**New Tests**: ~1,500 tests across 4 domains

---

## Phase Breakdown

### Week 3: Factory & Utils Critical (12-18h)

**Factory Testing** (0% → 90%, ~480 tests):
- `base.py` (928 lines): Controller creation, thread-safety, PSO integration
  - Test create_controller() with all 6 controller types
  - Test with_factory_lock() concurrency (100+ threads)
  - Test PSOControllerWrapper parameter passing
  - Test error handling (invalid types, missing params)
  - **Estimated**: 200 tests, 6-8 hours

- `registry.py` (330 lines): Controller metadata and lookups
  - Test CONTROLLER_REGISTRY completeness
  - Test canonicalize_controller_type() aliases
  - Test get_default_gains() for all types
  - Test get_controllers_by_category/complexity()
  - **Estimated**: 80 tests, 2-3 hours

- `validation.py` (577 lines): Comprehensive validation framework
  - Test validate_controller_gains() boundary cases
  - Test validate_configuration() with invalid configs
  - Test validate_state_vector() dimensions
  - Test ValidationResult error aggregation
  - **Estimated**: 120 tests, 3-4 hours

- `pso_utils.py`: PSO optimization utilities
  - Test create_optimized_controller_factory()
  - Test gain bounds extraction
  - Test PSO-specific parameter handling
  - **Estimated**: 80 tests, 2-3 hours

**Utils Critical Modules** (varies → 95%):
- `numerical_stability/` (CRITICAL - safety functions):
  - Test safe_divide(), safe_log(), safe_sqrt()
  - Test overflow/underflow prevention
  - Test NaN/Inf handling
  - **Estimated**: 60 tests, 2-3 hours

- `infrastructure/logging/` (operational monitoring):
  - Test log path management
  - Test rotation and cleanup
  - Test performance impact
  - **Estimated**: 40 tests, 1-2 hours

- `infrastructure/memory/` (leak prevention):
  - Test memory tracking
  - Test cleanup workflows
  - Test threshold alerts
  - **Estimated**: 30 tests, 1 hour

**Week 3 Total**: 590 tests, 12-18 hours

---

### Week 4: SMC Algorithms & Monitoring (10-16h)

**SMC Controllers** (27% → 90%, ~170 tests):
- `classical_smc.py`:
  - Test gain parameter variations
  - Test saturation edge cases
  - Test chattering metrics
  - Test boundary layer optimization
  - **Estimated**: 50 tests, 3-4 hours

- `sta_smc.py`:
  - Test super-twisting algorithm correctness
  - Test convergence rates
  - Test disturbance rejection
  - Test parameter sensitivity
  - **Estimated**: 40 tests, 2-3 hours

- `adaptive_smc.py`:
  - Test adaptation law behavior
  - Test uncertainty estimation
  - Test adaptive gain dynamics
  - Test stability under parameter drift
  - **Estimated**: 40 tests, 2-3 hours

- `hybrid_adaptive_sta_smc.py`:
  - Test mode switching logic
  - Test combined adaptation + super-twisting
  - Test performance vs individual controllers
  - **Estimated**: 40 tests, 2-3 hours

**Monitoring Systems**:
- `monitoring/realtime/`:
  - Test LatencyMonitor deadline tracking
  - Test StabilityMonitoringSystem diagnostics
  - Test metric collection accuracy
  - **Estimated**: 50 tests, 2-3 hours

**Week 4 Total**: 220 tests, 10-16 hours

---

### Week 5: Visualization, Analysis & Edge Cases (8-16h)

**Visualization** (→ 85%):
- `visualization/legacy_visualizer.py`:
  - Test plot generation (static + animated)
  - Test DIPAnimator frame rendering
  - Test figure management
  - **Estimated**: 60 tests, 3-4 hours

- `visualization/plotting/`:
  - Test performance plots
  - Test comparison visualizations
  - Test export functionality
  - **Estimated**: 40 tests, 2 hours

**Analysis Utilities**:
- `analysis/statistical/`:
  - Test confidence intervals
  - Test bootstrap methods
  - Test statistical comparisons (t-test, ANOVA)
  - **Estimated**: 50 tests, 2-3 hours

**Testing Utilities**:
- `testing/dev_tools/`:
  - Test debugging helpers
  - Test profiling utilities
  - **Estimated**: 30 tests, 1-2 hours

- `testing/fault_injection/`:
  - Test fault injection mechanisms
  - Test robustness testing workflows
  - **Estimated**: 40 tests, 2 hours

**Edge Cases & Integration**:
- Cross-module integration tests
- Performance regression tests
- Memory leak detection tests
- **Estimated**: 80 tests, 2-3 hours

**Week 5 Total**: 300 tests, 8-16 hours

---

## Total Plan Summary

| Week | Focus | Tests | Hours | Cumulative Coverage |
|------|-------|-------|-------|-------------------|
| 3 | Factory + Utils Critical | 590 | 12-18 | 10.4% → 45% |
| 4 | SMC Algorithms + Monitoring | 220 | 10-16 | 45% → 70% |
| 5 | Viz + Analysis + Edge Cases | 300 | 8-16 | 70% → 90% |
| **TOTAL** | **All Domains** | **1,110** | **30-50** | **10.4% → 90%** |

---

## Testing Strategy

### Test Structure Pattern
```python
# tests/test_MODULE/test_FEATURE.py

class TestFeatureBasicOperation:
    """Test core functionality."""
    def test_normal_case(self):
        # Happy path

    def test_boundary_values(self):
        # Edge cases at limits

class TestFeatureErrorHandling:
    """Test error cases."""
    def test_invalid_input_raises(self):
        # Type errors, value errors

    def test_error_messages_descriptive(self):
        # Error message quality

class TestFeaturePerformance:
    """Test performance characteristics."""
    @pytest.mark.benchmark
    def test_performance_baseline(self, benchmark):
        # Performance regression tests
```

### Coverage Targets by Module

**Safety-Critical** (100% required):
- `numerical_stability/` (safe operations)
- `controllers/smc/` (control algorithms)
- Factory validation (parameter checking)

**Mission-Critical** (95% target):
- Factory core (create_controller, registry)
- Monitoring systems (latency, stability)
- Configuration loading

**Operational** (85% target):
- Visualization (plotting, animation)
- Analysis utilities (statistics)
- Testing utilities (dev tools)

**Nice-to-Have** (70% target):
- Legacy compatibility layers
- Experimental features
- Debug utilities

---

## Implementation Approach

### Phase 1: Automated Test Generation (Hours 1-3)
- Use pytest-benchmark for performance baselines
- Use Hypothesis for property-based tests
- Generate parametrized tests for controllers

### Phase 2: Manual Critical Tests (Hours 4-15)
- Factory thread-safety (complex scenarios)
- SMC algorithm correctness (Lyapunov validation)
- Monitoring system integration

### Phase 3: Edge Cases & Integration (Hours 16-25)
- Cross-module integration
- Performance regression detection
- Memory leak prevention

### Phase 4: Documentation & Validation (Hours 26-30)
- Update test documentation
- Generate coverage reports
- Validate all quality gates

---

## Success Criteria

**Coverage Metrics**:
- [x] Overall: ≥90% (current: 10.4%)
- [ ] Factory: ≥90% (current: 0%)
- [ ] SMC Controllers: ≥90% (current: 27%)
- [ ] Utils Critical: ≥95% (current: varies)
- [ ] Safety-Critical: 100% (numerical_stability)

**Quality Gates**:
- [ ] 7/8 quality gates passing (current: 1/8)
- [ ] All safety-critical modules 100% coverage
- [ ] No regressions in existing tests
- [ ] <5 minutes total test execution time

**Test Count**:
- [ ] +1,110 new tests (current: 3,887 → target: 4,997)
- [ ] 0 collection errors (current: 5 → target: 0)
- [ ] All tests passing or skipped with clear reason

---

## Risk Mitigation

**Risk 1: Time Overrun**
- **Mitigation**: Prioritize safety-critical modules first
- **Fallback**: Accept 80% coverage, document gaps

**Risk 2: Test Complexity**
- **Mitigation**: Use property-based testing (Hypothesis)
- **Fallback**: Focus on happy path + error cases

**Risk 3: Performance Impact**
- **Mitigation**: Use pytest markers (@slow, @integration)
- **Fallback**: Separate fast/slow test suites

**Risk 4: Maintenance Burden**
- **Mitigation**: Follow DRY principles, use fixtures
- **Fallback**: Document test rationale for future refactoring

---

## Tools & Frameworks

**Testing**:
- pytest (core framework)
- pytest-cov (coverage measurement)
- pytest-benchmark (performance)
- Hypothesis (property-based)
- pytest-xdist (parallel execution)

**Analysis**:
- coverage.py (detailed reports)
- diff-cover (coverage diff tracking)
- pytest-html (test reports)

**CI/CD Integration**:
- Coverage thresholds in pytest.ini
- Automated quality gate checks
- Pre-commit hooks for test validation

---

## Next Steps (Immediate)

1. **Run baseline coverage analysis** (in progress)
2. **Start Week 3 - Factory testing** (base.py first)
3. **Generate parametrized controller tests** (all 6 types)
4. **Implement thread-safety stress tests** (100+ threads)
5. **Validate numerical_stability module** (100% target)

---

## Deliverables

**Week 3**:
- 590 new factory + utils tests
- Factory coverage 0% → 90%
- Utils critical 95%+ coverage
- Intermediate coverage report

**Week 4**:
- 220 new SMC + monitoring tests
- SMC coverage 27% → 90%
- Monitoring systems validated
- Performance benchmarks established

**Week 5**:
- 300 new viz + analysis tests
- Overall coverage 90%+
- 7/8 quality gates passing
- Final coverage report + summary

**Final Artifacts**:
- Comprehensive test suite (4,997 tests)
- Coverage report (HTML + JSON)
- Performance benchmark baseline
- Test documentation updates

---

**Document Version**: 1.0
**Last Updated**: December 20, 2025
**Status**: Ready to Execute
**Estimated Completion**: January 10, 2026 (3 weeks @ 10-17h/week)
