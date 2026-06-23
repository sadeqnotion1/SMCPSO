#==========================================================================================\\\
#================ docs/pso_troubleshooting_maintenance_manual.md ====================\\\
#==========================================================================================\\\

# PSO Troubleshooting and Maintenance Manual
**Double-Inverted Pendulum Sliding Mode Control System** ## Executive Summary This manual provides detailed troubleshooting procedures, maintenance guidelines, and diagnostic tools for the Particle Swarm Optimization (PSO) integration system within the Double-Inverted Pendulum Sliding Mode Control framework. The manual covers common issues, systematic debugging approaches, preventive maintenance, and performance optimization techniques to ensure reliable PSO operation. **Manual Scope:**
- **Diagnostic Procedures**: Systematic issue identification and resolution
- **Common Problems**: Frequently encountered issues with proven approaches - **Performance Optimization**: System tuning for optimal PSO performance
- **Preventive Maintenance**: Regular maintenance procedures and monitoring
- **Emergency Recovery**: Critical failure recovery procedures **Target Audience**: System administrators, control engineers, and maintenance personnel

---

## 1. Diagnostic Framework ### 1.1 PSO System Health Check **System Status Assessment:**

```python
# example-metadata:
# runnable: false #!/usr/bin/env python3
"""PSO System Health Checker""" import numpy as np
import json
import subprocess
import psutil
import time
from pathlib import Path
from src.config import load_config
from src.controllers.factory import ControllerFactory
from src.optimization.algorithms.pso_optimizer import PSOTuner class PSOHealthChecker: """PSO system health assessment.""" def __init__(self, config_path="config.yaml"): self.config_path = config_path self.health_report = { 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'overall_status': 'unknown', 'component_status': {}, 'performance_metrics': {}, 'issues_found': [], 'recommendations': [] } def run_comprehensive_check(self): """Execute complete health check suite.""" print("🔍 Starting PSO System Health Check...") # Component checks self._check_configuration() self._check_controller_factory() self._check_pso_engine() self._check_simulation_engine() self._check_dependencies() self._check_system_resources() # Performance benchmarks self._benchmark_performance() # Overall assessment self._assess_overall_health() return self.health_report def _check_configuration(self): """Validate PSO configuration integrity.""" print(" 📋 Checking configuration...") try: config = load_config(self.config_path) issues = [] # Check required sections required_sections = ['pso', 'cost_function', 'simulation', 'controllers'] for section in required_sections: if not hasattr(config, section): issues.append(f"Missing configuration section: {section}") # Validate PSO parameters if hasattr(config, 'pso'): pso_cfg = config.pso if not (10 <= getattr(pso_cfg, 'n_particles', 0) <= 200): issues.append("PSO n_particles outside recommended range [10, 200]") if not (20 <= getattr(pso_cfg, 'n_iterations', 0) <= 1000): issues.append("PSO n_iterations outside recommended range [20, 1000]") # Validate bounds if hasattr(config.pso, 'bounds'): for ctrl_type in ['classical_smc', 'sta_smc', 'adaptive_smc']: if hasattr(config.pso.bounds, ctrl_type): bounds = getattr(config.pso.bounds, ctrl_type) lower = np.array(bounds.lower) upper = np.array(bounds.upper) if not np.all(lower < upper): issues.append(f"Invalid bounds for {ctrl_type}: lower >= upper") self.health_report['component_status']['configuration'] = { 'status': 'healthy' if not issues else 'issues', 'issues': issues } except Exception as e: self.health_report['component_status']['configuration'] = { 'status': 'failed', 'error': str(e) } def _check_controller_factory(self): """Test controller factory functionality.""" print(" 🏭 Checking controller factory...") try: issues = [] test_results = {} # Test each controller type controller_tests = { 'classical_smc': np.array([5.0, 3.0, 7.0, 2.0, 25.0, 1.0]), 'sta_smc': np.array([8.0, 4.0, 12.0, 6.0, 4.85, 3.43]), 'adaptive_smc': np.array([5.0, 3.0, 7.0, 2.0, 1.5]), 'hybrid_adaptive_sta_smc': np.array([5.0, 5.0, 5.0, 0.5]) } for ctrl_type, test_gains in controller_tests.items(): try: controller = ControllerFactory.create_controller(ctrl_type, test_gains) # Test required attributes if not hasattr(controller, 'max_force'): issues.append(f"{ctrl_type}: Missing max_force property") if not hasattr(controller, 'compute_control'): issues.append(f"{ctrl_type}: Missing compute_control method") # Test control computation test_state = np.array([0.1, 0.05, 0.0, 0.0, 0.0, 0.0]) control = controller.compute_control(test_state) if not np.isfinite(control): issues.append(f"{ctrl_type}: Non-finite control output") test_results[ctrl_type] = 'passed' except Exception as e: issues.append(f"{ctrl_type}: Factory creation failed - {str(e)}") test_results[ctrl_type] = 'failed' self.health_report['component_status']['controller_factory'] = { 'status': 'healthy' if not issues else 'issues', 'test_results': test_results, 'issues': issues } except Exception as e: self.health_report['component_status']['controller_factory'] = { 'status': 'failed', 'error': str(e) } def _check_pso_engine(self): """Test PSO optimization engine.""" print(" 🔬 Checking PSO engine...") try: config = load_config(self.config_path) # Create test factory def test_factory(gains): return ControllerFactory.create_controller('classical_smc', gains) # Initialize PSO tuner pso_tuner = PSOTuner(test_factory, config, seed=42) # Quick optimization test (minimal resources) test_bounds = ( np.array([1.0, 1.0, 1.0, 1.0, 1.0, 0.1]), np.array([10.0, 10.0, 10.0, 10.0, 50.0, 5.0]) ) start_time = time.time() results = pso_tuner.optimize( bounds=test_bounds, n_particles=10, n_iterations=5, verbose=False ) optimization_time = time.time() - start_time issues = [] if not results.get('success', False): issues.append("PSO optimization test failed") if optimization_time > 30: # Should complete quickly issues.append(f"PSO test took too long: {optimization_time:.1f}s") if not np.all(np.isfinite(results.get('best_gains', [np.nan]))): issues.append("PSO returned non-finite gains") self.health_report['component_status']['pso_engine'] = { 'status': 'healthy' if not issues else 'issues', 'test_time': optimization_time, 'test_result': results.get('success', False), 'issues': issues } except Exception as e: self.health_report['component_status']['pso_engine'] = { 'status': 'failed', 'error': str(e) } def _check_simulation_engine(self): """Test vectorized simulation engine.""" print(" 🎯 Checking simulation engine...") try: from src.simulation.engines.vector_sim import simulate_system_batch # Test controller factory def test_factory(gains): return ControllerFactory.create_controller('classical_smc', gains) # Test particles test_particles = np.array([ [5.0, 3.0, 7.0, 2.0, 25.0, 1.0], [4.0, 2.5, 6.0, 1.8, 20.0, 0.8] ]) start_time = time.time() result = simulate_system_batch( controller_factory=test_factory, particles=test_particles, sim_time=1.0, # Short simulation dt=0.01, u_max=150.0 ) sim_time = time.time() - start_time issues = [] if result is None: issues.append("Simulation returned None") else: t, x_batch, u_batch, sigma_batch = result if not np.all(np.isfinite(x_batch)): issues.append("Simulation produced non-finite states") if not np.all(np.isfinite(u_batch)): issues.append("Simulation produced non-finite controls") if sim_time > 5.0: # Should be fast for short simulation issues.append(f"Simulation too slow: {sim_time:.1f}s") self.health_report['component_status']['simulation_engine'] = { 'status': 'healthy' if not issues else 'issues', 'test_time': sim_time, 'issues': issues } except Exception as e: self.health_report['component_status']['simulation_engine'] = { 'status': 'failed', 'error': str(e) } def _check_dependencies(self): """Check critical dependencies.""" print(" 📦 Checking dependencies...") required_packages = { 'numpy': '1.20.0', 'scipy': '1.7.0', 'matplotlib': '3.3.0', 'pyyaml': '5.4.0' } issues = [] installed_versions = {} for package, min_version in required_packages.items(): try: module = __import__(package) version = getattr(module, '__version__', 'unknown') installed_versions[package] = version # Simple version comparison (for basic cases) if version != 'unknown': try: from packaging import version as pkg_version if pkg_version.parse(version) < pkg_version.parse(min_version): issues.append(f"{package} version {version} < required {min_version}") except ImportError: pass # Skip version comparison if packaging not available except ImportError: issues.append(f"Missing required package: {package}") installed_versions[package] = 'not installed' self.health_report['component_status']['dependencies'] = { 'status': 'healthy' if not issues else 'issues', 'installed_versions': installed_versions, 'issues': issues } def _check_system_resources(self): """Check system resource availability.""" print(" 💻 Checking system resources...") # Memory check memory = psutil.virtual_memory() available_gb = memory.available / (1024**3) # CPU check cpu_count = psutil.cpu_count() cpu_percent = psutil.cpu_percent(interval=1) # Disk space check disk = psutil.disk_usage('.') free_gb = disk.free / (1024**3) issues = [] if available_gb < 1.0: issues.append(f"Low memory: {available_gb:.1f}GB available") if cpu_percent > 90: issues.append(f"High CPU usage: {cpu_percent:.1f}%") if free_gb < 1.0: issues.append(f"Low disk space: {free_gb:.1f}GB free") self.health_report['component_status']['system_resources'] = { 'status': 'healthy' if not issues else 'issues', 'memory_gb': available_gb, 'cpu_percent': cpu_percent, 'disk_free_gb': free_gb, 'cpu_count': cpu_count, 'issues': issues } def _benchmark_performance(self): """Run performance benchmarks.""" print(" ⚡ Running performance benchmarks...") try: # Quick PSO benchmark config = load_config(self.config_path) def benchmark_factory(gains): return ControllerFactory.create_controller('classical_smc', gains) pso_tuner = PSOTuner(benchmark_factory, config, seed=42) # Benchmark optimization iteration start_time = time.time() results = pso_tuner.optimize( bounds=(np.array([1.0, 1.0, 1.0, 1.0, 1.0, 0.1]), np.array([10.0, 10.0, 10.0, 10.0, 50.0, 5.0])), n_particles=20, n_iterations=10 ) benchmark_time = time.time() - start_time self.health_report['performance_metrics'] = { 'benchmark_time': benchmark_time, 'time_per_iteration': benchmark_time / 10, 'particles_per_second': (20 * 10) / benchmark_time, 'optimization_success': results.get('success', False) } except Exception as e: self.health_report['performance_metrics'] = { 'benchmark_failed': str(e) } def _assess_overall_health(self): """Assess overall system health.""" component_statuses = [ comp['status'] for comp in self.health_report['component_status'].values() ] failed_components = sum(1 for status in component_statuses if status == 'failed') issue_components = sum(1 for status in component_statuses if status == 'issues') if failed_components > 0: self.health_report['overall_status'] = 'critical' self.health_report['recommendations'].append("Critical components failed - system unusable") elif issue_components > 2: self.health_report['overall_status'] = 'degraded' self.health_report['recommendations'].append("Multiple issues detected - maintenance required") elif issue_components > 0: self.health_report['overall_status'] = 'warnings' self.health_report['recommendations'].append("Minor issues detected - monitoring recommended") else: self.health_report['overall_status'] = 'healthy' self.health_report['recommendations'].append("System operating normally") # Performance recommendations perf = self.health_report.get('performance_metrics', {}) if perf.get('time_per_iteration', 0) > 2.0: self.health_report['recommendations'].append("Slow optimization performance - consider system tuning") def save_report(self, filename='pso_health_report.json'): """Save health report to file.""" with open(filename, 'w') as f: json.dump(self.health_report, f, indent=2) print(f"📊 Health report saved to: {filename}") def print_summary(self): """Print health check summary.""" status_colors = { 'healthy': '✅', 'warnings': '⚠️', 'degraded': '🔶', 'critical': '❌', 'failed': '💥' } print(f"\n{'='*60}") print(f"🏥 PSO SYSTEM HEALTH REPORT") print(f"{'='*60}") print(f"Overall Status: {status_colors.get(self.health_report['overall_status'], '❓')} {self.health_report['overall_status'].upper()}") print(f"Timestamp: {self.health_report['timestamp']}") print(f"\n🔧 Component Status:") for component, status_info in self.health_report['component_status'].items(): status = status_info['status'] print(f" {status_colors.get(status, '❓')} {component}: {status}") if 'issues' in status_info and status_info['issues']: for issue in status_info['issues']: print(f" - {issue}") print(f"\n📈 Performance Metrics:") perf = self.health_report.get('performance_metrics', {}) if 'time_per_iteration' in perf: print(f" ⏱️ Time per iteration: {perf['time_per_iteration']:.2f}s") print(f" 🚀 Particles per second: {perf['particles_per_second']:.1f}") print(f"\n💡 Recommendations:") for rec in self.health_report['recommendations']: print(f" • {rec}") # Usage
if __name__ == "__main__": checker = PSOHealthChecker() health_report = checker.run_comprehensive_check() checker.print_summary() checker.save_report()
``` ### 1.2 Quick Diagnostic Commands **Essential System Checks:**

