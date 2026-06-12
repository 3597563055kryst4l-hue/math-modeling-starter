"""Tests for Phase 0: Problem Context."""
from src.phase0_context import load_problem_metadata, build_problem_framework, run, BUILTIN_FRAMEWORKS


class TestPhase0:
    def test_load_problem_metadata_default(self):
        config = {"contest": {"name": "Test Contest", "phase": 0}}
        ctx = load_problem_metadata("", config)
        assert ctx["problem_id"] == "unknown"
        assert ctx["contest_name"] == "Test Contest"
        assert ctx["phase"] == 0

    def test_load_problem_metadata_with_id(self):
        config = {"contest": {"name": "MCM"}}
        ctx = load_problem_metadata("C", config)
        assert ctx["problem_id"] == "C"

    def test_build_framework_contains_all_sections(self):
        framework = build_problem_framework("", "A")
        assert "system_components" in framework["sections"]
        assert "decision_variables" in framework["sections"]
        assert "constraints" in framework["sections"]
        assert "objective" in framework["sections"]
        assert "external_parameters" in framework["sections"]
        assert "subproblems" in framework["sections"]

    def test_build_framework_unknown_problem(self):
        framework = build_problem_framework("", "Z")
        assert framework["template_hint"] is None

    def test_build_framework_problem_A_hint(self):
        framework = build_problem_framework("some ODE text", "A")
        assert framework["template_hint"]["focus"] == "sensitivity"

    def test_builtin_frameworks_cover_abcd(self):
        for pid in ("A", "B", "C", "D"):
            assert pid in BUILTIN_FRAMEWORKS

    def test_build_framework_with_agent_guess(self):
        guess = {
            "system_components": {
                "proposed_entries": [{"name": "风电", "role": "发电"}],
                "confidence": "high",
            },
        }
        framework = build_problem_framework("", "C", agent_guess=guess)
        assert framework["sections"]["system_components"]["confidence"] == "high"
        assert len(framework["sections"]["system_components"]["proposed_entries"]) == 1

    def test_build_framework_agent_guess_merges_by_key(self):
        guess = {
            "decision_variables": {
                "proposed_entries": [{"symbol": "P", "units": "MW"}],
            },
            "objective": {
                "proposed_entries": [{"name": "min_cost", "direction": "min"}],
            },
        }
        framework = build_problem_framework("", "B", agent_guess=guess)
        assert len(framework["sections"]["decision_variables"]["proposed_entries"]) == 1
        assert len(framework["sections"]["objective"]["proposed_entries"]) == 1
        assert len(framework["sections"]["constraints"]["proposed_entries"]) == 0

    def test_run_returns_problem_id(self):
        result = run(problem_id="A", config={"contest": {"name": "Test"}})
        assert result["problem_id"] == "A"

    def test_run_returns_framework(self):
        result = run(config={"contest": {"name": "Test"}})
        assert "framework" in result
        assert "data_files" in result
