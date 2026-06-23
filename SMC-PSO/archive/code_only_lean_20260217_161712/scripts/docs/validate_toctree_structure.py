#!/usr/bin/env python3
"""
# example-metadata:
# runnable: true
#==============================================================================
# D:/Projects/main/scripts/docs/validate_toctree_structure.py
#==============================================================================
# Toctree Structure Validator - Phase 1
#
# Validates and analyzes toctree directive syntax in all markdown files.
# Detects malformed directives, orphaned documents, and provides fix suggestions.
#
# Usage:
#     python scripts/docs/validate_toctree_structure.py
#     python scripts/docs/validate_toctree_structure.py --path docs
#     python scripts/docs/validate_toctree_structure.py --file docs/index.md
#==============================================================================
"""

import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


def extract_toctree_blocks(content: str, filepath: Path) -> List[Dict]:
    """
    Extract all toctree directive blocks from markdown content.

    Args:
        content: File content
        filepath: Path to file

    Returns:
        List of dictionaries with toctree block metadata
    """
    blocks = []
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detect fenced toctree directive: ```{toctree}
        if re.match(r'^\s*```{toctree}', line):
            start_line = i
            options_lines = []
            content_lines = []

            # Find closing fence
            i += 1
            while i < len(lines) and not re.match(r'^\s*```\s*$', lines[i]):
                # Options start with ':'
                if lines[i].strip().startswith(':'):
                    options_lines.append(lines[i].strip())
                elif lines[i].strip():
                    # Non-empty line that doesn't start with ':' is content
                    content_lines.append(lines[i].strip())
                i += 1

            end_line = i

            blocks.append({
                "type": "fenced",
                "filepath": str(filepath),
                "start_line": start_line + 1,  # 1-indexed for human reading
                "end_line": end_line + 1,
                "options": options_lines,
                "content": content_lines,
                "raw": '\n'.join(lines[start_line:end_line+1])
            })

        # Detect RST-style toctree directive: .. toctree::
        elif re.match(r'^\s*\.\.\s+toctree::', line):
            start_line = i
            options_lines = []
            content_lines = []

            # Find options (indented lines starting with ':')
            i += 1
            while i < len(lines) and lines[i].strip().startswith(':'):
                options_lines.append(lines[i].strip())
                i += 1

            # Find content (indented non-empty lines)
            while i < len(lines):
                if lines[i].strip() and not lines[i].startswith(' '):
                    # Reached non-indented line, end of block
                    break
                elif lines[i].strip():
                    content_lines.append(lines[i].strip())
                i += 1

            blocks.append({
                "type": "rst",
                "filepath": str(filepath),
                "start_line": start_line + 1,
                "end_line": i,
                "options": options_lines,
                "content": content_lines,
                "raw": '\n'.join(lines[start_line:i])
            })
            continue

        i += 1

    return blocks


def validate_toctree_block(block: Dict) -> Dict:
    """
    Validate a single toctree block and detect issues.

    Args:
        block: Toctree block dictionary

    Returns:
        Validation result dictionary
    """
    issues = []
    severity = "OK"

    # Check for mixed syntax (RST options in fenced directive)
    if block["type"] == "fenced":
        for option in block["options"]:
            if not re.match(r'^:[a-z-]+:\s*', option):
                issues.append({
                    "type": "invalid_option_syntax",
                    "message": f"Invalid option syntax: {option}",
                    "suggestion": "Use MyST fenced directive option syntax"
                })
                severity = "ERROR"

    # Check for content where there should be none
    # Note: Some content lines might be parsed as options by Sphinx
    has_suspicious_content = False
    for line in block["content"]:
        # Check if line looks like it should be outside directive
        if any(pattern in line for pattern in [
            '```',  # Code block markers
            '##',  # Headers
            '**',  # Bold text
            'flowchart',  # Mermaid diagrams
            '- [',  # Lists
            ':::'  # Grid/card directives
        ]):
            has_suspicious_content = True
            break

    if has_suspicious_content:
        issues.append({
            "type": "content_should_be_outside",
            "message": "Toctree has non-document content (headers, code, etc.)",
            "suggestion": "Move narrative content outside toctree directive"
        })
        severity = "ERROR"

    # Check for duplicate entries
    seen_entries = set()
    for entry in block["content"]:
        if entry in seen_entries:
            issues.append({
                "type": "duplicate_entry",
                "message": f"Duplicate entry: {entry}",
                "suggestion": "Remove duplicate"
            })
            severity = "WARNING"
        seen_entries.add(entry)

    # Check for entries that look like they might be malformed
    for entry in block["content"]:
        # Check for entries with special characters that might indicate parsing issues
        if any(char in entry for char in ['`', '$', '|', '{', '}']):
            issues.append({
                "type": "suspicious_entry",
                "message": f"Entry contains special characters: {entry[:50]}",
                "suggestion": "This might be content parsed as document reference"
            })
            severity = "WARNING"

    return {
        "block": block,
        "issues": issues,
        "severity": severity,
        "issue_count": len(issues)
    }


