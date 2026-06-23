#!/usr/bin/env python3
import subprocess
import os
import shutil

pdflatex = '/mnt/c/Program Files/MiKTeX/miktex/bin/x64/pdflatex.exe'
tex_file = 'EP001_unified.tex'

# Clean old files
for f in ['EP001_unified.pdf', 'EP001_unified.aux', 'EP001_unified.log', 'EP001_unified.toc']:
    try:
        os.remove(f)
    except:
        pass

print("Compiling EP001_unified.tex...")
for i in range(4):
    print(f"  Pass {i+1}/4...")
    result = subprocess.run(
        [pdflatex, '-interaction=nonstopmode', tex_file],
        capture_output=True,
        text=True
    )

# Check result
if os.path.exists('EP001_unified.pdf'):
    size = os.path.getsize('EP001_unified.pdf') / 1024
    print(f"\n[SUCCESS] PDF created! ({size:.1f} KB)")
    
    # Extract sections
    with open('EP001_unified.pdf', 'rb') as f:
        content = f.read().decode('latin-1', errors='ignore')
    
    import re
    sections = set()
    for m in re.findall(r'\((section\.(\d+))\)', content):
        sections.add(f"section.{m[1]}")
    for m in re.findall(r'\((subsection\.(\d+)\.(\d+))\)', content):
        sections.add(f"subsection.{m[1]}.{m[2]}")
    
    print("\nSections found:")
    for s in sorted(sections):
        print(f"  {s}")
else:
    print("\n[FAILED] PDF not created")
    if os.path.exists('EP001_unified.log'):
        with open('EP001_unified.log') as f:
            log = f.read()
            if 'Error' in log or '!' in log:
                print("Errors:")
                for line in log.split('\n')[-20:]:
                    if line.strip() and ('Error' in line or '!' in line):
                        print(f"  {line}")
