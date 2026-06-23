# Processed Benchmark Data

Derived and aggregated analysis datasets generated from raw benchmark outputs.

## Files

- `hybrid_anomaly_trend_analysis.json` (11 KB) - Hybrid controller anomaly analysis
- `qw2_performance_ranking.csv` (655 B) - QW-2 controller performance rankings
- `control_accuracy_benchmark_*.json` (4.6 KB) - Control accuracy metrics

## Data Lineage

Processed data is derived from raw benchmarks through analysis scripts:
- Raw data: `benchmarks/raw/`
- Analysis modules: `src/benchmarks/analysis/`
- Visualization: `benchmarks/figures/`

## Reproducibility

All processed data can be regenerated from raw outputs using:
```python
from src.benchmarks.analysis import accuracy_metrics
# Analysis scripts in scripts/analysis/
```

## Methodology

Processing includes:
- Statistical aggregation across controllers
- Comparative performance analysis
- Trend detection and anomaly identification
- Energy and convergence metrics
