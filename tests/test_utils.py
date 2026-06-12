"""Tests for utils: batch scenario runner and aggregation."""
import numpy as np
from src.utils import run_scenarios, aggregate_scenarios, categorize_scenarios


class TestBatchScenarios:
    def test_run_scenarios_basic(self):
        def dummy_solver(x: float):
            return {"value": x * 2}

        params = [{"x": 1}, {"x": 2}, {"x": 3}]
        results = run_scenarios(dummy_solver, params, progress=False)
        assert len(results) == 3
        assert results[0]["value"] == 2
        assert results[2]["value"] == 6

    def test_run_scenarios_with_errors(self):
        def flaky_solver(x: float):
            if x < 0:
                raise ValueError("negative")
            return {"value": x}

        params = [{"x": 1}, {"x": -1}, {"x": 3}]
        results = run_scenarios(flaky_solver, params, progress=False)
        assert len(results) == 3
        assert results[0].get("status") != "error"
        assert results[1]["status"] == "error"
        assert results[2].get("status") != "error"

    def test_aggregate_scenarios_basic(self):
        results = [
            {"value": 10, "status": "solved", "scenario_idx": 0, "scenario_params": {}},
            {"value": 20, "status": "solved", "scenario_idx": 1, "scenario_params": {}},
            {"value": 30, "status": "solved", "scenario_idx": 2, "scenario_params": {}},
        ]
        agg = aggregate_scenarios(results)
        assert agg["n_total"] == 3
        assert agg["n_success"] == 3
        assert agg["aggregates"]["value"]["mean"] == 20.0
        assert agg["aggregates"]["value"]["min"] == 10.0
        assert agg["aggregates"]["value"]["max"] == 30.0

    def test_aggregate_scenarios_error_count(self):
        results = [
            {"value": 10, "status": "solved", "scenario_idx": 0, "scenario_params": {}},
            {"status": "error", "error": "oops", "scenario_idx": 1, "scenario_params": {}},
        ]
        agg = aggregate_scenarios(results)
        assert agg["n_total"] == 2
        assert agg["n_success"] == 1
        assert agg["n_error"] == 1

    def test_categorize_scenarios_binary(self):
        agg = {
            "aggregates": {
                "score": {
                    "all": [85, 92, 45, 73, 60, 95],
                }
            }
        }
        cat = categorize_scenarios(agg, "score", threshold_high=60)
        assert cat["n_satisfied"] == 5
        assert cat["n_unsatisfied"] == 1

    def test_categorize_scenarios_three_tier(self):
        agg = {
            "aggregates": {
                "score": {
                    "all": [85, 92, 45, 73, 30, 95],
                }
            }
        }
        cat = categorize_scenarios(agg, "score", threshold_high=60, threshold_low=40)
        assert cat["n_full"] == 4
        assert cat["n_partial"] == 1
        assert cat["n_none"] == 1

    def test_categorize_scenarios_field_not_found(self):
        agg = {"aggregates": {}}
        cat = categorize_scenarios(agg, "nope", threshold_high=10)
        assert "error" in cat