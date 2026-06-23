#!/usr/bin/env python3
"""Tests for the fix_concatenated_headings.py script.

This test suite validates the pattern detection and fixing logic for
concatenated Markdown headings that cause Sphinx build errors.
"""

import pytest
from pathlib import Path
import sys

# Add scripts/docs to path to import the fixer
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / 'scripts' / 'docs'))

from fix_concatenated_headings import MarkdownHeadingFixer  # noqa: E402


class TestMarkdownHeadingFixer:
    """Test the MarkdownHeadingFixer class."""

    @pytest.fixture
    def fixer(self):
        """Create a fixer instance for testing."""
        return MarkdownHeadingFixer(dry_run=False, verbose=False)

    def test_is_heading_detects_all_levels(self, fixer):
        """Test heading detection for all heading levels."""
        assert fixer.is_heading('# Heading 1')
        assert fixer.is_heading('## Heading 2')
        assert fixer.is_heading('### Heading 3')
        assert fixer.is_heading('#### Heading 4')
        assert fixer.is_heading('##### Heading 5')
        assert fixer.is_heading('###### Heading 6')

    def test_is_heading_rejects_non_headings(self, fixer):
        """Test that non-headings are not detected as headings."""
        assert not fixer.is_heading('Not a heading')
        assert not fixer.is_heading('####### Too many #')
        assert not fixer.is_heading('#No space after #')
        assert not fixer.is_heading('Text with # in middle')

    def test_is_code_fence_detects_fences(self, fixer):
        """Test code fence detection."""
        assert fixer.is_code_fence('```')
        assert fixer.is_code_fence('```python')
        assert fixer.is_code_fence('```{mermaid}')
        assert fixer.is_code_fence('```{toctree}')

    def test_is_code_fence_rejects_non_fences(self, fixer):
        """Test that non-fences are not detected as fences."""
        assert not fixer.is_code_fence('Not a fence')
        assert not fixer.is_code_fence('``Two backticks')
        assert not fixer.is_code_fence('Text with ``` in middle')

    def test_is_blank_detects_blank_lines(self, fixer):
        """Test blank line detection."""
        assert fixer.is_blank('')
        assert fixer.is_blank('   ')
        assert fixer.is_blank('\t')
        assert fixer.is_blank('  \t  ')

    def test_is_blank_rejects_non_blank(self, fixer):
        """Test that non-blank lines are not detected as blank."""
        assert not fixer.is_blank('Text')
        assert not fixer.is_blank('  Text  ')

    def test_needs_blank_line_after_heading(self, fixer):
        """Test that blank line is needed after heading followed by content."""
        assert fixer.needs_blank_line_after('# Heading', 'Content', False)
        assert fixer.needs_blank_line_after('## Heading', 'Content', False)
        assert fixer.needs_blank_line_after('### Heading', '- List item', False)

    def test_no_blank_line_after_heading_already_blank(self, fixer):
        """Test that blank line is not needed if next line is already blank."""
        assert not fixer.needs_blank_line_after('# Heading', '', False)
        assert not fixer.needs_blank_line_after('# Heading', '   ', False)

    def test_no_blank_line_inside_code_block(self, fixer):
        """Test that blank lines are not inserted inside code blocks."""
        assert not fixer.needs_blank_line_after('# Not a heading', 'Content', True)

    def test_needs_blank_line_after_code_fence(self, fixer):
        """Test that blank line is needed after code fence followed by content."""
        assert fixer.needs_blank_line_after('```', 'Content', False)
        assert not fixer.needs_blank_line_after('```', '## Heading', False)

    def test_fix_simple_concatenated_heading(self, fixer, tmp_path):
        """Test fixing a simple concatenated heading."""
        # Create test file
        test_file = tmp_path / 'test.md'
        test_file.write_text('# Heading\nContent\n')

        # Fix file
        was_modified, patterns_fixed = fixer.fix_file(test_file)

        # Verify results
        assert was_modified
        assert patterns_fixed == 1

        # Verify content
        fixed_content = test_file.read_text()
        assert fixed_content == '# Heading\n\nContent\n'

    def test_fix_multiple_concatenated_headings(self, fixer, tmp_path):
        """Test fixing multiple concatenated headings."""
        # Create test file
        test_file = tmp_path / 'test.md'
        content = '# Heading 1\nContent 1\n## Heading 2\nContent 2\n'
        test_file.write_text(content)

        # Fix file
        was_modified, patterns_fixed = fixer.fix_file(test_file)

        # Verify results
        assert was_modified
        assert patterns_fixed == 2

        # Verify content
        fixed_content = test_file.read_text()
        expected = '# Heading 1\n\nContent 1\n## Heading 2\n\nContent 2\n'
        assert fixed_content == expected

    def test_fix_preserves_existing_blank_lines(self, fixer, tmp_path):
        """Test that existing blank lines are preserved."""
        # Create test file with proper spacing
        test_file = tmp_path / 'test.md'
        content = '# Heading 1\n\nContent 1\n\n## Heading 2\n\nContent 2\n'
        test_file.write_text(content)

        # Fix file
        was_modified, patterns_fixed = fixer.fix_file(test_file)

        # Verify no changes needed
        assert not was_modified
        assert patterns_fixed == 0

        # Verify content unchanged
        assert test_file.read_text() == content

    def test_fix_code_blocks_not_modified(self, fixer, tmp_path):
        """Test that code blocks are not modified."""
        # Create test file with code block
        test_file = tmp_path / 'test.md'
        content = '# Heading\n\n```python\n# Not a heading\nContent\n```\n'
        test_file.write_text(content)

        # Fix file
        was_modified, patterns_fixed = fixer.fix_file(test_file)

        # Verify no changes to code block
        assert not was_modified
        assert patterns_fixed == 0
        assert test_file.read_text() == content

    def test_fix_blank_line_after_code_fence(self, fixer, tmp_path):
        """Test adding blank line after code fence."""
        # Create test file
        test_file = tmp_path / 'test.md'
        content = '```python\ncode\n```\nContent after\n'
        test_file.write_text(content)

        # Fix file
        was_modified, patterns_fixed = fixer.fix_file(test_file)

        # Verify blank line added after fence
        assert was_modified
        assert patterns_fixed == 1

        fixed_content = test_file.read_text()
        expected = '```python\ncode\n```\n\nContent after\n'
        assert fixed_content == expected

    def test_dry_run_does_not_modify_file(self, fixer, tmp_path):
        """Test that dry-run mode does not modify files."""
        # Create fixer in dry-run mode
        dry_run_fixer = MarkdownHeadingFixer(dry_run=True, verbose=False)

        # Create test file
        test_file = tmp_path / 'test.md'
        original_content = '# Heading\nContent\n'
        test_file.write_text(original_content)

        # Fix file in dry-run mode
        was_modified, patterns_fixed = dry_run_fixer.fix_file(test_file)

        # Verify detection worked
        assert was_modified
        assert patterns_fixed == 1

        # Verify file was NOT modified
        assert test_file.read_text() == original_content


