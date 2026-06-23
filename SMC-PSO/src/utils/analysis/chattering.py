"""
================================================================================
Chattering Metrics Analysis Module
================================================================================

Provides quantitative metrics for analyzing chattering in sliding mode control
signals using frequency-domain analysis (FFT) and time-domain measurements.

Chattering is high-frequency oscillation in SMC due to:
1. Finite switching frequency in digital implementations
2. Unmodeled actuator dynamics
3. Measurement noise

This module implements:
- FFT-based frequency analysis
- Chattering frequency detection (peak finding above threshold)
- Amplitude measurement (RMS of high-frequency components)
- Comprehensive chattering metrics (frequency, amplitude, power)

Author: DIP_SMC_PSO Team
Created: October 2025 (Week 1, Task QW-4)
"""

import numpy as np
from typing import Tuple, Dict, Optional


def fft_analysis(
    control_signal: np.ndarray,
    dt: float
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Perform FFT analysis on control signal to extract frequency spectrum.

    Uses numpy FFT with proper normalization and frequency axis scaling.
    Only returns positive frequencies (single-sided spectrum).

    Parameters
    ----------
    control_signal : np.ndarray
        Control signal time series, shape (N,)
    dt : float
        Sampling period (seconds)

    Returns
    -------
    freqs : np.ndarray
        Frequency array (Hz), shape (N//2,)
    magnitudes : np.ndarray
        Magnitude spectrum (amplitude), shape (N//2,)

    Notes
    -----
    The FFT magnitude is normalized by N to match continuous Fourier transform
    amplitude convention. For a sine wave A*sin(2πft), the FFT peak magnitude
    will be A/2 (due to two-sided to one-sided conversion).

    Examples
    --------
    >>> t = np.linspace(0, 1, 1000)
    >>> dt = t[1] - t[0]
    >>> signal = 5.0 * np.sin(2 * np.pi * 10 * t)  # 10 Hz, amplitude 5
    >>> freqs, mags = fft_analysis(signal, dt)
    >>> peak_idx = np.argmax(mags)
    >>> peak_freq = freqs[peak_idx]  # Should be ~10 Hz
    >>> peak_amp = mags[peak_idx]    # Should be ~2.5 (A/2 for sine)
    """
    N = len(control_signal)

    # Compute FFT
    fft_values = np.fft.fft(control_signal)

    # Compute frequency axis (single-sided, positive frequencies only)
    freqs = np.fft.fftfreq(N, d=dt)[:N//2]

    # Compute magnitude spectrum (normalized, single-sided)
    # Normalization by N gives amplitude, no factor of 2 for DC
    # For AC components, factor of 2 accounts for negative frequencies
    magnitudes = np.abs(fft_values[:N//2]) / N
    magnitudes[1:] *= 2.0  # Double all except DC component

    return freqs, magnitudes


def detect_chattering_frequency(
    freqs: np.ndarray,
    magnitudes: np.ndarray,
    threshold: float = 10.0
) -> Tuple[Optional[float], Optional[float]]:
    """
    Detect dominant chattering frequency above a threshold.

    Identifies the peak frequency in the magnitude spectrum that exceeds
    the threshold. If no peaks above threshold, returns None.

    Parameters
    ----------
    freqs : np.ndarray
        Frequency array (Hz) from FFT analysis
    magnitudes : np.ndarray
        Magnitude spectrum from FFT analysis
    threshold : float, optional
        Minimum amplitude threshold for chattering detection (default: 10.0)

    Returns
    -------
    peak_freq : float or None
        Frequency (Hz) of dominant chattering peak, or None if no peak above threshold
    peak_amp : float or None
        Amplitude of dominant chattering peak, or None if no peak above threshold

    Notes
    -----
    This function searches the ENTIRE frequency spectrum. For SMC applications,
    chattering typically occurs at:
    - 10-100 Hz for digital implementations (switching frequency)
    - 100-1000 Hz for high-frequency actuator dynamics

    Examples
    --------
    >>> freqs = np.array([0, 1, 2, 3, 4, 5, 10, 15, 20])
    >>> mags = np.array([0.1, 0.5, 1.0, 0.8, 0.3, 0.2, 25.0, 5.0, 1.0])
    >>> peak_freq, peak_amp = detect_chattering_frequency(freqs, mags, threshold=10.0)
    >>> peak_freq  # 10 Hz (chattering frequency)
    10.0
    >>> peak_amp   # 25.0 (amplitude)
    25.0
    """
    # Find indices where magnitude exceeds threshold
    above_threshold = magnitudes > threshold

    if not np.any(above_threshold):
        # No chattering detected
        return None, None

    # Find peak frequency among those above threshold
    peak_idx = np.argmax(magnitudes)

    if magnitudes[peak_idx] <= threshold:
        # Peak is below threshold
        return None, None

    peak_freq = freqs[peak_idx]
    peak_amp = magnitudes[peak_idx]

    return peak_freq, peak_amp


def measure_chattering_amplitude(
    control_signal: np.ndarray,
    dt: float,
    freq_min: float = 10.0,
    freq_max: float = 1000.0
) -> float:
    """
    Measure chattering amplitude as RMS of high-frequency components.

    Computes the root-mean-square (RMS) power in the specified frequency band,
    which represents the overall "strength" of chattering oscillations.

    Parameters
    ----------
    control_signal : np.ndarray
        Control signal time series, shape (N,)
    dt : float
        Sampling period (seconds)
    freq_min : float, optional
        Minimum frequency for chattering band (Hz), default: 10 Hz
    freq_max : float, optional
        Maximum frequency for chattering band (Hz), default: 1000 Hz

    Returns
    -------
    chattering_index : float
        RMS amplitude of high-frequency components (same units as control_signal)

    Notes
    -----
    The chattering index is defined as:

    .. math::
        I_{chat} = \\sqrt{\\frac{1}{N_{band}} \\sum_{f \\in [f_{min}, f_{max}]} |X(f)|^2}

    where X(f) is the FFT magnitude at frequency f, and N_band is the number
    of frequency bins in the specified band.

    A higher chattering index indicates more severe high-frequency oscillations.

    Examples
    --------
    >>> t = np.linspace(0, 1, 10000)
    >>> dt = t[1] - t[0]
    >>> signal = 100.0 * np.sin(2 * np.pi * 50 * t)  # 50 Hz chattering
    >>> index = measure_chattering_amplitude(signal, dt, freq_min=10, freq_max=100)
    >>> index  # Should be ~70.7 (RMS of 100-amplitude sine = 100/sqrt(2))
    70.7
    """
    freqs, magnitudes = fft_analysis(control_signal, dt)

    # Find frequency band indices
    band_mask = (freqs >= freq_min) & (freqs <= freq_max)

    if not np.any(band_mask):
        # No frequencies in specified band (sampling rate too low)
        return 0.0

    # Extract magnitudes in chattering band
    band_magnitudes = magnitudes[band_mask]

    # Compute RMS using Parseval's theorem
    # For sinusoids: RMS = amplitude / sqrt(2)
    # Sum of squared amplitudes gives total power, then take sqrt
    # Factor of 1/sqrt(2) accounts for sine wave RMS = A/sqrt(2)
    chattering_index = np.sqrt(np.sum(band_magnitudes**2) / 2.0)

    return chattering_index


def compute_chattering_metrics(
    control_signal: np.ndarray,
    dt: float,
    freq_threshold: float = 10.0,
    freq_min: float = 10.0,
    freq_max: float = 1000.0
) -> Dict[str, float]:
    """
    Compute comprehensive chattering metrics from control signal.

    Combines frequency detection, amplitude measurement, and power analysis
    into a single dictionary of quantitative metrics.

    Parameters
    ----------
    control_signal : np.ndarray
        Control signal time series, shape (N,)
    dt : float
        Sampling period (seconds)
    freq_threshold : float, optional
        Amplitude threshold for peak detection (default: 10.0)
    freq_min : float, optional
        Minimum chattering frequency (Hz), default: 10 Hz
    freq_max : float, optional
        Maximum chattering frequency (Hz), default: 1000 Hz

    Returns
    -------
    metrics : dict
        Dictionary with keys:
        - 'peak_frequency': Dominant chattering frequency (Hz), or None
        - 'peak_amplitude': Amplitude of dominant peak, or None
        - 'chattering_index': RMS amplitude in freq band
        - 'total_power': Total power in chattering band
        - 'has_chattering': Boolean, True if chattering detected

    Examples
    --------
    >>> t = np.linspace(0, 2, 20000)
    >>> dt = t[1] - t[0]
    >>> signal = 50.0 * np.sin(2 * np.pi * 30 * t)  # 30 Hz chattering
    >>> metrics = compute_chattering_metrics(signal, dt)
    >>> metrics['peak_frequency']  # ~30 Hz
    30.0
    >>> metrics['chattering_index']  # ~35.4 (RMS of 50-amp sine)
    35.4
    >>> metrics['has_chattering']  # True (peak > threshold)
    True
    """
    # Perform FFT analysis
    freqs, magnitudes = fft_analysis(control_signal, dt)

    # Detect dominant chattering frequency
    peak_freq, peak_amp = detect_chattering_frequency(
        freqs, magnitudes, threshold=freq_threshold
    )

    # Measure chattering amplitude (RMS)
    chattering_index = measure_chattering_amplitude(
        control_signal, dt, freq_min=freq_min, freq_max=freq_max
    )

    # Compute total power in chattering band
    band_mask = (freqs >= freq_min) & (freqs <= freq_max)
    if np.any(band_mask):
        total_power = np.sum(magnitudes[band_mask]**2)
    else:
        total_power = 0.0

    # Determine if chattering is present
    has_chattering = (peak_freq is not None) and (peak_amp is not None)

    metrics = {
        'peak_frequency': peak_freq,
        'peak_amplitude': peak_amp,
        'chattering_index': chattering_index,
        'total_power': total_power,
        'has_chattering': has_chattering
    }

    return metrics