```bash
# Quick health check
python -c "
from docs.pso_troubleshooting_maintenance_manual import PSOHealthChecker
checker = PSOHealthChecker()
report = checker.run_comprehensive_check()
checker.print_summary()
" # Test basic PSO functionality
python simulate.py --ctrl classical_smc --run-pso \ --pso-particles 5 --pso-iterations 3 \ --save diagnostic_test.json # Validate configuration
python -c "
from src.config import load_config
try: config = load_config('config.yaml') print('✅ Configuration valid')
except Exception as e: print(f'❌ Configuration error: {e}')
" # Check dependencies
python -c "
packages = ['numpy', 'scipy', 'matplotlib', 'pyyaml']
for pkg in packages: try: module = __import__(pkg) version = getattr(module, '__version__', 'unknown') print(f'✅ {pkg}: {version}') except ImportError: print(f'❌ {pkg}: not installed')
"
```

---

## 2. Common Issues and approaches ### 2.1 Optimization Failures **Issue: PSO Optimization Fails to Start** *Symptoms:*

- Error immediately after starting optimization
- "ModuleNotFoundError" or "ImportError"
- Configuration validation errors *Diagnostic Steps:*
```bash
# Check configuration syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))" # Verify controller factory
python -c "
from src.controllers.factory import ControllerFactory
import numpy as np
try: ctrl = ControllerFactory.create_controller('classical_smc', np.array([1,1,1,1,1,1])) print('✅ Controller factory working')
except Exception as e: print(f'❌ Controller factory error: {e}')
" # Test PSO imports
python -c "
try: from src.optimization.algorithms.pso_optimizer import PSOTuner print('✅ PSO imports successful')
except Exception as e: print(f'❌ PSO import error: {e}')
"
``` *Solutions:*

