#!/usr/bin/env python3
"""
# example-metadata:
# runnable: true
#==============================================================================
# D:/Projects/main/scripts/docs/fix_toctree_directives.py
#==============================================================================
# Toctree Directive Fixer - Phase 1, Day 2
#
# Automatically fixes malformed MyST fenced toctree directives that have
# narrative content incorrectly placed inside the directive body.
#
# Root Cause:
#   - Content after apparent "closing fence" is actually inside directive
#   - Sphinx parses narrative text as document references
#   - Results in 224 "toctree contains reference to nonexisting document" warnings
#
# Fix Strategy:
#   1. Detect fenced {toctree} directives with strict pattern matching
#   2. Parse options (lines starting with ':')
#   3. Parse document references (valid file paths only)
#   4. Separate narrative content (headers, code blocks, prose)
#   5. Reconstruct with proper fence closure
#   6. Move narrative content OUTSIDE directive
#
# Usage:
#     python scripts/docs/fix_toctree_directives.py --dry-run
#     python scripts/docs/fix_toctree_directives.py --file docs/references/index.md --dry-run
#     python scripts/docs/fix_toctree_directives.py --apply
#     python scripts/docs/fix_toctree_directives.py --apply --verbose
#==============================================================================
"""

import re
import json
import argparse
from pathlib import Path
from typing import Dict, List
from datetime import datetime


# Valid MyST toctree options (for validation)
VALID_TOCTREE_OPTIONS = {
    ':maxdepth:',
    ':caption:',
    ':hidden:',
    ':numbered:',
    ':titlesonly:',
    ':glob:',
    ':reversed:',
    ':includehidden:',
}


def is_valid_option_line(line: str) -> bool:
    """
    Check if line is a valid MyST toctree option.

    Args:
        line: Line to check

    Returns:
        True if valid option line
    """
    line = line.strip()
    if not line.startswith(':'):
        return False

    # Extract option name (e.g., ':maxdepth:' from ':maxdepth: 2')
    match = re.match(r'^(:[a-z]+:)', line)
    if match:
        option_name = match.group(1)
        return option_name in VALID_TOCTREE_OPTIONS

    return False


def is_valid_document_reference(line: str) -> bool:
    """
    Check if line looks like a valid document reference.

    Valid patterns:
        - simple_name
        - subdirectory/document
        - path/to/document
        - ../relative/path

    Invalid patterns:
        - Contains markdown syntax: **, ##, ```, :::
        - Contains special chars: {, }, |, $
        - Looks like prose (multiple words with spaces)

    Args:
        line: Line to check

    Returns:
        True if likely a document reference
    """
    line = line.strip()

    # Empty lines are not document refs
    if not line:
        return False

    # Lines with markdown/MyST syntax are not document refs
    if any(pattern in line for pattern in ['**', '##', '```', ':::', '{', '}', '|', '$']):
        return False

    # Lines that look like prose (multiple words separated by spaces, not paths)
    # Exception: Allow single spaces in document names (rare but valid)
    words = line.split()
    if len(words) > 3:  # Likely prose, not a document path
        return False

    # Lines with citation syntax
    if '{cite}' in line or '{doc}' in line or '{ref}' in line:
        return False

    # Valid document refs are typically: word, word/word, word/word/word
    # Allow alphanumeric, underscore, hyphen, dot, slash
    if re.match(r'^[\w\-./]+$', line):
        return True

    return False


