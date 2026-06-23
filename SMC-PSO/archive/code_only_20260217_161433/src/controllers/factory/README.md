# Controller Factory Module

## Overview

The Controller Factory module provides a comprehensive, thread-safe factory system for creating SMC (Sliding Mode Control) controllers with advanced PSO (Particle Swarm Optimization) integration. The module is designed for the double-inverted pendulum control system and includes backwards compatibility, error handling, and performance monitoring.

## Architecture

```
src/controllers/factory/
├── __init__.py                  # Public API and convenience functions
├── factory.py                   # Core factory implementation (moved to parent)
├── fallback_configs.py          # Fallback configuration classes
├── pso_integration.py           # Enhanced PSO integration
├── smc_factory.py              # Clean SMC-specific factory
├── legacy_factory.py           # Legacy compatibility layer
└── README.md                   # This documentation
```

## Core Features

### 1. Thread-Safe Operations
- All factory operations are protected with `threading.RLock()`
- Safe for concurrent use in multi-threaded applications
- Performance monitoring without thread conflicts

### 2. Enhanced PSO Integration
- `EnhancedPSOControllerWrapper`: Advanced wrapper with performance monitoring
- Automatic saturation handling and error recovery
- Statistical tracking and stability estimation
- Real-time performance metrics

### 3. Comprehensive Controller Support
- Classical SMC (6 gains: k1, k2, λ1, λ2, K, kd)
- Super-Twisting SMC (6 gains: K1, K2, k1, k2, λ1, λ2)
- Adaptive SMC (5 gains: k1, k2, λ1, λ2, γ)
- Hybrid Adaptive STA-SMC (4 gains: k1, k2, λ1, λ2)
- Optional MPC Controller (parameter-based)

### 4. Advanced Error Handling
- Graceful degradation with fallback configurations
- Comprehensive input validation
- Physical bounds checking for state vectors
- Safe fallback control algorithms

## Usage Examples

### Basic Controller Creation

```python
from src.controllers.factory import create_controller

# Create a classical SMC controller
controller = create_controller(
    'classical_smc',
    gains=[8.0, 6.0, 4.0, 3.0, 15.0, 2.0]
)

# Use the controller
state = np.array([0.1, 0.05, 0.02, 0.0, 0.0, 0.0])
result = controller.compute_control(state, (), {})
```

### PSO-Compatible Controller Creation

```python
from src.controllers.factory import create_controller_for_pso

# Create enhanced PSO controller
controller = create_controller_for_pso(
    'classical_smc',
    gains=[8.0, 6.0, 4.0, 3.0, 15.0, 2.0],
    enhanced=True  # Use enhanced wrapper
)

# PSO-compatible interface
state = np.array([0.1, 0.05, 0.02, 0.0, 0.0, 0.0])
control = controller.compute_control(state)  # Returns np.array([u])
```

### Advanced PSO Integration

```python
from src.controllers.factory.pso_integration import (
    create_enhanced_pso_controller,
    get_optimized_pso_bounds
)

# Create with performance monitoring
controller = create_enhanced_pso_controller(
    smc_type=SMCType.CLASSICAL,
    gains=[8.0, 6.0, 4.0, 3.0, 15.0, 2.0],
    enable_monitoring=True
)

# Get performance metrics
metrics = controller.get_performance_metrics()
print(f"Average computation time: {metrics.computation_time:.6f}s")
print(f"Success rate: {metrics.success_rate:.2%}")

# Get optimized bounds for PSO
lower, upper = get_optimized_pso_bounds(
    SMCType.CLASSICAL,
    performance_target='balanced'
)
```

### Gain Validation

```python
from src.controllers.factory import validate_controller_gains

# Simple validation
is_valid = validate_controller_gains(
    'classical_smc',
    [8.0, 6.0, 4.0, 3.0, 15.0, 2.0],
    advanced=False
)

# Advanced validation with detailed results
results = validate_controller_gains(
    'classical_smc',
    [8.0, 6.0, 4.0, 3.0, 15.0, 2.0],
    advanced=True
)
print(f"Valid: {results['valid']}")
print(f"Warnings: {results['warnings']}")
print(f"Stability estimate: {results['stability_estimate']}")
```

