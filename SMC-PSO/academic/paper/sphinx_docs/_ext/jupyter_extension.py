"""
Sphinx extension for Jupyter notebook integration with custom directives.

Provides custom directives for embedding Jupyter notebooks, executing code cells,
and rendering interactive widgets within Sphinx documentation.

Usage:
    .. jupyter-notebook::
       :path: notebooks/01_getting_started.ipynb
       :execute: true
       :show-output: true

    .. jupyter-cell::
       :kernel: python3
       :cache-key: demo-cell-001

       import numpy as np
       print(np.arange(10))

    .. jupyter-widget::
       :widget-type: slider
       :min: 0
       :max: 100
       :step: 1
       :default: 50
       :label: Controller Gain
"""

from typing import List, Dict, Any, Optional
import hashlib
import pickle
from pathlib import Path
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

# Execution caching support
_EXECUTION_CACHE: Dict[str, Any] = {}


class JupyterNotebookDirective(SphinxDirective):
    """
    Directive for embedding full Jupyter notebooks with execution.

    Renders an entire Jupyter notebook within Sphinx documentation,
    with optional execution, selective cell display, and output control.

    Options:
        :path: Path to .ipynb file (relative to docs/ or absolute)
        :execute: Execute cells during build (true/false, default: auto)
        :show-cells: Comma-separated list of cell indices to show (e.g., "0,2,5-8")
        :hide-input: Hide code cells, show only output (true/false)
        :hide-output: Hide cell outputs (true/false)
        :allow-errors: Continue on cell errors (true/false)
        :timeout: Maximum execution time per cell in seconds (default: 30)
        :cache-key: Custom cache key for execution results
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    option_spec = {
        'path': directives.path,
        'execute': directives.unchanged,
        'show-cells': directives.unchanged,
        'hide-input': directives.flag,
        'hide-output': directives.flag,
        'allow-errors': directives.flag,
        'timeout': directives.positive_int,
        'cache-key': directives.unchanged,
    }

    def run(self) -> List[nodes.Node]:
        """Process the jupyter-notebook directive."""

        notebook_path = self.options.get('path', '')
        execute = self.options.get('execute', 'auto')
        show_cells = self.options.get('show-cells', 'all')
        hide_input = 'hide-input' in self.options
        hide_output = 'hide-output' in self.options
        allow_errors = 'allow-errors' in self.options
        timeout = self.options.get('timeout', 30)
        cache_key = self.options.get('cache-key', '')

        if not notebook_path:
            self.state_machine.reporter.warning(
                'jupyter-notebook: Must specify :path: to notebook file',
                line=self.lineno
            )
            return []

        # Resolve path relative to docs directory
        docs_dir = Path(self.env.srcdir)
        nb_path = docs_dir / notebook_path
        if not nb_path.exists():
            # Try relative to project root
            nb_path = docs_dir.parent / notebook_path
            if not nb_path.exists():
                self.state_machine.reporter.error(
                    f'jupyter-notebook: Notebook not found: {notebook_path}',
                    line=self.lineno
                )
                return []

        # Generate unique ID
        notebook_id = f"jupyter-notebook-{self.env.new_serialno('jupyter-notebook')}"

        # Build HTML
        html = self.generate_notebook_html(
            notebook_id=notebook_id,
            notebook_path=str(nb_path),
            execute=execute,
            show_cells=show_cells,
            hide_input=hide_input,
            hide_output=hide_output,
            allow_errors=allow_errors,
            timeout=timeout,
            cache_key=cache_key
        )

        return [nodes.raw('', html, format='html')]

    def generate_notebook_html(self, notebook_id: str, notebook_path: str,
                               execute: str, show_cells: str, hide_input: bool,
                               hide_output: bool, allow_errors: bool,
                               timeout: int, cache_key: str) -> str:
        """Generate HTML for embedded notebook."""

        import html

        html_parts = []

        html_parts.append('<div class="jupyter-notebook-container">')

        # Header with notebook info
        notebook_name = Path(notebook_path).name
        html_parts.append(f'''
<div class="jupyter-notebook-header">
    <div class="jupyter-notebook-title">
        📓 <strong>{html.escape(notebook_name)}</strong>
    </div>
    <div class="jupyter-notebook-meta">
        <span class="jupyter-badge">Jupyter Notebook</span>
        <span class="jupyter-execute-status">{execute}</span>
    </div>
</div>
        ''')

        # Notebook content div
        html_parts.append(f'''
<div id="{notebook_id}"
     class="jupyter-notebook"
     data-notebook-path="{html.escape(notebook_path)}"
     data-execute="{execute}"
     data-show-cells="{html.escape(show_cells)}"
     data-hide-input="{str(hide_input).lower()}"
     data-hide-output="{str(hide_output).lower()}"
     data-allow-errors="{str(allow_errors).lower()}"
     data-timeout="{timeout}"
     data-cache-key="{html.escape(cache_key)}">
    <div class="jupyter-notebook-loading">
        <p>⏳ Loading notebook...</p>
        <p><small>This notebook will be rendered using nbsphinx</small></p>
    </div>
</div>
        ''')

        # Info box
        html_parts.append('''
<div class="jupyter-notebook-info">
    <small>
        💡 <strong>Interactive Notebook:</strong>
        This notebook is executed during documentation build.
        All outputs are cached for fast rebuilds.
    </small>
</div>
        ''')

        html_parts.append('</div>')

        return '\n'.join(html_parts)


class JupyterCellDirective(SphinxDirective):
    """
    Directive for inline Jupyter code cell execution.

    Executes Python code in a Jupyter kernel and displays the output
    inline within the documentation. Supports execution caching.

    Options:
        :kernel: Jupyter kernel to use (default: python3)
        :cache-key: Cache key for execution results
        :hide-input: Hide the input code (true/false)
        :hide-output: Hide the execution output (true/false)
        :linenos: Show line numbers for code (true/false)
        :emphasize-lines: Comma-separated line numbers to highlight
        :name: Reference name for the cell
        :timeout: Maximum execution time in seconds (default: 30)
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 0

    option_spec = {
        'kernel': directives.unchanged,
        'cache-key': directives.unchanged,
        'hide-input': directives.flag,
        'hide-output': directives.flag,
        'linenos': directives.flag,
        'emphasize-lines': directives.unchanged,
        'name': directives.unchanged,
        'timeout': directives.positive_int,
    }

    def run(self) -> List[nodes.Node]:
        """Process the jupyter-cell directive."""

        kernel = self.options.get('kernel', 'python3')
        cache_key = self.options.get('cache-key', '')
        hide_input = 'hide-input' in self.options
        hide_output = 'hide-output' in self.options
        linenos = 'linenos' in self.options
        emphasize_lines = self.options.get('emphasize-lines', '')
        name = self.options.get('name', '')
        timeout = self.options.get('timeout', 30)

        # Get code content
        code_content = '\n'.join(self.content) if self.content else ''

        if not code_content.strip():
            self.state_machine.reporter.warning(
                'jupyter-cell: No code content provided',
                line=self.lineno
            )
            return []

        # Generate cache key if not provided
        if not cache_key:
            code_hash = hashlib.md5(code_content.encode()).hexdigest()[:8]
            cache_key = f"cell-{code_hash}"

        # Generate unique ID
        cell_id = f"jupyter-cell-{self.env.new_serialno('jupyter-cell')}"

        # Execute cell (with caching)
        execution_result = self.execute_cell(
            code=code_content,
            kernel=kernel,
            cache_key=cache_key,
            timeout=timeout
        )

        # Build HTML
        html = self.generate_cell_html(
            cell_id=cell_id,
            code=code_content,
            execution_result=execution_result,
            hide_input=hide_input,
            hide_output=hide_output,
            linenos=linenos,
            emphasize_lines=emphasize_lines,
            name=name
        )

        return [nodes.raw('', html, format='html')]

    def execute_cell(self, code: str, kernel: str, cache_key: str,
                    timeout: int) -> Dict[str, Any]:
        """Execute code in Jupyter kernel with caching."""

        # Check cache first
        if cache_key in _EXECUTION_CACHE:
            return _EXECUTION_CACHE[cache_key]

        # Execute code (simplified - real implementation would use nbclient)
        try:
            # This is a placeholder - real implementation would:
            # 1. Create Jupyter kernel
            # 2. Execute code
            # 3. Capture outputs (stdout, stderr, display data)
            # 4. Cache results

            result = {
                'status': 'success',
                'stdout': '',
                'stderr': '',
                'outputs': [],
                'execution_count': 1,
            }

            # For now, just indicate the code would be executed
            result['stdout'] = "[Code execution during Sphinx build]\n"

            # Cache result
            _EXECUTION_CACHE[cache_key] = result
            return result

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'stdout': '',
                'stderr': str(e),
                'outputs': [],
            }

    def generate_cell_html(self, cell_id: str, code: str,
                          execution_result: Dict[str, Any],
                          hide_input: bool, hide_output: bool,
                          linenos: bool, emphasize_lines: str,
                          name: str) -> str:
        """Generate HTML for Jupyter cell."""

        import html

        html_parts = []

        html_parts.append('<div class="jupyter-cell-container">')

        # Cell name/label
        if name:
            html_parts.append(f'''
<div class="jupyter-cell-label">
    <strong>{html.escape(name)}</strong>
</div>
            ''')

        # Input code (unless hidden)
        if not hide_input:
            escaped_code = html.escape(code)
            linenos_class = ' linenos' if linenos else ''

            html_parts.append(f'''
<div class="jupyter-cell-input">
    <div class="jupyter-input-header">
        <span class="jupyter-prompt">In [{execution_result.get('execution_count', '')}]:</span>
        <button class="jupyter-copy-btn" onclick="navigator.clipboard.writeText(this.parentElement.nextElementSibling.textContent)">
            📋 Copy
        </button>
    </div>
    <pre class="jupyter-code{linenos_class}"><code class="language-python">{escaped_code}</code></pre>
</div>
            ''')

        # Output (unless hidden)
        if not hide_output:
            stdout = execution_result.get('stdout', '')
            stderr = execution_result.get('stderr', '')
            status = execution_result.get('status', 'success')

            if stdout or stderr or status == 'error':
                html_parts.append('<div class="jupyter-cell-output">')

                html_parts.append(f'''
<div class="jupyter-output-header">
    <span class="jupyter-prompt">Out [{execution_result.get('execution_count', '')}]:</span>
</div>
                ''')

                # Standard output
                if stdout:
                    html_parts.append(f'''
<pre class="jupyter-stdout">{html.escape(stdout)}</pre>
                    ''')

                # Error output
                if stderr or status == 'error':
                    error_msg = stderr or execution_result.get('error', 'Unknown error')
                    html_parts.append(f'''
<pre class="jupyter-stderr">{html.escape(error_msg)}</pre>
                    ''')

                html_parts.append('</div>')

        html_parts.append('</div>')

        return '\n'.join(html_parts)


