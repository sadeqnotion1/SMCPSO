# Testing Workflows & Best Practices **DIP-SMC-PSO Project**

**Last Updated**: 2025-10-04
**Status**: Production-Grade Testing Workflows

---

## Table of Contents 1. [Development Workflows](#1-development-workflows)

2. [CI/CD Integration](#2-cicd-integration)
3. [Test Execution Patterns](#3-test-execution-patterns)
4. [Quality Assurance](#4-quality-assurance)

---

## 1. Development Workflows ### 1.1 Test-Driven Development (TDD) #### 1.1.1 Red-Green-Refactor Cycle **Workflow**: Write failing test → Implement code → Refactor → Repeat ```python

# example-metadata:

# runnable: false # Step 1: RED - Write failing test

# tests/test_controllers/smc/algorithms/classical/test_new_feature.py def test_chattering_reduction_effectiveness(): """Test that chattering reduction algorithm reduces control rate.""" controller = ClassicalSMC( gains=[10, 8, 15, 12, 50, 5], max_force=100, boundary_layer=0.01, chattering_reduction=True # New feature ) state = np.array([0.1, 0.05, 0.08, 0.02, 0.03, 0.01]) control_history = [] for _ in range(100): result = controller.compute_control(state, {}, {}) control = result['control'] control_history.append(control) # Calculate control rate control_rate = np.std(np.diff(control_history)) # Should be significantly lower than baseline assert control_rate < 5.0, f"Chattering reduction ineffective: rate={control_rate}" # Run test → FAILS (feature not implemented)

# pytest tests/test_controllers/smc/algorithms/classical/test_new_feature.py -v

``` ```python
# example-metadata:
# runnable: false # Step 2: GREEN - Implement minimal code to pass
# src/controllers/smc/classic_smc.py class ClassicalSMC: def __init__(self, gains, max_force, boundary_layer=0.01, chattering_reduction=False): self.gains = gains self.max_force = max_force self.boundary_layer = boundary_layer self.chattering_reduction = chattering_reduction self.last_control = 0.0 def compute_control(self, state, state_vars, history): # ... existing SMC logic ... control = u_eq + u_switch + u_derivative if self.chattering_reduction: # Simple low-pass filter alpha = 0.8 control = alpha * self.last_control + (1 - alpha) * control self.last_control = control # Saturation control = np.clip(control, -self.max_force, self.max_force) return {'control': control} # Run test → PASSES
``` ```python
# example-metadata:

# runnable: false # Step 3: REFACTOR - Clean up implementation

class ChatteringReduction: """Encapsulate chattering reduction logic.""" def __init__(self, alpha=0.8): self.alpha = alpha self.last_control = 0.0 def apply(self, control): """Apply low-pass filter to control signal.""" filtered = self.alpha * self.last_control + (1 - self.alpha) * control self.last_control = filtered return filtered class ClassicalSMC: def __init__(self, gains, max_force, boundary_layer=0.01, chattering_reduction=False): self.gains = gains self.max_force = max_force self.boundary_layer = boundary_layer if chattering_reduction: self.chattering_filter = ChatteringReduction() else: self.chattering_filter = None def compute_control(self, state, state_vars, history): # ... existing SMC logic ... control = u_eq + u_switch + u_derivative if self.chattering_filter: control = self.chattering_filter.apply(control) control = np.clip(control, -self.max_force, self.max_force) return {'control': control} # Run test → STILL PASSES
# Run full test suite → ALL PASS

``` #### 1.1.2 Test-First Controller Development **Scenario**: Implementing a new Adaptive Super-Twisting SMC controller ```python
# example-metadata:
# runnable: false # Step 1: Write interface tests FIRST
# tests/test_controllers/smc/algorithms/adaptive_sta/test_adaptive_sta_interface.py class TestAdaptiveSTAInterface: """Test interface compliance for Adaptive STA SMC.""" def test_implements_controller_protocol(self): """Test controller implements required protocol.""" from src.controllers.interfaces import ControllerProtocol controller = AdaptiveSTASMC( gains=[20, 15, 12, 10], max_force=100, adaptation_rate=0.5 ) assert isinstance(controller, ControllerProtocol) assert hasattr(controller, 'compute_control') assert callable(controller.compute_control) def test_compute_control_signature(self): """Test compute_control has correct signature.""" controller = AdaptiveSTASMC(gains=[20,15,12,10], max_force=100) state = np.zeros(6) result = controller.compute_control(state, {}, {}) assert isinstance(result, dict) assert 'control' in result assert isinstance(result['control'], (int, float, np.ndarray)) # Step 2: Write functionality tests
class TestAdaptiveSTAFunctionality: """Test Adaptive STA SMC core functionality.""" def test_adaptation_increases_gains_under_uncertainty(self): """Test adaptive mechanism increases gains when needed.""" controller = AdaptiveSTASMC( gains=[20, 15, 12, 10], max_force=100, adaptation_rate=0.5 ) # High uncertainty scenario uncertain_state = np.array([0.5, 0.3, 0.2, 0.1, 0.05, 0.02]) initial_gains = controller.get_current_gains().copy() # Run adaptation for _ in range(50): controller.compute_control(uncertain_state, {}, {}) adapted_gains = controller.get_current_gains() assert np.any(adapted_gains > initial_gains), "Gains should adapt upward" # Step 3: Implement controller to pass tests
# src/controllers/smc/algorithms/adaptive_sta/adaptive_sta_smc.py class AdaptiveSTASMC: """Adaptive Super-Twisting Sliding Mode Controller.""" def __init__(self, gains, max_force, adaptation_rate=0.5): self.initial_gains = np.array(gains) self.current_gains = self.initial_gains.copy() self.max_force = max_force self.adaptation_rate = adaptation_rate def compute_control(self, state, state_vars, history): # ... Super-twisting control logic ... # ... Adaptive gain update ... return {'control': control} def get_current_gains(self): return self.current_gains.copy()
``` ### 1.2 Incremental Testing Strategy **Principle**: Build complex tests from simple foundations ```python
# Level 1: Component-level tests

def test_sliding_surface_computation(): """Test individual sliding surface computation.""" from src.controllers.smc.core.sliding_surface import LinearSlidingSurface surface = LinearSlidingSurface(gains=[5, 3, 4, 2]) state = np.array([0.1, 0.1, 0.1, 0.05, 0.05, 0.05]) s = surface.compute(state) assert isinstance(s, float) assert np.isfinite(s) # Level 2: Component integration tests
def test_sliding_surface_with_controller(): """Test sliding surface integrated with controller.""" from src.controllers.smc.classic_smc import ClassicalSMC controller = ClassicalSMC(gains=[10,8,15,12,50,5], max_force=100) state = np.array([0.1, 0.1, 0.1, 0.05, 0.05, 0.05]) result = controller.compute_control(state, {}, {}) assert 'control' in result assert np.isfinite(result['control']) # Level 3: System-level integration tests
def test_controller_with_dynamics(): """Test controller integrated with dynamics.""" from src.controllers.smc.classic_smc import ClassicalSMC from src.core.dynamics import SimplifiedDynamics controller = ClassicalSMC(gains=[10,8,15,12,50,5], max_force=100) dynamics = SimplifiedDynamics({'M': 1.0, 'm1': 0.1, 'm2': 0.1, 'L1': 0.5, 'L2': 0.5, 'g': 9.81}) state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0]) for _ in range(100): result = controller.compute_control(state, {}, {}) u = result['control'] x_dot = dynamics.dynamics(state, u) state = state + 0.01 * x_dot assert np.linalg.norm(state) < 0.5 # Partial stabilization # Level 4: End-to-end workflow tests
def test_complete_simulation_workflow(): """Test complete simulation from initialization to results.""" from src.core.simulation_runner import run_simulation controller = ClassicalSMC(gains=[10,8,15,12,50,5], max_force=100) result = run_simulation( controller=controller, duration=5.0, dt=0.01, initial_state=[0.0, 0.1, 0.1, 0.0, 0.0, 0.0] ) assert 'time' in result assert 'states' in result assert len(result['time']) == len(result['states']) assert np.linalg.norm(result['states'][-1]) < 0.05 # Full stabilization
``` ### 1.3 Debugging Workflow **Strategy**: Systematic diagnosis using test isolation ```bash
# 1. Run specific failing test with maximum verbosity
pytest tests/test_controllers/smc/algorithms/classical/test_classical_smc.py::TestClassicalSMC::test_compute_control_valid_output -vv --tb=long # 2. Show local variables on failure
pytest tests/test_controllers/smc/algorithms/classical/test_classical_smc.py::TestClassicalSMC::test_compute_control_valid_output -l # 3. Drop into debugger on failure
pytest tests/test_controllers/smc/algorithms/classical/test_classical_smc.py::TestClassicalSMC::test_compute_control_valid_output --pdb # 4. Add print statements (captured by pytest)
pytest tests/test_controllers/smc/algorithms/classical/test_classical_smc.py::TestClassicalSMC::test_compute_control_valid_output -s # 5. Isolate test in Python REPL
python -i tests/test_controllers/smc/algorithms/classical/test_classical_smc.py # 6. Use hypothesis to find minimal failing case
# tests/test_property_based_debug.py
from hypothesis import given, strategies as st, reproduce_failure @given(state=st.lists(st.floats(min_value=-10, max_value=10), min_size=6, max_size=6))
def test_controller_never_nan(state): controller = ClassicalSMC(gains=[10,8,15,12,50,5], max_force=100) result = controller.compute_control(np.array(state), {}, {}) assert np.isfinite(result['control']) # If test fails, Hypothesis prints:
# @reproduce_failure('6.82.0', b'AAAA...') to reproduce
```

---

## 2. CI/CD Integration ### 2.1 GitHub Actions Workflow ```yaml

# .github/workflows/test.yml name: Test Suite

on: push: branches: [main, develop] pull_request: branches: [main] jobs: test: runs-on: ${{ matrix.os }} strategy: fail-fast: false matrix: os: [ubuntu-latest, windows-latest, macos-latest] python-version: ['3.9', '3.10', '3.11'] steps: - uses: actions/checkout@v3 - name: Set up Python ${{ matrix.python-version }} uses: actions/setup-python@v4 with: python-version: ${{ matrix.python-version }} - name: Cache dependencies uses: actions/cache@v3 with: path: ~/.cache/pip key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }} - name: Install dependencies run: | python -m pip install --upgrade pip pip install -r requirements.txt pip install pytest pytest-cov pytest-xdist pytest-benchmark - name: Run config validation (fast fail) run: python validate_config.py - name: Run smoke tests run: pytest tests/config_validation/ tests/test_config/ -v - name: Run unit tests run: pytest tests/ -k "not integration and not slow" -n auto --cov=src --cov-report=xml - name: Run integration tests run: pytest tests/integration/ -v - name: Upload coverage to Codecov uses: codecov/codecov-action@v3 with: file: ./coverage.xml flags: unittests name: codecov-${{ matrix.os }}-py${{ matrix.python-version }} - name: Run benchmarks if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.10' run: pytest tests/test_benchmarks/ --benchmark-only --benchmark-save=ci_baseline - name: Store benchmark results if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.10' uses: actions/upload-artifact@v3 with: name: benchmark-results path: .benchmarks/
``` ### 2.2 Pre-commit Hooks ```bash
# .git/hooks/pre-commit
#!/bin/bash
# Pre-commit hook for quality gates set -e echo "Running pre-commit checks..." # 1. Configuration validation (fast fail)
echo "→ Validating configuration..."
python validate_config.py
if [ $? -ne 0 ]; then echo "❌ Configuration validation failed" exit 1
fi # 2. Fast unit tests
echo "→ Running fast unit tests..."
pytest tests/ -k "not integration and not slow" -q --tb=no
if [ $? -ne 0 ]; then echo "❌ Unit tests failed" exit 1
fi # 3. Mathematical property tests (critical)
echo "→ Running mathematical validation..."
pytest tests/validation/ -k "property" -q --tb=no
if [ $? -ne 0 ]; then echo "❌ Mathematical property tests failed" exit 1
fi # 4. Code formatting check (optional)
if command -v black &> /dev/null; then echo "→ Checking code formatting..." black --check src/ tests/ --quiet if [ $? -ne 0 ]; then echo "⚠️ Code formatting issues detected (run 'black src/ tests/')" # Don't fail commit, just warn fi
fi echo "✅ All pre-commit checks passed"
exit 0
``` ### 2.3 Automated Test Execution Strategy ```yaml
# pytest.ini

