# templates — 脚手架代码库

## 设计哲学

**这不是框架，是参考实现。**

每个模块解决一类常见问题，但你完全可以：
- 直接调用
- 复制代码段修改
- 完全不用，自己写

重点是**减少重复造轮子**，而不是约束你的编码方式。

## 模块速查

| 模块 | 用途 | 核心函数 |
|------|------|---------|
| `data_preprocessing.py` | 数据读取与检查 | `read_data()`, `read_multi_sheet()`, `data_summary()`, `normalize()` |
| `visualization.py` | 论文级图表 | `set_paper_style()`, `plot_lines()`, `plot_bar()`, `plot_heatmap()`, `subplots_grid()` |
| `metrics.py` | 评价指标 | `rmse()`, `mae()`, `mape()`, `r2()`, `regression_report()`, `compare_models()` |
| `prediction.py` | 预测参考 | `train_sklearn()`, `train_arima()`, `train_lstm()` → `(y_pred, y_true, model, scaler)`, `compare_models()` |
| `solvers.py` | 求解器参考（按问题类型组织） | `solve_lp()`, `solve_dp_example()`, `solve_assignment()`, `solve_ga()`, `pareto_front()` |
| `sensitivity.py` | 敏感性分析 | `scan_param()`, `plot_sensitivity()`, `perturbation_analysis()` |
| `validation.py` | 结果校验 | `sanity_check()`, `power_balance()`, `cross_validate()` |
| `paper_tools.py` | MD → tex/pdf/docx | `md_to_pdf()`, `md_to_tex()`, `md_to_docx()`, `write_docx_fallback()` |

## 使用示例

```python
# 统一导入（通过 __init__.py）
from templates import read_data, data_summary, plot_lines, regression_report

df = read_data('data/raw/附件1.xlsx')
data_summary(df)
plot_lines(range(len(df)), {'功率': df['功率']})
regression_report(y_true, y_pred, '模型名')
```

## utils 工具

除了 templates/，`utils/` 也提供通用工具：

| 模块 | 核心函数 |
|------|---------|
| `utils/file_utils.py` | `ensure_dir()`, `read_file()`, `save_output()` |
| `utils/logger.py` | `write_log()`（markdown 格式, 给 CLAUDE.md 工作流）, `setup_logger()`（实时日志, 控制台+文件） |

## 关于 solvers.py 的设计

`solvers.py` **不是算法名录**，而是按**问题场景**组织的参考：
- 场景A: 连续决策 + 线性约束
- 场景B: 离散决策 + 组合优化
- 场景C: 指派/分配
- 场景D: 非线性/非凸
- 场景E: 多目标

每个场景列出**可选方法**，让你先识别问题类型，再选合适方法。避免"手里有锤子看什么都像钉子"的路径依赖。

> 复杂方法不一定更好。在保证复杂度适中的前提下，选最合适的算法才重要。
