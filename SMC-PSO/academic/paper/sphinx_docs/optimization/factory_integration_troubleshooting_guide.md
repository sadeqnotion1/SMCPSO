#==========================================================================================\\\
#================ docs/factory_integration_troubleshooting_guide.md ==================\\\
#==========================================================================================\\\

# Factory Integration Troubleshooting Guide ## Overview This troubleshooting guide addresses common issues encountered when using the Enterprise Controller Factory system in the DIP SMC-PSO project. The guide provides systematic diagnostic procedures, root cause analysis, and proven approaches for factory integration problems. ## Table of Contents 1. [Quick Diagnosis](#quick-diagnosis)
2. [Controller Creation Issues](#controller-creation-issues)
3. [PSO Integration Problems](#pso-integration-problems)
4. [Configuration Issues](#configuration-issues)
5. [Performance Problems](#performance-problems)
6. [Import and Dependency Issues](#import-and-dependency-issues)
7. [Thread Safety Issues](#thread-safety-issues)
8. [Validation Failures](#validation-failures)
9. [Debugging Tools and Techniques](#debugging-tools-and-techniques)
10. [Prevention Strategies](#prevention-strategies)

---

## Quick Diagnosis ### Diagnostic Checklist When encountering factory issues, run this quick diagnostic sequence: ```python

# example-metadata:

# runnable: false #!/usr/bin/env python3

"""Factory integration quick diagnostic tool.""" import logging
import traceback
from src.controllers.factory import ( list_available_controllers, list_all_controllers, create_controller, get_default_gains
) def quick_diagnosis(): """Run quick diagnostic checks for factory integration.""" print("=== Factory Integration Diagnostic ===\n") # 1. Check available controllers print("1. Checking available controllers...") try: available = list_available_controllers() all_controllers = list_all_controllers() unavailable = set(all_controllers) - set(available) print(f" ✅ Available: {available}") if unavailable: print(f" ⚠️ Unavailable: {unavailable}") print() except Exception as e: print(f" ❌ Controller listing failed: {e}") return False # 2. Test basic controller creation print("2. Testing basic controller creation...") for controller_type in available: try: controller = create_controller(controller_type) print(f" ✅ {controller_type}: Created successfully") except Exception as e: print(f" ❌ {controller_type}: {e}") print() # 3. Test gain access print("3. Testing default gains access...") for controller_type in available: try: gains = get_default_gains(controller_type) print(f" ✅ {controller_type}: {len(gains)} gains") except Exception as e: print(f" ❌ {controller_type}: {e}") print() # 4. Test PSO integration print("4. Testing PSO integration...") try: from src.controllers.factory import create_pso_controller_factory, SMCType factory = create_pso_controller_factory(SMCType.CLASSICAL) test_gains = [20.0, 15.0, 12.0, 8.0, 35.0, 5.0] controller = factory(test_gains) print(f" ✅ PSO factory: Working") except Exception as e: print(f" ❌ PSO factory: {e}") print() # 5. Test configuration integration print("5. Testing configuration integration...") try: from src.config import load_config config = load_config("config.yaml") controller = create_controller('classical_smc', config=config) print(f" ✅ Configuration: Working") except Exception as e: print(f" ❌ Configuration: {e}") print() print("=== Diagnostic Complete ===") return True if __name__ == "__main__": quick_diagnosis()
``` ### Common Issue Indicators | Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| `ValueError: Unknown controller type` | Typo in controller name | Check `list_available_controllers()` |
| `ImportError: MPC controller missing` | Optional dependencies not installed | Install dependencies or use different controller |
| `ValueError: requires N gains, got M` | Wrong number of gains | Check `get_default_gains(controller_type)` |
| `RuntimeError: Lock timeout` | Thread contention | Reduce concurrent factory calls |
| `ConfigValueError: parameter invalid` | Invalid configuration values | Validate configuration parameters |

---

## Controller Creation Issues ### Issue 1: Unknown Controller Type #### Symptoms
```

ValueError: Unknown controller type 'classical'. Available: ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']
``` #### Root Causes
1. **Incorrect controller name**: Using abbreviated or incorrect names
2. **Typos**: Misspelling in controller type string
3. **Case sensitivity**: Using wrong case for controller names
4. **Outdated code**: Using deprecated controller names #### approaches **Solution 1: Check Available Controllers**
```python

from src.controllers.factory import list_available_controllers # Check what's actually available
available = list_available_controllers()
print(f"Available controllers: {available}") # Use correct names
controller = create_controller('classical_smc') # ✅ Correct
# controller = create_controller('classical') # ❌ Incorrect

``` **Solution 2: Use Controller Aliases**
```python
# example-metadata:

# runnable: false # These aliases are supported for backward compatibility

valid_names = { 'classical_smc': ['classical_smc', 'classic_smc', 'smc_classical', 'smc_v1'], 'sta_smc': ['sta_smc', 'super_twisting', 'sta'], 'adaptive_smc': ['adaptive_smc', 'adaptive'], 'hybrid_adaptive_sta_smc': ['hybrid_adaptive_sta_smc', 'hybrid', 'hybrid_sta']
} # Use any valid name
controller = create_controller('classic_smc') # ✅ Alias works
controller = create_controller('super_twisting') # ✅ Alias works
``` **Solution 3: Defensive Programming**
```python
# example-metadata:

# runnable: false def safe_create_controller(preferred_types, **kwargs): """Create controller with fallback options.""" available = list_available_controllers() for controller_type in preferred_types: if controller_type in available: try: return create_controller(controller_type, **kwargs) except Exception as e: print(f"Failed to create {controller_type}: {e}") continue raise RuntimeError(f"None of {preferred_types} could be created. Available: {available}") # Usage with fallbacks

controller = safe_create_controller(['classical_smc', 'adaptive_smc'])
``` ### Issue 2: Controller Class Not Available #### Symptoms
```

ImportError: Controller class for mpc_controller is not available
ImportError: MPC controller missing optional dependency
``` #### Root Causes
1. **Missing optional dependencies**: MPC controller requires additional packages
2. **Import failures**: Module import errors
3. **Installation issues**: Incomplete package installation #### approaches **Solution 1: Check Dependencies**
```python

def check_controller_dependencies(): """Check which controllers are available and why others aren't.""" from src.controllers.factory import CONTROLLER_REGISTRY for controller_type, info in CONTROLLER_REGISTRY.items(): if info['class'] is None: print(f"❌ {controller_type}: Class not available") if controller_type == 'mpc_controller': print(" Reason: Optional MPC dependencies not installed") print(" Solution: pip install control-systems-toolkit") else: print(f"✅ {controller_type}: Available") check_controller_dependencies()
``` **Solution 2: Install Missing Dependencies**
```bash
# For MPC controller

pip install control-systems-toolkit
pip install cvxopt # If using optimization-based MPC # Verify installation
python -c "from src.controllers.mpc.controller import MPCController; print('MPC available')"
``` **Solution 3: Dynamic Controller Availability**
```python
# example-metadata:

# runnable: false def create_controller_with_fallback(preferred_type, fallback_type, **kwargs): """Create controller with automatic fallback.""" try: return create_controller(preferred_type, **kwargs) except ImportError: print(f"Warning: {preferred_type} not available, using {fallback_type}") return create_controller(fallback_type, **kwargs) # Example: Try MPC, fallback to classical SMC

controller = create_controller_with_fallback( 'mpc_controller', 'classical_smc', gains=[20, 15, 12, 8, 35, 5]
)
``` ### Issue 3: Configuration Creation Failures #### Symptoms
```

Warning: Could not create full config, using minimal config
TypeError: __init__() got an unexpected keyword argument 'invalid_param'
``` #### Root Causes
1. **Invalid parameters**: Passing unsupported parameters to configuration classes
2. **Type mismatches**: Wrong parameter types
3. **Missing required parameters**: Not providing all required configuration values #### approaches **Solution 1: Parameter Validation**
```python

def validate_controller_parameters(controller_type, **params): """Validate parameters before controller creation.""" from src.controllers.factory import CONTROLLER_REGISTRY controller_info = CONTROLLER_REGISTRY[controller_type] required_params = controller_info['required_params'] # Check required parameters missing = set(required_params) - set(params.keys()) if missing: print(f"Missing required parameters: {missing}") return False # Controller-specific validation if controller_type == 'classical_smc': if 'gains' in params and len(params['gains']) != 6: print("Classical SMC requires exactly 6 gains") return False if 'boundary_layer' in params and params['boundary_layer'] <= 0: print("Boundary layer must be positive") return False elif controller_type == 'mpc_controller': if 'horizon' in params and (not isinstance(params['horizon'], int) or params['horizon'] < 1): print("MPC horizon must be positive integer") return False return True # Usage
params = {'gains': [20, 15, 12, 8, 35, 5], 'max_force': 150.0, 'boundary_layer': 0.02}
if validate_controller_parameters('classical_smc', **params): controller = create_controller('classical_smc', **params)
``` **Solution 2: Graceful Parameter Handling**
```python

def create_controller_robust(controller_type, **kwargs): """Create controller with robust parameter handling.""" try: # Try with provided parameters return create_controller(controller_type, **kwargs) except TypeError as e: if "unexpected keyword argument" in str(e): # Extract parameter name from error import re match = re.search(r"'(\w+)'", str(e)) if match: invalid_param = match.group(1) print(f"Removing invalid parameter: {invalid_param}") # Remove invalid parameter and retry filtered_kwargs = {k: v for k, v in kwargs.items() if k != invalid_param} return create_controller(controller_type, **filtered_kwargs) raise # Re-raise if we can't handle it # Usage
controller = create_controller_robust( 'classical_smc', gains=[20, 15, 12, 8, 35, 5], invalid_param='will_be_removed' # This will be filtered out
)
```

---

## PSO Integration Problems ### Issue 1: PSO Factory Creation Failures #### Symptoms
```

AttributeError: 'function' object has no attribute 'n_gains'
TypeError: create_pso_controller_factory() missing required argument
``` #### Root Causes
1. **Missing PSO attributes**: Factory function doesn't have required PSO metadata
2. **Incorrect factory usage**: Not using PSO-specific factory functions
3. **Parameter mismatches**: Wrong parameters for PSO integration #### approaches **Solution 1: Verify PSO Factory Attributes**
```python

from src.controllers.factory import create_pso_controller_factory, SMCType def verify_pso_factory(smc_type): """Verify PSO factory has required attributes.""" factory = create_pso_controller_factory(smc_type) required_attributes = ['n_gains', 'controller_type', 'max_force'] for attr in required_attributes: if not hasattr(factory, attr): print(f"❌ Missing attribute: {attr}") return False else: value = getattr(factory, attr) print(f"✅ {attr}: {value}") return True # Test factory
if verify_pso_factory(SMCType.CLASSICAL): print("PSO factory is properly configured")
``` **Solution 2: Debug Factory Creation**
```python
# example-metadata:

# runnable: false def debug_pso_factory_creation(smc_type): """Debug PSO factory creation step by step.""" print(f"Creating PSO factory for {smc_type.value}...") try: # Step 1: Check controller availability from src.controllers.factory import list_available_controllers available = list_available_controllers() if smc_type.value not in available: print(f"❌ Controller {smc_type.value} not available") return None # Step 2: Create factory factory = create_pso_controller_factory(smc_type) print(f"✅ Factory created successfully") # Step 3: Test factory attributes print(f" n_gains: {factory.n_gains}") print(f" controller_type: {factory.controller_type}") print(f" max_force: {factory.max_force}") # Step 4: Test factory function from src.controllers.factory import get_default_gains test_gains = get_default_gains(smc_type.value) controller = factory(test_gains) print(f"✅ Factory function works") return factory except Exception as e: print(f"❌ Factory creation failed: {e}") import traceback traceback.print_exc() return None # Debug factory creation

factory = debug_pso_factory_creation(SMCType.CLASSICAL)
``` ### Issue 2: Gain Validation Failures #### Symptoms
```

All PSO particles marked as invalid
validate_smc_gains returns False for valid-looking gains
``` #### Root Causes
1. **Incorrect gain bounds**: Using bounds that don't match controller requirements
2. **Type issues**: Passing wrong data types to validation
3. **Numerical precision**: Floating-point precision causing validation failures #### approaches **Solution 1: Debug Gain Validation**
```python

from src.controllers.factory import validate_smc_gains, get_gain_bounds_for_pso, SMCType
import numpy as np def debug_gain_validation(smc_type, gains): """Debug gain validation step by step.""" print(f"Validating gains for {smc_type.value}: {gains}") # Step 1: Check gain count from src.controllers.factory import get_expected_gain_count expected_count = get_expected_gain_count(smc_type) actual_count = len(gains) print(f"Gain count: expected {expected_count}, got {actual_count}") if actual_count != expected_count: print(f"❌ Wrong gain count") return False # Step 2: Check gain types for i, gain in enumerate(gains): if not isinstance(gain, (int, float)): print(f"❌ Gain {i} has wrong type: {type(gain)}") return False if not np.isfinite(gain): print(f"❌ Gain {i} is not finite: {gain}") return False if gain <= 0: print(f"❌ Gain {i} is not positive: {gain}") return False print("✅ All validation checks passed") # Step 3: Check against bounds lower_bounds, upper_bounds = get_gain_bounds_for_pso(smc_type) for i, (gain, lower, upper) in enumerate(zip(gains, lower_bounds, upper_bounds)): if not (lower <= gain <= upper): print(f"⚠️ Gain {i} outside recommended bounds: {gain} not in [{lower}, {upper}]") return True # Test validation
test_gains = [20.0, 15.0, 12.0, 8.0, 35.0, 5.0]
debug_gain_validation(SMCType.CLASSICAL, test_gains)
``` **Solution 2: Fix Common Validation Issues**
```python

def fix_common_gain_issues(gains, smc_type): """Fix common gain validation issues.""" import numpy as np # Convert to list if numpy array if isinstance(gains, np.ndarray): gains = gains.tolist() # Ensure all gains are float gains = [float(g) for g in gains] # Clamp to valid range for i, gain in enumerate(gains): if not np.isfinite(gain): gains[i] = 1.0 # Default for invalid values elif gain <= 0: gains[i] = 0.1 # Minimum positive value elif gain > 1000: gains[i] = 100.0 # Maximum reasonable value # Ensure correct count expected_count = get_expected_gain_count(smc_type) if len(gains) < expected_count: # Pad with defaults default_gains = get_default_gains(smc_type.value) gains.extend(default_gains[len(gains):]) elif len(gains) > expected_count: # Truncate gains = gains[:expected_count] return gains # Usage in PSO fitness function
def robust_fitness_function(gains): """PSO fitness function with gain fixing.""" # Fix common issues fixed_gains = fix_common_gain_issues(gains, SMCType.CLASSICAL) # Validate if not validate_smc_gains(SMCType.CLASSICAL, fixed_gains): return float('inf') # Create controller factory = create_pso_controller_factory(SMCType.CLASSICAL) controller = factory(fixed_gains) # Evaluate performance return evaluate_controller_performance(controller)
``` ### Issue 3: PSO Performance Problems #### Symptoms
```

PSO optimization extremely slow
High memory usage during PSO
PSO doesn't converge
``` #### Root Causes
1. **Factory recreation overhead**: Creating factory in fitness function
2. **Memory leaks**: Not properly cleaning up controllers
3. **Inefficient evaluation**: Complex performance evaluation
4. **Poor PSO parameters**: Suboptimal PSO configuration #### approaches **Solution 1: Optimize PSO Performance**
```python

class OptimizedPSOWorkflow: """Optimized PSO workflow for maximum performance.""" def __init__(self, smc_type, config): self.smc_type = smc_type self.config = config # Create factory once (expensive operation) self.factory = create_pso_controller_factory(smc_type, plant_config=config) # Pre-compute test scenarios self.test_scenarios = self._generate_test_scenarios() # Performance monitoring self.evaluation_count = 0 self.evaluation_times = [] def _generate_test_scenarios(self): """Pre-generate test scenarios for consistent evaluation.""" import numpy as np scenarios = [] # Standard test points test_states = [ np.array([0.1, 0.05, 0.0, 0.0, 0.0, 0.0]), # Small angle np.array([0.3, 0.2, 0.0, 0.0, 0.0, 0.0]), # Medium angle np.array([0.0, 0.0, 0.1, 0.0, 0.0, 0.0]), # Cart displacement ] for state in test_states: scenarios.append({ 'initial_state': state, 'simulation_time': 2.0, 'target_state': np.zeros(6) }) return scenarios def fast_fitness_function(self, gains): """Optimized fitness function for PSO.""" import time start_time = time.time() try: # Quick validation if not validate_smc_gains(self.smc_type, gains): return float('inf') # Create controller (fast operation with pre-created factory) controller = self.factory(gains) # Fast performance evaluation total_cost = 0.0 for scenario in self.test_scenarios: # Simplified simulation state = scenario['initial_state'].copy() cost = 0.0 for _ in range(10): # Short simulation steps control_output = controller.compute_control(state, 0.0, {}) control_value = control_output.u if hasattr(control_output, 'u') else control_output # Simple cost computation state_cost = np.sum(state[:4]**2) # Position and angle errors control_cost = 0.1 * control_value**2 cost += state_cost + control_cost # Simple state update (for speed) state += 0.01 * np.random.randn(6) * 0.1 # Simplified dynamics total_cost += cost # Performance monitoring self.evaluation_count += 1 elapsed = time.time() - start_time self.evaluation_times.append(elapsed) if self.evaluation_count % 100 == 0: avg_time = np.mean(self.evaluation_times[-100:]) print(f"Evaluation {self.evaluation_count}: {avg_time:.4f}s avg") return total_cost except Exception as e: return float('inf') def run_optimization(self): """Run optimized PSO.""" from src.optimization.algorithms.pso_optimizer import PSOTuner # Optimized PSO parameters pso_config = { 'n_particles': 20, # Smaller swarm for speed 'max_iter': 50, # Fewer iterations 'w': 0.9, 'c1': 2.0, 'c2': 2.0, 'early_stopping': True, 'patience': 10 } tuner = PSOTuner( controller_factory=self.fast_fitness_function, config=self.config, **pso_config ) return tuner.optimize() # Usage
optimizer = OptimizedPSOWorkflow(SMCType.CLASSICAL, config)
best_gains, best_fitness = optimizer.run_optimization()
```

---

## Configuration Issues ### Issue 1: Configuration Parameter Conflicts #### Symptoms
```

Warning: Could not extract controller parameters
Configuration parameter 'gains' overridden by explicit parameter
Inconsistent parameter values between config sources
``` #### Root Causes
1. **Multiple configuration sources**: Conflicting values from different sources
2. **Parameter priority confusion**: Not understanding resolution order
3. **Deprecated parameters**: Using old parameter names #### approaches **Solution 1: Configuration Priority Debugging**
```python

def debug_configuration_priority(controller_type, config=None, gains=None, **kwargs): """Debug configuration parameter resolution.""" print(f"Configuration priority debug for {controller_type}:") print(f"Parameters provided:") print(f" gains: {gains}") print(f" config: {config is not None}") print(f" kwargs: {kwargs}") print() # Priority 1: Explicit gains if gains is not None: print(f"✅ Priority 1 - Explicit gains: {gains}") final_gains = gains else: # Priority 2: Configuration object config_gains = None if config is not None: try: # Try different config structures if hasattr(config, 'controllers') and controller_type in config.controllers: controller_config = config.controllers[controller_type] if hasattr(controller_config, 'gains'): config_gains = controller_config.gains print(f"✅ Priority 2 - Config gains: {config_gains}") except Exception as e: print(f"❌ Config extraction failed: {e}") if config_gains is not None: final_gains = config_gains else: # Priority 3: Registry defaults from src.controllers.factory import get_default_gains default_gains = get_default_gains(controller_type) print(f"✅ Priority 3 - Default gains: {default_gains}") final_gains = default_gains print(f"\nFinal gains: {final_gains}") return final_gains # Test configuration priority
from src.config import load_config
config = load_config("config.yaml") gains = debug_configuration_priority( 'classical_smc', config=config, gains=[25, 20, 15, 10, 40, 6] # Should override config
)
``` **Solution 2: Configuration Validation and Cleanup**
```python
# example-metadata:

# runnable: false def validate_and_clean_config(controller_type, config): """Validate and clean configuration object.""" cleaned_config = {} warnings = [] # Extract controller-specific configuration try: if hasattr(config, 'controllers') and controller_type in config.controllers: controller_config = config.controllers[controller_type] # Handle different config types if hasattr(controller_config, 'model_dump'): # Pydantic model cleaned_config = controller_config.model_dump() elif isinstance(controller_config, dict): # Dictionary cleaned_config = controller_config.copy() else: # Object with attributes cleaned_config = { attr: getattr(controller_config, attr) for attr in dir(controller_config) if not attr.startswith('_') and not callable(getattr(controller_config, attr)) } except Exception as e: warnings.append(f"Config extraction failed: {e}") # Validate parameters if 'gains' in cleaned_config: gains = cleaned_config['gains'] if not isinstance(gains, (list, tuple)) or len(gains) == 0: warnings.append("Invalid gains format") del cleaned_config['gains'] if 'max_force' in cleaned_config: if not isinstance(cleaned_config['max_force'], (int, float)) or cleaned_config['max_force'] <= 0: warnings.append("Invalid max_force value") cleaned_config['max_force'] = 150.0 # Default # Handle deprecated parameters deprecated_mappings = { 'use_equivalent': 'enable_equivalent_control', 'k_gain': 'switching_gain', 'lambda_gains': 'surface_gains' } for old_param, new_param in deprecated_mappings.items(): if old_param in cleaned_config: cleaned_config[new_param] = cleaned_config.pop(old_param) warnings.append(f"Deprecated parameter '{old_param}' migrated to '{new_param}'") if warnings: print("Configuration warnings:") for warning in warnings: print(f" ⚠️ {warning}") return cleaned_config # Usage

config = load_config("config.yaml")
cleaned = validate_and_clean_config('classical_smc', config)
controller = create_controller('classical_smc', **cleaned)
``` ### Issue 2: YAML Configuration Errors #### Symptoms
```

yaml.scanner.ScannerError: mapping values are not allowed here
KeyError: 'controllers' not found in configuration
Pydantic validation error for configuration
``` #### Root Causes
1. **YAML syntax errors**: Invalid YAML formatting
2. **Missing configuration sections**: Required sections not present
3. **Type mismatches**: Wrong data types in configuration #### approaches **Solution 1: Configuration Validation Tool**
```python

def validate_yaml_configuration(config_path): """Validate YAML configuration file.""" import yaml from pathlib import Path print(f"Validating configuration: {config_path}") # Check file exists if not Path(config_path).exists(): print(f"❌ Configuration file not found: {config_path}") return False # Check YAML syntax try: with open(config_path, 'r') as f: config_data = yaml.safe_load(f) print("✅ YAML syntax valid") except yaml.YAMLError as e: print(f"❌ YAML syntax error: {e}") return False # Check required sections required_sections = ['controllers', 'physics', 'simulation'] for section in required_sections: if section not in config_data: print(f"⚠️ Missing section: {section}") else: print(f"✅ Section found: {section}") # Check controller configurations if 'controllers' in config_data: controllers = config_data['controllers'] for controller_type, controller_config in controllers.items(): print(f"\nValidating {controller_type}:") # Check gains if 'gains' in controller_config: gains = controller_config['gains'] if not isinstance(gains, list): print(f" ❌ gains must be a list, got {type(gains)}") elif len(gains) == 0: print(f" ❌ gains list is empty") else: print(f" ✅ gains: {len(gains)} values") # Check numeric parameters numeric_params = ['max_force', 'dt', 'boundary_layer'] for param in numeric_params: if param in controller_config: value = controller_config[param] if not isinstance(value, (int, float)): print(f" ❌ {param} must be numeric, got {type(value)}") elif value <= 0: print(f" ❌ {param} must be positive, got {value}") else: print(f" ✅ {param}: {value}") return True # Validate configuration
validate_yaml_configuration("config.yaml")
``` **Solution 2: Configuration Fix Tool**
```python

def fix_configuration_file(config_path, backup=True): """Fix common configuration file issues.""" import yaml import shutil from pathlib import Path config_file = Path(config_path) if backup: backup_file = config_file.with_suffix('.yaml.backup') shutil.copy2(config_file, backup_file) print(f"Created backup: {backup_file}") # Load current configuration with open(config_file, 'r') as f: config_data = yaml.safe_load(f) fixes_applied = [] # Fix 1: Ensure required sections exist required_sections = { 'controllers': {}, 'physics': { 'm1': 0.5, 'm2': 0.5, 'M': 2.0, 'l1': 0.5, 'l2': 0.5, 'b1': 0.1, 'b2': 0.1, 'I1': 0.1, 'I2': 0.1 }, 'simulation': { 'duration': 5.0, 'dt': 0.001 } } for section, defaults in required_sections.items(): if section not in config_data: config_data[section] = defaults fixes_applied.append(f"Added missing section: {section}") # Fix 2: Ensure controller defaults controller_defaults = { 'classical_smc': { 'gains': [20.0, 15.0, 12.0, 8.0, 35.0, 5.0], 'max_force': 150.0, 'boundary_layer': 0.02, 'dt': 0.001 }, 'adaptive_smc': { 'gains': [25.0, 18.0, 15.0, 10.0, 4.0], 'max_force': 150.0, 'dt': 0.001 }, 'sta_smc': { 'gains': [25.0, 15.0, 20.0, 12.0, 8.0, 6.0], 'max_force': 150.0, 'dt': 0.001 } } for controller_type, defaults in controller_defaults.items(): if controller_type not in config_data['controllers']: config_data['controllers'][controller_type] = defaults fixes_applied.append(f"Added controller defaults: {controller_type}") else: # Fix missing parameters controller_config = config_data['controllers'][controller_type] for param, default_value in defaults.items(): if param not in controller_config: controller_config[param] = default_value fixes_applied.append(f"Added missing parameter {controller_type}.{param}") # Fix 3: Validate and fix data types for controller_type, controller_config in config_data['controllers'].items(): if 'gains' in controller_config: gains = controller_config['gains'] if not isinstance(gains, list): # Try to convert to list try: controller_config['gains'] = list(gains) fixes_applied.append(f"Converted {controller_type}.gains to list") except: controller_config['gains'] = controller_defaults.get(controller_type, {}).get('gains', [1.0]) fixes_applied.append(f"Reset invalid {controller_type}.gains") # Write fixed configuration with open(config_file, 'w') as f: yaml.dump(config_data, f, default_flow_style=False, sort_keys=False) if fixes_applied: print("Fixes applied:") for fix in fixes_applied: print(f" ✅ {fix}") else: print("No fixes needed") return len(fixes_applied) > 0 # Fix configuration file
fix_configuration_file("config.yaml")
```

---

## Performance Problems ### Issue 1: Slow Controller Creation #### Symptoms
```

Controller creation takes >1 second
High CPU usage during factory operations
Memory usage grows with each controller creation
``` #### Root Causes
1. **Configuration overhead**: Complex configuration processing
2. **Import delays**: Slow module imports
3. **Memory allocation**: Large object creation
4. **Thread contention**: Multiple threads creating controllers #### approaches **Solution 1: Performance Profiling**
```python

def profile_controller_creation(controller_type, n_iterations=100): """Profile controller creation performance.""" import time import psutil import os process = psutil.Process(os.getpid()) # Warmup controller = create_controller(controller_type) # Measure performance times = [] memory_usage = [] for i in range(n_iterations): # Measure memory before mem_before = process.memory_info().rss / 1024 / 1024 # MB # Time controller creation start_time = time.time() controller = create_controller(controller_type) end_time = time.time() # Measure memory after mem_after = process.memory_info().rss / 1024 / 1024 # MB times.append(end_time - start_time) memory_usage.append(mem_after - mem_before) # Cleanup del controller # Analysis import numpy as np print(f"Performance Profile for {controller_type}:") print(f" Iterations: {n_iterations}") print(f" Average time: {np.mean(times):.4f}s") print(f" Std deviation: {np.std(times):.4f}s") print(f" Min time: {np.min(times):.4f}s") print(f" Max time: {np.max(times):.4f}s") print(f" Average memory per creation: {np.mean(memory_usage):.2f}MB") # Performance thresholds if np.mean(times) > 0.1: print("⚠️ Controller creation is slow (>0.1s)") if np.mean(memory_usage) > 10: print("⚠️ High memory usage per controller (>10MB)") return { 'mean_time': np.mean(times), 'std_time': np.std(times), 'mean_memory': np.mean(memory_usage) } # Profile different controllers
for controller_type in ['classical_smc', 'adaptive_smc', 'sta_smc']: try: profile_controller_creation(controller_type) print() except Exception as e: print(f"Profiling failed for {controller_type}: {e}")
``` **Solution 2: Performance Optimization**
```python
# example-metadata:

# runnable: false class OptimizedControllerFactory: """Optimized controller factory with caching and pooling.""" def __init__(self): self._config_cache = {} self._controller_pool = {} self._pool_size = 10 def _get_cached_config(self, controller_type, config_key): """Get cached configuration to avoid repeated processing.""" cache_key = (controller_type, config_key) if cache_key not in self._config_cache: # Create and cache configuration if config_key is None: # Use defaults from src.controllers.factory import get_default_gains gains = get_default_gains(controller_type) config_obj = self._create_minimal_config(controller_type, gains) else: # Process provided configuration config_obj = self._process_config(controller_type, config_key) self._config_cache[cache_key] = config_obj return self._config_cache[cache_key] def _create_minimal_config(self, controller_type, gains): """Create minimal configuration object.""" from src.controllers.factory import CONTROLLER_REGISTRY controller_info = CONTROLLER_REGISTRY[controller_type] config_class = controller_info['config_class'] # Minimal required parameters if controller_type == 'classical_smc': return config_class( gains=gains, max_force=150.0, boundary_layer=0.02, dt=0.001 ) elif controller_type == 'adaptive_smc': return config_class( gains=gains, max_force=150.0, dt=0.001 ) # ... other controller types def create_optimized_controller(self, controller_type, gains=None, config=None): """Create controller with optimization.""" # Use pooling for identical configurations pool_key = (controller_type, tuple(gains) if gains else None) if pool_key in self._controller_pool: # Reuse existing controller controller = self._controller_pool[pool_key] controller.reset() # Reset state return controller # Create new controller if gains is not None: controller = create_controller(controller_type, gains=gains) else: controller = create_controller(controller_type, config=config) # Add to pool if space available if len(self._controller_pool) < self._pool_size: self._controller_pool[pool_key] = controller return controller def clear_cache(self): """Clear all caches to free memory.""" self._config_cache.clear() self._controller_pool.clear() # Usage

factory = OptimizedControllerFactory() # Create controllers efficiently
controllers = []
for i in range(100): gains = [20.0 + i*0.1, 15.0, 12.0, 8.0, 35.0, 5.0] controller = factory.create_optimized_controller('classical_smc', gains=gains) controllers.append(controller) # Cleanup
factory.clear_cache()
``` ### Issue 2: Memory Leaks #### Symptoms
```

Memory usage continuously grows
"Out of memory" errors during long PSO runs
Python process not releasing memory
``` #### Root Causes
1. **Controller references**: Not properly releasing controller objects
2. **Configuration caching**: Unlimited cache growth
3. **Circular references**: Python garbage collection issues #### approaches **Solution 1: Memory Monitoring**
```python

class MemoryMonitor: """Monitor memory usage during controller operations.""" def __init__(self): import psutil import os self.process = psutil.Process(os.getpid()) self.baseline_memory = self.get_memory_usage() self.peak_memory = self.baseline_memory self.measurements = [] def get_memory_usage(self): """Get current memory usage in MB.""" return self.process.memory_info().rss / 1024 / 1024 def record_measurement(self, operation_name): """Record memory measurement.""" current_memory = self.get_memory_usage() self.peak_memory = max(self.peak_memory, current_memory) measurement = { 'operation': operation_name, 'memory_mb': current_memory, 'delta_mb': current_memory - self.baseline_memory } self.measurements.append(measurement) if measurement['delta_mb'] > 100: # Alert if >100MB growth print(f"⚠️ Memory alert: {operation_name} - {current_memory:.1f}MB (+{measurement['delta_mb']:.1f}MB)") def print_summary(self): """Print memory usage summary.""" current_memory = self.get_memory_usage() total_growth = current_memory - self.baseline_memory print(f"Memory Usage Summary:") print(f" Baseline: {self.baseline_memory:.1f}MB") print(f" Current: {current_memory:.1f}MB") print(f" Peak: {self.peak_memory:.1f}MB") print(f" Total growth: {total_growth:.1f}MB") if total_growth > 50: print("⚠️ Significant memory growth detected") # Usage with memory monitoring
monitor = MemoryMonitor() # Monitor PSO operation
factory = create_pso_controller_factory(SMCType.CLASSICAL)
monitor.record_measurement("Factory creation") for i in range(1000): gains = np.random.uniform(1, 50, 6) controller = factory(gains) if i % 100 == 0: monitor.record_measurement(f"Iteration {i}") # Explicit cleanup del controller monitor.record_measurement("PSO complete")
monitor.print_summary()
``` **Solution 2: Explicit Memory Management**
```python
# example-metadata:

# runnable: false import gc

import weakref class ManagedControllerFactory: """Controller factory with explicit memory management.""" def __init__(self): self._weak_references = set() self._creation_count = 0 self._cleanup_threshold = 100 def create_managed_controller(self, controller_type, **kwargs): """Create controller with memory management.""" # Create controller controller = create_controller(controller_type, **kwargs) # Add weak reference for tracking weak_ref = weakref.ref(controller, self._on_controller_deleted) self._weak_references.add(weak_ref) self._creation_count += 1 # Periodic cleanup if self._creation_count % self._cleanup_threshold == 0: self._perform_cleanup() return controller def _on_controller_deleted(self, weak_ref): """Callback when controller is garbage collected.""" self._weak_references.discard(weak_ref) def _perform_cleanup(self): """Perform explicit cleanup.""" # Remove dead weak references dead_refs = set() for ref in self._weak_references: if ref() is None: dead_refs.add(ref) self._weak_references -= dead_refs # Force garbage collection gc.collect() print(f"Cleanup: {len(self._weak_references)} controllers active, " f"{self._creation_count} total created") def get_active_controller_count(self): """Get number of active controllers.""" return len([ref for ref in self._weak_references if ref() is not None]) def force_cleanup(self): """Force immediate cleanup.""" self._perform_cleanup() # Usage with managed factory
managed_factory = ManagedControllerFactory() # PSO with memory management
def managed_pso_fitness(gains): """PSO fitness function with memory management.""" controller = managed_factory.create_managed_controller('classical_smc', gains=gains) try: # Evaluate controller performance = evaluate_controller_performance(controller) return performance['total_cost'] finally: # Explicit cleanup del controller # Periodic forced cleanup if managed_factory._creation_count % 50 == 0: managed_factory.force_cleanup() # Run PSO with memory management
# ... PSO optimization code

```

---

## Import and Dependency Issues ### Issue 1: Missing Module Imports #### Symptoms
```

ImportError: No module named 'src.controllers.factory'
ModuleNotFoundError: No module named 'control'
ImportError: cannot import name 'MPCController'
``` #### Root Causes
1. **Python path issues**: `src` directory not in Python path
2. **Missing dependencies**: Required packages not installed
3. **Circular imports**: Import dependency cycles
4. **Optional dependencies**: Missing optional packages #### approaches **Solution 1: Python Path Management**
```python

def fix_python_path(): """Fix Python path for project imports.""" import sys import os from pathlib import Path # Get project root directory current_dir = Path(__file__).resolve().parent project_root = current_dir # Find project root by looking for key files while project_root.parent != project_root: if (project_root / 'src').exists() and (project_root / 'config.yaml').exists(): break project_root = project_root.parent # Add to Python path if str(project_root) not in sys.path: sys.path.insert(0, str(project_root)) print(f"Added to Python path: {project_root}") # Verify imports work try: from src.controllers.factory import create_controller print("✅ Factory imports working") return True except ImportError as e: print(f"❌ Import still failing: {e}") return False # Fix path before imports
fix_python_path()
``` **Solution 2: Dependency Checker**
```python
# example-metadata:

# runnable: false def check_dependencies(): """Check all project dependencies.""" required_packages = { 'numpy': 'pip install numpy', 'scipy': 'pip install scipy', 'matplotlib': 'pip install matplotlib', 'pydantic': 'pip install pydantic', 'yaml': 'pip install pyyaml', 'numba': 'pip install numba' } optional_packages = { 'control': 'pip install control-systems-toolkit (for MPC)', 'cvxopt': 'pip install cvxopt (for optimization-based MPC)', 'streamlit': 'pip install streamlit (for web interface)' } print("Checking required dependencies:") missing_required = [] for package, install_cmd in required_packages.items(): try: __import__(package) print(f" ✅ {package}") except ImportError: print(f" ❌ {package} - {install_cmd}") missing_required.append((package, install_cmd)) print("\nChecking optional dependencies:") missing_optional = [] for package, install_cmd in optional_packages.items(): try: __import__(package) print(f" ✅ {package}") except ImportError: print(f" ⚠️ {package} - {install_cmd}") missing_optional.append((package, install_cmd)) # Installation script if missing_required: print("\nTo install missing required packages:") for package, install_cmd in missing_required: print(f" {install_cmd}") if missing_optional: print("\nTo install missing optional packages:") for package, install_cmd in missing_optional: print(f" {install_cmd}") return len(missing_required) == 0 # Check dependencies

check_dependencies()
``` **Solution 3: Import Debugging**
```python
# example-metadata:

# runnable: false def debug_import_issues(): """Debug specific import issues.""" import sys print(f"Python version: {sys.version}") print(f"Python path: {sys.path[:3]}...") # Show first 3 entries # Test specific imports import_tests = [ ('src', 'Basic src module'), ('src.controllers', 'Controllers module'), ('src.controllers.factory', 'Factory module'), ('src.config', 'Config module'), ('src.optimization.algorithms.pso_optimizer', 'PSO optimizer') ] for module_name, description in import_tests: try: module = __import__(module_name, fromlist=['']) print(f"✅ {description}: {module}") except ImportError as e: print(f"❌ {description}: {e}") # Try to give specific help if 'src' in module_name: print(" Try: sys.path.insert(0, '/path/to/project/root')") elif 'mpc' in module_name.lower(): print(" Try: pip install control-systems-toolkit") debug_import_issues()

```

---

## Thread Safety Issues ### Issue 1: Factory Lock Timeouts #### Symptoms
```

RuntimeError: Lock timeout exceeded (10.0s)
Deadlock detected in factory operations
Concurrent controller creation hanging
``` #### Root Causes
1. **Excessive concurrency**: Too many threads creating controllers
2. **Long-running operations**: Slow operations holding locks
3. **Nested locking**: Deadlock from recursive calls
4. **Resource contention**: Limited system resources #### approaches **Solution 1: Reduce Factory Contention**
```python
# example-metadata:

# runnable: false import threading

import time
from concurrent.futures import ThreadPoolExecutor, as_completed def parallel_controller_creation_safe(controller_configs): """Safe parallel controller creation with reduced contention.""" # Strategy 1: Batch creation to reduce lock contention batch_size = 4 # Limit concurrent factory calls results = [] def create_controller_batch(config_batch): """Create a batch of controllers.""" batch_results = [] for config in config_batch: try: controller = create_controller(**config) batch_results.append(('success', controller)) except Exception as e: batch_results.append(('error', str(e))) return batch_results # Split configs into batches batches = [ controller_configs[i:i+batch_size] for i in range(0, len(controller_configs), batch_size) ] # Process batches sequentially to avoid lock contention for batch in batches: batch_results = create_controller_batch(batch) results.extend(batch_results) return results # Usage
configs = [ {'controller_type': 'classical_smc', 'gains': [20, 15, 12, 8, 35, 5]}, {'controller_type': 'adaptive_smc', 'gains': [25, 18, 15, 10, 4]}, # ... more configs
] results = parallel_controller_creation_safe(configs)
``` **Solution 2: Lock-Free Factory Operations**
```python
# example-metadata:

# runnable: false class LockFreeControllerCache: """Lock-free controller cache using pre-created controllers.""" def __init__(self): self._controller_cache = {} self._cache_lock = threading.RLock() self._initialized = False def initialize_cache(self, preload_configs): """Pre-create controllers to avoid runtime factory calls.""" if self._initialized: return print("Initializing controller cache...") # Create controllers sequentially during initialization for config in preload_configs: try: controller = create_controller(**config) cache_key = self._make_cache_key(config) self._controller_cache[cache_key] = controller print(f"Cached: {config['controller_type']}") except Exception as e: print(f"Failed to cache {config}: {e}") self._initialized = True print(f"Cache initialized with {len(self._controller_cache)} controllers") def _make_cache_key(self, config): """Create cache key from configuration.""" key_parts = [config['controller_type']] if 'gains' in config: key_parts.extend([f"{g:.3f}" for g in config['gains']]) return tuple(key_parts) def get_controller(self, config): """Get controller from cache (thread-safe read).""" cache_key = self._make_cache_key(config) if cache_key in self._controller_cache: # Clone controller to avoid shared state issues cached_controller = self._controller_cache[cache_key] return self._clone_controller(cached_controller, config) else: # Fallback to factory (with lock) return create_controller(**config) def _clone_controller(self, cached_controller, config): """Create a new controller with same configuration.""" # Reset cached controller state cached_controller.reset() return cached_controller # Initialize cache at startup

cache = LockFreeControllerCache() # Pre-define common configurations
common_configs = [ {'controller_type': 'classical_smc', 'gains': [20, 15, 12, 8, 35, 5]}, {'controller_type': 'adaptive_smc', 'gains': [25, 18, 15, 10, 4]}, {'controller_type': 'sta_smc', 'gains': [25, 15, 20, 12, 8, 6]},
] cache.initialize_cache(common_configs) # Use cache in PSO (thread-safe)
def thread_safe_fitness_function(gains): """PSO fitness function using cached controllers.""" config = {'controller_type': 'classical_smc', 'gains': gains} controller = cache.get_controller(config) return evaluate_controller_performance(controller)
``` ### Issue 2: Shared State Problems #### Symptoms
```

Controllers interfering with each other
Unexpected state changes between calls
Race conditions in control computation
``` #### Root Causes
1. **Shared mutable state**: Controllers sharing mutable objects
2. **Singleton patterns**: Global state being modified
3. **Static variables**: Class-level shared state #### approaches **Solution 1: Controller State Isolation**
```python
# example-metadata:

# runnable: false class IsolatedControllerWrapper: """Wrapper to ensure controller state isolation.""" def __init__(self, controller): self._controller = controller self._state_lock = threading.RLock() self._initial_state = self._capture_state() def _capture_state(self): """Capture controller's initial state.""" state = {} # Capture gains if hasattr(self._controller, 'gains'): state['gains'] = self._controller.gains.copy() # Capture configuration if hasattr(self._controller, 'config'): state['config'] = self._controller.config # Controller-specific state if hasattr(self._controller, '_adaptive_gains'): state['adaptive_gains'] = self._controller._adaptive_gains.copy() return state def reset_state(self): """Reset controller to initial state.""" with self._state_lock: # Reset gains if 'gains' in self._initial_state: self._controller.gains = self._initial_state['gains'].copy() # Reset adaptive state if hasattr(self._controller, '_adaptive_gains') and 'adaptive_gains' in self._initial_state: self._controller._adaptive_gains = self._initial_state['adaptive_gains'].copy() # Call controller's reset method if hasattr(self._controller, 'reset'): self._controller.reset() def compute_control(self, state, last_control=0.0, history=None): """Thread-safe control computation.""" with self._state_lock: # Ensure clean state if history is None: history = {} # Compute control result = self._controller.compute_control(state, last_control, history) return result def __getattr__(self, name): """Delegate other attributes to wrapped controller.""" return getattr(self._controller, name) # Usage with thread safety

def create_isolated_controller(controller_type, **kwargs): """Create controller with state isolation.""" base_controller = create_controller(controller_type, **kwargs) return IsolatedControllerWrapper(base_controller) # PSO with isolated controllers
def isolated_fitness_function(gains): """PSO fitness function with isolated controllers.""" controller = create_isolated_controller('classical_smc', gains=gains) try: performance = evaluate_controller_performance(controller) return performance['total_cost'] finally: # Ensure clean state for next use controller.reset_state()
```

---

## Debugging Tools and Techniques ### Debugging Suite ```python
# example-metadata:
# runnable: false #!/usr/bin/env python3
"""factory debugging suite.""" import logging
import traceback
import time
import json
from pathlib import Path class FactoryDebugger: """debugging tools for factory integration.""" def __init__(self, log_file='factory_debug.log'): self.log_file = log_file self._setup_logging() self.debug_data = {} def _setup_logging(self): """Setup detailed logging.""" logging.basicConfig( level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[ logging.FileHandler(self.log_file), logging.StreamHandler() ] ) self.logger = logging.getLogger('FactoryDebugger') def debug_controller_creation(self, controller_type, **kwargs): """Debug controller creation step by step.""" debug_info = { 'timestamp': time.time(), 'controller_type': controller_type, 'kwargs': kwargs, 'steps': [], 'errors': [], 'success': False } try: # Step 1: Check controller availability step1 = self._debug_step_availability(controller_type) debug_info['steps'].append(step1) if not step1['success']: return debug_info # Step 2: Parameter resolution step2 = self._debug_step_parameters(controller_type, kwargs) debug_info['steps'].append(step2) # Step 3: Configuration creation step3 = self._debug_step_configuration(controller_type, step2['resolved_params']) debug_info['steps'].append(step3) # Step 4: Controller instantiation step4 = self._debug_step_instantiation(controller_type, step3['config']) debug_info['steps'].append(step4) if step4['success']: debug_info['success'] = True debug_info['controller'] = step4['controller'] except Exception as e: debug_info['errors'].append({ 'type': type(e).__name__, 'message': str(e), 'traceback': traceback.format_exc() }) # Store debug data self.debug_data[f"{controller_type}_{time.time()}"] = debug_info return debug_info def _debug_step_availability(self, controller_type): """Debug controller availability.""" step = {'name': 'availability_check', 'success': False} try: from src.controllers.factory import list_available_controllers, CONTROLLER_REGISTRY available = list_available_controllers() step['available_controllers'] = available step['controller_in_registry'] = controller_type in CONTROLLER_REGISTRY step['controller_available'] = controller_type in available if controller_type in available: controller_info = CONTROLLER_REGISTRY[controller_type] step['controller_info'] = { 'class_available': controller_info['class'] is not None, 'description': controller_info['description'], 'gain_count': controller_info['gain_count'] } step['success'] = True else: step['error'] = f"Controller {controller_type} not available" except Exception as e: step['error'] = str(e) return step def _debug_step_parameters(self, controller_type, kwargs): """Debug parameter resolution.""" step = {'name': 'parameter_resolution', 'success': False} try: # Analyze provided parameters step['provided_params'] = list(kwargs.keys()) step['gains_provided'] = 'gains' in kwargs step['config_provided'] = 'config' in kwargs # Check gains if provided if 'gains' in kwargs: gains = kwargs['gains'] step['gains_analysis'] = { 'type': type(gains).__name__, 'length': len(gains) if hasattr(gains, '__len__') else 'N/A', 'all_numeric': all(isinstance(g, (int, float)) for g in gains) if hasattr(gains, '__iter__') else False } # Resolve final parameters from src.controllers.factory import get_default_gains if 'gains' not in kwargs: default_gains = get_default_gains(controller_type) step['using_default_gains'] = True step['default_gains'] = default_gains resolved_gains = default_gains else: resolved_gains = kwargs['gains'] step['resolved_params'] = kwargs.copy() step['resolved_params']['gains'] = resolved_gains step['success'] = True except Exception as e: step['error'] = str(e) return step def _debug_step_configuration(self, controller_type, params): """Debug configuration creation.""" step = {'name': 'configuration_creation', 'success': False} try: from src.controllers.factory import CONTROLLER_REGISTRY controller_info = CONTROLLER_REGISTRY[controller_type] config_class = controller_info['config_class'] step['config_class'] = config_class.__name__ step['required_params'] = controller_info['required_params'] # Try to create configuration if controller_type == 'classical_smc': config = config_class( gains=params['gains'], max_force=params.get('max_force', 150.0), boundary_layer=params.get('boundary_layer', 0.02), dt=params.get('dt', 0.001) ) elif controller_type == 'adaptive_smc': config = config_class( gains=params['gains'], max_force=params.get('max_force', 150.0), dt=params.get('dt', 0.001) ) # ... other controller types else: # Generic creation config = config_class(**params) step['config'] = config step['success'] = True except Exception as e: step['error'] = str(e) step['traceback'] = traceback.format_exc() return step def _debug_step_instantiation(self, controller_type, config): """Debug controller instantiation.""" step = {'name': 'controller_instantiation', 'success': False} try: from src.controllers.factory import CONTROLLER_REGISTRY controller_info = CONTROLLER_REGISTRY[controller_type] controller_class = controller_info['class'] step['controller_class'] = controller_class.__name__ # Create controller controller = controller_class(config) # Verify controller interface step['has_compute_control'] = hasattr(controller, 'compute_control') step['has_reset'] = hasattr(controller, 'reset') step['has_gains'] = hasattr(controller, 'gains') if hasattr(controller, 'gains'): step['controller_gains'] = controller.gains step['controller'] = controller step['success'] = True except Exception as e: step['error'] = str(e) step['traceback'] = traceback.format_exc() return step def generate_debug_report(self, output_file='debug_report.json'): """Generate debug report.""" report = { 'timestamp': time.time(), 'total_debug_sessions': len(self.debug_data), 'sessions': self.debug_data } with open(output_file, 'w') as f: json.dump(report, f, indent=2, default=str) print(f"Debug report saved to: {output_file}") return report # Usage
debugger = FactoryDebugger() # Debug controller creation
debug_info = debugger.debug_controller_creation( 'classical_smc', gains=[20, 15, 12, 8, 35, 5]
) if debug_info['success']: print("✅ Controller creation successful")
else: print("❌ Controller creation failed") for error in debug_info['errors']: print(f"Error: {error['message']}") # Generate report
debugger.generate_debug_report()
```

---

## Prevention Strategies ### Best Practices for Robust Factory Integration ```python

#!/usr/bin/env python3
"""Best practices for robust factory integration.""" class RobustFactoryIntegration: """Demonstrates best practices for factory integration.""" def __init__(self): self.factory_cache = {} self.validation_cache = {} def create_controller_robust(self, controller_type, **kwargs): """Create controller with robustness patterns.""" # 1. Input validation if not self._validate_inputs(controller_type, kwargs): raise ValueError("Invalid inputs") # 2. Pre-creation checks if not self._pre_creation_checks(controller_type): raise ImportError(f"Controller {controller_type} not available") # 3. Safe creation with fallbacks try: return self._create_with_fallbacks(controller_type, kwargs) except Exception as e: self._log_creation_failure(controller_type, kwargs, e) raise def _validate_inputs(self, controller_type, kwargs): """Validate inputs before creation.""" # Check controller type if not isinstance(controller_type, str) or not controller_type.strip(): return False # Check gains if provided if 'gains' in kwargs: gains = kwargs['gains'] if not isinstance(gains, (list, tuple)): return False if not all(isinstance(g, (int, float)) for g in gains): return False if not all(g > 0 for g in gains): return False return True def _pre_creation_checks(self, controller_type): """Perform pre-creation availability checks.""" try: from src.controllers.factory import list_available_controllers available = list_available_controllers() return controller_type in available except Exception: return False def _create_with_fallbacks(self, controller_type, kwargs): """Create controller with fallback strategies.""" strategies = [ self._strategy_direct_creation, self._strategy_minimal_config, self._strategy_default_parameters ] last_exception = None for strategy in strategies: try: return strategy(controller_type, kwargs) except Exception as e: last_exception = e continue # All strategies failed raise last_exception def _strategy_direct_creation(self, controller_type, kwargs): """Strategy 1: Direct creation with provided parameters.""" from src.controllers.factory import create_controller return create_controller(controller_type, **kwargs) def _strategy_minimal_config(self, controller_type, kwargs): """Strategy 2: Minimal configuration creation.""" # Use only essential parameters essential_params = {} if 'gains' in kwargs: essential_params['gains'] = kwargs['gains'] # Add required defaults if controller_type == 'classical_smc': essential_params.update({ 'max_force': 150.0, 'boundary_layer': 0.02, 'dt': 0.001 }) elif controller_type == 'adaptive_smc': essential_params.update({ 'max_force': 150.0, 'dt': 0.001 }) from src.controllers.factory import create_controller return create_controller(controller_type, **essential_params) def _strategy_default_parameters(self, controller_type, kwargs): """Strategy 3: Use all default parameters.""" from src.controllers.factory import create_controller return create_controller(controller_type) def _log_creation_failure(self, controller_type, kwargs, exception): """Log creation failure for debugging.""" import logging logger = logging.getLogger(__name__) logger.error(f"Controller creation failed:") logger.error(f" Type: {controller_type}") logger.error(f" Parameters: {kwargs}") logger.error(f" Exception: {exception}") # Validation patterns
class FactoryValidationPatterns: """Common validation patterns for factory integration.""" @staticmethod def validate_controller_type(controller_type): """Validate controller type string.""" if not isinstance(controller_type, str): raise TypeError("Controller type must be string") if not controller_type.strip(): raise ValueError("Controller type cannot be empty") # Normalize return controller_type.strip().lower() @staticmethod def validate_gains(gains, expected_count=None): """Validate gain array.""" if gains is None: return True # Allow None for default gains # Convert numpy arrays if hasattr(gains, 'tolist'): gains = gains.tolist() if not isinstance(gains, (list, tuple)): raise TypeError("Gains must be list or tuple") if len(gains) == 0: raise ValueError("Gains cannot be empty") # Check types if not all(isinstance(g, (int, float)) for g in gains): raise TypeError("All gains must be numeric") # Check finite values import numpy as np if not all(np.isfinite(g) for g in gains): raise ValueError("All gains must be finite") # Check positivity if not all(g > 0 for g in gains): raise ValueError("All gains must be positive") # Check count if specified if expected_count is not None and len(gains) != expected_count: raise ValueError(f"Expected {expected_count} gains, got {len(gains)}") return True @staticmethod def validate_configuration(config, controller_type): """Validate configuration object.""" if config is None: return True # Allow None for default config # Check for required attributes based on controller type if controller_type == 'classical_smc': required_attrs = ['max_force', 'boundary_layer'] for attr in required_attrs: if hasattr(config, attr): value = getattr(config, attr) if not isinstance(value, (int, float)) or value <= 0: raise ValueError(f"Invalid {attr}: {value}") return True # Testing patterns
class FactoryTestingPatterns: """Testing patterns for factory integration.""" def test_all_controllers(self): """Test all available controllers.""" from src.controllers.factory import list_available_controllers results = {} available = list_available_controllers() for controller_type in available: try: # Test with defaults controller = create_controller(controller_type) results[controller_type] = {'default': 'success'} # Test with custom gains from src.controllers.factory import get_default_gains custom_gains = [g * 1.1 for g in get_default_gains(controller_type)] controller = create_controller(controller_type, gains=custom_gains) results[controller_type]['custom_gains'] = 'success' except Exception as e: results[controller_type] = {'error': str(e)} return results def stress_test_factory(self, n_iterations=1000): """Stress test factory with many creations.""" import time start_time = time.time() errors = [] for i in range(n_iterations): try: controller = create_controller('classical_smc') del controller # Explicit cleanup except Exception as e: errors.append((i, str(e))) end_time = time.time() return { 'total_time': end_time - start_time, 'avg_time_per_creation': (end_time - start_time) / n_iterations, 'errors': errors, 'success_rate': (n_iterations - len(errors)) / n_iterations } # Usage examples
if __name__ == "__main__": # Robust factory integration robust_factory = RobustFactoryIntegration() try: controller = robust_factory.create_controller_robust( 'classical_smc', gains=[20, 15, 12, 8, 35, 5] ) print("✅ Robust controller creation successful") except Exception as e: print(f"❌ Robust controller creation failed: {e}") # Validation patterns try: FactoryValidationPatterns.validate_gains([20, 15, 12, 8, 35, 5], expected_count=6) print("✅ Gain validation passed") except Exception as e: print(f"❌ Gain validation failed: {e}") # Testing patterns tester = FactoryTestingPatterns() test_results = tester.test_all_controllers() print(f"Controller test results: {test_results}")
```

---

This troubleshooting guide provides systematic approaches to diagnosing and resolving factory integration issues. Each section includes detailed diagnostic procedures, root cause analysis, and proven approaches with practical code examples. The guide emphasizes prevention through robust programming practices and testing strategies.