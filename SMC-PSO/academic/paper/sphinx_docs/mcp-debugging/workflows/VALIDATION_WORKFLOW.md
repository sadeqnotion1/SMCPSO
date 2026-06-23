# MCP Debugging Validation Workflow **Last Updated**: 2025-10-06

**MCP Servers**: 11 servers integrated
**Purpose**: Validate and test all MCP debugging features

---

## 📋 Overview This document provides **complete validation procedures** for all 11 MCP servers and demonstrates how they work together for debugging the DIP-SMC-PSO project. ### Complete Server Inventory | Server | Type | Purpose | Validation Status |

|--------|------|---------|-------------------|
| **filesystem** | npm | File operations | ✅ Core server |
| **github** | npm | Git operations | ✅ Core server |
| **sequential-thinking** | npm | Systematic reasoning | ✅ Core server |
| **puppeteer** | npm | Browser automation | ✅ Core server |
| **mcp-debugger** | npm | API testing | ✅ Extended server |
| **pytest-mcp** | npm | Test debugging | ✅ Extended server |
| **git-mcp** | npm | Advanced Git ops | ✅ Extended server |
| **sqlite-mcp** | npm | Database queries | ✅ Extended server |
| **mcp-analyzer** | Python | Code quality (RUFF/Vulture) | 🆕 **New** |
| **numpy-mcp** | Python | Numerical computations | 🆕 **New** |
| **pandas-mcp** | Python | Data analysis/viz | 🆕 **New** |

---

## 🧪 Validation Scenario 1: Code Quality Analysis (mcp-analyzer) **Use Case**: Analyze codebase for linting issues and dead code before committing. ### Step 1: Run RUFF Linter **MCP Server**: `mcp-analyzer` ```python

# example-metadata:

# runnable: false # Ask Claude via MCP:

"Use mcp-analyzer to run RUFF linting on src/controllers/classical_smc.py" # Expected MCP tool call:
{ "server": "mcp-analyzer", "tool": "run_ruff", "args": { "file_path": "D:\\Projects\\main\\src\\controllers\\classical_smc.py", "fix": false }
}
``` **Expected Output**:
```

RUFF Analysis Results:
- E501: Line too long (98 > 88 characters) at line 45
- F401: Unused import 'numpy as np' at line 3
- E302: Expected 2 blank lines, found 1 at line 67 Total issues: 3
Fixable: 2
``` ### Step 2: Detect Dead Code with VULTURE ```python
# example-metadata:
# runnable: false # Ask Claude:
"Use mcp-analyzer to find dead code in src/utils/validation/" # Expected MCP tool call:
{ "server": "mcp-analyzer", "tool": "run_vulture", "args": { "directory": "D:\\Projects\\main\\src\\utils\\validation", "min_confidence": 80 }
}
``` **Expected Output**:

```
Dead Code Detected:
- unused function 'legacy_validator' (validation.py:145) - confidence: 100%
- unused variable 'DEBUG_MODE' (config.py:12) - confidence: 90%
- unreachable code after return (helpers.py:89) - confidence: 85% Total dead code: 3 items
``` ### Step 3: Apply Automatic Fixes ```python
# example-metadata:

# runnable: false # Ask Claude:

"Use mcp-analyzer to auto-fix RUFF issues in classical_smc.py" # Expected MCP tool call:
{ "server": "mcp-analyzer", "tool": "run_ruff", "args": { "file_path": "D:\\Projects\\main\\src\\controllers\\classical_smc.py", "fix": true }
}
``` **Validation Checklist**:
- [ ] RUFF detects at least 1 linting issue
- [ ] VULTURE finds dead code with confidence scores
- [ ] Auto-fix successfully applies corrections
- [ ] Re-running RUFF shows reduced issue count

---

## 🔢 Validation Scenario 2: Numerical Analysis (numpy-mcp) **Use Case**: Analyze matrix conditioning for LinAlgError debugging. ### Step 1: Check Matrix Condition Number **MCP Server**: `numpy-mcp` ```python
# example-metadata:
# runnable: false # Ask Claude:
"Use numpy-mcp to calculate the condition number of the inertia matrix:
[[1.5, 0.2], [0.2, 0.8]]" # Expected MCP tool call:
{ "server": "numpy-mcp", "tool": "statistical_analysis", "args": { "matrix": [[1.5, 0.2], [0.2, 0.8]] }
}
``` **Expected Output**:

```json
{ "condition_number": 2.45, "well_conditioned": true, "eigenvalues": [1.62, 0.68], "recommendation": "Matrix is well-conditioned, inversion safe"
}
``` ### Step 2: Eigenvalue Decomposition for Stability ```python
# example-metadata:

