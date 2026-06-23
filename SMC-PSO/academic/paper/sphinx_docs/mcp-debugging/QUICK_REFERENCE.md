# MCP Debugging Quick Reference

**🚀 Quick access to common MCP debugging operations**



## 📋 Slash Commands

| Command | Description | Use When |
|---------|-------------|----------|
| `/analyze-logs` | Automated log analysis | Need to review simulation/PSO logs |
| `/analyze-pso-logs` | PSO convergence analysis | PSO optimization issues |
| `/test-controller` | Run controller test suite | Verifying controller implementations |
| `/test-browser` | Test Streamlit dashboard | UI/dashboard validation |
| `/validate-simulation` | Validate against control criteria | Checking simulation results |
| `/optimize-controller` | Launch PSO optimization | Tuning controller parameters |
| `/debug-with-mcp` | Integrated debugging session | Complex multi-domain issues |
| `/inspect-server` | Launch MCP Inspector | Testing server connectivity |



## 🔧 MCP Server Tools

### filesystem (File Operations)

```javascript
// Read file
read_file({ path: "src/controllers/smc.py" })

// Write file
write_file({ path: "config.json", content: "{...}" })

// List directory
list_directory({ path: "logs/" })

// Search files
search_files({ pattern: "*.log", query: "LinAlgError" })
```

### sqlite-mcp (Database Queries)

```sql
-- List all tables
list_tables()

-- Query PSO results
query({ sql: "SELECT * FROM pso_runs ORDER BY timestamp DESC LIMIT 10" })

-- Get convergence data
query({ sql: "SELECT iteration, gbest_fitness FROM pso_iterations WHERE run_id='<id>'" })

-- Analyze performance
query({ sql: "SELECT controller_type, AVG(settling_time) FROM results GROUP BY controller_type" })
```

### pytest-mcp (Test Debugging)

```javascript
// List recent failures
list_failures({ last: 10 })

// Analyze specific failure
analyze_failure({ test_id: "test_smc_stability" })

// Get failure patterns
get_patterns({ groupby: "test_name" })

// Track test
track_test({ name: "test_pso_convergence" })
```

### git-mcp (Version Control)

```bash
# View commit history
log({ options: "--oneline --since '1 week ago'" })

# Show differences
diff({ files: "src/controllers/" })

# Check status
status()

# Create branch
branch({ name: "fix/numerical-stability" })

# Show specific commit
show({ commit: "<hash>" })
```



## 🐛 Common Debugging Scenarios

### Scenario 1: PSO Not Converging

```bash
# 1. Check recent runs
/analyze-pso-logs

# 2. Query database
sqlite: SELECT * FROM pso_runs WHERE status='stagnated' LIMIT 5;

# 3. Review hyperparameters
filesystem: read_file("config/pso_config.yaml")

# 4. Check for bound violations
/analyze-logs --filter "parameter.*out of bounds"
```

## Scenario 2: Test Failing

```bash
# 1. List failures
pytest-mcp: list_failures({ last: 5 })

# 2. Get detailed info
pytest-mcp: analyze_failure({ test_id: "<id>" })

# 3. Check test code
filesystem: read_file("tests/test_<name>.py")

# 4. Review logs
/analyze-logs --pattern "FAILED"
```

## Scenario 3: Numerical Error

```bash
# 1. Search for errors
filesystem: search_files({ pattern: "*.log", query: "LinAlgError" })

# 2. Check matrix operations
filesystem: read_file("src/models/dynamics.py") | grep "np.linalg.inv"

# 3. Review recent changes
git-mcp: diff({ files: "src/models/" })

# 4. Run stability tests
/test-controller --filter numerical_stability
```

## Scenario 4: Dashboard Issue

```bash
# 1. Launch dashboard
streamlit run app.py

# 2. Test with Puppeteer
/test-browser

# 3. Check logs
filesystem: read_file("logs/streamlit.log")

# 4. Verify data
sqlite: SELECT COUNT(*) FROM simulation_results;
```



## 📊 Quick Data Queries

### PSO Performance

```sql
-- Best fitness by controller type
SELECT controller_type, MIN(best_fitness) as best
FROM pso_runs
GROUP BY controller_type
ORDER BY best;

-- Average convergence time
SELECT AVG(convergence_iteration) as avg_iter
FROM pso_runs
WHERE convergence_achieved = 1;

-- Recent failures
SELECT run_id, error_message
FROM pso_runs
WHERE status = 'failed'
ORDER BY timestamp DESC
LIMIT 5;
```

### Test Results

```sql
-- Test success rate
SELECT
  test_name,
  SUM(CASE WHEN status='passed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
FROM test_results
GROUP BY test_name
ORDER BY success_rate;

-- Recent failures
SELECT test_name, failure_message, timestamp
FROM test_results
WHERE status = 'failed'
ORDER BY timestamp DESC
LIMIT 10;
```

