#==========================================================================================\\\
#================== docs/pso_optimization_workflow_user_guide.md ====================\\\
#==========================================================================================\\\

# PSO Optimization Workflow User Guide
**Double-Inverted Pendulum Sliding Mode Control System** ## Executive Summary This user guide provides step-by-step instructions for using Particle Swarm Optimization (PSO) to optimize controller gains in the Double-Inverted Pendulum Sliding Mode Control system. The guide covers everything from basic optimization workflows to advanced uncertainty-aware tuning, ensuring users can effectively use the PSO integration system regardless of their expertise level. **Guide Scope:**
- **Beginner**: Basic PSO optimization workflows with default settings
- **Intermediate**: Custom parameter tuning and configuration optimization
- **Advanced**: Multi-objective optimization and uncertainty-aware tuning
- **Expert**: Custom fitness functions and algorithm modifications **System Requirements:**
- Python 3.9+ with NumPy, SciPy, PySwarms
- Double-Inverted Pendulum simulation environment
- Configured controller factory system

---

## 1. Quick Start Guide ### 1.1 Basic PSO Optimization (5 Minutes) **Objective**: Optimize Classical SMC gains using default PSO settings. **Step 1: Navigate to Project Directory**

```bash
cd /path/to/dip-smc-pso
``` **Step 2: Run Basic PSO Optimization**

```bash
python simulate.py --ctrl classical_smc --run-pso --save gains_optimized.json
``` **Expected Output:**

```
Starting PSO optimization for classical_smc...
Iteration 1/100: Best fitness = 1245.67
Iteration 10/100: Best fitness = 234.56
Iteration 50/100: Best fitness = 89.12
Iteration 100/100: Best fitness = 67.34
Optimization completed successfully!
Best gains: [5.23, 3.45, 7.89, 2.11, 45.67, 1.23]
Results saved to: gains_optimized.json
``` **Step 3: Test Optimized Controller**

```bash
python simulate.py --ctrl classical_smc --load gains_optimized.json --plot
``` ### 1.2 Understanding the Output **Optimization Results File (`gains_optimized.json`):**

```json
{ "controller_type": "classical_smc", "best_gains": [5.23, 3.45, 7.89, 2.11, 45.67, 1.23], "best_cost": 67.34, "optimization_info": { "n_particles": 50, "n_iterations": 100, "convergence_iteration": 78, "final_diversity": 0.012, "success": true }, "performance_metrics": { "ise": 12.34, "control_effort": 45.67, "control_rate": 8.90, "sliding_energy": 0.43 }, "timestamp": "2024-01-15T10:30:45Z"
}
``` **Gain Vector Interpretation (Classical SMC):**

- `gains[0]` (c1): Sliding surface gain for pendulum 1 position error
- `gains[1]` (λ1): Sliding surface coefficient for pendulum 1
- `gains[2]` (c2): Sliding surface gain for pendulum 2 position error
- `gains[3]` (λ2): Sliding surface coefficient for pendulum 2
- `gains[4]` (K): Control gain (determines control authority)
- `gains[5]` (kd): Derivative gain (damping effect)

---

## 2. Controller-Specific Optimization Workflows ### 2.1 Classical SMC Optimization **Mathematical Background:**

Classical SMC uses the sliding surface:
```
s = λ₁e₁ + λ₂e₂ + ė₁ + ė₂
```

where e₁, e₂ are position errors and ė₁, ė₂ are velocity errors. **Optimization Command:**
```bash
python simulate.py --ctrl classical_smc --run-pso --save classical_gains.json
``` **Parameter Bounds (Default):**

```python
# Lower bounds: [c1, λ1, c2, λ2, K, kd]
lower_bounds = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1] # Upper bounds
upper_bounds = [20.0, 20.0, 20.0, 20.0, 100.0, 10.0]
``` **Typical Optimization Results:**

- **Convergence Time**: 50-150 iterations
- **Expected ISE**: 10-50 (depending on initial conditions)
- **Control Effort**: Typically 20-80% of available force
- **Settling Time**: 2-5 seconds for ±0.1 rad stabilization ### 2.2 Super-Twisting SMC Optimization **Mathematical Background:**
STA-SMC uses second-order sliding mode:
```
u = -K₁|s|^(1/2)sign(s) + u₂
u̇₂ = -K₂sign(s)
``` **Optimization Command:**

```bash
python simulate.py --ctrl sta_smc --run-pso --save sta_gains.json
``` **Parameter Interpretation:**

