"""
Sphinx extension for Pyodide live Python code execution.

Provides custom directive for embedding executable Python code blocks
that run in the browser using Pyodide WebAssembly.

Usage:
    .. runnable-code::
       :language: python
       :caption: Example: NumPy Array Operations
       :preload: numpy,matplotlib
       :timeout: 10000

       import numpy as np
       arr = np.array([1, 2, 3, 4, 5])
       print(f"Sum: {arr.sum()}")
"""

from typing import List, Dict, Any
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
import hashlib


class RunnableCodeDirective(SphinxDirective):
    """
    Directive for embedding executable Python code blocks.

    Generates HTML with special CSS classes that PyodideRunner recognizes.
    Code blocks get Run/Reset buttons and can execute in browser.

    Options:
        :language: Programming language (only 'python' supported)
        :caption: Title displayed above code block
        :preload: Comma-separated packages to preload (numpy, matplotlib, scipy)
        :timeout: Execution timeout in milliseconds (default: 10000)
        :readonly: If present, code is not editable
        :hide-output: If present, output panel is initially collapsed
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 0

    option_spec = {
        'language': directives.unchanged,
        'caption': directives.unchanged,
        'preload': directives.unchanged,
        'timeout': directives.positive_int,
        'readonly': directives.flag,
        'hide-output': directives.flag,
    }

    def run(self) -> List[nodes.Node]:
        """Process the runnable-code directive and generate HTML."""

        # Get options
        language = self.options.get('language', 'python')
        caption = self.options.get('caption', '')
        preload = self.options.get('preload', 'numpy,matplotlib')
        timeout = self.options.get('timeout', 10000)
        readonly = 'readonly' in self.options
        hide_output = 'hide-output' in self.options

        # Validate language
        if language.lower() != 'python':
            self.state_machine.reporter.warning(
                f'Only Python is supported for runnable code (got: {language})',
                line=self.lineno
            )
            language = 'python'

        # Get code content
        code_content = '\n'.join(self.content)

        if not code_content.strip():
            self.state_machine.reporter.warning(
                'Empty runnable-code block',
                line=self.lineno
            )
            code_content = '# Empty code block'

        # Generate unique ID for this code block
        code_hash = hashlib.md5(code_content.encode()).hexdigest()[:8]
        code_id = f"runnable-{self.env.new_serialno('runnable')}-{code_hash}"

        # Build HTML
        html = self.generate_html(
            code_id=code_id,
            code_content=code_content,
            caption=caption,
            preload=preload,
            timeout=timeout,
            readonly=readonly,
            hide_output=hide_output
        )

        # Return raw HTML node
        raw_node = nodes.raw('', html, format='html')
        return [raw_node]

    def generate_html(self, code_id: str, code_content: str, caption: str,
                     preload: str, timeout: int, readonly: bool,
                     hide_output: bool) -> str:
        """Generate HTML for runnable code block."""

        # Escape HTML in code content
        import html
        escaped_code = html.escape(code_content)

        # Build HTML structure
        html_parts = []

        # Container div
        html_parts.append('<div class="runnable-code-container">')

        # Caption (if provided)
        if caption:
            html_parts.append(f'''
<div class="runnable-code-caption">
    <strong>📝 {html.escape(caption)}</strong>
</div>
            ''')

        # Code block with data attributes for PyodideRunner
        html_parts.append(f'''
<pre class="runnable-code highlight"
     data-code-id="{code_id}"
     data-preload="{html.escape(preload)}"
     data-timeout="{timeout}"
     data-readonly="{str(readonly).lower()}"
     data-hide-output="{str(hide_output).lower()}"><code class="language-python">{escaped_code}</code></pre>
        ''')

        # Info box
        html_parts.append('''
<div class="runnable-code-info">
    <small>
        💡 <strong>Interactive Code:</strong>
        Click "Run Code" to execute in your browser (first run loads Python, ~15-30s).
        Edit code directly and re-run.
        Use <kbd>Ctrl+Enter</kbd> to run.
    </small>
</div>
        ''')

        html_parts.append('</div>')

        return '\n'.join(html_parts)


class PyodideInfoDirective(SphinxDirective):
    """
    Directive for displaying Pyodide system requirements and info.

    Usage:
        .. pyodide-info::
           :show-requirements: true
           :show-limitations: true
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    option_spec = {
        'show-requirements': directives.flag,
        'show-limitations': directives.flag,
        'show-packages': directives.flag,
    }

    def run(self) -> List[nodes.Node]:
        """Generate info box about Pyodide."""

        show_requirements = 'show-requirements' in self.options
        show_limitations = 'show-limitations' in self.options
        show_packages = 'show-packages' in self.options

        html_parts = []
        html_parts.append('<div class="pyodide-info-box">')

        if show_requirements:
            html_parts.append('''
<div class="info-section">
    <h4>🖥️ System Requirements</h4>
    <ul>
        <li><strong>Browser:</strong> Chrome 90+, Firefox 88+, Safari 14+, Edge 90+</li>
        <li><strong>JavaScript:</strong> Must be enabled</li>
        <li><strong>WebAssembly:</strong> Required (supported in all modern browsers)</li>
        <li><strong>Memory:</strong> 2GB+ RAM recommended</li>
        <li><strong>First Load:</strong> 15-30 seconds to download Python + packages (~60MB)</li>
        <li><strong>Subsequent:</strong> Instant (cached in browser)</li>
    </ul>
</div>
            ''')

        if show_packages:
            html_parts.append('''
<div class="info-section">
    <h4>📦 Available Packages</h4>
    <ul>
        <li><strong>NumPy:</strong> Scientific computing with arrays</li>
        <li><strong>Matplotlib:</strong> Plotting and visualization</li>
        <li><strong>SciPy:</strong> Advanced scientific computing (optional)</li>
        <li><strong>Standard Library:</strong> Full Python 3.11 standard library</li>
    </ul>
</div>
            ''')

        if show_limitations:
            html_parts.append('''
<div class="info-section">
    <h4>⚠️ Limitations</h4>
    <ul>
        <li><strong>Execution Time:</strong> 10-second timeout (prevents infinite loops)</li>
        <li><strong>File I/O:</strong> No access to local filesystem</li>
        <li><strong>Network:</strong> Limited network access (CORS restrictions)</li>
        <li><strong>Memory:</strong> Limited by browser (typically 2GB)</li>
        <li><strong>Threading:</strong> No multiprocessing/threading support</li>
        <li><strong>Performance:</strong> ~50-70% of native Python speed</li>
    </ul>
</div>
            ''')

        html_parts.append('</div>')

        return [nodes.raw('', '\n'.join(html_parts), format='html')]


