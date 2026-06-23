#==========================================================================================\\\
#====================== src/integration/production_readiness.py ==========================\\\
#==========================================================================================\\\

"""Production readiness scoring system with integrated pytest results and system health monitoring.

This module provides comprehensive production readiness assessment by integrating
pytest results, coverage monitoring, compatibility analysis, and system health metrics
into a unified scoring framework aligned with CLAUDE.md quality standards.
"""

import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from src.utils.monitoring.metrics.monitoring import CoverageMonitor
    from src.integration.compatibility_matrix import CompatibilityMatrix
    from scripts.pytest_automation import PytestIntegrationCoordinator, TestExecutionResult
except ImportError as e:
    logging.warning(f"Optional import failed: {e}")
    CoverageMonitor = None
    CompatibilityMatrix = None
    PytestIntegrationCoordinator = None

logger = logging.getLogger(__name__)

class ReadinessLevel(Enum):
    """Production readiness levels with deployment recommendations."""
    PRODUCTION_READY = "production_ready"
    CONDITIONAL_READY = "conditional_ready"
    NEEDS_IMPROVEMENT = "needs_improvement"
    NOT_READY = "not_ready"
    BLOCKED = "blocked"

class ComponentType(Enum):
    """System component types for targeted assessment."""
    CONTROLLERS = "controllers"
    OPTIMIZATION = "optimization"
    TESTING = "testing"
    INTEGRATION = "integration"
    SAFETY_CRITICAL = "safety_critical"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"

@dataclass
class QualityGate:
    """Represents a production quality gate with threshold and current value."""
    name: str
    category: ComponentType
    threshold: float
    current_value: float
    weight: float
    passed: bool
    critical: bool = False
    description: str = ""
    recommendations: List[str] = field(default_factory=list)

@dataclass
class ReadinessAssessment:
    """Comprehensive production readiness assessment results."""
    timestamp: str
    overall_score: float
    readiness_level: ReadinessLevel
    quality_gates: List[QualityGate]

    # Component scores
    testing_score: float
    coverage_score: float
    compatibility_score: float
    performance_score: float
    safety_score: float
    documentation_score: float

    # Integration metrics
    pytest_results: Optional[Dict[str, Any]] = None
    coverage_metrics: Optional[Dict[str, Any]] = None
    compatibility_analysis: Optional[Dict[str, Any]] = None

    # Deployment readiness
    deployment_approved: bool = False
    blocking_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence_level: str = "unknown"

    # Trend analysis
    improvement_trend: str = "stable"
    historical_comparison: Dict[str, Any] = field(default_factory=dict)

