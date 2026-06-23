# MCP Troubleshooting Guide

**Last Updated:** November 9, 2025

This guide documents common MCP (Model Context Protocol) issues and their solutions, based on real debugging sessions in the DIP-SMC-PSO project.

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation Issues](#installation-issues)
3. [Configuration Problems](#configuration-problems)
4. [Server-Specific Issues](#server-specific-issues)
5. [Path and Environment Issues](#path-and-environment-issues)
6. [Health Check Usage](#health-check-usage)
7. [Common Error Messages](#common-error-messages)

---

## Quick Diagnostics

### Step 1: Run Health Check

```bash
python .project/dev_tools/check_mcp_health.py
```

This will verify all 13 configured MCP servers and report their status.

### Step 2: Verify npm Global Location

```bash
npm root -g
```

Expected output on Windows: `C:\Program Files\nodejs\node_modules`

If different, update all Node.js server paths in `.mcp.json`.

### Step 3: Check Individual Server

**Node.js servers:**
```bash
node "C:\Program Files\nodejs\node_modules\@modelcontextprotocol\server-sequential-thinking\dist\index.js" --help
```

**Python servers:**
```bash
python -m mcp_server_analyzer --help
python D:\Projects\main\.project\mcp\servers\pandas-mcp\server.py
```

**npx-based servers:**
```bash
npx -y @context7/mcp --version
```

---

## Installation Issues

### Issue 1: "Cannot find module" for MCP Servers

**Symptoms:**
- Error message: `Cannot find module '@modelcontextprotocol/server-sequential-thinking'`
- Server fails to start in Claude Code

**Root Cause:**
- MCP servers not actually installed despite being configured in `.mcp.json`

**Fix:**

```bash
# Install official MCP servers
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-puppeteer

# Install community MCP servers
npm install -g @cyanheads/git-mcp-server
npm install -g pytest-mcp-server
npm install -g mcp-sqlite
npm install -g mcp-debugger
npm install -g lighthouse-mcp

# Install Python MCP servers
pip install mcp-server-analyzer
```

**Verification:**
```bash
ls "C:\Program Files\nodejs\node_modules" | grep mcp
python -m mcp_server_analyzer --help
```

### Issue 2: npm Permission Errors

**Symptoms:**
- `EACCES: permission denied` during npm install
- Installation fails with permission errors

**Fix (Windows):**

Run PowerShell/Command Prompt as Administrator:
```bash
npm install -g <package-name>
```

**Fix (Linux/Mac):**

Option A (Recommended): Use nvm to avoid permission issues
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install node
```

Option B: Fix npm permissions
```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Issue 3: Python Module Not Found

**Symptoms:**
- `ModuleNotFoundError: No module named 'mcp_server_analyzer'`
- Python MCP server fails to start

**Fix:**

```bash
# Verify pip installation
pip list | grep mcp

# Reinstall if missing
pip install mcp-server-analyzer

# For custom servers, verify file exists
stat D:\Projects\main\.project\mcp\servers\pandas-mcp\server.py
```

---

## Configuration Problems

### Issue 4: Incorrect npm Global Paths

**Symptoms:**
- Servers configured in `.mcp.json` but don't work
- Error: `ENOENT: no such file or directory`

**Root Cause:**
- `.mcp.json` points to wrong npm global directory
- Common wrong path: `C:\Users\<username>\AppData\Roaming\npm\node_modules\`
- Correct path: `C:\Program Files\nodejs\node_modules\`

**Fix:**

1. Find correct npm global location:
```bash
npm root -g
```

2. Update ALL Node.js server paths in `.mcp.json`:

**Before (WRONG):**
```json
{
  "sequential-thinking": {
    "command": "node",
    "args": [
      "C:\\Users\\sadeg\\AppData\\Roaming\\npm\\node_modules\\@modelcontextprotocol\\server-sequential-thinking\\dist\\index.js"
    ]
  }
}
```

**After (CORRECT):**
```json
{
  "sequential-thinking": {
    "command": "node",
    "args": [
      "C:\\\\Program Files\\\\nodejs\\\\node_modules\\\\@modelcontextprotocol\\\\server-sequential-thinking\\\\dist\\\\index.js"
    ]
  }
}
```

**Note:** Use double backslashes (`\\\\`) in JSON for Windows paths.

### Issue 5: Missing Custom Server Files

**Symptoms:**
- Configuration references local Python server files
- Error: `FileNotFoundError` when server starts

**Root Cause:**
- `.mcp.json` points to server files that don't exist
- Example: `D:\Projects\main\.ai\mcp\servers\pandas-mcp\server.py` (old path)

**Fix:**

Option A: Remove entries from `.mcp.json` if not needed

Option B: Create custom servers (see Installation Guide)

**Verification:**
```bash
stat D:\Projects\main\.project\mcp\servers\pandas-mcp\server.py
stat D:\Projects\main\.project\mcp\servers\numpy-mcp\server.py
```

### Issue 6: Environment Variable Errors

**Symptoms:**
- Server starts but fails to authenticate
- Example: GitHub MCP server can't access GitHub API

**Root Cause:**
- Missing or incorrect environment variables in `.mcp.json`

**Fix:**

1. Ensure environment variables are set in `.mcp.json`:
```json
{
  "github": {
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
    }
  }
}
```

2. Set environment variable in system:

**Windows:**
```powershell
[System.Environment]::SetEnvironmentVariable('GITHUB_TOKEN', 'your-token-here', 'User')
```

**Linux/Mac:**
```bash
echo 'export GITHUB_TOKEN=your-token-here' >> ~/.bashrc
source ~/.bashrc
```

---

## Server-Specific Issues

### Node.js MCP Servers

**Common Issues:**
- Wrong Node.js version (requires Node.js 18+)
- Missing TypeScript dependencies
- Incorrect dist/ path in configuration

**Verification:**
```bash
node --version  # Should be 18.x or higher
npm list -g @modelcontextprotocol/server-sequential-thinking
```

### Python MCP Servers

**Common Issues:**
- Wrong Python version (requires Python 3.9+)
- Missing dependencies (pandas, numpy)
- Incorrect module path

**Verification:**
```bash
python --version  # Should be 3.9 or higher
pip list | grep -E "pandas|numpy|mcp"
```

### npx-based Servers (context7)

**Common Issues:**
- npx not in PATH
- Package download timeout
- Network/firewall blocking npm registry

**Verification:**
```bash
npx --version
npx -y @context7/mcp --version
```

**Fix:**
```bash
# Clear npx cache
npx clear-npx-cache

# Reinstall
npm install -g @context7/mcp
```

### Standalone Executables (lighthouse-mcp)

**Common Issues:**
- Executable not in PATH
- Wrong installation method

**Verification:**
```bash
lighthouse-mcp --version
```

**Fix:**
```bash
npm install -g lighthouse-mcp
# Verify added to PATH
where lighthouse-mcp  # Windows
which lighthouse-mcp  # Linux/Mac
```

---

## Path and Environment Issues

### Windows Path Issues

**Issue:** Spaces in paths cause errors

**Wrong:**
```bash
node C:\Program Files\nodejs\node_modules\...
```

**Correct:**
```bash
node "C:\Program Files\nodejs\node_modules\..."
```

**In .mcp.json:** Use double backslashes
```json
"args": ["C:\\\\Program Files\\\\nodejs\\\\node_modules\\\\..."]
```

### Unicode/Encoding Issues

**Issue:** Terminal displays garbled text or crashes

**Root Cause:** Windows terminal uses cp1252 encoding, can't display Unicode emojis

**Fix:**
- Health check script uses ASCII markers: `[OK]`, `[ERROR]`, `[INFO]`
- Avoid Unicode emojis in server output
- Use `chcp 65001` to switch to UTF-8 if needed

---

## Health Check Usage

### Running Health Check

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

### Interpreting Failures

**Example failure output:**
```
[ERROR] sequential-thinking     - File not found: C:\...\dist\index.js
[ERROR] pandas-mcp              - Module not found: pandas
```

**Actions:**
1. Check error message for specific issue
2. Follow relevant fix in this guide
3. Re-run health check to verify fix

---

## Common Error Messages

### Error: "Cannot find module"

**Meaning:** npm package not installed or wrong path

**Fix:** Install package or correct path in `.mcp.json`

### Error: "ENOENT: no such file or directory"

**Meaning:** File path in `.mcp.json` is incorrect

**Fix:** Verify path with `stat` command and update `.mcp.json`

### Error: "TimeoutExpired"

**Meaning:** Server is waiting for stdio input (this is OK!)

**Health Check Behavior:** Treats timeout as operational status

### Error: "ModuleNotFoundError"

**Meaning:** Python module not installed

**Fix:** `pip install <module-name>`

### Error: "spawn EACCES"

**Meaning:** File doesn't have execute permissions (Linux/Mac)

**Fix:**
```bash
chmod +x /path/to/server/file
```

### Error: "Command not found"

**Meaning:** Executable not in PATH

**Fix:** Add to PATH or use full path in `.mcp.json`

---

## Advanced Troubleshooting

### Debugging Individual Servers

**Test Node.js server:**
```bash
node "C:\Program Files\nodejs\node_modules\@modelcontextprotocol\server-sequential-thinking\dist\index.js"
# Should output: "Sequential Thinking MCP Server running on stdio"
```

**Test Python module:**
```bash
python -m mcp_server_analyzer
# Should start and wait for stdin
```

**Test custom Python server:**
```bash
python D:\Projects\main\.project\mcp\servers\pandas-mcp\server.py
# Should output: "[INFO] Pandas MCP Server started on stdio"
```

### Logging and Debugging

**Enable verbose output:**
```bash
python .project/dev_tools/check_mcp_health.py -v
```

**Check npm installation logs:**
```bash
npm install -g <package> --verbose
```

**Check Python installation logs:**
```bash
pip install <package> --verbose
```

### Complete Reset

If all else fails, perform a complete reset:

```bash
# 1. Remove all MCP servers
npm uninstall -g @modelcontextprotocol/server-filesystem
npm uninstall -g @modelcontextprotocol/server-github
npm uninstall -g @modelcontextprotocol/server-sequential-thinking
npm uninstall -g @modelcontextprotocol/server-puppeteer
npm uninstall -g @cyanheads/git-mcp-server
npm uninstall -g pytest-mcp-server
npm uninstall -g mcp-sqlite
npm uninstall -g mcp-debugger
npm uninstall -g lighthouse-mcp
pip uninstall mcp-server-analyzer

# 2. Clear caches
npm cache clean --force
pip cache purge

# 3. Reinstall (see Installation Guide)

# 4. Verify with health check
python .project/dev_tools/check_mcp_health.py
```

---

## Getting Help

### Resources

1. **MCP Documentation:** https://modelcontextprotocol.io/
2. **Project Documentation:** `docs/mcp-debugging/README.md`
3. **Installation Guide:** `docs/mcp-debugging/INSTALLATION.md`
4. **Quick Reference:** `docs/mcp-debugging/QUICK_REFERENCE.md`

### Reporting Issues

When reporting MCP issues, include:

1. Health check output:
```bash
python .project/dev_tools/check_mcp_health.py > mcp_health.txt 2>&1
```

2. npm global location:
```bash
npm root -g
```

3. Node.js and Python versions:
```bash
node --version
python --version
```

4. Relevant section of `.mcp.json`

5. Full error message with stack trace

---

## Appendix: Reference Commands

### Verification Commands

```bash
# Check npm packages
npm list -g --depth=0 | grep mcp

# Check Python packages
pip list | grep mcp

# Check file existence
stat "C:\Program Files\nodejs\node_modules\@modelcontextprotocol\server-sequential-thinking\dist\index.js"
stat D:\Projects\main\.project\mcp\servers\pandas-mcp\server.py

# Test individual servers
node "<npm-global-path>\@modelcontextprotocol\server-filesystem\dist\index.js" --help
python -m mcp_server_analyzer --help
python D:\Projects\main\.project\mcp\servers\pandas-mcp\server.py
```

### Maintenance Commands

```bash
# Update all npm MCP servers
npm update -g @modelcontextprotocol/server-filesystem
npm update -g @modelcontextprotocol/server-github
npm update -g @modelcontextprotocol/server-sequential-thinking
npm update -g @modelcontextprotocol/server-puppeteer
npm update -g @cyanheads/git-mcp-server
npm update -g pytest-mcp-server
npm update -g mcp-sqlite
npm update -g mcp-debugger
npm update -g lighthouse-mcp

# Update Python MCP servers
pip install --upgrade mcp-server-analyzer

# Run health check
python .project/dev_tools/check_mcp_health.py

# View MCP configuration
cat .mcp.json | python -m json.tool
```

---

**Last Updated:** November 9, 2025

**See Also:**
- [Installation Guide](INSTALLATION.md)
- [Quick Reference](QUICK_REFERENCE.md)
- [MCP Debugging README](README.md)
- [CLAUDE.md Section 20](../../CLAUDE.md#20-model-context-protocol-mcp-auto-triggers)
