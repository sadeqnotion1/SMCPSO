import subprocess
import os

os.chdir(r'D:\Projects\main\academic\learning\ep001_physical_system_description')

miktex = r'C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe'

print(f'MiKTeX path exists: {os.path.exists(miktex)}')
print(f'TEX file exists: {os.path.exists("EP001_unified.tex")}')

# Try with full path quoting
cmd = f'"{miktex}" -interaction=nonstopmode "EP001_unified.tex"'
print(f'Command: {cmd}')

try:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print('STDOUT:', result.stdout[:500] if result.stdout else 'None')
    print('STDERR:', result.stderr[:500] if result.stderr else 'None')
    print('Return code:', result.returncode)
except Exception as e:
    print(f'Exception: {e}')
