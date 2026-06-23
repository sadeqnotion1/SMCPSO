# interfaces.hil.test_automation

**Source:** `src\interfaces\hil\test_automation.py`

## Module Overview Automated

testing framework for HIL systems

.


This module provides test automation features including
test case management, assertion validation, performance testing, and
automated report generation for control system validation. ## Mathematical Foundation ### Automated Testing Framework Systematic testing of control systems: ```{math}
\mathcal{T} = \{(\vec{x}_0^{(i)}, u_{\text{profile}}^{(i)}, \text{criteria}^{(i)})\}_{i=1}^{M}
``` Where:
- $\vec{x}_0^{(i)}$: Initial condition for test $i$
- $u_{\text{profile}}^{(i)}$: Reference control profile
- $\text{criteria}^{(i)}$: Pass/fail criteria ### Test Coverage Metrics **1. State Space Coverage:**
```{math}

C_{\text{state}} = \frac{|\mathcal{X}_{\text{tested}}|}{|\mathcal{X}_{\text{total}}|}
``` **2. Input Space Coverage:**
```{math}

C_{\text{input}} = \frac{|\mathcal{U}_{\text{tested}}|}{|\mathcal{U}_{\text{total}}|}
``` **3. Scenario Coverage:**
```{math}

C_{\text{scenario}} = \frac{\text{Scenarios Tested}}{\text{Total Scenarios}}
``` ### Test Case Generation **1. Grid-Based Sampling:**
```{math}

\mathcal{X}_{\text{test}} = \{\vec{x}_0^{(i,j,k)}\} = \{(x_i, \theta_{1,j}, \theta_{2,k})\}
``` **2. Latin Hypercube Sampling:**
Stratified random sampling for better coverage. **3. Boundary Testing:**
Test extreme values and edge cases:
```{math}

\vec{x}_{\text{boundary}} \in \partial \mathcal{X}
``` ### Pass/Fail Criteria **1. Stability Criterion:**
```{math}

\text{PASS} \Leftrightarrow \lim_{t \to \infty} \|\vec{x}(t)\| < \epsilon_{\text{stable}}
``` **2. Performance Criterion:**
```{math}

\text{PASS} \Leftrightarrow \text{ITAE} < \text{ITAE}_{\text{threshold}}
``` **3. Safety Criterion:**
```{math}

\text{PASS} \Leftrightarrow \forall t : |u(t)| \leq u_{\text{max}}
``` ### Regression Testing **Performance Regression Detection:**
```{math}

\Delta P = P_{\text{current}} - P_{\text{baseline}}
``` **Statistical Significance Test:**
```{math}

H_0 : \mu_{\text{current}} = \mu_{\text{baseline}}
``` Use t-test with significance level $\alpha = 0.05$. ### Continuous Integration Workflow **1. Commit Trigger:**
Every code change triggers automated tests. **2. Test Execution:**
```{math}

\text{Result} = \bigwedge_{i=1}^{M} \text{Test}_i(\text{Code})
``` **3. Report Generation:**
- Pass/fail summary
- Performance metrics
- Regression analysis ### Test Execution Time **Total Execution Time:**
```{math}

T_{\text{total}} = \sum_{i=1}^{M} T_{\text{test}}^{(i)}
``` **Parallelization Speedup:**
```{math}

S = \frac{T_{\text{sequential}}}{T_{\text{parallel}}}
``` ### Test Reliability **Flaky Test Detection:**
```{math}

