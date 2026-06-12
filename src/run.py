"""Entry point: CLI for the FDE phase-gate runner.

Usage:
    python -m src.run phase=0
    python -m src.run phase=3 model=linear_regression
    python -m src.run all
"""
import sys
from pathlib import Path

import yaml


def load_config(path: str = "config/config.yaml") -> dict:
    """Load YAML config, return empty dict if missing."""
    p = Path(path)
    if p.exists():
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    print(f"[run] WARNING: config not found at {path}, using defaults.")
    return {}


def parse_cli(args: list[str]) -> tuple[str, dict[str, str]]:
    """Parse CLI args: key=value pairs. First non-kv token is the command."""
    command = "run"
    overrides = {}
    for arg in args:
        if "=" in arg:
            k, v = arg.split("=", 1)
            overrides[k] = v
        else:
            command = arg
    return command, overrides


def merge_overrides(config: dict, overrides: dict[str, str]) -> dict:
    """Apply CLI overrides to config (shallow merge for now)."""
    for k, v in overrides.items():
        if "." in k:
            parts = k.split(".")
            target = config
            for p in parts[:-1]:
                target = target.setdefault(p, {})
            target[parts[-1]] = v
        else:
            config[k] = v
    return config


def main():
    command, overrides = parse_cli(sys.argv[1:])
    config = load_config()
    config = merge_overrides(config, overrides)

    # Build output dir
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    config.setdefault("contest", {})["output_dir"] = f"output/{ts}"

    from src.runner import PhaseRunner
    runner = PhaseRunner(config)

    if command == "all":
        results = runner.run_all()
    elif command.startswith("phase"):
        phase_num = int(command.replace("phase", ""))
        results = runner.run_phase(phase_num)
    elif command == "from":
        start_phase = int(overrides.pop("start", "0"))
        results = runner.run_from(start_phase)
    else:
        print(f"Unknown command: {command}")
        print("Usage: python -m src.run [all|phaseN|from] [key=value ...]")
        sys.exit(1)

    print("\n[Done] Phase output saved. Check output/ directory for artifacts.")


if __name__ == "__main__":
    main()