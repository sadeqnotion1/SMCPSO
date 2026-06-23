# How-To: Testing & Validation

**What This Guide Covers:**
This guide shows you how to test and validate your controllers before deploying them. You'll learn how to run tests, interpret results, and ensure your controller works correctly. **Type:** Task-Oriented Guide

**Level:** Intermediate to Advanced
**Prerequisites:**
- [Getting Started Guide](../getting-started.md)
- Basic Python testing knowledge (helpful)

---

## Overview This guide shows you how to run tests, write new tests, validate controllers, and perform benchmarking in the DIP SMC PSO framework. **Common Tasks:**

- Run the test suite
- Write unit tests for new controllers
- Validate controller performance
- Run performance benchmarks
- Check code coverage

---

## Table of Contents - [Running Tests](#running-tests)

- [Writing Tests](#writing-tests)
- [Validation Workflows](#validation-workflows)
- [Performance Benchmarking](#performance-benchmarking)

---

## Running Tests ### Quick Test Execution ```bash

# Run all tests

python run_tests.py # Or use pytest directly
python -m pytest tests/ # Run with verbose output
python -m pytest tests/ -v # Run specific test file
python -m pytest tests/test_controllers/test_classical_smc.py -v # Run specific test function
python -m pytest tests/test_controllers/test_classical_smc.py::TestClassicalSMC::test_initialization -v
``` ### Test Organization ```
tests/
├── test_controllers/ # Controller unit tests
│ ├── test_classical_smc.py
│ ├── test_sta_smc.py
│ ├── test_adaptive_smc.py
│ └── test_hybrid_smc.py
├── test_core/ # Core simulation tests
│ ├── test_dynamics.py
│ ├── test_simulation_runner.py
│ └── test_vector_sim.py
├── test_optimizer/ # PSO tests
│ └── test_pso_optimizer.py
├── test_integration/ # Integration tests
│ └── test_end_to_end.py
└── conftest.py # Test fixtures
``` ### Running Specific Test Categories ```bash
# Unit tests only (fast)

python -m pytest tests/test_controllers/ -v # Integration tests only (slower)
python -m pytest tests/test_integration/ -v # Skip slow tests
python -m pytest tests/ -m "not slow" -v # Run only slow tests
python -m pytest tests/ -m "slow" -v
``` ### Coverage Analysis ```bash
# Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=html # View coverage report
# Open htmlcov/index.html in browser # Generate terminal coverage report
python -m pytest tests/ --cov=src --cov-report=term # Coverage for specific module
python -m pytest tests/test_controllers/ --cov=src/controllers --cov-report=term
``` **Coverage Targets:**

- Overall: ≥85%
- Critical components (controllers, dynamics): ≥95%
- Safety-critical code: 100% ### Performance Benchmarks ```bash
# Run benchmarks only

python -m pytest tests/test_benchmarks/ --benchmark-only # Run benchmarks with comparison
python -m pytest tests/test_benchmarks/ --benchmark-only --benchmark-compare # Save benchmark results
python -m pytest tests/test_benchmarks/ --benchmark-only --benchmark-save=baseline # Compare against baseline
python -m pytest tests/test_benchmarks/ --benchmark-only --benchmark-compare=baseline
```

---

## Writing Tests ### Unit Test Template ```python
# tests/test_controllers/test_my_controller.py
import pytest
import numpy as np
from src.controllers.my_controller import MyController class TestMyController: """Unit tests for MyController.""" def test_initialization(self): """Test controller initializes correctly.""" gains = [10.0, 8.0, 15.0, 12.0, 50.0, 5.0] controller = MyController(gains=gains, max_force=100.0) assert controller.gains == gains assert controller.max_force == 100.0 def test_invalid_gain_count(self): """Test ValueError raised for wrong number of gains.""" gains = [10.0, 8.0] # Too few with pytest.raises(ValueError, match="6 gains"): MyController(gains=gains, max_force=100.0) def test_compute_control(self): """Test control computation.""" controller = MyController( gains=[10, 8, 15, 12, 50, 5], max_force=100.0 ) state = np.array([0, 0, 0.1, 0, 0.15, 0]) control, state_vars, history = controller.compute_control( state, {}, {} ) # Check control is computed assert isinstance(control, (float, np.floating)) # Check bounds assert abs(control) <= 100.0 def test_control_saturation(self): """Test control saturates at max_force.""" controller = MyController( gains=[10, 8, 15, 12, 500.0, 5.0], # Very high K max_force=100.0 ) state = np.array([0, 0, 0.5, 0, 0.6, 0]) # Large errors control, _, _ = controller.compute_control(state, {}, {}) assert abs(control) == 100.0 # Should saturate def test_equilibrium(self): """Test zero control at equilibrium.""" controller = MyController( gains=[10, 8, 15, 12, 50, 5], max_force=100.0 ) state = np.zeros(6) # Perfect equilibrium control, _, _ = controller.compute_control(state, {}, {}) assert abs(control) < 1e-6 # Nearly zero
``` ### Parametrized Tests ```python
# example-metadata:

# runnable: false @pytest.mark.parametrize("gains,expected_valid", [ ([10, 8, 15, 12, 50, 5], True), # Valid ([0, 8, 15, 12, 50, 5], False), # k1 = 0 invalid ([-10, 8, 15, 12, 50, 5], False), # Negative gain

])
def test_gain_validation(gains, expected_valid): """Test gain validation with multiple cases.""" if expected_valid: controller = MyController(gains=gains, max_force=100.0) assert controller.gains == gains else: with pytest.raises(ValueError): MyController(gains=gains, max_force=100.0)
``` ### Fixture Usage ```python
# In conftest.py
import pytest
from src.config import load_config @pytest.fixture
def config(): """Load test configuration.""" return load_config('config.yaml') @pytest.fixture
def classical_controller(config): """Create classical SMC controller.""" from src.controllers import create_smc_for_pso, SMCType return create_smc_for_pso( SMCType.CLASSICAL, gains=[10, 8, 15, 12, 50, 5], max_force=100.0 ) # In test file
def test_with_fixture(classical_controller): """Test using pre-configured controller.""" state = np.array([0, 0, 0.1, 0, 0.15, 0]) control, _, _ = classical_controller.compute_control(state, {}, {}) assert abs(control) <= 100.0
``` ### Integration Tests ```python
# tests/test_integration/test_end_to_end.py

def test_full_simulation(): """Test complete simulation workflow.""" from src.controllers.factory import create_controller from src.core.simulation_runner import SimulationRunner from src.config import load_config # Load config config = load_config('config.yaml') # Create controller controller = create_controller( 'classical_smc', config=config.controllers.classical_smc ) # Run simulation runner = SimulationRunner(config) result = runner.run(controller) # Validate results assert 'metrics' in result assert 'time' in result assert 'state' in result assert 'control' in result # Check stability (state remains bounded) state = np.array(result['state']) assert np.all(np.abs(state) < 10.0), "State diverged" # Check settling time reasonable assert result['metrics']['settling_time'] < 10.0
```

---

## Validation Workflows ### Controller Validation Checklist ```python
def validate_controller(controller_name, gains): """ controller validation. Returns: dict with validation results """ from src.controllers import create_smc_for_pso, SMCType from src.core.simulation_runner import SimulationRunner from src.config import load_config results = { 'controller': controller_name, 'gains': gains, 'tests_passed': [], 'tests_failed': [] } config = load_config('config.yaml') # Test 1: Initialization try: controller = create_smc_for_pso( SMCType[controller_name.upper()], gains=gains, max_force=100.0 ) results['tests_passed'].append('Initialization') except Exception as e: results['tests_failed'].append(f'Initialization: {e}') return results # Test 2: Equilibrium stability try: state = np.zeros(6) control, _, _ = controller.compute_control(state, {}, {}) if abs(control) < 1e-3: results['tests_passed'].append('Equilibrium stability') else: results['tests_failed'].append(f'Equilibrium: control={control:.4f}') except Exception as e: results['tests_failed'].append(f'Equilibrium: {e}') # Test 3: Full simulation try: runner = SimulationRunner(config) result = runner.run(controller) if result['metrics']['settling_time'] < 10.0: results['tests_passed'].append('Settling time < 10s') else: results['tests_failed'].append( f'Settling time: {result["metrics"]["settling_time"]:.2f}s' ) state_final = np.array(result['state']) if np.all(np.abs(state_final) < 10.0): results['tests_passed'].append('State remains bounded') else: results['tests_failed'].append('State diverged') except Exception as e: results['tests_failed'].append(f'Simulation: {e}') return results # Run validation
validation = validate_controller('CLASSICAL', [10, 8, 15, 12, 50, 5]) print(f"\n{validation['controller']} Validation:")
print(f" Passed: {len(validation['tests_passed'])}")
print(f" Failed: {len(validation['tests_failed'])}") if validation['tests_failed']: print("\nFailed tests:") for test in validation['tests_failed']: print(f" - {test}")
``` ### Robustness Testing ```python

def test_robustness_to_mass_variation(): """Test controller with ±30% mass variation.""" from src.plant.models.dynamics import DoubleInvertedPendulum masses = [0.7, 0.85, 1.0, 1.15, 1.3] # ±30% variation results = [] for m0 in masses: # Create dynamics with varied mass dynamics = DoubleInvertedPendulum( m0=m0, m1=0.1, m2=0.1, l1=0.5, l2=0.5 ) # Create controller controller = create_smc_for_pso( SMCType.CLASSICAL, gains=[10, 8, 15, 12, 50, 5], max_force=100.0 ) # Run simulation result = simulate_with_dynamics(controller, dynamics) results.append({ 'm0': m0, 'ise': result['metrics']['ise'], 'settling_time': result['metrics']['settling_time'] }) # Check robustness ise_values = [r['ise'] for r in results] ise_variance = np.std(ise_values) / np.mean(ise_values) print(f"\nRobustness Analysis (Mass Variation):") for r in results: print(f" m0={r['m0']:.2f}: ISE={r['ise']:.4f}, " f"Settling={r['settling_time']:.2f}s") print(f"\nISE Coefficient of Variation: {ise_variance:.3f}") # Robustness criterion: CV < 0.3 assert ise_variance < 0.3, "Controller not robust to mass variation"
```

---

## Performance Benchmarking ### Running Benchmarks ```bash
# Run all benchmarks
python -m pytest tests/test_benchmarks/ --benchmark-only -v # Run specific benchmark
python -m pytest tests/test_benchmarks/test_controller_performance.py::test_classical_smc_benchmark --benchmark-only # Save baseline
python -m pytest tests/test_benchmarks/ --benchmark-only --benchmark-save=v1.0 # Compare to baseline
python -m pytest tests/test_benchmarks/ --benchmark-only --benchmark-compare=v1.0 # Fail if regression > 5%
python -m pytest tests/test_benchmarks/ --benchmark-only --benchmark-compare=v1.0 --benchmark-compare-fail=mean:5%
``` ### Writing Benchmarks ```python
# tests/test_benchmarks/test_controller_performance.py

import pytest
import numpy as np
from src.controllers import create_smc_for_pso, SMCType def test_classical_smc_benchmark(benchmark): """Benchmark classical SMC control computation.""" controller = create_smc_for_pso( SMCType.CLASSICAL, gains=[10, 8, 15, 12, 50, 5], max_force=100.0 ) state = np.array([0, 0, 0.1, 0, 0.15, 0]) state_vars = {} history = controller.initialize_history() # Benchmark the control computation result = benchmark( controller.compute_control, state, state_vars, history ) # Verify result is valid control, _, _ = result assert abs(control) <= 100.0 def test_full_simulation_benchmark(benchmark): """Benchmark full simulation.""" from src.controllers.factory import create_controller from src.core.simulation_runner import SimulationRunner from src.config import load_config config = load_config('config.yaml') controller = create_controller( 'classical_smc', config=config.controllers.classical_smc ) runner = SimulationRunner(config) # Benchmark full simulation result = benchmark(runner.run, controller) # Verify completion assert 'metrics' in result
``` ### Interpreting Benchmark Results ```
test_classical_smc_benchmark Mean: 125.43 µs StdDev: 12.34 µs Min: 110.21 µs Max: 180.45 µs Median: 123.67 µs
``` **Performance targets:**

- Control computation: < 200 µs (5 kHz capable)
- Full simulation (5s): < 10 seconds
- PSO iteration: < 5 seconds

---

## Best Practices ### Test-Driven Development 1. **Write test first** (red)

2. **Implement feature** (green)
3. **Refactor** (clean) ```python
# example-metadata:

# runnable: false # 1. Write failing test

def test_new_feature(): controller = MyController(...) result = controller.new_feature() assert result == expected_value # 2. Implement to pass test
class MyController: def new_feature(self): # Implementation return expected_value # 3. Refactor if needed
``` ### Continuous Integration ```yaml
# .github/workflows/tests.yml (example)
name: Tests on: [push, pull_request] jobs: test: runs-on: ubuntu-latest steps: - uses: actions/checkout@v2 - name: Set up Python uses: actions/setup-python@v2 with: python-version: 3.9 - name: Install dependencies run: pip install -r requirements.txt - name: Run tests run: python -m pytest tests/ --cov=src --cov-report=xml - name: Upload coverage uses: codecov/codecov-action@v2
```

---

## Troubleshooting ### Tests Fail ```bash

# Run with verbose output

python -m pytest tests/ -vv # Show print statements
python -m pytest tests/ -s # Stop at first failure
python -m pytest tests/ -x # Show full diff
python -m pytest tests/ --tb=long
``` ### Import Errors in Tests ```bash
# Verify PYTHONPATH
python -c "import sys; print('\n'.join(sys.path))" # Run from project root
cd /path/to/dip-smc-pso
python -m pytest tests/
``` ### Slow Tests ```bash
# Identify slow tests

python -m pytest tests/ --durations=10 # Run in parallel (requires pytest-xdist)
pip install pytest-xdist
python -m pytest tests/ -n auto
```

---

## Next Steps - [How-To: Running Simulations](running-simulations.md): Execute tests
- [Tutorial 04: Custom Controller](../tutorials/tutorial-04-custom-controller.md): Implement with tests
- [User Guide](../user-guide.md): Complete reference

---

**Last Updated:** October 2025
