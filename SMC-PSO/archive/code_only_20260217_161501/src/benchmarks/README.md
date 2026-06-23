# Benchmark Analysis Modules

Python utilities for benchmark execution, analysis, and comparison.

**Moved from:** `benchmarks/{analysis,benchmark,comparison,integration,examples}/`
**Migration Date:** December 18, 2025
**Reason:** Proper package structure (analysis modules belong in src/, not data directory)

## Modules

- `analysis/` - Accuracy metrics, statistical analysis, energy/convergence analyzers
- `benchmark/` - Integration benchmark runner and execution framework
- `comparison/` - Method comparison utilities and scenario management
- `integration/` - Numerical integration methods (RK4, adaptive RK45, etc.)
- `examples/` - Usage examples demonstrating benchmark workflows

## Import Changes

**Old (deprecated):**
```python
from benchmarks.analysis import accuracy_metrics
from benchmarks.benchmark import IntegrationBenchmark
```

**New:**
```python
from src.benchmarks.analysis import accuracy_metrics
from src.benchmarks.benchmark import IntegrationBenchmark
```

## Migration

All imports were automatically updated by `scripts/migration/update_benchmark_paths.py`.
If you encounter import errors, verify the new path structure.

## Integration with Benchmark Data

- Read raw data: `benchmarks/raw/`
- Write processed data: `benchmarks/processed/`
- Generate figures: `benchmarks/figures/`
- See also: `benchmarks/README.md` for data organization