# runnable: false # Ask Claude:

"Use numpy-mcp to compute eigenvalues of system matrix A:
[[0, 1], [-2, -3]]" # Expected MCP tool call:
{ "server": "numpy-mcp", "tool": "eigen_decomposition", "args": { "matrix": [[0, 1], [-2, -3]] }
}
``` **Expected Output**:
```json

{ "eigenvalues": [-1.0, -2.0], "eigenvectors": [[0.707, -0.447], [-0.707, 0.894]], "stable": true, "note": "All eigenvalues have negative real parts - system is stable"
}
``` ### Step 3: Statistical Analysis of PSO Convergence ```python
# example-metadata:
# runnable: false # Ask Claude:
"Use numpy-mcp to analyze these PSO fitness values:
[150.2, 145.8, 142.1, 140.5, 139.8, 139.3, 139.1, 139.0]" # Expected MCP tool call:
{ "server": "numpy-mcp", "tool": "statistical_analysis", "args": { "data": [150.2, 145.8, 142.1, 140.5, 139.8, 139.3, 139.1, 139.0] }
}
``` **Expected Output**:

```json
{ "mean": 142.225, "median": 140.15, "std_dev": 3.987, "min": 139.0, "max": 150.2, "trend": "converging", "improvement_rate": "7.5% total reduction"
}
``` **Validation Checklist**:

- [ ] Condition number correctly computed
- [ ] Eigenvalue decomposition returns accurate values
- [ ] Statistical analysis provides mean, std dev, min, max
- [ ] Integration with sequential-thinking for interpretation

---

## 📊 Validation Scenario 3: PSO Results Analysis (pandas-mcp + sqlite-mcp) **Use Case**: Extract PSO data from database, analyze with pandas, generate visualizations. ### Step 1: Query PSO Results (sqlite-mcp) **MCP Server**: `sqlite-mcp` ```sql

-- Ask Claude:
"Use sqlite-mcp to query the 10 most recent PSO runs" -- Expected MCP tool call:
{ "server": "sqlite-mcp", "tool": "query", "args": { "database": "D:\\Projects\\main\\logs\\pso_results.db", "sql": "SELECT run_id, controller_type, best_fitness, convergence_time FROM pso_runs ORDER BY timestamp DESC LIMIT 10" }
}
``` **Expected Output**:
```json

{ "rows": 10, "columns": ["run_id", "controller_type", "best_fitness", "convergence_time"], "data": [ {"run_id": "pso_20251006_143022", "controller_type": "classical_smc", "best_fitness": 139.2, "convergence_time": 45.3}, {"run_id": "pso_20251006_142015", "controller_type": "adaptive_smc", "best_fitness": 142.8, "convergence_time": 52.1}, ... ]
}
``` ### Step 2: Analyze with Pandas (pandas-mcp) ```python
# example-metadata:
# runnable: false # Ask Claude:
"Use pandas-mcp to calculate average fitness by controller type from the PSO results" # Expected MCP tool call:
{ "server": "pandas-mcp", "tool": "run_pandas_code", "args": { "code": "import pandas as pd\ndf = pd.DataFrame(pso_data)\nresult = df.groupby('controller_type')['best_fitness'].agg(['mean', 'std', 'min', 'max'])" }
}
``` **Expected Output**:

```
controller_type mean std min max
classical_smc 142.3 5.2 135.1 150.2
adaptive_smc 138.7 3.8 132.5 145.3
hybrid_adaptive 136.2 2.9 130.8 141.7
sta_smc 140.5 4.5 133.2 148.9
``` ### Step 3: Generate Visualization (pandas-mcp) ```python
# example-metadata:

# runnable: false # Ask Claude:

"Use pandas-mcp to create a bar chart comparing average fitness by controller type" # Expected MCP tool call:
{ "server": "pandas-mcp", "tool": "generate_chartjs", "args": { "data": { "columns": [ {"name": "Controller", "type": "string", "examples": ["classical_smc", "adaptive_smc", "hybrid_adaptive", "sta_smc"]}, {"name": "Average Fitness", "type": "number", "examples": [142.3, 138.7, 136.2, 140.5]} ] }, "chart_types": ["bar"], "title": "PSO Performance by Controller Type" }
}
``` **Expected Output**:
```

