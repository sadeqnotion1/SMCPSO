#==========================================================================================\\\
#======================= scripts/archive_management/compress_logs.py ====================\\\
#==========================================================================================\\\

"""
Three-Tier Log Archive Management System

Implements intelligent log file compression and retention with three archive tiers:
- Tier 1 (Hot): Recent logs (0-7 days) - Uncompressed, immediate access
- Tier 2 (Warm): Recent history (8-30 days) - Compressed (.gz), quick retrieval
- Tier 3 (Cold): Long-term storage (31+ days) - Highly compressed (.tar.gz), archived

Features:
    - Automatic tier migration based on age
    - Configurable retention policies
    - Integrity verification
    - Storage optimization
    - Safe cleanup with dry-run mode
"""

import argparse
import gzip
import hashlib
import shutil
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


class LogArchiveManager:
    """Manages three-tier log archive system with automatic compression and retention."""

    def __init__(self, root_dir: Path, config: Optional[Dict] = None):
        """
        Initialize log archive manager.

        Args:
            root_dir: Root directory for log files
            config: Optional configuration dictionary with keys:
                - tier1_days: Days to keep in hot tier (default: 7)
                - tier2_days: Days to keep in warm tier (default: 30)
                - tier3_days: Days to keep in cold tier (default: 365)
                - archive_dir: Directory for archived logs (default: root_dir/archives)
        """
        self.root_dir = root_dir
        self.config = config or {}

        # Default configuration
        self.tier1_days = self.config.get('tier1_days', 7)
        self.tier2_days = self.config.get('tier2_days', 30)
        self.tier3_days = self.config.get('tier3_days', 365)

        self.archive_dir = Path(self.config.get('archive_dir', root_dir / 'archives'))
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Define tier directories
        self.tier1_dir = self.archive_dir / 'tier1_hot'
        self.tier2_dir = self.archive_dir / 'tier2_warm'
        self.tier3_dir = self.archive_dir / 'tier3_cold'

        for tier_dir in [self.tier1_dir, self.tier2_dir, self.tier3_dir]:
            tier_dir.mkdir(parents=True, exist_ok=True)

    def calculate_file_age(self, filepath: Path) -> int:
        """
        Calculate age of file in days.

        Args:
            filepath: Path to file

        Returns:
            Age in days
        """
        mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
        age = (datetime.now() - mtime).days
        return age

    def get_log_files(self, directory: Path, pattern: str = "*.log") -> List[Path]:
        """
        Find all log files in directory.

        Args:
            directory: Directory to search
            pattern: File pattern to match (default: *.log)

        Returns:
            List of log file paths
        """
        return list(directory.rglob(pattern))

    def compress_to_gz(self, source: Path, dest: Path) -> bool:
        """
        Compress file to .gz format.

        Args:
            source: Source file path
            dest: Destination .gz file path

        Returns:
            True if compression successful
        """
        try:
            with open(source, 'rb') as f_in:
                with gzip.open(dest, 'wb', compresslevel=9) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            return True
        except Exception as e:
            print(f"Error compressing {source}: {e}")
            return False

    def compress_to_tar_gz(self, files: List[Path], dest: Path) -> bool:
        """
        Compress multiple files to .tar.gz archive.

        Args:
            files: List of files to compress
            dest: Destination .tar.gz file path

        Returns:
            True if compression successful
        """
        try:
            with tarfile.open(dest, 'w:gz') as tar:
                for file in files:
                    tar.add(file, arcname=file.name)
            return True
        except Exception as e:
            print(f"Error creating tar.gz archive {dest}: {e}")
            return False

    def verify_integrity(self, original: Path, compressed: Path, is_tarred: bool = False) -> bool:
        """
        Verify integrity of compressed file using checksums.

        Args:
            original: Original file path
            compressed: Compressed file path
            is_tarred: True if compressed file is .tar.gz

        Returns:
            True if integrity check passed
        """
        try:
            # Calculate original checksum
            original_hash = hashlib.sha256()
            with open(original, 'rb') as f:
                original_hash.update(f.read())

            # Calculate compressed checksum (decompress first)
            if is_tarred:
                with tarfile.open(compressed, 'r:gz') as tar:
                    # For tar.gz, we verify the archive can be opened
                    return len(tar.getmembers()) > 0
            else:
                compressed_hash = hashlib.sha256()
                with gzip.open(compressed, 'rb') as f:
                    compressed_hash.update(f.read())
                return original_hash.hexdigest() == compressed_hash.hexdigest()

        except Exception as e:
            print(f"Integrity verification failed for {compressed}: {e}")
            return False

    def migrate_to_tier2(self, file: Path, dry_run: bool = False) -> bool:
        """
        Migrate file from Tier 1 (hot) to Tier 2 (warm).

        Args:
            file: File to migrate
            dry_run: If True, don't actually perform migration

        Returns:
            True if migration successful
        """
        dest = self.tier2_dir / f"{file.name}.gz"

        if dry_run:
            print(f"[DRY RUN] Would migrate {file} → {dest}")
            return True

        print(f"Migrating to Tier 2: {file.name}")

        if self.compress_to_gz(file, dest):
            if self.verify_integrity(file, dest):
                file.unlink()  # Delete original
                return True
            else:
                print(f"⚠️  Integrity check failed for {dest}")
                dest.unlink()  # Delete bad compressed file
                return False

        return False

    def migrate_to_tier3(self, files: List[Path], dry_run: bool = False) -> bool:
        """
        Migrate files from Tier 2 (warm) to Tier 3 (cold).

        Args:
            files: List of files to migrate
            dry_run: If True, don't actually perform migration

        Returns:
            True if migration successful
        """
        if not files:
            return True

        # Group files by month
        date_str = datetime.now().strftime("%Y-%m")
        dest = self.tier3_dir / f"logs_{date_str}.tar.gz"

        if dry_run:
            print(f"[DRY RUN] Would migrate {len(files)} files → {dest}")
            return True

        print(f"Migrating to Tier 3: {len(files)} files → {dest.name}")

        if self.compress_to_tar_gz(files, dest):
            # Delete original files after successful archive
            for file in files:
                file.unlink()
            return True

        return False

    def cleanup_expired(self, dry_run: bool = False) -> int:
        """
        Delete expired files from Tier 3 based on retention policy.

        Args:
            dry_run: If True, don't actually delete files

        Returns:
            Number of files deleted
        """
        deleted = 0
        cutoff_date = datetime.now() - timedelta(days=self.tier3_days)

        for file in self.tier3_dir.rglob("*.tar.gz"):
            mtime = datetime.fromtimestamp(file.stat().st_mtime)

            if mtime < cutoff_date:
                if dry_run:
                    print(f"[DRY RUN] Would delete expired: {file.name}")
                else:
                    print(f"Deleting expired: {file.name}")
                    file.unlink()
                deleted += 1

        return deleted

    def run_maintenance(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Run full archive maintenance cycle.

        Args:
            dry_run: If True, simulate actions without modifying files

        Returns:
            Statistics dictionary with migration/deletion counts
        """
        stats = {
            'tier1_to_tier2': 0,
            'tier2_to_tier3': 0,
            'expired_deleted': 0,
            'errors': 0
        }

        print("=" * 90)
        print("LOG ARCHIVE MAINTENANCE")
        print("=" * 90)
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        print(f"Tier 1 retention: {self.tier1_days} days")
        print(f"Tier 2 retention: {self.tier2_days} days")
        print(f"Tier 3 retention: {self.tier3_days} days")
        print("=" * 90)

        # Migrate Tier 1 → Tier 2 (files older than tier1_days)
        print("\n📦 TIER 1 → TIER 2 MIGRATION")
        tier1_files = self.get_log_files(self.tier1_dir)
        for file in tier1_files:
            age = self.calculate_file_age(file)
            if age > self.tier1_days:
                if self.migrate_to_tier2(file, dry_run):
                    stats['tier1_to_tier2'] += 1
                else:
                    stats['errors'] += 1

        # Migrate Tier 2 → Tier 3 (files older than tier2_days)
        print("\n❄️  TIER 2 → TIER 3 MIGRATION")
        tier2_files = self.get_log_files(self.tier2_dir, "*.log.gz")
        tier2_to_migrate = [f for f in tier2_files if self.calculate_file_age(f) > self.tier2_days]

        if self.migrate_to_tier3(tier2_to_migrate, dry_run):
            stats['tier2_to_tier3'] = len(tier2_to_migrate)
        else:
            stats['errors'] += 1

        # Cleanup expired Tier 3 files
        print("\n🗑️  TIER 3 EXPIRED CLEANUP")
        stats['expired_deleted'] = self.cleanup_expired(dry_run)

        # Final statistics
        print("\n" + "=" * 90)
        print("MAINTENANCE SUMMARY")
        print("=" * 90)
        print(f"Tier 1 → Tier 2: {stats['tier1_to_tier2']} files")
        print(f"Tier 2 → Tier 3: {stats['tier2_to_tier3']} files")
        print(f"Expired deleted: {stats['expired_deleted']} files")
        print(f"Errors: {stats['errors']}")
        print("=" * 90)

        return stats


def main():
    """Main entry point for log archive management."""
    parser = argparse.ArgumentParser(
        description="Three-tier log archive management system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Tier Structure:
    Tier 1 (Hot):  0-7 days    - Uncompressed, immediate access
    Tier 2 (Warm): 8-30 days   - .gz compressed, quick retrieval
    Tier 3 (Cold): 31-365 days - .tar.gz archived, long-term storage

Examples:
    # Run maintenance (live)
    python compress_logs.py --root docs/testing/reports

    # Dry run (no changes)
    python compress_logs.py --root docs/testing/reports --dry-run

    # Custom retention policy
    python compress_logs.py --root docs/testing/reports --tier1 3 --tier2 14 --tier3 180
        """
    )
    parser.add_argument(
        '--root',
        type=Path,
        required=True,
        help='Root directory for log files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate actions without modifying files'
    )
    parser.add_argument(
        '--tier1',
        type=int,
        default=7,
        help='Days to keep in Tier 1 (hot) [default: 7]'
    )
    parser.add_argument(
        '--tier2',
        type=int,
        default=30,
        help='Days to keep in Tier 2 (warm) [default: 30]'
    )
    parser.add_argument(
        '--tier3',
        type=int,
        default=365,
        help='Days to keep in Tier 3 (cold) [default: 365]'
    )

    args = parser.parse_args()

    # Create configuration
    config = {
        'tier1_days': args.tier1,
        'tier2_days': args.tier2,
        'tier3_days': args.tier3
    }

    # Run maintenance
    manager = LogArchiveManager(args.root, config)
    stats = manager.run_maintenance(dry_run=args.dry_run)

    # Exit code based on errors
    return 1 if stats['errors'] > 0 else 0


if __name__ == '__main__':
    import sys
    sys.exit(main())