#!/usr/bin/env python
"""
Compile EP001 LaTeX to PDF with proper section numbering.
Run from Windows command line: python compile_pdf.py
"""
import os
import subprocess
import sys
import re
from datetime import datetime

os.chdir(r'D:\Projects\main\academic\learning\ep001_physical_system_description')

# Generate unique filename with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
tex_file = 'EP001_unified'
pdf_file = f'{tex_file}_v{timestamp}.pdf'

miktex_path = r'C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe'

print(f'[INFO] EP001 PDF Compiler')
print(f'[INFO] Source: {tex_file}.tex')
print(f'[INFO] Output: {pdf_file}')
print(f'[INFO] MiKTeX: {miktex_path}')

if not os.path.exists(miktex_path):
    print(f'[ERROR] MiKTeX not found at {miktex_path}')
    print(f'[INFO] Please ensure MiKTeX is installed')
    sys.exit(1)

# Check if .tex file exists
if not os.path.exists(f'{tex_file}.tex'):
    print(f'[ERROR] Source file {tex_file}.tex not found')
    sys.exit(1)

print(f'\n[INFO] Running pdflatex 4 times for proper cross-references...\n')

# Run pdflatex 4 times
for i in range(1, 5):
    print(f'  [INFO] Pass {i}/4...', end=' ')
    
    cmd = [miktex_path, '-interaction=nonstopmode', f'{tex_file}.tex']
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 or 'Output written on' in result.stdout:
        print('[OK]')
    else:
        print(f'[WARN] (exit code {result.returncode})')
        
        # Check if output was still created
        if os.path.exists(f'{tex_file}.pdf'):
            print('  [INFO] PDF created despite warnings')
            break
        else:
            print(f'  [ERROR] Pass {i} failed')
            # Print last few lines of log for debugging
            if os.path.exists(f'{tex_file}.log'):
                with open(f'{tex_file}.log', 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    print(f'  [INFO] Last 10 log lines:')
                    for line in lines[-10:]:
                        print(f'    {line.rstrip()}')
            sys.exit(1)

# Verify PDF was created
if os.path.exists(pdf_file):
    size = os.path.getsize(pdf_file)
    print(f'\n[OK] PDF successfully created: {pdf_file}')
    print(f'[OK] Size: {size:,} bytes')
    
    # Check section numbering in .aux file
    aux_file = f'{tex_file}.aux'
    if os.path.exists(aux_file):
        with open(aux_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Find all section labels
            sections = re.findall(r'\\newlabel\{([^}]+)\}\s*\{([^}]+)\}', content)
            section_nums = [m[1].strip() for m in sections if m[1].strip()]
            
            print(f'\n[INFO] Found {len(section_nums)} section references')
            
            if section_nums:
                print(f'[INFO] First 5 sections: {section_nums[:5]}')
                
                # Check for 0.0 numbering
                if '0.0' in section_nums:
                    print('\n[ERROR] Found 0.0 section numbering!')
                    print('[ERROR] The LaTeX file has \setcounter{section}{-1} or similar')
                    print('[INFO] Fix needed in EP001_unified.tex source file')
                else:
                    print('[OK] Section numbering looks correct')
    else:
        print(f'\n[WARN] Could not find .aux file to check sections')
    
    print(f'\n[OK] Compilation complete!')
    print(f'[INFO] View: {pdf_file}')
    
else:
    print(f'\n[ERROR] PDF file not created: {pdf_file}')
    print('[ERROR] Check the .log file for LaTeX errors')
    
    if os.path.exists(f'{tex_file}.log'):
        print(f'\n[INFO] Checking log file for errors...')
        with open(f'{tex_file}.log', 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            errors = [l for l in lines if 'Error' in l or 'Undefined' in l or 'LaTeX Error' in l]
            if errors:
                print(f'[WARN] Found {len(errors)} potential errors:')
                for l in errors[:10]:
                    print(f'  {l.rstrip()}')
    
    sys.exit(1)
