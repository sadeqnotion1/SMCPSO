#!/usr/bin/env python3
"""
=======================================================================================
                    scripts/docs/enhance_hil_docs.py
=======================================================================================
HIL Documentation Enhancement Script for Week 7 Phase 2

Enhances all 9 HIL (Hardware-in-the-Loop) documentation files with:
- Mathematical foundations (communication protocols, timing analysis, fault models)
- Architecture diagrams (Mermaid flowcharts for data flow and timing)
- Usage examples (4-5 comprehensive scenarios per file)
- Theory coverage (real-time systems, network protocols, fault tolerance)

Usage:
    python scripts/docs/enhance_hil_docs.py --dry-run
    python scripts/docs/enhance_hil_docs.py
"""

import re
from pathlib import Path
from typing import List
from dataclasses import dataclass

@dataclass
class HILEnhancementStats:
    """Statistics for HIL documentation enhancement."""
    files_enhanced: int = 0
    lines_added: int = 0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class HILDocEnhancer:
    """Enhances HIL documentation with comprehensive content."""

    # All 9 HIL documentation files to enhance
    HIL_FILES = [
        'hil_plant_server.md',
        'hil_controller_client.md',
        'hil_simulation_bridge.md',
        'hil_real_time_sync.md',
        'hil_fault_injection.md',
        'hil_data_logging.md',
        'hil_test_automation.md',
        'hil_enhanced_hil.md',
        'hil___init__.md',
    ]

    def __init__(self, docs_root: Path, dry_run: bool = False):
        self.docs_root = docs_root / 'reference' / 'interfaces'
        self.dry_run = dry_run
        self.stats = HILEnhancementStats()

    def enhance_all_files(self):
        """Enhance all HIL documentation files."""
        print("\n" + "="*80)
        print("Week 7 Phase 2: HIL Documentation Enhancement")
        print("="*80)

        for filename in self.HIL_FILES:
            doc_path = self.docs_root / filename
            if not doc_path.exists():
                error = f"File not found: {doc_path}"
                print(f"  ERROR: {error}")
                self.stats.errors.append(error)
                continue

            self._enhance_file(doc_path, filename)

        self._print_summary()

    def _enhance_file(self, doc_path: Path, filename: str):
        """Enhance a single HIL documentation file."""
        print(f"\nEnhancing: {filename}...")

        try:
            # Read existing content
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if already enhanced
            if '## Mathematical Foundation' in content:
                print("  SKIPPED: Already enhanced")
                return

            # Generate enhancements based on file type
            theory_section = self._generate_theory_section(filename)
            diagram_section = self._generate_diagram_section(filename)
            examples_section = self._generate_examples_section(filename)

            # Insert enhancements after Module Overview
            enhanced_content = self._insert_enhancements(
                content, theory_section, diagram_section, examples_section
            )

            # Calculate lines added
            lines_added = enhanced_content.count('\n') - content.count('\n')

            # Write enhanced content
            if not self.dry_run:
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(enhanced_content)
                print(f"  SUCCESS: Added {lines_added} lines")
            else:
                print(f"  [DRY RUN] Would add {lines_added} lines")

            self.stats.files_enhanced += 1
            self.stats.lines_added += lines_added

        except Exception as e:
            error = f"Error enhancing {filename}: {e}"
            print(f"  ERROR: {error}")
            self.stats.errors.append(error)

    def _insert_enhancements(self, content: str, theory: str, diagram: str, examples: str) -> str:
        """Insert enhancement sections after Module Overview."""
        # Find Module Overview section
        overview_match = re.search(r'(##\s+Module Overview.*?)(\n##\s+)', content, re.DOTALL)
        if overview_match:
            # Insert after Module Overview, before next section
            return (content[:overview_match.end(1)] +
                    f"\n\n{theory}\n\n{diagram}\n\n{examples}\n" +
                    content[overview_match.end(1):])

        # If no Module Overview found, insert after source reference
        source_match = re.search(r'(\*\*Source:\*\*.*?\n)', content, re.DOTALL)
        if source_match:
            return (content[:source_match.end(1)] +
                    f"\n{theory}\n\n{diagram}\n\n{examples}\n\n" +
                    content[source_match.end(1):])

        return content

    def _generate_theory_section(self, filename: str) -> str:
        """Generate mathematical foundation section based on file type."""
        if filename == 'hil_plant_server.md':
            return self._plant_server_theory()
        elif filename == 'hil_controller_client.md':
            return self._controller_client_theory()
        elif filename == 'hil_simulation_bridge.md':
            return self._simulation_bridge_theory()
        elif filename == 'hil_real_time_sync.md':
            return self._real_time_sync_theory()
        elif filename == 'hil_fault_injection.md':
            return self._fault_injection_theory()
        elif filename == 'hil_data_logging.md':
            return self._data_logging_theory()
        elif filename == 'hil_test_automation.md':
            return self._test_automation_theory()
        elif filename == 'hil_enhanced_hil.md':
            return self._enhanced_hil_theory()
        elif filename == 'hil___init__.md':
            return self._hil_package_theory()
        return ""

    def _plant_server_theory(self) -> str:
        return """## Mathematical Foundation

### Real-Time Dynamics Simulation

The plant server runs high-fidelity dynamics simulation with real-time constraints:

```{math}
\\dot{\\vec{x}}(t) = f(\\vec{x}(t), u(t))
```

Where:
- $\\vec{x} \\in \\mathbb{R}^6$: Full state (cart position, pendulum angles, velocities)
- $u \\in \\mathbb{R}$: Control input from remote controller
- $f$: Nonlinear dynamics function with all coupling effects

### Communication Protocol

TCP socket communication with message framing:

```{math}
\\text{Message} = \\text{Header}(\\text{size}, \\text{type}) || \\text{Payload}(\\vec{x}, t)
```

**Message Format:**
1. **Header**: 8 bytes (4-byte size + 4-byte type)
2. **Payload**: State vector + timestamp (56 bytes)
3. **Total**: 64 bytes per message

### Latency Model

Total round-trip latency components:

```{math}
T_{\\text{total}} = T_{\\text{serialize}} + T_{\\text{network}} + T_{\\text{process}} + T_{\\text{deserialize}}
```

Where:
- $T_{\\text{serialize}}$: JSON serialization time (~0.5 ms)
- $T_{\\text{network}}$: TCP round-trip time (configurable, default 5 ms)
- $T_{\\text{process}}$: Controller computation time (variable)
- $T_{\\text{deserialize}}$: JSON deserialization time (~0.5 ms)

**Timing Constraint:**
```{math}
T_{\\text{total}} < \\Delta t \\quad \\text{(Control period constraint)}
```

### Sensor Noise Model

Additive Gaussian noise on state measurements:

```{math}
\\tilde{\\vec{x}}(t) = \\vec{x}(t) + \\vec{\\eta}(t), \\quad \\vec{\\eta} \\sim \\mathcal{N}(0, \\sigma^2 I)
```

Where:
- $\\tilde{\\vec{x}}$: Noisy measurement
- $\\vec{\\eta}$: Gaussian noise vector
- $\\sigma$: Standard deviation (configurable, default 0.01)

### Server Architecture

**Thread-Safe State Management:**
- Main dynamics thread: Runs simulation at fixed timestep
- Network thread: Handles TCP connections and message exchange
- Shared state: Protected by locks for thread safety

**Graceful Degradation:**
- Connection timeout: 10 seconds
- Maximum steps: Prevents infinite loops
- Failsafe shutdown: Clean resource cleanup on errors"""

    def _controller_client_theory(self) -> str:
        return """## Mathematical Foundation

### Remote Controller Execution

The client executes control law remotely with network delay:

```{math}
u(t) = \\pi(\\tilde{\\vec{x}}(t - \\tau))
```

Where:
- $\\pi$: Controller policy (SMC, MPC, etc.)
- $\\tilde{\\vec{x}}$: Noisy state measurement from plant server
- $\\tau$: Network latency (round-trip delay)

### Request-Response Cycle

Synchronous communication pattern:

```{math}
\\begin{align}
t_0 &: \\text{Send state request} \\\\
t_1 &= t_0 + \\tau_{\\text{req}}: \\text{Receive state from server} \\\\
t_2 &= t_1 + \\Delta t_{\\text{compute}}: \\text{Compute control} \\\\
t_3 &= t_2 + \\tau_{\\text{resp}}: \\text{Send control to server}
\\end{align}
```

**Timing Budget:**
```{math}
\\tau_{\\text{req}} + \\Delta t_{\\text{compute}} + \\tau_{\\text{resp}} < \\Delta t_{\\text{control}}
```

### Control Delay Effects

Delayed control input affects stability margins:

```{math}
\\dot{\\vec{x}}(t) = f(\\vec{x}(t), u(t - \\tau))
```

**Smith Predictor Compensation:**
```{math}
u(t) = \\pi(\\hat{\\vec{x}}(t + \\tau))
```

Where $\\hat{\\vec{x}}$ is predicted state accounting for delay.

### Fallback Controller

PD controller for emergency scenarios:

```{math}
u_{\\text{fallback}} = -K_p \\theta_1 - K_d \\dot{\\theta}_1
```

**Failover Conditions:**
1. Network timeout (>1 second)
2. Server connection lost
3. Controller computation failure

### Message Serialization

JSON-based state representation:

```json
{
  "state": [x, theta1, theta2, x_dot, theta1_dot, theta2_dot],
  "time": 0.123,
  "step": 123,
  "control": 12.5
}
```

**Serialization Performance:**
- Encode time: ~0.3 ms
- Decode time: ~0.2 ms
- Message size: ~150 bytes

### Client Architecture

**Event Loop Pattern:**
1. Request state from server
2. Wait for response (with timeout)
3. Compute control action
4. Send control to server
5. Log data and metrics
6. Repeat until simulation complete

**Error Recovery:**
- Retry policy: 3 attempts with exponential backoff
- Graceful degradation: Switch to fallback controller
- Clean shutdown: Save partial results on failure"""

    def _simulation_bridge_theory(self) -> str:
        return """## Mathematical Foundation

### Bridge Architecture Pattern

The simulation bridge decouples plant and controller execution:

```{math}
\\text{Plant} \\xleftrightarrow{\\text{Bridge}} \\text{Controller}
```

**Key Properties:**
1. **Asynchrony**: Plant and controller run at different rates
2. **Location transparency**: Local or remote execution
3. **Protocol abstraction**: TCP, UDP, shared memory, etc.

### Data Exchange Protocol

Bi-directional message passing:

```{math}
\\begin{align}
M_{\\text{state}} &: \\text{Plant} \\rightarrow \\text{Controller} : (\\vec{x}, t, \\text{metadata}) \\\\
M_{\\text{control}} &: \\text{Controller} \\rightarrow \\text{Plant} : (u, t, \\text{flags})
\\end{align}
```

**Message Synchronization:**
```{math}
|t_{\\text{state}} - t_{\\text{control}}| < \\epsilon
```

Ensures temporal consistency between state and control.

### Communication Middleware

**Transport Layer Options:**
1. **TCP**: Reliable, ordered delivery (default)
2. **UDP**: Low-latency, unreliable
3. **Shared Memory**: Zero-copy for co-located processes

**Protocol Selection Criteria:**
```{math}
\\text{Protocol} = \\begin{cases}
\\text{TCP} & \\text{if reliability required} \\\\
\\text{UDP} & \\text{if latency critical} \\\\
\\text{Shared Mem} & \\text{if same machine}
\\end{cases}
```

### State Interpolation

For asynchronous execution, interpolate state:

```{math}
\\vec{x}(t_{\\text{req}}) \\approx \\vec{x}(t_k) + \\frac{t_{\\text{req}} - t_k}{t_{k+1} - t_k} (\\vec{x}(t_{k+1}) - \\vec{x}(t_k))
```

**Linear Interpolation Accuracy:**
```{math}
\\|\\vec{x}_{\\text{true}} - \\vec{x}_{\\text{interp}}\\| \\leq C \\|\\Delta t\\|^2
```

### Fault Tolerance

**Heartbeat Mechanism:**
```{math}
\\text{Health}(t) = \\begin{cases}
\\text{OK} & \\text{if } t - t_{\\text{last\_msg}} < T_{\\text{heartbeat}} \\\\
\\text{TIMEOUT} & \\text{otherwise}
\\end{cases}
```

**Automatic Reconnection:**
- Exponential backoff: $T_{\\text{retry}} = T_0 \\cdot 2^n$
- Maximum retries: 5 attempts
- Circuit breaker: Disable after persistent failures

### Performance Metrics

**Throughput:**
```{math}
\\text{Throughput} = \\frac{\\text{Messages}}{\\text{Time}} \\quad [\\text{msg/s}]
```

**Latency Percentiles:**
- P50: Median latency (typical)
- P95: 95th percentile (good)
- P99: 99th percentile (worst-case)

### Bridge Implementation

**Thread Model:**
- **Receiver thread**: Listens for incoming messages
- **Sender thread**: Sends outgoing messages
- **Main thread**: Orchestrates simulation logic

**Thread Safety:**
- Lock-free queues for message passing
- Atomic operations for shared state
- No blocking operations in critical path"""

    def _real_time_sync_theory(self) -> str:
        return """## Mathematical Foundation

### Real-Time Synchronization

Maintain synchronized execution across plant and controller:

```{math}
|t_{\\text{plant}} - t_{\\text{controller}}| < \\delta_{\\text{sync}}
```

Where $\\delta_{\\text{sync}}$ is the maximum allowable time skew (default: 1 ms).

### Clock Synchronization

**Network Time Protocol (NTP) Adaptation:**

```{math}
\\begin{align}
t_{\\text{offset}} &= \\frac{(t_2 - t_1) + (t_3 - t_4)}{2} \\\\
t_{\\text{latency}} &= \\frac{(t_4 - t_1) - (t_3 - t_2)}{2}
\\end{align}
```

Where:
- $t_1$: Client send time
- $t_2$: Server receive time
- $t_3$: Server send time
- $t_4$: Client receive time

### Rate Synchronization

Synchronize simulation rates using PLL-style feedback:

```{math}
\\Delta t_{\\text{adjusted}} = \\Delta t_{\\text{nominal}} + K_p (t_{\\text{ref}} - t_{\\text{local}})
```

Where:
- $K_p$: Proportional gain for rate adjustment
- $t_{\\text{ref}}$: Reference time from remote
- $t_{\\text{local}}$: Local simulation time

### Deadline-Driven Scheduling

**Earliest Deadline First (EDF) Policy:**

```{math}
\\text{Priority}(\\text{Task}_i) = \\frac{1}{D_i - t}
```

Where:
- $D_i$: Deadline for task $i$
- $t$: Current time
- Higher priority = earlier deadline

### Timing Constraints

**Hard Real-Time Constraint:**
```{math}
T_{\\text{exec}} + T_{\\text{comm}} \\leq \\Delta t_{\\text{control}}
```

**Jitter Bound:**
```{math}
J = \\max_k |t_k - t_{k-1} - \\Delta t| < J_{\\text{max}}
```

### Synchronization Protocols

**Barrier Synchronization:**
All processes wait at barrier until all arrive:

```{math}
\\forall p \\in \\text{Processes} : t_p \\geq t_{\\text{barrier}}
```

**Lockstep Execution:**
Synchronize every control cycle:

```{math}
\\begin{align}
\\text{Plant} &: \\text{step}(n) \\rightarrow \\text{wait}(n) \\\\
\\text{Controller} &: \\text{compute}(n) \\rightarrow \\text{signal}(n)
\\end{align}
```

### Time Warp Algorithm

Optimistic synchronization with rollback:

```{math}
\\begin{align}
\\text{Execute} &: t_{\\text{local}} < t_{\\text{virtual}} \\\\
\\text{Rollback} &: \\text{if } t_{\\text{msg}} < t_{\\text{virtual}}
\\end{align}
```

**Rollback Cost:**
```{math}
C_{\\text{rollback}} = C_{\\text{restore}} + C_{\\text{recompute}}
```

### Performance Monitoring

**Synchronization Quality Metrics:**

1. **Time Skew:**
   ```{math}
   \\text{Skew} = |t_{\\text{plant}} - t_{\\text{controller}}|
   ```

2. **Drift Rate:**
   ```{math}
   \\text{Drift} = \\frac{d}{dt}(t_{\\text{plant}} - t_{\\text{controller}})
   ```

3. **Synchronization Efficiency:**
   ```{math}
   \\eta_{\\text{sync}} = \\frac{T_{\\text{productive}}}{T_{\\text{total}}}
   ```

**Target Metrics:**
- Skew < 1 ms
- Drift < 100 ppm
- Efficiency > 95%"""

    def _fault_injection_theory(self) -> str:
        return """## Mathematical Foundation

### Fault Injection Models

Systematic fault injection for robustness testing:

```{math}
\\tilde{\\vec{x}}(t) = \\vec{x}(t) + \\vec{f}_{\\text{fault}}(t)
```

Where $\\vec{f}_{\\text{fault}}$ depends on fault type and severity.

### Sensor Fault Models

**1. Bias Fault:**
```{math}
\\tilde{x}_i(t) = x_i(t) + b_i
```

**2. Scaling Fault:**
```{math}
\\tilde{x}_i(t) = \\alpha_i x_i(t), \\quad \\alpha_i \\neq 1
```

**3. Dropout Fault:**
```{math}
\\tilde{x}_i(t) = \\begin{cases}
x_i(t) & \\text{with probability } 1 - p_{\\text{drop}} \\\\
x_i(t - \\tau) & \\text{with probability } p_{\\text{drop}}
\\end{cases}
```

**4. Noise Injection:**
```{math}
\\tilde{x}_i(t) = x_i(t) + \\eta_i(t), \\quad \\eta_i \\sim \\mathcal{N}(0, \\sigma_i^2)
```

### Actuator Fault Models

**1. Saturation Fault:**
```{math}
u_{\\text{actual}} = \\text{clip}(u_{\\text{cmd}}, u_{\\text{min}}^{\\text{fault}}, u_{\\text{max}}^{\\text{fault}})
```

**2. Delay Fault:**
```{math}
u_{\\text{actual}}(t) = u_{\\text{cmd}}(t - \\tau_{\\text{delay}})
```

**3. Degradation Fault:**
```{math}
u_{\\text{actual}}(t) = \\beta(t) \\cdot u_{\\text{cmd}}(t), \\quad 0 < \\beta < 1
```

**4. Stuck-at Fault:**
```{math}
u_{\\text{actual}}(t) = u_{\\text{stuck}}, \\quad \\forall t > t_{\\text{fault}}
```

### Communication Fault Models

**1. Packet Loss:**
```{math}
P(\\text{packet received}) = 1 - p_{\\text{loss}}
```

**2. Latency Spike:**
```{math}
\\tau_{\\text{actual}} = \\begin{cases}
\\tau_{\\text{nominal}} & \\text{with probability } 1 - p_{\\text{spike}} \\\\
\\tau_{\\text{nominal}} + \\Delta \\tau & \\text{with probability } p_{\\text{spike}}
\\end{cases}
```

**3. Message Corruption:**
```{math}
P(\\text{bit flip}) = p_{\\text{corrupt}}
```

### Fault Injection Strategies

**1. Random Injection:**
```{math}
P(\\text{fault at } t) = \\lambda \\cdot \\Delta t
```

Poisson process with rate $\\lambda$.

**2. Scenario-Based Injection:**
Deterministic fault at specific times:
```{math}
\\text{Fault}(t) = \\begin{cases}
\\text{Active} & \\text{if } t \\in [t_{\\text{start}}, t_{\\text{end}}] \\\\
\\text{Inactive} & \\text{otherwise}
\\end{cases}
```

**3. Stress Testing:**
Multiple concurrent faults:
```{math}
\\vec{f}_{\\text{total}} = \\sum_{i=1}^{N} \\alpha_i \\vec{f}_i(t)
```

### Fault Detection Metrics

**1. Detection Time:**
```{math}
T_{\\text{detect}} = t_{\\text{detected}} - t_{\\text{fault}}
```

**2. False Positive Rate:**
```{math}
\\text{FPR} = \\frac{\\text{False Alarms}}{\\text{Total Samples}}
```

**3. False Negative Rate:**
```{math}
\\text{FNR} = \\frac{\\text{Missed Faults}}{\\text{Total Faults}}
```

### Fault Severity Levels

**Categorization:**
1. **Low**: $\\|\\vec{f}\\| < \\epsilon_{\\text{low}}$ (minor disturbance)
2. **Medium**: $\\epsilon_{\\text{low}} \\leq \\|\\vec{f}\\| < \\epsilon_{\\text{high}}$ (degraded performance)
3. **High**: $\\|\\vec{f}\\| \\geq \\epsilon_{\\text{high}}$ (critical failure)
4. **Catastrophic**: System divergence or safety violation"""

    def _data_logging_theory(self) -> str:
        return """## Mathematical Foundation

### Data Logging Architecture

Capture comprehensive simulation data:

```{math}
\\mathcal{D} = \\{(t_k, \\vec{x}_k, u_k, \\vec{m}_k)\\}_{k=0}^{N}
```

Where:
- $t_k$: Timestamp
- $\\vec{x}_k$: State vector
- $u_k$: Control input
- $\\vec{m}_k$: Metadata (controller state, diagnostics)

### Sampling Strategies

**1. Fixed-Rate Sampling:**
```{math}
t_{k+1} = t_k + \\Delta t_{\\text{log}}
```

**2. Event-Triggered Sampling:**
```{math}
\\text{Log}(t) \\Leftrightarrow \\|\\vec{x}(t) - \\vec{x}(t_{\\text{last}})\\| > \\epsilon
```

**3. Adaptive Sampling:**
```{math}
\\Delta t_{\\text{log}} = \\begin{cases}
\\Delta t_{\\text{min}} & \\text{if } \\|\\dot{\\vec{x}}\\| > v_{\\text{thresh}} \\\\
\\Delta t_{\\text{max}} & \\text{otherwise}
\\end{cases}
```

### Data Compression

**Lossless Compression:**
- Delta encoding: Store differences instead of absolute values
- Run-length encoding: Compress repeated values

```{math}
\\Delta \\vec{x}_k = \\vec{x}_k - \\vec{x}_{k-1}
```

**Lossy Compression:**
- Quantization: Reduce precision
- Downsampling: Reduce temporal resolution

```{math}
\\vec{x}_{\\text{quantized}} = \\text{round}\\left(\\frac{\\vec{x}}{q}\\right) \\cdot q
```

### Storage Formats

**1. CSV (Human-Readable):**
```
time,x,theta1,theta2,x_dot,theta1_dot,theta2_dot,control
0.000,0.0,0.1,-0.05,0.0,0.0,0.0,0.0
0.010,0.0,0.099,-0.049,0.05,0.01,0.02,12.5
```

**2. HDF5 (High-Performance):**
- Hierarchical structure
- Chunked storage for efficient I/O
- Built-in compression (gzip, lzf)

**3. Parquet (Columnar):**
- Efficient for analytical queries
- Schema evolution support
- Good compression ratios

### Replay Functionality

**State Reconstruction:**
```{math}
\\vec{x}(t) = \\vec{x}(t_k) + \\int_{t_k}^{t} f(\\vec{x}(\\tau), u(\\tau)) d\\tau
```

**Control Reconstruction:**
```{math}
u(t) = u(t_k), \\quad \\forall t \\in [t_k, t_{k+1})
```

Zero-order hold interpolation.

### Performance Metrics

**1. Logging Overhead:**
```{math}
\\text{Overhead} = \\frac{T_{\\text{logging}}}{T_{\\text{total}}} \\times 100\\%
```

**2. Storage Efficiency:**
```{math}
\\text{Compression Ratio} = \\frac{\\text{Raw Size}}{\\text{Compressed Size}}
```

**3. I/O Throughput:**
```{math}
\\text{Throughput} = \\frac{\\text{Data Volume}}{\\text{Write Time}} \\quad [\\text{MB/s}]
```

### Real-Time Constraints

**Logging Deadline:**
```{math}
T_{\\text{write}} < \\Delta t_{\\text{control}}
```

**Buffer Management:**
- Ring buffer: Fixed-size circular buffer
- Double buffering: Write while logging
- Flush policy: Periodic or threshold-based

**Buffering Strategy:**
```{math}
\\text{Flush} \\Leftrightarrow (\\text{Buffer Full}) \\lor (t - t_{\\text{last\_flush}} > T_{\\text{flush}})
```"""

    def _test_automation_theory(self) -> str:
        return """## Mathematical Foundation

### Automated Testing Framework

Systematic testing of control systems:

```{math}
\\mathcal{T} = \\{(\\vec{x}_0^{(i)}, u_{\\text{profile}}^{(i)}, \\text{criteria}^{(i)})\\}_{i=1}^{M}
```

Where:
- $\\vec{x}_0^{(i)}$: Initial condition for test $i$
- $u_{\\text{profile}}^{(i)}$: Reference control profile
- $\\text{criteria}^{(i)}$: Pass/fail criteria

### Test Coverage Metrics

**1. State Space Coverage:**
```{math}
C_{\\text{state}} = \\frac{|\\mathcal{X}_{\\text{tested}}|}{|\\mathcal{X}_{\\text{total}}|}
```

**2. Input Space Coverage:**
```{math}
C_{\\text{input}} = \\frac{|\\mathcal{U}_{\\text{tested}}|}{|\\mathcal{U}_{\\text{total}}|}
```

**3. Scenario Coverage:**
```{math}
C_{\\text{scenario}} = \\frac{\\text{Scenarios Tested}}{\\text{Total Scenarios}}
```

### Test Case Generation

**1. Grid-Based Sampling:**
```{math}
\\mathcal{X}_{\\text{test}} = \\{\\vec{x}_0^{(i,j,k)}\\} = \\{(x_i, \\theta_{1,j}, \\theta_{2,k})\\}
```

**2. Latin Hypercube Sampling:**
Stratified random sampling for better coverage.

**3. Boundary Testing:**
Test extreme values and edge cases:
```{math}
\\vec{x}_{\\text{boundary}} \\in \\partial \\mathcal{X}
```

### Pass/Fail Criteria

**1. Stability Criterion:**
```{math}
\\text{PASS} \\Leftrightarrow \\lim_{t \\to \\infty} \\|\\vec{x}(t)\\| < \\epsilon_{\\text{stable}}
```

**2. Performance Criterion:**
```{math}
\\text{PASS} \\Leftrightarrow \\text{ITAE} < \\text{ITAE}_{\\text{threshold}}
```

**3. Safety Criterion:**
```{math}
\\text{PASS} \\Leftrightarrow \\forall t : |u(t)| \\leq u_{\\text{max}}
```

### Regression Testing

**Performance Regression Detection:**
```{math}
\\Delta P = P_{\\text{current}} - P_{\\text{baseline}}
```

**Statistical Significance Test:**
```{math}
H_0 : \\mu_{\\text{current}} = \\mu_{\\text{baseline}}
```

Use t-test with significance level $\\alpha = 0.05$.

### Continuous Integration Workflow

**1. Commit Trigger:**
Every code change triggers automated tests.

**2. Test Execution:**
```{math}
\\text{Result} = \\bigwedge_{i=1}^{M} \\text{Test}_i(\\text{Code})
```

**3. Report Generation:**
- Pass/fail summary
- Performance metrics
- Regression analysis

### Test Execution Time

**Total Execution Time:**
```{math}
T_{\\text{total}} = \\sum_{i=1}^{M} T_{\\text{test}}^{(i)}
```

**Parallelization Speedup:**
```{math}
S = \\frac{T_{\\text{sequential}}}{T_{\\text{parallel}}}
```

### Test Reliability

**Flaky Test Detection:**
```{math}
P(\\text{flaky}) = \\frac{\\text{Inconsistent Results}}{\\text{Total Runs}}
```

**Target:** $P(\\text{flaky}) < 0.01$ (1% flakiness)"""

    def _enhanced_hil_theory(self) -> str:
        return """## Mathematical Foundation

### Enhanced HIL Capabilities

Advanced HIL features beyond basic simulation:

```{math}
\\text{HIL}_{\\text{enhanced}} = \\text{HIL}_{\\text{basic}} + \\mathcal{F}_{\\text{advanced}}
```

Where $\\mathcal{F}_{\\text{advanced}}$ includes parameter variation, disturbance injection, and adaptive testing.

### Parameter Variation Studies

**Systematic Parameter Sweep:**
```{math}
\\mathcal{P} = \\{p_1, p_2, \\ldots, p_n\\} \\times \\{v_1, v_2, \\ldots, v_m\\}
```

**Monte Carlo Sampling:**
```{math}
p_i \\sim \\mathcal{D}_i \\quad \\text{(Distribution for parameter } i\\text{)}
```

### Disturbance Injection

**External Disturbances:**
```{math}
\\dot{\\vec{x}} = f(\\vec{x}, u) + g(\\vec{x}) \\vec{w}(t)
```

Where:
- $g(\\vec{x})$: Disturbance coupling matrix
- $\\vec{w}(t)$: Disturbance signal

**Common Disturbance Types:**
1. **Step**: $w(t) = A \\cdot \\mathbb{1}(t \\geq t_0)$
2. **Ramp**: $w(t) = k \\cdot t$
3. **Sinusoidal**: $w(t) = A \\sin(\\omega t + \\phi)$
4. **Random**: $w(t) \\sim \\mathcal{N}(0, \\sigma^2)$

### Adaptive Testing

**Difficulty Adaptation:**
```{math}
\\text{Difficulty}(n+1) = \\begin{cases}
\\text{Difficulty}(n) + \\Delta & \\text{if PASS} \\\\
\\text{Difficulty}(n) - \\Delta & \\text{if FAIL}
\\end{cases}
```

**Exploration-Exploitation Tradeoff:**
```{math}
\\text{Test}(n) = \\begin{cases}
\\text{Random} & \\text{with probability } \\epsilon \\\\
\\text{Hardest Failed} & \\text{with probability } 1 - \\epsilon
\\end{cases}
```

### Multi-Fidelity Simulation

**Fidelity Levels:**
```{math}
\\mathcal{M} = \\{M_{\\text{low}}, M_{\\text{medium}}, M_{\\text{high}}\\}
```

**Cost-Accuracy Tradeoff:**
```{math}
\\text{Total Cost} = \\sum_{i} C_i \\cdot N_i
```

Subject to accuracy constraint:
```{math}
\\|\\text{Error}_{\\text{total}}\\| < \\epsilon_{\\text{target}}
```

### Performance Profiling

**Execution Time Distribution:**
```{math}
T_{\\text{exec}} \\sim \\mathcal{D}_{\\text{exec}}
```

**Percentile Analysis:**
- P50 (median)
- P95 (tail latency)
- P99 (worst-case)

### Hardware Emulation

**Virtual Hardware Models:**
```{math}
\\text{Virtual Actuator}: u_{\\text{actual}} = h(u_{\\text{cmd}}, \\vec{p}_{\\text{hw}})
```

Where $\\vec{p}_{\\text{hw}}$ includes hardware parameters (bandwidth, saturation, delay).

**Sensor Emulation:**
```{math}
y = C\\vec{x} + \\vec{v}, \\quad \\vec{v} \\sim \\mathcal{N}(0, R)
```"""

    def _hil_package_theory(self) -> str:
        return """## Mathematical Foundation

### HIL Package Architecture

The HIL package provides comprehensive hardware-in-the-loop testing:

```{math}
\\text{HIL System} = (\\text{Server}, \\text{Client}, \\text{Bridge}, \\text{Sync}, \\text{Logging})
```

### System Integration

**Component Interaction:**
```{math}
\\begin{align}
\\text{Server} &\\xrightarrow{\\vec{x}(t)} \\text{Bridge} \\xrightarrow{\\vec{x}(t)} \\text{Client} \\\\
\\text{Client} &\\xrightarrow{u(t)} \\text{Bridge} \\xrightarrow{u(t)} \\text{Server}
\\end{align}
```

### End-to-End Latency

**Total System Latency:**
```{math}
T_{\\text{e2e}} = T_{\\text{server}} + T_{\\text{bridge}} + T_{\\text{network}} + T_{\\text{client}}
```

**Latency Budget:**
- Server: 1 ms (dynamics computation)
- Bridge: 0.5 ms (serialization/routing)
- Network: 5 ms (configurable)
- Client: 2 ms (control computation)
- **Total**: ~8.5 ms per cycle

### Quality of Service

**Reliability Metrics:**
1. **Availability**: $A = \\frac{T_{\\text{uptime}}}{T_{\\text{total}}}$
2. **Packet Loss Rate**: $P_{\\text{loss}} = \\frac{N_{\\text{lost}}}{N_{\\text{sent}}}$
3. **Mean Time Between Failures**: MTBF

**Performance Metrics:**
1. **Throughput**: Messages/second
2. **Latency**: Round-trip time
3. **Jitter**: Variance in latency

### Configuration Management

**System Configuration:**
```{math}
\\mathcal{C}_{\\text{system}} = \\{C_{\\text{server}}, C_{\\text{client}}, C_{\\text{bridge}}, C_{\\text{sync}}\\}
```

**Validation:**
```{math}
\\text{Valid}(\\mathcal{C}) \\Leftrightarrow \\bigwedge_{i} \\text{Constraint}_i(\\mathcal{C})
```

### Usage Patterns

**1. Local HIL Testing:**
- Same machine
- Shared memory or localhost TCP
- Minimal latency

**2. Distributed HIL Testing:**
- Different machines
- Network TCP
- Realistic latency

**3. Hybrid Testing:**
- Some components local, others remote
- Mixed latency profiles"""

    def _generate_diagram_section(self, filename: str) -> str:
        """Generate architecture diagram section based on file type."""
        if filename == 'hil_plant_server.md':
            return self._plant_server_diagram()
        elif filename == 'hil_controller_client.md':
            return self._controller_client_diagram()
        elif filename == 'hil_simulation_bridge.md':
            return self._simulation_bridge_diagram()
        elif filename == 'hil_real_time_sync.md':
            return self._real_time_sync_diagram()
        elif filename == 'hil_fault_injection.md':
            return self._fault_injection_diagram()
        elif filename == 'hil_data_logging.md':
            return self._data_logging_diagram()
        elif filename == 'hil_test_automation.md':
            return self._test_automation_diagram()
        elif filename == 'hil_enhanced_hil.md':
            return self._enhanced_hil_diagram()
        elif filename == 'hil___init__.md':
            return self._hil_package_diagram()
        return ""

    def _plant_server_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
