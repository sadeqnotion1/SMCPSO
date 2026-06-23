# Deprecated Monitoring Components

This directory contains deprecated monitoring components that have been superseded by canonical implementations.

## Contents

### Metrics Collectors (Deprecated Dec 19, 2025)

Three experimental metrics collector variants have been moved here:

1. **metrics_collector_threadsafe.py** - Thread-safe variant
2. **metrics_collector_deadlock_free.py** - Deadlock prevention variant  
3. **metrics_collector_fixed.py** - Production-safe variant with memory profiling

**Canonical Implementation**: `src/interfaces/monitoring/metrics_collector.py`

**Migration Guide**: See `MIGRATION.md` in this directory

**Removal Date**: January 16, 2026 (4 weeks from deprecation)

## Why Deprecated?

These files were experimental implementations created during development to explore different thread safety and memory management strategies. The canonical implementation at `src/interfaces/monitoring/metrics_collector.py` incorporates the best features from all variants and is the only version exported in the public API.

## Usage Warning

**DO NOT** import from files in this directory. They are:
- Not part of the public API
- Not actively maintained
- May be removed without notice after the removal date
- May contain bugs or incomplete features

Use the canonical implementation instead:
```python
from src.interfaces.monitoring.metrics_collector import MetricsCollector
```

## File Retention Policy

Deprecated files are retained for 4 weeks to allow time for:
1. Code review and migration
2. Discovery of any hidden dependencies
3. Emergency rollback if needed

After the removal date, these files will be permanently deleted from the repository (but preserved in git history via tags).
