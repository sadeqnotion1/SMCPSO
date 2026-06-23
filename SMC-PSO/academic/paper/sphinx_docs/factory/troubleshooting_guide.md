#==========================================================================================\\\
#==================== docs/factory/troubleshooting_guide.md ========================\\\
#==========================================================================================\\\

# Factory Troubleshooting and Diagnostics Guide
## GitHub Issue #6 Factory Integration Resolution ### Overview This troubleshooting guide addresses common issues, diagnostic procedures, and approaches for the enhanced controller factory system implemented in GitHub Issue #6 resolution. The guide is organized by symptom categories with systematic diagnostic workflows and validated solutions. ## Quick Diagnostic Checklist ### 🔍 **Immediate Health Check** Run this diagnostic script to quickly identify factory system status: ```python

from src.controllers.factory import ( list_available_controllers, get_default_gains, create_controller
)
import numpy as np def factory_health_check(): """factory system health check.""" print("=== Factory System Health Check ===\n") # 1. Check available controllers try: controllers = list_available_controllers() print(f"✓ Available controllers: {controllers}") except Exception as e: print(f"✗ Controller registry error: {e}") return False # 2. Test default gains retrieval for controller_type in controllers: try: gains = get_default_gains(controller_type) print(f"✓ {controller_type} default gains: {gains}") except Exception as e: print(f"✗ {controller_type} gains error: {e}") # 3. Test controller creation test_passed = 0 total_tests = len(controllers) for controller_type in controllers: try: gains = get_default_gains(controller_type) controller = create_controller(controller_type, gains=gains) # Test basic functionality test_state = np.array([0.1, 0.1, 0.0, 0.0, 0.0, 0.0]) result = controller.compute_control(test_state, (), {}) if hasattr(result, 'u'): control_value = result.u else: control_value = result if np.isfinite(control_value): print(f"✓ {controller_type} creation and test successful") test_passed += 1 else: print(f"✗ {controller_type} produced invalid control: {control_value}") except Exception as e: print(f"✗ {controller_type} creation failed: {e}") # 4. Summary success_rate = (test_passed / total_tests) * 100 print(f"\n=== Summary ===") print(f"Controllers tested: {total_tests}") print(f"Successful: {test_passed}") print(f"Success rate: {success_rate:.1f}%") if success_rate >= 95: print("✓ Factory system is healthy") return True elif success_rate >= 75: print("⚠ Factory system has minor issues") return False else: print("✗ Factory system has major issues") return False # Run the health check
factory_health_check()
``` ## Common Error Categories ### 1. Controller Creation Errors #### Error: "Unknown controller type 'X'" **Symptoms:**
```

ValueError: Unknown controller type 'xyz'. Available: ['classical_smc', 'sta_smc', ...]
``` **Diagnosis:**
```python

from src.controllers.factory import list_available_controllers, CONTROLLER_ALIASES def diagnose_controller_type_error(controller_type): print(f"Diagnosing controller type: '{controller_type}'") # Check available types available = list_available_controllers() print(f"Available types: {available}") # Check aliases normalized = controller_type.lower().replace('-', '_').replace(' ', '_') if normalized in CONTROLLER_ALIASES: canonical = CONTROLLER_ALIASES[normalized] print(f"Found alias: '{controller_type}' -> '{canonical}'") else: print(f"No alias found for '{controller_type}'") # Suggest closest match from difflib import get_close_matches matches = get_close_matches(normalized, available + list(CONTROLLER_ALIASES.keys())) if matches: print(f"Did you mean: {matches[0]}?") # Example usage
diagnose_controller_type_error("classic_smc") # Should find alias
``` **Solutions:**
1. **Use correct controller type**: Check `list_available_controllers()`
2. **Use supported aliases**: `'classic_smc'` → `'classical_smc'`
3. **Check spelling**: Common typos in controller names #### Error: "Controller requires X gains, got Y" **Symptoms:**
```

ValueError: Controller 'Classical sliding mode controller' requires 6 gains, got 5
``` **Diagnosis:**
```python

