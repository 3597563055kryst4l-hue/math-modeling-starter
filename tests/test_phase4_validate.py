"""Tests for Phase 4: Validate — metrics and cross-validation."""
import pytest
import numpy as np
from src.phase4_validate import (
    residual_analysis,
    compute_aic,
    compute_bic,
    compute_metrics_from_solver,
    kfold_cv,
    run,
)


class TestPhase4:
    # ── Residual Analysis ──

    def test_residual_analysis_centered(self):
        residuals = [0.1, -0.2, 0.15, -0.05, 0.0]
        ra = residual_analysis(residuals)
        assert abs(ra["mean_residual"]) < ra["std_residual"]
        assert ra["min_residual"] == pytest.approx(-0.2)
        assert ra["max_residual"] == pytest.approx(0.15)

    def test_residual_analysis_all_zero(self):
        residuals = [0, 0, 0]
        ra = residual_analysis(residuals)
        assert ra["mean_residual"] == 0.0
        assert ra["std_residual"] == 0.0

    # ── AIC / BIC ──

    def test_compute_aic(self):
        aic = compute_aic(100, 50.0, 3)
        assert isinstance(aic, float)
        # AIC = n·ln(RSS/n) + 2k, can be negative when RSS/n < 1 (good fit)

    def test_compute_aic_better_fit_lower(self):
        # Lower RSS should give lower AIC for same n, k
        aic_high = compute_aic(100, 50.0, 3)
        aic_low = compute_aic(100, 10.0, 3)
        assert aic_low < aic_high

    def test_compute_aic_penalizes_params(self):
        # More params should increase AIC for same n, RSS
        aic_few = compute_aic(100, 50.0, 3)
        aic_many = compute_aic(100, 50.0, 10)
        assert aic_many > aic_few

    def test_compute_bic(self):
        bic = compute_bic(100, 50.0, 3)
        assert isinstance(bic, float)

    def test_compute_bic_penalizes_params(self):
        bic_few = compute_bic(100, 50.0, 3)
        bic_many = compute_bic(100, 50.0, 10)
        assert bic_many > bic_few

    def test_compute_metrics_from_solver(self):
        result = {"residuals": [0.1, -0.2, 0.15], "coefficients": [1.0, 2.0]}
        metrics = compute_metrics_from_solver(result)
        assert "aic" in metrics
        assert "bic" in metrics
        assert "rss" in metrics
        assert metrics["n_params"] == 2

    # ── Cross-validation ──

    def test_kfold_cv_basic(self):
        x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        y = 2 * x + 1
        result = kfold_cv(x, y, k=3)
        assert result["k"] == 3
        assert len(result["rmse_scores"]) == 3
        assert result["r2_mean"] > 0.99

    def test_kfold_cv_reproducible(self):
        x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        y = 2 * x + 1
        r1 = kfold_cv(x, y, k=3)
        r2 = kfold_cv(x, y, k=3)
        assert r1["rmse_mean"] == pytest.approx(r2["rmse_mean"], abs=1e-10)

    # ── Run ──

    def test_run_no_result(self):
        result = run(solver_result=None)
        assert result["status"] == "HUMAN_GATE_REQUIRED"

    def test_run_with_bad_result(self):
        result = run(solver_result={"status": "error"})
        assert result["status"] == "HUMAN_GATE_REQUIRED"

    def test_run_with_good_result(self):
        solver_result = {"status": "solved", "r2": 0.95, "residuals": [0.1, -0.2, 0.15]}
        result = run(solver_result=solver_result)
        assert result["status"] == "validated"
        assert result["sanity_checks"]["r2_acceptable"] is True
        assert "selection_metrics" in result
        assert "aic" in result["selection_metrics"]

    def test_run_with_data_cv(self):
        np.random.seed(42)
        x = np.linspace(0, 10, 20)
        y = 2.5 * x + 1.0 + np.random.normal(0, 0.5, size=20)
        solver_result = {
            "status": "solved",
            "r2": 0.98,
            "residuals": list(np.random.normal(0, 0.5, size=20)),
            "coefficients": [1.0, 2.5],
        }
        data = {"x": x, "y": y}
        result = run(solver_result=solver_result, data=data)
        assert result["status"] == "validated"
        assert result["cross_validation"] is not None
        assert result["cross_validation"]["k"] == 5

    # ── State Variable Checks ──

    def test_state_variable_bounds_pass(self):
        from src.phase4_validate import check_state_variables
        trajectory = [10, 20, 30, 40, 50]
        result = check_state_variables(trajectory, bounds={0: (0, 100)})
        assert result["all_pass"] is True
        assert result["n_violations"] == 0

    def test_state_variable_bounds_violate(self):
        from src.phase4_validate import check_state_variables
        trajectory = [-5, 20, 105, 40, 50]
        result = check_state_variables(trajectory, bounds={0: (0, 100)})
        assert result["all_pass"] is False
        assert result["n_violations"] >= 1

    def test_state_variable_initial_terminal(self):
        from src.phase4_validate import check_state_variables
        trajectory = [10, 20, 30, 20, 10]
        result = check_state_variables(trajectory, initial_state=[10], terminal_state=[10])
        assert result["initial_state_ok"] is True
        assert result["terminal_state_ok"] is True

    def test_state_variable_terminal_mismatch(self):
        from src.phase4_validate import check_state_variables
        trajectory = [10, 20, 30, 20, 0]
        result = check_state_variables(trajectory, terminal_state=[10])
        assert result["terminal_state_ok"] is False

    def test_state_variable_nan_detected(self):
        from src.phase4_validate import check_state_variables
        trajectory = [10, float("nan"), 30]
        result = check_state_variables(trajectory)
        assert result["nan_count"] == 1