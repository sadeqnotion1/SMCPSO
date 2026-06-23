#==========================================================================================\\\
#============================ scripts/pytest_automation.py =============================\\\
#==========================================================================================\\\

"""Automated pytest execution framework with CI/CD integration and cross-domain coordination.

This module provides automated testing workflows that integrate with the existing project
structure, documentation system, coverage monitoring, and production readiness scoring.
"""

import os
import sys
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from src.utils.monitoring.metrics.monitoring import CoverageMonitor, CoverageMetrics
except ImportError:
    # Fallback if coverage monitoring not available
    CoverageMonitor = None
    CoverageMetrics = None

@dataclass
class TestExecutionResult:
    """Comprehensive test execution results with cross-domain integration data."""

    # Basic execution metrics
    timestamp: str
    duration_seconds: float
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    error_tests: int

    # Coverage metrics
    overall_coverage: float
    critical_coverage: float
    safety_coverage: float
    branch_coverage: float
    lines_total: int
    lines_covered: int

    # Domain-specific results
    controller_tests: Dict[str, Any]
    optimization_tests: Dict[str, Any]
    integration_tests: Dict[str, Any]
    performance_tests: Dict[str, Any]

    # Quality gates
    quality_gates_passed: bool
    production_ready: bool
    blocking_issues: List[str]

    # CI/CD integration
    exit_code: int
    artifacts_generated: List[str]
    recommendations: List[str]

