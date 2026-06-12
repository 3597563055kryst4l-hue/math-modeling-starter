"""Tests for Phase 5: Viz."""
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend, required for headless/CI

from pathlib import Path
import tempfile
import numpy as np
from src.phase5_viz import plot_residuals, plot_fit, run


class TestPhase5:
    def test_plot_residuals_creates_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = plot_residuals([0.1, -0.2, 0.3, -0.1], Path(tmp) / "residuals.png")
            assert Path(out).exists()
            assert Path(out).stat().st_size > 0

    def test_plot_fit_creates_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            x = np.array([1, 2, 3, 4, 5])
            y = np.array([2, 4, 6, 8, 10])
            y_pred = np.array([2, 4, 6, 8, 10])
            out = plot_fit(x, y, y_pred, Path(tmp) / "fit.png")
            assert Path(out).exists()
            assert Path(out).stat().st_size > 0

    def test_run_no_result(self):
        result = run(solver_result=None)
        assert result["status"] == "no_data"

    def test_run_with_residuals(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = {"viz": {"output_dir": tmp, "format": "png", "dpi": 72}}
            solver_result = {"residuals": [0.1, -0.2, 0.3]}
            result = run(solver_result=solver_result, config=config)
            assert result["status"] == "generated"
            assert "residual_plot" in result["figures"]