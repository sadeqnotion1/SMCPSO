#===================================================================================\\\
#====================== scripts/coverage/identify_gaps.py ==========================\\\
#===================================================================================\\\

"""
Coverage Gap Identification and Test Planning Tool.

This script analyzes uncovered code and provides actionable recommendations
for test development, prioritized by component criticality.

Usage:
    python scripts/coverage/identify_gaps.py                    # Full analysis
    python scripts/coverage/identify_gaps.py --safety-only      # Safety-critical only
    python scripts/coverage/identify_gaps.py --generate-plan    # Generate test plan JSON

Outputs:
    - Prioritized list of coverage gaps
    - Line-by-line uncovered code analysis
    - Test generation suggestions
    - Test plan JSON for automation
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import re


class CoverageLevel(Enum):
    """Coverage level categorization."""
    SAFETY_CRITICAL = 1  # 100% required
    CRITICAL = 2         # ≥95% required
    GENERAL = 3          # ≥85% required


@dataclass
class CoverageGap:
    """Individual coverage gap with context."""
    file_path: str
    level: CoverageLevel
    missing_lines: List[int]
    missing_branches: List[int]
    percent_covered: float
    lines_total: int
    suggested_tests: List[str]
    priority_score: int  # 1-10, 10 = highest priority


@dataclass
class TestPlan:
    """Test plan for addressing coverage gaps."""
    file_path: str
    test_file_path: str
    level: str
    current_coverage: float
    target_coverage: float
    missing_lines_count: int
    suggested_tests: List[str]
    estimated_hours: float


class GapIdentifier:
    """Identifies and analyzes coverage gaps."""

    # Safety-critical file patterns
    SAFETY_CRITICAL_PATTERNS = [
        "controllers/smc/core/switching_functions.py",
        "controllers/smc/core/sliding_surface.py",
        "controllers/base/control_primitives.py",
        "plant/core/state_validation.py",
    ]

    # Critical file patterns
    CRITICAL_PATTERNS = [
        "controllers/",
        "plant/models/",
        "core/simulation_runner.py",
        "core/dynamics",
        "optimizer/pso_optimizer.py",
    ]

    def __init__(self, coverage_file: Path = Path("coverage.json")):
        self.coverage_file = coverage_file
        self.gaps: List[CoverageGap] = []

    def categorize_file(self, file_path: str) -> CoverageLevel:
        """Categorize file by criticality level."""
        # Check safety-critical first
        for pattern in self.SAFETY_CRITICAL_PATTERNS:
            if pattern in file_path:
                return CoverageLevel.SAFETY_CRITICAL

        # Check critical
        for pattern in self.CRITICAL_PATTERNS:
            if pattern in file_path:
                return CoverageLevel.CRITICAL

        # Default to general
        return CoverageLevel.GENERAL

    def load_coverage_data(self) -> Optional[Dict]:
        """Load coverage data from JSON file."""
        if not self.coverage_file.exists():
            print(f"Error: {self.coverage_file} not found.")
            print("Run: python scripts/coverage/coverage_report.py --run-tests")
            return None

        with open(self.coverage_file, 'r') as f:
            return json.load(f)

    def load_source_file(self, file_path: Path) -> List[str]:
        """Load source file lines for context."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
            return []

    def suggest_tests_for_lines(self, file_path: str, missing_lines: List[int]) -> List[str]:
        """Suggest tests for uncovered lines based on code context."""
        suggestions = []

        # Load source file
        source_file = Path(file_path)
        if not source_file.exists():
            return ["Add unit tests for uncovered lines"]

        source_lines = self.load_source_file(source_file)

        # Analyze uncovered lines for patterns
        for line_num in missing_lines[:5]:  # Analyze first 5 missing lines
            if line_num > len(source_lines):
                continue

            line = source_lines[line_num - 1].strip()

            # Pattern matching for test suggestions
            if "def " in line and "__init__" not in line:
                func_name = re.search(r'def\s+(\w+)', line)
                if func_name:
                    suggestions.append(f"Test function: {func_name.group(1)}()")

            elif "if " in line or "elif " in line:
                suggestions.append(f"Test conditional branch at line {line_num}")

            elif "raise " in line:
                exception = re.search(r'raise\s+(\w+)', line)
                if exception:
                    suggestions.append(f"Test exception handling: {exception.group(1)}")

            elif "return " in line:
                suggestions.append(f"Test return value at line {line_num}")

        # Add general suggestions if no specific ones found
        if not suggestions:
            suggestions.append("Add unit tests for uncovered code paths")

        return suggestions

    def calculate_priority_score(self, gap: CoverageGap) -> int:
        """Calculate priority score for gap (1-10, 10 = highest)."""
        # Base score by level
        if gap.level == CoverageLevel.SAFETY_CRITICAL:
            base_score = 10
        elif gap.level == CoverageLevel.CRITICAL:
            base_score = 7
        else:
            base_score = 4

        # Adjust by coverage percentage (lower coverage = higher priority)
        if gap.percent_covered < 50:
            base_score = min(10, base_score + 2)
        elif gap.percent_covered < 70:
            base_score = min(10, base_score + 1)

        # Adjust by number of missing lines
        if len(gap.missing_lines) > 50:
            base_score = min(10, base_score + 1)

        return base_score

    def identify_gaps(self, coverage_data: Dict, safety_only: bool = False) -> List[CoverageGap]:
        """Identify all coverage gaps from coverage data."""
        gaps = []

        files = coverage_data.get("files", {})

        for file_path, file_data in files.items():
            # Skip non-source files
            if not file_path.startswith("src/"):
                continue

            # Categorize file
            level = self.categorize_file(file_path)

            # Skip non-safety-critical if safety_only mode
            if safety_only and level != CoverageLevel.SAFETY_CRITICAL:
                continue

            # Extract coverage metrics
            summary = file_data.get("summary", {})
            percent_covered = summary.get("percent_covered", 0.0)
            lines_total = summary.get("num_statements", 0)

            # Get missing lines and branches
            missing_lines = file_data.get("missing_lines", [])
            missing_branches = file_data.get("missing_branches", [])

            # Skip if already at target coverage
            target = self.get_target_coverage(level)
            if percent_covered >= target:
                continue

            # Suggest tests
            suggested_tests = self.suggest_tests_for_lines(file_path, missing_lines)

            # Create gap object
            gap = CoverageGap(
                file_path=file_path,
                level=level,
                missing_lines=missing_lines,
                missing_branches=missing_branches,
                percent_covered=percent_covered,
                lines_total=lines_total,
                suggested_tests=suggested_tests,
                priority_score=0  # Will calculate after creation
            )

            # Calculate priority score
            gap.priority_score = self.calculate_priority_score(gap)

            gaps.append(gap)

        # Sort by priority score (highest first)
        gaps.sort(key=lambda g: (-g.priority_score, g.percent_covered))

        self.gaps = gaps
        return gaps

    def get_target_coverage(self, level: CoverageLevel) -> float:
        """Get target coverage percentage for level."""
        if level == CoverageLevel.SAFETY_CRITICAL:
            return 100.0
        elif level == CoverageLevel.CRITICAL:
            return 95.0
        else:
            return 85.0

    def print_gap_analysis(self, gaps: List[CoverageGap], max_display: int = 20):
        """Print detailed gap analysis."""
        print("\n" + "="*90)
        print("                        COVERAGE GAP ANALYSIS")
        print("="*90)

        if not gaps:
            print("\n✓ No coverage gaps found! All targets met.\n")
            return

        print(f"\nTotal Gaps: {len(gaps)}")
        print(f"Displaying top {min(max_display, len(gaps))} by priority\n")

        print(f"{'Priority':<10} {'Level':<20} {'Coverage':<12} {'File':<40}")
        print("-"*90)

        for gap in gaps[:max_display]:
            level_name = gap.level.name.replace("_", " ").title()
            priority_str = f"[{gap.priority_score}/10]"

            print(f"{priority_str:<10} {level_name:<20} {gap.percent_covered:>6.2f}% "
                  f"{gap.file_path.replace('src/', ''):<40}")

        print("="*90 + "\n")

    def print_detailed_gap_report(self, gaps: List[CoverageGap], top_n: int = 5):
        """Print detailed report for top N gaps."""
        print("="*90)
        print(f"                   DETAILED GAP REPORT (Top {top_n})")
        print("="*90 + "\n")

        for i, gap in enumerate(gaps[:top_n], 1):
            level_name = gap.level.name.replace("_", " ").title()
            target = self.get_target_coverage(gap.level)
            deficit = target - gap.percent_covered

            print(f"[{i}] {gap.file_path}")
            print(f"    Level:            {level_name}")
            print(f"    Current Coverage: {gap.percent_covered:.2f}%")
            print(f"    Target Coverage:  {target:.2f}%")
            print(f"    Coverage Deficit: {deficit:.2f}%")
            print(f"    Missing Lines:    {len(gap.missing_lines)} lines")
            print(f"    Priority Score:   {gap.priority_score}/10")
            print("\n    Suggested Tests:")
            for j, test in enumerate(gap.suggested_tests[:3], 1):
                print(f"      {j}. {test}")
            print()

        print("="*90 + "\n")

    def generate_test_plan(self, gaps: List[CoverageGap]) -> List[TestPlan]:
        """Generate test plan for addressing gaps."""
        test_plans = []

        for gap in gaps:
            # Determine test file path
            test_file_path = gap.file_path.replace("src/", "tests/test_")
            test_file_path = test_file_path.replace(".py", "_test.py")

            # Estimate hours based on missing lines
            lines_to_cover = len(gap.missing_lines)
            estimated_hours = max(0.5, min(8.0, lines_to_cover * 0.1))  # 0.1 hours per line, capped

            # Target coverage
            target = self.get_target_coverage(gap.level)

            plan = TestPlan(
                file_path=gap.file_path,
                test_file_path=test_file_path,
                level=gap.level.name,
                current_coverage=gap.percent_covered,
                target_coverage=target,
                missing_lines_count=len(gap.missing_lines),
                suggested_tests=gap.suggested_tests,
                estimated_hours=estimated_hours
            )

            test_plans.append(plan)

        return test_plans

    def save_test_plan(self, test_plans: List[TestPlan], output_file: Path = Path("test_plan.json")):
        """Save test plan to JSON file."""
        plans_dict = [asdict(plan) for plan in test_plans]

        with open(output_file, 'w') as f:
            json.dump(plans_dict, f, indent=2)

        print(f"✓ Test plan saved to {output_file}")


