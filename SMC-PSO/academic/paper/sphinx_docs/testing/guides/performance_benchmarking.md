<!--======================================================================================\\\
============== docs/testing/guides/performance_benchmarking.md =======================\\\
=======================================================================================-->

# Performance Benchmarking Guide

**Purpose**: Systematic approach to measuring, analyzing, and optimizing performance of control systems, simulation engines, and optimization algorithms.



## 🎯 Quick Start

```bash
# Run all benchmarks
pytest tests/benchmarks/ --benchmark-only

# Compare with baseline
pytest tests/benchmarks/ --benchmark-compare=baseline --benchmark-compare-fail=mean:5%

# Profile specific component
pytest tests/benchmarks/test_controllers_bench.py -k classical_smc --benchmark-histogram
```



## 📊 Benchmark Categories

### 1. Controller Performance

**Metrics**:
- Control computation time (µs per call)
- Memory allocation per control cycle
- Cache efficiency
- Vectorization speedup

**Example**:
```python
import pytest
from pytest_benchmark.fixture import BenchmarkFixture

def test_classical_smc_benchmark(benchmark: BenchmarkFixture):
    """Benchmark classical SMC control computation"""
    controller = ClassicalSMC(gains=[10, 5, 8, 3, 15, 2])
    state = np.array([0.1, -0.2, 0.5, -0.3])

    result = benchmark(controller.compute_control, state)

    # Performance requirements
    assert benchmark.stats['mean'] < 50e-6  # <50µs mean
    assert benchmark.stats['stddev'] < 5e-6  # <5µs std dev
```

**Target Performance**:
| Controller | Mean Time | Max Time | Throughput |
|------------|-----------|----------|------------|
| Classical SMC | <50µs | <100µs | >20k Hz |
| Adaptive SMC | <200µs | <500µs | >5k Hz |
| STA SMC | <100µs | <200µs | >10k Hz |
| MPC | <10ms | <20ms | >100 Hz |



### 2. Dynamics Simulation

**Metrics**:
- Integration step time
- State vector update cost
- Numba compilation overhead
- Parallel scaling efficiency

**Example**:
```python
@pytest.mark.benchmark(group="dynamics")
def test_full_dynamics_performance(benchmark):
    """Benchmark full nonlinear dynamics"""
    dynamics = FullDynamics()
    state = np.array([0.1, 0.1, 0.0, 0.0])
    u = 1.0

    result = benchmark(dynamics.compute_derivatives, state, u)

    # Requirement: 1000 steps in <1ms
    assert benchmark.stats['mean'] < 1e-6  # <1µs per step
```



### 3. PSO Optimization

**Metrics**:
- Iteration time
- Convergence rate
- Particle diversity
- Fitness evaluations per second

**Example**:
```python
# example-metadata:
# runnable: false

def test_pso_optimization_benchmark(benchmark):
    """Benchmark PSO convergence speed"""
    tuner = PSOTuner(
        n_particles=30,
        iterations=50,
        bounds=[(1, 100)] * 6
    )

    def run_pso():
        return tuner.optimize(fitness_function)

    result = benchmark.pedantic(run_pso, iterations=5, rounds=3)

    # Requirements
    assert benchmark.stats['mean'] < 60.0  # <60s for 50 iterations
    assert result['cost'] < 0.1  # Converges to good solution
```



## 🔬 Measurement Techniques

### Statistical Rigor

```python
from pytest_benchmark.stats import welch_ttest

def test_optimization_comparison(benchmark):
    """Compare two implementations with statistical significance"""
    # Run baseline
    baseline_times = benchmark_baseline()

    # Run optimized version
    optimized_times = benchmark_optimized()

    # Welch's t-test for significance
    t_stat, p_value = welch_ttest(baseline_times, optimized_times)

    assert p_value < 0.05, "No statistically significant improvement"
    assert np.mean(optimized_times) < np.mean(baseline_times), \
        "Optimized version is slower"
```



### Profiling Integration

