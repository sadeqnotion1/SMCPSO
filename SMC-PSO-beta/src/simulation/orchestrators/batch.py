#======================================================================================
#======================= src/simulation/orchestrators/batch.py ========================
#======================================================================================

"""Batch simulation orchestrator for vectorized execution."""

from __future__ import annotations

import time
import logging
from typing import Callable, Optional
import numpy as np

from .base import BaseOrchestrator
from ..core.interfaces import ResultContainer
from ..results.containers import BatchResultContainer


class BatchOrchestrator(BaseOrchestrator):
    """Batch simulation orchestrator for vectorized execution.

    This orchestrator can execute multiple simulations simultaneously
    using vectorized operations, providing significant performance improvements
    for Monte Carlo analysis and parameter sweeps.
    """

    def execute(self,
               initial_state: np.ndarray,
               control_inputs: np.ndarray,
               dt: float,
               horizon: int,
               **kwargs) -> ResultContainer:
        """Execute batch simulation.

        Parameters
        ----------
        initial_state : np.ndarray
            Initial state(s) - shape (state_dim,) or (batch_size, state_dim)
        control_inputs : np.ndarray
            Control input sequence - shape (horizon,), (horizon, m), or (batch_size, horizon, m)
        dt : float
            Time step
        horizon : int
            Simulation horizon
        **kwargs
            Additional options

        Returns
        -------
        ResultContainer
            Batch simulation results
        """
        self._validate_simulation_inputs(initial_state, control_inputs, dt, horizon)

        start_time = time.perf_counter()

        # Determine batch size and normalize arrays
        initial_state = np.atleast_2d(initial_state)
        if initial_state.shape[0] == 1:
            batch_size = 1
            state_dim = initial_state.shape[1]
        else:
            batch_size = initial_state.shape[0]
            state_dim = initial_state.shape[1]

        # Normalize control inputs
        control_inputs = self._normalize_control_inputs(control_inputs, batch_size, horizon)

        # Extract options
        safety_guards = kwargs.get("safety_guards", True)
        stop_fn = kwargs.get("stop_fn", None)
        t0 = kwargs.get("t0", 0.0)

        # Prepare result arrays
        times = np.linspace(t0, t0 + horizon * dt, horizon + 1)
        states = np.zeros((batch_size, horizon + 1, state_dim))
        controls = np.zeros((batch_size, horizon))

        # Set initial states
        states[:, 0, :] = initial_state

        # Track which simulations are still active
        active_mask = np.ones(batch_size, dtype=bool)
        current_states = initial_state.copy()

        # Main simulation loop
        for i in range(horizon):
            if not np.any(active_mask):
                break

            # Get control inputs for this step
            if control_inputs.ndim == 3:
                step_controls = control_inputs[:, i, :]
            else:
                step_controls = control_inputs[:, i:i+1]

            controls[:, i] = step_controls.flat[:batch_size]

            # Apply stop condition
            if stop_fn is not None:
                for b in range(batch_size):
                    if active_mask[b] and stop_fn(current_states[b]):
                        active_mask[b] = False

            # Apply safety guards if enabled
            if safety_guards:
                for b in range(batch_size):
                    if active_mask[b]:
                        try:
                            from ..safety.guards import apply_safety_guards
                            apply_safety_guards(current_states[b], i, self.config)
                        except Exception:
                            active_mask[b] = False

            # Vectorized simulation step for active simulations
            next_states = current_states.copy()

            for b in range(batch_size):
                if active_mask[b]:
                    try:
                        control = step_controls[b] if step_controls.ndim > 1 else step_controls[b:b+1]
                        next_state = self.step(current_states[b], control, dt, t=times[i])

                        if np.isfinite(next_state).all():
                            next_states[b] = next_state
                            states[b, i+1, :] = next_state
                        else:
                            active_mask[b] = False

                    except Exception:
                        active_mask[b] = False

            current_states = next_states

        # Update statistics
        execution_time = time.perf_counter() - start_time
        total_steps = batch_size * horizon
        self._update_stats(total_steps, execution_time)

        # Create batch result container
        result = BatchResultContainer()
        for b in range(batch_size):
            # Find last valid step for this trajectory
            last_step = horizon
            for step in range(horizon, 0, -1):
                if np.isfinite(states[b, step, :]).all():
                    last_step = step
                    break

            batch_times = times[:last_step+1]
            batch_states = states[b, :last_step+1, :]
            batch_controls = controls[b, :last_step]

            result.add_trajectory(batch_states, batch_times,
                                controls=batch_controls, batch_index=b)

        return result

    def _normalize_control_inputs(self,
                                control_inputs: np.ndarray,
                                batch_size: int,
                                horizon: int) -> np.ndarray:
        """Normalize control inputs to consistent batch format."""
        control_inputs = np.atleast_2d(control_inputs)

        if control_inputs.shape[0] == horizon:
            # Shape (horizon, m) - broadcast to all batch elements
            if control_inputs.ndim == 2:
                # Expand to (batch_size, horizon, m)
                return np.tile(control_inputs[None, :, :], (batch_size, 1, 1))
            else:
                # Expand to (batch_size, horizon)
                return np.tile(control_inputs[None, :], (batch_size, 1))

        elif control_inputs.shape[0] == batch_size:
            # Already in batch format
            return control_inputs

        else:
            # Single control value - broadcast to all
            control_value = control_inputs.flat[0]
            return np.full((batch_size, horizon), control_value)


