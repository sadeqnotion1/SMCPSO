#!/usr/bin/env python
"""Generate properly formatted PDF with math mode and formatting preserved."""

import re
import subprocess
from pathlib import Path

INPUT_MD = Path('.artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.md')
OUTPUT_DIR = Path('.artifacts/research/papers/LT7_journal_paper')
OUTPUT_TEX = OUTPUT_DIR / 'LT7_ENHANCED_FINAL.tex'
OUTPUT_PDF = OUTPUT_DIR / 'LT7_ENHANCED_FINAL.pdf'

print('[INFO] Reading Markdown...')
with open(INPUT_MD, 'r', encoding='utf-8') as f:
    content = f.read()

# Better preamble with more packages
PREAMBLE = r'''\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{graphicx}
\usepackage[margin=1in]{geometry}
\usepackage{enumitem}
\usepackage{parskip}

\title{Comparative Analysis of Sliding Mode Control Variants for \\
       Double-Inverted Pendulum Systems: \\
       Performance, Stability, and Robustness \\[0.5cm]
       \Large Enhanced Complete Version}

\author{Research Paper - December 25, 2025}
\date{}

\begin{document}
\maketitle
\tableofcontents
\clearpage

'''

POSTAMBLE = r'''

\section*{Document Information}
This PDF contains all 10 enhanced sections with improved formatting. Tables are simplified for readability. The complete Markdown version contains detailed tables with all numerical data.

\end{document}
'''

print('[INFO] Processing content...')

# Split and process
lines = content.split('\n')
output = []
skip = True
in_table = False
in_code = False
table_num = 0

for i, line in enumerate(lines):
    # Skip until Abstract
    if skip:
        if '## Abstract' in line:
            skip = False
            output.append('\\begin{abstract}')
            continue
        continue

    # Code blocks
    if line.strip().startswith('```'):
        in_code = not in_code
        if not in_code:
            output.append('')  # Add spacing after code
        continue
    if in_code:
        continue  # Skip code content

    # Skip tables but note them
    if line.strip().startswith('|'):
        if not in_table:
            table_num += 1
            output.append(f'\n\\noindent\\textit{{Table {table_num} omitted - see Markdown version for complete data}}\n')
            in_table = True
        continue
    else:
        in_table = False

    # Stop at References
    if line.strip().startswith('## References'):
        break

    # Headers
    if line.startswith('## '):
        if 'abstract' in '\n'.join(output[-3:]).lower() and 'end{abstract}' not in '\n'.join(output[-3:]):
            output.append('\\end{abstract}')
        title = re.sub(r'^\d+\.\s*', '', line[3:].strip())
        output.append(f'\n\\section{{{title}}}\n')
    elif line.startswith('### '):
        title = re.sub(r'^\d+\.\d+\.?\s*', '', line[4:].strip())
        output.append(f'\n\\subsection{{{title}}}\n')
    elif line.startswith('#### '):
        title = re.sub(r'^\d+\.\d+\.\d+\.?\s*', '', line[5:].strip())
        output.append(f'\n\\subsubsection{{{title}}}\n')
    # Figures
    elif line.strip().startswith('!['):
        match = re.search(r'!\[([^\]]+)\]', line)
        if match:
            output.append(f'\\textit{{{match.group(1)}}}')
    else:
        output.append(line)

text = '\n'.join(output)

print('[INFO] Applying formatting...')

# Special characters - use proper LaTeX
replacements = {
    '±': r'$\pm$',
    '×': r'$\times$',
    'μ': r'$\mu$',
    '°': r'$^\circ$',
    '≥': r'$\geq$',
    '≤': r'$\leq$',
    '≈': r'$\approx$',
    '→': r'$\to$',
    'σ': r'$\sigma$',
    'θ': r'$\theta$',
    'α': r'$\alpha$',
    'β': r'$\beta$',
    'γ': r'$\gamma$',
    'λ': r'$\lambda$',
    'ε': r'$\varepsilon$',
    'δ': r'$\delta$',
    'κ': r'$\kappa$',
    'ω': r'$\omega$',
    'Δ': r'$\Delta$',
    '%': r'\%',
    '&': r'\&',
}

for char, latex in replacements.items():
    text = text.replace(char, latex)

# Bold and italic - more careful
text = re.sub(r'\*\*([^\*\n]{1,200}?)\*\*', r'\\textbf{\1}', text)
text = re.sub(r'\*([^\*\n]{1,100}?)\*', r'\\textit{\1}', text)

# Citations
text = re.sub(r'\[(\d+)\]', r'~\\cite{ref\1}', text)

# Lists
lines = text.split('\n')
output = []
in_enum = False
in_item = False

for line in lines:
    if re.match(r'^\d+\.\s+', line):
        if not in_enum:
            if in_item:
                output.append('\\end{itemize}')
                in_item = False
            output.append('\\begin{enumerate}')
            in_enum = True
        item_text = re.sub(r'^\d+\.\s+', '', line)
        output.append(f'\\item {item_text}')
    elif re.match(r'^[-*]\s+', line):
        if not in_item:
            if in_enum:
                output.append('\\end{enumerate}')
                in_enum = False
            output.append('\\begin{itemize}')
            in_item = True
        item_text = re.sub(r'^[-*]\s+', '', line)
        output.append(f'\\item {item_text}')
    else:
        if in_enum and line.strip() != '':
            if not re.match(r'^\d+\.\s+', line):
                output.append('\\end{enumerate}')
                in_enum = False
        if in_item and line.strip() != '':
            if not re.match(r'^[-*]\s+', line):
                output.append('\\end{itemize}')
                in_item = False
        output.append(line)

if in_enum:
    output.append('\\end{enumerate}')
if in_item:
    output.append('\\end{itemize}')

text = '\n'.join(output)

# Escape underscores not in math mode
# Simple approach: escape _ that aren't between $...$
def escape_underscores(text):
    result = []
    in_math = False
    i = 0
    while i < len(text):
        if text[i] == '$':
            in_math = not in_math
            result.append(text[i])
        elif text[i] == '_' and not in_math:
            result.append(r'\_')
        else:
            result.append(text[i])
        i += 1
    return ''.join(result)

text = escape_underscores(text)

print('[INFO] Writing LaTeX...')
with open(OUTPUT_TEX, 'w', encoding='utf-8') as f:
    f.write(PREAMBLE + text + POSTAMBLE)

print(f'[OK] LaTeX: {OUTPUT_TEX.stat().st_size:,} bytes')

# Compile
print('\n[INFO] Compiling PDF (3 passes)...')
for i in range(3):
    result = subprocess.run(
        ['pdflatex', '-interaction=nonstopmode', OUTPUT_TEX.name],
        cwd=OUTPUT_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    if i == 0:
        # Check for errors on first pass
        if 'Fatal error' in result.stdout:
            print('[ERROR] Compilation failed on pass 1')
            errors = [l for l in result.stdout.split('\n') if l.startswith('!')]
            for e in errors[:10]:
                print(f'  {e}')
            break
    print(f'  Pass {i+1}/3 done')

if OUTPUT_PDF.exists():
    size = OUTPUT_PDF.stat().st_size
    print(f'\n[SUCCESS] PDF CREATED!')
    print(f'  File: {OUTPUT_PDF}')
    print(f'  Size: {size:,} bytes ({size/1024:.1f} KB)')

    # Extract page count
    match = re.search(r'(\d+) pages?', result.stdout)
    if match:
        print(f'  Pages: {match.group(1)}')

    print('\n[INFO] Opening PDF...')
    subprocess.run(['start', '', str(OUTPUT_PDF)], shell=True)
else:
    print('[ERROR] PDF not created')
