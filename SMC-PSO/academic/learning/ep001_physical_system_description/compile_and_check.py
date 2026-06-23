#!/usr/bin/env python3
"""
Compile EP001 LaTeX and check for section numbering issues.
Run from Windows: python compile_and_check.py
"""
import subprocess
import os
import re
from datetime import datetime

TEX_DIR = r'D:\Projects\main\academic\learning\ep001_physical_system_description'
TEX_FILE = 'EP001_unified.tex'
MIKTEX = r'C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe'

os.chdir(TEX_DIR)

print('=' * 60)
print('EP001 PDF Compiler')
print('=' * 60)
print(f'Working directory: {TEX_DIR}')
print(f'MiKTeX path: {MIKTEX}')
print(f'Source file: {TEX_FILE}')
print()

if not os.path.exists(MIKTEX):
    print('[ERROR] MiKTeX not found!')
    exit(1)

if not os.path.exists(TEX_FILE):
    print(f'[ERROR] {TEX_FILE} not found!')
    exit(1)

# Clean previous outputs
print('[INFO] Cleaning previous outputs...')
for ext in ['.pdf', '.aux', '.log', '.out']:
    try:
        os.remove(TEX_FILE + ext)
    except FileNotFoundError:
        pass

# Compile 4 times
print('[INFO] Running pdflatex 4 times...')
for i in range(1, 5):
    print(f'  Pass {i}/4...', end=' ')
    cmd = [MIKTEX, '-interaction=nonstopmode', TEX_FILE]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if 'Output written on' in result.stdout:
        print('[OK]')
    elif result.returncode == 0:
        print('[OK] (no output message)')
    else:
        print(f'[WARN] exit code {result.returncode}')
        # Check log for errors
        if os.path.exists('EP001_unified.log'):
            with open('EP001_unified.log', 'r', encoding='utf-8', errors='ignore') as f:
                log = f.read()
                if 'Error' in log or 'Undefined' in log:
                    errors = [l for l in log.split('\n') if 'Error' in l or 'Undefined' in l][:5]
                    for e in errors:
                        print(f'    {e[:100]}')

# Check if PDF exists
PDF_FILE = 'EP001_unified.pdf'
if os.path.exists(PDF_FILE):
    size = os.path.getsize(PDF_FILE)
    print(f'\n[OK] PDF created: {PDF_FILE}')
    print(f'[OK] Size: {size:,} bytes')
else:
    print(f'\n[ERROR] PDF not created!')
    exit(1)

# Analyze .aux file for section numbering
print('\n' + '=' * 60)
print('Section Numbering Analysis')
print('=' * 60)

aux_file = 'EP001_unified.aux'
if os.path.exists(aux_file):
    with open(aux_file, 'r', encoding='utf-8', errors='ignore') as f:
        aux_content = f.read()
    
    # Extract all section labels
    section_labels = re.findall(r'\\newlabel\{([^}]+)\}\s*\{([^}]+)\}', aux_content)
    
    if section_labels:
        print(f'[INFO] Found {len(section_labels)} section/table/figure labels')
        
        # Check for 0.0 patterns
        zero_sections = [label for label, num in section_labels if num.strip() == '0.0']
        if zero_sections:
            print(f'\n[ERROR] Found {len(zero_sections)} labels with 0.0 numbering:')
            for label in zero_sections[:10]:
                print(f'  - {label}')
        else:
            print('[OK] No 0.0 section numbering found')
        
        # Show sample section numbers
        section_nums = [num.strip() for label, num in section_labels if num.strip()]
        if section_nums:
            unique_nums = sorted(set(section_nums))[:10]
            print(f'\n[INFO] Sample section numbers: {unique_nums}')
            
            # Check if we have proper numbering (1, 1.1, 2, 2.1, etc.)
            has_proper = any(num.isdigit() and int(num) > 0 for num in unique_nums)
            if has_proper:
                print('[OK] Found proper section numbering')
            else:
                print('[WARN] Section numbering may still have issues')
    else:
        print('[WARN] No section labels found in .aux file')
else:
    print('[WARN] .aux file not found')

# Check for enumerate counter issues
print('\n' + '=' * 60)
print('Enumerate Counter Analysis')
print('=' * 60)

if os.path.exists(aux_file):
    with open(aux_file, 'r', encoding='utf-8', errors='ignore') as f:
        aux_content = f.read()
    
    # Check for enumerate-related labels
    enum_labels = [l for l, n in section_labels if 'enum' in l.lower()] if section_labels else []
    if enum_labels:
        print(f'[INFO] Found {len(enum_labels)} enumerate-related labels')
        for l in enum_labels[:5]:
            print(f'  - {l}')
    else:
        print('[OK] No enumerate counter issues detected')

print('\n' + '=' * 60)
print('Compilation Complete!')
print('=' * 60)
print(f'View PDF: {os.path.abspath(PDF_FILE)}')
