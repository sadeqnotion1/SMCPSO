# Complete MCP Debugging Workflow **Last Updated**: 2025-10-06

**MCP Servers**: 8 servers integrated
**Project**: DIP-SMC-PSO

---

## 📋 Overview This document provides debugging workflows using the integrated MCP (Model Context Protocol) servers for the Double Inverted Pendulum Sliding Mode Control with PSO Optimization project. ### Available MCP Servers | Server | Purpose | Tools |

|--------|---------|-------|
| **filesystem** | File system operations | read, write, search, list |
| **github** | Git operations | commits, branches, issues, PRs |
| **sequential-thinking** | Systematic problem-solving | step-by-step reasoning |
| **puppeteer** | Browser automation | dashboard testing, UI validation |
| **mcp-debugger** | API testing | Postman collections, REST APIs |
| **pytest-mcp** | Test debugging | pytest failures, test tracking |
| **git-mcp** | Advanced Git ops | diff, log, merge, rebase |
| **sqlite-mcp** | Database queries | PSO results, convergence data |

---

## 🔧 Workflow 1: PSO Convergence Debugging **Use Case**: PSO optimization is converging slowly or getting stuck in local minima. ### Phase 1: Data Collection (sqlite-mcp) ```bash

# Query recent PSO runs

SELECT run_id, best_fitness, iterations, convergence_time
FROM pso_runs
ORDER BY timestamp DESC
LIMIT 10; # Check parameter ranges
SELECT parameter_name, min_value, max_value, optimal_value
FROM pso_parameters
WHERE run_id = '<latest_run_id>'; # Analyze convergence pattern
SELECT iteration, gbest_fitness, diversity_metric
FROM pso_iterations
WHERE run_id = '<latest_run_id>'
ORDER BY iteration;
``` ### Phase 2: Log Analysis (filesystem) ```bash
# Read PSO optimization logs
/analyze-pso-logs # Key indicators to check:
# - Swarm diversity collapse (< 0.01 after 10 iterations)
# - Fitness stagnation (no improvement for 20+ iterations)
# - Parameter bound violations
# - Particle velocity saturation
``` ### Phase 3: Code Inspection (sequential-thinking) ```

1. Check PSO hyperparameters: - Swarm size (recommended: 30-50 for 8D problem) - Inertia weight decay (0.9 → 0.4) - Cognitive/social coefficients (c1=2.05, c2=2.05) 2. Verify objective function: - Penalty terms properly scaled? - Constraint handling robust? - Numerical stability checks? 3. Examine initialization: - Latin Hypercube Sampling used? - Parameter bounds appropriate? - Initial diversity sufficient?
``` ### Phase 4: Fix Implementation (filesystem + git-mcp) ```bash
# Create feature branch
git checkout -b fix/pso-convergence-improvement # Apply fixes to src/optimization/pso_optimizer.py
# - Adjust hyperparameters
# - Add diversity maintenance mechanism
# - Implement adaptive velocity clamping # Commit changes
git add src/optimization/pso_optimizer.py
git commit -m "Improve PSO convergence with adaptive parameters"
``` ### Phase 5: Validation (pytest-mcp) ```bash
# Run PSO unit tests

/test-controller # Check specific tests:
# - test_pso_convergence_rate

# - test_pso_diversity_maintenance

# - test_pso_constraint_handling

```

---

## 🧪 Workflow 2: Controller Test Debugging **Use Case**: Controller tests are failing with unexpected behavior. ### Phase 1: Test Failure Analysis (pytest-mcp) ```bash
# View recent test failures
pytest-mcp list-failures --last 5 # Get detailed failure information
pytest-mcp analyze-failure --test-id <failure_id> # Check failure patterns
pytest-mcp patterns --groupby test_name
``` ### Phase 2: Log Examination (filesystem) ```bash
# Read pytest logs

cat tests/logs/pytest.log | grep -A 10 "FAILED" # Check controller simulation logs
cat logs/simulation_<timestamp>.log # Analyze numerical errors
/analyze-logs --filter "LinAlgError|RuntimeWarning"
``` ### Phase 3: Code Debugging (sequential-thinking) ```
1. Identify failure location: - Stack trace analysis - Line number where assertion failed - Input values that triggered failure 2. Hypothesis formation: - Numerical instability? - Incorrect state initialization? - Controller gains out of bounds? 3. Reproduce locally: - Create minimal test case - Add debug prints - Step through with debugpy
``` ### Phase 4: Interactive Debugging (mcp-debugger) ```bash
# Set up debugpy configuration

# Launch test with debugging

python -m debugpy --listen 5678 --wait-for-client -m pytest tests/test_controllers.py::test_smc_stability # Breakpoints to set:
# 1. Controller initialization