1. **Missing Dependencies:** ```bash pip install numpy scipy matplotlib pyyaml pyswarms ``` 2. **Configuration Errors:** ```bash # Validate YAML syntax python -c " import yaml try: with open('config.yaml') as f: yaml.safe_load(f) print('Configuration syntax OK') except yaml.YAMLError as e: print(f'YAML Error: {e}') " ``` 3. **Path Issues:** ```bash # Add project root to Python path export PYTHONPATH="${PYTHONPATH}:/path/to/dip-smc-pso" ``` **Issue: PSO Converges to Poor Solutions** *Symptoms:*
- Final cost > 500 after 100 iterations
- Controller performs poorly in simulation
- Gains at parameter bounds *Diagnostic Steps:*
```python
# Analyze convergence history
import json
import matplotlib.pyplot as plt with open('optimization_results.json', 'r') as f: results = json.load(f) cost_history = results.get('cost_history', [])
plt.plot(cost_history)
plt.title('PSO Convergence History')
plt.xlabel('Iteration')
plt.ylabel('Best Cost')
plt.show() # Check final gains against bounds
gains = results['best_gains']
bounds = results.get('bounds', {})
print(f"Final gains: {gains}")
print(f"At lower bound: {[g <= b+0.001 for g, b in zip(gains, bounds.get('lower', []))]}")
print(f"At upper bound: {[g >= b-0.001 for g, b in zip(gains, bounds.get('upper', []))]}")
``` *Solutions:*

1. **Expand Search Space:** ```yaml # In config.yaml pso: bounds: classical_smc: lower: [0.1, 0.1, 0.1, 0.1, 0.1, 0.1] # Reduce lower bounds upper: [30.0, 30.0, 30.0, 30.0, 200.0, 20.0] # Increase upper bounds ``` 2. **Increase Population Diversity:** ```bash python simulate.py --ctrl classical_smc --run-pso \ --pso-particles 100 \ --cognitive-weight 2.0 \ --social-weight 1.0 ``` 3. **Multi-Start Optimization:** ```bash # Run multiple optimizations with different seeds for seed in {42,123,456,789,999}; do python simulate.py --ctrl classical_smc --run-pso \ --seed $seed \ --save results_seed_$seed.json done ``` ### 2.2 Performance Issues **Issue: Slow Optimization (>30s per iteration)** *Symptoms:*
- Each iteration takes excessive time
- High CPU/memory usage
- System becomes unresponsive *Diagnostic Steps:*
```python
# example-metadata:
# runnable: false # Profile optimization performance
import time
import psutil
import os def profile_pso_iteration(): """Profile single PSO iteration.""" process = psutil.Process(os.getpid()) # Baseline measurements start_time = time.time() start_memory = process.memory_info().rss / 1024 / 1024 # MB # Run minimal PSO test # ... PSO code here ... end_time = time.time() end_memory = process.memory_info().rss / 1024 / 1024 # MB print(f"Iteration time: {end_time - start_time:.2f}s") print(f"Memory usage: {end_memory:.1f}MB (Δ{end_memory - start_memory:.1f}MB)") print(f"CPU count: {psutil.cpu_count()}") print(f"CPU usage: {psutil.cpu_percent()}%") profile_pso_iteration()
``` *Solutions:*

1. **Reduce Simulation Complexity:** ```yaml # In config.yaml simulation: duration: 5.0 # Reduce from 10.0 dt: 0.002 # Increase from 0.001 ``` 2. **Optimize PSO Parameters:** ```bash python simulate.py --ctrl classical_smc --run-pso \ --pso-particles 25 \ --pso-iterations 200 # More iterations, fewer particles ``` 3. **Vectorization:** ```python # Check if Numba is available try: import numba print("✅ Numba available for acceleration") except ImportError: print("❌ Numba not available - install with: pip install numba") ``` **Issue: Memory Leaks During Optimization** *Symptoms:*
- Memory usage continuously increases
- System runs out of memory
- Optimization crashes with MemoryError *Diagnostic Steps:*
```python
# example-metadata:
# runnable: false import gc
import psutil
import matplotlib.pyplot as plt def monitor_memory_usage(): """Monitor memory usage during optimization.""" memory_samples = [] process = psutil.Process() # Sample memory every 10 iterations (add to PSO callback) def memory_callback(iteration, **kwargs): if iteration % 10 == 0: memory_mb = process.memory_info().rss / 1024 / 1024 memory_samples.append(memory_mb) print(f"Iteration {iteration}: Memory usage = {memory_mb:.1f}MB") # Force garbage collection gc.collect() return memory_callback, memory_samples # Use in optimization
callback, samples = monitor_memory_usage()
# results = pso_tuner.optimize(callback=callback, ...) # Plot memory usage
plt.plot(samples)
plt.title('Memory Usage During Optimization')
plt.xlabel('Sample')
plt.ylabel('Memory (MB)')
plt.show()
``` *Solutions:*

1. **Force Garbage Collection:** ```python
# example-metadata:

# runnable: false import gc def cleanup_callback(iteration, **kwargs): if iteration % 20 == 0: gc.collect() # Force garbage collection return False results = pso_tuner.optimize(callback=cleanup_callback, ...) ``` 2. **Reduce Memory Footprint:** ```python # Use smaller data types import numpy as np # In PSO configuration pso_config = { 'n_particles': 30, # Reduce from 50 'store_history': False, # Don't store full history 'dtype': np.float32 # Use 32-bit floats } ``` 3. **Batch Processing:** ```bash # Process controllers sequentially instead of parallel controllers=("classical_smc" "sta_smc" "adaptive_smc") for ctrl in "${controllers[@]}"; do python simulate.py --ctrl $ctrl --run-pso --save ${ctrl}_result.json sleep 5 # Allow memory cleanup between runs done ``` ### 2.3 Controller-Specific Issues **Issue: Unstable Optimized Controllers** *Symptoms:*

- Optimized gains produce unstable simulation
- System diverges rapidly
- NaN or infinite control outputs *Diagnostic Steps:*
```python
def diagnose_controller_stability(gains, controller_type): """Diagnose controller stability issues.""" from src.controllers.factory import ControllerFactory import numpy as np # Create controller controller = ControllerFactory.create_controller(controller_type, gains) # Test with various states test_states = [ np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]), # Equilibrium np.array([0.1, 0.1, 0.0, 0.0, 0.0, 0.0]), # Small perturbation np.array([0.5, 0.3, 0.1, 0.0, 0.0, 0.0]), # Large perturbation np.array([0.1, 0.1, 0.0, 0.2, 0.2, 0.0]) # With velocities ] print(f"🔍 Stability diagnosis for {controller_type}") print(f"Gains: {gains}") for i, state in enumerate(test_states): try: control = controller.compute_control(state) status = "✅" if np.isfinite(control) and abs(control) <= controller.max_force else "❌" print(f"Test {i+1}: {status} u = {control:.3f}, |u| <= {controller.max_force}") except Exception as e: print(f"Test {i+1}: ❌ Error: {e}") # Check gain ratios (controller-specific) if controller_type == 'classical_smc': lambda1, lambda2 = gains[1], gains[3] K = gains[4] print(f"λ₁/λ₂ ratio: {lambda1/lambda2:.2f} (should be 0.5-2.0)") print(f"K/λ₁ ratio: {K/lambda1:.2f} (should be 5-50)") # Usage
diagnose_controller_stability([5.0, 3.0, 7.0, 2.0, 25.0, 1.0], 'classical_smc')
``` *Solutions:*

