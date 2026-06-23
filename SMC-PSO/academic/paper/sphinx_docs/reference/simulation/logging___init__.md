# simulation.logging.__init__

**Source:** `src\simulation\logging\__init__.py`

## Module Overview Data

logging and recording for simulation framework

.


This module provides logging features for simulation data,
performance metrics, and real-time recording for analysis and debugging. ## Complete Source Code ```{literalinclude} ../../../src/simulation/logging/__init__.py
:language: python
:linenos:
```

---

## Advanced Mathematical Theory

### Structured Logging Theory

Structured logging provides data recording for simulation analysis and debugging.

#### Log Level Hierarchy $$
\text{Level} = \{\text{DEBUG} < \text{INFO} < \text{WARNING} < \text{ERROR} < \text{CRITICAL}\}
$$ **Filtering rule:**
$$
\text{Record}(\text{msg}) = \begin{cases}
\text{True} & \text{if } \text{msg.level} \geq \text{threshold} \\
\text{False} & \text{otherwise}
\end{cases}
$$ #### Ring Buffer Implementation **Circular buffer** for memory-bounded logging: $$
\text{index}(k) = k \mod N
$$ **Write operation:**
$$
\text{buffer}[k \mod N] = \text{log}\_\text{entry}_k
$$ **Capacity:** Fixed at $N$ entries, overwrites oldest when full. #### Log Rotation Policy **Size-based rotation:**
$$
\text{Rotate} = \begin{cases}
\text{True} & \text{if } \text{file\_size} \geq \text{max\_size} \\
\text{False} & \text{otherwise}
\end{cases}
$$ **Time-based rotation:**
$$
\text{Rotate} = (t_{\text{current}} - t_{\text{created}} \geq T_{\text{rotation}})
$$ #### Performance Tracing **Execution time measurement:**
$$
t_{\text{exec}} = t_{\text{end}} - t_{\text{start}}
$$ **Overhead ratio:**
$$
\text{Overhead} = \frac{t_{\text{logging}}}{t_{\text{total}}} < \epsilon_{\text{max}}
$$ Target: $\epsilon_{\text{max}} < 0.01$ (1% overhead) ## Architecture Diagram \`\`\`{mermaid}
graph TD A[Logging System] --> B[Structured Logger] A --> C[Performance Tracer] A --> D[Ring Buffer] A --> E[Log Rotator] B --> F{Log Level Filter} F -->|Level ≥ threshold| G[Format Message] F -->|Level < threshold| H[Discard] G --> I[Write to Buffer] I --> D D --> J{Buffer Full?} J -->|Yes| K[Overwrite Oldest] J -->|No| L[Append] C --> M[Start Timer] M --> N[Trace Event] N --> O[End Timer] O --> P[Log Performance] E --> Q{Rotation Trigger?} Q -->|Size| R[Size-based Rotation] Q -->|Time| S[Time-based Rotation] R --> T[Create New File] S --> T T --> U[Archive Old Log] style F fill:#fff4e1 style J fill:#fff4e1 style T fill:#e8f5e9
\`\`\` ## Usage Examples ### Example 1: Basic Structured Logging \`\`\`python
from src.simulation.logging import StructuredLogger # Create structured logger
logger = StructuredLogger( name='simulation', level='INFO', format='json' # or 'text'
) # Log simulation events
logger.info('Simulation started', extra={ 'controller_type': 'classical_smc', 'duration': 10.0, 'dt': 0.01
}) logger.debug('Control computed', extra={ 'step': 100, 'state': x.tolist(), 'control': u.tolist()
}) logger.warning('High control effort', extra={ 'control_magnitude': float(np.linalg.norm(u)), 'saturation': 0.95
}) logger.info('Simulation completed', extra={ 'final_state': x_final.tolist(), 'num_steps': 1000
})
\`\`\` ### Example 2: Performance Tracing \`\`\`python
from src.simulation.logging import PerformanceTracer # Create performance tracer
tracer = PerformanceTracer(overhead_limit=0.01) # 1% max overhead # Trace simulation loop
for k in range(num_steps): with tracer.trace('control_computation'): u = controller.compute_control(x, state_vars, history) with tracer.trace('integration'): x = integrator.integrate(dynamics.compute_dynamics, x, u, t) t += dt # Get performance statistics
stats = tracer.get_statistics() for operation, op_stats in stats.items(): print(f"{operation}:") print(f" Mean: {op_stats['mean']:.6f}s") print(f" 95th percentile: {op_stats['p95']:.6f}s") print(f" Total time: {op_stats['total']:.4f}s") print(f" Overhead: {op_stats['overhead']:.2%}")
\`\`\` ### Example 3: Ring Buffer Logging \`\`\`python
from src.simulation.logging import RingBufferLogger # Create memory-bounded logger
logger = RingBufferLogger(capacity=1000) # Log in memory (circular buffer)
for k in range(10000): logger.log({ 'step': k, 'time': k * 0.01, 'state': x[k].tolist(), 'control': u[k].tolist() }) # Only last 1000 entries are kept
recent_logs = logger.get_logs(last_n=100)
print(f"Retrieved {len(recent_logs)} most recent log entries") # Dump to file when needed
logger.dump_to_file('simulation_log.json')
\`\`\` ### Example 4: Log Rotation \`\`\`python
from src.simulation.logging import RotatingFileLogger # Create logger with rotation
logger = RotatingFileLogger( filename='simulation.log', max_size_mb=10, # Rotate at 10 MB max_files=5, # Keep 5 backup files rotation_policy='size' # or 'time'
) # Long-running simulation
for trial in range(1000): logger.info(f'Trial {trial} started') result = run_simulation() logger.info(f'Trial {trial} completed', extra={'result': result.to_dict()}) # Logs automatically rotate: simulation.log, simulation.log.1, ..., simulation.log.5
print(f"Log files: {logger.get_log_files()}")
\`\`\` ### Example 5: Integrated Logging Pipeline \`\`\`python
from src.simulation.logging import ( StructuredLogger, PerformanceTracer, RingBufferLogger
) class SimulationWithLogging: def __init__(self): # Multiple logging strategies self.logger = StructuredLogger(name='sim', level='INFO') self.tracer = PerformanceTracer() self.debug_buffer = RingBufferLogger(capacity=100) def run_simulation(self, controller, dynamics, duration, dt): self.logger.info('Simulation started', extra={'duration': duration}) x = initial_state t = 0.0 while t < duration: # Performance tracing with self.tracer.trace('step'): # Control computation with debug logging self.debug_buffer.log({'step': int(t/dt), 'state': x.tolist()}) u = controller.compute_control(x, state_vars, history) x = integrator.integrate(dynamics.compute_dynamics, x, u, t) t += dt # Summary logging perf_stats = self.tracer.get_statistics() self.logger.info('Simulation completed', extra={ 'mean_step_time': perf_stats['step']['mean'], 'overhead': perf_stats['step']['overhead'] }) return x # Use integrated logging
sim = SimulationWithLogging()
result = sim.run_simulation(controller, dynamics, 10.0, 0.01)
\`\`\` ## Architecture Diagram \`\`\`{mermaid}
graph TD A[Component] --> B[Subcomponent 1] A --> C[Subcomponent 2] B --> D[Output] C --> D style A fill:#e1f5ff style D fill:#e8f5e9
\`\`\` ## Usage Examples ### Example 1: Basic Usage \`\`\`python
# Basic usage example
from src.simulation.logging import Component component = Component()
result = component.process(data)
\`\`\` ### Example 2: Advanced Configuration \`\`\`python
# Advanced configuration
component = Component( option1=value1, option2=value2
)
\`\`\` ### Example 3: Integration with Framework \`\`\`python
# Integration example
from src.simulation import SimulationRunner runner = SimulationRunner()
runner.use_component(component)
\`\`\` ### Example 4: Performance Optimization \`\`\`python
# Performance-optimized usage
component = Component(enable_caching=True)
\`\`\` ### Example 5: Error Handling \`\`\`python
# Error handling
try: result = component.process(data)
except ComponentError as e: print(f"Error: {e}")
\`\`\` 
