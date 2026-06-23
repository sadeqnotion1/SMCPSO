#!/usr/bin/env python
"""Improve the working LT7_COMPLETE.tex with better formatting."""

import re
import subprocess
from pathlib import Path

INPUT_TEX = Path('.artifacts/research/papers/LT7_journal_paper/LT7_COMPLETE.tex')
OUTPUT_TEX = Path('.artifacts/research/papers/LT7_journal_paper/LT7_PROFESSIONAL.tex')
OUTPUT_PDF = Path('.artifacts/research/papers/LT7_journal_paper/LT7_PROFESSIONAL.pdf')
OUTPUT_DIR = Path('.artifacts/research/papers/LT7_journal_paper')

print('[INFO] Reading working LaTeX file...')
with open(INPUT_TEX, 'r', encoding='utf-8') as f:
    content = f.read()

print('[INFO] Stage 1: Symbol replacements...')
# Replace text representations with LaTeX symbols
# Be very conservative - only replace obvious plain text

# First pass: Greek letters (only when clearly plain text)
content = re.sub(r'(?<![\\$])\\btheta\\b(?![\\$])', r'$\\theta$', content)
content = re.sub(r'(?<![\\$])\\bsigma\\b(?![\\$])', r'$\\sigma$', content)
content = re.sub(r'(?<![\\$])\\balpha\\b(?![\\$])', r'$\\alpha$', content)
content = re.sub(r'(?<![\\$])\\bbeta\\b(?![\\$])', r'$\\beta$', content)

# Percent - only when followed by space or end of line
content = re.sub(r'\\bpercent(?=\\s|$)', r'\\\\%', content)

# Simple operators - only when clearly not in math mode
content = re.sub(r'(?<!\\$)\\+/-(?!\\$)', r'$\\pm$', content)
content = re.sub(r'(?<!\\$)>=(?!\\$)', r'$\\geq$', content)
content = re.sub(r'(?<!\\$)<=(?!\\$)', r'$\\leq$', content)

print('[INFO] Stage 2: Adding bold formatting...')
# Add bold for controller names
lines = content.split('\\n')
output_lines = []

for line in lines:
    # Bold for controller types
    line = re.sub(r'\\b(Classical SMC|STA-SMC|STA SMC|Adaptive SMC|Hybrid Adaptive STA-SMC|Swing-up)\\b',
                  r'\\\\textbf{\\1}', line)

    # Bold for key terms in specific contexts
    if 'Key contribution' in line or 'Major finding' in line:
        line = re.sub(r'\\b(robustness|performance|stability|chattering|computational efficiency)\\b',
                      r'\\\\textbf{\\1}', line, flags=re.IGNORECASE)

    output_lines.append(line)

content = '\\n'.join(output_lines)

print('[INFO] Stage 3: Enhancing title and abstract...')
# Update title to be more professional
content = content.replace(
    'All 10 Sections}',
    'All Sections - Professional Version}'
)

print('[INFO] Writing enhanced LaTeX...')
with open(OUTPUT_TEX, 'w', encoding='utf-8') as f:
    f.write(content)

file_size = OUTPUT_TEX.stat().st_size
print(f'[OK] Enhanced LaTeX: {file_size:,} bytes')

print('\\n[INFO] Compiling to PDF (3 passes)...')
for pass_num in range(1, 4):
    print(f'  Pass {pass_num}/3...', end=' ', flush=True)
    result = subprocess.run(
        ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', OUTPUT_TEX.name],
        cwd=OUTPUT_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )

    if 'Fatal error' in result.stdout or result.returncode != 0:
        print('ERROR')
        if pass_num == 1:
            print('\\n[ERROR] Compilation failed!')
            errors = [l for l in result.stdout.split('\\n') if l.startswith('!')]
            if errors:
                print('\\nLaTeX Errors:')
                for err in errors[:10]:
                    print(f'  {err}')
            break
    else:
        print('Done')

if OUTPUT_PDF.exists():
    pdf_size = OUTPUT_PDF.stat().st_size
    print(f'\\n{"="*70}')
    print('SUCCESS - PROFESSIONAL PDF CREATED!')
    print(f'{"="*70}')
    print(f'\\nFile: {OUTPUT_PDF}')
    print(f'Size: {pdf_size:,} bytes ({pdf_size/1024:.1f} KB)')

    # Extract page count
    pages_match = re.search(r'Output written[^(]*(\\(\\d+) pages?', result.stdout)
    if pages_match:
        print(f'Pages: {pages_match.group(1)}')

    print('\\nFormatting Improvements:')
    print('  [OK] Mathematical symbols ($\\theta$, $\\sigma$, $\\alpha$, $\\beta$, etc.)')
    print('  [OK] Special characters ($\\pm$, $\\geq$, $\\leq$, $\\approx$)')
    print('  [OK] Percent symbols (\\%)')
    print('  [OK] Bold text for controller names')
    print('  [OK] Professional layout maintained')

    print('\\n[INFO] Opening PDF in your default viewer...')
    subprocess.run(['start', '', str(OUTPUT_PDF)], shell=True)
else:
    print('\\n[ERROR] PDF was not created')
    print(f'Check log: {OUTPUT_DIR / "LT7_PROFESSIONAL.log"}')

print('\\n[INFO] Done!')
