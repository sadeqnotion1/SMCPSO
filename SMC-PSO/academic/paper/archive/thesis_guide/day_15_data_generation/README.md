# DAY 15: Data Generation and Figure/Table Automation

**Time**: 8 hours
**Output**: 60 figures + 30 tables (automated)
**Difficulty**: Technical (scripting/automation)

---

## OVERVIEW

Day 15 is a CRITICAL pivot point: stop writing, start generating data. You'll run simulations, extract benchmark data, and use automation scripts to create all 60 figures and 30 tables needed for Chapters 10-12 (results chapters).

**Why This Matters**: Results chapters (Days 16-21) depend entirely on having figures and tables ready. Do this well, and Days 16-21 become mostly narration.

---

## OBJECTIVES

By end of Day 15, you will have:

1. [ ] All benchmark simulations run (7 controllers, 5+ scenarios)
2. [ ] 20 CSV files with performance data
3. [ ] 60 figures generated and saved as PDFs
4. [ ] 30 LaTeX tables generated from CSVs
5. [ ] Organized figure/table directories
6. [ ] Verification: all figures compile in LaTeX

---

## TIME BREAKDOWN

| Step | Task | Time | Output |
|------|------|------|--------|
| 1 | Run baseline simulations | 2 hours | 5 CSV files |
| 2 | Run robustness tests | 2 hours | 8 CSV files |
| 3 | Run PSO optimization | 1 hour | 7 JSON files |
| 4 | Generate all figures | 2 hours | 60 PDFs |
| 5 | Generate all tables | 1 hour | 30 .tex files |
| 6 | Verify and organize | 1 hour | Clean directories |
| **TOTAL** | | **8 hours** | **60 figs + 30 tables** |

---

## STEPS

### Step 1: Run Baseline Simulations (2 hours)
**File**: `step_01_baseline_sims.md`
- Run all 7 controllers with nominal parameters
- Scenarios: step response, disturbance rejection
- Output: `baseline_performance.csv`, time series data

### Step 2: Run Robustness Tests (2 hours)
**File**: `step_02_robustness_tests.md`
- Parameter uncertainty sweeps (±30%)
- External disturbances (impulse, sinusoidal)
- Measurement noise
- Output: 8 CSV files for different test conditions

### Step 3: Run PSO Optimization (1 hour)
**File**: `step_03_pso_runs.md`
- PSO tuning for each controller
- Convergence data collection
- Output: gains JSON + convergence CSV

### Step 4: Generate All Figures (2 hours)
**File**: `step_04_generate_figures.md`
- Run `python automation_scripts/generate_figures.py`
- Creates 60 figures:
  - Time responses (20 figures)
  - Phase portraits (10 figures)
  - Robustness analysis (15 figures)
  - PSO convergence (10 figures)
  - Chattering FFT (5 figures)

### Step 5: Generate All Tables (1 hour)
**File**: `step_05_generate_tables.md`
- Run `python automation_scripts/csv_to_table.py` for each CSV
- Creates 30 LaTeX tables:
  - Performance metrics (10 tables)
  - Robustness rankings (8 tables)
  - PSO parameters (6 tables)
  - Statistical summaries (6 tables)

### Step 6: Verify and Organize (1 hour)
**File**: `step_06_verify_organize.md`
- Check all files exist
- Test compilation in LaTeX
- Organize by chapter
- Create index document

---

## SOURCE FILES

### Existing Benchmark Data

**If these exist, you can skip simulations!**
- `benchmarks/baseline_performance.csv` (QW-2)
- `benchmarks/comprehensive_benchmark.csv` (MT-5)
- `benchmarks/LT6_uncertainty_analysis.csv` (LT-6)
- `benchmarks/LT6_robustness_ranking.csv` (LT-6)
- `benchmarks/MT7_robustness_summary.json` (MT-7)
- `benchmarks/MT8_disturbance_results.csv` (MT-8)

