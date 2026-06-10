# 数学建模竞赛工作环境

大一第一次单人打数学建模竞赛，发现有限时间根本来不及做那么多事情，所以做了这个。

不是想封装一个"万能框架"——数学建模的题千奇百怪，框架反而碍事。只是把那些**比赛期间一定会重复做的事**标准化：读数据、出图、算指标、校验结果、写论文。让 AI agent 能高度自主地执行，你只做关键决策。

## 使用方式

```bash
# 1. 把题目材料拖进项目根目录（PDF / 文件夹 / 压缩包 都行）
# 2. 对 agent 说"开始"
# 3. 等 agent 自动执行，只在关键决策点回应即可
```

---

## 你只需关注这些

| 你关心的 | 位置 | 说明 |
|---------|------|------|
| 放题目数据 | `data/raw/` | 把题目 Excel/CSV/PDF 放这里 |
| 看求解结果 | `problems/problem_N/results/` | 每问的结果和数据 |
| 看图 | `paper/figures/` | 所有图表汇总到此 |
| 看过程日志 | `logs/` | agent 每步都写 md 日志 |
| 论文草稿 | `paper/draft.md` | agent 自动填入内容 |

其他文件（templates/、utils/、scripts/、config/settings.py 等）都是脚手架代码，agent 会自动使用，你不需要手动管理。

---

## 工作流

详见 [CLAUDE.md](file:///c:/Users/35975/Desktop/agift/math-modeling-starter/CLAUDE.md)，流程概览：

```
用户拖入题目材料 → 说"开始"
  ↓ Step 1-2  agent 自动：扫描材料 + 智能初始化
  ↓ Step 3    agent 报告发现 → 用户确认
  ↓ Step 4-5  agent 拆题 → 用户确认
  ↓ Step 6-10 agent 逐问求解 + 校验 + 敏感性分析 → 每问完展示结果
  ↓ Step 11-12 agent 生成论文初稿 → 用户审阅
  ↓ 完成
```

---

## 接入 CLI / IDE

本项目专门为 AI agent 设计，核心入口是 [CLAUDE.md](file:///c:/Users/35975/Desktop/agift/math-modeling-starter/CLAUDE.md)。以下环境开箱即用：

### Cursor / Windsurf / Trae 等 IDE

```
1. 用 IDE 打开本项目文件夹
2. 把题目材料复制到项目根目录
3. 在对话窗口输入："开始"
```

### Claude CLI / 终端 agent

```bash
cd math-modeling-starter
cp /path/to/题目.pdf ./
claude
# 在 agent 对话中输入："开始"
```

对于不支持自动读取 CLAUDE.md 的 agent，手动告诉它：**"先阅读项目中的 CLAUDE.md 文件，然后按照其中的指示执行。"**

---

## 依赖

```
numpy pandas matplotlib scipy scikit-learn
pulp openpyxl python-docx pyyaml
# 以下按需安装（agent 会根据题目自动判断）
xgboost lightgbm torch statsmodels pmdarima
```

---

## 比赛策略要点

- **假设合理性 > 方法高级程度**：脱离实际的假设是最大扣分项
- **物理意义 > 数学形式**：建模创造性强调整对问题的原创思考
- **敏感性分析是区分点**：系统化参数扫描，展示参数理解深度
- **逻辑闭环 > 单点突破**：假设→建模→求解→验证→分析，完整闭环