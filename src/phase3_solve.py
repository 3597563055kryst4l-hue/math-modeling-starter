"""Phase 3: Solve — Dispatch the solver.

Takes a ModelSpec from Phase 2 and data from Phase 1, runs the solver.
Supports linear regression, scipy.optimize, scipy.integrate, and custom solvers.
"""
from typing import Any

import numpy as np
import scipy
import scipy.optimize as opt
import scipy.integrate as integrate
import scipy.stats as stats

# Check scipy version for MILP support
_SCIPY_HAS_MILP = False
try:
    from scipy.optimize import milp as _scipy_milp
    _SCIPY_HAS_MILP = True
except ImportError:
    pass


# ── Solver Registry ─────────────────────────────────────────────

SOLVER_REGISTRY: dict[str, Any] = {}


def register_solver(name: str):
    """Decorator to register a solver function."""
    def decorator(fn):
        SOLVER_REGISTRY[name] = fn
        return fn
    return decorator


# ═══════════════════════════════════════════════════════════════
# 1. Linear Regression (Normal Equations / SVD)
# ═══════════════════════════════════════════════════════════════

@register_solver("linear_regression")
def solve_lr(x: np.ndarray, y: np.ndarray, alpha: float = 0.0) -> dict[str, Any]:
    """Linear regression via normal equations with optional L2 regularization."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    # Add bias term
    X = np.c_[np.ones(x.shape[0]), x]
    n_features = X.shape[1]
    try:
        theta = np.linalg.inv(X.T @ X + alpha * np.eye(n_features)) @ X.T @ y
    except np.linalg.LinAlgError:
        theta = np.linalg.lstsq(X, y, rcond=None)[0]
    y_pred = X @ theta
    residuals = y - y_pred
    n = len(y)
    p = len(theta)
    rss = np.sum(residuals ** 2)
    tss = np.sum((y - np.mean(y)) ** 2)
    return {
        "coefficients": theta.tolist(),
        "residuals": residuals.tolist(),
        "rmse": float(np.sqrt(np.mean(residuals ** 2))),
        "r2": float(1 - rss / tss) if tss > 0 else 0.0,
        "adj_r2": float(1 - (rss / (n - p)) / (tss / (n - 1))) if tss > 0 and n > p else 0.0,
        "converged": True,
        "solver": "linear_regression",
    }


# ═══════════════════════════════════════════════════════════════
# 2. SciPy Minimize — General optimization
# ═══════════════════════════════════════════════════════════════

@register_solver("scipy_minimize")
def solve_scipy_minimize(
    objective_fn: callable,
    x0: np.ndarray,
    bounds: list | None = None,
    method: str = "L-BFGS-B",
    **kwargs,
) -> dict[str, Any]:
    """General-purpose optimization via scipy.optimize.minimize."""
    result = opt.minimize(
        objective_fn,
        x0=x0,
        bounds=bounds,
        method=method,
        options={"maxiter": kwargs.get("max_iter", 1000)},
    )
    return {
        "x_opt": result.x.tolist(),
        "fun": float(result.fun),
        "success": bool(result.success),
        "message": result.message,
        "nit": int(result.nit),
        "solver": "scipy_minimize",
        "converged": bool(result.success),
    }


# ═══════════════════════════════════════════════════════════════
# 3. Curve Fitting — Non-linear least squares
# ═══════════════════════════════════════════════════════════════

@register_solver("curve_fit")
def solve_curve_fit(
    model_fn: callable,
    xdata: np.ndarray,
    ydata: np.ndarray,
    p0: list | None = None,
    bounds: tuple | None = None,
) -> dict[str, Any]:
    """Non-linear least squares curve fitting via scipy.optimize.curve_fit."""
    if bounds is not None:
        popt, pcov = opt.curve_fit(model_fn, xdata, ydata, p0=p0, bounds=bounds,
                                    maxfev=10000)
    else:
        popt, pcov = opt.curve_fit(model_fn, xdata, ydata, p0=p0, maxfev=10000)
    perr = np.sqrt(np.diag(pcov))
    y_pred = model_fn(xdata, *popt)
    residuals = ydata - y_pred
    return {
        "popt": popt.tolist(),
        "perr": perr.tolist(),
        "residuals": residuals.tolist(),
        "rmse": float(np.sqrt(np.mean(residuals ** 2))),
        "solver": "curve_fit",
        "converged": True,
    }


# ═══════════════════════════════════════════════════════════════
# 4. ODE Integration
# ═══════════════════════════════════════════════════════════════

@register_solver("odeint")
def solve_odeint(
    deriv_fn: callable,
    y0: np.ndarray,
    t_span: np.ndarray,
    args: tuple = (),
) -> dict[str, Any]:
    """Solve ODE system via scipy.integrate.solve_ivp."""
    result = integrate.solve_ivp(
        deriv_fn, [t_span[0], t_span[-1]], y0, method="RK45",
        t_eval=t_span, args=args, rtol=1e-6, atol=1e-8,
    )
    # solve_ivp returns y shape (n_states, n_timesteps), transpose to (n_timesteps, n_states)
    return {
        "t": result.t.tolist(),
        "y": result.y.T.tolist(),
        "success": bool(result.success),
        "message": result.message,
        "solver": "odeint",
        "converged": bool(result.success),
    }


# ═══════════════════════════════════════════════════════════════
# 5. Root Finding
# ═══════════════════════════════════════════════════════════════

@register_solver("root_find")
def solve_root(
    func: callable,
    x0: np.ndarray,
    method: str = "hybr",
) -> dict[str, Any]:
    """Find roots of a system of equations via scipy.optimize.root."""
    result = opt.root(func, x0, method=method)
    return {
        "x_root": result.x.tolist(),
        "success": bool(result.success),
        "message": result.message,
        "solver": "root_find",
        "converged": bool(result.success),
    }


# ═══════════════════════════════════════════════════════════════
# 6. Hypothesis Test Wrapper
# ═══════════════════════════════════════════════════════════════

@register_solver("ttest")
def solve_ttest(sample1: np.ndarray, sample2: np.ndarray, equal_var: bool = True) -> dict[str, Any]:
    """Two-sample t-test."""
    t_stat, p_value = stats.ttest_ind(sample1, sample2, equal_var=equal_var)
    return {
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "solver": "ttest",
        "converged": True,
    }


# ═══════════════════════════════════════════════════════════════
# 7. Linear Programming — scipy.optimize.linprog
# ═══════════════════════════════════════════════════════════════

@register_solver("lp")
def solve_lp(
    c: np.ndarray,
    A_ub: np.ndarray | None = None,
    b_ub: np.ndarray | None = None,
    A_eq: np.ndarray | None = None,
    b_eq: np.ndarray | None = None,
    bounds: list | None = None,
    method: str = "highs",
) -> dict[str, Any]:
    """Linear programming via scipy.optimize.linprog.

    Minimize: c @ x
    Subject to: A_ub @ x <= b_ub, A_eq @ x == b_eq, bounds on x

    Args:
        c: Coefficients of the linear objective (n,).
        A_ub: Inequality constraint matrix (m, n).
        b_ub: Inequality constraint vector (m,).
        A_eq: Equality constraint matrix (p, n).
        b_eq: Equality constraint vector (p,).
        bounds: Sequence of (min, max) pairs for each variable.
                None means unbounded, (0, None) means non-negative.
        method: Solver method ('highs' recommended).
    """
    from scipy.optimize import linprog
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                     bounds=bounds, method=method)
    return {
        "x_opt": result.x.tolist() if result.x is not None else None,
        "fun": float(result.fun) if result.fun is not None else None,
        "success": bool(result.success),
        "message": result.message,
        "solver": "lp",
        "converged": bool(result.success),
    }


# ═══════════════════════════════════════════════════════════════
# 8. Mixed-Integer Linear Programming — scipy.optimize.milp
# ═══════════════════════════════════════════════════════════════

@register_solver("milp")
def solve_milp(
    c: np.ndarray,
    integrality: np.ndarray,
    A_ub: np.ndarray | None = None,
    b_ub: np.ndarray | None = None,
    A_eq: np.ndarray | None = None,
    b_eq: np.ndarray | None = None,
    bounds: list | None = None,
) -> dict[str, Any]:
    """Mixed-integer linear programming.

    Uses scipy.optimize.milp (SciPy >= 1.9.0) if available.
    Falls back to solving the LP relaxation if not.

    Minimize: c @ x
    Subject to: A_ub @ x <= b_ub, A_eq @ x == b_eq, bounds on x
               x_j integer where integrality[j] == 1

    Args:
        c: Coefficients of the linear objective (n,).
        integrality: Array of 0/1 flags, 1 = integer variable.
        A_ub: Inequality constraint matrix (m, n).
        b_ub: Inequality constraint vector (m,).
        A_eq: Equality constraint matrix (p, n).
        b_eq: Equality constraint vector (p,).
        bounds: Sequence of (min, max) pairs for each variable.
    """
    if _SCIPY_HAS_MILP:
        from scipy.optimize import milp as scipy_milp, LinearConstraint, Bounds
        constraints = []
        if A_ub is not None and b_ub is not None:
            constraints.append(LinearConstraint(A_ub, -np.inf, b_ub))
        if A_eq is not None and b_eq is not None:
            constraints.append(LinearConstraint(A_eq, b_eq, b_eq))

        # Convert list-of-tuples bounds to scipy Bounds object
        if bounds is not None:
            lb = [b[0] if b[0] is not None else -np.inf for b in bounds]
            ub = [b[1] if b[1] is not None else np.inf for b in bounds]
            converted_bounds = Bounds(lb, ub)
        else:
            converted_bounds = None

        result = scipy_milp(c=c, constraints=constraints,
                            bounds=converted_bounds, integrality=integrality)
        return {
            "x_opt": result.x.tolist() if result.x is not None else None,
            "fun": float(result.fun) if result.fun is not None else None,
            "success": bool(result.success),
            "message": result.message,
            "solver": "milp",
            "converged": bool(result.success),
        }
    else:
        # Fallback: LP relaxation (ignore integrality)
        result = solve_lp(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds)
        result["solver"] = "milp_relaxation"
        result["warning"] = "LP relaxation (scipy>=1.9.0 required for true MILP)"
        return result


# ═══════════════════════════════════════════════════════════════
# Generic dispatch
# ═══════════════════════════════════════════════════════════════

def solve_generic(model_spec: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    """Generic solver dispatch based on model spec name."""
    model_type = model_spec.get("name", "")

    if not model_type:
        return {"status": "HUMAN_GATE_REQUIRED", "message": "No model specified. Run Phase 2 first to select a model."}

    solver_fn = SOLVER_REGISTRY.get(model_type)

    if solver_fn is None:
        return {"status": "error", "message": f"Solver for '{model_type}' not implemented. Available: {list(SOLVER_REGISTRY.keys())}"}

    try:
        if model_type == "linear_regression":
            x = data.get("x")
            y = data.get("y")
            if x is None or y is None:
                return {"status": "error", "message": "Linear regression requires x and y data."}
            alpha = model_spec.get("params", {}).get("alpha", 0.0)
            result = solver_fn(x, y, alpha=alpha)
        else:
            # For other solvers, pass data as kwargs
            result = solver_fn(**data)

        result["status"] = "solved"
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── Run entry point ─────────────────────────────────────────────

def run(model_spec: dict | None = None, data: dict | None = None,
        config: dict | None = None) -> dict[str, Any]:
    """Execute Phase 3: run the solver."""
    if model_spec is None:
        return {"status": "HUMAN_GATE_REQUIRED", "message": "No model spec provided. Run Phase 2 first."}
    if data is None:
        return {"status": "HUMAN_GATE_REQUIRED", "message": "No data provided. Run Phase 1 first."}
    result = solve_generic(model_spec, data)
    result.setdefault("status", "solved")
    return result