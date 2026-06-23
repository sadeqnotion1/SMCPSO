# Migration Guide for Existing Configurations ## Overview This migration guide helps users transition from older controller factory configurations to the enhanced GitHub Issue #6 resolution implementation. The guide covers automated migration tools, manual migration procedures, and best practices for maintaining system stability during transitions. ## Migration Overview ### What Changed in GitHub Issue #6 Resolution The factory integration fixes address several critical areas: 1. **Parameter Interface Unification**: Standardized parameter handling across all SMC controller types

2. **Gamma vs Gains Resolution**: Clarified parameter roles and eliminated confusion
3. **Thread Safety Implementation**: Added locking and concurrent operation support
4. **Enhanced Validation**: Improved parameter validation with detailed error messages
5. **PSO Integration Optimization**: Streamlined PSO optimization workflows
6. **Deprecation Management**: Systematic handling of deprecated parameters ### Migration Impact Assessment ```python
# example-metadata:

# runnable: false # Pre-Migration Configuration (v1.x)

old_config = { 'classical_smc': { 'gains': [10, 5, 8, 3, 15], # 5 gains instead of 6 'K_switching': 2.0, # Separate switching gain 'gamma': 0.1, # Invalid for classical SMC 'switch_function': 'sign' # Old parameter name }, 'adaptive_smc': { 'gains': [12, 10, 6, 5], # 4 gains instead of 5 'adaptation_gain': 2.5, # Separate adaptation gain 'boundary_layer_thickness': 0.02, # Old parameter name 'estimate_bounds': [0.1, 100.0] # Old format }
} # Post-Migration Configuration (v2.x+)
new_config = { 'classical_smc': { 'gains': [10, 5, 8, 3, 15, 2.0], # 6 gains with K included 'boundary_layer': 0.02, # Correct parameter 'switch_method': 'sign' # New parameter name }, 'adaptive_smc': { 'gains': [12, 10, 6, 5, 2.5], # 5 gains with gamma included 'boundary_layer': 0.02, # Renamed parameter 'K_min': 0.1, # Split parameter 'K_max': 100.0 # Split parameter }
}
``` ## Automated Migration Tools ### Quick Migration Utility ```python
from src.controllers.factory.deprecation import ConfigurationMigrationUtility def quick_migrate_configuration(config_file_path: str) -> None: """ One-command migration for most common use cases. Usage: quick_migrate_configuration("config.yaml") """ migrator = ConfigurationMigrationUtility() # Perform migration with backup result = migrator.migrate_configuration_file( config_file_path=config_file_path, create_backup=True ) if result.success: print(f"✓ Migration successful!") print(f" Original: {result.original_file}") print(f" Migrated: {result.migrated_file}") print(f" Backup: {result.backup_file}") if result.warnings: print(f" Warnings: {len(result.warnings)} deprecation warnings") print(f" Summary: {result.migration_summary}") else: print(f"✗ Migration failed: {result.error}") if result.backup_file: print(f" Backup available: {result.backup_file}") # Example usage
quick_migrate_configuration("my_controller_config.yaml")
``` ### Batch Migration Script ```python

def migrate_project_configurations(project_directory: str) -> None: """ Migrate all configuration files in a project directory. Usage: migrate_project_configurations("/path/to/project") """ import os from pathlib import Path project_path = Path(project_directory) migrator = ConfigurationMigrationUtility() # Find all configuration files config_patterns = ['*.yaml', '*.yml', '*.json'] config_files = [] for pattern in config_patterns: config_files.extend(project_path.rglob(pattern)) # Filter for likely controller configuration files controller_configs = [] for config_file in config_files: if any(keyword in config_file.name.lower() for keyword in ['controller', 'smc', 'config', 'param']): controller_configs.append(config_file) print(f"Found {len(controller_configs)} potential configuration files") migration_results = [] for config_file in controller_configs: print(f"\nMigrating: {config_file}") result = migrator.migrate_configuration_file( config_file_path=config_file, create_backup=True ) migration_results.append(result) if result.success: print(f" ✓ Success - {len(result.warnings)} warnings") else: print(f" ✗ Failed - {result.error}") # Summary successful = sum(1 for r in migration_results if r.success) total = len(migration_results) print(f"\n=== Migration Summary ===") print(f"Total files processed: {total}") print(f"Successful migrations: {successful}") print(f"Failed migrations: {total - successful}") if successful < total: print("\nFailed files require manual migration:") for result in migration_results: if not result.success: print(f" - {result.original_file}: {result.error}") # Example usage
migrate_project_configurations("./my_smc_project")
``` ### Interactive Migration Wizard ```python
# example-metadata:
# runnable: false def interactive_migration_wizard() -> None: """ Interactive step-by-step migration wizard for complex configurations. """ print("=== SMC Controller Configuration Migration Wizard ===\n") # Step 1: Configuration file location config_path = input("Enter path to configuration file: ").strip() if not os.path.exists(config_path): print(f"Error: File not found - {config_path}") return # Step 2: Backup preferences create_backup = input("Create backup before migration? (Y/n): ").strip().lower() create_backup = create_backup != 'n' # Step 3: Migration analysis print("\nAnalyzing configuration...") migrator = ConfigurationMigrationUtility() # Load and analyze configuration try: with open(config_path, 'r') as f: if config_path.endswith(('.yml', '.yaml')): import yaml config_data = yaml.safe_load(f) else: import json config_data = json.load(f) # Analyze deprecations warner = ControllerDeprecationWarner() analysis_results = {} if 'controllers' in config_data: for controller_type, controller_config in config_data['controllers'].items(): if isinstance(controller_config, dict): _, warnings = warner.check_deprecated_parameters(controller_type, controller_config) analysis_results[controller_type] = warnings # Display analysis total_warnings = sum(len(warnings) for warnings in analysis_results.values()) if total_warnings == 0: print("✓ No deprecated parameters found. Configuration is up to date.") return print(f"Found {total_warnings} deprecated parameters:") for controller_type, warnings in analysis_results.items(): if warnings: print(f"\n {controller_type}:") for warning in warnings: print(f" - {warning.old_parameter}: {warning.migration_guide}") # Step 4: Confirm migration proceed = input(f"\nProceed with migration? (Y/n): ").strip().lower() if proceed == 'n': print("Migration cancelled.") return # Step 5: Perform migration print("\nPerforming migration...") result = migrator.migrate_configuration_file( config_file_path=config_path, create_backup=create_backup ) if result.success: print("✓ Migration completed successfully!") if result.backup_file: print(f" Backup created: {result.backup_file}") # Step 6: Validation validate = input("\nValidate migrated configuration? (Y/n): ").strip().lower() if validate != 'n': validation_result = migrator.validate_migrated_configuration( result.migration_summary.get('migrated_config', {}) ) if validation_result.success: print("✓ Validation passed - configuration is ready to use.") else: print("⚠ Validation issues found:") for issue in validation_result.issues: print(f" - {issue}") else: print(f"✗ Migration failed: {result.error}") except Exception as e: print(f"Error during migration analysis: {e}") # Run the wizard
interactive_migration_wizard()
``` ## Manual Migration Procedures ### Classical SMC Migration ```python
# example-metadata:

# runnable: false def migrate_classical_smc_manually(old_config: Dict[str, Any]) -> Dict[str, Any]: """ Manual migration procedure for Classical SMC configurations. Changes: 1. Combine gains and K_switching into 6-element gains array 2. Remove invalid 'gamma' parameter 3. Rename 'switch_function' to 'switch_method' 4. Ensure boundary_layer parameter is present """ new_config = {} # Step 1: Handle gains array gains = old_config.get('gains', [8.0, 6.0, 4.0, 3.0, 15.0]) # If gains has only 5 elements, add K_switching as 6th element if len(gains) == 5: K_switching = old_config.get('K_switching', 2.0) gains = gains + [K_switching] elif len(gains) < 5: # Fill missing gains with defaults default_gains = [8.0, 6.0, 4.0, 3.0, 15.0, 2.0] gains = gains + default_gains[len(gains):] new_config['gains'] = gains[:6] # Ensure exactly 6 gains # Step 2: Handle deprecated parameters deprecated_params = ['gamma', 'adaptation_rate', 'K_switching'] for param in deprecated_params: if param in old_config: if param == 'gamma': print(f"Warning: Removed invalid 'gamma' parameter for Classical SMC") elif param == 'adaptation_rate': print(f"Warning: Removed 'adaptation_rate' - not valid for Classical SMC") # K_switching already handled in gains array # Step 3: Handle renamed parameters if 'switch_function' in old_config: new_config['switch_method'] = old_config['switch_function'] print(f"Migrated: switch_function -> switch_method") # Step 4: Copy valid parameters valid_params = [ 'max_force', 'dt', 'boundary_layer', 'switch_method', 'damping_gain', 'dynamics_model' ] for param in valid_params: if param in old_config: new_config[param] = old_config[param] # Step 5: Ensure required parameters have defaults new_config.setdefault('max_force', 150.0) new_config.setdefault('dt', 0.001) new_config.setdefault('boundary_layer', 0.02) return new_config # Example usage

old_classical_config = { 'gains': [10, 5, 8, 3, 15], 'K_switching': 2.0, 'gamma': 0.1, # Invalid - will be removed 'switch_function': 'sign', # Will be renamed 'max_force': 100.0
} new_classical_config = migrate_classical_smc_manually(old_classical_config)
print("Migrated Classical SMC config:", new_classical_config)
``` ### Adaptive SMC Migration ```python
# example-metadata:
# runnable: false def migrate_adaptive_smc_manually(old_config: Dict[str, Any]) -> Dict[str, Any]: """ Manual migration procedure for Adaptive SMC configurations. Changes: 1. Combine gains and adaptation_gain into 5-element gains array 2. Rename 'boundary_layer_thickness' to 'boundary_layer' 3. Split 'estimate_bounds' into 'K_min' and 'K_max' 4. Rename 'adaptation_law' to 'alpha' """ new_config = {} # Step 1: Handle gains array with gamma (adaptation rate) gains = old_config.get('gains', [12.0, 10.0, 6.0, 5.0]) # If gains has only 4 elements, add adaptation_gain as 5th element if len(gains) == 4: adaptation_gain = old_config.get('adaptation_gain', 2.5) gains = gains + [adaptation_gain] elif len(gains) < 4: # Fill missing gains with defaults default_gains = [12.0, 10.0, 6.0, 5.0, 2.5] gains = gains + default_gains[len(gains):] new_config['gains'] = gains[:5] # Ensure exactly 5 gains # Step 2: Handle renamed parameters renames = { 'boundary_layer_thickness': 'boundary_layer', 'adaptation_law': 'alpha' } for old_name, new_name in renames.items(): if old_name in old_config: new_config[new_name] = old_config[old_name] print(f"Migrated: {old_name} -> {new_name}") # Step 3: Handle split parameters if 'estimate_bounds' in old_config: bounds = old_config['estimate_bounds'] if isinstance(bounds, (list, tuple)) and len(bounds) == 2: new_config['K_min'] = bounds[0] new_config['K_max'] = bounds[1] print(f"Split: estimate_bounds -> K_min, K_max") else: print(f"Warning: Invalid estimate_bounds format, using defaults") new_config['K_min'] = 0.1 new_config['K_max'] = 100.0 # Step 4: Copy valid parameters valid_params = [ 'max_force', 'dt', 'boundary_layer', 'leak_rate', 'adapt_rate_limit', 'K_min', 'K_max', 'K_init', 'alpha', 'dead_zone', 'smooth_switch', 'dynamics_model' ] for param in valid_params: if param in old_config: new_config[param] = old_config[param] # Step 5: Ensure required parameters have defaults new_config.setdefault('max_force', 150.0) new_config.setdefault('dt', 0.001) new_config.setdefault('boundary_layer', 0.01) new_config.setdefault('leak_rate', 0.01) new_config.setdefault('adapt_rate_limit', 10.0) new_config.setdefault('K_min', 0.1) new_config.setdefault('K_max', 100.0) new_config.setdefault('K_init', 10.0) new_config.setdefault('alpha', 0.5) return new_config # Example usage
old_adaptive_config = { 'gains': [12, 10, 6, 5], 'adaptation_gain': 2.5, 'boundary_layer_thickness': 0.02, 'estimate_bounds': [0.1, 100.0], 'adaptation_law': 0.5, 'max_force': 150.0
} new_adaptive_config = migrate_adaptive_smc_manually(old_adaptive_config)
print("Migrated Adaptive SMC config:", new_adaptive_config)
``` ### Super-Twisting SMC Migration ```python
# example-metadata:

# runnable: false def migrate_sta_smc_manually(old_config: Dict[str, Any]) -> Dict[str, Any]: """ Manual migration procedure for Super-Twisting SMC configurations. Changes: 1. Combine K1, K2, and other gains into 6-element gains array 2. Rename 'alpha_power' to 'power_exponent' 3. Rename 'switching_function_type' to 'switch_method' """ new_config = {} # Step 1: Handle gains array with K1, K2 integration gains = old_config.get('gains', []) # If K1 and K2 are separate parameters, integrate them if 'K1' in old_config and 'K2' in old_config: K1 = old_config['K1'] K2 = old_config['K2'] # If gains array exists, assume it contains [k1, k2, lam1, lam2] if len(gains) >= 4: gains = [K1, K2] + gains[:4] else: # Create full gains array default_surface_gains = [25.0, 18.0, 12.0, 8.0] surface_gains = gains + default_surface_gains[len(gains):] gains = [K1, K2] + surface_gains[:4] print(f"Integrated: K1={K1}, K2={K2} into gains array") elif len(gains) < 6: # Fill missing gains with defaults default_gains = [35.0, 20.0, 25.0, 18.0, 12.0, 8.0] gains = gains + default_gains[len(gains):] new_config['gains'] = gains[:6] # Ensure exactly 6 gains # Step 2: Handle renamed parameters renames = { 'alpha_power': 'power_exponent', 'switching_function_type': 'switch_method' } for old_name, new_name in renames.items(): if old_name in old_config: new_config[new_name] = old_config[old_name] print(f"Migrated: {old_name} -> {new_name}") # Step 3: Copy valid parameters valid_params = [ 'max_force', 'dt', 'power_exponent', 'regularization', 'boundary_layer', 'switch_method', 'damping_gain', 'dynamics_model' ] for param in valid_params: if param in old_config: new_config[param] = old_config[param] # Step 4: Ensure required parameters have defaults new_config.setdefault('max_force', 150.0) new_config.setdefault('dt', 0.001) new_config.setdefault('power_exponent', 0.5) new_config.setdefault('regularization', 1e-6) new_config.setdefault('boundary_layer', 0.01) new_config.setdefault('switch_method', 'tanh') return new_config # Example usage

old_sta_config = { 'K1': 35.0, 'K2': 20.0, 'gains': [25.0, 18.0, 12.0, 8.0], # Surface gains 'alpha_power': 0.5, 'switching_function_type': 'tanh', 'max_force': 150.0
} new_sta_config = migrate_sta_smc_manually(old_sta_config)
print("Migrated STA-SMC config:", new_sta_config)
``` ### Hybrid SMC Migration ```python
# example-metadata:
# runnable: false def migrate_hybrid_smc_manually(old_config: Dict[str, Any]) -> Dict[str, Any]: """ Manual migration procedure for Hybrid SMC configurations. Changes: 1. Rename 'mode' to 'hybrid_mode' 2. Replace 'sub_controller_gains' with full sub-configurations 3. Update 'switch_threshold' to 'switching_criteria' """ new_config = {} # Step 1: Handle surface gains (4 elements for hybrid controller) gains = old_config.get('gains', [18.0, 12.0, 10.0, 8.0]) new_config['gains'] = gains[:4] # Ensure exactly 4 surface gains # Step 2: Handle mode parameter if 'mode' in old_config: new_config['hybrid_mode'] = old_config['mode'] print(f"Migrated: mode -> hybrid_mode") else: new_config['hybrid_mode'] = 'CLASSICAL_ADAPTIVE' # Default # Step 3: Handle sub-controller configurations if 'sub_controller_gains' in old_config: sub_gains = old_config['sub_controller_gains'] # Create proper sub-configurations if isinstance(sub_gains, dict): classical_gains = sub_gains.get('classical', [20.0, 15.0, 12.0, 8.0, 35.0, 5.0]) adaptive_gains = sub_gains.get('adaptive', [25.0, 18.0, 15.0, 10.0, 4.0]) else: # Use defaults if format is unrecognized classical_gains = [20.0, 15.0, 12.0, 8.0, 35.0, 5.0] adaptive_gains = [25.0, 18.0, 15.0, 10.0, 4.0] # Create full sub-configurations new_config['classical_config'] = { 'gains': classical_gains, 'max_force': 150.0, 'dt': 0.001, 'boundary_layer': 0.02 } new_config['adaptive_config'] = { 'gains': adaptive_gains, 'max_force': 150.0, 'dt': 0.001, 'leak_rate': 0.01, 'adapt_rate_limit': 10.0, 'K_min': 0.1, 'K_max': 100.0, 'K_init': 10.0, 'alpha': 0.5 } print("Converted: sub_controller_gains -> full sub-configurations") # Step 4: Handle switching criteria if 'switch_threshold' in old_config: threshold = old_config['switch_threshold'] new_config['switching_criteria'] = { 'error_threshold': threshold, 'time_threshold': 2.0 # Default } print("Converted: switch_threshold -> switching_criteria") # Step 5: Copy valid parameters valid_params = [ 'dt', 'max_force', 'k1_init', 'k2_init', 'gamma1', 'gamma2', 'dynamics_model', 'hybrid_mode', 'classical_config', 'adaptive_config' ] for param in valid_params: if param in old_config: new_config[param] = old_config[param] # Step 6: Ensure required parameters have defaults new_config.setdefault('dt', 0.001) new_config.setdefault('max_force', 150.0) new_config.setdefault('k1_init', 5.0) new_config.setdefault('k2_init', 3.0) new_config.setdefault('gamma1', 0.5) new_config.setdefault('gamma2', 0.3) return new_config # Example usage
old_hybrid_config = { 'gains': [18.0, 12.0, 10.0, 8.0], 'mode': 'CLASSICAL_ADAPTIVE', 'sub_controller_gains': { 'classical': [20.0, 15.0, 12.0, 8.0, 35.0, 5.0], 'adaptive': [25.0, 18.0, 15.0, 10.0, 4.0] }, 'switch_threshold': 0.1, 'max_force': 150.0
} new_hybrid_config = migrate_hybrid_smc_manually(old_hybrid_config)
print("Migrated Hybrid SMC config:", new_hybrid_config)
``` ## Configuration File Migration Examples ### YAML Configuration Migration ```yaml
# Before Migration (config_old.yaml)

controllers: classical_smc: gains: [10, 5, 8, 3, 15] K_switching: 2.0 gamma: 0.1 # Invalid parameter switch_function: "sign" # Old parameter name max_force: 100.0 adaptive_smc: gains: [12, 10, 6, 5] adaptation_gain: 2.5 # Separate parameter boundary_layer_thickness: 0.02 # Old parameter name estimate_bounds: [0.1, 100.0] # Old format max_force: 150.0 sta_smc: K1: 35.0 # Separate parameters K2: 20.0 gains: [25, 18, 12, 8] # Surface gains only alpha_power: 0.5 # Old parameter name max_force: 150.0 # After Migration (config_new.yaml)
controllers: classical_smc: gains: [10, 5, 8, 3, 15, 2.0] # 6-element array switch_method: "sign" # New parameter name boundary_layer: 0.02 # Required parameter max_force: 100.0 dt: 0.001 adaptive_smc: gains: [12, 10, 6, 5, 2.5] # 5-element array with gamma boundary_layer: 0.02 # Renamed parameter K_min: 0.1 # Split parameter K_max: 100.0 # Split parameter leak_rate: 0.01 adapt_rate_limit: 10.0 K_init: 10.0 alpha: 0.5 max_force: 150.0 dt: 0.001 sta_smc: gains: [35.0, 20.0, 25, 18, 12, 8] # 6-element array with K1, K2 power_exponent: 0.5 # Renamed parameter regularization: 1.0e-06 boundary_layer: 0.01 switch_method: "tanh" max_force: 150.0 dt: 0.001
``` ### JSON Configuration Migration ```json
// Before Migration (config_old.json)
{ "controllers": { "classical_smc": { "gains": [10, 5, 8, 3, 15], "K_switching": 2.0, "gamma": 0.1, "switch_function": "sign", "max_force": 100.0 }, "adaptive_smc": { "gains": [12, 10, 6, 5], "adaptation_gain": 2.5, "boundary_layer_thickness": 0.02, "estimate_bounds": [0.1, 100.0], "max_force": 150.0 } }
} // After Migration (config_new.json)
{ "controllers": { "classical_smc": { "gains": [10, 5, 8, 3, 15, 2.0], "switch_method": "sign", "boundary_layer": 0.02, "max_force": 100.0, "dt": 0.001 }, "adaptive_smc": { "gains": [12, 10, 6, 5, 2.5], "boundary_layer": 0.02, "K_min": 0.1, "K_max": 100.0, "leak_rate": 0.01, "adapt_rate_limit": 10.0, "K_init": 10.0, "alpha": 0.5, "max_force": 150.0, "dt": 0.001 } }
}
``` ## Validation and Testing ### Post-Migration Validation ```python

def validate_migrated_configuration(config_file_path: str) -> bool: """ Validate that migrated configuration works correctly. Returns: True if validation passes, False otherwise """ try: # Load migrated configuration with open(config_file_path, 'r') as f: if config_file_path.endswith(('.yml', '.yaml')): import yaml config_data = yaml.safe_load(f) else: import json config_data = json.load(f) # Test controller creation from src.controllers.factory import create_controller from src.plant.configurations import ConfigurationFactory plant_config = ConfigurationFactory.create_default_config("simplified") validation_results = {} if 'controllers' in config_data: for controller_type, controller_config in config_data['controllers'].items(): try: # Create controller with migrated configuration controller = create_controller( controller_type=controller_type, config=plant_config, gains=controller_config.get('gains') ) # Test basic functionality test_state = np.array([0.1, 0.1, 0.1, 0.0, 0.0, 0.0]) control_output = controller.compute_control(test_state, (), {}) validation_results[controller_type] = { 'creation_success': True, 'control_computation_success': True, 'control_value': control_output.u if hasattr(control_output, 'u') else control_output } print(f"✓ {controller_type} validation passed") except Exception as e: validation_results[controller_type] = { 'creation_success': False, 'error': str(e) } print(f"✗ {controller_type} validation failed: {e}") # Overall validation result all_passed = all( result.get('creation_success', False) for result in validation_results.values() ) print(f"\nValidation Summary:") print(f"Controllers tested: {len(validation_results)}") print(f"Successful: {sum(1 for r in validation_results.values() if r.get('creation_success', False))}") print(f"Overall result: {'PASS' if all_passed else 'FAIL'}") return all_passed except Exception as e: print(f"Validation error: {e}") return False # Example usage
validation_passed = validate_migrated_configuration("config_migrated.yaml")
``` ### Migration Testing Suite ```python
# example-metadata:
# runnable: false def run_migration_test_suite() -> None: """ test suite for migration functionality. """ print("=== Migration Test Suite ===\n") # Test 1: Classical SMC migration print("Test 1: Classical SMC Migration") old_classical = { 'gains': [10, 5, 8, 3, 15], 'K_switching': 2.0, 'gamma': 0.1, 'switch_function': 'sign' } new_classical = migrate_classical_smc_manually(old_classical) # Validation checks assert len(new_classical['gains']) == 6, "Classical SMC should have 6 gains" assert new_classical['gains'][5] == 2.0, "K_switching should be integrated" assert 'gamma' not in new_classical, "Invalid gamma should be removed" assert new_classical.get('switch_method') == 'sign', "switch_function should be renamed" print("✓ Classical SMC migration test passed\n") # Test 2: Adaptive SMC migration print("Test 2: Adaptive SMC Migration") old_adaptive = { 'gains': [12, 10, 6, 5], 'adaptation_gain': 2.5, 'boundary_layer_thickness': 0.02, 'estimate_bounds': [0.1, 100.0] } new_adaptive = migrate_adaptive_smc_manually(old_adaptive) # Validation checks assert len(new_adaptive['gains']) == 5, "Adaptive SMC should have 5 gains" assert new_adaptive['gains'][4] == 2.5, "Adaptation gain should be integrated" assert new_adaptive.get('boundary_layer') == 0.02, "Parameter should be renamed" assert new_adaptive.get('K_min') == 0.1, "estimate_bounds should be split" assert new_adaptive.get('K_max') == 100.0, "estimate_bounds should be split" print("✓ Adaptive SMC migration test passed\n") # Test 3: STA-SMC migration print("Test 3: STA-SMC Migration") old_sta = { 'K1': 35.0, 'K2': 20.0, 'gains': [25, 18, 12, 8], 'alpha_power': 0.5 } new_sta = migrate_sta_smc_manually(old_sta) # Validation checks assert len(new_sta['gains']) == 6, "STA-SMC should have 6 gains" assert new_sta['gains'][0] == 35.0, "K1 should be first gain" assert new_sta['gains'][1] == 20.0, "K2 should be second gain" assert new_sta.get('power_exponent') == 0.5, "alpha_power should be renamed" print("✓ STA-SMC migration test passed\n") print("All migration tests passed! ✓") # Run the test suite
run_migration_test_suite()
``` ## Common Migration Issues and approaches ### Issue 1: Missing Required Parameters **Problem**: Controller creation fails due to missing required parameters after migration. **Solution**:

```python
# example-metadata:
# runnable: false def fix_missing_parameters(controller_type: str, config: Dict[str, Any]) -> Dict[str, Any]: """Add missing required parameters with safe defaults.""" required_defaults = { 'classical_smc': { 'boundary_layer': 0.02, 'max_force': 150.0, 'dt': 0.001 }, 'adaptive_smc': { 'leak_rate': 0.01, 'adapt_rate_limit': 10.0, 'K_min': 0.1, 'K_max': 100.0, 'K_init': 10.0, 'alpha': 0.5, 'max_force': 150.0, 'dt': 0.001 }, 'sta_smc': { 'power_exponent': 0.5, 'regularization': 1e-6, 'boundary_layer': 0.01, 'switch_method': 'tanh', 'max_force': 150.0, 'dt': 0.001 } } if controller_type in required_defaults: for param, default_value in required_defaults[controller_type].items(): config.setdefault(param, default_value) return config
``` ### Issue 2: Invalid Gain Array Lengths **Problem**: Gain arrays have incorrect number of elements after migration. **Solution**:

```python
# example-metadata:
# runnable: false def fix_gain_array_length(controller_type: str, gains: List[float]) -> List[float]: """Fix gain array length to match controller requirements.""" expected_lengths = { 'classical_smc': 6, 'adaptive_smc': 5, 'sta_smc': 6, 'hybrid_adaptive_sta_smc': 4 } expected_length = expected_lengths.get(controller_type, 6) if len(gains) < expected_length: # Pad with reasonable defaults default_gains = { 'classical_smc': [8.0, 6.0, 4.0, 3.0, 15.0, 2.0], 'adaptive_smc': [12.0, 10.0, 6.0, 5.0, 2.5], 'sta_smc': [35.0, 20.0, 25.0, 18.0, 12.0, 8.0], 'hybrid_adaptive_sta_smc': [18.0, 12.0, 10.0, 8.0] } defaults = default_gains.get(controller_type, [1.0] * expected_length) gains.extend(defaults[len(gains):expected_length]) elif len(gains) > expected_length: # Truncate to expected length gains = gains[:expected_length] return gains
``` ### Issue 3: Configuration Format Incompatibility **Problem**: Old configuration format is not recognized by new factory system. **Solution**:

```python
# example-metadata:
# runnable: false def convert_legacy_format(old_config: Dict[str, Any]) -> Dict[str, Any]: """Convert legacy configuration format to new structure.""" new_config = {} # Handle legacy controller_defaults structure if 'controller_defaults' in old_config: new_config['controllers'] = old_config['controller_defaults'] # Handle direct controller configuration elif 'controllers' not in old_config: # Assume root-level controller configuration controllers = {} for key, value in old_config.items(): if key in ['classical_smc', 'adaptive_smc', 'sta_smc', 'hybrid_adaptive_sta_smc']: controllers[key] = value if controllers: new_config['controllers'] = controllers else: new_config = old_config else: new_config = old_config return new_config
``` ## Best Practices for Migration ### 1. Always Create Backups ```python
# Always backup before migration

backup_created = create_backup_before_migration(config_file)
assert backup_created, "Backup creation failed - aborting migration"
``` ### 2. Validate Before and After ```python
# Pre-migration validation
pre_validation = validate_configuration_syntax(original_config)
if not pre_validation.success: raise ValueError(f"Original configuration invalid: {pre_validation.errors}") # Post-migration validation
post_validation = validate_migrated_configuration(migrated_config)
if not post_validation.success: restore_from_backup(backup_file) raise ValueError("Migration validation failed - restored from backup")
``` ### 3. Test with Sample Data ```python
# Test migrated configuration with sample scenarios

test_scenarios = [ np.array([0.1, 0.1, 0.1, 0.0, 0.0, 0.0]), # Small disturbance np.array([0.3, 0.4, 0.2, 0.1, 0.0, 0.0]), # Medium angles
] for scenario in test_scenarios: control_output = migrated_controller.compute_control(scenario, (), {}) assert np.isfinite(control_output.u), "Control output must be finite"
``` ### 4. Document Migration Changes ```python
# example-metadata:
# runnable: false def document_migration_changes(migration_log: List[str]) -> str: """Create documentation of migration changes for reference.""" timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") doc = f"""
Migration Report - {timestamp} Changes Applied:
{chr(10).join(f"- {change}" for change in migration_log)} Validation Status: PASSED
Next Steps:
- Update any hardcoded parameter references in code
- Test controllers with actual plant dynamics
- Update documentation and training materials
""" return doc
``` ## SimulationRunner API Migration (v2.0+)

### Overview

Starting in v2.0, the `SimulationRunner` class-based API has been deprecated in favor of the functional `run_simulation` API. The new functional API provides better composability, clearer interfaces, and easier testing.

### Migration Pattern

```python
# example-metadata:
# runnable: false

# OLD API (SimulationRunner class - DEPRECATED)
from src.core.simulation_runner import SimulationRunner
from src.controllers.factory import create_controller
from src.core.dynamics import DIPDynamics
from src.config import load_config

config = load_config("config.yaml")
controller = create_controller('classical_smc', config)
dynamics = DIPDynamics(config)

# Class-based approach
runner = SimulationRunner(controller, dynamics, config)
result = runner.run()

# Access results from result object
settling_time = result.settling_time
overshoot = result.max_theta1
energy = np.sum(result.control_history**2) * config.simulation.dt
time_vector = result.time_history
states = result.state_history
controls = result.control_history

# NEW API (run_simulation function - RECOMMENDED)
from src.core.simulation_runner import run_simulation  # Note: functional import
from src.controllers.factory import create_controller
from src.core.dynamics import DIPDynamics
from src.config import load_config

config = load_config("config.yaml")
controller = create_controller('classical_smc', config)
dynamics = DIPDynamics(config)

# Functional approach
t_arr, x_arr, u_arr = run_simulation(
    controller=controller,
    dynamics_model=dynamics,
    sim_time=config.simulation.duration,
    dt=config.simulation.dt,
    initial_state=config.simulation.initial_state
)

# Calculate metrics from raw arrays
def calculate_settling_time(t, x):
    cart_pos = x[:, 0]
    final_pos = cart_pos[-1]
    threshold = 0.02 * abs(final_pos) if abs(final_pos) > 1e-6 else 0.02
    settled_idx = np.where(np.abs(cart_pos - final_pos) < threshold)[0]
    return t[settled_idx[0]] if len(settled_idx) > 0 else t[-1]

settling_time = calculate_settling_time(t_arr, x_arr)
overshoot = np.max(np.abs(x_arr[:, 2]))  # theta1
energy = np.sum(u_arr**2) * (t_arr[1] - t_arr[0])
time_vector = t_arr
states = x_arr
controls = u_arr
```

### Key Differences

1. **Function vs Class**: Use `run_simulation()` function instead of `SimulationRunner` class
2. **Return Values**: Returns tuple `(t_arr, x_arr, u_arr)` instead of result object
3. **Metrics**: Calculate metrics manually from raw arrays
4. **Parameters**: Keyword-only parameters extracted from config
5. **Import Path**: Same module `src.core.simulation_runner`, different symbol

### Helper Functions for Metrics

```python
def calculate_metrics(t_arr, x_arr, u_arr):
    """Calculate performance metrics from raw simulation arrays."""
    # Settling time
    cart_pos = x_arr[:, 0]
    final_pos = cart_pos[-1]
    threshold = 0.02 * abs(final_pos) if abs(final_pos) > 1e-6 else 0.02
    settled_idx = np.where(np.abs(cart_pos - final_pos) < threshold)[0]
    settling_time = t_arr[settled_idx[0]] if len(settled_idx) > 0 else t_arr[-1]

    # Overshoot (theta1)
    max_theta1 = np.max(np.abs(x_arr[:, 2]))

    # Energy
    dt = t_arr[1] - t_arr[0]
    energy = np.sum(u_arr**2) * dt

    # Convergence check
    final_window = int(len(x_arr) * 0.1)
    theta1_final = x_arr[-final_window:, 2]
    theta2_final = x_arr[-final_window:, 3]
    converged = (np.all(np.abs(theta1_final) < np.deg2rad(5)) and
                 np.all(np.abs(theta2_final) < np.deg2rad(5)))

    return {
        'settling_time': settling_time,
        'max_theta1': max_theta1,
        'energy': energy,
        'converged': converged
    }

# Usage
metrics = calculate_metrics(t_arr, x_arr, u_arr)
print(f"Settling time: {metrics['settling_time']:.2f}s")
print(f"Overshoot: {np.rad2deg(metrics['max_theta1']):.2f} deg")
print(f"Energy: {metrics['energy']:.1f} J")
```

### Monte Carlo Simulations

```python
# OLD API
for run in range(n_runs):
    runner = SimulationRunner(controller, dynamics, config)
    result = runner.run()
    if result.converged:
        results.append(result.settling_time)

# NEW API
for run in range(n_runs):
    t_arr, x_arr, u_arr = run_simulation(
        controller=controller,
        dynamics_model=dynamics,
        sim_time=config.simulation.duration,
        dt=config.simulation.dt,
        initial_state=config.simulation.initial_state
    )
    metrics = calculate_metrics(t_arr, x_arr, u_arr)
    if metrics['converged']:
        results.append(metrics['settling_time'])
```

### Migration Checklist

- [ ] Replace `from src.core.simulation_runner import SimulationRunner` with `from src.core.simulation_runner import run_simulation`
- [ ] Change `runner = SimulationRunner(...); result = runner.run()` to `t_arr, x_arr, u_arr = run_simulation(...)`
- [ ] Update parameter calls: extract `sim_time`, `dt`, `initial_state` from `config`
- [ ] Replace `result.property` access with metric calculation functions
- [ ] Update plotting code to use `(t_arr, x_arr, u_arr)` instead of `result` object
- [ ] Test migrated code with end-to-end simulation

### Benefits of Functional API

1. **Composability**: Easier to chain with other functional operations
2. **Testing**: Simpler mocking and unit testing
3. **Clarity**: Explicit parameters make dependencies clear
4. **Performance**: No object overhead for large batch simulations
5. **Flexibility**: Easy to customize metrics calculation

---

This migration guide provides the tools, procedures, and best practices necessary to successfully transition from older controller factory configurations to the enhanced GitHub Issue #6 implementation, ensuring system stability and backward compatibility throughout the migration process.