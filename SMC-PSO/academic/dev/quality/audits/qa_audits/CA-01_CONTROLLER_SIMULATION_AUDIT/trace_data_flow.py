"""
CA-01 Audit Phase 2: Data Flow Tracing Script

Traces data flow through the complete Controller Factory -> Simulation Runner pipeline.
Generates detailed logs and flow diagrams for all 4 controller types.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
from src.controllers.factory.smc_factory import SMCFactory, SMCType
from src.simulation.engines.simulation_runner import run_simulation
from src.plant.models.lowrank.dynamics import LowRankDIPDynamics
from src.plant.models.lowrank.config import LowRankDIPConfig


class DataFlowTracer:
    """Traces data flow through controller-simulation integration."""

    def __init__(self):
        self.trace_log = []
        self.current_step = 0

    def log(self, stage: str, component: str, data_type: str, data_value: Any, metadata: Dict[str, Any] = None):
        """Log a data flow event."""
        entry = {
            'step': self.current_step,
            'timestamp': datetime.now().isoformat(),
            'stage': stage,
            'component': component,
            'data_type': data_type,
            'data_value': self._serialize_value(data_value),
            'metadata': metadata or {}
        }
        self.trace_log.append(entry)

    def _serialize_value(self, value: Any) -> Any:
        """Serialize value for JSON output."""
        if isinstance(value, np.ndarray):
            return {
                'type': 'ndarray',
                'shape': value.shape,
                'dtype': str(value.dtype),
                'value': value.tolist() if value.size < 20 else f"array({value.shape})"
            }
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(v) for v in value]
        elif hasattr(value, '__dict__') and not callable(value):
            # Namedtuple or dataclass
            return {
                'type': type(value).__name__,
                'attributes': {k: self._serialize_value(v) for k, v in value.__dict__.items() if not k.startswith('_')}
            }
        elif isinstance(value, (int, float, bool, str, type(None))):
            return value
        else:
            return str(value)

    def generate_flow_diagram(self) -> str:
        """Generate ASCII flow diagram from trace log."""
        diagram = []
        diagram.append("=" * 80)
        diagram.append("DATA FLOW DIAGRAM: Controller Factory -> Simulation Runner")
        diagram.append("=" * 80)
        diagram.append("")

        stages = {}
        for entry in self.trace_log:
            stage = entry['stage']
            if stage not in stages:
                stages[stage] = []
            stages[stage].append(entry)

        stage_order = ['factory_create', 'controller_init', 'simulation_setup',
                       'control_loop', 'dynamics_step', 'output']

        for stage in stage_order:
            if stage in stages:
                diagram.append(f"\n[{stage.upper()}]")
                diagram.append("-" * 80)
                for entry in stages[stage]:
                    diagram.append(f"  {entry['component']}: {entry['data_type']}")
                    if isinstance(entry['data_value'], dict) and 'type' in entry['data_value']:
                        diagram.append(f"    -> {entry['data_value']}")
                    metadata_str = ", ".join(f"{k}={v}" for k, v in entry['metadata'].items())
                    if metadata_str:
                        diagram.append(f"    ({metadata_str})")

        diagram.append("\n" + "=" * 80)
        return "\n".join(diagram)


def trace_controller_creation(controller_type: str, tracer: DataFlowTracer):
    """Trace controller creation through factory."""
    print(f"\n[TRACING] Controller creation: {controller_type}")

    tracer.log('factory_create', 'SMCFactory', 'controller_type', controller_type,
               {'operation': 'create_from_gains'})

    gains = [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
    tracer.log('factory_create', 'SMCFactory', 'gains', gains,
               {'n_gains': len(gains)})

    # Create controller
    controller = SMCFactory.create_from_gains(controller_type, gains=gains)

    tracer.log('factory_create', 'SMCFactory', 'controller_instance', type(controller).__name__,
               {'has_compute_control': hasattr(controller, 'compute_control'),
                'has_max_force': hasattr(controller, 'max_force')})

    return controller


def trace_controller_initialization(controller: Any, tracer: DataFlowTracer):
    """Trace controller state and history initialization."""
    print("[TRACING] Controller initialization")

    # Initialize state_vars
    state_vars = controller.initialize_state()
    tracer.log('controller_init', type(controller).__name__, 'state_vars', state_vars,
               {'state_vars_type': type(state_vars).__name__})

    # Initialize history
    history = controller.initialize_history()
    tracer.log('controller_init', type(controller).__name__, 'history', history,
               {'history_type': type(history).__name__,
                'history_keys': list(history.keys()) if isinstance(history, dict) else None})

    return state_vars, history


def trace_simulation_setup(tracer: DataFlowTracer):
    """Trace simulation runner setup."""
    print("[TRACING] Simulation setup")

    # Create dynamics
    config = LowRankDIPConfig()
    dynamics = LowRankDIPDynamics(config=config)

    tracer.log('simulation_setup', 'LowRankDIPDynamics', 'config', type(config).__name__,
               {'config_type': 'LowRankDIPConfig'})

    # Initial state
    initial_state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])
    tracer.log('simulation_setup', 'SimulationRunner', 'initial_state', initial_state,
               {'state_dim': len(initial_state)})

    # Simulation parameters
    sim_params = {'sim_time': 0.1, 'dt': 0.01}  # Short simulation for tracing
    tracer.log('simulation_setup', 'SimulationRunner', 'sim_params', sim_params)

    return dynamics, initial_state, sim_params


def trace_control_loop(controller: Any, dynamics: Any, initial_state: np.ndarray,
                       sim_params: Dict[str, float], tracer: DataFlowTracer):
    """Trace control loop execution with detailed logging."""
    print("[TRACING] Control loop execution")

    # Initialize controller
    state_vars = controller.initialize_state()
    history = controller.initialize_history()

    # Trace first 3 steps manually for detailed inspection
    dt = sim_params['dt']
    state = initial_state.copy()

    for i in range(3):
        tracer.current_step = i
        print(f"  Step {i}:")

        # Compute control
        tracer.log('control_loop', 'Controller', 'state_input', state,
                   {'step': i})

        control_output = controller.compute_control(state, state_vars, history)

        tracer.log('control_loop', 'Controller', 'control_output', control_output,
                   {'output_type': type(control_output).__name__})

        # Extract control value
        if hasattr(control_output, 'u'):
            u_val = control_output.u
        elif isinstance(control_output, tuple):
            u_val = control_output[0]
            if len(control_output) >= 2:
                state_vars = control_output[1]
            if len(control_output) >= 3:
                history = control_output[2]
        else:
            u_val = float(control_output)

        tracer.log('control_loop', 'Controller', 'control_value', u_val,
                   {'step': i, 'units': 'N'})

        # Dynamics step
        state_next = dynamics.step(state, u_val, dt)

        tracer.log('dynamics_step', 'Dynamics', 'state_output', state_next,
                   {'step': i, 'is_finite': bool(np.all(np.isfinite(state_next)))})

        state = state_next

    # Run full simulation
    t, x, u = run_simulation(
        controller=controller,
        dynamics_model=dynamics,
        sim_time=sim_params['sim_time'],
        dt=sim_params['dt'],
        initial_state=initial_state
    )

    tracer.log('output', 'SimulationRunner', 'time_array', t,
               {'length': len(t)})
    tracer.log('output', 'SimulationRunner', 'state_trajectory', x,
               {'shape': x.shape})
    tracer.log('output', 'SimulationRunner', 'control_trajectory', u,
               {'shape': u.shape, 'rms': float(np.sqrt(np.mean(u**2)))})

    return t, x, u


def trace_single_controller(controller_type: str) -> Dict[str, Any]:
    """Trace complete data flow for a single controller type."""
    print("=" * 80)
    print(f"TRACING: {controller_type}")
    print("=" * 80)

    tracer = DataFlowTracer()

    try:
        # 1. Factory creation
        controller = trace_controller_creation(controller_type, tracer)

        # 2. Controller initialization
        state_vars, history = trace_controller_initialization(controller, tracer)

        # 3. Simulation setup
        dynamics, initial_state, sim_params = trace_simulation_setup(tracer)

        # 4. Control loop
        t, x, u = trace_control_loop(controller, dynamics, initial_state, sim_params, tracer)

        # 5. Generate flow diagram
        flow_diagram = tracer.generate_flow_diagram()

        print("\n[OK] Tracing complete")

        return {
            'status': 'SUCCESS',
            'controller_type': controller_type,
            'trace_log': tracer.trace_log,
            'flow_diagram': flow_diagram,
            'summary': {
                'total_events': len(tracer.trace_log),
                'simulation_steps': len(t),
                'control_effort_rms': float(np.sqrt(np.mean(u**2))),
                'final_state_norm': float(np.linalg.norm(x[-1]))
            }
        }

    except Exception as e:
        print(f"\n[ERROR] Tracing failed: {e}")
        return {
            'status': 'FAILED',
            'controller_type': controller_type,
            'error': str(e),
            'trace_log': tracer.trace_log
        }


def main():
    """Main tracing execution."""
    print("[INFO] CA-01 Phase 2 Task 2.1: Data Flow Tracing")
    print("=" * 80)

    results = {}

    # Trace all 4 controller types
    for ctrl_type in SMCType:
        result = trace_single_controller(ctrl_type.value)
        results[ctrl_type.value] = result

        # Save individual flow diagram
        if result['status'] == 'SUCCESS':
            output_dir = Path(__file__).parent / 'flow_diagrams'
            output_dir.mkdir(exist_ok=True)
            diagram_file = output_dir / f"{ctrl_type.value}_flow.txt"
            with open(diagram_file, 'w') as f:
                f.write(result['flow_diagram'])
            print(f"[INFO] Flow diagram saved: {diagram_file}")

    # Save complete trace results
    output_file = Path(__file__).parent / 'data_flow_trace_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n[INFO] Complete trace results saved: {output_file}")

    # Summary
    successes = sum(1 for r in results.values() if r['status'] == 'SUCCESS')
    print(f"\n[SUMMARY] {successes}/{len(results)} controller types traced successfully")

    # Generate combined flow comparison
    generate_combined_flow_comparison(results)

    return results


def generate_combined_flow_comparison(results: Dict[str, Any]):
    """Generate combined flow comparison across all controllers."""
    output_dir = Path(__file__).parent
    comparison_file = output_dir / 'flow_comparison.txt'

    with open(comparison_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("DATA FLOW COMPARISON: All 4 SMC Controllers\n")
        f.write("=" * 80 + "\n\n")

        for ctrl_type, result in results.items():
            if result['status'] == 'SUCCESS':
                f.write(f"\n{ctrl_type.upper()}\n")
                f.write("-" * 80 + "\n")
                summary = result['summary']
                f.write(f"  Total events: {summary['total_events']}\n")
                f.write(f"  Simulation steps: {summary['simulation_steps']}\n")
                f.write(f"  Control effort (RMS): {summary['control_effort_rms']:.4f} N\n")
                f.write(f"  Final state norm: {summary['final_state_norm']:.4f}\n")

        f.write("\n" + "=" * 80 + "\n")

    print(f"[INFO] Flow comparison saved: {comparison_file}")


if __name__ == '__main__':
    main()
