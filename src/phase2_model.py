"""Phase 2: Model — Specify the mathematical model.

HUMAN GATE: The contest team must select the model type.
This module provides a registry of common models and a way to configure them.
"""
from typing import Any, Callable
from dataclasses import dataclass, field


@dataclass
class ModelSpec:
    """A model specification — what to solve and how."""
    name: str
    description: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    solver_hint: str = "auto"
    is_selected: bool = False


# ── Model Registry ──────────────────────────────────────────────

MODEL_REGISTRY: dict[str, Callable[[dict[str, Any]], ModelSpec]] = {}


def register(name: str):
    """Decorator to register a model builder."""
    def decorator(fn):
        MODEL_REGISTRY[name] = fn
        return fn
    return decorator


@register("linear_regression")
def linear_regression(params: dict[str, Any]) -> ModelSpec:
    return ModelSpec(
        name="linear_regression",
        description="Ordinary least squares linear regression",
        params={"alpha": params.get("alpha", 1.0)},
        solver_hint="scipy.minimize",
    )


@register("arima")
def arima(params: dict[str, Any]) -> ModelSpec:
    return ModelSpec(
        name="arima",
        description="Autoregressive Integrated Moving Average for time series",
        params={"p": params.get("p", 1), "d": params.get("d", 1), "q": params.get("q", 1)},
        solver_hint="statsmodels.ARIMA",
    )


@register("svm")
def svm(params: dict[str, Any]) -> ModelSpec:
    return ModelSpec(
        name="svm",
        description="Support Vector Machine for classification",
        params={"C": params.get("C", 1.0), "kernel": params.get("kernel", "rbf")},
        solver_hint="sklearn.svm",
    )


def build_model(model_type: str, params: dict[str, Any] | None = None) -> ModelSpec:
    """Build a ModelSpec from the registry."""
    if params is None:
        params = {}
    builder = MODEL_REGISTRY.get(model_type)
    if builder is None:
        available = list(MODEL_REGISTRY.keys())
        raise ValueError(f"Unknown model type '{model_type}'. Available: {available}")
    spec = builder(params)
    spec.is_selected = True
    return spec


def run(model_type: str = "", config: dict | None = None) -> dict[str, Any]:
    """Execute Phase 2: build model spec from config."""
    if config is None:
        config = {}
    model_cfg = config.get("model", {})
    model_type = model_type or model_cfg.get("type", "")
    if not model_type:
        return {
            "status": "HUMAN_GATE_REQUIRED",
            "message": "No model type selected. Team must choose a model.",
            "available_models": list(MODEL_REGISTRY.keys()),
        }
    params = model_cfg.get("params", {})
    spec = build_model(model_type, params)
    return {
        "status": "spec_ready",
        "model": {
            "name": spec.name,
            "description": spec.description,
            "params": spec.params,
            "solver_hint": spec.solver_hint,
        },
    }