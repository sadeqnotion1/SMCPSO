#==========================================================================================\\\
#======================= src/utils/coverage/monitoring.py =============================\\\
#==========================================================================================\\\

"""Real-time coverage monitoring and alerting system for GitHub Issue #9.

This module provides advanced coverage monitoring with trend analysis,
automated alerting, and integration with the CLAUDE.md quality standards.
"""

import time
import json
import sqlite3
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from pathlib import Path
import numpy as np
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CoverageMetrics:
    """Coverage metrics data structure with mathematical validation."""
    timestamp: float
    overall_coverage: float
    critical_coverage: float
    safety_coverage: float
    branch_coverage: float
    test_count: int
    execution_time: float
    lines_total: int
    lines_covered: int

    def __post_init__(self):
        """Validate coverage metrics after initialization."""
        # Ensure coverage percentages are in valid range [0, 100]
        for attr in ['overall_coverage', 'critical_coverage', 'safety_coverage', 'branch_coverage']:
            value = getattr(self, attr)
            if not (0 <= value <= 100):
                raise ValueError(f"{attr} must be between 0 and 100, got {value}")

        # Ensure line counts are non-negative
        if self.lines_total < 0 or self.lines_covered < 0:
            raise ValueError("Line counts must be non-negative")

        # Ensure covered lines don't exceed total lines
        if self.lines_covered > self.lines_total:
            raise ValueError("Covered lines cannot exceed total lines")

