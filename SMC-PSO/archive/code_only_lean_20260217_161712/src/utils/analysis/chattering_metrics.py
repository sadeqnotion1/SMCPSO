#======================================================================================\\
#================ src/utils/analysis/chattering_metrics.py ===========================\\
#======================================================================================\\

"""
Chattering Analysis Metrics for Sliding Mode Control

Provides quantitative metrics for measuring chattering in SMC controllers:
- Chattering index (control rate variance)
- Control rate standard deviation
- Zero-crossing frequency

Used for MT-7 validation and controller comparison studies.
"""

import numpy as np
from typing import Optional


def compute_chattering_index(
    u_traj: np.ndarray,
    dt: float,
    transient_time: float = 1.0
) -> float:
    """Compute chattering index from control trajectory.

    The chattering index quantifies high-frequency oscillations in the control
    signal by measuring the variance of the control rate (du/dt).

    Parameters
    ----------
    u_traj : np.ndarray
        Control signal trajectory, shape (n_steps,)
    dt : float
        Time step (s)
    transient_time : float, optional
        Transient period to exclude from analysis (s), default 1.0

    Returns
    -------
    chattering_index : float
        Chattering index (variance of control rate)
        Higher values indicate more chattering
        Typical range: 0.01-100+ (controller-dependent)
    """
    # Skip transient period
    n_skip = int(transient_time / dt)
    u_steady = u_traj[n_skip:]

    if len(u_steady) < 2:
        return 0.0

    # Compute control rate (du/dt)
    du_dt = np.diff(u_steady) / dt

    # Chattering index = variance of control rate
    chattering_idx = float(np.var(du_dt))

    return chattering_idx


def compute_control_rate_std(
    u_traj: np.ndarray,
    dt: float,
    transient_time: float = 1.0
) -> float:
    """Compute standard deviation of control rate.

    Alternative chattering metric that measures control rate variability.

    Parameters
    ----------
    u_traj : np.ndarray
        Control signal trajectory, shape (n_steps,)
    dt : float
        Time step (s)
    transient_time : float, optional
        Transient period to exclude from analysis (s), default 1.0

    Returns
    -------
    control_rate_std : float
        Standard deviation of control rate (N/s for force control)
    """
    # Skip transient period
    n_skip = int(transient_time / dt)
    u_steady = u_traj[n_skip:]

    if len(u_steady) < 2:
        return 0.0

    # Compute control rate (du/dt)
    du_dt = np.diff(u_steady) / dt

    # Return standard deviation
    return float(np.std(du_dt))


def compute_zero_crossings(
    u_traj: np.ndarray,
    dt: float,
    transient_time: float = 1.0
) -> float:
    """Compute zero-crossing frequency of control signal.

    Measures how often the control signal changes sign, indicating
    rapid switching behavior characteristic of chattering.

    Parameters
    ----------
    u_traj : np.ndarray
        Control signal trajectory, shape (n_steps,)
    dt : float
        Time step (s)
    transient_time : float, optional
        Transient period to exclude from analysis (s), default 1.0

    Returns
    -------
    zero_crossing_freq : float
        Zero-crossing frequency (Hz)
    """
    # Skip transient period
    n_skip = int(transient_time / dt)
    u_steady = u_traj[n_skip:]

    if len(u_steady) < 2:
        return 0.0

    # Detect sign changes
    sign_changes = np.diff(np.sign(u_steady)) != 0
    n_crossings = np.sum(sign_changes)

    # Compute frequency
    duration = (len(u_steady) - 1) * dt
    zero_crossing_freq = n_crossings / duration if duration > 0 else 0.0

    return float(zero_crossing_freq)


def compute_chattering_metrics(
    u_traj: np.ndarray,
    dt: float,
    transient_time: float = 1.0
) -> dict:
    """Compute all chattering metrics for a control trajectory.

    Parameters
    ----------
    u_traj : np.ndarray
        Control signal trajectory, shape (n_steps,)
    dt : float
        Time step (s)
    transient_time : float, optional
        Transient period to exclude from analysis (s), default 1.0

    Returns
    -------
    metrics : dict
        Dictionary containing:
        - chattering_index: float
        - control_rate_std: float
        - zero_crossing_freq: float
    """
    return {
        'chattering_index': compute_chattering_index(u_traj, dt, transient_time),
        'control_rate_std': compute_control_rate_std(u_traj, dt, transient_time),
        'zero_crossing_freq': compute_zero_crossings(u_traj, dt, transient_time),
    }
