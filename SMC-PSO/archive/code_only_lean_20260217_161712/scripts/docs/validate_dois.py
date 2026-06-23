#!/usr/bin/env python3
"""
Validate DOI accessibility by checking HTTP status codes.

This script:
1. Extracts all DOI/URL entries from BibTeX files
2. Checks HTTP accessibility (200 OK)
3. Reports broken links and success rate

Usage:
    python scripts/docs/validate_dois.py
    python scripts/docs/validate_dois.py --timeout 10 --max-retries 3
"""
# example-metadata:
# runnable: true
# expected_result: DOI accessibility report with ≥95% success rate

import argparse
import re
import time
from pathlib import Path
from typing import Dict, List, Tuple
import sys

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("[WARN] 'requests' module not available. Install with: pip install requests")


def parse_bibtex_dois(bib_path: Path) -> List[Dict[str, str]]:
    """
    Extract DOI and URL entries from BibTeX file.

    Returns:
        List of dicts with {key, type, doi, url, source_file}
    """
    entries = []
    content = bib_path.read_text(encoding='utf-8')

    # Find all entry starts: @type{key,
    entry_start_pattern = r'@(\w+)\{([^,]+),'

    for match in re.finditer(entry_start_pattern, content):
        entry_type = match.group(1)
        key = match.group(2).strip()
        start_pos = match.end()

        # Count braces to find matching closing brace
        brace_count = 1  # We already have the opening brace from @type{
        pos = start_pos
        while pos < len(content) and brace_count > 0:
            if content[pos] == '{':
                brace_count += 1
            elif content[pos] == '}':
                brace_count -= 1
            pos += 1

        if brace_count == 0:
            # Extract entry body between opening and closing braces
            body = content[start_pos:pos-1]

            # Extract DOI and URL from full entry body
            doi_match = re.search(r'doi\s*=\s*\{([^}]+)\}', body, re.IGNORECASE)
            url_match = re.search(r'url\s*=\s*\{([^}]+)\}', body, re.IGNORECASE)

            doi = doi_match.group(1).strip() if doi_match else None
            url = url_match.group(1).strip() if url_match else None

            entries.append({
                'key': key,
                'type': entry_type,
                'doi': doi,
                'url': url,
                'source_file': bib_path.name
            })

    return entries


def check_doi_accessibility(doi: str, timeout: int = 10) -> Tuple[bool, int, str]:
    """
    Check if a DOI resolves successfully.

    Args:
        doi: DOI string (e.g., "10.1109/TCST.2014.2329187")
        timeout: Request timeout in seconds

    Returns:
        (accessible, status_code, message)
    """
    if not REQUESTS_AVAILABLE:
        return False, 0, "requests module not installed"

    # Construct DOI URL
    if doi.startswith('http'):
        url = doi
    else:
        url = f"https://doi.org/{doi}"

    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        accessible = 200 <= response.status_code < 400
        return accessible, response.status_code, "OK" if accessible else f"HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        return False, 0, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, 0, "Connection error"
    except requests.exceptions.RequestException as e:
        return False, 0, str(e)[:50]


def check_url_accessibility(url: str, timeout: int = 10) -> Tuple[bool, int, str]:
    """
    Check if a URL is accessible.

    Args:
        url: Full URL string
        timeout: Request timeout in seconds

    Returns:
        (accessible, status_code, message)
    """
    if not REQUESTS_AVAILABLE:
        return False, 0, "requests module not installed"

    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        accessible = 200 <= response.status_code < 400
        return accessible, response.status_code, "OK" if accessible else f"HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        return False, 0, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, 0, "Connection error"
    except requests.exceptions.RequestException as e:
        return False, 0, str(e)[:50]