class CoverageMonitor:
    """Real-time coverage monitoring with scientific trend analysis.

    Implements mathematical analysis of coverage trends with automated
    alerting for threshold violations and quality gate enforcement.
    """

    # Quality gate thresholds from CLAUDE.md standards
    QUALITY_THRESHOLDS = {
        'overall': 85.0,
        'critical': 95.0,
        'safety': 100.0,
        'branch': 80.0
    }

    def __init__(self, db_path: Path = Path("coverage_monitoring.db")):
        """Initialize coverage monitor with persistent storage.

        Args:
            db_path: Path to SQLite database for metrics storage
        """
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for coverage metrics storage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS coverage_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    overall_coverage REAL NOT NULL,
                    critical_coverage REAL NOT NULL,
                    safety_coverage REAL NOT NULL,
                    branch_coverage REAL NOT NULL,
                    test_count INTEGER NOT NULL,
                    execution_time REAL NOT NULL,
                    lines_total INTEGER NOT NULL,
                    lines_covered INTEGER NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON coverage_metrics(timestamp)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at
                ON coverage_metrics(created_at)
            """)

    def record_coverage_run(self, coverage_data: Dict) -> CoverageMetrics:
        """Record coverage metrics from test run with validation.

        Args:
            coverage_data: Dictionary containing coverage metrics

        Returns:
            CoverageMetrics object with validated data

        Raises:
            ValueError: If coverage data is invalid
        """
        try:
            metrics = CoverageMetrics(
                timestamp=time.time(),
                overall_coverage=float(coverage_data.get('overall', 0.0)),
                critical_coverage=float(coverage_data.get('critical', 0.0)),
                safety_coverage=float(coverage_data.get('safety', 0.0)),
                branch_coverage=float(coverage_data.get('branch', 0.0)),
                test_count=int(coverage_data.get('test_count', 0)),
                execution_time=float(coverage_data.get('execution_time', 0.0)),
                lines_total=int(coverage_data.get('lines_total', 0)),
                lines_covered=int(coverage_data.get('lines_covered', 0))
            )

            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO coverage_metrics
                    (timestamp, overall_coverage, critical_coverage, safety_coverage,
                     branch_coverage, test_count, execution_time, lines_total, lines_covered)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.timestamp, metrics.overall_coverage, metrics.critical_coverage,
                    metrics.safety_coverage, metrics.branch_coverage, metrics.test_count,
                    metrics.execution_time, metrics.lines_total, metrics.lines_covered
                ))

            logger.info(f"Recorded coverage metrics: {metrics.overall_coverage:.1f}% overall")
            return metrics

        except (ValueError, TypeError) as e:
            logger.error(f"Invalid coverage data: {e}")
            raise ValueError(f"Failed to record coverage metrics: {e}")

    def get_recent_metrics(self, window_size: int = 10) -> List[CoverageMetrics]:
        """Retrieve recent coverage metrics from database.

        Args:
            window_size: Number of recent metrics to retrieve

        Returns:
            List of recent CoverageMetrics objects
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, overall_coverage, critical_coverage, safety_coverage,
                       branch_coverage, test_count, execution_time, lines_total, lines_covered
                FROM coverage_metrics
                ORDER BY timestamp DESC
                LIMIT ?
            """, (window_size,))

            metrics = []
            for row in cursor.fetchall():
                metrics.append(CoverageMetrics(*row))

            return list(reversed(metrics))  # Return in chronological order

    def analyze_coverage_trends(self, window_size: int = 10) -> Dict:
        """Analyze coverage trends using mathematical regression analysis.

        Args:
            window_size: Number of recent metrics for trend analysis

        Returns:
            Dictionary containing trend analysis results
        """
        metrics = self.get_recent_metrics(window_size)

        if len(metrics) < 3:
            return {
                "trend_status": "insufficient_data",
                "message": f"Need at least 3 data points for trend analysis, have {len(metrics)}"
            }

        # Extract time series data
        timestamps = np.array([m.timestamp for m in metrics])
        overall_coverage = np.array([m.overall_coverage for m in metrics])
        critical_coverage = np.array([m.critical_coverage for m in metrics])
        safety_coverage = np.array([m.safety_coverage for m in metrics])

        # Normalize timestamps for regression analysis
        time_normalized = (timestamps - timestamps[0]) / (timestamps[-1] - timestamps[0]) if len(timestamps) > 1 else np.array([0])

        # Calculate linear regression slopes
        def calculate_slope(x: np.ndarray, y: np.ndarray) -> float:
            """Calculate linear regression slope using least squares method."""
            if len(x) < 2 or len(y) < 2:
                return 0.0

            len(x)
            x_mean = np.mean(x)
            y_mean = np.mean(y)

            numerator = np.sum((x - x_mean) * (y - y_mean))
            denominator = np.sum((x - x_mean) ** 2)

            return numerator / denominator if denominator != 0 else 0.0

        overall_slope = calculate_slope(time_normalized, overall_coverage)
        critical_slope = calculate_slope(time_normalized, critical_coverage)
        safety_slope = calculate_slope(time_normalized, safety_coverage)

        # Calculate trend classifications
        def classify_trend(slope: float, threshold: float = 0.5) -> str:
            """Classify trend based on slope magnitude."""
            if slope > threshold:
                return "improving"
            elif slope < -threshold:
                return "declining"
            else:
                return "stable"

        # Calculate coverage velocity (percentage points per day)
        time_span_days = (timestamps[-1] - timestamps[0]) / 86400  # Convert to days
        velocity_overall = overall_slope / max(time_span_days, 1)
        velocity_critical = critical_slope / max(time_span_days, 1)

        # Statistical analysis
        overall_variance = np.var(overall_coverage)
        overall_std = np.std(overall_coverage)

        return {
            "trend_status": "analyzed",
            "window_size": len(metrics),
            "time_span_days": time_span_days,
            "trends": {
                "overall": {
                    "classification": classify_trend(overall_slope),
                    "slope": overall_slope,
                    "velocity_per_day": velocity_overall,
                    "current": overall_coverage[-1],
                    "variance": overall_variance,
                    "std_dev": overall_std
                },
                "critical": {
                    "classification": classify_trend(critical_slope),
                    "slope": critical_slope,
                    "velocity_per_day": velocity_critical,
                    "current": critical_coverage[-1]
                },
                "safety": {
                    "classification": classify_trend(safety_slope),
                    "slope": safety_slope,
                    "current": safety_coverage[-1]
                }
            },
            "latest_metrics": asdict(metrics[-1]),
            "recommendation": self._generate_trend_recommendation(overall_slope, velocity_overall)
        }

    def _generate_trend_recommendation(self, slope: float, velocity: float) -> str:
        """Generate actionable recommendations based on trend analysis."""
        if slope > 1.0:
            return "Excellent progress! Maintain current improvement trajectory."
        elif slope > 0.1:
            return "Good improvement trend. Continue systematic coverage enhancement."
        elif slope > -0.1:
            return "Stable coverage. Consider targeted improvements for quality gates."
        else:
            return "Declining trend detected. Immediate action required to prevent regression."

    def check_quality_gates(self, latest_metrics: Optional[CoverageMetrics] = None) -> Dict:
        """Check current coverage against quality gate thresholds.

        Args:
            latest_metrics: Optional metrics to check, uses most recent if None

        Returns:
            Dictionary containing quality gate validation results
        """
        if latest_metrics is None:
            recent_metrics = self.get_recent_metrics(1)
            if not recent_metrics:
                return {"status": "no_data", "gates": {}}
            latest_metrics = recent_metrics[0]

        gates = {
            "overall_system": {
                "current": latest_metrics.overall_coverage,
                "threshold": self.QUALITY_THRESHOLDS['overall'],
                "passed": latest_metrics.overall_coverage >= self.QUALITY_THRESHOLDS['overall'],
                "gap": self.QUALITY_THRESHOLDS['overall'] - latest_metrics.overall_coverage
            },
            "critical_components": {
                "current": latest_metrics.critical_coverage,
                "threshold": self.QUALITY_THRESHOLDS['critical'],
                "passed": latest_metrics.critical_coverage >= self.QUALITY_THRESHOLDS['critical'],
                "gap": self.QUALITY_THRESHOLDS['critical'] - latest_metrics.critical_coverage
            },
            "safety_critical": {
                "current": latest_metrics.safety_coverage,
                "threshold": self.QUALITY_THRESHOLDS['safety'],
                "passed": latest_metrics.safety_coverage >= self.QUALITY_THRESHOLDS['safety'],
                "gap": self.QUALITY_THRESHOLDS['safety'] - latest_metrics.safety_coverage
            },
            "branch_coverage": {
                "current": latest_metrics.branch_coverage,
                "threshold": self.QUALITY_THRESHOLDS['branch'],
                "passed": latest_metrics.branch_coverage >= self.QUALITY_THRESHOLDS['branch'],
                "gap": self.QUALITY_THRESHOLDS['branch'] - latest_metrics.branch_coverage
            }
        }

        failed_gates = [name for name, gate in gates.items() if not gate['passed']]
        all_passed = len(failed_gates) == 0

        return {
            "status": "passed" if all_passed else "failed",
            "gates": gates,
            "failed_gates": failed_gates,
            "production_ready": all_passed,
            "timestamp": latest_metrics.timestamp
        }

    def generate_coverage_alert(self, alert_level: str = "warning") -> str:
        """Generate coverage alert with detailed analysis.

        Args:
            alert_level: Alert severity level ('info', 'warning', 'critical')

        Returns:
            Formatted alert message
        """
        gate_results = self.check_quality_gates()
        trend_analysis = self.analyze_coverage_trends()

        if gate_results["status"] == "no_data":
            return "⚠️ No coverage data available for alert generation"

        alert_icon = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🚨"
        }.get(alert_level, "⚠️")

        alert = f"{alert_icon} COVERAGE MONITORING ALERT\n"
        alert += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        alert += "**Repository**: https://github.com/theSadeQ/dip-smc-pso.git\n"
        alert += "**Issue**: GitHub Issue #9 - Coverage Analysis Framework\n\n"

        # Quality gate status
        if gate_results["failed_gates"]:
            alert += f"❌ **QUALITY GATE VIOLATIONS**: {len(gate_results['failed_gates'])} gates failing\n"
            for gate_name in gate_results["failed_gates"]:
                gate = gate_results["gates"][gate_name]
                alert += f"   - {gate_name}: {gate['current']:.1f}% (gap: {gate['gap']:+.1f}%)\n"
        else:
            alert += "✅ **ALL QUALITY GATES PASSED**\n"

        # Current metrics summary
        alert += "\n📊 **CURRENT COVERAGE STATUS**:\n"
        for gate_name, gate in gate_results["gates"].items():
            status_icon = "✅" if gate['passed'] else "❌"
            alert += f"   - {gate_name.replace('_', ' ').title()}: {gate['current']:.1f}% {status_icon}\n"

        # Trend analysis
        if trend_analysis["trend_status"] == "analyzed":
            trends = trend_analysis["trends"]
            alert += f"\n📈 **TREND ANALYSIS** ({trend_analysis['window_size']} samples):\n"
            alert += f"   - Overall: {trends['overall']['classification']} ({trends['overall']['velocity_per_day']:+.2f}%/day)\n"
            alert += f"   - Critical: {trends['critical']['classification']}\n"
            alert += f"   - Safety: {trends['safety']['classification']}\n"
            alert += f"\n💡 **Recommendation**: {trend_analysis['recommendation']}\n"

        # Production readiness
        alert += f"\n🚀 **PRODUCTION STATUS**: {'✅ READY' if gate_results['production_ready'] else '❌ BLOCKED'}\n"

        return alert

    def export_metrics_json(self, output_path: Path, days: int = 30) -> None:
        """Export coverage metrics to JSON for external analysis.

        Args:
            output_path: Path to output JSON file
            days: Number of days of history to export
        """
        cutoff_timestamp = time.time() - (days * 86400)  # Convert days to seconds

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, overall_coverage, critical_coverage, safety_coverage,
                       branch_coverage, test_count, execution_time, lines_total, lines_covered,
                       created_at
                FROM coverage_metrics
                WHERE timestamp > ?
                ORDER BY timestamp ASC
            """, (cutoff_timestamp,))

            metrics_data = []
            for row in cursor.fetchall():
                metrics_data.append({
                    "timestamp": row[0],
                    "overall_coverage": row[1],
                    "critical_coverage": row[2],
                    "safety_coverage": row[3],
                    "branch_coverage": row[4],
                    "test_count": row[5],
                    "execution_time": row[6],
                    "lines_total": row[7],
                    "lines_covered": row[8],
                    "created_at": row[9]
                })

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "repository": "https://github.com/theSadeQ/dip-smc-pso.git",
            "issue": "GitHub Issue #9",
            "days_exported": days,
            "total_records": len(metrics_data),
            "quality_thresholds": self.QUALITY_THRESHOLDS,
            "metrics": metrics_data
        }

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Exported {len(metrics_data)} coverage records to {output_path}")

