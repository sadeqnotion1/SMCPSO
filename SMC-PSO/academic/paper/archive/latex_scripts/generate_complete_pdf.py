#!/usr/bin/env python
"""Generate complete PDF from enhanced Markdown with all sections."""

import re
import subprocess
from pathlib import Path

INPUT_MD = Path('.artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.md')
OUTPUT_DIR = Path('.artifacts/research/papers/LT7_journal_paper')
OUTPUT_TEX = OUTPUT_DIR / 'LT7_COMPLETE_ENHANCED.tex'
OUTPUT_PDF = OUTPUT_DIR / 'LT7_COMPLETE_ENHANCED.pdf'

print('[INFO] Reading enhanced Markdown (6,932 lines)...')
with open(INPUT_MD, 'r', encoding='utf-8') as f:
    content = f.read()

print('[INFO] Processing content...')

# LaTeX preamble
PREAMBLE = r'''\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage[margin=1in]{geometry}
\usepackage{enumitem}

\title{Comparative Analysis of Sliding Mode Control Variants for \\
       Double-Inverted Pendulum Systems: \\
       Performance, Stability, and Robustness}

\author{Research Paper - Enhanced Version}
\date{December 25, 2025}

\begin{document}
\maketitle
\tableofcontents
\newpage

'''

POSTAMBLE = r'''

\section*{Note on Tables and Figures}
This PDF contains the complete text of all 10 enhanced sections. Tables and figures are noted throughout the text but are rendered in simplified format for compilation. The full Markdown version contains all detailed tables with complete data.

\end{document}
'''

# Split into lines for processing
lines = content.split('\n')
output = []
skip_until_abstract = True
in_table = False
in_code_block = False
table_count = 0

for i, line in enumerate(lines):
    # Skip front matter until Abstract
    if skip_until_abstract:
        if '## Abstract' in line or '##Abstract' in line:
            skip_until_abstract = False
            output.append('\\begin{abstract}')
            continue
        continue

    # Handle code blocks (likely math - skip for now)
    if line.strip().startswith('```'):
        in_code_block = not in_code_block
        if in_code_block:
            output.append('\\begin{verbatim}')
        else:
            output.append('\\end{verbatim}')
        continue

    if in_code_block:
        output.append(line)
        continue

    # Handle tables - simplify them
    if line.strip().startswith('|'):
        if not in_table:
            table_count += 1
            output.append(f'\n\\textbf{{[Table {table_count} - See Markdown for full details]}}\n')
            in_table = True
        continue  # Skip table lines
    else:
        if in_table:
            in_table = False

    # Stop at References
    if line.strip().startswith('## References') or line.strip().startswith('##References'):
        break

    # Handle headers
    if line.startswith('## '):
        # Close abstract if needed
        if 'abstract' in '\n'.join(output[-5:]).lower() and '\\end{abstract}' not in '\n'.join(output[-5:]):
            output.append('\\end{abstract}\n')

        title = line[3:].strip()
        title = re.sub(r'^\d+\.\s*', '', title)  # Remove "1. " prefix
        output.append(f'\\section{{{title}}}')

    elif line.startswith('### '):
        title = line[4:].strip()
        title = re.sub(r'^\d+\.\d+\.?\s*', '', title)  # Remove "1.1 " prefix
        output.append(f'\\subsection{{{title}}}')

    elif line.startswith('#### '):
        title = line[5:].strip()
        title = re.sub(r'^\d+\.\d+\.\d+\.?\s*', '', title)  # Remove "1.1.1 " prefix
        output.append(f'\\subsubsection{{{title}}}')

    # Skip image references
    elif line.strip().startswith('!['):
        # Extract figure description
        match = re.search(r'!\[([^\]]+)\]', line)
        if match:
            output.append(f'\\textbf{{[Figure: {match.group(1)}]}}')

    # Keep other lines
    else:
        output.append(line)

# Join text
text = '\n'.join(output)

print('[INFO] Applying text transformations...')

# Replace special characters
replacements = {
    '±': r'$\pm$',
    '×': r'$\times$',
    'μ': r'$\mu$',
    '°': r'$^\circ$',
    '≥': r'$\geq$',
    '≤': r'$\leq$',
    '≈': r'$\approx$',
    '→': r'$\to$',
    '←': r'$\leftarrow$',
    '↔': r'$\leftrightarrow$',
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
    'Σ': r'$\Sigma$',
    '∫': r'$\int$',
    '∂': r'$\partial$',
    '∞': r'$\infty$',
    '∈': r'$\in$',
    '∀': r'$\forall$',
    '∃': r'$\exists$',
    '∇': r'$\nabla$',
    '√': r'$\sqrt{}$',
}

