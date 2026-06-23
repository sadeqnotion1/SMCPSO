# ClassicalSMCConfig Parameters and Validation Rules This document provides specification of the `ClassicalSMCConfig` parameters, their mathematical foundations, validation rules, and edge case handling. ## 1. Configuration Schema Overview The `ClassicalSMCConfig` dataclass provides type-safe, validated configuration for Classical Sliding Mode Control with the following parameter categories: - **Control Parameters**: Core SMC gains and timing

- **Boundary Layer Parameters**: Chattering reduction settings
- **Numerical Parameters**: Regularization and thresholds
- **System Parameters**: Force limits and dynamics model
- **Switching Parameters**: Control law selection ## 2. Parameter Specifications ### 2.1 Required Parameters #### 2.1.1 Control Timestep (`dt`) ```python
dt: float = field() # Control timestep in seconds
``` **Mathematical Foundation:**
- Determines discrete-time control update rate
- Affects numerical stability of control law
- Must satisfy Nyquist criterion for system bandwidth **Validation Rules:**
```python

if self.dt <= 0: raise ValueError("dt must be positive")
``` **Typical Range:** `0.001 ≤ dt ≤ 0.1` seconds
**Recommended:** `dt = 0.01` (100 Hz control rate) #### 2.1.2 Gains Vector (`gains`) ```python
gains: List[float] = field() # [k1, k2, lam1, lam2, K, kd]
``` **Mathematical Foundation:**

The gains vector contains six parameters with specific roles: 1. **k1** (c₁): Joint 1 position gain in sliding surface
2. **k2** (c₂): Joint 2 position gain in sliding surface
3. **lam1** (λ₁): Joint 1 velocity gain in sliding surface
4. **lam2** (λ₂): Joint 2 velocity gain in sliding surface
5. **K**: Switching gain for reaching law
6. **kd**: Derivative gain for damping **Sliding Surface Definition:**
```
s = λ₁θ̇₁ + k₁θ₁ + λ₂θ̇₂ + k₂θ₂
``` **Control Law Components:**

```
u_switching = -K · sign(s)
u_derivative = -kd · ṡ
``` **Validation Rules:**

```python
# example-metadata:
# runnable: false def _validate_gains(self) -> None: """Validate gain vector according to SMC theory.""" if len(self.gains) != 6: raise ValueError("Classical SMC requires exactly 6 gains: [k1, k2, lam1, lam2, K, kd]") k1, k2, lam1, lam2, K, kd = self.gains # Surface gains must be positive for Hurwitz stability if any(g <= 0 for g in [k1, k2, lam1, lam2]): raise ValueError("Surface gains [k1, k2, λ1, λ2] must be positive for stability") # Switching gain must be positive for reaching condition if K <= 0: raise ValueError("Switching gain K must be positive") # Derivative gain must be non-negative if kd < 0: raise ValueError("Derivative gain kd must be non-negative")
``` **Stability Requirements:** 1. **Surface Gains Positivity**: k₁, k₂, λ₁, λ₂ > 0 - Ensures Hurwitz stability of sliding dynamics - Guarantees negative real eigenvalues 2. **Switching Gain Positivity**: K > 0 - Required for reaching condition: sṣ ≤ -η|s| - Larger K provides faster convergence but more chattering 3. **Derivative Gain Non-negativity**: kd ≥ 0 - Provides additional damping - Zero value is acceptable (no derivative term) **Typical Ranges:**

- Position gains: `1.0 ≤ k₁, k₂ ≤ 20.0`
- Velocity gains: `1.0 ≤ λ₁, λ₂ ≤ 15.0`
- Switching gain: `5.0 ≤ K ≤ 100.0`
- Derivative gain: `0.0 ≤ kd ≤ 10.0` #### 2.1.3 Maximum Force (`max_force`) ```python
max_force: float = field() # Control saturation limit in Newtons
``` **Mathematical Foundation:**
- Implements actuator saturation: `u_saturated = clip(u, -max_force, max_force)`
- Prevents actuator damage and ensures realistic control signals
- Affects reachability and performance under constraints **Validation Rules:**
```python