def main():
    # Fix Windows UTF-8 encoding
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description='Validate DOI/URL accessibility')
    parser.add_argument('--bibtex', type=Path, default=Path('docs/bib'),
                        help='Directory containing BibTeX files')
    parser.add_argument('--timeout', type=int, default=10,
                        help='Request timeout in seconds')
    parser.add_argument('--delay', type=float, default=0.5,
                        help='Delay between requests (seconds)')
    parser.add_argument('--max-retries', type=int, default=2,
                        help='Maximum retry attempts for failed requests')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed validation results')

    args = parser.parse_args()

    if not REQUESTS_AVAILABLE:
        print("[FAIL] Cannot validate DOI accessibility without 'requests' module")
        print("       Install with: pip install requests")
        return 1

    print("=" * 80)
    print("DOI/URL ACCESSIBILITY VALIDATION")
    print("=" * 80)
    print()

    # Collect all entries
    all_entries = []
    bib_files = list(args.bibtex.glob('*.bib'))

    if not bib_files:
        print(f"[FAIL] No .bib files found in {args.bibtex}")
        return 1

    print(f"[BIB] Parsing BibTeX files from {args.bibtex}")
    for bib_file in bib_files:
        entries = parse_bibtex_dois(bib_file)
        all_entries.extend(entries)
        print(f"  [OK] {bib_file.name}: {len(entries)} entries")

    print(f"\n  Total entries: {len(all_entries)}")
    print()

    # Check accessibility
    print("=" * 80)
    print("Checking DOI/URL Accessibility")
    print("=" * 80)
    print(f"Timeout: {args.timeout}s | Delay: {args.delay}s | Max retries: {args.max_retries}")
    print()

    accessible_count = 0
    inaccessible_count = 0
    no_link_count = 0
    results = []

    for i, entry in enumerate(all_entries, 1):
        key = entry['key']
        doi = entry['doi']
        url = entry['url']

        if not doi and not url:
            no_link_count += 1
            results.append({
                'key': key,
                'accessible': False,
                'status': 0,
                'message': 'No DOI/URL',
                'source': entry['source_file']
            })
            continue

        # Try DOI first, then URL
        link_type = 'DOI' if doi else 'URL'

        # Retry logic
        accessible = False
        status = 0
        message = ""

        for attempt in range(args.max_retries + 1):
            if doi:
                accessible, status, message = check_doi_accessibility(doi, args.timeout)
            else:
                accessible, status, message = check_url_accessibility(url, args.timeout)

            if accessible:
                break

            if attempt < args.max_retries:
                time.sleep(args.delay * 2)  # Longer delay on retry

        if accessible:
            accessible_count += 1
            if args.verbose:
                print(f"  [OK] [{i}/{len(all_entries)}] {key} ({link_type}): {message}")
        else:
            inaccessible_count += 1
            print(f"  [FAIL] [{i}/{len(all_entries)}] {key} ({link_type}): {message}")

        results.append({
            'key': key,
            'accessible': accessible,
            'status': status,
            'message': message,
            'link_type': link_type,
            'source': entry['source_file']
        })

        # Rate limiting
        if i < len(all_entries):
            time.sleep(args.delay)

    print()

    # Calculate success rate
    total_with_links = accessible_count + inaccessible_count
    success_rate = 100 * accessible_count / total_with_links if total_with_links > 0 else 0

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total entries:         {len(all_entries)}")
    print(f"No DOI/URL:            {no_link_count}")
    print(f"Accessible:            {accessible_count}")
    print(f"Inaccessible:          {inaccessible_count}")
    print(f"Success rate:          {success_rate:.1f}%")
    print()

    # Show inaccessible entries
    if inaccessible_count > 0:
        print("Inaccessible entries:")
        for result in results:
            if not result['accessible'] and result['message'] != 'No DOI/URL':
                print(f"  - {result['key']} [{result['source']}]: {result['message']}")
        print()

    # Exit code based on success rate
    if success_rate >= 95:
        print("[PASS] VALIDATION PASSED (>=95% target)")
        return 0
    else:
        print("[FAIL] VALIDATION FAILED (<95% target)")
        print(f"       Need {int((0.95 * total_with_links) - accessible_count)} more accessible link(s)")
        return 1


if __name__ == '__main__':
    sys.exit(main())
