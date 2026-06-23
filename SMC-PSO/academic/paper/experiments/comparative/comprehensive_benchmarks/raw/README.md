# MT-5: Comprehensive Benchmark Suite

**Task:** Medium-term Task 5 - Comprehensive Benchmark Suite
**Completed:** October 25, 2025
**Research Phase:** Phase 5 (Research & Validation)

## Provenance

**Controller Suite:** 7 controllers tested
- Classical SMC
- Super-Twisting Algorithm (STA) SMC
- Adaptive SMC
- Hybrid Adaptive STA-SMC
- Boundary Layer SMC
- Swing-Up Controller
- Model Predictive Control (MPC)

**Test Parameters:**
- Simulation time: 10 seconds
- Time step: 0.01 seconds
- Initial conditions: Small angle perturbation [0.1, 0, 0.1, 0, 0, 0]
- Performance metrics: RMSE, settling time, chattering index, control effort

## Output Files

- `comprehensive_benchmark.csv` (1.2 KB) - Tabular results
- `comprehensive_benchmark.json` (3.4 KB) - Detailed time series

## Usage

Load results:
```python
import pandas as pd
results = pd.read_csv('benchmarks/raw/MT-5_comprehensive/comprehensive_benchmark.csv')
```

## Related Outputs

- Figures: `benchmarks/figures/comprehensive_benchmark_*.png`
- Report: `benchmarks/reports/MT5_ANALYSIS_SUMMARY.md`