graph TD
    A[TCP Socket Listener] --> B[Accept Connection]
    B --> C[Spawn Server Thread]
    C --> D{Receive Request}
    D --> E[Deserialize Message]
    E --> F[Extract Control Input]
    F --> G[Step Dynamics]
    G --> H[Add Sensor Noise]
    H --> I[Serialize State]
    I --> J[Send Response]
    J --> K{Connection Active?}
    K -->|Yes| D
    K -->|No| L[Cleanup & Exit]

    G --> M[Dynamics Model]
    M --> N[Compute Derivatives]
    N --> O[Integrate Step]
    O --> P[Update State]

    style G fill:#9cf
    style H fill:#ff9
    style M fill:#f9f
    style L fill:#9f9
```

**Data Flow:**
1. Listen for client connections on TCP socket
2. Receive control input from client
3. Step dynamics simulation with control
4. Add configurable sensor noise
5. Send noisy state back to client
6. Repeat until simulation complete"""

    def _controller_client_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
graph TD
    A[Connect to Server] --> B[Initialize Controller]
    B --> C{Simulation Loop}
    C --> D[Request State]
    D --> E[Receive State]
    E --> F[Compute Control]
    F --> G[Send Control]
    G --> H[Log Data]
    H --> I{More Steps?}
    I -->|Yes| C
    I -->|No| J[Disconnect]
    J --> K[Save Results]

    E --> L{Timeout?}
    L -->|Yes| M[Fallback Controller]
    L -->|No| F
    M --> G

    F --> N[Controller Logic]
    N --> O[SMC/MPC/PID]

    style F fill:#9cf
    style M fill:#ff9
    style N fill:#f9f
    style K fill:#9f9
```

