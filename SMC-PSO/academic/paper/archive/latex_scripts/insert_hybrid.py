#!/usr/bin/env python
"""Insert Hybrid Adaptive STA-SMC block diagram into research paper."""

insert_content = """
**Figure 3.4:** Hybrid Adaptive STA-SMC with mode switching

```
                                    ┌──────────────────────┐
                                    │  Mode Selector       │
State x → [Sliding Surface σ] ──→  │  |σ| vs σ_switch     │
                  │                 │  with hysteresis Δ   │
                  │                 └──────────┬───────────┘
                  │                            │
                  │                     ┌──────┴──────┐
                  │                     │             │
                  │                 Mode=STA      Mode=Adaptive
                  │                     │             │
                  │                     ▼             ▼
                  ├────────→ [STA Controller] → u_STA
                  │          (K₁, K₂, z)
                  │
                  └────────→ [Adaptive Controller] → u_Adaptive
                             (K(t), γ, β, δ)
                                     │             │
                                     └──────┬──────┘
                                            ▼
                              [Switch/Select based on Mode]
                                            │
                                            ▼
State x → [Equivalent Control u_eq] ──→  [+] → u → Plant
```

**Signal Flow:**
1. Measure state x = [x, θ₁, θ₂, ẋ, θ̇₁, θ̇₂]ᵀ
2. Compute sliding surface σ = λ₁θ₁ + λ₂θ₂ + k₁θ̇₁ + k₂θ̇₂
3. Compute equivalent control u_eq (model-based feedforward)
4. Evaluate mode selector:
   - If |σ| > σ_switch + Δ → Mode = STA
   - If |σ| < σ_switch - Δ → Mode = Adaptive
   - Otherwise → Keep previous mode (hysteresis)
5. Compute control based on mode:
   - STA mode: u_sw = -K₁|σ|^(1/2)·sign(σ) + z
   - Adaptive mode: u_sw = -K(t)·sat(σ/ε) - k_d·σ
6. Total control: u = u_eq + u_sw
7. Apply saturation: u_sat = clip(u, -20N, +20N)

**Implementation Notes:**

**Mode Switching Logic (Critical for Safety):**

1. **Hysteresis Implementation:**
   ```python
   def select_mode(sigma, sigma_switch, delta, current_mode):
       if abs(sigma) > sigma_switch + delta:
           return 'STA'
       elif abs(sigma) < sigma_switch - delta:
           return 'ADAPTIVE'
       else:
           return current_mode  # Stay in current mode
   ```

2. **State Continuity:** When switching modes, ensure control continuity:
   - Transfer integral state z from STA to Adaptive K(t)
   - Use smooth transition: u[k] = α·u_STA + (1-α)·u_Adaptive where α ∈ [0,1] based on hysteresis position

3. **Mode Initialization:**
   - Start in STA mode (typical for large initial errors)
   - Initialize z=0, K(t)=K_init
   - Track mode transitions for debugging

**Numerical Stability:**

- **Bumpless Transfer:** During mode switch, match initial conditions:
  - STA→Adaptive: Set K(t) = current equivalent switching gain
  - Adaptive→STA: Set z = accumulated adaptive correction
- **Anti-Windup:** Reset integral states (z or K) if control saturates for >100ms
- **Mode Chattering Prevention:** Enforce minimum dwell time (50ms) in each mode

**Common Pitfalls:**

1. **Mode chattering:** If Δ too small (<0.005), controller oscillates between modes → instability
2. **Discontinuous control:** Without bumpless transfer, u jumps at mode switches → excites high-frequency dynamics
3. **Incorrect state initialization:** Forgetting to transfer integral states causes transient spikes (>20% overshoot)
4. **Hysteresis too large:** If Δ > σ_switch/2, mode never switches → defeats hybrid design purpose
"""

# Read the original file
file_path = '.artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the insertion point (after "- Requires tuning both STA and Adaptive gains\n")
search_str = "- Requires tuning both STA and Adaptive gains\n"
pos = content.find(search_str)
if pos == -1:
    print("[ERROR] Could not find insertion point")
    exit(1)

# Insert after the line
insertion_point = pos + len(search_str)
new_content = content[:insertion_point] + insert_content + content[insertion_point:]

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("[OK] Hybrid Adaptive STA-SMC block diagram inserted successfully")
