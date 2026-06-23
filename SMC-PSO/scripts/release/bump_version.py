#!/usr/bin/env python
"""
=================================================================================
File: scripts/release/bump_version.py
Description: Automated version bumping for DIP-SMC-PSO releases
=================================================================================

Phase 6.6: Changelog & Version Documentation - Version Automation

This script automates version bumping across the project, ensuring consistency
between setup.py, docs/conf.py, and creating git tags.

Usage:
    python scripts/release/bump_version.py --bump major  # 1.2.3 -> 2.0.0
    python scripts/release/bump_version.py --bump minor  # 1.2.3 -> 1.3.0
    python scripts/release/bump_version.py --bump patch  # 1.2.3 -> 1.2.4
    python scripts/release/bump_version.py --set 2.0.0   # Set specific version
    python scripts/release/bump_version.py --dry-run     # Preview changes
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class VersionBumper:
    """Automates version bumping across project files."""

    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.version_files = {
            'setup.py': project_root / 'setup.py',
            'docs/conf.py': project_root / 'docs' / 'conf.py',
            '__init__.py': project_root / 'src' / '__init__.py',
        }

    def print_header(self, title: str) -> None:
        """Print a formatted section header."""
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'═' * 80}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{title}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{'═' * 80}{Colors.END}\n")

    def parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse semantic version string."""
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:-.*)?$', version)
        if not match:
            raise ValueError(f"Invalid version format: {version}")
        return tuple(map(int, match.groups()))

    def format_version(self, major: int, minor: int, patch: int) -> str:
        """Format version as semantic version string."""
        return f"{major}.{minor}.{patch}"

    def get_current_version(self) -> str:
        """Extract current version from setup.py."""
        setup_py = self.version_files['setup.py']

        if not setup_py.exists():
            raise FileNotFoundError(f"setup.py not found at {setup_py}")

        content = setup_py.read_text(encoding='utf-8')
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)

        if not match:
            raise ValueError("Could not find version in setup.py")

        return match.group(1)

    def bump_version(self, current: str, bump_type: str) -> str:
        """Calculate new version based on bump type."""
        major, minor, patch = self.parse_version(current)

        if bump_type == 'major':
            return self.format_version(major + 1, 0, 0)
        elif bump_type == 'minor':
            return self.format_version(major, minor + 1, 0)
        elif bump_type == 'patch':
            return self.format_version(major, minor, patch + 1)
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

    def update_version_in_file(self, file_path: Path, old_version: str, new_version: str) -> bool:
        """Update version string in a file."""
        if not file_path.exists():
            print(f"{Colors.YELLOW}⚠ Skipped:{Colors.END} {file_path.name} (not found)")
            return False

        content = file_path.read_text(encoding='utf-8')
        original_content = content

        # Update version patterns
        patterns = [
            (r'version\s*=\s*["\']([^"\']+)["\']', f'version = "{new_version}"'),
            (r'__version__\s*=\s*["\']([^"\']+)["\']', f'__version__ = "{new_version}"'),
            (r'release\s*=\s*["\']([^"\']+)["\']', f'release = "{new_version}"'),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        if content == original_content:
            print(f"{Colors.YELLOW}⚠ No change:{Colors.END} {file_path.name}")
            return False

        if not self.dry_run:
            file_path.write_text(content, encoding='utf-8')

        print(f"{Colors.GREEN}✓ Updated:{Colors.END} {file_path.name} ({old_version} → {new_version})")
        return True

    def create_git_tag(self, version: str, message: Optional[str] = None) -> bool:
        """Create annotated git tag for release."""
        tag_name = f"v{version}"
        tag_message = message or f"Release version {version}"

        if self.dry_run:
            print(f"{Colors.YELLOW}Would create:{Colors.END} Git tag {tag_name}")
            return True

        try:
            # Check if tag already exists
            result = subprocess.run(
                ['git', 'tag', '-l', tag_name],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            if result.stdout.strip():
                print(f"{Colors.RED}✗ Failed:{Colors.END} Tag {tag_name} already exists")
                return False

            # Create annotated tag
            subprocess.run(
                ['git', 'tag', '-a', tag_name, '-m', tag_message],
                check=True,
                cwd=self.project_root
            )

            print(f"{Colors.GREEN}✓ Created:{Colors.END} Git tag {tag_name}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}✗ Failed:{Colors.END} Git tag creation: {e}")
            return False

    def update_changelog(self, version: str) -> bool:
        """Update CHANGELOG.md with new version section."""
        changelog = self.project_root / 'CHANGELOG.md'

        if not changelog.exists():
            print(f"{Colors.YELLOW}⚠ Skipped:{Colors.END} CHANGELOG.md not found")
            return False

        content = changelog.read_text(encoding='utf-8')
        today = subprocess.check_output(['date', '+%Y-%m-%d'], text=True).strip()

        # Insert new version section after header
        new_section = f"""
## [{version}] - {today}

### Added
-

### Changed
-

### Fixed
-

"""

        # Find position to insert (after # Changelog header)
        lines = content.split('\n')
        insert_pos = 0

        for i, line in enumerate(lines):
            if line.strip().startswith('##'):
                insert_pos = i
                break

        if insert_pos > 0:
            lines.insert(insert_pos, new_section.strip())
            new_content = '\n'.join(lines)

            if not self.dry_run:
                changelog.write_text(new_content, encoding='utf-8')

            print(f"{Colors.GREEN}✓ Updated:{Colors.END} CHANGELOG.md")
            return True

        return False

    def run(self, bump_type: Optional[str] = None, set_version: Optional[str] = None,
            tag_message: Optional[str] = None) -> int:
        """Run version bumping workflow."""
        self.print_header("DIP-SMC-PSO Version Bumper")

        if self.dry_run:
            print(f"{Colors.YELLOW}DRY RUN MODE{Colors.END} - No changes will be made\n")

        # Get current version
        try:
            current_version = self.get_current_version()
            print(f"Current version: {Colors.BOLD}{current_version}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}Error:{Colors.END} {e}")
            return 1

        # Calculate new version
        if set_version:
            new_version = set_version
            print(f"Setting version: {Colors.BOLD}{new_version}{Colors.END}")
        elif bump_type:
            try:
                new_version = self.bump_version(current_version, bump_type)
                print(f"Bumping {bump_type}: {Colors.BOLD}{current_version} → {new_version}{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}Error:{Colors.END} {e}")
                return 1
        else:
            print(f"{Colors.RED}Error:{Colors.END} Must specify --bump or --set")
            return 1

        # Validate new version
        try:
            self.parse_version(new_version)
        except ValueError as e:
            print(f"{Colors.RED}Error:{Colors.END} {e}")
            return 1

        # Update version files
        self.print_header("Updating Version Files")

        updated_files = []
        for name, file_path in self.version_files.items():
            if self.update_version_in_file(file_path, current_version, new_version):
                updated_files.append(file_path)

        # Update changelog
        self.print_header("Updating Changelog")
        self.update_changelog(new_version)

        # Create git tag
        self.print_header("Creating Git Tag")
        self.create_git_tag(new_version, tag_message)

        # Summary
        self.print_header("Summary")

        if self.dry_run:
            print(f"{Colors.YELLOW}DRY RUN COMPLETE{Colors.END}")
            print(f"\nWould update {len(updated_files)} files")
            print(f"Would create tag: v{new_version}")
            print("\nRun without --dry-run to apply changes")
        else:
            print(f"{Colors.GREEN}✓ Version bumped successfully!{Colors.END}")
            print(f"\nNew version: {Colors.BOLD}{new_version}{Colors.END}")
            print(f"Updated: {len(updated_files)} files")
            print(f"Tag created: v{new_version}")
            print(f"\n{Colors.YELLOW}Next steps:{Colors.END}")
            print("  1. Review changes: git diff")
            print(f"  2. Commit changes: git add . && git commit -m 'chore: bump version to {new_version}'")
            print(f"  3. Push tag: git push origin v{new_version}")
            print("  4. Create release on GitHub")

        return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Bump version for DIP-SMC-PSO releases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Bump patch version (1.2.3 -> 1.2.4):
    python scripts/release/bump_version.py --bump patch

  Bump minor version (1.2.3 -> 1.3.0):
    python scripts/release/bump_version.py --bump minor

  Bump major version (1.2.3 -> 2.0.0):
    python scripts/release/bump_version.py --bump major

  Set specific version:
    python scripts/release/bump_version.py --set 2.0.0

  Dry run (preview changes):
    python scripts/release/bump_version.py --bump minor --dry-run
        """
    )

    parser.add_argument(
        '--bump',
        choices=['major', 'minor', 'patch'],
        help='Bump type (major.minor.patch)'
    )
    parser.add_argument(
        '--set',
        type=str,
        metavar='VERSION',
        help='Set specific version (e.g., 2.0.0)'
    )
    parser.add_argument(
        '--tag-message',
        type=str,
        metavar='MESSAGE',
        help='Custom git tag message'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.bump and not args.set:
        parser.error("Must specify either --bump or --set")

    if args.bump and args.set:
        parser.error("Cannot specify both --bump and --set")

    project_root = Path(__file__).parent.parent.parent
    bumper = VersionBumper(project_root, dry_run=args.dry_run)

    return bumper.run(
        bump_type=args.bump,
        set_version=args.set,
        tag_message=args.tag_message
    )


if __name__ == "__main__":
    sys.exit(main())