from src.controllers.factory import CONTROLLER_REGISTRY def diagnose_gain_count_error(controller_type, provided_gains): print(f"Diagnosing gain count for {controller_type}") if controller_type in CONTROLLER_REGISTRY: info = CONTROLLER_REGISTRY[controller_type] required = info['gain_count'] provided = len(provided_gains) print(f"Required gains: {required}") print(f"Provided gains: {provided}") print(f"Gain names: {info.get('gain_names', 'Not specified')}") if provided < required: print(f"Missing {required - provided} gains") defaults = info['default_gains'] suggested = provided_gains + defaults[provided:required] print(f"Suggested gains: {suggested}") elif provided > required: print(f"Extra {provided - required} gains provided") suggested = provided_gains[:required] print(f"Suggested gains: {suggested}") else: print(f"Unknown controller type: {controller_type}") # Example usage
diagnose_gain_count_error('classical_smc', [10, 5, 8]) # Too few gains
``` **Solutions:**
1. **Classical SMC**: Requires 6 gains `[k1, k2, λ1, λ2, K, kd]`
2. **Adaptive SMC**: Requires 5 gains `[k1, k2, λ1, λ2, γ]`
3. **Super-Twisting SMC**: Requires 6 gains `[K1, K2, k1, k2, λ1, λ2]`
4. **Hybrid SMC**: Requires 4 gains `[k1, k2, λ1, λ2]` #### Error: "All gains must be positive" **Symptoms:**
```

ValueError: All gains must be positive
``` **Diagnosis:**
```python
# example-metadata:

# runnable: false def diagnose_gain_values(gains): print(f"Diagnosing gain values: {gains}") for i, gain in enumerate(gains): if not isinstance(gain, (int, float)): print(f"✗ Gain {i}: {gain} is not numeric (type: {type(gain)})") elif not np.isfinite(gain): print(f"✗ Gain {i}: {gain} is not finite") elif gain <= 0: print(f"✗ Gain {i}: {gain} is not positive") else: print(f"✓ Gain {i}: {gain} is valid") # Example usage

diagnose_gain_values([10.0, -5.0, float('inf'), 'invalid', 8.0])
``` **Solutions:**
1. **Check for negative values**: All SMC gains must be positive for stability
2. **Check for infinite/NaN values**: Use `np.isfinite()` to validate
3. **Check data types**: Ensure all gains are numeric ### 2. Configuration Errors #### Error: "Config validation failed" **Symptoms:**
```

ValidationError: Missing required parameter 'boundary_layer' for classical_smc
``` **Diagnosis:**
```python
# example-metadata:

# runnable: false def diagnose_config_validation(controller_type, config_params): print(f"Diagnosing configuration for {controller_type}") required_params = { 'classical_smc': ['gains', 'max_force', 'boundary_layer', 'dt'], 'adaptive_smc': ['gains', 'max_force', 'dt', 'leak_rate', 'adapt_rate_limit'], 'sta_smc': ['gains', 'max_force', 'dt', 'power_exponent'], 'hybrid_adaptive_sta_smc': ['gains', 'hybrid_mode', 'dt', 'max_force'] } if controller_type in required_params: required = required_params[controller_type] provided = list(config_params.keys()) missing = set(required) - set(provided) extra = set(provided) - set(required) if missing: print(f"✗ Missing required parameters: {list(missing)}") if extra: print(f"ℹ Extra parameters (optional): {list(extra)}") for param in required: if param in config_params: value = config_params[param] print(f"✓ {param}: {value}") else: print(f"✗ {param}: MISSING") else: print(f"No validation rules for {controller_type}") # Example usage

config = {'gains': [10, 5, 8, 3, 15, 2], 'max_force': 150.0}
diagnose_config_validation('classical_smc', config)
``` **Solutions:**
1. **Add missing parameters**: Check required parameters for each controller type
2. **Use default values**: Factory provides sensible defaults for optional parameters
3. **Validate parameter types**: Ensure correct data types (float, bool, etc.) #### Error: "Deprecated parameter warning" **Symptoms:**
```

DeprecationWarning: Parameter 'switch_function' deprecated, use 'switch_method'
``` **Diagnosis:**
```python

from src.controllers.factory.deprecation import get_controller_migration_guide def diagnose_deprecation_warnings(controller_type): print(f"Checking deprecation warnings for {controller_type}") migration_guide = get_controller_migration_guide(controller_type) if migration_guide: print("Migration guide:") for instruction in migration_guide: print(f" - {instruction}") else: print("No deprecation warnings for this controller type") # Example usage
diagnose_deprecation_warnings('classical_smc')
``` **Solutions:**
1. **Update parameter names**: Use new parameter names to avoid warnings
2. **Automatic migration**: Factory automatically migrates most deprecated parameters
3. **Check migration guide**: Use `get_controller_migration_guide()` for specific instructions ### 3. PSO Integration Errors #### Error: "PSO factory creation failed" **Symptoms:**
```

