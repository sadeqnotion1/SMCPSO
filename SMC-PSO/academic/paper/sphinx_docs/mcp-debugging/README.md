# MCP Debugging Workflows for DIP-SMC-PSO

Model Context Protocol (MCP) integration for systematic debugging of control systems, PSO optimization, and simulation workflows.



## 📦 Available MCP Servers

### Active Servers (configured in `.mcp.json`)

1. **Filesystem Server**
   - Code and log file analysis
   - Documentation validation
   - Test result inspection

2. **GitHub Server**
   - Issue tracking integration
   - PR review automation
   - Commit history analysis

3. **Sequential Thinking**
   - Methodical problem-solving
   - Multi-step debugging workflows
   - Systematic root cause analysis

4. **Puppeteer Server** (optional)
   - Streamlit dashboard testing
   - UI validation
   - Screenshot capture



## 🔧 Quick Start

### 1. Verify MCP Installation

```bash
npm list -g | grep mcp
# Should show:
# @modelcontextprotocol/server-filesystem
# @modelcontextprotocol/server-github
# @modelcontextprotocol/server-sequential-thinking
# @modelcontextprotocol/server-puppeteer
```

## 2. Test MCP Inspector

```bash
/inspect-server
# Launches MCP Inspector UI at localhost:6274
```

## 3. Run Debugging Command

```bash
/debug-with-mcp
# Starts integrated debugging workflow
```



## 📁 Directory Structure

```
docs/mcp-debugging/
├── README.md (this file)
├── workflows/              # Debugging workflow documentation
│   ├── pso-optimization-debugging.md
│   ├── controller-test-debugging.md
│   ├── simulation-failure-analysis.md
│   └── log-analysis-workflow.md
├── server-configs/         # MCP server setup guides
│   ├── filesystem-server-setup.md
│   ├── github-server-setup.md
│   └── sequential-thinking-usage.md
└── inspector-guide/        # MCP Inspector usage
    └── mcp-inspector-quickstart.md
```



## 🎯 Common Use Cases

### Debug PSO Convergence Issues

```bash
/analyze-pso-logs pso_lyapunov_run.log
```

### Validate Simulation Results

```bash
/validate-simulation results/sim_classical_smc.json classical_smc
```

### Run Controller Tests

```bash
/test-controller classical_smc --coverage
```

### Optimize Controller Gains

```bash
/optimize-controller adaptive_smc --swarm_size 50
```



## 📊 Slash Commands

| Command | Purpose | MCP Servers Used |
|---------|---------|------------------|
| `/analyze-logs` | Analyze pytest/PSO logs | Filesystem |
| `/analyze-pso-logs` | PSO convergence analysis | Filesystem, Sequential Thinking |
| `/debug-with-mcp` | Integrated debugging session | All servers |
| `/inspect-server` | Launch MCP Inspector | N/A (launches inspector) |
| `/test-browser` | Test Streamlit dashboard | Puppeteer |
| `/test-controller` | Run controller test suite | Filesystem, Sequential Thinking |
| `/validate-simulation` | Validate simulation results | Filesystem, Sequential Thinking |
| `/optimize-controller` | PSO optimization workflow | Filesystem, Sequential Thinking, GitHub |



## 🔗 Configuration

**MCP Configuration File**: `.mcp.json` (project root)

**GitHub Token Setup** (for GitHub server):
```bash
# Windows
setx GITHUB_TOKEN "your_personal_access_token"

# Linux/Mac
export GITHUB_TOKEN="your_personal_access_token"
```



## 📚 Further Reading

**MCP Server Configuration:**
- Filesystem Server: See `.mcp.json` configuration in project root
- GitHub Server: Configured via MCP server settings
- MCP Inspector: Run `/inspect-server` slash command for interactive debugging



**Created**: 2025-10-06
**Purpose**: MCP-powered debugging for DIP-SMC-PSO project
**Status**: Active - all servers configured
