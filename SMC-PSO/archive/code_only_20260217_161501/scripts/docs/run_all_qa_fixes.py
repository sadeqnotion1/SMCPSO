"""
Master QA Fix Orchestration Script
===================================

Runs all automated QA fix scripts in the correct sequence and re-audits results.

Workflow:
1. Run emoji_replacer.py (auto-fix Unicode emojis)
2. Run heading_fixer.py (auto-fix heading structure)
3. Run sentence_analyzer.py (report long sentences)
4. Run QA audit script to verify improvements

Usage:
    python scripts/docs/run_all_qa_fixes.py --all --backup
    python scripts/docs/run_all_qa_fixes.py --file README.md

Options:
    --all: Process all 4 main entry points
    --file PATH: Process single file
    --backup: Create .bak backups before modification
    --dry-run: Report what would be fixed without modifying files

Author: Claude Code (Automated QA Script)
Date: November 2025
"""

import subprocess
import argparse
import sys
from pathlib import Path
from typing import List, Dict


def run_command(cmd: List[str], description: str) -> Dict:
    """
    Run a subprocess command and capture output.

    Args:
        cmd: Command list (e.g., ['python', 'script.py', '--arg'])
        description: Human-readable description

    Returns:
        Dictionary with exit code, stdout, stderr
    """
    print(f"\n{'=' * 70}")
    print(f"[INFO] {description}")
    print(f"{'=' * 70}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        # Print stdout
        if result.stdout:
            print(result.stdout)

        # Print stderr if error
        if result.returncode != 0 and result.stderr:
            print(f"[ERROR] {result.stderr}", file=sys.stderr)

        return {
            'success': result.returncode == 0,
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

    except subprocess.TimeoutExpired:
        print(f"[ERROR] Command timed out after 120 seconds", file=sys.stderr)
        return {
            'success': False,
            'exit_code': -1,
            'stdout': '',
            'stderr': 'Command timed out'
        }
    except Exception as e:
        print(f"[ERROR] Failed to run command: {e}", file=sys.stderr)
        return {
            'success': False,
            'exit_code': -1,
            'stdout': '',
            'stderr': str(e)
        }


def main():
    parser = argparse.ArgumentParser(
        description='Run all QA fix scripts in sequence'
    )
    parser.add_argument(
        '--file',
        type=Path,
        help='Single file to process'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all 4 main entry points'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create .bak backup files before modification'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Report what would be changed without modifying files'
    )

    args = parser.parse_args()

    if not args.all and not args.file:
        parser.error("Must specify either --file or --all")

    # Build base arguments for child scripts
    target_args = ['--all'] if args.all else ['--file', str(args.file)]
    backup_args = ['--backup'] if args.backup else []
    dry_run_args = ['--dry-run'] if args.dry_run else []

    print("\n" + "=" * 70)
    print("QA FIX ORCHESTRATION WORKFLOW")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Backup: {'Enabled' if args.backup else 'Disabled'}")
    print(f"Target: {'All 4 files' if args.all else args.file}")
    print("=" * 70)

    results = {}

    # Step 1: Emoji Replacer
    results['emoji_replacer'] = run_command(
        ['python', 'scripts/docs/emoji_replacer.py'] + target_args + backup_args + dry_run_args,
        description="STEP 1/3: Replace Unicode Emojis with ASCII"
    )

    if not results['emoji_replacer']['success']:
        print("\n[ERROR] Emoji replacer failed. Aborting workflow.", file=sys.stderr)
        return 1

    # Step 2: Heading Fixer
    results['heading_fixer'] = run_command(
        ['python', 'scripts/docs/heading_fixer.py'] + target_args + backup_args + dry_run_args,
        description="STEP 2/3: Fix Heading Structure (Capitalization, Trailing Punctuation)"
    )

    if not results['heading_fixer']['success']:
        print("\n[ERROR] Heading fixer failed. Aborting workflow.", file=sys.stderr)
        return 1

    # Step 3: Sentence Analyzer (reporting only)
    results['sentence_analyzer'] = run_command(
        ['python', 'scripts/docs/sentence_analyzer.py'] + target_args,
        description="STEP 3/3: Analyze Long Sentences (Reporting Only)"
    )

    if not results['sentence_analyzer']['success']:
        print("\n[WARNING] Sentence analyzer failed (non-fatal)")

    # Step 4: Re-audit (if not dry-run and processing all files)
    if not args.dry_run and args.all:
        print("\n" + "=" * 70)
        print("[INFO] VERIFICATION: Re-running QA Audit")
        print("=" * 70)

        results['reaudit'] = run_command(
            ['python', '.project/ai/qa/qa_02_audit_script.py'] + target_args,
            description="Re-audit QA-02 Scores After Fixes"
        )

        if results['reaudit']['success']:
            print("\n[OK] Re-audit completed successfully")
        else:
            print("\n[WARNING] Re-audit failed (may need manual verification)")

    # Final Summary
    print("\n" + "=" * 70)
    print("WORKFLOW SUMMARY")
    print("=" * 70)

    step_names = {
        'emoji_replacer': 'Emoji Replacer',
        'heading_fixer': 'Heading Fixer',
        'sentence_analyzer': 'Sentence Analyzer',
        'reaudit': 'QA Re-Audit'
    }

    for step, name in step_names.items():
        if step in results:
            status = "[OK]" if results[step]['success'] else "[FAILED]"
            print(f"  {status} {name}")

    print("=" * 70)

    # Extract key metrics from stdout
    if not args.dry_run:
        print("\nKey Metrics:")

        # Emoji replacements
        if 'Total replacements:' in results['emoji_replacer']['stdout']:
            for line in results['emoji_replacer']['stdout'].splitlines():
                if 'Total replacements:' in line:
                    print(f"  - Emoji replacements: {line.split(':')[1].strip()}")

        # Heading fixes
        if 'Headings fixed:' in results['heading_fixer']['stdout']:
            for line in results['heading_fixer']['stdout'].splitlines():
                if 'Headings fixed:' in line:
                    print(f"  - Headings fixed: {line.split(':')[1].strip()}")

        # Long sentences
        if 'Total long sentences' in results['sentence_analyzer']['stdout']:
            for line in results['sentence_analyzer']['stdout'].splitlines():
                if 'Total long sentences' in line:
                    print(f"  - Long sentences found: {line.split(':')[1].strip()}")

    print("\n[INFO] QA fix workflow complete!")

    # Return exit code based on critical steps
    critical_failures = sum(
        1 for step in ['emoji_replacer', 'heading_fixer']
        if not results.get(step, {}).get('success', False)
    )

    return 1 if critical_failures > 0 else 0


if __name__ == '__main__':
    exit(main())