1. **Constrain Gain Ratios:** ```python
# example-metadata:

# runnable: false def validate_gain_ratios(particles, controller_type): """Enhanced gain validation with ratio constraints.""" valid = np.ones(particles.shape[0], dtype=bool) if controller_type == 'classical_smc': c1, lambda1, c2, lambda2, K, kd = particles.T # Ratio constraints valid &= (lambda1 / lambda2 > 0.5) & (lambda1 / lambda2 < 2.0) valid &= (K / lambda1 > 5) & (K / lambda1 < 50) valid &= (kd / K > 0.01) & (kd / K < 0.5) return valid ``` 2. **Conservative Bounds:** ```yaml # More conservative parameter bounds pso: bounds: classical_smc: lower: [1.0, 1.0, 1.0, 1.0, 5.0, 0.5] upper: [15.0, 15.0, 15.0, 15.0, 75.0, 8.0] ``` 3. **Stability-Focused Cost Function:** ```yaml cost_function: weights: state_error: 1.0 control_effort: 0.01 control_rate: 0.001 stability: 100.0 # Heavily penalize instability ```

## 3. Performance Optimization ### 3.1 PSO Algorithm Tuning **Convergence Speed Optimization:** ```python

# example-metadata:

# runnable: false class OptimizedPSOConfig: """Optimized PSO configurations for different scenarios.""" @staticmethod def fast_exploration(): """Configuration for rapid initial exploration.""" return { 'n_particles': 30, 'n_iterations': 50, 'cognitive_weight': 2.5, 'social_weight': 0.5, 'inertia_weight': 0.9, 'velocity_clamp': [0.2, 0.8] } @staticmethod def precision_optimization(): """Configuration for high-precision results.""" return { 'n_particles': 100, 'n_iterations': 300, 'cognitive_weight': 1.49445, 'social_weight': 1.49445, 'inertia_weight': 0.729, 'w_schedule': [0.9, 0.4], 'tolerance': 1e-8 } @staticmethod def balanced_performance(): """Configuration balancing speed and quality.""" return { 'n_particles': 50, 'n_iterations': 150, 'cognitive_weight': 1.8, 'social_weight': 1.2, 'inertia_weight': 0.8, 'w_schedule': [0.8, 0.3], 'velocity_clamp': [0.1, 0.5] } # Usage

def optimize_with_config(controller_type, config_type='balanced'): """Optimize controller with specific PSO configuration.""" from src.optimization.algorithms.pso_optimizer import PSOTuner config_map = { 'fast': OptimizedPSOConfig.fast_exploration(), 'precision': OptimizedPSOConfig.precision_optimization(), 'balanced': OptimizedPSOConfig.balanced_performance() } pso_config = config_map[config_type] # Apply configuration and run optimization # ... implementation details
``` **Adaptive PSO Implementation:** ```python
# example-metadata:
# runnable: false class AdaptivePSOTuner(PSOTuner): """PSO tuner with adaptive parameter adjustment.""" def __init__(self, *args, **kwargs): super().__init__(*args, **kwargs) self.stagnation_threshold = 20 self.diversity_threshold = 0.01 self.restart_fraction = 0.3 def adaptive_callback(self, iteration, best_cost, best_position, **kwargs): """Adaptive PSO parameter adjustment callback.""" # Get swarm statistics diversity = kwargs.get('diversity', 0) cost_history = kwargs.get('cost_history', []) # Detect stagnation if len(cost_history) > self.stagnation_threshold: recent_improvement = cost_history[-self.stagnation_threshold] - cost_history[-1] if recent_improvement < 1e-6: print(f"🔄 Stagnation detected at iteration {iteration} - adapting parameters") self._adapt_for_stagnation() # Detect low diversity if diversity < self.diversity_threshold: print(f"🌟 Low diversity detected at iteration {iteration} - increasing exploration") self._adapt_for_low_diversity() # Convergence acceleration if iteration > 100 and iteration % 50 == 0: self._adapt_for_convergence(iteration) return False # Continue optimization def _adapt_for_stagnation(self): """Adapt parameters for stagnation recovery.""" # Increase cognitive weight, decrease social weight self.cognitive_weight *= 1.2 self.social_weight *= 0.8 # Restart some particles n_restart = int(self.n_particles * self.restart_fraction) # ... particle restart implementation def _adapt_for_low_diversity(self): """Adapt parameters for diversity enhancement.""" # Increase inertia weight temporarily self.inertia_weight = min(0.9, self.inertia_weight * 1.1) # Increase velocity limits if hasattr(self, 'velocity_clamp'): self.velocity_clamp = [v * 1.2 for v in self.velocity_clamp] def _adapt_for_convergence(self, iteration): """Adapt parameters for convergence acceleration.""" progress = iteration / self.max_iterations # Linear adaptation schedule self.inertia_weight = 0.9 - 0.5 * progress self.cognitive_weight = 2.0 - 0.5 * progress self.social_weight = 0.5 + 1.5 * progress
``` ### 3.2 Computational Optimization **Parallel Processing Setup:** ```python

import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import numpy as np class ParallelPSOOptimizer: """PSO optimizer with parallel fitness evaluation.""" def __init__(self, controller_factory, config, n_processes=None): self.controller_factory = controller_factory self.config = config self.n_processes = n_processes or mp.cpu_count() def parallel_fitness_evaluation(self, particles): """Evaluate fitness for particles in parallel.""" def evaluate_single_particle(gains): """Evaluate single particle fitness.""" try: controller = self.controller_factory(gains) # Simulate and compute cost cost = self._simulate_and_evaluate(controller) return cost except Exception as e: return float('inf') # Penalty for failed evaluation # Parallel evaluation with ProcessPoolExecutor(max_workers=self.n_processes) as executor: fitness_values = list(executor.map(evaluate_single_particle, particles)) return np.array(fitness_values) def _simulate_and_evaluate(self, controller): """Simulate controller and compute cost.""" # Implementation depends on simulation engine # This is a placeholder for the actual simulation pass # Usage
def parallel_optimization(controller_type, n_processes=4): """Run PSO optimization with parallel processing.""" def factory(gains): return ControllerFactory.create_controller(controller_type, gains) parallel_optimizer = ParallelPSOOptimizer( controller_factory=factory, config=load_config('config.yaml'), n_processes=n_processes ) results = parallel_optimizer.optimize( bounds=get_controller_bounds(controller_type), n_particles=50, n_iterations=100 ) return results
``` **Memory-Efficient Implementation:** ```python
# example-metadata:
# runnable: false class MemoryEfficientPSO: """PSO implementation optimized for memory usage.""" def __init__(self, max_memory_mb=1000): self.max_memory_mb = max_memory_mb self.memory_monitor = psutil.Process() def optimize_with_memory_management(self, *args, **kwargs): """Run optimization with active memory management.""" def memory_callback(iteration, **cb_kwargs): current_memory = self.memory_monitor.memory_info().rss / 1024 / 1024 if current_memory > self.max_memory_mb: print(f"⚠️ Memory limit exceeded: {current_memory:.1f}MB > {self.max_memory_mb}MB") # Force garbage collection import gc gc.collect() # Reduce particle count if memory still high new_memory = self.memory_monitor.memory_info().rss / 1024 / 1024 if new_memory > self.max_memory_mb * 0.9: self.n_particles = max(10, int(self.n_particles * 0.8)) print(f"🔽 Reduced particle count to {self.n_particles}") return False # Add memory callback to optimization kwargs['callback'] = memory_callback return self.base_optimize(*args, **kwargs) # Usage
memory_efficient_pso = MemoryEfficientPSO(max_memory_mb=2000)
results = memory_efficient_pso.optimize_with_memory_management(...)
``` ### 3.3 Simulation Optimization **Vectorized Simulation Enhancements:** ```python