AttributeError: 'function' object has no attribute 'n_gains'
``` **Diagnosis:**
```python

from src.controllers.factory import create_pso_controller_factory, SMCType def diagnose_pso_factory_error(smc_type): print(f"Diagnosing PSO factory for {smc_type}") try: factory_func = create_pso_controller_factory(smc_type) # Check required attributes required_attrs = ['n_gains', 'controller_type', 'max_force'] for attr in required_attrs: if hasattr(factory_func, attr): value = getattr(factory_func, attr) print(f"✓ {attr}: {value}") else: print(f"✗ Missing attribute: {attr}") # Test factory function from src.controllers.factory import get_default_gains test_gains = get_default_gains(smc_type.value) controller = factory_func(test_gains) print(f"✓ Factory function test successful") except Exception as e: print(f"✗ PSO factory creation failed: {e}") # Example usage
diagnose_pso_factory_error(SMCType.CLASSICAL)
``` **Solutions:**
1. **Use SMCType enum**: Use proper enum values instead of strings
2. **Check factory attributes**: Ensure factory function has required PSO attributes
3. **Validate gains compatibility**: Test factory with valid gain arrays #### Error: "PSO bounds validation failed" **Symptoms:**
```

ValueError: Gain bounds validation failed for particle
``` **Diagnosis:**
```python

from src.controllers.factory import get_gain_bounds_for_pso, validate_smc_gains def diagnose_pso_bounds_error(smc_type, particle_gains): print(f"Diagnosing PSO bounds for {smc_type}") # Get expected bounds lower_bounds, upper_bounds = get_gain_bounds_for_pso(smc_type) print(f"Expected bounds:") print(f" Lower: {lower_bounds}") print(f" Upper: {upper_bounds}") print(f"Particle gains: {particle_gains}") # Check each gain for i, (gain, lower, upper) in enumerate(zip(particle_gains, lower_bounds, upper_bounds)): if gain < lower: print(f"✗ Gain {i}: {gain} < {lower} (too low)") elif gain > upper: print(f"✗ Gain {i}: {gain} > {upper} (too high)") else: print(f"✓ Gain {i}: {gain} within bounds [{lower}, {upper}]") # Overall validation is_valid = validate_smc_gains(smc_type, particle_gains) print(f"Overall validation: {'PASS' if is_valid else 'FAIL'}") # Example usage
diagnose_pso_bounds_error(SMCType.CLASSICAL, [100, 50, 30, 25, 200, 15]) # Out of bounds
``` **Solutions:**
1. **Use correct bounds**: Get bounds from `get_gain_bounds_for_pso()`
2. **Validate particles**: Pre-validate gains before expensive simulation
3. **Adjust PSO parameters**: Modify PSO bounds or constraints ### 4. Thread Safety Issues #### Error: "Thread lock timeout" **Symptoms:**
```

TimeoutError: Factory lock acquisition timeout after 10 seconds
``` **Diagnosis:**
```python

import threading
import time
from src.controllers.factory import create_controller def diagnose_thread_safety_issues(): print("Diagnosing thread safety issues") def blocking_operation(): # Simulate long-running operation controller = create_controller('classical_smc', gains=[10]*6) time.sleep(5) # Simulate work return controller # Test concurrent access start_time = time.time() threads = [] for i in range(5): thread = threading.Thread(target=blocking_operation) threads.append(thread) thread.start() time.sleep(0.1) # Stagger starts for thread in threads: thread.join(timeout=15) if thread.is_alive(): print(f"✗ Thread still running after timeout") else: print(f"✓ Thread completed successfully") total_time = time.time() - start_time print(f"Total execution time: {total_time:.2f} seconds") if total_time > 30: print("⚠ Possible deadlock or contention detected") else: print("✓ Thread safety test completed normally") # Run diagnostic
diagnose_thread_safety_issues()
``` **Solutions:**
1. **Avoid long-running operations**: Keep factory calls brief
2. **Use timeouts**: Set appropriate timeouts for lock acquisition
3. **Check for deadlocks**: Avoid nested lock acquisition patterns ### 5. Import and Dependency Errors #### Error: "ModuleNotFoundError" **Symptoms:**
```

ModuleNotFoundError: No module named 'src.controllers.smc.algorithms.classical.config'
``` **Diagnosis:**
```python

