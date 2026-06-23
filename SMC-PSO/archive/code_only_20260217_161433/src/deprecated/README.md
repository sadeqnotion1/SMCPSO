# Deprecated Code Directory

**Purpose**: Temporary storage for deprecated code during migration grace periods.

**Policy**: All files in this directory are scheduled for permanent removal after a 4-week grace period.

---

## Removal Schedule

| Module/File | Deprecation Date | Removal Date | Status | Canonical Location |
|-------------|-----------------|--------------|--------|-------------------|
| **Controllers** | | | | |
| `controllers/classic_smc.py` | Dec 19, 2025 | Jan 16, 2026 | Pending | `src/controllers/smc/classical_smc.py` |
| `controllers/adaptive_smc.py` | Dec 19, 2025 | Jan 16, 2026 | Pending | `src/controllers/smc/adaptive_smc.py` |
| `controllers/sta_smc.py` | Dec 19, 2025 | Jan 16, 2026 | Pending | `src/controllers/smc/sta_smc.py` |
| `controllers/mpc_controller.py` | Dec 19, 2025 | Jan 16, 2026 | Pending | `src/controllers/mpc/mpc_controller.py` |
| `controllers/swing_up_smc.py` | Dec 19, 2025 | Jan 16, 2026 | Pending | `src/controllers/specialized/swing_up_smc.py` |
| **Interfaces** | | | | |
| `monitoring/metrics_collector_threadsafe.py` | Dec 19, 2025 | Jan 16, 2026 | Pending | `src/interfaces/monitoring/metrics_collector.py` |
| `monitoring/metrics_collector_deadlock_free.py` | Dec 19, 2025 | Jan 16, 2026 | Pending | `src/interfaces/monitoring/metrics_collector.py` |
| `monitoring/metrics_collector_fixed.py` | Dec 19, 2025 | Jan 16, 2026 | Pending | `src/interfaces/monitoring/metrics_collector.py` |
| **Fault Detection** | | | | |
| `fault_detection/fdi.py` | Dec 19, 2025 | Jan 16, 2026 | Pending | `src/analysis/fault_detection/fdi.py` |
| `fault_detection/__init__.py` | Dec 19, 2025 | Jan 16, 2026 | Pending | N/A (wrapper) |

---

## Migration Guides

### Controllers (Phase 2.1)

**Affected Files**: 5 controller compatibility shims

**Why Deprecated**: Reorganization moved controllers into domain-specific subdirectories (`smc/`, `mpc/`, `specialized/`) for better organization.

**Migration**:

```python
# OLD (deprecated)
from src.controllers.classical_smc import ClassicalSMC
from src.controllers.adaptive_smc import AdaptiveSMC
from src.controllers.sta_smc import STASMC
from src.controllers.mpc_controller import MPCController
from src.controllers.swing_up_smc import SwingUpSMC

# NEW (canonical)
from src.controllers.smc.classical_smc import ClassicalSMC
from src.controllers.smc.adaptive_smc import AdaptiveSMC
from src.controllers.smc.sta_smc import STASMC
from src.controllers.mpc.mpc_controller import MPCController
from src.controllers.specialized.swing_up_smc import SwingUpSMC
```

**Automated Migration**:
```bash
# Use sed to update imports (Unix/Linux/Mac)
find . -name "*.py" -exec sed -i 's/from src\.controllers\.classical_smc/from src.controllers.smc.classical_smc/g' {} \;

# Or use Python script (cross-platform)
python scripts/migration/update_controller_imports.py
```

**Factory Usage** (Recommended):
```python
# Factory pattern handles canonical paths automatically
from src.controllers.factory import create_controller
controller = create_controller('classical_smc', gains=[...])
```

---

### Metrics Collectors (Phase 1.2)

**Affected Files**: 3 metrics collector variants

**Why Deprecated**: Multiple implementations caused confusion. Canonical version is more comprehensive and stable.

**Migration**:

```python
# OLD (deprecated)
from src.interfaces.monitoring.metrics_collector_threadsafe import MetricsCollector
from src.interfaces.monitoring.metrics_collector_deadlock_free import MetricsCollector
from src.interfaces.monitoring.metrics_collector_fixed import MetricsCollector

# NEW (canonical)
from src.interfaces.monitoring.metrics_collector import MetricsCollector
```

**Feature Comparison**:

| Feature | Canonical | Threadsafe | Deadlock-free | Fixed |
|---------|-----------|------------|---------------|-------|
| Basic metrics | ✓ | ✓ | ✓ | ✓ |
| Thread-safe | ✓ | ✓ | ✓ | ✓ |
| Control metrics | ✓ | ✗ | ✗ | ✗ |
| Fault metrics | ✓ | ✗ | ✗ | ✗ |
| Latency tracking | ✓ | ✗ | ✓ | ✓ |
| Memory efficient | ✓ | ✗ | ✓ | ✓ |
| **Lines of code** | **595** | **480** | **423** | **424** |

**Conclusion**: Canonical version is most comprehensive. All features from deprecated versions are available.

**If You Need Thread Safety**:
```python
# Canonical version is already thread-safe
from src.interfaces.monitoring.metrics_collector import MetricsCollector
import threading

collector = MetricsCollector()

def worker():
    collector.record_metric('latency', 0.01)

threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# No race conditions, no deadlocks
```

---

### Fault Detection (Phase 2.3)

**Affected Files**: `fault_detection/` directory

