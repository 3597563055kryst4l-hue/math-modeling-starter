# FDE Architecture — Math Modeling Contest Scaffold

> Forward Deployed Engineer paradigm adapted for mathematical modeling competitions (MCM/ICM, CUMCM).
> **Core thesis**: The coder is not the modeler. The architect is not the competitor. This scaffold is a **platform** for the contest team — you (the FDE) build the rails, they run the race.

---

## 1. FDE Mindset

| Principle | In Math Modeling Context |
|-----------|--------------------------|
| **Site-aware context** | Understand contest format (4–5 day sprints, A/B/C/D problem types, 20-page paper limit) |
| **End-to-end delivery** | From raw contest data → final paper-ready figures, tables, and sensitivity summaries |
| **Rapid prototype iteration** | "Try a model in 15 min" — throw away and redo is expected, not failure |
| **Human at phase gates** | Model selection, assumption validation, result interpretation → those are the modelers' job. Data ETL, solving, viz, report assembly → the scaffold's job. |

**Division of labor:**

| Who | Owns |
|-----|------|
| **Contest team (humans)** | Problem interpretation, model selection, assumption decisions, result narrative |
| **FDE (you)** | Code scaffold, phase runner, data plumbing, solver dispatch, viz pipeline, report boilerplate |

---

## 2. Phase-Gate Architecture

```
 ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
 │ Phase 0  │ → │ Phase 1  │ → │ Phase 2  │ → │ Phase 3  │ → │ Phase 4  │ → │ Phase 5  │ → │ Phase 6  │
 │ Context  │   │  Data    │   │  Model   │   │  Solve   │   │Validate  │   │  Viz     │   │  Report  │
 └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
      ↑              ↑              ↑              ↑              ↑              ↑              ↑
   human:        human:        HUMAN         human:        human:        human:        human:
   read-prob     inspect      GATE:         monitor,      sanity-       pick figs,    write
                 data         pick model    tune params   check, sens   polish        sections
```

### Phase Details

| Phase | Module | Input | Output | Human Gate |
|-------|--------|-------|--------|------------|
| **0 — Context** | `phase0_context.py` | Problem statement PDF | Structured problem framework (components, variables, constraints, objective, params) | Read problem, fill in framework skeleton |
| **1 — Data** | `phase1_data.py` | Raw data files (CSV, Excel, TXT) | Cleaned DataFrame, EDA stats, missing-value report | Inspect EDA, flag outliers |
| **2 — Model** | `phase2_model.py` | Cleaned data + problem context | Model specification, parameter bounds, solver choice | **YES — select model type** |
| **3 — Solve** | `phase3_solve.py` | Model spec → runs solver | Solution vectors, objective values, convergence logs | Monitor, tune if diverges |
| | | | *Solvers: LR, LP, MILP, scipy.minimize, curve_fit, ODE, root-find, t-test* |
| **4 — Validate** | `phase4_validate.py` | Solution + data | Residuals, AIC/BIC, k-fold CV, **state variable checks**, sensitivity tables | Sanity-check results |
| **5 — Viz** | `phase5_viz.py` | Validation results | Publication-quality figures (PNG, PDF) | Pick winners from candidate plots |
| **6 — Report** | `phase6_report.py` | All prior outputs | Markdown/LaTeX tables, summary stats, export bundle | Write / paste into paper |

---

## 3. How the FDE Works Day-to-Day

### Init (Day 1, Contest Start)
```bash
python -m src.run phase=0 problem=<which-problem>
# → Sets up problem context, creates output/<timestamp>/
```

### Iterate (Days 1–4)
```bash
# FDE tweaks solver, modeler picks model — both work in parallel
python -m src.run phase=1   # Re-run data prep with new filters
python -m src.run phase=2   # Re-select model
python -m src.run phase=3   # Re-solve
```

### Team asks "what if we try X?"
```bash
# FDE writes a quick Phase 3 variant
# → 5 lines in phase3_solve.py or a new solver subclass
python -m src.run phase=3 solver=variant_b
```

### Paper Sprint (Day 4–5)
```bash
# Batch generate all figures, tables, sensitivity stats
python -m src.run phase=5 output=final
python -m src.run phase=6 export=paper

# Run scenario batch (e.g., 24 wind/solar scenarios)
python -c "from src.utils import run_scenarios, aggregate_scenarios; ..."
```

---

## 4. File Structure After FDE Transformation

```
root/
├── src/
│   ├── __init__.py
│   ├── run.py                    # Entry point: phase runner CLI
│   ├── phase0_context.py         # Problem context & metadata
│   ├── phase1_data.py            # Data reading, cleaning, EDA
│   ├── phase2_model.py           # Model specification (abstract + registry)
│   ├── phase3_solve.py           # Solver dispatch (numeric, opt, simulation)
│   ├── phase4_validate.py        # Validation + sensitivity
│   ├── phase5_viz.py             # Visualization pipeline
│   ├── phase6_report.py          # Report generation (tables, export)
│   ├── runner.py                 # PhaseRunner orchestrator
│   └── utils.py                  # Shared utilities
├── config/
│   └── config.yaml               # Phase-aware config
├── data/                         # Raw data (copy from contest here)
├── output/                       # Timestamped run outputs
├── notebooks/                    # Scratch exploration (modeler territory)
├── dataforcoder/                 # FDE logs per loop
├── tests/
│   ├── test_phase1_data.py
│   ├── test_phase3_solve.py
│   └── ...
├── pyproject.toml
├── README.md
└── FDE_ARCHITECTURE.md           # ← This file
```

---

## 5. Config-Driven Workflow

`config/config.yaml` is the single source of truth for the current run:

```yaml
contest:
  name: "2026 MCM Problem C"
  phase: 2                    # current phase gate
  output_dir: "output/002"

data:
  raw_path: "data/raw.csv"
  cleaned_path: "output/002/cleaned.csv"

model:
  type: "linear_regression"   # or "arima", "svm", "custom"
  params:
    alpha: 0.01

solver:
  method: "scipy.minimize"
  max_iter: 1000

viz:
  format: "png"
  dpi: 300
```

The runner reads `config.phase` to decide which phases to execute. Phases before it are assumed complete; the current phase runs with the option to re-run any earlier phase.

---

## 6. FDE Logs (dataforcoder/)

Every `/loop` iteration writes a markdown file at `dataforcoder/YYYY-MM-DD_HHMM-loop-log.md` with:
1. What was attempted this iteration
2. What succeeded / failed / needs human input
3. Next planned actions
4. Any phase-gate transitions triggered

These logs are for **developer handoff** — the next FDE (or the same one in the next loop) can pick up exactly where work stopped.

---

## 7. Key Decisions / Tradeoffs

| Decision | Rationale |
|----------|-----------|
| Flat phase modules (not a package per phase) | Simpler imports, faster iteration. Math modeling projects are 4 days — deep nesting hurts, not helps. |
| PhaseRunner orchestrates but does NOT own logic | Each phase module is independently importable and testable. Runner just calls them in order. |
| Human gates are DOCUMENTED not ENFORCED | We can't enforce human review in code. Instead, the runner logs `HUMAN GATE: confirm model choice` and pauses if `config.human_gate: true`. |
| Config is YAML, not CLI args-only | YAML is team-accessible. The modeler (non-coder) can edit `model.type` without touching Python. CLI args override YAML. |
| No database, no API | Time horizon is 4 days. Files + folders + YAML is the right persistence layer. |

---

*Architecture designed 2026-06-11. Last updated: [loop-iteration].*