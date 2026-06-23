"""LT-7 Bibliography Completion Script

Parses IEEE-formatted references from markdown and generates complete BibTeX entries.
Replaces the auto-generated stubs with proper citation data.

Usage:
    python scripts/lt7_complete_bibliography.py

Output:
    benchmarks/LT7_RESEARCH_PAPER.bib (updated)
"""

import re
from pathlib import Path
from typing import Dict, Tuple, Optional

INPUT_PAPER = Path(".artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.md")
OUTPUT_BIB = Path(".artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.bib")

def parse_ieee_book(ref_text: str) -> Optional[Dict]:
    """Parse IEEE book citation format."""
    # Pattern: Author(s), Title. Publisher, Year.
    # Pattern: Author(s), Title, Edition. Publisher, Year.

    patterns = [
        r'^(.+?),\s+\*(.+?)\*(?:,\s+(\d+(?:st|nd|rd|th)\s+ed\.))?[.,]\s+(.+?):\s+(.+?),\s+(\d{4})\.',
        r'^(.+?),\s+\*(.+?)\*\.\s+(.+?):\s+(.+?),\s+(\d{4})\.',
    ]

    for pattern in patterns:
        match = re.match(pattern, ref_text)
        if match:
            if len(match.groups()) == 6:
                author, title, edition, city, publisher, year = match.groups()
            else:
                author, title, city, publisher, year = match.groups()
                edition = None

            return {
                'type': 'book',
                'author': author.strip(),
                'title': title.strip(),
                'publisher': publisher.strip(),
                'address': city.strip(),
                'year': year.strip(),
                'edition': edition.strip() if edition else None
            }

    return None

def parse_ieee_article(ref_text: str) -> Optional[Dict]:
    """Parse IEEE journal article citation format."""
    # Pattern: Author, "Title," Journal, vol. X, no. Y, pp. A-B, Month Year.
    # Multiple variants to handle different formatting
    patterns = [
        # Standard: Author, "Title," *Journal*, vol. X, no. Y, pp. A-B, Month Year.
        r'^(.+?),\s+"(.+?),"?\s+\*(.+?)\*,\s+vol\.\s+([\w\-]+),\s+no\.\s+([\d\-]+),\s+pp\.\s+([\d\-–]+),\s+(\w+\.?\s+\d{4})',
        # Without month: Author, "Title," *Journal*, vol. X, no. Y, pp. A-B, Year.
        r'^(.+?),\s+"(.+?),"?\s+\*(.+?)\*,\s+vol\.\s+([\w\-]+),\s+no\.\s+([\d\-]+),\s+pp\.\s+([\d\-–]+),\s+(\d{4})',
        # Translation note: Author, "Title," *Journal*, vol. X, no. Y, pp. A-B, Year (special note).
        r'^(.+?),\s+"(.+?),"?\s+\*(.+?)\*,\s+vol\.\s+([\w\-]+),\s+no\.\s+([\d\-]+),\s+pp\.\s+([\d\-–]+),\s+(\d{4})\s*\([^)]+\)',
    ]

    for pattern in patterns:
        match = re.match(pattern, ref_text)
        if match:
            author, title, journal, volume, number, pages, date = match.groups()
            # Extract year and month
            date_parts = date.strip().split()
            year = date_parts[-1] if date_parts[-1].isdigit() else date.strip()
            month = date_parts[0].strip('.') if len(date_parts) > 1 and not date_parts[0].isdigit() else None

            return {
                'type': 'article',
                'author': author.strip(),
                'title': title.strip(),
                'journal': journal.strip(),
                'volume': volume.strip(),
                'number': number.strip(),
                'pages': pages.strip(),
                'year': year,
                'month': month
            }

    return None