[pytest]
markers = smoke: Fast smoke tests (< 5 seconds total) unit: Unit tests (< 1 second each) integration: Integration tests (1-10 seconds each) slow: Slow tests (> 10 seconds) critical: Safety-critical tests (100% coverage required) # CI execution stages
# Stage 1: Smoke tests (30 seconds)

addopts = -m smoke --maxfail=1 --tb=short [pytest:stage_unit]
# Stage 2: Unit tests (5 minutes)

addopts = -m "unit and not slow" -n auto --maxfail=5 [pytest:stage_integration]
# Stage 3: Integration tests (10 minutes)

addopts = -m integration -v --maxfail=3 [pytest:stage_full]
# Stage 4: Full suite (30 minutes)

addopts = -v --cov=src --cov-report=html --cov-fail-under=85
``` ### 2.4 Coverage Enforcement ```bash
# Coverage requirements in CI
pytest tests/ --cov=src --cov-report=term --cov-fail-under=85 # Component-specific coverage
pytest tests/test_controllers/ --cov=src.controllers --cov-fail-under=95
pytest tests/test_utils/test_control/ --cov=src.utils.control --cov-fail-under=100 # Safety-critical # Coverage diff (only new code)
diff-cover coverage.xml --compare-branch=main --fail-under=90
```

---

## 3. Test Execution Patterns ### 3.1 Local Development Testing #### 3.1.1 Fast Feedback Loop ```bash