# Convenience functions for integration
def record_pytest_coverage(coverage_xml_path: Path, monitor: Optional[CoverageMonitor] = None) -> CoverageMetrics:
    """Record coverage metrics from pytest-cov XML output.

    Args:
        coverage_xml_path: Path to coverage.xml file
        monitor: Optional CoverageMonitor instance

    Returns:
        Recorded CoverageMetrics
    """
    if monitor is None:
        monitor = CoverageMonitor()

    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(coverage_xml_path)
        root = tree.getroot()

        coverage_data = {
            'overall': float(root.get('line-rate', 0)) * 100,
            'lines_total': int(root.get('lines-valid', 0)),
            'lines_covered': int(root.get('lines-covered', 0)),
            'branch': 0.0,  # Would need additional parsing for branch coverage
            'critical': 0.0,  # Would need component-specific analysis
            'safety': 0.0,  # Would need component-specific analysis
            'test_count': 0,  # Would need test result parsing
            'execution_time': 0.0  # Would need test timing data
        }

        return monitor.record_coverage_run(coverage_data)

    except Exception as e:
        logger.error(f"Failed to record pytest coverage: {e}")
        raise

if __name__ == "__main__":
    # Example usage for testing
    monitor = CoverageMonitor()

    # Simulate coverage data recording
    test_data = {
        'overall': 75.5,
        'critical': 88.2,
        'safety': 95.0,
        'branch': 70.3,
        'test_count': 150,
        'execution_time': 45.2,
        'lines_total': 17354,
        'lines_covered': 13100
    }

    metrics = monitor.record_coverage_run(test_data)
    print(f"Recorded metrics: {metrics}")

    # Generate alert
    alert = monitor.generate_coverage_alert("warning")
    print(f"\nAlert:\n{alert}")

    # Export metrics
    monitor.export_metrics_json(Path("coverage_monitoring_export.json"), days=7)
    print("Exported coverage monitoring data")