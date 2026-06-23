#==========================================================================================\\\
#=================== scripts/docs_organization/detect_redundancy.py ===================\\\
#==========================================================================================\\\

"""Documentation Redundancy Detection Tool.

This script detects duplicate content and redundant sections across
documentation files using content similarity analysis.

Usage:
    python detect_redundancy.py --threshold 0.7     # Detect 70%+ similar content
    python detect_redundancy.py --report            # Generate detailed report
    python detect_redundancy.py --sections          # Analyze section-level duplication

Features:
    - Content similarity detection using difflib
    - Section-level duplication analysis
    - Multi-file redundancy mapping
    - Configurable similarity threshold
"""

import argparse
import difflib
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class RedundancyDetector:
    """Detects redundant content in documentation files."""

    # Excluded directories
    EXCLUDED_DIRS = {
        '.git', '__pycache__', '.pytest_cache', '.venv', 'venv',
        'node_modules', '.tox', '.eggs', 'dist', 'build',
        '.archive', '.build', '.dev_tools', '.tools', '.benchmarks'
    }

    def __init__(
        self,
        project_root: Path,
        similarity_threshold: float = 0.7,
        min_section_length: int = 100
    ):
        """Initialize redundancy detector.

        Args:
            project_root: Absolute path to project root
            similarity_threshold: Minimum similarity ratio (0.0-1.0) to flag
            min_section_length: Minimum section length to analyze (characters)
        """
        self.project_root = project_root
        self.similarity_threshold = similarity_threshold
        self.min_section_length = min_section_length
        self.duplicates: List[Dict] = []

    def extract_sections(self, content: str, filepath: Path) -> List[Dict]:
        """Extract sections from markdown content.

        Args:
            content: File content as string
            filepath: Path to file

        Returns:
            List of section dictionaries with keys: title, content, line_start
        """
        sections = []

        # Split on markdown headers
        header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        matches = list(header_pattern.finditer(content))

        if not matches:
            # No headers, treat entire file as single section
            if len(content) >= self.min_section_length:
                sections.append({
                    'title': filepath.name,
                    'content': content,
                    'line_start': 1,
                    'file': filepath
                })
            return sections

        for i, match in enumerate(matches):
            level = len(match.group(1))
            title = match.group(2).strip()
            start = match.end()

            # Find end of section (next header or end of file)
            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(content)

            section_content = content[start:end].strip()

            # Only include sections meeting minimum length
            if len(section_content) >= self.min_section_length:
                # Calculate line number
                line_start = content[:match.start()].count('\n') + 1

                sections.append({
                    'title': title,
                    'content': section_content,
                    'line_start': line_start,
                    'level': level,
                    'file': filepath
                })

        return sections

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity ratio between two text strings.

        Args:
            text1: First text string
            text2: Second text string

        Returns:
            Similarity ratio between 0.0 and 1.0
        """
        # Normalize whitespace
        text1 = re.sub(r'\s+', ' ', text1.lower().strip())
        text2 = re.sub(r'\s+', ' ', text2.lower().strip())

        # Use difflib for similarity calculation
        return difflib.SequenceMatcher(None, text1, text2).ratio()

    def find_file_duplicates(
        self,
        files: List[Path]
    ) -> List[Tuple[Path, Path, float]]:
        """Find duplicate content between entire files.

        Args:
            files: List of file paths to compare

        Returns:
            List of tuples (file1, file2, similarity_ratio)
        """
        duplicates = []

        # Read all file contents
        file_contents = {}
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    file_contents[filepath] = f.read()
            except Exception as e:
                print(f"Warning: Could not read {filepath}: {e}")
                continue

        # Compare all pairs
        file_list = list(file_contents.keys())
        for i in range(len(file_list)):
            for j in range(i + 1, len(file_list)):
                file1, file2 = file_list[i], file_list[j]
                content1, content2 = file_contents[file1], file_contents[file2]

                similarity = self.calculate_similarity(content1, content2)

                if similarity >= self.similarity_threshold:
                    duplicates.append((file1, file2, similarity))

        return sorted(duplicates, key=lambda x: x[2], reverse=True)

    def find_section_duplicates(self, files: List[Path]) -> List[Dict]:
        """Find duplicate content at section level.

        Args:
            files: List of file paths to analyze

        Returns:
            List of duplicate section dictionaries
        """
        duplicates = []

        # Extract all sections
        all_sections = []
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                sections = self.extract_sections(content, filepath)
                all_sections.extend(sections)
            except Exception as e:
                print(f"Warning: Could not process {filepath}: {e}")
                continue

        # Compare all section pairs
        for i in range(len(all_sections)):
            for j in range(i + 1, len(all_sections)):
                section1, section2 = all_sections[i], all_sections[j]

                # Skip if same file
                if section1['file'] == section2['file']:
                    continue

                similarity = self.calculate_similarity(
                    section1['content'],
                    section2['content']
                )

                if similarity >= self.similarity_threshold:
                    duplicates.append({
                        'section1': section1,
                        'section2': section2,
                        'similarity': similarity
                    })

        return sorted(duplicates, key=lambda x: x['similarity'], reverse=True)

    def scan_documentation(
        self,
        extensions: List[str] = ['.md', '.rst', '.txt']
    ) -> Tuple[List, List]:
        """Scan documentation for redundancy.

        Args:
            extensions: List of documentation file extensions

        Returns:
            Tuple of (file_duplicates, section_duplicates)
        """
        # Find all documentation files
        doc_files = []
        for ext in extensions:
            for filepath in self.project_root.rglob(f"*{ext}"):
                if any(excluded in filepath.parts for excluded in self.EXCLUDED_DIRS):
                    continue
                doc_files.append(filepath)

        print(f"Found {len(doc_files)} documentation files")

        # Find file-level duplicates
        print("Analyzing file-level redundancy...")
        file_duplicates = self.find_file_duplicates(doc_files)

        # Find section-level duplicates
        print("Analyzing section-level redundancy...")
        section_duplicates = self.find_section_duplicates(doc_files)

        return file_duplicates, section_duplicates

    def generate_report(
        self,
        file_duplicates: List,
        section_duplicates: List,
        output_path: Optional[Path] = None
    ) -> str:
        """Generate redundancy report.

        Args:
            file_duplicates: List of file-level duplicates
            section_duplicates: List of section-level duplicates
            output_path: Optional path to save report

        Returns:
            Report as formatted string
        """
        # Calculate redundancy percentage
        total_comparisons = 0
        if file_duplicates:
            n_files = len(set([f for dup in file_duplicates for f in dup[:2]]))
            total_comparisons = n_files * (n_files - 1) // 2

        redundancy_rate = (
            (len(file_duplicates) / total_comparisons * 100)
            if total_comparisons > 0 else 0
        )

        report_lines = [
            "=" * 90,
            "DOCUMENTATION REDUNDANCY REPORT",
            "=" * 90,
            f"\nSimilarity Threshold: {self.similarity_threshold * 100:.0f}%",
            f"Minimum Section Length: {self.min_section_length} characters",
            f"\nFile-Level Duplicates Found: {len(file_duplicates)}",
            f"Section-Level Duplicates Found: {len(section_duplicates)}",
            f"Redundancy Rate: {redundancy_rate:.1f}%",
        ]

        # File-level duplicates
        if file_duplicates:
            report_lines.extend([
                "\n" + "=" * 90,
                "FILE-LEVEL DUPLICATES:",
                "=" * 90,
            ])

            for file1, file2, similarity in file_duplicates:
                rel1 = file1.relative_to(self.project_root)
                rel2 = file2.relative_to(self.project_root)
                report_lines.append(f"\nSimilarity: {similarity * 100:.1f}%")
                report_lines.append(f"  File 1: {rel1}")
                report_lines.append(f"  File 2: {rel2}")

        # Section-level duplicates
        if section_duplicates:
            report_lines.extend([
                "\n" + "=" * 90,
                "SECTION-LEVEL DUPLICATES:",
                "=" * 90,
            ])

            for dup in section_duplicates[:20]:  # Limit to top 20
                s1, s2 = dup['section1'], dup['section2']
                similarity = dup['similarity']

                rel1 = s1['file'].relative_to(self.project_root)
                rel2 = s2['file'].relative_to(self.project_root)

                report_lines.append(f"\nSimilarity: {similarity * 100:.1f}%")
                report_lines.append(f"  Section 1: {s1['title']} ({rel1}, line {s1['line_start']})")
                report_lines.append(f"  Section 2: {s2['title']} ({rel2}, line {s2['line_start']})")

        report = "\n".join(report_lines)

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)

        return report


def main() -> None:
    """Main entry point for redundancy detection tool."""
    parser = argparse.ArgumentParser(
        description="Detect redundant content in documentation files"
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.7,
        help='Similarity threshold (0.0-1.0, default: 0.7)'
    )
    parser.add_argument(
        '--min-length',
        type=int,
        default=100,
        help='Minimum section length in characters (default: 100)'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate detailed report'
    )
    parser.add_argument(
        '--sections',
        action='store_true',
        help='Analyze section-level duplication'
    )
    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['.md', '.rst', '.txt'],
        help='File extensions to analyze (default: .md .rst .txt)'
    )
    parser.add_argument(
        '--root',
        type=str,
        default='.',
        help='Project root directory (default: current directory)'
    )

    args = parser.parse_args()

    # Validate threshold
    if not 0.0 <= args.threshold <= 1.0:
        print("Error: Threshold must be between 0.0 and 1.0")
        return

    # Resolve project root
    project_root = Path(args.root).resolve()

    print(f"Scanning project: {project_root}")
    print(f"Similarity threshold: {args.threshold * 100:.0f}%\n")

    # Create detector and scan
    detector = RedundancyDetector(
        project_root,
        similarity_threshold=args.threshold,
        min_section_length=args.min_length
    )

    file_dups, section_dups = detector.scan_documentation(args.extensions)

    print(f"\nFound {len(file_dups)} file-level duplicates")
    print(f"Found {len(section_dups)} section-level duplicates")

    # Generate report
    if args.report:
        report_path = project_root / 'artifacts' / 'redundancy_report.txt'
        report = detector.generate_report(file_dups, section_dups, report_path)
        print(f"\nReport saved to: {report_path}\n")
        print(report)
    else:
        # Print summary
        if file_dups:
            print("\nTop File-Level Duplicates:")
            for file1, file2, similarity in file_dups[:5]:
                rel1 = file1.relative_to(project_root)
                rel2 = file2.relative_to(project_root)
                print(f"  {similarity * 100:.1f}%: {rel1} <-> {rel2}")

        if args.sections and section_dups:
            print("\nTop Section-Level Duplicates:")
            for dup in section_dups[:5]:
                s1, s2 = dup['section1'], dup['section2']
                similarity = dup['similarity']
                rel1 = s1['file'].relative_to(project_root)
                rel2 = s2['file'].relative_to(project_root)
                print(f"  {similarity * 100:.1f}%: {s1['title']} ({rel1}) <-> {s2['title']} ({rel2})")


if __name__ == '__main__':
    main()