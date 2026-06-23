"""LT-7 LaTeX Polishing Script

Fixes remaining issues in auto-generated LaTeX:
1. Converts ```math blocks to proper equation environments
2. Converts markdown tables to LaTeX tabular
3. Adds equation labels where appropriate
4. Fixes formatting issues

Usage:
    python scripts/lt7_polish_latex.py

Input:  benchmarks/LT7_RESEARCH_PAPER.tex
Output: benchmarks/LT7_RESEARCH_PAPER.tex (updated in place)
"""

import re
from pathlib import Path
from typing import List, Tuple

INPUT_TEX = Path(".artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.tex")
BACKUP_TEX = Path(".artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.tex.backup")

def convert_math_blocks(content: str) -> str:
    """Convert ```math blocks to LaTeX equation/align environments."""
    # Pattern: ```math ... ```
    def replace_math_block(match):
        math_content = match.group(1).strip()

        # Check if it uses align syntax (multiple lines with &)
        if '\\begin{aligned}' in math_content or '&' in math_content:
            # Already in aligned environment, just wrap in equation
            if '\\begin{aligned}' not in math_content:
                # Add aligned environment
                math_content = '\\begin{aligned}\n' + math_content + '\n\\end{aligned}'
            return f"\\begin{{equation}}\n{math_content}\n\\end{{equation}}\n"
        else:
            # Single equation
            return f"\\begin{{equation}}\n{math_content}\n\\end{{equation}}\n"

    # Replace ```math ... ``` blocks
    content = re.sub(r'```math\s*\n(.+?)\n```', replace_math_block, content, flags=re.DOTALL)

    return content

def convert_markdown_tables(content: str) -> str:
    """Convert markdown tables to LaTeX tabular format."""
    lines = content.split('\n')
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this looks like a markdown table (has pipe symbols)
        if '|' in line and i + 1 < len(lines) and '|' in lines[i+1]:
            # Check if next line is separator (has dashes)
            if '---' in lines[i+1] or '--|--' in lines[i+1]:
                # Found a markdown table
                table_lines = [line]
                i += 1
                # Skip separator line
                i += 1

                # Collect remaining table rows
                while i < len(lines) and '|' in lines[i] and lines[i].strip():
                    table_lines.append(lines[i])
                    i += 1

                # Convert to LaTeX tabular
                latex_table = markdown_table_to_latex(table_lines)
                result_lines.extend(latex_table.split('\n'))
                continue

        result_lines.append(line)
        i += 1

    return '\n'.join(result_lines)

def markdown_table_to_latex(table_lines: List[str]) -> str:
    """Convert a markdown table to LaTeX tabular."""
    if not table_lines:
        return ""

    # Parse header
    header_cells = [cell.strip() for cell in table_lines[0].split('|') if cell.strip()]

    # Parse body rows
    body_rows = []
    for line in table_lines[1:]:
        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        if cells:
            body_rows.append(cells)

    # Determine column alignment (default to left)
    num_cols = len(header_cells)
    col_spec = 'l' * num_cols

    # Build LaTeX table
    latex = []
    latex.append("\\begin{table}[htbp]")
    latex.append("\\centering")
    latex.append(f"\\begin{{tabular}}{{{col_spec}}}")
    latex.append("\\toprule")

    # Header
    header_row = " & ".join(header_cells) + " \\\\"
    latex.append(header_row)
    latex.append("\\midrule")

    # Body rows
    for row in body_rows:
        # Pad row if needed
        while len(row) < num_cols:
            row.append("")
        row_str = " & ".join(row[:num_cols]) + " \\\\"
        latex.append(row_str)

    latex.append("\\bottomrule")
    latex.append("\\end{tabular}")
    latex.append("\\end{table}")

    return '\n'.join(latex)