def add_pyodide_assets(app: Sphinx, pagename: str, templatename: str,
                       context: Dict[str, Any], doctree: nodes.Node) -> None:
    """Add Pyodide CSS to HTML pages."""

    if not hasattr(context, 'metatags'):
        context['metatags'] = ''

    # Add custom styles for directive-generated elements
    pyodide_styles = '''
<style>
/* Runnable code container */
.runnable-code-container {
    margin: 2em 0;
    background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

/* Caption */
.runnable-code-caption {
    margin-bottom: 15px;
    padding: 10px 15px;
    background: white;
    border-radius: 8px;
    border-left: 4px solid #2196F3;
    font-size: 15px;
    color: #333;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

/* Info box */
.runnable-code-info {
    margin-top: 15px;
    padding: 12px 15px;
    background: #e3f2fd;
    border-radius: 6px;
    border-left: 3px solid #2196F3;
}

.runnable-code-info small {
    font-size: 13px;
    color: #0d47a1;
    line-height: 1.5;
}

.runnable-code-info kbd {
    background: #fff;
    border: 1px solid #ccc;
    border-radius: 3px;
    padding: 2px 6px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: #333;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

/* Pyodide info box */
.pyodide-info-box {
    background: #f8f9fa;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    padding: 20px;
    margin: 2em 0;
}

.pyodide-info-box .info-section {
    margin-bottom: 20px;
}

.pyodide-info-box .info-section:last-child {
    margin-bottom: 0;
}

.pyodide-info-box h4 {
    margin-top: 0;
    margin-bottom: 12px;
    color: #333;
    font-size: 16px;
    border-bottom: 2px solid #dee2e6;
    padding-bottom: 8px;
}

.pyodide-info-box ul {
    margin: 0;
    padding-left: 20px;
}

.pyodide-info-box li {
    margin-bottom: 8px;
    color: #555;
    line-height: 1.6;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
    .runnable-code-container {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
    }

    .runnable-code-caption {
        background: #2d3748;
        color: #e2e8f0;
    }

    .runnable-code-info {
        background: #1e2d3d;
        border-left-color: #60a5fa;
    }

    .runnable-code-info small {
        color: #90caf9;
    }

    .runnable-code-info kbd {
        background: #374151;
        border-color: #4b5563;
        color: #e5e7eb;
    }

    .pyodide-info-box {
        background: #1f2937;
        border-color: #374151;
    }

    .pyodide-info-box h4 {
        color: #f3f4f6;
        border-bottom-color: #374151;
    }

    .pyodide-info-box li {
        color: #d1d5db;
    }
}
</style>
    '''

    context['metatags'] += pyodide_styles


def setup(app: Sphinx) -> Dict[str, Any]:
    """Setup the Pyodide extension."""

    # Register directives
    app.add_directive('runnable-code', RunnableCodeDirective)
    app.add_directive('pyodide-info', PyodideInfoDirective)

    # Add custom CSS to pages
    app.connect('html-page-context', add_pyodide_assets)

    return {
        'version': '1.0.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
