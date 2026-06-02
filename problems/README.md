# problems/ — 问题求解规范

## 使用方式

每道题（或每个子问题）在 `problems/` 下新建一个文件夹：

```
problems/problem_1/
├── main.py             # 求解主脚本
├── verify.py           # 结果校验 + 交叉验证
├── config.yaml         # 本问特定参数
└── results/            # 本问输出
    ├── figures/        # 图表
    ├── data/           # 数值结果（csv/json）
    └── report.md       # 结果说明
```

## 文件规范

### main.py

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
from config.settings import set_plot_style, RANDOM_SEED
from templates.data_preprocessing import read_data, data_summary

set_plot_style()
np.random.seed(RANDOM_SEED)

# 1. 读数据
# 2. 建模/求解
# 3. 出图（保存到 results/figures/）
# 4. 输出结果（保存到 results/data/）
```

### verify.py

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from templates.validation import sanity_check, cross_validate

# 1. 加载 main.py 的计算结果
# 2. 合理性检查
# 3. 交叉验证（如适用）
# 4. 生成校验报告
```

## 原则

- 每个问题的脚本尽量独立，避免跨问题 import
- 公共参数放 `config.yaml`，不硬编码在脚本里
- 图表统一 300dpi，中文字体，保存到 `results/figures/`
- 校验不是可选项，是必选项