## Controller Registry

The factory maintains a comprehensive registry of available controllers:

```python
from src.controllers.factory import CONTROLLER_REGISTRY, list_available_controllers

# List all available controllers
controllers = list_available_controllers()
print(controllers)  # ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']

# Get controller information
info = CONTROLLER_REGISTRY['classical_smc']
print(f"Gain count: {info['gain_count']}")
print(f"Description: {info['description']}")
print(f"Required params: {info['required_params']}")
```

## Performance Monitoring

The enhanced PSO wrapper provides comprehensive performance monitoring:

```python
# Performance metrics available
class PSOPerformanceMetrics:
    computation_time: float    # Average computation time per call
    control_effort: float      # RMS control effort
    stability_margin: float    # Estimated stability margin
    success_rate: float        # Success rate of computations
    error_count: int          # Number of computation errors

# Access metrics
controller = create_enhanced_pso_controller(...)
metrics = controller.get_performance_metrics()

# Reset metrics for new evaluation
controller.reset_metrics()
```

## Safety Features

### Input Validation
- State vector shape and finite value checking
- Physical bounds validation for cart position and pendulum angles
- Gain positivity and finite value validation

### Control Saturation
- Automatic force saturation within actuator limits
- Rate limiting to prevent excessive control changes
- Safe fallback control for error conditions

### Error Recovery
- Graceful degradation when controllers fail
- Safe fallback control using simple PD laws
- Comprehensive error logging and reporting

## Backwards Compatibility

The factory maintains full backwards compatibility with existing code:

```python
# Legacy interfaces still work
from src.controllers.factory import (
    create_controller_legacy,
    SMCFactory,
    create_smc_for_pso
)

# Old-style creation
controller = create_controller_legacy('classical_smc', gains=[...])

# Legacy PSO interface
wrapper = create_smc_for_pso(SMCType.CLASSICAL, gains=[...])
```

## Thread Safety

All factory operations are thread-safe:

```python
import threading
from src.controllers.factory import create_controller

def worker_thread():
    # Safe to call from multiple threads
    controller = create_controller('classical_smc', gains=[...])
    # Use controller...

# Create multiple threads
threads = [threading.Thread(target=worker_thread) for _ in range(10)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
```

## Configuration Management

### Automatic Configuration Creation
The factory automatically creates appropriate configuration objects based on controller type and provided parameters.

### Fallback Configurations
When full configuration classes are not available, the factory uses minimal fallback configurations to ensure graceful operation.

### Dynamic Parameter Injection
Controller-specific parameters are automatically added based on controller type:

- **Classical SMC**: `boundary_layer`, `switch_method`
- **STA SMC**: `power_exponent`, `regularization`, `damping_gain`
- **Adaptive SMC**: `leak_rate`, `dead_zone`, `adaptation_bounds`
- **Hybrid SMC**: Sub-controller configurations

## Error Handling

The factory provides comprehensive error handling:

```python
try:
    controller = create_controller('invalid_type', gains=[...])
except ValueError as e:
    print(f"Controller creation failed: {e}")
    # Error message includes available controller types

try:
    wrapper = create_controller_for_pso('classical_smc', gains=[1, 2])  # Wrong count
except ValueError as e:
    print(f"Gain validation failed: {e}")
    # Error message explains expected gain count
```

## Testing

The factory includes comprehensive test coverage:

- Unit tests for all factory functions
- Integration tests with plant dynamics
- Thread safety validation
- Performance regression testing
- Memory leak detection
- Error condition testing

## Future Extensions

The factory architecture supports easy extension:

1. **New Controller Types**: Add to `CONTROLLER_REGISTRY` with metadata
2. **Enhanced PSO Features**: Extend `EnhancedPSOControllerWrapper`
3. **Additional Validation**: Extend validation functions
4. **Performance Metrics**: Add new metrics to `PSOPerformanceMetrics`

## Dependencies

- `numpy`: Numerical operations
- `threading`: Thread safety
- `typing`: Type hints
- `dataclasses`: Configuration structures
- `logging`: Error reporting and debugging

## Version History

- **v2.0.0**: Major refactor with enhanced PSO integration and thread safety
- **v1.x.x**: Legacy versions with basic factory functionality