```python
# STA-SMC gains: [K1, K2, k1, k2, λ1, λ2]
gains_meaning = { 'K1': 'First-order sliding gain (0.5-power term)', 'K2': 'Second-order sliding gain (integral term)', 'k1': 'Surface gain for pendulum 1', 'k2': 'Surface gain for pendulum 2', 'lambda1': 'Surface coefficient for pendulum 1', 'lambda2': 'Surface coefficient for pendulum 2'
}
``` **STA-SMC Optimization Tips:**

- K₁ and K₂ should satisfy: K₂ > K₁ × 0.5 for stability
- Higher λ values provide faster convergence but may cause overshoot
- Start with K₁ ∈ [5, 15] and K₂ ∈ [2, 10] for initial exploration ### 2.3 Adaptive SMC Optimization **Mathematical Background:**
Adaptive SMC adjusts control gains online:
```
u = -K̂(t)·sign(s)
K̇ = γ·|s| (outside dead zone)
``` **Optimization Command:**

```bash
python simulate.py --ctrl adaptive_smc --run-pso --save adaptive_gains.json
``` **Parameter Guidelines:**

```python
# Adaptive SMC gains: [c1, λ1, c2, λ2, γ]
optimization_tips = { 'c1, c2': 'Surface gains (1.0-10.0 typical range)', 'lambda1, lambda2': 'Surface coefficients (0.5-5.0 typical)', 'gamma': 'Adaptation rate (0.1-2.0, higher = faster adaptation)'
}
``` **Adaptive SMC Characteristics:**

- **Adaptation Speed**: Controlled by γ parameter
- **Robustness**: Higher than classical SMC for uncertain systems
- **Computational Cost**: Slightly higher due to online adaptation ### 2.4 Hybrid Adaptive STA-SMC Optimization **Mathematical Background:**
Combines adaptive estimation with super-twisting algorithm. **Optimization Command:**
```bash
python simulate.py --ctrl hybrid_adaptive_sta_smc --run-pso --save hybrid_gains.json
``` **Parameter Interpretation:**

```python
# Hybrid gains: [c1, λ1, c2, λ2]
# Note: K1, K2 are adapted online automatically
hybrid_features = { 'c1, c2': 'Proportional-like surface gains', 'lambda1, lambda2': 'Integral-like surface coefficients', 'adaptation': 'K1, K2 adapt based on sliding surface magnitude'
}
```

---

## 3. Advanced Configuration and Customization ### 3.1 Custom PSO Parameters **Configuration File Modification (`config.yaml`):**

```yaml
pso: # Basic PSO parameters n_particles: 50 # Swarm size (20-100 typical) n_iterations: 100 # Maximum iterations (50-200 typical) cognitive_weight: 1.49445 # c1: Personal best attraction social_weight: 1.49445 # c2: Global best attraction inertia_weight: 0.729 # w: Velocity persistence # Advanced features velocity_clamp: [0.1, 0.5] # Velocity limits as fraction of search space w_schedule: [0.9, 0.4] # Inertia weight schedule [start, end] # Convergence criteria tolerance: 1e-6 stagnation_iterations: 20
``` **Custom Optimization with Parameters:**

```bash
python simulate.py --ctrl classical_smc --run-pso \ --pso-particles 100 \ --pso-iterations 200 \ --save classical_high_res.json
``` ### 3.2 Custom Parameter Bounds **Method 1: Configuration File**

```yaml
pso: bounds: classical_smc: lower: [0.5, 0.5, 0.5, 0.5, 1.0, 0.1] upper: [15.0, 15.0, 15.0, 15.0, 80.0, 8.0] sta_smc: lower: [2.0, 1.0, 2.0, 1.0, 1.0, 1.0] upper: [25.0, 15.0, 25.0, 15.0, 8.0, 8.0]
``` **Method 2: Programmatic Bounds**

```python
import numpy as np
from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.controllers.factory import ControllerFactory # Custom bounds for aggressive tuning
custom_bounds = { 'lower': np.array([1.0, 1.0, 1.0, 1.0, 5.0, 0.5]), 'upper': np.array([25.0, 25.0, 25.0, 25.0, 150.0, 15.0])
} # Create factory and run optimization
def create_controller(gains): return ControllerFactory.create_controller('classical_smc', gains) pso_tuner = PSOTuner(create_controller, config, seed=42)
results = pso_tuner.optimize( bounds=(custom_bounds['lower'], custom_bounds['upper']), n_particles=75, n_iterations=150
)
``` ### 3.3 Custom Cost Function Weights **Multi-Objective Optimization Configuration:**

