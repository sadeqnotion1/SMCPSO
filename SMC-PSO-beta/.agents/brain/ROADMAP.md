# ROADMAP — migration milestones

> Only the **current** milestone is active. Don't pull work forward. Repo:
> https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## ✅ M0 — Scaffold + brain (DONE-ish)
- Clean beta scaffold (`config.yaml`, `requirements.txt`, `setup.py`, `src/`).
- `.agents/` brain installed and filled. ← you are here

## 🟦 M1 — Controllers (ACTIVE)
- Port `src/controllers/` (classical, sta, adaptive, hybrid) + `factory.py`.
- Controllers instantiate from `config.yaml`.

## ⬜ M2 — Plant + core simulation engine
- Port `src/plant/` (simplified / full nonlinear / low-rank).
- Port `src/core/` (`simulation_runner`, `vector_sim`, `safety_guards`).
- One end-to-end simulation runs in beta.

## ⬜ M3 — Optimization (PSO)
- Port `src/optimization/` (PSO algorithms, cost objectives, results).
- A PSO tuning run produces optimized gains.

## ⬜ M4 — Analysis, interfaces, utils + entry points
- Port `src/analysis/`, `src/interfaces/` (HIL), `src/utils/`.
- Add `simulate.py` CLI and the Streamlit dashboard.

## ⬜ M5 — Tests, docs, parity sign-off
- Port `tests/` (pytest) green in beta.
- Confirm numeric parity vs. source on a benchmark set; refresh docs + graph.
