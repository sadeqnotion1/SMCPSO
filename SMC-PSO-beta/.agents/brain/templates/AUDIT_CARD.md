# AUDIT CARD -- <module path, e.g. src/plant/>

> Copy this file to `brain/audits/<module>.md` when you start auditing a module.
> A module cannot be marked [DONE] in STATE.md until this card is complete and the gate passes.
> ASCII markers only. Severities: [P0] wrong/unsafe, [P1] bug, [P2] slop, [P3] nit.

- **Module:** `src/.../`
- **Source ref:** `SMC-PSO/src/.../`
- **Branch:** `migration/<module>`
- **Date / session:**
- **Status:** [TODO] | [WIP] | [DONE]

## Lens A -- AI-slop / code quality
| # | File:line | Finding | Sev | Fix / status |
|---|-----------|---------|-----|--------------|
| A1 |  |  |  |  |

## Lens B -- scientific / mathematical correctness
| # | What it should match (equation / reference) | Finding | Sev | Fix / status |
|---|----------------------------------------------|---------|-----|--------------|
| B1 |  |  |  |  |

(Plant: M PD + energy + equilibria. Controllers: sliding surface, Vdot<=0, STA gains,
adaptive boundedness, chattering, saturation. Optimization: fitness penalizes instability,
bounds, reproducibility, hold-out. Numerics: integrator, Numba parity, no NaN. Stats: CI/t-test
assumptions, sample size.)

## Lens C -- tests + numeric parity
- [ ] Real tests with real assertions added/ported
- [ ] Coverage: overall >= 85% / critical >= 95% / safety-critical = 100%
- [ ] Parity harness passes (rtol/atol: ______ )
- [ ] Property/invariant tests added (which: ______ )

## Gate decision
- [ ] [P0] = 0 open
- [ ] [P1] = 0 open
- [ ] Parity pass (or documented, justified divergence)
- [ ] Coverage gate met
- [ ] No emojis / no `python3` / no stray magic numbers
- **Decision:** ACCEPT to trunk  |  HOLD on branch
- **Notes / deliberate divergences (-> DECISIONS.md):**
