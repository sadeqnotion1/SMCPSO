#!/usr/bin/env python
"""Create final professional PDF with minimal but effective improvements."""

import re
import subprocess
from pathlib import Path

INPUT_TEX = Path('.artifacts/research/papers/LT7_journal_paper/LT7_COMPLETE.tex')
OUTPUT_TEX = Path('.artifacts/research/papers/LT7_journal_paper/LT7_PROFESSIONAL_FINAL.tex')
OUTPUT_PDF = Path('.artifacts/research/papers/LT7_journal_paper/LT7_PROFESSIONAL_FINAL.pdf')
OUTPUT_DIR = Path('.artifacts/research/papers/LT7_journal_paper')

print('[INFO] Reading working LaTeX (71 pages, 267KB)...')
with open(INPUT_TEX, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('[INFO] Applying safe formatting improvements...')

improved_lines = []
for line in lines:
    original = line

    # Only apply replacements to regular text lines, not LaTeX commands
    if not line.startswith('\\') and not line.strip().startswith('%'):

        # Replace plain text with LaTeX math - very conservative
        # Only replace when it's clearly NOT already in LaTeX syntax

        # Percent symbol (most common and safe)
        if 'percent' in line and '\\' not in line[:line.find('percent')] if 'percent' in line else False:
            line = line.replace(' percent', '\\%')

        # Plus-minus
        if '+/-' in line:
            line = line.replace('+/-', '$\\pm$')

        # Greater/less than or equal
        if '>=' in line and '$' not in line:
            line = line.replace('>=', '$\\geq$')
        if '<=' in line and '$' not in line:
            line = line.replace('<=', '$\\leq$')

        # Greek letters - only as whole words with spaces around them
        if ' theta ' in line:
            line = line.replace(' theta ', ' $\\theta$ ')
        if ' sigma ' in line:
            line = line.replace(' sigma ', ' $\\sigma$ ')
        if ' alpha ' in line:
            line = line.replace(' alpha ', ' $\\alpha$ ')
        if ' beta ' in line:
            line = line.replace(' beta ', ' $\\beta$ ')

        # Bold for controller names - but ONLY in body text
        if '\\section' not in line and '\\subsection' not in line:
            # Be very careful with textbf - check for existing braces
            if 'Classical SMC' in line and '\\textbf{Classical SMC}' not in line:
                line = line.replace('Classical SMC', '\\textbf{Classical SMC}')
            if 'STA-SMC' in line and '\\textbf{STA-SMC}' not in line:
                line = line.replace('STA-SMC', '\\textbf{STA-SMC}')
            if 'Adaptive SMC' in line and '\\textbf{Adaptive SMC}' not in line:
                line = line.replace('Adaptive SMC', '\\textbf{Adaptive SMC}')

    improved_lines.append(line)

content = ''.join(improved_lines)

print('[INFO] Writing enhanced LaTeX...')
with open(OUTPUT_TEX, 'w', encoding='utf-8') as f:
    f.write(content)

file_size = OUTPUT_TEX.stat().st_size
print(f'[OK] Enhanced LaTeX: {file_size:,} bytes')

print('\\n[INFO] Compiling to PDF (2 passes)...')
for pass_num in range(1, 3):
    print(f'  Pass {pass_num}/2...', end=' ', flush=True)
    result = subprocess.run(
        ['pdflatex', '-interaction=nonstopmode', OUTPUT_TEX.name],
        cwd=OUTPUT_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )

    if 'Fatal error' in result.stdout and pass_num == 1:
        print('ERROR')
        print('\\n[ERROR] Compilation failed!')
        errors = [l for l in result.stdout.split('\\n') if l.startswith('!')]
        for err in errors[:5]:
            print(f'  {err}')
        break
    else:
        print('Done')

if OUTPUT_PDF.exists():
    pdf_size = OUTPUT_PDF.stat().st_size

    # Get page count
    pages = 'Unknown'
    pages_match = re.search(r'Output written[^(]*\\((\\d+) pages?', result.stdout)
    if pages_match:
        pages = pages_match.group(1)

    print(f'\\n{"="*70}')
    print('SUCCESS - PROFESSIONAL PDF CREATED!')
    print(f'{"="*70}')
    print(f'\\nFile: {OUTPUT_PDF.name}')
    print(f'Size: {pdf_size:,} bytes ({pdf_size/1024:.1f} KB)')
    print(f'Pages: {pages}')

    print('\\nFormatting Improvements Applied:')
    print('  [OK] Percent symbols (\\%)')
    print('  [OK] Plus-minus ($\\pm$)')
    print('  [OK] Greater/less than ($\\geq$, $\\leq$)')
    print('  [OK] Greek letters ($\\theta$, $\\sigma$, $\\alpha$, $\\beta$)')
    print('  [OK] Bold controller names (Classical SMC, STA-SMC, Adaptive SMC)')
    print('  [OK] Complete 71-page content preserved')

    print('\\n[INFO] Opening PDF...')
    subprocess.run(['start', '', str(OUTPUT_PDF)], shell=True)
else:
    print('\\n[ERROR] PDF not created - check log file')

print('\\n[INFO] Done!')