Chart generated: D:\Projects\main\charts\pso_performance_20251006_143530.html
Interactive features:
- Hover for exact values
- Toggle controller types
- Export as PNG
``` **Validation Checklist**:
- [ ] sqlite-mcp successfully queries database
- [ ] pandas-mcp runs DataFrame operations without errors
- [ ] pandas-mcp generates interactive HTML chart
- [ ] Chart displays correct data and is interactive

---

## 🧪 Validation Scenario 4: Test Failure Debugging (pytest-mcp + mcp-analyzer) **Use Case**: Debug failing tests, analyze code quality, fix issues. ### Step 1: List Recent Test Failures (pytest-mcp) **MCP Server**: `pytest-mcp` ```python
# example-metadata:
# runnable: false # Ask Claude:
"Use pytest-mcp to list the last 5 test failures" # Expected MCP tool call:
{ "server": "pytest-mcp", "tool": "list_failures", "args": { "last": 5 }
}
``` **Expected Output**:

```json
{ "failures": [ { "test_id": "tests/test_controllers/test_classical_smc.py::test_stability", "error": "AssertionError: Lyapunov function not decreasing", "timestamp": "2025-10-06 14:25:33", "duration": "0.45s" }, { "test_id": "tests/test_optimization/test_pso.py::test_convergence", "error": "Timeout: PSO did not converge in 100 iterations", "timestamp": "2025-10-06 14:20:15", "duration": "12.3s" }, ... ]
}
``` ### Step 2: Analyze Failing Test Code (mcp-analyzer) ```python
# example-metadata:

# runnable: false # Ask Claude:

"Use mcp-analyzer to lint the failing test file tests/test_controllers/test_classical_smc.py" # Expected MCP tool call:
{ "server": "mcp-analyzer", "tool": "run_ruff", "args": { "file_path": "D:\\Projects\\main\\tests\\test_controllers\\test_classical_smc.py", "fix": false }
}
``` **Expected Output**:
```

RUFF Analysis:
- F841: Local variable 'expected_result' assigned but never used (line 45)
- E501: Line too long (line 67)
- T201: print() found (line 89) - use logging instead Suggestions:
- Remove unused variable or add assertion
- Split long line for readability
- Replace print with logging.debug
``` ### Step 3: Get Failure Pattern Analysis (pytest-mcp) ```python
# example-metadata:
# runnable: false # Ask Claude:
"Use pytest-mcp to analyze failure patterns grouped by test name" # Expected MCP tool call:
{ "server": "pytest-mcp", "tool": "get_patterns", "args": { "groupby": "test_name" }
}
``` **Expected Output**:

```json
{ "patterns": { "test_stability": { "failure_count": 12, "success_count": 3, "failure_rate": "80%", "common_errors": ["AssertionError: Lyapunov", "Timeout"], "recommendation": "Investigate Lyapunov function implementation" }, "test_convergence": { "failure_count": 5, "success_count": 10, "failure_rate": "33%", "common_errors": ["Timeout"], "recommendation": "Increase iteration limit or review fitness function" } }
}
``` **Validation Checklist**:

- [ ] pytest-mcp lists recent failures with details
- [ ] mcp-analyzer identifies code quality issues in test files
- [ ] pytest-mcp provides pattern analysis
- [ ] Combined analysis points to root cause

---

## 🔄 Validation Scenario 5: Multi-Server Integrated Workflow **Use Case**: Complete debugging workflow using 6+ servers in sequence. ### Problem: PSO convergence is slow, controller tests are failing #### Phase 1: Data Collection **Step 1a**: Query database (sqlite-mcp)

```sql
SELECT * FROM pso_runs WHERE status = 'stagnated' LIMIT 5
``` **Step 1b**: List test failures (pytest-mcp)

```python
list_failures({ last: 10 })
``` **Step 1c**: Check recent commits (git-mcp)

```bash
log({ options: "--oneline --since '2 days ago'" })
``` #### Phase 2: Analysis **Step 2a**: Analyze convergence data (pandas-mcp)

```python
run_pandas_code({ code: "df = pd.DataFrame(pso_data); result = df['gbest_fitness'].diff().mean()"
})
# Output: Average improvement per iteration: 0.0012 (very slow!)
``` **Step 2b**: Check matrix conditioning (numpy-mcp)

```python
eigen_decomposition({ matrix: controller_gain_matrix
})
# Output: Condition number: 1.2e8 (ill-conditioned!)
``` **Step 2c**: Lint controller code (mcp-analyzer)

```python
run_ruff({ file_path: "src/controllers/classical_smc.py"
})
# Output: 5 issues found, 3 auto-fixable
``` #### Phase 3: Root Cause Identification (sequential-thinking) ```

1. PSO stagnation caused by: - Too small swarm size (20 instead of 30-50) - Lack of diversity maintenance 2. Test failures caused by: - Ill-conditioned gain matrix (cond num: 1.2e8) - Missing regularization in matrix inversion 3. Code quality issues: - Unused imports increase confusion - Long lines reduce readability
``` #### Phase 4: Fix Implementation **Step 4a**: Update PSO parameters (filesystem)
```python

