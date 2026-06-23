#======================================================================================\\\
#======================== validate_getting_started.py =================================\\\
#======================================================================================\\\

"""
Automated validation suite for Getting Started Guide (Phase 5.1).

This script validates that the installation and first simulation instructions
in docs/guides/getting-started.md are accurate and work as documented.

Usage:
    python scripts/validation/validate_getting_started.py
    python scripts/validation/validate_getting_started.py --verbose
    python scripts/validation/validate_getting_started.py --controller classical_smc
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Color codes for terminal output (Windows compatible)
try:
    import colorama
    colorama.init()
    GREEN = colorama.Fore.GREEN
    RED = colorama.Fore.RED
    YELLOW = colorama.Fore.YELLOW
    BLUE = colorama.Fore.BLUE
    RESET = colorama.Style.RESET_ALL
except ImportError:
    GREEN = RED = YELLOW = BLUE = RESET = ""


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    test_name: str
    passed: bool
    message: str
    details: Optional[str] = None
    duration_ms: Optional[float] = None


class GettingStartedValidator:
    """Validates Getting Started Guide instructions."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[ValidationResult] = []
        self.repo_root = Path(__file__).resolve().parent.parent.parent

    def run_all_checks(self) -> bool:
        """Run all validation checks and return overall success status."""
        print(f"{BLUE}========================================")
        print("Getting Started Guide Validation")
        print(f"========================================{RESET}\n")

        # Phase 1: Installation validation
        print(f"{BLUE}Phase 1: Installation Validation{RESET}")
        self._check_python_version()
        self._check_repository_structure()
        self._check_simulate_py_help()
        self._check_dependencies()
        print()

        # Phase 2: Controller validation
        print(f"{BLUE}Phase 2: Controller Validation{RESET}")
        self._check_controller("classical_smc")
        self._check_controller("sta_smc")
        self._check_controller("adaptive_smc")
        self._check_controller("hybrid_adaptive_sta_smc")
        print()

        # Phase 3: CLI parameter validation
        print(f"{BLUE}Phase 3: CLI Interface Validation{RESET}")
        self._check_cli_parameters()
        print()

        # Summary
        self._print_summary()

        # Return overall success
        return all(r.passed for r in self.results)

    def _check_python_version(self) -> None:
        """Validate Python version meets requirements (3.9+)."""
        start = time.time()
        try:
            result = subprocess.run(
                ["python", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version_str = result.stdout.strip()

            # Parse version (e.g., "Python 3.12.6")
            parts = version_str.split()
            if len(parts) >= 2:
                version = parts[1]
                major, minor = map(int, version.split(".")[:2])

                if major >= 3 and minor >= 9:
                    self._record_pass(
                        "Python Version Check",
                        f"Python {version} (meets requirement: 3.9+)",
                        time.time() - start
                    )
                else:
                    self._record_fail(
                        "Python Version Check",
                        f"Python {version} is too old (requires 3.9+)",
                        time.time() - start
                    )
            else:
                self._record_fail(
                    "Python Version Check",
                    f"Could not parse version: {version_str}",
                    time.time() - start
                )
        except Exception as e:
            self._record_fail(
                "Python Version Check",
                f"Failed to check Python version: {e}",
                time.time() - start
            )

    def _check_repository_structure(self) -> None:
        """Validate essential files exist."""
        start = time.time()
        essential_files = [
            "simulate.py",
            "config.yaml",
            "requirements.txt",
            "README.md",
            "src/controllers/factory.py",
            "src/core/simulation_runner.py"
        ]

        missing = []
        for file in essential_files:
            if not (self.repo_root / file).exists():
                missing.append(file)

        if not missing:
            self._record_pass(
                "Repository Structure",
                f"All {len(essential_files)} essential files present",
                time.time() - start
            )
        else:
            self._record_fail(
                "Repository Structure",
                f"Missing files: {', '.join(missing)}",
                time.time() - start
            )

    def _check_simulate_py_help(self) -> None:
        """Validate simulate.py --help works."""
        start = time.time()
        try:
            result = subprocess.run(
                ["python", "simulate.py", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.repo_root
            )

            if result.returncode == 0 and "usage:" in result.stdout:
                # Check for documented parameters
                has_controller = "--controller" in result.stdout
                has_plot = "--plot" in result.stdout
                has_pso = "--run-pso" in result.stdout

                if has_controller and has_plot and has_pso:
                    self._record_pass(
                        "simulate.py Help",
                        "Help output displays correctly with all key parameters",
                        time.time() - start
                    )
                else:
                    missing = []
                    if not has_controller: missing.append("--controller")
                    if not has_plot: missing.append("--plot")
                    if not has_pso: missing.append("--run-pso")
                    self._record_fail(
                        "simulate.py Help",
                        f"Help output missing parameters: {', '.join(missing)}",
                        time.time() - start,
                        details=result.stdout
                    )
            else:
                self._record_fail(
                    "simulate.py Help",
                    f"Help command failed (exit code: {result.returncode})",
                    time.time() - start,
                    details=result.stderr
                )
        except Exception as e:
            self._record_fail(
                "simulate.py Help",
                f"Failed to run help command: {e}",
                time.time() - start
            )

    def _check_dependencies(self) -> None:
        """Validate key dependencies are installed."""
        start = time.time()
        dependencies = [
            "numpy",
            "matplotlib",
            "yaml",
            "pyswarms"
        ]

        missing = []
        for dep in dependencies:
            try:
                __import__(dep)
            except ImportError:
                missing.append(dep)

        if not missing:
            self._record_pass(
                "Dependencies",
                f"All {len(dependencies)} key dependencies installed",
                time.time() - start
            )
        else:
            self._record_fail(
                "Dependencies",
                f"Missing dependencies: {', '.join(missing)}",
                time.time() - start
            )

    def _check_controller(self, controller_name: str) -> None:
        """Validate a controller runs successfully."""
        start = time.time()
        try:
            result = subprocess.run(
                [
                    "python", "simulate.py",
                    "--controller", controller_name,
                    "--duration", "0.5",  # Short duration for speed
                ],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.repo_root
            )

            if result.returncode == 0:
                self._record_pass(
                    f"Controller: {controller_name}",
                    f"Simulation completed successfully",
                    time.time() - start
                )
            else:
                self._record_fail(
                    f"Controller: {controller_name}",
                    f"Simulation failed (exit code: {result.returncode})",
                    time.time() - start,
                    details=result.stderr
                )
        except subprocess.TimeoutExpired:
            self._record_fail(
                f"Controller: {controller_name}",
                "Simulation timed out after 30 seconds",
                time.time() - start
            )
        except Exception as e:
            self._record_fail(
                f"Controller: {controller_name}",
                f"Failed to run simulation: {e}",
                time.time() - start
            )

    def _check_cli_parameters(self) -> None:
        """Validate CLI parameters match documentation."""
        start = time.time()

        # Test documented parameters (from getting-started.md)
        documented_params = [
            ("--controller", "classical_smc"),  # Documented as --ctrl
            ("--plot", None),
            ("--run-pso", None),
            ("--save-gains", None),  # Documented as --save
            ("--load-gains", None),  # Documented as --load
        ]

        # Check if documented legacy parameters fail
        try:
            result = subprocess.run(
                ["python", "simulate.py", "--ctrl", "classical_smc"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=self.repo_root
            )

            if result.returncode != 0 and "unrecognized arguments: --ctrl" in result.stderr:
                self._record_fail(
                    "CLI Parameter Consistency",
                    "Documentation uses --ctrl but CLI requires --controller",
                    time.time() - start,
                    details="Getting started guide needs update: --ctrl → --controller, --save → --save-gains, --load → --load-gains"
                )
            else:
                self._record_pass(
                    "CLI Parameter Consistency",
                    "CLI parameters match documentation",
                    time.time() - start
                )
        except Exception as e:
            self._record_fail(
                "CLI Parameter Consistency",
                f"Failed to validate CLI parameters: {e}",
                time.time() - start
            )

    def _record_pass(self, test_name: str, message: str, duration: float) -> None:
        """Record a passed test."""
        result = ValidationResult(
            test_name=test_name,
            passed=True,
            message=message,
            duration_ms=duration * 1000
        )
        self.results.append(result)

        duration_str = f"{duration * 1000:.1f}ms" if duration < 1 else f"{duration:.2f}s"
        print(f"{GREEN}[PASS]{RESET} {test_name}: {message} ({duration_str})")

    def _record_fail(
        self,
        test_name: str,
        message: str,
        duration: float,
        details: Optional[str] = None
    ) -> None:
        """Record a failed test."""
        result = ValidationResult(
            test_name=test_name,
            passed=False,
            message=message,
            details=details,
            duration_ms=duration * 1000
        )
        self.results.append(result)

        duration_str = f"{duration * 1000:.1f}ms" if duration < 1 else f"{duration:.2f}s"
        print(f"{RED}[FAIL]{RESET} {test_name}: {message} ({duration_str})")

        if details and self.verbose:
            print(f"  {YELLOW}Details:{RESET}")
            for line in details.split("\n")[:10]:  # Show first 10 lines
                print(f"    {line}")

    def _print_summary(self) -> None:
        """Print validation summary."""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)

        print(f"\n{BLUE}========================================")
        print("Summary")
        print(f"========================================{RESET}")
        print(f"Total Tests:  {total}")
        print(f"{GREEN}Passed:       {passed}{RESET}")
        print(f"{RED}Failed:       {failed}{RESET}")

        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")

        if failed > 0:
            print(f"\n{YELLOW}Failed Tests:{RESET}")
            for r in self.results:
                if not r.passed:
                    print(f"  - {r.test_name}: {r.message}")

    def export_json(self, output_path: Path) -> None:
        """Export results to JSON file."""
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r.passed),
            "failed": sum(1 for r in self.results if not r.passed),
            "results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details,
                    "duration_ms": r.duration_ms
                }
                for r in self.results
            ]
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\n{GREEN}Results exported to: {output_path}{RESET}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Getting Started Guide instructions"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output for failed tests"
    )
    parser.add_argument(
        "--export",
        type=Path,
        help="Export results to JSON file"
    )

    args = parser.parse_args()

    validator = GettingStartedValidator(verbose=args.verbose)
    success = validator.run_all_checks()

    if args.export:
        validator.export_json(args.export)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
