#==========================================================================================\\\
#=============== scripts/docs_organization/enforce_naming_conventions.py ==============\\\
#==========================================================================================\\\

"""File Naming Convention Enforcement Tool.

This script validates file naming patterns across the project to ensure
consistency with snake_case for Python files and kebab-case for documentation.

Usage:
    python enforce_naming_conventions.py --check      # Check compliance
    python enforce_naming_conventions.py --report     # Generate report
    python enforce_naming_conventions.py --suggest    # Suggest corrections

Naming Rules:
    - Python files: snake_case.py (e.g., classical_smc.py)
    - Markdown docs: kebab-case.md or UPPERCASE.md (e.g., user-guide.md, README.md)
    - Config files: lowercase with underscores (e.g., pytest.ini, .gitignore)
    - Test files: test_*.py pattern
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional


class NamingValidator:
    """Validates file naming conventions."""

    # Naming patterns
    SNAKE_CASE = re.compile(r'^[a-z0-9_]+$')
    KEBAB_CASE = re.compile(r'^[a-z0-9\-]+$')
    UPPER_CASE = re.compile(r'^[A-Z0-9_]+$')
    TEST_PATTERN = re.compile(r'^test_[a-z0-9_]+$')

    # Excluded directories
    EXCLUDED_DIRS = {
        '.git', '__pycache__', '.pytest_cache', '.venv', 'venv',
        'node_modules', '.tox', '.eggs', 'dist', 'build',
        '.archive', '.build', '.dev_tools', '.tools', '.benchmarks',
        '.github', '.streamlit', '.claude'
    }

    # Special allowed names
    SPECIAL_NAMES = {
        'README.md', 'CHANGELOG.md', 'LICENSE', 'CONTRIBUTING.md',
        'CLAUDE.md', 'Makefile', 'Dockerfile', '.gitignore',
        'requirements.txt', 'setup.py', 'setup.cfg', 'pyproject.toml',
        'pytest.ini', 'tox.ini', '.flake8', '.pylintrc'
    }

    def __init__(self, project_root: Path):
        """Initialize naming validator.

        Args:
            project_root: Absolute path to project root
        """
        self.project_root = project_root
        self.violations: List[Dict] = []

    def validate_python_file(self, filepath: Path) -> Optional[Dict]:
        """Validate Python file naming.

        Args:
            filepath: Absolute path to Python file

        Returns:
            Violation dictionary if non-compliant, None otherwise
        """
        stem = filepath.stem

        # Check if it's a test file
        if stem.startswith('test_'):
            if not self.TEST_PATTERN.match(stem):
                return {
                    'file': filepath,
                    'violation': 'invalid_test_name',
                    'message': f"Test file '{stem}' must match pattern: test_[snake_case]",
                    'suggestion': self._suggest_snake_case(stem)
                }
        else:
            # Regular Python file - must be snake_case
            if not self.SNAKE_CASE.match(stem):
                return {
                    'file': filepath,
                    'violation': 'not_snake_case',
                    'message': f"Python file '{stem}' must use snake_case",
                    'suggestion': self._suggest_snake_case(stem)
                }

        return None

    def validate_markdown_file(self, filepath: Path) -> Optional[Dict]:
        """Validate Markdown file naming.

        Args:
            filepath: Absolute path to Markdown file

        Returns:
            Violation dictionary if non-compliant, None otherwise
        """
        name = filepath.name
        stem = filepath.stem

        # Check if it's a special allowed name
        if name in self.SPECIAL_NAMES:
            return None

        # Check if it's uppercase (README-style)
        if self.UPPER_CASE.match(stem):
            return None

        # Otherwise must be kebab-case
        if not self.KEBAB_CASE.match(stem):
            return {
                'file': filepath,
                'violation': 'not_kebab_case',
                'message': f"Markdown file '{stem}' must use kebab-case or UPPERCASE",
                'suggestion': self._suggest_kebab_case(stem)
            }

        return None

    def validate_config_file(self, filepath: Path) -> Optional[Dict]:
        """Validate configuration file naming.

        Args:
            filepath: Absolute path to config file

        Returns:
            Violation dictionary if non-compliant, None otherwise
        """
        name = filepath.name

        # Check if it's a special allowed name
        if name in self.SPECIAL_NAMES:
            return None

        stem = filepath.stem

        # Config files should be lowercase with underscores or dots
        if not re.match(r'^[a-z0-9_\.]+$', stem):
            return {
                'file': filepath,
                'violation': 'invalid_config_name',
                'message': f"Config file '{stem}' should use lowercase_with_underscores",
                'suggestion': stem.lower().replace('-', '_').replace(' ', '_')
            }

        return None

    def _suggest_snake_case(self, name: str) -> str:
        """Generate snake_case suggestion.

        Args:
            name: Original filename

        Returns:
            Suggested snake_case filename
        """
        # Replace hyphens with underscores
        suggestion = name.replace('-', '_')

        # Split on capital letters and join with underscores
        suggestion = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', suggestion)

        # Lowercase everything
        suggestion = suggestion.lower()

        # Remove duplicate underscores
        suggestion = re.sub(r'_+', '_', suggestion)

        # Remove leading/trailing underscores
        suggestion = suggestion.strip('_')

        return suggestion

    def _suggest_kebab_case(self, name: str) -> str:
        """Generate kebab-case suggestion.

        Args:
            name: Original filename

        Returns:
            Suggested kebab-case filename
        """
        # Replace underscores with hyphens
        suggestion = name.replace('_', '-')

        # Split on capital letters and join with hyphens
        suggestion = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', suggestion)

        # Lowercase everything
        suggestion = suggestion.lower()

        # Remove duplicate hyphens
        suggestion = re.sub(r'-+', '-', suggestion)

        # Remove leading/trailing hyphens
        suggestion = suggestion.strip('-')

        return suggestion

    def scan_directory(self) -> List[Dict]:
        """Scan project directory for naming violations.

        Returns:
            List of violation dictionaries
        """
        self.violations = []

        # File type handlers
        handlers = {
            '.py': self.validate_python_file,
            '.md': self.validate_markdown_file,
            '.yaml': self.validate_config_file,
            '.yml': self.validate_config_file,
            '.toml': self.validate_config_file,
            '.ini': self.validate_config_file,
            '.cfg': self.validate_config_file,
        }

        # Scan all files
        for filepath in self.project_root.rglob('*'):
            # Skip directories
            if filepath.is_dir():
                continue

            # Skip excluded directories
            if any(excluded in filepath.parts for excluded in self.EXCLUDED_DIRS):
                continue

            # Skip special allowed names
            if filepath.name in self.SPECIAL_NAMES:
                continue

            # Validate based on extension
            extension = filepath.suffix
            if extension in handlers:
                violation = handlers[extension](filepath)
                if violation:
                    self.violations.append(violation)

        return self.violations

    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """Generate naming compliance report.

        Args:
            output_path: Optional path to save report

        Returns:
            Report as formatted string
        """
        total_files = sum(
            1 for _ in self.project_root.rglob('*')
            if _.is_file() and not any(
                excluded in _.parts for excluded in self.EXCLUDED_DIRS
            )
        )

        violation_count = len(self.violations)
        compliant_count = total_files - violation_count
        compliance_rate = (
            (compliant_count / total_files * 100) if total_files > 0 else 0
        )

        # Group violations by type
        violations_by_type = {}
        for violation in self.violations:
            vtype = violation['violation']
            if vtype not in violations_by_type:
                violations_by_type[vtype] = []
            violations_by_type[vtype].append(violation)

        report_lines = [
            "=" * 90,
            "FILE NAMING CONVENTION COMPLIANCE REPORT",
            "=" * 90,
            f"\nTotal Files Scanned: {total_files}",
            f"Compliant Files: {compliant_count}",
            f"Violations Found: {violation_count}",
            f"Compliance Rate: {compliance_rate:.1f}%",
            "\n" + "=" * 90,
            "VIOLATIONS BY TYPE:",
            "=" * 90,
        ]

        for vtype, violations in violations_by_type.items():
            report_lines.append(f"\n{vtype.replace('_', ' ').upper()} ({len(violations)}):")
            for violation in violations:
                rel_path = violation['file'].relative_to(self.project_root)
                report_lines.append(f"  ✗ {rel_path}")
                report_lines.append(f"    {violation['message']}")
                report_lines.append(f"    Suggestion: {violation['suggestion']}")

        report = "\n".join(report_lines)

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)

        return report


def main() -> None:
    """Main entry point for naming convention enforcement tool."""
    parser = argparse.ArgumentParser(
        description="Validate and enforce file naming conventions"
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check naming compliance'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate detailed compliance report'
    )
    parser.add_argument(
        '--suggest',
        action='store_true',
        help='Show suggestions for fixing violations'
    )
    parser.add_argument(
        '--root',
        type=str,
        default='.',
        help='Project root directory (default: current directory)'
    )

    args = parser.parse_args()

    # Resolve project root
    project_root = Path(args.root).resolve()

    print(f"Scanning project: {project_root}\n")

    # Create validator and scan
    validator = NamingValidator(project_root)
    violations = validator.scan_directory()

    # Calculate compliance
    total_files = sum(
        1 for _ in project_root.rglob('*')
        if _.is_file() and not any(
            excluded in _.parts for excluded in validator.EXCLUDED_DIRS
        )
    )

    compliant = total_files - len(violations)
    compliance_rate = (compliant / total_files * 100) if total_files > 0 else 0

    print(f"Compliance Rate: {compliance_rate:.1f}% ({compliant}/{total_files})")
    print(f"Violations Found: {len(violations)}\n")

    # Report mode
    if args.report:
        report_path = project_root / 'artifacts' / 'naming_conventions_report.txt'
        report = validator.generate_report(report_path)
        print(f"Report saved to: {report_path}\n")
        print(report)

    # Check/suggest mode
    if args.check or args.suggest or not args.report:
        if violations:
            print("Violations Found:")
            for violation in violations:
                rel_path = violation['file'].relative_to(project_root)
                print(f"\n  ✗ {rel_path}")
                print(f"    {violation['message']}")
                if args.suggest:
                    print(f"    Suggestion: {violation['suggestion']}")
        else:
            print("✓ All files comply with naming conventions!")


if __name__ == '__main__':
    main()