import sys
import importlib.util def diagnose_import_errors(): print("Diagnosing import errors") critical_modules = [ 'src.controllers.factory', 'src.controllers.smc.algorithms.classical.controller', 'src.controllers.smc.algorithms.adaptive.controller', 'src.controllers.smc.algorithms.super_twisting.controller', 'src.controllers.smc.algorithms.hybrid.controller' ] for module_name in critical_modules: try: spec = importlib.util.find_spec(module_name) if spec is None: print(f"✗ Module not found: {module_name}") else: print(f"✓ Module available: {module_name}") # Try importing module = importlib.import_module(module_name) print(f" ✓ Import successful") except ImportError as e: print(f"✗ Import error for {module_name}: {e}") except Exception as e: print(f"✗ Unexpected error for {module_name}: {e}") # Check Python path print(f"\nPython path:") for path in sys.path: print(f" - {path}") # Run diagnostic
diagnose_import_errors()
``` **Solutions:**
1. **Check PYTHONPATH**: Ensure `src/` directory is in Python path
2. **Verify file structure**: Check that all required files exist
3. **Install dependencies**: Run `pip install -r requirements.txt` #### Error: "Optional dependency missing" **Symptoms:**
```

ImportError: MPC controller is not available. Check dependencies.
``` **Diagnosis:**
```python
# example-metadata:

# runnable: false def diagnose_optional_dependencies(): print("Checking optional dependencies") optional_deps = { 'casadi': 'MPC controller', 'control': 'Advanced control features', 'cvxpy': 'Optimization-based controllers' } for package, feature in optional_deps.items(): try: importlib.import_module(package) print(f"✓ {package} available - {feature} supported") except ImportError: print(f"✗ {package} missing - {feature} not available") # Run diagnostic

diagnose_optional_dependencies()
``` **Solutions:**
1. **Install optional dependencies**: `pip install casadi control cvxpy`
2. **Use fallback controllers**: Use available controller types
3. **Check feature flags**: Verify optional features are properly handled ## Performance Diagnostics ### Factory Performance Profiling ```python
import time
import statistics
from src.controllers.factory import create_controller, get_default_gains def profile_factory_performance(): print("Profiling factory performance") controller_types = ['classical_smc', 'adaptive_smc', 'sta_smc'] results = {} for controller_type in controller_types: print(f"\nTesting {controller_type}:") gains = get_default_gains(controller_type) creation_times = [] # Warmup for _ in range(5): create_controller(controller_type, gains=gains) # Actual measurements for i in range(20): start_time = time.perf_counter() controller = create_controller(controller_type, gains=gains) end_time = time.perf_counter() creation_time = (end_time - start_time) * 1000 # Convert to ms creation_times.append(creation_time) # Statistics mean_time = statistics.mean(creation_times) std_time = statistics.stdev(creation_times) min_time = min(creation_times) max_time = max(creation_times) results[controller_type] = { 'mean': mean_time, 'std': std_time, 'min': min_time, 'max': max_time } print(f" Mean: {mean_time:.2f} ms") print(f" Std: {std_time:.2f} ms") print(f" Min: {min_time:.2f} ms") print(f" Max: {max_time:.2f} ms") # Performance assessment if mean_time > 10: print(f" ⚠ Slow creation time (>{10}ms)") else: print(f" ✓ Acceptable creation time") return results # Run performance profiling
profile_results = profile_factory_performance()
``` ### Memory Usage Diagnostics ```python

import psutil
import os
from src.controllers.factory import create_controller def diagnose_memory_usage(): print("Diagnosing memory usage") process = psutil.Process(os.getpid()) initial_memory = process.memory_info().rss / 1024 / 1024 # MB print(f"Initial memory usage: {initial_memory:.2f} MB") controllers = [] memory_measurements = [] for i in range(100): controller = create_controller('classical_smc', gains=[10]*6) controllers.append(controller) if i % 10 == 0: current_memory = process.memory_info().rss / 1024 / 1024 memory_measurements.append(current_memory) print(f"After {i+1} controllers: {current_memory:.2f} MB") final_memory = process.memory_info().rss / 1024 / 1024 memory_increase = final_memory - initial_memory print(f"Final memory usage: {final_memory:.2f} MB") print(f"Memory increase: {memory_increase:.2f} MB") print(f"Memory per controller: {memory_increase/100:.3f} MB") # Check for memory leaks if memory_increase > 50: # More than 50MB for 100 controllers print("⚠ Possible memory leak detected") else: print("✓ Memory usage within acceptable limits") # Run memory diagnostic
diagnose_memory_usage()
``` ## Systematic Troubleshooting Workflow ### Step 1: Identify Problem Category ```python
# example-metadata:
# runnable: false def categorize_problem(error_message): """Categorize problem based on error message.""" categories = { 'creation': ['Unknown controller type', 'requires.*gains', 'Invalid parameter'], 'configuration': ['Config validation', 'Missing.*parameter', 'Deprecated parameter'], 'pso': ['PSO factory', 'bounds validation', 'n_gains'], 'threading': ['lock timeout', 'deadlock', 'thread'], 'import': ['ModuleNotFoundError', 'ImportError', 'No module named'], 'performance': ['timeout', 'slow', 'memory'] } error_lower = error_message.lower() for category, keywords in categories.items(): for keyword in keywords: if keyword.lower() in error_lower: return category return 'unknown' # Example usage
error = "Controller 'classical_smc' requires 6 gains, got 5"
category = categorize_problem(error)
print(f"Problem category: {category}")
``` ### Step 2: Gather Diagnostic Information ```python