# Quick test while developing

pytest tests/test_controllers/smc/algorithms/classical/ -k "test_compute_control" --tb=short # Watch mode (requires pytest-watch)
ptw tests/test_controllers/smc/algorithms/classical/ -- -k "test_compute_control" # Parallel execution for speed
pytest tests/ -n auto -k "not slow" # Only run tests that failed last time
pytest --lf # Run failed tests first, then rest
pytest --ff
``` #### 3.1.2 Validation Before Merge ```bash
# Full validation checklist
#!/bin/bash echo "Running validation..." # 1. All unit tests
pytest tests/ -k "not integration and not slow" -n auto # 2. All integration tests
pytest tests/integration/ -v # 3. Coverage check
pytest tests/ --cov=src --cov-report=html --cov-fail-under=85 # 4. Benchmarks (regression detection)
pytest tests/test_benchmarks/ --benchmark-only --benchmark-compare --benchmark-compare-fail=mean:5% # 5. Property-based tests (thorough)
pytest tests/ -k "property" --hypothesis-profile=thorough # 6. Code quality (if tools available)
if command -v pylint &> /dev/null; then pylint src/controllers/ src/core/
fi echo "Validation complete!"
``` ### 3.2 Selective Test Execution ```bash
# By marker

pytest -m unit # Unit tests only
pytest -m "integration" # Integration tests only
pytest -m "not slow" # Exclude slow tests
pytest -m "critical" # Safety-critical tests only # By keyword
pytest -k "classical" # Tests with "classical" in name
pytest -k "smc or adaptive" # Tests matching either keyword
pytest -k "not property" # Exclude property-based tests # By module
pytest tests/test_controllers/ # All controller tests
pytest tests/test_controllers/smc/algorithms/ # SMC algorithm tests # By specific test
pytest tests/test_controllers/smc/algorithms/classical/test_classical_smc.py::TestClassicalSMC::test_compute_control_valid_output
``` ### 3.3 Parallel Execution Strategies ```bash
# Auto-detect CPU cores
pytest tests/ -n auto # Specific number of workers
pytest tests/ -n 4 # Distribute by module (better for integration tests)
pytest tests/ -n auto --dist=loadfile # Distribute by test (better for many small tests)
pytest tests/ -n auto --dist=loadscope # Parallel with coverage (requires pytest-cov plugin)
pytest tests/ -n auto --cov=src --cov-report=html
```

---

## 4. Quality Assurance ### 4.1 Coverage Analysis #### 4.1.1 Identifying Coverage Gaps ```bash

