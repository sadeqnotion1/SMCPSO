#==========================================================================================\\\
#===================== docs/testing/standards/testing_standards.md ====================\\\
#==========================================================================================\\\

# Testing Standards and Guidelines

## Overview

This document defines the testing standards for the DIP SMC PSO project, ensuring consistent quality, maintainability, and scientific rigor across all test implementations.

## Test Architecture Standards

### Test Directory Structure

```
tests/
├── conftest.py # Global test configuration and fixtures
├── test_controllers/ # Controller-specific unit tests
│ ├── conftest.py # Controller test fixtures
│ ├── test_classical_smc.py # Classical SMC unit tests
│ ├── test_adaptive_smc.py # Adaptive SMC unit tests
│ ├── test_sta_smc.py # Super-twisting SMC unit tests
│ └── test_hybrid_adaptive_sta_smc.py # Hybrid SMC unit tests
├── test_core/ # Core simulation engine tests
│ ├── test_dynamics.py # Dynamics model validation
│ ├── test_simulation_runner.py # Simulation orchestration tests
│ └── test_vector_sim.py # Batch simulation tests
├── test_optimizer/ # PSO optimization tests
│ └── test_pso_optimizer.py # PSO algorithm validation
├── test_benchmarks/ # Performance and scientific validation
│ ├── test_statistical_benchmarks.py # Statistical analysis validation
│ ├── test_integration_accuracy.py # Numerical integration accuracy
│ └── test_modular_framework.py # Framework component tests
└── test_integration/ # End-to-end integration tests ├── test_cli_workflows.py # CLI application workflows ├── test_hil_system.py # Hardware-in-the-loop tests └── test_pso_workflows.py # PSO optimization workflows
``` ### Naming Conventions #### Test Files
- **Pattern**: `test_<module_name>.py`
- **Location**: Mirror source structure under `tests/`
- **Example**: `src/controllers/classical_smc.py` → `tests/test_controllers/test_classical_smc.py` #### Test Functions
- **Unit Tests**: `test_<functionality>_<condition>`
- **Property Tests**: `test_<property>_holds_<scenario>`
- **Integration Tests**: `test_<workflow>_<outcome>`
- **Performance Tests**: `test_<component>_performance_<metric>` #### Test Classes
- **Pattern**: `Test<ComponentName><TestType>`
- **Examples**: - `TestClassicalSMCValidation` - `TestPSOConvergenceProperties` - `TestIntegrationAccuracy` ## Test Categories and Requirements ### 1. Unit Tests **Purpose**: Validate individual component behavior in isolation **Coverage Requirements**:
- **Public methods**: 100% coverage
- **Edge cases**: Boundary conditions, invalid inputs
- **Error handling**: Exception scenarios and error messages **Standards**:
```python
# example-metadata:

# runnable: false def test_classical_smc_control_computation_valid_input(): """Test classical SMC control computation with valid state input.""" # Setup controller = ClassicalSMC(gains=[10, 8, 15, 12, 50, 5], max_force=100.0) state = np.array([0.1, 0.05, 0.02, 0.0, 0.0, 0.0]) # Execute control = controller.compute_control(state, 0.0, {}) # Verify assert isinstance(control, float) assert -100.0 <= control <= 100.0 # Within actuator limits assert not np.isnan(control) and not np.isinf(control) def test_classical_smc_invalid_state_dimension(): """Test classical SMC raises appropriate error for invalid state dimension.""" controller = ClassicalSMC(gains=[10, 8, 15, 12, 50, 5]) invalid_state = np.array([0.1, 0.05]) # Only 2 elements instead of 6 with pytest.raises(ValueError, match="State vector must have 6 elements"): controller.compute_control(invalid_state, 0.0, {})

``` ### 2. Property-Based Tests **Purpose**: Validate mathematical and control-theoretic properties **Requirements**:
- **Stability properties**: Lyapunov stability verification
- **Bound preservation**: Control saturation, state constraints
- **Conservation laws**: Energy conservation (where applicable)
- **Convergence properties**: SMC sliding surface convergence **Standards**:
```python

from hypothesis import given, strategies as st @given( gains=st.lists(st.floats(min_value=0.1, max_value=100.0), min_size=6, max_size=6), state=st.lists(st.floats(min_value=-10.0, max_value=10.0), min_size=6, max_size=6)
)
def test_control_output_bounded_property(gains, state): """Property: Control output must always be within actuator limits.""" controller = ClassicalSMC(gains=gains, max_force=100.0) state_array = np.array(state) control = controller.compute_control(state_array, 0.0, {}) assert -100.0 <= control <= 100.0 assert not np.isnan(control) and not np.isinf(control) @given( initial_state=st.lists(st.floats(min_value=-1.0, max_value=1.0), min_size=6, max_size=6)
)
def test_lyapunov_stability_property(initial_state): """Property: Lyapunov function decreases for stable controllers.""" controller = ClassicalSMC(gains=[10, 8, 15, 12, 50, 5]) # Simulate short trajectory trajectory = simulate_short_trajectory(controller, np.array(initial_state)) # Compute Lyapunov function V_values = [compute_lyapunov_function(state) for state in trajectory] # Property: V should generally decrease (allowing for small numerical errors) decreasing_trend = np.polyfit(range(len(V_values)), V_values, 1)[0] assert decreasing_trend <= 0.01 # Allow small positive slope for numerical stability
``` ### 3. Integration Tests **Purpose**: Validate end-to-end workflows and component interactions **Requirements**:
- **Complete workflows**: CLI → PSO → Simulation → Results
- **System integration**: Controller + Dynamics + Simulation
- **Configuration validation**: YAML config → System behavior
- **Error propagation**: Graceful handling of component failures **Standards**:
```python
# example-metadata:

# runnable: false def test_complete_pso_optimization_workflow(): """Test complete PSO optimization workflow from CLI to results.""" # Setup configuration config = create_test_config( controller_type="classical_smc", pso_iterations=10, # Reduced for testing pso_particles=5 ) # Execute workflow results = run_pso_optimization_workflow(config) # Verify results assert results.optimization_successful assert len(results.optimized_gains) == 6 assert results.final_cost < results.initial_cost assert all(0.1 <= gain <= 100.0 for gain in results.optimized_gains) # Verify simulation with optimized gains controller = create_controller_from_gains(results.optimized_gains) simulation_result = run_simulation(controller, config.simulation) assert simulation_result.successful assert simulation_result.final_state_error < 0.1

``` ### 4. Performance Tests **Purpose**: Detect performance regressions and validate computational efficiency **Requirements**:
- **Benchmark critical paths**: Control computation, PSO optimization, simulation
- **Memory usage monitoring**: Detect memory leaks in long simulations
- **Scaling validation**: Performance vs. simulation duration/complexity
- **Regression detection**: Alert on >5% performance degradation **Standards**:
```python

import pytest @pytest.mark.benchmark(group="control_computation")
def test_classical_smc_performance(benchmark): """Benchmark classical SMC control computation performance.""" controller = ClassicalSMC(gains=[10, 8, 15, 12, 50, 5]) state = np.array([0.1, 0.05, 0.02, 0.0, 0.0, 0.0]) result = benchmark(controller.compute_control, state, 0.0, {}) # Performance requirements assert benchmark.stats.mean < 0.001 # Mean execution time < 1ms assert benchmark.stats.stddev < 0.0005 # Low variance @pytest.mark.benchmark(group="batch_simulation")
def test_batch_simulation_scaling(benchmark): """Benchmark batch simulation scaling with number of trials.""" controller_factory = lambda: ClassicalSMC(gains=[10, 8, 15, 12, 50, 5]) def run_batch(n_trials=100): return run_multiple_trials(controller_factory, create_test_config(), n_trials) result = benchmark(run_batch) # Scaling requirements assert benchmark.stats.mean < 10.0 # 100 trials in < 10 seconds
``` ### 5. Scientific Validation Tests **Purpose**: Verify control-theoretic and mathematical properties **Requirements**:
- **Theoretical properties**: Sliding surface design, stability margins
- **Physical constraints**: Energy conservation, momentum preservation
- **Numerical accuracy**: Integration method accuracy, convergence rates
- **Robustness validation**: Performance under parameter variations **Standards**:
```python
# example-metadata:

# runnable: false def test_sliding_surface_design_theory(): """Validate sliding surface design follows control theory principles.""" gains = [10, 8, 15, 12, 50, 5] # k1, k2, λ1, λ2, K, η # Extract gains according to theory k1, k2, λ1, λ2, K, η = gains # Theoretical requirements for stability assert k1 > 0 and k2 > 0, "Position gains must be positive" assert λ1 > 0 and λ2 > 0, "Surface parameters must be positive" assert K > 0, "Switching gain must be positive" assert η >= 0, "Boundary layer must be non-negative" # Pole placement verification characteristic_poly = [1, λ1 + λ2, λ1*λ2 + k1, k2*λ1] roots = np.roots(characteristic_poly) # All poles should have negative real parts for stability assert all(np.real(root) < 0 for root in roots), "System must be stable" def test_energy_conservation_in_simulation(): """Verify energy conservation in frictionless simulation.""" # Setup frictionless configuration config = create_test_config( friction_coefficients=[0.0, 0.0, 0.0], # No friction simulation_duration=5.0 ) controller = ClassicalSMC(gains=[10, 8, 15, 12, 50, 5]) result = run_simulation(controller, config) # Compute total energy throughout simulation potential_energy = compute_potential_energy(result.states, config.physics) kinetic_energy = compute_kinetic_energy(result.states, config.physics) total_energy = potential_energy + kinetic_energy # Energy should be approximately conserved (allowing for numerical errors) energy_variation = np.std(total_energy) / np.mean(total_energy) assert energy_variation < 0.01, "Energy should be conserved in frictionless system"

``` ## Quality Gates ### Coverage Requirements | Component Type | Minimum Coverage | Critical Coverage |
|----------------|------------------|-------------------|
| Controllers | 95% | 100% |
| Core Dynamics | 95% | 100% |
| Simulation Engine | 90% | 95% |
| Optimization | 85% | 95% |
| Utilities | 85% | 90% |
| **Overall Project** | **85%** | **95%** | ### Performance Standards | Metric | Requirement | Critical Threshold |
|--------|-------------|-------------------|
| Control Computation | < 1ms mean | < 2ms max |
| Single Simulation | < 1s (5s duration) | < 2s |
| PSO Optimization | < 5min (50 particles, 100 iterations) | < 10min |
| Test Suite Execution | < 30s | < 60s |
| Memory Usage | < 500MB peak | < 1GB | ### Regression Detection | Change Type | Alert Threshold | Block Threshold |
|-------------|-----------------|-----------------|
| Performance Degradation | 5% | 15% |
| Coverage Decrease | 2% | 5% |
| Test Failure Rate | Any increase | >1% failure rate |
| Memory Increase | 10% | 25% | ## Continuous Integration Standards ### Pre-commit Hooks 1. **Code Quality** - Black code formatting - isort import sorting - flake8 linting - mypy type checking 2. **Testing** - Unit test execution - Coverage reporting - Performance benchmark comparison 3. **Documentation** - Docstring validation - README updates - Changelog maintenance ### CI Pipeline Stages 1. **Static Analysis** (< 2 minutes) - Code quality checks - Type validation - Security scanning 2. **Unit Tests** (< 5 minutes) - Component isolation tests - Property-based validation - Coverage reporting 3. **Integration Tests** (< 10 minutes) - End-to-end workflows - Configuration validation - System integration 4. **Performance Tests** (< 15 minutes) - Benchmark execution - Regression detection - Memory usage monitoring 5. **Scientific Validation** (< 10 minutes) - Control theory property validation - Physical constraint verification - Numerical accuracy assessment ### Deployment Gates | Gate | Criteria | Override Authority |
|------|----------|-------------------|
| **Quality Gate** | 85% coverage, all tests pass | Tech Lead |
| **Performance Gate** | No >15% regression | Tech Lead |
| **Security Gate** | No critical vulnerabilities | Security Team |
| **Scientific Gate** | All theoretical properties validated | Research Lead | ## Test Data Management ### Test Fixtures - **Centralized**: Common fixtures in `conftest.py`
- **Scoped**: Module-specific fixtures for specialized testing
- **Parameterized**: Multiple test scenarios from single fixture
- **Realistic**: Test data reflects real system behavior ### Synthetic Data Generation ```python
# example-metadata:
# runnable: false # Example: Generate valid SMC parameters
@pytest.fixture
def valid_smc_gains(): """Generate valid SMC gain sets for testing.""" return [ [10.0, 8.0, 15.0, 12.0, 50.0, 5.0], # Typical values [5.0, 3.0, 8.0, 6.0, 25.0, 2.0], # Conservative gains [20.0, 15.0, 30.0, 25.0, 100.0, 10.0], # Aggressive gains ] @pytest.fixture
def test_trajectories(): """Generate test state trajectories for validation.""" # Analytical approaches for linear cases # Numerical approaches for nonlinear cases # Edge cases and boundary conditions pass
``` ### Data Validation - **Schema Validation**: Pydantic models for all test data

- **Physical Consistency**: Test data must respect physical laws
- **Statistical Properties**: Generated data has expected distributions
- **Reproducibility**: Seeded random generation for consistent tests ## Documentation Standards ### Test Documentation - **Purpose**: Clear description of what is being tested
- **Theory**: Mathematical/control-theoretic background
- **Setup**: Test configuration and assumptions
- **Verification**: How results are validated
- **References**: Link to theoretical sources ### Example Documentation ```python
# example-metadata:

# runnable: false def test_sliding_surface_convergence(): """Test that states converge to sliding surface under classical SMC. Theory: ------- Classical SMC guarantees finite-time convergence to sliding surface s(x) = 0 when switching gain K > uncertainty bound. Reference: Utkin, V. "Sliding Modes in Control and Optimization" Test Setup: ---------- - Initial state away from equilibrium - Classical SMC with sufficient switching gain - Simulation until convergence or timeout Verification: ------------ - |s(x(t))| → 0 as t increases - Convergence time < theoretical bound - No chattering beyond boundary layer """ # Test implementation here pass

``` ## Maintenance Guidelines ### Test Lifecycle 1. **Creation**: Tests written before/during feature development
2. **Evolution**: Tests updated with feature changes
3. **Optimization**: Performance optimization without functionality loss
4. **Deprecation**: Graceful removal of obsolete tests ### Test Debt Management - **Regular Reviews**: Monthly test suite health assessment
- **Refactoring**: Quarterly test code refactoring
- **Coverage Analysis**: Continuous coverage gap identification
- **Performance Monitoring**: Ongoing test execution time tracking ### Best Practices 1. **Independence**: Tests should not depend on each other
2. **Determinism**: Tests should produce consistent results
3. **Speed**: Unit tests should execute quickly
4. **Clarity**: Tests should be self-documenting
5. **Maintenance**: Tests should be easy to update

---

*These standards ensure consistent, high-quality testing practices across the DIP SMC PSO project, supporting both research rigor and engineering excellence.*