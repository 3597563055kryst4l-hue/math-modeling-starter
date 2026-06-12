"""Tests for Phase 2: Model."""
import pytest
from src.phase2_model import build_model, ModelSpec, run, MODEL_REGISTRY


class TestPhase2:
    def test_build_linear_regression(self):
        spec = build_model("linear_regression", {"alpha": 0.5})
        assert spec.name == "linear_regression"
        assert spec.params["alpha"] == 0.5
        assert spec.is_selected is True

    def test_build_unknown_model(self):
        with pytest.raises(ValueError, match="Unknown model type"):
            build_model("nonexistent")

    def test_run_without_model_type(self):
        result = run(model_type="", config={})
        assert result["status"] == "HUMAN_GATE_REQUIRED"
        assert "available_models" in result

    def test_run_with_model_type(self):
        config = {"model": {"type": "arima", "params": {"p": 2}}}
        result = run(config=config)
        assert result["status"] == "spec_ready"
        assert result["model"]["name"] == "arima"
        assert result["model"]["params"]["p"] == 2

    def test_registry_contains_expected(self):
        assert "linear_regression" in MODEL_REGISTRY
        assert "arima" in MODEL_REGISTRY
        assert "svm" in MODEL_REGISTRY