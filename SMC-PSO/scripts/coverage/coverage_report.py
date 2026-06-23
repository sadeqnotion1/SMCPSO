#===================================================================================\\\
#====================== scripts/coverage/coverage_report.py ========================\\\
#===================================================================================\\\

"""
Comprehensive Coverage Report Generator.

This script generates detailed coverage reports with statistics,
trend analysis, and gap identification.

Usage:
    python scripts/coverage/coverage_report.py                      # Generate all reports
    python scripts/coverage/coverage_report.py --run-tests          # Run tests first
    python scripts/coverage/coverage_report.py --save-baseline      # Save as baseline
    python scripts/coverage/coverage_report.py --compare-baseline   # Compare to baseline

Outputs:
    - HTML report: .htmlcov/index.html
    - JSON report: coverage.json
    - Terminal summary table
    - Coverage trends (if baseline exists)
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class CoverageSnapshot:
    """Coverage snapshot for trend analysis."""
    timestamp: str
    overall_percent: float
    safety_critical_percent: float
    critical_percent: float
    general_percent: float
    total_lines: int
    covered_lines: int
    total_branches: int
    covered_branches: int
    test_count: int


class CoverageReportGenerator:
    """Comprehensive coverage report generator."""

    def __init__(self, project_root: Path = Path(".")):
        self.project_root = project_root
        self.coverage_file = project_root / "coverage.json"
        self.html_dir = project_root / ".htmlcov"
        self.baseline_file = project_root / ".coverage_baseline.json"
        self.history_file = project_root / ".coverage_history.json"

    def run_coverage_tests(self) -> bool:
        """Run pytest with coverage collection."""
        print("Running tests with coverage collection...")
        print("Command: pytest --cov=src --cov-report=html --cov-report=json\n")
        print("[INFO] Terminal output disabled to avoid Windows Unicode issues (cp1252)")
        print("[INFO] View results in HTML report: .htmlcov/index.html\n")

        try:
            result = subprocess.run(
                [
                    "pytest",
                    "--cov=src",
                    "--cov-report=html",
                    "--cov-report=json",
                    # Note: --cov-report=term removed to fix Windows cp1252 Unicode issues
                    "-v"
                ],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            print(result.stdout)
            if result.returncode != 0:
                print(result.stderr)
                print(f"\nWarning: Some tests failed (exit code {result.returncode})")
                print("Coverage data still generated.\n")

            return True

        except subprocess.TimeoutExpired:
            print("Error: Test execution timed out (10 minutes)")
            return False
        except FileNotFoundError:
            print("Error: pytest not found. Install with: pip install pytest pytest-cov")
            return False
        except Exception as e:
            print(f"Error running tests: {e}")
            return False

    def load_coverage_data(self) -> Optional[Dict]:
        """Load coverage data from JSON file."""
        if not self.coverage_file.exists():
            print(f"Error: {self.coverage_file} not found.")
            print("Run with --run-tests to generate coverage data.")
            return None

        with open(self.coverage_file, 'r') as f:
            return json.load(f)

    def extract_snapshot(self, coverage_data: Dict) -> CoverageSnapshot:
        """Extract coverage snapshot from coverage data."""
        # Get overall metrics
        totals = coverage_data.get("totals", {})
        overall_percent = totals.get("percent_covered", 0.0)
        total_lines = totals.get("num_statements", 0)
        covered_lines = totals.get("covered_lines", 0)
        total_branches = totals.get("num_branches", 0)
        covered_branches = totals.get("covered_branches", 0)

        # Calculate by-level percentages (simplified - use categorization logic)
        safety_critical_percent = 0.0  # Would need full categorization
        critical_percent = 0.0
        general_percent = overall_percent

        # Count tests (approximate from meta data if available)
        test_count = coverage_data.get("meta", {}).get("test_count", 0)

        return CoverageSnapshot(
            timestamp=datetime.now().isoformat(),
            overall_percent=overall_percent,
            safety_critical_percent=safety_critical_percent,
            critical_percent=critical_percent,
            general_percent=general_percent,
            total_lines=total_lines,
            covered_lines=covered_lines,
            total_branches=total_branches,
            covered_branches=covered_branches,
            test_count=test_count
        )

    def save_baseline(self, snapshot: CoverageSnapshot):
        """Save current coverage as baseline."""
        with open(self.baseline_file, 'w') as f:
            json.dump(asdict(snapshot), f, indent=2)
        print(f"✓ Baseline saved to {self.baseline_file}")

    def load_baseline(self) -> Optional[CoverageSnapshot]:
        """Load baseline coverage snapshot."""
        if not self.baseline_file.exists():
            return None

        with open(self.baseline_file, 'r') as f:
            data = json.load(f)
            return CoverageSnapshot(**data)

    def append_to_history(self, snapshot: CoverageSnapshot):
        """Append snapshot to coverage history."""
        history = []

        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                history = json.load(f)

        history.append(asdict(snapshot))

        # Keep last 100 snapshots
        history = history[-100:]

        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)

    def print_summary_table(self, snapshot: CoverageSnapshot, baseline: Optional[CoverageSnapshot] = None):
        """Print summary statistics table."""
        print("\n" + "="*80)
        print("                  COVERAGE SUMMARY STATISTICS")
        print("="*80)

        # Overall metrics
        print(f"\nOverall Coverage:    {snapshot.overall_percent:6.2f}%")
        print(f"Lines Covered:       {snapshot.covered_lines:6d} / {snapshot.total_lines} lines")
        print(f"Branches Covered:    {snapshot.covered_branches:6d} / {snapshot.total_branches} branches")

        # Comparison to baseline
        if baseline:
            delta_percent = snapshot.overall_percent - baseline.overall_percent
            delta_lines = snapshot.covered_lines - baseline.covered_lines

            if delta_percent > 0:
                direction = "↑"
                color_code = ""  # Green in terminals that support it
            elif delta_percent < 0:
                direction = "↓"
                color_code = ""  # noqa: F841 - color_code unused
            else:
                direction = "="
                color_code = ""  # noqa: F841 - color_code unused

            print("\nChange from Baseline:")
            print(f"  Percentage:        {direction} {delta_percent:+.2f}%")
            print(f"  Lines:             {direction} {delta_lines:+d} lines")

        # Quality gates status
        print("\nQuality Gates:")
        print(f"  Overall (≥85%):           {'✓ PASS' if snapshot.overall_percent >= 85 else '✗ FAIL'}")
        print(f"  Critical (≥95%):          {'✓ PASS' if snapshot.critical_percent >= 95 else '✗ FAIL'}")
        print(f"  Safety-Critical (100%):   {'✓ PASS' if snapshot.safety_critical_percent >= 100 else '✗ FAIL'}")

        print("\n" + "="*80 + "\n")

    def print_file_coverage_table(self, coverage_data: Dict, top_n: int = 15):
        """Print table of files with lowest coverage."""
        files = coverage_data.get("files", {})

        # Extract file coverage
        file_coverage = []
        for file_path, file_data in files.items():
            if not file_path.startswith("src/"):
                continue

            summary = file_data.get("summary", {})
            percent = summary.get("percent_covered", 0.0)
            lines_total = summary.get("num_statements", 0)
            lines_covered = summary.get("covered_lines", 0)
            missing = lines_total - lines_covered

            file_coverage.append({
                "path": file_path.replace("src/", ""),
                "percent": percent,
                "covered": lines_covered,
                "total": lines_total,
                "missing": missing
            })

        # Sort by coverage percentage (lowest first)
        file_coverage.sort(key=lambda x: x["percent"])

        # Print table
        print("="*80)
        print(f"          FILES WITH LOWEST COVERAGE (Top {top_n})")
        print("="*80)
        print(f"{'File':<45} {'Coverage':>10} {'Lines':>12} {'Missing':>8}")
        print("-"*80)

        for file_info in file_coverage[:top_n]:
            print(f"{file_info['path']:<45} {file_info['percent']:>9.2f}% "
                  f"{file_info['covered']:>5d}/{file_info['total']:<5d} "
                  f"{file_info['missing']:>7d}")

        print("="*80 + "\n")

    def print_trend_analysis(self):
        """Print coverage trend analysis if history exists."""
        if not self.history_file.exists():
            print("No coverage history available. Run --save-baseline to start tracking trends.\n")
            return

        with open(self.history_file, 'r') as f:
            history = json.load(f)

        if len(history) < 2:
            print("Insufficient history for trend analysis (need at least 2 data points).\n")
            return

        print("="*80)
        print("                      COVERAGE TREND ANALYSIS")
        print("="*80)

        # Show last 10 snapshots
        recent = history[-10:]

        print(f"{'Timestamp':<20} {'Overall %':>12} {'Lines':>15} {'Change':>10}")
        print("-"*80)

        for i, snapshot in enumerate(recent):
            timestamp = snapshot["timestamp"][:16]  # Truncate to minute
            percent = snapshot["overall_percent"]
            covered = snapshot["covered_lines"]
            total = snapshot["total_lines"]

            # Calculate change from previous
            if i > 0:
                prev_percent = recent[i-1]["overall_percent"]
                change = percent - prev_percent
                change_str = f"{change:+.2f}%"
            else:
                change_str = "-"

            print(f"{timestamp:<20} {percent:>11.2f}% {covered:>6d}/{total:<6d} {change_str:>10}")

        print("="*80 + "\n")

    def generate_report(self, run_tests: bool = False, save_baseline: bool = False,
                       compare_baseline: bool = False):
        """Generate comprehensive coverage report."""
        # Step 1: Run tests if requested
        if run_tests:
            if not self.run_coverage_tests():
                print("Error: Failed to run coverage tests.")
                return False

        # Step 2: Load coverage data
        coverage_data = self.load_coverage_data()
        if not coverage_data:
            return False

        # Step 3: Extract current snapshot
        current_snapshot = self.extract_snapshot(coverage_data)

        # Step 4: Load baseline if comparing
        baseline = None
        if compare_baseline:
            baseline = self.load_baseline()
            if not baseline:
                print("Warning: No baseline found. Run with --save-baseline first.\n")

        # Step 5: Print summary table
        self.print_summary_table(current_snapshot, baseline)

        # Step 6: Print file coverage table
        self.print_file_coverage_table(coverage_data)

        # Step 7: Print trend analysis
        self.print_trend_analysis()

        # Step 8: Save baseline if requested
        if save_baseline:
            self.save_baseline(current_snapshot)

        # Step 9: Append to history
        self.append_to_history(current_snapshot)

        # Step 10: Print report locations
        print("Generated Reports:")
        print(f"  HTML Report:  {self.html_dir}/index.html")
        print(f"  JSON Report:  {self.coverage_file}")
        if save_baseline:
            print(f"  Baseline:     {self.baseline_file}")
        print()

        return True


def main():
    """Main entry point."""
    # Parse arguments
    run_tests = "--run-tests" in sys.argv
    save_baseline = "--save-baseline" in sys.argv
    compare_baseline = "--compare-baseline" in sys.argv

    # Generate report
    generator = CoverageReportGenerator()
    success = generator.generate_report(
        run_tests=run_tests,
        save_baseline=save_baseline,
        compare_baseline=compare_baseline
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
