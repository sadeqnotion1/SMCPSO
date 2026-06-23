#==========================================================================================\\\
#============================= docs/test_execution_guide.md ===============================\\\
#==========================================================================================\\\

# Test Execution Guide
## Double-Inverted Pendulum SMC-PSO Project **Guide Version**: 1.0

**Last Updated**: 2025-09-28
**Target Audience**: Developers, CI/CD Engineers, Research Scientists

---

## Quick Start Test Commands ### Essential Test Runs ```bash

# Quick development testing (unit tests only)

pytest -m "unit" -v # Fast integration testing (no slow tests)
pytest -m "not slow" -v # Complete test suite with coverage
pytest --cov=src --cov-report=html --cov-report=term # Scientific validation (convergence, stability, robustness)
pytest -m "convergence or numerical_stability or numerical_robustness" -v
``` ### Pre-Commit Validation ```bash
# Recommended pre-commit test sequence
pytest -m "unit" --tb=short # Fast feedback
pytest -m "integration and not slow" -v # Core integration
pytest --cov=src --cov-fail-under=85 # Coverage check
```

---

## Test Categories and Execution ### 1. Unit Tests - Individual Component Validation **Purpose**: Validate isolated functions and class methods

**Execution Time**: <30 seconds
**Coverage Target**: >95% for critical components ```bash
# Run all unit tests

pytest -m "unit" -v # Unit tests with coverage report
pytest -m "unit" --cov=src/controllers --cov-report=term-missing # Specific component unit tests
pytest tests/test_controllers/test_classical_smc.py::test_compute_control -v
``` **Example Unit Test Output**:
```

tests/test_controllers/test_classical_smc.py::test_compute_control PASSED
tests/test_controllers/test_classical_smc.py::test_sliding_surface PASSED
tests/test_controllers/test_classical_smc.py::test_parameter_validation PASSED
========================== 3 passed in 0.12s ==========================
``` ### 2. Integration Tests - Multi-Component Validation **Purpose**: Test component interactions and system workflows
**Execution Time**: 2-5 minutes
**Coverage Target**: End-to-end workflow validation ```bash
# All integration tests
pytest -m "integration" -v # Integration without slow tests
pytest -m "integration and not slow" -v # Specific integration scenarios
pytest -m "integration" -k "pso" -v # PSO integration
pytest -m "integration" -k "controller" -v # Controller integration
pytest -m "integration" -k "simulation" -v # Simulation integration
``` **Example Integration Test Output**:

```
tests/test_integration/test_pso_controller.py::test_optimization_workflow PASSED
tests/test_integration/test_simulation_runner.py::test_complete_simulation PASSED
========================== 2 passed in 3.45s ==========================
``` ### 3. Scientific Validation Tests #### Convergence Analysis Tests ```bash
# Test algorithm convergence properties

pytest -m "convergence" -v # PSO convergence validation
pytest -m "convergence" -k "pso" -v # SMC sliding surface reachability
pytest -m "convergence" -k "sliding" -v
``` **Scientific Context**: Validates mathematical convergence guarantees
- PSO swarm convergence to global optimum
- SMC finite-time reachability to sliding surface
- Adaptive parameter convergence properties #### Numerical Stability Tests ```bash
# Numerical integration stability
pytest -m "numerical_stability" -v # Energy conservation tests
pytest -m "numerical_stability" -k "energy" -v # Floating-point precision tests
pytest -m "numerical_stability" -k "precision" -v
``` **Scientific Context**: Validates numerical method accuracy

- Integration error accumulation analysis
- Energy conservation in symplectic integrators
- Condition number stability verification #### Robustness Tests ```bash
# Parameter uncertainty robustness

pytest -m "numerical_robustness" -v # Monte Carlo robustness validation
pytest -m "statistical and numerical_robustness" -v # Disturbance rejection tests
pytest -m "numerical_robustness" -k "disturbance" -v
``` **Scientific Context**: Validates system robustness
- Parameter uncertainty propagation
- Measurement noise tolerance
- Model mismatch robustness ### 4. Performance and Benchmark Tests ```bash
# All benchmark tests
pytest -m "benchmark" --benchmark-only # Controller performance benchmarks
pytest -m "benchmark" -k "controller" --benchmark-only # Optimization performance benchmarks
pytest -m "benchmark" -k "pso" --benchmark-only # Memory usage benchmarks
pytest -m "memory" -v
``` **Benchmark Targets**:

- Classical SMC: <1ms per control computation
- PSO Optimization: <60s for 100 iterations
- Integration (RK4): <10μs per time step
- Memory Growth: <10% in extended simulations ### 5. Statistical Validation Tests ```bash
# Monte Carlo statistical tests

