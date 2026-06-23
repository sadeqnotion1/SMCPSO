#======================================================================================\\\
#==================================== docs/conf.py ====================================\\\
#======================================================================================\\\

"""World-class Sphinx configuration for DIP_SMC_PSO documentation."""

import os
import sys
import subprocess
import inspect
from pathlib import Path
from urllib.parse import quote

# Ensure repository root and `src` are importable for autodoc/linkcode
REPO_ROOT = Path(__file__).parent.parent.resolve()
SRC_PATH = REPO_ROOT / "src"
SCRIPTS_PATH = REPO_ROOT / "scripts"
EXT_PATH = Path(__file__).parent / "_ext"
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SRC_PATH))
sys.path.insert(0, str(SCRIPTS_PATH))
sys.path.insert(0, str(EXT_PATH))

# Project information
project = 'DIP_SMC_PSO'
author = 'Research Team'
copyright = '2024, Research Team'
release = '1.0.0'

# Exclude patterns - files/directories to ignore during build
exclude_patterns = [
    '_build',                    # Build output directory
    'Thumbs.db',                # Windows thumbnail cache
    '.DS_Store',                # macOS folder metadata
    '.github/**',               # GitHub templates and workflows
    '**.ipynb_checkpoints',     # Jupyter notebook checkpoints
    'implementation/api/**',    # Auto-generated API docs (autosummary disabled)
    'implementation/legacy_*.md',   # Legacy documentation with autosummary

    # All directories successfully re-included after fixing docutils transition errors
    # Previously excluded directories are now building without errors
    # 'advanced/**',       # Re-included - All directories (Phase 2 accelerated)
    # 'analysis/**',
    # 'api/**',            # Re-included - Step 3 (Batch 1)
    # 'architecture/**',   # Re-included - Step 3 (Batch 1)
    # 'benchmarks/**',     # Re-included - Step 3 (Batch 1)
    # 'code_quality/**',
    # 'controllers/**',    # Re-included for testing - Step 1 of gradual re-inclusion
    # 'coverage/**',
    # 'deployment/**',
    # 'development/**',
    # 'examples/**',
    # 'factory/**',        # Re-included for testing - Step 2 of gradual re-inclusion
    # 'for_reviewers/**',  # Re-included - Phase 1.1: Content completeness
    # 'optimization_simulation/**',  # Re-included - Phase 1.2: Content completeness
    # 'guides/**',
    # 'hil/**',
    # 'how-to/**',
    'implementation/**',   # Keep excluded - contains legacy autosummary docs
    # 'integration/**',
    # 'optimization/**',
    # 'plant/**',
    # 'production/**',
    # 'reference/**',
    # 'resources/**',
    # 'security/**',
    # 'simulation/**',
    # 'streamlit/**',
    # 'style/**',
    # 'theory/**',
    # 'troubleshooting/**',
    # 'utils/**',
    # 'workflows/**',
    # '*quickstart*',
    # '*GUIDE*',
    # '*guide*',
    # '*technical*',
    # '*verification*',
]

# Extensions - comprehensive set for world-class docs
extensions = [
    # Core Sphinx extensions
    'sphinx.ext.autodoc',         # Auto-generate docs from docstrings
    # 'sphinx.ext.autosummary',     # Temporarily disabled for testing
    'sphinx.ext.napoleon',        # Google/NumPy style docstrings
    'sphinx.ext.viewcode',        # Add source code links
    'sphinx.ext.linkcode',        # Permalinks to GitHub
    'sphinx.ext.githubpages',     # Emit .nojekyll for GitHub Pages
    # 'sphinx.ext.mathjax',       # DISABLED (Wave 2 LCP): Loads MathJax on ALL pages
    'sphinx.ext.intersphinx',     # Replaced with mathjax_extension (conditional loading)
    # 'sphinx.ext.autosectionlabel',  # DISABLED Phase 1 Day 3: Causes O(n²) slowdown with 788 files

    # External extensions
    'myst_parser',
    'sphinxcontrib.bibtex',       # Bibliography support
    'sphinx_copybutton',
    'sphinx_design',
    'sphinxcontrib.mermaid',  # Re-enabled after replacing Greek letters with ASCII
    # 'sphinx_reredirects',  # Temporarily disabled for testing
    'sphinx.ext.doctest',         # Test code blocks
    'sphinx.ext.duration',
    # 'sphinx_gallery.gen_gallery', # Temporarily disabled for testing
    # 'traceability',               # Temporarily disabled for testing

    # Custom extensions
    'chartjs_extension',          # Chart.js interactive visualizations
    'pyodide_extension',          # Pyodide live Python code execution (Phase 2)
    'plotly_extension',           # Plotly interactive charts (Phase 3)
    'nbsphinx',                   # Jupyter notebook integration (Phase 4 - base)
    'jupyter_extension',          # Custom Jupyter directives (Phase 4 - custom)
    'mathviz_extension',          # Mathematical visualization library (Phase 5)
    'mathjax_extension',          # Conditional MathJax loading (Wave 2 LCP optimization)
    'search_index_generator',     # Custom Lunr.js search index generator
]

