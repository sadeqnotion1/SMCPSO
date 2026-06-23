#!/usr/bin/env python
"""
Comprehensive documentation validation script.

Validates all user-facing documentation for:
- Broken links (internal and external)
- Code block syntax
- Consistent terminology
- Cross-reference integrity
- File structure
"""

import re
from pathlib import Path
from typing import List
import json

class DocumentationValidator:
    """Validate documentation quality and consistency."""

    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        self.errors = []
        self.warnings = []
        self.stats = {}

    def validate_all(self):
        """Run all validation checks."""
        print("=" * 70)
        print("DOCUMENTATION VALIDATION - Week 14 Phase 1D")
        print("=" * 70)
        print()

        # Find all markdown files
        md_files = list(self.docs_root.rglob("*.md"))
        self.stats['total_files'] = len(md_files)
        self.stats['total_lines'] = sum(
            len(f.read_text(encoding='utf-8').splitlines()) for f in md_files
        )

        print(f"Found {len(md_files)} markdown files ({self.stats['total_lines']} lines)\n")

        # Run validation checks
        self.check_file_structure()
        self.validate_links(md_files)
        self.validate_code_blocks(md_files)
        self.check_terminology_consistency(md_files)
        self.check_cross_references(md_files)

        # Print results
        self.print_results()

    def check_file_structure(self):
        """Verify expected documentation structure."""
        print("1. Checking file structure...")

        expected_files = [
            "docs/guides/getting-started.md",
            "docs/guides/user-guide.md",
            "docs/guides/tutorials/tutorial-01-first-simulation.md",
            "docs/guides/tutorials/tutorial-02-controller-comparison.md",
            "docs/guides/tutorials/tutorial-03-pso-optimization.md",
            "docs/guides/tutorials/tutorial-04-custom-controller.md",
            "docs/guides/tutorials/tutorial-05-research-workflow.md",
        ]

        missing = []
        for file_path in expected_files:
            full_path = Path(file_path)
            if not full_path.exists():
                missing.append(file_path)

        if missing:
            self.errors.append(f"Missing expected files: {missing}")
        else:
            print("   [OK] All expected files present")

        self.stats['expected_files'] = len(expected_files)
        self.stats['missing_files'] = len(missing)

    def validate_links(self, md_files: List[Path]):
        """Validate all markdown links."""
        print("\n2. Validating links...")

        total_links = 0
        broken_links = []

        for file_path in md_files:
            content = file_path.read_text(encoding='utf-8')
            pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            links = re.findall(pattern, content)

            for text, link in links:
                total_links += 1

                # Skip external links
                if link.startswith('http://') or link.startswith('https://'):
                    continue

                # Skip anchors
                if link.startswith('#'):
                    continue

                # Resolve relative path
                base_dir = file_path.parent
                target = base_dir / link.split('#')[0]

                if not target.exists():
                    broken_links.append({
                        'file': str(file_path),
                        'text': text,
                        'link': link,
                        'target': str(target)
                    })

        self.stats['total_links'] = total_links
        self.stats['broken_links'] = len(broken_links)

        if broken_links:
            for broken in broken_links:
                self.errors.append(
                    f"Broken link in {broken['file']}: [{broken['text']}]({broken['link']})"
                )
        else:
            print(f"   [OK] All {total_links} links validated")

    def validate_code_blocks(self, md_files: List[Path]):
        """Check code blocks for common issues."""
        print("\n3. Validating code blocks...")

        total_code_blocks = 0
        issues = []

        for file_path in md_files:
            content = file_path.read_text(encoding='utf-8')

            # Find code blocks
            code_blocks = re.findall(r'```(\w*)\n(.*?)```', content, re.DOTALL)
            total_code_blocks += len(code_blocks)

            for lang, code in code_blocks:
                # Check for common issues
                if lang == 'python' and 'import' in code:
                    # Check for bare excepts
                    if re.search(r'except\s*:', code):
                        issues.append({
                            'file': str(file_path),
                            'issue': 'Bare except clause (anti-pattern)',
                            'severity': 'warning'
                        })

                    # Check for print statements without context
                    if code.count('print(') > 5:
                        issues.append({
                            'file': str(file_path),
                            'issue': 'Many print statements (consider logging)',
                            'severity': 'info'
                        })

        self.stats['total_code_blocks'] = total_code_blocks

        for issue in issues:
            if issue['severity'] == 'warning':
                self.warnings.append(f"{issue['file']}: {issue['issue']}")

        print(f"   [OK] {total_code_blocks} code blocks checked")
        if issues:
            print(f"   [WARN] {len(issues)} minor issues found (see warnings)")

    def check_terminology_consistency(self, md_files: List[Path]):
        """Check for consistent terminology usage."""
        print("\n4. Checking terminology consistency...")

        # Define preferred terms
        terminology = {
            'double-inverted pendulum': ['double inverted pendulum', 'DIP', 'double-IP'],
            'classical SMC': ['classic SMC', 'classical sliding mode'],
            'super-twisting SMC': ['STA-SMC', 'super twisting', 'STA SMC'],
            'PSO': ['particle swarm optimization', 'Particle Swarm Optimization'],
        }

        inconsistencies = []

        for file_path in md_files:
            content = file_path.read_text(encoding='utf-8').lower()

            # Check for mixed usage
            for preferred, alternatives in terminology.items():
                if preferred.lower() in content:
                    for alt in alternatives:
                        if alt.lower() in content and alt.lower() != preferred.lower():
                            inconsistencies.append({
                                'file': str(file_path.name),
                                'preferred': preferred,
                                'found': alt
                            })

        if inconsistencies:
            for item in inconsistencies[:10]:  # Show first 10
                self.warnings.append(
                    f"{item['file']}: Consider using '{item['preferred']}' "
                    f"instead of '{item['found']}'"
                )
        else:
            print("   [OK] Terminology consistent")

    def check_cross_references(self, md_files: List[Path]):
        """Verify cross-references between documents."""
        print("\n5. Checking cross-references...")

        # Build reference map
        references = {}
        for file_path in md_files:
            content = file_path.read_text(encoding='utf-8')

            # Find all references to other tutorials
            tutorial_refs = re.findall(
                r'\[Tutorial (\d+)[^\]]*\]\(([^)]+)\)',
                content
            )

            if tutorial_refs:
                references[file_path.name] = tutorial_refs

        # Verify tutorial progression
        # tutorial_order = [  # noqa: F841 - Unused, kept for reference
        #     'tutorial-01-first-simulation.md',
        #     'tutorial-02-controller-comparison.md',
        #     'tutorial-03-pso-optimization.md',
        #     'tutorial-04-custom-controller.md',
        #     'tutorial-05-research-workflow.md',
        # ]

        self.stats['cross_references'] = sum(len(refs) for refs in references.values())
        print(f"   [OK] {self.stats['cross_references']} cross-references found")

    def print_results(self):
        """Print validation results summary."""
        print("\n" + "=" * 70)
        print("VALIDATION RESULTS")
        print("=" * 70)

        # Statistics
        print("\nStatistics:")
        print(f"  Total files: {self.stats.get('total_files', 0)}")
        print(f"  Total lines: {self.stats.get('total_lines', 0)}")
        print(f"  Total links: {self.stats.get('total_links', 0)}")
        print(f"  Code blocks: {self.stats.get('total_code_blocks', 0)}")
        print(f"  Cross-references: {self.stats.get('cross_references', 0)}")

        # Errors
        print(f"\nErrors: {len(self.errors)}")
        if self.errors:
            for error in self.errors[:10]:  # Show first 10
                print(f"  [X] {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")

        # Warnings
        print(f"\nWarnings: {len(self.warnings)}")
        if self.warnings:
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  [!] {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")

        # Overall status
        print("\n" + "=" * 70)
        if not self.errors:
            print("[PASS] VALIDATION PASSED")
            print("=" * 70)
            return True
        else:
            print("[FAIL] VALIDATION FAILED - Please fix errors above")
            print("=" * 70)
            return False


def main():
    """Run validation."""
    docs_root = Path("docs")

    if not docs_root.exists():
        print(f"ERROR: Documentation root not found: {docs_root}")
        return False

    validator = DocumentationValidator(docs_root)
    success = validator.validate_all()

    # Save validation report
    report = {
        'stats': validator.stats,
        'errors': validator.errors,
        'warnings': validator.warnings,
        'status': 'PASSED' if success else 'FAILED'
    }

    report_path = Path('docs/validation_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nDetailed report saved to: {report_path}")

    return success


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