```yaml
cost_function: weights: state_error: 1.0 # ISE penalty (primary objective) control_effort: 0.01 # Energy efficiency control_rate: 0.001 # Actuator wear reduction stability: 10.0 # Sliding mode performance # Performance vs. efficiency trade-off combine_weights: mean: 0.7 # Average performance weight max: 0.3 # Worst-case performance weight
``` **Application-Specific Weight Tuning:** 1. **High Performance (Racing/Aggressive):** ```yaml weights: {state_error: 10.0, control_effort: 0.001, control_rate: 0.0001, stability: 5.0} ``` 2. **Energy Efficient (Long Operation):** ```yaml weights: {state_error: 1.0, control_effort: 0.1, control_rate: 0.01, stability: 2.0} ``` 3. **Actuator Friendly (Reduced Wear):** ```yaml weights: {state_error: 1.0, control_effort: 0.05, control_rate: 0.1, stability: 3.0} ```

---

## 4. Uncertainty-Aware Optimization ### 4.1 Parameter Uncertainty Configuration **System Parameter Uncertainty:**

```yaml
physics_uncertainty: n_evals: 5 # Number of uncertainty samples cart_mass: 0.05 # ±5% uncertainty in cart mass pendulum1_mass: 0.1 # ±10% uncertainty in pendulum 1 mass pendulum2_mass: 0.1 # ±10% uncertainty in pendulum 2 mass pendulum1_length: 0.02 # ±2% uncertainty in length pendulum2_length: 0.02 # ±2% uncertainty in length friction_cart: 0.2 # ±20% uncertainty in friction
``` **Robust Optimization Command:**

```bash
python simulate.py --ctrl classical_smc --run-pso \ --enable-uncertainty \ --uncertainty-samples 10 \ --save robust_gains.json
``` ### 4.2 Understanding Robust Optimization Results **Robust Cost Function:**

The optimizer evaluates performance across uncertainty samples:
```
J_robust = w_mean × E[J(θ)] + w_max × max[J(θ)]
``` **Interpretation of Results:**

```json
{ "best_gains": [4.12, 2.89, 6.45, 1.98, 38.5, 0.95], "robust_cost": 89.34, "uncertainty_analysis": { "mean_cost": 76.21, "max_cost": 127.89, "std_cost": 18.45, "worst_case_scenario": { "parameter_combination": {...}, "cost": 127.89 } }
}
``` **Robust vs. Nominal Comparison:**

- **Robust gains**: Often more conservative, better worst-case performance
- **Nominal gains**: May be more aggressive, better average performance
- **Trade-off**: Robust optimization sacrifices some nominal performance for reliability

---

## 5. Multi-Controller Optimization Workflows ### 5.1 Batch Optimization for All Controllers **Sequential Optimization Script:**

```bash
#!/bin/bash
# optimize_all_controllers.sh echo "Starting multi-controller PSO optimization..." controllers=("classical_smc" "sta_smc" "adaptive_smc" "hybrid_adaptive_sta_smc") for ctrl in "${controllers[@]}"; do echo "Optimizing ${ctrl}..." python simulate.py --ctrl ${ctrl} --run-pso --save ${ctrl}_optimized.json if [ $? -eq 0 ]; then echo "✓ ${ctrl} optimization completed" else echo "✗ ${ctrl} optimization failed" fi
done echo "All optimizations completed!"
``` **Parallel Optimization (Advanced):**

```python
import concurrent.futures
import subprocess
from pathlib import Path def optimize_controller(controller_type): """Optimize single controller type.""" cmd = [ 'python', 'simulate.py', '--ctrl', controller_type, '--run-pso', '--save', f'{controller_type}_parallel.json' ] result = subprocess.run(cmd, capture_output=True, text=True) return controller_type, result.returncode == 0, result.stdout def parallel_optimization(): """Run parallel PSO optimization for multiple controllers.""" controllers = ['classical_smc', 'sta_smc', 'adaptive_smc'] with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor: futures = {executor.submit(optimize_controller, ctrl): ctrl for ctrl in controllers} for future in concurrent.futures.as_completed(futures): controller = futures[future] ctrl_name, success, output = future.result() if success: print(f"✓ {ctrl_name} optimization completed") else: print(f"✗ {ctrl_name} optimization failed") print(f"Error output: {output}") if __name__ == "__main__": parallel_optimization()
``` ### 5.2 Performance Comparison Analysis **Comparison Script:**

