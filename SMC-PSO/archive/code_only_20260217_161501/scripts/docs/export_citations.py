#!/usr/bin/env python3
"""
Citation Export Tool
===================

Converts BibTeX citations to multiple formats for bibliography managers.

Supported Formats:
    - RIS (EndNote, Mendeley, RefWorks)
    - CSL JSON (Zotero, Pandoc)
    - BibTeX (combined file)

Usage:
    python scripts/docs/export_citations.py --format ris
    python scripts/docs/export_citations.py --format csl-json
    python scripts/docs/export_citations.py --format bibtex
    python scripts/docs/export_citations.py --all  # Export all formats

Output:
    .artifacts/exports/citations.{ris,json,bib}

Author: Claude Code
Date: 2025-10-09
"""

import re
import json
from pathlib import Path
from typing import Dict, List
import argparse


class BibTeXEntry:
    """Represents a single BibTeX entry."""

    def __init__(self, entry_type: str, key: str, fields: Dict[str, str]):
        self.entry_type = entry_type
        self.key = key
        self.fields = fields

    def __repr__(self):
        return f"BibTeXEntry({self.entry_type}, {self.key})"


def parse_bibtex_file(file_path: Path) -> List[BibTeXEntry]:
    """Parse a BibTeX file and return list of entries."""
    entries = []

    content = file_path.read_text(encoding='utf-8')

    # Pattern for @type{key, ...}
    pattern = r'@(\w+)\{([^,]+),\s*((?:[^{}]|\{[^}]*\})*)\}'

    for match in re.finditer(pattern, content, re.DOTALL):
        entry_type = match.group(1).lower()
        key = match.group(2).strip()
        fields_text = match.group(3)

        # Parse fields
        fields = {}
        field_pattern = r'(\w+)\s*=\s*\{([^}]*)\}'

        for field_match in re.finditer(field_pattern, fields_text):
            field_name = field_match.group(1).lower()
            field_value = field_match.group(2).strip()
            fields[field_name] = field_value

        entries.append(BibTeXEntry(entry_type, key, fields))

    return entries


def load_all_bibtex() -> List[BibTeXEntry]:
    """Load all BibTeX entries from docs/bib/*.bib."""
    all_entries = []

    bib_dir = Path("docs/bib")
    for bib_file in sorted(bib_dir.glob("*.bib")):
        entries = parse_bibtex_file(bib_file)
        all_entries.extend(entries)

    return all_entries


