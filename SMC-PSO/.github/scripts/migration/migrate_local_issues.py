#!/usr/bin/env python3
#==========================================================================================\\\
#========================= migrate_local_issues.py =====================================\\\
#==========================================================================================\\\
"""
Migration script to convert local problem-tracking issues to GitHub Issues.

This script reads existing CSV files from the problem-tracking/ directory and creates
corresponding GitHub issues with proper labels, priorities, and formatting.

Usage:
    python .github/scripts/migration/migrate_local_issues.py
    python .github/scripts/migration/migrate_local_issues.py --dry-run
    python .github/scripts/migration/migrate_local_issues.py --category stability
"""

import argparse
import csv
import json
import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any

# Project paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PROBLEM_TRACKING_DIR = REPO_ROOT / "problem-tracking"

@dataclass
class LocalIssue:
    """Structure for local issue data."""
    id: str
    title: str
    category: str
    priority: str
    description: str
    status: str
    reproduction_steps: str
    controller: Optional[str] = None
    file_path: Optional[str] = None
    created_date: Optional[str] = None
    resolved_date: Optional[str] = None
    resolution: Optional[str] = None

class IssueMigrator:
    """Migrates local problem-tracking issues to GitHub Issues."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.create_issue_script = REPO_ROOT / ".github" / "scripts" / "create_issue.sh"
        if not self.create_issue_script.exists():
            self.create_issue_script = REPO_ROOT / ".github" / "scripts" / "create_issue.bat"

        self.issues_migrated = []
        self.migration_log = []

    def migrate_all_issues(self, category_filter: Optional[str] = None) -> int:
        """Migrate all issues from the local problem-tracking system."""
        if not PROBLEM_TRACKING_DIR.exists():
            print(f"❌ Problem tracking directory not found: {PROBLEM_TRACKING_DIR}")
            return 1

        print("🔍 Scanning for local issues to migrate...")

        # Find all CSV files in the problem-tracking directory
        csv_files = self._find_csv_files()

        if not csv_files:
            print("📝 No CSV files found in problem-tracking directory")
            return 0

        print(f"📂 Found {len(csv_files)} CSV files to process")

        total_migrated = 0
        total_skipped = 0

        for csv_file in csv_files:
            try:
                issues = self._parse_csv_file(csv_file)

                # Filter by category if specified
                if category_filter:
                    issues = [issue for issue in issues if issue.category.lower() == category_filter.lower()]

                if not issues:
                    print(f"⚠️  No issues found in {csv_file.name} (or filtered out)")
                    continue

                print(f"\n📋 Processing {csv_file.name}: {len(issues)} issues")

                for issue in issues:
                    if self._should_migrate_issue(issue):
                        if self._migrate_single_issue(issue, csv_file):
                            total_migrated += 1
                        else:
                            total_skipped += 1
                    else:
                        print(f"⏭️  Skipping {issue.id}: {issue.title} (already resolved/migrated)")
                        total_skipped += 1

            except Exception as e:
                print(f"❌ Error processing {csv_file}: {e}")
                continue

        # Generate migration summary
        self._generate_migration_summary(total_migrated, total_skipped)

        return 0 if total_migrated > 0 else 1

    def _find_csv_files(self) -> List[Path]:
        """Find all CSV files in the problem-tracking directory structure."""
        csv_files = []

        # Search in all subdirectories
        for subdir in ["active", "resolved", "archive", "categories"]:
            subdir_path = PROBLEM_TRACKING_DIR / subdir
            if subdir_path.exists():
                csv_files.extend(subdir_path.glob("*.csv"))

        # Also check the root problem-tracking directory
        csv_files.extend(PROBLEM_TRACKING_DIR.glob("*.csv"))

        return sorted(csv_files)

    def _parse_csv_file(self, csv_file: Path) -> List[LocalIssue]:
        """Parse a CSV file and extract issue data."""
        issues = []

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                # Try to detect the CSV format
                sample = f.read(1024)
                f.seek(0)

                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter

                reader = csv.DictReader(f, delimiter=delimiter)

                for row in reader:
                    issue = self._parse_csv_row(row, csv_file)
                    if issue:
                        issues.append(issue)

        except Exception as e:
            print(f"⚠️  Error parsing {csv_file}: {e}")

        return issues

    def _parse_csv_row(self, row: Dict[str, str], csv_file: Path) -> Optional[LocalIssue]:
        """Parse a single CSV row into a LocalIssue object."""
        try:
            # Map common column variations
            id_field = self._get_field(row, ['id', 'issue_id', 'ID', 'Issue ID'])
            title_field = self._get_field(row, ['title', 'problem', 'issue', 'description', 'Title'])
            category_field = self._get_field(row, ['category', 'type', 'Category', 'Type'])
            priority_field = self._get_field(row, ['priority', 'Priority', 'severity', 'Severity'])
            description_field = self._get_field(row, ['description', 'details', 'Description', 'Details'])
            status_field = self._get_field(row, ['status', 'Status', 'state', 'State'])

            if not id_field or not title_field:
                return None

            return LocalIssue(
                id=id_field,
                title=title_field,
                category=category_field or "implementation",
                priority=priority_field or "medium",
                description=description_field or title_field,
                status=status_field or "active",
                reproduction_steps=self._get_field(row, ['reproduction', 'steps', 'reproduce']) or "See description",
                controller=self._get_field(row, ['controller', 'Controller']),
                file_path=str(csv_file),
                created_date=self._get_field(row, ['created', 'date', 'Created']),
                resolved_date=self._get_field(row, ['resolved', 'resolved_date']),
                resolution=self._get_field(row, ['resolution', 'solution'])
            )

        except Exception as e:
            print(f"⚠️  Error parsing row in {csv_file}: {e}")
            return None

    def _get_field(self, row: Dict[str, str], field_names: List[str]) -> Optional[str]:
        """Get field value from row using multiple possible field names."""
        for field_name in field_names:
            if field_name in row and row[field_name].strip():
                return row[field_name].strip()
        return None

    def _should_migrate_issue(self, issue: LocalIssue) -> bool:
        """Determine if an issue should be migrated."""
        # Skip already resolved issues unless they're in the archive
        if issue.status.lower() in ["resolved", "closed", "completed"] and "archive" not in issue.file_path:
            return False

        # Skip empty or invalid issues
        if not issue.title or issue.title.lower() in ["", "n/a", "none"]:
            return False

        return True

    def _migrate_single_issue(self, issue: LocalIssue, csv_file: Path) -> bool:
        """Migrate a single issue to GitHub Issues."""
        try:
            # Map local categories to GitHub issue types
            github_type = self._map_category_to_type(issue.category)
            github_priority = self._map_priority(issue.priority)

            # Create enhanced description
            description = self._create_github_description(issue, csv_file)

            if self.dry_run:
                print(f"🔄 [DRY RUN] Would create issue: {issue.title}")
                print(f"   Type: {github_type}, Priority: {github_priority}")
                self.migration_log.append({
                    "action": "would_create",
                    "issue_id": issue.id,
                    "title": issue.title,
                    "type": github_type,
                    "priority": github_priority
                })
                return True
            else:
                return self._create_github_issue(issue, github_type, github_priority, description)

        except Exception as e:
            print(f"❌ Error migrating issue {issue.id}: {e}")
            return False

    def _map_category_to_type(self, category: str) -> str:
        """Map local category to GitHub issue type."""
        category_lower = category.lower()

        if any(keyword in category_lower for keyword in ["stability", "lyapunov", "unstable"]):
            return "stability"
        elif any(keyword in category_lower for keyword in ["performance", "overshoot", "settling"]):
            return "performance"
        elif any(keyword in category_lower for keyword in ["convergence", "pso", "optimization"]):
            return "convergence"
        elif any(keyword in category_lower for keyword in ["bounds", "parameter"]):
            return "parameter-bounds"
        elif any(keyword in category_lower for keyword in ["bug", "error", "implementation"]):
            return "implementation"
        elif any(keyword in category_lower for keyword in ["feature", "enhancement"]):
            return "enhancement"
        else:
            return "implementation"

    def _map_priority(self, priority: str) -> str:
        """Map local priority to GitHub priority."""
        priority_lower = priority.lower()

        if priority_lower in ["critical", "urgent", "high"]:
            return "critical" if priority_lower in ["critical", "urgent"] else "high"
        elif priority_lower in ["medium", "normal", "moderate"]:
            return "medium"
        elif priority_lower in ["low", "minor"]:
            return "low"
        else:
            return "medium"

    def _create_github_description(self, issue: LocalIssue, csv_file: Path) -> str:
        """Create an enhanced GitHub issue description."""
        description = f"""