```python
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path def compare_optimization_results(result_files): """Compare PSO optimization results across controllers.""" results = {} for file in result_files: with open(file, 'r') as f: data = json.load(f) controller_type = data['controller_type'] results[controller_type] = data # Create comparison plot fig, axes = plt.subplots(2, 2, figsize=(12, 8)) # Plot 1: Best cost comparison controllers = list(results.keys()) costs = [results[ctrl]['best_cost'] for ctrl in controllers] axes[0, 0].bar(controllers, costs) axes[0, 0].set_title('Best Cost Comparison') axes[0, 0].set_ylabel('Cost') axes[0, 0].tick_params(axis='x', rotation=45) # Plot 2: Convergence comparison for ctrl in controllers: if 'cost_history' in results[ctrl]: axes[0, 1].plot(results[ctrl]['cost_history'], label=ctrl) axes[0, 1].set_title('Convergence History') axes[0, 1].set_xlabel('Iteration') axes[0, 1].set_ylabel('Cost') axes[0, 1].legend() # Plot 3: Performance metrics metrics = ['ise', 'control_effort', 'control_rate', 'sliding_energy'] x = np.arange(len(metrics)) width = 0.2 for i, ctrl in enumerate(controllers): if 'performance_metrics' in results[ctrl]: values = [results[ctrl]['performance_metrics'].get(m, 0) for m in metrics] axes[1, 0].bar(x + i*width, values, width, label=ctrl) axes[1, 0].set_title('Performance Metrics') axes[1, 0].set_xlabel('Metrics') axes[1, 0].set_xticks(x + width) axes[1, 0].set_xticklabels(metrics, rotation=45) axes[1, 0].legend() # Plot 4: Optimization info info_data = [] for ctrl in controllers: info = results[ctrl]['optimization_info'] info_data.append([ info['n_iterations'], info.get('convergence_iteration', info['n_iterations']), info.get('final_diversity', 0) ]) info_array = np.array(info_data) x = np.arange(len(controllers)) axes[1, 1].bar(x - 0.2, info_array[:, 0], 0.4, label='Total Iterations') axes[1, 1].bar(x + 0.2, info_array[:, 1], 0.4, label='Convergence Iteration') axes[1, 1].set_title('Optimization Statistics') axes[1, 1].set_xlabel('Controller') axes[1, 1].set_xticks(x) axes[1, 1].set_xticklabels(controllers, rotation=45) axes[1, 1].legend() plt.tight_layout() plt.savefig('optimization_comparison.png', dpi=300, bbox_inches='tight') plt.show() return results # Usage example
result_files = [ 'classical_smc_optimized.json', 'sta_smc_optimized.json', 'adaptive_smc_optimized.json'
] comparison = compare_optimization_results(result_files)
```

---

## 6. Troubleshooting and Optimization Tips ### 6.1 Common Optimization Issues **Issue 1: Poor Convergence (High Final Cost)** *Symptoms:*

- Best cost > 200 after 100 iterations
- Cost history shows no improvement after iteration 20
- Final diversity < 0.001 (premature convergence) *Solutions:*
```bash
# Increase population diversity
python simulate.py --ctrl classical_smc --run-pso \ --pso-particles 100 \ --pso-iterations 200 \ --cognitive-weight 2.0 \ --social-weight 1.0 # Or restart with different random seed
python simulate.py --ctrl classical_smc --run-pso --seed 123
``` **Issue 2: Unstable Optimized Controllers** *Symptoms:*

- Simulation fails with optimized gains
- Control outputs exceed actuator limits frequently
- System becomes unstable during simulation *Solutions:*
```python
# example-metadata:
# runnable: false # Tighten parameter bounds
custom_bounds = { 'lower': [1.0, 1.0, 1.0, 1.0, 5.0, 0.5], # More conservative 'upper': [10.0, 10.0, 10.0, 10.0, 50.0, 5.0] # Reduced ranges
} # Increase stability weight in cost function
stability_focused_weights = { 'state_error': 1.0, 'control_effort': 0.01, 'control_rate': 0.001, 'stability': 50.0 # Heavily penalize instability
}
``` **Issue 3: Slow Optimization (>5 minutes per iteration)** *Symptoms:*

