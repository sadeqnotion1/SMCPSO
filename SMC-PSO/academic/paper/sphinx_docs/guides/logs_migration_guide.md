# Log Directory Migration Guide

## Overview

**Migration Date:** December 17, 2025
**Reason:** Workspace reorganization and centralized log path management

This guide explains the log directory reorganization that centralizes all logging to `.logs/` with a unified configuration system.

---

## What Changed?

### Directory Structure

**Before (Pre-Dec 17, 2025):**
```
Project Root/
├── logs/                    # Visible, hardcoded paths
│   ├── pso_*.log
│   ├── test_*.log
│   └── combined.log
├── monitoring_data/         # Visible, separate location
└── [scripts with "logs/" hardcoded]
```

**After (Dec 17, 2025):**
```
Project Root/
├── .logs/                   # Hidden, centralized
│   ├── pso/                # PSO optimization logs
│   ├── test/               # Test execution logs
│   ├── monitoring/         # Monitoring system logs
│   └── archive/            # Historical compressed logs
├── src/utils/logging/paths.py  # Single source of truth
└── [scripts using centralized config]
```

### Key Benefits

1. **Centralized Configuration:** All log paths in `src/utils/logging/paths.py`
2. **Environment Variable Override:** Set `LOG_DIR` to customize log location
3. **Cleaner Workspace:** Hidden `.logs/` directory reduces visible clutter
4. **Structured Organization:** Separate subdirectories for different log types
5. **Automatic Archival:** Old logs compressed to `.logs/archive/YYYY-MM-DD/`

---

## For Users

### Quick Start

**No changes required for basic usage!** The default configuration works out of the box.

```bash
# All these commands work as before
python simulate.py --ctrl classical_smc --run-pso
python scripts/optimization/run_pso_parallel.py --all
streamlit run streamlit_app.py
```

Logs are now automatically stored in `.logs/` instead of `logs/`.

### Finding Your Logs

**PSO Logs:**
```bash
# Old location (deprecated)
tail -f logs/pso_classical.log

# New location
tail -f .logs/pso/pso_classical.log
```

**Test Logs:**
```bash
# Old location (deprecated)
cat logs/test_validation.log

# New location
cat .logs/test/test_validation.log
```

**Monitoring Logs:**
```bash
# Old location (deprecated)
ls monitoring_data/

# New location
ls .logs/monitoring/
```

### Custom Log Directory (Advanced)

Override the default `.logs/` location with the `LOG_DIR` environment variable:

```bash
# Linux/Mac
export LOG_DIR=/var/log/dip-smc-pso
python simulate.py --ctrl adaptive_smc --run-pso

# Windows (PowerShell)
$env:LOG_DIR = "C:\Logs\dip-smc-pso"
python simulate.py --ctrl adaptive_smc --run-pso

# Windows (cmd)
set LOG_DIR=C:\Logs\dip-smc-pso
python simulate.py --ctrl adaptive_smc --run-pso
```

All scripts automatically use the overridden directory.

---

## For Developers

### Using Centralized Paths

**ALWAYS import from the centralized module:**

```python
from src.utils.logging.paths import PSO_LOG_DIR, TEST_LOG_DIR, MONITORING_LOG_DIR

# Good
log_file = PSO_LOG_DIR / f"pso_{controller}.log"

# Bad - DO NOT hardcode paths
log_file = "logs/pso_classical.log"  # WRONG
log_file = ".logs/pso/pso_classical.log"  # WRONG
```

### Available Path Constants

```python
from src.utils.logging.paths import (
    LOG_DIR,             # Base log directory (.logs/)
    PSO_LOG_DIR,         # .logs/pso/
    TEST_LOG_DIR,        # .logs/test/
    MONITORING_LOG_DIR,  # .logs/monitoring/
    ARCHIVE_DIR,         # .logs/archive/
)
```

### Migration Checklist for Custom Scripts

If you have custom scripts that hardcode log paths:

