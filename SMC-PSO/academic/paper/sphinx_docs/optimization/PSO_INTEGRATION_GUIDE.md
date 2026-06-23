# PSO Integration Guide

## Overview

This guide documents the complete PSO (Particle Swarm Optimization) integration for SMC (Sliding Mode Controller) parameter tuning in the double-inverted pendulum control system.

## Quick Start

### Basic PSO Controller Creation

```python
from src.controllers.factory import SMCType, create_smc_for_pso
from src.plant.configurations import ConfigurationFactory

# Create plant configuration
plant_config = ConfigurationFactory.create_default_config("simplified")

# Create controller with PSO-friendly interface
gains = [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]  # 6 gains for Classical SMC
controller = create_smc_for_pso(SMCType.CLASSICAL, gains, plant_config)

# Use simplified control interface
state = np.array([0.1, 0.2, 0.3, 0.0, 0.0, 0.0])
control = controller.compute_control(state)  # Returns np.ndarray([control_value])
```

### PSO Optimization Workflow

```python
from src.controllers.factory import get_gain_bounds_for_pso, validate_smc_gains

# Get optimization bounds
bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL)
lower_bounds, upper_bounds = bounds

# Example PSO fitness function
def fitness_function(gains):
    """PSO fitness function for controller tuning."""
    # Validate gains first
    if not validate_smc_gains(SMCType.CLASSICAL, gains):
        return 1e6  # High penalty for invalid gains

    try:
        # Create controller
        controller = create_smc_for_pso(SMCType.CLASSICAL, gains, plant_config)

        # Evaluate performance across test scenarios
        total_cost = 0.0
        test_states = [
            np.array([0.1, 0.2, 0.3, 0.0, 0.0, 0.0]),
            np.array([0.2, 0.1, 0.4, 0.1, 0.0, 0.0]),
        ]

        for state in test_states:
            control = controller.compute_control(state)
            # Cost function: state error + control effort
            state_cost = np.sum(state[:3]**2)
            control_cost = np.sum(control**2)
            total_cost += state_cost + 0.1 * control_cost

        return total_cost
    except Exception:
        return 1e6  # High penalty for errors

# Use with PySwarms or other PSO libraries
# bounds = (lower_bounds, upper_bounds)
# optimizer.optimize(fitness_function, bounds=bounds)
```

## Architecture

### PSO Integration Components

1. **PSOControllerWrapper**: Simplifies controller interface for PSO usage
2. **create_smc_for_pso()**: Factory function optimized for PSO parameter tuning
3. **get_gain_bounds_for_pso()**: Retrieves optimization bounds for each SMC type
4. **validate_smc_gains()**: Validates gain vectors for stability and correctness

### Supported SMC Types

| SMC Type | Gains Required | Description |
|----------|----------------|-------------|
| CLASSICAL | 6 | [k1, k2, lam1, lam2, K, kd] - Classical SMC with switching and damping |
| ADAPTIVE | 5 | [k1, k2, lam1, lam2, gamma] - Adaptive SMC with online gain adaptation |
| SUPER_TWISTING | 6 | [K1, K2, k1, k2, lam1, lam2] - Super-twisting algorithm |
| HYBRID | 4 | [c1, lambda1, c2, lambda2] - Hybrid adaptive super-twisting |

## Technical Details

### Interface Compatibility

The `PSOControllerWrapper` supports both calling patterns:

```python
# PSO-friendly simplified interface
control = controller.compute_control(state)

# Full interface (backward compatibility)
control_output = controller.compute_control(state, state_vars, history)
```

### Gain Bounds Specifications

Default optimization bounds for each SMC type:

```python
# example-metadata:
# runnable: false

# Classical SMC bounds
CLASSICAL_BOUNDS = {
    'k1': (0.1, 50.0),    # Surface gain 1
    'k2': (0.1, 50.0),    # Surface gain 2
    'lam1': (0.1, 50.0),  # Sliding surface parameter 1
    'lam2': (0.1, 50.0),  # Sliding surface parameter 2
    'K': (1.0, 200.0),    # Switching gain
    'kd': (0.0, 50.0)     # Damping gain (can be zero)
}

# Adaptive SMC bounds
ADAPTIVE_BOUNDS = {
    'k1': (0.1, 50.0),    # Surface gain 1
    'k2': (0.1, 50.0),    # Surface gain 2
    'lam1': (0.1, 50.0),  # Sliding surface parameter 1
    'lam2': (0.1, 50.0),  # Sliding surface parameter 2
    'gamma': (0.01, 10.0) # Adaptation rate
}
```

