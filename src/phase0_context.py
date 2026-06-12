"""Phase 0: Problem Context — Build a structured problem framework.

Reads the problem text, makes educated guesses about the structure,
then presents them to the human for confirmation.

Flow:
  1. Agent reads problem PDF/text
  2. Agent makes guesses about components, variables, constraints, etc.
  3. Phase 0 outputs these as "proposed" entries with confidence levels
  4. Human says "yes" or "no" to each category → framework is finalized
"""
from pathlib import Path
from typing import Any


def load_problem_metadata(problem_id: str, config: dict[str, Any]) -> dict[str, Any]:
    """Load or infer problem metadata from the contest config."""
    contest_cfg = config.get("contest", {})
    return {
        "problem_id": problem_id or contest_cfg.get("problem", "unknown"),
        "contest_name": contest_cfg.get("name", "Unspecified Contest"),
        "phase": contest_cfg.get("phase", 0),
        "output_dir": Path(contest_cfg.get("output_dir", "output/default")),
    }


BUILTIN_FRAMEWORKS: dict[str, dict] = {
    "A": {
        "description": "MCM Problem A — Continuous / Differential Equations",
        "prompt": "物理系统建模，关注微分方程和连续时间演化",
        "focus": "sensitivity",
        "common_components": ["物理系统", "微分方程", "边界条件"],
    },
    "B": {
        "description": "MCM Problem B — Discrete / Graph / Optimization",
        "prompt": "离散数学结构，关注组合优化和决策",
        "focus": "relaxation",
        "common_components": ["网络/图", "离散状态", "组合决策"],
    },
    "C": {
        "description": "MCM Problem C — Data Insights / Big Data",
        "prompt": "大规模数据分析，关注模式识别和预测",
        "focus": "eda",
        "common_components": ["数据集", "特征变量", "预测目标"],
    },
    "D": {
        "description": "MCM Problem D — Operations Research / Network",
        "prompt": "运筹优化，关注资源分配、物流、调度",
        "focus": "constraints",
        "common_components": ["资源", "需求节点", "运输路径"],
    },
}


def build_problem_framework(
    problem_text: str,
    problem_id: str,
    agent_guess: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a structured problem framework.

    The agent reads the problem text and supplies its educated guesses
    via `agent_guess`. The function wraps those guesses into a standard
    framework structure. The human then confirms or corrects each section.

    Args:
        problem_text: The full problem statement text.
        problem_id: A/B/C/D or other.
        agent_guess: Dict with keys matching framework sections, each
                     containing the agent's inferred entries.
                     If None, empty proposals are returned (agent
                     analysis should happen before calling this).

    Returns:
        Framework dict with 'proposed_entries' instead of blank entries.
    """
    template_info = BUILTIN_FRAMEWORKS.get(problem_id.upper(), None)

    # Default empty structure — agent fills it before presenting
    framework = {
        "status": "proposed",
        "problem_id": problem_id,
        "template_hint": template_info,
        "instruction": "Agent读了题，以下是它对这个问题的结构化推断。请逐项确认或修正。",
        "sections": {
            "system_components": {
                "question": "题目涉及哪些物理实体或子系统？",
                "proposed_entries": [],
                "confidence": "",
                "human_verdict": None,  # True / False / corrected dict
            },
            "decision_variables": {
                "question": "我们需要决策什么？",
                "proposed_entries": [],
                "confidence": "",
                "human_verdict": None,
            },
            "constraints": {
                "question": "决策变量受哪些限制？",
                "proposed_entries": [],
                "confidence": "",
                "human_verdict": None,
            },
            "objective": {
                "question": "目标是什么？",
                "proposed_entries": [],
                "confidence": "",
                "human_verdict": None,
            },
            "external_parameters": {
                "question": "哪些是外部给定的参数？",
                "proposed_entries": [],
                "confidence": "",
                "human_verdict": None,
            },
            "subproblems": {
                "question": "题目分几问？每问的输入输出是什么？",
                "proposed_entries": [],
                "confidence": "",
                "human_verdict": None,
            },
        },
    }

    # Merge agent guesses if provided
    if agent_guess:
        for section, guess in agent_guess.items():
            if section in framework["sections"]:
                if isinstance(guess, dict):
                    framework["sections"][section].update(guess)
                elif isinstance(guess, list):
                    framework["sections"][section]["proposed_entries"] = guess

    return framework


def run(problem_id: str = "", raw_data_path: str = "",
        config: dict | None = None,
        problem_text: str = "",
        agent_guess: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute Phase 0: establish problem context with a structured framework.

    The agent should read the problem text FIRST, make its analysis,
    then pass it via `agent_guess`. Example agent_guess structure:

    {
        "system_components": {
            "proposed_entries": [
                {"name": "风电", "role": "发电", "properties": "40MW装机"},
                {"name": "光伏", "role": "发电", "properties": "64MW装机"},
            ],
            "confidence": "high",
        },
        "decision_variables": {
            "proposed_entries": [
                {"symbol": "P_elec", "description": "电解槽功率", "units": "MW",
                 "type": "continuous", "range": "[0, 20]"},
            ],
            "confidence": "medium",
        },
        ...
    }
    """
    if config is None:
        config = {}
    ctx = load_problem_metadata(problem_id, config)
    ctx["framework"] = build_problem_framework(problem_text, ctx["problem_id"],
                                                agent_guess=agent_guess)

    # Read data dir listing if raw_data_path provided
    data_files = []
    if raw_data_path:
        p = Path(raw_data_path)
        if p.exists() and p.is_dir():
            data_files = [str(f.relative_to(p)) for f in p.iterdir() if f.is_file()]
    ctx["data_files"] = data_files

    return ctx