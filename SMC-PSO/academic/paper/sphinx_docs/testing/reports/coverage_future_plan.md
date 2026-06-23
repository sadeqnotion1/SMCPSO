# Future Optional Coverage Plan

**Status**: Not Started
**Last Updated**: November 16, 2025
**Total Estimated Effort**: ~35-45 hours, ~320 tests

---

## Overview

This document outlines the optional future coverage work to further improve test coverage across the `dip-smc-pso` project. These items are **not blockers** for the current release but represent high-impact modules that would benefit from comprehensive testing.

**Current Project Coverage** (after Phase 2.1-2.3): ~65-70%
**Potential Coverage** (after completing this plan): ~80-85%

---

## Priority 1: Simulation Infrastructure (~12-15 hours, ~150 tests)

**Goal**: Bring the entire integrator stack to ~80%+ coverage, building on the already-tested `error_control.py` and `base.py`.

**Impact**: HIGH - These modules are critical for numerical simulation accuracy and stability.

### Modules

- [ ] **`src/simulation/integrators/adaptive/runge_kutta.py`**
  - **Current Coverage**: ~25% (indirect tests only)
  - **Target Coverage**: ~90%+
  - **Estimated Tests**: ~25 tests
  - **Estimated Effort**: ~4 hours
  - **Focus Areas**:
    - Error estimation accuracy (embedded RK method)
    - Step acceptance/rejection logic
    - Suggested step size computation
    - Convergence order verification on test problems
    - Handling of stiff systems
    - Dormand-Prince coefficients validation
    - Function evaluation counting (should be 7 per step)
  - **Test File**: `tests/test_simulation/integrators/test_adaptive_runge_kutta.py`