def export_to_ris(entries: List[BibTeXEntry], output_path: Path) -> None:
    """Export entries to RIS format (EndNote, Mendeley)."""
    ris_type_map = {
        'article': 'JOUR',
        'book': 'BOOK',
        'inproceedings': 'CONF',
        'incollection': 'CHAP',
        'phdthesis': 'THES',
        'mastersthesis': 'THES',
        'techreport': 'RPRT',
        'misc': 'GEN',
        'software': 'COMP',
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in entries:
            # Type of reference
            ris_type = ris_type_map.get(entry.entry_type, 'GEN')
            f.write(f"TY  - {ris_type}\n")

            # Title
            if 'title' in entry.fields:
                f.write(f"TI  - {entry.fields['title']}\n")

            # Authors
            if 'author' in entry.fields:
                authors = entry.fields['author'].split(' and ')
                for author in authors:
                    f.write(f"AU  - {author.strip()}\n")

            # Year
            if 'year' in entry.fields:
                f.write(f"PY  - {entry.fields['year']}\n")

            # Journal/Book title
            if 'journal' in entry.fields:
                f.write(f"JO  - {entry.fields['journal']}\n")
            elif 'booktitle' in entry.fields:
                f.write(f"T2  - {entry.fields['booktitle']}\n")

            # Volume
            if 'volume' in entry.fields:
                f.write(f"VL  - {entry.fields['volume']}\n")

            # Number
            if 'number' in entry.fields:
                f.write(f"IS  - {entry.fields['number']}\n")

            # Pages
            if 'pages' in entry.fields:
                pages = entry.fields['pages'].replace('--', '-')
                f.write(f"SP  - {pages}\n")

            # Publisher
            if 'publisher' in entry.fields:
                f.write(f"PB  - {entry.fields['publisher']}\n")

            # DOI
            if 'doi' in entry.fields:
                f.write(f"DO  - {entry.fields['doi']}\n")

            # URL
            if 'url' in entry.fields:
                f.write(f"UR  - {entry.fields['url']}\n")

            # Edition
            if 'edition' in entry.fields:
                f.write(f"ET  - {entry.fields['edition']}\n")

            # ISBN
            if 'isbn' in entry.fields:
                f.write(f"SN  - {entry.fields['isbn']}\n")

            # Note
            if 'note' in entry.fields:
                f.write(f"N1  - {entry.fields['note']}\n")

            # ID (BibTeX key)
            f.write(f"ID  - {entry.key}\n")

            # End of record
            f.write("ER  - \n\n")


def export_to_csl_json(entries: List[BibTeXEntry], output_path: Path) -> None:
    """Export entries to CSL JSON format (Zotero, Pandoc)."""
    csl_type_map = {
        'article': 'article-journal',
        'book': 'book',
        'inproceedings': 'paper-conference',
        'incollection': 'chapter',
        'phdthesis': 'thesis',
        'mastersthesis': 'thesis',
        'techreport': 'report',
        'misc': 'article',
        'software': 'software',
    }

    csl_entries = []

    for entry in entries:
        csl_entry = {
            'id': entry.key,
            'type': csl_type_map.get(entry.entry_type, 'article')
        }

        # Title
        if 'title' in entry.fields:
            csl_entry['title'] = entry.fields['title']

        # Authors
        if 'author' in entry.fields:
            authors = []
            for author in entry.fields['author'].split(' and '):
                author = author.strip()
                # Try to parse "Last, First" or "First Last"
                if ',' in author:
                    parts = author.split(',', 1)
                    authors.append({
                        'family': parts[0].strip(),
                        'given': parts[1].strip()
                    })
                else:
                    # Assume "First Last" format
                    parts = author.rsplit(' ', 1)
                    if len(parts) == 2:
                        authors.append({
                            'family': parts[1].strip(),
                            'given': parts[0].strip()
                        })
                    else:
                        authors.append({'literal': author})
            csl_entry['author'] = authors

        # Year
        if 'year' in entry.fields:
            csl_entry['issued'] = {'date-parts': [[int(entry.fields['year'])]]}

        # Journal
        if 'journal' in entry.fields:
            csl_entry['container-title'] = entry.fields['journal']

        # Book title
        if 'booktitle' in entry.fields:
            csl_entry['container-title'] = entry.fields['booktitle']

        # Volume
        if 'volume' in entry.fields:
            csl_entry['volume'] = entry.fields['volume']

        # Issue/Number
        if 'number' in entry.fields:
            csl_entry['issue'] = entry.fields['number']

        # Pages
        if 'pages' in entry.fields:
            csl_entry['page'] = entry.fields['pages'].replace('--', '-')

        # Publisher
        if 'publisher' in entry.fields:
            csl_entry['publisher'] = entry.fields['publisher']

        # DOI
        if 'doi' in entry.fields:
            csl_entry['DOI'] = entry.fields['doi']

        # URL
        if 'url' in entry.fields:
            csl_entry['URL'] = entry.fields['url']

        # Edition
        if 'edition' in entry.fields:
            csl_entry['edition'] = entry.fields['edition']

        # ISBN
        if 'isbn' in entry.fields:
            csl_entry['ISBN'] = entry.fields['isbn']

        # Note
        if 'note' in entry.fields:
            csl_entry['note'] = entry.fields['note']

        csl_entries.append(csl_entry)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(csl_entries, f, indent=2, ensure_ascii=False)


def export_to_bibtex(entries: List[BibTeXEntry], output_path: Path) -> None:
    """Export entries to combined BibTeX file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("% Combined BibTeX Bibliography\n")
        f.write("% DIP-SMC-PSO Project\n")
        f.write("% Generated: 2025-10-09\n")
        f.write("% Total entries: {}\n\n".format(len(entries)))

        for entry in entries:
            f.write(f"@{entry.entry_type}{{{entry.key},\n")

            for field_name, field_value in entry.fields.items():
                f.write(f"  {field_name:12} = {{{field_value}}},\n")

            f.write("}\n\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export BibTeX citations to multiple formats"
    )
    parser.add_argument(
        '--format',
        choices=['ris', 'csl-json', 'bibtex'],
        help="Output format (ris, csl-json, bibtex)"
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help="Export all formats"
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(".artifacts/exports"),
        help="Output directory (default: .artifacts/exports)"
    )

    args = parser.parse_args()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("Citation Export Tool")
    print("=" * 60)
    print()

    # Load all BibTeX entries
    print("[1/3] Loading BibTeX entries...")
    entries = load_all_bibtex()
    print(f"      Loaded {len(entries)} entries from docs/bib/")

    # Export to requested format(s)
    print("[2/3] Exporting citations...")

    formats_to_export = []
    if args.all:
        formats_to_export = ['ris', 'csl-json', 'bibtex']
    elif args.format:
        formats_to_export = [args.format]
    else:
        print("Error: Specify --format or --all")
        return

    for fmt in formats_to_export:
        if fmt == 'ris':
            output_path = args.output_dir / "citations.ris"
            export_to_ris(entries, output_path)
            print(f"      RIS format -> {output_path} ({len(entries)} entries)")

        elif fmt == 'csl-json':
            output_path = args.output_dir / "citations.json"
            export_to_csl_json(entries, output_path)
            print(f"      CSL JSON -> {output_path} ({len(entries)} entries)")

        elif fmt == 'bibtex':
            output_path = args.output_dir / "citations.bib"
            export_to_bibtex(entries, output_path)
            print(f"      BibTeX -> {output_path} ({len(entries)} entries)")

    # Summary
    print("[3/3] Export complete!")
    print()
    print("Exported files:")
    for fmt in formats_to_export:
        if fmt == 'ris':
            print(f"  - {args.output_dir}/citations.ris (EndNote, Mendeley)")
        elif fmt == 'csl-json':
            print(f"  - {args.output_dir}/citations.json (Zotero, Pandoc)")
        elif fmt == 'bibtex':
            print(f"  - {args.output_dir}/citations.bib (LaTeX, BibDesk)")

    print()
    print("Import Instructions:")
    print("  EndNote:  File -> Import -> File (citations.ris)")
    print("  Zotero:   File -> Import -> (citations.json)")
    print("  Mendeley: File -> Add Files -> (citations.ris)")


if __name__ == "__main__":
    main()