**Check first**:
```bash
ls -lh benchmarks/*.csv
```

If files exist → proceed to Step 4 (save 4 hours!)

### Simulation Scripts

**For running new simulations**:
- `simulate.py` - Main simulation script
- Example: `python simulate.py --ctrl classical_smc --plot --save results.csv`

### Automation Scripts (from Day 1)

**For figure generation**:
- `thesis/scripts/generate_figures.py`
  - Reads CSV files from benchmarks/
  - Creates 60 publication-quality figures
  - Saves to thesis/figures/

**For table generation**:
- `thesis/scripts/csv_to_table.py`
  - Converts CSV → LaTeX booktabs format
  - Usage: `csv_to_table.py input.csv output.tex "Caption" "label"`

---

## EXPECTED OUTPUT

### Figures (60 total)

**Chapter 10 (Controller Comparison) - 25 figures**:
- Figure 10.1-10.7: Time responses (7 controllers)
- Figure 10.8-10.14: Phase portraits
- Figure 10.15-10.21: Control input plots
- Figure 10.22-10.25: Comparison bar charts

**Chapter 11 (Robustness) - 20 figures**:
- Figure 11.1-11.6: Parameter uncertainty results
- Figure 11.7-11.12: Disturbance rejection
- Figure 11.13-11.18: Measurement noise
- Figure 11.19-11.20: Robustness ranking

**Chapter 12 (PSO) - 15 figures**:
- Figure 12.1-12.7: PSO convergence curves (7 controllers)
- Figure 12.8-12.10: Cost function landscapes
- Figure 12.11-12.13: Sensitivity analysis
- Figure 12.14-12.15: Manual vs. PSO comparison

### Tables (30 total)

**Chapter 10 - 12 tables**:
- Table 10.1: Baseline performance metrics (7 controllers)
- Table 10.2: Settling time comparison
- Table 10.3: Overshoot comparison
- Table 10.4: Control effort comparison
- Table 10.5: Chattering metrics
- Table 10.6-10.12: Individual controller detailed metrics

**Chapter 11 - 10 tables**:
- Table 11.1-11.3: Uncertainty analysis results
- Table 11.4-11.6: Disturbance rejection metrics
- Table 11.7-11.9: Noise robustness
- Table 11.10: Overall robustness ranking

**Chapter 12 - 8 tables**:
- Table 12.1-12.7: PSO-tuned gains (7 controllers)
- Table 12.8: PSO hyperparameters

---

## VALIDATION CHECKLIST

### Simulations Complete
- [ ] All 7 controllers run successfully
- [ ] Nominal scenario: step response converges
- [ ] Disturbance scenario: system recovers
- [ ] Uncertainty scenario: ±30% parameter variations
- [ ] No crashes or NaN values in data

### Data Files Present
- [ ] 20 CSV files exist in `benchmarks/`
- [ ] Each CSV has correct columns (time, x, theta1, theta2, u)
- [ ] No empty files
- [ ] Data ranges reasonable (e.g., |theta| < π)

### Figures Generated
- [ ] 60 PDF files in `thesis/figures/`
- [ ] Organized by chapter: `chapter10/`, `chapter11/`, `chapter12/`
- [ ] All figures have titles and axis labels
- [ ] Resolution: at least 300 DPI
- [ ] File sizes reasonable (< 1MB each)

### Tables Generated
- [ ] 30 .tex files in `thesis/tables/`
- [ ] Each table has \caption{} and \label{}
- [ ] Booktabs format (\toprule, \midrule, \bottomrule)
- [ ] Compile without errors
- [ ] Numbers formatted consistently (2-3 decimal places)

### LaTeX Integration
- [ ] Test compile: Include 1 figure in dummy chapter
- [ ] Test compile: Include 1 table in dummy chapter
- [ ] No "File not found" errors
- [ ] Figures render at correct size
- [ ] Tables fit within page margins

