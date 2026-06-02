# 数学建模竞赛模板

大一第一次单人打数学建模竞赛，发现有限时间根本来不及做那么多事情，所以我做了这套模板

不是想封装一个"万能框架"——数学建模的题千奇百怪，框架反而碍事。只是想把那些**比赛期间一定会重复做的事**标准化：读数据、出图、算指标、校验结果、写论文。让下次拿到题目时，可以跳过环境搭建和重复造轮子，直接进入拆题和建模。

拿到题目后，让你和 AI 协作能**跳过环境搭建**，直接进入拆题和建模。

## 快速开始

```bash
# 1. 初始化环境（安装依赖）
python setup.py

# 2. 读 CLAUDE.md 了解工作方式
# 3. 把题目数据放到 data/raw/
# 4. 拆题 → 在 problems/ 下创建问题文件夹 → 开写
```

## 目录结构

```
math_modeling_template/
│
├── CLAUDE.md              # Agent 行为准则（新 agent 必读）
├── README.md              # 本文件
├── setup.py               # 初始化脚本（装依赖 + 建目录）
├── quick_start.py         # 快速示例
│
├── config/                # 赛时参数
│   ├── settings.py       # 全局设置（路径、样式、种子）
│   └── params.yaml       # 比赛参数（赛时修改）
│
├── data/                  # 数据
│   ├── raw/              # 原始数据（只读）
│   ├── processed/        # 清洗后数据
│   └── README.md         # 数据规范
│
├── templates/             # 脚手架代码（参考实现，不是框架）
│   ├── README.md         # 设计哲学 + 速查表
│   ├── __init__.py
│   ├── data_preprocessing.py   # 数据读取/清洗
│   ├── visualization.py         # 论文级图表
│   ├── metrics.py               # 评价指标
│   ├── prediction.py            # 预测参考实现
│   ├── solvers.py               # 求解器参考（按问题类型组织）
│   ├── sensitivity.py           # 敏感性分析
│   ├── validation.py            # 校验工具
│   └── paper_tools.py          # MD → tex/pdf/word
│
├── problems/              # 赛时创建（每题一个文件夹）
│   └── README.md          # 问题脚本规范
│
├── logs/                  # 过程日志
│   └── README.md          # 日志规范
│
├── paper/                 # 论文
│   ├── template/
│   │   ├── template.tex  # LaTeX 模板
│   │   └── template.md   # MD 起手框架
│   └── README.md          # 写作规范
│
└── utils/                 # 小工具
    ├── file_utils.py     # 文件操作
    └── logger.py         # 日志封装
```

## 工作流

```
拿到题目
  ↓ 拆解（写入 logs/）
物理对象是什么？→ 已知/未知/约束 → 子问题分解 → 预期输出
  ↓ 确认
和用户对齐理解
  ↓ 执行
data/raw → problems/problem_N/main.py → 出图 → 校验
  ↓ 验证
交叉验证 + 物理一致性 + 敏感性分析
  ↓ 论文
paper/template/template.md → Pandoc 转 .tex → PDF
```

## 依赖

```
numpy pandas matplotlib scipy scikit-learn
pulp openpyxl python-docx pyyaml
# 以下按需安装
xgboost lightgbm torch statsmodels pmdarima
```

## 比赛策略要点

- **假设合理性 > 方法高级程度**：脱离实际的假设是最大扣分项
- **物理意义 > 数学形式**：建模创造性强调整对问题的原创思考
- **敏感性分析是区分点**：系统化参数扫描，展示参数理解深度
- **逻辑闭环 > 单点突破**：假设→建模→求解→验证→分析，完整闭环

