#======================================================================================\\\
#============= src/controllers/smc/algorithms/classical/boundary_layer.py =============\\\
#======================================================================================\\\

"""
Boundary Layer Implementation for Classical SMC.

Implements boundary layer method for chattering reduction in sliding mode control.
Extracted from the original monolithic controller to provide focused, reusable
boundary layer logic.

Mathematical Background:
- Boundary layer thickness ε controls trade-off between chattering and tracking error
- Adaptive boundary layer: ε_eff = ε + α|ṡ| adapts to surface motion
- Switching function approximates sign(s) with continuous function within ±ε
"""

from typing import Union, Optional
import numpy as np
from ...core.switching_functions import SwitchingFunction


class BoundaryLayer:
    """
    Boundary layer implementation for chattering reduction.

    Provides continuous approximation to discontinuous switching within
    a thin layer around the sliding surface.
    """

    def __init__(self,
                 thickness: float,
                 slope: float = 0.0,
                 switch_method: str = "tanh"):
        """
        Initialize boundary layer.

        Args:
            thickness: Base boundary layer thickness ε > 0
            slope: Adaptive slope coefficient α ≥ 0 for ε_eff = ε + α|ṡ|
            switch_method: Switching function type ("tanh", "linear", "sign")
        """
        # Enhanced mathematical validation
        if not np.isfinite(thickness):
            raise ValueError("Boundary layer thickness must be finite")
        if thickness <= 0:
            raise ValueError("Boundary layer thickness must be positive")
        if thickness < 1e-12:
            raise ValueError("Boundary layer thickness too small (minimum: 1e-12)")
        if not np.isfinite(slope):
            raise ValueError("Boundary layer slope must be finite")
        if slope < 0:
            raise ValueError("Boundary layer slope must be non-negative")

        self.base_thickness = thickness
        self.slope = slope
        self.switching_func = SwitchingFunction(switch_method)

    def get_effective_thickness(self, surface_derivative: float = 0.0) -> float:
        """
        Compute effective boundary layer thickness.

        For adaptive boundary layer: ε_eff = ε_base + α|ṡ|
        Larger thickness when surface is changing rapidly (high |ṡ|).

        Args:
            surface_derivative: Surface time derivative ṡ

        Returns:
            Effective boundary layer thickness
        """
        # Handle invalid surface derivative
        if not np.isfinite(surface_derivative):
            surface_derivative = 0.0

        if self.slope == 0.0:
            return self.base_thickness

        adaptive_component = self.slope * abs(surface_derivative)

        # Mathematical safety: ensure finite result
        if not np.isfinite(adaptive_component):
            adaptive_component = 0.0

        effective_thickness = self.base_thickness + adaptive_component

        # Ensure minimum thickness to prevent division by zero
        return max(effective_thickness, 1e-12)

    def apply_to_surface(self, surface_value: float,
                        surface_derivative: float = 0.0) -> float:
        """
        Apply boundary layer switching to surface value.

        Args:
            surface_value: Sliding surface value s
            surface_derivative: Surface derivative ṡ (for adaptive thickness)

        Returns:
            Switching function output ∈ [-1, 1]
        """
        # Validate inputs for mathematical safety
        if not np.isfinite(surface_value):
            return 0.0  # Safe fallback for invalid input
        if not np.isfinite(surface_derivative):
            surface_derivative = 0.0  # Use zero derivative if invalid

        effective_epsilon = self.get_effective_thickness(surface_derivative)

        # Ensure effective epsilon is never zero
        if effective_epsilon <= 0:
            effective_epsilon = max(self.base_thickness, 1e-12)

        return self.switching_func.compute(surface_value, effective_epsilon)

    def compute_switching_control(self, surface_value: float,
                                 switching_gain: float,
                                 surface_derivative: float = 0.0) -> float:
        """
        Compute switching control component.

        Args:
            surface_value: Sliding surface value s
            switching_gain: Switching gain K > 0
            surface_derivative: Surface derivative ṡ

        Returns:
            Switching control: u_switch = -K * switch_func(s/ε_eff)
        """
        if switching_gain <= 0:
            raise ValueError("Switching gain must be positive")

        switch_output = self.apply_to_surface(surface_value, surface_derivative)
        return -switching_gain * switch_output

    def is_in_boundary_layer(self, surface_value: float,
                           surface_derivative: float = 0.0) -> bool:
        """
        Check if system is within boundary layer.

        Args:
            surface_value: Sliding surface value s
            surface_derivative: Surface derivative ṡ

        Returns:
            True if |s| ≤ ε_eff, False otherwise
        """
        effective_epsilon = self.get_effective_thickness(surface_derivative)
        return abs(surface_value) <= effective_epsilon

    def get_chattering_index(self, control_history: Union[list, np.ndarray],
                           dt: float = 0.01,
                           method: str = "frequency",
                           cutoff_hz: float = 20.0) -> float:
        """
        Compute chattering index from control signal history.

        **IMPORTANT:** Default method changed from "combined" to "frequency" (Oct 2025).
        The old "combined" method (RMS(du/dt) + frequency) is BIASED against adaptive
        boundary layers because it penalizes time-varying ε(t) from adaptation, NOT
        true high-frequency chattering. See MT-6 analysis for details.

        Measures high-frequency oscillations in the control signal using unbiased
        frequency-domain analysis. Higher values indicate more chattering.

        Args:
            control_history: Time series of control signal values
            dt: Sampling time (seconds)
            method: Chattering detection method:
                - "frequency" (default, RECOMMENDED): Frequency-domain only, unbiased
                - "zero_crossing": Count sign changes per second
                - "combined_legacy": Old biased method (DEPRECATED, use for comparison only)
            cutoff_hz: High-frequency cutoff in Hz (default: 20.0, adjusted from 10.0)

        Returns:
            Chattering index (dimensionless for frequency/combined, Hz for zero_crossing)

        Notes:
            - **Frequency method:** Measures fraction of power above cutoff_hz
              * Unbiased for adaptive boundary layers
              * Typical range: [0, 0.01] for well-tuned SMC
              * RECOMMENDED for all chattering analysis

            - **Zero-crossing method:** Counts switching frequency
              * Unbiased, direct measure of oscillations
              * Typical range: [0, 10] Hz for DIP systems
              * Good for qualitative comparison

            - **Combined_legacy method:** RMS(du/dt) + frequency (DEPRECATED)
              * BIASED against adaptive boundary layers
              * Inflates chattering index by 300-400% for adaptive controllers
              * Only use for backward compatibility testing

        References:
            - MT-6 Chattering Metric Bias Analysis (Oct 2025)
            - benchmarks/MT6_PHASE2_FINAL_REPORT.md
        """
        if len(control_history) < 3:
            return 0.0

        control_array = np.asarray(control_history)

        if method == "frequency":
            # RECOMMENDED: Frequency-domain only (unbiased)
            return self._chattering_frequency_domain(control_array, dt, cutoff_hz)

        elif method == "zero_crossing":
            # Alternative: Zero-crossing rate (unbiased)
            return self._chattering_zero_crossing(control_array, dt)

        elif method == "combined_legacy":
            # DEPRECATED: Old biased method (kept for backward compatibility)
            import warnings
            warnings.warn(
                "The 'combined_legacy' chattering metric is BIASED against adaptive "
                "boundary layers. Use method='frequency' (default) instead. "
                "See MT-6 analysis for details.",
                DeprecationWarning,
                stacklevel=2
            )
            return self._chattering_combined_legacy(control_array, dt, cutoff_hz=10.0)

        else:
            raise ValueError(f"Unknown chattering method: {method}. "
                           f"Choose from: 'frequency', 'zero_crossing', 'combined_legacy'")

    def _chattering_frequency_domain(self, control_array: np.ndarray,
                                    dt: float,
                                    cutoff_hz: float) -> float:
        """
        Frequency-domain chattering index (UNBIASED).

        Computes fraction of power above cutoff frequency using FFT.
        Unbiased for adaptive boundary layers because ε(t) variations are
        low-frequency (<1 Hz) and filtered out.

        Args:
            control_array: Control signal array
            dt: Sampling time
            cutoff_hz: High-frequency cutoff (Hz)

        Returns:
            High-frequency power ratio [0, 1]
        """
        if len(control_array) < 10:
            return 0.0

        from scipy.fft import fft, fftfreq

        # Compute FFT
        spectrum = np.abs(fft(control_array))
        freqs = fftfreq(len(control_array), d=dt)

        # High-frequency mask
        hf_mask = np.abs(freqs) > cutoff_hz
        if not np.any(hf_mask):
            return 0.0

        # Power ratio
        hf_power = np.sum(spectrum[hf_mask]**2)
        total_power = np.sum(spectrum**2) + 1e-12

        return float(hf_power / total_power)

    def _chattering_zero_crossing(self, control_array: np.ndarray,
                                  dt: float) -> float:
        """
        Zero-crossing rate chattering index (UNBIASED).

        Counts sign changes per second. Unbiased for adaptive boundary layers
        because sign changes are independent of ε(t) magnitude variations.

        Args:
            control_array: Control signal array
            dt: Sampling time

        Returns:
            Zero-crossing rate (Hz)
        """
        if len(control_array) < 2:
            return 0.0

        # Count sign changes
        sign_changes = np.sum(np.diff(np.sign(control_array)) != 0)
        total_time = len(control_array) * dt

        return float(sign_changes / total_time)

    def _chattering_combined_legacy(self, control_array: np.ndarray,
                                    dt: float,
                                    cutoff_hz: float = 10.0) -> float:
        """
        Combined time+frequency chattering index (BIASED - DEPRECATED).

        Uses 70% RMS(du/dt) + 30% frequency-domain. BIASED against adaptive
        boundary layers because du/dt includes dε/dt component from time-varying
        boundary layer thickness.

        DO NOT USE for comparing fixed vs adaptive boundary layers.

        Args:
            control_array: Control signal array
            dt: Sampling time
            cutoff_hz: High-frequency cutoff (Hz)

        Returns:
            Combined chattering index (BIASED)
        """
        # Time-domain component: RMS of derivative (BIASED)
        control_derivative = np.gradient(control_array, dt)
        time_domain_index = np.sqrt(np.mean(control_derivative**2))

        # Frequency-domain component
        if len(control_array) > 10:
            from scipy.fft import fft, fftfreq
            spectrum = np.abs(fft(control_array))
            freqs = fftfreq(len(control_array), d=dt)

            hf_mask = np.abs(freqs) > cutoff_hz
            hf_power = np.sum(spectrum[hf_mask]) if np.any(hf_mask) else 0.0
            total_power = np.sum(spectrum) + 1e-12

            freq_domain_index = hf_power / total_power
        else:
            freq_domain_index = 0.0

        # Combined (BIASED weighting)
        return float(0.7 * time_domain_index + 0.3 * freq_domain_index)

    def update_thickness(self, new_thickness: float) -> None:
        """
        Update base boundary layer thickness.

        Args:
            new_thickness: New thickness value ε > 0
        """
        if new_thickness <= 0:
            raise ValueError("Boundary layer thickness must be positive")
        self.base_thickness = new_thickness

    def update_slope(self, new_slope: float) -> None:
        """
        Update adaptive slope coefficient.

        Args:
            new_slope: New slope coefficient α ≥ 0
        """
        if new_slope < 0:
            raise ValueError("Boundary layer slope must be non-negative")
        self.slope = new_slope

    def get_parameters(self) -> dict:
        """
        Get boundary layer parameters.

        Returns:
            Dictionary with current parameters
        """
        return {
            'base_thickness': self.base_thickness,
            'slope': self.slope,
            'switch_method': self.switching_func.method.value,
            'adaptive': self.slope > 0
        }

    def analyze_performance(self, surface_history: Union[list, np.ndarray],
                          control_history: Union[list, np.ndarray],
                          dt: float = 0.01,
                          state_history: Optional[np.ndarray] = None) -> dict:
        """
        Analyze boundary layer performance with comprehensive metrics.

        Args:
            surface_history: Time series of surface values
            control_history: Time series of control values
            dt: Sampling time
            state_history: Optional full state trajectory for tracking error analysis

        Returns:
            Performance analysis dictionary including chattering, smoothness,
            boundary layer effectiveness, and frequency-domain metrics
        """
        surface_array = np.asarray(surface_history)
        control_array = np.asarray(control_history)

        if len(surface_array) < 2 or len(control_array) < 2:
            return {'error': 'Insufficient data for analysis'}

        # Chattering metrics (using unbiased frequency-domain method)
        chattering_index = self.get_chattering_index(control_array, dt, method="frequency")

        # Control smoothness index (Total Variation Diminishing metric)
        total_variation = np.sum(np.abs(np.diff(control_array)))
        smoothness_index = 1.0 / (1.0 + total_variation)

        # High-frequency power ratio
        from scipy.fft import fft, fftfreq
        if len(control_array) > 10:
            spectrum = np.abs(fft(control_array))
            freqs = fftfreq(len(control_array), d=dt)
            hf_power = np.sum(spectrum[np.abs(freqs) > 10])
            total_power = np.sum(spectrum)
            hf_ratio = hf_power / (total_power + 1e-12)
        else:
            hf_ratio = 0.0

        # Boundary layer effectiveness (time spent in boundary layer)
        time_in_boundary = float(np.mean([
            self.is_in_boundary_layer(s) for s in surface_array
        ]))

        # Lipschitz continuity measure (control signal smoothness)
        lipschitz_constant = np.max(np.abs(np.diff(control_array))) / dt if len(control_array) > 1 else 0.0

        # Compute performance metrics
        analysis = {
            # Core chattering reduction metrics
            'chattering_index': float(chattering_index),
            'control_smoothness_index': float(smoothness_index),
            'high_frequency_power_ratio': float(hf_ratio),
            'boundary_layer_effectiveness': float(time_in_boundary),
            'lipschitz_constant': float(lipschitz_constant),

            # Traditional metrics
            'surface_rms': float(np.sqrt(np.mean(surface_array**2))),
            'control_rms': float(np.sqrt(np.mean(control_array**2))),
            'time_in_boundary': time_in_boundary,
            'avg_effective_thickness': self.base_thickness,

            # Performance indicators
            'steady_state_error': float(np.mean(np.abs(surface_array[-10:]))),
            'convergence_time': self._estimate_convergence_time(surface_array, dt),
        }

        # Add adaptive thickness statistics if applicable
        if self.slope > 0:
            surface_derivatives = np.gradient(surface_array, dt)
            effective_thicknesses = [
                self.get_effective_thickness(sd) for sd in surface_derivatives
            ]
            analysis.update({
                'min_effective_thickness': float(np.min(effective_thicknesses)),
                'max_effective_thickness': float(np.max(effective_thicknesses)),
                'avg_effective_thickness': float(np.mean(effective_thicknesses))
            })

        # Tracking error analysis (if state provided)
        if state_history is not None and len(state_history) > 0:
            # Assuming state is [x, th1, th2, xdot, th1dot, th2dot]
            tracking_error = np.sqrt(np.mean(state_history[:, 1:3]**2, axis=1))  # RMS of pendulum angles
            analysis['tracking_error_rms'] = float(np.mean(tracking_error))

        return analysis

    def _estimate_convergence_time(self, surface_history: np.ndarray,
                                  dt: float, tolerance: float = 0.1) -> float:
        """
        Estimate time to converge to boundary layer.

        Args:
            surface_history: Surface value time series
            dt: Sampling time
            tolerance: Convergence tolerance

        Returns:
            Estimated convergence time
        """
        # Find first time when |s| < tolerance for sustained period
        abs_surface = np.abs(surface_history)
        converged_indices = np.where(abs_surface < tolerance)[0]

        if len(converged_indices) == 0:
            return float('inf')  # Never converged

        # Look for sustained convergence (at least 10 samples)
        for i in range(len(converged_indices) - 10):
            if np.all(np.diff(converged_indices[i:i+10]) == 1):
                return float(converged_indices[i] * dt)

        return float(converged_indices[0] * dt)  # First convergence point