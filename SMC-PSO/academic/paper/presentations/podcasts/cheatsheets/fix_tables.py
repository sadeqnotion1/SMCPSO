#!/usr/bin/env python
"""
Fix table formatting across all podcast cheatsheet episodes.
Replaces paragraph columns (p{...}) with standard columns (lll)
and removes excessive \midrule usage.
"""

import re
import os
from pathlib import Path

def fix_table_formatting(content):
    """Fix table formatting issues in LaTeX content."""

    # Pattern 1: Replace paragraph columns with standard columns
    # Match tabular environments with p{...} columns
    def replace_tabular_spec(match):
        spec = match.group(1)
        # Count number of columns
        num_cols = spec.count('p{') + spec.count('|')
        if 'p{' in spec:
            num_cols = spec.count('p{')
        # Replace with 'l' columns (left-aligned)
        return '\\begin{tabular}{' + 'l' * num_cols + '}'

    content = re.sub(r'\\begin\{tabular\}\{([^}]*p\{[^}]*)\}',
                     replace_tabular_spec, content)

    # Pattern 2: Fix table structure - replace tableheadcolor + header pattern
    # with toprule + header + midrule
    def fix_table_header(match):
        full_match = match.group(0)
        header_line = match.group(1)

        # Replace tableheadcolor pattern with toprule
        result = full_match.replace('\\tableheadcolor\n', '\\toprule\n')
        return result

    content = re.sub(r'\\tableheadcolor\n(.+?\\\\)\n',
                     fix_table_header, content)

    # Pattern 3: Remove excessive \midrule between data rows
    # Keep only one \midrule after header and before footer
    def clean_midrules(match):
        table_content = match.group(1)
        lines = table_content.split('\n')

        result_lines = []
        in_data_section = False
        midrule_count = 0

        for line in lines:
            stripped = line.strip()

            # If we hit a toprule, we're starting
            if '\\toprule' in stripped:
                result_lines.append(line)
                continue

            # Header line (has textbf)
            if '\\textbf{' in stripped and '\\\\' in stripped:
                result_lines.append(line)
                continue

            # First midrule after header
            if '\\midrule' in stripped and not in_data_section:
                result_lines.append(line)
                in_data_section = True
                midrule_count += 1
                continue

            # Data rows (has & and \\)
            if ' & ' in stripped and '\\\\' in stripped and '\\textbf{' not in stripped:
                result_lines.append(line)
                continue

            # Second midrule (before summary/total row)
            if '\\midrule' in stripped and in_data_section and midrule_count == 1:
                # Check if next non-empty line has \textbf (summary row)
                remaining = '\n'.join(lines[lines.index(line)+1:])
                if '\\textbf{' in remaining.split('\\\\')[0]:
                    result_lines.append(line)
                    midrule_count += 1
                continue

            # Skip excessive midrules
            if '\\midrule' in stripped:
                continue

            # Bottomrule or end of table
            if '\\bottomrule' in stripped or '\\end{tabular}' in stripped:
                # Add bottomrule if missing
                if '\\end{tabular}' in stripped and not any('\\bottomrule' in l for l in result_lines[-3:]):
                    result_lines.append('\\bottomrule')
                result_lines.append(line)
                continue

            result_lines.append(line)

        return '\n'.join(result_lines)

    # Apply to each table
    content = re.sub(r'(\\begin\{tabular\}.*?\\end\{tabular\})',
                     clean_midrules, content, flags=re.DOTALL)

    return content

def process_file(filepath):
    """Process a single LaTeX file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file has tables with issues
    if 'begin{tabular}' not in content:
        return False

    has_issues = ('p{' in content or
                  content.count('\\midrule') > content.count('\\begin{tabular}') * 2)

    if not has_issues:
        return False

    # Fix the formatting
    new_content = fix_table_formatting(content)

    # Only write if content changed
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True

    return False

def main():
    """Process all episode files."""
    base_dir = Path('.')

    phases = [
        'phase1_foundational',
        'phase2_technical',
        'phase3_professional',
        'phase4_appendix'
    ]

    fixed_count = 0
    for phase in phases:
        phase_dir = base_dir / phase
        if not phase_dir.exists():
            continue

        for tex_file in sorted(phase_dir.glob('E*.tex')):
            if process_file(tex_file):
                print(f"Fixed: {tex_file}")
                fixed_count += 1

    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