# Generate detailed HTML coverage report

pytest tests/ --cov=src --cov-report=html # Open coverage_html_report/index.html
# Navigate to src/controllers/smc/classic_smc.py

# Red lines = not covered

# Green lines = covered # Terminal report with missing lines

pytest tests/ --cov=src --cov-report=term-missing # Example output:
# Name Stmts Miss Cover Missing

# ----------------------------------------------------------------

# src/controllers/smc/classic_smc.py 245 12 95% 89-92, 134, 201-205 # Focus on specific module

pytest tests/test_controllers/ --cov=src.controllers.smc.classic_smc --cov-report=term-missing
``` #### 4.1.2 Closing Coverage Gaps ```python
# example-metadata:
# runnable: false # Identify uncovered code
# src/controllers/smc/classic_smc.py:89-92 not covered # Lines 89-92: Error handling for invalid state
if np.any(np.isnan(state)): raise ValueError("State contains NaN values")
if np.any(np.isinf(state)): raise ValueError("State contains infinite values") # Write test to cover this code
def test_nan_state_rejection(): """Test that NaN states are rejected.""" controller = ClassicalSMC(gains=[10,8,15,12,50,5], max_force=100) nan_state = np.array([0.1, np.nan, 0.08, 0.02, 0.03, 0.01]) with pytest.raises(ValueError, match="NaN values"): controller.compute_control(nan_state, {}, {}) def test_inf_state_rejection(): """Test that infinite states are rejected.""" controller = ClassicalSMC(gains=[10,8,15,12,50,5], max_force=100) inf_state = np.array([0.1, np.inf, 0.08, 0.02, 0.03, 0.01]) with pytest.raises(ValueError, match="infinite values"): controller.compute_control(inf_state, {}, {}) # Run coverage again → Lines 89-92 now covered
``` ### 4.2 Mutation Testing ```python
# example-metadata:

