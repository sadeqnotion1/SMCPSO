@echo off
echo.
echo =====================================================
echo  Step 1: Close your browser showing the docs
echo =====================================================
echo.
echo Please close the browser tab/window showing:
echo file:///D:/Projects/main/docs/_build/html/index.html
echo.
pause
echo.
echo =====================================================
echo  Step 2: Cleaning and rebuilding documentation...
echo =====================================================
echo.
cd /d D:\Projects\main\docs
rmdir /s /q _build 2>nul
python -m sphinx . _build/html
echo.
echo =====================================================
echo  Step 3: Open the rebuilt documentation
echo =====================================================
echo.
echo Opening: D:\Projects\main\docs\_build\html\index.html
echo.
start _build\html\index.html
echo.
echo Done! You should see the new Modern Colorful theme with:
echo - Animated admonitions (note, tip, warning, danger, success)
echo - Gradient status badges (stable, experimental, beta)
echo - Modern tables with #0b2763 dark blue header
echo - Smooth hover effects and transitions
echo.
pause
