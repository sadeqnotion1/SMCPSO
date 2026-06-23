# Baseline Benchmarks

Original baseline performance data for controller validation and comparison.

## Files

- `baseline_performance.csv` (642 B) - Initial performance baselines
- `baseline_integration.csv` (89 B) - Integration accuracy baselines
- `baseline_integration_template.csv` (1.8 KB) - Template for integration tests

## Purpose

These baselines establish reference performance metrics for:
1. Controller validation (performance regression detection)
2. Comparative analysis (improvement quantification)
3. PSO optimization (baseline vs optimized comparison)

## Usage

```python
import pandas as pd
baseline = pd.read_csv('benchmarks/raw/baselines/baseline_performance.csv')
```

## Related Work

- PSO optimization results: `optimization_results/`
- Comprehensive benchmarks: `benchmarks/raw/MT-5_comprehensive/`
