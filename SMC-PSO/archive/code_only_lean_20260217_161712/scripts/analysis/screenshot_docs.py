#!/usr/bin/env python3
"""
===============================================================================
                    DIP-SMC-PSO Documentation Screenshot Generator
===============================================================================
File: scripts/analysis/screenshot_docs.py
Purpose: Automated visual documentation audit via browser screenshots
===============================================================================
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict
from playwright.async_api import async_playwright
import sys
import io

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class DocumentationScreenshotter:
    """Automated screenshot generator for HTML documentation."""

    # Viewport presets for different devices
    VIEWPORTS = {
        "desktop": {"width": 1920, "height": 1080},
        "mobile": {"width": 375, "height": 812},   # iPhone 13
        "tablet": {"width": 768, "height": 1024},  # iPad
    }

    def __init__(
        self,
        docs_dir: Path,
        output_dir: Path,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        viewport_preset: str = "desktop",
        image_format: str = "png",
        image_quality: int = 85
    ):
        """
        Initialize screenshot generator.

        Args:
            docs_dir: Path to docs/_build/html/ directory
            output_dir: Path to save screenshots
            viewport_width: Browser viewport width in pixels (overridden by preset)
            viewport_height: Browser viewport height in pixels (overridden by preset)
            viewport_preset: Viewport preset ("desktop", "mobile", "tablet")
            image_format: Screenshot format ("png", "jpeg", "webp")
            image_quality: Quality for lossy formats (1-100, default: 85)
        """
        self.docs_dir = Path(docs_dir)
        self.output_dir = Path(output_dir)
        self.viewport_preset = viewport_preset
        self.image_format = image_format
        self.image_quality = image_quality

        # Apply viewport preset if specified
        if viewport_preset in self.VIEWPORTS:
            viewport = self.VIEWPORTS[viewport_preset]
            self.viewport_width = viewport["width"]
            self.viewport_height = viewport["height"]
        else:
            self.viewport_width = viewport_width
            self.viewport_height = viewport_height

        self.screenshot_index: List[Dict[str, str]] = []

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def find_html_files(self) -> List[Path]:
        """Find all HTML files in documentation directory."""
        html_files = sorted(self.docs_dir.rglob("*.html"))
        print(f"📁 Found {len(html_files)} HTML files")
        return html_files

    def get_screenshot_path(self, html_file: Path) -> Path:
        """Generate screenshot path from HTML file path."""
        # Create relative path structure
        rel_path = html_file.relative_to(self.docs_dir)

        # Determine file extension based on image format
        extension = f".{self.image_format}"

        # Convert path to safe filename: path/to/file.html -> path_to_file.png
        screenshot_name = str(rel_path).replace("\\", "_").replace("/", "_").replace(".html", extension)

        return self.output_dir / screenshot_name

    async def capture_screenshot(
        self,
        page,
        html_file: Path,
        screenshot_path: Path
    ):
        """
        Capture full-page screenshot of HTML file.

        Args:
            page: Playwright browser page instance
            html_file: Path to HTML file to capture
            screenshot_path: Path to save screenshot
        """
        # Convert to file:// URL
        file_url = html_file.as_uri()

        try:
            # Navigate to page
            await page.goto(file_url, wait_until="networkidle", timeout=30000)

            # Wait for Mermaid diagrams to render (if present)
            try:
                await page.wait_for_selector(".mermaid svg", timeout=5000)
                print("  ✅ Mermaid diagram detected and rendered")
            except Exception:  # noqa: E722
                pass  # No Mermaid diagrams on this page

            # Configure screenshot options based on format
            screenshot_options = {
                "path": str(screenshot_path),
                "full_page": True,
            }

            if self.image_format in ["jpeg", "webp"]:
                screenshot_options["type"] = self.image_format
                screenshot_options["quality"] = self.image_quality
            else:
                screenshot_options["type"] = "png"

            # Take full-page screenshot
            await page.screenshot(**screenshot_options)

            # Log file size for format comparison
            file_size_mb = screenshot_path.stat().st_size / 1024 / 1024
            print(f"  💾 Saved: {screenshot_path.name} ({file_size_mb:.2f} MB)")

            # Get page title
            page_title = await page.title()

            # Record in index
            self.screenshot_index.append({
                "html_file": str(html_file.relative_to(self.docs_dir)),
                "screenshot": str(screenshot_path.relative_to(self.output_dir)),
                "title": page_title,
                "url": file_url
            })

            print(f"✅ {html_file.name} → {screenshot_path.name}")

        except Exception as e:
            print(f"❌ Failed to capture {html_file.name}: {e}")

    async def generate_all_screenshots(self):
        """Generate screenshots for all HTML files."""
        html_files = self.find_html_files()

        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)

            # Create browser context with viewport settings
            context = await browser.new_context(
                viewport={"width": self.viewport_width, "height": self.viewport_height}
            )

            # Create page
            page = await context.new_page()

            print("\n📸 Generating screenshots...\n")

            # Capture screenshots
            for html_file in html_files:
                screenshot_path = self.get_screenshot_path(html_file)
                await self.capture_screenshot(page, html_file, screenshot_path)

            # Close browser
            await browser.close()

        # Save screenshot index
        index_path = self.output_dir / "screenshot_index.json"
        with open(index_path, "w") as f:
            json.dump(self.screenshot_index, f, indent=2)

        print(f"\n✅ Generated {len(self.screenshot_index)} screenshots")
        print(f"📊 Screenshot index: {index_path}")


async def main():
    """Main entry point."""
    import argparse

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Generate screenshots of documentation pages with configurable viewports and formats"
    )
    parser.add_argument(
        '--viewport',
        choices=['desktop', 'mobile', 'tablet'],
        default='desktop',
        help='Viewport preset for screenshots (default: desktop)'
    )
    parser.add_argument(
        '--format',
        choices=['png', 'jpeg', 'webp'],
        default='png',
        help='Screenshot image format (default: png)'
    )
    parser.add_argument(
        '--quality',
        type=int,
        default=85,
        help='Quality for jpeg/webp formats, 1-100 (default: 85)'
    )

    args = parser.parse_args()

    # Configuration
    project_root = Path(__file__).parent.parent.parent
    docs_dir = project_root / "docs" / "_build" / "html"

    # Adjust output directory based on viewport and format
    if args.viewport != "desktop" or args.format != "png":
        output_dir = project_root / ".test_artifacts" / f"doc_screenshots_{args.viewport}_{args.format}"
    else:
        output_dir = project_root / ".test_artifacts" / "doc_screenshots"

    # Verify docs exist
    if not docs_dir.exists():
        print(f"❌ Documentation directory not found: {docs_dir}")
        print("   Run: sphinx-build -b html docs docs/_build/html")
        sys.exit(1)

    # Display configuration
    print("📸 Screenshot Configuration:")
    print(f"   Viewport: {args.viewport}")
    print(f"   Format: {args.format.upper()}")
    if args.format in ["jpeg", "webp"]:
        print(f"   Quality: {args.quality}%")
    print()

    # Create screenshotter
    screenshotter = DocumentationScreenshotter(
        docs_dir=docs_dir,
        output_dir=output_dir,
        viewport_preset=args.viewport,
        image_format=args.format,
        image_quality=args.quality
    )

    # Generate screenshots
    await screenshotter.generate_all_screenshots()

    print(f"\n📂 Screenshots saved to: {output_dir}")
    print(f"\n🔍 Next step: Visual analysis of {len(screenshotter.screenshot_index)} screenshots")


if __name__ == "__main__":
    asyncio.run(main())
