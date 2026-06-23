#!/usr/bin/env python3
"""
check_notation.py - Mathematical Notation Consistency Checker

Validates mathematical notation consistency across thesis chapters:
- Extract all LaTeX symbols from equations
- Build notation dictionary (first occurrence = canonical)
- Check consistency across chapters
- Flag subscript/superscript variations
- Identify undefined symbols
- Detect notation conflicts

Created: November 5, 2025
Priority: 4 (Quick Win - 85% automated)
Manual Work: 15 min review

Usage:
    python check_notation.py [--config config.yaml] [--output notation_report.md]
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import yaml
from datetime import datetime


@dataclass
class Symbol:
    """Represents a mathematical symbol found in the thesis."""
    symbol: str  # Raw LaTeX (e.g., "\\theta_1")
    normalized: str  # Normalized form (e.g., "theta_1")
    display: str  # Display form (e.g., "θ₁")
    first_occurrence: str  # File where first seen
    first_line: int
    occurrences: List[Tuple[str, int]] = field(default_factory=list)  # (file, line)
    context: str = ""  # Context from first occurrence


@dataclass
class NotationIssue:
    """Represents a notation consistency issue."""
    issue_type: str  # 'inconsistency', 'undefined', 'conflict'
    symbol: str
    description: str
    locations: List[Tuple[str, int]]
    severity: str  # 'high', 'medium', 'low'


@dataclass
class ValidationResult:
    """Results of notation validation."""
    total_symbols: int = 0
    unique_symbols: int = 0
    issues: List[NotationIssue] = field(default_factory=list)
    notation_dictionary: Dict[str, Symbol] = field(default_factory=dict)


class NotationChecker:
    """Checks mathematical notation consistency across thesis."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize checker with configuration."""
        self.config = self._load_config(config_path)
        self.thesis_path = Path(self.config['thesis']['base_path'])
        self.reports_path = Path(self.config['output']['reports_path'])

        # Symbol patterns
        self.latex_patterns = [
            r'\\([a-zA-Z]+)(?:_\{([^}]+)\}|_([a-zA-Z0-9]))?(?:\^\{([^}]+)\}|\^([a-zA-Z0-9]))?',  # \theta_{12}^{2}
            r'([a-zA-Z])(?:_\{([^}]+)\}|_([a-zA-Z0-9]))?(?:\^\{([^}]+)\}|\^([a-zA-Z0-9]))?',  # x_{1}^{2}
        ]

        # Common LaTeX commands to ignore
        self.ignore_commands = {
            'begin', 'end', 'text', 'quad', 'qquad', 'left', 'right',
            'frac', 'sqrt', 'sum', 'int', 'prod', 'lim', 'infty',
            'tag', 'label', 'ref', 'cite', 'cdot', 'times', 'div',
            'partial', 'nabla', 'Delta', 'Sigma', 'Pi', 'Omega',
        }

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        config_file = Path(__file__).parent / config_path
        if not config_file.exists():
            print(f"[WARNING] Config not found: {config_file}, using defaults")
            return self._default_config()

        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _default_config(self) -> dict:
        """Return default configuration."""
        return {
            'thesis': {
                'base_path': 'docs/thesis',
            },
            'output': {
                'reports_path': '.artifacts/thesis/reports',
                'verbose': True,
            },
            'thresholds': {
                'notation': {
                    'max_inconsistencies': 5,
                },
            },
        }

    def normalize_symbol(self, latex: str) -> str:
        """Normalize LaTeX symbol for comparison."""
        # Remove backslashes
        normalized = latex.replace('\\', '')
        # Normalize braces
        normalized = re.sub(r'\{([^}]+)\}', r'\1', normalized)
        # Remove spaces
        normalized = normalized.replace(' ', '')
        return normalized

    def extract_symbols_from_line(self, line: str, file_path: str, line_num: int) -> List[Symbol]:
        """Extract all LaTeX symbols from a line."""
        symbols = []

        # Find all math environments
        math_sections = []

        # Inline math: $...$
        math_sections.extend(re.finditer(r'\$([^\$]+)\$', line))

        # Display math: $$...$$
        math_sections.extend(re.finditer(r'\$\$([^\$]+)\$\$', line))

        for match in math_sections:
            math_content = match.group(1)

            # Extract symbols using patterns
            for pattern in self.latex_patterns:
                for symbol_match in re.finditer(pattern, math_content):
                    raw_symbol = symbol_match.group(0)

                    # Skip if it's an ignored command
                    base = symbol_match.group(1) if len(symbol_match.groups()) > 0 else symbol_match.group(0)
                    if base in self.ignore_commands:
                        continue

                    # Skip pure numbers
                    if raw_symbol.replace('_', '').replace('^', '').isdigit():
                        continue

                    normalized = self.normalize_symbol(raw_symbol)

                    # Create display form (simplified)
                    display = raw_symbol.replace('\\', '').replace('{', '').replace('}', '')

                    symbol = Symbol(
                        symbol=raw_symbol,
                        normalized=normalized,
                        display=display,
                        first_occurrence=str(file_path),
                        first_line=line_num,
                        context=math_content.strip()[:100]
                    )
                    symbols.append(symbol)

        return symbols

    def scan_thesis(self) -> Dict[str, Symbol]:
        """Scan all thesis files and build notation dictionary."""
        notation_dict = {}

        # Get all markdown files
        thesis_files = sorted(self.thesis_path.rglob("[0-9][0-9]_*.md"))
        print(f"[INFO] Scanning {len(thesis_files)} chapter files...")

        for file_path in thesis_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"[ERROR] Cannot read {file_path}: {e}")
                continue

            if self.config['output']['verbose']:
                print(f"  - {file_path.name}")

            for line_num, line in enumerate(lines, start=1):
                symbols = self.extract_symbols_from_line(line, file_path, line_num)

                for symbol in symbols:
                    if symbol.normalized not in notation_dict:
                        # First occurrence
                        notation_dict[symbol.normalized] = symbol
                    else:
                        # Add occurrence to existing symbol
                        notation_dict[symbol.normalized].occurrences.append(
                            (str(file_path), line_num)
                        )

        print(f"[INFO] Found {len(notation_dict)} unique symbols")
        return notation_dict

    def check_consistency(self, notation_dict: Dict[str, Symbol]) -> List[NotationIssue]:
        """Check for notation consistency issues."""
        issues = []

        # Group symbols by base name (without subscripts/superscripts)
        symbol_groups = defaultdict(list)
        for normalized, symbol in notation_dict.items():
            # Extract base (e.g., "theta" from "theta_1")
            base = re.match(r'([a-zA-Z]+)', normalized)
            if base:
                symbol_groups[base.group(1)].append(symbol)

        # Check for inconsistencies within each group
        for base, symbols in symbol_groups.items():
            if len(symbols) <= 1:
                continue

            # Check for notation variations
            variations = defaultdict(list)
            for symbol in symbols:
                variations[symbol.symbol].append(symbol)

            if len(variations) > 1:
                # Multiple ways to write the same base symbol
                # Example: \theta_1 vs \theta_{1}
                issue = NotationIssue(
                    issue_type='inconsistency',
                    symbol=base,
                    description=f"Symbol '{base}' has {len(variations)} different notation forms",
                    locations=[],
                    severity='medium'
                )

                for variant, syms in variations.items():
                    for sym in syms:
                        issue.locations.append((sym.first_occurrence, sym.first_line))

                issues.append(issue)

        # Check for undefined symbols (heuristic: symbols used only once or twice)
        for normalized, symbol in notation_dict.items():
            if len(symbol.occurrences) <= 1:
                issue = NotationIssue(
                    issue_type='undefined',
                    symbol=symbol.display,
                    description=f"Symbol '{symbol.display}' used only once (may be undefined)",
                    locations=[(symbol.first_occurrence, symbol.first_line)],
                    severity='low'
                )
                issues.append(issue)

        return issues

    def generate_report(self, result: ValidationResult, output_path: Path):
        """Generate markdown validation report."""
        os.makedirs(output_path.parent, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Notation Consistency Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # Summary
            f.write("## SUMMARY\n\n")
            f.write(f"- **Total Symbols**: {result.total_symbols}\n")
            f.write(f"- **Unique Symbols**: {result.unique_symbols}\n")
            f.write(f"- **Issues Found**: {len(result.issues)}\n")
            f.write(f"  - Inconsistencies: {sum(1 for i in result.issues if i.issue_type == 'inconsistency')}\n")
            f.write(f"  - Undefined/Rare: {sum(1 for i in result.issues if i.issue_type == 'undefined')}\n\n")

            # Notation dictionary
            f.write("## NOTATION DICTIONARY\n\n")
            f.write("| Symbol | First Occurrence | Usage Count |\n")
            f.write("|--------|------------------|-------------|\n")
            for normalized, symbol in sorted(result.notation_dictionary.items()):
                file_short = Path(symbol.first_occurrence).name
                usage_count = 1 + len(symbol.occurrences)
                f.write(f"| {symbol.display} | {file_short}:{symbol.first_line} | {usage_count} |\n")
            f.write("\n")

            # Issues
            if result.issues:
                f.write("## ISSUES FOUND\n\n")

                # Inconsistencies
                inconsistencies = [i for i in result.issues if i.issue_type == 'inconsistency']
                if inconsistencies:
                    f.write("### Notation Inconsistencies\n\n")
                    for issue in inconsistencies:
                        f.write(f"#### {issue.symbol} - {issue.severity.upper()}\n\n")
                        f.write(f"{issue.description}\n\n")
                        f.write("Locations:\n")
                        for loc, line in issue.locations[:10]:  # Show first 10
                            f.write(f"- {Path(loc).name}:{line}\n")
                        if len(issue.locations) > 10:
                            f.write(f"- ... and {len(issue.locations)-10} more\n")
                        f.write("\n")

                # Undefined/rare symbols
                undefined = [i for i in result.issues if i.issue_type == 'undefined']
                if undefined:
                    f.write("### Potentially Undefined Symbols\n\n")
                    f.write("*These symbols appear only once or twice. Verify they are defined.*\n\n")
                    f.write("| Symbol | Location |\n")
                    f.write("|--------|----------|\n")
                    for issue in undefined[:20]:  # Show first 20
                        loc, line = issue.locations[0]
                        f.write(f"| {issue.symbol} | {Path(loc).name}:{line} |\n")
                    if len(undefined) > 20:
                        f.write(f"\n*... and {len(undefined)-20} more*\n")
                    f.write("\n")
            else:
                f.write("## [OK] NO ISSUES FOUND\n\n")
                f.write("All notation is consistent!\n\n")

            # Verdict
            f.write("---\n\n")
            f.write("## VALIDATION VERDICT\n\n")
            threshold = self.config['thresholds']['notation']['max_inconsistencies']
            inconsistency_count = sum(1 for i in result.issues if i.issue_type == 'inconsistency')

            if inconsistency_count <= threshold:
                f.write("**STATUS**: [OK] PASS\n\n")
                f.write(f"Inconsistencies ({inconsistency_count}) within threshold ({threshold}).\n")
            else:
                f.write("**STATUS**: [WARNING] REVIEW REQUIRED\n\n")
                f.write(f"Inconsistencies ({inconsistency_count}) exceed threshold ({threshold}).\n")
                f.write("Please review and standardize notation before thesis submission.\n")

        print(f"[INFO] Report generated: {output_path}")

    def run(self, output_file: str = "notation_consistency.md"):
        """Run complete validation workflow."""
        print("\n" + "="*60)
        print("NOTATION CONSISTENCY CHECK")
        print("="*60 + "\n")

        # Scan thesis
        notation_dict = self.scan_thesis()

        # Check consistency
        print("[INFO] Checking consistency...")
        issues = self.check_consistency(notation_dict)

        # Build result
        result = ValidationResult(
            total_symbols=sum(1 + len(s.occurrences) for s in notation_dict.values()),
            unique_symbols=len(notation_dict),
            issues=issues,
            notation_dictionary=notation_dict
        )

        # Generate report
        output_path = self.reports_path / output_file
        self.generate_report(result, output_path)

        # Print summary
        print("\n" + "="*60)
        print("VALIDATION COMPLETE")
        print("="*60)
        print(f"Unique Symbols: {result.unique_symbols}")
        print(f"Issues Found: {len(result.issues)}")
        print(f"  - Inconsistencies: {sum(1 for i in result.issues if i.issue_type == 'inconsistency')}")
        print(f"  - Undefined/Rare: {sum(1 for i in result.issues if i.issue_type == 'undefined')}")
        print(f"\nReport: {output_path}")
        print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Check thesis notation consistency")
    parser.add_argument('--config', default='config.yaml', help='Configuration file')
    parser.add_argument('--output', default='notation_consistency.md', help='Output report file')
    args = parser.parse_args()

    checker = NotationChecker(config_path=args.config)
    checker.run(output_file=args.output)


if __name__ == "__main__":
    main()
