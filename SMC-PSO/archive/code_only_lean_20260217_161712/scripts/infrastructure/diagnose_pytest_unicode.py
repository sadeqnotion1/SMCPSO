#!/usr/bin/env python
"""
Diagnostic Tool for pytest Unicode Encoding Issues on Windows
==============================================================

This script diagnoses and reports on the current encoding configuration
to help identify and resolve pytest Unicode display issues on Windows.

The main issue: Windows terminals use cp1252 encoding by default, which
cannot display Unicode characters (checkmarks, arrows, etc.) that pytest
uses in its output, causing crashes or garbled output.

Usage:
    python scripts/diagnose_pytest_unicode.py
"""

import sys
import os
import locale
import platform
from pathlib import Path


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def get_encoding_info(stream_name: str) -> dict:
    """Get encoding information for a given stream."""
    stream = getattr(sys, stream_name, None)
    if stream is None:
        return {"exists": False}

    info = {"exists": True}

    # Get encoding
    if hasattr(stream, "encoding"):
        info["encoding"] = stream.encoding
    else:
        info["encoding"] = "unknown"

    # Check if it has buffer
    info["has_buffer"] = hasattr(stream, "buffer")

    # Check if it supports reconfigure
    info["supports_reconfigure"] = hasattr(stream, "reconfigure")

    return info


def test_unicode_output() -> dict:
    """Test if Unicode characters can be printed without errors."""
    test_chars = {
        "checkmark": "\u2713",
        "cross": "\u2717",
        "arrow": "\u2192",
        "block": "\u2588",
        "warning": "\u26A0",
        "bullet": "\u2022",
    }

    results = {}
    for name, char in test_chars.items():
        try:
            # Try to encode with current stdout encoding
            char.encode(sys.stdout.encoding or "utf-8")
            results[name] = {"char": char, "status": "OK"}
        except (UnicodeEncodeError, AttributeError) as e:
            results[name] = {"char": char, "status": f"FAIL: {type(e).__name__}"}

    return results


def main():
    """Run complete diagnostic and print report."""

    print_section("PLATFORM INFORMATION")
    print(f"Platform: {platform.system()} ({platform.platform()})")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")

    print_section("LOCALE INFORMATION")
    try:
        preferred_encoding = locale.getpreferredencoding()
        print(f"Preferred Encoding: {preferred_encoding}")
    except Exception as e:
        print(f"Preferred Encoding: ERROR - {e}")

    try:
        default_locale = locale.getdefaultlocale()
        print(f"Default Locale: {default_locale}")
    except Exception as e:
        print(f"Default Locale: ERROR - {e}")

    print_section("ENVIRONMENT VARIABLES")
    env_vars = [
        "PYTHONIOENCODING",
        "PYTHONUTF8",
        "PYTHONLEGACYWINDOWSSTDIO",
        "LC_ALL",
        "LANG",
    ]

    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"{var}: {value}")
        else:
            print(f"{var}: [NOT SET]")

    print_section("STREAM ENCODING INFORMATION")
    for stream_name in ["stdin", "stdout", "stderr"]:
        info = get_encoding_info(stream_name)
        print(f"{stream_name}:")
        if info["exists"]:
            print(f"  Encoding: {info.get('encoding', 'unknown')}")
            print(f"  Has Buffer: {info.get('has_buffer', False)}")
            print(f"  Supports Reconfigure: {info.get('supports_reconfigure', False)}")
        else:
            print(f"  [STREAM DOES NOT EXIST]")
        print()

    print_section("FILESYSTEM ENCODING")
    try:
        fs_encoding = sys.getfilesystemencoding()
        print(f"Filesystem Encoding: {fs_encoding}")
    except Exception as e:
        print(f"Filesystem Encoding: ERROR - {e}")

    print_section("UNICODE CHARACTER TEST")
    results = test_unicode_output()

    all_ok = True
    for name, result in results.items():
        status = result["status"]
        char = result["char"]
        if status == "OK":
            print(f"  [{char}] {name}: {status}")
        else:
            print(f"  [?] {name}: {status}")
            all_ok = False

    print()
    if all_ok:
        print("[INFO] All Unicode characters can be encoded successfully!")
    else:
        print("[WARNING] Some Unicode characters cannot be encoded.")
        print("[WARNING] pytest may have issues displaying Unicode symbols.")

    print_section("RECOMMENDATIONS")

    if os.name == "nt":  # Windows
        stdout_encoding = sys.stdout.encoding if hasattr(sys.stdout, "encoding") else "unknown"

        if stdout_encoding and "utf" not in stdout_encoding.lower():
            print("[ACTION NEEDED] stdout encoding is not UTF-8")
            print()
            print("SOLUTION 1 (Environment Variable - RECOMMENDED):")
            print("  Set environment variable before running pytest:")
            print("    set PYTHONIOENCODING=utf-8")
            print("    python -m pytest")
            print()
            print("SOLUTION 2 (Batch Wrapper):")
            print("  Create run_tests.bat with:")
            print("    @echo off")
            print("    set PYTHONIOENCODING=utf-8")
            print("    python -m pytest %*")
            print()
            print("SOLUTION 3 (conftest.py Hook - ALREADY IMPLEMENTED):")
            print("  Add UTF-8 enforcement in tests/conftest.py")
            print("  [STATUS] Already implemented in this project!")
            print()
        else:
            print("[OK] stdout encoding is UTF-8 compatible")
            print()
            print("Current configuration:")
            if "PYTHONIOENCODING" in os.environ:
                print(f"  - PYTHONIOENCODING: {os.environ['PYTHONIOENCODING']}")
            if "PYTHONUTF8" in os.environ:
                print(f"  - PYTHONUTF8: {os.environ['PYTHONUTF8']}")

            # Check if conftest.py has UTF-8 enforcement
            conftest_path = Path("tests/conftest.py")
            if conftest_path.exists():
                content = conftest_path.read_text(encoding="utf-8")
                if "PYTHONIOENCODING" in content or "PYTHONUTF8" in content:
                    print("  - conftest.py has UTF-8 enforcement [OK]")
    else:
        print("[OK] Not running on Windows - Unicode encoding should work by default")

    print("\n" + "=" * 70)
    print("  DIAGNOSTIC COMPLETE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