def simulate_batch(
    initial_states: np.ndarray,
    control_inputs: np.ndarray,
    dt: float,
    horizon: Optional[int] = None,
    *,
    energy_limits: Optional[float] = None,
    state_bounds: Optional[tuple] = None,
    stop_fn: Optional[Callable[[np.ndarray], bool]] = None,
    t0: float = 0.0,
    **kwargs
) -> np.ndarray:
    """Vectorized batch simulation function for backward compatibility.

    This function provides a simplified interface similar to the original
    vector_sim.simulate function.

    Parameters
    ----------
    initial_states : np.ndarray
        Initial states - shape (batch_size, state_dim)
    control_inputs : np.ndarray
        Control inputs - shape (batch_size, horizon) or (batch_size, horizon, m)
    dt : float
        Time step
    horizon : int, optional
        Simulation horizon (inferred from control_inputs if None)
    energy_limits : float, optional
        Energy limit for safety guards
    state_bounds : tuple, optional
        State bounds for safety guards
    stop_fn : callable, optional
        Early stopping function
    t0 : float, optional
        Initial time
    **kwargs
        Additional arguments

    Returns
    -------
    np.ndarray
        Batch state trajectories - shape (batch_size, horizon+1, state_dim)
    """
    from ..core.simulation_context import SimulationContext

    # Create context and orchestrator
    context = SimulationContext()
    orchestrator = BatchOrchestrator(context)

    # Infer horizon if not provided
    if horizon is None:
        if control_inputs.ndim >= 2:
            horizon = control_inputs.shape[1]
        else:
            raise ValueError("Cannot infer horizon from control_inputs shape")

    # Execute simulation
    result = orchestrator.execute(
        initial_states, control_inputs, dt, horizon,
        energy_limits=energy_limits,
        state_bounds=state_bounds,
        stop_fn=stop_fn,
        t0=t0,
        **kwargs
    )

    # Extract state trajectories
    trajectories = []
    batch_size = len(initial_states) if initial_states.ndim > 1 else 1

    for b in range(batch_size):
        states = result.get_states(batch_index=b)
        trajectories.append(states)

    return np.array(trajectories)


