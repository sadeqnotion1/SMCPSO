"""
================================================================================
Tests for Chattering Metrics Analysis Module
================================================================================

Unit tests for src/utils/analysis/chattering.py

Tests cover:
1. FFT analysis correctness (frequency detection, amplitude accuracy)
2. Chattering frequency detection (peak finding with thresholds)
3. Amplitude measurement (RMS computation in frequency bands)
4. Integration test (full chattering metrics pipeline)

Author: DIP_SMC_PSO Team
Created: October 2025 (Week 1, Task QW-4)
"""

import numpy as np
import pytest
from src.utils.analysis.chattering import (
    fft_analysis,
    detect_chattering_frequency,
    measure_chattering_amplitude,
    compute_chattering_metrics
)


def test_fft_analysis_sine_wave():
    """
    Test FFT analysis on a pure sine wave at 10 Hz.

    Verifies:
    - Peak frequency matches expected (10 Hz)
    - Peak amplitude matches expected (~A/2 for sine wave)
    - Frequency resolution is correct
    """
    # Generate 10 Hz sine wave with amplitude 100
    f_signal = 10.0  # Hz
    amplitude = 100.0
    duration = 2.0  # seconds
    fs = 1000.0  # sampling rate (Hz)
    dt = 1.0 / fs

    t = np.linspace(0, duration, int(duration * fs), endpoint=False)
    signal = amplitude * np.sin(2 * np.pi * f_signal * t)

    # Perform FFT analysis
    freqs, magnitudes = fft_analysis(signal, dt)

    # Find peak frequency
    peak_idx = np.argmax(magnitudes)
    peak_freq = freqs[peak_idx]
    peak_amp = magnitudes[peak_idx]

    # Verify peak frequency (within 1 Hz tolerance due to frequency resolution)
    assert abs(peak_freq - f_signal) < 1.0, \
        f"Expected peak at {f_signal} Hz, got {peak_freq} Hz"

    # Verify peak amplitude (for sine wave, FFT peak is A in single-sided spectrum)
    expected_amp = amplitude  # 100.0
    assert abs(peak_amp - expected_amp) < 5.0, \
        f"Expected amplitude ~{expected_amp}, got {peak_amp}"

    # Verify frequency array properties
    assert len(freqs) == len(magnitudes), "Frequency and magnitude arrays must match"
    assert freqs[0] >= 0, "Frequencies should be non-negative (single-sided)"
    assert freqs[-1] <= fs / 2, "Maximum frequency should not exceed Nyquist frequency"


def test_detect_chattering_frequency_above_threshold():
    """
    Test chattering frequency detection with amplitude threshold.

    Verifies:
    - Detects peak above threshold
    - Returns None when no peak above threshold
    - Correctly identifies dominant frequency
    """
    # Create synthetic frequency spectrum with peak at 50 Hz
    freqs = np.linspace(0, 500, 1000)  # 0-500 Hz
    magnitudes = 5.0 * np.ones_like(freqs)  # Baseline noise ~5
    magnitudes[100] = 150.0  # Strong peak at ~50 Hz (index 100)
    magnitudes[200] = 25.0   # Weaker peak at ~100 Hz

    # Test 1: Detect peak above threshold = 10
    peak_freq, peak_amp = detect_chattering_frequency(freqs, magnitudes, threshold=10.0)
    assert peak_freq is not None, "Should detect peak above threshold"
    assert abs(peak_freq - 50.0) < 5.0, f"Expected ~50 Hz, got {peak_freq} Hz"
    assert peak_amp > 100.0, f"Expected amplitude >100, got {peak_amp}"

    # Test 2: No peak above very high threshold
    peak_freq_high, peak_amp_high = detect_chattering_frequency(
        freqs, magnitudes, threshold=200.0
    )
    assert peak_freq_high is None, "Should return None when no peak above threshold"
    assert peak_amp_high is None, "Should return None amplitude when no peak"

    # Test 3: Detect weaker peak with lower threshold
    peak_freq_low, peak_amp_low = detect_chattering_frequency(
        freqs, magnitudes, threshold=20.0
    )
    assert peak_freq_low is not None, "Should detect peak with lower threshold"
    # Should still find the strongest peak (50 Hz, amp 150), not the 100 Hz peak
    assert abs(peak_freq_low - 50.0) < 5.0, "Should find strongest peak"