**Control Loop:**
1. Request current state from plant server
2. Wait for state response (with timeout)
3. Compute control action using controller
4. Send control input to server
5. Log data for analysis
6. Repeat until simulation complete

**Fault Tolerance:**
- Timeout detection: Switch to fallback PD controller
- Retry logic: 3 attempts with exponential backoff
- Graceful degradation: Save partial results on failure"""

    def _simulation_bridge_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
graph LR
    A[Plant Server] <-->|State| B[Bridge]
    B <-->|Control| A
    B <-->|State| C[Controller Client]
    C <-->|Control| B

    B --> D[Protocol Handler]
    D --> E[TCP Handler]
    D --> F[UDP Handler]
    D --> G[Shared Mem Handler]

    B --> H[State Buffer]
    B --> I[Control Buffer]

    H --> J[Interpolator]
    I --> K[Extrapolator]

    style B fill:#9cf
    style D fill:#ff9
    style J fill:#f9f
```

**Bridge Responsibilities:**
1. **Protocol Translation**: Convert between different transport protocols
2. **State Management**: Buffer and interpolate state data
3. **Timing Coordination**: Synchronize plant and controller clocks
4. **Fault Handling**: Detect timeouts and connection failures
5. **Logging**: Record all messages for debugging"""

    def _real_time_sync_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
