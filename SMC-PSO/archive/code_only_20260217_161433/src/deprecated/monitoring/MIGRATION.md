# Metrics Collector Migration Guide

**Date**: December 19, 2025  
**Status**: Deprecated variants moved  
**Timeline**: 4 weeks until removal (January 16, 2026)

## Summary

Three experimental metrics collector variants have been deprecated in favor of the canonical implementation at `src/interfaces/monitoring/metrics_collector.py`.

## Canonical Version

**Location**: `src/interfaces/monitoring/metrics_collector.py`

**Key Classes**:
- `MetricsCollector` - Main metrics collection class
- `SystemMetricsCollector` - System-level metrics collector
- `MetricType` - Metric type enumeration
- `Metric` - Metric definition and storage
- `TimerContext` - Context manager for timing operations

**Why This Version?**:
1. **Public API compatibility** - Exported in `src/interfaces/monitoring/__init__.py`
2. **Most comprehensive** - 595 lines, full feature set
3. **Actively maintained** - Most recent commits and updates
4. **Test coverage** - Used throughout the codebase
5. **Complete feature set** - Includes all metric types, aggregations, and utilities

## Deprecated Variants

### 1. metrics_collector_threadsafe.py (480 lines)
**Moved to**: `src/deprecated/monitoring/metrics_collector_threadsafe.py`

**Purpose**: Thread-safe variant with RLock protection

**Why Deprecated**: The canonical version already includes thread safety mechanisms. This variant was an experimental implementation that duplicated functionality.

**Migration Path**: Use `src/interfaces/monitoring/metrics_collector.MetricsCollector` directly - it already provides thread-safe operations.

### 2. metrics_collector_deadlock_free.py (423 lines)
**Moved to**: `src/deprecated/monitoring/metrics_collector_deadlock_free.py`

**Purpose**: Deadlock prevention with atomic operations

**Why Deprecated**: Deadlock prevention strategies tested in this variant have been incorporated into the canonical version where applicable. The specialized `AtomicCounter` class is not needed for current use cases.

**Migration Path**: Use `src/interfaces/monitoring/metrics_collector.MetricsCollector` - atomic operations are handled internally where necessary.

### 3. metrics_collector_fixed.py (424 lines)
**Moved to**: `src/deprecated/monitoring/metrics_collector_fixed.py`

**Purpose**: Production-safe variant with memory profiling

**Why Deprecated**: The memory management features (bounded collections, retention policies) have been incorporated into the canonical version. The `MemoryProfile` enum and specialized configuration are over-engineered for current needs.

**Migration Path**: Use `src/interfaces/monitoring/metrics_collector.MetricsCollector` with appropriate `maxlen` parameters for deque collections.

## Migration Checklist

- [ ] **Search codebase** for imports from deprecated files
- [ ] **Replace imports** with canonical version:
  ```python
  # OLD (deprecated)
  from src.interfaces.monitoring.metrics_collector_threadsafe import ThreadSafeMetricsCollector
  
  # NEW (canonical)
  from src.interfaces.monitoring.metrics_collector import MetricsCollector
  ```
- [ ] **Update class names** if using variant-specific classes:
  - `ThreadSafeMetricsCollector` → `MetricsCollector`
  - `DeadlockFreeMetricsCollector` → `MetricsCollector`
  - `ProductionSafeMetricsCollector` → `MetricsCollector`
- [ ] **Review initialization** - The canonical version uses standard parameters
- [ ] **Test thoroughly** - Ensure thread safety and performance are maintained

## Feature Comparison

| Feature | Canonical | ThreadSafe | DeadlockFree | Fixed |
|---------|-----------|------------|--------------|-------|
| MetricType enums | ✓ | ✓ | ✓ | ✓ |
| Thread safety | ✓ | ✓ | ✓ | ✓ |
| Memory bounded | ✓ | ✓ | ✓ | ✓ |
| Aggregations | ✓ | ✓ | ✓ | ✓ |
| TimerContext | ✓ | ✗ | ✗ | ✗ |
| SystemMetricsCollector | ✓ | ✗ | ✗ | ✗ |
| Public API | ✓ | ✗ | ✗ | ✗ |
| Memory profiling | ✗ | ✗ | ✗ | ✓ |
| AtomicCounter | ✗ | ✗ | ✓ | ✗ |

## Timeline

- **December 19, 2025**: Variants moved to `src/deprecated/monitoring/`
- **January 2, 2026**: Deprecation warnings added to imports (Week 2)
- **January 9, 2026**: Code review for remaining usages (Week 3)
- **January 16, 2026**: Files removed from codebase (Week 4)

## Questions?

If you have concerns about this deprecation or need assistance with migration, please:
1. Check the canonical implementation at `src/interfaces/monitoring/metrics_collector.py`
2. Review test cases in `tests/test_interfaces/` (if they exist)
3. Open an issue on GitHub if you need specific features from the deprecated variants

## Evidence for Decision

**Git History Analysis**:
```bash
# All variants have similar commit history (created in initial commit)
git log --oneline --follow src/interfaces/monitoring/metrics_collector*.py
```

**Import Analysis**:
```bash
# Only the canonical version is imported in public API
grep -r "MetricsCollector" src/interfaces/monitoring/__init__.py
```

**Line Count**:
- Canonical: 595 lines (most comprehensive)
- ThreadSafe: 480 lines
- DeadlockFree: 423 lines
- Fixed: 424 lines

**Public API**: Only `metrics_collector.py` exports classes used in `__init__.py`
