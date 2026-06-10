# problems/ — 问题求解规范

## 使用方式

用脚手架脚本创建题目骨架（推荐）：

```bash
python scripts/new_problem.py 1 --desc "问题一：功率预测"
```

这会自动生成：

```
problems/problem_1/
├── main.py             # 求解主脚本（已 import 所有模板工具）
├── verify.py           # 结果校验 + 交叉验证（已 import validation 工具）
├── config.yaml         # 本问特定参数
└── results/            # 本问输出
    ├── figures/        # 图表
    ├── data/           # 数值结果（csv/json）
    └── report.md       # 结果说明
```

也可手动创建（参考 scripts/new_problem.py 生成的骨架）。

## 文件规范

### main.py

```python
try:
    from config.settings import set_plot_style, RANDOM_SEED
    from templates.data_preprocessing import read_data, data_summary
    from templates.visualization import plot_lines, plot_bar, plot_heatmap
    from templates.metrics import regression_report
    from templates.validation import sanity_check, cross_validate
    from templates.sensitivity import perturbation_analysis
    from utils.file_utils import ensure_dir, save_output
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from config.settings import set_plot_style, RANDOM_SEED
    from templates.data_preprocessing import read_data, data_summary
    from templates.visualization import plot_lines, plot_bar, plot_heatmap
    from templates.metrics import regression_report
    from templates.validation import sanity_check, cross_validate
    from templates.sensitivity import perturbation_analysis
    from utils.file_utils import ensure_dir, save_output

set_plot_style()
np.random.seed(RANDOM_SEED)

# 1. 读数据（参考 templates.data_preprocessing）
# 2. 建模/求解（参考 templates.solvers）
# 3. 校验（参考 templates.validation）
# 4. 出图，保存到 results/figures/
# 5. 输出结果，保存到 results/data/
```

### verify.py

```python
try:
    from templates.validation import sanity_check, cross_validate
    from utils.logger import setup_logger
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from templates.validation import sanity_check, cross_validate
    from utils.logger import setup_logger

# 1. 加载 main.py 的计算结果
# 2. 合理性检查（sanity_check）
# 3. 交叉验证（cross_validate）
# 4. 敏感性分析（参考 templates.sensitivity）
# 5. 生成校验报告
```

## 原则

- 优先用 `scripts/new_problem.py` 创建骨架，减少重复劳动
- 每个问题的脚本尽量独立，避免跨问题 import
- 公共参数放 `config.yaml`，不硬编码在脚本里
- 图表统一 300dpi，保存到 `results/figures/`，中文字体由 settings.py 自动处理
- 校验不是可选项，是必选项