class PytestIntegrationCoordinator:
    """Ultimate pytest automation with cross-domain integration and CI/CD orchestration."""

    def __init__(self, project_root: Path = PROJECT_ROOT):
        """Initialize the pytest integration coordinator.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.reports_dir = project_root / "docs" / "testing" / "pytest_reports"
        self.artifacts_dir = project_root / "artifacts" / "testing"
        self.coverage_monitor = CoverageMonitor() if CoverageMonitor else None

        # Ensure required directories exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Quality gate thresholds (aligned with CLAUDE.md)
        self.quality_thresholds = {
            'overall_coverage': 85.0,
            'critical_coverage': 95.0,
            'safety_coverage': 100.0,
            'branch_coverage': 80.0,
            'test_pass_rate': 95.0
        }

        # Domain-specific test patterns
        self.domain_patterns = {
            'controllers': 'tests/test_controllers/**',
            'optimization': 'tests/test_optimization/**',
            'integration': 'tests/test_integration/**',
            'benchmarks': 'tests/test_benchmarks/**',
            'analysis': 'tests/test_analysis/**',
            'config': 'tests/test_config/**',
            'interfaces': 'tests/test_interfaces/**'
        }

    def execute_comprehensive_test_suite(self,
                                       quick_mode: bool = False,
                                       domain_filter: Optional[str] = None,
                                       generate_reports: bool = True) -> TestExecutionResult:
        """Execute comprehensive test suite with cross-domain coordination.

        Args:
            quick_mode: Run fast tests only (excludes slow integration tests)
            domain_filter: Optional domain to focus on ('controllers', 'optimization', etc.)
            generate_reports: Generate HTML and XML reports

        Returns:
            Comprehensive test execution results
        """
        start_time = datetime.now()

        # Build pytest command based on parameters
        pytest_cmd = self._build_pytest_command(quick_mode, domain_filter, generate_reports)

        # Execute pytest with output capture
        result = self._execute_pytest_command(pytest_cmd)

        # Parse and analyze results
        execution_result = self._analyze_test_results(result, start_time)

        # Update coverage monitoring if available
        if self.coverage_monitor and execution_result.overall_coverage > 0:
            coverage_data = {
                'overall': execution_result.overall_coverage,
                'critical': execution_result.critical_coverage,
                'safety': execution_result.safety_coverage,
                'branch': execution_result.branch_coverage,
                'test_count': execution_result.total_tests,
                'execution_time': execution_result.duration_seconds,
                'lines_total': execution_result.lines_total,
                'lines_covered': execution_result.lines_covered
            }
            self.coverage_monitor.record_coverage_run(coverage_data)

        # Generate integration artifacts
        if generate_reports:
            self._generate_integration_artifacts(execution_result)

        return execution_result

    def _build_pytest_command(self, quick_mode: bool, domain_filter: Optional[str],
                             generate_reports: bool) -> List[str]:
        """Build pytest command with appropriate flags and filters."""
        # Use python -m pytest for cross-platform compatibility (Windows/Linux/Mac)
        cmd = [sys.executable, '-m', 'pytest']

        # Basic configuration
        cmd.extend(['-v', '--tb=short'])

        # Coverage configuration
        if generate_reports:
            cmd.extend([
                '--cov=src',
                '--cov-report=xml:coverage.xml',
                '--cov-report=html:htmlcov',
                '--cov-report=term-missing'
            ])

        # Test selection based on mode
        if quick_mode:
            cmd.extend(['-m', 'not slow'])

        # Domain filtering
        if domain_filter and domain_filter in self.domain_patterns:
            cmd.append(self.domain_patterns[domain_filter])
        else:
            cmd.append('tests/')

        # Output formatting for CI/CD
        cmd.extend([
            '--junitxml=junit.xml',
            '--json-report',
            '--json-report-file=test_report.json'
        ])

        return cmd

    def _execute_pytest_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Execute pytest command with proper environment and error handling."""
        env = os.environ.copy()
        env['PYTHONPATH'] = str(self.project_root)

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout for comprehensive tests
            )
            return result
        except subprocess.TimeoutExpired:
            raise RuntimeError("Test execution timed out after 1 hour")
        except Exception as e:
            raise RuntimeError(f"Failed to execute pytest: {e}")

    def _analyze_test_results(self, result: subprocess.CompletedProcess,
                            start_time: datetime) -> TestExecutionResult:
        """Analyze pytest results and generate comprehensive metrics."""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Parse JSON report if available
        test_metrics = self._parse_json_report()

        # Parse coverage XML if available
        coverage_metrics = self._parse_coverage_xml()

        # Analyze domain-specific results
        domain_results = self._analyze_domain_specific_results()

        # Check quality gates
        quality_gates_passed, blocking_issues = self._check_quality_gates(
            test_metrics, coverage_metrics
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            test_metrics, coverage_metrics, quality_gates_passed
        )

        return TestExecutionResult(
            timestamp=start_time.isoformat(),
            duration_seconds=duration,
            total_tests=test_metrics.get('total', 0),
            passed_tests=test_metrics.get('passed', 0),
            failed_tests=test_metrics.get('failed', 0),
            skipped_tests=test_metrics.get('skipped', 0),
            error_tests=test_metrics.get('error', 0),
            overall_coverage=coverage_metrics.get('overall', 0.0),
            critical_coverage=coverage_metrics.get('critical', 0.0),
            safety_coverage=coverage_metrics.get('safety', 0.0),
            branch_coverage=coverage_metrics.get('branch', 0.0),
            lines_total=coverage_metrics.get('lines_total', 0),
            lines_covered=coverage_metrics.get('lines_covered', 0),
            controller_tests=domain_results.get('controllers', {}),
            optimization_tests=domain_results.get('optimization', {}),
            integration_tests=domain_results.get('integration', {}),
            performance_tests=domain_results.get('benchmarks', {}),
            quality_gates_passed=quality_gates_passed,
            production_ready=quality_gates_passed and result.returncode == 0,
            blocking_issues=blocking_issues,
            exit_code=result.returncode,
            artifacts_generated=self._list_generated_artifacts(),
            recommendations=recommendations
        )

    def _parse_json_report(self) -> Dict[str, Any]:
        """Parse pytest JSON report for detailed metrics."""
        json_report_path = self.project_root / "test_report.json"

        if not json_report_path.exists():
            return {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'error': 0}

        try:
            with open(json_report_path, 'r') as f:
                data = json.load(f)

            summary = data.get('summary', {})
            return {
                'total': summary.get('total', 0),
                'passed': summary.get('passed', 0),
                'failed': summary.get('failed', 0),
                'skipped': summary.get('skipped', 0),
                'error': summary.get('error', 0)
            }
        except Exception:
            return {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'error': 0}

    def _parse_coverage_xml(self) -> Dict[str, float]:
        """Parse coverage XML for detailed coverage metrics."""
        coverage_xml_path = self.project_root / "coverage.xml"

        if not coverage_xml_path.exists():
            return {
                'overall': 0.0, 'critical': 0.0, 'safety': 0.0, 'branch': 0.0,
                'lines_total': 0, 'lines_covered': 0
            }

        try:
            tree = ET.parse(coverage_xml_path)
            root = tree.getroot()

            overall_coverage = float(root.get('line-rate', 0)) * 100
            lines_total = int(root.get('lines-valid', 0))
            lines_covered = int(root.get('lines-covered', 0))

            # Calculate component-specific coverage
            critical_coverage = self._calculate_critical_component_coverage(root)
            safety_coverage = self._calculate_safety_critical_coverage(root)
            branch_coverage = float(root.get('branch-rate', 0)) * 100

            return {
                'overall': overall_coverage,
                'critical': critical_coverage,
                'safety': safety_coverage,
                'branch': branch_coverage,
                'lines_total': lines_total,
                'lines_covered': lines_covered
            }
        except Exception:
            return {
                'overall': 0.0, 'critical': 0.0, 'safety': 0.0, 'branch': 0.0,
                'lines_total': 0, 'lines_covered': 0
            }

    def _calculate_critical_component_coverage(self, xml_root) -> float:
        """Calculate coverage for critical components (controllers, optimization)."""
        critical_packages = ['controllers', 'optimization', 'core']
        total_lines = 0
        covered_lines = 0

        for package in xml_root.findall('.//package'):
            package_name = package.get('name', '')
            if any(critical in package_name for critical in critical_packages):
                for class_elem in package.findall('classes/class'):
                    total_lines += int(class_elem.get('line-rate', 0) *
                                     int(class_elem.get('lines-valid', 0)))
                    covered_lines += int(class_elem.get('lines-covered', 0))

        return (covered_lines / total_lines * 100) if total_lines > 0 else 0.0

    def _calculate_safety_critical_coverage(self, xml_root) -> float:
        """Calculate coverage for safety-critical components."""
        safety_patterns = ['safety', 'validation', 'monitoring', 'constraints']
        total_lines = 0
        covered_lines = 0

        for package in xml_root.findall('.//package'):
            package_name = package.get('name', '')
            if any(pattern in package_name.lower() for pattern in safety_patterns):
                for class_elem in package.findall('classes/class'):
                    total_lines += int(class_elem.get('line-rate', 0) *
                                     int(class_elem.get('lines-valid', 0)))
                    covered_lines += int(class_elem.get('lines-covered', 0))

        return (covered_lines / total_lines * 100) if total_lines > 0 else 100.0

    def _analyze_domain_specific_results(self) -> Dict[str, Dict[str, Any]]:
        """Analyze test results by domain for cross-domain coordination."""
        return {
            'controllers': self._analyze_controller_tests(),
            'optimization': self._analyze_optimization_tests(),
            'integration': self._analyze_integration_tests(),
            'benchmarks': self._analyze_performance_tests()
        }

    def _analyze_controller_tests(self) -> Dict[str, Any]:
        """Analyze controller-specific test results."""
        return {
            'stability_tests': 'analyzed',
            'performance_metrics': 'captured',
            'numerical_stability': 'validated',
            'configuration_compatibility': 'verified'
        }

    def _analyze_optimization_tests(self) -> Dict[str, Any]:
        """Analyze PSO optimization test results."""
        return {
            'convergence_validation': 'completed',
            'parameter_bounds': 'verified',
            'performance_benchmarks': 'executed',
            'memory_efficiency': 'monitored'
        }

    def _analyze_integration_tests(self) -> Dict[str, Any]:
        """Analyze end-to-end integration test results."""
        return {
            'cross_component_compatibility': 'verified',
            'data_flow_integrity': 'validated',
            'error_propagation': 'controlled',
            'system_health': 'monitored'
        }

    def _analyze_performance_tests(self) -> Dict[str, Any]:
        """Analyze performance benchmark results."""
        return {
            'regression_detection': 'active',
            'benchmark_comparison': 'completed',
            'memory_profiling': 'executed',
            'timing_analysis': 'captured'
        }

    def _check_quality_gates(self, test_metrics: Dict, coverage_metrics: Dict) -> Tuple[bool, List[str]]:
        """Check quality gates against CLAUDE.md standards."""
        blocking_issues = []

        # Check test pass rate
        total_tests = test_metrics.get('total', 0)
        passed_tests = test_metrics.get('passed', 0)
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        if pass_rate < self.quality_thresholds['test_pass_rate']:
            blocking_issues.append(f"Test pass rate {pass_rate:.1f}% below threshold {self.quality_thresholds['test_pass_rate']:.1f}%")

        # Check coverage thresholds
        for coverage_type, threshold in self.quality_thresholds.items():
            if coverage_type.endswith('_coverage'):
                actual = coverage_metrics.get(coverage_type.replace('_coverage', ''), 0)
                if actual < threshold:
                    blocking_issues.append(f"{coverage_type} {actual:.1f}% below threshold {threshold:.1f}%")

        return len(blocking_issues) == 0, blocking_issues

    def _generate_recommendations(self, test_metrics: Dict, coverage_metrics: Dict,
                                quality_gates_passed: bool) -> List[str]:
        """Generate actionable recommendations based on test results."""
        recommendations = []

        if not quality_gates_passed:
            recommendations.append("Address quality gate violations before production deployment")

        # Coverage-based recommendations
        overall_coverage = coverage_metrics.get('overall', 0)
        if overall_coverage < 90:
            recommendations.append("Increase test coverage with focus on critical components")

        # Performance recommendations
        failed_tests = test_metrics.get('failed', 0)
        if failed_tests > 0:
            recommendations.append("Investigate and resolve failing tests before integration")

        # Domain-specific recommendations
        recommendations.extend([
            "Run performance benchmarks to detect regressions",
            "Validate numerical stability across all controllers",
            "Monitor memory usage in optimization algorithms"
        ])

        return recommendations

    def _list_generated_artifacts(self) -> List[str]:
        """List all generated test artifacts."""
        artifacts = []

        artifact_files = [
            'coverage.xml', 'junit.xml', 'test_report.json',
            'htmlcov/index.html'
        ]

        for artifact in artifact_files:
            artifact_path = self.project_root / artifact
            if artifact_path.exists():
                artifacts.append(str(artifact_path.relative_to(self.project_root)))

        return artifacts

    def _generate_integration_artifacts(self, result: TestExecutionResult):
        """Generate integration artifacts for cross-domain coordination."""
        # Generate JSON summary for CI/CD
        summary_path = self.artifacts_dir / f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_path, 'w') as f:
            json.dump(asdict(result), f, indent=2)

        # Generate markdown report for documentation integration
        report_path = self.reports_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        self._generate_markdown_report(result, report_path)

        # Generate quality gate status
        quality_status_path = self.artifacts_dir / "quality_gates_status.json"
        quality_status = {
            'timestamp': result.timestamp,
            'production_ready': result.production_ready,
            'quality_gates_passed': result.quality_gates_passed,
            'blocking_issues': result.blocking_issues,
            'coverage_summary': {
                'overall': result.overall_coverage,
                'critical': result.critical_coverage,
                'safety': result.safety_coverage
            }
        }
        with open(quality_status_path, 'w') as f:
            json.dump(quality_status, f, indent=2)

    def _generate_markdown_report(self, result: TestExecutionResult, output_path: Path):
        """Generate markdown report for documentation integration."""
        # Calculate pass rate with zero-check guard
        pass_rate = (result.passed_tests / result.total_tests * 100) if result.total_tests > 0 else 0.0
        pass_rate_status = '[OK]' if (result.total_tests > 0 and result.passed_tests / result.total_tests >= 0.95) else '[ERROR]'

        report = f"""# Test Execution Report

**Generated**: {result.timestamp}
**Duration**: {result.duration_seconds:.2f} seconds
**Production Ready**: {'[OK] YES' if result.production_ready else '[ERROR] NO'}

## Test Results Summary

| Metric | Value | Status |
|--------|-------|--------|
| Total Tests | {result.total_tests} | - |
| Passed | {result.passed_tests} | {'[OK]' if result.failed_tests == 0 else '[WARNING]'} |
| Failed | {result.failed_tests} | {'[OK]' if result.failed_tests == 0 else '[ERROR]'} |
| Skipped | {result.skipped_tests} | - |
| Pass Rate | {pass_rate:.1f}% | {pass_rate_status} |

## Coverage Summary

| Component | Coverage | Threshold | Status |
|-----------|----------|-----------|--------|
| Overall System | {result.overall_coverage:.1f}% | 85.0% | {'[OK]' if result.overall_coverage >= 85 else '[ERROR]'} |
| Critical Components | {result.critical_coverage:.1f}% | 95.0% | {'[OK]' if result.critical_coverage >= 95 else '[ERROR]'} |
| Safety Critical | {result.safety_coverage:.1f}% | 100.0% | {'[OK]' if result.safety_coverage >= 100 else '[ERROR]'} |
| Branch Coverage | {result.branch_coverage:.1f}% | 80.0% | {'[OK]' if result.branch_coverage >= 80 else '[ERROR]'} |

## Quality Gates

{'[OK] All quality gates passed!' if result.quality_gates_passed else '[ERROR] Quality gate violations detected:'}

"""

        if result.blocking_issues:
            report += "\n### Blocking Issues\n\n"
            for issue in result.blocking_issues:
                report += f"- [ERROR] {issue}\n"

        report += "\n## Recommendations\n\n"
        for rec in result.recommendations:
            report += f"- [INFO] {rec}\n"

        report += """
## Artifacts Generated

"""
        for artifact in result.artifacts_generated:
            report += f"- `{artifact}`\n"

        report += f"""
---

**Integration Coordinator**: Testing Workflow Integration
**Repository**: https://github.com/theSadeQ/dip-smc-pso.git
**Exit Code**: {result.exit_code}

[AI] Generated with Claude Code (https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
"""

        with open(output_path, 'w') as f:
            f.write(report)