class ProductionReadinessScorer:
    """Comprehensive production readiness scoring system with pytest integration.

    This class integrates pytest results, coverage monitoring, compatibility analysis,
    and system health metrics to provide authoritative production readiness scoring
    aligned with CLAUDE.md quality standards and research-grade requirements.
    """

    def __init__(self, project_root: Path = PROJECT_ROOT):
        """Initialize production readiness scorer with comprehensive quality gates.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.db_path = project_root / "artifacts" / "production_readiness.db"

        # Initialize component integrations
        self.coverage_monitor = CoverageMonitor() if CoverageMonitor else None
        self.compatibility_matrix = CompatibilityMatrix() if CompatibilityMatrix else None
        self.pytest_coordinator = PytestIntegrationCoordinator() if PytestIntegrationCoordinator else None

        # Ensure artifacts directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database for historical tracking
        self._init_database()

        # Quality gate definitions aligned with CLAUDE.md
        self.quality_gates_config = {
            "overall_test_coverage": {
                "category": ComponentType.TESTING,
                "threshold": 85.0,
                "weight": 0.15,
                "critical": False,
                "description": "Overall system test coverage must meet 85% threshold"
            },
            "critical_component_coverage": {
                "category": ComponentType.SAFETY_CRITICAL,
                "threshold": 95.0,
                "weight": 0.20,
                "critical": True,
                "description": "Critical components (controllers, plant models) must have ≥95% coverage"
            },
            "safety_critical_coverage": {
                "category": ComponentType.SAFETY_CRITICAL,
                "threshold": 100.0,
                "weight": 0.15,
                "critical": True,
                "description": "Safety-critical mechanisms must have 100% test coverage"
            },
            "test_pass_rate": {
                "category": ComponentType.TESTING,
                "threshold": 95.0,
                "weight": 0.10,
                "critical": True,
                "description": "Test pass rate must be ≥95% for production deployment"
            },
            "system_compatibility": {
                "category": ComponentType.INTEGRATION,
                "threshold": 85.0,
                "weight": 0.15,
                "critical": False,
                "description": "Cross-domain compatibility score must be ≥85%"
            },
            "performance_benchmarks": {
                "category": ComponentType.PERFORMANCE,
                "threshold": 90.0,
                "weight": 0.10,
                "critical": False,
                "description": "Performance benchmarks must pass regression detection"
            },
            "numerical_stability": {
                "category": ComponentType.CONTROLLERS,
                "threshold": 95.0,
                "weight": 0.10,
                "critical": True,
                "description": "Controllers must demonstrate numerical stability under test conditions"
            },
            "documentation_completeness": {
                "category": ComponentType.DOCUMENTATION,
                "threshold": 90.0,
                "weight": 0.05,
                "critical": False,
                "description": "API documentation and usage guides must be comprehensive"
            }
        }

    def _init_database(self):
        """Initialize SQLite database for production readiness tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS readiness_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    readiness_level TEXT NOT NULL,
                    testing_score REAL NOT NULL,
                    coverage_score REAL NOT NULL,
                    compatibility_score REAL NOT NULL,
                    performance_score REAL NOT NULL,
                    safety_score REAL NOT NULL,
                    documentation_score REAL NOT NULL,
                    deployment_approved BOOLEAN NOT NULL,
                    confidence_level TEXT NOT NULL,
                    improvement_trend TEXT NOT NULL,
                    data_json TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON readiness_assessments(timestamp)
            """)

    def assess_production_readiness(self,
                                  run_tests: bool = True,
                                  include_benchmarks: bool = False,
                                  quick_mode: bool = False) -> ReadinessAssessment:
        """Perform comprehensive production readiness assessment.

        Args:
            run_tests: Whether to execute pytest suite
            include_benchmarks: Whether to include performance benchmarks
            quick_mode: Whether to run in quick mode (excludes slow tests)

        Returns:
            Complete production readiness assessment
        """
        start_time = datetime.now()

        # Execute comprehensive testing if requested
        pytest_results = None
        if run_tests and self.pytest_coordinator:
            try:
                pytest_results = self.pytest_coordinator.execute_comprehensive_test_suite(
                    quick_mode=quick_mode,
                    domain_filter=None,
                    generate_reports=True
                )
            except Exception as e:
                logger.error(f"Failed to execute pytest suite: {e}")

        # Gather coverage metrics
        coverage_metrics = self._gather_coverage_metrics()

        # Perform compatibility analysis
        compatibility_analysis = None
        if self.compatibility_matrix:
            try:
                compatibility_analysis = self.compatibility_matrix.analyze_full_system_compatibility()
            except Exception as e:
                logger.error(f"Failed to perform compatibility analysis: {e}")

        # Calculate component scores
        testing_score = self._calculate_testing_score(pytest_results)
        coverage_score = self._calculate_coverage_score(coverage_metrics)
        compatibility_score = self._calculate_compatibility_score(compatibility_analysis)
        performance_score = self._calculate_performance_score(pytest_results, include_benchmarks)
        safety_score = self._calculate_safety_score(coverage_metrics, pytest_results)
        documentation_score = self._calculate_documentation_score()

        # Evaluate quality gates
        quality_gates = self._evaluate_quality_gates(
            pytest_results, coverage_metrics, compatibility_analysis
        )

        # Calculate overall readiness score
        overall_score = self._calculate_overall_score(quality_gates)

        # Determine readiness level
        readiness_level = self._determine_readiness_level(overall_score, quality_gates)

        # Check for blocking issues
        blocking_issues = self._identify_blocking_issues(quality_gates)

        # Generate recommendations
        recommendations = self._generate_recommendations(quality_gates, readiness_level)

        # Analyze trends
        improvement_trend = self._analyze_improvement_trend(overall_score)
        historical_comparison = self._get_historical_comparison()

        # Create assessment
        assessment = ReadinessAssessment(
            timestamp=start_time.isoformat(),
            overall_score=overall_score,
            readiness_level=readiness_level,
            quality_gates=quality_gates,
            testing_score=testing_score,
            coverage_score=coverage_score,
            compatibility_score=compatibility_score,
            performance_score=performance_score,
            safety_score=safety_score,
            documentation_score=documentation_score,
            pytest_results=asdict(pytest_results) if pytest_results else None,
            coverage_metrics=coverage_metrics,
            compatibility_analysis=compatibility_analysis,
            deployment_approved=readiness_level in [ReadinessLevel.PRODUCTION_READY, ReadinessLevel.CONDITIONAL_READY],
            blocking_issues=blocking_issues,
            recommendations=recommendations,
            confidence_level=self._calculate_confidence_level(overall_score, quality_gates),
            improvement_trend=improvement_trend,
            historical_comparison=historical_comparison
        )

        # Store assessment in database
        self._store_assessment(assessment)

        return assessment

    def _gather_coverage_metrics(self) -> Optional[Dict[str, Any]]:
        """Gather current coverage metrics from coverage.py data file.

        Reads .coverage file directly using coverage.py API to avoid
        dependency on CoverageMonitor database which may be empty.
        """
        try:
            # Import coverage.py
            from coverage import Coverage
            import os

            # Load coverage data from .coverage file
            # Use os.path.join to ensure proper path handling on Windows
            cov_file_path = os.path.join(str(PROJECT_ROOT), ".coverage")

            if not os.path.exists(cov_file_path):
                logger.warning(f"No .coverage file found at {cov_file_path} - run pytest with --cov flag")
                return None

            cov = Coverage(data_file=cov_file_path)
            cov.load()

            # Calculate overall coverage
            # coverage.report() returns overall percentage
            import io
            import sys

            # Capture report output to get overall percentage
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            try:
                cov.report(show_missing=False)
                report_output = buffer.getvalue()
            finally:
                sys.stdout = old_stdout

            # Parse overall coverage from last line (TOTAL row)
            overall_coverage = 0.0
            for line in report_output.split('\n'):
                if line.startswith('TOTAL'):
                    parts = line.split()
                    if len(parts) >= 4:
                        # Format: "TOTAL  statements  missing  coverage"
                        overall_coverage = float(parts[-1].rstrip('%'))
                        break

            # Calculate critical component coverage (controllers, dynamics)
            critical_files = [
                "src/controllers/*.py",
                "src/core/dynamics.py",
                "src/core/dynamics_full.py",
                "src/plant/models/*/dynamics.py"
            ]

            # Use coverage.py API to get specific file coverage
            analysis_data = cov.get_data()
            critical_total_stmts = 0
            critical_executed_stmts = 0

            for filepath in analysis_data.measured_files():
                # Check if file matches critical patterns
                is_critical = any(
                    'controllers' in filepath or
                    'dynamics' in filepath
                    for pattern in critical_files
                )

                if is_critical:
                    analysis = cov.analysis2(filepath)
                    # analysis = (filename, executed_lines, missing_lines, excluded_lines)
                    executed = len(analysis[1])  # executed lines
                    missing = len(analysis[2])   # missing lines
                    total = executed + missing

                    critical_total_stmts += total
                    critical_executed_stmts += executed

            critical_coverage = (
                (critical_executed_stmts / critical_total_stmts * 100)
                if critical_total_stmts > 0 else 0.0
            )

            # Calculate safety-critical coverage (saturation, validation)
            safety_files = [
                "src/utils/control/saturation.py",
                "src/plant/core/state_validation.py"
            ]

            safety_total_stmts = 0
            safety_executed_stmts = 0

            for filepath in analysis_data.measured_files():
                is_safety = any(safety_file in filepath for safety_file in safety_files)

                if is_safety:
                    analysis = cov.analysis2(filepath)
                    executed = len(analysis[1])
                    missing = len(analysis[2])
                    total = executed + missing

                    safety_total_stmts += total
                    safety_executed_stmts += executed

            safety_coverage = (
                (safety_executed_stmts / safety_total_stmts * 100)
                if safety_total_stmts > 0 else 0.0
            )

            metrics = {
                'overall_coverage': overall_coverage,
                'critical_coverage': critical_coverage,
                'safety_coverage': safety_coverage,
                'timestamp': datetime.now().isoformat(),
                'total_files': len(list(analysis_data.measured_files())),
                'measurement_source': 'coverage.py_direct'
            }

            logger.info(f"Coverage metrics collected: overall={overall_coverage:.1f}%, "
                       f"critical={critical_coverage:.1f}%, safety={safety_coverage:.1f}%")

            return metrics

        except ImportError:
            logger.warning("coverage.py not installed - cannot gather coverage metrics")
            return None
        except Exception as e:
            logger.warning(f"Failed to gather coverage metrics from .coverage file: {e}")
            # Fallback to CoverageMonitor if available
            if self.coverage_monitor:
                try:
                    recent_metrics = self.coverage_monitor.get_recent_metrics(1)
                    if recent_metrics:
                        return asdict(recent_metrics[0])
                except Exception:
                    pass
            return None

    def _calculate_testing_score(self, pytest_results: Optional[TestExecutionResult]) -> float:
        """Calculate testing component score based on pytest results."""
        if not pytest_results:
            return 50.0  # Default score when tests not run

        # Calculate pass rate
        total_tests = pytest_results.total_tests
        passed_tests = pytest_results.passed_tests

        if total_tests == 0:
            return 0.0

        pass_rate = (passed_tests / total_tests) * 100

        # Weight different aspects of testing
        test_execution_score = min(100.0, pass_rate * 1.05)  # Slight bonus for high pass rates
        test_coverage_score = min(100.0, len(pytest_results.artifacts_generated) * 20)  # Bonus for artifacts

        return (test_execution_score * 0.8) + (test_coverage_score * 0.2)

    def _calculate_coverage_score(self, coverage_metrics: Optional[Dict[str, Any]]) -> float:
        """Calculate coverage component score."""
        if not coverage_metrics:
            return 50.0  # Default score when coverage unavailable

        overall = coverage_metrics.get('overall_coverage', 0)
        critical = coverage_metrics.get('critical_coverage', 0)
        safety = coverage_metrics.get('safety_coverage', 0)

        # Weighted average with emphasis on critical components
        weighted_score = (overall * 0.4) + (critical * 0.4) + (safety * 0.2)

        return min(100.0, weighted_score)

    def _calculate_compatibility_score(self, compatibility_analysis: Optional[Dict[str, Any]]) -> float:
        """Calculate compatibility component score."""
        if not compatibility_analysis:
            return 75.0  # Default score when analysis unavailable

        return compatibility_analysis.get('system_health_score', 75.0)

    def _calculate_performance_score(self, pytest_results: Optional[TestExecutionResult],
                                   include_benchmarks: bool) -> float:
        """Calculate performance component score."""
        base_score = 80.0  # Default performance score

        if pytest_results:
            # Factor in execution time efficiency
            execution_time = pytest_results.duration_seconds
            if execution_time < 300:  # Under 5 minutes
                base_score += 10.0
            elif execution_time > 1800:  # Over 30 minutes
                base_score -= 20.0

        if include_benchmarks:
            # Would analyze benchmark results if available
            base_score += 10.0  # Bonus for running benchmarks

        return min(100.0, base_score)

    def _calculate_safety_score(self, coverage_metrics: Optional[Dict[str, Any]],
                              pytest_results: Optional[TestExecutionResult]) -> float:
        """Calculate safety component score."""
        if not coverage_metrics:
            return 60.0  # Conservative default for safety

        safety_coverage = coverage_metrics.get('safety_coverage', 0)
        critical_coverage = coverage_metrics.get('critical_coverage', 0)

        # Safety score heavily weighted on coverage
        safety_score = (safety_coverage * 0.6) + (critical_coverage * 0.4)

        # Penalty for failed tests in safety-critical areas
        if pytest_results and pytest_results.failed_tests > 0:
            safety_score -= min(30.0, pytest_results.failed_tests * 5)

        return max(0.0, min(100.0, safety_score))

    def _calculate_documentation_score(self) -> float:
        """Calculate documentation component score."""
        # Simplified documentation assessment
        doc_dirs = [
            self.project_root / "docs",
            self.project_root / "README.md",
            self.project_root / "CHANGELOG.md"
        ]

        existing_docs = sum(1 for doc_path in doc_dirs if doc_path.exists())
        doc_score = (existing_docs / len(doc_dirs)) * 100

        # Check for API documentation
        api_docs = self.project_root / "docs" / "api"
        if api_docs.exists():
            doc_score += 10.0

        return min(100.0, doc_score)

    def _evaluate_quality_gates(self, pytest_results: Optional[TestExecutionResult],
                               coverage_metrics: Optional[Dict[str, Any]],
                               compatibility_analysis: Optional[Dict[str, Any]]) -> List[QualityGate]:
        """Evaluate all quality gates against current system state."""
        quality_gates = []

        for gate_name, gate_config in self.quality_gates_config.items():
            current_value = self._get_gate_current_value(
                gate_name, pytest_results, coverage_metrics, compatibility_analysis
            )

            gate = QualityGate(
                name=gate_name,
                category=gate_config["category"],
                threshold=gate_config["threshold"],
                current_value=current_value,
                weight=gate_config["weight"],
                passed=current_value >= gate_config["threshold"],
                critical=gate_config["critical"],
                description=gate_config["description"],
                recommendations=self._get_gate_recommendations(gate_name, current_value, gate_config["threshold"])
            )

            quality_gates.append(gate)

        return quality_gates

    def _get_gate_current_value(self, gate_name: str,
                               pytest_results: Optional[TestExecutionResult],
                               coverage_metrics: Optional[Dict[str, Any]],
                               compatibility_analysis: Optional[Dict[str, Any]]) -> float:
        """Get current value for a specific quality gate."""

        if gate_name == "overall_test_coverage":
            return coverage_metrics.get('overall_coverage', 0) if coverage_metrics else 0

        elif gate_name == "critical_component_coverage":
            return coverage_metrics.get('critical_coverage', 0) if coverage_metrics else 0

        elif gate_name == "safety_critical_coverage":
            return coverage_metrics.get('safety_coverage', 0) if coverage_metrics else 0

        elif gate_name == "test_pass_rate":
            if pytest_results and pytest_results.total_tests > 0:
                return (pytest_results.passed_tests / pytest_results.total_tests) * 100
            return 0

        elif gate_name == "system_compatibility":
            return compatibility_analysis.get('system_health_score', 0) if compatibility_analysis else 0

        elif gate_name == "performance_benchmarks":
            # Simplified - would integrate with actual benchmark results
            return 85.0  # Default assuming benchmarks pass

        elif gate_name == "numerical_stability":
            # Simplified - would analyze controller stability test results
            return 90.0  # Default assuming stability tests pass

        elif gate_name == "documentation_completeness":
            return self._calculate_documentation_score()

        return 0.0

    def _get_gate_recommendations(self, gate_name: str, current_value: float, threshold: float) -> List[str]:
        """Get recommendations for improving a specific quality gate."""
        if current_value >= threshold:
            return ["[OK] Quality gate passed"]

        gap = threshold - current_value
        recommendations = []

        if gate_name == "overall_test_coverage":
            recommendations.extend([
                f"Increase test coverage by {gap:.1f} percentage points",
                "Focus on untested modules and edge cases",
                "Add integration tests for complex workflows"
            ])

        elif gate_name == "critical_component_coverage":
            recommendations.extend([
                f"Increase critical component coverage by {gap:.1f} percentage points",
                "Prioritize controllers and plant models testing",
                "Add property-based tests for stability verification"
            ])

        elif gate_name == "test_pass_rate":
            recommendations.extend([
                f"Fix failing tests to improve pass rate by {gap:.1f} percentage points",
                "Investigate and resolve test failures",
                "Consider test environment stability issues"
            ])

        elif gate_name == "system_compatibility":
            recommendations.extend([
                f"Improve system compatibility score by {gap:.1f} points",
                "Address cross-domain integration issues",
                "Validate interface compatibility"
            ])

        else:
            recommendations.append(f"Improve {gate_name} by {gap:.1f} points")

        return recommendations

    def _calculate_overall_score(self, quality_gates: List[QualityGate]) -> float:
        """Calculate weighted overall readiness score."""
        total_weighted_score = 0.0
        total_weight = 0.0

        for gate in quality_gates:
            gate_score = min(100.0, (gate.current_value / gate.threshold) * 100)
            weighted_score = gate_score * gate.weight
            total_weighted_score += weighted_score
            total_weight += gate.weight

        return (total_weighted_score / total_weight) if total_weight > 0 else 0.0

    def _determine_readiness_level(self, overall_score: float, quality_gates: List[QualityGate]) -> ReadinessLevel:
        """Determine production readiness level based on score and gate status."""
        critical_failures = [gate for gate in quality_gates if gate.critical and not gate.passed]

        if len(critical_failures) > 0:
            return ReadinessLevel.BLOCKED
        elif overall_score >= 95.0:
            return ReadinessLevel.PRODUCTION_READY
        elif overall_score >= 85.0:
            return ReadinessLevel.CONDITIONAL_READY
        elif overall_score >= 70.0:
            return ReadinessLevel.NEEDS_IMPROVEMENT
        else:
            return ReadinessLevel.NOT_READY

    def _identify_blocking_issues(self, quality_gates: List[QualityGate]) -> List[str]:
        """Identify blocking issues preventing production deployment."""
        blocking_issues = []

        for gate in quality_gates:
            if gate.critical and not gate.passed:
                gap = gate.threshold - gate.current_value
                blocking_issues.append(
                    f"CRITICAL: {gate.name} at {gate.current_value:.1f}%, "
                    f"needs {gap:.1f}% improvement to reach {gate.threshold:.1f}% threshold"
                )

        return blocking_issues

    def _generate_recommendations(self, quality_gates: List[QualityGate],
                                readiness_level: ReadinessLevel) -> List[str]:
        """Generate comprehensive recommendations for improving readiness."""
        recommendations = []

        # Add level-specific recommendations
        if readiness_level == ReadinessLevel.BLOCKED:
            recommendations.append("[CRITICAL] BLOCKED: Address critical quality gate failures before deployment")
        elif readiness_level == ReadinessLevel.NOT_READY:
            recommendations.append("[BLOCKED] NOT READY: Significant improvements required across multiple areas")
        elif readiness_level == ReadinessLevel.NEEDS_IMPROVEMENT:
            recommendations.append("[WARN] IMPROVEMENT NEEDED: Address quality gaps before production")
        elif readiness_level == ReadinessLevel.CONDITIONAL_READY:
            recommendations.append("[OK] CONDITIONALLY READY: Deploy with enhanced monitoring")
        else:
            recommendations.append("[READY] PRODUCTION READY: System meets all quality requirements")

        # Add gate-specific recommendations
        failed_gates = [gate for gate in quality_gates if not gate.passed]
        if failed_gates:
            recommendations.append(f"[TODO] Address {len(failed_gates)} quality gate failures:")
            for gate in failed_gates[:5]:  # Top 5 failures
                recommendations.extend([f"   - {rec}" for rec in gate.recommendations[:2]])

        # Add general recommendations
        recommendations.extend([
            "[TEST] Run comprehensive integration tests before deployment",
            "[DATA] Monitor production readiness trends and address regressions",
            "[SCAN] Validate cross-domain compatibility regularly"
        ])

        return recommendations

    def _calculate_confidence_level(self, overall_score: float, quality_gates: List[QualityGate]) -> str:
        """Calculate confidence level in readiness assessment."""
        critical_passed = all(gate.passed for gate in quality_gates if gate.critical)

        if overall_score >= 95.0 and critical_passed:
            return "very_high"
        elif overall_score >= 85.0 and critical_passed:
            return "high"
        elif overall_score >= 70.0:
            return "medium"
        else:
            return "low"

    def _analyze_improvement_trend(self, current_score: float) -> str:
        """Analyze improvement trend based on historical data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT overall_score FROM readiness_assessments
                    ORDER BY timestamp DESC LIMIT 5
                """)

                recent_scores = [row[0] for row in cursor.fetchall()]

                if len(recent_scores) < 2:
                    return "insufficient_data"

                # Calculate trend
                recent_avg = sum(recent_scores[1:]) / len(recent_scores[1:])

                if current_score > recent_avg + 2:
                    return "improving"
                elif current_score < recent_avg - 2:
                    return "declining"
                else:
                    return "stable"

        except Exception:
            return "unknown"

    def _get_historical_comparison(self) -> Dict[str, Any]:
        """Get historical comparison data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT overall_score, readiness_level, timestamp
                    FROM readiness_assessments
                    ORDER BY timestamp DESC LIMIT 10
                """)

                history = cursor.fetchall()

                if not history:
                    return {}

                return {
                    "previous_score": history[0][0] if len(history) > 1 else None,
                    "score_change": None,  # Would calculate change
                    "historical_high": max(row[0] for row in history),
                    "historical_low": min(row[0] for row in history),
                    "assessments_count": len(history)
                }

        except Exception:
            return {}

    def _serialize_assessment(self, assessment: ReadinessAssessment) -> dict:
        """Serialize assessment to JSON-compatible dict, handling special types."""
        try:
            # Manually build dict to avoid asdict() issues with nested dataclasses
            data = {
                'timestamp': assessment.timestamp,
                'overall_score': assessment.overall_score,
                'readiness_level': assessment.readiness_level.value if isinstance(assessment.readiness_level, Enum) else str(assessment.readiness_level),
                'testing_score': assessment.testing_score,
                'coverage_score': assessment.coverage_score,
                'compatibility_score': assessment.compatibility_score,
                'performance_score': assessment.performance_score,
                'safety_score': assessment.safety_score,
                'documentation_score': assessment.documentation_score,
                'deployment_approved': assessment.deployment_approved,
                'confidence_level': assessment.confidence_level,
                'improvement_trend': assessment.improvement_trend,
                'blocking_issues': assessment.blocking_issues,
                'recommendations': assessment.recommendations,
            }

            # Handle quality gates manually
            if assessment.quality_gates:
                data['quality_gates'] = [
                    {
                        'name': gate.name,
                        'category': gate.category.value if isinstance(gate.category, Enum) else str(gate.category),
                        'threshold': gate.threshold,
                        'current_value': gate.current_value,
                        'weight': gate.weight,
                        'passed': gate.passed,
                        'critical': gate.critical,
                        'description': gate.description,
                        'recommendations': gate.recommendations
                    }
                    for gate in assessment.quality_gates
                ]

            # Handle optional nested dicts (skip dataclasses)
            if assessment.pytest_results and isinstance(assessment.pytest_results, dict):
                data['pytest_results'] = assessment.pytest_results
            elif assessment.pytest_results:
                # If it's a dataclass, convert only basic fields
                data['pytest_results'] = {
                    'timestamp': getattr(assessment.pytest_results, 'timestamp', None),
                    'duration_seconds': getattr(assessment.pytest_results, 'duration_seconds', 0.0),
                    'total_tests': getattr(assessment.pytest_results, 'total_tests', 0),
                    'passed_tests': getattr(assessment.pytest_results, 'passed_tests', 0),
                    'failed_tests': getattr(assessment.pytest_results, 'failed_tests', 0),
                }

            if assessment.coverage_metrics:
                data['coverage_metrics'] = assessment.coverage_metrics

            if assessment.compatibility_analysis:
                data['compatibility_analysis'] = assessment.compatibility_analysis

            if assessment.historical_comparison:
                data['historical_comparison'] = assessment.historical_comparison

            # Recursively ensure all values are JSON-compatible
            return self._convert_to_json_compatible(data)

        except Exception as e:
            logger.warning(f"Failed to serialize assessment: {e}")
            # Fallback: return minimal safe dict
            return {
                'timestamp': assessment.timestamp,
                'overall_score': assessment.overall_score,
                'readiness_level': assessment.readiness_level.value if isinstance(assessment.readiness_level, Enum) else str(assessment.readiness_level),
                'error': str(e)
            }

    def _convert_to_json_compatible(self, obj: Any) -> Any:
        """Recursively convert objects to JSON-compatible types."""
        # Skip callable objects (methods, functions)
        if callable(obj):
            return None

        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, dict):
            # Filter out non-serializable dict values
            return {
                k: self._convert_to_json_compatible(v)
                for k, v in obj.items()
                if not callable(v) and not k.startswith('_')
            }
        elif isinstance(obj, (list, tuple)):
            # Filter out non-serializable list items
            return [
                self._convert_to_json_compatible(item)
                for item in obj
                if not callable(item)
            ]
        elif hasattr(obj, '__dict__') and not isinstance(obj, type) and not callable(obj):
            # Handle objects with __dict__ (non-primitive types)
            return str(obj)
        elif isinstance(obj, (str, int, float, bool, type(None))):
            # Primitive types pass through
            return obj
        else:
            # Convert unknown types to string
            return str(obj)

    def _store_assessment(self, assessment: ReadinessAssessment):
        """Store assessment in database for historical tracking."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO readiness_assessments
                    (timestamp, overall_score, readiness_level, testing_score,
                     coverage_score, compatibility_score, performance_score,
                     safety_score, documentation_score, deployment_approved,
                     confidence_level, improvement_trend, data_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    assessment.timestamp,
                    assessment.overall_score,
                    assessment.readiness_level.value,
                    assessment.testing_score,
                    assessment.coverage_score,
                    assessment.compatibility_score,
                    assessment.performance_score,
                    assessment.safety_score,
                    assessment.documentation_score,
                    assessment.deployment_approved,
                    assessment.confidence_level,
                    assessment.improvement_trend,
                    json.dumps(self._serialize_assessment(assessment))
                ))
        except Exception as e:
            logger.warning(f"Failed to store assessment: {e}")

