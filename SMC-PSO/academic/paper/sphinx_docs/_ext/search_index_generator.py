"""
============================================================================
LUNR.JS SEARCH INDEX GENERATOR FOR SPHINX
============================================================================
Purpose: Generate Lunr.js-compatible search index from Sphinx HTML output
Usage: Automatically runs after Sphinx HTML build completes
Output: docs/_build/html/_static/searchindex.json
============================================================================
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Dict, Any


def extract_text_from_html(html_path: Path) -> Dict[str, str]:
    """
    Extract title, headings, and body text from an HTML file.

    Args:
        html_path: Path to HTML file

    Returns:
        Dictionary with 'title', 'headings', 'body' keys
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Extract title
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else ''

    # Remove " — DIP_SMC_PSO Documentation" suffix
    title = re.sub(r'\s*—\s*DIP_SMC_PSO Documentation$', '', title)

    # Extract headings (h1-h6)
    headings = []
    for i in range(1, 7):
        for heading in soup.find_all(f'h{i}'):
            text = heading.get_text(strip=True)
            # Remove permalink symbols
            text = re.sub(r'[¶#]+$', '', text)
            if text:
                headings.append(text)

    # Extract body text from main content
    # Look for common Sphinx/Furo content containers
    content_selectors = [
        'article',  # Furo theme
        'div.body',  # Classic theme
        'div.document',  # RTD theme
        'main',  # Generic
    ]

    body_text = ''
    for selector in content_selectors:
        content = soup.select_one(selector)
        if content:
            # Remove script and style elements
            for script in content(['script', 'style', 'nav', 'header', 'footer']):
                script.decompose()

            body_text = content.get_text(separator=' ', strip=True)
            break

    # Clean up whitespace
    body_text = re.sub(r'\s+', ' ', body_text)

    return {
        'title': title,
        'headings': ' '.join(headings),
        'body': body_text[:1000],  # Limit to first 1000 chars for index size
    }


def generate_search_index(build_dir: Path, output_path: Path) -> None:
    """
    Generate Lunr.js search index from Sphinx HTML output.

    Args:
        build_dir: Path to Sphinx HTML build directory
        output_path: Path to output searchindex.json
    """
    print('[SEARCH] Generating Lunr.js search index...')

    documents = []

    # Find all HTML files (excluding special Sphinx pages)
    exclude_patterns = [
        'genindex.html',
        'search.html',
        'modindex.html',
        '_sources',
        '_static',
        '_modules',
    ]

    html_files = []
    for html_file in build_dir.rglob('*.html'):
        # Skip excluded files
        if any(pattern in str(html_file) for pattern in exclude_patterns):
            continue
        html_files.append(html_file)

    print(f'[SEARCH] Found {len(html_files)} HTML files to index')

    # Extract content from each HTML file
    for i, html_path in enumerate(html_files):
        if (i + 1) % 100 == 0:
            print(f'[SEARCH] Processing {i + 1}/{len(html_files)} files...')

        # Get relative URL
        rel_path = html_path.relative_to(build_dir)
        url = '/' + str(rel_path).replace('\\', '/')

        # Extract content
        try:
            content = extract_text_from_html(html_path)

            # Create document for Lunr index
            doc = {
                'id': str(i),
                'url': url,
                'title': content['title'],
                'headings': content['headings'],
                'body': content['body'],
            }

            documents.append(doc)

        except Exception as e:
            print(f'[SEARCH] Warning: Failed to process {html_path}: {e}')
            continue

    print(f'[SEARCH] Indexed {len(documents)} documents')

    # Create Lunr.js index structure
    # We'll build the index client-side for better compatibility
    index_data = {
        'version': '1.0',
        'docs': documents,
        'fields': ['title', 'headings', 'body'],
        'pipeline': ['stemmer'],
    }

    # Write to JSON file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False)

    # Calculate file size
    file_size_kb = output_path.stat().st_size / 1024
    print(f'[SEARCH] Search index saved to {output_path}')
    print(f'[SEARCH] Index size: {file_size_kb:.1f} KB')
    print(f'[SEARCH] Done!')


def build_search_index(app, exception):
    """
    Sphinx build-finished event handler.

    Called automatically after Sphinx HTML build completes.
    """
    # Only generate search index for HTML builds
    if app.builder.name != 'html':
        return

    # Proceed even if there were warnings/exceptions from other extensions
    # (as long as HTML files were successfully generated)

    # Paths
    build_dir = Path(app.outdir)
    output_path = build_dir / '_static' / 'searchindex.json'

    # Generate index
    try:
        generate_search_index(build_dir, output_path)
    except Exception as e:
        print(f'[SEARCH] Error generating search index: {e}')
        import traceback
        traceback.print_exc()


def setup(app):
    """
    Sphinx extension setup.
    """
    app.connect('build-finished', build_search_index)

    return {
        'version': '1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