P(\text{flaky}) = \frac{\text{Inconsistent Results}}{\text{Total Runs}}
``` **Target:** $P(\text{flaky}) < 0.01$ (1% flakiness) ## Architecture Diagram ```{mermaid}
graph TD A[Test Suite] --> B[Test Generator] B --> C{Generation Method} C -->|Grid| D[Grid Sampling] C -->|Random| E[Latin Hypercube] C -->|Boundary| F[Boundary Testing] D --> G[Test Case Pool] E --> G F --> G G --> H[Test Executor] H --> I[Run HIL Simulation] I --> J[Collect Results] J --> K{Pass/Fail} K -->|Pass| L[Success Log] K -->|Fail| M[Failure Analysis] M --> N[Debug Report] M --> O[Regression Check] L --> P[Test Report] N --> P O --> P P --> Q[CI Dashboard] style H fill:#9cf style K fill:#ff9 style P fill:#f9f style Q fill:#9f9
``` **Automated Testing Workflow:**

1. **Test Generation**: Create test cases using sampling strategies
2. **Test Execution**: Run HIL simulations for each test case
3. **Result Collection**: Gather performance metrics and logs
4. **Pass/Fail Evaluation**: Check against acceptance criteria
5. **Reporting**: Generate test report
6. **Integration**: Push results to CI dashboard ## Usage Examples ### Example 1: Basic Test Suite ```python
from src.interfaces.hil.test_automation import TestSuite # Create test suite
suite = TestSuite(name="HIL_Controller_Tests") # Define test cases
suite.add_test( name="stability_test", initial_state=[0.0, 0.1, -0.05, 0.0, 0.0, 0.0], duration=5.0, pass_criteria={"max_angle": 0.2, "settling_time": 3.0}
) suite.add_test( name="disturbance_rejection", initial_state=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], disturbance={"type": "step", "magnitude": 10.0, "time": 2.0}, pass_criteria={"recovery_time": 2.0}
) # Run all tests
results = suite.run_all() # Report
suite.print_report()
``` ### Example 2: Grid-Based Test Generation ```python
from src.interfaces.hil.test_automation import GridTestGenerator # Generate test cases on grid
generator = GridTestGenerator() # Define parameter ranges
theta1_values = np.linspace(-0.2, 0.2, 5)
theta2_values = np.linspace(-0.2, 0.2, 5) test_cases = generator.generate( theta1=theta1_values, theta2=theta2_values, x=[0.0], # Fixed cart position velocities=[0.0, 0.0, 0.0] # Zero initial velocity
) print(f"Generated {len(test_cases)} test cases") # Run all generated tests
for i, test_case in enumerate(test_cases): result = run_hil_simulation(initial_state=test_case) print(f"Test {i+1}: {'PASS' if result.stable else 'FAIL'}")
``` ### Example 3: Monte Carlo Robustness Testing ```python

from src.interfaces.hil.test_automation import MonteCarloTester # Monte Carlo test generator
tester = MonteCarloTester(n_trials=100) # Define parameter distributions
tester.set_distribution( "theta1", distribution="normal", mean=0.0, std=0.1
)
tester.set_distribution( "theta2", distribution="normal", mean=0.0, std=0.1
)
tester.set_distribution( "noise", distribution="uniform", low=0.0, high=0.05
) # Run Monte Carlo tests
results = tester.run() # Analyze results
success_rate = sum(r.passed for r in results) / len(results)
print(f"Success rate: {success_rate * 100:.1f}%")
``` ### Example 4: Continuous Integration Testing ```python
from src.interfaces.hil.test_automation import CITestRunner # CI test runner
ci_runner = CITestRunner( test_suite_path="tests/hil_tests.yaml", report_path="ci_report.json"
) # Run tests
results = ci_runner.run() # Check for regressions
if results.has_regressions(): print("REGRESSION DETECTED!") for test in results.regressions: print(f" {test.name}: {test.baseline_time:.2f}s -> {test.current_time:.2f}s") exit(1) print("All tests passed, no regressions")
exit(0)
``` ### Example 5: Adaptive Test Difficulty ```python

from src.interfaces.hil.test_automation import AdaptiveTester # Adaptive tester
tester = AdaptiveTester( initial_difficulty=0.5, adjustment_rate=0.1
) # Run adaptive tests
for i in range(20): test_case = tester.generate_test() result = run_hil_simulation(test_case) # Adjust difficulty based on result tester.update(result.passed) print(f"Test {i+1}: difficulty={tester.current_difficulty:.2f}, " f"result={'PASS' if result.passed else 'FAIL'}") # Report final difficulty
print(f"Final difficulty: {tester.current_difficulty:.2f}")
``` ## Complete Source Code ```{literalinclude} ../../../src/interfaces/hil/test_automation.py
:language: python
:linenos:
```

---

## Classes

### `TestStatus`

**Inherits from:** `Enum` Test execution status enumeration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/test_automation.py

:language: python
:pyobject: TestStatus
:linenos:
```

### `AssertionType`

**Inherits from:** `Enum` Test assertion type enumeration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/test_automation.py
:language: python
:pyobject: AssertionType
:linenos:
```

### `TestAssertion`

Test assertion configuration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/test_automation.py

:language: python
:pyobject: TestAssertion
:linenos:
```

### `TestCase`

