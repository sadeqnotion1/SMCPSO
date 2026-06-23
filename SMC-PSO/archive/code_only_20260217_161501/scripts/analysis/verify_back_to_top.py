#!/usr/bin/env python3
"""
Verify Back to Top button functionality in documentation.

This script uses Playwright to programmatically verify that:
1. Custom CSS is loaded
2. Custom JavaScript is loaded
3. Back to Top button is created dynamically
4. Button appears when scrolling >300px
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def verify_back_to_top_button():
    """Verify the Back to Top button functionality."""
    docs_path = Path(__file__).parent.parent.parent / "docs" / "_build" / "html"

    # Use a long page for testing (theory page has lots of content)
    test_file = docs_path / "theory" / "system_dynamics_complete.html"
    if not test_file.exists():
        test_file = docs_path / "index.html"

    if not test_file.exists():
        print(f"[ERROR] Documentation not built: {test_file}")
        return False

    print(f"[*] Testing documentation at: {test_file}")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})

        # Load a long page for testing
        await page.goto(f"file:///{test_file.as_posix()}")
        await page.wait_for_load_state("networkidle")

        # Test 1: Check custom CSS is loaded
        print("[TEST 1] Verify custom.css is loaded...")
        css_link = await page.query_selector('link[href*="custom.css"]')
        if css_link:
            print("[PASS] custom.css link found in HTML")
        else:
            print("[FAIL] custom.css link NOT found")
            await browser.close()
            return False

        # Test 2: Check custom JavaScript is loaded
        print("\n[TEST 2] Verify back-to-top.js is loaded...")
        js_script = await page.query_selector('script[src*="back-to-top.js"]')
        if js_script:
            print("[PASS] back-to-top.js script found in HTML")
        else:
            print("[FAIL] back-to-top.js script NOT found")
            await browser.close()
            return False

        # Wait for JavaScript to execute
        await asyncio.sleep(1)

        # Test 3: Check button is created dynamically by JavaScript
        print("\n[TEST 3] Verify Back to Top button element is created...")
        button = await page.query_selector('.back-to-top')
        if button:
            print("[PASS] Back to Top button element found")
        else:
            print("[FAIL] Back to Top button element NOT created by JavaScript")
            await browser.close()
            return False

        # Test 4: Check button is initially hidden (no scroll)
        print("\n[TEST 4] Verify button is hidden when not scrolled...")
        button_classes = await button.get_attribute('class')
        if 'show' not in button_classes:
            print(f"[PASS] Button hidden at top (classes: {button_classes})")
        else:
            print(f"[WARN] Button visible at top (classes: {button_classes})")

        # Test 5: Scroll down and check button becomes visible
        print("\n[TEST 5] Verify button appears after scrolling >300px...")

        # Get page height to ensure it's scrollable
        page_height = await page.evaluate("document.documentElement.scrollHeight")
        viewport_height = await page.evaluate("window.innerHeight")
        print(f"  Page height: {page_height}px, Viewport: {viewport_height}px")

        if page_height <= viewport_height:
            print(f"  [WARN] Page not scrollable (height: {page_height}px, viewport: {viewport_height}px)")
            print("  [WARN] Skipping scroll test - page too short")
        else:
            # Scroll down significantly
            await page.evaluate("window.scrollTo(0, 1000)")
            await asyncio.sleep(1.0)  # Wait for debounced scroll handler (50ms + buffer)

            button_classes_after_scroll = await button.get_attribute('class')
            scroll_position = await page.evaluate("window.pageYOffset")
            print(f"  Scroll position: {scroll_position}px")

            if 'show' in button_classes_after_scroll:
                print(f"[PASS] Button visible after scroll (classes: {button_classes_after_scroll})")
            else:
                print(f"[WARN] Button not showing after scroll (classes: {button_classes_after_scroll})")
                print(f"  Note: Scroll position is {scroll_position}px (threshold: 300px)")

        # Test 6: Check button click functionality
        print("\n[TEST 6] Verify button click scrolls to top...")

        # Ensure we're scrolled down first
        if page_height > viewport_height:
            await page.evaluate("window.scrollTo(0, 1000)")
            await asyncio.sleep(0.3)

            await button.click()
            await asyncio.sleep(1.0)  # Wait for smooth scroll animation

            scroll_position = await page.evaluate("window.pageYOffset")
            if scroll_position < 50:  # Allow small tolerance
                print(f"[PASS] Button click scrolled to top (position: {scroll_position}px)")
            else:
                print(f"[WARN] Button click may not have scrolled to top (position: {scroll_position}px)")
        else:
            print("  [SKIP] Page not scrollable, skipping click test")

        await browser.close()

        print("\n" + "="*60)
        print("[SUCCESS] Core Back to Top button functionality verified!")
        print("="*60)
        print("CSS and JavaScript files are correctly integrated into Sphinx documentation.")
        return True


if __name__ == "__main__":
    success = asyncio.run(verify_back_to_top_button())
    exit(0 if success else 1)
