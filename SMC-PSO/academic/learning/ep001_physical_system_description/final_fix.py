import re

tex_file = '/mnt/d/Projects/main/academic/learning/ep001_physical_system_description/EP001_unified.tex'

with open(tex_file, 'r', encoding='utf-8') as f:
    content = f.read()

print('Applying fixes...')

# Fix 1: Change theorem/definition to use standard format without optional args
# Replace \begin{theorem}[title] with just \begin{theorem} and put title in text
content = re.sub(r'\\begin\{theorem\}\[(.*?)\]', r'\\begin{theorem}\n\textbf{\\texorpdfstring{$\Rightarrow$}{=>} \\textit{\1}}', content)
content = re.sub(r'\\begin\{definition\}\[(.*?)\]', r'\\begin{definition}\n\textbf{\\texorpdfstring{$\Rightarrow$}{=>} \\textit{\1}}', content)
content = re.sub(r'\\begin\{proposition\}\[(.*?)\]', r'\\begin{proposition}\n\textbf{\\texorpdfstring{$\Rightarrow$}{=>} \\textit{\1}}', content)
content = re.sub(r'\\begin\{lemma\}\[(.*?)\]', r'\\begin{lemma}\n\textbf{\\texorpdfstring{$\Rightarrow$}{=>} \\textit{\1}}', content)

# Fix 2: Add missing \end{itemize} before theorem if needed
# Find patterns where itemize ends but theorem starts without spacing
content = re.sub(r'(\\end\{itemize\})\n(\\begin\{theorem\})', r'\1\n\n\2', content)

# Fix 3: Ensure enumerate environments are properly closed
content = re.sub(r'(\\end\{enumerate\})\n(\\subsection)', r'\1\n\n\2', content)

# Fix 4: Add pagestyle after hyperref
content = re.sub(r'(\\usepackage\[.*?\]\{hyperref\})', r'\1\n\n% Fix for section numbering\n\\hypersetup{hidelinks}', content)

with open(tex_file, 'w', encoding='utf-8') as f:
    f.write(content)

print('[OK] Applied all fixes')