pytest -m "statistical" -v # Property-based testing with Hypothesis
pytest -m "property_based" --hypothesis-show-statistics # Confidence interval validation
pytest -m "statistical" -k "confidence" -v
``` **Statistical Validation**:
- 95% confidence intervals for performance metrics
- Hypothesis testing for stability claims
- Distribution analysis for optimization results

---

## Advanced Test Execution ### Coverage Analysis #### Generate Coverage Report ```bash
# HTML coverage report with line-by-line analysis
pytest --cov=src --cov-report=html --cov-branch # Terminal coverage with missing lines
pytest --cov=src --cov-report=term-missing # XML coverage for CI/CD integration
pytest --cov=src --cov-report=xml
``` #### Critical Component Coverage Validation ```bash
# Controllers (target: ≥95%)

pytest tests/test_controllers/ --cov=src/controllers --cov-fail-under=95 # Core dynamics (target: ≥95%)
pytest tests/test_core/ --cov=src/core --cov-fail-under=95 # Optimization (target: ≥95%)
pytest tests/test_optimization/ --cov=src/optimization --cov-fail-under=95 # Safety-critical validation (target: 100%)
pytest tests/test_utils/validation/ --cov=src/utils/validation --cov-fail-under=100
``` ### Performance Regression Detection ```bash
# Save performance baseline
pytest -m "benchmark" --benchmark-save=baseline # Compare with baseline (fail if >5% regression)
pytest -m "benchmark" --benchmark-compare=baseline --benchmark-compare-fail=mean:5% # Generate performance report
pytest -m "benchmark" --benchmark-html=performance_report.html
``` ### Memory Leak Detection ```bash
# Memory usage monitoring

pytest -m "memory" --tb=long -v # Extended simulation memory tests
pytest -m "memory" -k "extended" -v # Profile memory usage with psutil
pytest -m "memory" --tb=line -s
``` ### Parallel Test Execution ```bash
# Parallel execution (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto # Auto-detect CPU cores
pytest -n 4 # Use 4 parallel workers # Parallel with coverage (requires coverage[toml])
pytest -n auto --cov=src --cov-report=html
```

---

## Test Troubleshooting Guide ### Common Issues and approaches #### 1. Matplotlib Backend Errors **Symptoms**:

```
RuntimeError: Invalid DISPLAY variable
``` **Solution**:

```bash
export MPLBACKEND=Agg
pytest tests/
``` **Permanent Fix**: The project automatically configures Agg backend in `tests/conftest.py` #### 2. Coverage Collection Failures **Symptoms**:

```
CoverageWarning: Module X was never imported
``` **Investigation**:

```bash
# Check if module exists and is importable
python -c "import src.module_name" # Run with coverage debug
pytest --cov=src --cov-report=term --cov-debug=trace
``` #### 3. Slow Test Performance **Identification**:

```bash
# Find slowest tests
pytest --durations=10 # Profile specific slow tests
pytest tests/slow_test.py -v -s --tb=short
``` **Optimization**:

```bash
# Run without slow tests during development
pytest -m "not slow" -v # Use parallel execution
pytest -n auto -m "not slow"
``` #### 4. Memory Test Failures **Symptoms**:

```
AssertionError: Memory growth exceeded threshold
``` **Debugging**:

```bash
# Run with garbage collection
python -X dev pytest -m "memory" -v # Profile memory usage
pip install memory-profiler
pytest -m "memory" --tb=long -s
``` #### 5. Statistical Test Failures (Rare) **Symptoms**:

```
AssertionError: Statistical hypothesis rejected
``` **Analysis**:

```bash
# Increase sample size (if appropriate)
pytest -m "statistical" --hypothesis-max-examples=1000 # Check for systematic bias
pytest -m "statistical" -v -s --tb=long
``` #### 6. Benchmark Regression Failures **Symptoms**:

```
BenchmarkComparisonFailed: Performance regression detected
``` **Investigation**:

```bash
# Compare detailed benchmark results
pytest -m "benchmark" --benchmark-compare=baseline --benchmark-verbose # Update baseline if change is intentional
pytest -m "benchmark" --benchmark-save=new_baseline
``` ### Platform-Specific Issues #### Windows-Specific ```bash
# Long path support (if needed)