def gather_diagnostic_info(): """Gather diagnostic information.""" import sys import platform import numpy as np info = { 'system': { 'platform': platform.platform(), 'python_version': sys.version, 'numpy_version': np.__version__ }, 'factory': {}, 'performance': {}, 'errors': [] } # Factory information try: from src.controllers.factory import list_available_controllers, CONTROLLER_REGISTRY info['factory']['available_controllers'] = list_available_controllers() info['factory']['registry_size'] = len(CONTROLLER_REGISTRY) except Exception as e: info['errors'].append(f"Factory info error: {e}") # Performance information try: start_time = time.perf_counter() create_controller('classical_smc', gains=[10]*6) creation_time = (time.perf_counter() - start_time) * 1000 info['performance']['creation_time_ms'] = creation_time except Exception as e: info['errors'].append(f"Performance test error: {e}") return info # Gather diagnostic information
diagnostic_info = gather_diagnostic_info()
print("Diagnostic information gathered:")
for category, data in diagnostic_info.items(): print(f" {category}: {data}")
``` ### Step 3: Apply Category-Specific approaches ```python
# example-metadata:
# runnable: false def apply_solutions(category, error_details): """Apply category-specific solutions.""" approaches = { 'creation': [ "Check controller type spelling and available types", "Verify gain array length matches controller requirements", "Ensure all gains are positive finite numbers" ], 'configuration': [ "Add missing required parameters", "Update deprecated parameter names", "Validate parameter types and ranges" ], 'pso': [ "Use SMCType enum instead of string", "Check PSO bounds and particle validation", "Verify factory function has required attributes" ], 'threading': [ "Reduce lock hold time", "Check for nested lock acquisition", "Use timeouts for lock operations" ], 'import': [ "Check PYTHONPATH includes src/ directory", "Verify all required files exist", "Install missing dependencies" ], 'performance': [ "Profile controller creation times", "Check for memory leaks", "Optimize hot code paths" ] } category_solutions = solutions.get(category, ["Unknown category - manual investigation required"]) print(f"Recommended approaches for {category} problems:") for i, solution in enumerate(category_solutions, 1): print(f" {i}. {solution}") return category_solutions # Example usage
category = 'creation'
approaches = apply_solutions(category, "gain count mismatch")
``` ## Prevention and Best Practices ### 1. Proactive Error Prevention ```python