def main():
    """Main entry point."""
    # Parse arguments
    safety_only = "--safety-only" in sys.argv
    generate_plan = "--generate-plan" in sys.argv

    # Initialize identifier
    identifier = GapIdentifier()

    # Load coverage data
    coverage_data = identifier.load_coverage_data()
    if not coverage_data:
        sys.exit(1)

    # Identify gaps
    gaps = identifier.identify_gaps(coverage_data, safety_only=safety_only)

    # Print gap analysis
    identifier.print_gap_analysis(gaps)

    # Print detailed report for top gaps
    identifier.print_detailed_gap_report(gaps, top_n=5)

    # Generate and save test plan if requested
    if generate_plan:
        test_plans = identifier.generate_test_plan(gaps)
        identifier.save_test_plan(test_plans)

        # Print summary
        total_hours = sum(plan.estimated_hours for plan in test_plans)
        print("\nTest Plan Summary:")
        print(f"  Total Files:       {len(test_plans)}")
        print(f"  Estimated Hours:   {total_hours:.1f}")
        print(f"  Safety-Critical:   {sum(1 for p in test_plans if p.level == 'SAFETY_CRITICAL')}")
        print(f"  Critical:          {sum(1 for p in test_plans if p.level == 'CRITICAL')}")
        print(f"  General:           {sum(1 for p in test_plans if p.level == 'GENERAL')}")
        print()


if __name__ == "__main__":
    main()
