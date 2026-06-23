#!/usr/bin/env python
"""
Documentation Validation Script for DIP-SMC-PSO Project

Validates generated documentation files to ensure:
- All literalinclude paths are valid
- All cross-references resolve correctly
- Documentation coverage is complete
- No broken links exist

Usage:
    python scripts/docs/validate_code_docs.py --check-paths
    python scripts/docs/validate_code_docs.py --coverage-report
    python scripts/docs/validate_code_docs.py --check-all
"""

import argparse
import re
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
import sys

@dataclass
class ValidationResult:
    """Result of a validation check."""
    passed: bool
    message: str
    details: List[str] = None


class DocumentationValidator:
    """Validates generated Sphinx documentation."""

    def __init__(self, project_root: Path, docs_root: Path):
        self.project_root = project_root
        self.docs_root = docs_root
        self.src_dir = project_root / 'src'
        self.reference_dir = docs_root / 'reference'

        self.errors = []
        self.warnings = []

    def validate_literalinclude_paths(self) -> ValidationResult:
        """Validate all literalinclude directive paths."""
        print("Validating literalinclude paths...")

        invalid_paths = []
        total_directives = 0

        # Find all markdown files
        md_files = list(self.reference_dir.rglob('*.md'))

        for md_file in md_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find all literalinclude directives
            pattern = r'```\{literalinclude\}\s+([^\n]+)'
            matches = re.findall(pattern, content)

            for source_path in matches:
                total_directives += 1
                # Resolve relative path from markdown file
                absolute_path = (md_file.parent / source_path).resolve()

                if not absolute_path.exists():
                    invalid_paths.append({
                        'doc_file': md_file.relative_to(self.docs_root),
                        'source_path': source_path,
                        'resolved': absolute_path
                    })

        if invalid_paths:
            details = [
                f"{item['doc_file']}: {item['source_path']} -> {item['resolved']}"
                for item in invalid_paths
            ]
            return ValidationResult(
                passed=False,
                message=f"Found {len(invalid_paths)} invalid literalinclude paths out of {total_directives} total",
                details=details
            )

        return ValidationResult(
            passed=True,
            message=f"All {total_directives} literalinclude paths are valid",
            details=[]
        )

    def validate_coverage(self) -> ValidationResult:
        """Check documentation coverage of Python files."""
        print("Checking documentation coverage...")

        # Find all Python files in src/
        py_files = set(self.src_dir.rglob('*.py'))
        py_files = {f for f in py_files if '__pycache__' not in str(f)}

        # Find all documented files
        md_files = list(self.reference_dir.rglob('*.md'))
        documented_sources = set()

        for md_file in md_files:
            if md_file.name == 'index.md':
                continue

            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract source path from header
            match = re.search(r'\*\*Source:\*\*\s+`([^`]+)`', content)
            if match:
                source_path = match.group(1).replace('\\', '/')
                source_file = self.project_root / source_path
                if source_file.exists():
                    documented_sources.add(source_file)

        # Calculate coverage
        total_files = len(py_files)
        documented_files = len(documented_sources)
        undocumented = py_files - documented_sources

        coverage_percent = (documented_files / total_files * 100) if total_files > 0 else 0

        if coverage_percent < 95:
            details = [str(f.relative_to(self.src_dir)) for f in sorted(undocumented)]
            return ValidationResult(
                passed=False,
                message=f"Documentation coverage: {coverage_percent:.1f}% ({documented_files}/{total_files} files)",
                details=details[:10]  # Show first 10 undocumented files
            )

        return ValidationResult(
            passed=True,
            message=f"Documentation coverage: {coverage_percent:.1f}% ({documented_files}/{total_files} files)",
            details=[]
        )

    def validate_toctree_entries(self) -> ValidationResult:
        """Validate that all toctree entries point to existing files."""
        print("Validating toctree entries...")

        broken_references = []
        total_references = 0

        # Find all index.md files with toctrees
        index_files = list(self.reference_dir.rglob('index.md'))

        for index_file in index_files:
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract toctree entries
            toctree_pattern = r'```\{toctree\}.*?\n(.*?)```'
            matches = re.findall(toctree_pattern, content, re.DOTALL)

            for toctree_content in matches:
                # Extract file references
                lines = toctree_content.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith(':'):
                        continue

                    total_references += 1
                    # Convert toctree reference to file path
                    ref_path = index_file.parent / (line + '.md')

                    if not ref_path.exists():
                        broken_references.append({
                            'index_file': index_file.relative_to(self.docs_root),
                            'reference': line,
                            'expected_path': ref_path.relative_to(self.docs_root)
                        })

        if broken_references:
            details = [
                f"{item['index_file']}: {item['reference']} -> {item['expected_path']}"
                for item in broken_references
            ]
            return ValidationResult(
                passed=False,
                message=f"Found {len(broken_references)} broken toctree references out of {total_references} total",
                details=details
            )

        return ValidationResult(
            passed=True,
            message=f"All {total_references} toctree references are valid",
            details=[]
        )

    def validate_syntax(self) -> ValidationResult:
        """Check for Sphinx syntax errors in markdown files."""
        print("Checking Sphinx directive syntax...")

        syntax_errors = []

        md_files = list(self.reference_dir.rglob('*.md'))

        for md_file in md_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for common syntax errors
            errors = []

            # Check for unclosed code blocks
            if content.count('```') % 2 != 0:
                errors.append("Unclosed code block (mismatched ```)")

            # Check for malformed directives
            if re.search(r'```\{[^}]+$', content, re.MULTILINE):
                errors.append("Malformed directive (unclosed {)")

            # Check for literalinclude without language
            literalinclude_blocks = re.findall(r'```\{literalinclude\}[^`]*```', content, re.DOTALL)
            for block in literalinclude_blocks:
                if ':language:' not in block:
                    errors.append("literalinclude directive missing :language: option")

            if errors:
                syntax_errors.append({
                    'file': md_file.relative_to(self.docs_root),
                    'errors': errors
                })

        if syntax_errors:
            details = []
            for item in syntax_errors:
                details.append(f"{item['file']}:")
                for error in item['errors']:
                    details.append(f"  - {error}")

            return ValidationResult(
                passed=False,
                message=f"Found syntax errors in {len(syntax_errors)} files",
                details=details[:20]
            )

        return ValidationResult(
            passed=True,
            message=f"No syntax errors found in {len(md_files)} documentation files",
            details=[]
        )

    def run_all_validations(self) -> Dict[str, ValidationResult]:
        """Run all validation checks."""
        results = {
            'literalinclude_paths': self.validate_literalinclude_paths(),
            'coverage': self.validate_coverage(),
            'toctree_entries': self.validate_toctree_entries(),
            'syntax': self.validate_syntax()
        }

        return results

    def print_results(self, results: Dict[str, ValidationResult]):
        """Print validation results in a formatted way."""
        print("\n" + "="*80)
        print("DOCUMENTATION VALIDATION RESULTS")
        print("="*80)

        total_checks = len(results)
        passed_checks = sum(1 for r in results.values() if r.passed)

        for check_name, result in results.items():
            status = "[PASS]" if result.passed else "[FAIL]"
            print(f"\n{status}: {check_name.replace('_', ' ').title()}")
            print(f"  {result.message}")

            if result.details:
                print("\n  Details:")
                for detail in result.details[:10]:  # Show first 10 details
                    print(f"    - {detail}")
                if len(result.details) > 10:
                    print(f"    ... and {len(result.details) - 10} more")

        print("\n" + "="*80)
        print(f"Overall: {passed_checks}/{total_checks} checks passed")
        print("="*80 + "\n")

        return passed_checks == total_checks


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate generated Sphinx documentation'
    )

    parser.add_argument(
        '--check-paths', action='store_true',
        help='Validate literalinclude paths'
    )
    parser.add_argument(
        '--coverage-report', action='store_true',
        help='Check documentation coverage'
    )
    parser.add_argument(
        '--check-toctree', action='store_true',
        help='Validate toctree references'
    )
    parser.add_argument(
        '--check-syntax', action='store_true',
        help='Check Sphinx syntax'
    )
    parser.add_argument(
        '--check-all', action='store_true',
        help='Run all validation checks'
    )

    args = parser.parse_args()

    # Set up paths
    project_root = Path(__file__).parent.parent.parent
    docs_root = project_root / 'docs'

    validator = DocumentationValidator(project_root, docs_root)

    # Determine which checks to run
    if args.check_all or not any([args.check_paths, args.coverage_report,
                                   args.check_toctree, args.check_syntax]):
        # Run all checks
        results = validator.run_all_validations()
        all_passed = validator.print_results(results)
        sys.exit(0 if all_passed else 1)

    # Run individual checks
    results = {}

    if args.check_paths:
        results['literalinclude_paths'] = validator.validate_literalinclude_paths()

    if args.coverage_report:
        results['coverage'] = validator.validate_coverage()

    if args.check_toctree:
        results['toctree_entries'] = validator.validate_toctree_entries()

    if args.check_syntax:
        results['syntax'] = validator.validate_syntax()

    all_passed = validator.print_results(results)
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
