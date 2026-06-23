#!/usr/bin/env python
"""
=================================================================================
File: scripts/validation/fix_common_issues.py
Description: Automated fixer for common quality issues in DIP-SMC-PSO
=================================================================================

Phase 6.5: Documentation Quality Gates - Auto-Fix Script

This script automatically fixes common quality issues to reduce manual effort:
- Import statement organization (isort)
- Code formatting (black/ruff)
- Trailing whitespace
- Missing final newlines
- Common markdown issues
- Simple spelling corrections

Usage:
    python scripts/validation/fix_common_issues.py
    python scripts/validation/fix_common_issues.py --dry-run  # Preview changes only
    python scripts/validation/fix_common_issues.py --target src  # Specific directory
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class CommonIssueFixer:
    """Automatically fixes common quality issues."""

    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.fixes_applied = 0
        self.files_modified = set()

    def print_header(self, title: str) -> None:
        """Print a formatted section header."""
        print(f"\n{Colors.BLUE}{Colors.BOLD}{title}{Colors.END}")
        print(f"{Colors.BLUE}{'─' * 60}{Colors.END}")

    def print_fix(self, description: str, file_path: Path = None) -> None:
        """Print a fix notification."""
        mode = "Would fix" if self.dry_run else "Fixed"
        file_info = f" in {file_path.name}" if file_path else ""
        print(f"{Colors.GREEN}✓{Colors.END} {mode}: {description}{file_info}")
        if not self.dry_run:
            self.fixes_applied += 1
            if file_path:
                self.files_modified.add(file_path)

    def run_command(self, cmd: List[str], description: str) -> bool:
        """Execute a shell command."""
        try:
            if self.dry_run:
                print(f"{Colors.YELLOW}Would run:{Colors.END} {' '.join(cmd)}")
                return True

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.project_root
            )
            if result.returncode == 0:
                self.print_fix(description)
                return True
            else:
                print(f"{Colors.RED}Failed:{Colors.END} {description}")
                if result.stderr:
                    print(f"  Error: {result.stderr[:200]}")
                return False
        except Exception as e:
            print(f"{Colors.RED}Error:{Colors.END} {description} - {e}")
            return False

    def fix_trailing_whitespace(self, target_dir: Path) -> None:
        """Remove trailing whitespace from Python and Markdown files."""
        self.print_header("🧹 Fixing Trailing Whitespace")

        for pattern in ["**/*.py", "**/*.md"]:
            for file_path in target_dir.glob(pattern):
                if '.git' in str(file_path) or '__pycache__' in str(file_path):
                    continue

                original_content = file_path.read_text(encoding='utf-8')
                lines = original_content.splitlines(keepends=True)
                fixed_lines = [line.rstrip() + '\n' if line.endswith(('\n', '\r\n')) else line.rstrip()
                              for line in lines]
                fixed_content = ''.join(fixed_lines)

                if original_content != fixed_content:
                    if not self.dry_run:
                        file_path.write_text(fixed_content, encoding='utf-8')
                    self.print_fix("Removed trailing whitespace", file_path)

    def fix_final_newlines(self, target_dir: Path) -> None:
        """Ensure files end with a single newline."""
        self.print_header("📄 Fixing Final Newlines")

        for pattern in ["**/*.py", "**/*.md", "**/*.yaml", "**/*.yml"]:
            for file_path in target_dir.glob(pattern):
                if '.git' in str(file_path) or '__pycache__' in str(file_path):
                    continue

                content = file_path.read_text(encoding='utf-8')

                if content and not content.endswith('\n'):
                    if not self.dry_run:
                        file_path.write_text(content + '\n', encoding='utf-8')
                    self.print_fix("Added final newline", file_path)
                elif content.endswith('\n\n'):
                    if not self.dry_run:
                        file_path.write_text(content.rstrip('\n') + '\n', encoding='utf-8')
                    self.print_fix("Fixed multiple final newlines", file_path)

    def fix_imports_with_isort(self, target_dir: Path) -> None:
        """Organize imports using isort."""
        self.print_header("📦 Organizing Imports (isort)")

        cmd = ["isort", str(target_dir), "--profile", "black"]
        self.run_command(cmd, "Organized imports with isort")

    def fix_formatting_with_ruff(self, target_dir: Path) -> None:
        """Format code using ruff."""
        self.print_header("🎨 Code Formatting (ruff)")

        cmd = ["ruff", "format", str(target_dir)]
        self.run_command(cmd, "Formatted code with ruff")

    def fix_common_linting_issues(self, target_dir: Path) -> None:
        """Auto-fix common linting issues with ruff."""
        self.print_header("🔧 Auto-Fixing Linting Issues (ruff)")

        cmd = ["ruff", "check", str(target_dir), "--fix"]
        self.run_command(cmd, "Fixed auto-fixable linting issues")

    def fix_markdown_issues(self, target_dir: Path) -> None:
        """Fix common markdown issues."""
        self.print_header("📝 Fixing Markdown Issues")

        for file_path in target_dir.glob("**/*.md"):
            if '.git' in str(file_path):
                continue

            content = file_path.read_text(encoding='utf-8')
            original_content = content

            # Fix: Multiple blank lines → single blank line
            content = re.sub(r'\n{3,}', '\n\n', content)

            # Fix: Spaces before heading markers
            content = re.sub(r'^\s+(#{1,6})\s+', r'\1 ', content, flags=re.MULTILINE)

            # Fix: Missing space after list markers
            content = re.sub(r'^([-*+])\s*([^\s])', r'\1 \2', content, flags=re.MULTILINE)

            # Fix: Inconsistent code fence markers (use triple backticks)
            content = re.sub(r'^~~~', '```', content, flags=re.MULTILINE)

            if content != original_content:
                if not self.dry_run:
                    file_path.write_text(content, encoding='utf-8')
                self.print_fix("Fixed markdown formatting", file_path)

    def fix_common_typos(self, target_dir: Path) -> None:
        """Fix common typos in documentation."""
        self.print_header("✏️ Fixing Common Typos")

        # Common typos mapping (conservative list)
        typo_fixes = {
            r'\bteh\b': 'the',
            r'\boccured\b': 'occurred',
            r'\bsucessful\b': 'successful',
            r'\bperformace\b': 'performance',
            r'\bparameter\s+parameter\b': 'parameter',  # Duplicate word
        }

        for file_path in target_dir.glob("**/*.md"):
            if '.git' in str(file_path):
                continue

            content = file_path.read_text(encoding='utf-8')
            original_content = content

            for typo_pattern, correction in typo_fixes.items():
                content = re.sub(typo_pattern, correction, content, flags=re.IGNORECASE)

            if content != original_content:
                if not self.dry_run:
                    file_path.write_text(content, encoding='utf-8')
                self.print_fix("Fixed typos", file_path)

    def run_all_fixes(self, target_dir: Path) -> None:
        """Run all auto-fixes."""
        print(f"\n{Colors.BOLD}DIP-SMC-PSO Auto-Fix Runner{Colors.END}")
        print(f"Target: {target_dir}")
        print(f"Mode: {'DRY RUN (no changes)' if self.dry_run else 'APPLY FIXES'}\n")

        # Python file fixes
        if (target_dir / "src").exists() or target_dir.name == "src":
            self.fix_trailing_whitespace(target_dir)
            self.fix_final_newlines(target_dir)
            self.fix_imports_with_isort(target_dir)
            self.fix_formatting_with_ruff(target_dir)
            self.fix_common_linting_issues(target_dir)

        # Documentation fixes
        if (target_dir / "docs").exists() or target_dir.name == "docs":
            self.fix_markdown_issues(target_dir)
            self.fix_common_typos(target_dir)

        # Summary
        self.print_summary()

    def print_summary(self) -> None:
        """Print final summary."""
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'═' * 60}{Colors.END}")
        print(f"{Colors.BOLD}Summary{Colors.END}")
        print(f"{'─' * 60}")

        if self.dry_run:
            print(f"Mode: {Colors.YELLOW}DRY RUN{Colors.END} (no changes applied)")
            print(f"Potential fixes: {self.fixes_applied}")
            print("\nRun without --dry-run to apply these fixes.")
        else:
            print(f"Fixes applied: {Colors.GREEN}{self.fixes_applied}{Colors.END}")
            print(f"Files modified: {len(self.files_modified)}")

            if self.files_modified:
                print("\nModified files:")
                for file_path in sorted(self.files_modified)[:10]:
                    print(f"  • {file_path.relative_to(self.project_root)}")
                if len(self.files_modified) > 10:
                    print(f"  ... and {len(self.files_modified) - 10} more")

            print(f"\n{Colors.GREEN}✓ Auto-fix complete!{Colors.END}")
            print("Run quality checks to verify: python scripts/validation/run_quality_checks.py")

        print(f"{Colors.BLUE}{'═' * 60}{Colors.END}\n")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automatically fix common quality issues in DIP-SMC-PSO project"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )
    parser.add_argument(
        '--target',
        type=str,
        default='.',
        help='Target directory (default: project root)'
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    target_dir = project_root if args.target == '.' else project_root / args.target

    if not target_dir.exists():
        print(f"{Colors.RED}Error:{Colors.END} Target directory does not exist: {target_dir}")
        return 1

    fixer = CommonIssueFixer(project_root, dry_run=args.dry_run)
    fixer.run_all_fixes(target_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