sequenceDiagram
    participant P as Plant
    participant S as Sync Manager
    participant C as Controller

    Note over P,C: Synchronization Cycle

    P->>S: Send Timestamp t_p
    C->>S: Send Timestamp t_c
    S->>S: Compute Offset
    S->>P: Adjust Rate
    S->>C: Adjust Rate

    Note over P,C: Execution Cycle

    P->>P: Step Dynamics
    P->>S: Wait at Barrier
    C->>C: Compute Control
    C->>S: Wait at Barrier
    S->>P: Release
    S->>C: Release

    Note over P,C: Metrics Collection

    S->>S: Log Skew
    S->>S: Log Jitter
    S->>S: Check Violations
```

**Synchronization Protocol:**
1. **Clock Sync Phase**: Exchange timestamps and compute offset
2. **Barrier Phase**: Wait for all processes to reach synchronization point
3. **Release Phase**: All processes proceed together
4. **Monitoring Phase**: Track timing metrics and violations"""

    def _fault_injection_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
graph TD
    A[Fault Injection Manager] --> B{Fault Type}
    B -->|Sensor| C[Sensor Fault Injector]
    B -->|Actuator| D[Actuator Fault Injector]
    B -->|Communication| E[Comm Fault Injector]

    C --> F[Add Bias]
    C --> G[Add Noise]
    C --> H[Dropout]
    C --> I[Scaling]

    D --> J[Saturation]
    D --> K[Delay]
    D --> L[Stuck-at]
    D --> M[Degradation]

    E --> N[Packet Loss]
    E --> O[Latency Spike]
    E --> P[Corruption]

    A --> Q[Fault Scheduler]
    Q --> R{Injection Time}
    R -->|Random| S[Poisson Process]
    R -->|Deterministic| T[Scenario-Based]

    style A fill:#9cf
    style Q fill:#ff9
    style B fill:#f9f
```