Individual test case configuration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/test_automation.py
:language: python
:pyobject: TestCase
:linenos:
```

### `TestSuite`

Test suite containing multiple test cases.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/test_automation.py

:language: python
:pyobject: TestSuite
:linenos:
```

### `TestResult`

Test execution result.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/test_automation.py
:language: python
:pyobject: TestResult
:linenos:
```

### `HILTestFramework`

test automation framework for HIL systems. Provides automated test execution, assertion validation,

performance testing, and report generation features. #### Source Code ```{literalinclude} ../../../src/interfaces/hil/test_automation.py
:language: python
:pyobject: HILTestFramework
:linenos:
``` #### Methods (19) ##### `__init__(self, hil_system, test_scenarios)` Initialize HIL test framework. [View full source →](#method-hiltestframework-__init__) ##### `add_test_suite(self, suite)` Add test suite to framework. [View full source →](#method-hiltestframework-add_test_suite) ##### `add_test_case(self, suite_name, test_case)` Add test case to existing suite. [View full source →](#method-hiltestframework-add_test_case) ##### `run_test_suite(self, suite_name)` Run complete test suite. [View full source →](#method-hiltestframework-run_test_suite) ##### `run_test_case(self, test_case)` Run individual test case. [View full source →](#method-hiltestframework-run_test_case) ##### `run_all_suites(self)` Run all configured test suites. [View full source →](#method-hiltestframework-run_all_suites) ##### `_run_sequential_tests(self, suite)` Run test cases sequentially. [View full source →](#method-hiltestframework-_run_sequential_tests) ##### `_run_parallel_tests(self, suite)` Run test cases in parallel. [View full source →](#method-hiltestframework-_run_parallel_tests) ##### `_execute_test_case(self, test_case)` Execute individual test case logic. [View full source →](#method-hiltestframework-_execute_test_case) ##### `_run_test_assertions(self, test_case, result)` Run test assertions and collect results. [View full source →](#method-hiltestframework-_run_test_assertions) ##### `_monitor_assertion(self, assertion, start_time, duration)` Monitor and validate test assertion. [View full source →](#method-hiltestframework-_monitor_assertion) ##### `_validate_assertion(self, assertion, actual_value)` Validate individual assertion. [View full source →](#method-hiltestframework-_validate_assertion) ##### `_get_signal_value(self, signal_name)` Get current value of specified signal. [View full source →](#method-hiltestframework-_get_signal_value) ##### `_execute_setup_commands(self, commands)` Execute setup commands. [View full source →](#method-hiltestframework-_execute_setup_commands) ##### `_execute_teardown_commands(self, commands)` Execute teardown commands. [View full source →](#method-hiltestframework-_execute_teardown_commands) ##### `_execute_command(self, command)` Execute individual command. [View full source →](#method-hiltestframework-_execute_command) ##### `_set_signal_value(self, signal_name, value)` Set signal value in HIL system. [View full source →](#method-hiltestframework-_set_signal_value) ##### `_apply_initial_conditions(self, conditions)` Apply initial conditions for test. [View full source →](#method-hiltestframework-_apply_initial_conditions) ##### `_apply_test_inputs(self, inputs)` Apply test inputs. [View full source →](#method-hiltestframework-_apply_test_inputs)

### `TestReportGenerator`

Generate test reports.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/test_automation.py
:language: python
:pyobject: TestReportGenerator
:linenos:
``` #### Methods (6) ##### `__init__(self)` [View full source →](#method-testreportgenerator-__init__) ##### `generate_comprehensive_report(self, suite_results, test_results)` Generate test report. [View full source →](#method-testreportgenerator-generate_comprehensive_report) ##### `_generate_summary(self, suite_results, test_results)` Generate test summary. [View full source →](#method-testreportgenerator-_generate_summary) ##### `_generate_statistics(self, test_results)` Generate test statistics. [View full source →](#method-testreportgenerator-_generate_statistics) ##### `_generate_recommendations(self, test_results)` Generate test recommendations. [View full source →](#method-testreportgenerator-_generate_recommendations) ##### `_result_to_dict(self, result)` Convert test result to dictionary. [View full source →](#method-testreportgenerator-_result_to_dict)

---

## Dependencies This module imports: - `import asyncio`

- `import time`
- `import json`
- `from dataclasses import dataclass, field`
- `from typing import Dict, Any, Optional, List, Callable, Union`
- `from enum import Enum`
- `import logging`
