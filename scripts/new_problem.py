"""新建问题脚手架 — 在 problems/ 下生成题目骨架。

用法：
    python scripts/new_problem.py 1 --desc "问题一：功率预测"
    python scripts/new_problem.py 2 --desc "问题二：风电场选址" --deps problem_1

这会创建：
    problems/problem_N/
    ├── main.py         # 求解骨架（已 import 常用工具）
    ├── verify.py       # 校验骨架（已 import validation 工具）
    ├── config.yaml     # 本问参数
    └── results/
        ├── figures/
        ├── data/
        └── report.md
"""
import argparse
import os
import sys
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBLEMS_DIR = os.path.join(BASE, 'problems')

MAIN_PY_TEMPLATE = '''\
\"\"\"Problem {num}: {desc} — 求解脚本。

使用方式：从项目根目录运行
    python problems/problem_{num}/main.py
或直接用 IDE 运行本文件。
\"\"\"

import sys
import os
import numpy as np

# 尝试正常导入，失败则用 sys.path 回退
try:
    from config.settings import set_plot_style, RANDOM_SEED
    from templates.data_preprocessing import read_data, data_summary
    from templates.visualization import set_paper_style, plot_lines, plot_bar, plot_heatmap
    from templates.metrics import regression_report, compare_models as compare_metrics
    from templates.validation import sanity_check, cross_validate
    from templates.sensitivity import scan_param, plot_sensitivity, perturbation_analysis
    from utils.file_utils import ensure_dir, save_output
    from utils.logger import setup_logger
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from config.settings import set_plot_style, RANDOM_SEED
    from templates.data_preprocessing import read_data, data_summary
    from templates.visualization import set_paper_style, plot_lines, plot_bar, plot_heatmap
    from templates.metrics import regression_report, compare_models as compare_metrics
    from templates.validation import sanity_check, cross_validate
    from templates.sensitivity import scan_param, plot_sensitivity, perturbation_analysis
    from utils.file_utils import ensure_dir, save_output
    from utils.logger import setup_logger

import yaml

# ── 配置 ──────────────────────────────────────────────

set_plot_style()
np.random.seed(RANDOM_SEED)
logger = setup_logger(f'problem_{num}', log_dir='logs')

# 加载本问参数
with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), encoding='utf-8') as f:
    CONFIG = yaml.safe_load(f)

# 结果输出目录
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
ensure_dir(os.path.join(RESULTS_DIR, 'figures'))
ensure_dir(os.path.join(RESULTS_DIR, 'data'))


# ── 求解 ──────────────────────────────────────────────

def solve():
    \"\"\"主求解逻辑。返回结果字典，供 verify.py 调用。\"\"\"
    logger.info("Starting problem {num}...")

    # 1. 读数据
    # raw_path = os.path.join('data', 'raw', CONFIG['data']['file'])
    # df = read_data(raw_path)
    # data_summary(df)

    # 2. 建模 / 求解
    # ...

    # 3. 出图
    # plot_lines(x, {{'label': y}}, save_path=os.path.join(RESULTS_DIR, 'figures', 'fig1.png'))

    # 4. 输出结果
    result = {{'status': 'done', 'num': {num}}}
    save_output(result, os.path.join(RESULTS_DIR, 'data', 'result.json'))

    logger.info("Problem {num} completed.")
    return result


# ── 主入口 ────────────────────────────────────────────

if __name__ == '__main__':
    result = solve()
    print(f"Problem {num} done.")
'''

VERIFY_PY_TEMPLATE = '''\
"""Problem {num}: {desc} — 结果校验 + 交叉验证。

需在 main.py 运行之后执行。
"""
import sys
import os
import json

try:
    from templates.validation import sanity_check, cross_validate
    from utils.logger import setup_logger
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from templates.validation import sanity_check, cross_validate
    from utils.logger import setup_logger

logger = setup_logger(f'verify_{num}', log_dir='logs')


def verify():
    \"\"\"加载求解结果并进行校验。\"\"\"
    logger.info("Verifying problem {num}...")

    # 1. 加载结果
    result_path = os.path.join(os.path.dirname(__file__), 'results', 'data', 'result.json')
    if not os.path.exists(result_path):
        logger.error("No result found. Run main.py first.")
        return

    with open(result_path, encoding='utf-8') as f:
        result = json.load(f)
    logger.info(f"Loaded result: {{result}}")

    # 2. 合理性检查
    # sanity_check(value, name='key', expected_range=(0, 100))

    # 3. 交叉验证（如有多种方法）
    # cross_validate({{'method_A': val_a, 'method_B': val_b}})

    logger.info("Verification done.")


if __name__ == '__main__':
    verify()
'''

CONFIG_YAML_TEMPLATE = """# Problem {num}: {desc} — 本问参数
# 在求解前按需修改

problem:
  num: {num}
  description: '{desc}'

data:
  file: ''              # 数据文件名（相对 data/raw/）
  sheet: 0              # Excel sheet 索引或名称

model:
  params: {{}}            # 模型参数
"""

REPORT_MD_TEMPLATE = """# Problem {num}: {desc}

## 求解思路

[在这里写本问的求解思路]

## 结果

| 指标 | 值 |
|------|-----|
| ...  | ... |

## 关键图表

![fig1](figures/fig1.png)

## 结论

[在这里写本问的结论]

---

*由 new_problem.py 自动生成于 {date}*
"""


def create_problem(num, desc, deps=None):
    prob_dir = os.path.join(PROBLEMS_DIR, f'problem_{num}')
    results_dir = os.path.join(prob_dir, 'results')

    dirs = [
        prob_dir,
        os.path.join(results_dir, 'figures'),
        os.path.join(results_dir, 'data'),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    files = {
        'main.py': MAIN_PY_TEMPLATE.format(num=num, desc=desc),
        'verify.py': VERIFY_PY_TEMPLATE.format(num=num, desc=desc),
        'config.yaml': CONFIG_YAML_TEMPLATE.format(num=num, desc=desc),
        os.path.join('results', 'report.md'): REPORT_MD_TEMPLATE.format(
            num=num, desc=desc, date=datetime.now().strftime('%Y-%m-%d %H:%M')
        ),
    }

    for relpath, content in files.items():
        abspath = os.path.join(prob_dir, relpath)
        # 跳过已存在的文件
        if os.path.exists(abspath):
            print(f'  [skip] {relpath} (already exists)')
            continue
        with open(abspath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  [ok]   {relpath}')

    if deps:
        deps_path = os.path.join(prob_dir, 'DEPENDS_ON')
        with open(deps_path, 'w', encoding='utf-8') as f:
            f.write(f'{deps}\n')
        print(f'  [ok]   DEPENDS_ON -> {deps}')

    print(f'\nDone. problems/problem_{num}/ is ready.')
    return prob_dir


def main():
    parser = argparse.ArgumentParser(description='新建问题脚手架')
    parser.add_argument('num', type=int, help='问题编号（如 1 2 3）')
    parser.add_argument('--desc', '-d', default='', help='问题描述')
    parser.add_argument('--deps', '-D', default=None,
                        help='依赖的其他问题目录名（如 problem_1）')
    args = parser.parse_args()

    desc = args.desc or f'问题{args.num}'
    create_problem(args.num, desc, deps=args.deps)


if __name__ == '__main__':
    main()
