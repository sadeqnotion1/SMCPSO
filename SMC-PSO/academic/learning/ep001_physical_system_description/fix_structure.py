import re

tex_file = '/mnt/d/Projects/main/academic/learning/ep001_physical_system_description/EP001_unified.tex'

with open(tex_file, 'r', encoding='utf-8') as f:
    content = f.read()

# The fix: Move \subsection{Control Implications} before the \begin{itemize}
# Current structure is wrong - subsection should come first

# Find the problematic section
old_pattern = r'''(    \item \textbf{Disturbance rejection} requirements
\end{enumerate}

\subsection{Control Implications}

\begin{itemize})'''

new_pattern = r'''\subsection{Control Implications}

\begin{itemize}
    \item Linear control methods require careful gain scheduling
    \item Nonlinear control (SMC, MPC) can handle larger operating ranges
    \item Robust designs must account for parameter variations
    \item Adaptive methods can compensate for uncertainties
\end{itemize}

    \item \textbf{Disturbance rejection} requirements
\end{enumerate}'''

# Actually, let's read the exact content and fix it properly
lines = content.split('\n')

# Find line numbers
fix_idx = None
for i, line in enumerate(lines):
    if '\\subsection{Control Implications}' in line:
        fix_idx = i
        break

if fix_idx:
    print(f'Found subsection at line {fix_idx + 1}')
    
    # We need to move the subsection BEFORE the first itemize
    # Find the first itemize before this subsection
    for i in range(fix_idx - 1, -1, -1):
        if '\\begin{itemize}' in lines[i]:
            print(f'Found itemize at line {i + 1}')
            
            # Extract the subsection line
            subsection_line = lines[fix_idx]
            
            # Remove subsection line
            del lines[fix_idx]
            
            # Insert after itemize (but before items)
            lines.insert(i + 1, subsection_line)
            
            print(f'Moved subsection to line {i + 2}')
            break
    
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f'[OK] Fixed structure')
else:
    print('[ERROR] Could not find subsection')
