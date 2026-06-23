@echo off
cd /d "%~dp0"
set "MIKTEX=C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe"
set "TEXFILE=EP001_unified"
set "TIMESTAMP=%date:~-4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"
set "PDFFILE=%TEXFILE%_v%TIMESTAMP%.pdf"

echo [INFO] Compiling %TEXFILE%.tex -> %PDFFILE%
echo [INFO] MiKTeX path: %MIKTEX%

if not exist "%MIKTEX%" (
    echo [ERROR] MiKTeX not found at %MIKTEX%
    pause
    exit /b 1
)

del /f /q %TEXFILE%.pdf %TEXFILE%.aux %TEXFILE%.log 2>nul

for /L %%i in (1,1,4) do (
    echo   [INFO] Pass %%i/4...
    "%MIKTEX%" -interaction=nonstopmode %TEXFILE%.tex
    if errorlevel 1 (
        echo   [WARN] Pass %%i returned error
    )
)

if exist %PDFFILE% (
    echo.
    echo [OK] PDF created: %PDFFILE%
    for %%F in (%PDFFILE%) do echo [OK] Size: %%~zF bytes
    echo.
    echo [INFO] Verify sections with: type %TEXFILE%.log | findstr "section"
    pause
) else (
    echo.
    echo [ERROR] PDF not created
    echo [INFO] Check %TEXFILE%.log for errors
    pause
    exit /b 1
)
