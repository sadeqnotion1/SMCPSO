#!/usr/bin/env python
"""Insert STA block diagram into research paper."""

insert_content = """
**Figure 3.3:** Super-Twisting Algorithm (STA) block diagram

```
State x → [Sliding Surface σ] → [|σ|^(1/2) · sign(σ)] → [×] ← K₁
                  │                                       │
                  │                                       ▼
                  └────────→ [sign(σ)] → [Integrator z] → [+] → u_STA
                                           ▲              ▲
                                           │              │
                             K₂ ───────────┘              │
                                                          │
State x → [Equivalent Control u_eq] ─────────────────────┘ → [+] → u → Plant
```

**Signal Flow:**
1. Measure state x = [x, θ₁, θ₂, ẋ, θ̇₁, θ̇₂]ᵀ
2. Compute sliding surface σ = λ₁θ₁ + λ₂θ₂ + k₁θ̇₁ + k₂θ̇₂
3. Compute equivalent control u_eq (model-based feedforward)
4. Compute proportional term: -K₁|σ|^(1/2)·sign(σ)
5. Compute integral state: ż = -K₂·sign(σ)
6. Sum STA terms: u_STA = -K₁|σ|^(1/2)·sign(σ) + z
7. Total control: u = u_eq + u_STA
8. Apply saturation: u_sat = clip(u, -20N, +20N)

**Implementation Notes:**

**Discretization (dt = 0.01s):**

1. **Fractional Power Term:** |σ|^(1/2) can cause numerical issues for small σ. Use safety threshold:
   ```math
   |σ|^{1/2} = \\begin{cases}
   \\sqrt{|\\sigma|} & |\\sigma| > 10^{-6} \\\\
   0 & \\text{otherwise}
   \\end{cases}
   ```

2. **Integral State Update:** Use backward Euler for stability:
   ```math
   z[k+1] = z[k] - K_2 \\cdot \\text{sign}(\\sigma[k]) \\cdot dt
   ```

3. **Sign Function Smoothing:** Replace discontinuous sign with smooth saturation:
   ```math
   \\text{sign}(\\sigma) \\approx \\tanh(\\sigma / \\epsilon), \\quad \\epsilon = 0.01
   ```

**Numerical Stability:**

- **Integral Windup:** Clip z to prevent unbounded growth: z ∈ [-100, +100]
- **Division by Zero:** Check |σ| > ε_min before computing fractional power
- **Overflow Protection:** Clip u_STA before adding to u_eq: u_STA ∈ [-50N, +50N]

**Common Pitfalls:**

1. **Instability from violating Lyapunov conditions:** Ensure K₁² ≥ 2K₂d̄ where d̄ is disturbance bound (~1.0 for DIP)
2. **Integral windup:** Without anti-windup (z clamping), integral state can grow unbounded during saturation
3. **Chattering from small ε:** If ε<0.005, sign function becomes too sharp → high-frequency switching
4. **Slow convergence from small K₁:** If K₁<8.0, reaching time increases beyond acceptable limits (>5s)
"""

# Read the original file
file_path = '.artifacts/research/papers/LT7_journal_paper/LT7_RESEARCH_PAPER.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the insertion point (after "- Less intuitive than classical SMC\n")
search_str = "- Less intuitive than classical SMC\n"
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

print("[OK] STA block diagram inserted successfully")
