/**
 * ============================================================================
 * Pyodide Web Worker - Async Python Execution
 * ============================================================================
 *
 * Web Worker for non-blocking Python code execution using Pyodide.
 * Handles loading Pyodide runtime, packages, and executing user code.
 *
 * Features:
 * - Async loading (doesn't block main thread)
 * - stdout/stderr capture
 * - Matplotlib figure extraction
 * - Error handling with stack traces
 * - Package management (NumPy, Matplotlib, SciPy)
 * ============================================================================
 */

// Worker state
let pyodide = null;
let pyodideReady = false;
let packagesLoaded = {
    numpy: false,
    matplotlib: false,
    scipy: false
};

/**
 * Initialize Pyodide runtime
 */
async function initPyodide() {
    try {
        // Load Pyodide from CDN
        self.importScripts('https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js');

        // Initialize Pyodide
        pyodide = await loadPyodide({
            indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/'
        });

        // Set up stdout/stderr capture
        pyodide.runPython(`
import sys
import io

class StdoutCapture(io.StringIO):
    def __init__(self):
        super().__init__()
        self.output = []

    def write(self, text):
        self.output.append(text)
        return len(text)

    def get_output(self):
        return ''.join(self.output)

_stdout = StdoutCapture()
_stderr = StdoutCapture()
sys.stdout = _stdout
sys.stderr = _stderr
        `);

        pyodideReady = true;

        self.postMessage({
            type: 'init-complete',
            success: true
        });

    } catch (error) {
        self.postMessage({
            type: 'init-complete',
            success: false,
            error: error.message
        });
    }
}

/**
 * Load a Python package
 */
async function loadPackage(packageName) {
    if (packagesLoaded[packageName]) {
        return { success: true };
    }

    try {
        await pyodide.loadPackage(packageName);
        packagesLoaded[packageName] = true;

        return { success: true };
    } catch (error) {
        return {
            success: false,
            error: `Failed to load ${packageName}: ${error.message}`
        };
    }
}

/**
 * Execute Python code and capture output
 */
async function executeCode(code, options = {}) {
    if (!pyodideReady) {
        return {
            success: false,
            error: 'Pyodide not initialized. Please wait for initialization to complete.'
        };
    }

    try {
        // Clear previous output
        pyodide.runPython(`
_stdout.output = []
_stderr.output = []
        `);

        // Load required packages if specified
        if (options.packages) {
            for (const pkg of options.packages) {
                const result = await loadPackage(pkg);
                if (!result.success) {
                    return result;
                }
            }
        }

        // Set up matplotlib backend for figure capture
        pyodide.runPython(`
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

_figures = []

def capture_figures():
    """Capture all open matplotlib figures as base64 PNG."""
    global _figures
    _figures = []

    for fig_num in plt.get_fignums():
        fig = plt.figure(fig_num)

        import io
        import base64

        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)

        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        _figures.append(img_base64)

        plt.close(fig)

    return _figures
        `);

        // Execute user code with timeout
        const startTime = Date.now();
        const timeout = options.timeout || 10000; // 10 second default

        // Execute in try-except to catch Python errors
        const executionCode = `
try:
    ${code}

    # Capture any matplotlib figures
    _captured_figures = capture_figures()
except Exception as e:
    import traceback
    _error_traceback = traceback.format_exc()
    raise
        `;

        // Run with timeout check
        await Promise.race([
            pyodide.runPythonAsync(executionCode),
            new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Execution timeout')), timeout)
            )
        ]);

        const executionTime = Date.now() - startTime;

        // Get stdout/stderr
        const stdout = pyodide.runPython('_stdout.get_output()');
        const stderr = pyodide.runPython('_stderr.get_output()');

        // Get captured figures
        const figures = pyodide.runPython('_captured_figures').toJs();

        return {
            success: true,
            stdout: stdout || '',
            stderr: stderr || '',
            figures: Array.from(figures || []),
            executionTime: executionTime
        };

    } catch (error) {
        // Check if it's a Python error with traceback
        let errorMessage = error.message;
        try {
            const traceback = pyodide.runPython('_error_traceback');
            if (traceback) {
                errorMessage = traceback;
            }
        } catch (e) {
            // Traceback not available, use error message
        }

        return {
            success: false,
            error: errorMessage,
            type: error.type || 'PythonError'
        };
    }
}

/**
 * Message handler - processes requests from main thread
 */
self.onmessage = async (event) => {
    const { type, id, code, options } = event.data;

    switch (type) {
        case 'init':
            await initPyodide();
            break;

        case 'execute':
            const result = await executeCode(code, options);
            self.postMessage({
                type: 'result',
                id: id,
                result: result
            });
            break;

        case 'load-package':
            const loadResult = await loadPackage(options.package);
            self.postMessage({
                type: 'package-loaded',
                id: id,
                result: loadResult
            });
            break;

        default:
            self.postMessage({
                type: 'error',
                id: id,
                error: `Unknown message type: ${type}`
            });
    }
};

// Worker ready notification
self.postMessage({ type: 'worker-ready' });
