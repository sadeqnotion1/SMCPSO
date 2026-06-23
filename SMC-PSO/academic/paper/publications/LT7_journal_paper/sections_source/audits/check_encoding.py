#!/usr/bin/env python
"""
UTF-8 Encoding Verification Script
Scans section files for Unicode symbols and verifies correct encoding
"""

import os
from pathlib import Path
from collections import defaultdict

# Symbols to check
UNICODE_SYMBOLS = {
    '±': r'$\pm$',
    'β': r'$\beta$',
    'θ': r'$\theta$',
    '≈': r'$\approx$',
    '≥': r'$\geq$',
    '≤': r'$\leq$',
    '→': r'$\to$',
    '×': r'$\times$',
    '°': r'$^\circ$',
    'σ': r'$\sigma$',
    'λ': r'$\lambda$',
    'γ': r'$\gamma$',
    'ε': r'$\epsilon$',
    'α': r'$\alpha$',
    '∈': r'$\in$',
    '∀': r'$\forall$',
    '∃': r'$\exists$',
    '∞': r'$\infty$',
    '∑': r'$\sum$',
    '∏': r'$\prod$',
    '√': r'$\sqrt{}$',
    '∫': r'$\int$',
    '∂': r'$\partial$',
    '∇': r'$\nabla$',
    '∆': r'$\Delta$',
    'Δ': r'$\Delta$',
}

def check_file_encoding(filepath):
    """Check file for encoding issues and Unicode symbols"""
    results = {
        'encoding_ok': True,
        'symbols_found': defaultdict(int),
        'mojibake_patterns': [],
        'line_count': 0
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                results['line_count'] += 1

                # Check for Unicode symbols
                for symbol in UNICODE_SYMBOLS:
                    if symbol in line:
                        results['symbols_found'][symbol] += 1

                # Check for common mojibake patterns
                mojibake = ['Ã', 'â€', 'Â±', 'Î²', 'Ã—']
                for pattern in mojibake:
                    if pattern in line:
                        results['mojibake_patterns'].append((line_num, pattern, line.strip()[:80]))

    except UnicodeDecodeError as e:
        results['encoding_ok'] = False
        results['error'] = str(e)

    return results

def main():
    sections_dir = Path(__file__).parent.parent
    modified_files = [
        'Section_03_Controller_Design.md',
        'Section_04_Lyapunov_Stability.md',
        'Section_05_PSO_Methodology.md',
        'Section_07_Performance_Results.md',
        'Section_08_Robustness_Analysis.md',
        'Section_10_Conclusion.md',
    ]

    output_file = Path(__file__).parent / 'encoding_report.txt'

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("UTF-8 ENCODING VERIFICATION REPORT\n")
        out.write("="*80 + "\n\n")

        all_ok = True
        total_symbols = defaultdict(int)

        for filename in modified_files:
            filepath = sections_dir / filename
            out.write(f"\n{filename}\n")
            out.write("-"*80 + "\n")

            results = check_file_encoding(filepath)

            # Encoding status
            if results['encoding_ok']:
                out.write("[OK] File is valid UTF-8\n")
            else:
                out.write(f"[ERROR] Encoding error: {results.get('error')}\n")
                all_ok = False

            out.write(f"Lines: {results['line_count']}\n")

            # Mojibake check
            if results['mojibake_patterns']:
                out.write(f"\n[WARNING] Potential mojibake detected:\n")
                for line_num, pattern, context in results['mojibake_patterns']:
                    out.write(f"  Line {line_num}: '{pattern}' in '{context}'\n")
                all_ok = False
            else:
                out.write("[OK] No mojibake patterns detected\n")

            # Unicode symbols
            if results['symbols_found']:
                out.write(f"\nUnicode symbols found ({sum(results['symbols_found'].values())} total):\n")
                for symbol, count in sorted(results['symbols_found'].items(), key=lambda x: -x[1]):
                    latex_cmd = UNICODE_SYMBOLS.get(symbol, '???')
                    out.write(f"  {symbol} : {count:4d} occurrences -> LaTeX: {latex_cmd}\n")
                    total_symbols[symbol] += count
            else:
                out.write("\n[INFO] No Unicode symbols detected\n")

        # Summary
        out.write("\n" + "="*80 + "\n")
        out.write("SUMMARY\n")
        out.write("="*80 + "\n\n")

        if all_ok:
            out.write("[OK] All files passed encoding validation\n")
        else:
            out.write("[ERROR] Some files have encoding issues\n")

        out.write(f"\nTotal Unicode symbols across all files: {sum(total_symbols.values())}\n\n")

        if total_symbols:
            out.write("Symbol distribution:\n")
            for symbol, count in sorted(total_symbols.items(), key=lambda x: -x[1])[:20]:
                latex_cmd = UNICODE_SYMBOLS.get(symbol, '???')
                out.write(f"  {symbol} : {count:5d} -> {latex_cmd}\n")

        out.write("\n" + "="*80 + "\n")
        out.write("RECOMMENDATIONS FOR LaTeX CONVERSION\n")
        out.write("="*80 + "\n\n")

        out.write("Current status: Unicode symbols in Markdown are VALID for UTF-8\n\n")

        out.write("For LaTeX/PDF conversion:\n")
        out.write("1. Most symbols are already in math mode ($$...$$) and will render correctly\n")
        out.write("2. Verify symbols outside math mode are wrapped in LaTeX commands\n")
        out.write("3. Compile with pdflatex using UTF-8 input encoding:\n")
        out.write("   \\usepackage[utf8]{inputenc}\n")
        out.write("   \\usepackage[T1]{fontenc}\n\n")

        out.write("If any symbols fail to render, use find/replace with LaTeX commands:\n")
        for symbol, latex in sorted(UNICODE_SYMBOLS.items())[:10]:
            out.write(f"  {symbol} -> {latex}\n")

    print(f"[OK] Encoding report generated: {output_file}")
    return 0

if __name__ == '__main__':
    exit(main())
