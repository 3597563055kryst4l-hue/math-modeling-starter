"""MCM Problem-Type Templates.

Each MCM problem has a distinct flavor:
  - A: Continuous / differential equations
  - B: Discrete / optimization
  - C: Data insights / big data
  - D: Operations research / network flow

These templates provide problem-specific config presets,
suggested models, and solver hints to accelerate the contest team.
"""
from typing import Any


PROBLEM_TEMPLATES: dict[str, dict[str, Any]] = {
    "A": {
        "name": "MCM Problem A — Continuous",
        "description": "Differential equations, physical modeling, continuous optimization",
        "suggested_models": ["ode_derivative", "curve_fit", "linear_regression"],
        "suggested_solver": "odeint",
        "config_preset": {
            "model": {"type": "ode_derivative", "params": {}},
            "solver": {"method": "RK45", "max_iter": 5000},
            "viz": {"format": "png", "dpi": 300},
        },
        "tip": "Focus on sensitivity analysis — small parameter changes should not destabilize the system.",
    },
    "B": {
        "name": "MCM Problem B — Discrete",
        "description": "Discrete math, graph theory, integer/network optimization",
        "suggested_models": ["linear_regression", "scipy_minimize"],
        "suggested_solver": "scipy_minimize",
        "config_preset": {
            "model": {"type": "scipy_minimize", "params": {}},
            "solver": {"method": "L-BFGS-B", "max_iter": 2000},
            "viz": {"format": "png", "dpi": 300},
        },
        "tip": "Prob B often involves combinatorial choices — try integer relaxation for solvability, then round.",
    },
    "C": {
        "name": "MCM Problem C — Data Insights",
        "description": "Large dataset analysis, pattern recognition, data mining",
        "suggested_models": ["linear_regression", "curve_fit", "ttest"],
        "suggested_solver": "linear_regression",
        "config_preset": {
            "model": {"type": "linear_regression", "params": {"alpha": 0.0}},
            "solver": {"method": "normal_equations", "max_iter": 1000},
            "viz": {"format": "png", "dpi": 300},
        },
        "tip": "EDA is critical for C. Use Phase 1 thoroughly — many datasets have missing values or outliers.",
    },
    "D": {
        "name": "MCM Problem D — Operations Research",
        "description": "Network flow, scheduling, resource allocation, logistics",
        "suggested_models": ["scipy_minimize", "linear_regression"],
        "suggested_solver": "scipy_minimize",
        "config_preset": {
            "model": {"type": "scipy_minimize", "params": {}},
            "solver": {"method": "SLSQP", "max_iter": 3000},
            "viz": {"format": "png", "dpi": 300},
        },
        "tip": "Formulate constraints carefully. Try linear programming relaxation before integer constraints.",
    },
}


def get_template(problem_id: str) -> dict[str, Any] | None:
    """Get template for a problem ID (case-insensitive, A/B/C/D)."""
    key = problem_id.strip().upper()
    return PROBLEM_TEMPLATES.get(key)


def apply_template_to_config(problem_id: str, base_config: dict[str, Any]) -> dict[str, Any]:
    """Merge a problem template into a base config dict.

    Template values take precedence over base_config.
    """
    template = get_template(problem_id)
    if template is None:
        return base_config

    merged = dict(base_config)
    preset = template.get("config_preset", {})
    for section, values in preset.items():
        if section not in merged:
            merged[section] = {}
        merged[section].update(values)
    return merged


def list_problems() -> list[dict[str, str]]:
    """List all available problem templates."""
    return [
        {"id": pid, "name": info["name"], "description": info["description"]}
        for pid, info in PROBLEM_TEMPLATES.items()
    ]


def run(problem_id: str = "", config: dict | None = None) -> dict[str, Any]:
    """Phase 2 helper: apply problem template to select model."""
    if not problem_id:
        return {
            "status": "HUMAN_GATE_REQUIRED",
            "message": "No problem selected. Available: " + ", ".join(PROBLEM_TEMPLATES.keys()),
            "available_problems": list_problems(),
        }

    template = get_template(problem_id)
    if template is None:
        return {
            "status": "error",
            "message": f"Unknown problem: {problem_id}. Available: {list(PROBLEM_TEMPLATES.keys())}",
            "available_problems": list_problems(),
        }

    # Build a config preset
    merged = apply_template_to_config(problem_id, config or {})
    return {
        "status": "template_applied",
        "problem_id": problem_id,
        "template": {
            "name": template["name"],
            "description": template["description"],
            "suggested_models": template["suggested_models"],
            "suggested_solver": template["suggested_solver"],
            "tip": template["tip"],
        },
        "config_preset": template["config_preset"],
    }