**Fault Injection Workflow:**
1. **Configure Faults**: Define type, severity, timing
2. **Schedule Injection**: Random or scenario-based
3. **Apply Fault**: Modify sensor/actuator/communication
4. **Monitor Response**: Track detection and recovery
5. **Record Metrics**: Log fault events and system response"""

    def _data_logging_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
graph TD
    A[Simulation Data] --> B{Sampling Strategy}
    B -->|Fixed Rate| C[Fixed Sampler]
    B -->|Event Trigger| D[Event Sampler]
    B -->|Adaptive| E[Adaptive Sampler]

    C --> F[Data Buffer]
    D --> F
    E --> F

    F --> G{Buffer Full?}
    G -->|Yes| H[Flush to Disk]
    G -->|No| F

    H --> I{Format}
    I -->|CSV| J[CSV Writer]
    I -->|HDF5| K[HDF5 Writer]
    I -->|Parquet| L[Parquet Writer]

    J --> M[File Storage]
    K --> M
    L --> M

    M --> N[Replay System]
    N --> O[State Reconstruction]
    N --> P[Control Reconstruction]

    style F fill:#9cf
    style H fill:#ff9
    style M fill:#f9f
```

**Logging Pipeline:**
1. **Data Sampling**: Choose sampling strategy based on requirements
2. **Buffering**: Store data in memory buffer for efficiency
3. **Flushing**: Write to disk when buffer full or timeout
4. **Serialization**: Convert to chosen format (CSV, HDF5, Parquet)
5. **Storage**: Save to disk for later analysis
6. **Replay**: Reconstruct simulation from logged data"""

    def _test_automation_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
graph TD
    A[Test Suite] --> B[Test Generator]
    B --> C{Generation Method}
    C -->|Grid| D[Grid Sampling]
    C -->|Random| E[Latin Hypercube]
    C -->|Boundary| F[Boundary Testing]

    D --> G[Test Case Pool]
    E --> G
    F --> G

    G --> H[Test Executor]
    H --> I[Run HIL Simulation]
    I --> J[Collect Results]
    J --> K{Pass/Fail}

    K -->|Pass| L[Success Log]
    K -->|Fail| M[Failure Analysis]

    M --> N[Debug Report]
    M --> O[Regression Check]

    L --> P[Test Report]
    N --> P
    O --> P

    P --> Q[CI Dashboard]

    style H fill:#9cf
    style K fill:#ff9
    style P fill:#f9f
    style Q fill:#9f9
```

**Automated Testing Workflow:**
1. **Test Generation**: Create test cases using sampling strategies
2. **Test Execution**: Run HIL simulations for each test case
3. **Result Collection**: Gather performance metrics and logs
4. **Pass/Fail Evaluation**: Check against acceptance criteria
5. **Reporting**: Generate comprehensive test report
6. **Integration**: Push results to CI dashboard"""

    def _enhanced_hil_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
graph TD
    A[Enhanced HIL] --> B[Parameter Variation]
    B --> C[Monte Carlo Sampling]
    B --> D[Grid Search]

    A --> E[Disturbance Injection]
    E --> F[Step Disturbance]
    E --> G[Sinusoidal Disturbance]
    E --> H[Random Disturbance]

    A --> I[Adaptive Testing]
    I --> J[Difficulty Adaptation]
    I --> K[Exploration/Exploitation]

    A --> L[Multi-Fidelity]
    L --> M[Low Fidelity Model]
    L --> N[Medium Fidelity Model]
    L --> O[High Fidelity Model]

    C --> P[Test Execution]
    D --> P
    F --> P
    G --> P
    H --> P
    J --> P
    K --> P
    M --> P
    N --> P
    O --> P

    P --> Q[Results Analysis]
    Q --> R[Performance Profiling]
    Q --> S[Robustness Assessment]

    style A fill:#9cf
    style P fill:#ff9
    style Q fill:#f9f
```

**Enhanced Features:**
1. **Parameter Variation**: Systematic exploration of parameter space
2. **Disturbance Injection**: Test robustness under external disturbances
3. **Adaptive Testing**: Dynamically adjust test difficulty
4. **Multi-Fidelity**: Trade accuracy for speed using model hierarchy"""

    def _hil_package_diagram(self) -> str:
        return """## Architecture Diagram

```{mermaid}
graph TB
    subgraph HIL System
        A[Plant Server] <--> B[Simulation Bridge]
        B <--> C[Controller Client]

        D[Real-Time Sync] --> A
        D --> C

        E[Fault Injection] --> A
        E --> C

        F[Data Logging] --> A
        F --> C

        G[Test Automation] --> A
        G --> C

        H[Enhanced HIL] --> A
        H --> C
    end

    I[Configuration Manager] --> A
    I --> B
    I --> C
    I --> D
    I --> E
    I --> F
    I --> G
    I --> H

    J[Results Storage] <-- F
    J <-- G

    style A fill:#9cf
    style C fill:#9cf
    style B fill:#ff9
    style I fill:#f9f
```

**System Components:**
- **Core**: Server, Client, Bridge
- **Timing**: Real-Time Sync
- **Testing**: Fault Injection, Test Automation
- **Logging**: Data Logging
- **Advanced**: Enhanced HIL features
- **Management**: Configuration Manager"""

    def _generate_examples_section(self, filename: str) -> str:
        """Generate usage examples section based on file type."""
        if filename == 'hil_plant_server.md':
            return self._plant_server_examples()
        elif filename == 'hil_controller_client.md':
            return self._controller_client_examples()
        elif filename == 'hil_simulation_bridge.md':
            return self._simulation_bridge_examples()
        elif filename == 'hil_real_time_sync.md':
            return self._real_time_sync_examples()
        elif filename == 'hil_fault_injection.md':
            return self._fault_injection_examples()
        elif filename == 'hil_data_logging.md':
            return self._data_logging_examples()
        elif filename == 'hil_test_automation.md':
            return self._test_automation_examples()
        elif filename == 'hil_enhanced_hil.md':
            return self._enhanced_hil_examples()
        elif filename == 'hil___init__.md':
            return self._hil_package_examples()
        return ""

    def _plant_server_examples(self) -> str:
        return """## Usage Examples

### Example 1: Basic HIL Server Setup

```python
from src.interfaces.hil import PlantServer
from src.config import load_config

# Load configuration
config = load_config("config.yaml")

# Initialize server
server = PlantServer(
    cfg=config,
    bind_addr=("127.0.0.1", 5555),
    dt=0.01,  # 10 ms control period
    extra_latency_ms=5,  # 5 ms network latency
    sensor_noise_std=0.01,  # 1% sensor noise
    max_steps=5000  # 50 seconds simulation
)

# Start server (blocks until client connects)
server.start()

# Server runs until client disconnects or max_steps reached
server.close()
```

### Example 2: Custom Dynamics Configuration

```python
from src.interfaces.hil import PlantServer
from src.plant.models.full import FullDIPDynamics

# Create high-fidelity dynamics model
dynamics = FullDIPDynamics(
    config=config,
    enable_monitoring=True,
    enable_validation=True
)

# Server with custom dynamics
server = PlantServer(
    cfg=config,
    bind_addr=("0.0.0.0", 5555),  # Listen on all interfaces
    dt=0.01
)

# Override dynamics model
server._dynamics = dynamics

server.start()
```

### Example 3: Multi-Client Testing

```python
from threading import Thread
from src.interfaces.hil import PlantServer

def run_server(port, max_steps):
    server = PlantServer(
        cfg=config,
        bind_addr=("127.0.0.1", port),
        dt=0.01,
        max_steps=max_steps
    )
    server.start()
    server.close()

# Run multiple servers for parallel testing
threads = []
for port in [5555, 5556, 5557]:
    t = Thread(target=run_server, args=(port, 5000))
    t.start()
    threads.append(t)

# Wait for all servers to complete
for t in threads:
    t.join()

print("All parallel tests complete")
```

### Example 4: Server with Logging and Monitoring

```python
from src.interfaces.hil import PlantServer
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='hil_server.log'
)

# Server with logging
server = PlantServer(
    cfg=config,
    bind_addr=("127.0.0.1", 5555),
    dt=0.01,
    extra_latency_ms=5,
    sensor_noise_std=0.01
)

# Enable detailed monitoring
logger = logging.getLogger('HIL.PlantServer')
logger.info("Starting HIL plant server...")

try:
    server.start()
except Exception as e:
    logger.error(f"Server error: {e}")
finally:
    server.close()
    logger.info("Server shutdown complete")
```