def add_equation_labels(content: str) -> str:
    """Add labels to equation environments that don't have them."""
    lines = content.split('\n')
    result = []
    eq_counter = 1
    section = "unknown"

    for i, line in enumerate(lines):
        # Track current section for label naming
        if '\\section{' in line:
            section_match = re.search(r'\\section\{(\d+)\.', line)
            if section_match:
                section = section_match.group(1)

        # Check if this is an equation environment without a label
        if '\\begin{equation}' in line:
            # Check if label exists in next few lines
            has_label = False
            for j in range(i+1, min(i+10, len(lines))):
                if '\\label{' in lines[j]:
                    has_label = True
                    break
                if '\\end{equation}' in lines[j]:
                    break

            result.append(line)

            # Add label if missing
            if not has_label:
                result.append(f"\\label{{eq:{section}_{eq_counter}}}")
                eq_counter += 1
        else:
            result.append(line)

    return '\n'.join(result)

def fix_text_formatting(content: str) -> str:
    """Fix various formatting issues."""
    # Fix escaped underscores in math mode (LaTeX doesn't need them)
    # content = re.sub(r'\$([^$]*)\\_([^$]*)\$', r'$\1_\2$', content)

    # Fix double backslashes in textit/textbf
    content = re.sub(r'\\textit\{\\textit\{(.+?)\}\}', r'\\textit{\1}', content)
    content = re.sub(r'\\textbf\{\\textbf\{(.+?)\}\}', r'\\textbf{\1}', content)

    # Fix common Unicode issues
    content = content.replace('μ', r'$\mu$')
    content = content.replace('–', '--')  # en-dash
    content = content.replace('—', '---')  # em-dash

    return content

def main():
    print("\n" + "="*70)
    print("LT-7 LATEX POLISHING")
    print("="*70 + "\n")

    print(f"[INFO] Reading LaTeX file: {INPUT_TEX}")
    with open(INPUT_TEX, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"[INFO] Creating backup: {BACKUP_TEX}")
    with open(BACKUP_TEX, 'w', encoding='utf-8') as f:
        f.write(content)

    original_length = len(content)

    print("[INFO] Converting ```math blocks to equation environments...")
    content = convert_math_blocks(content)
    math_blocks_converted = content.count('\\begin{equation}')
    print(f"     Found {math_blocks_converted} equation environments")

    print("[INFO] Converting markdown tables to LaTeX tabular...")
    before_tables = content.count('|')
    content = convert_markdown_tables(content)
    after_tables = content.count('|')
    tables_converted = (before_tables - after_tables) // 2  # Rough estimate
    print(f"     Converted approximately {tables_converted} markdown table rows")

    print("[INFO] Adding equation labels...")
    content = add_equation_labels(content)
    labels_added = content.count('\\label{eq:')
    print(f"     Added {labels_added} equation labels")

    print("[INFO] Fixing text formatting issues...")
    content = fix_text_formatting(content)

    print(f"[INFO] Writing polished LaTeX...")
    with open(INPUT_TEX, 'w', encoding='utf-8') as f:
        f.write(content)

    new_length = len(content)
    size_diff = new_length - original_length
    size_diff_pct = (size_diff / original_length * 100) if original_length > 0 else 0

    print(f"\n[OK] LaTeX polishing complete!")
    print(f"     Input:  {original_length:,} characters")
    print(f"     Output: {new_length:,} characters ({size_diff:+,} / {size_diff_pct:+.1f}%)")
    print(f"     Backup: {BACKUP_TEX}")

    print(f"\n[INFO] Polish summary:")
    print(f"     - Equation environments: {math_blocks_converted}")
    print(f"     - Equation labels added: {labels_added}")
    print(f"     - Tables converted: ~{tables_converted}")

    print(f"\n[WARNING] Manual review still needed:")
    print(f"     1. Check equation labels are meaningful")
    print(f"     2. Verify table captions")
    print(f"     3. Review complex math formatting")
    print(f"     4. Add \\caption and \\label to table environments")
    print()

if __name__ == "__main__":
    main()
