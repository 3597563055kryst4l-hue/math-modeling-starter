"""Tests for PhaseRunner orchestrator."""
from src.runner import PhaseRunner


class TestPhaseRunner:
    def test_init(self):
        config = {"human_gate": {"enabled": False}}
        runner = PhaseRunner(config)
        assert runner._human_gate_enabled is False

    def test_run_phase0(self):
        config = {
            "contest": {"name": "Test"},
            "data": {"raw_path": "", "cleaned_path": ""},
            "human_gate": {"enabled": False},
        }
        runner = PhaseRunner(config)
        result = runner.run_phase(0)
        assert "problem_id" in result

    def test_run_phase1(self):
        config = {
            "data": {"raw_path": "", "cleaned_path": ""},
            "human_gate": {"enabled": False},
        }
        runner = PhaseRunner(config)
        result = runner.run_phase(1)
        assert "raw_shape" in result

    def test_run_phase2_no_model(self):
        config = {"human_gate": {"enabled": False}}
        runner = PhaseRunner(config)
        result = runner.run_phase(2)
        assert result["status"] == "HUMAN_GATE_REQUIRED"

    def test_run_phase2_with_model(self):
        config = {
            "model": {"type": "linear_regression", "params": {"alpha": 0.0}},
            "human_gate": {"enabled": False},
        }
        runner = PhaseRunner(config)
        result = runner.run_phase(2)
        assert result["status"] == "spec_ready"

    def test_run_phase3_needs_prereqs(self):
        config = {"human_gate": {"enabled": False}}
        runner = PhaseRunner(config)
        result = runner.run_phase(3)
        assert "HUMAN_GATE" in result["status"]

    def test_run_phase4_needs_prereqs(self):
        config = {"human_gate": {"enabled": False}}
        runner = PhaseRunner(config)
        result = runner.run_phase(4)
        assert "HUMAN_GATE" in result["status"]

    def test_run_all(self):
        config = {
            "data": {"raw_path": "", "cleaned_path": ""},
            "model": {"type": "linear_regression", "params": {"alpha": 0.0}},
            "human_gate": {"enabled": False},
        }
        runner = PhaseRunner(config)
        results = runner.run_all()
        assert len(results) == 7
        assert 0 in results
        assert 6 in results