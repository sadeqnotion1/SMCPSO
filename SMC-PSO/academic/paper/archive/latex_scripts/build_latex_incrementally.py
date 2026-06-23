#!/usr/bin/env python
"""Build a working LaTeX file incrementally from Markdown."""

import re
import subprocess
from pathlib import Path

INPUT_MD = Path('.artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.md')
OUTPUT_DIR = Path('.artifacts/research/papers/LT7_journal_paper')
OUTPUT_TEX = OUTPUT_DIR / 'LT7_FINAL.tex'

# Simple but complete preamble
PREAMBLE = r'''\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage[margin=1in]{geometry}

\title{Comparative Analysis of Sliding Mode Control Variants for \\ Double-Inverted Pendulum Systems: \\ Performance, Stability, and Robustness}

\author{Author Names \\ Affiliation \\ \texttt{email@example.com}}
\date{\today}

\begin{document}
\maketitle

'''

POST = r'''
\end{document}
'''

# Read markdown
print('[INFO] Reading markdown...')
with open(INPUT_MD, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Extract sections
sections = md_content.split('\n## ')
print(f'[INFO] Found {len(sections)} sections')

# Process content
output = []
in_abstract = False

for i, section in enumerate(sections):
    lines = section.split('\n')

    if i == 0:
        # Skip front matter before Abstract
        if 'Abstract' in section:
            idx = section.find('Abstract')
            abstract_part = section[idx:]
            lines = abstract_part.split('\n')[1:]  # Skip "Abstract" line
            output.append('\\begin{abstract}')
            in_abstract = True
        else:
            continue

    # Check if this is still abstract or a new section
    if i > 0:
        # This is a new section
        if in_abstract:
            output.append('\\end{abstract}\n')
            in_abstract = False

        section_title = lines[0].strip()
        # Remove numbers like "1. " from titles
        section_title = re.sub(r'^\d+\.\s+', '', section_title)
        output.append(f'\\section{{{section_title}}}')
        lines = lines[1:]  # Remove title line

    # Process content lines
    for line in lines:
        # Subsections
        if line.startswith('### '):
            title = line[4:].strip()
            title = re.sub(r'^\d+\.\d+\.?\s+', '', title)
            output.append(f'\\subsection{{{title}}}')
        elif line.startswith('#### '):
            title = line[5:].strip()
            title = re.sub(r'^\d+\.\d+\.\d+\.?\s+', '', title)
            output.append(f'\\subsubsection{{{title}}}')
        # Skip tables for now (complex)
        elif line.strip().startswith('|'):
            continue
        # Skip code blocks
        elif line.strip().startswith('```'):
            continue
        # Skip image references
        elif line.strip().startswith('!['):
            continue
        # Skip References section entirely
        elif 'References' in line and line.startswith('#'):
            break
        else:
            output.append(line)

# Join text
text = '\n'.join(output)

# Replace special characters
replacements = {
    '±': r'$\pm$',
    '×': r'$\times$',
    'μ': r'$\mu$',
    '°': r'$^\circ$',
    '≥': r'$\geq$',
    '≤': r'$\leq$',
    '≈': r'$\approx$',
    '→': r'$\rightarrow$',
    'σ': r'$\sigma$',
    'θ': r'$\theta$',
    'α': r'$\alpha$',
    'β': r'$\beta$',
    'γ': r'$\gamma$',
    'λ': r'$\lambda$',
    'ε': r'$\epsilon$',
    'δ': r'$\delta$',
    'κ': r'$\kappa$',
}

for char, latex in replacements.items():
    text = text.replace(char, latex)

# Format text
# Bold
text = re.sub(r'\*\*([^*]+)\*\*', r'\\textbf{\1}', text)
# Italic
text = re.sub(r'\*([^*]+)\*', r'\\textit{\1}', text)

# Citations [1] -> \cite{ref1}
text = re.sub(r'\[(\d+)\]', r'~\\cite{ref\1}', text)

# Lists - simple numbered lists
text = re.sub(r'^\d+\.\s+', r'\\item ', text, flags=re.MULTILINE)

# Write
print('[INFO] Writing LaTeX file...')
with open(OUTPUT_TEX, 'w', encoding='utf-8') as f:
    f.write(PREAMBLE)
    f.write(text)
    f.write(POST)

print(f'[OK] Created: {OUTPUT_TEX}')
print(f'[INFO] File size: {OUTPUT_TEX.stat().st_size} bytes')

# Try to compile
print('\n[INFO] Attempting PDF compilation...')
try:
    result = subprocess.run(
        ['pdflatex', '-interaction=nonstopmode', 'LT7_FINAL.tex'],
        cwd=OUTPUT_DIR,
        capture_output=True,
        text=True,
        timeout=60
    )
    if 'Output written' in result.stdout:
        print('[OK] PDF compiled successfully!')
        print(f'[OK] PDF: {OUTPUT_DIR / "LT7_FINAL.pdf"}')
    else:
        print('[ERROR] Compilation failed')
        # Show last few lines
        lines = result.stdout.split('\n')
        print('\n'.join(lines[-20:]))
except Exception as e:
    print(f'[ERROR] Compilation error: {e}')
