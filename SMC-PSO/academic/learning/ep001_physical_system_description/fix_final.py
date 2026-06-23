import re

tex_file = '/mnt/d/Projects/main/academic/learning/ep001_physical_system_description/EP001_unified.tex'

with open(tex_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
skip_next = False

for i, line in enumerate(lines):
    # Skip lines that have theorem definitions with optional args
    if '\\begin{theorem}[Control' in line:
        # Replace with regular theorem and put title in text
        fixed_lines.append('\\begin{theorem}\n')
        fixed_lines.append('Control design for the DIP involves trade-offs between:\n')
        print(f'Line {i+1}: Fixed theorem environment')
        skip_next = True
        continue
    
    if skip_next and '\\begin{enumerate}' in line:
        skip_next = False
        fixed_lines.append(line)
        continue
    
    fixed_lines.append(line)

with open(tex_file, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('[OK] Fixed theorem environment')
