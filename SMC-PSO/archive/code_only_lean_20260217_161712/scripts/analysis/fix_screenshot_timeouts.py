#!/usr/bin/env python3
"""
===============================================================================
                    Screenshot Timeout Fix Script
===============================================================================
File: scripts/analysis/fix_screenshot_timeouts.py
Purpose: Re-capture failed pages with optimized timeout settings
===============================================================================
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# Failed pages from visual audit
FAILED_PAGES = [
    "docs/_build/html/coverage_analysis_methodology.html",
    "docs/_build/html/genindex.html"
]


async def capture_with_optimized_settings(page, html_file: Path, screenshot_path: Path):
    """Capture screenshot with optimized timeout settings."""
    file_url = html_file.as_uri()

    try:
        print(f"\n🔄 Attempting: {html_file.name}")

        # Strategy 1: Use 'domcontentloaded' instead of 'networkidle'
        print("  Strategy: domcontentloaded (60s timeout)")
        await page.goto(file_url, wait_until="domcontentloaded", timeout=60000)

        # Wait for body to be ready
        await page.wait_for_selector("body", timeout=10000)

        # Additional wait for any heavy rendering
        await asyncio.sleep(2)

        # Take screenshot
        await page.screenshot(path=str(screenshot_path), full_page=True)

        print(f"  ✅ SUCCESS: {screenshot_path.name}")
        return True

    except Exception as e:
        print(f"  ❌ FAILED: {e}")

        # Fallback: Try with 'load' strategy
        try:
            print("  🔄 Fallback: load strategy")
            await page.goto(file_url, wait_until="load", timeout=90000)
            await asyncio.sleep(3)
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"  ✅ FALLBACK SUCCESS: {screenshot_path.name}")
            return True
        except Exception as e2:
            print(f"  ❌ FALLBACK FAILED: {e2}")
            return False


async def main():
    """Re-capture failed pages."""
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / ".test_artifacts" / "doc_screenshots"

    print("🔧 Screenshot Timeout Fix Tool")
    print(f"📂 Output directory: {output_dir}")
    print(f"📄 Pages to retry: {len(FAILED_PAGES)}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        success_count = 0

        for html_path in FAILED_PAGES:
            html_file = project_root / html_path

            if not html_file.exists():
                print(f"❌ File not found: {html_file}")
                continue

            # Generate screenshot filename
            rel_path = html_file.relative_to(project_root / "docs/_build/html")
            screenshot_name = str(rel_path).replace("\\", "_").replace("/", "_").replace(".html", ".png")
            screenshot_path = output_dir / screenshot_name

            result = await capture_with_optimized_settings(page, html_file, screenshot_path)
            if result:
                success_count += 1

        await browser.close()

        print(f"\n{'='*70}")
        print(f"✅ Successfully captured: {success_count}/{len(FAILED_PAGES)}")
        print(f"❌ Failed: {len(FAILED_PAGES) - success_count}/{len(FAILED_PAGES)}")
        print(f"{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())