def validate_before_creation(controller_type, gains, config=None): """pre-creation validation.""" from src.controllers.factory import ( list_available_controllers, CONTROLLER_REGISTRY, validate_smc_gains, SMCType ) errors = [] warnings = [] # Controller type validation if controller_type not in list_available_controllers(): errors.append(f"Unknown controller type: {controller_type}") # Gains validation if gains is not None: if controller_type in CONTROLLER_REGISTRY: expected_count = CONTROLLER_REGISTRY[controller_type]['gain_count'] if len(gains) != expected_count: errors.append(f"Expected {expected_count} gains, got {len(gains)}") if not all(isinstance(g, (int, float)) for g in gains): errors.append("All gains must be numeric") if any(g <= 0 for g in gains): errors.append("All gains must be positive") # Configuration validation if config is not None: # Add configuration-specific validation pass return { 'valid': len(errors) == 0, 'errors': errors, 'warnings': warnings } # Example usage
validation = validate_before_creation('classical_smc', [10, 5, 8, 3, 15, 2])
if not validation['valid']: print("Validation errors:") for error in validation['errors']: print(f" - {error}")
``` ### 2. Robust Error Handling Patterns ```python
# example-metadata:
# runnable: false def robust_controller_creation(controller_type, gains=None, config=None, max_retries=3): """Robust controller creation with automatic error recovery.""" from src.controllers.factory import create_controller, get_default_gains for attempt in range(max_retries): try: return create_controller(controller_type, config=config, gains=gains) except ValueError as e: error_str = str(e) if "gains" in error_str and gains is None: # Try with default gains gains = get_default_gains(controller_type) print(f"Attempt {attempt + 1}: Using default gains") continue elif "requires" in error_str and "gains" in error_str: # Fix gain count if gains and controller_type in CONTROLLER_REGISTRY: required = CONTROLLER_REGISTRY[controller_type]['gain_count'] defaults = get_default_gains(controller_type) if len(gains) < required: gains = gains + defaults[len(gains):required] elif len(gains) > required: gains = gains[:required] print(f"Attempt {attempt + 1}: Adjusted gain count") continue raise # Re-raise if can't handle except Exception as e: if attempt == max_retries - 1: raise print(f"Attempt {attempt + 1} failed: {e}, retrying...") raise RuntimeError(f"Failed to create controller after {max_retries} attempts") # Example usage
controller = robust_controller_creation('classical_smc', gains=[10, 5, 8])
``` ### 3. Monitoring and Logging ```python

import logging
from functools import wraps def monitor_factory_operations(func): """Decorator to monitor factory operations.""" @wraps(func) def wrapper(*args, **kwargs): logger = logging.getLogger('factory_monitor') start_time = time.perf_counter() try: result = func(*args, **kwargs) end_time = time.perf_counter() duration = (end_time - start_time) * 1000 # ms logger.info(f"{func.__name__} completed in {duration:.2f}ms") return result except Exception as e: end_time = time.perf_counter() duration = (end_time - start_time) * 1000 logger.error(f"{func.__name__} failed after {duration:.2f}ms: {e}") raise return wrapper # Apply monitoring to factory functions
import src.controllers.factory as factory
factory.create_controller = monitor_factory_operations(factory.create_controller)
``` ## Emergency Recovery Procedures ### Factory System Reset ```python
# example-metadata:
# runnable: false def emergency_factory_reset(): """Emergency factory system reset procedure.""" print("Performing emergency factory reset...") # 1. Clear any cached data try: import importlib import src.controllers.factory importlib.reload(src.controllers.factory) print("✓ Factory module reloaded") except Exception as e: print(f"✗ Module reload failed: {e}") # 2. Test basic functionality try: from src.controllers.factory import create_controller test_controller = create_controller('classical_smc', gains=[10]*6) print("✓ Basic factory test successful") except Exception as e: print(f"✗ Basic factory test failed: {e}") # 3. Verify thread safety try: import threading def test_creation(): create_controller('classical_smc', gains=[10]*6) threads = [threading.Thread(target=test_creation) for _ in range(3)] for t in threads: t.start() for t in threads: t.join(timeout=5) print("✓ Thread safety test passed") except Exception as e: print(f"✗ Thread safety test failed: {e}") print("Emergency reset completed") # Run emergency reset if needed
# emergency_factory_reset()
``` ### Fallback Controller Creation ```python
# example-metadata:

# runnable: false def fallback_controller_creation(controller_type, gains=None): """Fallback controller creation using minimal dependencies.""" # Minimal controller implementation for emergency use class FallbackController: def __init__(self, gains): self.gains = gains or [10, 8, 6, 4, 20, 2] def compute_control(self, state, last_control, history): # Simple proportional control as fallback error = state[:2] # Angular errors control = -sum(g * e for g, e in zip(self.gains[:2], error)) return min(max(control, -150), 150) # Saturate def reset(self): pass print(f"Using fallback controller for {controller_type}") return FallbackController(gains) # Use as last resort

# fallback_controller = fallback_controller_creation('classical_smc')

``` ## Summary This troubleshooting guide provides: 1. **Quick diagnostics**: Immediate health checks and problem identification
2. **Systematic workflows**: Category-based problem solving approaches
3. **Preventive measures**: Proactive error prevention and robust error handling
4. **Emergency procedures**: Recovery options for critical failures
5. **Performance optimization**: Monitoring and optimization guidance The enhanced factory system implemented in GitHub Issue #6 significantly improves reliability and error handling, but this guide ensures users can effectively diagnose and resolve any remaining issues while maintaining system stability and performance.