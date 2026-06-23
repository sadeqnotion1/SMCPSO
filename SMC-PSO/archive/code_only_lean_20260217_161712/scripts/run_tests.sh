#!/bin/bash
################################################################################
# Pytest Test Runner for Unix/Linux/Mac
################################################################################
#
# This script ensures UTF-8 encoding for pytest output.
#
# Usage:
#   ./run_tests.sh                    (run all tests)
#   ./run_tests.sh -v                 (verbose output)
#   ./run_tests.sh tests/test_*.py    (specific test file)
#   ./run_tests.sh -k "test_name"     (run tests matching name)
#
# Note: conftest.py already enforces UTF-8 encoding, but this wrapper
#       provides explicit environment variable setup as defense-in-depth.
#
################################################################################

# Set UTF-8 encoding for Python I/O
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

# Run pytest with all arguments passed through
python -m pytest "$@"
