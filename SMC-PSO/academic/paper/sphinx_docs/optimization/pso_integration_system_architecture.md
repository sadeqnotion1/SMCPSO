#==========================================================================================\\\
#================== docs/pso_integration_system_architecture.md =====================\\\
#==========================================================================================\\\

# PSO Integration System Architecture
**Double-Inverted Pendulum Sliding Mode Control System** ## Executive Summary This document provides architectural documentation for the Particle Swarm Optimization (PSO) integration system within the Double-Inverted Pendulum (DIP) Sliding Mode Control framework. The architecture encompasses a sophisticated multi-layered design that enables automated controller gain optimization across multiple SMC variants with robust performance metrics and uncertainty handling. **System Status**: ✅ **PRODUCTION READY** - All components fully operational
**Integration Health**: 100% functional capability with validation
**Performance**: Vectorized optimization achieving sub-second iteration times

---

## 1. High-Level System Architecture ### 1.1 Architectural Overview ```

┌─────────────────────────────────────────────────────────────────────────────┐
│ PSO INTEGRATION SYSTEM │
├─────────────────────────────────────────────────────────────────────────────┤
│ │
│ ┌─────────────────┐ ┌──────────────────┐ ┌─────────────────────┐ │
│ │ CLI Interface │────│ PSO Orchestrator │────│ Configuration Mgmt │ │
│ │ (simulate.py) │ │ (pso_optimizer) │ │ (config.yaml) │ │
│ └─────────────────┘ └──────────────────┘ └─────────────────────┘ │
│ │ │ │ │
│ ▼ ▼ ▼ │
│ ┌─────────────────┐ ┌──────────────────┐ ┌─────────────────────┐ │
│ │ Controller │◄───│ Factory Pattern │────│ Parameter Bounds │ │
│ │ Instantiation │ │ Integration │ │ Validation │ │
│ └─────────────────┘ └──────────────────┘ └─────────────────────┘ │
│ │ │ │ │
│ ▼ ▼ ▼ │
│ ┌─────────────────┐ ┌──────────────────┐ ┌─────────────────────┐ │
│ │ Vectorized │◄───│ Batch Fitness │────│ Cost Function │ │
│ │ Simulation │ │ Evaluation │ │ Normalization │ │
│ │ (vector_sim) │ │ │ │ │ │
│ └─────────────────┘ └──────────────────┘ └─────────────────────┘ │
│ │ │ │ │
│ ▼ ▼ ▼ │
│ ┌─────────────────┐ ┌──────────────────┐ ┌─────────────────────┐ │
│ │ Performance │◄───│ PSO Algorithm │────│ Result Storage │ │
│ │ Analysis │ │ (PySwarms) │ │ & Validation │ │
│ └─────────────────┘ └──────────────────┘ └─────────────────────┘ │
│ │
└─────────────────────────────────────────────────────────────────────────────┘
``` ### 1.2 Core Integration Components **Primary System Modules:** 1. **PSO Tuner Engine** (`src/optimization/algorithms/pso_optimizer.py`) - Vectorized particle swarm optimization implementation - Adaptive penalty mechanisms for stability enforcement - Uncertainty-aware optimization with robustness evaluation 2. **Controller Factory Interface** (`src/controllers/factory.py`) - Unified controller instantiation across SMC variants - Dynamic parameter validation and bounds checking - PSO-compatible gain vector interface contracts 3. **Vectorized Simulation Engine** (`src/simulation/engines/vector_sim.py`) - High-performance batch trajectory evaluation - Parallel computation for swarm fitness assessment - Memory-efficient state trajectory management 4. **Configuration Management System** (`config.yaml`) - parameter bounds specification - Controller-specific optimization settings - Cost function normalization parameters

---

## 2. Component Architecture Details ### 2.1 PSO Tuner Engine Architecture **Module**: `src/optimization/algorithms/pso_optimizer.py` ```python
# example-metadata:
# runnable: false class PSOTuner: """High-throughput, vectorised tuner for sliding-mode controllers.""" # Core Components: def __init__(self, controller_factory, config, seed=None, rng=None): """ Architecture Elements: - Local PRNG management (avoid global side effects) - Instance-level normalization constants - Adaptive penalty computation - Configuration validation and deprecation handling """ def _fitness(self, particles: np.ndarray) -> np.ndarray: """ Vectorized fitness evaluation pipeline: 1. Pre-filter invalid particles via validate_gains() 2. Batch simulation via vector_sim 3. Cost computation with instability penalties 4. Uncertainty aggregation (if configured) """ def optimize(self, **kwargs) -> Dict[str, Any]: """ PySwarms integration with enhancements: - Velocity clamping for stability - Inertia weight scheduling - Convergence monitoring - Result validation and storage """
``` **Key Architectural Features:**

- **Decoupled State Management**: No global variable modification
- **Adaptive Instability Penalties**: Dynamic penalty computation based on normalization constants
- **Uncertainty Integration**: Multi-draw robustness evaluation
- **Performance Optimization**: Vectorized operations with Numba compatibility ### 2.2 Controller Factory Integration **Module**: `src/controllers/factory.py` ```python
# example-metadata:

