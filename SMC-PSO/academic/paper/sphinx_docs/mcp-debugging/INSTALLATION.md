# MCP Installation Guide

**Last Updated:** November 9, 2025

Complete installation guide for all 13 MCP (Model Context Protocol) servers used in the DIP-SMC-PSO project.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Install (All Servers)](#quick-install-all-servers)
3. [Individual Server Installation](#individual-server-installation)
4. [Custom Python Servers](#custom-python-servers)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

#### Node.js and npm

**Version:** Node.js 18.x or higher

**Check if installed:**
```bash
node --version
npm --version
```

**Installation:**

**Windows:**
- Download installer: https://nodejs.org/en/download/
- Run installer and follow prompts
- Verify: `node --version` (should show v18.x or higher)

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**macOS:**
```bash
brew install node@18
```

#### Python and pip

**Version:** Python 3.9 or higher

**Check if installed:**
```bash
python --version
pip --version
```

**Installation:**

**Windows:**
- Download installer: https://www.python.org/downloads/
- Check "Add Python to PATH" during installation
- Verify: `python --version` (should show 3.9.x or higher)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3.9 python3-pip
```

**macOS:**
```bash
brew install python@3.9
```

### Required Python Packages

```bash
pip install pandas numpy
```

These are needed for custom pandas-mcp and numpy-mcp servers.

---

## Quick Install (All Servers)

### Step 1: Install Official MCP Servers

```bash
npm install -g @modelcontextprotocol/server-filesystem @modelcontextprotocol/server-github @modelcontextprotocol/server-sequential-thinking @modelcontextprotocol/server-puppeteer
```

**Expected Output:**
```
added 324 packages in 45s
```

### Step 2: Install Community MCP Servers

```bash
npm install -g @cyanheads/git-mcp-server pytest-mcp-server mcp-sqlite mcp-debugger lighthouse-mcp
```

**Expected Output:**
```
added 888 packages in 90s
```

### Step 3: Install Python MCP Server

```bash
pip install mcp-server-analyzer
```

**Expected Output:**
```
Successfully installed mcp-server-analyzer
```

### Step 4: Install npx-based Server

```bash
npx -y @context7/mcp --version
```

**Note:** This server uses npx and will download on first use.

### Step 5: Verify Installation

```bash
python .project/dev_tools/check_mcp_health.py
```

**Expected Output:**
```
[INFO] Checking 13 MCP servers...

[OK] filesystem              - Operational
[OK] github                  - Operational
[OK] sequential-thinking     - Operational (stdio)
[OK] puppeteer               - Operational
[OK] mcp-debugger            - Operational
[OK] pytest-mcp              - Operational
[OK] git-mcp                 - Operational
[OK] sqlite-mcp              - Operational
[OK] mcp-analyzer            - Operational (module)
[OK] context7                - Operational (npx)
[OK] lighthouse-mcp          - Operational (standalone)
[OK] pandas-mcp              - Operational (file)
[OK] numpy-mcp               - Operational (file)

[OK] All MCP servers are operational!
```

---

## Individual Server Installation

### Official MCP Servers

#### 1. Filesystem Server

**Purpose:** File system access for code and log analysis

```bash
npm install -g @modelcontextprotocol/server-filesystem
```

**Verification:**
```bash
node "C:\Program Files\nodejs\node_modules\@modelcontextprotocol\server-filesystem\dist\index.js" --help
```

#### 2. GitHub Server

**Purpose:** GitHub integration for issue tracking and repository management

```bash
npm install -g @modelcontextprotocol/server-github
```

**Additional Setup:**
Set GitHub token as environment variable:

**Windows (PowerShell):**
```powershell
[System.Environment]::SetEnvironmentVariable('GITHUB_TOKEN', 'your-token-here', 'User')
```

**Linux/Mac:**
```bash
echo 'export GITHUB_TOKEN=your-token-here' >> ~/.bashrc
source ~/.bashrc
```

**Get GitHub Token:**
1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `read:org`, `read:user`
4. Copy token and set as environment variable

**Verification:**
```bash
node "C:\Program Files\nodejs\node_modules\@modelcontextprotocol\server-github\dist\index.js" --help
```

#### 3. Sequential-Thinking Server (ultrathink)

**Purpose:** Methodical problem-solving and debugging workflows

```bash
npm install -g @modelcontextprotocol/server-sequential-thinking
```

**Verification:**
```bash
node "C:\Program Files\nodejs\node_modules\@modelcontextprotocol\server-sequential-thinking\dist\index.js" --help
```

**Expected Output:**
```
Sequential Thinking MCP Server running on stdio
```

#### 4. Puppeteer Server

**Purpose:** Browser automation for Streamlit dashboard testing

```bash
npm install -g @modelcontextprotocol/server-puppeteer
```

**Note:** First run will download Chromium (approx. 150MB).

**Verification:**
```bash
node "C:\Program Files\nodejs\node_modules\@modelcontextprotocol\server-puppeteer\dist\index.js" --help
```

### Community MCP Servers

#### 5. Git MCP Server

**Purpose:** Comprehensive Git operations and version control

```bash
npm install -g @cyanheads/git-mcp-server
```

**Verification:**
```bash
node "C:\Program Files\nodejs\node_modules\@cyanheads\git-mcp-server\dist\index.js" --help
```

#### 6. Pytest MCP Server

**Purpose:** Pytest test failure tracking and debugging

```bash
npm install -g pytest-mcp-server
```

**Verification:**
```bash
node "C:\Program Files\nodejs\node_modules\pytest-mcp-server\dist\cli.js" --help
```

#### 7. SQLite MCP Server

**Purpose:** SQLite database operations for PSO results analysis

```bash
npm install -g mcp-sqlite
```

**Verification:**
```bash
node "C:\Program Files\nodejs\node_modules\mcp-sqlite\mcp-sqlite-server.js" --help
```

#### 8. MCP Debugger

**Purpose:** Postman collection debugging and API testing

```bash
npm install -g mcp-debugger
```

**Verification:**
```bash
node "C:\Program Files\nodejs\node_modules\mcp-debugger\bin\mcp-debugger.js" --help
```

#### 9. Lighthouse MCP Server

**Purpose:** Automated Lighthouse accessibility and performance audits

```bash
npm install -g lighthouse-mcp
```

**Verification:**
```bash
lighthouse-mcp --version
```

**Troubleshooting:**
If `lighthouse-mcp` is not in PATH, add to PATH manually or use full path in `.mcp.json`.

### Python MCP Servers

#### 10. MCP Analyzer

**Purpose:** RUFF linting and VULTURE dead code detection

```bash
pip install mcp-server-analyzer
```

**Verification:**
```bash
python -m mcp_server_analyzer --help
```

**Expected Output:**
```
[INFO] MCP Analyzer Server started on stdio
```

### npx-based MCP Servers

#### 11. Context7 Server

**Purpose:** Intelligent context search and semantic retrieval across documentation and codebase

```bash
npx -y @context7/mcp --version
```

**Note:** Downloads on first use (approx. 50MB). Cached for future use.

**Verification:**
```bash
npx -y @context7/mcp --version
```

---

## Custom Python Servers

### 12. Pandas MCP Server

**Purpose:** Advanced data analysis and visualization of PSO convergence and simulation results

**Prerequisites:**
```bash
pip install pandas numpy
```

**Server Location:**
```
D:\Projects\main\.project\mcp\servers\pandas-mcp\server.py
```

**Verify File Exists:**
```bash
stat D:\Projects\main\.project\mcp\servers\pandas-mcp\server.py
```

**Test Server:**
```bash
python D:\Projects\main\.project\mcp\servers\pandas-mcp\server.py
```

**Expected Output:**
```
[INFO] Pandas MCP Server started on stdio
```

Press `Ctrl+C` to stop.

**Capabilities:**
- `load_csv`: Load CSV file and return summary (shape, columns, dtypes, head, stats)
- `analyze`: Analyze data in CSV file (column-specific or full summary)

**Example Usage (JSON-RPC over stdio):**
```json
{"id": 1, "method": "load_csv", "params": {"filepath": "data.csv"}}
{"id": 2, "method": "analyze", "params": {"filepath": "data.csv", "column": "error"}}
```

### 13. NumPy MCP Server

**Purpose:** Numerical computations, matrix operations, statistical analysis for control systems

**Prerequisites:**
```bash
pip install numpy
```

**Server Location:**
```
D:\Projects\main\.project\mcp\servers\numpy-mcp\server.py
```

**Verify File Exists:**
```bash
stat D:\Projects\main\.project\mcp\servers\numpy-mcp\server.py
```

**Test Server:**
```bash
python D:\Projects\main\.project\mcp\servers\numpy-mcp\server.py
```

**Expected Output:**
```
[INFO] NumPy MCP Server started on stdio
```

Press `Ctrl+C` to stop.

**Capabilities:**
- `matrix_op`: Matrix operations (eigenvalues, inverse, multiply)
- `stats`: Statistical analysis (mean, median, std, var, min, max)

**Example Usage (JSON-RPC over stdio):**
```json
{"id": 1, "method": "matrix_op", "params": {"operation": "eigenvalues", "matrix_a": [[1, 2], [3, 4]]}}
{"id": 2, "method": "stats", "params": {"data": [1, 2, 3, 4, 5]}}
```

---

## Configuration

### .mcp.json Setup

After installation, verify `.mcp.json` has correct paths:

**Windows:** Use double backslashes (`\\\\`) in JSON

**Example Configuration:**
```json
{
  "mcpServers": {
    "sequential-thinking": {
      "type": "stdio",
      "command": "node",
      "args": [
        "C:\\\\Program Files\\\\nodejs\\\\node_modules\\\\@modelcontextprotocol\\\\server-sequential-thinking\\\\dist\\\\index.js"
      ],
      "env": {},
      "description": "Methodical problem-solving and debugging workflows"
    },
    "pandas-mcp": {
      "type": "stdio",
      "command": "python",
      "args": ["D:\\\\Projects\\\\main\\\\.project\\\\mcp\\\\servers\\\\pandas-mcp\\\\server.py"],
      "env": {},
      "description": "Pandas data analysis and visualization for PSO results"
    }
  }
}
```

### Verify npm Global Location

```bash
npm root -g
```

**Expected Output (Windows):**
```
C:\Program Files\nodejs\node_modules
```

If different, update all Node.js server paths in `.mcp.json` to match.

### Environment Variables

**Required for GitHub server:**
```bash
# Windows (PowerShell)
[System.Environment]::SetEnvironmentVariable('GITHUB_TOKEN', 'your-token-here', 'User')

# Linux/Mac
echo 'export GITHUB_TOKEN=your-token-here' >> ~/.bashrc
source ~/.bashrc
```

---

## Verification

### Run Health Check

```bash
python .project/dev_tools/check_mcp_health.py
```

### Expected Output

```
[INFO] Checking 13 MCP servers...

[OK] filesystem              - Operational
[OK] github                  - Operational
[OK] sequential-thinking     - Operational (stdio)
[OK] puppeteer               - Operational
[OK] mcp-debugger            - Operational
[OK] pytest-mcp              - Operational
[OK] git-mcp                 - Operational
[OK] sqlite-mcp              - Operational
[OK] mcp-analyzer            - Operational (module)
[OK] context7                - Operational (npx)
[OK] lighthouse-mcp          - Operational (standalone)
[OK] pandas-mcp              - Operational (file)
[OK] numpy-mcp               - Operational (file)

============================================================
SUMMARY
============================================================
Total servers: 13
Operational: 13
Failed: 0

[OK] All MCP servers are operational!
```

### Manual Verification

**Test Node.js server:**
```bash
node "C:\Program Files\nodejs\node_modules\@modelcontextprotocol\server-sequential-thinking\dist\index.js" --help
```

**Test Python module:**
```bash
python -m mcp_server_analyzer --help
```

**Test custom Python server:**
```bash
python D:\Projects\main\.project\mcp\servers\pandas-mcp\server.py
```

**Test npx server:**
```bash
npx -y @context7/mcp --version
```

**Test standalone executable:**
```bash
lighthouse-mcp --version
```

---

## Troubleshooting

### Common Installation Issues

#### Issue: npm Permission Errors

**Error:** `EACCES: permission denied`

**Fix (Windows):** Run PowerShell as Administrator
```bash
npm install -g <package-name>
```

**Fix (Linux/Mac):** Use nvm or fix npm permissions (see Troubleshooting Guide)

#### Issue: Python Module Not Found

**Error:** `ModuleNotFoundError: No module named 'pandas'`

**Fix:**
```bash
pip install pandas numpy
```

#### Issue: Executable Not in PATH

**Error:** `lighthouse-mcp: command not found`

**Fix (Windows):**
Add to PATH manually or use full path in `.mcp.json`

**Fix (Linux/Mac):**
```bash
echo 'export PATH="$(npm root -g)/.bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Issue: Chromium Download Failure (Puppeteer)

**Error:** `Failed to download Chromium`

**Fix:**
```bash
# Set environment variable for manual Chromium download
export PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

# Or retry with better network connection
npm install -g @modelcontextprotocol/server-puppeteer
```

### Verification After Fixes

After applying any fixes, always run the health check:

```bash
python .project/dev_tools/check_mcp_health.py
```

---

## Updating MCP Servers

### Update All npm Servers

```bash
npm update -g @modelcontextprotocol/server-filesystem
npm update -g @modelcontextprotocol/server-github
npm update -g @modelcontextprotocol/server-sequential-thinking
npm update -g @modelcontextprotocol/server-puppeteer
npm update -g @cyanheads/git-mcp-server
npm update -g pytest-mcp-server
npm update -g mcp-sqlite
npm update -g mcp-debugger
npm update -g lighthouse-mcp
```

### Update Python Servers

```bash
pip install --upgrade mcp-server-analyzer
pip install --upgrade pandas numpy
```

### Verify After Updates

```bash
python .project/dev_tools/check_mcp_health.py
```

---

## Uninstalling MCP Servers

### Uninstall All npm Servers

```bash
npm uninstall -g @modelcontextprotocol/server-filesystem
npm uninstall -g @modelcontextprotocol/server-github
npm uninstall -g @modelcontextprotocol/server-sequential-thinking
npm uninstall -g @modelcontextprotocol/server-puppeteer
npm uninstall -g @cyanheads/git-mcp-server
npm uninstall -g pytest-mcp-server
npm uninstall -g mcp-sqlite
npm uninstall -g mcp-debugger
npm uninstall -g lighthouse-mcp
```

### Uninstall Python Servers

```bash
pip uninstall mcp-server-analyzer
```

### Clear Caches

```bash
npm cache clean --force
pip cache purge
npx clear-npx-cache
```

---

## Additional Resources

### Documentation

- **MCP Official Docs:** https://modelcontextprotocol.io/
- **Troubleshooting Guide:** `docs/mcp-debugging/TROUBLESHOOTING.md`
- **Quick Reference:** `docs/mcp-debugging/QUICK_REFERENCE.md`
- **MCP Debugging README:** `docs/mcp-debugging/README.md`
- **CLAUDE.md Section 20:** `CLAUDE.md#20-model-context-protocol-mcp-auto-triggers`

### Command Reference

**List installed npm packages:**
```bash
npm list -g --depth=0
```

**List installed Python packages:**
```bash
pip list
```

**Check npm global location:**
```bash
npm root -g
```

**View .mcp.json:**
```bash
cat .mcp.json | python -m json.tool
```

**Run health check:**
```bash
python .project/dev_tools/check_mcp_health.py
```

---

**Last Updated:** November 9, 2025

**See Also:**
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Quick Reference](QUICK_REFERENCE.md)
- [MCP Debugging README](README.md)
- [CLAUDE.md](../../CLAUDE.md)