- Each PSO iteration takes >5 seconds
- Memory usage continuously increases
- CPU usage consistently at 100% *Solutions:*
```bash
# Reduce simulation time or increase time step
python simulate.py --ctrl classical_smc --run-pso \ --sim-time 5.0 \ --dt 0.002 # Use fewer particles for faster iterations
python simulate.py --ctrl classical_smc --run-pso \ --pso-particles 25 \ --pso-iterations 200
``` ### 6.2 Parameter Tuning Guidelines **PSO Hyperparameter Selection:** 1. **Population Size (`n_particles`):** - Small problems (4-6 parameters): 20-40 particles - Medium problems (6-10 parameters): 40-80 particles - Large problems (>10 parameters): 80-150 particles 2. **Iteration Count (`n_iterations`):** - Quick exploration: 50-100 iterations - Standard optimization: 100-200 iterations - High-precision tuning: 200-500 iterations 3. **Cognitive vs. Social Balance:** - Exploration phase: c₁ > c₂ (e.g., c₁=2.0, c₂=1.0) - Exploitation phase: c₁ < c₂ (e.g., c₁=1.0, c₂=2.0) - Balanced search: c₁ ≈ c₂ ≈ 1.5 **Controller-Specific Tuning Tips:** **Classical SMC:**

- Start with λ₁, λ₂ ∈ [1, 5] for moderate damping
- K should be 2-5× larger than surface gains
- kd provides damping; start with 10-20% of K **STA-SMC:**
- K₁ determines convergence speed; K₂ provides robustness
- Relationship: K₂ > 0.5×K₁ for stability
- Surface gains k₁, k₂ similar to classical SMC c₁, c₂ **Adaptive SMC:**
- γ (adaptation rate): Start with 0.5-2.0
- Too high γ causes oscillations; too low γ gives poor adaptation
- Monitor K_adaptive evolution during simulation

---

## 7. Integration with Control Workflows ### 7.1 Design → Optimize → Validate Workflow **Step 1: Initial Controller Design**

```bash
# Test default controller performance
python simulate.py --ctrl classical_smc --plot --save baseline_results.json
``` **Step 2: PSO Optimization**

```bash
# Optimize with standard settings
python simulate.py --ctrl classical_smc --run-pso --save optimized_gains.json
``` **Step 3: Performance Validation**

```bash
# Validate optimized controller
python simulate.py --ctrl classical_smc --load optimized_gains.json --plot # Compare with baseline
python compare_controllers.py baseline_results.json optimized_results.json
``` **Step 4: Robustness Testing**

```bash
# Test with parameter uncertainty
python simulate.py --ctrl classical_smc --load optimized_gains.json \ --enable-uncertainty --uncertainty-samples 20 --plot
``` ### 7.2 Hardware-in-the-Loop (HIL) Integration **PSO for HIL Systems:**

```bash
# Optimize for HIL deployment
python simulate.py --ctrl classical_smc --run-pso \ --hil-mode \ --real-time-constraints \ --save hil_optimized.json
``` **HIL-Specific Considerations:**

- **Real-time constraints**: Limit control computation time
- **Actuator models**: Include actual actuator dynamics
- **Sensor noise**: Add realistic measurement noise
- **Communication delays**: Account for control loop delays **HIL Validation Workflow:**
```python
# example-metadata:
# runnable: false # HIL optimization with realistic constraints
hil_config = { 'max_control_time': 0.001, # 1ms control computation limit 'actuator_bandwidth': 100, # 100 Hz actuator bandwidth 'sensor_noise_std': 0.01, # 1% measurement noise 'communication_delay': 0.0005 # 0.5ms delay
} # Run optimization with HIL constraints
results = pso_tuner.optimize( bounds=bounds, hil_constraints=hil_config, real_time_validation=True
)
``` ### 7.3 Production Deployment Workflow **Pre-Deployment Checklist:**

```python
# example-metadata:
# runnable: false def validate_optimized_controller(gains_file): """validation before deployment.""" checks = { 'stability_margins': False, 'actuator_limits': False, 'robustness': False, 'performance': False } # Load optimized gains with open(gains_file, 'r') as f: data = json.load(f) gains = data['best_gains'] controller_type = data['controller_type'] # Stability margin check # ... implementation details # Actuator saturation check # ... implementation details # Robustness analysis # ... implementation details # Performance verification # ... implementation details return all(checks.values()), checks # Usage
is_ready, check_results = validate_optimized_controller('optimized_gains.json')
if is_ready: print("✓ Controller ready for production deployment")
else: print("✗ Validation failed:", check_results)
```

---

## 8. Advanced Optimization Techniques ### 8.1 Multi-Objective Optimization **Pareto Front Exploration:**