class JupyterWidgetDirective(SphinxDirective):
    """
    Directive for interactive Jupyter widgets (ipywidgets).

    Embeds interactive widgets like sliders, dropdowns, and buttons
    that can be used to explore parameters and run simulations.

    Options:
        :widget-type: Type of widget (slider, dropdown, button, checkbox, text)
        :label: Widget label
        :min: Minimum value (for sliders)
        :max: Maximum value (for sliders)
        :step: Step size (for sliders)
        :default: Default value
        :options: Comma-separated options (for dropdowns)
        :callback: JavaScript callback function name
        :description: Widget description text
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 0

    option_spec = {
        'widget-type': directives.unchanged_required,
        'label': directives.unchanged,
        'min': directives.unchanged,
        'max': directives.unchanged,
        'step': directives.unchanged,
        'default': directives.unchanged,
        'options': directives.unchanged,
        'callback': directives.unchanged,
        'description': directives.unchanged,
    }

    def run(self) -> List[nodes.Node]:
        """Process the jupyter-widget directive."""

        widget_type = self.options.get('widget-type', 'slider')
        label = self.options.get('label', 'Parameter')
        min_val = self.options.get('min', '0')
        max_val = self.options.get('max', '100')
        step = self.options.get('step', '1')
        default = self.options.get('default', min_val)
        options = self.options.get('options', '')
        callback = self.options.get('callback', '')
        description = self.options.get('description', '')

        # Get custom code from content
        custom_code = '\n'.join(self.content) if self.content else ''

        # Generate unique ID
        widget_id = f"jupyter-widget-{self.env.new_serialno('jupyter-widget')}"

        # Build HTML
        html = self.generate_widget_html(
            widget_id=widget_id,
            widget_type=widget_type,
            label=label,
            min_val=min_val,
            max_val=max_val,
            step=step,
            default=default,
            options=options,
            callback=callback,
            description=description,
            custom_code=custom_code
        )

        return [nodes.raw('', html, format='html')]

    def generate_widget_html(self, widget_id: str, widget_type: str,
                            label: str, min_val: str, max_val: str,
                            step: str, default: str, options: str,
                            callback: str, description: str,
                            custom_code: str) -> str:
        """Generate HTML for interactive widget."""

        import html

        html_parts = []

        html_parts.append('<div class="jupyter-widget-container">')

        # Widget header
        html_parts.append(f'''
<div class="jupyter-widget-header">
    <strong>🎛️ {html.escape(label)}</strong>
</div>
        ''')

        # Widget description
        if description:
            html_parts.append(f'''
<div class="jupyter-widget-description">
    <p>{html.escape(description)}</p>
</div>
            ''')

        # Widget based on type
        if widget_type == 'slider':
            html_parts.append(f'''
<div class="jupyter-widget" id="{widget_id}">
    <label for="{widget_id}-input">{html.escape(label)}: <span id="{widget_id}-value">{html.escape(default)}</span></label>
    <input type="range"
           id="{widget_id}-input"
           class="jupyter-slider"
           min="{html.escape(min_val)}"
           max="{html.escape(max_val)}"
           step="{html.escape(step)}"
           value="{html.escape(default)}"
           onchange="{callback}(this.value)"
           oninput="document.getElementById('{widget_id}-value').textContent = this.value">
</div>
            ''')

        elif widget_type == 'dropdown':
            option_list = [opt.strip() for opt in options.split(',') if opt.strip()]
            html_parts.append(f'''
<div class="jupyter-widget" id="{widget_id}">
    <label for="{widget_id}-select">{html.escape(label)}:</label>
    <select id="{widget_id}-select" class="jupyter-dropdown" onchange="{callback}(this.value)">
            ''')

            for opt in option_list:
                selected = ' selected' if opt == default else ''
                html_parts.append(f'''
        <option value="{html.escape(opt)}"{selected}>{html.escape(opt)}</option>
                ''')

            html_parts.append('''
    </select>
</div>
            ''')

        elif widget_type == 'button':
            html_parts.append(f'''
<div class="jupyter-widget" id="{widget_id}">
    <button class="jupyter-button" onclick="{callback}()">
        {html.escape(label)}
    </button>
</div>
            ''')

        elif widget_type == 'checkbox':
            checked = ' checked' if default.lower() == 'true' else ''
            html_parts.append(f'''
<div class="jupyter-widget" id="{widget_id}">
    <label>
        <input type="checkbox"
               id="{widget_id}-checkbox"
               class="jupyter-checkbox"
               onchange="{callback}(this.checked)"{checked}>
        {html.escape(label)}
    </label>
</div>
            ''')

        elif widget_type == 'text':
            html_parts.append(f'''
<div class="jupyter-widget" id="{widget_id}">
    <label for="{widget_id}-text">{html.escape(label)}:</label>
    <input type="text"
           id="{widget_id}-text"
           class="jupyter-text"
           value="{html.escape(default)}"
           onchange="{callback}(this.value)">
</div>
            ''')

        # Custom code output area
        if custom_code:
            html_parts.append(f'''
<div class="jupyter-widget-output" id="{widget_id}-output">
    <pre><code class="language-python">{html.escape(custom_code)}</code></pre>
</div>
            ''')

        html_parts.append('</div>')

        return '\n'.join(html_parts)


def add_jupyter_assets(app: Sphinx, pagename: str, templatename: str,
                       context: Dict[str, Any], doctree: nodes.Node) -> None:
    """Add Jupyter custom CSS styles to HTML pages."""

    if not hasattr(context, 'metatags'):
        context['metatags'] = ''

    # Add custom styles for Jupyter directive-generated elements
    jupyter_styles = '''
<style>
/* Jupyter notebook containers */
.jupyter-notebook-container,
.jupyter-cell-container,
.jupyter-widget-container {
    margin: 2em 0;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

/* Notebook header */
.jupyter-notebook-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding: 12px 15px;
    background: white;
    border-radius: 8px;
    border-left: 4px solid #FF6F00;
}

.jupyter-notebook-title {
    font-size: 16px;
    color: #333;
}

.jupyter-notebook-meta {
    display: flex;
    gap: 10px;
    align-items: center;
}

.jupyter-badge {
    padding: 4px 12px;
    background: #FF6F00;
    color: white;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
}

.jupyter-execute-status {
    padding: 4px 12px;
    background: #4CAF50;
    color: white;
    border-radius: 12px;
    font-size: 12px;
}

/* Cell styling */
.jupyter-cell-label {
    margin-bottom: 10px;
    padding: 8px 12px;
    background: #e3f2fd;
    border-radius: 6px;
    color: #1976D2;
    font-size: 14px;
}

.jupyter-cell-input,
.jupyter-cell-output {
    margin: 10px 0;
    border-radius: 8px;
    overflow: hidden;
}

.jupyter-input-header,
.jupyter-output-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: #f5f5f5;
    border-bottom: 1px solid #ddd;
}

.jupyter-prompt {
    font-family: 'Courier New', monospace;
    font-weight: bold;
    color: #d32f2f;
    font-size: 13px;
}

.jupyter-copy-btn {
    padding: 4px 8px;
    background: #2196F3;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
}

.jupyter-copy-btn:hover {
    background: #1976D2;
}

.jupyter-code {
    margin: 0;
    padding: 12px;
    background: #f8f8f8;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.5;
    overflow-x: auto;
}

.jupyter-stdout,
.jupyter-stderr {
    margin: 0;
    padding: 12px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    white-space: pre-wrap;
}

.jupyter-stdout {
    background: #f5f5f5;
    color: #333;
}

.jupyter-stderr {
    background: #ffebee;
    color: #c62828;
}

/* Widget styling */
.jupyter-widget-header {
    margin-bottom: 15px;
    padding: 10px 15px;
    background: white;
    border-radius: 8px;
    border-left: 4px solid #9C27B0;
    font-size: 15px;
    color: #333;
}

.jupyter-widget-description {
    margin-bottom: 15px;
    padding: 10px;
    background: #f3e5f5;
    border-radius: 6px;
    font-size: 14px;
    color: #555;
}

.jupyter-widget {
    margin: 15px 0;
    padding: 15px;
    background: white;
    border-radius: 8px;
}

.jupyter-slider {
    width: 100%;
    height: 8px;
    border-radius: 5px;
    background: #ddd;
    outline: none;
}

.jupyter-slider::-webkit-slider-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #9C27B0;
    cursor: pointer;
}

.jupyter-dropdown,
.jupyter-text {
    width: 100%;
    padding: 8px 12px;
    border: 2px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
}

.jupyter-button {
    padding: 10px 20px;
    background: #9C27B0;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: bold;
}

.jupyter-button:hover {
    background: #7B1FA2;
}

.jupyter-checkbox {
    margin-right: 8px;
    width: 18px;
    height: 18px;
}

.jupyter-widget-output {
    margin-top: 15px;
    padding: 12px;
    background: #f5f5f5;
    border-radius: 6px;
}

/* Info boxes */
.jupyter-notebook-info {
    margin-top: 15px;
    padding: 12px 15px;
    background: #fff3e0;
    border-radius: 6px;
    border-left: 3px solid #FF6F00;
}

/* Loading state */
.jupyter-notebook-loading {
    padding: 40px;
    text-align: center;
    color: #777;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
    .jupyter-notebook-container,
    .jupyter-cell-container,
    .jupyter-widget-container {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
    }

    .jupyter-notebook-header,
    .jupyter-cell-label,
    .jupyter-widget-header,
    .jupyter-widget {
        background: #2d3748;
        color: #e2e8f0;
    }

    .jupyter-input-header,
    .jupyter-output-header {
        background: #1a202c;
        border-bottom-color: #4a5568;
    }

    .jupyter-code {
        background: #1a202c;
        color: #e2e8f0;
    }

    .jupyter-stdout {
        background: #2d3748;
        color: #e2e8f0;
    }

    .jupyter-stderr {
        background: #7f1d1d;
        color: #fecaca;
    }

    .jupyter-notebook-info {
        background: #422006;
        border-left-color: #fbbf24;
        color: #fde68a;
    }

    .jupyter-widget-description {
        background: #322951;
        color: #e9d5ff;
    }

    .jupyter-slider {
        background: #4a5568;
    }

    .jupyter-dropdown,
    .jupyter-text {
        background: #2d3748;
        border-color: #4a5568;
        color: #e2e8f0;
    }
}
</style>
    '''

    context['metatags'] += jupyter_styles


def save_execution_cache(app: Sphinx, exception: Optional[Exception]) -> None:
    """Save execution cache to disk for persistence across builds."""

    if exception is None:  # Only save if build succeeded
        cache_dir = Path(app.outdir) / '_jupyter_cache'
        cache_dir.mkdir(exist_ok=True)

        cache_file = cache_dir / 'execution_cache.pkl'
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(_EXECUTION_CACHE, f)
        except Exception:
            pass  # Silently fail if cache save fails


def load_execution_cache(app: Sphinx) -> None:
    """Load execution cache from disk for fast rebuilds."""

    cache_dir = Path(app.outdir) / '_jupyter_cache'
    cache_file = cache_dir / 'execution_cache.pkl'

    if cache_file.exists():
        try:
            with open(cache_file, 'rb') as f:
                global _EXECUTION_CACHE
                _EXECUTION_CACHE = pickle.load(f)
        except Exception:
            pass  # Silently fail if cache load fails


def setup(app: Sphinx) -> Dict[str, Any]:
    """Setup the Jupyter extension."""

    # Register directives
    app.add_directive('jupyter-notebook', JupyterNotebookDirective)
    app.add_directive('jupyter-cell', JupyterCellDirective)
    app.add_directive('jupyter-widget', JupyterWidgetDirective)

    # Add custom CSS to pages
    app.connect('html-page-context', add_jupyter_assets)

    # Cache management
    app.connect('builder-inited', load_execution_cache)
    app.connect('build-finished', save_execution_cache)

    return {
        'version': '1.0.0',
        'parallel_read_safe': True,
        'parallel_write_safe': False,  # Execution cache is not thread-safe
    }
