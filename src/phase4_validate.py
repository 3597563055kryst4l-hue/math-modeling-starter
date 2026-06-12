"""Phase 4: Validate — Sanity-check, sensitivity, model selection metrics."""
from typing import Any

import numpy as np


def residual_analysis(residuals: list[float]) -> dict[str, Any]:
    """Basic residual diagnostics."""
    arr = np.asarray(residuals)
    return {
        "mean_residual": float(np.mean(arr)),
        "std_residual": float(np.std(arr)),
        "min_residual": float(np.min(arr)),
        "max_residual": float(np.max(arr)),
    }


def compute_aic(n: int, rss: float, k: int) -> float:
    """Akaike Information Criterion.

    AIC = n * ln(RSS/n) + 2k
    where n = number of observations, k = number of parameters, RSS = residual sum of squares.
    """
    if n <= 0 or rss <= 0:
        return float("inf")
    return float(n * np.log(rss / n) + 2 * k)


def compute_bic(n: int, rss: float, k: int) -> float:
    """Bayesian Information Criterion.

    BIC = n * ln(RSS/n) + k * ln(n)
    """
    if n <= 0 or rss <= 0:
        return float("inf")
    return float(n * np.log(rss / n) + k * np.log(n))


def kfold_cv(x: np.ndarray, y: np.ndarray, k: int = 5,
             model_fn: callable = None) -> dict[str, Any]:
    """K-fold cross-validation for linear models.

    Args:
        x: Feature matrix (n_samples, n_features) or vector.
        y: Target vector (n_samples,).
        k: Number of folds.
        model_fn: A function (x_train, y_train) -> coefficients. Default: OLS.

    Returns:
        dict with fold-wise and aggregated CV scores.
    """
    if model_fn is None:
        from src.phase3_solve import solve_lr

        def model_fn(x_tr, y_tr):
            return solve_lr(x_tr, y_tr, alpha=0.0)

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(y)
    indices = np.random.default_rng(42).permutation(n)
    fold_sizes = np.full(k, n // k)
    fold_sizes[:n % k] += 1
    current = 0
    rmse_scores = []
    r2_scores = []

    for i in range(k):
        test_idx = indices[current:current + fold_sizes[i]]
        train_idx = np.setdiff1d(indices, test_idx)
        current += fold_sizes[i]

        x_train, x_test = x[train_idx], x[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        result = model_fn(x_train, y_train)
        # Predict on test set
        coef = np.asarray(result["coefficients"])
        x_test_mat = np.c_[np.ones(len(x_test)), x_test]
        y_pred = x_test_mat @ coef
        residuals = y_test - y_pred
        rmse = float(np.sqrt(np.mean(residuals ** 2)))
        rmse_scores.append(rmse)
        tss = np.sum((y_test - np.mean(y_test)) ** 2)
        rss = np.sum(residuals ** 2)
        r2 = float(1 - rss / tss) if tss > 0 else 0.0
        r2_scores.append(r2)

    return {
        "k": k,
        "rmse_scores": rmse_scores,
        "r2_scores": r2_scores,
        "rmse_mean": float(np.mean(rmse_scores)),
        "rmse_std": float(np.std(rmse_scores)),
        "r2_mean": float(np.mean(r2_scores)),
        "r2_std": float(np.std(r2_scores)),
    }


def sensitivity_by_noise(x: np.ndarray, y: np.ndarray,
                         noise_levels: list[float] | None = None) -> list[dict[str, Any]]:
    """Perturb y with Gaussian noise and re-estimate — simple sensitivity."""
    if noise_levels is None:
        noise_levels = [0.01, 0.05, 0.1, 0.2, 0.5]
    results = []
    for sigma in noise_levels:
        y_noisy = y + np.random.default_rng(42).normal(0, sigma, size=y.shape)
        x_mat = np.c_[np.ones(x.shape[0]), x]
        try:
            theta = np.linalg.lstsq(x_mat, y_noisy, rcond=None)[0]
        except np.linalg.LinAlgError:
            theta = np.zeros(x_mat.shape[1])
        results.append({"noise_sigma": sigma, "theta": theta.tolist()})
    return results


def check_state_variables(
    state_trajectory: np.ndarray | list,
    bounds: dict[str, tuple[float, float]] | None = None,
    initial_state: np.ndarray | None = None,
    terminal_state: np.ndarray | None = None,
    tolerance: float = 1e-6,
) -> dict[str, Any]:
    """Validate state variable trajectories for physical consistency.

    Use this for systems with storage, inventory, or other time-coupled
    state variables (battery SOC, tank levels, queue lengths, etc.).

    Args:
        state_trajectory: Array of shape (n_timesteps, n_states) or (n_timesteps,).
        bounds: Dict mapping state index/name to (min, max). E.g.
                {0: (0, 100)} for state 0 bounded in [0, 100].
        initial_state: Expected initial state. If provided, checks
                       state_trajectory[0] matches within tolerance.
        terminal_state: Expected terminal state. If provided, checks
                        state_trajectory[-1] matches within tolerance.
        tolerance: Tolerance for initial/terminal state comparison.

    Returns:
        dict with pass/fail flags and violation details.
    """
    arr = np.asarray(state_trajectory, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    n_timesteps, n_states = arr.shape

    violations = []

    # Check bounds
    if bounds:
        for idx, (lo, hi) in bounds.items():
            if idx < n_states:
                col = arr[:, idx]
                below = col[col < lo - tolerance]
                above = col[col > hi + tolerance]
                if len(below) > 0:
                    violations.append({
                        "type": "below_bounds",
                        "state_idx": idx,
                        "count": int(len(below)),
                        "min_value": float(np.min(below)),
                        "bound": lo,
                    })
                if len(above) > 0:
                    violations.append({
                        "type": "above_bounds",
                        "state_idx": idx,
                        "count": int(len(above)),
                        "max_value": float(np.max(above)),
                        "bound": hi,
                    })

    # Check initial state
    init_ok = True
    if initial_state is not None:
        init = np.asarray(initial_state, dtype=float)
        if init.shape[0] == arr.shape[1]:
            diff = np.abs(arr[0] - init)
            if np.any(diff > tolerance):
                init_ok = False
                violations.append({
                    "type": "initial_state_mismatch",
                    "expected": init.tolist(),
                    "actual": arr[0].tolist(),
                })

    # Check terminal state
    term_ok = True
    if terminal_state is not None:
        term = np.asarray(terminal_state, dtype=float)
        if term.shape[0] == arr.shape[1]:
            diff = np.abs(arr[-1] - term)
            if np.any(diff > tolerance):
                term_ok = False
                violations.append({
                    "type": "terminal_state_mismatch",
                    "expected": term.tolist(),
                    "actual": arr[-1].tolist(),
                })

    # Check for NaN/Inf
    nan_count = int(np.sum(np.isnan(arr)))
    inf_count = int(np.sum(np.isinf(arr)))

    return {
        "n_violations": len(violations),
        "violations": violations,
        "all_pass": len(violations) == 0 and nan_count == 0 and inf_count == 0,
        "initial_state_ok": init_ok if initial_state is not None else None,
        "terminal_state_ok": term_ok if terminal_state is not None else None,
        "nan_count": nan_count,
        "inf_count": inf_count,
        "state_range": {
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
        },
    }


def compute_metrics_from_solver(solver_result: dict[str, Any],
                                n_params: int | None = None) -> dict[str, Any]:
    """Compute AIC, BIC, and other criteria from the solver result dict."""
    residuals = solver_result.get("residuals", [])
    n = len(residuals)
    if n == 0:
        return {"error": "No residuals to compute metrics."}
    rss = np.sum(np.asarray(residuals) ** 2)
    if n_params is None:
        # Estimate from coefficients count
        coef = solver_result.get("coefficients", [])
        n_params = len(coef) if coef else 2
    return {
        "n_observations": n,
        "n_params": n_params,
        "rss": float(rss),
        "aic": compute_aic(n, rss, n_params),
        "bic": compute_bic(n, rss, n_params),
    }


def run(solver_result: dict | None = None,
        data: dict | None = None,
        config: dict | None = None) -> dict[str, Any]:
    """Execute Phase 4: validate solution, compute selection criteria."""
    if solver_result is None or solver_result.get("status") != "solved":
        return {"status": "HUMAN_GATE_REQUIRED", "message": "No solver result to validate. Run Phase 3 first."}

    residuals = solver_result.get("residuals", [])
    ra = residual_analysis(residuals)

    selection_metrics = compute_metrics_from_solver(solver_result)

    cv_result = None
    if data and "x" in data and "y" in data:
        try:
            x = data["x"]
            y = data["y"]
            if len(x) > 10 and len(y) > 10:
                cv_result = kfold_cv(x, y, k=5)
        except Exception:
            pass

    validation = {
        "status": "validated",
        "residual_analysis": ra,
        "selection_metrics": selection_metrics,
        "cross_validation": cv_result,
        "sanity_checks": {
            "r2_acceptable": solver_result.get("r2", 0) >= 0.5,
            "residuals_centered": abs(ra["mean_residual"]) < ra["std_residual"] if ra["std_residual"] > 0 else True,
        },
    }
    return validation