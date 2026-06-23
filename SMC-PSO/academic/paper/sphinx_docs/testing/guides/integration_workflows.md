<!--======================================================================================\\\
================ docs/testing/guides/integration_workflows.md ========================\\\
=======================================================================================-->

# Integration Testing Workflows

**Purpose**: End-to-end integration testing patterns for control systems, covering controller-dynamics integration, PSO tuning workflows, and HIL validation.



## 🎯 Integration Test Categories

### 1. Controller-Dynamics Integration

```python
# example-metadata:
# runnable: false

def test_closed_loop_integration():
    """Test full closed-loop system"""
    controller = ClassicalSMC(gains=[77.62, 44.45, 17.31, 14.25, 18.66, 9.76])
    dynamics = FullDynamics()
    initial_state = [0.2, -0.1, 0.0, 0.0]

    # Simulate closed loop
    trajectory = simulate(
        controller=controller,
        dynamics=dynamics,
        initial_state=initial_state,
        duration=5.0,
        dt=0.01
    )

    # Integration assertions
    final_state = trajectory[-1]
    assert np.linalg.norm(final_state) < 0.05, "Did not stabilize"

    # Check no integration errors
    assert len(trajectory) == 500, "Unexpected trajectory length"
    assert all(is_valid_state(s) for s in trajectory), "Invalid states generated"
```



### 2. PSO-Controller Integration

```python
# example-metadata:
# runnable: false

def test_pso_tuning_workflow():
    """Test complete PSO tuning pipeline"""
    # Define optimization problem
    bounds = [(1, 100), (1, 100), (1, 100), (1, 100), (1, 100), (0.1, 10)]

    def fitness(gains):
        controller = ClassicalSMC(gains=gains)
        cost = evaluate_controller(controller, test_scenarios)
        return cost

    # Run PSO
    tuner = PSOTuner(n_particles=30, iterations=50, bounds=bounds)
    result = tuner.optimize(fitness)

    # Validate result
    assert result['cost'] < 1.0, "PSO did not find good solution"
    assert len(result['best_gains']) == 6, "Incorrect number of gains"

    # Test optimized controller
    optimized_controller = ClassicalSMC(gains=result['best_gains'])
    performance = evaluate_controller(optimized_controller, validation_scenarios)
    assert performance < 0.5, "Optimized controller underperforms"
```



### 3. Configuration Loading Integration

```python
# example-metadata:
# runnable: false

def test_config_to_simulation_workflow():
    """Test configuration → controller → simulation pipeline"""
    # Load config
    config = load_config("config.yaml")

    # Create controller from config
    controller = create_controller(
        config['control']['type'],
        config=config['control']['classical_smc']
    )

    # Create dynamics from config
    dynamics = DoublePendulum(
        m1=config['plant']['m1'],
        l1=config['plant']['l1'],
        # ... other params
    )

    # Run simulation
    results = run_simulation(controller, dynamics, config['simulation'])

    # Integration checks
    assert results['success'], "Simulation failed"
    assert 'trajectory' in results, "Missing trajectory data"
    assert results['settling_time'] < 3.0, "Took too long to settle"
```



## 🏗️ Workflow Patterns

### Pattern 1: Factory-Based Integration

```python
# example-metadata:
# runnable: false

@pytest.fixture
def integrated_system():
    """Fixture providing fully integrated system"""
    config = load_test_config()

    return {
        'controller': create_controller_from_config(config),
        'dynamics': create_dynamics_from_config(config),
        'observer': create_observer_from_config(config),
        'reference': create_reference_from_config(config)
    }

def test_with_integrated_system(integrated_system):
    results = run_closed_loop(integrated_system)
    assert results['tracking_error'] < 0.01
```



## Pattern 2: Multi-Stage Validation

```python
# example-metadata:
# runnable: false

def test_multi_stage_integration():
    """Progressive integration testing"""
    # Stage 1: Unit level
    controller = ClassicalSMC(gains=[10, 5, 8])
    assert controller.compute_control([0.1, 0, 0, 0]) is not None

    # Stage 2: Subsystem integration
    dynamics = SimplifiedDynamics()
    state = [0.1, 0, 0, 0]
    u = controller.compute_control(state)
    next_state = dynamics.step(state, u, 0.01)
    assert dynamics.is_valid_state(next_state)

    # Stage 3: Full system integration
    trajectory = simulate(controller, dynamics, state, duration=1.0)
    assert len(trajectory) > 0

    # Stage 4: Performance validation
    metrics = analyze_performance(trajectory)
    assert metrics['settling_time'] < 2.0
```



## 📊 Integration Test Scenarios

### Scenario 1: Nominal Operation

```python
# example-metadata:
# runnable: false

@pytest.mark.integration
def test_nominal_stabilization():
    """Baseline integration test"""
    initial_states = [
        [0.1, 0, 0, 0],
        [0, 0.1, 0, 0],
        [-0.1, -0.1, 0, 0]
    ]

    for state in initial_states:
        trajectory = simulate(controller, dynamics, state, duration=5.0)
        final_error = np.linalg.norm(trajectory[-1])
        assert final_error < 0.05, f"Failed for initial state {state}"
```



## Scenario 2: Disturbance Rejection

```python
# example-metadata:
# runnable: false

def test_disturbance_rejection_integration():
    """Integration test with external disturbances"""
    state = [0, 0, 0, 0]

    for t in np.arange(0, 5.0, 0.01):
        # Apply disturbance at t=2.5s
        disturbance = 0.5 if 2.5 <= t < 2.6 else 0

        u = controller.compute_control(state)
        u_total = u + disturbance

        state = dynamics.step(state, u_total, dt=0.01)

    # Should recover despite disturbance
    assert np.linalg.norm(state) < 0.1, "Failed to reject disturbance"
```



### Scenario 3: Parameter Variation

```python
@pytest.mark.parametrize("mass_error", [0.8, 0.9, 1.1, 1.2])
def test_robust_integration(mass_error):
    """Integration test with plant uncertainties"""
    perturbed_dynamics = DoublePendulum(
        m1=M1_NOMINAL * mass_error,
        m2=M2_NOMINAL * mass_error
    )

    trajectory = simulate(controller, perturbed_dynamics, [0.2, 0, 0, 0], 5.0)
    assert np.linalg.norm(trajectory[-1]) < 0.1
```



## 🔧 CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run integration tests
        run: pytest tests/integration/ -v --tb=short

      - name: Generate integration report
        run: pytest tests/integration/ --html=integration_report.html
```



## 📚 Related Documentation

- [Control Systems Unit Testing](control_systems_unit_testing.md)
- [Property-Based Testing](property_based_testing.md)
- [Performance Benchmarking](performance_benchmarking.md)



## 🔗 Navigation

[⬅️ Back to Guides](../guides/) | [🏠 Testing Home](../README.md) | [➡️ Testing Standards](../standards/testing_standards.md)



**Last Updated**: September 30, 2025
**Maintainer**: Integration Testing Team