def optimize_simulation_performance(): """Optimize simulation engine performance.""" # Check Numba availability and configuration try: import numba print(f"✅ Numba version: {numba.__version__}") # Configure Numba for optimal performance numba.config.THREADING_LAYER = 'omp' # Use OpenMP numba.config.NUMBA_NUM_THREADS = psutil.cpu_count() print(f"🚀 Numba configured for {numba.config.NUMBA_NUM_THREADS} threads") except ImportError: print("❌ Numba not available - install for acceleration:") print(" pip install numba") # Optimize NumPy settings import numpy as np print(f"📊 NumPy version: {np.__version__}") print(f"🔧 BLAS library: {np.__config__.get_info('blas_opt_info', {}).get('libraries', 'Unknown')}") # Check for optimized BLAS blas_info = np.__config__.get_info('blas_opt_info') if 'openblas' in str(blas_info).lower() or 'mkl' in str(blas_info).lower(): print("✅ Optimized BLAS library detected") else: print("⚠️ Basic BLAS - consider installing optimized version:") print(" conda install numpy mkl") # Run performance optimization check
optimize_simulation_performance()
``` **Adaptive Time Step Control:** ```python
# example-metadata:
# runnable: false class AdaptiveSimulation: """Simulation with adaptive time step for efficiency.""" def __init__(self, base_dt=0.001, max_dt=0.01, error_tolerance=1e-6): self.base_dt = base_dt self.max_dt = max_dt self.error_tolerance = error_tolerance def simulate_with_adaptive_timestep(self, controller, initial_state, duration): """Simulate with adaptive time step control.""" t = 0 state = initial_state.copy() dt = self.base_dt trajectory = {'t': [0], 'x': [state.copy()], 'u': [], 'dt': []} while t < duration: # Compute control u = controller.compute_control(state, dt=dt) # Try two time steps: dt and dt/2 state_full = self._integrate_step(state, u, dt) state_half1 = self._integrate_step(state, u, dt/2) state_half2 = self._integrate_step(state_half1, u, dt/2) # Estimate error error = np.linalg.norm(state_full - state_half2) if error < self.error_tolerance: # Accept step and possibly increase dt state = state_full t += dt trajectory['t'].append(t) trajectory['x'].append(state.copy()) trajectory['u'].append(u) trajectory['dt'].append(dt) # Increase time step if error is very small if error < self.error_tolerance / 4: dt = min(self.max_dt, dt * 1.2) else: # Reduce time step and retry dt = max(self.base_dt, dt * 0.5) return trajectory def _integrate_step(self, state, u, dt): """Single integration step (placeholder).""" # Implement actual dynamics integration # This is controller and system dependent pass
```

---

## 4. Preventive Maintenance ### 4.1 Regular Health Monitoring **Automated Health Check Script:** ```bash

#!/bin/bash
# pso_health_monitor.sh - Regular PSO system health monitoring LOG_FILE="/var/log/pso_health.log"

DATE=$(date '+%Y-%m-%d %H:%M:%S') echo "[$DATE] Starting PSO health check..." >> $LOG_FILE # Run health check
python3 -c "
from docs.pso_troubleshooting_maintenance_manual import PSOHealthChecker
import json checker = PSOHealthChecker()
report = checker.run_comprehensive_check() # Log summary
status = report['overall_status']
print(f'Health Status: {status}') # Save detailed report
checker.save_report('daily_health_report.json') # Alert on issues
if status in ['critical', 'degraded']: print('ALERT: PSO system issues detected!') exit(1)
else: print('PSO system healthy') exit(0)
" >> $LOG_FILE 2>&1 HEALTH_STATUS=$? if [ $HEALTH_STATUS -ne 0 ]; then echo "[$DATE] ❌ Health check failed - issues detected" >> $LOG_FILE # Send alert (email, Slack, etc.) # mail -s "PSO System Alert" admin@company.com < daily_health_report.json
else echo "[$DATE] ✅ Health check passed" >> $LOG_FILE
fi
``` **Cron Job Setup:**
```bash
# Add to crontab (crontab -e)

# Run health check daily at 2 AM

0 2 * * * /path/to/pso_health_monitor.sh # Run quick check every 4 hours
0 */4 * * * /path/to/quick_pso_check.sh
``` **Performance Monitoring Dashboard:** ```python
import matplotlib.pyplot as plt
import json
import pandas as pd
from datetime import datetime, timedelta class PSOPerformanceDashboard: """Performance monitoring dashboard for PSO system.""" def __init__(self, log_directory='./logs'): self.log_directory = Path(log_directory) def generate_performance_report(self, days=7): """Generate performance report for last N days.""" # Collect health reports reports = [] for i in range(days): date = datetime.now() - timedelta(days=i) report_file = self.log_directory / f"health_report_{date.strftime('%Y%m%d')}.json" if report_file.exists(): with open(report_file) as f: report = json.load(f) report['date'] = date reports.append(report) if not reports: print("No health reports found") return # Create performance dashboard fig, axes = plt.subplots(2, 2, figsize=(15, 10)) fig.suptitle('PSO System Performance Dashboard (Last 7 Days)') # Plot 1: Overall health status dates = [r['date'] for r in reports] statuses = [r['overall_status'] for r in reports] status_colors = {'healthy': 'green', 'warnings': 'yellow', 'degraded': 'orange', 'critical': 'red'} axes[0, 0].scatter(dates, range(len(dates)), c=[status_colors.get(s, 'gray') for s in statuses], s=100) axes[0, 0].set_title('System Health Status') axes[0, 0].set_yticks(range(len(dates))) axes[0, 0].set_yticklabels([d.strftime('%m/%d') for d in dates]) # Plot 2: Performance metrics perf_times = [r.get('performance_metrics', {}).get('time_per_iteration', 0) for r in reports] axes[0, 1].plot(dates, perf_times, 'b-o') axes[0, 1].set_title('Optimization Performance') axes[0, 1].set_ylabel('Time per Iteration (s)') axes[0, 1].tick_params(axis='x', rotation=45) # Plot 3: System resources memory_usage = [r.get('component_status', {}).get('system_resources', {}).get('memory_gb', 0) for r in reports] cpu_usage = [r.get('component_status', {}).get('system_resources', {}).get('cpu_percent', 0) for r in reports] axes[1, 0].plot(dates, memory_usage, 'g-o', label='Memory (GB)') axes[1, 0].plot(dates, cpu_usage, 'r-o', label='CPU (%)') axes[1, 0].set_title('System Resources') axes[1, 0].legend() axes[1, 0].tick_params(axis='x', rotation=45) # Plot 4: Component status summary component_names = ['configuration', 'controller_factory', 'pso_engine', 'simulation_engine'] component_health = {} for comp in component_names: health_scores = [] for report in reports: status = report.get('component_status', {}).get(comp, {}).get('status', 'unknown') score = {'healthy': 3, 'warnings': 2, 'issues': 1, 'failed': 0}.get(status, 0) health_scores.append(score) component_health[comp] = sum(health_scores) / len(health_scores) comp_names = list(component_health.keys()) comp_scores = list(component_health.values()) axes[1, 1].bar(comp_names, comp_scores, color=['green' if s > 2.5 else 'orange' if s > 1.5 else 'red' for s in comp_scores]) axes[1, 1].set_title('Component Health Average') axes[1, 1].set_ylabel('Health Score') axes[1, 1].tick_params(axis='x', rotation=45) plt.tight_layout() plt.savefig('pso_performance_dashboard.png', dpi=300, bbox_inches='tight') plt.show() # Generate summary statistics print("\n📊 PSO PERFORMANCE SUMMARY (Last 7 Days)") print("=" * 50) print(f"Average iteration time: {np.mean(perf_times):.2f}s") print(f"Best iteration time: {np.min(perf_times):.2f}s") print(f"Worst iteration time: {np.max(perf_times):.2f}s") print(f"Healthy days: {statuses.count('healthy')}/{len(statuses)}") return reports # Usage
dashboard = PSOPerformanceDashboard()
reports = dashboard.generate_performance_report(days=7)
``` ### 4.2 Configuration Management **Configuration Validation Pipeline:** ```python