if self.max_force <= 0: raise ValueError("max_force must be positive")
``` **Typical Range:** `10.0 ≤ max_force ≤ 500.0` Newtons
**Recommended:** `max_force = 100.0` N for laboratory setup ### 2.2 Boundary Layer Parameters #### 2.2.1 Boundary Layer Thickness (`boundary_layer`) ```python
boundary_layer: float = field() # Chattering reduction thickness ε > 0
``` **Mathematical Foundation:**

Replaces discontinuous switching function with continuous approximation within ±ε: ```
sign(s) ≈ tanh(s/ε) or s/(|s| + ε)
``` **Trade-off Analysis:**
- **Small ε**: Better tracking accuracy, more chattering
- **Large ε**: Less chattering, worse steady-state error
- **Optimal ε**: Balance between chattering and tracking performance **Validation Rules:**
```python

if self.boundary_layer <= 0: raise ValueError("boundary_layer must be positive")
``` **Typical Range:** `0.001 ≤ ε ≤ 0.1`
**Recommended:** `ε = 0.01` for most applications #### 2.2.2 Boundary Layer Slope (`boundary_layer_slope`) ```python
boundary_layer_slope: float = field(default=0.0) # Adaptive slope α ≥ 0
``` **Mathematical Foundation:**

Adaptive boundary layer with effective thickness: ```
ε_eff = ε + α|ṡ|
``` Where:
- `ε`: Base boundary layer thickness
- `α`: Adaptive slope coefficient
- `ṡ`: Surface derivative **Benefits:**
- Thinner layer when surface derivative is small (near equilibrium)
- Thicker layer when surface derivative is large (during transients)
- Automatically adapts to system dynamics **Validation Rules:**
```python

if self.boundary_layer_slope < 0: raise ValueError("boundary_layer_slope must be non-negative")
``` **Typical Range:** `0.0 ≤ α ≤ 1.0`
**Default:** `α = 0.0` (constant boundary layer) ### 2.3 Switching Function Parameters #### 2.3.1 Switch Method (`switch_method`) ```python
switch_method: Literal["tanh", "linear", "sign"] = field(default="tanh")
``` **Mathematical Foundation:** 1. **Hyperbolic Tangent ("tanh")**: ``` switch(s, ε) = tanh(s/ε) ``` - Smooth, differentiable everywhere - Asymptotically approaches ±1 - Good chattering reduction 2. **Linear Saturation ("linear")**: ``` switch(s, ε) = clip(s/ε, -1, 1) ``` - Piecewise linear, continuous - Exact linear behavior within boundary layer - Simple computation 3. **Sign Function ("sign")**: ``` switch(s, ε) = sign(s) ``` - Discontinuous switching (traditional SMC) - Maximum performance, maximum chattering - Use only with very small ε **Selection Guidelines:**

- **"tanh"**: Default choice for most applications
- **"linear"**: When simple linear interpolation is preferred
- **"sign"**: Only for theoretical analysis or with hardware switching ### 2.4 Numerical Parameters #### 2.4.1 Regularization (`regularization`) ```python
regularization: float = field(default=1e-10) # Matrix regularization ρ > 0
``` **Mathematical Foundation:**
Prevents numerical issues in equivalent control computation: ```
u_eq = -(L·M⁻¹·B + ρI)⁻¹ · L·M⁻¹·F
``` Where:

- `ρ`: Regularization parameter
- `I`: Identity matrix
- Ensures matrix is always invertible **Validation Rules:**
```python
if self.regularization <= 0: raise ValueError("regularization must be positive")
``` **Typical Range:** `1e-12 ≤ ρ ≤ 1e-6`

**Default:** `ρ = 1e-10` #### 2.4.2 Controllability Threshold (`controllability_threshold`) ```python
controllability_threshold: Optional[float] = field(default=None)
``` **Mathematical Foundation:**
Minimum condition number for equivalent control computation: ```
if cond(L·M⁻¹·B) > threshold: u_eq = 0 # Fall back to switching control only
``` **Auto-computation:**

When `None`, automatically computed as:
```python
def get_effective_controllability_threshold(self) -> float: if self.controllability_threshold is not None: return self.controllability_threshold # Default: scale with surface gains return 0.05 * (self.k1 + self.k2)
``` **Validation Rules:**

```python
if self.controllability_threshold is not None and self.controllability_threshold <= 0: raise ValueError("controllability_threshold must be positive when specified")
``` #### 2.4.3 Dynamics Model (`dynamics_model`) ```python

