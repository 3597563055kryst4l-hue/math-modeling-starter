"""Phase 5: Viz — Generate publication-quality figures."""
from pathlib import Path
from typing import Any

import numpy as np

# Lazy matplotlib import — only pulled in when a plotting function is called
def _setup_mpl(dpi: int = 300):
    """Configure matplotlib for non-interactive, publication-quality output."""
    import matplotlib
    from matplotlib import pyplot as plt
    matplotlib.rcParams.update({
        "figure.dpi": dpi,
        "savefig.dpi": dpi,
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 12,
        "legend.fontsize": 10,
    })
    return plt


def plot_residuals(residuals: list[float], output_path: str | Path, dpi: int = 300) -> str:
    """Residual plot: scatter + histogram."""
    plt = _setup_mpl(dpi)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.scatter(range(len(residuals)), residuals, alpha=0.6)
    ax1.axhline(0, color="red", linestyle="--", alpha=0.5)
    ax1.set_title("Residuals")
    ax1.set_xlabel("Observation")
    ax1.set_ylabel("Residual")
    ax2.hist(residuals, bins=20, edgecolor="white", alpha=0.7)
    ax2.set_title("Residual Distribution")
    ax2.set_xlabel("Residual")
    plt.tight_layout()
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def plot_fit(x: np.ndarray, y: np.ndarray, y_pred: np.ndarray,
             output_path: str | Path, dpi: int = 300) -> str:
    """Scatter plot with regression line."""
    plt = _setup_mpl(dpi)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(x, y, alpha=0.6, label="Data")
    sort_idx = np.argsort(x.ravel())
    ax.plot(x.ravel()[sort_idx], y_pred.ravel()[sort_idx], color="red", label="Fit")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Model Fit")
    ax.legend()
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def run(solver_result: dict | None = None, config: dict | None = None) -> dict[str, Any]:
    """Execute Phase 5: generate plots."""
    if solver_result is None:
        return {"status": "no_data", "message": "No solver result."}
    viz_cfg = config.get("viz", {}) if config else {}
    fmt = viz_cfg.get("format", "png")
    dpi = viz_cfg.get("dpi", 300)
    output_dir = Path(viz_cfg.get("output_dir", "output/viz"))
    output_dir.mkdir(parents=True, exist_ok=True)

    generated = {}
    residuals = solver_result.get("residuals", [])
    if residuals:
        generated["residual_plot"] = plot_residuals(residuals, output_dir / f"residuals.{fmt}", dpi=dpi)

    return {
        "status": "generated",
        "figures": generated,
        "output_dir": str(output_dir),
    }