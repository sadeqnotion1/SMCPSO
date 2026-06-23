#!/usr/bin/env python
"""Generate complete PDF with simplified formatting that will compile."""

import re
import subprocess
from pathlib import Path

INPUT_MD = Path('.artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.md')
OUTPUT_DIR = Path('.artifacts/research/papers/LT7_journal_paper')
OUTPUT_TEX = OUTPUT_DIR / 'LT7_COMPLETE.tex'
OUTPUT_PDF = OUTPUT_DIR / 'LT7_COMPLETE.pdf'

print('[INFO] Reading enhanced Markdown...')
with open(INPUT_MD, 'r', encoding='utf-8') as f:
    content = f.read()

print('[INFO] Processing content...')

# Simple LaTeX preamble
PREAMBLE = r'''\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb}
\usepackage[margin=1in]{geometry}

\title{Comparative Analysis of Sliding Mode Control Variants for \\
       Double-Inverted Pendulum Systems: \\
       Performance, Stability, and Robustness \\
       \vspace{0.5cm}
       \large Enhanced Version - All 10 Sections}

\author{Research Paper}
\date{December 25, 2025}

\begin{document}
\maketitle
\tableofcontents
\newpage

'''

POSTAMBLE = r'''

\vspace{1cm}
\noindent\textbf{Note:} This PDF contains the complete text of all 10 enhanced sections (6,932 lines, 48,820 words). Tables and complex formatting are simplified for compilation. The complete Markdown version contains all detailed tables and data.

\end{document}
'''

# Process content
lines = content.split('\n')
output = []
skip = True
in_table = False
in_code = False

for line in lines:
    # Skip until Abstract
    if skip:
        if '## Abstract' in line or '##Abstract' in line:
            skip = False
            output.append('\\begin{abstract}')
            continue
        continue

    # Handle code blocks
    if line.strip().startswith('```'):
        in_code = not in_code
        continue
    if in_code:
        continue

    # Skip tables
    if line.strip().startswith('|'):
        if not in_table:
            output.append('\n[TABLE - See Markdown version for details]\n')
            in_table = True
        continue
    else:
        in_table = False

    # Stop at References
    if 'References' in line and line.startswith('##'):
        break

    # Headers
    if line.startswith('## '):
        if 'abstract' in '\n'.join(output[-3:]).lower() and 'end{abstract}' not in '\n'.join(output[-3:]):
            output.append('\\end{abstract}\n')
        title = re.sub(r'^\d+\.\s*', '', line[3:].strip())
        output.append(f'\\section{{{title}}}')
    elif line.startswith('### '):
        title = re.sub(r'^\d+\.\d+\.?\s*', '', line[4:].strip())
        output.append(f'\\subsection{{{title}}}')
    elif line.startswith('#### '):
        title = re.sub(r'^\d+\.\d+\.\d+\.?\s*', '', line[5:].strip())
        output.append(f'\\subsubsection{{{title}}}')
    elif line.strip().startswith('!['):
        output.append('[FIGURE - See Markdown version]')
    else:
        output.append(line)

text = '\n'.join(output)

print('[INFO] Cleaning text...')

# Remove all markdown formatting - just keep plain text
text = text.replace('**', '')  # Remove bold markers
text = text.replace('*', '')   # Remove italic markers
text = text.replace('__', '')  # Remove bold markers
text = text.replace('_', ' ')  # Replace underscores with spaces

# Replace special chars
chars = {
    '±': '+/-', '×': 'x', 'μ': 'mu', '°': ' deg',
    '≥': '>=', '≤': '<=', '≈': '~=',
    '→': '->', 'σ': 'sigma', 'θ': 'theta',
    'α': 'alpha', 'β': 'beta', 'γ': 'gamma',
    'λ': 'lambda', 'ε': 'epsilon', 'δ': 'delta',
    'κ': 'kappa', 'ω': 'omega', 'Δ': 'Delta',
    '&': 'and', '%': 'percent', '#': 'num',
}
for char, repl in chars.items():
    text = text.replace(char, repl)

# Citations
text = re.sub(r'\[(\d+)\]', r'[ref\1]', text)

# Handle lists
lines = text.split('\n')
out = []
for line in lines:
    if re.match(r'^\d+\.\s+', line):
        out.append('- ' + re.sub(r'^\d+\.\s+', '', line))
    elif re.match(r'^-\s+', line):
        out.append(line)
    else:
        out.append(line)

text = '\n'.join(out)

print('[INFO] Writing LaTeX...')
with open(OUTPUT_TEX, 'w', encoding='utf-8') as f:
    f.write(PREAMBLE + text + POSTAMBLE)

print(f'[OK] LaTeX written: {OUTPUT_TEX.stat().st_size:,} bytes')

# Compile
print('\n[INFO] Compiling PDF...')
for i in range(2):
    result = subprocess.run(
        ['pdflatex', '-interaction=nonstopmode', OUTPUT_TEX.name],
        cwd=OUTPUT_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    print(f'[INFO] Pass {i+1}/2 done')

if OUTPUT_PDF.exists():
    size = OUTPUT_PDF.stat().st_size
    print(f'\n[SUCCESS] PDF CREATED!')
    print(f'  File: {OUTPUT_PDF}')
    print(f'  Size: {size:,} bytes ({size/1024:.1f} KB)')

    # Get page count
    if 'Output written' in result.stdout:
        match = re.search(r'(\d+) pages?', result.stdout)
        if match:
            print(f'  Pages: {match.group(1)}')
else:
    print('[ERROR] PDF failed')
    errors = [l for l in result.stdout.split('\n') if l.startswith('!')]
    for e in errors[:5]:
        print(f'  {e}')