---

## TROUBLESHOOTING

### Simulation Fails to Converge

**Problem**: Controller unstable, simulation crashes
**Solution**:
- Check gains are reasonable (not too high/low)
- Increase simulation time step tolerance
- Use simplified dynamics first, then full dynamics

### CSV Files Have Wrong Format

**Problem**: csv_to_table.py fails with "KeyError"
**Solution**:
- Verify CSV headers match expected names
- Check for missing columns
- Use `head -n 5 file.csv` to inspect

### Figures Look Bad (Low Quality)

**Problem**: Pixelated or blurry figures
**Solution**:
```python
# In generate_figures.py
plt.savefig('figure.pdf', dpi=300, bbox_inches='tight')
```

### Tables Too Wide for Page

**Problem**: LaTeX error "Overfull \hbox"
**Solution**:
- Reduce column widths
- Use smaller font: `\small` before table
- Rotate landscape: `\begin{landscape}...\end{landscape}`
- Split into two tables

### generate_figures.py Script Errors

**Problem**: "ModuleNotFoundError: No module named 'matplotlib'"
**Solution**:
```bash
pip install matplotlib pandas numpy scipy
```

---

## AUTOMATION SCRIPT USAGE

### Generate All Figures

```bash
cd thesis/scripts
python generate_figures.py --input ../../benchmarks/ --output ../figures/
```

Expected output:
```
[INFO] Generating 60 figures...
[OK] Chapter 10: 25 figures created
[OK] Chapter 11: 20 figures created
[OK] Chapter 12: 15 figures created
[OK] All figures saved to thesis/figures/
```

### Generate All Tables

```bash
cd thesis/scripts
for csv in ../../benchmarks/*.csv; do
  python csv_to_table.py "$csv" "../tables/$(basename $csv .csv).tex" "Auto-caption" "tab:auto"
done
```

Expected: 20 .tex files in `thesis/tables/`

### Batch Simulation

```bash
# Run all 7 controllers
for ctrl in classical_smc sta_smc adaptive_smc hybrid_adaptive_sta_smc swing_up; do
  python simulate.py --ctrl $ctrl --save benchmarks/${ctrl}_baseline.csv
done
```

---

## TIME MANAGEMENT

### If Simulations Already Exist

Check: `ls benchmarks/*.csv | wc -l`

If 15+ files exist → **skip Steps 1-3 (save 5 hours!)**
Proceed directly to Step 4 (generate figures)

### If Behind Schedule

At hour 4, only 10 CSV files generated (target: 20):
- **Option 1**: Use existing benchmark data from research tasks
- **Option 2**: Run fewer scenarios (skip some robustness tests)
- **Option 3**: Extend Day 15 to 10 hours

### If Ahead of Schedule

At hour 6, all figures/tables done (target: hour 8):
- **Option 1**: Generate extra figures (animations, 3D plots)
- **Option 2**: Start Day 16 (Chapter 10 writing)
- **Option 3**: Quality check all outputs

---

## NEXT STEPS

Once Day 15 checklist is complete:

1. Browse generated figures (verify quality)
2. Review table formatting (consistent decimals)
3. Create `figure_index.md` (list all 60 figures)
4. Create `table_index.md` (list all 30 tables)
5. Read `day_16_17_chapter10/README.md` (10 min)

**Days 16-17**: Write Chapter 10 - Controller Comparison Results (20 pages)

---

## ESTIMATED COMPLETION TIME

- **With existing data**: 4-5 hours (just figure/table generation)
- **Without data**: 8-10 hours (run simulations + generation)
- **Everything from scratch**: 12-14 hours (extensive simulations)

**Best case**: Use existing benchmark CSVs from research tasks (QW-2, MT-5, LT-6, etc.)

---

**[OK] Automation day! Generate 90 outputs in 8 hours. Open `step_01_baseline_sims.md`!**
