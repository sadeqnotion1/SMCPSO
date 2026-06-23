import re

tex_file = '/mnt/d/Projects/main/academic/learning/ep001_physical_system_description/EP001_unified.tex'

with open(tex_file, 'r', encoding='utf-8') as f:
    content = f.read()

# The issue: theorem with optional argument [title] doesn't work with hyperref/titlesec
# Fix: Remove the optional argument from theorem

# Replace \begin{theorem}[title] with \begin{theorem}
content = re.sub(r'\\begin\{theorem\}\[([^\]]+)\]', r'\\begin{theorem}', content)

# Also fix any other environments with optional arguments that might break
content = re.sub(r'\\begin\{definition\}\[([^\]]+)\]', r'\\begin{definition}', content)
content = re.sub(r'\\begin\{proposition\}\[([^\]]+)\]', r'\\begin{proposition}', content)
content = re.sub(r'\\begin\{lemma\}\[([^\]]+)\]', r'\\begin{lemma}', content)

with open(tex_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'[OK] Fixed theorem/definition/proposition/lemma environments')
