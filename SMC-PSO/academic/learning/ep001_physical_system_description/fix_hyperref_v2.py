import re

tex_file = '/mnt/d/Projects/main/academic/learning/ep001_physical_system_description/EP001_unified.tex'

with open(tex_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the hyperref package line and move it BEFORE titlesec
lines = content.split('\n')

# Find titlesec loading line and hyperref
titlesec_idx = None
hyperref_idx = None

for i, line in enumerate(lines):
    if '\\usepackage{titlesec}' in line:
        titlesec_idx = i
    if 'hypertexnames' in line or ('hyperref' in line and 'colorlinks' in line):
        hyperref_idx = i

print(f'Current order:')
print(f'  line {titlesec_idx + 1}: titlesec')
print(f'  line {hyperref_idx + 1}: hyperref')

# We need hyperref BEFORE titlesec
if hyperref_idx and titlesec_idx and hyperref_idx > titlesec_idx:
    # Extract hyperref line
    hyperref_line = lines[hyperref_idx]
    
    # Remove hyperref from current position
    del lines[hyperref_idx]
    
    # Insert BEFORE titlesec
    lines.insert(titlesec_idx, hyperref_line)
    
    print(f'\nMoved hyperref from line {hyperref_idx + 1} to line {titlesec_idx + 1}')
    
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f'[OK] Fixed hyperref positioning - now loads BEFORE titlesec')
else:
    print('[OK] hyperref is already before titlesec')