def parse_ieee_inproceedings(ref_text: str) -> Optional[Dict]:
    """Parse IEEE conference paper citation format."""
    # Pattern: Author, "Title," in Proc. Conference, Location, Month Year, pp. A-B.
    patterns = [
        # With volume: Author, "Title," in *Proc...*, vol. X, Location, Month Year, pp. A-B.
        r'^(.+?),\s+"(.+?),"?\s+in\s+\*(.+?)\*,\s+vol\.\s+(\d+),\s+(.+?),\s+(\w+\.?\s+\d{4}),\s+pp\.\s+([\d\-–]+)',
        # Standard: Author, "Title," in *Proc...*, Location, Month Year, pp. A-B.
        r'^(.+?),\s+"(.+?),"?\s+in\s+\*(.+?)\*,\s+(.+?),\s+(\w+\.?\s+\d{4}),\s+pp\.\s+([\d\-–]+)',
        # Without pages: Author, "Title," in *Proc...*, Location, Month Year.
        r'^(.+?),\s+"(.+?),"?\s+in\s+\*(.+?)\*,\s+(.+?),\s+(\w+\.?\s+\d{4})',
    ]

    for i, pattern in enumerate(patterns):
        match = re.match(pattern, ref_text)
        if match:
            groups = match.groups()
            if i == 0:  # With volume
                author, title, booktitle, volume, location, date, pages = groups
            elif i == 1:  # Standard with pages
                author, title, booktitle, location, date, pages = groups
                volume = None
            else:  # Without pages
                author, title, booktitle, location, date = groups
                volume = None
                pages = None

            date_parts = date.strip().split()
            year = date_parts[-1] if date_parts else date.strip()
            month = date_parts[0].strip('.') if len(date_parts) > 1 else None

            return {
                'type': 'inproceedings',
                'author': author.strip(),
                'title': title.strip(),
                'booktitle': booktitle.strip(),
                'address': location.strip(),
                'year': year,
                'month': month,
                'pages': pages.strip() if pages else None,
                'volume': volume.strip() if volume else None
            }

    return None

def parse_ieee_incollection(ref_text: str) -> Optional[Dict]:
    """Parse IEEE book chapter citation format."""
    # Pattern: Author, "Title," in BookTitle, Editors, Eds. Publisher, Year, pp. A-B.
    pattern = r'^(.+?),\s+"(.+?),"?\s+in\s+\*(.+?)\*,\s+(.+?),\s+Eds?\.\s+(.+?):\s+(.+?),\s+(\d{4}),\s+pp\.\s+([\d\-]+)\.'

    match = re.match(pattern, ref_text)
    if match:
        author, title, booktitle, editors, city, publisher, year, pages = match.groups()
        return {
            'type': 'incollection',
            'author': author.strip(),
            'title': title.strip(),
            'booktitle': booktitle.strip(),
            'editor': editors.strip(),
            'publisher': publisher.strip(),
            'address': city.strip(),
            'year': year.strip(),
            'pages': pages.strip()
        }

    return None

def parse_ieee_phdthesis(ref_text: str) -> Optional[Dict]:
    """Parse IEEE PhD dissertation citation format."""
    # Pattern: Author, "Title," Ph.D. dissertation, Dept., Institution, City, State, Year.
    pattern = r'^(.+?),\s+"(.+?),"?\s+Ph\.D\.\s+dissertation,\s+(.+?),\s+(.+?),\s+(.+?),\s+(.+?),\s+(\d{4})\.'

    match = re.match(pattern, ref_text)
    if match:
        author, title, dept, institution, city, state, year = match.groups()
        return {
            'type': 'phdthesis',
            'author': author.strip(),
            'title': title.strip(),
            'school': f"{institution}, {dept}".strip(),
            'address': f"{city}, {state}".strip(),
            'year': year.strip()
        }

    return None

def parse_ieee_techreport(ref_text: str) -> Optional[Dict]:
    """Parse IEEE technical report citation format."""
    # Pattern: Author, "Title," Institution, Tech. Rep. Number, Location, Year.
    pattern = r'^(.+?),\s+"(.+?),"?\s+(.+?),\s+Tech\.\s+Rep\.\s+(.+?),\s+(.+?),\s+(.+?),\s+(\d{4})\.'

    match = re.match(pattern, ref_text)
    if match:
        author, title, institution, number, dept, location, year = match.groups()
        return {
            'type': 'techreport',
            'author': author.strip(),
            'title': title.strip(),
            'institution': f"{institution}, {dept}".strip(),
            'number': number.strip(),
            'address': location.strip(),
            'year': year.strip()
        }

    return None

