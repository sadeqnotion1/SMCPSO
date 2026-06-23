#======================================================================================\\\
#========== tests/test_documentation/test_cross_references.py =========================\\\
#======================================================================================\\\

"""Validation test suite for documentation cross-references.

This module tests that all internal links in documentation are valid
and that documents are properly cross-referenced.

Usage:
    pytest tests/test_documentation/test_cross_references.py -v
"""

import json
from pathlib import Path
import pytest


# Load cross-reference analysis results
ARTIFACTS_DIR = Path('.test_artifacts/cross_references')
DB_FILE = ARTIFACTS_DIR / 'cross_reference_database.json'
BROKEN_FILE = ARTIFACTS_DIR / 'broken_links.json'
STATS_FILE = ARTIFACTS_DIR / 'statistics.json'


def load_cross_reference_data():
    """Load cross-reference analysis data."""
    if not DB_FILE.exists():
        pytest.skip(f"Cross-reference database not found: {DB_FILE}", allow_module_level=True)

    with open(DB_FILE, 'r', encoding='utf-8') as f:
        db = json.load(f)

    with open(BROKEN_FILE, 'r', encoding='utf-8') as f:
        broken = json.load(f)

    with open(STATS_FILE, 'r', encoding='utf-8') as f:
        stats = json.load(f)

    return db, broken, stats


# Load data once at module level
try:
    CROSS_REF_DB, BROKEN_LINKS, STATISTICS = load_cross_reference_data()
except Exception:  # Catch pytest.skip or file errors
    CROSS_REF_DB = {'cross_references': {}, 'external_links': {}}
    BROKEN_LINKS = []
    STATISTICS = {}


# =====================================================================================
# Link Validation Tests
# =====================================================================================

def test_no_broken_internal_links():
    """Test that all internal documentation links are valid."""
    if not BROKEN_LINKS:
        return  # All links valid

    # Filter out false positives (mathematical notation, etc.)
    false_positives = ['t', 't+1', 't-1', 'x', 'y', 'z', 'i', 'j', 'k']

    real_broken = [
        link for link in BROKEN_LINKS
        if link['target'] not in false_positives
    ]

    if real_broken:
        # Group by source file
        by_source = {}
        for link in real_broken:
            by_source.setdefault(link['source'], []).append(link)

        # Create detailed error message
        error_msg = f"\nFound {len(real_broken)} broken internal links:\n\n"
        for source, links in sorted(by_source.items())[:10]:  # Show first 10 files
            error_msg += f"  {source}:\n"
            for link in links[:3]:  # Show first 3 links per file
                error_msg += f"    Line {link['line']}: [{link['text']}]({link['target']})\n"

        if len(by_source) > 10:
            error_msg += f"\n  ... and {len(by_source) - 10} more files with broken links\n"

        pytest.fail(error_msg)


def test_link_coverage_adequate():
    """Test that documentation has adequate cross-referencing."""
    link_density = STATISTICS.get('link_density', 0)
    docs_with_links_pct = (STATISTICS.get('documents_with_links', 0) /
                           STATISTICS.get('total_documents', 1)) * 100

    # Minimum thresholds
    MIN_LINK_DENSITY = 0.5  # At least 0.5 links per document
    MIN_DOCS_WITH_LINKS_PCT = 10  # At least 10% of docs have links

    assert link_density >= MIN_LINK_DENSITY, \
        f"Link density too low: {link_density:.2f} (target: ≥{MIN_LINK_DENSITY})"

    assert docs_with_links_pct >= MIN_DOCS_WITH_LINKS_PCT, \
        f"Too few documents with links: {docs_with_links_pct:.1f}% (target: ≥{MIN_DOCS_WITH_LINKS_PCT}%)"


def test_critical_docs_not_orphaned():
    """Test that critical documentation files are not orphaned."""
    # Load orphaned documents
    orphaned_file = ARTIFACTS_DIR / 'orphaned_docs.json'
    if not orphaned_file.exists():
        pytest.skip("Orphaned documents list not found")

    with open(orphaned_file, 'r', encoding='utf-8') as f:
        orphaned = json.load(f)

    # Critical documents that MUST be referenced
    critical_docs = [
        'guides/getting-started.md',
        'guides/user-guide.md',
        'guides/INDEX.md',
        'guides/tutorials/tutorial-01-first-simulation.md',
        'api/index.md',
    ]

    orphaned_critical = [doc for doc in critical_docs if doc in orphaned]

    if orphaned_critical:
        pytest.fail(
            "Critical documents are orphaned (no incoming links):\n" +
            "\n".join(f"  - {doc}" for doc in orphaned_critical)
        )


