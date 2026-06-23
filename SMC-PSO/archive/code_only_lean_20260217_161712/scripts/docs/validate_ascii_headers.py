#==========================================================================================\\\
#================== scripts/docs_organization/validate_ascii_headers.py ================\\\
#==========================================================================================\\\

"""ASCII Header Validation and Correction Tool.

This script validates and corrects ASCII headers in Python and Markdown files
to ensure compliance with the 90-character width standard.

Usage:
    python validate_ascii_headers.py --check          # Check compliance
    python validate_ascii_headers.py --fix            # Auto-fix headers
    python validate_ascii_headers.py --report         # Generate report

Expected Header Format (Python):
    #==========================================================================================\\\
    #======================================== filename.py ===================================\\\
    #==========================================================================================\\\

Expected Header Format (Markdown):
    <!--======================================================================================\\\
    ======================================== filename.md ===================================\\\
    =======================================================================================-->
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def calculate_header_parts(filepath: str, width: int = 90) -> Tuple[str, str, str]:
    """Calculate ASCII header components for given file path.

    Args:
        filepath: Relative path to file from project root
        width: Total width of header (default: 90)

    Returns:
        Tuple of (top_border, file_line, bottom_border)

    Example:
        >>> top, mid, bot = calculate_header_parts("src/test.py")
        >>> len(mid)
        90
    """
    # Determine comment style
    if filepath.endswith('.py'):
        comment_start = '#'
        comment_end = '\\\\'
    elif filepath.endswith('.md'):
        comment_start = ''
        comment_end = ''
    else:
        raise ValueError(f"Unsupported file type: {filepath}")

    # Calculate padding
    filename_width = len(filepath)
    available_space = width - len(comment_start) - len(comment_end)
    padding_total = available_space - filename_width

    if padding_total < 4:
        raise ValueError(f"Filename too long: {filepath} ({filename_width} chars)")

    padding_left = padding_total // 2
    padding_right = padding_total - padding_left

    # Build lines
    if filepath.endswith('.py'):
        top_border = f"#{'=' * (width - 3)}\\\\{comment_end[1:]}"
        file_line = (
            f"#{'=' * padding_left}{filepath}{'=' * padding_right}\\\\{comment_end[1:]}"
        )
        bottom_border = top_border
    else:  # Markdown
        top_border = f"<!--{'=' * (width - 8)}\\\\{comment_end}"
        file_line = f"{'=' * padding_left}{filepath}{'=' * padding_right}\\\\{comment_end}"
        bottom_border = f"{'=' * (width - 7)}-->{comment_end}"

    return top_border, file_line, bottom_border


def extract_existing_header(content: str, is_python: bool) -> Optional[str]:
    """Extract existing ASCII header from file content.

    Args:
        content: File content as string
        is_python: True for .py files, False for .md files

    Returns:
        Existing header as string, or None if not found
    """
    if is_python:
        pattern = r'^(#=+\\\\\n#=+.*?=+\\\\\n#=+\\\\\n)'
    else:
        pattern = r'^(<!--=+\\\\\n=+.*?=+\\\\\n=+-->\n)'

    match = re.match(pattern, content, re.MULTILINE)
    return match.group(1) if match else None


def validate_header(filepath: Path, project_root: Path) -> Dict[str, any]:
    """Validate ASCII header in single file.

    Args:
        filepath: Absolute path to file
        project_root: Absolute path to project root

    Returns:
        Validation result dictionary with keys:
        - compliant (bool): True if header is correct
        - existing_header (str): Current header or None
        - expected_header (str): Correct header format
        - errors (List[str]): List of validation errors
    """
    result = {
        'compliant': False,
        'existing_header': None,
        'expected_header': '',
        'errors': []
    }

    try:
        # Calculate relative path
        rel_path = str(filepath.relative_to(project_root)).replace('\\', '/')

        # Generate expected header
        top, mid, bot = calculate_header_parts(rel_path)
        expected = f"{top}\n{mid}\n{bot}\n"
        result['expected_header'] = expected

        # Read file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract existing header
        is_python = filepath.suffix == '.py'
        existing = extract_existing_header(content, is_python)
        result['existing_header'] = existing

        if existing is None:
            result['errors'].append("No ASCII header found")
            return result

        # Compare headers
        if existing.strip() == expected.strip():
            result['compliant'] = True
        else:
            result['errors'].append("Header format incorrect")

    except Exception as e:
        result['errors'].append(f"Error processing file: {e}")

    return result


def fix_header(filepath: Path, project_root: Path) -> bool:
    """Fix ASCII header in single file.

    Args:
        filepath: Absolute path to file
        project_root: Absolute path to project root

    Returns:
        True if header was fixed, False otherwise
    """
    try:
        # Calculate relative path and expected header
        rel_path = str(filepath.relative_to(project_root)).replace('\\', '/')
        top, mid, bot = calculate_header_parts(rel_path)
        expected = f"{top}\n{mid}\n{bot}\n"

        # Read file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove existing header if present
        is_python = filepath.suffix == '.py'
        existing = extract_existing_header(content, is_python)

        if existing:
            content = content[len(existing):]

        # Add new header
        new_content = expected + content

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True

    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False


def scan_files(project_root: Path, extensions: List[str]) -> List[Path]:
    """Scan project for files with specified extensions.

    Args:
        project_root: Absolute path to project root
        extensions: List of file extensions to scan (e.g., ['.py', '.md'])

    Returns:
        List of absolute file paths
    """
    files = []

    # Excluded directories
    excluded_dirs = {
        '.git', '__pycache__', '.pytest_cache', '.venv', 'venv',
        'node_modules', '.tox', '.eggs', '*.egg-info', 'dist', 'build',
        '.archive', '.build', '.dev_tools', '.tools', '.benchmarks'
    }

    for ext in extensions:
        for filepath in project_root.rglob(f"*{ext}"):
            # Check if file is in excluded directory
            if any(excluded in filepath.parts for excluded in excluded_dirs):
                continue
            files.append(filepath)

    return sorted(files)


def generate_report(
    results: Dict[Path, Dict],
    output_path: Optional[Path] = None
) -> str:
    """Generate compliance report.

    Args:
        results: Dictionary mapping file paths to validation results
        output_path: Optional path to save report

    Returns:
        Report as formatted string
    """
    total = len(results)
    compliant = sum(1 for r in results.values() if r['compliant'])
    compliance_rate = (compliant / total * 100) if total > 0 else 0

    report_lines = [
        "=" * 90,
        "ASCII HEADER COMPLIANCE REPORT",
        "=" * 90,
        f"\nTotal Files Scanned: {total}",
        f"Compliant Files: {compliant}",
        f"Non-Compliant Files: {total - compliant}",
        f"Compliance Rate: {compliance_rate:.1f}%",
        "\n" + "=" * 90,
        "NON-COMPLIANT FILES:",
        "=" * 90,
    ]

    for filepath, result in results.items():
        if not result['compliant']:
            report_lines.append(f"\n{filepath}")
            for error in result['errors']:
                report_lines.append(f"  - {error}")

    report = "\n".join(report_lines)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

    return report


def main() -> None:
    """Main entry point for ASCII header validation tool."""
    parser = argparse.ArgumentParser(
        description="Validate and fix ASCII headers in Python and Markdown files"
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check header compliance without fixing'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Automatically fix non-compliant headers'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate detailed compliance report'
    )
    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['.py', '.md'],
        help='File extensions to process (default: .py .md)'
    )
    parser.add_argument(
        '--root',
        type=str,
        default='.',
        help='Project root directory (default: current directory)'
    )

    args = parser.parse_args()

    # Resolve project root
    project_root = Path(args.root).resolve()

    print(f"Scanning project: {project_root}")
    print(f"Extensions: {', '.join(args.extensions)}")

    # Scan files
    files = scan_files(project_root, args.extensions)
    print(f"Found {len(files)} files to process\n")

    # Validate all files
    results = {}
    for filepath in files:
        results[filepath] = validate_header(filepath, project_root)

    # Calculate compliance
    total = len(results)
    compliant = sum(1 for r in results.values() if r['compliant'])
    compliance_rate = (compliant / total * 100) if total > 0 else 0

    print(f"Compliance Rate: {compliance_rate:.1f}% ({compliant}/{total})")

    # Fix mode
    if args.fix:
        print("\nFixing non-compliant headers...")
        fixed_count = 0
        for filepath, result in results.items():
            if not result['compliant']:
                if fix_header(filepath, project_root):
                    fixed_count += 1
                    print(f"  ✓ Fixed: {filepath.relative_to(project_root)}")
                else:
                    print(f"  ✗ Failed: {filepath.relative_to(project_root)}")

        print(f"\nFixed {fixed_count} files")

    # Report mode
    if args.report:
        report_path = project_root / 'artifacts' / 'ascii_header_report.txt'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report = generate_report(results, report_path)
        print(f"\nReport saved to: {report_path}")
        print("\n" + report)

    # Check mode (default)
    if args.check or not (args.fix or args.report):
        print("\nNon-compliant files:")
        for filepath, result in results.items():
            if not result['compliant']:
                rel_path = filepath.relative_to(project_root)
                print(f"  ✗ {rel_path}")
                for error in result['errors']:
                    print(f"    - {error}")


if __name__ == '__main__':
    main()