import yaml
import jsonschema
from pathlib import Path class ConfigurationValidator: """Validate PSO configuration files.""" def __init__(self): self.schema = self._load_config_schema() def _load_config_schema(self): """Load configuration validation schema.""" return { "type": "object", "required": ["pso", "cost_function", "simulation", "controllers"], "properties": { "pso": { "type": "object", "required": ["n_particles", "n_iterations"], "properties": { "n_particles": {"type": "integer", "minimum": 5, "maximum": 500}, "n_iterations": {"type": "integer", "minimum": 10, "maximum": 2000}, "cognitive_weight": {"type": "number", "minimum": 0.1, "maximum": 5.0}, "social_weight": {"type": "number", "minimum": 0.1, "maximum": 5.0}, "inertia_weight": {"type": "number", "minimum": 0.1, "maximum": 1.0} } }, "cost_function": { "type": "object", "required": ["weights"], "properties": { "weights": { "type": "object", "required": ["state_error", "control_effort", "control_rate", "stability"], "properties": { "state_error": {"type": "number", "minimum": 0}, "control_effort": {"type": "number", "minimum": 0}, "control_rate": {"type": "number", "minimum": 0}, "stability": {"type": "number", "minimum": 0} } } } } } } def validate_config(self, config_path): """Validate configuration file.""" try: with open(config_path, 'r') as f: config = yaml.safe_load(f) # JSON Schema validation jsonschema.validate(config, self.schema) # Custom validations validation_results = { 'syntax_valid': True, 'schema_valid': True, 'warnings': [], 'errors': [] } # Check parameter ranges pso_config = config.get('pso', {}) if pso_config.get('n_particles', 0) * pso_config.get('n_iterations', 0) > 50000: validation_results['warnings'].append( "High computational load: particles × iterations > 50,000" ) # Check cost function weights weights = config.get('cost_function', {}).get('weights', {}) total_weight = sum(weights.values()) if weights else 0 if total_weight < 0.1: validation_results['warnings'].append( "Very low total cost function weights - optimization may be ineffective" ) return validation_results except yaml.YAMLError as e: return { 'syntax_valid': False, 'schema_valid': False, 'errors': [f"YAML syntax error: {e}"], 'warnings': [] } except jsonschema.ValidationError as e: return { 'syntax_valid': True, 'schema_valid': False, 'errors': [f"Schema validation error: {e.message}"], 'warnings': [] } def backup_config(self, config_path): """Create timestamped backup of configuration.""" config_file = Path(config_path) timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') backup_path = config_file.parent / f"{config_file.stem}_backup_{timestamp}{config_file.suffix}" shutil.copy2(config_path, backup_path) print(f"✅ Configuration backed up to: {backup_path}") return backup_path # Usage
validator = ConfigurationValidator()
validation_result = validator.validate_config('config.yaml') if validation_result['schema_valid']: print("✅ Configuration is valid") if validation_result['warnings']: print("⚠️ Warnings:") for warning in validation_result['warnings']: print(f" - {warning}")
else: print("❌ Configuration validation failed:") for error in validation_result['errors']: print(f" - {error}")
``` **Configuration Version Control:** ```bash
#!/bin/bash
# config_management.sh - Configuration version control CONFIG_DIR="/path/to/pso/config"
BACKUP_DIR="/path/to/pso/config/backups"
GIT_REPO="/path/to/pso/config/git" # Initialize git repository if it doesn't exist
if [ ! -d "$GIT_REPO/.git" ]; then echo "Initializing configuration git repository..." cd $GIT_REPO git init git add . git commit -m "Initial configuration commit"
fi # Function to save configuration version
save_config_version() { local description="$1" local timestamp=$(date '+%Y%m%d_%H%M%S') cd $GIT_REPO # Copy current configuration cp $CONFIG_DIR/config.yaml ./config_${timestamp}.yaml # Validate configuration python3 -c "
from docs.pso_troubleshooting_maintenance_manual import ConfigurationValidator
validator = ConfigurationValidator()
result = validator.validate_config('./config_${timestamp}.yaml')
print('Validation result:', 'PASS' if result['schema_valid'] else 'FAIL')
exit(0 if result['schema_valid'] else 1)
" if [ $? -eq 0 ]; then # Add to git git add config_${timestamp}.yaml git commit -m "Config update: $description (${timestamp})" echo "✅ Configuration version saved: $timestamp" else rm config_${timestamp}.yaml echo "❌ Configuration validation failed - version not saved" exit 1 fi
} # Function to restore configuration version
restore_config_version() { local version="$1" cd $GIT_REPO if [ -f "config_${version}.yaml" ]; then cp "config_${version}.yaml" "$CONFIG_DIR/config.yaml" echo "✅ Configuration restored to version: $version" else echo "❌ Version not found: $version" echo "Available versions:" ls config_*.yaml | sed 's/config_\(.*\)\.yaml/ \1/' exit 1 fi
} # Command line interface
case "$1" in save) save_config_version "$2" ;; restore) restore_config_version "$2" ;; list) cd $GIT_REPO echo "Available configuration versions:" ls config_*.yaml | sed 's/config_\(.*\)\.yaml/ \1/' ;; *) echo "Usage: $0 {save|restore|list} [description|version]" echo " save [description] - Save current configuration" echo " restore [version] - Restore specific version" echo " list - List available versions" exit 1 ;;
esac
``` ### 4.3 Database and Log Management **Log Rotation and Cleanup:** ```python
# example-metadata:

# runnable: false import logging

