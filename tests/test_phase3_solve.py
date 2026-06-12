"""Tests for Phase 3: Solve — scipy-powered solvers."""
import pytest
import numpy as np
from src.phase3_solve import (
    solve_lr, solve_generic, run, SOLVER_REGISTRY,
    solve_scipy_minimize, solve_curve_fit, solve_ttest,
)


class TestPhase3:
    # ── Linear Regression ──

    def test_solve_lr_perfect_fit(self):
        x = np.array([1, 2, 3, 4, 5])
        y = 2 * x + 1
        result = solve_lr(x, y, alpha=0.0)
        assert result["converged"] is True
        assert result["r2"] == pytest.approx(1.0, abs=1e-10)
        assert len(result["coefficients"]) == 2
        assert result["adj_r2"] == pytest.approx(1.0, abs=1e-10)

    def test_solve_lr_noisy(self):
        np.random.seed(42)
        x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        y = 3 * x + 5 + np.random.normal(0, 1, size=10)
        result = solve_lr(x, y, alpha=0.0)
        assert result["converged"] is True
        assert result["r2"] > 0.9

    def test_solve_lr_l2_regularization(self):
        x = np.array([1, 2, 3, 4, 5])
        y = 2 * x + 1
        result = solve_lr(x, y, alpha=0.1)
        assert result["converged"] is True
        assert result["r2"] > 0.99

    # ── SciPy Minimize ──

    def test_scipy_minimize_quadratic(self):
        result = solve_scipy_minimize(
            objective_fn=lambda x: (x[0] - 3) ** 2 + (x[1] + 1) ** 2,
            x0=np.array([0.0, 0.0]),
        )
        assert result["success"] is True
        assert result["x_opt"][0] == pytest.approx(3.0, abs=0.1)
        assert result["x_opt"][1] == pytest.approx(-1.0, abs=0.1)

    # ── Curve Fit ──

    def test_curve_fit_linear(self):
        def model(x, a, b):
            return a * x + b
        xdata = np.array([1, 2, 3, 4, 5])
        ydata = 3.0 * xdata + 1.0
        result = solve_curve_fit(model, xdata, ydata, p0=[1, 1])
        assert result["converged"] is True
        assert result["popt"][0] == pytest.approx(3.0, abs=0.1)
        assert result["popt"][1] == pytest.approx(1.0, abs=0.1)

    # ── T-Test ──

    def test_ttest_same_distribution(self):
        np.random.seed(42)
        a = np.random.normal(0, 1, 100)
        b = np.random.normal(0, 1, 100)
        result = solve_ttest(a, b)
        assert result["p_value"] > 0.05

    def test_ttest_different_distribution(self):
        np.random.seed(42)
        a = np.random.normal(0, 1, 100)
        b = np.random.normal(3, 1, 100)
        result = solve_ttest(a, b)
        assert result["p_value"] < 0.001

    # ── Registry ──

    def test_registry_contains_solvers(self):
        for name in ("linear_regression", "scipy_minimize", "curve_fit", "ttest", "odeint", "root_find", "lp", "milp"):
            assert name in SOLVER_REGISTRY, f"{name} missing from registry"

    # ── Generic Dispatch ──

    def test_solve_generic_lr(self):
        result = solve_generic(
            {"name": "linear_regression", "params": {"alpha": 0.0}},
            {"x": np.array([1, 2, 3]), "y": np.array([2, 4, 6])},
        )
        assert result["status"] == "solved"
        assert result["r2"] == pytest.approx(1.0, abs=1e-10)

    def test_solve_generic_missing_data(self):
        result = solve_generic({"name": "linear_regression"}, {"x": None, "y": None})
        assert result["status"] == "error"

    def test_solve_generic_unknown_model(self):
        result = solve_generic({"name": "nonexistent"}, {})
        assert result["status"] == "error"
        assert "not implemented" in result["message"]

    def test_solve_generic_ttest(self):
        np.random.seed(42)
        a = np.random.normal(0, 1, 100)
        b = np.random.normal(0, 1, 100)
        result = solve_generic(
            {"name": "ttest"},
            {"sample1": a, "sample2": b},
        )
        assert result["status"] == "solved"
        assert "p_value" in result

    # ── Run entry point ──

    def test_run_no_spec(self):
        result = run(model_spec=None, data={})
        assert result["status"] == "HUMAN_GATE_REQUIRED"

    def test_run_no_data(self):
        result = run(model_spec={"name": "linear_regression"}, data=None)
        assert result["status"] == "HUMAN_GATE_REQUIRED"

    def test_run_full(self):
        result = run(
            model_spec={"name": "linear_regression", "params": {"alpha": 0.0}},
            data={"x": np.array([1, 2, 3]), "y": np.array([2, 4, 6])},
        )
        assert result["status"] == "solved"

    # ── LP Solver ──

    def test_solve_lp_basic(self):
        from src.phase3_solve import solve_lp
        c = np.array([-1, -2])
        A_ub = np.array([[1, 1]])
        b_ub = np.array([10])
        bounds = [(0, None), (0, None)]
        result = solve_lp(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds)
        assert result["converged"] is True
        assert result["x_opt"] == [0.0, 10.0]
        assert result["fun"] == pytest.approx(-20.0)

    def test_solve_lp_no_constraints(self):
        from src.phase3_solve import solve_lp
        result = solve_lp(np.array([1, 1]), bounds=[(0, 1), (0, 1)])
        assert result["converged"] is True

    def test_solve_lp_unbounded(self):
        from src.phase3_solve import solve_lp
        result = solve_lp(np.array([-1, -2]))
        assert result["converged"] is False  # unbounded

    # ── MILP Solver ──

    def test_solve_milp_basic(self):
        from src.phase3_solve import solve_milp
        c = np.array([-1, -2])
        integrality = np.array([1, 1])
        A_ub = np.array([[1, 1]])
        b_ub = np.array([10])
        bounds = [(0, None), (0, None)]
        result = solve_milp(c, integrality=integrality, A_ub=A_ub, b_ub=b_ub, bounds=bounds)
        assert result["converged"] is True
        assert result["x_opt"] == [0.0, 10.0]

    def test_solve_milp_binary(self):
        from src.phase3_solve import solve_milp
        # Binary variables: select items with weights w and values v, max weight 5
        c = np.array([-10, -20, -15])  # maximize = minimize negative
        integrality = np.array([1, 1, 1])
        A_ub = np.array([[2, 3, 2]])  # weight constraint
        b_ub = np.array([5])
        bounds = [(0, 1), (0, 1), (0, 1)]
        result = solve_milp(c, integrality=integrality, A_ub=A_ub, b_ub=b_ub, bounds=bounds)
        assert result["converged"] is True
        # Select item 2 (value 20, weight 3) + item 3 (value 15, weight 2) = 35
        assert result["fun"] == pytest.approx(-35.0, abs=0.01)