```python
from src.optimization.multi_objective import ParetoFrontPSO # Define multiple objectives
objectives = { 'performance': {'weight': 1.0, 'minimize': True}, 'energy': {'weight': 0.01, 'minimize': True}, 'robustness': {'weight': 10.0, 'minimize': True}
} # Multi-objective PSO
mo_pso = ParetoFrontPSO( controller_factory=create_controller, objectives=objectives, config=config
) # Get Pareto front
pareto_solutions = mo_pso.optimize( bounds=bounds, n_particles=100, n_iterations=200
) # Select solution based on preferences
selected_solution = mo_pso.select_solution( pareto_solutions, preferences={'performance': 0.6, 'energy': 0.2, 'robustness': 0.2}
)
``` ### 8.2 Adaptive PSO Parameters **Dynamic Parameter Adaptation:**

```python
# example-metadata:
# runnable: false class AdaptivePSO(PSOTuner): """PSO with adaptive parameters based on convergence.""" def adapt_parameters(self, iteration, diversity, improvement): """Adapt PSO parameters during optimization.""" if diversity < 0.01: # Low diversity self.cognitive_weight *= 1.1 # Increase exploration self.social_weight *= 0.9 if improvement < 0.001: # Slow improvement self.inertia_weight *= 0.95 # Decrease inertia # Restart mechanism for stagnation if iteration > 50 and improvement < 1e-6: self.restart_particles(fraction=0.3)
``` ### 8.3 Hybrid Optimization Approaches **PSO + Local Search:**

```python
def hybrid_pso_local_search(controller_factory, config): """Combine PSO global search with local refinement.""" # Phase 1: Global PSO search pso_tuner = PSOTuner(controller_factory, config) pso_results = pso_tuner.optimize( bounds=bounds, n_particles=50, n_iterations=100 ) # Phase 2: Local refinement around best solution from scipy.optimize import minimize def local_objective(gains): controller = controller_factory(gains) # Simulate and return cost cost = simulate_and_evaluate(controller) return cost # Local optimization starting from PSO result local_result = minimize( local_objective, x0=pso_results['best_gains'], bounds=[(bounds[0][i], bounds[1][i]) for i in range(len(bounds[0]))], method='L-BFGS-B' ) return { 'pso_result': pso_results, 'local_result': local_result, 'final_gains': local_result.x, 'final_cost': local_result.fun }
```

---

## 9. Performance Monitoring and Analysis ### 9.1 Real-Time Optimization Monitoring **Progress Tracking:**

```python
# example-metadata:
# runnable: false def optimization_callback(iteration, best_cost, best_position, **kwargs): """Real-time optimization monitoring callback.""" # Log progress print(f"Iteration {iteration:3d}: Cost = {best_cost:.6f}") # Update visualization plt.scatter(iteration, best_cost, c='blue', alpha=0.7) plt.xlabel('Iteration') plt.ylabel('Best Cost') plt.pause(0.01) # Save intermediate results if iteration % 20 == 0: save_checkpoint(iteration, best_position, best_cost) # Early stopping condition if best_cost < 10.0: # Target achieved return True # Stop optimization return False # Continue optimization # Use callback in optimization
results = pso_tuner.optimize( bounds=bounds, callback=optimization_callback, n_particles=50, n_iterations=200
)
``` ### 9.2 Convergence Analysis **Statistical Convergence Assessment:**

```python
# example-metadata:
# runnable: false def analyze_convergence(cost_history, window_size=10): """Analyze PSO convergence characteristics.""" analysis = {} # Convergence rate if len(cost_history) > window_size: recent_improvement = cost_history[-window_size] - cost_history[-1] analysis['improvement_rate'] = recent_improvement / window_size # Stagnation detection if len(cost_history) > 20: recent_costs = cost_history[-20:] stagnation = np.std(recent_costs) < 0.001 analysis['is_stagnant'] = stagnation # Convergence quality final_cost = cost_history[-1] if final_cost < 50: analysis['convergence_quality'] = 'excellent' elif final_cost < 100: analysis['convergence_quality'] = 'good' elif final_cost < 200: analysis['convergence_quality'] = 'acceptable' else: analysis['convergence_quality'] = 'poor' return analysis # Analyze optimization results
convergence_analysis = analyze_convergence(results['cost_history'])
print(f"Convergence Quality: {convergence_analysis['convergence_quality']}")
``` ### 9.3 Performance Benchmarking **Optimization Performance Metrics:**

