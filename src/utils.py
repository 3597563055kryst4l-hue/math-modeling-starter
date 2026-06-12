"""Shared utilities for all phases."""

from pathlib import Path
from typing import Any
import json
import numpy as np


def ensure_dir(path: str | Path) -> Path:
    """Ensure a directory exists and return it as a Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_json(data: Any, path: str | Path) -> str:
    """Save data as JSON."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return str(p)


def load_json(path: str | Path) -> Any:
    """Load JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def timestamp() -> str:
    """Return a compact timestamp string."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ── Batch scenario runner ──────────────────────────────────────────

def run_scenarios(solver_fn: callable, param_grid: list[dict],
                  n_jobs: int = 1, progress: bool = True) -> list[dict]:
    """Run a solver function over multiple scenarios and aggregate results.

    Each scenario is a dict of keyword arguments passed to solver_fn.
    Useful for 24-scenario problems (wind/solar combinations, etc.).

    Args:
        solver_fn: A callable that takes **kwargs and returns a dict.
        param_grid: List of kwarg dicts, one per scenario.
        n_jobs: Number of parallel jobs. 1 = sequential.
        progress: Print progress bar (sequential only).

    Returns:
        List of result dicts, one per scenario, each with a 'scenario_idx' field.
    """
    results = []
    total = len(param_grid)
    for i, params in enumerate(param_grid):
        if progress:
            print(f"[batch] scenario {i+1}/{total}")
        try:
            result = solver_fn(**params)
            result.setdefault("status", "solved")
            result["scenario_idx"] = i
            result["scenario_params"] = params
            results.append(result)
        except Exception as e:
            results.append({
                "scenario_idx": i,
                "scenario_params": params,
                "status": "error",
                "error": str(e),
            })
    return results


def aggregate_scenarios(results: list[dict],
                        key_fields: list[str] | None = None
                        ) -> dict[str, Any]:
    """Aggregate batch scenario results into summary statistics.

    Args:
        results: List of result dicts from run_scenarios.
        key_fields: Numeric fields to aggregate (auto-detected if None).

    Returns:
        dict with counts, means, stds, distributions.
    """
    successful = [r for r in results if r.get("status") != "error"]
    errors = [r for r in results if r.get("status") == "error"]

    # Auto-detect numeric fields if not specified
    if key_fields is None and successful:
        key_fields = [k for k, v in successful[0].items()
                      if isinstance(v, (int, float)) and k not in ("scenario_idx",)]

    agg = {}
    if key_fields:
        for field in key_fields:
            values = [r.get(field) for r in successful if r.get(field) is not None]
            if values:
                agg[field] = {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values)),
                    "p25": float(np.percentile(values, 25)),
                    "p50": float(np.percentile(values, 50)),
                    "p75": float(np.percentile(values, 75)),
                    "all": values,
                }

    # Categorization helper: classify scenarios by threshold
    return {
        "n_total": len(results),
        "n_success": len(successful),
        "n_error": len(errors),
        "success_rate": len(successful) / len(results) if results else 0.0,
        "aggregates": agg,
        "error_details": [{"idx": r["scenario_idx"], "msg": r.get("error", "")} for r in errors],
    }


def categorize_scenarios(aggregated: dict, field: str,
                          threshold_high: float, threshold_low: float | None = None
                          ) -> dict[str, Any]:
    """Categorize scenarios by meeting/not meeting a threshold.

    Useful for "fully satisfied / partially satisfied / not satisfied"
    classifications in contest problems.

    Args:
        aggregated: Output from aggregate_scenarios.
        field: Field name to categorize.
        threshold_high: Values >= this are "fully satisfied".
        threshold_low: Values between this and threshold_high are "partially".
                       If None, only binary classification is done.

    Returns:
        dict with counts and indices per category.
    """
    if field not in aggregated.get("aggregates", {}):
        return {"error": f"Field '{field}' not found in aggregates"}

    all_values = aggregated["aggregates"][field]["all"]

    if threshold_low is None:
        satisfied = [i for i, v in enumerate(all_values) if v >= threshold_high]
        unsatisfied = [i for i, v in enumerate(all_values) if v < threshold_high]
        return {
            "n_satisfied": len(satisfied),
            "n_unsatisfied": len(unsatisfied),
            "satisfied_indices": satisfied,
            "unsatisfied_indices": unsatisfied,
            "threshold": threshold_high,
        }
    else:
        full = [i for i, v in enumerate(all_values) if v >= threshold_high]
        partial = [i for i, v in enumerate(all_values) if threshold_low <= v < threshold_high]
        none = [i for i, v in enumerate(all_values) if v < threshold_low]
        return {
            "n_full": len(full),
            "n_partial": len(partial),
            "n_none": len(none),
            "full_indices": full,
            "partial_indices": partial,
            "none_indices": none,
            "threshold_high": threshold_high,
            "threshold_low": threshold_low,
        }