# =====================================================================================
# Cross-Reference Pattern Tests
# =====================================================================================

def test_tutorials_link_to_api():
    """Test that tutorials link to relevant API documentation."""
    cross_refs = CROSS_REF_DB['cross_references']

    # Find tutorial files
    tutorials = [doc for doc in cross_refs if 'tutorial' in doc.lower()]

    tutorials_with_api_links = 0
    for tutorial in tutorials:
        refs = cross_refs[tutorial]
        has_api_link = any('api/' in ref['target'] for ref in refs if ref['exists'])
        if has_api_link:
            tutorials_with_api_links += 1

    if tutorials:
        api_link_ratio = tutorials_with_api_links / len(tutorials)
        # At least 50% of tutorials should link to API docs
        assert api_link_ratio >= 0.5, \
            f"Too few tutorials link to API docs: {api_link_ratio:.1%} (target: ≥50%)"


def test_api_docs_link_to_examples():
    """Test that API documentation links to examples or tutorials."""
    cross_refs = CROSS_REF_DB['cross_references']

    # Find API files
    api_docs = [doc for doc in cross_refs if 'api/' in doc]

    api_with_example_links = 0
    for api_doc in api_docs:
        refs = cross_refs[api_doc]
        has_example_link = any(
            'example' in ref['target'].lower() or
            'tutorial' in ref['target'].lower() or
            'guide' in ref['target'].lower()
            for ref in refs if ref['exists']
        )
        if has_example_link:
            api_with_example_links += 1

    if api_docs and len(api_docs) > 10:  # Only test if we have substantial API docs
        example_link_ratio = api_with_example_links / len(api_docs)
        # At least 20% of API docs should link to examples
        assert example_link_ratio >= 0.2, \
            f"Too few API docs link to examples: {example_link_ratio:.1%} (target: ≥20%)"


# =====================================================================================
# External Link Tests
# =====================================================================================

def test_external_links_documented():
    """Test that external links are documented and reasonable."""
    external_links = CROSS_REF_DB.get('external_links', {})

    total_external = sum(len(links) for links in external_links.values())

    # Should have some external links (citations, references)
    assert total_external > 0, "No external links found in documentation"

    # But not too many (documentation should be self-contained)
    total_internal = STATISTICS.get('total_internal_links', 0)
    if total_internal > 0:
        external_ratio = total_external / (total_internal + total_external)
        assert external_ratio < 0.2, \
            f"Too many external links: {external_ratio:.1%} (target: <20%)"


# =====================================================================================
# Statistical Summary Tests
# =====================================================================================

def test_cross_reference_statistics_summary():
    """Display cross-reference statistics for documentation."""
    stats = STATISTICS

    print("\n" + "=" * 80)
    print("Cross-Reference Statistics Summary")
    print("=" * 80)

    print("\nDocumentation Coverage:")
    print(f"  Total documents: {stats.get('total_documents', 0)}")
    print(f"  Documents with links: {stats.get('documents_with_links', 0)} "
          f"({stats.get('documents_with_links', 0) / stats.get('total_documents', 1) * 100:.1f}%)")

    print("\nLink Metrics:")
    print(f"  Internal links: {stats.get('total_internal_links', 0)}")
    print(f"  External links: {stats.get('total_external_links', 0)}")
    print(f"  Link density: {stats.get('link_density', 0):.2f} links/document")

    print("\nQuality Metrics:")
    print(f"  Broken links: {stats.get('broken_links', 0)} "
          f"({stats.get('broken_link_rate', 0) * 100:.1f}%)")
    print(f"  Orphaned documents: {stats.get('orphaned_documents', 0)}")

    if stats.get('most_linked_documents'):
        print("\nTop 5 Most Referenced Documents:")
        for item in stats['most_linked_documents'][:5]:
            print(f"  {item['doc']}: {item['incoming_links']} incoming links")

    # Always pass - this is just informational
    assert True


# =====================================================================================
# Main Test Suite Info
# =====================================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("Documentation Cross-Reference Validation Suite")
    print("=" * 80)
    print(f"\nTotal Documents: {STATISTICS.get('total_documents', 0)}")
    print(f"Internal Links: {STATISTICS.get('total_internal_links', 0)}")
    print(f"Broken Links: {len(BROKEN_LINKS)}")
    print("\nRun with: pytest tests/test_documentation/test_cross_references.py -v")