# MyST Parser configuration - quality-of-life features
myst_enable_extensions = [
    'dollarmath',      # $...$ for inline math
    'amsmath',         # amsmath LaTeX extension
    'colon_fence',     # ::: fences for directives
    'deflist',         # definition lists
    'tasklist',        # GitHub-style task lists
    'fieldlist',       # field lists
    'linkify',         # auto-link URLs
]
myst_heading_anchors = 3
myst_update_mathjax = False  # CRITICAL (Wave 2 LCP): Disable MyST's automatic MathJax injection
                             # Our mathjax_extension handles conditional loading instead

# nbsphinx configuration - Jupyter notebook integration (Phase 4)
nbsphinx_execute = 'auto'  # Execute notebooks during build (cached with jupyter-cache)
nbsphinx_allow_errors = False  # Fail build on notebook errors for quality control
nbsphinx_timeout = 180  # 3 minutes maximum per cell execution
nbsphinx_kernel_name = 'python3'  # Use Python 3 kernel
nbsphinx_execute_arguments = [
    '--InlineBackend.figure_formats={"svg", "pdf"}',
    '--InlineBackend.rc={"figure.dpi": 96}',
]

# MathJax configuration - globally numbered equations
mathjax3_config = {
    'tex': {
        'tags': 'all',           # Number all equations
        'tagSide': 'right',      # Put numbers on the right
        'macros': {
            'vec': ['\\boldsymbol{#1}', 1],
            'mat': ['\\boldsymbol{#1}', 1],
            'norm': ['\\left\\|#1\\right\\|', 1],
            'R': '\\mathbb{R}',
            'C': '\\mathbb{C}',
            'N': '\\mathbb{N}',
            'Z': '\\mathbb{Z}',
        }
    }
}

# Figure and table numbering for cross-references
numfig = True
numfig_secnum_depth = 2
numfig_format = {
    'figure': 'Figure %s',
    'table': 'Table %s',
    'code-block': 'Listing %s',
}

# Bibliography configuration
bibtex_bibfiles = [
    'reference/legacy/refs.bib',  # Main bibliography file (moved from root in Phase 1)
    'bib/smc.bib',         # Sliding mode control references
    'bib/pso.bib',         # PSO optimization references
    'bib/dip.bib',         # Double inverted pendulum references
    'bib/software.bib',    # Software and tools references
    'bib/stability.bib',   # Lyapunov stability and finite-time stability
    'bib/adaptive.bib',    # Adaptive control theory
    'bib/fdi.bib',         # Fault detection and isolation
    'bib/numerical.bib',   # Numerical methods and integration
]
bibtex_default_style = 'alpha'  # Built-in alphabetic style

# Auto-section labeling for stable cross-references (DISABLED Phase 1 Day 3)
# autosectionlabel_prefix_document = True

# Autodoc configuration - generates API docs from source code
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'

# Autosummary configuration - temporarily disabled for testing
# autosummary_generate = True
# autosummary_imported_members = True

# Intersphinx mapping for external documentation
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
}

# HTML theme configuration
html_theme = 'furo'  # Modern, responsive theme
html_title = f'{project} Documentation'
html_static_path = ['_static']

html_theme_options = {
    'sidebar_hide_name': False,
    'navigation_with_keys': True,
    # Removed 'top_of_page_button' - deprecated in Furo, uses built-in back-to-top automatically
    'source_repository': 'https://github.com/theSadeQ/DIP_SMC_PSO/',
    'source_branch': 'main',
    'source_directory': 'docs/',
}

# PWA Manifest and meta tags (Phase 6)
def add_pwa_tags(app, pagename, templatename, context, doctree):
    """Add PWA meta tags, manifest link, and Apple touch icon to HTML head."""
    pwa_tags = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#667eea">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="DIP SMC">
