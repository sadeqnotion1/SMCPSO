#==========================================================================================\\\
#============ scripts/docs_organization/generate_structure_report.py ====================\\\
#==========================================================================================\\\

"""
Documentation Structure Health Report Generator

Generates comprehensive health score and structural analysis for documentation directories.

Health Scoring Criteria (10-point scale):
    - Organization: Clear directory hierarchy and logical file placement
    - ASCII Headers: Compliance with 90-character header standard
    - Naming Conventions: Consistent file/directory naming patterns
    - Navigation: Presence of index files and breadcrumb trails
    - Redundancy: Absence of duplicate or overlapping content
    - Coverage: Completeness of documentation across domains
    - Maintainability: Automation scripts and tooling presence
    - Cleanliness: No cache files, temporary files, or artifacts

Output:
    - Overall health score (0-10)
    - Component-wise breakdown
    - Actionable recommendations
    - Trend analysis (if historical data available)
"""

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict


class DocumentationHealthAnalyzer:
    """Analyzes documentation structure and generates health reports."""

    def __init__(self, docs_root: Path):
        """
        Initialize analyzer with documentation root.

        Args:
            docs_root: Root directory for documentation
        """
        self.docs_root = docs_root
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'root_path': str(docs_root),
            'scores': {},
            'metrics': {},
            'issues': [],
            'recommendations': []
        }

    def analyze_organization(self) -> float:
        """
        Analyze directory organization and structure.

        Returns:
            Score from 0.0 to 10.0
        """
        score = 10.0
        issues = []

        # Check for excessive root-level files
        root_files = [f for f in self.docs_root.iterdir() if f.is_file()]
        if len(root_files) > 5:
            penalty = min(2.0, (len(root_files) - 5) * 0.2)
            score -= penalty
            issues.append(f"Too many root-level files ({len(root_files)}). Target: ≤5")

        # Check for empty directories
        empty_dirs = [d for d in self.docs_root.rglob("*") if d.is_dir() and not any(d.iterdir())]
        if empty_dirs:
            score -= min(1.5, len(empty_dirs) * 0.3)
            issues.append(f"{len(empty_dirs)} empty directories found")

        # Check for proper subdirectory structure
        expected_subdirs = {'guides', 'standards', 'templates', 'reports'}
        existing_subdirs = {d.name for d in self.docs_root.iterdir() if d.is_dir() and not d.name.startswith('.')}
        missing = expected_subdirs - existing_subdirs

        if missing:
            score -= min(2.0, len(missing) * 0.5)
            issues.append(f"Missing expected subdirectories: {', '.join(missing)}")

        self.results['issues'].extend(issues)
        self.results['metrics']['root_files'] = len(root_files)
        self.results['metrics']['empty_directories'] = len(empty_dirs)

        return max(0.0, score)

    def analyze_ascii_headers(self) -> float:
        """
        Analyze ASCII header compliance in markdown files.

        Returns:
            Score from 0.0 to 10.0
        """
        md_files = list(self.docs_root.rglob("*.md"))
        compliant = 0
        issues = []

        header_pattern = r'^<!--=+\\\\\n=+.*?=+\\\\\n=+-->'

        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)  # Check first 500 chars

                if re.match(header_pattern, content):
                    compliant += 1
                else:
                    issues.append(f"Missing/incorrect header: {md_file.relative_to(self.docs_root)}")

            except Exception as e:
                issues.append(f"Error reading {md_file.name}: {e}")

        compliance_rate = (compliant / len(md_files) * 100) if md_files else 100
        score = (compliance_rate / 100) * 10

        if compliance_rate < 95:
            self.results['recommendations'].append(
                "Run validate_ascii_headers.py --fix to achieve 100% compliance"
            )

        self.results['metrics']['ascii_header_compliance'] = f"{compliance_rate:.1f}%"
        self.results['metrics']['compliant_files'] = compliant
        self.results['metrics']['total_md_files'] = len(md_files)

        return score

    def analyze_naming_conventions(self) -> float:
        """
        Analyze file and directory naming consistency.

        Returns:
            Score from 0.0 to 10.0
        """
        score = 10.0
        issues = []

        # Check for consistent naming patterns
        all_files = list(self.docs_root.rglob("*.md"))

        # Naming rules:
        # - Use snake_case for multi-word names
        # - Avoid spaces and special characters
        # - Use descriptive names (not test1.md, doc.md, etc.)

        non_compliant_names = []
        for file in all_files:
            name = file.stem

            # Check for spaces
            if ' ' in name:
                non_compliant_names.append((file, "Contains spaces"))

            # Check for generic names
            generic_names = ['test', 'doc', 'file', 'temp', 'new', 'untitled']
            if name.lower() in generic_names:
                non_compliant_names.append((file, "Generic name"))

            # Check for camelCase or PascalCase (prefer snake_case)
            if re.search(r'[a-z][A-Z]', name):
                non_compliant_names.append((file, "Should use snake_case"))

        if non_compliant_names:
            penalty = min(3.0, len(non_compliant_names) * 0.3)
            score -= penalty

            for file, reason in non_compliant_names[:5]:  # Show first 5
                issues.append(f"{file.relative_to(self.docs_root)}: {reason}")

        self.results['issues'].extend(issues)
        self.results['metrics']['naming_violations'] = len(non_compliant_names)

        return max(0.0, score)

    def analyze_navigation(self) -> float:
        """
        Analyze navigation aids (index files, breadcrumbs).

        Returns:
            Score from 0.0 to 10.0
        """
        score = 10.0
        issues = []

        # Check for master navigation index
        master_index = self.docs_root / 'navigation_index.md'
        if not master_index.exists():
            score -= 3.0
            issues.append("Missing master navigation_index.md")
            self.results['recommendations'].append("Create navigation_index.md at documentation root")

        # Check for README
        readme = self.docs_root / 'README.md'
        if not readme.exists():
            score -= 2.0
            issues.append("Missing README.md")

        # Check for subdirectory navigation files
        subdirs = [d for d in self.docs_root.iterdir() if d.is_dir() and not d.name.startswith('.')]
        subdirs_with_nav = 0

        for subdir in subdirs:
            nav_files = list(subdir.glob("*navigation*.md")) + list(subdir.glob("README.md"))
            if nav_files:
                subdirs_with_nav += 1

        if subdirs:
            subdir_nav_rate = (subdirs_with_nav / len(subdirs)) * 100
            if subdir_nav_rate < 80:
                penalty = (100 - subdir_nav_rate) / 100 * 2.0
                score -= penalty
                issues.append(f"Only {subdir_nav_rate:.0f}% of subdirectories have navigation files")

        self.results['issues'].extend(issues)
        self.results['metrics']['subdirectories_with_navigation'] = f"{subdirs_with_nav}/{len(subdirs)}"

        return max(0.0, score)

    def analyze_redundancy(self) -> float:
        """
        Detect duplicate or highly similar files.

        Returns:
            Score from 0.0 to 10.0
        """
        score = 10.0
        issues = []

        # Check for duplicate filenames in different directories
        file_names = defaultdict(list)
        for file in self.docs_root.rglob("*.md"):
            file_names[file.name].append(file)

        duplicates = {name: paths for name, paths in file_names.items() if len(paths) > 1}

        if duplicates:
            penalty = min(3.0, len(duplicates) * 0.5)
            score -= penalty

            for name, paths in list(duplicates.items())[:3]:  # Show first 3
                rel_paths = [str(p.relative_to(self.docs_root)) for p in paths]
                issues.append(f"Duplicate filename '{name}': {', '.join(rel_paths)}")

            self.results['recommendations'].append(
                "Run detect_redundancy.py to identify and consolidate duplicate content"
            )

        self.results['metrics']['duplicate_filenames'] = len(duplicates)

        return max(0.0, score)

    def analyze_cleanliness(self) -> float:
        """
        Check for cache files, temporary files, and artifacts.

        Returns:
            Score from 0.0 to 10.0
        """
        score = 10.0
        issues = []

        # Check for __pycache__ directories
        pycache_dirs = list(self.docs_root.rglob("__pycache__"))
        if pycache_dirs:
            score -= 2.0
            issues.append(f"{len(pycache_dirs)} __pycache__ directories found")

        # Check for temporary files
        temp_patterns = ['*.tmp', '*.temp', '*~', '*.bak', '*.backup']
        temp_files = []
        for pattern in temp_patterns:
            temp_files.extend(self.docs_root.rglob(pattern))

        if temp_files:
            penalty = min(2.0, len(temp_files) * 0.2)
            score -= penalty
            issues.append(f"{len(temp_files)} temporary files found")

        # Check for uncompressed old log files
        log_files = list(self.docs_root.rglob("*.log"))
        large_logs = [f for f in log_files if f.stat().st_size > 100000]  # >100KB

        if large_logs:
            score -= min(2.0, len(large_logs) * 0.5)
            issues.append(f"{len(large_logs)} large uncompressed log files")
            self.results['recommendations'].append("Run compress_logs.py to archive large log files")

        self.results['issues'].extend(issues)
        self.results['metrics']['cache_directories'] = len(pycache_dirs)
        self.results['metrics']['temporary_files'] = len(temp_files)
        self.results['metrics']['large_log_files'] = len(large_logs)

        return max(0.0, score)

    def analyze_automation(self) -> float:
        """
        Check for presence of automation scripts and tooling.

        Returns:
            Score from 0.0 to 10.0
        """
        score = 10.0

        # Expected automation scripts
        expected_scripts = [
            'validate_ascii_headers.py',
            'enforce_naming_conventions.py',
            'detect_redundancy.py',
            'generate_structure_report.py',
            'validate_links.py',
            'compress_logs.py'
        ]

        scripts_dir = self.docs_root.parent.parent / 'scripts'
        existing_scripts = []

        if scripts_dir.exists():
            for script_name in expected_scripts:
                script_paths = list(scripts_dir.rglob(script_name))
                if script_paths:
                    existing_scripts.append(script_name)

        automation_rate = (len(existing_scripts) / len(expected_scripts)) * 100
        score = (automation_rate / 100) * 10

        self.results['metrics']['automation_scripts'] = f"{len(existing_scripts)}/{len(expected_scripts)}"
        self.results['metrics']['automation_coverage'] = f"{automation_rate:.0f}%"

        if automation_rate < 100:
            missing = set(expected_scripts) - set(existing_scripts)
            self.results['recommendations'].append(
                f"Deploy missing automation scripts: {', '.join(missing)}"
            )

        return score

    def generate_report(self) -> Dict:
        """
        Generate comprehensive health report.

        Returns:
            Report dictionary with scores, metrics, and recommendations
        """
        print("=" * 90)
        print("DOCUMENTATION STRUCTURE HEALTH ANALYSIS")
        print("=" * 90)
        print(f"Documentation Root: {self.docs_root}")
        print(f"Analysis Time: {self.results['timestamp']}")
        print("=" * 90)

        # Run all analyses
        components = {
            'Organization': self.analyze_organization(),
            'ASCII Headers': self.analyze_ascii_headers(),
            'Naming Conventions': self.analyze_naming_conventions(),
            'Navigation': self.analyze_navigation(),
            'Redundancy': self.analyze_redundancy(),
            'Cleanliness': self.analyze_cleanliness(),
            'Automation': self.analyze_automation()
        }

        self.results['scores'] = components

        # Calculate overall score
        overall_score = sum(components.values()) / len(components)
        self.results['overall_score'] = round(overall_score, 1)

        # Print component scores
        print("\n📊 COMPONENT SCORES (0-10 scale):")
        for component, score in components.items():
            status = "✅" if score >= 9.0 else "⚠️" if score >= 7.0 else "❌"
            print(f"  {status} {component:20s}: {score:4.1f}/10.0")

        print(f"\n{'=' * 90}")
        print(f"OVERALL HEALTH SCORE: {overall_score:.1f}/10.0")

        # Determine status
        if overall_score >= 9.5:
            status = "EXCELLENT - Production Ready"
        elif overall_score >= 8.0:
            status = "GOOD - Minor improvements needed"
        elif overall_score >= 7.0:
            status = "FAIR - Moderate improvements needed"
        elif overall_score >= 6.0:
            status = "CONDITIONAL - Significant improvements required"
        else:
            status = "POOR - Major restructuring needed"

        print(f"Status: {status}")
        print("=" * 90)

        # Print issues
        if self.results['issues']:
            print("\n⚠️  ISSUES DETECTED:")
            for i, issue in enumerate(self.results['issues'][:10], 1):  # Show first 10
                print(f"  {i}. {issue}")

            if len(self.results['issues']) > 10:
                print(f"  ... and {len(self.results['issues']) - 10} more issues")

        # Print recommendations
        if self.results['recommendations']:
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(self.results['recommendations'], 1):
                print(f"  {i}. {rec}")

        print("\n" + "=" * 90)

        return self.results


def main():
    """Main entry point for structure health analysis."""
    parser = argparse.ArgumentParser(
        description="Generate documentation structure health report"
    )
    parser.add_argument(
        '--root',
        type=Path,
        required=True,
        help='Documentation root directory'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Save report to JSON file'
    )

    args = parser.parse_args()

    analyzer = DocumentationHealthAnalyzer(args.root)
    report = analyzer.generate_report()

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")

    # Exit code based on health score
    if report['overall_score'] >= 9.0:
        return 0
    elif report['overall_score'] >= 7.0:
        return 1
    else:
        return 2


if __name__ == '__main__':
    import sys
    sys.exit(main())