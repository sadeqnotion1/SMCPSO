#!/usr/bin/env python3
"""
BibTeX Deduplication Script for Sphinx Bibliography

Eliminates ~145 duplicate citation warnings by:
1. Finding duplicate entries across multiple .bib files
2. Creating canonical key mappings
3. Removing duplicates from .bib files
4. Updating all {cite} references in Markdown files

Usage:
    python deduplicate_bibtex.py --dry-run  # Preview changes
    python deduplicate_bibtex.py            # Apply fixes
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict


class BibTeXDeduplicator:
    """Deduplicate BibTeX entries across multiple files."""

    def __init__(self, docs_root: Path, dry_run: bool = False):
        self.docs_root = docs_root
        self.dry_run = dry_run
        self.stats = {
            'bib_files_processed': 0,
            'md_files_processed': 0,
            'duplicates_found': 0,
            'duplicates_removed': 0,
            'citations_updated': 0,
            'errors': []
        }
        self.key_mapping: Dict[str, str] = {}  # old_key -> canonical_key
        self.canonical_keys: Set[str] = set()

    def find_all_bib_files(self) -> List[Path]:
        """Find all .bib files in docs directory."""
        bib_files = list(self.docs_root.glob('**/*.bib'))
        # Exclude build directories
        return [f for f in bib_files if '_build' not in str(f)]

    def parse_bib_file(self, filepath: Path) -> List[Dict]:
        """Parse a BibTeX file manually (no external dependencies)."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            entries = []
            # Match @type{key, ... }
            pattern = r'@(\w+)\s*\{\s*([^,\s]+)\s*,([^@]*?)\n\}'
            for match in re.finditer(pattern, content, re.DOTALL):
                entry_type = match.group(1)
                key = match.group(2)
                fields_str = match.group(3)

                # Parse fields
                fields = {'ID': key, 'ENTRYTYPE': entry_type}
                field_pattern = r'(\w+)\s*=\s*\{([^}]*)\}|(\w+)\s*=\s*"([^"]*)"'
                for field_match in re.finditer(field_pattern, fields_str):
                    if field_match.group(1):
                        field_name = field_match.group(1).lower()
                        field_value = field_match.group(2)
                    else:
                        field_name = field_match.group(3).lower()
                        field_value = field_match.group(4)
                    fields[field_name] = field_value.strip()

                entries.append(fields)

            return entries
        except Exception as e:
            self.stats['errors'].append(f"Error parsing {filepath}: {e}")
            return []

    def find_duplicates(self) -> Dict[str, List[Tuple[str, Path]]]:
        """
        Find duplicate entries by DOI or title.

        Returns:
            Dict mapping canonical_key -> [(duplicate_key, source_file), ...]
        """
        # Group entries by DOI or normalized title
        doi_map = defaultdict(list)
        title_map = defaultdict(list)

        bib_files = self.find_all_bib_files()
        print(f"\nScanning {len(bib_files)} BibTeX files for duplicates...")

        for bib_file in bib_files:
            entries = self.parse_bib_file(bib_file)
            self.stats['bib_files_processed'] += 1

            for entry in entries:
                key = entry['ID']

                # Group by DOI (most reliable)
                if 'doi' in entry:
                    doi = entry['doi'].strip().lower()
                    doi_map[doi].append((key, bib_file, entry))

                # Group by normalized title (fallback)
                elif 'title' in entry:
                    title = self.normalize_title(entry['title'])
                    title_map[title].append((key, bib_file, entry))

        # Find duplicates
        duplicates = {}

        for doi, entries in doi_map.items():
            if len(entries) > 1:
                canonical = self.choose_canonical_key([e[0] for e in entries])
                duplicates[canonical] = [(e[0], e[1]) for e in entries if e[0] != canonical]
                self.stats['duplicates_found'] += len(entries) - 1

        for title, entries in title_map.items():
            if len(entries) > 1:
                keys = [e[0] for e in entries]
                # Skip if already found by DOI
                if not any(k in self.key_mapping for k in keys):
                    canonical = self.choose_canonical_key(keys)
                    duplicates[canonical] = [(e[0], e[1]) for e in entries if e[0] != canonical]
                    self.stats['duplicates_found'] += len(entries) - 1

        return duplicates

    def normalize_title(self, title: str) -> str:
        """Normalize title for comparison."""
        # Remove LaTeX commands, punctuation, convert to lowercase
        title = re.sub(r'[{}\\\"]', '', title)
        title = re.sub(r'[^\w\s]', '', title)
        return ' '.join(title.lower().split())

    def choose_canonical_key(self, keys: List[str]) -> str:
        """
        Choose canonical key from duplicates.

        Prefer: longest key with prefix (smc_, pso_, dip_) > shortest key
        """
        prefixed = [k for k in keys if k.startswith(('smc_', 'pso_', 'dip_', 'soft_'))]
        if prefixed:
            return max(prefixed, key=len)  # Longest prefixed key
        return min(keys, key=len)  # Shortest key as fallback

    def create_key_mapping(self, duplicates: Dict[str, List[Tuple[str, Path]]]) -> None:
        """Create mapping from duplicate keys to canonical keys."""
        for canonical, dups in duplicates.items():
            self.canonical_keys.add(canonical)
            for dup_key, _ in dups:
                self.key_mapping[dup_key] = canonical

    def remove_duplicates_from_bib(self, duplicates: Dict[str, List[Tuple[str, Path]]]) -> None:
        """Remove duplicate entries from .bib files."""
        files_to_update = defaultdict(set)

        # Collect which keys to remove from which files
        for canonical, dups in duplicates.items():
            for dup_key, bib_file in dups:
                files_to_update[bib_file].add(dup_key)

        # Update each file
        for bib_file, keys_to_remove in files_to_update.items():
            try:
                with open(bib_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content
                removed = 0

                # Remove entries by key
                for key in keys_to_remove:
                    # Match entire entry: @type{key, ...}
                    pattern = rf'@\w+\s*\{{\s*{re.escape(key)}\s*,.*?\n}}'
                    match = re.search(pattern, content, re.DOTALL)
                    if match:
                        content = content.replace(match.group(0), '')
                        removed += 1

                self.stats['duplicates_removed'] += removed

                if self.dry_run:
                    print(f"  [DRY RUN] Would remove {removed} duplicates from {bib_file.name}")
                else:
                    # Write back
                    with open(bib_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  [OK] Removed {removed} duplicates from {bib_file.name}")

            except Exception as e:
                self.stats['errors'].append(f"Error updating {bib_file}: {e}")

    def update_citations_in_md(self) -> None:
        """Update {cite} references in Markdown files."""
        if not self.key_mapping:
            return

        md_files = list(self.docs_root.glob('**/*.md'))
        md_files = [f for f in md_files if '_build' not in str(f)]

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                original = content

                # Update {cite}`old_key` -> {cite}`new_key`
                for old_key, new_key in self.key_mapping.items():
                    # Pattern: {cite}`old_key` or {cite}`key1,old_key,key3`
                    pattern1 = rf'\{{cite\}}`{re.escape(old_key)}`'
                    replace1 = f'{{cite}}`{new_key}`'
                    content = re.sub(pattern1, replace1, content)

                    # Pattern in comma-separated lists
                    pattern2 = rf'\{{cite\}}`([^`]*?)(?:^|,){re.escape(old_key)}(?:,|$)([^`]*?)`'
                    def replacer(m):
                        before = m.group(1)
                        after = m.group(2)
                        # Reconstruct with new key
                        parts = [p.strip() for p in (before + ',' + after).split(',') if p.strip()]
                        parts = [new_key if p == old_key else p for p in parts]
                        return f"{{cite}}`{','.join(parts)}`"
                    content = re.sub(pattern2, replacer, content)

                if content != original:
                    if self.dry_run:
                        print(f"  [DRY RUN] Would update citations in {md_file.relative_to(self.docs_root)}")
                    else:
                        md_file.write_text(content, encoding='utf-8')
                        print(f"  [OK] Updated citations in {md_file.relative_to(self.docs_root)}")

                    self.stats['md_files_processed'] += 1
                    self.stats['citations_updated'] += len([k for k in self.key_mapping if k in original])

            except Exception as e:
                self.stats['errors'].append(f"Error updating {md_file}: {e}")

    def print_summary(self) -> None:
        """Print summary statistics."""
        print("\n" + "="*70)
        print("BIBTEX DEDUPLICATION SUMMARY")
        print("="*70)
        print(f"BibTeX files scanned: {self.stats['bib_files_processed']}")
        print(f"Duplicate entries found: {self.stats['duplicates_found']}")
        print(f"Duplicate entries removed: {self.stats['duplicates_removed']}")
        print(f"Markdown files updated: {self.stats['md_files_processed']}")
        print(f"Citations updated: {self.stats['citations_updated']}")

        if self.stats['errors']:
            print(f"\nErrors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:10]:
                print(f"  - {error}")

        print(f"\nCanonical keys: {len(self.canonical_keys)}")
        print(f"Key mappings: {len(self.key_mapping)}")

        if self.key_mapping:
            print("\nSample key mappings:")
            for old, new in list(self.key_mapping.items())[:10]:
                print(f"  {old} -> {new}")

        if self.dry_run:
            print("\n[WARNING] DRY RUN MODE - No files were modified")
            print("Run without --dry-run to apply changes")
        else:
            print("\n[SUCCESS] Deduplication complete")

    def run(self) -> int:
        """Execute deduplication process."""
        try:
            # Step 1: Find duplicates
            duplicates = self.find_duplicates()

            if not duplicates:
                print("No duplicates found!")
                return 0

            # Step 2: Create key mapping
            self.create_key_mapping(duplicates)

            print(f"\nFound {self.stats['duplicates_found']} duplicate entries")
            print(f"Canonical keys: {len(self.canonical_keys)}")

            # Step 3: Remove duplicates from .bib files
            print("\nRemoving duplicates from BibTeX files...")
            self.remove_duplicates_from_bib(duplicates)

            # Step 4: Update citations in Markdown files
            print("\nUpdating citations in Markdown files...")
            self.update_citations_in_md()

            # Summary
            self.print_summary()

            return 0 if not self.stats['errors'] else 1

        except Exception as e:
            print(f"Fatal error: {e}")
            import traceback
            traceback.print_exc()
            return 1


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Deduplicate BibTeX entries and update citations'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--docs-root',
        type=Path,
        default=Path(__file__).parent.parent,
        help='Root directory of documentation (default: ../)'
    )

    args = parser.parse_args()

    deduplicator = BibTeXDeduplicator(args.docs_root, dry_run=args.dry_run)
    return deduplicator.run()


if __name__ == '__main__':
    sys.exit(main())