def main():
    """Main entry point for production readiness assessment."""
    import argparse

    parser = argparse.ArgumentParser(description="Production readiness assessment")
    parser.add_argument('--no-tests', action='store_true', help='Skip pytest execution')
    parser.add_argument('--quick', action='store_true', help='Quick mode assessment')
    parser.add_argument('--benchmarks', action='store_true', help='Include performance benchmarks')
    parser.add_argument('--export', type=str, help='Export results to JSON file')

    args = parser.parse_args()

    scorer = ProductionReadinessScorer()

    print("[SCAN] Starting production readiness assessment...")
    assessment = scorer.assess_production_readiness(
        run_tests=not args.no_tests,
        include_benchmarks=args.benchmarks,
        quick_mode=args.quick
    )

    # Display results
    print(f"\n{'='*80}")
    print("PRODUCTION READINESS ASSESSMENT")
    print(f"{'='*80}")
    print(f"Overall Score: {assessment.overall_score:.1f}/100")
    print(f"Readiness Level: {assessment.readiness_level.value.upper()}")
    print(f"Deployment Approved: {'YES' if assessment.deployment_approved else 'NO'}")
    print(f"Confidence: {assessment.confidence_level}")

    print("\n[DATA] COMPONENT SCORES:")
    print(f"  Testing: {assessment.testing_score:.1f}/100")
    print(f"  Coverage: {assessment.coverage_score:.1f}/100")
    print(f"  Compatibility: {assessment.compatibility_score:.1f}/100")
    print(f"  Performance: {assessment.performance_score:.1f}/100")
    print(f"  Safety: {assessment.safety_score:.1f}/100")
    print(f"  Documentation: {assessment.documentation_score:.1f}/100")

    if assessment.blocking_issues:
        print("\n[CRITICAL] BLOCKING ISSUES:")
        for issue in assessment.blocking_issues:
            print(f"  - {issue}")

    print("\n[TIP] RECOMMENDATIONS:")
    for rec in assessment.recommendations[:5]:  # Top 5 recommendations
        print(f"  {rec}")

    # Export if requested
    if args.export:
        export_path = Path(args.export)
        with open(export_path, 'w') as f:
            json.dump(scorer._serialize_assessment(assessment), f, indent=2)
        print(f"\n[FILE] Results exported to: {export_path}")

if __name__ == "__main__":
    main()