## Issue Summary

{issue.description}

## Migration Information

**Migrated from**: `{csv_file.relative_to(REPO_ROOT)}`
**Original ID**: `{issue.id}`
**Original Category**: `{issue.category}`
**Original Status**: `{issue.status}`
"""

        if issue.controller:
            description += f"**Controller**: `{issue.controller}`\n"

        if issue.created_date:
            description += f"**Original Created Date**: `{issue.created_date}`\n"

        if issue.resolved_date:
            description += f"**Original Resolved Date**: `{issue.resolved_date}`\n"

        description += f"""
## Reproduction Steps

{issue.reproduction_steps}
"""

        if issue.resolution:
            description += f"""
## Previous Resolution

{issue.resolution}
"""

        description += f"""
---

🔄 **This issue was migrated from the local problem-tracking system**

🤖 **Migration performed by**: [GitHub CLI Migration Script](.github/scripts/migration/migrate_local_issues.py)
"""

        return description.strip()

    def _create_github_issue(self, issue: LocalIssue, github_type: str,
                           github_priority: str, description: str) -> bool:
        """Create a GitHub issue using the create_issue script."""
        try:
            # Prepare command
            cmd = [str(self.create_issue_script)]
            cmd.extend(["-t", github_type])
            cmd.extend(["-p", github_priority])
            cmd.extend(["-T", f"[MIGRATED] {issue.title}"])
            cmd.extend(["-d", description])
            cmd.extend(["-r", issue.reproduction_steps])

            if issue.controller:
                cmd.extend(["-c", issue.controller])

            # Execute the issue creation
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ Migrated: {issue.title}")
                self.issues_migrated.append(issue.title)
                self.migration_log.append({
                    "action": "created",
                    "issue_id": issue.id,
                    "title": issue.title,
                    "github_url": result.stdout.strip() if result.stdout else "unknown"
                })
                return True
            else:
                print(f"❌ Failed to migrate: {issue.title}")
                print(f"   Error: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error creating GitHub issue for {issue.title}: {e}")
            return False

    def _generate_migration_summary(self, migrated: int, skipped: int) -> None:
        """Generate and save migration summary."""
        summary = {
            "migration_date": str(Path().cwd()),
            "total_migrated": migrated,
            "total_skipped": skipped,
            "issues_migrated": self.issues_migrated,
            "detailed_log": self.migration_log
        }

        # Save summary to file
        summary_file = REPO_ROOT / ".github" / "migration_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n📊 Migration Summary:")
        print(f"✅ Successfully migrated: {migrated} issues")
        print(f"⏭️  Skipped: {skipped} issues")
        print(f"📄 Detailed log saved to: {summary_file}")

        if self.dry_run:
            print("\n🔄 This was a DRY RUN - no issues were actually created")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Migrate local problem-tracking issues to GitHub Issues")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without creating issues")
    parser.add_argument("--category", help="Only migrate issues from specific category")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    print("🚀 Starting local issue migration to GitHub Issues...")

    if args.dry_run:
        print("🔄 DRY RUN MODE - No issues will be created")

    migrator = IssueMigrator(dry_run=args.dry_run)
    return migrator.migrate_all_issues(category_filter=args.category)

if __name__ == "__main__":
    sys.exit(main())