- [ ] **`src/simulation/integrators/fixed_step/euler.py`**
  - **Current Coverage**: ~15%
  - **Target Coverage**: ~85%+
  - **Estimated Tests**: ~25 tests
  - **Estimated Effort**: ~4 hours
  - **Focus Areas**:
    - Order verification (global error ~ O(dt) for Forward Euler)
    - Stability analysis on stiff vs non-stiff problems
    - Implicit solver convergence (BackwardEuler)
    - Fallback behavior when implicit solver fails
    - Modified Euler (Heun's method) predictor-corrector accuracy
    - Function evaluation counts
    - Max iterations enforcement
  - **Test File**: `tests/test_simulation/integrators/test_fixed_step_euler.py`

- [ ] **`src/simulation/integrators/fixed_step/runge_kutta.py`**
  - **Current Coverage**: ~20%
  - **Target Coverage**: ~85%+
  - **Estimated Tests**: ~20 tests
  - **Estimated Effort**: ~3 hours
  - **Focus Areas**:
    - RK2 (midpoint method) accuracy and order verification
    - RK4 (classic 4th-order) accuracy and order verification
    - RK38 (3/8 rule) accuracy and comparison with RK4
    - Function evaluation counts (2, 4, 4 respectively)
    - Convergence rates on standard test problems
    - Comparison to analytical solutions
  - **Test File**: `tests/test_simulation/integrators/test_fixed_step_runge_kutta.py`

- [ ] **`src/simulation/integrators/factory.py`**
  - **Current Coverage**: 0%
  - **Target Coverage**: ~90%+
  - **Estimated Tests**: ~20 tests
  - **Estimated Effort**: ~3 hours
  - **Focus Areas**:
    - Integrator creation for all registered types (12 aliases)
    - Name normalization (lowercase, hyphens, spaces)
    - Custom integrator registration
    - Error handling for unknown types
    - Default integrator creation (should return RK4)
    - `get_integrator_info()` metadata retrieval
    - Inheritance validation (must extend BaseIntegrator)
    - dt attribute assignment
  - **Test File**: `tests/test_simulation/integrators/test_factory.py`

- [ ] **`src/simulation/integrators/discrete/zero_order_hold.py`**
  - **Current Coverage**: 0%
  - **Target Coverage**: ~85%+
  - **Estimated Tests**: ~20 tests
  - **Estimated Effort**: ~3 hours
  - **Focus Areas**:
    - Matrix exponential computation (compare to analytical)
    - Discrete-time matrices (Ad, Bd) correctness
    - Exactness for linear systems
    - Fallback to RK4 for nonlinear systems
    - Discrete sequence simulation (multi-step)
    - Consistency between continuous and discrete representations
    - Edge cases (singular A matrix, dt mismatch)
  - **Test File**: `tests/test_simulation/integrators/test_zero_order_hold.py`

- [ ] **`src/simulation/integrators/compatibility.py`**
  - **Current Coverage**: 0%
  - **Target Coverage**: ~80%+
  - **Estimated Tests**: ~25 tests
  - **Estimated Effort**: ~4 hours
  - **Focus Areas**:
    - DynamicsCompatibilityWrapper: interface adaptation, time tracking
    - LegacyDynamicsWrapper: finite difference estimation accuracy
    - IntegratorSafetyWrapper: fallback chain behavior
    - Non-finite detection and automatic fallback
    - Failure count tracking
    - Reset functionality
    - TypeError handling (integrators without 't' parameter)
    - Convenience functions (`create_compatible_dynamics`, etc.)
  - **Test File**: `tests/test_simulation/integrators/test_compatibility.py`

- [ ] **`src/simulation/context/simulation_context.py`**
  - **Current Coverage**: 0%
  - **Target Coverage**: ~75%+
  - **Estimated Tests**: ~15 tests
  - **Estimated Effort**: ~2 hours
  - **Focus Areas**:
    - Configuration loading from YAML
    - Dynamics model selection (simplified vs full)
    - Controller creation with validated gains
    - FDI system initialization (if enabled)
    - Lazy imports (no circular dependencies)
    - Error handling for missing config keys
    - Integration with `wrap_physics_config()`
  - **Test File**: `tests/test_simulation/context/test_simulation_context.py`

---

## Priority 2: Plant Dynamics (Full Model) (~8-10 hours, ~40 tests)

**Goal**: Validate the full nonlinear dynamics model to ensure research-grade accuracy.

**Impact**: MEDIUM-HIGH - Important for research accuracy, though simplified model is often sufficient for basic control testing.

### Modules

- [ ] **`src/plant/models/full/dynamics.py`**
  - **Current Coverage**: ~11.5%
  - **Target Coverage**: ~75%+
  - **Estimated Tests**: ~40 tests
  - **Estimated Effort**: ~8 hours
  - **Focus Areas**:
    - Full nonlinear dynamics computation
    - Consistency with simplified model on simple scenarios
    - Coriolis and centrifugal force terms
    - Gravity vector computation
    - Energy conservation properties
    - Stability properties at equilibrium
    - Singularity handling (θ ≈ π/2)
    - Linearization accuracy
    - Edge cases (extreme angles, high velocities)
    - Matrix conditioning
  - **Test File**: `tests/test_plant/models/full/test_full_dynamics_comprehensive.py`

---

## Priority 3: Analysis & Optimization (~15-20 hours, ~65 tests)

**Goal**: Validate core optimization and statistical analysis tools used for controller tuning and performance evaluation.

**Impact**: HIGH (PSO) / MEDIUM (Monte Carlo)

### Modules

- [ ] **`src/optimization/algorithms/pso_optimizer.py`**
  - **Current Coverage**: 0%
  - **Target Coverage**: ~75%+
  - **Estimated Tests**: ~35 tests
  - **Estimated Effort**: ~6 hours
  - **Focus Areas**:
    - Swarm initialization (uniform, random)
    - Particle position and velocity updates
    - Bounds handling and constraint enforcement
    - Convergence behavior on simple test functions
    - Deterministic behavior with fixed seed
    - Handling of bad objectives (NaN, Inf)
    - Best position tracking (personal and global)
    - Inertia weight decay
    - Cognitive and social parameters
    - Stopping criteria (max iterations, tolerance)
    - Cost function evaluation counting
  - **Test File**: `tests/test_optimization/algorithms/test_pso_optimizer.py`

- [ ] **`src/analysis/validation/monte_carlo.py`**
  - **Current Coverage**: 0%
  - **Target Coverage**: ~75%+
  - **Estimated Tests**: ~30 tests
  - **Estimated Effort**: ~5 hours
  - **Focus Areas**:
    - Sampling correctness (uniform, Gaussian)
    - Reproducibility with fixed seed
    - Basic statistical properties (mean, variance, distribution)
    - Handling of failure cases in simulations
    - Parallel vs sequential execution consistency
    - Result aggregation
    - Confidence interval computation
    - Sample size validation
    - Memory efficiency for large sample counts
  - **Test File**: `tests/test_analysis/validation/test_monte_carlo.py`

---

## Additional Lower-Priority Modules

These modules are identified as potentially beneficial but are lower priority than the above:

- `src/optimization/algorithms/robust_pso_optimizer.py` (~20 tests, ~3 hours)
- `src/analysis/validation/cross_validation.py` (~25 tests, ~4 hours)
- `src/analysis/validation/statistical_tests.py` (~30 tests, ~5 hours)
- `src/utils/fault_injection/fault_injector.py` (~15 tests, ~2 hours)
- `src/interfaces/hil/plant_server.py` (~20 tests, ~3 hours)
- `src/interfaces/hil/controller_client.py` (~20 tests, ~3 hours)

---

## How to Use This Plan

### Workflow for Each Module

1. **Check Baseline Coverage**
   ```bash
   python -m pytest tests/test_<module_area> --cov=src/<module_path> --cov-report=term-missing -q
   ```

2. **Design Tests**
   - Review the "Focus Areas" for the module
   - Identify edge cases and critical paths
   - Use shared fixtures from `conftest.py` where applicable
   - Aim for target coverage percentage

3. **Implement Tests**
   - Create test file at specified path
   - Write tests following existing patterns (see Phase 2.1-2.3 examples)
   - Use descriptive test names and docstrings
   - Validate both correctness and edge cases

4. **Run Tests and Verify**
   ```bash
   python -m pytest tests/test_<module_area>/test_<module>.py -v
   python -m pytest tests/test_<module_area>/test_<module>.py --cov=src/<module_path> --cov-report=term-missing
   ```

5. **Update This Checklist**
   - Mark checkbox as complete: `- [x]`
   - Document actual results:
     - Tests added: `X tests`
     - Final coverage: `Y%`
     - Any limitations or TODOs

### Progress Tracking

**Completed Modules**: 0 / 10
**Estimated Remaining Effort**: ~35-45 hours

### Notes

- **Dependencies**: Some modules may have shared fixtures or dependencies. Check `conftest.py` files in related test directories.
- **Parallel Work**: Items within the same priority can be worked on in parallel by different contributors.
- **Coverage Goals**: Target percentages are guidelines. Achieving 80%+ with good edge case coverage is more valuable than 100% with only happy-path tests.
- **Test Quality**: Focus on:
  - Edge cases (NaN, Inf, zero values, boundary conditions)
  - Numerical accuracy (compare to analytical solutions where possible)
  - Deterministic behavior (seed-based reproducibility)
  - Error handling and validation

---

## References

- **Completed Work**: See Phase 2.1, 2.2, 2.3 test files for examples
- **Test Fixtures**: `tests/test_simulation/integrators/conftest.py` (analytical test problems)
- **Coverage Standards**: `.ai/config/testing_standards.md`
- **Project Status**: See overall project status summary in session notes

---

**Document Status**: ACTIVE (ready for implementation)
**Next Review Date**: When first module is completed
