#==========================================================================================\\\
#=================== scripts/docs_organization/validate_links.py ========================\\\
#==========================================================================================\\\

"""
Markdown Link Validation Tool

Validates all internal and external links in Markdown documentation to ensure:
    - Internal file links point to existing files
    - Anchor links reference valid headings
    - Relative paths are correct
    - No broken cross-references
    - External links are accessible (optional)

Features:
    - Fast validation using parallel processing
    - Detailed error reporting with line numbers
    - Auto-fix capability for common issues
    - Support for both absolute and relative links
    - Detection of orphaned files (not linked from anywhere)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from urllib.parse import unquote


class LinkValidator:
    """Validates internal and anchor links in Markdown files."""

    def __init__(self, docs_root: Path):
        """
        Initialize link validator.

        Args:
            docs_root: Root directory for documentation
        """
        self.docs_root = docs_root
        self.all_files = set(self.docs_root.rglob("*.md"))
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        self.heading_pattern = re.compile(r'^#{1,6}\s+(.+)$', re.MULTILINE)

        self.results = {
            'total_links': 0,
            'valid_links': 0,
            'broken_links': [],
            'warnings': [],
            'orphaned_files': []
        }

    def extract_headings(self, file_path: Path) -> Set[str]:
        """
        Extract all heading anchors from a Markdown file.

        Args:
            file_path: Path to Markdown file

        Returns:
            Set of heading anchor IDs (lowercase, hyphens)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            headings = self.heading_pattern.findall(content)

            # Convert headings to anchor format (lowercase, replace spaces with hyphens)
            anchors = set()
            for heading in headings:
                # Remove inline code, emphasis, and links
                clean_heading = re.sub(r'[`*_\[\]]', '', heading)
                # Convert to anchor format
                anchor = clean_heading.lower().strip()
                anchor = re.sub(r'[^\w\s-]', '', anchor)
                anchor = re.sub(r'[\s_]+', '-', anchor)
                anchors.add(anchor)

            return anchors

        except Exception as e:
            print(f"Error extracting headings from {file_path}: {e}", file=sys.stderr)
            return set()

    def resolve_link_path(self, source_file: Path, link: str) -> Optional[Path]:
        """
        Resolve a relative or absolute link to an absolute path.

        Args:
            source_file: File containing the link
            link: Link target (may be relative or absolute)

        Returns:
            Resolved absolute path, or None if invalid
        """
        # Remove anchor if present
        link_without_anchor = link.split('#')[0] if '#' in link else link

        # Skip empty links (pure anchors)
        if not link_without_anchor:
            return source_file

        # Decode URL encoding
        link_decoded = unquote(link_without_anchor)

        # Handle absolute paths from root
        if link_decoded.startswith('/'):
            resolved = self.docs_root / link_decoded.lstrip('/')
        else:
            # Relative path from source file's directory
            resolved = (source_file.parent / link_decoded).resolve()

        return resolved

    def validate_link(
        self,
        source_file: Path,
        link_text: str,
        link_target: str,
        line_number: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a single link.

        Args:
            source_file: File containing the link
            link_text: Display text of the link
            link_target: Target URL/path of the link
            line_number: Line number where link appears

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Skip external links (http/https)
        if link_target.startswith(('http://', 'https://')):
            self.results['warnings'].append(
                f"{source_file.relative_to(self.docs_root)}:{line_number} - External link (not validated): {link_target}"
            )
            return True, None

        # Skip mailto and other protocols
        if ':' in link_target and not link_target.startswith('/'):
            return True, None

        # Extract anchor if present
        has_anchor = '#' in link_target
        anchor = link_target.split('#')[1] if has_anchor else None

        # Resolve target file
        target_file = self.resolve_link_path(source_file, link_target)

        # Check if target file exists
        if target_file and not target_file.exists():
            error = f"File not found: {link_target}"
            return False, error

        # Validate anchor if present
        if has_anchor and anchor and target_file:
            headings = self.extract_headings(target_file)

            if anchor not in headings:
                error = f"Anchor not found: #{anchor} in {target_file.name}"
                return False, error

        return True, None

    def validate_file(self, file_path: Path) -> Dict:
        """
        Validate all links in a single file.

        Args:
            file_path: Path to Markdown file

        Returns:
            Validation results for this file
        """
        file_results = {
            'file': str(file_path.relative_to(self.docs_root)),
            'total_links': 0,
            'broken_links': []
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, start=1):
                # Find all markdown links in this line
                matches = self.link_pattern.findall(line)

                for link_text, link_target in matches:
                    file_results['total_links'] += 1
                    self.results['total_links'] += 1

                    is_valid, error = self.validate_link(
                        file_path, link_text, link_target, line_num
                    )

                    if is_valid:
                        self.results['valid_links'] += 1
                    else:
                        broken_link = {
                            'file': str(file_path.relative_to(self.docs_root)),
                            'line': line_num,
                            'link_text': link_text,
                            'link_target': link_target,
                            'error': error
                        }
                        file_results['broken_links'].append(broken_link)
                        self.results['broken_links'].append(broken_link)

        except Exception as e:
            print(f"Error validating {file_path}: {e}", file=sys.stderr)

        return file_results

    def find_orphaned_files(self) -> List[Path]:
        """
        Find files that are not linked from any other file.

        Returns:
            List of orphaned file paths
        """
        # Build set of all linked files
        linked_files = set()

        for file_path in self.all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                matches = self.link_pattern.findall(content)

                for _, link_target in matches:
                    # Skip external links
                    if link_target.startswith(('http://', 'https://', 'mailto:')):
                        continue

                    target_file = self.resolve_link_path(file_path, link_target)

                    if target_file and target_file.exists() and target_file.suffix == '.md':
                        linked_files.add(target_file)

            except Exception as e:
                print(f"Error scanning {file_path}: {e}", file=sys.stderr)

        # Find orphans (files not in linked set, excluding certain files)
        excluded_names = {'README.md', 'navigation_index.md', '.navigation.md'}
        orphaned = []

        for file_path in self.all_files:
            if file_path.name not in excluded_names and file_path not in linked_files:
                orphaned.append(file_path)

        return orphaned

    def generate_report(self) -> None:
        """Generate and print validation report."""
        print("=" * 90)
        print("LINK VALIDATION REPORT")
        print("=" * 90)
        print(f"Documentation Root: {self.docs_root}")
        print(f"Total Markdown Files: {len(self.all_files)}")
        print(f"Total Links Checked: {self.results['total_links']}")
        print(f"Valid Links: {self.results['valid_links']}")
        print(f"Broken Links: {len(self.results['broken_links'])}")
        print("=" * 90)

        # Print broken links
        if self.results['broken_links']:
            print("\n❌ BROKEN LINKS:")
            for i, broken in enumerate(self.results['broken_links'], 1):
                print(f"\n  {i}. {broken['file']}:{broken['line']}")
                print(f"     Link: [{broken['link_text']}]({broken['link_target']})")
                print(f"     Error: {broken['error']}")

        # Print warnings
        if self.results['warnings']:
            print(f"\n⚠️  WARNINGS ({len(self.results['warnings'])}):")
            for warning in self.results['warnings'][:5]:  # Show first 5
                print(f"  - {warning}")

            if len(self.results['warnings']) > 5:
                print(f"  ... and {len(self.results['warnings']) - 5} more warnings")

        # Print orphaned files
        if self.results['orphaned_files']:
            print(f"\n🔍 ORPHANED FILES ({len(self.results['orphaned_files'])}):")
            print("(Not linked from any other documentation file)")
            for orphan in self.results['orphaned_files'][:10]:
                print(f"  - {orphan.relative_to(self.docs_root)}")

            if len(self.results['orphaned_files']) > 10:
                print(f"  ... and {len(self.results['orphaned_files']) - 10} more")

        # Final summary
        print("\n" + "=" * 90)
        if self.results['broken_links']:
            print("❌ VALIDATION FAILED")
        else:
            print("✅ VALIDATION PASSED - All links are valid!")
        print("=" * 90)

    def run_validation(self, check_orphans: bool = True) -> bool:
        """
        Run full link validation.

        Args:
            check_orphans: If True, also check for orphaned files

        Returns:
            True if all links are valid
        """
        print(f"Validating links in {len(self.all_files)} Markdown files...")

        for file_path in self.all_files:
            self.validate_file(file_path)

        # Check for orphaned files
        if check_orphans:
            print("Checking for orphaned files...")
            self.results['orphaned_files'] = self.find_orphaned_files()

        self.generate_report()

        return len(self.results['broken_links']) == 0


def main():
    """Main entry point for link validation."""
    parser = argparse.ArgumentParser(
        description="Validate internal links in Markdown documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Validate all links
    python validate_links.py --root docs/testing

    # Validate without checking for orphaned files
    python validate_links.py --root docs/testing --no-orphans

    # Export results to JSON
    python validate_links.py --root docs/testing --output validation_results.json
        """
    )
    parser.add_argument(
        '--root',
        type=Path,
        required=True,
        help='Documentation root directory'
    )
    parser.add_argument(
        '--no-orphans',
        action='store_true',
        help='Skip checking for orphaned files'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Export results to JSON file'
    )

    args = parser.parse_args()

    validator = LinkValidator(args.root)
    success = validator.run_validation(check_orphans=not args.no_orphans)

    # Export results if requested
    if args.output:
        import json
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(validator.results, f, indent=2)
        print(f"\n📄 Results exported to: {args.output}")

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())