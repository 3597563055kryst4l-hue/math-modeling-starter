"""Phase 1: Data — Read, clean, and explore raw contest data."""
from pathlib import Path
from typing import Any

import pandas as pd
import numpy as np


def load_raw_data(path: str) -> pd.DataFrame:
    """Load raw data from CSV/Excel/TXT. Returns empty DataFrame if path missing."""
    if not path:
        print("[Phase1] WARNING: no raw data path provided. Using empty DataFrame.")
        return pd.DataFrame()
    p = Path(path)
    if not p.exists():
        print(f"[Phase1] WARNING: raw data not found at {path}. Using empty DataFrame.")
        return pd.DataFrame()
    suffix = p.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(p)
    elif suffix in (".xls", ".xlsx"):
        return pd.read_excel(p)
    elif suffix == ".txt":
        return pd.read_csv(p, sep="\\s+")
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def quick_eda(df: pd.DataFrame) -> dict[str, Any]:
    """Run basic EDA and return summary stats."""
    return {
        "shape": df.shape,
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing": df.isnull().sum().to_dict(),
        "missing_pct": (df.isnull().mean() * 100).round(2).to_dict(),
        "numeric_stats": df.describe(include=[np.number]).to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {},
        "head": df.head(5).to_dict(orient="records"),
    }


def clean_data(df: pd.DataFrame, strategy: str = "drop") -> pd.DataFrame:
    """Simple cleaning: drop or fill missing values."""
    if strategy == "drop":
        return df.dropna().reset_index(drop=True)
    elif strategy == "fill_mean":
        num_cols = df.select_dtypes(include=[np.number]).columns
        df = df.copy()
        df[num_cols] = df[num_cols].fillna(df[num_cols].mean())
        return df
    elif strategy == "fill_median":
        num_cols = df.select_dtypes(include=[np.number]).columns
        df = df.copy()
        df[num_cols] = df[num_cols].fillna(df[num_cols].median())
        return df
    else:
        raise ValueError(f"Unknown cleaning strategy: {strategy}")


def run(raw_path: str = "", cleaned_path: str = "", config: dict | None = None) -> dict[str, Any]:
    """Execute Phase 1: load, EDA, clean."""
    if config is None:
        config = {}
    data_cfg = config.get("data", {})
    raw = load_raw_data(raw_path or data_cfg.get("raw_path", ""))
    eda_report = quick_eda(raw)
    strategy = data_cfg.get("cleaning_strategy", "drop")
    cleaned = clean_data(raw, strategy=strategy)

    out_path = cleaned_path or data_cfg.get("cleaned_path", "")
    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        cleaned.to_csv(out_path, index=False)

    return {
        "raw_shape": eda_report["shape"],
        "cleaned_shape": cleaned.shape,
        "eda": eda_report,
        "cleaned_head": cleaned.head(5).to_dict(orient="records"),
        "strategy": strategy,
        "cleaned_path": out_path,
    }