def simulate_system_batch(
    *,
    controller_factory: Callable[[np.ndarray], Any],
    particles: Any,
    sim_time: float,
    dt: float,
    u_max: Optional[float] = None,
    seed: Optional[int] = None,
    params_list: Optional[Iterable[Any]] = None,
    initial_state: Optional[Any] = None,
    convergence_tol: Optional[float] = None,
    grace_period: float = 0.0,
    rng: Optional[np.random.Generator] = None,
    **_kwargs: Any,
) -> Any:
    """Vectorised closed-loop batch simulation of multiple controllers.

    Restored in M6 Slice 1a from the legacy ``simulation/engines/vector_sim``
    facade (dropped in M4 S5). Instantiates one controller per particle gain
    vector, drives each closed loop, and returns time, state, control and
    sliding-surface arrays for the whole batch.

    Returns ``(t, x_b, u_b, sigma_b)`` with shapes ``(N+1,)``, ``(B, N+1, D)``,
    ``(B, N)`` and ``(B, N)``. When ``params_list`` is provided, returns a list
    of such tuples (one per element); perturbed physics are replicated, matching
    legacy behaviour.
    """
    import numpy as _np
    part_arr = _np.asarray(particles, dtype=float)
    if part_arr.ndim == 1:
        part_arr = part_arr[_np.newaxis, :]
    B, G = part_arr.shape
    dt = float(dt)
    sim_time = float(sim_time)
    H = int(round(sim_time / dt)) if sim_time > 0 else 0
    controllers = []
    for j in range(B):
        try:
            ctrl = controller_factory(part_arr[j])
        except Exception:
            ctrl = controller_factory(part_arr[j])
        controllers.append(ctrl)
    if initial_state is None:
        state_dim = None
        try:
            state_dim = int(getattr(controllers[0], "state_dim"))
        except Exception:
            try:
                state_dim = int(getattr(controllers[0], "dynamics_model").state_dim)
            except Exception:
                state_dim = 6
        init_b = _np.zeros((B, state_dim), dtype=float)
    else:
        init = _np.asarray(initial_state, dtype=float)
        if init.ndim == 1:
            init_b = _np.broadcast_to(init, (B, init.shape[0])).copy()
        else:
            init_b = init.copy()
    t_arr = _np.zeros(H + 1, dtype=float)
    x_b = _np.zeros((B, H + 1, init_b.shape[1]), dtype=float)
    u_b = _np.zeros((B, H), dtype=float)
    sigma_b = _np.zeros((B, H), dtype=float)
    x_b[:, 0, :] = init_b
    check_convergence = (convergence_tol is not None) and (convergence_tol is not False)
    conv_tol = float(convergence_tol) if convergence_tol else 0.0
    grace_steps = int(round(float(grace_period) / dt)) if grace_period > 0 else 0
    state_vars = [None] * B
    histories = [None] * B
    for j, ctrl in enumerate(controllers):
        try:
            if hasattr(ctrl, "initialize_state"):
                state_vars[j] = ctrl.initialize_state()
        except Exception as e:
            logging.getLogger(__name__).debug(
                f"Controller {j} ({type(ctrl).__name__}) doesn't support state initialization: {e}"
            )
            state_vars[j] = None
        try:
            if hasattr(ctrl, "initialize_history"):
                histories[j] = ctrl.initialize_history()
        except Exception as e:
            logging.getLogger(__name__).debug(
                f"Controller {j} ({type(ctrl).__name__}) doesn't support history initialization: {e}"
            )
            histories[j] = None
    u_limits = _np.full(B, _np.inf, dtype=float)
    if u_max is not None:
        u_limits[:] = float(u_max)
    else:
        for j, ctrl in enumerate(controllers):
            if hasattr(ctrl, "max_force"):
                try:
                    u_limits[j] = float(getattr(ctrl, "max_force"))
                except Exception:
                    u_limits[j] = _np.inf
    times = t_arr
    for i in range(H):
        t_now = i * dt
        times[i] = t_now
        for j, ctrl in enumerate(controllers):
            x_curr = x_b[j, i]
            try:
                if hasattr(ctrl, "compute_control"):
                    ret = ctrl.compute_control(x_curr, state_vars[j], histories[j])
                    try:
                        u_val = float(ret[0])
                    except Exception:
                        u_val = float(ret)
                    try:
                        if len(ret) >= 2:
                            state_vars[j] = ret[1]
                        if len(ret) >= 3:
                            histories[j] = ret[2]
                    except Exception:
                        pass
                    sigma_val = 0.0
                    if hasattr(ret, "sigma"):
                        sigma_val = float(ret.sigma)
                    elif hasattr(ret, "__len__") and len(ret) >= 4:
                        sigma_val = float(ret[3])
                else:
                    u_val = float(ctrl(t_now, x_curr))
                    sigma_val = 0.0
            except Exception as e:
                if isinstance(e, Warning):
                    raise
                H = i
                u_b = u_b[:, :i]
                x_b = x_b[:, : i + 1]
                sigma_b = sigma_b[:, :i]
                times = times[: i + 1]
                for jj, c in enumerate(controllers):
                    hist = histories[jj]
                    if hist is not None:
                        try:
                            setattr(c, "_last_history", hist)
                        except Exception as e:
                            logging.getLogger(__name__).debug(
                                f"Could not attach history to controller {jj}: {e}"
                            )
                if params_list is not None:
                    return [(_np.copy(times), _np.copy(x_b), _np.copy(u_b), _np.copy(sigma_b)) for _ in params_list]
                return times, x_b, u_b, sigma_b
            limit = u_limits[j]
            if limit < _np.inf:
                if u_val > limit:
                    u_val = limit
                elif u_val < -limit:
                    u_val = -limit
            u_b[j, i] = u_val
            sigma_b[j, i] = sigma_val
        early_stop = False
        for j, ctrl in enumerate(controllers):
            dyn = getattr(ctrl, "dynamics_model", None)
            if dyn is None:
                try:
                    x_next = ctrl.step(x_b[j, i], u_b[j, i], dt)
                except Exception:
                    x_next = None
            else:
                try:
                    x_next = dyn.step(x_b[j, i], u_b[j, i], dt)
                except Exception:
                    x_next = None
            if x_next is None:
                early_stop = True
                break
            x_next_arr = _np.asarray(x_next, dtype=float).reshape(-1)
            if not _np.all(_np.isfinite(x_next_arr)):
                early_stop = True
                break
            x_b[j, i + 1] = x_next_arr
        if early_stop:
            H = i
            u_b = u_b[:, :i]
            x_b = x_b[:, : i + 1]
            sigma_b = sigma_b[:, :i]
            times = times[: i + 1]
            for jj, c in enumerate(controllers):
                hist = histories[jj]
                if hist is not None:
                    try:
                        setattr(c, "_last_history", hist)
                    except Exception:
                        pass
            if params_list is not None:
                return [(_np.copy(times), _np.copy(x_b), _np.copy(u_b), _np.copy(sigma_b)) for _ in params_list]
            return times, x_b, u_b, sigma_b
        if check_convergence and (i >= grace_steps):
            max_sigma = _np.max(_np.abs(sigma_b[:, i]))
            if max_sigma < conv_tol:
                H = i + 1
                u_b = u_b[:, : i + 1]
                x_b = x_b[:, : i + 2]
                sigma_b = sigma_b[:, : i + 1]
                times = times[: i + 2]
                for jj, c in enumerate(controllers):
                    hist = histories[jj]
                    if hist is not None:
                        try:
                            setattr(c, "_last_history", hist)
                        except Exception:
                            pass
                if params_list is not None:
                    return [(_np.copy(times), _np.copy(x_b), _np.copy(u_b), _np.copy(sigma_b)) for _ in params_list]
                return times, x_b, u_b, sigma_b
    times[H] = H * dt
    for jj, c in enumerate(controllers):
        hist = histories[jj]
        if hist is not None:
            try:
                setattr(c, "_last_history", hist)
            except Exception:
                pass
    result = (times, x_b, u_b, sigma_b)
    if params_list is None:
        return result
    return [(_np.copy(times), _np.copy(x_b), _np.copy(u_b), _np.copy(sigma_b)) for _ in params_list]
