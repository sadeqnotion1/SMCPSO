#!/usr/bin/env python
"""Fix markdown-style lists in LaTeX file."""

import re

INPUT_FILE = '.artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.tex'

# Read the file
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Process lines to convert numbered lists
result = []
in_enumerate = False
in_itemize = False

for i, line in enumerate(lines):
    # Detect start of numbered list (lines starting with '1. ')
    if re.match(r'^1\.\s+', line):
        if not in_enumerate:
            result.append('\\begin{enumerate}\n')
            in_enumerate = True
        result.append(re.sub(r'^\d+\.\s+', r'\\item ', line))
    # Detect continuation of numbered list (lines starting with '2. ', '3. ', etc.)
    elif re.match(r'^\d+\.\s+', line) and in_enumerate:
        result.append(re.sub(r'^\d+\.\s+', r'\\item ', line))
    # Detect bulleted lists (lines starting with '- ')
    elif re.match(r'^-\s+', line):
        if not in_itemize:
            if in_enumerate:  # Close enumerate if open
                result.append('\\end{enumerate}\n')
                in_enumerate = False
            result.append('\\begin{itemize}\n')
            in_itemize = True
        result.append(re.sub(r'^-\s+', r'\\item ', line))
    # Detect end of list (blank line or new section)
    elif (line.strip() == '' or line.startswith('\\section') or line.startswith('\\subsection')) and (in_enumerate or in_itemize):
        if in_enumerate:
            result.append('\\end{enumerate}\n')
            in_enumerate = False
        if in_itemize:
            result.append('\\end{itemize}\n')
            in_itemize = False
        result.append(line)
    else:
        result.append(line)

# Close any remaining lists
if in_enumerate:
    result.append('\\end{enumerate}\n')
if in_itemize:
    result.append('\\end{itemize}\n')

# Write back
with open(INPUT_FILE, 'w', encoding='utf-8') as f:
    f.writelines(result)

print('[OK] Converted numbered and bulleted lists to LaTeX environments')