### Example 5: Performance Profiling

```python
from src.interfaces.hil import PlantServer
import time
import psutil

# Metrics collection
metrics = {
    'step_times': [],
    'memory_usage': [],
    'cpu_usage': []
}

# Custom server with profiling
server = PlantServer(cfg=config, bind_addr=("127.0.0.1", 5555), dt=0.01)

# Override step function for profiling
original_step = server._step
def profiled_step(control):
    start = time.time()
    result = original_step(control)
    metrics['step_times'].append(time.time() - start)
    metrics['memory_usage'].append(psutil.Process().memory_info().rss / 1024**2)
    metrics['cpu_usage'].append(psutil.cpu_percent())
    return result

server._step = profiled_step
server.start()
server.close()

# Analyze performance
print(f"Mean step time: {np.mean(metrics['step_times']):.4f} s")
print(f"Max memory: {max(metrics['memory_usage']):.1f} MB")
print(f"Mean CPU: {np.mean(metrics['cpu_usage']):.1f}%")
```"""

    def _controller_client_examples(self) -> str:
        return """## Usage Examples

### Example 1: Basic Controller Client

```python
from src.interfaces.hil import HILControllerClient
from src.config import load_config

# Load configuration
config = load_config("config.yaml")

# Connect to HIL server
client = HILControllerClient(
    cfg=config,
    plant_addr=("127.0.0.1", 5555),
    bind_addr=("127.0.0.1", 0),  # Auto-assign port
    dt=0.01,
    steps=5000,
    results_path="hil_results.json"
)

# Run HIL simulation
client.run()

print("HIL simulation complete, results saved to hil_results.json")
```

### Example 2: Custom Controller Integration

```python
from src.interfaces.hil import HILControllerClient
from src.controllers import ClassicalSMC

# Create custom controller
controller = ClassicalSMC(
    gains=[10, 8, 15, 12, 50, 5],
    max_force=100.0,
    boundary_layer=0.01
)

# Client with custom controller
client = HILControllerClient(
    cfg=config,
    plant_addr=("192.168.1.100", 5555),  # Remote server
    bind_addr=("0.0.0.0", 6666),
    dt=0.01,
    steps=10000
)

# Override controller
client._controller = controller

# Run simulation
client.run()
```

### Example 3: Fallback Controller Testing

```python
from src.interfaces.hil import HILControllerClient
import time

# Client with aggressive timeout
client = HILControllerClient(
    cfg=config,
    plant_addr=("127.0.0.1", 5555),
    bind_addr=("127.0.0.1", 0),
    dt=0.01,
    steps=5000,
    recv_timeout_s=0.5  # 500 ms timeout
)

# Monitor fallback activations
fallback_count = 0
original_run = client.run

def monitored_run():
    global fallback_count
    # Count timeout events
    try:
        original_run()
    except TimeoutError:
        fallback_count += 1
        print(f"Fallback controller activated: {fallback_count} times")

client.run = monitored_run
client.run()

print(f"Total fallback activations: {fallback_count}")
```

### Example 4: Latency Measurement

```python
from src.interfaces.hil import HILControllerClient
import time

# Latency tracking
latencies = []

# Override communication for measurement
original_send_receive = client._send_receive

def measured_send_receive(msg):
    start = time.time()
    result = original_send_receive(msg)
    latency = (time.time() - start) * 1000  # ms
    latencies.append(latency)
    return result

client._send_receive = measured_send_receive
client.run()

# Analyze latencies
print(f"Mean latency: {np.mean(latencies):.2f} ms")
print(f"P95 latency: {np.percentile(latencies, 95):.2f} ms")
print(f"P99 latency: {np.percentile(latencies, 99):.2f} ms")
```

### Example 5: Robust Client with Retry Logic

```python
from src.interfaces.hil import HILControllerClient
import time

def run_client_with_retry(max_retries=3):
    for attempt in range(max_retries):
        try:
            client = HILControllerClient(
                cfg=config,
                plant_addr=("127.0.0.1", 5555),
                bind_addr=("127.0.0.1", 0),
                dt=0.01,
                steps=5000
            )
            client.run()
            print(f"Success on attempt {attempt + 1}")
            return
        except ConnectionError as e:
            print(f"Connection failed (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

    print("All retry attempts failed")

run_client_with_retry()
```"""

    def _simulation_bridge_examples(self) -> str:
        return """## Usage Examples

### Example 1: Basic Bridge Setup

```python
from src.interfaces.hil.simulation_bridge import SimulationBridge

# Initialize bridge
bridge = SimulationBridge(
    server_addr=("127.0.0.1", 5555),
    client_addr=("127.0.0.1", 6666),
    protocol="tcp"
)

# Start bridge
bridge.start()

# Bridge runs until shutdown
bridge.stop()
```

### Example 2: Protocol Translation

```python
from src.interfaces.hil.simulation_bridge import SimulationBridge

# TCP server, UDP client
bridge = SimulationBridge(
    server_addr=("127.0.0.1", 5555),
    client_addr=("127.0.0.1", 6666),
    server_protocol="tcp",
    client_protocol="udp"
)

bridge.start()
```

### Example 3: State Interpolation

```python
from src.interfaces.hil.simulation_bridge import SimulationBridge
import numpy as np

# Bridge with interpolation
bridge = SimulationBridge(
    server_addr=("127.0.0.1", 5555),
    client_addr=("127.0.0.1", 6666)
)

# Enable state interpolation
bridge.enable_interpolation(method="linear")

# Custom interpolation
def custom_interpolator(state_buffer, t_req):
    # Find surrounding states
    t_prev, x_prev = state_buffer.get_before(t_req)
    t_next, x_next = state_buffer.get_after(t_req)

    # Linear interpolation
    alpha = (t_req - t_prev) / (t_next - t_prev)
    x_interp = x_prev + alpha * (x_next - x_prev)

    return x_interp

bridge.set_interpolator(custom_interpolator)
bridge.start()
```

### Example 4: Fault-Tolerant Bridge

```python
from src.interfaces.hil.simulation_bridge import SimulationBridge
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SimulationBridge')

# Bridge with fault tolerance
bridge = SimulationBridge(
    server_addr=("127.0.0.1", 5555),
    client_addr=("127.0.0.1", 6666),
    heartbeat_interval=1.0,  # 1 second heartbeat
    reconnect_attempts=5
)

# Monitor health
def health_callback(status):
    if status == "TIMEOUT":
        logger.warning("Connection timeout detected")
    elif status == "RECONNECTING":
        logger.info("Attempting reconnection...")
    elif status == "OK":
        logger.info("Connection healthy")

bridge.set_health_callback(health_callback)
bridge.start()
```

### Example 5: Performance Monitoring

```python
from src.interfaces.hil.simulation_bridge import SimulationBridge
import time

# Bridge with metrics
bridge = SimulationBridge(
    server_addr=("127.0.0.1", 5555),
    client_addr=("127.0.0.1", 6666)
)

# Metrics collection
metrics = {
    'throughput': [],
    'latency': [],
    'packet_loss': 0
}

# Override message handler for monitoring
original_forward = bridge._forward_message

def monitored_forward(msg, direction):
    start = time.time()
    try:
        result = original_forward(msg, direction)
        latency = (time.time() - start) * 1000
        metrics['latency'].append(latency)
        return result
    except Exception as e:
        metrics['packet_loss'] += 1
        raise

bridge._forward_message = monitored_forward
bridge.start()

# Report metrics
print(f"Mean latency: {np.mean(metrics['latency']):.2f} ms")
print(f"Packet loss: {metrics['packet_loss']} packets")
```"""

    def _real_time_sync_examples(self) -> str:
        return """## Usage Examples

### Example 1: Basic Synchronization

```python
from src.interfaces.hil.real_time_sync import RealTimeSync

# Initialize synchronizer
sync = RealTimeSync(
    processes=["plant", "controller"],
    target_dt=0.01,  # 10 ms control period
    tolerance=0.001  # 1 ms tolerance
)

# Synchronize processes
sync.synchronize()

# Plant and controller now running at same rate
```

### Example 2: Clock Synchronization

```python
from src.interfaces.hil.real_time_sync import ClockSync

# Create clock synchronizer
clock_sync = ClockSync()

# Client-server clock sync
def client_sync():
    t1 = time.time()
    # Send to server
    t2, t3 = server.get_timestamps()
    t4 = time.time()

    # Compute offset
    offset = clock_sync.compute_offset(t1, t2, t3, t4)
    print(f"Clock offset: {offset * 1000:.2f} ms")

client_sync()
```

### Example 3: Barrier Synchronization

```python
from src.interfaces.hil.real_time_sync import BarrierSync
from threading import Thread

# Create barrier
barrier = BarrierSync(n_processes=2)

def plant_process():
    for step in range(1000):
        # Compute dynamics
        plant.step()
        # Wait for controller
        barrier.wait()

def controller_process():
    for step in range(1000):
        # Compute control
        controller.compute()
        # Wait for plant
        barrier.wait()

# Run synchronized
t1 = Thread(target=plant_process)
t2 = Thread(target=controller_process)
t1.start()
t2.start()
t1.join()
t2.join()
```

### Example 4: Adaptive Rate Synchronization

```python
from src.interfaces.hil.real_time_sync import AdaptiveSync

# Adaptive synchronizer
sync = AdaptiveSync(
    kp=0.1,  # Proportional gain
    target_rate=100.0  # 100 Hz
)

# Plant loop with adaptive timing
plant_time = 0.0
for step in range(10000):
    start = time.time()

    # Step dynamics
    plant.step(dt_adjusted)

    # Measure actual time
    actual_dt = time.time() - start

    # Adjust for next iteration
    dt_adjusted = sync.adjust_rate(actual_dt, step)

    plant_time += dt_adjusted
```