def find_all_documents(docs_dir: Path) -> Set[str]:
    """
    Find all markdown documents in docs directory.

    Args:
        docs_dir: Path to docs directory

    Returns:
        Set of document paths (relative to docs_dir, without .md extension)
    """
    documents = set()

    for md_file in docs_dir.rglob("*.md"):
        rel_path = md_file.relative_to(docs_dir)
        # Remove .md extension
        doc_path = str(rel_path).replace('\\', '/')[:-3]
        documents.add(doc_path)

    return documents


def find_orphaned_documents(docs_dir: Path, toctree_blocks: List[Dict]) -> List[str]:
    """
    Find documents that aren't referenced in any toctree.

    Args:
        docs_dir: Path to docs directory
        toctree_blocks: All toctree blocks found

    Returns:
        List of orphaned document paths
    """
    all_docs = find_all_documents(docs_dir)

    # Extract all referenced documents from toctrees
    referenced_docs = set()
    for block in toctree_blocks:
        for entry in block["content"]:
            # Clean up entry (remove leading/trailing whitespace, special chars)
            clean_entry = entry.strip()
            # Skip entries that are obviously not document paths
            if not any(char in clean_entry for char in ['`', '$', '|', '**', '---', '###']):
                referenced_docs.add(clean_entry)

    # Special case: index.md is always implicitly included
    referenced_docs.add("index")

    orphaned = []
    for doc in sorted(all_docs):
        if doc not in referenced_docs:
            # Check if it's referenced with a different path variant
            doc_basename = doc.split('/')[-1]
            is_referenced = any(
                ref.endswith(doc_basename) or doc.endswith(ref)
                for ref in referenced_docs
            )
            if not is_referenced:
                orphaned.append(doc)

    return orphaned


def generate_fix_suggestions(validation_results: List[Dict], orphaned_docs: List[str]) -> Dict:
    """
    Generate actionable fix suggestions.

    Args:
        validation_results: Validation results for all blocks
        orphaned_docs: List of orphaned documents

    Returns:
        Dictionary with fix suggestions
    """
    suggestions = {
        "malformed_toctrees": [],
        "orphaned_documents": {},
        "summary": {}
    }

    # Group malformed toctrees by file
    malformed_by_file = defaultdict(list)
    for result in validation_results:
        if result["issues"]:
            filepath = result["block"]["filepath"]
            malformed_by_file[filepath].append(result)

    # Generate suggestions for malformed toctrees
    for filepath, results in malformed_by_file.items():
        total_issues = sum(r["issue_count"] for r in results)
        suggestions["malformed_toctrees"].append({
            "file": filepath,
            "block_count": len(results),
            "issue_count": total_issues,
            "blocks": [
                {
                    "start_line": r["block"]["start_line"],
                    "end_line": r["block"]["end_line"],
                    "issues": r["issues"]
                }
                for r in results
            ]
        })

    # Group orphaned documents by directory
    orphaned_by_dir = defaultdict(list)
    for doc in orphaned_docs:
        parent_dir = '/'.join(doc.split('/')[:-1]) if '/' in doc else 'root'
        orphaned_by_dir[parent_dir].append(doc)

    # Generate suggestions for orphaned documents
    for directory, docs in orphaned_by_dir.items():
        # Suggest which index file to add them to
        if directory == 'root':
            suggested_index = "index.md"
        else:
            suggested_index = f"{directory}/index.md"

        suggestions["orphaned_documents"][directory] = {
            "count": len(docs),
            "suggested_index": suggested_index,
            "documents": docs
        }

    # Summary statistics
    suggestions["summary"] = {
        "total_malformed_files": len(malformed_by_file),
        "total_malformed_blocks": sum(len(r) for r in malformed_by_file.values()),
        "total_orphaned_documents": len(orphaned_docs),
        "orphaned_by_directory": len(orphaned_by_dir)
    }

    return suggestions


