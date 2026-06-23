# Step 1: Run Classical SMC Simulation and Collect Data

**Time**: 1 hour | **Output**: CSV files + figures for Classical SMC

---

## OBJECTIVE

Run comprehensive simulations for Classical SMC controller and generate all data files needed for Chapters 10-12.

---

## EXECUTION COMMANDS (45 min)

### 1. Baseline Simulation
```bash
cd D:\Projects\main
python simulate.py --ctrl classical_smc --plot --save results_classical_baseline.json
```

**Outputs**:
- `results_classical_baseline.json` (state trajectories, control signals)
- Figures: position, angles, control signal vs time

### 2. PSO Optimization
```bash
python simulate.py --ctrl classical_smc --run-pso --seed 42 --save gains_classical_pso.json
```

**Outputs**:
- `optimization_results/gains_classical_pso.json` (optimized gains)
- PSO convergence plot

### 3. Robustness Tests
```bash
# IC variations
python simulate.py --ctrl classical_smc --load gains_classical_pso.json --ic "[0.05,0.03,0.02,0,0,0]" --save results_classical_ic1.json
python simulate.py --ctrl classical_smc --load gains_classical_pso.json --ic "[0.1,0.05,0.03,0,0,0]" --save results_classical_ic2.json
python simulate.py --ctrl classical_smc --load gains_classical_pso.json --ic "[0.2,0.1,0.08,0,0,0]" --save results_classical_ic3.json
python simulate.py --ctrl classical_smc --load gains_classical_pso.json --ic "[0.3,0.15,0.12,0,0,0]" --save results_classical_ic4.json

# Step disturbance
python simulate.py --ctrl classical_smc --load gains_classical_pso.json --disturbance step --save results_classical_step.json

# Impulse disturbance
python simulate.py --ctrl classical_smc --load gains_classical_pso.json --disturbance impulse --save results_classical_impulse.json
```

### 4. Statistical Analysis (Monte Carlo)
```bash
# Run with 10 different seeds
for seed in 42 43 44 45 46 47 48 49 50 51; do
    python simulate.py --ctrl classical_smc --seed $seed --save results_classical_seed_${seed}.json
done
```

### 5. Extract Metrics to CSV
```bash
python scripts/extract_metrics.py results_classical_*.json --output benchmarks/classical_smc_comprehensive.csv
```

**CSV columns**: seed, settling_time, overshoot, ss_error, control_effort, chattering, convergence_rate

---

## DATA VERIFICATION (15 min)

### Check File Existence
```bash
ls -lh results_classical_*.json
ls -lh optimization_results/gains_classical_pso.json
ls -lh benchmarks/classical_smc_comprehensive.csv
```

### Validate CSV Content
```bash
head -20 benchmarks/classical_smc_comprehensive.csv
python -c "import pandas as pd; df = pd.read_csv('benchmarks/classical_smc_comprehensive.csv'); print(df.describe())"
```

**Expected**:
- 16 JSON files (1 baseline + 4 IC + 2 disturbance + 1 PSO + 10 seeds = 18 total)
- 1 CSV file with 16+ rows
- Settling times: 2-8 seconds
- Overshoot: <0.2 rad
- No NaN values

---

## VALIDATION CHECKLIST

### Simulation Outputs
- [ ] Baseline simulation completed (results_classical_baseline.json)
- [ ] PSO optimization completed (gains in JSON)
- [ ] 4 IC variations completed
- [ ] 2 disturbance scenarios completed
- [ ] 10 Monte Carlo runs completed

### Data Files
- [ ] All JSON files present (check file count)
- [ ] CSV file generated with metrics
- [ ] No errors in simulation logs

### Data Quality
- [ ] No NaN or Inf values in CSV
- [ ] Settling times reasonable (1-10 seconds)
- [ ] Overshoot values reasonable (<0.5 rad)
- [ ] Control forces within limits (±150 N)

---

## COMMON ISSUES

**Issue**: Simulation diverges (NaN values)
**Fix**:
- Check gains are in valid range
- Verify initial condition not too large
- Reduce time step if needed (dt=0.0005)

**Issue**: PSO takes too long (>5 minutes)
**Fix**:
- Reduce iterations: --pso-iter 30
- Reduce particles: --pso-particles 20

**Issue**: CSV extraction fails
**Fix**:
- Verify JSON files are valid: `python -m json.tool results_classical_baseline.json`
- Check extract_metrics.py script exists

---

## TIME CHECK
- Baseline + PSO: 10 min
- IC variations: 10 min (4 × 2.5 min)
- Disturbances: 5 min (2 × 2.5 min)
- Monte Carlo: 15 min (10 × 1.5 min)
- CSV extraction: 5 min
- Verification: 15 min
- **Total**: ~1 hour

---

## NEXT STEP

**Proceed to**: `step_02_run_sta_smc.md`

Repeat this process for STA-SMC controller.

---

**[OK] Classical SMC data generation complete!**
