#!/usr/bin/env python3
"""
# example-metadata:
# runnable: true
#==============================================================================
# D:/Projects/main/scripts/docs/fix_orphan_documents.py
#==============================================================================
# Orphaned Document Resolver - Phase 1, Day 2
#
# Automatically adds orphaned documents to appropriate toctree directives.
# Orphaned documents are those that exist but aren't referenced in any toctree.
#
# Strategy (Simplified):
#   1. Load orphaned documents from Day 1 baseline report
#   2. Group by parent directory (root, subdirs)
#   3. Find appropriate index.md for each group
#   4. Add to hidden toctree (or create new hidden toctree)
#   5. Maintain alphabetical order
#
# Usage:
#     python scripts/docs/fix_orphan_documents.py
#     python scripts/docs/fix_orphan_documents.py --apply
#     python scripts/docs/fix_orphan_documents.py --verbose
#==============================================================================
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
from datetime import datetime


def load_orphaned_documents() -> List[str]:
    """
    Load list of orphaned documents from Day 1 baseline artifacts.

    Returns:
        List of document paths (relative to docs/, without .md extension)
    """
    # Try multiple artifact locations
    possible_artifacts = [
        Path('.artifacts/toctree_validation_report.json'),
        Path('.artifacts/sphinx_warnings_baseline_report.json'),
    ]

    for artifact_path in possible_artifacts:
        if artifact_path.exists():
            try:
                report = json.load(open(artifact_path, encoding='utf-8'))

                # Check for orphaned_documents key
                if 'orphaned_documents' in report:
                    orphans = report['orphaned_documents']
                    print(f"[INFO] Loaded {len(orphans)} orphans from {artifact_path}")
                    return orphans
            except Exception as e:
                print(f"[WARN] Failed to load {artifact_path}: {e}")
                continue

    # Fallback: Scan for documents not in any toctree
    print("[INFO] No artifact found, scanning docs for orphans...")
    return scan_for_orphans(Path('docs'))


def scan_for_orphans(docs_dir: Path) -> List[str]:
    """
    Scan docs directory for markdown files not in any toctree.

    Args:
        docs_dir: Path to docs directory

    Returns:
        List of orphaned document paths
    """
    # Find all markdown files
    all_docs = set()
    for md_file in docs_dir.rglob('*.md'):
        rel_path = md_file.relative_to(docs_dir)
        doc_path = str(rel_path).replace('\\', '/')[:-3]  # Remove .md
        all_docs.add(doc_path)

    # Find all documents referenced in toctrees
    referenced_docs = set()
    for md_file in docs_dir.rglob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
            lines = content.split('\n')

            in_toctree = False
            for line in lines:
                if '```{toctree}' in line:
                    in_toctree = True
                elif in_toctree and line.strip() == '```':
                    in_toctree = False
                elif in_toctree and line.strip() and not line.strip().startswith(':'):
                    # This is a document reference
                    ref = line.strip()
                    # Clean up the reference
                    if ref and not any(c in ref for c in ['**', '##', '```', ':::', '{', '}']):
                        referenced_docs.add(ref)
        except Exception:
            continue

    # index.md is always implicitly included
    referenced_docs.add('index')

    # Orphans are docs not referenced
    orphans = sorted(all_docs - referenced_docs)
    return orphans


def group_by_directory(orphans: List[str]) -> Dict[str, List[str]]:
    """
    Group orphaned documents by parent directory.

    Args:
        orphans: List of orphaned document paths

    Returns:
        Dictionary mapping directory path to list of orphans
    """
    groups = defaultdict(list)

    for orphan in orphans:
        parts = orphan.split('/')

        if len(parts) == 1:
            # Root-level file
            groups['root'].append(orphan)
        else:
            # Subdirectory file
            parent_dir = '/'.join(parts[:-1])
            groups[parent_dir].append(orphan)

    return dict(groups)


def find_parent_index(directory: str, docs_dir: Path = Path('docs')) -> Path:
    """
    Determine which index.md should contain the orphaned documents.

    Args:
        directory: Directory path ('root' or 'subdir/path')
        docs_dir: Path to docs directory

    Returns:
        Path to parent index.md file
    """
    if directory == 'root':
        return docs_dir / 'index.md'

    # Check if directory has its own index.md
    dir_index = docs_dir / directory / 'index.md'
    if dir_index.exists():
        return dir_index

    # Fall back to parent directory
    parts = directory.split('/')
    if len(parts) > 1:
        parent_dir = '/'.join(parts[:-1])
        parent_index = docs_dir / parent_dir / 'index.md'
        if parent_index.exists():
            return parent_index

    # Ultimate fallback: root index.md
    return docs_dir / 'index.md'


def add_orphans_to_toctree(
    index_file: Path,
    orphans: List[str],
    dry_run: bool = True,
    verbose: bool = False
) -> Dict:
    """
    Add orphaned documents to index file's toctree.

    Args:
        index_file: Path to index.md file
        orphans: List of document paths to add
        dry_run: If True, don't write changes
        verbose: If True, print detailed progress

    Returns:
        Dictionary with operation results
    """
    if verbose:
        print(f"\nProcessing: {index_file}")
        print(f"  Adding {len(orphans)} orphan(s)")

    try:
        content = index_file.read_text(encoding='utf-8')
    except Exception as e:
        return {
            "file": str(index_file),
            "success": False,
            "error": str(e),
            "orphans_added": 0
        }

    lines = content.split('\n')

    # Find existing toctree block
    toctree_start = None
    toctree_end = None

    for i, line in enumerate(lines):
        if '```{toctree}' in line:
            toctree_start = i
            # Find closing fence
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == '```':
                    toctree_end = j
                    break
            break

    if toctree_start is None or toctree_end is None:
        # No toctree found OR malformed toctree - create a new hidden one at end of file
        if verbose:
            if toctree_start is None:
                print("  No existing toctree - creating new hidden toctree")
            else:
                print("  Malformed toctree (no closing fence) - creating new hidden toctree at end")

        new_toctree = [
            '',
            '```{toctree}',
            ':hidden:',
            '',
        ]
        # Add orphans in alphabetical order
        new_toctree.extend(sorted(orphans))
        new_toctree.append('```')

        lines.extend(new_toctree)
        added_count = len(orphans)

    else:
        # Insert into existing toctree before closing fence
        if verbose:
            print(f"  Found existing toctree at lines {toctree_start+1}-{toctree_end+1}")

        # Extract current toctree entries
        current_entries = []
        for i in range(toctree_start + 1, toctree_end):
            line = lines[i].strip()
            # Skip options and empty lines
            if line and not line.startswith(':'):
                current_entries.append(line)

        # Add orphans (avoid duplicates)
        all_entries = set(current_entries + orphans)
        sorted_entries = sorted(all_entries)

        # Reconstruct toctree
        new_toctree_content = []
        for i in range(toctree_start + 1, toctree_end):
            line = lines[i]
            # Keep options
            if line.strip().startswith(':'):
                new_toctree_content.append(line)
            elif line.strip() == '':
                # Keep first empty line after options
                if not new_toctree_content or new_toctree_content[-1].strip().startswith(':'):
                    new_toctree_content.append(line)

        # Add all entries
        new_toctree_content.extend(sorted_entries)

        # Replace toctree content
        lines = lines[:toctree_start+1] + new_toctree_content + lines[toctree_end:]
        added_count = len(set(orphans) - set(current_entries))

    # Write changes
    if not dry_run and added_count > 0:
        try:
            new_content = '\n'.join(lines)
            index_file.write_text(new_content, encoding='utf-8')
            if verbose:
                print(f"  [OK] Added {added_count} orphan(s) to {index_file}")
        except Exception as e:
            return {
                "file": str(index_file),
                "success": False,
                "error": f"Failed to write: {e}",
                "orphans_added": 0
            }
    elif dry_run and added_count > 0:
        if verbose:
            print(f"  [DRY RUN] Would add {added_count} orphan(s)")

    return {
        "file": str(index_file),
        "success": True,
        "orphans_added": added_count,
        "dry_run": dry_run
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fix orphaned documents by adding them to toctrees",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run (default)
  python scripts/docs/fix_orphan_documents.py

  # Apply fixes
  python scripts/docs/fix_orphan_documents.py --apply

  # Verbose output
  python scripts/docs/fix_orphan_documents.py --apply --verbose
        """
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply fixes (default is dry-run)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed progress information"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".artifacts/orphan_resolution_report.json"),
        help="Output JSON report path"
    )

    args = parser.parse_args()

    dry_run = not args.apply

    if dry_run:
        print("=" * 70)
        print("DRY RUN MODE - No changes will be written")
        print("=" * 70)
    else:
        print("=" * 70)
        print("APPLY MODE - Changes will be written to files")
        print("=" * 70)

    # Load orphaned documents
    print("\nLoading orphaned documents...")
    orphans = load_orphaned_documents()
    print(f"Found {len(orphans)} orphaned documents")

    if not orphans:
        print("[INFO] No orphaned documents found!")
        return 0

    # Group by directory
    print("\nGrouping by directory...")
    groups = group_by_directory(orphans)
    print(f"Grouped into {len(groups)} directories")

    # Process each group
    results = []
    total_added = 0

    for directory, docs in sorted(groups.items()):
        parent_index = find_parent_index(directory)

        # Compute relative paths for orphans based on index file location
        relative_docs = []
        for doc in docs:
            # If doc is 'presentation/0-Introduction & Motivation'
            # and parent_index is 'docs/presentation/index.md'
            # then we want just '0-Introduction & Motivation'
            if directory != 'root':
                # Strip directory prefix if present
                if doc.startswith(directory + '/'):
                    relative_doc = doc[len(directory) + 1:]  # +1 for the '/'
                    relative_docs.append(relative_doc)
                else:
                    # Orphan doesn't start with expected prefix, keep as-is
                    relative_docs.append(doc)
            else:
                # Root-level orphans: keep full path
                relative_docs.append(doc)

        if args.verbose:
            print(f"\n{directory}: {len(docs)} orphans -> {parent_index}")

        result = add_orphans_to_toctree(
            parent_index,
            relative_docs,
            dry_run=dry_run,
            verbose=args.verbose
        )

        results.append(result)
        total_added += result.get('orphans_added', 0)

    # Generate report
    report = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_orphans_processed": len(orphans),
            "dry_run": dry_run
        },
        "summary": {
            "total_orphans_added": total_added,
            "index_files_modified": sum(1 for r in results if r.get('orphans_added', 0) > 0),
            "directories_processed": len(groups)
        },
        "results": results,
        "orphan_groups": {
            directory: docs for directory, docs in groups.items()
        }
    }

    # Save report
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Orphaned documents:   {len(orphans)}")
    print(f"Directories:          {len(groups)}")
    print(f"Index files modified: {report['summary']['index_files_modified']}")
    print(f"Orphans added:        {total_added}")
    print()

    if dry_run:
        print("[INFO] This was a DRY RUN. Use --apply to write changes.")
    else:
        print("[OK] Fixes applied successfully!")

    print(f"\nDetailed report: {args.output}")

    # Show top directories with orphans
    if groups:
        print("\nTop directories with orphans:")
        for directory, docs in sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            print(f"  {directory}: {len(docs)} orphan(s)")

    return 0


if __name__ == "__main__":
    exit(main())
