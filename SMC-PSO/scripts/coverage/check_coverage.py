#===================================================================================\\\
#======================== scripts/coverage/check_coverage.py =======================\\\
#===================================================================================\\\

"""
Real-Time Coverage Analysis Script.

This script parses coverage.json and provides component-level breakdown
with color-coded terminal output for quick assessment.

Usage:
    python scripts/coverage/check_coverage.py
    python scripts/coverage/check_coverage.py --json  # Output JSON format
    python scripts/coverage/check_coverage.py --ci    # CI mode (exit codes)

Exit Codes (CI mode):
    0: All coverage targets met (≥85% overall, ≥95% critical, 100% safety-critical)
    1: Overall coverage below 85%
    2: Critical components below 95%
    3: Safety-critical components below 100%
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class CoverageLevel(Enum):
    """Coverage level categorization."""
    SAFETY_CRITICAL = "safety_critical"  # 100% required
    CRITICAL = "critical"                # ≥95% required
    GENERAL = "general"                  # ≥85% required


@dataclass
class ComponentCoverage:
    """Coverage data for a single component."""
    name: str
    level: CoverageLevel
    percent_covered: float
    lines_covered: int
    lines_total: int
    branches_covered: int
    branches_total: int
    missing_lines: List[int]


class CoverageColors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def get_color_for_coverage(percent: float, level: CoverageLevel) -> str:
    """Get appropriate color based on coverage percentage and level."""
    if level == CoverageLevel.SAFETY_CRITICAL:
        threshold = 100.0
    elif level == CoverageLevel.CRITICAL:
        threshold = 95.0
    else:  # GENERAL
        threshold = 85.0

    if percent >= threshold:
        return CoverageColors.GREEN
    elif percent >= threshold - 10:
        return CoverageColors.YELLOW
    else:
        return CoverageColors.RED


def load_coverage_data(coverage_file: Path = Path("coverage.json")) -> Dict:
    """Load coverage data from JSON file."""
    if not coverage_file.exists():
        print(f"{CoverageColors.RED}Error: {coverage_file} not found.{CoverageColors.RESET}")
        print(f"{CoverageColors.YELLOW}Run: pytest --cov=src --cov-report=json{CoverageColors.RESET}")
        sys.exit(1)

    with open(coverage_file, 'r') as f:
        return json.load(f)


def categorize_component(file_path: str) -> CoverageLevel:
    """Categorize component based on file path."""
    # Safety-critical components (100% coverage required)
    safety_critical_patterns = [
        "controllers/smc/core/switching_functions.py",
        "controllers/smc/core/sliding_surface.py",
        "controllers/base/control_primitives.py",
        "plant/core/state_validation.py",
    ]

    # Critical components (≥95% coverage required)
    critical_patterns = [
        "controllers/",
        "plant/models/",
        "core/simulation_runner.py",
        "core/dynamics",
        "optimizer/pso_optimizer.py",
    ]

    # Check safety-critical first
    for pattern in safety_critical_patterns:
        if pattern in file_path:
            return CoverageLevel.SAFETY_CRITICAL

    # Check critical
    for pattern in critical_patterns:
        if pattern in file_path:
            return CoverageLevel.CRITICAL

    # Default to general
    return CoverageLevel.GENERAL


def parse_coverage_by_component(coverage_data: Dict) -> List[ComponentCoverage]:
    """Parse coverage data and organize by component."""
    components = []

    files = coverage_data.get("files", {})

    for file_path, file_data in files.items():
        # Normalize path separators (Windows backslash to forward slash)
        file_path_normalized = file_path.replace("\\", "/")

        # Skip non-source files
        if not file_path_normalized.startswith("src/"):
            continue

        summary = file_data.get("summary", {})

        # Extract coverage metrics
        percent_covered = summary.get("percent_covered", 0.0)
        lines_covered = summary.get("covered_lines", 0)
        lines_total = summary.get("num_statements", 0)
        branches_covered = summary.get("covered_branches", 0)
        branches_total = summary.get("num_branches", 0)

        # Get missing lines
        missing_lines = file_data.get("missing_lines", [])

        # Categorize component (use normalized path)
        level = categorize_component(file_path_normalized)

        # Simplify file path for display (use normalized path)
        display_name = file_path_normalized.replace("src/", "")

        component = ComponentCoverage(
            name=display_name,
            level=level,
            percent_covered=percent_covered,
            lines_covered=lines_covered,
            lines_total=lines_total,
            branches_covered=branches_covered,
            branches_total=branches_total,
            missing_lines=missing_lines
        )

        components.append(component)

    return components


def calculate_aggregate_coverage(components: List[ComponentCoverage], level: CoverageLevel = None) -> Tuple[float, int, int]:
    """Calculate aggregate coverage for components at a specific level."""
    filtered = [c for c in components if level is None or c.level == level]

    if not filtered:
        return 0.0, 0, 0

    total_covered = sum(c.lines_covered for c in filtered)
    total_lines = sum(c.lines_total for c in filtered)

    if total_lines == 0:
        return 0.0, 0, 0

    percent = (total_covered / total_lines) * 100
    return percent, total_covered, total_lines


def print_coverage_summary(components: List[ComponentCoverage], output_json: bool = False):
    """Print coverage summary with color-coded output."""
    if output_json:
        # JSON output for programmatic consumption
        output = {
            "overall": {},
            "by_level": {},
            "components": []
        }

        # Calculate aggregate metrics
        overall_pct, overall_covered, overall_total = calculate_aggregate_coverage(components)
        output["overall"] = {
            "percent": round(overall_pct, 2),
            "covered": overall_covered,
            "total": overall_total
        }

        # By level
        for level in CoverageLevel:
            pct, covered, total = calculate_aggregate_coverage(components, level)
            output["by_level"][level.value] = {
                "percent": round(pct, 2),
                "covered": covered,
                "total": total
            }

        # Component details
        for comp in components:
            output["components"].append({
                "name": comp.name,
                "level": comp.level.value,
                "percent": round(comp.percent_covered, 2),
                "covered": comp.lines_covered,
                "total": comp.lines_total,
                "branches_covered": comp.branches_covered,
                "branches_total": comp.branches_total,
                "missing_lines_count": len(comp.missing_lines)
            })

        print(json.dumps(output, indent=2))
        return

    # Terminal output with colors (ASCII-safe for Windows cp1252)
    print(f"\n{CoverageColors.BOLD}{CoverageColors.BLUE}{'='*70}{CoverageColors.RESET}")
    print(f"{CoverageColors.BOLD}{CoverageColors.BLUE}     DIP SMC PSO Coverage Analysis Report{CoverageColors.RESET}")
    print(f"{CoverageColors.BOLD}{CoverageColors.BLUE}{'='*70}{CoverageColors.RESET}\n")

    # Overall summary
    overall_pct, overall_covered, overall_total = calculate_aggregate_coverage(components)
    overall_color = get_color_for_coverage(overall_pct, CoverageLevel.GENERAL)

    print(f"{CoverageColors.BOLD}Overall Coverage:{CoverageColors.RESET}")
    print(f"  {overall_color}{overall_pct:6.2f}%{CoverageColors.RESET} ({overall_covered}/{overall_total} lines)")
    print(f"  Target: {CoverageColors.GREEN}>=85%{CoverageColors.RESET}")
    print()

    # By level summary
    print(f"{CoverageColors.BOLD}Coverage by Level:{CoverageColors.RESET}")

    for level in [CoverageLevel.SAFETY_CRITICAL, CoverageLevel.CRITICAL, CoverageLevel.GENERAL]:
        pct, covered, total = calculate_aggregate_coverage(components, level)
        color = get_color_for_coverage(pct, level)

        if level == CoverageLevel.SAFETY_CRITICAL:
            label = "Safety-Critical"
            target = "100%"
        elif level == CoverageLevel.CRITICAL:
            label = "Critical"
            target = ">=95%"
        else:
            label = "General"
            target = ">=85%"

        print(f"  {label:20s}: {color}{pct:6.2f}%{CoverageColors.RESET} ({covered}/{total} lines) - Target: {target}")

    print()

    # Component breakdown (top 10 lowest coverage)
    print(f"{CoverageColors.BOLD}Top 10 Components Needing Improvement:{CoverageColors.RESET}")

    sorted_components = sorted(components, key=lambda c: c.percent_covered)[:10]

    for comp in sorted_components:
        color = get_color_for_coverage(comp.percent_covered, comp.level)
        level_badge = comp.level.value[:4].upper()

        print(f"  [{level_badge}] {color}{comp.percent_covered:6.2f}%{CoverageColors.RESET} {comp.name}")
        print(f"         ({comp.lines_covered}/{comp.lines_total} lines, {len(comp.missing_lines)} missing)")

    print()


def check_coverage_gates(components: List[ComponentCoverage]) -> int:
    """Check coverage gates and return appropriate exit code."""
    overall_pct, _, _ = calculate_aggregate_coverage(components)
    critical_pct, _, _ = calculate_aggregate_coverage(components, CoverageLevel.CRITICAL)
    safety_pct, _, _ = calculate_aggregate_coverage(components, CoverageLevel.SAFETY_CRITICAL)

    # Check gates (priority order)
    if safety_pct < 100.0:
        print(f"{CoverageColors.RED}✗ FAIL: Safety-critical coverage {safety_pct:.2f}% < 100%{CoverageColors.RESET}")
        return 3

    if critical_pct < 95.0:
        print(f"{CoverageColors.RED}✗ FAIL: Critical coverage {critical_pct:.2f}% < 95%{CoverageColors.RESET}")
        return 2

    if overall_pct < 85.0:
        print(f"{CoverageColors.RED}✗ FAIL: Overall coverage {overall_pct:.2f}% < 85%{CoverageColors.RESET}")
        return 1

    print(f"{CoverageColors.GREEN}✓ PASS: All coverage gates met{CoverageColors.RESET}")
    return 0


def main():
    """Main entry point."""
    # Parse arguments
    output_json = "--json" in sys.argv
    ci_mode = "--ci" in sys.argv

    # Load coverage data
    coverage_data = load_coverage_data()

    # Parse by component
    components = parse_coverage_by_component(coverage_data)

    if not components:
        print(f"{CoverageColors.YELLOW}Warning: No source files found in coverage data{CoverageColors.RESET}")
        sys.exit(1)

    # Print summary
    print_coverage_summary(components, output_json=output_json)

    # Check gates if in CI mode
    if ci_mode:
        exit_code = check_coverage_gates(components)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