def main():
    parser = argparse.ArgumentParser(
        description="Validate toctree structure in Sphinx documentation"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("docs"),
        help="Path to docs directory"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Validate single file instead of entire directory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".artifacts/toctree_validation_report.json"),
        help="Output JSON report path"
    )

    args = parser.parse_args()

    if args.file:
        # Single file validation
        if not args.file.exists():
            print(f"ERROR: File not found: {args.file}")
            return 1

        content = args.file.read_text(encoding='utf-8')
        blocks = extract_toctree_blocks(content, args.file)

        print(f"\nAnalyzing: {args.file}")
        print(f"Found {len(blocks)} toctree blocks")

        for i, block in enumerate(blocks, 1):
            result = validate_toctree_block(block)
            print(f"\nBlock {i} (lines {block['start_line']}-{block['end_line']}):")
            print(f"  Type: {block['type']}")
            print(f"  Severity: {result['severity']}")
            print(f"  Issues: {result['issue_count']}")
            for issue in result["issues"]:
                print(f"    - {issue['message']}")

        return 0

    # Full directory validation
    if not args.path.exists():
        print(f"ERROR: Path not found: {args.path}")
        return 1

    print(f"Scanning documentation in {args.path}...")

    # Find all markdown files
    md_files = list(args.path.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files")

    # Extract all toctree blocks
    all_blocks = []
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            blocks = extract_toctree_blocks(content, md_file)
            all_blocks.extend(blocks)
        except Exception as e:
            print(f"WARNING: Failed to process {md_file}: {e}")

    print(f"Found {len(all_blocks)} toctree blocks")

    # Validate all blocks
    print("\nValidating toctree blocks...")
    validation_results = [validate_toctree_block(block) for block in all_blocks]

    # Find orphaned documents
    print("Finding orphaned documents...")
    orphaned_docs = find_orphaned_documents(args.path, all_blocks)

    # Generate fix suggestions
    print("Generating fix suggestions...")
    fix_suggestions = generate_fix_suggestions(validation_results, orphaned_docs)

    # Compile full report
    report = {
        "metadata": {
            "timestamp": Path(__file__).stat().st_mtime,
            "docs_directory": str(args.path),
            "total_markdown_files": len(md_files),
            "total_toctree_blocks": len(all_blocks)
        },
        "validation_results": [
            {
                "filepath": r["block"]["filepath"],
                "start_line": r["block"]["start_line"],
                "end_line": r["block"]["end_line"],
                "type": r["block"]["type"],
                "severity": r["severity"],
                "issues": r["issues"]
            }
            for r in validation_results
        ],
        "orphaned_documents": orphaned_docs,
        "fix_suggestions": fix_suggestions
    }

    # Save report
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total toctree blocks:       {len(all_blocks)}")
    print(f"Blocks with issues:         {sum(1 for r in validation_results if r['issues'])}")
    print(f"Orphaned documents:         {len(orphaned_docs)}")
    print()
    print("Severity breakdown:")
    severity_counts = defaultdict(int)
    for r in validation_results:
        severity_counts[r["severity"]] += 1
    for severity, count in sorted(severity_counts.items()):
        print(f"  {severity}: {count}")
    print()
    print(f"Report saved to: {args.output}")

    # Show top offending files
    if fix_suggestions["malformed_toctrees"]:
        print("\nTop 10 files with malformed toctrees:")
        for item in sorted(
            fix_suggestions["malformed_toctrees"],
            key=lambda x: x["issue_count"],
            reverse=True
        )[:10]:
            print(f"  {item['file']}: {item['issue_count']} issues in {item['block_count']} blocks")

    return 0


if __name__ == "__main__":
    exit(main())
