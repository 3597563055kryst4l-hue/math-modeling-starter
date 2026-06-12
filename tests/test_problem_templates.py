"""Tests for MCM problem-type templates."""
import pytest
from src.problem_templates import (
    get_template,
    apply_template_to_config,
    list_problems,
    run,
    PROBLEM_TEMPLATES,
)


class TestProblemTemplates:
    def test_all_problems_present(self):
        for pid in ("A", "B", "C", "D"):
            assert pid in PROBLEM_TEMPLATES, f"Missing problem {pid}"

    def test_get_template_valid(self):
        t = get_template("A")
        assert t is not None
        assert "suggested_models" in t

    def test_get_template_case_insensitive(self):
        t = get_template("a")
        assert t is not None
        assert t["name"] == PROBLEM_TEMPLATES["A"]["name"]

    def test_get_template_invalid(self):
        t = get_template("Z")
        assert t is None

    def test_apply_template_to_config(self):
        base = {"data": {"raw_path": "data.csv"}}
        merged = apply_template_to_config("C", base)
        assert merged["data"]["raw_path"] == "data.csv"  # preserved from base
        assert merged["model"]["type"] == "linear_regression"  # from template

    def test_apply_template_invalid(self):
        merged = apply_template_to_config("Z", {"data": {}})
        assert merged == {"data": {}}

    def test_list_problems(self):
        problems = list_problems()
        assert len(problems) >= 4
        for p in problems:
            assert "id" in p
            assert "name" in p

    def test_run_no_problem(self):
        result = run(problem_id="")
        assert result["status"] == "HUMAN_GATE_REQUIRED"
        assert "available_problems" in result

    def test_run_invalid_problem(self):
        result = run(problem_id="Z")
        assert result["status"] == "error"

    def test_run_valid_problem(self):
        result = run(problem_id="B")
        assert result["status"] == "template_applied"
        assert result["problem_id"] == "B"
        assert "suggested_models" in result["template"]
        assert "config_preset" in result