```python
import cProfile
import pstats

def profile_controller_step():
    """Profile control loop with cProfile"""
    profiler = cProfile.Profile()

    profiler.enable()
    for _ in range(1000):
        u = controller.compute_control(state)
        state = dynamics.step(state, u, dt=0.01)
    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions
```



## 📈 Regression Detection

### Automated Baseline Comparison

```bash
# Save baseline
pytest tests/benchmarks/ --benchmark-only --benchmark-save=v1_0_baseline

# Compare against baseline
pytest tests/benchmarks/ --benchmark-only \
  --benchmark-compare=v1_0_baseline \
  --benchmark-compare-fail=mean:5%  # Fail if >5% slower
```



## CI Integration

```yaml
# .github/workflows/benchmark.yml
- name: Run Benchmarks
  run: pytest tests/benchmarks/ --benchmark-json=benchmark_results.json

- name: Compare with Main
  run: |
    pytest-benchmark compare main benchmark_results.json \
      --csv=comparison.csv
```



## 🎯 Optimization Workflow

### Step 1: Identify Bottlenecks

```python
import line_profiler

@profile  # Use kernprof -lv script.py
def slow_function():
    # Line-by-line profiling
    for i in range(1000):
        expensive_operation(i)
```



### Step 2: Vectorization

**Before**:
```python
def compute_cost(states):
    costs = []
    for state in states:
        cost = sum(state**2)  # Slow Python loop
        costs.append(cost)
    return np.array(costs)
```

**After**:
```python
def compute_cost(states):
    return np.sum(states**2, axis=1)  # Vectorized NumPy
```

**Speedup**: 50-100x



### Step 3: Numba Compilation

```python
from numba import jit

@jit(nopython=True, cache=True)
def compute_control_numba(state, gains):
    """Compiled controller - 10-50x faster"""
    k1, k2, k3, k4, k5, k6 = gains
    # Control law implementation
    u = -k1 * state[0] - k2 * state[1] - k3 * state[2]
    return np.clip(u, -MAX_TORQUE, MAX_TORQUE)
```

**Speedup**: 10-50x for numerical code



## 📊 Reporting

### Generate HTML Report

```bash
pytest tests/benchmarks/ --benchmark-only --benchmark-histogram
```

**Output**: `benchmarks/histogram.svg`, `comparison.html`



### Custom Metrics

```python
from pytest_benchmark.utils import format_time

def test_with_custom_metrics(benchmark):
    """Track custom metrics beyond time"""
    def func_with_metrics():
        result = expensive_function()
        # Custom metrics
        return {
            'result': result,
            'memory_mb': get_memory_usage(),
            'cache_misses': get_cache_misses()
        }

    output = benchmark(func_with_metrics)
    print(f"Memory: {output['memory_mb']:.2f} MB")
```



## 🛠️ Best Practices

### 1. Isolate Benchmarks

```python
@pytest.fixture(scope="function")
def fresh_controller():
    """New controller instance per benchmark"""
    return ClassicalSMC(gains=[10, 5, 8, 3, 15, 2])
```



### 2. Warm-Up Iterations

```python
def test_with_warmup(benchmark):
    """Include warm-up for JIT-compiled code"""
    benchmark.pedantic(
        function,
        rounds=10,
        iterations=100,
        warmup_rounds=2  # Warm up JIT compiler
    )
```



### 3. Control Interference

```python
# example-metadata:
# runnable: false

@pytest.mark.benchmark(
    disable_gc=True,  # Disable garbage collector
    min_rounds=10,    # Ensure statistical significance
    timer=time.perf_counter  # High-resolution timer
)
def test_precise_benchmark():
    ...
```



## 📚 Related Documentation

- [PSO Convergence Analysis](../reports/2025-09-30/pso_convergence_analysis.md)
- [Control Systems Unit Testing](control_systems_unit_testing.md)



## 🔗 Navigation

[⬅️ Back to Guides](../guides/) | [🏠 Testing Home](../README.md) | [➡️ Property-Based Testing](property_based_testing.md)



**Last Updated**: September 30, 2025
**Maintainer**: Performance Engineering Team