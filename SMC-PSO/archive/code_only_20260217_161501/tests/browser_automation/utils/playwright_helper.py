"""
Playwright helper utilities for automated browser testing.

Provides high-level abstractions for common Playwright operations including
navigation, console log capture, screenshot management, and animation timing.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import re


class PlaywrightHelper:
    """
    High-level wrapper for Playwright page operations.

    Simplifies common testing tasks like navigation, console log capture,
    element interaction, and screenshot capture.
    """

    def __init__(self, page, base_path: Optional[Path] = None):
        """
        Initialize the Playwright helper.

        Args:
            page: Playwright Page object
            base_path: Base path for artifacts (screenshots, logs)
        """
        self.page = page
        self.base_path = base_path or Path(".cache/browser_automation/artifacts")
        self.console_logs: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []

        # Set up console listeners
        self.page.on("console", self._handle_console)
        self.page.on("pageerror", self._handle_error)

    def _handle_console(self, msg):
        """Capture console messages."""
        self.console_logs.append({
            "type": msg.type,
            "text": msg.text,
            "timestamp": datetime.now().isoformat()
        })

    def _handle_error(self, error):
        """Capture JavaScript errors."""
        self.errors.append({
            "message": str(error),
            "timestamp": datetime.now().isoformat()
        })

    def goto_docs(self, page_path: str = "index.html") -> None:
        """
        Navigate to documentation page.

        Args:
            page_path: Relative path from docs/_build/html/ (default: index.html)
        """
        # Use file:// protocol for local files
        # Find project root (where docs/ directory is)
        current_file = Path(__file__).resolve()
        project_root = current_file.parents[3]  # Go up from utils/ -> browser_automation/ -> tests/ -> main/
        docs_path = project_root / "docs/_build/html" / page_path

        if not docs_path.exists():
            raise FileNotFoundError(f"Documentation file not found: {docs_path}")

        url = f"file:///{docs_path.as_posix()}"

        self.page.goto(url, wait_until="networkidle")
        self.page.wait_for_load_state("domcontentloaded")

        # Wait for code-collapse.js to initialize
        # The script exposes window.clearCodeBlockStates when loaded
        self.page.wait_for_function("typeof window.clearCodeBlockStates !== 'undefined'", timeout=10000)

    def get_console_logs(self, filter_pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get captured console logs, optionally filtered.

        Args:
            filter_pattern: Regex pattern to filter log messages

        Returns:
            List of console log dictionaries
        """
        if not filter_pattern:
            return self.console_logs

        pattern = re.compile(filter_pattern)
        return [log for log in self.console_logs if pattern.search(log["text"])]

    def get_code_collapse_logs(self) -> List[Dict[str, Any]]:
        """Get console logs from code-collapse.js (starting with [CodeCollapse])."""
        return self.get_console_logs(r"\[CodeCollapse\]")

    def check_coverage_report(self) -> Dict[str, Any]:
        """
        Parse coverage report from console logs.

        Returns:
            Dictionary with coverage statistics
        """
        logs = self.get_code_collapse_logs()

        coverage = {
            "total_blocks": 0,
            "matched_blocks": 0,
            "unmatched_blocks": 0,
            "coverage_percent": 0.0,
            "has_100_coverage": False
        }

        for log in logs:
            text = log["text"]

            # Extract total blocks
            if match := re.search(r"Found (\d+) code blocks", text):
                coverage["total_blocks"] = int(match.group(1))

            # Check for 100% coverage message
            if "✅ 100% coverage" in text:
                coverage["has_100_coverage"] = True
                coverage["matched_blocks"] = coverage["total_blocks"]
                coverage["coverage_percent"] = 100.0

            # Extract unmatched count
            if match := re.search(r"⚠️ (\d+) unmatched", text):
                coverage["unmatched_blocks"] = int(match.group(1))
                coverage["matched_blocks"] = coverage["total_blocks"] - coverage["unmatched_blocks"]
                coverage["coverage_percent"] = (coverage["matched_blocks"] / coverage["total_blocks"] * 100
                                                if coverage["total_blocks"] > 0 else 0)

        return coverage

    def get_collapse_buttons(self):
        """Get all collapse button elements."""
        return self.page.query_selector_all(".code-collapse-btn")

    def get_code_blocks(self):
        """
        Get all code block container elements that were processed by code-collapse.js.

        Returns only blocks that have buttons inserted (marked with .collapsible-processed).
        """
        return self.page.query_selector_all(".collapsible-processed")

    def collapse_block(self, index: int = 0, wait_for_animation: bool = True) -> None:
        """
        Collapse a specific code block by index.

        Args:
            index: Index of code block (0-based)
            wait_for_animation: Whether to wait for animation to complete
        """
        buttons = self.get_collapse_buttons()
        if index >= len(buttons):
            raise IndexError(f"Code block index {index} out of range (max: {len(buttons)-1})")

        button = buttons[index]

        # Check if already collapsed
        is_collapsed = button.get_attribute("aria-expanded") == "false"
        if is_collapsed:
            return  # Already collapsed

        button.click()

        if wait_for_animation:
            self.wait_for_animation()

    def expand_block(self, index: int = 0, wait_for_animation: bool = True) -> None:
        """
        Expand a specific code block by index.

        Args:
            index: Index of code block (0-based)
            wait_for_animation: Whether to wait for animation to complete
        """
        buttons = self.get_collapse_buttons()
        if index >= len(buttons):
            raise IndexError(f"Code block index {index} out of range (max: {len(buttons)-1})")

        button = buttons[index]

        # Check if already expanded
        is_expanded = button.get_attribute("aria-expanded") == "true"
        if is_expanded:
            return  # Already expanded

        button.click()

        if wait_for_animation:
            self.wait_for_animation()

    def collapse_all(self, wait_for_animation: bool = True) -> None:
        """Collapse all code blocks using master control."""
        collapse_all_btn = self.page.query_selector("button.code-control-btn:has-text('Collapse All')")
        if not collapse_all_btn:
            raise RuntimeError("Collapse All button not found")

        collapse_all_btn.click()

        if wait_for_animation:
            self.wait_for_animation(duration_ms=500)  # Longer for stagger effect

    def expand_all(self, wait_for_animation: bool = True) -> None:
        """Expand all code blocks using master control."""
        expand_all_btn = self.page.query_selector("button.code-control-btn:has-text('Expand All')")
        if not expand_all_btn:
            raise RuntimeError("Expand All button not found")

        expand_all_btn.click()

        if wait_for_animation:
            self.wait_for_animation(duration_ms=500)

    def wait_for_animation(self, duration_ms: int = 400) -> None:
        """
        Wait for collapse/expand animation to complete.

        Args:
            duration_ms: Animation duration in milliseconds (default: 400ms = 350ms + buffer)
        """
        self.page.wait_for_timeout(duration_ms)

    def take_screenshot(self, name: str, element_selector: Optional[str] = None,
                       subdirectory: str = "screenshots") -> Path:
        """
        Capture screenshot of page or specific element.

        Args:
            name: Screenshot filename (without extension)
            element_selector: Optional CSS selector for element screenshot
            subdirectory: Subdirectory under artifacts/ (default: screenshots)

        Returns:
            Path to saved screenshot
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"

        screenshot_dir = self.base_path / subdirectory / datetime.now().strftime("%Y%m%d")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        filepath = screenshot_dir / filename

        if element_selector:
            element = self.page.query_selector(element_selector)
            if element:
                element.screenshot(path=str(filepath))
            else:
                raise ValueError(f"Element not found: {element_selector}")
        else:
            self.page.screenshot(path=str(filepath), full_page=True)

        return filepath

    def measure_button_gap(self) -> float:
        """
        Measure pixel gap between copy button and collapse button.

        Returns:
            Gap in pixels
        """
        # Find first code block with both buttons
        copy_btn = self.page.query_selector(".copybtn")
        collapse_btn = self.page.query_selector(".copybtn + .code-collapse-btn")

        if not copy_btn or not collapse_btn:
            raise RuntimeError("Could not find adjacent copy and collapse buttons")

        copy_box = copy_btn.bounding_box()
        collapse_box = collapse_btn.bounding_box()

        if not copy_box or not collapse_box:
            raise RuntimeError("Could not get button bounding boxes")

        # Layout: [Collapse Button] [Gap] [Copy Button]
        # Gap = left edge of copy button - right edge of collapse button
        gap = copy_box["x"] - (collapse_box["x"] + collapse_box["width"])

        return gap

    def check_aria_attributes(self, index: int = 0) -> Dict[str, str]:
        """
        Check ARIA attributes on a collapse button.

        Args:
            index: Button index (0-based)

        Returns:
            Dictionary of ARIA attributes
        """
        buttons = self.get_collapse_buttons()
        if index >= len(buttons):
            raise IndexError(f"Button index {index} out of range")

        button = buttons[index]

        return {
            "aria-label": button.get_attribute("aria-label") or "",
            "aria-expanded": button.get_attribute("aria-expanded") or "",
            "title": button.get_attribute("title") or ""
        }

    def get_state_from_localstorage(self) -> Dict[str, str]:
        """
        Get collapse state from localStorage.

        Returns:
            Dictionary mapping block indices to states
        """
        state_json = self.page.evaluate("() => localStorage.getItem('code-block-states')")

        if state_json:
            return json.loads(state_json)
        return {}

    def clear_localstorage_state(self) -> None:
        """Clear code block states from localStorage."""
        self.page.evaluate("() => localStorage.removeItem('code-block-states')")

    def trigger_keyboard_shortcut(self, shortcut: str) -> None:
        """
        Trigger keyboard shortcut.

        Args:
            shortcut: Shortcut string (e.g., "Control+Shift+C")
        """
        self.page.keyboard.press(shortcut)
        self.wait_for_animation()

    def save_console_logs(self, filename: str = "console_logs.json") -> Path:
        """
        Save captured console logs to JSON file.

        Args:
            filename: Output filename

        Returns:
            Path to saved log file
        """
        logs_dir = self.base_path / "logs" / datetime.now().strftime("%Y%m%d")
        logs_dir.mkdir(parents=True, exist_ok=True)

        filepath = logs_dir / filename

        with open(filepath, "w") as f:
            json.dump({
                "console_logs": self.console_logs,
                "errors": self.errors,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)

        return filepath

    def has_errors(self) -> bool:
        """Check if any JavaScript errors were captured."""
        return len(self.errors) > 0

    def get_viewport_size(self) -> Dict[str, int]:
        """Get current viewport size."""
        return self.page.viewport_size

    def set_viewport_size(self, width: int, height: int) -> None:
        """Set viewport size for responsive testing."""
        self.page.set_viewport_size({"width": width, "height": height})