### Validation Rules

Gain validation enforces SMC stability requirements:

1. **Positive Surface Gains**: First 4 gains must be positive for stability
2. **Appropriate Ranges**: Gains must be within reasonable control engineering ranges
3. **Type-Specific Rules**: Each SMC type has specific validation criteria

## Error Handling

### Common Issues and Approaches

1. **TypeError: 'SimplifiedDIPConfig' object cannot be compared**
   - **Cause**: Passing plant_config as max_force parameter
   - **Solution**: Use `create_smc_for_pso(smc_type, gains, plant_config)` format

2. **ValueError: classical_smc requires at least 6 gains, got 4**
   - **Cause**: Insufficient gains provided for controller type
   - **Solution**: Provide correct number of gains per SMC type specification

3. **AttributeError: compute_control() missing required arguments**
   - **Cause**: Using full controller interface instead of PSO wrapper
   - **Solution**: Use `create_smc_for_pso()` which returns PSO-friendly wrapper

### Debugging Tips

```python
# Check gain requirements
from src.controllers.factory import SMC_GAIN_SPECS
spec = SMC_GAIN_SPECS[SMCType.CLASSICAL]
print(f"Required gains: {spec.n_gains}")
print(f"Gain names: {spec.gain_names}")

# Validate gains before optimization
gains = [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
is_valid = validate_smc_gains(SMCType.CLASSICAL, gains)
print(f"Gains valid: {is_valid}")

# Check bounds format
bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL)
print(f"Bounds format: {type(bounds)}")
print(f"Lower bounds: {bounds[0]}")
print(f"Upper bounds: {bounds[1]}")
```

## Performance Considerations

### PSO Parameter Recommendations

1. **Swarm Size**: 10-30 particles for most problems
2. **Iterations**: 50-200 depending on convergence requirements
3. **Bounds**: Use provided bounds to ensure stable controllers
4. **Fitness Function**: Include both performance and stability metrics

### Optimization Tips

1. **Multi-Objective**: Balance tracking performance vs control effort
2. **Robustness**: Test controllers across multiple scenarios
3. **Validation**: Always validate gains before controller creation
4. **Convergence**: Monitor PSO convergence and adjust parameters

## Integration with Existing Code

### Legacy Compatibility

The new PSO integration maintains backward compatibility:

```python
# Old interface still works
from src.controllers.factory import SMCFactory, SMCConfig
config = SMCConfig(gains=gains, max_force=100.0, dt=0.01)
controller = SMCFactory.create_controller(SMCType.CLASSICAL, config)

# New PSO interface provides simplified access
controller = create_smc_for_pso(SMCType.CLASSICAL, gains, plant_config)
```

### Migration Guide

To migrate existing PSO code:

1. Replace direct factory calls with `create_smc_for_pso()`
2. Update fitness functions to use simplified `compute_control(state)` interface
3. Use `get_gain_bounds_for_pso()` for optimization bounds
4. Add `validate_smc_gains()` checks in fitness functions

## Testing and Validation

### Unit Tests

PSO integration includes tests:

```python
# Run PSO integration tests
python -m pytest tests/test_controllers/factory/test_controller_factory.py::TestPSOIntegration -v

# Run end-to-end validation
python test_pso_integration_workflow.py
```

### Test Coverage

- Controller creation with PSO interface
- Gain bounds retrieval and format validation
- Gain validation with positive and negative test cases
- Multi-SMC type compatibility
- Error handling and edge cases

## References

1. [SMC Controller Factory Documentation](./CONTROLLER_FACTORY.md)
2. [PSO Optimizer Implementation](../src/optimization/algorithms/pso_optimizer.py)
3. [Plant Configuration Guide](./PLANT_CONFIGURATION.md)
4. [Testing Framework Documentation](./TESTING.md)

---

**Generated with Claude Code - PSO Integration Resolution**
