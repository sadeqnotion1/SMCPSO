/**
 * ============================================================================
 * Pyodide Code Runner - Main Controller
 * ============================================================================
 *
 * Manages interactive Python code blocks with Pyodide execution.
 * Handles UI, Worker communication, output display, and code persistence.
 *
 * Features:
 * - Run/Reset buttons for code blocks
 * - Inline code editing with ContentEditable
 * - Output panels (stdout, stderr, figures)
 * - Loading indicators with progress
 * - Error display with clear formatting
 * - LocalStorage code persistence
 * - Keyboard shortcuts (Ctrl+Enter to run)
 * ============================================================================
 */

class PyodideRunner {
    constructor(codeBlockElement, options = {}) {
        this.element = codeBlockElement;
        this.code = codeBlockElement.textContent;
        this.originalCode = this.code;
        this.codeId = options.id || `code-${Math.random().toString(36).substr(2, 9)}`;
        this.options = options;

        // State
        this.isRunning = false;
        this.executionCount = 0;

        // UI elements
        this.ui = {};

        // Initialize
        this.setupUI();
        this.loadFromLocalStorage();
        this.setupKeyboardShortcuts();
    }

    /**
     * Set up UI components
     */
    setupUI() {
        // Wrap code block in container
        const container = document.createElement('div');
        container.className = 'code-runner-container';
        container.setAttribute('data-code-id', this.codeId);

        this.element.parentNode.insertBefore(container, this.element);
        container.appendChild(this.element);

        // Make code editable
        this.element.contentEditable = this.options.readonly ? 'false' : 'true';
        this.element.spellcheck = false;
        this.element.className += ' editable-code';

        // Add event listener for code changes
        this.element.addEventListener('input', () => {
            this.code = this.element.textContent;
            this.saveToLocalStorage();
        });

        // Create control buttons
        const controls = document.createElement('div');
        controls.className = 'code-controls';

        // Run button
        const runBtn = document.createElement('button');
        runBtn.className = 'code-btn code-btn-run';
        runBtn.innerHTML = '▶ Run Code';
        runBtn.onclick = () => this.runCode();
        controls.appendChild(runBtn);
        this.ui.runBtn = runBtn;

        // Reset button
        const resetBtn = document.createElement('button');
        resetBtn.className = 'code-btn code-btn-reset';
        resetBtn.innerHTML = '⟲ Reset';
        resetBtn.onclick = () => this.resetCode();
        controls.appendChild(resetBtn);
        this.ui.resetBtn = resetBtn;

        // Loading indicator
        const loading = document.createElement('div');
        loading.className = 'code-loading';
        loading.style.display = 'none';
        loading.innerHTML = `
            <div class="loading-spinner"></div>
            <span class="loading-text">Initializing Python...</span>
        `;
        controls.appendChild(loading);
        this.ui.loading = loading;

        container.insertBefore(controls, this.element);

        // Output panel
        const outputPanel = document.createElement('div');
        outputPanel.className = 'code-output';
        outputPanel.style.display = 'none';
        container.appendChild(outputPanel);
        this.ui.outputPanel = outputPanel;
    }

    /**
     * Set up keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        this.element.addEventListener('keydown', (e) => {
            // Ctrl+Enter or Cmd+Enter to run
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.runCode();
            }

            // Tab key to insert 4 spaces
            if (e.key === 'Tab') {
                e.preventDefault();
                document.execCommand('insertText', false, '    ');
            }
        });
    }

    /**
     * Run Python code
     */
    async runCode() {
        if (this.isRunning) {
            return;
        }

        this.isRunning = true;
        this.executionCount++;

        try {
            // Show loading
            this.showLoading('Executing Python...');
            this.clearOutput();

            // Initialize worker if needed
            if (!window.pyodideWorker) {
                this.showLoading('Loading Python runtime... (15-30s first time)');
                await this.initializeWorker();
            }

            // Execute code
            const result = await this.executeInWorker(this.code);

            // Display results
            this.displayResult(result);

        } catch (error) {
            this.displayError(error.message || 'Unknown error occurred');
        } finally {
            this.hideLoading();
            this.isRunning = false;
        }
    }

    /**
     * Initialize Pyodide Worker
     */
    initializeWorker() {
        return new Promise((resolve, reject) => {
            // Create worker
            const worker = new Worker('/docs/_static/pyodide-worker.js');
            window.pyodideWorker = worker;
            window.pyodideWorkerReady = false;

            // Track pending callbacks
            window.pyodideCallbacks = new Map();

            // Message handler
            worker.onmessage = (event) => {
                const { type, id, result } = event.data;

                if (type === 'worker-ready') {
                    // Worker script loaded
                    worker.postMessage({ type: 'init' });
                }

                if (type === 'init-complete') {
                    if (result && result.success === false) {
                        reject(new Error('Failed to initialize Pyodide'));
                    } else {
                        window.pyodideWorkerReady = true;
                        resolve();
                    }
                }

                if (type === 'result') {
                    const callback = window.pyodideCallbacks.get(id);
                    if (callback) {
                        callback.resolve(result);
                        window.pyodideCallbacks.delete(id);
                    }
                }
            };

            worker.onerror = (error) => {
                reject(error);
            };

            // Timeout after 60 seconds
            setTimeout(() => {
                if (!window.pyodideWorkerReady) {
                    reject(new Error('Pyodide initialization timeout'));
                }
            }, 60000);
        });
    }