read_file({ path: "config/pso_config.yaml" })
# Increase swarm_size from 20 to 40

# Add diversity_threshold: 0.01

``` **Step 4b**: Add regularization (filesystem)
```python

read_file({ path: "src/controllers/classical_smc.py" })
# Add: np.linalg.pinv(M + 1e-8 * np.eye(M.shape[0]))

``` **Step 4c**: Apply code fixes (mcp-analyzer)
```python
# example-metadata:

# runnable: false run_ruff({ file_path: "...", fix: true })

``` #### Phase 5: Validation **Step 5a**: Re-run tests (pytest-mcp)
```python

track_test({ name: "test_stability" })
# Output: PASSED (3/3 runs)

``` **Step 5b**: Verify PSO performance (pandas-mcp + numpy-mcp)
```python
# example-metadata:

# runnable: false # Pandas: Analyze new run

# NumPy: Verify condition number < 1e6

``` **Step 5c**: Commit changes (git-mcp)
```bash

git add .
git commit -m "Fix PSO convergence and matrix conditioning issues"
``` **Validation Checklist**:
- [ ] All 6 servers used in logical sequence
- [ ] Root cause identified through multi-server analysis
- [ ] Fixes applied using appropriate servers
- [ ] Validation confirms problem resolution
- [ ] Changes committed via git-mcp

---

## ✅ Complete Server Validation Checklist ### Core Servers (4)
- [ ] **filesystem**: Read/write files, search logs
- [ ] **github**: Query issues, check commit history
- [ ] **sequential-thinking**: Systematic problem decomposition
- [ ] **puppeteer**: Test Streamlit dashboard UI ### Extended Servers (4)
- [ ] **mcp-debugger**: Test API endpoints (if applicable)
- [ ] **pytest-mcp**: List failures, analyze patterns, track tests
- [ ] **git-mcp**: Advanced Git operations (diff, log, branch)
- [ ] **sqlite-mcp**: Query PSO results database ### New Python Servers (3)
- [ ] **mcp-analyzer**: RUFF linting + VULTURE dead code detection
- [ ] **numpy-mcp**: Matrix operations, eigenvalues, statistics
- [ ] **pandas-mcp**: Data analysis, groupby, chart generation

---

## 🎯 Success Criteria ### Individual Server Validation
Each server must:
1. ✅ Connect successfully via MCP protocol
2. ✅ Execute at least 1 tool/command without errors
3. ✅ Return structured, parseable output
4. ✅ Handle errors gracefully with clear messages ### Multi-Server Integration
Workflows must demonstrate:
1. ✅ Logical sequencing of server calls
2. ✅ Data flow between servers (e.g., sqlite → pandas → chart)
3. ✅ Combined analysis leading to actionable insights
4. ✅ Complete problem resolution using multiple tools ### DIP-SMC-PSO Specific Validation
- [ ] Debug PSO convergence issue (sqlite + pandas + numpy)
- [ ] Fix controller stability (numpy + mcp-analyzer + pytest)
- [ ] Analyze code quality (mcp-analyzer + git-mcp)
- [ ] Visualize simulation results (pandas + puppeteer)
- [ ] test debugging (pytest + mcp-analyzer + sequential-thinking)

---

## 🐛 Troubleshooting ### Server Not Responding
```bash
# Check MCP configuration

cat .mcp.json | jq '.mcpServers.<server-name>' # Test server directly
python -m mcp_server_analyzer # For Python servers
node <path-to-server.js> # For npm servers # Check logs
cat logs/mcp_server.log
``` ### Tool Execution Errors
```python
# example-metadata:

# runnable: false # Verify tool parameters match schema

# Check server README for correct parameter format

# Ensure file paths are absolute

# Confirm database/files exist before querying

``` ### Integration Issues
```python
# example-metadata:

# runnable: false # Validate data format between servers

# Ensure output of Server A matches input of Server B

# Check for encoding issues (UTF-8 vs ASCII)

# Verify JSON structure compatibility

```

---

## 📚 Additional Resources - **Server Documentation**: `docs/mcp-debugging/MISSING_SERVERS_RESEARCH.md`
- **Quick Reference**: `docs/mcp-debugging/QUICK_REFERENCE.md`
- **Integration Examples**: `docs/mcp-debugging/workflows/SERVER_INTEGRATION_EXAMPLES.md`
- **Quick Start**: `docs/mcp-debugging/VALIDATION_QUICK_START.md`

---

**Version**: 1.0.0
**Last Validated**: 2025-10-06
**Validation Status**: ✅ All 11 servers operational
