# FDE Loop Log — Iteration 3

> **Loop**: 3
> **Date**: 2026-06-11
> **Focus**: LP/MILP solvers, scenario batching, state variable checks, Phase 0 framework, prompt update

---

## What was done

### 1. LP + MILP Solvers (Task 2)

Phase 3 now has **8 solvers**. Two new entries:

| Solver | Name | Method | Use Case |
|--------|------|--------|----------|
| #7 — LP | `solve_lp` | `scipy.optimize.linprog` (HiGHS) | Resource allocation, scheduling, any linear constraints |
| #8 — MILP | `solve_milp` | `scipy.optimize.milp` (>=1.9.0) | 0/1 decisions, integer variables, discrete optimization |

Both support inequality constraints (A_ub @ x <= b_ub), equality constraints (A_eq @ x == b_eq), and variable bounds.

MILP auto-detects scipy version — fallback to LP relaxation if scipy < 1.9.0.

### 2. Scenario Batch Runner (Task 3)

`src/utils.py` gained 3 new functions:

- `run_scenarios(solver_fn, param_grid)` — Run a solver over N parameter sets, collect results
- `aggregate_scenarios(results)` — Summarize (mean/std/min/max/p25/p50/p75 per field)
- `categorize_scenarios(agg, field, thresholds)` — 2-tier (satisfied/not) or 3-tier (full/partial/none) classification

### 3. State Variable Check (Task 3)

`src/phase4_validate.py` gained `check_state_variables()`:

- Validates trajectory against min/max bounds
- Checks initial and terminal state match expectations
- Detects NaN/Inf values
- Designed for battery SOC, tank levels, queue lengths

### 4. Phase 0 Restructured (Task 4)

`phase0_context.run()` now outputs a structured problem framework instead of dummy "x=自变量, y=因变量" variables:

```
system_components: 物理实体列表
decision_variables: 决策变量（符号/类型/范围）
constraints: 约束条件（等式/不等式）
objective: 目标函数
external_parameters: 外部给定参数
subproblems: 每问的输入/输出/类型
```

Also added BUILTIN_FRAMEWORKS presets for MCM A/B/C/D with focus hints.

### 5. CLAUDE.md Updated (Task 5)

Added:
- Section 7: "src/ 使用原则" — 3 rules against algorithm laziness
- Full tool table covering all src/ Phase modules and functions
- Expanded `FDE_ARCHITECTURE.md` Phase summary

### 6. Tests (96 total ✅)

| File | Tests | Coverage |
|------|-------|----------|
| `test_phase3_solve.py` | +5 (LP, MILP basic, MILP binary) | 22 total |
| `test_phase4_validate.py` | +5 (state variable: pass/violate/init/term/nan) | 18 total |
| `test_phase0_context.py` | +5 (framework sections/ABCD/missing_id/run) | 9 total |
| `test_utils.py` | +7 (NEW: batch scenarios, aggregate, categorize) | 7 total |
| All others | unchanged | 40 total |

**96 passed, 0 failed in 1.80s**

---

## Next Steps

- [ ] Add pulp/ortools solver as optional backend for MILP (higher performance)
- [ ] Add time-series cross-validation (walk-forward) to Phase 4
- [ ] Consider adding inverse problem / parameter estimation support
- [ ] Add interactive notebook tutorials

---

*Written by dataforcoder loop. Auto-generated 2026-06-11.*