import logging.handlers
from pathlib import Path
import gzip
import os
from datetime import datetime, timedelta class PSOLogManager: """Centralized PSO log management.""" def __init__(self, log_directory='./logs', max_log_size_mb=100, backup_count=10): self.log_directory = Path(log_directory) self.log_directory.mkdir(exist_ok=True) self.max_log_size = max_log_size_mb * 1024 * 1024 # Convert to bytes self.backup_count = backup_count self._setup_loggers() def _setup_loggers(self): """Setup rotating file handlers for different log types.""" # PSO optimization logs pso_handler = logging.handlers.RotatingFileHandler( self.log_directory / 'pso_optimization.log', maxBytes=self.max_log_size, backupCount=self.backup_count ) pso_handler.setFormatter(logging.Formatter( '%(asctime)s - %(levelname)s - %(module)s - %(message)s' )) self.pso_logger = logging.getLogger('pso_optimization') self.pso_logger.addHandler(pso_handler) self.pso_logger.setLevel(logging.INFO) # System health logs health_handler = logging.handlers.RotatingFileHandler( self.log_directory / 'system_health.log', maxBytes=self.max_log_size, backupCount=self.backup_count ) health_handler.setFormatter(logging.Formatter( '%(asctime)s - %(levelname)s - %(message)s' )) self.health_logger = logging.getLogger('system_health') self.health_logger.addHandler(health_handler) self.health_logger.setLevel(logging.INFO) def log_optimization_start(self, controller_type, config): """Log optimization start.""" self.pso_logger.info(f"Starting PSO optimization for {controller_type}") self.pso_logger.info(f"PSO config: particles={config.get('n_particles')}, iterations={config.get('n_iterations')}") def log_optimization_result(self, controller_type, results): """Log optimization results.""" success = results.get('success', False) best_cost = results.get('best_cost', 'unknown') convergence_iter = results.get('convergence_iteration', 'unknown') self.pso_logger.info(f"PSO optimization for {controller_type} completed: success={success}") self.pso_logger.info(f"Best cost: {best_cost}, Convergence iteration: {convergence_iter}") if not success: self.pso_logger.warning(f"PSO optimization failed for {controller_type}") def log_health_check(self, health_status, issues): """Log system health check results.""" self.health_logger.info(f"Health check completed: status={health_status}") if issues: for issue in issues: self.health_logger.warning(f"Health issue: {issue}") def cleanup_old_logs(self, days_to_keep=30): """Clean up old log files.""" cutoff_date = datetime.now() - timedelta(days=days_to_keep) for log_file in self.log_directory.glob('*.log*'): if log_file.stat().st_mtime < cutoff_date.timestamp(): # Compress old logs before deletion if not log_file.name.endswith('.gz'): compressed_name = f"{log_file}.gz" with open(log_file, 'rb') as f_in: with gzip.open(compressed_name, 'wb') as f_out: f_out.writelines(f_in) os.remove(log_file) self.health_logger.info(f"Compressed and archived log: {log_file}") def get_log_summary(self, days=7): """Get summary of recent log activity.""" summary = { 'optimization_runs': 0, 'successful_optimizations': 0, 'health_checks': 0, 'warnings': 0, 'errors': 0 } cutoff_date = datetime.now() - timedelta(days=days) # Analyze PSO logs pso_log_file = self.log_directory / 'pso_optimization.log' if pso_log_file.exists(): with open(pso_log_file, 'r') as f: for line in f: # Parse log lines and count events if 'Starting PSO optimization' in line: summary['optimization_runs'] += 1 elif 'completed: success=True' in line: summary['successful_optimizations'] += 1 elif 'WARNING' in line: summary['warnings'] += 1 elif 'ERROR' in line: summary['errors'] += 1 # Analyze health logs health_log_file = self.log_directory / 'system_health.log' if health_log_file.exists(): with open(health_log_file, 'r') as f: for line in f: if 'Health check completed' in line: summary['health_checks'] += 1 return summary # Usage
log_manager = PSOLogManager() # Log optimization session
log_manager.log_optimization_start('classical_smc', {'n_particles': 50, 'n_iterations': 100})
# ... run optimization ...

log_manager.log_optimization_result('classical_smc', {'success': True, 'best_cost': 67.3}) # Daily maintenance
log_manager.cleanup_old_logs(days_to_keep=30)
summary = log_manager.get_log_summary(days=7)
print(f"Last 7 days: {summary['optimization_runs']} optimizations, {summary['successful_optimizations']} successful")
```

---

## 5. Emergency Recovery Procedures ### 5.1 Critical Failure Recovery **System Recovery Checklist:** ```bash
#!/bin/bash
# emergency_recovery.sh - Emergency PSO system recovery echo "🚨 PSO EMERGENCY RECOVERY PROCEDURE"
echo "==================================" # Step 1: Stop all running optimizations
echo "Step 1: Stopping all PSO processes..."
pkill -f "simulate.py.*pso"
pkill -f "pso_optimizer"
sleep 5 # Step 2: Check system resources
echo "Step 2: Checking system resources..."
echo "Memory usage:"
free -h
echo "Disk usage:"
df -h .
echo "CPU load:"
uptime # Step 3: Backup current state
echo "Step 3: Creating emergency backup..."
BACKUP_DIR="emergency_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR # Backup configuration
cp config.yaml $BACKUP_DIR/ 2>/dev/null
cp -r logs/ $BACKUP_DIR/ 2>/dev/null
cp -r results/ $BACKUP_DIR/ 2>/dev/null echo "Emergency backup created: $BACKUP_DIR" # Step 4: Reset to known good state
echo "Step 4: Resetting to known good configuration..." # Use last known good configuration
if [ -f "config.yaml.backup" ]; then cp config.yaml.backup config.yaml echo "✅ Restored from config.yaml.backup"
else echo "❌ No backup configuration found"
fi # Step 5: Run system health check
echo "Step 5: Running health check..."
python3 -c "
from docs.pso_troubleshooting_maintenance_manual import PSOHealthChecker
checker = PSOHealthChecker()
report = checker.run_comprehensive_check()
checker.print_summary()
exit(0 if report['overall_status'] in ['healthy', 'warnings'] else 1)
" HEALTH_STATUS=$? if [ $HEALTH_STATUS -eq 0 ]; then echo "✅ System health check passed - recovery successful"
else echo "❌ System health check failed - manual intervention required" echo "Please contact system administrator" exit 1
fi echo "🎉 Emergency recovery completed successfully"
``` **Recovery Validation Procedure:** ```python