**Why Deprecated**: Minimal implementation (23 lines) superseded by rich implementation in `src/analysis/fault_detection/` (5 files, 1200+ lines).

**Migration**:

```python
# OLD (deprecated)
from src.fault_detection.fdi import FaultDetector

# NEW (canonical)
from src.analysis.fault_detection.fdi import FaultDetector
```

**Feature Enhancements in Canonical Version**:
- Multiple fault detection algorithms (residual-based, observer-based, data-driven)
- Fault classification (sensor faults, actuator faults, system faults)
- Fault isolation logic
- Real-time fault detection
- Historical fault logging

**Example**:
```python
from src.analysis.fault_detection.fdi import FaultDetector

detector = FaultDetector(
    detection_threshold=0.01,
    isolation_window=50,  # Number of samples
    fault_types=['sensor', 'actuator', 'system']
)

# During simulation
for state, control in simulation_loop:
    fault_detected = detector.detect(state, control, expected_state)

    if fault_detected:
        fault_type = detector.classify_fault()
        print(f"Fault detected: {fault_type}")
```

---

## Deprecation Workflow

This directory follows the project's standard deprecation policy (see `src/ARCHITECTURE.md` for details):

### Timeline

1. **Week 0**: File moved to new canonical location (with `git mv`)
2. **Weeks 1-4**: Compatibility shim remains in old location with `DeprecationWarning`
3. **Week 4**: Shim moved to `src/deprecated/` (Dec 19, 2025)
4. **Weeks 5-8**: File remains in `src/deprecated/` with clear removal date
5. **Week 8**: Permanent removal (Jan 16, 2026)

### Current Status (Dec 19, 2025)

All files in this directory are at **Week 4** (just moved to `src/deprecated/`).

**Removal Date**: **January 16, 2026** (4 weeks from now)

### Actions Required Before Jan 16, 2026

1. **Search your codebase** for deprecated imports:
   ```bash
   grep -r "from src.controllers.classical_smc" .
   grep -r "from src.interfaces.monitoring.metrics_collector_threadsafe" .
   grep -r "from src.fault_detection.fdi" .
   ```

2. **Update imports** to canonical locations (see migration guides above)

3. **Test your code** to ensure migrations work:
   ```bash
   python -m pytest tests/ -v
   ```

4. **Update documentation** if you reference deprecated paths

---

## Permanent Removal Process (Jan 16, 2026)

**DO NOT MANUALLY DELETE FILES BEFORE Jan 16, 2026**

On the removal date, the following automated process will execute:

```bash
# 1. Verify zero usage in codebase
python scripts/validation/check_deprecated_usage.py

# 2. If clear, remove entire deprecated directory
git rm -r src/deprecated/

# 3. Commit removal
git commit -m "refactor: Remove deprecated code (Phase 1+2 cleanup, 4-week grace period expired)"

# 4. Update CHANGELOG.md
echo "### Removed\n- Deprecated controller shims (src/controllers/*.py)\n- Deprecated metrics collectors\n- Deprecated fault_detection/ directory" >> CHANGELOG.md

# 5. Push to remote
git push origin main
```

---

## Emergency Rollback

If critical code breaks due to deprecations:

### Temporary Workaround (Quick Fix)

```python
# Add temporary compatibility shim in your code
import sys
from src.controllers.smc.classical_smc import ClassicalSMC
sys.modules['src.controllers.classical_smc'] = sys.modules['src.controllers.smc.classical_smc']

# Now old imports work
from src.controllers.classical_smc import ClassicalSMC  # Works temporarily
```

### Permanent Fix (Recommended)

1. Update imports to canonical paths
2. Run tests to verify
3. Remove temporary workaround

---

## Questions?

**Q: Can I still use deprecated imports?**

A: Yes, until Jan 16, 2026. But you'll see deprecation warnings. Update to canonical paths as soon as possible.

**Q: Will my code break on Jan 16, 2026?**

A: Yes, if you're still using deprecated imports. Update before then.

**Q: How do I know if I'm using deprecated code?**

A: Run your code. If you see `DeprecationWarning` messages, you're using deprecated imports. Or run:
```bash
python -m pytest tests/ -W error::DeprecationWarning
```

**Q: Can I request an extension?**

A: No. The 4-week grace period (8 weeks total from original move) is firm. However, if you discover a critical blocker, open a GitHub issue immediately.

**Q: What if I need a deprecated feature not in canonical version?**

A: This shouldn't happen (canonical versions are supersets). But if it does, open a GitHub issue with details.

---

## Statistics

**Total Deprecated Files**: 10 Python files
**Total Lines Removed**: ~1,500 lines
**Removal Date**: January 16, 2026
**Days Until Removal**: 28 days (from Dec 19, 2025)

**Impact Assessment**:
- Zero production imports found (verified Dec 19, 2025)
- All tests passing with canonical imports
- Documentation updated to reference new paths
- Low risk of breakage

---

## References

- **Architecture**: `src/ARCHITECTURE.md` (Section: Deprecation Policy)
- **Phase 1 Report**: `.project/ai/planning/PHASE1_COMPLETION_REPORT.md`
- **Phase 2 Report**: `.project/ai/planning/PHASE2_COMPLETION_REPORT.md`
- **Import Validation**: `scripts/validation/validate_imports.py`

---

**Maintained by**: Repository maintainers
**Created**: December 19, 2025
**Review Frequency**: Weekly until removal date
**Next Review**: December 26, 2025