dynamics_model: Optional[object] = field(default=None, compare=False)
``` **Purpose:**
- Optional plant model for equivalent control computation
- When `None`, equivalent control is disabled
- Must implement required dynamics interface **Interface Requirements:**
```python

class DynamicsModel: def compute_dynamics(self, state: np.ndarray) -> Tuple[np.ndarray, np.ndarray]: """Return (F, B) where ẋ = F(x) + B(x)u""" pass def get_mass_matrix(self, state: np.ndarray) -> np.ndarray: """Return mass matrix M(x)""" pass
``` ## 3. Property Accessors The configuration provides convenient property accessors for individual gains: ```python
# example-metadata:
# runnable: false @property
def k1(self) -> float: """Joint 1 position gain.""" return self.gains[0] @property
def k2(self) -> float: """Joint 2 position gain.""" return self.gains[1] @property
def lam1(self) -> float: """Joint 1 velocity gain (λ₁).""" return self.gains[2] @property
def lam2(self) -> float: """Joint 2 velocity gain (λ₂).""" return self.gains[3] @property
def K(self) -> float: """Switching gain.""" return self.gains[4] @property
def kd(self) -> float: """Derivative gain.""" return self.gains[5]
``` Additional utility methods: ```python
# example-metadata:

# runnable: false def get_surface_gains(self) -> List[float]: """Get sliding surface gains [k1, k2, λ1, λ2].""" return self.gains[:4] def get_effective_controllability_threshold(self) -> float: """Get effective controllability threshold.""" # Implementation shown above def to_dict(self) -> dict: """Convert configuration to dictionary.""" # Returns serializable dictionary @classmethod

def from_dict(cls, config_dict: dict, dynamics_model=None) -> 'ClassicalSMCConfig': """Create configuration from dictionary.""" # Factory method for deserialization @classmethod
def create_default(cls, gains: List[float], max_force: float = 100.0, dt: float = 0.01, boundary_layer: float = 0.01, **kwargs) -> 'ClassicalSMCConfig': """Create configuration with sensible defaults.""" # Factory method with defaults
``` ## 4. Edge Case Handling ### 4.1 Zero Gains **Problem:** Zero gains violate stability requirements and can cause division by zero. **Solution:** Strict validation prevents zero gains:
```python

if any(g <= 0 for g in [k1, k2, lam1, lam2]): raise ValueError("Surface gains must be positive for stability")
``` ### 4.2 Negative Gains **Problem:** Negative gains can make the sliding dynamics unstable. **Solution:** Validation ensures all critical gains are positive:
```python

