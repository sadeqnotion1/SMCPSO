#!/usr/bin/env python
"""
Test execution script for automated browser testing.

Usage:
    python run_tests.py                      # Run all tests in Chromium
    python run_tests.py --browser firefox    # Run in Firefox
    python run_tests.py --functional         # Run only functional tests
    python run_tests.py --all-browsers       # Run in Chromium, Firefox, Webkit
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import argparse


def run_tests(browser="chromium", test_category=None, all_browsers=False, headed=False):
    """
    Run pytest with specified options.

    Args:
        browser: Browser name (chromium, firefox, webkit)
        test_category: Test category marker (functional, performance, etc.)
        all_browsers: Run tests in all browsers
        headed: Run browser in headed mode (visible)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if all_browsers:
        browsers = ["chromium", "firefox"]
        for browser_name in browsers:
            print(f"\n{'='*80}")
            print(f"Running tests in {browser_name.upper()}")
            print(f"{'='*80}\n")
            _run_single_browser(browser_name, test_category, headed, timestamp)
    else:
        _run_single_browser(browser, test_category, headed, timestamp)


def _run_single_browser(browser, test_category, headed, timestamp):
    """Run tests in a single browser."""
    cmd = [
        "pytest",
        "tests/browser_automation/test_code_collapse_comprehensive.py",
        f"--browser={browser}",
        "-v",
        "--tb=short",
        f"--html=.cache/browser_automation/artifacts/reports/report_{browser}_{timestamp}.html",
        "--self-contained-html"
    ]

    if test_category:
        cmd.append(f"-m {test_category}")

    if headed:
        # Headed mode would require modifying conftest.py to use headless=False
        print("Note: Headed mode not yet implemented in conftest.py")

    print(f"Running command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent)

    if result.returncode != 0:
        print(f"\n[FAIL] Tests failed in {browser}")
    else:
        print(f"\n[PASS] Tests passed in {browser}")

    return result.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run automated browser tests for code collapse feature")

    parser.add_argument("--browser", choices=["chromium", "firefox", "webkit"],
                       default="chromium", help="Browser to test (default: chromium)")

    parser.add_argument("--all-browsers", action="store_true",
                       help="Run tests in all browsers")

    parser.add_argument("--functional", action="store_true",
                       help="Run only functional tests")

    parser.add_argument("--performance", action="store_true",
                       help="Run only performance tests")

    parser.add_argument("--accessibility", action="store_true",
                       help="Run only accessibility tests")

    parser.add_argument("--regression", action="store_true",
                       help="Run only regression tests")

    parser.add_argument("--edge-case", action="store_true",
                       help="Run only edge case tests")

    parser.add_argument("--headed", action="store_true",
                       help="Run browser in headed mode (visible)")

    args = parser.parse_args()

    # Determine test category
    test_category = None
    if args.functional:
        test_category = "functional"
    elif args.performance:
        test_category = "performance"
    elif args.accessibility:
        test_category = "accessibility"
    elif args.regression:
        test_category = "regression"
    elif args.edge_case:
        test_category = "edge_case"

    # Run tests
    exit_code = run_tests(
        browser=args.browser,
        test_category=test_category,
        all_browsers=args.all_browsers,
        headed=args.headed
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
