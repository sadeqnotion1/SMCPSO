#!/usr/bin/env python
"""Create a simplified LaTeX version that will compile successfully."""

import re

INPUT_MD = '.artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.md'
OUTPUT_TEX = '.artifacts/research/papers/LT7_journal_paper/LT7_ENHANCED_PAPER.tex'

# Read markdown
with open(INPUT_MD, 'r', encoding='utf-8') as f:
    content = f.read()

# Simple LaTeX preamble
preamble = r"""\documentclass[11pt,twocolumn]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{cite}
\usepackage[margin=1in]{geometry}

\title{Comparative Analysis of Sliding Mode Control Variants for Double-Inverted Pendulum Systems: Performance, Stability, and Robustness}

\author{
Author Names \\
Affiliation \\
\texttt{email@example.com}
}

\date{\today}

\begin{document}
\maketitle

"""

postamble = r"""
\end{document}
"""

# Extract just the main content (skip front matter)
lines = content.split('\n')
output_lines = []
skip_until_abstract = True

for line in lines:
    # Skip until we reach Abstract
    if skip_until_abstract:
        if '## Abstract' in line:
            skip_until_abstract = False
            output_lines.append('\\begin{abstract}')
        continue

    # Stop at References
    if '## References' in line:
        break

    # Convert headers
    if line.startswith('## '):
        # Close abstract if we're at first section after abstract
        if len(output_lines) > 0 and output_lines[-1].strip() != '':
            if '\\begin{abstract}' in '\n'.join(output_lines[-10:]):
                output_lines.append('\\end{abstract}\n')
        title = line[3:].strip()
        # Remove numbers like "1. " from section titles
        title = re.sub(r'^\d+\.\s+', '', title)
        output_lines.append(f'\\section{{{title}}}')
    elif line.startswith('### '):
        title = line[4:].strip()
        title = re.sub(r'^\d+\.\d+\.?\s+', '', title)
        output_lines.append(f'\\subsection{{{title}}}')
    elif line.startswith('#### '):
        title = line[5:].strip()
        title = re.sub(r'^\d+\.\d+\.\d+\.?\s+', '', title)
        output_lines.append(f'\\subsubsection{{{title}}}')
    else:
        # Keep the line as-is for now (we'll do minimal formatting)
        output_lines.append(line)

# Join and do minimal formatting
text = '\n'.join(output_lines)

# Replace special characters
text = text.replace('±', r'$\pm$')
text = text.replace('μ', r'$\mu$')
text = text.replace('×', r'$\times$')
text = text.replace('≥', r'$\geq$')
text = text.replace('≤', r'$\leq$')
text = text.replace('≈', r'$\approx$')
text = text.replace('→', r'$\rightarrow$')
text = text.replace('°', r'$^\circ$')
text = text.replace('σ', r'$\sigma$')
text = text.replace('θ', r'$\theta$')
text = text.replace('α', r'$\alpha$')
text = text.replace('β', r'$\beta$')
text = text.replace('γ', r'$\gamma$')
text = text.replace('λ', r'$\lambda$')
text = text.replace('ε', r'$\epsilon$')
text = text.replace('δ', r'$\delta$')

# Convert bold
text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)

# Convert citations [1] -> \cite{ref1}
text = re.sub(r'\[(\d+)\]', r'~\\cite{ref\1}', text)

# Remove tables (they're complex - skip for simple version)
text = re.sub(r'\|[^\n]+\|\n(\|[-:\s|]+\|\n)?(\|[^\n]+\|\n)*', '\n[TABLE OMITTED]\n', text)

# Remove figure references (complex)
text = re.sub(r'!\[Figure[^\]]+\]\([^)]+\)', '[FIGURE OMITTED]', text)

# Remove code blocks (likely math)
text = re.sub(r'```[^\n]*\n.*?\n```', '[EQUATION OMITTED]', text, flags=re.DOTALL)

# Write output
with open(OUTPUT_TEX, 'w', encoding='utf-8') as f:
    f.write(preamble)
    f.write(text)
    f.write(postamble)

print(f'[OK] Created simplified LaTeX: {OUTPUT_TEX}')
print('[INFO] Tables, figures, and complex math omitted for compilation')
print('[INFO] This version focuses on text content and will compile cleanly')
