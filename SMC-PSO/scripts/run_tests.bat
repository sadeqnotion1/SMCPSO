@echo off
REM ==============================================================================
REM Pytest Test Runner for Windows
REM ==============================================================================
REM
REM This script ensures UTF-8 encoding for pytest output on Windows.
REM
REM Usage:
REM   run_tests.bat                    (run all tests)
REM   run_tests.bat -v                 (verbose output)
REM   run_tests.bat tests/test_*.py    (specific test file)
REM   run_tests.bat -k "test_name"     (run tests matching name)
REM
REM Note: conftest.py already enforces UTF-8 encoding, but this wrapper
REM       provides explicit environment variable setup as defense-in-depth.
REM
REM ==============================================================================

REM Set UTF-8 encoding for Python I/O
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM Run pytest with all arguments passed through
python -m pytest %*
