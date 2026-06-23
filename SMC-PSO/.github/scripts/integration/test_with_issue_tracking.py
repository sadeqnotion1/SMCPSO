#!/usr/bin/env python3
#==========================================================================================\\\
#========================= test_with_issue_tracking.py =================================\\\
#==========================================================================================\\\
"""
Enhanced test runner that automatically creates GitHub issues for test failures and regressions.

This script wraps pytest execution and monitors for:
- Unit test failures
- Integration test failures
- Performance regression failures
- Coverage drops
- Property-based test failures

Usage:
    python .github/scripts/integration/test_with_issue_tracking.py tests/test_controllers/
    python .github/scripts/integration/test_with_issue_tracking.py --benchmark-only
    python .github/scripts/integration/test_with_issue_tracking.py tests/ --cov=src
"""

import argparse
import json
import logging
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

# Add the repository root to path for imports
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DIP_PROJECT = REPO_ROOT
sys.path.insert(0, str(DIP_PROJECT))

@dataclass
class TestFailure:
    """Structure for test failure data."""
    test_name: str
    test_file: str
    failure_type: str  # failed, error, regression, coverage
    error_message: str
    traceback: Optional[str] = None
    line_number: Optional[int] = None

@dataclass
class IssueReport:
    """Structure for issue creation data."""
    title: str
    issue_type: str  # implementation, performance, coverage
    priority: str    # critical, high, medium, low
    description: str
    reproduction_steps: str
    test_file: Optional[str] = None
    labels: List[str] = None
    error_output: Optional[str] = None

