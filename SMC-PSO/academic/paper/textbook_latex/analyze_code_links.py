"""
Analyze code references in LaTeX textbook chapters.
Checks for \coderef, \pyfile, and lstlisting blocks with file paths.
"""

import re
import os
from pathlib import Path

print('=' * 80)
print('CODE LINKING STATUS REPORT - TEXTBOOK LATEX')
print('=' * 80)
print()

# Analysis categories
chapters_dir = Path('source/chapters')
code_refs = []
pyfile_refs = []
lstlisting_refs = []

# Scan all chapter files
for tex_file in sorted(chapters_dir.glob('ch*.tex')):
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()

    chapter_num = tex_file.stem.split('_')[0].replace('ch', '')

    # Extract \coderef{path}{line}
    coderef_pattern = r'\\coderef\{([^}]+)\}\{([^}]+)\}'
    for match in re.finditer(coderef_pattern, content):
        path, line = match.groups()
        code_refs.append((chapter_num, path, line, tex_file.name))

    # Extract \pyfile{path}
    pyfile_pattern = r'\\pyfile\{([^}]+)\}'
    for match in re.finditer(pyfile_pattern, content):
        path = match.group(1).replace('\\_', '_')
        pyfile_refs.append((chapter_num, path, tex_file.name))

    # Extract lstlisting with captions mentioning file paths
    lstlisting_pattern = r'\\begin\{lstlisting\}.*?caption=\{([^}]+)\}.*?\\end\{lstlisting\}'
    for match in re.finditer(lstlisting_pattern, content, re.DOTALL):
        caption = match.group(1)
        # Extract file path from caption if present (looks for .py files)
        path_in_caption = re.search(r'\(([^)]*\.py[^)]*)\)', caption)
        if path_in_caption:
            lstlisting_refs.append((chapter_num, path_in_caption.group(1), caption, tex_file.name))
        else:
            lstlisting_refs.append((chapter_num, None, caption, tex_file.name))

print('1. DIRECT CODE REFERENCES (\\coderef with line numbers)')
print('-' * 80)
if code_refs:
    for ch, path, line, file in code_refs:
        # Path is relative to project root
        full_path = Path('../../..') / path
        exists = full_path.exists()
        status = '[OK]' if exists else '[ERROR]'
        print(f'{status} Ch{ch:>2} | Line {line:>4} | {path}')
        if exists:
            with open(full_path, 'r') as f:
                total_lines = sum(1 for _ in f)
            line_num = int(line)
            if line_num > total_lines:
                print(f'         [WARNING] Line {line} > file length {total_lines}')
else:
    print('[WARN] No \\coderef commands found')
print()

print('2. PYTHON FILE REFERENCES (\\pyfile without line numbers)')
print('-' * 80)
if pyfile_refs:
    for ch, path, file in pyfile_refs:
        full_path = Path('../../..') / path
        exists = full_path.exists()
        status = '[OK]' if exists else '[ERROR]'
        print(f'{status} Ch{ch:>2} | {path} (in {file})')
else:
    print('[WARN] No \\pyfile commands found')
print()

print('3. EMBEDDED CODE LISTINGS (lstlisting with file paths in captions)')
print('-' * 80)
if lstlisting_refs:
    for ch, path, caption, file in lstlisting_refs:
        if path:
            # Clean path
            clean_path = path.replace('\\_', '_').strip()
            full_path = Path('../../..') / clean_path
            exists = full_path.exists()
            status = '[OK]' if exists else '[CHECK]'
            print(f'{status} Ch{ch:>2} | {clean_path}')
        else:
            print(f'[INFO] Ch{ch:>2} | Generic listing: {caption[:60]}...')
else:
    print('[WARN] No lstlisting blocks found')
print()

print('=' * 80)
print('SUMMARY')
print('=' * 80)
total_refs = len(code_refs) + len(pyfile_refs) + len(lstlisting_refs)
print(f'Total code references: {total_refs}')
print(f'  - \\coderef (line-specific): {len(code_refs)}')
print(f'  - \\pyfile (file-level): {len(pyfile_refs)}')
print(f'  - lstlisting (embedded code): {len(lstlisting_refs)}')
print()

# Chapter coverage
chapters_with_refs = set()
for ch, *_ in code_refs + pyfile_refs + lstlisting_refs:
    chapters_with_refs.add(ch)

print(f'Chapters with code references: {len(chapters_with_refs)}/12')
print(f'Covered chapters: {sorted(chapters_with_refs)}')
print()

# Identify gaps
all_chapters = set(f'{i:02d}' for i in range(1, 13))
missing_chapters = all_chapters - chapters_with_refs
if missing_chapters:
    print(f'[WARN] Chapters WITHOUT code references: {sorted(missing_chapters)}')
    print()
    print('Missing chapters:')
    chapter_names = {
        '01': 'Introduction',
        '02': 'Mathematical Foundations',
        '03': 'Classical SMC',
        '04': 'Super-Twisting',
        '05': 'Adaptive SMC',
        '06': 'Hybrid SMC',
        '07': 'PSO Theory',
        '08': 'Benchmarking',
        '09': 'PSO Results',
        '10': 'Advanced Topics',
        '11': 'Software',
        '12': 'Case Studies'
    }
    for ch in sorted(missing_chapters):
        print(f'  - Chapter {ch}: {chapter_names.get(ch, "Unknown")}')
print()

# Recommendations
print('=' * 80)
print('RECOMMENDATIONS')
print('=' * 80)
print()
print('[ACTION NEEDED] Add code references to chapters without links:')
for ch in sorted(missing_chapters):
    name = chapter_names.get(ch, "Unknown")
    print(f'  - Ch{ch} ({name}): Add \\coderef or \\pyfile commands')
print()

# Check for broken references
broken_refs = []
for ch, path, line, file in code_refs:
    full_path = Path('../../..') / path
    if not full_path.exists():
        broken_refs.append((ch, path, 'coderef'))

for ch, path, file in pyfile_refs:
    full_path = Path('../../..') / path
    if not full_path.exists():
        broken_refs.append((ch, path, 'pyfile'))

if broken_refs:
    print('[ERROR] Broken references found:')
    for ch, path, ref_type in broken_refs:
        print(f'  - Ch{ch}: {path} ({ref_type})')
    print()

print('Analysis complete.')
