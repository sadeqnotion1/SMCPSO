# Migration Guide: src.optimizer → src.optimization

**Status:** DEPRECATED as of 2025-10-28
**Removal Date:** v2.0.0 (estimated Q1 2026)
**Migration Priority:** HIGH

---

## Why This Change?

The `src.optimizer/` module is a legacy compatibility layer. The project now uses the more comprehensive `src.optimization/` framework:

| Aspect | src.optimizer/ (Legacy) | src.optimization/ (Current) |
|--------|------------------------|-----------------------------|
| Files | 2 | 40+ |
| Structure | Monolithic | Modular (algorithms, analysis, results) |
| Functionality | PSO only | PSO, genetic algorithms, multi-objective |
| Maintenance | Deprecated | Active |

---

## Migration Steps

### 1. Update Imports

**OLD (Deprecated):**
```python
from src.optimizer.pso_optimizer import PSOTuner
```

**NEW (Recommended):**
```python
from src.optimization.algorithms.pso_optimizer import PSOTuner
```

### 2. Update Configuration

No configuration changes needed - the public API is **identical**:

```python
# Same API works with both imports
tuner = PSOTuner(
    num_particles=30,
    num_iterations=50,
    bounds=bounds,
    fitness_func=fitness_function,
    seed=42
)
results = tuner.optimize()
```

### 3. Run Tests

Verify your code still works:

```bash
python -m pytest tests/test_optimization/ -v
```

### 4. Update Documentation

If you have internal documentation referencing the old module:

```bash
# Find all references
grep -r "src.optimizer" docs/

# Update each reference to use new path
```

---

## What If I Don't Migrate?

**Current Behavior (v1.x):**
- ✓ Old imports still work
- ⚠️ DeprecationWarning issued on import
- ✓ No breaking changes

**Future Behavior (v2.0.0):**
- ✗ Old imports will fail with ImportError
- ✗ Code will break unless migrated

---

## Migration Examples

### Example 1: Simple PSO Optimization

**Before:**
```python
from src.optimizer.pso_optimizer import PSOTuner

def fitness(gains):
    controller = create_controller("classical_smc", gains=gains)
    return evaluate_controller(controller)

tuner = PSOTuner(num_particles=30, num_iterations=50)
best_gains = tuner.optimize()
```

**After:**
```python
from src.optimization.algorithms.pso_optimizer import PSOTuner

def fitness(gains):
    controller = create_controller("classical_smc", gains=gains)
    return evaluate_controller(controller)

tuner = PSOTuner(num_particles=30, num_iterations=50)
best_gains = tuner.optimize()
```

### Example 2: CLI Script

**Before:**
```bash
# simulate.py line 373
from src.optimizer.pso_optimizer import PSOTuner
```

**After:**
```bash
# simulate.py line 373
from src.optimization.algorithms.pso_optimizer import PSOTuner
```

### Example 3: Test File

**Before:**
```python
# tests/integration/test_issue2_pso_validation.py line 21
from src.optimizer.pso_optimizer import PSOTuner
```

**After:**
```python
# tests/integration/test_issue2_pso_validation.py line 21
from src.optimization.algorithms.pso_optimizer import PSOTuner
```

---

## Deprecation Timeline

| Date | Version | Status |
|------|---------|--------|
| 2025-10-28 | v1.x | Deprecation warning added |
| TBD | v2.0.0 | Module removed, imports will fail |

---

## Getting Help

**Have questions?**
1. Check examples: `examples/optimization/`
2. Read documentation: `docs/optimization/`
3. Review complete API: `docs/api/index.md`
4. Report issues: GitHub Issues

**Need a code review?**
- Before: `from src.optimizer.pso_optimizer import PSOTuner`
- After: `from src.optimization.algorithms.pso_optimizer import PSOTuner`

---

## FAQ

**Q: Will my old code break immediately?**
A: No, v1.x still supports old imports with deprecation warnings. Breakage happens in v2.0.0.

**Q: Is the API identical?**
A: Yes, `PSOTuner` has the same public API in both locations.

**Q: Should I update now or later?**
A: Update now to remove deprecation warnings and prepare for v2.0.0.

**Q: What about other modules in src.optimizer?**
A: Only `PSOTuner` is actively used. All functionality is available in `src.optimization`.