def parse_ieee_reference(ref_num: int, ref_text: str) -> Dict:
    """Parse any IEEE reference format and return BibTeX dict."""
    # Try all parsers in order
    parsers = [
        parse_ieee_article,
        parse_ieee_inproceedings,
        parse_ieee_incollection,
        parse_ieee_phdthesis,
        parse_ieee_techreport,
        parse_ieee_book,
    ]

    for parser in parsers:
        result = parser(ref_text)
        if result:
            result['key'] = f"ref{ref_num}"
            return result

    # Fallback: create misc entry with full text
    return {
        'type': 'misc',
        'key': f"ref{ref_num}",
        'note': ref_text[:200] + "..." if len(ref_text) > 200 else ref_text
    }

def format_bibtex_entry(ref: Dict) -> str:
    """Format parsed reference as BibTeX entry."""
    entry_type = ref['type']
    key = ref['key']

    lines = [f"@{entry_type}{{{key},"]

    # Common fields
    if 'author' in ref and ref['author']:
        lines.append(f"  author = {{{ref['author']}}},")
    if 'title' in ref and ref['title']:
        lines.append(f"  title = {{{{{ref['title']}}}}},")

    # Type-specific fields
    if entry_type == 'article':
        if 'journal' in ref: lines.append(f"  journal = {{{ref['journal']}}},")
        if 'volume' in ref: lines.append(f"  volume = {{{ref['volume']}}},")
        if 'number' in ref: lines.append(f"  number = {{{ref['number']}}},")
        if 'pages' in ref: lines.append(f"  pages = {{{ref['pages']}}},")
        if 'month' in ref and ref['month']: lines.append(f"  month = {ref['month']},")
        if 'year' in ref: lines.append(f"  year = {{{ref['year']}}}")

    elif entry_type == 'book':
        if 'publisher' in ref: lines.append(f"  publisher = {{{ref['publisher']}}},")
        if 'address' in ref: lines.append(f"  address = {{{ref['address']}}},")
        if 'edition' in ref and ref['edition']: lines.append(f"  edition = {{{ref['edition']}}},")
        if 'year' in ref: lines.append(f"  year = {{{ref['year']}}}")

    elif entry_type == 'inproceedings':
        if 'booktitle' in ref: lines.append(f"  booktitle = {{{ref['booktitle']}}},")
        if 'address' in ref: lines.append(f"  address = {{{ref['address']}}},")
        if 'volume' in ref and ref['volume']: lines.append(f"  volume = {{{ref['volume']}}},")
        if 'pages' in ref: lines.append(f"  pages = {{{ref['pages']}}},")
        if 'month' in ref and ref['month']: lines.append(f"  month = {ref['month']},")
        if 'year' in ref: lines.append(f"  year = {{{ref['year']}}}")

    elif entry_type == 'incollection':
        if 'booktitle' in ref: lines.append(f"  booktitle = {{{ref['booktitle']}}},")
        if 'editor' in ref: lines.append(f"  editor = {{{ref['editor']}}},")
        if 'publisher' in ref: lines.append(f"  publisher = {{{ref['publisher']}}},")
        if 'address' in ref: lines.append(f"  address = {{{ref['address']}}},")
        if 'pages' in ref: lines.append(f"  pages = {{{ref['pages']}}},")
        if 'year' in ref: lines.append(f"  year = {{{ref['year']}}}")

    elif entry_type == 'phdthesis':
        if 'school' in ref: lines.append(f"  school = {{{ref['school']}}},")
        if 'address' in ref: lines.append(f"  address = {{{ref['address']}}},")
        if 'year' in ref: lines.append(f"  year = {{{ref['year']}}}")

    elif entry_type == 'techreport':
        if 'institution' in ref: lines.append(f"  institution = {{{ref['institution']}}},")
        if 'number' in ref: lines.append(f"  number = {{{ref['number']}}},")
        if 'address' in ref: lines.append(f"  address = {{{ref['address']}}},")
        if 'year' in ref: lines.append(f"  year = {{{ref['year']}}}")

    elif entry_type == 'misc':
        if 'note' in ref: lines.append(f"  note = {{{{{ref['note']}}}}}")

    lines.append("}")
    return '\n'.join(lines)