### Simulation Metrics

```sql
-- Performance comparison
SELECT
  controller_type,
  AVG(settling_time) as avg_settling,
  AVG(overshoot) as avg_overshoot,
  AVG(steady_state_error) as avg_sse
FROM simulation_results
GROUP BY controller_type;

-- Best performing runs
SELECT controller_type, settling_time, overshoot
FROM simulation_results
ORDER BY settling_time
LIMIT 5;
```



## 🔍 Search Patterns

### Log Analysis Patterns

```bash
# Numerical errors
/analyze-logs --pattern "LinAlgError|RuntimeWarning|singular matrix"

# Convergence issues
/analyze-logs --pattern "stagnation|divergence|no improvement"

# Test failures
/analyze-logs --pattern "FAILED|ERROR|AssertionError"

# Performance issues
/analyze-logs --pattern "timeout|slow|exceeded limit"
```

## Code Search Patterns

```bash
# Find matrix inversions
filesystem: search_files({ pattern: "*.py", query: "np.linalg.inv" })

# Find todos
filesystem: search_files({ pattern: "*.py", query: "TODO|FIXME" })

# Find type errors
filesystem: search_files({ pattern: "*.py", query: "type:.*ignore" })

# Find deprecated
filesystem: search_files({ pattern: "*.py", query: "deprecated" })
```



## 🛠️ Configuration Files

### .mcp.json Structure

```json
{
  "mcpServers": {
    "<server-name>": {
      "type": "stdio",
      "command": "node",
      "args": ["<path-to-server>", "<optional-args>"],
      "env": {
        "KEY": "value"
      },
      "description": "Server description"
    }
  }
}
```

### Server Paths

```
mcp-debugger:
  C:\Users\sadeg\AppData\Roaming\npm\node_modules\mcp-debugger\bin\mcp-debugger.js

pytest-mcp:
  C:\Users\sadeg\AppData\Roaming\npm\node_modules\pytest-mcp-server\dist\cli.js

git-mcp:
  C:\Users\sadeg\AppData\Roaming\npm\node_modules\@cyanheads\git-mcp-server\dist\index.js

sqlite-mcp:
  C:\Users\sadeg\AppData\Roaming\npm\node_modules\mcp-sqlite\mcp-sqlite-server.js
```



## 🚨 Troubleshooting

### Server Not Responding

```bash
# 1. Check server status
npx @modelcontextprotocol/inspector

# 2. Verify configuration
cat .mcp.json | jq '.mcpServers.<server-name>'

# 3. Test server directly
node <server-path> --test

# 4. Check logs
cat ~/.mcp/logs/<server-name>.log
```

## Database Connection Failed

```bash
# 1. Verify database exists
ls -la logs/pso_results.db

# 2. Check permissions
chmod 664 logs/pso_results.db

# 3. Test connection
sqlite3 logs/pso_results.db "SELECT 1;"

# 4. Recreate if corrupted
mv logs/pso_results.db logs/pso_results.db.bak
python scripts/create_pso_database.py
```

## Import Errors

```bash
# 1. Check Python path
echo $PYTHONPATH

# 2. Verify installation
pip list | grep <package>

# 3. Reinstall
pip install --force-reinstall <package>

# 4. Check virtual environment
which python
```



## 📖 Documentation Links

### Workflows

- [Complete Debugging Workflow](workflows/complete-debugging-workflow.md)
- [PSO Optimization Workflow](../guides/workflows/pso-optimization-workflow.md)
- [Controller Testing Guide](../testing/guides/control_systems_unit_testing.md)

### Configuration

- MCP Configuration: See `.mcp.json` in project root
- [Pytest Configuration](../../pytest.ini)
- Environment Variables: See `.env.example` in project root

### Slash Commands

- [Analyze Logs](../../.claude/commands/analyze-logs.md)
- [Debug with MCP](../../.claude/commands/debug-with-mcp.md)
- [Test Controller](../../.claude/commands/test-controller.md)



## 💡 Tips and Tricks

### 1. Parallel Debugging

```bash
# Run multiple slash commands in sequence
/analyze-logs && /test-controller && /validate-simulation
```

## 2. Custom Queries

```sql
-- Create view for common queries
CREATE VIEW recent_failures AS
SELECT * FROM pso_runs
WHERE status = 'failed'
ORDER BY timestamp DESC
LIMIT 20;

-- Query the view
SELECT * FROM recent_failures;
```

### 3. Batch Operations

```bash
# Process multiple log files
for log in logs/*.log; do
    /analyze-logs --file "$log" >> analysis.txt
done
```

## 4. Integration with CI/CD

```bash
# Add to pytest configuration
[pytest]
addopts = --mcp-server=pytest-mcp --track-failures
```



**Last Updated**: 2025-10-06
**Version**: 1.0.0
