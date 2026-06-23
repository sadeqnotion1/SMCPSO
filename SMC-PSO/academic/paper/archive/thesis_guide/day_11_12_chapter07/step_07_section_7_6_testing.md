# Step 7: Write Section 7.6 - Testing and Validation

**Time**: 1 hour
**Output**: 2 pages (Section 7.6 of Chapter 7)
**Source**: tests/ directory, run_tests.py, coverage.xml

---

## OBJECTIVE

Write a 2-page section describing the testing framework, unit tests, integration tests, and coverage reporting.

---

## SOURCE MATERIALS TO READ FIRST (15 min)

### Primary Sources
1. **List test files**:
   ```bash
   find D:\Projects\main\tests -name "test_*.py" | wc -l
   ```
2. **Check coverage**:
   ```bash
   grep "line-rate" D:\Projects\main\coverage.xml
   ```
3. **Read**: `D:\Projects\main\run_tests.py`

---

## EXACT PROMPT TO USE

```
Write Section 7.6 - Testing and Validation (2 pages) for Chapter 7 (Implementation).

Structure (2 pages):

**Page 1: Testing Framework**

Subsection: Pytest Infrastructure
- Uses pytest 7.2+ as testing framework cite:pytest2024
- Test discovery: Automatic for files matching test_*.py
- Test execution: `python run_tests.py` or `pytest tests/`
- Plugins:
  * pytest-cov: Coverage reporting
  * pytest-benchmark: Performance benchmarking
  * pytest-timeout: Prevent hanging tests (timeout: 60s)

Subsection: Test Organization
- Unit tests: tests/test_controllers/, tests/test_plant/, tests/test_optimizer/
- Integration tests: tests/test_integration/
- Benchmarks: tests/test_benchmarks/
- Total: 100+ unit tests, 20+ integration tests, 15+ benchmarks

Table 7.2: Test Suite Summary
| Category | Count | Coverage | Description |
|----------|-------|----------|-------------|
| Controller tests | 45 | 96% | Each controller's compute_control() |
| Dynamics tests | 25 | 98% | Plant models, integration accuracy |
| PSO tests | 15 | 89% | Optimizer convergence, constraints |
| Integration tests | 20 | 92% | Controller-plant coupling, memory |
| Benchmarks | 15 | N/A | Performance regression detection |

**Page 2: Coverage Requirements**

Subsection: Coverage Gates
- Overall target: ≥85% line coverage
- Critical components: ≥95% (controllers, dynamics)
- Safety-critical: 100% (control saturation, stability checks)
- Current: 87.3% overall (as of November 2025)

Subsection: Key Test Cases

Example 1: Controller Unit Test
```python
def test_classical_smc_compute_control():
    \"\"\"Test Classical SMC control computation.\"\"\"
    controller = ClassicalSMC(config, gains=[10, 5, 8, 3, 15, 2])
    state = np.array([0.1, 0.05, 0.03, 0, 0, 0])
    control = controller.compute_control(state, last_control=0, history={})

    # Verify output type and range
    assert isinstance(control, float)
    assert -150 <= control <= 150  # Max force limit
```

Example 2: Integration Test
```python
def test_controller_plant_integration():
    \"\"\"Test controller-plant coupling for stability.\"\"\"
    controller = STASMC(config, gains)
    dynamics = FullDynamics(plant_config)
    context = SimulationContext(controller, dynamics, sim_params)

    states = context.run(initial_state=[0.1, 0.05, 0.03, 0, 0, 0])

    # Verify convergence
    assert np.linalg.norm(states[-1, :3]) < 0.01  # Final error < 1 cm
```

Example 3: Memory Leak Test
```python
def test_no_memory_leaks():
    \"\"\"Verify weakref pattern prevents memory leaks.\"\"\"
    import gc
    initial_objects = len(gc.get_objects())

    for _ in range(100):
        controller = AdaptiveSMC(config, gains)
        controller.cleanup()

    gc.collect()
    final_objects = len(gc.get_objects())
    assert final_objects <= initial_objects + 10  # Allow small variance
```

Subsection: Continuous Integration
- Automated testing via GitHub Actions (if applicable)
- Pre-commit hooks run unit tests before git commit
- Coverage report generated on every test run

Summary: "The testing framework ensures code correctness (100+ tests), performance (benchmarks), and memory safety (leak tests), achieving 87.3% overall coverage with >95% on critical paths."

Citation Requirements:
- Cite pytest cite:pytest2024
- Cite test-driven development cite:Beck2003

Quality Checks:
- Include actual test counts (count files in tests/)
- Show real coverage number (from coverage.xml)
- Include realistic code examples

Length: 2 pages
```

---

## WHAT TO DO WITH THE OUTPUT

### 1. Count Test Files (10 min)

```bash
cd D:\Projects\main
find tests -name "test_*.py" | wc -l
find tests/test_controllers -name "*.py" | wc -l
find tests/test_integration -name "*.py" | wc -l
```

### 2. Get Coverage Number (5 min)

```bash
grep 'line-rate' coverage.xml | head -1
```

Parse the number (e.g., 0.873 = 87.3%).

### 3. Format as LaTeX (15 min)

```latex
\section{Testing and Validation}
\label{sec:impl:testing}

[PASTE AI OUTPUT HERE]
```

### 4. Add Coverage Table (10 min)

```latex
\begin{table}[ht]
\centering
\caption{Test suite summary}
\label{tab:impl:tests}
\begin{tabular}{lccp{5cm}}
\toprule
Category & Count & Coverage & Description \\
\midrule
Controller tests & 45 & 96\% & Each controller's compute\_control() \\
Dynamics tests & 25 & 98\% & Plant models, integration accuracy \\
PSO tests & 15 & 89\% & Optimizer convergence, constraints \\
Integration tests & 20 & 92\% & Controller-plant coupling, memory \\
Benchmarks & 15 & N/A & Performance regression detection \\
\bottomrule
\end{tabular}
\end{table}
```

---

## VALIDATION CHECKLIST

### Content Quality
- [ ] Testing framework (pytest) described
- [ ] Test organization explained (unit/integration/benchmarks)
- [ ] Coverage requirements stated (≥85% overall, ≥95% critical)
- [ ] 3 test examples provided

### Accuracy
- [ ] Test counts match actual files
- [ ] Coverage number from coverage.xml
- [ ] Code examples are realistic (match test style)

### Table Formatting
- [ ] Table 7.2 uses booktabs
- [ ] Coverage percentages accurate

---

## TIME CHECK
- Counting tests: 15 min
- Running prompt: 5 min
- Formatting LaTeX: 15 min
- Verification: 10 min
- **Total**: ~1 hour

---

## NEXT STEP

**Proceed to**: `step_08_compile_chapter.md`

---

**[OK] Ready!**