### Example 5: Deadline Monitoring

```python
from src.interfaces.hil.real_time_sync import DeadlineMonitor

# Deadline monitor
monitor = DeadlineMonitor(
    deadline=0.01,  # 10 ms deadline
    tolerance=0.001  # 1 ms tolerance
)

# Control loop with deadline checking
for step in range(5000):
    start = time.time()

    # Compute control
    control = controller.compute(state)

    # Check deadline
    elapsed = time.time() - start
    if not monitor.check_deadline(elapsed):
        print(f"Deadline violation at step {step}: {elapsed*1000:.2f} ms")

# Report violations
print(f"Total violations: {monitor.violation_count}")
print(f"Violation rate: {monitor.violation_rate * 100:.2f}%")
```"""

    def _fault_injection_examples(self) -> str:
        return """## Usage Examples

### Example 1: Sensor Bias Fault

```python
from src.interfaces.hil.fault_injection import FaultInjector, FaultType

# Create fault injector
injector = FaultInjector()

# Add sensor bias fault
injector.add_fault(
    fault_type=FaultType.SENSOR_BIAS,
    target="theta1",  # First pendulum angle
    bias=0.1,  # 0.1 radian bias
    start_time=2.0,  # Start at 2 seconds
    duration=3.0  # Last for 3 seconds
)

# Apply fault during simulation
for t in np.arange(0, 10, 0.01):
    state = plant.get_state()
    faulty_state = injector.apply(state, t)
    control = controller.compute(faulty_state)
```

### Example 2: Actuator Saturation Fault

```python
from src.interfaces.hil.fault_injection import FaultInjector, FaultType

# Actuator fault
injector = FaultInjector()

injector.add_fault(
    fault_type=FaultType.ACTUATOR_SATURATION,
    target="control",
    saturation_min=-50.0,  # Reduced from -100
    saturation_max=50.0,   # Reduced from +100
    start_time=5.0
)

# Simulation with fault
for t in np.arange(0, 10, 0.01):
    state = plant.get_state()
    control = controller.compute(state)
    faulty_control = injector.apply(control, t)
    plant.step(faulty_control)
```

### Example 3: Communication Fault (Packet Loss)

```python
from src.interfaces.hil.fault_injection import FaultInjector, FaultType

# Packet loss fault
injector = FaultInjector()

injector.add_fault(
    fault_type=FaultType.PACKET_LOSS,
    loss_probability=0.2,  # 20% packet loss
    start_time=3.0,
    duration=5.0
)

# HIL with communication faults
for t in np.arange(0, 10, 0.01):
    # Request state from server
    state_msg = client.request_state()

    # Apply packet loss
    if injector.check_packet_loss(t):
        # Use last known state
        state = last_state
    else:
        state = state_msg.state

    control = controller.compute(state)
    client.send_control(control)
    last_state = state
```

### Example 4: Multiple Concurrent Faults

```python
from src.interfaces.hil.fault_injection import FaultInjector

# Multiple faults
injector = FaultInjector()

# Sensor noise
injector.add_fault(
    fault_type=FaultType.SENSOR_NOISE,
    target="theta1",
    noise_std=0.05,
    start_time=0.0
)

# Actuator delay
injector.add_fault(
    fault_type=FaultType.ACTUATOR_DELAY,
    delay_time=0.05,  # 50 ms delay
    start_time=4.0
)

# Communication latency spike
injector.add_fault(
    fault_type=FaultType.LATENCY_SPIKE,
    spike_probability=0.1,
    spike_duration=0.1,
    start_time=2.0
)

# Run with all faults
for t in np.arange(0, 10, 0.01):
    state = plant.get_state()
    faulty_state = injector.apply_all(state, t)
    control = controller.compute(faulty_state)
    faulty_control = injector.apply_all(control, t)
    plant.step(faulty_control)
```

### Example 5: Fault Detection Testing

```python
from src.interfaces.hil.fault_injection import FaultInjector
from src.analysis.fault_detection import FDISystem

# Create fault injector and detector
injector = FaultInjector()
fdi = FDISystem(threshold=0.15)

# Inject sensor bias
injector.add_fault(
    fault_type=FaultType.SENSOR_BIAS,
    target="theta2",
    bias=0.2,
    start_time=5.0
)

# Track detection performance
detection_time = None
false_positives = 0

for t in np.arange(0, 10, 0.01):
    state = plant.get_state()
    faulty_state = injector.apply(state, t)

    # Check fault detection
    fault_detected = fdi.check(faulty_state)

    if fault_detected and detection_time is None and t >= 5.0:
        detection_time = t
        print(f"Fault detected at t={t:.2f}s (actual fault at 5.0s)")

    if fault_detected and t < 5.0:
        false_positives += 1

# Report results
print(f"Detection delay: {detection_time - 5.0:.3f}s")
print(f"False positives: {false_positives}")
```"""

    def _data_logging_examples(self) -> str:
        return """## Usage Examples

### Example 1: Basic CSV Logging

```python
from src.interfaces.hil.data_logging import DataLogger

# Create logger
logger = DataLogger(
    output_path="hil_data.csv",
    format="csv",
    sample_rate=100.0  # 100 Hz
)

# Simulation with logging
for t in np.arange(0, 10, 0.01):
    state = plant.get_state()
    control = controller.compute(state)

    # Log data
    logger.log(time=t, state=state, control=control)

# Close logger
logger.close()
print("Data saved to hil_data.csv")
```

### Example 2: HDF5 High-Performance Logging

```python
from src.interfaces.hil.data_logging import HDF5Logger

# HDF5 logger with compression
logger = HDF5Logger(
    output_path="hil_data.h5",
    compression="gzip",
    compression_opts=9  # Maximum compression
)

# Create datasets
logger.create_dataset("time", dtype=np.float64)
logger.create_dataset("state", shape=(6,), dtype=np.float64)
logger.create_dataset("control", dtype=np.float64)

# Log simulation data
for t in np.arange(0, 10, 0.01):
    state = plant.get_state()
    control = controller.compute(state)

    logger.append("time", t)
    logger.append("state", state)
    logger.append("control", control)

logger.close()
```

### Example 3: Event-Triggered Logging

```python
from src.interfaces.hil.data_logging import EventLogger

# Event-based logger
logger = EventLogger(
    output_path="events.csv",
    threshold=0.1  # Log when state changes > 0.1
)

last_state = None

for t in np.arange(0, 10, 0.01):
    state = plant.get_state()

    # Check if significant change
    if last_state is not None:
        state_change = np.linalg.norm(state - last_state)
        if state_change > logger.threshold:
            logger.log(time=t, state=state)

    last_state = state

logger.close()
print(f"Logged {logger.event_count} events")
```

### Example 4: Multi-Format Logging

```python
from src.interfaces.hil.data_logging import MultiLogger

# Log to multiple formats simultaneously
logger = MultiLogger(
    outputs=[
        ("hil_data.csv", "csv"),
        ("hil_data.h5", "hdf5"),
        ("hil_data.parquet", "parquet")
    ]
)

for t in np.arange(0, 10, 0.01):
    state = plant.get_state()
    control = controller.compute(state)

    # Log to all formats
    logger.log_all(time=t, state=state, control=control)

logger.close_all()
```

### Example 5: Replay from Logged Data

```python
from src.interfaces.hil.data_logging import DataLogger, Replay

# Log data
logger = DataLogger("original.csv", format="csv")
for t in np.arange(0, 10, 0.01):
    state = plant.get_state()
    control = controller.compute(state)
    logger.log(time=t, state=state, control=control)
logger.close()

# Replay simulation
replay = Replay("original.csv")

for entry in replay:
    t = entry["time"]
    state = entry["state"]
    control = entry["control"]

    # Reconstruct dynamics
    reconstructed_state = plant.step(control)

    # Compare original vs reconstructed
    error = np.linalg.norm(state - reconstructed_state)
    if error > 0.01:
        print(f"Reconstruction error at t={t:.2f}: {error:.4f}")

print("Replay complete")
```"""

    def _test_automation_examples(self) -> str:
        return """## Usage Examples

### Example 1: Basic Test Suite

```python
from src.interfaces.hil.test_automation import TestSuite

# Create test suite
suite = TestSuite(name="HIL_Controller_Tests")

# Define test cases
suite.add_test(
    name="stability_test",
    initial_state=[0.0, 0.1, -0.05, 0.0, 0.0, 0.0],
    duration=5.0,
    pass_criteria={"max_angle": 0.2, "settling_time": 3.0}
)

suite.add_test(
    name="disturbance_rejection",
    initial_state=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    disturbance={"type": "step", "magnitude": 10.0, "time": 2.0},
    pass_criteria={"recovery_time": 2.0}
)

# Run all tests
results = suite.run_all()

# Report
suite.print_report()
```

### Example 2: Grid-Based Test Generation

```python
from src.interfaces.hil.test_automation import GridTestGenerator

# Generate test cases on grid
generator = GridTestGenerator()

# Define parameter ranges
theta1_values = np.linspace(-0.2, 0.2, 5)
theta2_values = np.linspace(-0.2, 0.2, 5)

test_cases = generator.generate(
    theta1=theta1_values,
    theta2=theta2_values,
    x=[0.0],  # Fixed cart position
    velocities=[0.0, 0.0, 0.0]  # Zero initial velocity
)

print(f"Generated {len(test_cases)} test cases")

# Run all generated tests
for i, test_case in enumerate(test_cases):
    result = run_hil_simulation(initial_state=test_case)
    print(f"Test {i+1}: {'PASS' if result.stable else 'FAIL'}")
```

