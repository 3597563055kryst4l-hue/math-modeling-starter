"""PhaseRunner — Orchestrate all phases with human gate checkpoints."""

from pathlib import Path
from typing import Any

import src.phase0_context as phase0_context
import src.phase1_data as phase1_data
import src.phase2_model as phase2_model
import src.phase3_solve as phase3_solve
import src.phase4_validate as phase4_validate
import src.phase5_viz as phase5_viz
import src.phase6_report as phase6_report

import pandas as pd


class PhaseRunner:
    """Orchestrates the phase-gate pipeline.

    Usage:
        runner = PhaseRunner(config)
        runner.run_phase(0)   # Run a single phase
        runner.run_all()      # Run all phases sequentially
        runner.run_from(2)    # Run phases 2–6
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.ctx: dict[str, Any] = {}
        self.data: dict[str, Any] = {}
        self.model_spec: dict[str, Any] = {}
        self.solver_result: dict[str, Any] = {}
        self.validation: dict[str, Any] = {}
        self.viz: dict[str, Any] = {}
        self.report: dict[str, Any] = {}
        self._human_gate_enabled = config.get("human_gate", {}).get("enabled", True)

    def _gate(self, phase_num: int, message: str):
        """Print a human gate checkpoint."""
        if self._human_gate_enabled:
            print(f"\n{'='*60}")
            print(f"[HUMAN GATE — Phase {phase_num}] {message}")
            print(f"{'='*60}\n")

    def run_phase(self, phase: int, **kwargs) -> dict[str, Any]:
        """Run a single phase. Returns the phase output."""
        if phase == 0:
            self.ctx = phase0_context.run(**kwargs, config=self.config)
            self._gate(0, "Confirm problem understanding and variable definitions.")
            return self.ctx
        elif phase == 1:
            self.data = phase1_data.run(**kwargs, config=self.config)
            self._gate(1, "Inspect EDA report. Flag outliers or data issues.")
            return self.data
        elif phase == 2:
            self.model_spec = phase2_model.run(**kwargs, config=self.config)
            self._gate(2, "HUMAN GATE — Team MUST select model type.")
            return self.model_spec
        elif phase == 3:
            model_spec = kwargs.pop("model_spec", self.model_spec)
            data = kwargs.pop("data", self.data)
            self.solver_result = phase3_solve.run(model_spec=model_spec, data=data, **kwargs, config=self.config)
            return self.solver_result
        elif phase == 4:
            self.validation = phase4_validate.run(solver_result=kwargs.pop("solver_result", self.solver_result),
                                                   config=self.config)
            self._gate(4, "Sanity-check validation results. Are assumptions holding?")
            return self.validation
        elif phase == 5:
            self.viz = phase5_viz.run(solver_result=kwargs.pop("solver_result", self.solver_result),
                                       config=self.config)
            self._gate(5, "Select which figures go in the paper.")
            return self.viz
        elif phase == 6:
            self.report = phase6_report.run(
                solver_result=kwargs.pop("solver_result", self.solver_result),
                validation_result=kwargs.pop("validation_result", self.validation),
                viz_result=kwargs.pop("viz_result", self.viz),
                config=self.config,
            )
            return self.report
        else:
            raise ValueError(f"Unknown phase: {phase}")

    def run_all(self) -> dict[int, dict[str, Any]]:
        """Run phases 0 through 6 sequentially."""
        results = {}
        for p in range(7):
            results[p] = self.run_phase(p)
        return results

    def run_from(self, start: int) -> dict[int, dict[str, Any]]:
        """Run from phase `start` to 6."""
        results = {}
        for p in range(start, 7):
            results[p] = self.run_phase(p)
        return results