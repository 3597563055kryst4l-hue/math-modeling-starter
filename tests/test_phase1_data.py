"""Tests for Phase 1: Data."""
import pandas as pd
import numpy as np
import tempfile
from pathlib import Path
from src.phase1_data import load_raw_data, quick_eda, clean_data, run


class TestPhase1:
    def test_load_raw_data_csv(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
            f.write("a,b\n1,2\n3,4")
            path = f.name
        df = load_raw_data(path)
        assert df.shape == (2, 2)
        Path(path).unlink()

    def test_load_raw_data_missing(self):
        df = load_raw_data("/nonexistent.csv")
        assert df.empty is True

    def test_quick_eda(self):
        df = pd.DataFrame({"x": [1, 2, 3, None], "y": [4.0, 5.0, 6.0, 7.0]})
        eda = quick_eda(df)
        assert eda["shape"] == (4, 2)
        assert eda["missing"]["x"] == 1
        assert eda["missing"]["y"] == 0
        assert "numeric_stats" in eda

    def test_clean_data_drop(self):
        df = pd.DataFrame({"x": [1, None, 3]})
        cleaned = clean_data(df, strategy="drop")
        assert cleaned.shape == (2, 1)

    def test_clean_data_fill_mean(self):
        df = pd.DataFrame({"x": [1.0, None, 3.0]})
        cleaned = clean_data(df, strategy="fill_mean")
        assert cleaned["x"].iloc[1] == 2.0  # mean of [1, 3]

    def test_run_without_path(self):
        result = run(raw_path="", cleaned_path="")
        assert "raw_shape" in result
        assert "eda" in result
        assert result["strategy"] == "drop"