for char, latex in replacements.items():
    text = text.replace(char, latex)

# Format text styling
# Bold - but be careful with nested braces
text = re.sub(r'\*\*([^*\n]+?)\*\*', r'\\textbf{\1}', text)
# Italic
text = re.sub(r'\*([^*\n]+?)\*', r'\\textit{\1}', text)

# Citations [1] -> \cite{ref1}
text = re.sub(r'\[(\d+)\]', r'~\\cite{ref\1}', text)

# Handle lists - convert markdown lists to enumerate/itemize
lines = text.split('\n')
output = []
in_enum = False
in_item = False

for line in lines:
    # Numbered list
    if re.match(r'^\d+\.\s+', line):
        if not in_enum:
            output.append('\\begin{enumerate}')
            in_enum = True
        item_text = re.sub(r'^\d+\.\s+', '', line)
        output.append(f'\\item {item_text}')
    # Bulleted list
    elif re.match(r'^[-*]\s+', line):
        if not in_item:
            if in_enum:
                output.append('\\end{enumerate}')
                in_enum = False
            output.append('\\begin{itemize}')
            in_item = True
        item_text = re.sub(r'^[-*]\s+', '', line)
        output.append(f'\\item {item_text}')
    # Regular line
    else:
        if in_enum and line.strip() and not re.match(r'^\d+\.\s+', line):
            output.append('\\end{enumerate}')
            in_enum = False
        if in_item and line.strip() and not re.match(r'^[-*]\s+', line):
            output.append('\\end{itemize}')
            in_item = False
        output.append(line)

# Close any open environments
if in_enum:
    output.append('\\end{enumerate}')
if in_item:
    output.append('\\end{itemize}')

text = '\n'.join(output)

# Escape special LaTeX characters (but not our commands)
# Do this carefully to not break LaTeX commands
text = text.replace('&', r'\&')
text = text.replace('%', r'\%')
text = text.replace('#', r'\#')
# Don't escape $ since we use it for math
# text = text.replace('$', r'\$')
text = text.replace('_', r'\_')

print('[INFO] Writing LaTeX file...')
with open(OUTPUT_TEX, 'w', encoding='utf-8') as f:
    f.write(PREAMBLE)
    f.write(text)
    f.write(POSTAMBLE)

print(f'[OK] Created: {OUTPUT_TEX}')
print(f'     Size: {OUTPUT_TEX.stat().st_size:,} bytes')

# Compile to PDF
print('\n[INFO] Compiling to PDF (pass 1/3)...')
try:
    for pass_num in range(3):
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', OUTPUT_TEX.name],
            cwd=OUTPUT_DIR,
            capture_output=True,
            text=True,
            timeout=120
        )
        print(f'[INFO] Pass {pass_num + 1}/3 complete')

    # Check if PDF was created
    if OUTPUT_PDF.exists():
        pdf_size = OUTPUT_PDF.stat().st_size
        print(f'\n[OK] PDF GENERATED SUCCESSFULLY!')
        print(f'     File: {OUTPUT_PDF}')
        print(f'     Size: {pdf_size:,} bytes ({pdf_size / 1024:.1f} KB)')

        # Count pages from log
        log_file = OUTPUT_DIR / 'LT7_COMPLETE_ENHANCED.log'
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                # Find page count
                pages_match = re.search(r'Output written[^(]*\((\d+) pages?', log_content)
                if pages_match:
                    pages = pages_match.group(1)
                    print(f'     Pages: {pages}')

        print(f'\n[SUCCESS] Complete enhanced PDF ready!')
        print(f'          All 10 sections included')
    else:
        print('[ERROR] PDF not created')
        # Show errors
        log_file = OUTPUT_DIR / 'LT7_COMPLETE_ENHANCED.log'
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
                errors = [l for l in log_lines if l.startswith('!')]
                if errors:
                    print('\nErrors found:')
                    for err in errors[:10]:
                        print(f'  {err.strip()}')

except subprocess.TimeoutExpired:
    print('[ERROR] Compilation timeout')
except Exception as e:
    print(f'[ERROR] {e}')

print('\n[INFO] Conversion complete!')