def validate_emergency_recovery(): """Validate system after emergency recovery.""" print("🔍 VALIDATING EMERGENCY RECOVERY") print("=" * 40) validation_results = { 'configuration_valid': False, 'controllers_functional': False, 'pso_engine_operational': False, 'simulation_working': False, 'overall_success': False } # Test 1: Configuration validation try: from src.config import load_config config = load_config('config.yaml') validation_results['configuration_valid'] = True print("✅ Configuration loads successfully") except Exception as e: print(f"❌ Configuration error: {e}") # Test 2: Controller factory try: from src.controllers.factory import ControllerFactory import numpy as np test_gains = np.array([5.0, 3.0, 7.0, 2.0, 25.0, 1.0]) controller = ControllerFactory.create_controller('classical_smc', test_gains) test_state = np.zeros(6) control = controller.compute_control(test_state) if np.isfinite(control): validation_results['controllers_functional'] = True print("✅ Controller factory operational") else: print("❌ Controller produces invalid output") except Exception as e: print(f"❌ Controller factory error: {e}") # Test 3: PSO engine try: from src.optimization.algorithms.pso_optimizer import PSOTuner def test_factory(gains): return ControllerFactory.create_controller('classical_smc', gains) pso_tuner = PSOTuner(test_factory, config, seed=42) # Quick test optimization test_bounds = ( np.array([1.0, 1.0, 1.0, 1.0, 1.0, 0.1]), np.array([10.0, 10.0, 10.0, 10.0, 50.0, 5.0]) ) results = pso_tuner.optimize( bounds=test_bounds, n_particles=5, n_iterations=3 ) if results.get('success', False): validation_results['pso_engine_operational'] = True print("✅ PSO engine operational") else: print("❌ PSO engine test failed") except Exception as e: print(f"❌ PSO engine error: {e}") # Test 4: Simulation engine try: from src.simulation.engines.vector_sim import simulate_system_batch test_particles = np.array([[5.0, 3.0, 7.0, 2.0, 25.0, 1.0]]) result = simulate_system_batch( controller_factory=test_factory, particles=test_particles, sim_time=0.5, dt=0.01, u_max=150.0 ) if result is not None: validation_results['simulation_working'] = True print("✅ Simulation engine operational") else: print("❌ Simulation engine test failed") except Exception as e: print(f"❌ Simulation engine error: {e}") # Overall assessment success_count = sum(validation_results.values()) total_tests = len(validation_results) - 1 # Exclude overall_success if success_count == total_tests: validation_results['overall_success'] = True print("\n🎉 RECOVERY VALIDATION SUCCESSFUL") print("System is ready for normal operation") else: print(f"\n❌ RECOVERY VALIDATION FAILED") print(f"Only {success_count}/{total_tests} tests passed") print("Manual intervention required") return validation_results # Run validation
if __name__ == "__main__": results = validate_emergency_recovery() exit(0 if results['overall_success'] else 1)
``` ### 5.2 Data Recovery Procedures **Configuration Recovery:** ```python
import shutil
import json
from pathlib import Path
from datetime import datetime class ConfigurationRecovery: """Handle configuration file recovery and restoration.""" def __init__(self, config_dir='.', backup_dir='./config_backups'): self.config_dir = Path(config_dir) self.backup_dir = Path(backup_dir) self.backup_dir.mkdir(exist_ok=True) def create_emergency_backup(self, description="emergency"): """Create emergency backup of current configuration.""" timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') backup_name = f"config_emergency_{description}_{timestamp}.yaml" backup_path = self.backup_dir / backup_name try: shutil.copy2(self.config_dir / 'config.yaml', backup_path) print(f"✅ Emergency backup created: {backup_path}") return backup_path except Exception as e: print(f"❌ Failed to create emergency backup: {e}") return None def list_available_backups(self): """List all available configuration backups.""" backups = sorted(self.backup_dir.glob('config_*.yaml')) print("📋 Available Configuration Backups:") print("=" * 50) for i, backup in enumerate(backups, 1): # Extract timestamp from filename parts = backup.stem.split('_') if len(parts) >= 3: timestamp = f"{parts[-2]}_{parts[-1]}" try: dt = datetime.strptime(timestamp, '%Y%m%d_%H%M%S') formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S') except: formatted_date = timestamp print(f" {i:2d}. {backup.name}") print(f" Date: {formatted_date}") print(f" Size: {backup.stat().st_size} bytes") print() return backups def restore_from_backup(self, backup_index=None, backup_name=None): """Restore configuration from backup.""" backups = sorted(self.backup_dir.glob('config_*.yaml')) if backup_index is not None: if 1 <= backup_index <= len(backups): selected_backup = backups[backup_index - 1] else: print(f"❌ Invalid backup index: {backup_index}") return False elif backup_name is not None: selected_backup = self.backup_dir / backup_name if not selected_backup.exists(): print(f"❌ Backup not found: {backup_name}") return False else: print("❌ Must specify either backup_index or backup_name") return False try: # Create backup of current config before restoration self.create_emergency_backup("pre_restore") # Restore from backup shutil.copy2(selected_backup, self.config_dir / 'config.yaml') print(f"✅ Configuration restored from: {selected_backup.name}") # Validate restored configuration from src.config import load_config try: config = load_config('config.yaml') print("✅ Restored configuration is valid") return True except Exception as e: print(f"❌ Restored configuration is invalid: {e}") return False except Exception as e: print(f"❌ Failed to restore configuration: {e}") return False def restore_factory_defaults(self): """Restore factory default configuration.""" default_config = { 'global_seed': 42, 'pso': { 'n_particles': 50, 'n_iterations': 100, 'cognitive_weight': 1.49445, 'social_weight': 1.49445, 'inertia_weight': 0.729, 'bounds': { 'classical_smc': { 'lower': [0.1, 0.1, 0.1, 0.1, 0.1, 0.1], 'upper': [20.0, 20.0, 20.0, 20.0, 100.0, 10.0] } } }, 'cost_function': { 'weights': { 'state_error': 1.0, 'control_effort': 0.01, 'control_rate': 0.001, 'stability': 10.0 } }, 'simulation': { 'duration': 10.0, 'dt': 0.001 }, 'controllers': { 'classical_smc': { 'max_force': 150.0, 'boundary_layer': 0.02 } } } try: # Backup current config self.create_emergency_backup("pre_factory_reset") # Write factory defaults import yaml with open(self.config_dir / 'config.yaml', 'w') as f: yaml.dump(default_config, f, default_flow_style=False, indent=2) print("✅ Factory default configuration restored") return True except Exception as e: print(f"❌ Failed to restore factory defaults: {e}") return False # Usage example
recovery = ConfigurationRecovery() # List backups and restore
recovery.list_available_backups()
# recovery.restore_from_backup(backup_index=1)
# recovery.restore_factory_defaults()
```

**Results Data Recovery:**

```python
class OptimizationResultsRecovery:
    """Recover and validate optimization results."""

    def __init__(self, results_dir='./results'):
        self.results_dir = Path(results_dir)

    def scan_for_results(self):
        """Scan for all optimization result files."""
        result_files = list(self.results_dir.glob('*.json'))
        print(f"Found {len(result_files)} result files")

        valid_results = []
        corrupted_results = []

        for result_file in result_files:
            try:
                with open(result_file, 'r') as f:
                    data = json.load(f)

                # Validate result structure
                required_fields = ['controller_type', 'best_gains', 'best_cost']
                if all(field in data for field in required_fields):
                    valid_results.append(result_file)
                    print(f"[OK] {result_file.name} - Valid")
                else:
                    corrupted_results.append(result_file)
                    print(f"[WARNING] {result_file.name} - Missing required fields")
            except json.JSONDecodeError:
                corrupted_results.append(result_file)
                print(f"[ERROR] {result_file.name} - JSON corruption")
            except Exception as e:
                corrupted_results.append(result_file)
                print(f"[ERROR] {result_file.name} - Error: {e}")

        return valid_results, corrupted_results

# Usage
recovery = OptimizationResultsRecovery()
valid, corrupted = recovery.scan_for_results()
```

---

## 6. Conclusion This troubleshooting and maintenance manual provides complete procedures for maintaining PSO system health and resolving issues. Key manual sections include: **Diagnostic Framework:**
- Automated health checking with component validation
- Quick diagnostic commands for rapid issue identification
- Performance benchmarking and monitoring features **Issue Resolution:**
- Systematic troubleshooting for common optimization failures
- Performance optimization techniques for slow or resource-intensive operations
- Controller-specific debugging procedures with stability analysis **Preventive Maintenance:**
- Regular health monitoring with automated alerting
- Configuration management and version control
- Log rotation and cleanup procedures **Emergency Procedures:**
- Critical failure recovery with system restoration
- Data recovery for corrupted configurations and results
- Factory reset procedures with validation **Best Practices:**
- Proactive monitoring prevents most critical issues
- Regular backups ensure quick recovery from failures
- Systematic validation catches issues before production deployment
- Performance optimization maintains system efficiency This manual successfully addresses the maintenance requirements for GitHub Issue #4 resolution, ensuring long-term PSO system reliability and optimal performance through troubleshooting procedures and preventive maintenance protocols.