# 2. First control input computation

# 3. State update loop

# 4. Assertion location

``` ### Phase 5: Fix and Verify (git-mcp + pytest-mcp) ```bash
# Create fix branch
git checkout -b fix/controller-test-failures # Apply fixes
# Run tests
pytest tests/test_controllers.py -v # Commit if passing
git add tests/test_controllers.py src/controllers/
git commit -m "Fix controller test failures with proper initialization"
```

---

## 🔢 Workflow 3: Numerical Error Analysis **Use Case**: Getting `LinAlgError: Singular matrix` or numerical warnings. ### Phase 1: Error Detection (filesystem) ```bash

# Search for numerical errors in logs

/analyze-logs --pattern "LinAlgError|ill-conditioned|singular matrix" # Check simulation logs
grep -r "RuntimeWarning" logs/ # Find affected files
grep -r "LinAlgError" src/ --include="*.py"
``` ### Phase 2: Matrix Condition Analysis (sequential-thinking) ```
1. Identify problematic matrices: - Inertia matrix M(q) - Jacobian matrices - Control gain matrices 2. Check condition numbers: - Log condition numbers before inversion - Typical range: 1e6-1e12 indicates ill-conditioning 3. Locate source: - Which state values trigger the error? - Parameter combinations that cause singularity?
``` ### Phase 3: Code Inspection (filesystem + git-mcp) ```bash
# View recent changes to dynamics code

git-mcp diff --file src/models/dynamics.py --since "1 week ago" # Check numerical stability utilities
cat src/utils/numerical_stability.py # Review matrix operations
grep -n "np.linalg.inv\|np.linalg.solve" src/models/dynamics.py
``` ### Phase 4: Implement Regularization (filesystem) ```python
# example-metadata:
# runnable: false # Add to src/utils/numerical_stability.py def safe_matrix_inverse(M: np.ndarray, eps: float = 1e-10) -> np.ndarray: """ Compute matrix inverse with regularization for ill-conditioned matrices. Args: M: Input matrix eps: Regularization parameter Returns: Regularized inverse """ cond_num = np.linalg.cond(M) if cond_num > 1e8: # Use SVD-based pseudo-inverse return np.linalg.pinv(M, rcond=eps) else: # Standard inversion with small ridge return np.linalg.inv(M + eps * np.eye(M.shape[0]))
``` ### Phase 5: Validation (pytest-mcp) ```bash
# Run numerical stability tests

pytest tests/test_numerical_stability.py -v # Check edge cases
pytest tests/test_dynamics.py::test_singular_configurations -v # Verify no regressions
pytest tests/ -k "not slow" --tb=short
```

---

## 📊 Workflow 4: Code Quality Improvement **Use Case**: Improving code quality, finding bugs, and ensuring best practices. ### Phase 1: Static Analysis (filesystem) ```bash
# Run ruff linter
ruff check src/ tests/ # Check type hints
mypy src/ --strict # Find unused imports
vulture src/ --min-confidence 80
``` ### Phase 2: Code Review (git-mcp) ```bash
# Review recent commits

git-mcp log --oneline --since "1 week ago" # Check specific file changes
git-mcp show <commit-hash> # Compare branches
git-mcp diff main..feature/new-controller
``` ### Phase 3: Test Coverage (pytest-mcp) ```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html # Find untested code
coverage report --show-missing # Check critical paths
pytest tests/test_controllers.py --cov=src/controllers --cov-report=term-missing
``` ### Phase 4: Documentation Review (filesystem) ```bash
# Check docstring coverage

python -c "import ast; from pathlib import Path; count=0; for f in Path('src').rglob('*.py'): try: tree = ast.parse(f.read_text(encoding='utf-8')); for node in ast.walk(tree): if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)): if ast.get_docstring(node): count += 1 except: pass
print(f'{count} docstrings found in src/')" # Review API documentation
cat docs/api/controllers.md
``` ### Phase 5: Refactoring (git-mcp + pytest-mcp) ```bash
# Create refactor branch
git checkout -b refactor/code-quality-improvements # Apply fixes:
# - Add missing type hints
# - Remove unused imports
# - Update docstrings
# - Improve variable names # Run full test suite
pytest tests/ -v # Commit if all pass
git add .
git commit -m "Code quality improvements: type hints, docs, linting"
```

---

## 🎨 Workflow 5: Simulation Result Analysis **Use Case**: Analyzing and validating simulation results for research publication. ### Phase 1: Data Extraction (sqlite-mcp) ```sql