def test_chattering_amplitude_measurement():
    """
    Test RMS amplitude measurement in specified frequency band.

    Verifies:
    - Correct RMS computation for pure sine wave
    - Frequency band filtering works correctly
    - Handles multiple frequency components
    """
    # Generate signal with chattering at 50 Hz (amplitude 100)
    fs = 2000.0  # sampling rate (Hz)
    dt = 1.0 / fs
    duration = 2.0
    t = np.linspace(0, duration, int(duration * fs), endpoint=False)

    # Signal: low-freq (5 Hz) + high-freq chattering (50 Hz)
    signal = 10.0 * np.sin(2 * np.pi * 5 * t) + \
             100.0 * np.sin(2 * np.pi * 50 * t)

    # Test 1: Measure chattering in 10-100 Hz band (should capture 50 Hz component)
    chattering_index = measure_chattering_amplitude(
        signal, dt, freq_min=10.0, freq_max=100.0
    )

    # For a 100-amplitude sine wave, RMS = 100 / sqrt(2) ≈ 70.7
    # With some noise from other components, allow tolerance
    expected_rms = 100.0 / np.sqrt(2)
    assert abs(chattering_index - expected_rms) < 10.0, \
        f"Expected RMS ~{expected_rms}, got {chattering_index}"

    # Test 2: Measure in band that excludes chattering (1-8 Hz, only low-freq)
    low_freq_index = measure_chattering_amplitude(
        signal, dt, freq_min=1.0, freq_max=8.0
    )

    # Should capture the 5 Hz component (amplitude 10, RMS = 10/sqrt(2) ≈ 7.07)
    expected_low_rms = 10.0 / np.sqrt(2)
    assert abs(low_freq_index - expected_low_rms) < 2.0, \
        f"Expected RMS ~{expected_low_rms}, got {low_freq_index}"

    # Test 3: Measure in band with no signal (200-300 Hz)
    no_signal_index = measure_chattering_amplitude(
        signal, dt, freq_min=200.0, freq_max=300.0
    )
    assert no_signal_index < 1.0, \
        f"Expected near-zero RMS in empty band, got {no_signal_index}"