### Example 3: Monte Carlo Robustness Testing

```python
from src.interfaces.hil.test_automation import MonteCarloTester

# Monte Carlo test generator
tester = MonteCarloTester(n_trials=100)

# Define parameter distributions
tester.set_distribution(
    "theta1", distribution="normal", mean=0.0, std=0.1
)
tester.set_distribution(
    "theta2", distribution="normal", mean=0.0, std=0.1
)
tester.set_distribution(
    "noise", distribution="uniform", low=0.0, high=0.05
)

# Run Monte Carlo tests
results = tester.run()

# Analyze results
success_rate = sum(r.passed for r in results) / len(results)
print(f"Success rate: {success_rate * 100:.1f}%")
```

### Example 4: Continuous Integration Testing

```python
from src.interfaces.hil.test_automation import CITestRunner

# CI test runner
ci_runner = CITestRunner(
    test_suite_path="tests/hil_tests.yaml",
    report_path="ci_report.json"
)

# Run tests
results = ci_runner.run()

# Check for regressions
if results.has_regressions():
    print("REGRESSION DETECTED!")
    for test in results.regressions:
        print(f"  {test.name}: {test.baseline_time:.2f}s -> {test.current_time:.2f}s")
    exit(1)

print("All tests passed, no regressions")
exit(0)
```

### Example 5: Adaptive Test Difficulty

```python
from src.interfaces.hil.test_automation import AdaptiveTester

# Adaptive tester
tester = AdaptiveTester(
    initial_difficulty=0.5,
    adjustment_rate=0.1
)

# Run adaptive tests
for i in range(20):
    test_case = tester.generate_test()
    result = run_hil_simulation(test_case)

    # Adjust difficulty based on result
    tester.update(result.passed)

    print(f"Test {i+1}: difficulty={tester.current_difficulty:.2f}, "
          f"result={'PASS' if result.passed else 'FAIL'}")

# Report final difficulty
print(f"Final difficulty: {tester.current_difficulty:.2f}")
```"""

    def _enhanced_hil_examples(self) -> str:
        return """## Usage Examples

### Example 1: Parameter Variation Study

```python
from src.interfaces.hil.enhanced_hil import ParameterSweep

# Parameter sweep
sweep = ParameterSweep()

# Define parameter ranges
sweep.add_parameter("mass_cart", values=np.linspace(0.8, 1.2, 5))
sweep.add_parameter("length_1", values=np.linspace(0.3, 0.5, 5))

# Run sweep
results = sweep.run()

# Analyze sensitivity
for param, result in results.items():
    print(f"{param}: sensitivity = {result.sensitivity:.4f}")
```

### Example 2: Disturbance Injection

```python
from src.interfaces.hil.enhanced_hil import DisturbanceInjector

# Create disturbance injector
injector = DisturbanceInjector()

# Add sinusoidal disturbance
injector.add_disturbance(
    type="sinusoidal",
    amplitude=5.0,
    frequency=1.0,
    start_time=2.0
)

# Simulate with disturbance
for t in np.arange(0, 10, 0.01):
    state = plant.get_state()
    control = controller.compute(state)

    # Add disturbance
    disturbed_control = injector.apply(control, t)

    plant.step(disturbed_control)
```

### Example 3: Multi-Fidelity Simulation

```python
from src.interfaces.hil.enhanced_hil import MultiFidelitySimulator

# Multi-fidelity simulator
simulator = MultiFidelitySimulator()

# Define fidelity levels
simulator.add_model("low", SimplifiedDynamics())
simulator.add_model("medium", FullDynamics(accuracy="medium"))
simulator.add_model("high", FullDynamics(accuracy="high"))

# Run with adaptive fidelity
result = simulator.run_adaptive(
    initial_fidelity="low",
    accuracy_target=1e-3,
    max_cost=100.0
)

print(f"Final fidelity: {result.final_fidelity}")
print(f"Total cost: {result.total_cost:.1f}")
print(f"Accuracy achieved: {result.accuracy:.6f}")
```

### Example 4: Hardware Emulation

```python
from src.interfaces.hil.enhanced_hil import HardwareEmulator

# Hardware emulator
emulator = HardwareEmulator()

# Configure actuator model
emulator.set_actuator_model(
    bandwidth=50.0,  # 50 Hz bandwidth
    saturation=100.0,
    delay=0.01  # 10 ms delay
)

# Configure sensor model
emulator.set_sensor_model(
    noise_std=0.01,
    bias=0.005,
    dropout_rate=0.01
)

# Simulate with hardware emulation
for t in np.arange(0, 10, 0.01):
    state = plant.get_state()

    # Emulate sensor
    measured_state = emulator.sensor(state)

    # Compute control
    control = controller.compute(measured_state)

    # Emulate actuator
    actual_control = emulator.actuator(control)

    plant.step(actual_control)
```

### Example 5: Performance Profiling

```python
from src.interfaces.hil.enhanced_hil import PerformanceProfiler

# Performance profiler
profiler = PerformanceProfiler()

# Profile simulation
profiler.start()

for t in np.arange(0, 10, 0.01):
    with profiler.section("dynamics"):
        state = plant.get_state()

    with profiler.section("control"):
        control = controller.compute(state)

    with profiler.section("communication"):
        client.send_control(control)

profiler.stop()

# Report profiling results
report = profiler.generate_report()
print(report.to_string())

# Identify bottlenecks
for section, time in report.sorted_sections():
    print(f"{section}: {time:.2f} ms ({report.percentage(section):.1f}%)")
```"""

    def _hil_package_examples(self) -> str:
        return """## Usage Examples

### Example 1: Complete HIL Setup

```python
from src.interfaces import hil

# Complete HIL system setup
config = hil.load_config("config.yaml")

# Start plant server
server = hil.PlantServer(
    cfg=config,
    bind_addr=("127.0.0.1", 5555),
    dt=0.01
)

# Start controller client
client = hil.HILControllerClient(
    cfg=config,
    plant_addr=("127.0.0.1", 5555),
    bind_addr=("127.0.0.1", 0),
    dt=0.01,
    steps=5000
)

# Run HIL simulation
server.start()  # Blocks until client connects
```

### Example 2: Distributed HIL Testing

```python
from src.interfaces import hil
from threading import Thread

# Server on one thread
def run_server():
    server = hil.PlantServer(
        cfg=config,
        bind_addr=("0.0.0.0", 5555),
        dt=0.01
    )
    server.start()

# Client on another thread
def run_client():
    time.sleep(1.0)  # Wait for server to start
    client = hil.HILControllerClient(
        cfg=config,
        plant_addr=("127.0.0.1", 5555),
        bind_addr=("127.0.0.1", 0),
        dt=0.01,
        steps=5000
    )
    client.run()

# Run distributed
t1 = Thread(target=run_server)
t2 = Thread(target=run_client)
t1.start()
t2.start()
t1.join()
t2.join()
```

### Example 3: HIL with Fault Injection

```python
from src.interfaces import hil

# Setup with fault injection
server = hil.PlantServer(cfg=config, bind_addr=("127.0.0.1", 5555), dt=0.01)

# Add fault injector
injector = hil.FaultInjector()
injector.add_fault(
    fault_type=hil.FaultType.SENSOR_BIAS,
    target="theta1",
    bias=0.1,
    start_time=5.0
)

# Attach to server
server.set_fault_injector(injector)

server.start()
```

### Example 4: HIL with Data Logging

```python
from src.interfaces import hil

# Setup with logging
server = hil.PlantServer(cfg=config, bind_addr=("127.0.0.1", 5555), dt=0.01)
client = hil.HILControllerClient(
    cfg=config,
    plant_addr=("127.0.0.1", 5555),
    bind_addr=("127.0.0.1", 0),
    dt=0.01,
    steps=5000
)

# Add logger
logger = hil.DataLogger("hil_results.h5", format="hdf5")

# Attach to client
client.set_logger(logger)

# Run with logging
server.start()
```

### Example 5: Automated HIL Test Suite

```python
from src.interfaces import hil

# Create test suite
suite = hil.TestSuite(name="Controller_Validation")

# Add test cases
suite.add_test(
    name="stability",
    initial_state=[0.0, 0.1, -0.05, 0.0, 0.0, 0.0],
    pass_criteria={"settling_time": 3.0}
)

suite.add_test(
    name="robustness",
    initial_state=[0.0, 0.2, -0.1, 0.0, 0.0, 0.0],
    disturbance={"type": "step", "magnitude": 10.0},
    pass_criteria={"recovery_time": 2.0}
)

# Run all tests
results = suite.run_all()

# Generate report
suite.save_report("test_report.json")
print(f"Tests passed: {results.pass_count}/{results.total_count}")
```"""

    def _print_summary(self):
        """Print enhancement summary."""
        print("\n" + "="*80)
        print("Enhancement Summary")
        print("="*80)
        print(f"Files enhanced: {self.stats.files_enhanced}")
        print(f"Total lines added: {self.stats.lines_added}")

        if self.stats.errors:
            print(f"\nErrors ({len(self.stats.errors)}):")
            for error in self.stats.errors:
                print(f"  - {error}")
        else:
            print("\n✅ All files enhanced successfully!")

        print("="*80)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Enhance HIL documentation for Week 7 Phase 2")
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no files written)')
    args = parser.parse_args()

    # Paths
    docs_root = Path(__file__).parent.parent.parent / 'docs'

    # Run enhancement
    enhancer = HILDocEnhancer(docs_root, dry_run=args.dry_run)
    enhancer.enhance_all_files()


if __name__ == '__main__':
    main()