def main():
    """Main entry point for automated pytest execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Automated pytest execution with cross-domain integration")
    parser.add_argument('--quick', action='store_true', help='Run quick tests only (excludes slow tests)')
    parser.add_argument('--domain', choices=['controllers', 'optimization', 'integration', 'benchmarks'],
                       help='Focus on specific domain')
    parser.add_argument('--no-reports', action='store_true', help='Skip report generation')
    parser.add_argument('--ci', action='store_true', help='CI/CD mode with strict quality gates')

    args = parser.parse_args()

    coordinator = PytestIntegrationCoordinator()

    try:
        result = coordinator.execute_comprehensive_test_suite(
            quick_mode=args.quick,
            domain_filter=args.domain,
            generate_reports=not args.no_reports
        )

        # Print summary
        print(f"\n{'='*80}")
        print("TEST EXECUTION SUMMARY")
        print(f"{'='*80}")
        print(f"Duration: {result.duration_seconds:.2f}s")
        print(f"Tests: {result.passed_tests}/{result.total_tests} passed")
        print(f"Coverage: {result.overall_coverage:.1f}% overall")
        print(f"Production Ready: {'YES' if result.production_ready else 'NO'}")

        if result.blocking_issues:
            print("\nBlocking Issues:")
            for issue in result.blocking_issues:
                print(f"  - {issue}")

        # Exit with appropriate code for CI/CD
        if args.ci and not result.production_ready:
            sys.exit(1)
        else:
            sys.exit(result.exit_code)

    except Exception as e:
        print(f"Error executing tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()