class TestRegressionOnFixedFiles:
    """Regression tests on already-fixed files to ensure no unwanted changes."""

    @pytest.fixture
    def fixer(self):
        """Create a fixer instance for testing."""
        return MarkdownHeadingFixer(dry_run=False, verbose=False)

    def test_no_changes_to_quality_gates(self, fixer):
        """Test that quality_gates.md requires no changes after manual fix."""
        file_path = REPO_ROOT / 'docs' / 'development' / 'quality_gates.md'

        if not file_path.exists():
            pytest.skip(f"File not found: {file_path}")

        # Fix file
        was_modified, patterns_fixed = fixer.fix_file(file_path)

        # Should not need any changes
        assert not was_modified
        assert patterns_fixed == 0

    def test_no_changes_to_index(self, fixer):
        """Test that index.md requires no changes after manual fix."""
        file_path = REPO_ROOT / 'docs' / 'index.md'

        if not file_path.exists():
            pytest.skip(f"File not found: {file_path}")

        # Fix file
        was_modified, patterns_fixed = fixer.fix_file(file_path)

        # Should not need any changes
        assert not was_modified
        assert patterns_fixed == 0


class TestDirectoryProcessing:
    """Test directory processing functionality."""

    @pytest.fixture
    def fixer(self):
        """Create a fixer instance for testing."""
        return MarkdownHeadingFixer(dry_run=False, verbose=False)

    def test_fix_directory_non_recursive(self, fixer, tmp_path):
        """Test fixing directory without recursion."""
        # Create test files
        (tmp_path / 'file1.md').write_text('# Heading\nContent\n')
        (tmp_path / 'file2.md').write_text('# Heading\n\nContent\n')

        # Create subdirectory with file (should be ignored)
        subdir = tmp_path / 'subdir'
        subdir.mkdir()
        (subdir / 'file3.md').write_text('# Heading\nContent\n')

        # Fix directory non-recursively
        fixer.fix_directory(tmp_path, recursive=False)

        # Verify only top-level files processed
        assert fixer.files_modified == 1
        assert fixer.patterns_fixed == 1

    def test_fix_directory_recursive(self, fixer, tmp_path):
        """Test fixing directory with recursion."""
        # Create test files
        (tmp_path / 'file1.md').write_text('# Heading\nContent\n')

        # Create subdirectory with file
        subdir = tmp_path / 'subdir'
        subdir.mkdir()
        (subdir / 'file2.md').write_text('# Heading\nContent\n')

        # Fix directory recursively
        fixer.fix_directory(tmp_path, recursive=True)

        # Verify all files processed
        assert fixer.files_modified == 2
        assert fixer.patterns_fixed == 2

    def test_fix_directory_with_exclusions(self, fixer, tmp_path):
        """Test fixing directory with exclusion patterns."""
        # Create test files
        (tmp_path / 'file1.md').write_text('# Heading\nContent\n')

        # Create _build subdirectory (should be excluded)
        build_dir = tmp_path / '_build'
        build_dir.mkdir()
        (build_dir / 'file2.md').write_text('# Heading\nContent\n')

        # Fix directory with exclusion
        fixer.fix_directory(tmp_path, recursive=True, exclude_patterns=['_build/**'])

        # Verify only non-excluded files processed
        assert fixer.files_modified == 1
        assert fixer.patterns_fixed == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