    /**
     * Execute code in Worker
     */
    executeInWorker(code) {
        return new Promise((resolve, reject) => {
            const id = `exec-${Date.now()}-${Math.random()}`;

            // Store callback
            window.pyodideCallbacks.set(id, { resolve, reject });

            // Send to worker
            window.pyodideWorker.postMessage({
                type: 'execute',
                id: id,
                code: code,
                options: {
                    packages: ['numpy', 'matplotlib'],
                    timeout: this.options.timeout || 10000
                }
            });

            // Timeout
            setTimeout(() => {
                if (window.pyodideCallbacks.has(id)) {
                    window.pyodideCallbacks.delete(id);
                    reject(new Error('Execution timeout (10 seconds)'));
                }
            }, this.options.timeout || 10000);
        });
    }

    /**
     * Display execution result
     */
    displayResult(result) {
        this.ui.outputPanel.style.display = 'block';

        let html = '';

        // Execution info
        html += `<div class="output-header">`;
        html += `<span class="output-label">Execution #${this.executionCount}</span>`;
        html += `<span class="output-time">${result.executionTime}ms</span>`;
        html += `</div>`;

        // stdout
        if (result.stdout) {
            html += `<div class="output-section output-stdout">`;
            html += `<div class="output-section-header">Output:</div>`;
            html += `<pre>${this.escapeHtml(result.stdout)}</pre>`;
            html += `</div>`;
        }

        // stderr (warnings)
        if (result.stderr) {
            html += `<div class="output-section output-stderr">`;
            html += `<div class="output-section-header">Warnings:</div>`;
            html += `<pre>${this.escapeHtml(result.stderr)}</pre>`;
            html += `</div>`;
        }

        // Figures
        if (result.figures && result.figures.length > 0) {
            html += `<div class="output-section output-figures">`;
            html += `<div class="output-section-header">Figures (${result.figures.length}):</div>`;
            result.figures.forEach((figData, index) => {
                html += `<img src="data:image/png;base64,${figData}" alt="Figure ${index + 1}" class="output-figure">`;
            });
            html += `</div>`;
        }

        // Success message if no output
        if (!result.stdout && !result.stderr && (!result.figures || result.figures.length === 0)) {
            html += `<div class="output-section output-success">`;
            html += `<div class="output-message">✓ Code executed successfully (no output)</div>`;
            html += `</div>`;
        }

        this.ui.outputPanel.innerHTML = html;
    }

    /**
     * Display error
     */
    displayError(errorMessage) {
        this.ui.outputPanel.style.display = 'block';

        let html = '';
        html += `<div class="output-header output-header-error">`;
        html += `<span class="output-label">Error</span>`;
        html += `</div>`;

        html += `<div class="output-section output-error">`;
        html += `<div class="output-section-header">Error:</div>`;
        html += `<pre>${this.escapeHtml(errorMessage)}</pre>`;
        html += `</div>`;

        html += `<div class="output-section output-help">`;
        html += `<strong>Troubleshooting:</strong><br>`;
        html += `• Check for syntax errors (missing colons, indentation)<br>`;
        html += `• Verify all variables are defined<br>`;
        html += `• Make sure imports are correct<br>`;
        html += `• Try running code step-by-step`;
        html += `</div>`;

        this.ui.outputPanel.innerHTML = html;
    }

    /**
     * Show loading indicator
     */
    showLoading(message) {
        this.ui.loading.style.display = 'flex';
        this.ui.loading.querySelector('.loading-text').textContent = message;
        this.ui.runBtn.disabled = true;
        this.ui.resetBtn.disabled = true;
    }

    /**
     * Hide loading indicator
     */
    hideLoading() {
        this.ui.loading.style.display = 'none';
        this.ui.runBtn.disabled = false;
        this.ui.resetBtn.disabled = false;
    }

    /**
     * Clear output
     */
    clearOutput() {
        this.ui.outputPanel.innerHTML = '';
        this.ui.outputPanel.style.display = 'none';
    }

    /**
     * Reset code to original
     */
    resetCode() {
        this.element.textContent = this.originalCode;
        this.code = this.originalCode;
        this.clearOutput();
        this.removeFromLocalStorage();
    }

    /**
     * Save edited code to LocalStorage
     */
    saveToLocalStorage() {
        try {
            const key = `pyodide-code-${this.codeId}`;
            localStorage.setItem(key, this.code);
        } catch (e) {
            console.warn('LocalStorage not available');
        }
    }

    /**
     * Load edited code from LocalStorage
     */
    loadFromLocalStorage() {
        try {
            const key = `pyodide-code-${this.codeId}`;
            const saved = localStorage.getItem(key);
            if (saved) {
                this.element.textContent = saved;
                this.code = saved;
            }
        } catch (e) {
            console.warn('LocalStorage not available');
        }
    }

    /**
     * Remove from LocalStorage
     */
    removeFromLocalStorage() {
        try {
            const key = `pyodide-code-${this.codeId}`;
            localStorage.removeItem(key);
        } catch (e) {
            console.warn('LocalStorage not available');
        }
    }

    /**
     * Escape HTML for safe display
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

/**
 * Initialize all runnable code blocks on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    // Find all runnable code blocks (marked by Sphinx extension)
    const runnableBlocks = document.querySelectorAll('.runnable-code');

    runnableBlocks.forEach((block) => {
        const codeId = block.getAttribute('data-code-id');
        const timeout = parseInt(block.getAttribute('data-timeout')) || 10000;
        const readonly = block.getAttribute('data-readonly') === 'true';

        new PyodideRunner(block, {
            id: codeId,
            timeout: timeout,
            readonly: readonly
        });
    });

    console.log(`Initialized ${runnableBlocks.length} runnable code blocks`);
});