# runnable: false # Install mutpy

pip install mutpy # Run mutation testing
mut.py --target src.controllers.smc.classic_smc --unit-test tests.test_controllers.smc.algorithms.classical.test_classical_smc --report-html mutation_report.html # Example mutation: Change + to -
# Original: control = u_eq + u_switch

# Mutant: control = u_eq - u_switch # If tests still pass → weak test suite

# If tests fail → strong test suite (mutation killed) # Target: >80% mutation score

``` ### 4.3 Code Review Checklists #### 4.3.1 Test Code Review Checklist - [ ] **Test Coverage**: Does the test cover the new functionality?
- [ ] **Edge Cases**: Are boundary conditions tested?
- [ ] **Error Paths**: Are exception paths tested?
- [ ] **Test Independence**: Can test run in isolation?
- [ ] **Determinism**: Does test produce consistent results?
- [ ] **Clarity**: Is test purpose clear from name and docstring?
- [ ] **Performance**: Does test run in reasonable time (<1s for unit tests)?
- [ ] **Assertions**: Are assertions specific and informative?
- [ ] **Setup/Teardown**: Is test cleanup handled properly?
- [ ] **Parametrization**: Could test benefit from parametrization? #### 4.3.2 Implementation Code Review Checklist (Testing Focus) - [ ] **Testability**: Is code easy to test in isolation?
- [ ] **Dependencies**: Are dependencies injected for mocking?
- [ ] **Side Effects**: Are side effects minimized and documented?
- [ ] **Error Handling**: Are all error paths testable?
- [ ] **Observability**: Can internal state be inspected for testing?
- [ ] **Complexity**: Is code simple enough to test thoroughly?
- [ ] **Documentation**: Do docstrings include testing examples? ### 4.4 Test Quality Metrics ```python
# example-metadata:
# runnable: false # Metric 1: Test-to-Code Ratio
test_loc = count_lines_of_code('tests/')
src_loc = count_lines_of_code('src/')
ratio = test_loc / src_loc # Target: 1.5-2.0 (150-200% test code)
assert ratio >= 1.5, f"Insufficient test coverage: ratio={ratio:.2f}" # Metric 2: Average Test Execution Time
total_time = pytest_duration
test_count = pytest_test_count
avg_time = total_time / test_count # Target: <100ms per test
assert avg_time < 0.1, f"Tests too slow: avg={avg_time*1000:.0f}ms" # Metric 3: Test Flakiness
flaky_tests = count_flaky_tests() # Tests that intermittently fail
total_tests = count_total_tests()
flakiness_rate = flaky_tests / total_tests # Target: <1% flakiness
assert flakiness_rate < 0.01, f"Too many flaky tests: {flakiness_rate*100:.1f}%"
``` ### 4.5 Continuous Improvement Practices #### 4.5.1 Regular Test Audits ```bash
# Monthly test audit checklist # 1. Remove obsolete tests

