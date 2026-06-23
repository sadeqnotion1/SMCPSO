"""
Create baseline screenshots for visual regression testing.

Captures key states of collapsible code blocks feature:
- Default state (all expanded)
- All collapsed
- Single block collapsed
- Mobile viewport
- Dark mode (if applicable)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from playwright.sync_api import sync_playwright
from utils.playwright_helper import PlaywrightHelper
from utils.screenshot_manager import ScreenshotManager


def create_baselines():
    """Create baseline screenshots for visual regression testing."""

    artifacts_path = Path(".cache/browser_automation/artifacts")
    screenshot_manager = ScreenshotManager(artifacts_path)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        helper = PlaywrightHelper(page, base_path=artifacts_path)

        print("Creating baseline screenshots...")
        print("=" * 60)

        # Baseline 1: Default state (all expanded)
        print("\n1. Capturing default state (all expanded)...")
        helper.goto_docs()
        screenshot_path = helper.take_screenshot("baseline_01_default_expanded")
        screenshot_manager.save_screenshot(screenshot_path, "baseline_01_default_expanded", is_baseline=True)
        print(f"   [OK] Saved: {screenshot_path.name}")

        # Baseline 2: All collapsed
        print("\n2. Capturing all collapsed state...")
        helper.collapse_all(wait_for_animation=True)
        screenshot_path = helper.take_screenshot("baseline_02_all_collapsed")
        screenshot_manager.save_screenshot(screenshot_path, "baseline_02_all_collapsed", is_baseline=True)
        print(f"   [OK] Saved: {screenshot_path.name}")

        # Baseline 3: First block collapsed
        print("\n3. Capturing first block collapsed...")
        helper.expand_all(wait_for_animation=True)
        helper.collapse_block(index=0, wait_for_animation=True)
        screenshot_path = helper.take_screenshot("baseline_03_first_collapsed")
        screenshot_manager.save_screenshot(screenshot_path, "baseline_03_first_collapsed", is_baseline=True)
        print(f"   [OK] Saved: {screenshot_path.name}")

        # Baseline 4: Mobile viewport (320x568)
        print("\n4. Capturing mobile viewport (iPhone SE)...")
        helper.set_viewport_size(320, 568)
        helper.goto_docs()
        screenshot_path = helper.take_screenshot("baseline_04_mobile_320px")
        screenshot_manager.save_screenshot(screenshot_path, "baseline_04_mobile_320px", is_baseline=True)
        print(f"   [OK] Saved: {screenshot_path.name}")

        # Baseline 5: Tablet viewport (768x1024)
        print("\n5. Capturing tablet viewport (iPad)...")
        helper.set_viewport_size(768, 1024)
        helper.goto_docs()
        screenshot_path = helper.take_screenshot("baseline_05_tablet_768px")
        screenshot_manager.save_screenshot(screenshot_path, "baseline_05_tablet_768px", is_baseline=True)
        print(f"   [OK] Saved: {screenshot_path.name}")

        # Baseline 6: Master controls visible
        print("\n6. Capturing master controls...")
        helper.set_viewport_size(1280, 720)
        helper.goto_docs()
        # Take element screenshot of master controls
        controls = page.query_selector(".code-controls-master")
        if controls:
            controls.screenshot(path=str(artifacts_path / "screenshots/baseline/baseline_06_master_controls.png"))
            print(f"   [OK] Saved: baseline_06_master_controls.png")

        # Baseline 7: Single code block with buttons
        print("\n7. Capturing single code block detail...")
        first_block = page.query_selector(".collapsible-processed")
        if first_block:
            first_block.screenshot(path=str(artifacts_path / "screenshots/baseline/baseline_07_code_block_detail.png"))
            print(f"   [OK] Saved: baseline_07_code_block_detail.png")

        browser.close()

        print("\n" + "=" * 60)
        print("[OK] Baseline screenshots created successfully!")
        print(f"  Location: {screenshot_manager.baseline_path}")
        print(f"  Total: 7 baseline images")
        print("\nTo use for visual regression testing:")
        print("  1. Review baselines to ensure they look correct")
        print("  2. Run tests with --baseline-compare flag")
        print("  3. Any visual changes will be flagged as diffs")


if __name__ == "__main__":
    create_baselines()
