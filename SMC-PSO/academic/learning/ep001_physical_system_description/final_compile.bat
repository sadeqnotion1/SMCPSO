@echo off
cd /d D:\Projects\main\academic\learning\ep001_physical_system_description
echo [INFO] Final compilation with clean hyperref settings...
del /f /q EP001_unified.pdf EP001_unified.aux EP001_unified.log EP001_unified.out 2>nul

"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex > compile_log.txt 2>&1
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex >> compile_log.txt 2>&1
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex >> compile_log.txt 2>&1
"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode EP001_unified.tex >> compile_log.txt 2>&1

echo [OK] Compilation complete!
echo.
echo PDF file: EP001_unified.pdf
echo Size:
for %%F in (EP001_unified.pdf) do echo   %%~zF bytes
echo.
echo Check compile_log.txt for any errors/warnings
pause