git config --global core.longpaths true # Path separator issues
pytest tests/test_file.py -v # Use forward slashes in pytest paths
``` #### Linux/macOS-Specific ```bash
# Permission issues with executable tests
chmod +x tests/test_executable.py # Shared library issues
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
```

---

## CI/CD Integration Examples ### GitHub Actions Workflow ```yaml

name: Test Suite
on: [push, pull_request] jobs: test: runs-on: ubuntu-latest strategy: matrix: python-version: [3.9, 3.10, 3.11] steps: - uses: actions/checkout@v3 - name: Set up Python ${{ matrix.python-version }} uses: actions/setup-python@v4 with: python-version: ${{ matrix.python-version }} - name: Install dependencies run: | pip install --upgrade pip pip install -r requirements.txt pip install pytest-cov pytest-benchmark pytest-xdist - name: Run unit tests run: | pytest -m "unit" --cov=src --cov-report=xml - name: Run integration tests run: | pytest -m "integration and not slow" --cov=src --cov-append - name: Run scientific validation run: | pytest -m "convergence or numerical_stability" -v - name: Run benchmarks run: | pytest -m "benchmark" --benchmark-only - name: Upload coverage to Codecov uses: codecov/codecov-action@v3 with: file: ./coverage.xml flags: unittests name: codecov-umbrella
``` ### Quality Gate Script ```bash
#!/bin/bash
# quality_gate.sh - Production deployment validation set -e echo "🚀 Starting quality gate validation..." # 1. Fast unit tests
echo "📋 Running unit tests..."
pytest -m "unit" --tb=short || { echo "❌ Unit tests failed"; exit 1; } # 2. Integration tests (excluding slow)
echo "🔗 Running integration tests..."
pytest -m "integration and not slow" --tb=short || { echo "❌ Integration tests failed"; exit 1; } # 3. Coverage validation
echo "📊 Validating coverage..."
pytest --cov=src --cov-fail-under=85 --tb=no || { echo "❌ Coverage below threshold"; exit 1; } # 4. Critical component coverage
echo "🎯 Validating critical component coverage..."
pytest tests/test_controllers/ --cov=src/controllers --cov-fail-under=95 --tb=no || { echo "❌ Controller coverage insufficient"; exit 1; }
pytest tests/test_core/ --cov=src/core --cov-fail-under=95 --tb=no || { echo "❌ Core coverage insufficient"; exit 1; }
pytest tests/test_optimization/ --cov=src/optimization --cov-fail-under=95 --tb=no || { echo "❌ Optimization coverage insufficient"; exit 1; } # 5. Scientific validation
echo "🔬 Running scientific validation..."
pytest -m "convergence or numerical_stability" --tb=short || { echo "❌ Scientific validation failed"; exit 1; } # 6. Performance regression check
echo "⚡ Checking performance regression..."
pytest -m "benchmark" --benchmark-compare --benchmark-compare-fail=mean:5% || { echo "❌ Performance regression detected"; exit 1; } # 7. Statistical validation
echo "📈 Running statistical validation..."
pytest -m "statistical" --tb=short || { echo "❌ Statistical validation failed"; exit 1; } echo "✅ All quality gates passed! Deployment approved."
``` ### Pre-commit Hook Configuration ```yaml
# .pre-commit-config.yaml

repos: - repo: local hooks: - id: pytest-unit name: Run unit tests entry: pytest -m "unit" --tb=short language: system pass_filenames: false always_run: true - id: pytest-coverage name: Check test coverage entry: pytest --cov=src --cov-fail-under=85 --tb=no language: system pass_filenames: false always_run: true - id: pytest-integration-fast name: Run fast integration tests entry: pytest -m "integration and not slow" --tb=short language: system pass_filenames: false always_run: true
```

---

## Test Data and Fixtures ### Standard Test Fixtures #### Configuration Fixtures
```python
# Available in all tests via conftest.py

config # Project configuration with attribute access
physics_cfg # Physics parameters for dynamics models
physics_params # Alias for physics_cfg (backward compatibility)
``` #### Dynamics Fixtures
```python

dynamics # Simplified DIP dynamics instance
full_dynamics # Full nonlinear DIP dynamics instance
initial_state # Standard initial state: [0.0, 0.1, -0.05, 0.0, 0.0, 0.0]
``` #### Controller Fixtures
```python

make_hybrid # Factory for creating HybridAdaptiveSTASMC controllers
``` **Example Usage**:
```python