<meta name="application-name" content="DIP SMC Documentation">
<meta name="msapplication-TileColor" content="#667eea">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/_static/icons/icon-192x192.png">
'''

    # Inject via head_extra context variable
    if 'head_extra' not in context:
        context['head_extra'] = ''
    context['head_extra'] += pwa_tags

def setup(app):
    """Sphinx extension setup - Add PWA support."""
    # Add PWA tags to every page
    app.connect('html-page-context', add_pwa_tags)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }

# Custom CSS and JavaScript files
html_css_files = [
    'custom.css',
    'beginner-roadmap.css',  # Beginner roadmap phase styling (Week 2)
    'code-collapse.css',
    'code-runner.css',  # Pyodide live code execution styles (Phase 2)
    'mathviz.css',  # Mathematical visualization library styles (Phase 5)
    'search.css',  # Lunr.js search UI styles (custom implementation)

    # REMOVED FROM GLOBAL LOADING (Wave 2 LCP optimization - CSS files):
    # These CSS files are 100% unused on homepage, now load conditionally via extensions:
    # - 'visual-tree.css' (0% used on homepage) → loads only on pages with visual-tree directive
    # - 'threejs-pendulum.css' (0% used) → loads only on pages with threejs-pendulum directive
    # - 'plotly-charts.css' (0% used) → loads only on pages with plotly-chart directive
    # - 'pwa.css' (0% used) → loads only when PWA features enabled
    # Total savings: 36 KB transfer size, 988ms CSS blocking time
]

html_js_files = [
    # Search functionality (Lunr.js from CDN)
    ('https://cdn.jsdelivr.net/npm/lunr@2.3.9/lunr.min.js', {'defer': 'defer'}),

    # Core lightweight utilities (load on all pages)
    # 'back-to-top.js',  # Disabled - replaced by unified handler (Nov 2025)
    # 'smooth-scroll-fix.js',  # Disabled - replaced by unified handler (Nov 2025)
    'unified-back-to-top.js',  # Unified visibility manager: syncs Furo + custom systems (Nov 2025)
    'lazy-load.js',
    'dark-mode.js',
    'visual-sitemap.js',
    'control-room.js',
    'code-collapse.js',
    'fix-caption-aria.js',  # Wave 1 validation fix: aria-level for caption headings
    'search.js',  # Custom Lunr.js search UI (loads after lunr.min.js)

    # REMOVED FROM GLOBAL LOADING (Wave 2 LCP optimization):
    # Heavyweight visualization libraries now load ONLY on pages that use them
    # via custom Sphinx extensions (pyodide_extension, plotly_extension, etc.)
    #
    # Previously loaded globally (causing 18.4s JS bootup, 7.6s LCP regression):
    # - Pyodide (16.5s execution): pyodide.js, pyodide-worker.js, pyodide-runner.js
    # - Plotly (1066 KB): plotly-2.27.0.min.js, plotly-integration.js
    # - Three.js (158 KB): three.min.js, OrbitControls.js, threejs-pendulum.js
    # - MathViz (45 KB): mathviz-interactive.js
    # - PWA (15 KB): pwa-register.js
    #
    # Wave 2 Fix: Extensions inject these scripts only when directive is used:
    # - .. pyodide:: directive -> loads Pyodide on that page only
    # - .. plotly-chart:: directive -> loads Plotly on that page only
    # - .. threejs-pendulum:: directive -> loads Three.js on that page only
]

# HTML output options
html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True
html_last_updated_fmt = '%b %d, %Y'

# Copy button configuration
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
copybutton_exclude = '.linenos, .gp, .go'

# Code highlighting configuration - Pygments
pygments_style = 'monokai'  # Dark mode compatible
pygments_dark_style = 'monokai'  # Explicit dark mode style

# Literalinclude default options for embedded source code
highlight_language = 'python'
highlight_options = {
    'stripnl': False,  # Keep newlines at start/end
}

# Default options for literalinclude directive (Week 1 automation)
# These apply to all literalinclude blocks unless overridden
literalinclude_default_options = {
    'linenos': True,           # Show line numbers by default
    'dedent': 0,               # No automatic dedentation
    'encoding': 'utf-8',       # File encoding
    'tab-width': 4,            # Tab width for display
}

# Mermaid configuration - use client-side rendering (no CLI required)
mermaid_output_format = 'raw'  # Embed Mermaid code for browser rendering
mermaid_init_js = "mermaid.initialize({startOnLoad:true,theme:'neutral'});"

# LaTeX output configuration (for PDF generation)
latex_engine = 'pdflatex'
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': r'''
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
''',
}

# Build configuration - strict mode for CI
if os.environ.get('READTHEDOCS'):
    # Suppress some warnings on RTD
    suppress_warnings = [
        'epub.unknown_project_files',
        'app.add_directive',  # Suppress deprecated extension warnings
        'toc.not_included',  # Suppress orphaned document warnings during migration
        'autodoc.import_object',  # Suppress autodoc import errors (Phase 9F)
    ]
else:
    # Strict mode for local development
    suppress_warnings = [
        'app.add_directive',  # Suppress deprecated extension warnings (sphinxcontrib.autoclassdiag)
        'toc.not_included',  # Suppress orphaned document warnings during migration
        'autodoc.import_object',  # Suppress autodoc import errors (Phase 9F)
    ]

# Parallel build configuration for faster builds (OPTIMIZED Phase 1 Day 3)
parallel_jobs = 8  # Increased from 4 to 8 for faster source reading

# Redirects for moved pages (disabled while sphinx_reredirects extension is unavailable)
# redirects = {
#     # Legacy landing pages moved to new Reference IA
#     'controllers/index': 'reference/controllers/index',
#     'optimization/index': 'reference/optimizer/index',
#     'implementation/index': 'reference/index',
#     'implementation/code_documentation_index': 'reference/index',
#     # Controllers detail pages
#     'controllers/classical-smc': 'reference/controllers/classical-smc',
#     'controllers/super-twisting-smc': 'reference/controllers/super-twisting-smc',
#     'controllers/adaptive-smc': 'reference/controllers/adaptive-smc',
#     'controllers/hybrid-adaptive-smc': 'reference/controllers/hybrid-adaptive-smc',
# }

# ----------------------------- GitHub linkcode ------------------------------
GITHUB_USER = "theSadeQ"
GITHUB_REPO = "DIP_SMC_PSO"

def _get_commit_sha():
    """Return a commit SHA for permalinks or 'main' as fallback.

    Order of preference: GITHUB_SHA -> READTHEDOCS_GIT_IDENTIFIER -> git HEAD -> 'main'
    """
    for env in ("GITHUB_SHA", "READTHEDOCS_GIT_IDENTIFIER"):
        v = os.getenv(env)
        if v and len(v) >= 7:
            return v
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "main"


def linkcode_resolve(domain, info):
    """Resolve GitHub permalink to source code with line anchors.

    Returns None for unsupported or missing info, otherwise a URL like:
    https://github.com/<user>/<repo>/blob/<sha>/<path>#L<start>-L<end>
    """
    if domain != "py":
        return None

    modname = info.get("module")
    fullname = info.get("fullname")
    if not modname or not fullname:
        return None

    try:
        submod = __import__(modname, fromlist=["*"])
        obj = submod
        for part in fullname.split("."):
            obj = getattr(obj, part)

        # Unwrap common wrappers
        if isinstance(obj, property):
            obj = obj.fget
        elif isinstance(obj, (classmethod, staticmethod)):
            obj = obj.__func__
        elif hasattr(obj, "__wrapped__"):
            obj = obj.__wrapped__
        elif hasattr(obj, "func"):
            obj = obj.func

        fn = inspect.getsourcefile(inspect.unwrap(obj))
        if fn is None:
            return None
        source, lineno = inspect.getsourcelines(obj)
    except Exception:
        return None

    try:
        rel_fn = Path(fn).resolve().relative_to(REPO_ROOT)
    except Exception:
        return None

    rel_fn_posix = str(rel_fn).replace(os.sep, "/")
    start_line = lineno
    end_line = lineno + len(source) - 1
    sha = _get_commit_sha()

    return (
        f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/blob/{quote(sha)}/"
        f"{quote(rel_fn_posix)}#L{start_line}-L{end_line}"
    )


# Mock heavy dependencies to keep doc builds lightweight
autodoc_mock_imports = [
    'numpy', 'scipy', 'matplotlib', 'control', 'pyswarms', 'optuna', 'numba',
    'streamlit', 'pandas', 'yaml', 'pydantic', 'pydantic_settings'
]


# ----------------------------- Sphinx-Gallery -------------------------------
# Temporarily disabled while sphinx_gallery extension is unavailable
# # Run only fast examples in CI when DOCS_FAST=1 is set
# _fast_mode = os.environ.get("DOCS_FAST")
# _filename_pattern = r"^plot_fast_" if _fast_mode else r"^plot_"
#
# sphinx_gallery_conf = {
#     'examples_dirs': ['examples'],      # relative to docs/
#     'gallery_dirs': ['auto_examples'],  # built gallery target
#     'filename_pattern': _filename_pattern,
#     'ignore_pattern': r"_heavy|_skip",
#     'min_reported_time': 0,
#     'remove_config_comments': True,
# }


# ----------------------------- Link Checker -------------------------------
# Configuration for 'sphinx-build -b linkcheck' builder
# Validates external URLs and intersphinx references

linkcheck_ignore = [
    r'http://localhost:\d+',              # Local development servers
    r'https://github.com/.*/issues/\d+',  # GitHub issues (may be private)
    r'https://github.com/.*/pull/\d+',    # GitHub PRs (may be private)
    r'https://.*\.local',                 # Local network resources
    r'https://example\.com',              # Example URLs in documentation
]

linkcheck_timeout = 15        # Seconds per URL (default: 10)
linkcheck_workers = 8         # Parallel workers (match parallel_jobs)
linkcheck_retries = 2         # Retry failed URLs
linkcheck_anchors = True      # Validate HTML anchors
linkcheck_anchors_ignore = [
    r'^\!',                   # Skip anchors starting with !
    r'^#$',                   # Skip empty anchors
]
