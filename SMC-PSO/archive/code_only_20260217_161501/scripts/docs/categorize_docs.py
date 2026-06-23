#!/usr/bin/env python3
"""
Categorize documentation files into user/api/dev projects.

This script copies files from the monolithic docs/ directory into the appropriate
split project directories (docs-user/, docs-api/, docs-dev/) based on a predefined
category mapping.

Usage:
    python scripts/categorize_docs.py [--dry-run]
"""

import shutil
import sys
from pathlib import Path
from typing import Dict, List

# Category mapping: directory name → target project
CATEGORY_MAP: Dict[str, str] = {
    # USER DOCUMENTATION (~180 files)
    'guides': 'user',
    'controllers': 'user',  # User-facing controller guides
    'presentation': 'user',
    'for_reviewers': 'user',
    'deployment': 'user',
    'theory': 'user',
    'examples': 'user',
    'workflows': 'user',

    # API REFERENCE (~390 files)
    'reference': 'api',
    'api': 'api',
    'factory': 'api',
    'mathematical_foundations': 'api',

    # DEVELOPER INTERNAL (~210 files)
    'testing': 'dev',
    'plans': 'dev',
    'reports': 'dev',
    'mcp-debugging': 'dev',
    'implementation': 'dev',
    'analysis': 'dev',
    'benchmarks': 'dev',
    'validation': 'dev',
    'technical': 'dev',
    'styling-library': 'dev',
    'architecture': 'dev',
    'code_quality': 'dev',
}

# Root-level files to copy to user docs (project overview)
ROOT_FILES_TO_USER: List[str] = [
    'README.md',
    'CONTRIBUTING.md',
    'CHANGELOG.md',
    'CITATIONS.md',
    'CITATIONS_ACADEMIC.md',
    'QUICKSTART_VALIDATION.md',
]


def categorize_docs(dry_run: bool = False) -> None:
    """
    Copy documentation files from docs/ to appropriate split projects.

    Args:
        dry_run: If True, print actions without executing
    """
    repo_root = Path(__file__).parent.parent
    docs_dir = repo_root / 'docs'

    if not docs_dir.exists():
        print(f"ERROR: {docs_dir} does not exist!")
        sys.exit(1)

    # Statistics
    stats = {'user': 0, 'api': 0, 'dev': 0, 'skipped': 0}

    print("="*80)
    print("Documentation Categorization Script")
    print("="*80)
    print(f"Source: {docs_dir}")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print("="*80)

    # Copy directories according to category map
    for src_dir_name, category in CATEGORY_MAP.items():
        src_dir = docs_dir / src_dir_name
        dst_dir = repo_root / f'docs-{category}' / src_dir_name

        if not src_dir.exists():
            print(f"SKIP: {src_dir_name}/ (not found)")
            stats['skipped'] += 1
            continue

        if src_dir.is_dir():
            file_count = len(list(src_dir.rglob('*')))
            print(f"COPY: {src_dir_name}/ -> docs-{category}/ ({file_count} items)")

            if not dry_run:
                if dst_dir.exists():
                    shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)

            stats[category] += file_count

    # Copy root-level files to user docs
    print("\n" + "="*80)
    print("Copying root-level files to docs-user/")
    print("="*80)

    for filename in ROOT_FILES_TO_USER:
        src_file = docs_dir / filename
        dst_file = repo_root / 'docs-user' / filename

        if not src_file.exists():
            print(f"SKIP: {filename} (not found)")
            continue

        print(f"COPY: {filename} -> docs-user/")

        if not dry_run:
            shutil.copy2(src_file, dst_file)

        stats['user'] += 1

    # Copy _static directories to each project
    print("\n" + "="*80)
    print("Copying _static/ to each project")
    print("="*80)

    static_src = docs_dir / '_static'
    if static_src.exists():
        for project in ['user', 'api', 'dev']:
            static_dst = repo_root / f'docs-{project}' / '_static'
            print(f"COPY: _static/ -> docs-{project}/_static/")

            if not dry_run:
                if static_dst.exists():
                    shutil.rmtree(static_dst)
                shutil.copytree(static_src, static_dst)

    # Copy _templates directories to each project (if they exist)
    templates_src = docs_dir / '_templates'
    if templates_src.exists():
        for project in ['user', 'api', 'dev']:
            templates_dst = repo_root / f'docs-{project}' / '_templates'
            print(f"COPY: _templates/ -> docs-{project}/_templates/")

            if not dry_run:
                if templates_dst.exists():
                    shutil.rmtree(templates_dst)
                shutil.copytree(templates_src, templates_dst)

    # Copy _ext directories (custom extensions)
    ext_src = docs_dir / '_ext'
    if ext_src.exists():
        for project in ['user', 'api', 'dev']:
            ext_dst = repo_root / f'docs-{project}' / '_ext'
            print(f"COPY: _ext/ -> docs-{project}/_ext/")

            if not dry_run:
                if ext_dst.exists():
                    shutil.rmtree(ext_dst)
                shutil.copytree(ext_src, ext_dst)

    # Copy bib/ directories to each project (for bibliography)
    bib_src = docs_dir / 'bib'
    if bib_src.exists():
        for project in ['user', 'api', 'dev']:
            bib_dst = repo_root / f'docs-{project}' / 'bib'
            print(f"COPY: bib/ -> docs-{project}/bib/")

            if not dry_run:
                if bib_dst.exists():
                    shutil.rmtree(bib_dst)
                shutil.copytree(bib_src, bib_dst)

    # Copy refs.bib to each project (main bibliography)
    refs_src = docs_dir / 'refs.bib'
    if refs_src.exists():
        for project in ['user', 'api', 'dev']:
            refs_dst = repo_root / f'docs-{project}' / 'refs.bib'
            print(f"COPY: refs.bib -> docs-{project}/refs.bib")

            if not dry_run:
                shutil.copy2(refs_src, refs_dst)

    # Print statistics
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"User docs:     {stats['user']} items")
    print(f"API docs:      {stats['api']} items")
    print(f"Dev docs:      {stats['dev']} items")
    print(f"Skipped:       {stats['skipped']} directories")
    print(f"Total copied:  {stats['user'] + stats['api'] + stats['dev']} items")
    print("="*80)

    if dry_run:
        print("\nDRY RUN COMPLETE - No files were actually copied")
        print("Run without --dry-run to execute")
    else:
        print("\nCATEGORIZATION COMPLETE")
        print("\nNext steps:")
        print("1. Create conf.py for each project")
        print("2. Create index.rst for each project")
        print("3. Run initial builds")


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    categorize_docs(dry_run=dry_run)