```python
import time
import psutil
import os class OptimizationProfiler: """Profile PSO optimization performance.""" def __init__(self): self.start_time = None self.memory_samples = [] self.cpu_samples = [] def start_profiling(self): """Start performance profiling.""" self.start_time = time.time() self.process = psutil.Process(os.getpid()) def sample_performance(self): """Sample current performance metrics.""" if self.start_time: self.memory_samples.append(self.process.memory_info().rss / 1024 / 1024) # MB self.cpu_samples.append(self.process.cpu_percent()) def get_summary(self): """Get performance summary.""" total_time = time.time() - self.start_time return { 'total_time': total_time, 'peak_memory_mb': max(self.memory_samples) if self.memory_samples else 0, 'avg_cpu_percent': np.mean(self.cpu_samples) if self.cpu_samples else 0, 'memory_trend': np.polyfit(range(len(self.memory_samples)), self.memory_samples, 1)[0] if len(self.memory_samples) > 1 else 0 } # Usage in optimization
profiler = OptimizationProfiler()
profiler.start_profiling() # Optimization with profiling callback
def profiling_callback(iteration, **kwargs): profiler.sample_performance() return False results = pso_tuner.optimize( bounds=bounds, callback=profiling_callback, n_particles=50, n_iterations=100
) performance_summary = profiler.get_summary()
print(f"Optimization completed in {performance_summary['total_time']:.1f} seconds")
print(f"Peak memory usage: {performance_summary['peak_memory_mb']:.1f} MB")
```

---

## 10. Best Practices and Recommendations ### 10.1 Optimization Strategy Guidelines **1. Start Simple, Then Refine:**

```bash
# Phase 1: Quick exploration with default settings
python simulate.py --ctrl classical_smc --run-pso --save quick_result.json # Phase 2: Refined optimization with more particles
python simulate.py --ctrl classical_smc --run-pso \ --pso-particles 100 --pso-iterations 200 \ --save refined_result.json # Phase 3: Fine-tuning with uncertainty
python simulate.py --ctrl classical_smc --run-pso \ --load refined_result.json \ --enable-uncertainty \ --save final_result.json
``` **2. Systematic Parameter Exploration:**

```python
# example-metadata:
# runnable: false # Systematic bounds exploration
bounds_sets = [ ([0.1, 0.1, 0.1, 0.1, 0.1, 0.1], [10, 10, 10, 10, 50, 5]), # Conservative ([0.5, 0.5, 0.5, 0.5, 1.0, 0.5], [20, 20, 20, 20, 100, 10]), # Standard ([1.0, 1.0, 1.0, 1.0, 5.0, 1.0], [30, 30, 30, 30, 150, 15]) # Aggressive
] best_overall = None
best_cost = float('inf') for i, (lower, upper) in enumerate(bounds_sets): print(f"Testing bounds set {i+1}/3...") results = pso_tuner.optimize( bounds=(np.array(lower), np.array(upper)), n_particles=50, n_iterations=100 ) if results['best_cost'] < best_cost: best_cost = results['best_cost'] best_overall = results print(f"Bounds set {i+1}: Best cost = {results['best_cost']:.3f}") print(f"Overall best cost: {best_cost:.3f}")
``` ### 10.2 Quality Assurance Checklist **Pre-Optimization Checklist:**

- [ ] Configuration file validated
- [ ] Parameter bounds are reasonable for controller type
- [ ] Simulation settings appropriate for system dynamics
- [ ] Cost function weights reflect optimization objectives
- [ ] Random seed set for reproducible results **Post-Optimization Checklist:**
- [ ] Convergence achieved (cost improvement < tolerance)
- [ ] Optimized gains within expected ranges
- [ ] Controller stability verified through simulation
- [ ] Performance meets requirements across operating conditions
- [ ] Robustness validated with parameter uncertainty **Production Deployment Checklist:**
- [ ] Extensive validation with realistic disturbances
- [ ] Hardware-in-the-loop testing completed
- [ ] Safety margins verified
- [ ] Performance benchmarks documented
- [ ] Rollback plan prepared ### 10.3 Documentation and Reproducibility **Optimization Documentation Template:**
```python
# example-metadata:
# runnable: false optimization_report = { 'metadata': { 'date': '2024-01-15', 'operator': 'user_name', 'objective': 'Optimize Classical SMC for improved settling time', 'system_version': 'v2.1.0' }, 'configuration': { 'controller_type': 'classical_smc', 'pso_parameters': {...}, 'bounds': {...}, 'cost_weights': {...} }, 'results': { 'best_gains': [...], 'best_cost': 67.34, 'convergence_iteration': 78, 'total_iterations': 100 }, 'validation': { 'stability_margin': 0.65, 'settling_time': 2.3, 'overshoot': 0.05, 'robustness_score': 0.82 }, 'recommendations': [ 'Deploy gains for production use', 'Monitor performance during initial operation', 'Schedule re-optimization in 6 months' ]
} # Save report
with open('optimization_report.json', 'w') as f: json.dump(optimization_report, f, indent=2)
``` **Version Control Integration:**

