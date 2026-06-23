# Step 6: Write Section 8.5 - Hardware Specifications

**Time**: 45 minutes
**Output**: 1.5 pages
**Source**: thesis/notes/chapter08_hardware.txt

---

## EXACT PROMPT

```
Write Section 8.5 - Hardware Specifications (1.5 pages) for Chapter 8.

Structure (1.5 pages):

**Page 1: Computational Platform**

Subsection: Development Workstation
- CPU: [Extract actual specs - e.g., Intel Core i7-11700K @ 3.6 GHz, 8 cores/16 threads]
- RAM: [Extract - e.g., 32 GB DDR4-3200]
- OS: Windows 11 (64-bit)
- Storage: SSD (for fast I/O during data logging)

Subsection: Software Environment
- Python: 3.9.x (from python --version)
- Key libraries:
  * NumPy 1.24+ (vectorized computation)
  * SciPy 1.10+ (numerical integration)
  * Numba 0.56+ (JIT compilation for 50x speedup)
  * PySwarms 1.3.0 (PSO implementation)
  * pytest 7.2+ (testing framework)
- Development: VS Code with Python extension

Table 8.4: Software Environment
| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.9.x | Core language |
| NumPy | 1.24+ | Array computation |
| SciPy | 1.10+ | Numerical methods |
| Numba | 0.56+ | JIT compilation |
| PySwarms | 1.3.0 | PSO optimization |
| Matplotlib | 3.7+ | Visualization |

**Page 2: Computational Performance**

Subsection: Simulation Timing
- Single simulation: ~50 ms (5 seconds simulated at 1 kHz sampling)
- Batch simulation (30): ~1.5 seconds (Numba parallelized)
- PSO optimization: ~10-20 seconds (30 particles × 50 iterations)
- Speedup vs pure Python: 50x (Numba JIT)

Subsection: Reproducibility
- Global seed: 42 (set in config.yaml)
- Deterministic execution: All RNG seeded (NumPy, Python random)
- Version control: Git commit hash recorded in results metadata
- Configuration archival: config.yaml stored with each result

Subsection: Data Management
- Results directory: optimization_results/
- Benchmarks: benchmarks/*.csv
- Logs: test_logs/test_YYYY-MM-DD.log
- Format: JSON (structured), CSV (tabular), PNG (figures)
- Size: ~50 MB total (all experiments)

Summary: "All experiments run on identical hardware/software configuration. Reproducibility ensured via seeded RNG and version-controlled configuration files. Computational cost is modest: <1 minute per controller evaluation."

Citations: cite:Numba (Lam2015), cite:PySwarms (Miranda2018)

Length: 1.5 pages
```

---

## WHAT TO DO

1. **Extract actual system specs** (10 min):
   ```bash
   python --version
   python -c "import numpy; print(numpy.__version__)"
   python -c "import sys; print(sys.platform)"
   ```
2. **Create Table 8.4** (10 min) - Software environment
3. **Format as LaTeX** (10 min)

---

## VALIDATION

- [ ] CPU/RAM specs extracted
- [ ] Python and library versions listed
- [ ] Table 8.4 with 6 software components
- [ ] Timing data provided (50 ms per sim, 10-20 s per PSO)
- [ ] Reproducibility measures described
- [ ] 1.3-1.7 pages

---

## TIME: ~45 min

## NEXT STEP: `step_07_compile_chapter.md`