- [ ] Replace `"logs/"` with `PSO_LOG_DIR /` (or appropriate subdirectory)
- [ ] Replace `"monitoring_data/"` with `MONITORING_LOG_DIR /`
- [ ] Add import: `from src.utils.logging.paths import PSO_LOG_DIR`
- [ ] Test with `python -m py_compile your_script.py`
- [ ] Verify logs appear in `.logs/` subdirectories

### Examples

**Before:**
```python
# Old hardcoded approach
log_file = f"logs/pso_{controller}.log"
with open(log_file, 'w') as f:
    f.write(output)
```

**After:**
```python
# New centralized approach
from src.utils.logging.paths import PSO_LOG_DIR

log_file = PSO_LOG_DIR / f"pso_{controller}.log"
with open(log_file, 'w') as f:
    f.write(output)
```

---

## Breaking Changes

### Hardcoded Path Scripts

If you have custom scripts with hardcoded paths like:
- `logs/pso_*.log`
- `monitoring_data/logs/data_manager.log`
- `D:/Projects/main/logs` (absolute paths)

These will **fail** after the migration. Update them using the centralized paths module (see Developer section).

### External Tools

If you have external monitoring tools (e.g., log aggregators, dashboards) pointing to the old `logs/` directory:

1. Update them to point to `.logs/` (note the dot prefix)
2. Or set `LOG_DIR` environment variable to a known location for compatibility

---

## Archival & Retention Policy

### Automatic Archival

Old logs are automatically compressed and moved to `.logs/archive/YYYY-MM-DD/`:

**Retention Periods:**
- **Test logs:** 30 days
- **PSO logs:** 90 days
- **Monitoring logs:** System-managed (keep recent only)

**Compression Ratios:**
- PSO JSON logs: ~70% compression (357KB → 102KB)
- Test logs: ~90% compression (220KB → 21KB)
- Simulation runs: ~85% compression (compressed to tar.gz)

### Manual Archival

To manually archive old logs:

```bash
# Compress logs older than 30 days
find .logs/test/ -name "*.log" -mtime +30 -exec gzip {} \;

# Move compressed logs to archive
mkdir -p .logs/archive/$(date +%Y-%m-%d)
mv .logs/test/*.gz .logs/archive/$(date +%Y-%m-%d)/
```

---

## Troubleshooting

### "FileNotFoundError: logs/pso_classical.log"

**Cause:** Script still using hardcoded `logs/` path
**Solution:** Update script to use centralized paths:
```python
from src.utils.logging.paths import PSO_LOG_DIR
log_file = PSO_LOG_DIR / "pso_classical.log"
```

### "Can't find my old logs"

**Cause:** Logs moved from `logs/` to `.logs/`
**Solution:** Check `.logs/` directory (note the dot):
```bash
ls -la .logs/
```

### "Environment variable not working"

**Verify it's set:**
```bash
# Linux/Mac
echo $LOG_DIR

# Windows (PowerShell)
echo $env:LOG_DIR

# Windows (cmd)
echo %LOG_DIR%
```

**Ensure scripts restart after setting:**
Environment variables only affect new processes, not already-running ones.

---

## Migration Timeline

| Date | Event |
|------|-------|
| Dec 17, 2025 | Initial workspace reorganization (Phase 2) |
| Dec 17, 2025 | Centralized paths module created (Phase 4) |
| Dec 17, 2025 | 10 Python files updated with centralized paths |
| Dec 17, 2025 | Documentation migration guide created |

---

## Related Documentation

- [Workspace Organization Guide](.project/ai/config/workspace_organization.md)
- [Logging Architecture](docs/architecture/logging_architecture.md)
- [PSO Troubleshooting Manual](docs/pso_troubleshooting_maintenance_manual.md)
- [Development Guidelines](CLAUDE.md)

---

## Questions?

If you encounter issues not covered by this guide:

1. Check [GitHub Issues](https://github.com/theSadeQ/dip-smc-pso/issues)
2. Review commit history for log-related changes: `git log --grep="logs" --oneline`
3. Examine the centralized paths module: `src/utils/logging/paths.py`

---

**Last Updated:** December 17, 2025
**Version:** 1.0
**Status:** Active
