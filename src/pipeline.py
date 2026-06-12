"""Legacy wrapper — delegates to PhaseRunner.

Usage:
    python -m src.pipeline              # run all phases
    python -m src.pipeline --phase 2    # single phase
"""
import sys

from src.runner import PhaseRunner
from src.run import load_config, parse_cli, merge_overrides


def main():
    command, overrides = parse_cli(sys.argv[1:])
    config = load_config()
    config = merge_overrides(config, overrides)

    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    config.setdefault("contest", {})["output_dir"] = f"output/{ts}"

    runner = PhaseRunner(config)

    if command == "all" or command == "run":
        runner.run_all()
    elif command.startswith("phase"):
        phase_num = int(command.replace("phase", ""))
        runner.run_phase(phase_num)
    else:
        print("Use: python -m src.pipeline [all|phaseN]")
        sys.exit(1)


if __name__ == "__main__":
    main()