```bash
# Create optimization branch
git checkout -b optimization/classical_smc_v2 # Run optimization
python simulate.py --ctrl classical_smc --run-pso --save optimized_gains.json # Commit results
git add optimized_gains.json optimization_report.json
git commit -m "PSO optimization: Classical SMC gains v2.0 - Improved settling time from 3.2s to 2.3s
- Reduced overshoot from 8% to 5%
- Maintained stability margins > 0.6
- Validated with ±10% parameter uncertainty" # Merge to main after validation
git checkout main
git merge optimization/classical_smc_v2
```

---

## 11. Frequently Asked Questions (FAQ) ### 11.1 General Questions **Q: How long should PSO optimization take?**

A: Typical optimization times:
- Quick exploration (25 particles, 50 iterations): 2-5 minutes
- Standard optimization (50 particles, 100 iterations): 5-15 minutes
- High-resolution optimization (100 particles, 200 iterations): 15-45 minutes
- Uncertainty-aware optimization: 2-5× longer than nominal **Q: How do I know if optimization converged successfully?**
A: Check these indicators:
- Final cost < 100 (controller-dependent)
- Cost improvement < 0.001 for last 20 iterations
- Final diversity > 0.001 (not premature convergence)
- Optimized controller passes stability tests **Q: Can I stop and resume optimization?**
A: Currently, optimization cannot be resumed. Use checkpointing:
```python
# Save intermediate results every 20 iterations
def checkpoint_callback(iteration, best_position, best_cost, **kwargs): if iteration % 20 == 0: np.save(f'checkpoint_{iteration}.npy', { 'iteration': iteration, 'best_position': best_position, 'best_cost': best_cost })
``` ### 11.2 Technical Questions **Q: What if PSO finds unstable gains?**

A: Several solutions:
1. Tighten parameter bounds
2. Increase stability weight in cost function
3. Add controller-specific constraints via `validate_gains()`
4. Use robust optimization with uncertainty **Q: How to handle different controller types in batch optimization?**
A: Use controller-specific configurations:
```python
# example-metadata:
# runnable: false controller_configs = { 'classical_smc': {'bounds': [...], 'weights': {...}}, 'sta_smc': {'bounds': [...], 'weights': {...}}, # ... etc
} for ctrl_type, config in controller_configs.items(): optimize_with_config(ctrl_type, config)
``` **Q: Can I use custom cost functions?**

A: Yes, modify the cost function in `PSOTuner`:
```python
def custom_cost_function(self, trajectory_data): """Custom cost function implementation.""" t, x, u, sigma = trajectory_data # Custom performance metrics custom_metric = compute_custom_performance(x, u) # Combine with standard metrics standard_cost = self._compute_cost_from_traj(t, x, u, sigma) return standard_cost + 0.1 * custom_metric
``` ### 11.3 Troubleshooting **Q: Optimization takes too long per iteration**

A: Optimization strategies:
1. Reduce simulation time: `--sim-time 5.0`
2. Increase time step: `--dt 0.002`
3. Use fewer particles: `--pso-particles 25`
4. Disable uncertainty: Remove `--enable-uncertainty` **Q: Results are not reproducible**
A: Ensure reproducibility:
1. Set random seed: `--seed 42`
2. Use same configuration file
3. Use same software versions
4. Document system parameters **Q: Memory usage keeps increasing**
A: Memory management:
1. Monitor with `htop` or Task Manager
2. Use smaller particle count
3. Reduce simulation duration
4. Restart Python session between optimizations

---

## 12. Conclusion This user guide provides complete workflows for PSO optimization within the Double-Inverted Pendulum Sliding Mode Control system. Key takeaways: **For Beginners:**

- Start with default settings and basic optimization commands
- Use the quick start guide for immediate results
- Focus on understanding gain vector meanings for your controller type **For Intermediate Users:**
- Explore custom parameter bounds and cost function weights
- Implement uncertainty-aware optimization for robustness
- Use multi-controller comparison workflows **For Advanced Users:**
- Develop custom optimization strategies and hybrid approaches
- Implement real-time monitoring and performance profiling
- Create production deployment workflows with validation **Best Practices:**
- Always validate optimized controllers before deployment
- Document optimization settings and results for reproducibility
- Use systematic approaches for parameter exploration
- Monitor convergence characteristics and optimization performance The PSO integration system successfully resolves GitHub Issue #4 and provides a robust, user-friendly framework for controller optimization across all SMC variants. Regular use of these workflows will ensure optimal controller performance while maintaining system stability and robustness.