class TestMonitor:
    """Monitors test execution and creates GitHub issues for failures."""

    def __init__(self):
        self.create_issue_script = REPO_ROOT / ".github" / "scripts" / "create_issue.sh"
        if not self.create_issue_script.exists():
            self.create_issue_script = REPO_ROOT / ".github" / "scripts" / "create_issue.bat"

        self.issues_created = []
        self.baseline_file = DIP_PROJECT / ".regression_baselines.json"

    def run_tests_with_monitoring(self, args: List[str]) -> int:
        """Run pytest with monitoring and issue detection."""
        # Ensure we're in the repository root directory
        original_cwd = Path.cwd()
        os.chdir(DIP_PROJECT)

        try:
            # Construct pytest command
            pytest_cmd = ["python", "-m", "pytest"] + args + [
                "--tb=short",  # Shorter traceback format
                "--json-report",  # JSON output for analysis
                "--json-report-file=.reports/test_results.json"
            ]

            logging.info(f"Running tests: {' '.join(pytest_cmd)}")

            # Execute with monitoring
            start_time = time.time()
            result = subprocess.run(
                pytest_cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            execution_time = time.time() - start_time

            # Parse test results and create issues if needed
            issues = self._analyze_test_results(
                result.returncode,
                result.stdout,
                result.stderr,
                args,
                execution_time
            )

            # Create GitHub issues for detected problems
            for issue in issues:
                self._create_github_issue(issue)

            # Print original output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

            return result.returncode

        except subprocess.TimeoutExpired:
            issue = IssueReport(
                title="Test execution timeout - tests exceeded 10 minutes",
                issue_type="performance",
                priority="high",
                description="Test suite failed to complete within reasonable time",
                reproduction_steps=f"Run: pytest {' '.join(args)}",
                labels=["timeout", "performance", "testing"]
            )
            self._create_github_issue(issue)
            return 1

        except Exception as e:
            issue = IssueReport(
                title=f"Test execution error: {str(e)}",
                issue_type="implementation",
                priority="high",
                description=f"Unexpected error during test execution: {str(e)}",
                reproduction_steps=f"Run: pytest {' '.join(args)}",
                labels=["execution-error", "implementation", "testing"]
            )
            self._create_github_issue(issue)
            return 1

        finally:
            os.chdir(original_cwd)

    def _analyze_test_results(self, returncode: int, stdout: str, stderr: str,
                            args: List[str], execution_time: float) -> List[IssueReport]:
        """Analyze test results for issues."""
        issues = []

        # Parse test failures from output
        test_failures = self._parse_test_failures(stdout, stderr)

        # Create issues for different types of failures
        for failure in test_failures:
            issue = self._create_issue_from_failure(failure, args)
            if issue:
                issues.append(issue)

        # Check for performance regressions
        if "--benchmark-only" in args:
            regression_issues = self._detect_performance_regressions(stdout)
            issues.extend(regression_issues)

        # Check for coverage drops
        if any("--cov" in arg for arg in args):
            coverage_issues = self._detect_coverage_issues(stdout)
            issues.extend(coverage_issues)

        # Check for slow test execution
        if execution_time > 300:  # 5 minutes
            issues.append(IssueReport(
                title=f"Slow test execution: {execution_time:.1f}s",
                issue_type="performance",
                priority="medium",
                description=f"Test suite took {execution_time:.1f} seconds to complete",
                reproduction_steps=f"Run: pytest {' '.join(args)}",
                labels=["performance", "slow-tests", "medium"]
            ))

        return issues

    def _parse_test_failures(self, stdout: str, stderr: str) -> List[TestFailure]:
        """Parse test failures from pytest output."""
        failures = []

        # Parse JSON report if available
        json_report_path = DIP_PROJECT / ".reports" / "test_results.json"
        if json_report_path.exists():
            try:
                with open(json_report_path, 'r') as f:
                    report = json.load(f)

                for test in report.get('tests', []):
                    if test.get('outcome') in ['failed', 'error']:
                        failure = TestFailure(
                            test_name=test.get('nodeid', 'unknown'),
                            test_file=test.get('nodeid', '').split('::')[0],
                            failure_type=test.get('outcome', 'failed'),
                            error_message=test.get('call', {}).get('longrepr', 'Unknown error'),
                            traceback=test.get('call', {}).get('longrepr')
                        )
                        failures.append(failure)
            except (FileNotFoundError, json.JSONDecodeError):
                pass

        # Fallback to parsing text output
        if not failures:
            failures = self._parse_text_failures(stdout, stderr)

        return failures

    def _parse_text_failures(self, stdout: str, stderr: str) -> List[TestFailure]:
        """Parse test failures from text output."""
        failures = []
        combined_output = stdout + "\n" + stderr

        # Look for pytest failure patterns
        failure_pattern = r"FAILED (.*?)::(.*?) - (.*?)(?=\n\w+|\n=|$)"
        matches = re.findall(failure_pattern, combined_output, re.DOTALL)

        for match in matches:
            test_file, test_name, error_msg = match
            failure = TestFailure(
                test_name=f"{test_file}::{test_name}",
                test_file=test_file,
                failure_type="failed",
                error_message=error_msg.strip()
            )
            failures.append(failure)

        # Look for ERROR patterns
        error_pattern = r"ERROR (.*?)::(.*?) - (.*?)(?=\n\w+|\n=|$)"
        matches = re.findall(error_pattern, combined_output, re.DOTALL)

        for match in matches:
            test_file, test_name, error_msg = match
            failure = TestFailure(
                test_name=f"{test_file}::{test_name}",
                test_file=test_file,
                failure_type="error",
                error_message=error_msg.strip()
            )
            failures.append(failure)

        return failures

    def _create_issue_from_failure(self, failure: TestFailure, args: List[str]) -> Optional[IssueReport]:
        """Create an issue report from a test failure."""
        # Determine priority based on failure type and test location
        priority = self._determine_failure_priority(failure)

        # Determine issue type
        if "benchmark" in failure.test_file or "--benchmark" in args:
            issue_type = "performance"
        elif failure.failure_type == "error":
            issue_type = "implementation"
        else:
            issue_type = "implementation"

        # Create descriptive title
        title = f"Test failure: {failure.test_name}"

        # Create detailed description
        description = f"""
Test failure detected in automated testing:

**Test**: `{failure.test_name}`
**File**: `{failure.test_file}`
**Failure Type**: {failure.failure_type}

**Error Message**:
```
{failure.error_message}
```
"""

        if failure.traceback:
            description += f"""
**Full Traceback**:
```
{failure.traceback}
```
"""

        # Determine labels
        labels = ["testing", issue_type, priority]

        if "controller" in failure.test_file:
            labels.append("control-systems")
        elif "optimization" in failure.test_file or "pso" in failure.test_file:
            labels.append("optimization")
        elif "benchmark" in failure.test_file:
            labels.append("performance")

        return IssueReport(
            title=title,
            issue_type=issue_type,
            priority=priority,
            description=description.strip(),
            reproduction_steps=f"Run: pytest {failure.test_file} -v",
            test_file=failure.test_file,
            labels=labels,
            error_output=failure.error_message
        )

    def _determine_failure_priority(self, failure: TestFailure) -> str:
        """Determine priority level for a test failure."""
        # Critical: Core controller or safety tests
        if any(keyword in failure.test_file.lower() for keyword in
               ["stability", "safety", "lyapunov", "control"]):
            return "critical"

        # High: Core functionality tests
        elif any(keyword in failure.test_file.lower() for keyword in
                ["core", "simulation", "optimization"]):
            return "high"

        # Medium: Feature tests, integration tests
        elif any(keyword in failure.test_file.lower() for keyword in
                ["integration", "feature", "app"]):
            return "medium"

        # Low: Performance tests, documentation tests
        else:
            return "low"

    def _detect_performance_regressions(self, stdout: str) -> List[IssueReport]:
        """Detect performance regressions from benchmark output."""
        issues = []

        # Look for regression indicators in benchmark output
        if "slower" in stdout.lower():
            # Parse benchmark regression details
            regression_pattern = r"(\w+.*?) is (\d+\.?\d*)x slower"
            matches = re.findall(regression_pattern, stdout)

            for test_name, slowdown in matches:
                if float(slowdown) > 1.5:  # More than 50% slower
                    priority = "high" if float(slowdown) > 2.0 else "medium"
                    issues.append(IssueReport(
                        title=f"Performance regression: {test_name} is {slowdown}x slower",
                        issue_type="performance",
                        priority=priority,
                        description=f"Benchmark test '{test_name}' shows {slowdown}x performance regression",
                        reproduction_steps="Run: pytest --benchmark-only",
                        labels=["regression", "performance", priority]
                    ))

        return issues

    def _detect_coverage_issues(self, stdout: str) -> List[IssueReport]:
        """Detect coverage drops from coverage reports."""
        issues = []

        # Parse coverage percentage
        coverage_pattern = r"TOTAL.*?(\d+)%"
        match = re.search(coverage_pattern, stdout)

        if match:
            current_coverage = int(match.group(1))

            # Load baseline coverage if available
            baseline_coverage = self._load_baseline_coverage()

            if baseline_coverage and current_coverage < baseline_coverage - 5:  # 5% drop
                issues.append(IssueReport(
                    title=f"Coverage drop: {current_coverage}% (was {baseline_coverage}%)",
                    issue_type="implementation",
                    priority="medium",
                    description=f"Test coverage dropped from {baseline_coverage}% to {current_coverage}%",
                    reproduction_steps="Run: pytest --cov=src --cov-report=term",
                    labels=["coverage", "regression", "medium"]
                ))

        return issues

    def _load_baseline_coverage(self) -> Optional[int]:
        """Load baseline coverage from regression file."""
        try:
            if self.baseline_file.exists():
                with open(self.baseline_file, 'r') as f:
                    baselines = json.load(f)
                    return baselines.get('coverage_percentage')
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return None

    def _create_github_issue(self, issue: IssueReport) -> None:
        """Create a GitHub issue using the create_issue script."""
        try:
            # Prepare command
            cmd = [str(self.create_issue_script)]

            # Add arguments based on issue type
            cmd.extend(["-t", issue.issue_type])
            cmd.extend(["-p", issue.priority])
            cmd.extend(["-T", issue.title])
            cmd.extend(["-d", issue.description])
            cmd.extend(["-r", issue.reproduction_steps])

            if issue.test_file:
                cmd.extend(["-f", issue.test_file])

            # Execute the issue creation
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✓ Created GitHub issue: {issue.title}")
                self.issues_created.append(issue.title)
            else:
                print(f"✗ Failed to create issue: {issue.title}")
                print(f"Error: {result.stderr}")

        except Exception as e:
            print(f"✗ Error creating issue '{issue.title}': {e}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Enhanced test runner with automatic GitHub issue creation",
        add_help=False  # We'll pass through all args to pytest
    )

    # Parse known args to capture our special flags
    parser.add_argument("--no-issue-tracking", action="store_true",
                       help="Disable automatic issue creation")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose monitoring output")

    # Parse known args and pass the rest to pytest
    known_args, unknown_args = parser.parse_known_args()

    if known_args.verbose:
        logging.basicConfig(level=logging.INFO)

    # Create monitor and run tests
    monitor = TestMonitor()

    if known_args.no_issue_tracking:
        # Just run pytest directly
        import os
        os.chdir(DIP_PROJECT)
        pytest_cmd = ["python", "-m", "pytest"] + unknown_args
        return subprocess.call(pytest_cmd)
    else:
        # Run with monitoring
        return monitor.run_tests_with_monitoring(unknown_args)

if __name__ == "__main__":
    import os
    sys.exit(main())