def extract_references_from_markdown() -> Dict[int, str]:
    """Extract all references from markdown file."""
    with open(INPUT_PAPER, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    references = {}
    in_references = False
    current_ref_num = None
    current_ref_text = []

    for line in lines:
        if "## References" in line:
            in_references = True
            continue

        if in_references:
            # Stop at appendices or end markers
            if line.startswith("##") and "Appendix" in line:
                break
            if "---" in line and current_ref_num:
                # Save last reference
                if current_ref_text:
                    references[current_ref_num] = ' '.join(current_ref_text).strip()
                break

            # Match reference number: [1] Author, ...
            match = re.match(r'^\[(\d+)\]\s+(.+)', line.strip())
            if match:
                # Save previous reference
                if current_ref_num and current_ref_text:
                    references[current_ref_num] = ' '.join(current_ref_text).strip()

                # Start new reference
                current_ref_num = int(match.group(1))
                current_ref_text = [match.group(2)]
            elif current_ref_num and line.strip():
                # Continuation of current reference
                current_ref_text.append(line.strip())

    # Save last reference
    if current_ref_num and current_ref_text:
        references[current_ref_num] = ' '.join(current_ref_text).strip()

    return references

def main():
    print("\n" + "="*70)
    print("LT-7 BIBLIOGRAPHY COMPLETION")
    print("="*70 + "\n")

    print("[INFO] Extracting references from markdown...")
    references = extract_references_from_markdown()
    print(f"[OK] Found {len(references)} references\n")

    print("[INFO] Parsing IEEE citations...")
    bibtex_entries = []
    parse_stats = {'article': 0, 'book': 0, 'inproceedings': 0,
                   'incollection': 0, 'phdthesis': 0, 'techreport': 0, 'misc': 0}

    for ref_num in sorted(references.keys()):
        ref_text = references[ref_num]
        parsed = parse_ieee_reference(ref_num, ref_text)
        bibtex_entry = format_bibtex_entry(parsed)
        bibtex_entries.append(bibtex_entry)
        parse_stats[parsed['type']] += 1

        if parsed['type'] == 'misc':
            # Handle Unicode characters in console output
            safe_text = ref_text[:80].encode('ascii', errors='replace').decode('ascii')
            print(f"[WARNING] Could not parse [{ref_num}]: {safe_text}...")

    print(f"\n[INFO] Parse statistics:")
    for entry_type, count in parse_stats.items():
        if count > 0:
            print(f"     {entry_type}: {count}")

    print(f"\n[INFO] Writing BibTeX file...")
    with open(OUTPUT_BIB, 'w', encoding='utf-8') as f:
        f.write("% LT-7 Research Paper Bibliography\n")
        f.write("% Auto-generated from IEEE formatted references\n")
        f.write(f"% Total entries: {len(bibtex_entries)}\n")
        f.write("% Format: IEEE style\n\n")

        for i, entry in enumerate(bibtex_entries, 1):
            f.write(entry)
            f.write("\n\n")

    print(f"[OK] Bibliography written to: {OUTPUT_BIB}")
    print(f"     Total entries: {len(bibtex_entries)}")
    print(f"     Successfully parsed: {len(bibtex_entries) - parse_stats['misc']}/{len(bibtex_entries)}")

    if parse_stats['misc'] > 0:
        print(f"\n[WARNING] {parse_stats['misc']} entries fell back to 'misc' type")
        print(f"          Review these entries manually in {OUTPUT_BIB}")
    else:
        print(f"\n[OK] All references successfully parsed!")

    print()

if __name__ == "__main__":
    main()