if K <= 0: raise ValueError("Switching gain K must be positive")
if kd < 0: raise ValueError("Derivative gain kd must be non-negative")
``` ### 4.3 Very Small Boundary Layer **Problem:** Extremely small boundary layer approaches discontinuous switching. **Handling:**
- Allow small values but warn in documentation
- Numerical switching functions handle small ε gracefully
- Minimum practical value: ε ≥ 1e-6 ### 4.4 Very Large Boundary Layer **Problem:** Large boundary layer reduces control performance. **Handling:**
- No upper limit enforced (user responsibility)
- Documentation provides guidelines
- Recommended maximum: ε ≤ 0.1 ### 4.5 Missing Dynamics Model **Problem:** Equivalent control requires plant model. **Solution:**
- When `dynamics_model=None`, equivalent control is disabled
- Controller falls back to switching + derivative control only
- Graceful degradation without errors ## 5. Validation Test Examples ### 5.1 Valid Configuration ```python
# example-metadata:
# runnable: false config = ClassicalSMCConfig( gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0], # All positive max_force=100.0, # Positive force limit dt=0.01, # 100 Hz control rate boundary_layer=0.01, # 1% boundary layer boundary_layer_slope=0.1, # Mild adaptation switch_method="tanh", # Smooth switching regularization=1e-10, # Standard regularization controllability_threshold=0.5, # Moderate threshold dynamics_model=None # No equivalent control
)
``` ### 5.2 Invalid Configurations ```python
# example-metadata:

# runnable: false # Zero gain - should raise ValueError

invalid_config = ClassicalSMCConfig( gains=[0.0, 3.0, 4.0, 2.0, 10.0, 1.0], # k1 = 0! max_force=100.0, dt=0.01, boundary_layer=0.01
) # Negative switching gain - should raise ValueError
invalid_config = ClassicalSMCConfig( gains=[5.0, 3.0, 4.0, 2.0, -10.0, 1.0], # K < 0! max_force=100.0, dt=0.01, boundary_layer=0.01
) # Zero boundary layer - should raise ValueError
invalid_config = ClassicalSMCConfig( gains=[5.0, 3.0, 4.0, 2.0, 10.0, 1.0], max_force=100.0, dt=0.01, boundary_layer=0.0 # ε = 0!
)
``` ## 6. Configuration Migration and Compatibility ### 6.1 Version Compatibility The current configuration schema is designed to be backward compatible: - New optional parameters have sensible defaults
- Required parameters remain consistent
- Validation rules preserve existing behavior ### 6.2 Parameter Migration For updating from older configurations: ```python
# example-metadata:
# runnable: false def migrate_legacy_config(legacy_dict: dict) -> ClassicalSMCConfig: """Migrate legacy configuration format.""" # Map old parameter names to new names if 'epsilon' in legacy_dict: legacy_dict['boundary_layer'] = legacy_dict.pop('epsilon') if 'control_gains' in legacy_dict: legacy_dict['gains'] = legacy_dict.pop('control_gains') # Add missing defaults if 'boundary_layer_slope' not in legacy_dict: legacy_dict['boundary_layer_slope'] = 0.0 if 'switch_method' not in legacy_dict: legacy_dict['switch_method'] = "tanh" return ClassicalSMCConfig.from_dict(legacy_dict)
``` ## 7. Performance Considerations ### 7.1 Validation Overhead - Validation occurs only at configuration creation

- Runtime overhead is minimal (no repeated validation)
- Validation complexity: O(1) for all checks ### 7.2 Memory Usage - Configuration is immutable (frozen dataclass)
- Small memory footprint (~100 bytes)
- Safe for sharing between controller instances ### 7.3 Serialization - Full support for JSON serialization via `to_dict()`
- Compatible with YAML configuration files
- Preserves all parameter values and types ## References 1. Utkin, V. I. (1992). *Sliding Modes in Control and Optimization*. Springer-Verlag. 2. Edwards, C., & Spurgeon, S. (1998). *Sliding Mode Control: Theory and Applications*. CRC Press. 3. Young, K. D., Utkin, V. I., & Özgüner, Ü. (1999). A control engineer's guide to sliding mode control. *IEEE Transactions on Control Systems Technology*, 7(3), 328-342. 4. Bartolini, G., Ferrara, A., & Usai, E. (1998). Chattering avoidance by second-order sliding mode control. *IEEE Transactions on Automatic Control*, 43(2), 241-246.