git log --all --oneline --grep="Remove.*test" --since="1 month ago" # 2. Update flaky tests
pytest --lf --tb=short # Review last failed tests # 3. Refactor duplicated test code
pytest --collect-only | grep "test_" | sort | uniq -d # 4. Update test documentation
find tests/ -name "*.py" -exec grep -L "\"\"\"" {} \; # Tests without docstrings # 5. Performance regression check
pytest tests/test_benchmarks/ --benchmark-only --benchmark-compare=baseline --benchmark-compare-fail=mean:10%
``` #### 4.5.2 Test Retrospectives After each major feature or bug fix, conduct a test retrospective: 1. **What tests caught the bug early?** → Reinforce that pattern
2. **What tests missed the bug?** → Add regression tests
3. **What tests are slow/flaky?** → Refactor or remove
4. **What new test patterns emerged?** → Document and share

---

## Summary Effective testing workflows combine: 1. **Development Practices**: TDD, incremental testing, systematic debugging
2. **Automation**: CI/CD integration, pre-commit hooks, automated quality gates
3. **Execution Strategy**: Fast feedback loops, parallel execution, selective testing
4. **Quality Focus**: Coverage analysis, mutation testing, code reviews, continuous improvement **Key Metrics:**
- Test execution time: <100ms per unit test
- Coverage: ≥85% overall, ≥95% critical, 100% safety-critical
- Test-to-code ratio: 1.5-2.0
- Flakiness rate: <1%
- Mutation score: >80% **Best Practices:**
- Write tests before implementation (TDD)
- Keep tests fast, isolated, and deterministic
- Use CI/CD for continuous validation
- Review and refactor tests regularly
- Document testing patterns and decisions

---

## References 1. Beck, K. (2003). *Test-Driven Development: By Example*. Addison-Wesley.
2. Feathers, M. (2004). *Working Effectively with Legacy Code*. Prentice Hall.
3. Martin, R. C. (2008). *Clean Code: A Handbook of Agile Software Craftsmanship*. Prentice Hall.
4. pytest Documentation: https://docs.pytest.org/
5. Hypothesis Documentation: https://hypothesis.readthedocs.io/

---

**End of Week 5 Testing Documentation** **Previous**: [Validation Methodology Guide](validation_methodology_guide.md)
**See Also**: [Testing Framework Technical Guide](testing_framework_technical_guide.md), [Benchmarking Framework Technical Guide](benchmarking_framework_technical_guide.md)