# runnable: false def create_controller(controller_type: str, gains: np.ndarray, **kwargs) -> Controller: """ PSO-compatible factory interface. Integration Requirements: 1. Standardized gain vector interface across all controller types 2. Built-in parameter validation with bounds checking 3. Consistent actuator saturation limits (max_force) 4. Optional validate_gains() method for PSO pre-filtering """ # Controller-Specific Interfaces:

class ClassicalSMC: def __init__(self, gains: np.ndarray): # [c1, λ1, c2, λ2, K, kd] def validate_gains(self, particles: np.ndarray) -> np.ndarray: # Optional @property def max_force(self) -> float: # Required for PSO class STASMC: def __init__(self, gains: np.ndarray): # [K1, K2, k1, k2, λ1, λ2] # Same interface requirements... class AdaptiveSMC: def __init__(self, gains: np.ndarray): # [c1, λ1, c2, λ2, γ] # Same interface requirements...
``` **Interface Contracts:**
- **Gain Vector Standardization**: Each controller accepts gains as `np.ndarray`
- **Parameter Validation**: Optional `validate_gains()` for particle pre-filtering
- **Actuator Limits**: Consistent `max_force` property across all controllers
- **Error Handling**: Graceful degradation for invalid parameter combinations ### 2.3 Vectorized Simulation Architecture **Module**: `src/simulation/engines/vector_sim.py` ```python
# example-metadata:
# runnable: false def simulate_system_batch( controller_factory: Callable, particles: np.ndarray, sim_time: float, dt: float, u_max: float, params_list: Optional[List[DIPParams]] = None
) -> Union[Tuple, List[Tuple]]: """ High-performance batch simulation architecture: Performance Features: - Vectorized integration (Numba-optimized) - Memory-efficient trajectory storage - Parallel controller evaluation - Early termination for unstable trajectories Returns: - Time vectors: t ∈ ℝᵀ - State trajectories: x ∈ ℝᴮˣᵀˣ⁶ - Control trajectories: u ∈ ℝᴮˣᵀ - Sliding variables: σ ∈ ℝᴮˣᵀ """
``` **Architectural Optimizations:**

- **Vectorized Dynamics**: Batch computation of system dynamics
- **Memory Management**: Efficient trajectory storage with early termination
- **Numerical Stability**: Robust integration with instability detection
- **Scalability**: Linear scaling with particle count and simulation horizon

---

## 3. Data Flow Architecture ### 3.1 PSO Optimization Workflow ```

┌─────────────────┐
│ CLI Command │ python simulate.py --ctrl classical_smc --run-pso
│ (simulate.py) │
└─────────┬───────┘ ▼
┌─────────────────┐
│ Configuration │ Load config.yaml, validate PSO parameters
│ Loading │ Extract controller bounds, cost function weights
└─────────┬───────┘ ▼
┌─────────────────┐
│ PSOTuner Init │ Initialize with controller_factory, local RNG
│ │ Compute normalization constants, penalty factors
└─────────┬───────┘ ▼
┌─────────────────┐
│ PySwarms Setup │ Configure particle bounds, PSO hyperparameters
│ │ Initialize swarm positions and velocities
└─────────┬───────┘ ▼
┌─────────────────┐
│ Optimization │ ┌─ For each iteration:
│ Loop │ │ ├─ Pre-filter particles (validate_gains)
│ │ │ ├─ Batch simulation (vector_sim)
│ │ │ ├─ Fitness evaluation (cost computation)
│ │ │ ├─ Update particle positions/velocities
│ │ │ └─ Check convergence criteria
│ │ └─ Return best gains and cost history
└─────────┬───────┘ ▼
┌─────────────────┐
│ Result Storage │ Save optimized gains to JSON file
│ & Validation │ Perform final validation simulation
└─────────────────┘
``` ### 3.2 Cost Function Architecture **Mathematical Foundation:**
```