def test_compute_chattering_metrics_integration():
    """
    Integration test for complete chattering metrics computation.

    Verifies:
    - All metrics computed correctly
    - Dictionary keys present
    - Chattering detection logic works
    - Metrics are physically meaningful
    """
    # Generate control signal with chattering at 30 Hz (amplitude 80)
    fs = 2000.0  # sampling rate
    dt = 1.0 / fs
    duration = 2.0
    t = np.linspace(0, duration, int(duration * fs), endpoint=False)

    # Chattering signal: 30 Hz sine wave
    signal = 80.0 * np.sin(2 * np.pi * 30 * t)

    # Compute comprehensive metrics
    metrics = compute_chattering_metrics(
        signal, dt,
        freq_threshold=10.0,
        freq_min=10.0,
        freq_max=100.0
    )

    # Verify all expected keys present
    expected_keys = {
        'peak_frequency',
        'peak_amplitude',
        'chattering_index',
        'total_power',
        'has_chattering'
    }
    assert set(metrics.keys()) == expected_keys, \
        f"Missing metrics keys: {expected_keys - set(metrics.keys())}"

    # Verify peak frequency detection
    assert metrics['peak_frequency'] is not None, "Should detect chattering peak"
    assert abs(metrics['peak_frequency'] - 30.0) < 2.0, \
        f"Expected peak ~30 Hz, got {metrics['peak_frequency']} Hz"

    # Verify peak amplitude
    assert metrics['peak_amplitude'] is not None, "Should detect peak amplitude"
    assert metrics['peak_amplitude'] > 20.0, \
        f"Expected significant amplitude, got {metrics['peak_amplitude']}"

    # Verify chattering index (RMS of 80-amp sine ≈ 56.6)
    expected_rms = 80.0 / np.sqrt(2)
    assert abs(metrics['chattering_index'] - expected_rms) < 10.0, \
        f"Expected RMS ~{expected_rms}, got {metrics['chattering_index']}"

    # Verify total power (should be positive)
    assert metrics['total_power'] > 0, \
        f"Expected positive total power, got {metrics['total_power']}"

    # Verify chattering detection flag
    assert metrics['has_chattering'] is True, \
        "Should flag chattering as present"

    # Test case 2: No chattering (low-amplitude signal)
    quiet_signal = 1.0 * np.sin(2 * np.pi * 30 * t)  # amplitude 1 (below threshold)
    quiet_metrics = compute_chattering_metrics(
        quiet_signal, dt, freq_threshold=10.0, freq_min=10.0, freq_max=100.0
    )

    # Should not detect chattering (peak below threshold)
    assert quiet_metrics['has_chattering'] is False, \
        "Should not detect chattering for low-amplitude signal"
    assert quiet_metrics['peak_frequency'] is None, \
        "Peak frequency should be None when below threshold"
    assert quiet_metrics['peak_amplitude'] is None, \
        "Peak amplitude should be None when below threshold"

    # Chattering index should still be computable (RMS of all components)
    assert quiet_metrics['chattering_index'] >= 0, \
        "Chattering index should be non-negative"


def test_fft_analysis_edge_cases():
    """
    Test FFT analysis on edge cases (DC signal, impulse, noise).
    """
    dt = 0.001  # 1 kHz sampling

    # Test 1: DC signal (zero frequency)
    dc_signal = 10.0 * np.ones(1000)
    freqs_dc, mags_dc = fft_analysis(dc_signal, dt)
    assert mags_dc[0] > 5.0, "DC component should have large magnitude at f=0"
    assert np.max(mags_dc[1:]) < 1.0, "Should have minimal AC components"

    # Test 2: White noise (broad spectrum)
    noise_signal = np.random.randn(1000)
    freqs_noise, mags_noise = fft_analysis(noise_signal, dt)
    # Noise should have roughly uniform spectrum (no dominant peaks)
    assert np.std(mags_noise) < np.mean(mags_noise), \
        "White noise should have relatively flat spectrum"

    # Test 3: Impulse (all frequencies)
    impulse_signal = np.zeros(1000)
    impulse_signal[500] = 100.0  # Single spike
    freqs_impulse, mags_impulse = fft_analysis(impulse_signal, dt)
    # Impulse should have energy across all frequencies
    assert np.mean(mags_impulse) > 0, "Impulse should have broad spectrum"


def test_measure_chattering_amplitude_empty_band():
    """
    Test chattering amplitude when frequency band is empty (sampling rate too low).
    """
    # Generate signal with very low sampling rate
    fs = 50.0  # 50 Hz sampling (Nyquist = 25 Hz)
    dt = 1.0 / fs
    duration = 1.0
    t = np.linspace(0, duration, int(duration * fs), endpoint=False)
    signal = 10.0 * np.sin(2 * np.pi * 5 * t)

    # Try to measure chattering in band above Nyquist frequency (should return 0)
    chattering_index = measure_chattering_amplitude(
        signal, dt, freq_min=100.0, freq_max=200.0
    )
    assert chattering_index == 0.0, \
        "Should return 0 when frequency band is empty (sampling rate too low)"


if __name__ == "__main__":
    # Allow running tests directly with: python tests/test_utils/test_chattering.py
    pytest.main([__file__, "-v"])
