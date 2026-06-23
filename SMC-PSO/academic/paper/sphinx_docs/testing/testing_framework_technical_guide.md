# Testing Framework Technical Guide **DIP-SMC-PSO Project**

**Last Updated**: 2025-10-04
**Status**: Research-Grade Testing Infrastructure

---

## Table of Contents 1. [Testing Architecture](#1-testing-architecture)

2. [Test Infrastructure](#2-test-infrastructure)
3. [Unit Testing Patterns](#3-unit-testing-patterns)
4. [Integration Testing](#4-integration-testing)
5. [Test Utilities & Helpers](#5-test-utilities--helpers)
6. [Quick Reference](#6-quick-reference)

---

## 1. Testing Architecture ### 1.1 Overview The DIP-SMC-PSO testing framework provides validation across **143 test files** organized into **22 specialized modules**. The architecture follows scientific computing best practices with rigorous coverage requirements and multi-level testing strategies. ```

tests/ # 143 test files, 22 modules
├── conftest.py # Session-scoped fixtures and pytest configuration
├── test_controllers/ # Controller unit and integration tests (28 files)
│ ├── base/ # Base controller interfaces and primitives
│ ├── factory/ # Controller factory pattern tests
│ ├── smc/ # SMC algorithm-specific tests
│ │ ├── algorithms/
│ │ │ ├── classical/ # Classical SMC tests
│ │ │ ├── adaptive/ # Adaptive SMC tests
│ │ │ ├── super_twisting/ # Super-Twisting SMC tests
│ │ │ └── hybrid/ # Hybrid Adaptive-STA tests
│ ├── specialized/ # Swing-up controller tests
│ └── mpc/ # MPC controller tests
├── test_benchmarks/ # Benchmarking framework tests (18 files)
│ ├── core/ # Core benchmark functionality
│ ├── statistics/ # Statistical analysis tests
│ ├── integration/ # Integration method benchmarks
│ ├── performance/ # Performance regression tests
│ └── validation/ # Parameter realism validation
├── test_simulation/ # Simulation engine tests (15 files)
│ ├── core/ # Core simulation runner
│ ├── engines/ # Simulation engines (standard, batch, vector)
│ ├── integrators/ # Numerical integrators (Euler, RK4, RK45)
│ ├── context/ # Simulation context management
│ ├── results/ # Result storage and analysis
│ ├── safety/ # Safety constraint validation
│ └── vector/ # Numba-accelerated vector simulation
├── test_plant/ # Plant dynamics tests (12 files)
│ ├── models/ # Simplified, full, low-rank dynamics
│ ├── configurations/ # Physics parameter configurations
│ ├── core/ # Core dynamics interfaces
│ └── parameters/ # Parameter validation
├── test_optimization/ # Optimization framework tests (10 files)
│ ├── algorithms/ # PSO, GA, differential evolution
│ ├── objectives/ # Cost function design
│ ├── results/ # Optimization result analysis
│ └── core/ # Core optimization interfaces
├── test_utils/ # Utility module tests (18 files)
│ ├── analysis/ # Performance analysis utilities
│ ├── control/ # Control primitives (saturation, deadband)
│ ├── monitoring/ # Real-time monitoring (latency, deadlines)
│ ├── validation/ # Input/output validation
│ ├── visualization/ # Plotting and animation tests
│ ├── types/ # Type system tests
│ └── reproducibility/ # Seed management and determinism
├── test_interfaces/ # HIL and data exchange tests (8 files)
│ ├── core/ # Interface protocols
│ ├── hil/ # Hardware-in-the-loop testing
│ ├── data_exchange/ # Data serialization and exchange
│ ├── hardware/ # Hardware abstraction layer
│ ├── monitoring/ # Interface monitoring
│ └── network/ # Network communication tests
├── test_analysis/ # Analysis infrastructure tests (12 files)
│ ├── core/ # Core analysis pipelines
│ ├── performance/ # Lyapunov, performance metrics
│ ├── fault_detection/ # FDI (Fault Detection & Isolation)
│ ├── validation/ # Cross-validation and Monte Carlo
│ ├── visualization/ # Analysis visualization
│ └── infrastructure/ # Analysis chain orchestration
├── test_config/ # Configuration validation tests (4 files)
├── test_app/ # Application interface tests (8 files)
│ ├── CLI tests (simulate.py)
│ ├── Streamlit dashboard tests
│ ├── Data export functionality
│ └── Visualization tests
├── integration/ # End-to-end integration tests (15 files)
│ ├── PSO-controller integration
│ ├── Factory integration workflows
│ ├── HIL integration scenarios
│ ├── Full simulation pipelines
│ └── Issue regression tests
├── validation/ # Scientific validation tests (5 files)
│ ├── Control theory property tests
│ ├── Stability analysis validation
│ ├── Convergence verification
│ └── Performance benchmarking
└── config_validation/ # Configuration schema tests (3 files)
``` ### 1.2 Test Categories #### 1.2.1 Unit Tests (85 files) **Purpose**: Validate individual components in isolation **Coverage Requirements**:
- **Critical components** (controllers, dynamics): ≥95%
- **Safety-critical** (control saturation, stability): 100%
- **Overall project**: ≥85% **Example**: Controller unit test
```python
# tests/test_controllers/smc/algorithms/classical/test_classical_smc.py

import pytest
import numpy as np
from src.controllers.smc.classic_smc import ClassicalSMC class TestClassicalSMC: """Unit tests for Classical Sliding Mode Controller.""" def test_initialization_valid_parameters(self): """Test controller initialization with valid parameters.""" gains = [10.0, 8.0, 15.0, 12.0, 50.0, 5.0] controller = ClassicalSMC( gains=gains, max_force=100.0, boundary_layer=0.01, dt=0.01 ) assert controller.k1 == 10.0 assert controller.k2 == 8.0 assert controller.lam1 == 15.0 assert controller.lam2 == 12.0 assert controller.K == 50.0 assert controller.kd == 5.0 assert controller.max_force == 100.0 assert controller.boundary_layer == 0.01 def test_compute_control_valid_output(self): """Test that compute_control returns finite, bounded output.""" gains = [10.0, 8.0, 15.0, 12.0, 50.0, 5.0] controller = ClassicalSMC(gains=gains, max_force=100.0, boundary_layer=0.01) state = np.array([0.1, 0.05, 0.08, 0.02, 0.03, 0.01]) result = controller.compute_control(state, {}, {}) control = result.get('control_output', result.get('control', result.get('u'))) assert control is not None assert np.all(np.isfinite(control)) assert np.all(np.abs(control) <= 100.0) # Within saturation def test_gain_validation(self): """Test that invalid gains are rejected.""" # Negative gain should raise ValueError with pytest.raises(ValueError, match="must be positive"): ClassicalSMC( gains=[10.0, -8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, boundary_layer=0.01 ) # Zero gain should raise ValueError with pytest.raises(ValueError, match="must be positive"): ClassicalSMC( gains=[0.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, boundary_layer=0.01 )
``` #### 1.2.2 Integration Tests (35 files) **Purpose**: Validate interactions between multiple components **Scope**:
- End-to-end simulation workflows
- PSO-controller optimization pipelines
- Factory pattern integration
- HIL communication protocols **Example**: PSO-controller integration
```python
# tests/integration/test_pso_controller_integration.py

import pytest
from src.controllers.factory import SMCFactory, SMCType
from src.optimizer.pso_optimizer import PSOTuner class TestPSOControllerIntegration: """Integration tests for PSO optimization of SMC controllers.""" def test_pso_optimization_classical_smc(self): """Test full PSO optimization pipeline for classical SMC.""" # Setup bounds = [(0.1, 50.0)] * 4 + [(1.0, 200.0), (0.0, 50.0)] tuner = PSOTuner( controller_type='classical_smc', bounds=bounds, n_particles=10, iters=5 # Quick test ) # Execute optimization best_gains, best_cost = tuner.optimize() # Validate results assert len(best_gains) == 6 assert all(0.1 <= g <= 200.0 for g in best_gains) assert best_cost < float('inf') assert not np.isnan(best_cost) def test_optimized_controller_performance(self): """Test that PSO-optimized controller stabilizes system.""" # Load PSO-optimized gains optimized_gains = [12.3, 9.1, 18.7, 14.2, 65.3, 7.8] controller = SMCFactory.create_controller( SMCType.CLASSICAL, gains=optimized_gains, max_force=100.0, boundary_layer=0.01 ) # Simulate from src.core.simulation_runner import run_simulation result = run_simulation( controller=controller, duration=5.0, dt=0.01, initial_state=[0.1, 0.1, 0.0, 0.0, 0.0, 0.0] ) # Performance criteria final_state = result['states'][-1] assert np.linalg.norm(final_state) < 0.01 # Stabilized to equilibrium
``` #### 1.2.3 Property-Based Tests (12 files) **Purpose**: Validate mathematical properties across random inputs using Hypothesis **Properties Tested**:
- Linearity of sliding surfaces
- Homogeneity of control laws
- Monotonicity of switching functions
- Boundedness of controller outputs
- Lyapunov function properties **Example**: Property-based sliding surface test
```python
# tests/test_controllers/smc/test_property_based_smc.py

from hypothesis import given, strategies as st
import numpy as np class TestSlidingSurfaceProperties: """Property-based tests for sliding surface mathematics.""" @given( k1=st.floats(min_value=0.1, max_value=50.0), k2=st.floats(min_value=0.1, max_value=50.0), lam1=st.floats(min_value=0.1, max_value=50.0), lam2=st.floats(min_value=0.1, max_value=50.0) ) def test_sliding_surface_linearity(self, k1, k2, lam1, lam2): """Test linearity property: s(x1 + x2) = s(x1) + s(x2).""" gains = [k1, k2, lam1, lam2] surface = LinearSlidingSurface(gains) x1 = np.random.uniform(-1, 1, size=6) x2 = np.random.uniform(-1, 1, size=6) s1 = surface.compute(x1) s2 = surface.compute(x2) s_combined = surface.compute(x1 + x2) # Linearity property within numerical precision assert abs(s_combined - (s1 + s2)) < 1e-10 @given( state=st.lists( st.floats(min_value=-10.0, max_value=10.0), min_size=6, max_size=6 ) ) def test_controller_output_bounded(self, state): """Test that controller output is always bounded for finite input.""" gains = [10.0, 8.0, 15.0, 12.0, 50.0, 5.0] controller = ClassicalSMC(gains=gains, max_force=100.0, boundary_layer=0.01) state_array = np.array(state) if np.all(np.isfinite(state_array)): result = controller.compute_control(state_array, {}, {}) control = result.get('control_output', result.get('control')) if control is not None: # Control must be finite and within saturation limits assert np.all(np.isfinite(control)) assert np.all(np.abs(control) <= 100.0)
``` #### 1.2.4 Performance Benchmarks (18 files) **Purpose**: Regression detection for computational performance **Metrics**:
- Execution time (mean, median, stddev)
- Memory usage (peak, average)
- Throughput (simulations/second)
- Numba compilation overhead **Example**: Controller performance benchmark
```python
# tests/test_benchmarks/performance/test_performance_benchmarks_deep.py

import pytest class TestControllerPerformanceBenchmarks: """Performance benchmarks for controller computations.""" @pytest.mark.benchmark def test_classical_smc_compute_speed(self, benchmark): """Benchmark classical SMC control computation.""" gains = [10.0, 8.0, 15.0, 12.0, 50.0, 5.0] controller = ClassicalSMC(gains=gains, max_force=100.0, boundary_layer=0.01) state = np.array([0.1, 0.05, 0.08, 0.02, 0.03, 0.01]) result = benchmark(controller.compute_control, state, {}, {}) # Performance criteria assert benchmark.stats['mean'] < 1e-4 # < 0.1 ms per control step assert benchmark.stats['stddev'] < 1e-5 # Low variance @pytest.mark.benchmark def test_simulation_throughput(self, benchmark): """Benchmark end-to-end simulation throughput.""" controller = ClassicalSMC( gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, boundary_layer=0.01 ) def run_short_simulation(): return run_simulation( controller=controller, duration=1.0, dt=0.01, initial_state=[0.1, 0.1, 0.0, 0.0, 0.0, 0.0] ) result = benchmark(run_short_simulation) # Throughput criteria (100 timesteps in <100ms) assert benchmark.stats['mean'] < 0.1
``` ### 1.3 Coverage Requirements #### 1.3.1 Overall Coverage Targets ```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term # Coverage thresholds
# Overall project: ≥85%
# Critical components: ≥95%
# Safety-critical: 100%
``` #### 1.3.2 Component-Specific Coverage | Component | Target | Critical | Rationale |

|----------------------------|--------|----------|------------------------------------|
| Controllers (SMC) | 95% | Yes | Safety-critical control algorithms |
| Plant Dynamics | 95% | Yes | Accuracy essential for simulation |
| Simulation Engine | 90% | Yes | Core functionality |
| PSO Optimizer | 85% | No | Performance vs correctness tradeoff|
| Factory Patterns | 90% | No | Dependency injection critical |
| Utilities (control) | 95% | Yes | Saturation, deadband safety |
| Utilities (visualization) | 70% | No | Visual output, non-critical |
| HIL Interfaces | 85% | Yes | Real hardware safety |
| Configuration Validation | 100% | Yes | Invalid config prevents startup | #### 1.3.3 Coverage Reporting ```python
# example-metadata:

# runnable: false # .coveragerc configuration

[run]
source = src
omit = */tests/* */conftest.py */__init__.py [report]
precision = 2
show_missing = True
skip_covered = False [html]
directory = coverage_html_report [term]
missing = True
skip_covered = False
``` ### 1.4 Test Execution Hierarchy ```bash
# Level 1: Smoke Tests (fast, essential validation)
pytest tests/config_validation/ tests/test_config/ -v
# ~30 seconds, validates configuration and core imports # Level 2: Unit Tests (component isolation)
pytest tests/test_controllers/ tests/test_plant/ tests/test_utils/ -v -k "not integration"
# ~5 minutes, 85 unit test files # Level 3: Integration Tests (cross-component validation)
pytest tests/integration/ tests/test_simulation/ -v
# ~10 minutes, 35 integration test files # Level 4: Performance Benchmarks (regression detection)
pytest tests/test_benchmarks/ --benchmark-only
# ~15 minutes, 18 benchmark files # Level 5: Property-Based Tests (extensive randomized testing)
pytest tests/ -k "property" --hypothesis-profile=thorough
# ~20 minutes, 12 property-based test files # Full Test Suite (all levels)
pytest tests/ -v
# ~30 minutes, 143 test files
```

---

## 2. Test Infrastructure ### 2.1 pytest Configuration #### 2.1.1 Setup (pyproject.toml) ```toml

[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"] # Markers for selective test execution
markers = [ "slow: marks tests as slow (deselect with '-m \"not slow\"')", "integration: marks tests as integration tests", "benchmark: marks tests as performance benchmarks", "property: marks tests as property-based (Hypothesis)", "numerical_stability: marks numerical stability tests", "critical: marks safety-critical tests (100% coverage required)",
] # Coverage configuration
addopts = [ "--strict-markers", "--strict-config", "--tb=short", "--disable-warnings", "-ra", # Show summary of all test outcomes
] # Hypothesis configuration
hypothesis_profile = "ci" [tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/conftest.py", "*/__init__.py"] [tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
fail_under = 85 # Enforce minimum coverage
``` #### 2.1.2 Hypothesis Profiles ```python
# tests/conftest.py
from hypothesis import settings, Verbosity # CI profile: fast, deterministic
settings.register_profile("ci", max_examples=50, deadline=500, verbosity=Verbosity.verbose) # Development profile: moderate testing
settings.register_profile("dev", max_examples=100, deadline=1000) # Thorough profile: property testing
settings.register_profile("thorough", max_examples=1000, deadline=5000) # Load profile from environment or default to CI
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "ci"))
``` ### 2.2 Fixture System #### 2.2.1 Session-Scoped Fixtures (conftest.py) ```python
# tests/conftest.py

import pytest
import numpy as np
from pathlib import Path
from types import SimpleNamespace @pytest.fixture(scope="session")
def config(): """Load configuration from config.yaml for tests. Provides session-scoped configuration to avoid repeated file I/O. Backfills controller_defaults gains for core controllers. """ import yaml raw = yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8")) or {} def _to_ns(obj): """Convert dict to SimpleNamespace for attribute access.""" if isinstance(obj, dict): return SimpleNamespace(**{k: _to_ns(v) for k, v in obj.items()}) return obj cfg = _to_ns(raw) # Backfill controller_defaults if missing if not hasattr(cfg, "controller_defaults"): cfg.controller_defaults = SimpleNamespace() # Ensure all core controllers have default gains defaults = { "classical_smc": [10.0, 8.0, 15.0, 12.0, 50.0, 5.0], "adaptive_smc": [10.0, 8.0, 15.0, 12.0, 0.5], "sta_smc": [25.0, 10.0, 15.0, 12.0, 20.0, 15.0], "hybrid_adaptive_sta_smc": [15.0, 12.0, 18.0, 15.0] } for ctrl_name, default_gains in defaults.items(): if not hasattr(cfg.controller_defaults, ctrl_name): setattr(cfg.controller_defaults, ctrl_name, SimpleNamespace(gains=default_gains)) return cfg @pytest.fixture(scope="session")
def physics_cfg(config): """Physics parameters from configuration.""" return config.physics @pytest.fixture(scope="session")
def dynamics_simplified(physics_cfg): """Session-scoped simplified dynamics model.""" from src.core.dynamics import SimplifiedDynamics return SimplifiedDynamics(physics_cfg) @pytest.fixture(scope="session")
def dynamics_full(physics_cfg): """Session-scoped full nonlinear dynamics model.""" from src.core.dynamics_full import FullNonlinearDynamics return FullNonlinearDynamics(physics_cfg)
``` #### 2.2.2 Function-Scoped Fixtures ```python
@pytest.fixture
def initial_state(): """Standard initial state for testing: small perturbation from equilibrium.""" return np.array([0.0, 0.0, 0.1, 0.1, 0.0, 0.0]) @pytest.fixture
def controller_gains_classical(): """Standard classical SMC gains for testing.""" return [10.0, 8.0, 15.0, 12.0, 50.0, 5.0] @pytest.fixture
def make_classical_controller(controller_gains_classical): """Factory fixture for creating classical SMC controllers.""" def _make(**kwargs): from src.controllers.smc.classic_smc import ClassicalSMC default_params = { 'gains': controller_gains_classical, 'max_force': 100.0, 'boundary_layer': 0.01, 'dt': 0.01 } default_params.update(kwargs) return ClassicalSMC(**default_params) return _make @pytest.fixture
def simulation_params(): """Standard simulation parameters for testing.""" return { 'duration': 5.0, 'dt': 0.01, 'max_force': 100.0 }
``` ### 2.3 Headless Matplotlib Enforcement ```python
# tests/conftest.py (top of file, before any imports)

"""
Matplotlib enforcement: headless tests with Agg backend and show-ban.
This file MUST be imported before any test that imports matplotlib.pyplot.
"""
import os
import warnings # 1) Enforce Agg backend as early as possible
os.environ.setdefault("MPLBACKEND", "Agg") import matplotlib
matplotlib.use("Agg", force=True) # 2) Treat Matplotlib warnings as errors
warnings.filterwarnings("error", message=r".*Matplotlib.*", category=UserWarning) def pytest_sessionstart(session): """Verify Agg backend at session start.""" backend = matplotlib.get_backend().lower() assert backend == "agg", ( f"Matplotlib backend is {backend!r}, expected 'agg'. " "Ensure MPLBACKEND=Agg is set before matplotlib import." ) # 3) Runtime ban on plt.show()
import matplotlib.pyplot as plt def _no_show(*args, **kwargs): raise AssertionError( "plt.show() is banned in tests. Use savefig(), return the Figure, " "or use image comparisons." ) plt.show = _no_show # type: ignore[assignment]
``` **Rationale**: Prevents tests from blocking CI/CD pipelines by attempting to display plots. All visualization tests must use `savefig()` or return Figure objects for validation. ### 2.4 Test Isolation #### 2.4.1 Random Seed Management ```python
# tests/conftest.py
import random
import numpy as np @pytest.fixture(autouse=True)
def reset_random_seeds(): """Reset random seeds before each test for reproducibility.""" seed = 42 random.seed(seed) np.random.seed(seed) yield # Cleanup: restore to random state random.seed(None) np.random.seed(None)
``` #### 2.4.2 Temporary Directories ```python

@pytest.fixture
def temp_output_dir(tmp_path): """Provide temporary directory for test outputs.""" output_dir = tmp_path / "test_outputs" output_dir.mkdir() yield output_dir # Cleanup handled automatically by pytest tmp_path
``` #### 2.4.3 Mock External Dependencies ```python
@pytest.fixture
def mock_psutil(monkeypatch): """Mock psutil for systems where it's unavailable.""" try: import psutil yield psutil except ImportError: # Provide fallback mock class MockProcess: def memory_info(self): return type('obj', (object,), {'rss': 1024 * 1024 * 100})() # 100 MB mock_psutil_module = type('obj', (object,), { 'Process': lambda pid: MockProcess() })() monkeypatch.setitem(__import__('sys').modules, 'psutil', mock_psutil_module) yield mock_psutil_module
``` ### 2.5 Parallel Test Execution ```bash
# Install pytest-xdist for parallel execution

pip install pytest-xdist # Run tests in parallel (auto-detect CPU count)
pytest tests/ -n auto # Run tests with 4 workers
pytest tests/ -n 4 # Parallel execution with coverage
pytest tests/ -n auto --cov=src --cov-report=html
``` **Important**: Ensure test isolation when using parallel execution. Avoid shared state and use temporary directories for file I/O.

---

## 3. Unit Testing Patterns ### 3.1 Controller Unit Tests #### 3.1.1 Initialization Validation ```python
# example-metadata:
# runnable: false class TestClassicalSMCInitialization: """Test Classical SMC controller initialization.""" def test_valid_initialization(self): """Test successful initialization with valid parameters.""" gains = [10.0, 8.0, 15.0, 12.0, 50.0, 5.0] controller = ClassicalSMC( gains=gains, max_force=100.0, boundary_layer=0.01, dt=0.01 ) # Verify all parameters stored correctly assert controller.k1 == 10.0 assert controller.k2 == 8.0 assert controller.lam1 == 15.0 assert controller.lam2 == 12.0 assert controller.K == 50.0 assert controller.kd == 5.0 assert controller.max_force == 100.0 assert controller.boundary_layer == 0.01 assert controller.dt == 0.01 def test_invalid_gains_negative(self): """Test that negative gains are rejected.""" with pytest.raises(ValueError, match="must be positive"): ClassicalSMC( gains=[10.0, -8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, boundary_layer=0.01 ) def test_invalid_gains_zero(self): """Test that zero gains are rejected.""" with pytest.raises(ValueError, match="must be positive"): ClassicalSMC( gains=[0.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, boundary_layer=0.01 ) def test_invalid_max_force(self): """Test that invalid max_force is rejected.""" with pytest.raises(ValueError, match="max_force must be positive"): ClassicalSMC( gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=-100.0, boundary_layer=0.01 ) def test_invalid_boundary_layer(self): """Test that invalid boundary_layer is rejected.""" with pytest.raises(ValueError, match="boundary_layer must be positive"): ClassicalSMC( gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, boundary_layer=0.0 )
``` #### 3.1.2 Control Computation Tests ```python
# example-metadata:

# runnable: false class TestClassicalSMCControlComputation: """Test Classical SMC control computation.""" def test_compute_control_valid_output(self): """Test that compute_control returns valid, bounded output.""" controller = ClassicalSMC( gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, boundary_layer=0.01 ) state = np.array([0.1, 0.05, 0.08, 0.02, 0.03, 0.01]) result = controller.compute_control(state, {}, {}) control = result.get('control_output', result.get('control', result.get('u'))) # Validate output properties assert control is not None assert isinstance(control, (float, np.ndarray)) assert np.all(np.isfinite(control)) assert np.all(np.abs(control) <= 100.0) # Within saturation def test_compute_control_equilibrium(self): """Test control at equilibrium (should be near zero).""" controller = ClassicalSMC( gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, boundary_layer=0.01 ) equilibrium = np.zeros(6) result = controller.compute_control(equilibrium, {}, {}) control = result.get('control_output', result.get('control', result.get('u'))) # At equilibrium, control should be minimal if control is not None: assert np.abs(control) < 1.0 # Small control near equilibrium def test_compute_control_large_deviation(self): """Test control with large state deviation (saturation).""" controller = ClassicalSMC( gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, boundary_layer=0.01 ) large_state = np.array([1.0, 0.5, 0.8, 0.3, 0.5, 0.2]) result = controller.compute_control(large_state, {}, {}) control = result.get('control_output', result.get('control', result.get('u'))) # Large deviation should saturate control if control is not None: assert np.abs(control) == pytest.approx(100.0, abs=0.1) def test_compute_control_deterministic(self): """Test that repeated calls produce identical results.""" controller = ClassicalSMC( gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, boundary_layer=0.01 ) state = np.array([0.1, 0.05, 0.08, 0.02, 0.03, 0.01]) results = [] for _ in range(100): result = controller.compute_control(state, {}, {}) control = result.get('control_output', result.get('control', result.get('u'))) if control is not None: results.append(control) results = np.array(results) # All results should be identical (deterministic) std_dev = np.std(results, axis=0) assert np.all(std_dev < 1e-15) # Machine precision

``` ### 3.2 Dynamics Model Tests ```python
class TestSimplifiedDynamics: """Test simplified double-inverted pendulum dynamics.""" def test_initialization(self, physics_cfg): """Test dynamics initialization with physics configuration.""" dynamics = SimplifiedDynamics(physics_cfg) assert dynamics.M == physics_cfg.M assert dynamics.m1 == physics_cfg.m1 assert dynamics.m2 == physics_cfg.m2 assert dynamics.L1 == physics_cfg.L1 assert dynamics.L2 == physics_cfg.L2 assert dynamics.g == physics_cfg.g def test_dynamics_output_shape(self, dynamics_simplified): """Test that dynamics returns correct output shape.""" state = np.array([0.0, 0.0, 0.1, 0.1, 0.0, 0.0]) control = 10.0 state_dot = dynamics_simplified.dynamics(state, control) assert state_dot.shape == (6,) assert np.all(np.isfinite(state_dot)) def test_equilibrium_dynamics(self, dynamics_simplified): """Test dynamics at equilibrium with zero control.""" equilibrium = np.zeros(6) control = 0.0 state_dot = dynamics_simplified.dynamics(equilibrium, control) # At equilibrium with zero control, derivatives should be near zero assert np.linalg.norm(state_dot) < 1e-6 def test_energy_conservation(self, dynamics_simplified): """Test energy conservation for conservative dynamics.""" from src.utils.analysis.energy import compute_total_energy state = np.array([0.0, 0.0, 0.1, 0.1, 0.0, 0.0]) control = 0.0 # No external input # Integrate for short time dt = 0.01 t_span = np.arange(0, 1.0, dt) states = [state] for _ in t_span[1:]: state_dot = dynamics_simplified.dynamics(states[-1], control) states.append(states[-1] + dt * state_dot) states = np.array(states) # Compute energy at each timestep energies = [compute_total_energy(s, dynamics_simplified) for s in states] # Energy should be approximately conserved (no friction) energy_drift = np.max(np.abs(np.diff(energies))) assert energy_drift < 0.01 # Small drift due to Euler integration
``` ### 3.3 Factory Pattern Tests ```python

class TestSMCFactory: """Test SMC controller factory.""" def test_create_classical_smc(self): """Test factory creation of classical SMC.""" from src.controllers.factory import SMCFactory, SMCType controller = SMCFactory.create_controller( SMCType.CLASSICAL, gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, boundary_layer=0.01 ) from src.controllers.smc.classic_smc import ClassicalSMC assert isinstance(controller, ClassicalSMC) assert controller.max_force == 100.0 def test_create_all_controller_types(self): """Test factory can create all SMC types.""" from src.controllers.factory import SMCFactory, SMCType gain_configs = { SMCType.CLASSICAL: [10.0, 8.0, 15.0, 12.0, 50.0, 5.0], SMCType.ADAPTIVE: [10.0, 8.0, 15.0, 12.0, 0.5], SMCType.SUPER_TWISTING: [25.0, 10.0, 15.0, 12.0, 20.0, 15.0], SMCType.HYBRID: [15.0, 12.0, 18.0, 15.0] } for smc_type, gains in gain_configs.items(): controller = SMCFactory.create_controller( smc_type, gains=gains, max_force=100.0, boundary_layer=0.01 ) assert controller is not None assert hasattr(controller, 'compute_control') def test_invalid_controller_type(self): """Test factory raises error for invalid controller type.""" from src.controllers.factory import SMCFactory with pytest.raises((ValueError, KeyError)): SMCFactory.create_controller( "invalid_type", gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0 )
```

---

## 4. Integration Testing ### 4.1 End-to-End Simulation Tests ```python
class TestEndToEndSimulation: """Integration tests for complete simulation workflows.""" def test_full_simulation_pipeline(self): """Test complete simulation from initialization to results.""" from src.controllers.smc.classic_smc import ClassicalSMC from src.core.simulation_runner import run_simulation # Setup controller = ClassicalSMC( gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, boundary_layer=0.01 ) initial_state = [0.0, 0.0, 0.1, 0.1, 0.0, 0.0] # Execute result = run_simulation( controller=controller, duration=5.0, dt=0.01, initial_state=initial_state ) # Validate assert 'time' in result assert 'states' in result assert 'controls' in result assert len(result['time']) == len(result['states']) assert len(result['time']) == len(result['controls']) + 1 # Performance validation final_state = result['states'][-1] assert np.linalg.norm(final_state) < 0.05 # Stabilized def test_simulation_with_disturbance(self): """Test simulation with external disturbance.""" from src.controllers.smc.classic_smc import ClassicalSMC from src.core.simulation_runner import run_simulation controller = ClassicalSMC( gains=[10.0, 8.0, 15.0, 12.0, 50.0, 5.0], max_force=100.0, boundary_layer=0.01 ) # Define disturbance function def disturbance(t): if 1.0 <= t <= 2.0: return 20.0 # Impulse disturbance return 0.0 result = run_simulation( controller=controller, duration=5.0, dt=0.01, initial_state=[0.0, 0.0, 0.1, 0.1, 0.0, 0.0], disturbance=disturbance ) # Controller should recover from disturbance final_state = result['states'][-1] assert np.linalg.norm(final_state) < 0.1 # Recovered
``` ### 4.2 PSO-Controller Integration ```python

class TestPSOIntegration: """Integration tests for PSO optimization workflows.""" def test_pso_optimization_workflow(self): """Test complete PSO optimization workflow.""" from src.optimizer.pso_optimizer import PSOTuner bounds = [(0.1, 50.0)] * 4 + [(1.0, 200.0), (0.0, 50.0)] tuner = PSOTuner( controller_type='classical_smc', bounds=bounds, n_particles=10, iters=5 ) best_gains, best_cost = tuner.optimize() # Validate optimization results assert len(best_gains) == 6 assert all(bounds[i][0] <= best_gains[i] <= bounds[i][1] for i in range(6)) assert best_cost < float('inf') assert not np.isnan(best_cost) def test_optimized_gains_improve_performance(self): """Test that PSO-optimized gains improve performance.""" from src.optimizer.pso_optimizer import PSOTuner from src.controllers.smc.classic_smc import ClassicalSMC from src.core.simulation_runner import run_simulation # Initial (unoptimized) gains initial_gains = [5.0, 5.0, 10.0, 10.0, 30.0, 2.0] # Run PSO optimization bounds = [(0.1, 50.0)] * 4 + [(1.0, 200.0), (0.0, 50.0)] tuner = PSOTuner( controller_type='classical_smc', bounds=bounds, n_particles=10, iters=10 ) optimized_gains, _ = tuner.optimize() # Compare performance def evaluate_performance(gains): controller = ClassicalSMC(gains=gains, max_force=100.0, boundary_layer=0.01) result = run_simulation( controller=controller, duration=5.0, dt=0.01, initial_state=[0.0, 0.0, 0.1, 0.1, 0.0, 0.0] ) # ISE metric states = np.array(result['states']) return np.sum(np.sum(states**2, axis=1) * 0.01) initial_ise = evaluate_performance(initial_gains) optimized_ise = evaluate_performance(optimized_gains) # PSO should improve (reduce) ISE assert optimized_ise < initial_ise
``` ### 4.3 HIL Integration Tests ```python
class TestHILIntegration: """Integration tests for Hardware-in-the-Loop.""" @pytest.mark.slow def test_hil_plant_server_startup(self): """Test HIL plant server can start and accept connections.""" from src.hil.plant_server import PlantServer import threading import time server = PlantServer(port=5555) # Start server in background thread server_thread = threading.Thread(target=server.run, daemon=True) server_thread.start() time.sleep(1.0) # Allow server to start # Verify server is running assert server.is_running() # Cleanup server.shutdown() @pytest.mark.slow def test_hil_controller_client_connection(self): """Test HIL controller client can connect to plant server.""" from src.hil.plant_server import PlantServer from src.hil.controller_client import ControllerClient import threading import time # Start server server = PlantServer(port=5556) server_thread = threading.Thread(target=server.run, daemon=True) server_thread.start() time.sleep(1.0) # Connect client client = ControllerClient(host='localhost', port=5556) connected = client.connect() assert connected # Cleanup client.disconnect() server.shutdown()
```

---

## 5. Test Utilities & Helpers ### 5.1 Custom Assertions ```python

# example-metadata:

# runnable: false # tests/utils/assertions.py def assert_stabilized(final_state, tolerance=0.05): """Assert that final state is stabilized to equilibrium.""" error = np.linalg.norm(final_state) assert error < tolerance, f"System not stabilized: error={error:.4f} > {tolerance}" def assert_control_bounded(control_history, max_force): """Assert that all control values are within saturation limits.""" violations = np.sum(np.abs(control_history) > max_force) assert violations == 0, f"Control violations: {violations} timesteps exceeded {max_force}N" def assert_lyapunov_decreasing(lyapunov_values): """Assert that Lyapunov function is non-increasing.""" diffs = np.diff(lyapunov_values) increasing = np.sum(diffs > 0) assert increasing == 0, f"Lyapunov not decreasing: {increasing} increases detected" def assert_convergence(states, final_tolerance=0.01, settling_time=5.0, dt=0.01): """Assert exponential convergence to equilibrium.""" errors = np.linalg.norm(states, axis=1) final_error = errors[-1] settling_index = int(settling_time / dt) assert final_error < final_tolerance, f"Final error {final_error:.4f} > {final_tolerance}" assert np.all(errors[settling_index:] < final_tolerance), "Not settled within settling time"

``` ### 5.2 Test Data Generators ```python
# example-metadata:
# runnable: false # tests/utils/generators.py def generate_initial_conditions(n_samples=100, max_deviation=0.2): """Generate random initial conditions for robustness testing.""" return np.random.uniform( -max_deviation, max_deviation, size=(n_samples, 6) ) def generate_physics_variations(base_params, uncertainty=0.1, n_samples=50): """Generate physics parameter variations for robustness testing.""" variations = [] for _ in range(n_samples): varied = {} for param, value in base_params.items(): if isinstance(value, (int, float)): variation = value * (1 + np.random.uniform(-uncertainty, uncertainty)) varied[param] = variation else: varied[param] = value variations.append(varied) return variations def generate_disturbance_profiles(duration, dt, disturbance_types=['impulse', 'step', 'ramp']): """Generate disturbance profiles for testing.""" profiles = {} t = np.arange(0, duration, dt) for dist_type in disturbance_types: if dist_type == 'impulse': profile = np.zeros_like(t) impulse_index = len(t) // 2 profile[impulse_index] = 50.0 elif dist_type == 'step': profile = np.where(t > duration/2, 20.0, 0.0) elif dist_type == 'ramp': profile = 10.0 * t / duration profiles[dist_type] = profile return profiles
``` ### 5.3 Mock and Stub Patterns ```python
# example-metadata:

# runnable: false # tests/mocks/mock_controller.py class MockController: """Mock controller for testing simulation framework.""" def __init__(self, control_value=0.0): self.control_value = control_value self.call_count = 0 def compute_control(self, state, state_vars, history): self.call_count += 1 return { 'control_output': self.control_value, 'state_vars': state_vars, 'history': history } def initialize_history(self): return {} class MockDynamics: """Mock dynamics for testing controllers.""" def __init__(self, dynamics_function=None): self.dynamics_function = dynamics_function or (lambda state, control: np.zeros(6)) def dynamics(self, state, control): return self.dynamics_function(state, control)

``` ### 5.4 Error Injection Framework ```python
# example-metadata:
# runnable: false # tests/utils/error_injection.py class ErrorInjector: """Inject errors for fault tolerance testing.""" @staticmethod def inject_nan(state, probability=0.1): """Randomly inject NaN values into state.""" mask = np.random.random(state.shape) < probability corrupted = state.copy() corrupted[mask] = np.nan return corrupted @staticmethod def inject_sensor_noise(state, std_dev=0.01): """Add Gaussian noise to state (sensor noise simulation).""" noise = np.random.normal(0, std_dev, size=state.shape) return state + noise @staticmethod def inject_latency(control_history, delay_steps=1): """Simulate actuator latency by delaying control application.""" if len(control_history) <= delay_steps: return 0.0 return control_history[-(delay_steps + 1)]
```

---

## 6. Quick Reference ### 6.1 Common Test Commands ```bash

# Run all tests

pytest tests/ -v # Run specific test file
pytest tests/test_controllers/smc/algorithms/classical/test_classical_smc.py -v # Run tests matching pattern
pytest tests/ -k "classical" -v # Run tests with specific marker
pytest tests/ -m "integration" -v # Run tests excluding slow tests
pytest tests/ -m "not slow" -v # Run with coverage
pytest tests/ --cov=src --cov-report=html # Run benchmarks only
pytest tests/test_benchmarks/ --benchmark-only # Run property-based tests with thorough profile
pytest tests/ -k "property" --hypothesis-profile=thorough # Parallel execution
pytest tests/ -n auto # Stop on first failure
pytest tests/ -x # Verbose output with full tracebacks
pytest tests/ -vv --tb=long # Show local variables on failure
pytest tests/ -l # Quiet mode (minimal output)
pytest tests/ -q # Run last failed tests
pytest tests/ --lf # Run failed tests first, then rest
pytest tests/ --ff
``` ### 6.2 Coverage Analysis ```bash
# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html
# Open coverage_html_report/index.html # Generate terminal coverage report
pytest tests/ --cov=src --cov-report=term # Coverage with missing line numbers
pytest tests/ --cov=src --cov-report=term-missing # Fail if coverage below 85%
pytest tests/ --cov=src --cov-fail-under=85 # Coverage for specific module
pytest tests/test_controllers/ --cov=src.controllers --cov-report=term
``` ### 6.3 Test Selection Patterns ```bash
# Test specific class

pytest tests/test_controllers/smc/algorithms/classical/test_classical_smc.py::TestClassicalSMC -v # Test specific method
pytest tests/test_controllers/smc/algorithms/classical/test_classical_smc.py::TestClassicalSMC::test_compute_control_valid_output -v # Run tests in directory
pytest tests/test_controllers/ -v # Run tests matching multiple keywords
pytest tests/ -k "classical or adaptive" -v # Run tests with multiple markers
pytest tests/ -m "critical and not slow" -v
``` ### 6.4 Debugging Failed Tests ```bash
# Drop into debugger on failure
pytest tests/ --pdb # Drop into debugger on first failure
pytest tests/ -x --pdb # Capture output (show print statements)
pytest tests/ -s # Show warnings
pytest tests/ -v -W default # Increase verbosity for fixture setup
pytest tests/ -vv --setup-show
```

---

## Summary This testing framework provides: 1. **Coverage**: 143 test files across 22 modules

2. **Multi-Level Testing**: Unit, integration, property-based, performance
3. **Rigorous Quality**: 85% overall, 95% critical, 100% safety-critical coverage
4. **Scientific Rigor**: Mathematical property validation, stability analysis
5. **Reproducibility**: Deterministic seeds, isolated tests, parallel execution
6. **CI/CD Ready**: Automated workflows, regression detection, quality gates **Next**: [Benchmarking Framework Technical Guide](benchmarking_framework_technical_guide.md)