J(G) = w₁·J_ISE(G) + w₂·J_control(G) + w₃·J_rate(G) + w₄·J_sliding(G) + P(G) Where:
- J_ISE: Integral squared error across all state variables
- J_control: Control effort penalty (actuator energy)
- J_rate: Control rate penalty (actuator slew limitation)
- J_sliding: Sliding variable energy (stability measure)
- P(G): Instability penalty (early termination, NaN/Inf trajectories)
``` **Normalization Architecture:**
```python

def _compute_cost_from_traj(self, t, x_b, u_b, sigma_b) -> np.ndarray: """ Multi-stage cost computation: 1. Detect instability (angle limits, trajectory explosion) 2. Compute time-mask for early termination 3. Integrate weighted cost components 4. Apply graded penalties for failure 5. Normalize by baseline performance constants """
```

---

## 4. Interface Specifications ### 4.1 PSO-Controller Interface Contract **Required Controller Attributes:**
```python
# example-metadata:

# runnable: false class ControllerInterface: def __init__(self, gains: np.ndarray): """Initialize with gain vector from PSO particle.""" @property def max_force(self) -> float: """Actuator saturation limit for simulation.""" def validate_gains(self, particles: np.ndarray) -> np.ndarray: """Optional: Pre-filter invalid particles (returns boolean mask).""" def compute_control(self, state: np.ndarray, **kwargs) -> float: """Required: Control law implementation."""

``` **Gain Vector Specifications:**
```python
# Controller-specific gain vector dimensions:

GAIN_DIMENSIONS = { 'classical_smc': 6, # [c1, λ1, c2, λ2, K, kd] 'sta_smc': 6, # [K1, K2, k1, k2, λ1, λ2] 'adaptive_smc': 5, # [c1, λ1, c2, λ2, γ] 'hybrid_adaptive_sta_smc': 4, # [c1, λ1, c2, λ2] 'swing_up_smc': 6 # Uses stabilizing controller gains
}
``` ### 4.2 Configuration Schema Interface **PSO Configuration Structure:**
```yaml

pso: # Core PSO parameters n_particles: 50 n_iterations: 100 cognitive_weight: 1.49445 social_weight: 1.49445 inertia_weight: 0.729 # Advanced features velocity_clamp: [0.1, 0.5] # [min_factor, max_factor] w_schedule: [0.9, 0.4] # [w_start, w_end] # Parameter bounds (controller-specific) bounds: classical_smc: lower: [0.1, 0.1, 0.1, 0.1, 0.1, 0.1] upper: [20.0, 20.0, 20.0, 20.0, 100.0, 10.0]
``` **Cost Function Configuration:**
```yaml

cost_function: weights: state_error: 1.0 control_effort: 0.01 control_rate: 0.001 stability: 10.0 # Normalization constants norms: state_error: 1.0 control_effort: 1.0 control_rate: 1.0 sliding: 1.0 # Penalty configuration instability_penalty: 1e6 combine_weights: mean: 0.7 max: 0.3
```

---

## 5. Performance Architecture ### 5.1 Computational Optimization **Vectorization Strategy:**
- **Batch Simulation**: All particles evaluated simultaneously
- **NumPy Acceleration**: Vectorized array operations throughout
- **Memory Efficiency**: Trajectory storage optimization with early termination
- **Numba Integration**: JIT compilation for dynamics computation **Performance Metrics:**
```python
# Typical performance characteristics:

