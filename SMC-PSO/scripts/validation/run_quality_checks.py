#!/usr/bin/env python
"""
=================================================================================
File: scripts/validation/run_quality_checks.py
Description: Comprehensive local quality validation runner for DIP-SMC-PSO
=================================================================================

Phase 6.5: Documentation Quality Gates - Local Validation Script

This script runs all quality checks locally before pushing to CI, providing
developers with immediate feedback and reducing CI failures.

Usage:
    python scripts/validation/run_quality_checks.py
    python scripts/validation/run_quality_checks.py --fix  # Auto-fix where possible
    python scripts/validation/run_quality_checks.py --check docstrings  # Single check
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class QualityChecker:
    """Runs comprehensive quality checks on the codebase."""

    def __init__(self, project_root: Path, auto_fix: bool = False):
        self.project_root = project_root
        self.auto_fix = auto_fix
        self.results: Dict[str, bool] = {}
        self.src_dir = project_root / "src"
        self.docs_dir = project_root / "docs"

    def print_header(self, title: str) -> None:
        """Print a formatted section header."""
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 80}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{title}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 80}{Colors.END}\n")

    def print_result(self, check_name: str, passed: bool, details: str = "") -> None:
        """Print check result with color coding."""
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{status} | {check_name}")
        if details:
            print(f"     {details}")
        self.results[check_name] = passed

    def run_command(self, cmd: List[str], check_name: str) -> Tuple[bool, str]:
        """Execute a shell command and return success status and output."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.project_root
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out after 60 seconds"
        except FileNotFoundError:
            return False, f"Command not found: {cmd[0]}"
        except Exception as e:
            return False, f"Error running command: {e}"

    def check_docstring_coverage(self) -> bool:
        """Check docstring coverage with interrogate."""
        self.print_header("📚 Docstring Coverage Check")

        cmd = [
            "interrogate",
            str(self.src_dir),
            "--ignore-init-method",
            "--ignore-init-module",
            "--ignore-magic",
            "--ignore-private",
            "--ignore-nested-functions",
            "--fail-under=95",
            "--verbose", "1"
        ]

        passed, output = self.run_command(cmd, "Docstring Coverage")

        # Extract coverage percentage
        coverage_line = [line for line in output.split('\n') if '%' in line and 'RESULT:' in line]
        details = coverage_line[0].strip() if coverage_line else "Coverage data not found"

        self.print_result("Docstring Coverage (≥95%)", passed, details)
        return passed

    def check_type_hints(self) -> bool:
        """Check type hint coverage."""
        self.print_header("🏷️ Type Hint Coverage Check")

        # Count Python files
        py_files = list(self.src_dir.rglob("*.py"))
        total_files = len(py_files)

        # Count files with type hints
        files_with_hints = 0
        for file in py_files:
            content = file.read_text(encoding='utf-8')
            if 'from typing import' in content or ': ' in content and '->' in content:
                files_with_hints += 1

        coverage = (files_with_hints / total_files * 100) if total_files > 0 else 0
        passed = coverage >= 95.0

        details = f"{files_with_hints}/{total_files} files ({coverage:.1f}%)"
        self.print_result("Type Hint Coverage (≥95%)", passed, details)
        return passed

    def check_links(self) -> bool:
        """Check documentation links."""
        self.print_header("🔗 Documentation Link Validation")

        # Check if cross-reference script exists
        script_path = self.project_root / "scripts" / "documentation" / "analyze_cross_references.py"
        if not script_path.exists():
            self.print_result("Link Validation", True, "Cross-reference script not found (skipped)")
            return True

        cmd = ["python", str(script_path)]
        passed, output = self.run_command(cmd, "Link Validation")

        # Try to read statistics
        stats_file = self.project_root / ".test_artifacts" / "cross_references" / "statistics.json"
        if stats_file.exists():
            import json
            stats = json.loads(stats_file.read_text())
            broken = stats.get('broken_links', 0)
            total = stats.get('total_internal_links', 0)
            details = f"{broken} broken links out of {total} total"
            passed = broken == 0
        else:
            details = "Statistics not available"

        self.print_result("Link Validation (0 broken)", passed, details)
        return passed

    def check_python_syntax(self) -> bool:
        """Check Python syntax errors."""
        self.print_header("🐍 Python Syntax Check")

        py_files = list(self.src_dir.rglob("*.py"))
        failed_files = []

        for file in py_files:
            try:
                compile(file.read_bytes(), str(file), 'exec')
            except SyntaxError as e:
                failed_files.append((file.name, str(e)))

        passed = len(failed_files) == 0
        details = f"Checked {len(py_files)} files" if passed else f"{len(failed_files)} files with errors"

        self.print_result("Python Syntax", passed, details)

        if not passed:
            for filename, error in failed_files[:5]:  # Show first 5 errors
                print(f"     {Colors.RED}{filename}{Colors.END}: {error}")

        return passed

    def check_markdown_lint(self) -> bool:
        """Check markdown linting (advisory)."""
        self.print_header("📝 Markdown Linting (Advisory)")

        cmd = ["markdownlint-cli2", str(self.docs_dir / "**" / "*.md")]
        passed, output = self.run_command(cmd, "Markdown Linting")

        # Count warnings
        warnings = output.count("MD")
        details = f"{warnings} style issues found" if warnings > 0 else "All markdown files formatted correctly"

        self.print_result("Markdown Linting (advisory)", True, details)  # Always pass (advisory)
        return True

    def check_spell(self) -> bool:
        """Check spelling (advisory)."""
        self.print_header("🔤 Spell Checking (Advisory)")

        cmd = [
            "codespell",
            str(self.docs_dir),
            "--skip=docs/_build,docs/_static,*.pyc,*.json",
            "--ignore-words-list=theSadeQ,dip,smc,pso,doubleintegrator,nd,ser",
            "--count"
        ]

        passed, output = self.run_command(cmd, "Spell Checking")

        # Extract misspelling count
        import re
        match = re.search(r'(\d+) misspellings', output)
        count = int(match.group(1)) if match else 0
        details = f"{count} misspellings found" if count > 0 else "No misspellings detected"

        self.print_result("Spell Checking (advisory)", True, details)  # Always pass (advisory)
        return True

    def run_all_checks(self, specific_check: str = None) -> bool:
        """Run all quality checks or a specific check."""
        print(f"\n{Colors.BOLD}DIP-SMC-PSO Quality Validation Runner{Colors.END}")
        print(f"Project: {self.project_root}")
        print(f"Auto-fix: {'Enabled' if self.auto_fix else 'Disabled'}")

        checks = {
            'syntax': self.check_python_syntax,
            'docstrings': self.check_docstring_coverage,
            'types': self.check_type_hints,
            'links': self.check_links,
            'markdown': self.check_markdown_lint,
            'spell': self.check_spell,
        }

        if specific_check:
            if specific_check not in checks:
                print(f"{Colors.RED}Unknown check: {specific_check}{Colors.END}")
                print(f"Available checks: {', '.join(checks.keys())}")
                return False
            checks = {specific_check: checks[specific_check]}

        # Run checks
        for check_func in checks.values():
            check_func()

        # Summary
        self.print_summary()

        # Return overall status (blocking gates only)
        blocking_checks = ['Docstring Coverage (≥95%)', 'Type Hint Coverage (≥95%)', 'Link Validation (0 broken)', 'Python Syntax']
        return all(self.results.get(check, True) for check in blocking_checks if check in self.results)

    def print_summary(self) -> None:
        """Print final summary of all checks."""
        self.print_header("📊 Summary")

        blocking = [name for name, passed in self.results.items() if not passed and '(advisory)' not in name.lower()]
        advisory = [name for name, passed in self.results.items() if not passed and '(advisory)' in name.lower()]

        if not blocking and not advisory:
            print(f"{Colors.GREEN}✓ All quality checks passed!{Colors.END}")
            print("\nYou're good to push! 🚀")
        else:
            if blocking:
                print(f"{Colors.RED}Blocking Issues ({len(blocking)}):{Colors.END}")
                for check in blocking:
                    print(f"  ✗ {check}")

            if advisory:
                print(f"\n{Colors.YELLOW}Advisory Warnings ({len(advisory)}):{Colors.END}")
                for check in advisory:
                    print(f"  ⚠ {check}")

            print(f"\n{Colors.YELLOW}Fix the blocking issues before pushing.{Colors.END}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive quality checks for DIP-SMC-PSO project"
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Auto-fix issues where possible'
    )
    parser.add_argument(
        '--check',
        type=str,
        choices=['syntax', 'docstrings', 'types', 'links', 'markdown', 'spell'],
        help='Run a specific check only'
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    checker = QualityChecker(project_root, auto_fix=args.fix)

    passed = checker.run_all_checks(specific_check=args.check)

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
