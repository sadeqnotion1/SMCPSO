# PSO Convergence Analysis - Issue #12

Generated: D:\Projects\main

## Summary Table

| Controller | Status | Initial Cost | Final Cost | Improvement | Converged At |
|------------|--------|--------------|------------|-------------|-------------|
| classical_smc | CONVERGED | 1.2 | 533.0 | -44689.9% | Iter 43 |
| adaptive_smc | CONVERGED | 2.8 | 1.6 | 42.9% | Iter 5 |
| sta_smc | CONVERGED | 1.4 | 2.1 | -47.2% | Iter 5 |
| hybrid_adaptive_sta_smc | CONVERGED | 1.0 | 1.0 | ? | Iter 5 |

## Detailed Analysis

### classical_smc

- **Status**: CONVERGED
- **Initial Cost**: 1.19
- **Final Cost**: 533.00
- **Min Cost**: 1.19
- **Improvement**: -44689.92%
- **Converged At**: Iteration 43
- **Total Iterations Logged**: 91
- **Assessment**: ❌ **FAIL** (chattering target < 2.0 not met)

### adaptive_smc

- **Status**: CONVERGED
- **Initial Cost**: 2.82
- **Final Cost**: 1.61
- **Min Cost**: 1.61
- **Improvement**: 42.91%
- **Converged At**: Iteration 5
- **95% Convergence Rate**: Iteration 15
- **Total Iterations Logged**: 72
- **Assessment**: ✅ **PASS** (chattering target < 2.0 met)

### sta_smc

- **Status**: CONVERGED
- **Initial Cost**: 1.44
- **Final Cost**: 2.12
- **Min Cost**: 1.44
- **Improvement**: -47.22%
- **Converged At**: Iteration 5
- **Total Iterations Logged**: 74
- **Assessment**: ❌ **FAIL** (chattering target < 2.0 not met)

### hybrid_adaptive_sta_smc

- **Status**: CONVERGED
- **Initial Cost**: 1.00
- **Final Cost**: 1.00
- **Min Cost**: 1.00
- **Improvement**: 0.00%
- **Converged At**: Iteration 5
- **Total Iterations Logged**: 248
- **Assessment**: ✅ **PASS** (chattering target < 2.0 met)

## Observations

- **Target**: Chattering index < 2.0
- **Convergence Criterion**: Standard deviation < 1.0 over 20-iteration window
- **PSO Configuration**: 30 particles, 150 iterations, seed=42
