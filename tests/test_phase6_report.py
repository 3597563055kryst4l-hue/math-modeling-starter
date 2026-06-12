"""Tests for Phase 6: Report — Markdown and LaTeX export."""
import tempfile
from pathlib import Path
from src.phase6_report import (
    build_summary_table,
    build_latex_table,
    export_markdown_report,
    export_latex_report,
    run,
)


class TestPhase6:
    # ── Markdown Table ──

    def test_build_summary_table(self):
        solver = {"r2": 0.95, "rmse": 0.12, "converged": True}
        validation = {"residual_analysis": {"mean_residual": 0.01, "std_residual": 0.5}}
        table = build_summary_table(solver, validation)
        assert "| r2 | 0.95 |" in table
        assert "| rmse | 0.12 |" in table
        assert "| mean_residual | 0.0100 |" in table

    def test_build_summary_table_no_data(self):
        table = build_summary_table(None, None)
        assert "Model Results Summary" in table

    # ── LaTeX Table ──

    def test_build_latex_table(self):
        solver = {"r2": 0.95, "rmse": 0.1234, "converged": True}
        validation = {"residual_analysis": {"mean_residual": 0.01}}
        tex = build_latex_table(solver, validation)
        assert "\\begin{table}" in tex
        assert "0.9500" in tex
        assert "0.1234" in tex
        assert "0.0100" in tex
        assert "\\end{table}" in tex

    def test_build_latex_table_no_data(self):
        tex = build_latex_table(None, None)
        assert "\\begin{table}" in tex
        # An empty table with no rows is still valid LaTeX
        assert "\\hline" in tex

    # ── Export Markdown ──

    def test_export_markdown_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.md"
            result = export_markdown_report(
                {"r2": 0.9, "rmse": 0.1},
                {"residual_analysis": {"mean_residual": 0.0}},
                {"figures": {"residual_plot": "figs/residuals.png"}},
                path,
            )
            content = Path(result).read_text()
            assert "Contest Report" in content
            assert "residual_plot" in content

    # ── Export LaTeX ──

    def test_export_latex_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.tex"
            result = export_latex_report(
                {"r2": 0.9, "rmse": 0.1},
                {"residual_analysis": {"mean_residual": 0.0}},
                {"figures": {"residual_plot": "figs/residuals.png"}},
                path,
            )
            content = Path(result).read_text()
            assert "\\documentclass" in content
            assert "\\begin{document}" in content
            assert "\\includegraphics" in content
            assert "\\end{document}" in content

    # ── Run ──

    def test_run_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = {"report": {"output_dir": str(tmp)}}
            result = run(config=config)
            assert result["status"] == "report_generated"
            assert "markdown" in result["files"]
            assert Path(result["files"]["markdown"]).exists()

    def test_run_latex_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = {"report": {"output_dir": str(tmp), "formats": ["tex"]}}
            result = run(config=config)
            assert result["status"] == "report_generated"
            assert "latex" in result["files"]
            assert Path(result["files"]["latex"]).exists()
            content = Path(result["files"]["latex"]).read_text()
            assert "\\documentclass" in content

    def test_run_both_formats(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = {"report": {"output_dir": str(tmp), "formats": ["md", "tex"]}}
            result = run(config=config)
            assert result["status"] == "report_generated"
            assert "markdown" in result["files"]
            assert "latex" in result["files"]