def extract_toctree_blocks(content: str, filepath: Path) -> List[Dict]:
    """
    Extract all fenced toctree directive blocks from markdown content.

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
        if re.match(r'^\s*```\{toctree\}', line):
            start_line = i
            block_lines = [line]

            # Find ACTUAL closing fence (end of directive)
            i += 1
            fence_depth = 1  # Track nested fences

            while i < len(lines):
                block_lines.append(lines[i])

                # Check for nested code blocks (don't mistake these for directive close)
                if re.match(r'^\s*```', lines[i]):
                    # This could be closing fence OR start of nested code block
                    # Heuristic: if next line is not blank and not option, it's nested
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and not next_line.startswith(':'):
                            # Likely nested code block opening
                            fence_depth += 1
                            i += 1
                            continue

                    # Assume this is the closing fence
                    fence_depth -= 1
                    if fence_depth == 0:
                        end_line = i
                        break

                i += 1

            if fence_depth > 0:
                # Never found closing fence - entire rest of file is inside directive
                end_line = len(lines) - 1

            blocks.append({
                "filepath": str(filepath),
                "start_line": start_line + 1,  # 1-indexed for human reading
                "end_line": end_line + 1,
                "block_lines": block_lines,
                "raw_content": '\n'.join(block_lines)
            })

        i += 1

    return blocks


def parse_toctree_block(block: Dict) -> Dict:
    """
    Parse a toctree block into structured components.

    Args:
        block: Toctree block dictionary with block_lines

    Returns:
        Parsed structure with options, doc_refs, and narrative
    """
    lines = block["block_lines"]

    # Skip opening fence
    lines = lines[1:]

    # Parse components
    options = []
    doc_refs = []
    narrative = []

    state = "OPTIONS"  # Start by parsing options

    for line in lines:
        # Check for closing fence (may have content on same line!)
        fence_match = re.match(r'^\s*```\s*(.*)', line)
        if fence_match:
            state = "AFTER_FENCE"
            # Check if there's content after the fence on the same line
            after_fence = fence_match.group(1).strip()
            if after_fence:
                narrative.append(after_fence)
            continue

        if state == "OPTIONS":
            # Skip empty lines in OPTIONS state (they're formatting, not transitions)
            if line.strip() == "":
                continue

            # Check if line is a malformed option like ":hidden: bibliography"
            option_match = re.match(r'^:([a-z]+):\s+(.+)$', line.strip())
            if option_match:
                option_name = f':{option_match.group(1)}:'
                option_value = option_match.group(2).strip()

                if option_name in VALID_TOCTREE_OPTIONS:
                    # Split: option goes to options, value might be doc ref
                    if option_name in [':hidden:', ':numbered:', ':titlesonly:', ':glob:', ':reversed:']:
                        # These are boolean options - shouldn't have values
                        options.append(option_name)
                        # If there's a value, it's likely a document ref
                        if option_value and is_valid_document_reference(option_value):
                            state = "DOC_REFS"
                            doc_refs.append(option_value)
                    else:
                        # Options with values (like :maxdepth: 2, :caption: "Title")
                        options.append(line.strip())
                else:
                    # Unknown option format - might be narrative
                    narrative.append(line)
                    state = "NARRATIVE"
            elif is_valid_option_line(line):
                options.append(line.strip())
            elif is_valid_document_reference(line):
                # Found document ref - transition to DOC_REFS state
                state = "DOC_REFS"
                doc_refs.append(line.strip())
            else:
                # Invalid content in options section - likely narrative
                state = "NARRATIVE"
                narrative.append(line)

        elif state == "DOC_REFS":
            if is_valid_document_reference(line):
                doc_refs.append(line.strip())
            elif line.strip() == "":
                # Empty line within doc refs - keep state
                pass
            else:
                # Non-document-ref line - transition to narrative
                state = "NARRATIVE"
                narrative.append(line)

        elif state == "NARRATIVE":
            narrative.append(line)

        elif state == "AFTER_FENCE":
            # Content after closing fence should be outside directive
            narrative.append(line)

    return {
        "options": options,
        "doc_refs": doc_refs,
        "narrative": narrative,
        "original_lines": block["block_lines"]
    }


def reconstruct_toctree_block(parsed: Dict) -> List[str]:
    """
    Reconstruct a properly formatted toctree block.

    Args:
        parsed: Parsed toctree structure

    Returns:
        List of lines for reconstructed block
    """
    result = []

    # Opening fence
    result.append("```{toctree}")

    # Options
    for option in parsed["options"]:
        result.append(option)

    # Blank line separator (if we have doc refs)
    if parsed["doc_refs"]:
        result.append("")

        # Document references
        for ref in parsed["doc_refs"]:
            result.append(ref)

    # Closing fence
    result.append("```")

    # Narrative content (OUTSIDE directive)
    if parsed["narrative"]:
        result.append("")  # Blank line after directive
        result.extend(parsed["narrative"])

    return result


def fix_toctree_in_file(
    filepath: Path,
    dry_run: bool = True,
    verbose: bool = False
) -> Dict:
    """
    Fix all malformed toctree directives in a single file.

    Args:
        filepath: Path to markdown file
        dry_run: If True, don't write changes
        verbose: If True, print detailed progress

    Returns:
        Dictionary with fix statistics
    """
    if verbose:
        print(f"\nProcessing: {filepath}")

    # Read file
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return {
            "filepath": str(filepath),
            "success": False,
            "error": str(e),
            "blocks_found": 0,
            "blocks_fixed": 0
        }

    # Extract toctree blocks
    blocks = extract_toctree_blocks(content, filepath)

    if not blocks:
        if verbose:
            print("  No toctree blocks found")
        return {
            "filepath": str(filepath),
            "success": True,
            "blocks_found": 0,
            "blocks_fixed": 0
        }

    if verbose:
        print(f"  Found {len(blocks)} toctree block(s)")

    # Parse and reconstruct each block
    fixes_applied = 0
    new_content = content

    # Process blocks in reverse order (so line numbers don't shift)
    for block in reversed(blocks):
        parsed = parse_toctree_block(block)

        # Check if fix is needed
        if parsed["narrative"] or len(parsed["doc_refs"]) < 5:
            # Has narrative content OR suspiciously few doc refs (likely malformed)
            reconstructed = reconstruct_toctree_block(parsed)

            # Replace in content
            original_block = '\n'.join(block["block_lines"])
            new_block = '\n'.join(reconstructed)

            if original_block != new_block:
                new_content = new_content.replace(original_block, new_block, 1)
                fixes_applied += 1

                if verbose:
                    print(f"  Fixed block at lines {block['start_line']}-{block['end_line']}")
                    print(f"    Options: {len(parsed['options'])}")
                    print(f"    Doc refs: {len(parsed['doc_refs'])}")
                    print(f"    Narrative lines moved outside: {len(parsed['narrative'])}")

    # Write changes (if not dry-run)
    if not dry_run and fixes_applied > 0:
        try:
            filepath.write_text(new_content, encoding='utf-8')
            if verbose:
                print(f"  [OK] Changes written to {filepath}")
        except Exception as e:
            return {
                "filepath": str(filepath),
                "success": False,
                "error": f"Failed to write: {e}",
                "blocks_found": len(blocks),
                "blocks_fixed": fixes_applied
            }
    elif dry_run and fixes_applied > 0:
        if verbose:
            print(f"  [DRY RUN] Would fix {fixes_applied} block(s)")

    return {
        "filepath": str(filepath),
        "success": True,
        "blocks_found": len(blocks),
        "blocks_fixed": fixes_applied,
        "dry_run": dry_run
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fix malformed MyST toctree directives in Sphinx documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run on entire docs directory
  python scripts/docs/fix_toctree_directives.py --dry-run

  # Fix specific file (dry-run)
  python scripts/docs/fix_toctree_directives.py --file docs/references/index.md --dry-run

  # Apply fixes to entire docs directory
  python scripts/docs/fix_toctree_directives.py --apply

  # Apply fixes with verbose output
  python scripts/docs/fix_toctree_directives.py --apply --verbose
        """
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("docs"),
        help="Path to docs directory (default: docs)"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Fix single file instead of entire directory"
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
        default=Path(".artifacts/toctree_fix_report.json"),
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

    # Single file mode
    if args.file:
        if not args.file.exists():
            print(f"ERROR: File not found: {args.file}")
            return 1

        result = fix_toctree_in_file(args.file, dry_run=dry_run, verbose=True)

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"File: {result['filepath']}")
        print(f"Success: {result['success']}")
        print(f"Blocks found: {result['blocks_found']}")
        print(f"Blocks fixed: {result['blocks_fixed']}")

        return 0 if result['success'] else 1

    # Directory mode
    if not args.path.exists():
        print(f"ERROR: Path not found: {args.path}")
        return 1

    print(f"\nScanning directory: {args.path}")

    # Find all markdown files
    md_files = sorted(args.path.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files")

    # Process all files
    results = []
    total_blocks = 0
    total_fixed = 0

    for md_file in md_files:
        result = fix_toctree_in_file(md_file, dry_run=dry_run, verbose=args.verbose)
        results.append(result)
        total_blocks += result.get('blocks_found', 0)
        total_fixed += result.get('blocks_fixed', 0)

    # Generate report
    report = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "docs_directory": str(args.path),
            "total_files_processed": len(md_files),
            "dry_run": dry_run
        },
        "summary": {
            "total_toctree_blocks": total_blocks,
            "total_blocks_fixed": total_fixed,
            "files_with_fixes": sum(1 for r in results if r.get('blocks_fixed', 0) > 0)
        },
        "results": results
    }

    # Save report
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Files processed:      {len(md_files)}")
    print(f"Toctree blocks found: {total_blocks}")
    print(f"Blocks fixed:         {total_fixed}")
    print(f"Files with fixes:     {report['summary']['files_with_fixes']}")
    print()

    if dry_run:
        print("[INFO] This was a DRY RUN. Use --apply to write changes.")
    else:
        print("[OK] Fixes applied successfully!")

    print(f"\nDetailed report: {args.output}")

    # Show top files with fixes
    files_with_fixes = [r for r in results if r.get('blocks_fixed', 0) > 0]
    if files_with_fixes:
        print("\nFiles with fixes applied:")
        for result in sorted(files_with_fixes, key=lambda x: x.get('blocks_fixed', 0), reverse=True)[:10]:
            print(f"  {result['filepath']}: {result['blocks_fixed']} block(s)")

    return 0


if __name__ == "__main__":
    exit(main())
