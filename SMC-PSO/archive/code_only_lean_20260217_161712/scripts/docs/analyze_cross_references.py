#======================================================================================\\\
#========== scripts/documentation/analyze_cross_references.py =========================\\\
#======================================================================================\\\

"""Analyze and validate cross-references in documentation.

This script scans all markdown files for internal and external links,
validates their targets exist, and generates a comprehensive report.

Usage:
    python scripts/documentation/analyze_cross_references.py

Output:
    - .test_artifacts/cross_references/cross_reference_database.json
    - .test_artifacts/cross_references/broken_links.json
    - .test_artifacts/cross_references/orphaned_docs.json
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from urllib.parse import urlparse
import sys


class CrossReferenceAnalyzer:
    """Analyze cross-references in documentation."""

    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir
        self.all_docs = list(docs_dir.rglob('*.md'))
        self.cross_references: Dict[str, List[Dict[str, str]]] = {}
        self.broken_links: List[Dict[str, Any]] = []
        self.orphaned_docs: List[str] = []
        self.external_links: Dict[str, List[str]] = {}

    def extract_links_from_file(self, md_file: Path) -> List[Tuple[str, str, int]]:
        """Extract all markdown links from a file.

        Returns:
            List of (link_text, link_target, line_number) tuples
        """
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"[!] Error reading {md_file}: {e}")
            return []

        links = []

        # Pattern: [text](url)
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'

        # Track if we're inside a code block
        in_code_block = False

        for line_num, line in enumerate(content.splitlines(), 1):
            # Check for code block markers
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue

            # Skip links inside code blocks
            if in_code_block:
                continue

            # Also skip links inside inline code (backticks)
            # Simple heuristic: if line has more backticks than link patterns, likely in code
            if line.count('`') >= 2:
                # Check if the link is inside backticks
                temp_line = line
                while '`' in temp_line:
                    start = temp_line.find('`')
                    end = temp_line.find('`', start + 1)
                    if end == -1:
                        break
                    # Remove the inline code section
                    temp_line = temp_line[:start] + temp_line[end+1:]

                # Only search for links in the non-code parts
                for match in re.finditer(pattern, temp_line):
                    link_text = match.group(1).strip()
                    link_target = match.group(2).strip()
                    links.append((link_text, link_target, line_num))
            else:
                # No inline code, process normally
                for match in re.finditer(pattern, line):
                    link_text = match.group(1).strip()
                    link_target = match.group(2).strip()
                    links.append((link_text, link_target, line_num))

        return links

    def is_external_link(self, link: str) -> bool:
        """Check if a link is external (http/https)."""
        return link.startswith(('http://', 'https://'))

    def resolve_relative_link(self, source_file: Path, link_target: str) -> Path:
        """Resolve a relative link target to absolute path.

        Args:
            source_file: Source markdown file containing the link
            link_target: Relative link target (e.g., ../api/controllers.md)

        Returns:
            Absolute path to target file
        """
        # Remove anchor fragments (#section)
        if '#' in link_target:
            link_target = link_target.split('#')[0]

        # Skip empty links (pure anchors like #section)
        if not link_target:
            return None

        # Resolve relative to source file's directory
        source_dir = source_file.parent
        target_path = (source_dir / link_target).resolve()

        return target_path

    def analyze_all_links(self):
        """Analyze all links in all documentation files."""
        print(f"\n[*] Analyzing links in {len(self.all_docs)} documentation files...")

        for md_file in self.all_docs:
            relative_path = str(md_file.relative_to(self.docs_dir))
            links = self.extract_links_from_file(md_file)

            if not links:
                continue

            # Track cross-references from this file
            self.cross_references[relative_path] = []

            for link_text, link_target, line_num in links:
                # External link
                if self.is_external_link(link_target):
                    self.external_links.setdefault(relative_path, []).append({
                        'text': link_text,
                        'url': link_target,
                        'line': line_num
                    })
                    continue

                # Internal link
                resolved = self.resolve_relative_link(md_file, link_target)

                if resolved is None:
                    # Pure anchor link (e.g., #section) - skip validation
                    continue

                # Check if target exists
                exists = resolved.exists()

                # Store cross-reference
                self.cross_references[relative_path].append({
                    'text': link_text,
                    'target': link_target,
                    'resolved': str(resolved),
                    'exists': exists,
                    'line': line_num
                })

                # Track broken link
                if not exists:
                    self.broken_links.append({
                        'source': relative_path,
                        'target': link_target,
                        'resolved': str(resolved),
                        'line': line_num,
                        'text': link_text
                    })

        print(f"[+] Found {sum(len(refs) for refs in self.cross_references.values())} internal links")
        print(f"[+] Found {sum(len(links) for links in self.external_links.values())} external links")
        print(f"[!] Found {len(self.broken_links)} broken internal links")

    def find_orphaned_documents(self):
        """Find documents with no incoming links (orphaned)."""
        print(f"\n[*] Finding orphaned documents...")

        # Build set of all referenced documents
        referenced_docs = set()
        for refs in self.cross_references.values():
            for ref in refs:
                if ref['exists']:
                    # Normalize path
                    try:
                        target = Path(ref['resolved']).relative_to(self.docs_dir)
                        referenced_docs.add(str(target))
                    except ValueError:
                        # Outside docs directory
                        pass

        # Find docs with no incoming references
        for md_file in self.all_docs:
            relative_path = str(md_file.relative_to(self.docs_dir))

            # Exclude index files and root README (always valid entry points)
            if relative_path in ['index.md', 'README.md'] or '/index.md' in relative_path:
                continue

            if relative_path not in referenced_docs:
                self.orphaned_docs.append(relative_path)

        print(f"[!] Found {len(self.orphaned_docs)} orphaned documents")

    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate cross-reference statistics."""
        total_docs = len(self.all_docs)
        docs_with_links = len([d for d in self.cross_references if self.cross_references[d]])
        total_internal_links = sum(len(refs) for refs in self.cross_references.values())
        total_external_links = sum(len(links) for links in self.external_links.values())
        broken_link_count = len(self.broken_links)
        orphaned_count = len(self.orphaned_docs)

        # Most linked documents
        incoming_links: Dict[str, int] = {}
        for refs in self.cross_references.values():
            for ref in refs:
                if ref['exists']:
                    try:
                        target = Path(ref['resolved']).relative_to(self.docs_dir)
                        incoming_links[str(target)] = incoming_links.get(str(target), 0) + 1
                    except ValueError:
                        pass

        most_linked = sorted(incoming_links.items(), key=lambda x: -x[1])[:10]

        # Most outbound links
        outbound_links = [(doc, len(refs)) for doc, refs in self.cross_references.items()]
        most_outbound = sorted(outbound_links, key=lambda x: -x[1])[:10]

        return {
            'total_documents': total_docs,
            'documents_with_links': docs_with_links,
            'total_internal_links': total_internal_links,
            'total_external_links': total_external_links,
            'broken_links': broken_link_count,
            'orphaned_documents': orphaned_count,
            'link_density': total_internal_links / total_docs if total_docs > 0 else 0,
            'broken_link_rate': broken_link_count / total_internal_links if total_internal_links > 0 else 0,
            'most_linked_documents': [{'doc': doc, 'incoming_links': count} for doc, count in most_linked],
            'most_outbound_links': [{'doc': doc, 'outbound_links': count} for doc, count in most_outbound]
        }

    def save_results(self, output_dir: Path):
        """Save analysis results to JSON files."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Cross-reference database
        db_file = output_dir / 'cross_reference_database.json'
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump({
                'cross_references': self.cross_references,
                'external_links': self.external_links
            }, f, indent=2)
        print(f"[+] Saved cross-reference database: {db_file}")

        # Broken links
        broken_file = output_dir / 'broken_links.json'
        with open(broken_file, 'w', encoding='utf-8') as f:
            json.dump(self.broken_links, f, indent=2)
        print(f"[+] Saved broken links report: {broken_file}")

        # Orphaned documents
        orphaned_file = output_dir / 'orphaned_docs.json'
        with open(orphaned_file, 'w', encoding='utf-8') as f:
            json.dump(self.orphaned_docs, f, indent=2)
        print(f"[+] Saved orphaned documents: {orphaned_file}")

        # Statistics
        stats = self.calculate_statistics()
        stats_file = output_dir / 'statistics.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        print(f"[+] Saved statistics: {stats_file}")


def main():
    """Main analysis workflow."""
    print("=" * 80)
    print("Documentation Cross-Reference Analyzer")
    print("=" * 80)

    docs_dir = Path('docs')
    if not docs_dir.exists():
        print(f"[!] Documentation directory not found: {docs_dir}")
        sys.exit(1)

    analyzer = CrossReferenceAnalyzer(docs_dir)

    # Analyze all links
    analyzer.analyze_all_links()

    # Find orphaned documents
    analyzer.find_orphaned_documents()

    # Calculate statistics
    stats = analyzer.calculate_statistics()

    # Display summary
    print(f"\n[*] Cross-Reference Analysis Summary:")
    print(f"  Total documents: {stats['total_documents']}")
    print(f"  Documents with links: {stats['documents_with_links']} ({stats['documents_with_links']/stats['total_documents']*100:.1f}%)")
    print(f"  Internal links: {stats['total_internal_links']}")
    print(f"  External links: {stats['total_external_links']}")
    print(f"  Broken links: {stats['broken_links']} ({stats['broken_link_rate']*100:.1f}%)")
    print(f"  Orphaned documents: {stats['orphaned_documents']}")
    print(f"  Link density: {stats['link_density']:.2f} links/document")

    if stats['most_linked_documents']:
        print(f"\n[*] Top 5 Most Linked Documents:")
        for item in stats['most_linked_documents'][:5]:
            print(f"  {item['doc']}: {item['incoming_links']} incoming links")

    # Save results
    output_dir = Path('.test_artifacts/cross_references')
    analyzer.save_results(output_dir)

    print(f"\n[+] Analysis complete!")
    print(f"   Next step: Review broken links and fix")
    print(f"   Command: pytest tests/test_documentation/test_cross_references.py -v")

    # Exit code based on issues
    if stats['broken_links'] > 0:
        print(f"\n[!] WARNING: Found {stats['broken_links']} broken links")
        sys.exit(1)
    else:
        print(f"\n[+] SUCCESS: All internal links valid")
        sys.exit(0)


if __name__ == '__main__':
    main()
