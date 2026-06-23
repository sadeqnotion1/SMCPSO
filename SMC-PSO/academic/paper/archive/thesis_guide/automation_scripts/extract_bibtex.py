#!/usr/bin/env python
"""
BibTeX Citation Extractor

Extracts citation information from CITATIONS_ACADEMIC.md and formats
as BibTeX entries for thesis bibliography.

Usage:
    python extract_bibtex.py input.md output_dir/

Example:
    python extract_bibtex.py docs/CITATIONS_ACADEMIC.md thesis/bibliography/

Saves ~5 hours of manual citation formatting!
"""

import argparse
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple


class CitationExtractor:
    """Extract and format citations as BibTeX."""

    def __init__(self):
        """Initialize citation extractor."""
        self.books = []
        self.articles = []
        self.conference = []
        self.software = []

    def extract_book_citation(self, text: str) -> Dict:
        """
        Extract book citation information.

        Args:
            text (str): Citation text

        Returns:
            dict: Parsed citation information
        """
        # Pattern: Author(s) (Year). Title. Publisher.
        pattern = r'([^(]+)\((\d{4})\)\.\s*\*?(.+?)\*?\.\s*(.+?)\.'

        match = re.search(pattern, text)
        if not match:
            return None

        authors_raw = match.group(1).strip()
        year = match.group(2)
        title = match.group(3).strip()
        publisher = match.group(4).strip()

        # Parse authors
        authors = self.parse_authors(authors_raw)

        # Generate citation key: FirstAuthorYear
        first_author_last = authors.split(' and ')[0].split(',')[0].strip()
        key = f"{first_author_last.replace(' ', '').replace('.', '')}{year}"

        return {
            'type': 'book',
            'key': key,
            'author': authors,
            'year': year,
            'title': title,
            'publisher': publisher,
        }

    def extract_article_citation(self, text: str) -> Dict:
        """
        Extract journal article citation.

        Args:
            text (str): Citation text

        Returns:
            dict: Parsed citation information
        """
        # Pattern: Author(s) (Year). "Title." Journal, volume(issue), pages.
        pattern = r'([^(]+)\((\d{4})\)\.\s*"(.+?)"\.\s*\*?(.+?)\*?,\s*(\d+)\((\d+)\),\s*([\d-]+)\.'

        match = re.search(pattern, text)
        if not match:
            return None

        authors_raw = match.group(1).strip()
        year = match.group(2)
        title = match.group(3).strip()
        journal = match.group(4).strip()
        volume = match.group(5)
        number = match.group(6)
        pages = match.group(7)

        authors = self.parse_authors(authors_raw)

        first_author_last = authors.split(' and ')[0].split(',')[0].strip()
        key = f"{first_author_last.replace(' ', '').replace('.', '')}{year}"

        return {
            'type': 'article',
            'key': key,
            'author': authors,
            'year': year,
            'title': title,
            'journal': journal,
            'volume': volume,
            'number': number,
            'pages': pages,
        }

    def extract_conference_citation(self, text: str) -> Dict:
        """
        Extract conference paper citation.

        Args:
            text (str): Citation text

        Returns:
            dict: Parsed citation information
        """
        # Pattern: Author(s) (Year). "Title." Proceedings of Conference, pages.
        pattern = r'([^(]+)\((\d{4})\)\.\s*"(.+?)"\.\s*\*?(.+?)\*?,\s*([\d-]+)\.'

        match = re.search(pattern, text)
        if not match:
            return None

        authors_raw = match.group(1).strip()
        year = match.group(2)
        title = match.group(3).strip()
        booktitle = match.group(4).strip()
        pages = match.group(5)

        authors = self.parse_authors(authors_raw)

        first_author_last = authors.split(' and ')[0].split(',')[0].strip()
        key = f"{first_author_last.replace(' ', '').replace('.', '')}{year}"

        return {
            'type': 'inproceedings',
            'key': key,
            'author': authors,
            'year': year,
            'title': title,
            'booktitle': booktitle,
            'pages': pages,
        }

    def parse_authors(self, authors_raw: str) -> str:
        """
        Parse author names to BibTeX format.

        Args:
            authors_raw (str): Raw author string

        Returns:
            str: BibTeX formatted author string
        """
        # Split by commas or "and"
        if ' and ' in authors_raw.lower():
            authors_list = re.split(r'\s+and\s+', authors_raw, flags=re.IGNORECASE)
        else:
            authors_list = [authors_raw]

        # Clean each author name
        cleaned = []
        for author in authors_list:
            author = author.strip().rstrip(',').rstrip('.')
            # Remove trailing commas/periods
            author = re.sub(r'[,\.]+$', '', author)
            cleaned.append(author)

        return ' and '.join(cleaned)

    def format_bibtex_book(self, citation: Dict) -> str:
        """
        Format book citation as BibTeX.

        Args:
            citation (dict): Citation information

        Returns:
            str: BibTeX entry
        """
        return f"""@book{{{citation['key']},
  author    = {{{citation['author']}}},
  title     = {{{citation['title']}}},
  publisher = {{{citation['publisher']}}},
  year      = {{{citation['year']}}}
}}"""

    def format_bibtex_article(self, citation: Dict) -> str:
        """
        Format article citation as BibTeX.

        Args:
            citation (dict): Citation information

        Returns:
            str: BibTeX entry
        """
        return f"""@article{{{citation['key']},
  author  = {{{citation['author']}}},
  title   = {{{citation['title']}}},
  journal = {{{citation['journal']}}},
  volume  = {{{citation['volume']}}},
  number  = {{{citation['number']}}},
  pages   = {{{citation['pages']}}},
  year    = {{{citation['year']}}}
}}"""

    def format_bibtex_inproceedings(self, citation: Dict) -> str:
        """
        Format conference paper as BibTeX.

        Args:
            citation (dict): Citation information

        Returns:
            str: BibTeX entry
        """
        return f"""@inproceedings{{{citation['key']},
  author    = {{{citation['author']}}},
  title     = {{{citation['title']}}},
  booktitle = {{{citation['booktitle']}}},
  pages     = {{{citation['pages']}}},
  year      = {{{citation['year']}}}
}}"""

    def parse_markdown_file(self, md_path: Path) -> None:
        """
        Parse markdown file and extract citations.

        Args:
            md_path (Path): Path to markdown file
        """
        print(f"[INFO] Reading: {md_path}")

        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into sections
        lines = content.split('\n')

        current_section = None
        for line in lines:
            # Detect section headers
            if line.startswith('### Books'):
                current_section = 'books'
                print("[INFO] Parsing books section...")
            elif line.startswith('### Journal Papers'):
                current_section = 'articles'
                print("[INFO] Parsing journal papers section...")
            elif line.startswith('### Conference Papers'):
                current_section = 'conference'
                print("[INFO] Parsing conference papers section...")

            # Extract numbered list items
            if line.strip().startswith(tuple(f'{i}.' for i in range(1, 100))):
                citation_text = line[line.index('.')+1:].strip()

                if current_section == 'books':
                    citation = self.extract_book_citation(citation_text)
                    if citation:
                        self.books.append(citation)

                elif current_section == 'articles':
                    citation = self.extract_article_citation(citation_text)
                    if citation:
                        self.articles.append(citation)

                elif current_section == 'conference':
                    citation = self.extract_conference_citation(citation_text)
                    if citation:
                        self.conference.append(citation)

        print(f"[OK] Extracted: {len(self.books)} books, {len(self.articles)} articles, {len(self.conference)} conference papers")

    def write_bibtex_files(self, output_dir: Path) -> None:
        """
        Write BibTeX files.

        Args:
            output_dir (Path): Output directory
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write books
        if self.books:
            books_path = output_dir / 'books.bib'
            with open(books_path, 'w', encoding='utf-8') as f:
                f.write("% Books - Auto-generated from CITATIONS_ACADEMIC.md\n\n")
                for citation in self.books:
                    f.write(self.format_bibtex_book(citation))
                    f.write("\n\n")
            print(f"[OK] Written: {books_path} ({len(self.books)} entries)")

        # Write journal articles
        if self.articles:
            articles_path = output_dir / 'papers.bib'
            with open(articles_path, 'w', encoding='utf-8') as f:
                f.write("% Journal Papers - Auto-generated from CITATIONS_ACADEMIC.md\n\n")
                for citation in self.articles:
                    f.write(self.format_bibtex_article(citation))
                    f.write("\n\n")
            print(f"[OK] Written: {articles_path} ({len(self.articles)} entries)")

        # Write conference papers
        if self.conference:
            conference_path = output_dir / 'conference.bib'
            with open(conference_path, 'w', encoding='utf-8') as f:
                f.write("% Conference Papers - Auto-generated from CITATIONS_ACADEMIC.md\n\n")
                for citation in self.conference:
                    f.write(self.format_bibtex_inproceedings(citation))
                    f.write("\n\n")
            print(f"[OK] Written: {conference_path} ({len(self.conference)} entries)")

        # Write combined file
        combined_path = output_dir / 'references.bib'
        with open(combined_path, 'w', encoding='utf-8') as f:
            f.write("% Complete Bibliography - Auto-generated from CITATIONS_ACADEMIC.md\n")
            f.write("% Includes books, journal papers, and conference papers\n\n")

            if self.books:
                f.write("% ========== BOOKS ==========\n\n")
                for citation in self.books:
                    f.write(self.format_bibtex_book(citation))
                    f.write("\n\n")

            if self.articles:
                f.write("% ========== JOURNAL PAPERS ==========\n\n")
                for citation in self.articles:
                    f.write(self.format_bibtex_article(citation))
                    f.write("\n\n")

            if self.conference:
                f.write("% ========== CONFERENCE PAPERS ==========\n\n")
                for citation in self.conference:
                    f.write(self.format_bibtex_inproceedings(citation))
                    f.write("\n\n")

        print(f"[OK] Written: {combined_path} ({len(self.books) + len(self.articles) + len(self.conference)} entries)")


def main():
    parser = argparse.ArgumentParser(
        description='Extract citations from markdown and format as BibTeX',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_bibtex.py docs/CITATIONS_ACADEMIC.md thesis/bibliography/

  python extract_bibtex.py --help

Output Files:
  - books.bib       : Book citations only
  - papers.bib      : Journal article citations only
  - conference.bib  : Conference paper citations only
  - references.bib  : All citations combined

Features:
  - Automatic author name parsing
  - IEEE-style BibTeX formatting
  - Citation key generation (AuthorYear format)
  - Separate files by publication type
        """
    )

    parser.add_argument('input', help='Input markdown file (CITATIONS_ACADEMIC.md)')
    parser.add_argument('output_dir', help='Output directory for .bib files')
    parser.add_argument('--dry-run', action='store_true',
                       help='Parse only, do not write files')

    args = parser.parse_args()

    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {args.input}")
        sys.exit(1)

    output_dir = Path(args.output_dir)

    # Extract citations
    extractor = CitationExtractor()
    extractor.parse_markdown_file(input_path)

    if extractor.books == [] and extractor.articles == [] and extractor.conference == []:
        print("[WARNING] No citations extracted - check input file format")
        sys.exit(1)

    # Write output
    if args.dry_run:
        print("\n[INFO] Dry run mode - files not written")
        print(f"[INFO] Would write to: {output_dir}")
    else:
        extractor.write_bibtex_files(output_dir)
        print("\n[OK] BibTeX extraction complete")
        print(f"[INFO] Total entries: {len(extractor.books) + len(extractor.articles) + len(extractor.conference)}")


if __name__ == '__main__':
    main()