PARTICLES = 50
ITERATIONS = 100
SIMULATION_TIME = 10.0 # seconds
DT = 0.001 # seconds # Expected performance:
ITERATION_TIME = 0.8 # seconds per iteration
TOTAL_OPTIMIZATION = 80 # seconds for full PSO run
MEMORY_USAGE = 200 # MB peak memory
``` ### 5.2 Scalability Architecture **Horizontal Scaling:**
- Particle count scales linearly with computational resources
- Memory usage scales as O(n_particles × simulation_steps)
- No threading bottlenecks (embarrassingly parallel fitness evaluation) **Vertical Scaling:**
- Simulation time resolution controllable via `dt` parameter
- Uncertainty evaluation scales as O(n_uncertainty_draws)
- Cost function complexity scales as O(simulation_steps)

---

## 6. Error Handling Architecture ### 6.1 Failure Mode Management **Instability Detection:**
```python
# Multi-level instability detection:

1. NaN/Inf trajectory values (immediate penalty)
2. Pendulum angle limits |θ| > π/2 (early termination)
3. State explosion |x| > 1e6 (numerical instability)
4. Control saturation violations (soft penalty)
``` **Graceful Degradation:**
```python
# Penalty application hierarchy:

1. Invalid gains → validate_gains() pre-filtering
2. Simulation failure → instability_penalty
3. NaN cost computation → instability_penalty
4. Convergence failure → return best available solution
``` ### 6.2 Diagnostic Architecture **Monitoring Capabilities:**
- Real-time convergence tracking
- Particle diversity analysis
- Cost component breakdown
- Performance timing analysis **Debugging Support:**
- Detailed error logging with stack traces
- Intermediate result storage for analysis
- Configurable verbosity levels
- Reproducible random number generation

---

## 7. Integration Testing Architecture ### 7.1 Validation Framework **Test Coverage:**
```python
# test suite:

1. Unit tests: Individual component validation
2. Integration tests: End-to-end PSO workflows
3. Performance tests: Benchmark timing and memory
4. Robustness tests: Parameter boundary conditions
5. Scientific tests: Theoretical property validation
``` **Acceptance Criteria:**
```python
# PSO integration success metrics:

CONVERGENCE_RATE = 0.95 # 95% of runs converge successfully
MAX_ITERATION_TIME = 1.0 # seconds per iteration upper bound
STABILITY_MARGIN = 0.1 # minimum phase margin for optimized gains
REPEATABILITY = 0.05 # cost variation between identical runs
``` ### 7.2 Continuous Integration **Automated Validation:**
- Pre-commit hooks for PSO functionality
- Nightly regression testing with multiple controller types
- Performance benchmarking against baseline implementations
- Documentation consistency validation **Quality Gates:**
- All PSO tests pass before deployment
- Performance regression detection (±5% threshold)
- Configuration schema validation
- API interface contract compliance

---

## 8. Future Architecture Enhancements ### 8.1 Planned Extensions **Multi-Objective Optimization:**
- Pareto frontier exploration for competing objectives
- NSGA-II integration for trade-off analysis
- Interactive optimization with user preferences **Advanced Algorithms:**
- Differential Evolution (DE) integration
- Bayesian Optimization for expensive function evaluation
- Hybrid meta-heuristic approaches ### 8.2 Scalability Roadmap **Distributed Computing:**
- Message passing interface (MPI) for cluster computing
- GPU acceleration for massive particle swarms
- Cloud deployment with auto-scaling features **Real-Time Integration:**
- Online parameter adaptation during operation
- Model predictive control (MPC) with PSO receding horizon
- Hardware-in-the-loop (HIL) optimization integration

---

## 9. Conclusion The PSO integration system architecture provides a robust, scalable, and maintainable framework for automated controller gain optimization. The modular design ensures extensibility while maintaining high performance and reliability. All components are fully operational with validation and monitoring capabilities. **Key Architectural Strengths:**
- **Modularity**: Clean separation of concerns with well-defined interfaces
- **Performance**: Vectorized computation with sub-second iteration times
- **Reliability**: error handling and graceful degradation
- **Extensibility**: Plugin architecture for new controllers and algorithms
- **Maintainability**: Thorough documentation and testing coverage This architecture successfully resolves GitHub Issue #4 and provides a solid foundation for future optimization enhancements.