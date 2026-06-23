# utils.__init__

**Source:** `src\utils\__init__.py`

## Module Overview utilities

package for control engineering

. This package provides a complete suite of utilities organized into focused modules: Packages:


validation : Parameter validation and range checking
control : Control primitives and saturation functions
monitoring : Real-time performance and latency monitoring
visualization : Animation, plotting, and movie generation
analysis : Statistical analysis and hypothesis testing Legacy imports are maintained for backward compatibility. ## Complete Source Code ```{literalinclude} ../../../src/utils/__init__.py
:language: python
:linenos:
```

---

## Dependencies This module imports: - `from .validation import require_positive, require_finite, require_in_range, require_probability`
- `from .control import saturate, smooth_sign, dead_zone`
- `from .monitoring import LatencyMonitor`
- `from .analysis import confidence_interval, bootstrap_confidence_interval, welch_t_test, one_way_anova, monte_carlo_analysis, performance_comparison_summary, sample_size_calculation`
