#!/usr/bin/env python
"""
Coverage Quality Gates Validator
=================================

Implements 3-tier coverage quality gates for the DIP-SMC-PSO project:

Tier 1 (MINIMUM):
  - Overall coverage >= 85%

Tier 2 (CRITICAL):
  - Core simulation engine >= 95%
  - PSO optimizer >= 95%

Tier 3 (SAFETY-CRITICAL):
  - Controllers >= 95%
  - Plant models >= 95%

Usage:
    python scripts/check_coverage_gates.py
    python scripts/check_coverage_gates.py --xml coverage.xml
    python scripts/check_coverage_gates.py --strict  # Fail on any gate violation

Exit Codes:
    0 - All gates passed
    1 - One or more gates failed
    2 - Coverage report not found or invalid
"""

import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class CoverageGate:
    """Definition of a coverage quality gate."""

    name: str
    tier: int
    threshold: float
    modules: List[str]  # Glob patterns for modules to check
    description: str
    is_safety_critical: bool = False


@dataclass
class GateResult:
    """Result of evaluating a coverage gate."""

    gate: CoverageGate
    passed: bool
    actual_coverage: float
    failing_modules: List[Tuple[str, float]]  # (module_name, coverage)
    message: str


class CoverageGateValidator:
    """Validates coverage against defined quality gates."""

    # Define quality gates (3-tier system)
    GATES = [
        # Tier 1: Overall coverage (MINIMUM)
        CoverageGate(
            name="Overall Coverage",
            tier=1,
            threshold=85.0,
            modules=["*"],  # All modules
            description="Minimum overall coverage for entire codebase",
            is_safety_critical=False,
        ),
        # Tier 2: Critical components
        CoverageGate(
            name="Core Simulation Engine",
            tier=2,
            threshold=95.0,
            modules=[
                "src/core/dynamics.py",
                "src/core/dynamics_full.py",
                "src/core/simulation_runner.py",
                "src/core/simulation_context.py",
                "src/core/vector_sim.py",
            ],
            description="Simulation engine components (critical for correctness)",
            is_safety_critical=False,
        ),
        CoverageGate(
            name="PSO Optimizer",
            tier=2,
            threshold=95.0,
            modules=[
                "src/optimizer/pso_optimizer.py",
                "src/optimizer/*.py",
            ],
            description="PSO optimization algorithms (critical for performance)",
            is_safety_critical=False,
        ),
        # Tier 3: Safety-critical components
        CoverageGate(
            name="Controllers",
            tier=3,
            threshold=95.0,
            modules=[
                "src/controllers/smc/*.py",
                "src/controllers/*.py",
                "src/controllers/base/*.py",
            ],
            description="Control algorithms (safety-critical)",
            is_safety_critical=True,
        ),
        CoverageGate(
            name="Plant Models",
            tier=3,
            threshold=95.0,
            modules=[
                "src/plant/models/*.py",
                "src/plant/core/*.py",
            ],
            description="Physical plant models (safety-critical)",
            is_safety_critical=True,
        ),
    ]

    def __init__(self, coverage_xml_path: str = "coverage.xml"):
        """Initialize validator with coverage report path."""
        self.coverage_xml_path = Path(coverage_xml_path)
        self.module_coverage: Dict[str, float] = {}
        self.overall_coverage: float = 0.0

    def parse_coverage(self) -> bool:
        """Parse coverage.xml and extract per-module coverage.

        Returns:
            True if parsing succeeded, False otherwise.
        """
        if not self.coverage_xml_path.exists():
            print(f"[ERROR] Coverage report not found: {self.coverage_xml_path}")
            print("[INFO] Run: python -m pytest --cov=src --cov-report=xml")
            return False

        try:
            tree = ET.parse(self.coverage_xml_path)
            root = tree.getroot()

            # Get overall coverage from root
            line_rate = float(root.attrib.get("line-rate", 0))
            self.overall_coverage = line_rate * 100

            # Extract per-module coverage
            for package in root.findall(".//package"):
                package_name = package.attrib.get("name", "")

                for class_elem in package.findall(".//class"):
                    filename = class_elem.attrib.get("filename", "")
                    line_rate = float(class_elem.attrib.get("line-rate", 0))
                    coverage_pct = line_rate * 100

                    # Construct module path
                    if package_name and package_name != ".":
                        module_path = f"src/{package_name}/{filename}"
                    else:
                        module_path = f"src/{filename}"

                    # Normalize path separators
                    module_path = module_path.replace("\\", "/")

                    self.module_coverage[module_path] = coverage_pct

            return True

        except ET.ParseError as e:
            print(f"[ERROR] Failed to parse coverage XML: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error parsing coverage: {e}")
            return False

    def match_module(self, module_path: str, pattern: str) -> bool:
        """Check if module path matches glob pattern.

        Args:
            module_path: Module path like "src/core/dynamics.py"
            pattern: Glob pattern like "src/core/*.py" or "*"

        Returns:
            True if module matches pattern.
        """
        if pattern == "*":
            return True

        # Simple glob matching (supports * wildcard)
        import fnmatch

        return fnmatch.fnmatch(module_path, pattern)

    def check_gate(self, gate: CoverageGate) -> GateResult:
        """Evaluate a single coverage gate.

        Args:
            gate: Gate definition to check.

        Returns:
            GateResult with pass/fail status and details.
        """
        # Special case: overall coverage
        if gate.modules == ["*"]:
            passed = self.overall_coverage >= gate.threshold
            message = (
                f"Overall: {self.overall_coverage:.2f}% "
                f"(threshold: {gate.threshold:.1f}%)"
            )
            return GateResult(
                gate=gate,
                passed=passed,
                actual_coverage=self.overall_coverage,
                failing_modules=[],
                message=message,
            )

        # Collect matching modules
        matching_modules = []
        for module_path, coverage in self.module_coverage.items():
            if any(self.match_module(module_path, pattern) for pattern in gate.modules):
                matching_modules.append((module_path, coverage))

        if not matching_modules:
            # No modules found matching patterns
            return GateResult(
                gate=gate,
                passed=True,  # Pass if no modules (not applicable)
                actual_coverage=100.0,
                failing_modules=[],
                message=f"No modules found matching patterns: {gate.modules}",
            )

        # Calculate average coverage for matching modules
        avg_coverage = sum(cov for _, cov in matching_modules) / len(matching_modules)

        # Find failing modules
        failing_modules = [
            (path, cov) for path, cov in matching_modules if cov < gate.threshold
        ]

        passed = avg_coverage >= gate.threshold and len(failing_modules) == 0

        message = (
            f"Avg: {avg_coverage:.2f}% across {len(matching_modules)} modules "
            f"(threshold: {gate.threshold:.1f}%)"
        )

        if failing_modules:
            message += f" - {len(failing_modules)} module(s) below threshold"

        return GateResult(
            gate=gate,
            passed=passed,
            actual_coverage=avg_coverage,
            failing_modules=failing_modules,
            message=message,
        )

    def validate(self, strict: bool = False) -> Tuple[bool, List[GateResult]]:
        """Run all quality gates and return results.

        Args:
            strict: If True, fail on any gate violation (even tier 1).
                   If False, only fail on safety-critical (tier 3) violations.

        Returns:
            Tuple of (all_passed, list of gate results)
        """
        if not self.parse_coverage():
            return False, []

        results = []
        all_passed = True
        tier1_failed = False
        tier2_failed = False
        tier3_failed = False

        for gate in self.GATES:
            result = self.check_gate(gate)
            results.append(result)

            if not result.passed:
                if gate.tier == 1:
                    tier1_failed = True
                elif gate.tier == 2:
                    tier2_failed = True
                elif gate.tier == 3:
                    tier3_failed = True

        # Determine overall pass/fail based on strict mode
        if strict:
            all_passed = not (tier1_failed or tier2_failed or tier3_failed)
        else:
            # In non-strict mode, only tier 3 (safety-critical) failures block
            all_passed = not tier3_failed

        return all_passed, results

    def print_results(self, results: List[GateResult], verbose: bool = True) -> None:
        """Print formatted results to stdout.

        Args:
            results: List of gate results to print.
            verbose: If True, show detailed module breakdowns.
        """
        print("\n" + "=" * 80)
        print("  COVERAGE QUALITY GATES VALIDATION")
        print("=" * 80 + "\n")

        # Group by tier
        tier1_results = [r for r in results if r.gate.tier == 1]
        tier2_results = [r for r in results if r.gate.tier == 2]
        tier3_results = [r for r in results if r.gate.tier == 3]

        def print_tier(tier_name: str, tier_results: List[GateResult]) -> None:
            """Print results for a tier."""
            print(f"\n{tier_name}:")
            print("-" * 80)

            for result in tier_results:
                status = "[PASS]" if result.passed else "[FAIL]"
                safety_marker = " [SAFETY-CRITICAL]" if result.gate.is_safety_critical else ""

                print(f"\n{status} {result.gate.name}{safety_marker}")
                print(f"  {result.gate.description}")
                print(f"  {result.message}")

                if not result.passed and result.failing_modules and verbose:
                    print(f"\n  Failing modules ({len(result.failing_modules)}):")
                    for module, coverage in sorted(
                        result.failing_modules, key=lambda x: x[1]
                    ):
                        print(f"    - {module}: {coverage:.2f}%")

        print_tier("TIER 1: MINIMUM COVERAGE", tier1_results)
        print_tier("TIER 2: CRITICAL COMPONENTS", tier2_results)
        print_tier("TIER 3: SAFETY-CRITICAL COMPONENTS", tier3_results)

        # Summary
        print("\n" + "=" * 80)
        total_passed = sum(1 for r in results if r.passed)
        total_gates = len(results)
        print(f"  SUMMARY: {total_passed}/{total_gates} gates passed")
        print("=" * 80 + "\n")


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate coverage against 3-tier quality gates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--xml",
        default="coverage.xml",
        help="Path to coverage.xml file (default: coverage.xml)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode: fail on any gate violation (default: fail only on tier 3)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress detailed output (show only summary)",
    )

    args = parser.parse_args()

    validator = CoverageGateValidator(coverage_xml_path=args.xml)
    all_passed, results = validator.validate(strict=args.strict)

    if not results:
        print("[ERROR] Failed to validate coverage gates (no coverage data)")
        return 2

    # Print results
    validator.print_results(results, verbose=not args.quiet)

    # Exit code
    if all_passed:
        print("[OK] All required quality gates passed!")
        return 0
    else:
        tier3_failed = any(
            not r.passed for r in results if r.gate.tier == 3
        )

        if tier3_failed:
            print("[ERROR] SAFETY-CRITICAL gates failed - build BLOCKED")
        else:
            print("[WARNING] Coverage gates failed (non-critical)")

        return 1


if __name__ == "__main__":
    sys.exit(main())
