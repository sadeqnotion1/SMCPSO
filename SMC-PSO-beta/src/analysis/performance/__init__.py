#======================================================================================
#======================== src/analysis/performance/__init__.py ========================
#======================================================================================

"""Performance analysis and metrics for control systems."""

# M8-SCHED-1: benchmarks re-exports (calculate_control_metrics, StabilityMetrics)
# were dropped to decouple this package from src.benchmarks. Import them directly
# from src.benchmarks.metrics.* if needed.
from .control_analysis import ControlAnalyzer

__all__ = [
    "ControlAnalyzer",
]
