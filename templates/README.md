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
| `data_preprocessing.py` | 数据读取与检查 | `read_data()`, `data_summary()`, `normalize()` |
| `visualization.py` | 论文级图表 | `plot_lines()`, `plot_bar()`, `plot_heatmap()` |
| `metrics.py` | 评价指标 | `regression_report()`, `compare_models()` |
| `prediction.py` | 预测参考 | `train_sklearn()`, `train_arima()`, `compare_models()` |
| `solvers.py` | 求解器参考（按问题类型组织） | `solve_lp()`, `solve_dp_example()`, `solve_ga()`, `pareto_front()` |
| `sensitivity.py` | 敏感性分析 | `scan_param()`, `plot_sensitivity()`, `perturbation_analysis()` |
| `validation.py` | 结果校验 | `sanity_check()`, `power_balance()`, `cross_validate()` |
| `paper_tools.py` | MD → tex/pdf/docx | `md_to_pdf()`, `md_to_tex()`, `write_docx_fallback()` |

## 使用示例

```python
from templates.data_preprocessing import read_data, data_summary
from templates.visualization import plot_lines
from templates.metrics import regression_report

df = read_data('data/raw/附件1.xlsx')
data_summary(df)
plot_lines(range(len(df)), {'功率': df['功率']})
regression_report(y_true, y_pred, '模型名')
```

## 关于 solvers.py 的设计

`solvers.py` **不是算法名录**，而是按**问题场景**组织的参考：
- 场景A: 连续决策 + 线性约束
- 场景B: 离散决策 + 组合优化
- 场景C: 指派/分配
- 场景D: 非线性/非凸
- 场景E: 多目标

每个场景列出**可选方法**，让你先识别问题类型，再选合适方法。避免"手里有锤子看什么都像钉子"的路径依赖。

> 复杂方法不一定更好。在保证复杂度适中的前提下，选最合适的算法才重要。