def test_controller_stability(dynamics, initial_state, make_hybrid): """Test controller stability with standard fixtures.""" controller = make_hybrid(gains=[0.5, 2.0, 0.8, 1.5]) control_output = controller.compute_control(initial_state) assert abs(control_output) <= controller.max_force
``` ### Test Data Management #### Temporary Test Data
```python

import tempfile
import pytest @pytest.fixture
def temp_config_file(): """Create temporary configuration file for testing.""" with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f: yaml.dump(test_config, f) yield f.name os.unlink(f.name)
``` #### Benchmark Data Storage
```bash
# Benchmark results are stored in .benchmarks/

ls .benchmarks/
Linux-CPython-3.9-64bit/ baseline.json comparison.json
```

---

## Test Reporting and Analysis ### Coverage Reports #### HTML Coverage Report
```bash

pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser for detailed line-by-line coverage

``` #### Terminal Coverage Summary
```bash

pytest --cov=src --cov-report=term-missing
# Shows missing lines directly in terminal

``` #### Coverage for Specific Modules
```bash
# Controller coverage analysis

pytest tests/test_controllers/ --cov=src/controllers --cov-report=term # Dynamics coverage analysis
pytest tests/test_core/ --cov=src/core --cov-report=term
``` ### Benchmark Reports #### HTML Benchmark Report
```bash

pytest -m "benchmark" --benchmark-html=benchmarks.html
# Detailed performance analysis with graphs

``` #### JSON Benchmark Export
```bash

pytest -m "benchmark" --benchmark-json=benchmarks.json
# Machine-readable performance data

``` #### Benchmark Comparison
```bash
# Compare current run with saved baseline

pytest -m "benchmark" --benchmark-compare=baseline --benchmark-verbose
``` ### Test Result Analysis #### JUnit XML for CI/CD
```bash

pytest --junitxml=test-results.xml
# Standard format for CI/CD integration

``` #### Detailed Failure Analysis
```bash
# Full traceback for debugging

pytest --tb=long # Show local variables in tracebacks
pytest --tb=auto --showlocals # Capture stdout/stderr
pytest -s --tb=short
```

## Best Practices and Guidelines

### Development Workflow

1. **Write Tests First** (TDD Approach) ```bash # 1. Write failing test pytest tests/test_new_feature.py::test_new_functionality -v # 2. Implement minimal feature # 3. Run test to verify it passes pytest tests/test_new_feature.py::test_new_functionality -v # 4. Refactor and re-test pytest -m "unit" -k "new_functionality" -v ``` 2. **Incremental Testing** ```bash # Test changes incrementally pytest tests/modified_module/ -v # Test modified module pytest -m "integration" -k "modified" -v # Test related integration pytest --lf # Re-run last failures ``` 3. **Performance-Aware Testing** ```bash # Monitor test performance during development pytest --durations=5 # Show 5 slowest tests pytest -m "not slow" --tb=short # Skip slow tests for quick feedback ``` ### Scientific Validation Best Practices 1. **Statistical Significance** - Use adequate sample sizes for Monte Carlo tests - Report confidence intervals with statistical tests - Validate assumptions (normality, independence) before statistical tests 2. **Numerical Stability** - Test edge cases (very small/large values) - Validate convergence properties - Monitor condition numbers and numerical precision 3. **Property-Based Testing** - Define invariants that must hold for all inputs - Use Hypothesis to explore input space systematically - Validate mathematical properties across domains ### CI/CD Best Practices 1. **Staged Testing** ```bash # Stage 1: Fast feedback (< 1 minute) pytest -m "unit" --tb=short # Stage 2: Integration validation (< 5 minutes) pytest -m "integration and not slow" --tb=short # Stage 3: validation (< 30 minutes) pytest --cov=src --cov-fail-under=85 ``` 2. **Parallel Execution** ```bash # Use parallel execution for faster CI/CD pytest -n auto -m "not slow" pytest -n 4 --dist=loadscope # Load balancing by test scope ``` 3. **Artifact Management** ```bash # Save important artifacts pytest --cov=src --cov-report=xml # Coverage for codecov pytest -m "benchmark" --benchmark-json=perf.json # Performance data pytest --junitxml=results.xml # Test results for CI ```

---

**Document Authority**: Documentation Expert Agent
**Technical Review**: Integration Coordinator
**Quality Assurance**: Ultimate Orchestrator **Generated with [Claude Code](https://claude.ai/code)** **Co-Authored-By: Claude <noreply@anthropic.com>**