-- Extract best PSO results
SELECT controller_type, AVG(settling_time) as avg_settling_time, AVG(overshoot) as avg_overshoot, AVG(steady_state_error) as avg_sse, COUNT(*) as num_trials
FROM simulation_results
WHERE status = 'completed'
GROUP BY controller_type
ORDER BY avg_settling_time; -- Get convergence statistics
SELECT run_id, MIN(gbest_fitness) as best_fitness, AVG(convergence_iteration) as avg_conv_iter
FROM pso_runs
WHERE convergence_achieved = 1
GROUP BY controller_type;
``` ### Phase 2: Validation (filesystem + sequential-thinking) ```
1. Check control-theoretic criteria: - Lyapunov stability verified? - Phase margin > 45 degrees? - Gain margin > 6 dB? 2. Verify physical feasibility: - Control inputs within actuator limits? - State trajectories realistic? - Energy consumption reasonable? 3. Statistical validation: - Sample size sufficient (n ≥ 30)? - Confidence intervals calculated? - Significance tests performed?
``` ### Phase 3: Visualization (puppeteer) ```bash
# Launch Streamlit dashboard

streamlit run app.py # Test dashboard with Puppeteer
/test-browser # Verify plots:
# - State trajectories

# - Control inputs

# - PSO convergence curves

# - Performance metrics comparison

``` ### Phase 4: Documentation (filesystem) ```bash
# Generate experiment report
python scripts/generate_experiment_report.py \ --run-id <run_id> \ --output docs/experiments/exp_<date>.md # Update results summary
vim docs/results/README.md # Create figures for paper
python scripts/generate_publication_figures.py --run-id <run_id>
``` ### Phase 5: Commit and Archive (git-mcp) ```bash
# Commit results

git add docs/experiments/ docs/results/ figures/
git commit -m "Add experiment results for <controller_name> on <date>" # Tag milestone
git tag -a v1.0-results -m "Complete simulation results for publication" # Push to remote
git push origin main --tags
```

---

## 🚀 Quick Reference Commands ### Slash Commands | Command | Description |
|---------|-------------|
| `/analyze-logs` | Automated log analysis |
| `/analyze-pso-logs` | PSO convergence analysis |
| `/test-controller` | Run controller test suite |
| `/test-browser` | Test Streamlit dashboard |
| `/validate-simulation` | Validate against control criteria |
| `/optimize-controller` | Launch PSO optimization |
| `/debug-with-mcp` | Integrated debugging session |
| `/inspect-server` | Launch MCP Inspector | ### MCP Server Tools Quick Reference **filesystem**
- `read_file(path)` - Read file contents
- `write_file(path, content)` - Write to file
- `list_directory(path)` - List directory
- `search_files(pattern)` - Search by pattern **sqlite-mcp**
- `query(sql)` - Execute SQL query
- `execute(sql)` - Execute SQL statement
- `list_tables()` - Show all tables
- `describe_table(name)` - Table schema **pytest-mcp**
- `list_failures()` - Recent test failures
- `analyze_failure(id)` - Detailed analysis
- `get_patterns()` - Failure patterns
- `track_test(name)` - Monitor specific test **git-mcp**
- `log(options)` - Commit history
- `diff(files)` - Show differences
- `status()` - Working tree status
- `branch(name)` - Create/switch branch

---

## 📚 Additional Resources ### Documentation
- [MCP Debugging Quick Start](../README.md)
- [Controller Testing Guide](../../testing/guides/control_systems_unit_testing.md)
- [PSO Optimization Workflow](../../guides/workflows/pso-optimization-workflow.md) ### Slash Commands
- [Analyze Logs](../../../.claude/commands/analyze-logs.md)
- [Debug with MCP](../../../.claude/commands/debug-with-mcp.md)
- [Test Controller](../../../.claude/commands/test-controller.md) ### Configuration
- MCP Configuration: See `.mcp.json` in project root
- [pytest.ini](../../../pytest.ini) - Test configuration
- Environment Variables: See `.env.example` in project root

---

## 🐛 Troubleshooting ### MCP Server Not Responding ```bash
# Check server status
npx @modelcontextprotocol/inspector # Verify paths in .mcp.json
cat .mcp.json | jq '.mcpServers' # Test individual server
node <server_path> --test
``` ### Database Connection Issues ```bash
# Check database exists

ls -la logs/pso_results.db # Verify permissions
chmod 664 logs/pso_results.db # Test SQLite connection
sqlite3 logs/pso_results.db "SELECT sqlite_version();"
``` ### Test Failures ```bash
# Clear pytest cache
pytest --cache-clear # Run with verbose output
pytest -vv --tb=long # Check for conflicts
pip list | grep pytest
```

---

**Version**: 1.0.0
**Last Updated**: 2025-10-06
**Maintainer**: DIP-SMC-PSO Team
