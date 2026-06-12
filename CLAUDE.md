# 数学建模竞赛 — Agent 操作手册

本项目是一个数学建模竞赛的**工作环境**，不是框架。它定义了一套完整的比赛工作流，让 AI agent 能高度自主地执行，用户只需要做关键决策。

---

## 零、用户做什么？

**只需要做一件事：把题目材料放到项目根目录。**

放的方式可以是以下任意一种：
- 把题目文件夹（含数据文件）拖进来
- 把题目 PDF 放进来
- 把题目压缩包放进来

放好之后，对 agent 说"开始"即可。后续 agent 会自动执行以下全部流程，只在关键决策点停下来问你。

---

## 一、启动流程（自动执行）

当你收到"开始"指令时，按以下顺序执行：

### Step 1：扫描题目材料

1. 扫描项目根目录，识别用户放入的文件/文件夹
2. 判断题目材料的类型：
   - 是 PDF/Word 题目描述？→ 读取内容
   - 是文件夹（含数据文件）？→ 遍历所有文件
   - 是压缩包？→ 自动解压到 `data/raw/`
3. 将题目描述文件移动到 `data/raw/` 统一管理
4. 输出一份**题目清单**到 `logs/`，列出：找到的文件、各自格式、大致内容

### Step 2：智能初始化

不要直接跑 `setup.py`。先判断题目需要什么：

1. **读题目**：如果有 PDF/Word 题目描述，先读内容，了解这个比赛在做什么
2. **扫数据**：看 `data/raw/` 下的所有数据文件：
   - 格式是什么？（Excel / CSV / JSON / 图片 / 文本 / 数据库）
   - 数据量多大？（几百行？几十万行？）
   - 数据类型是什么？（数值 / 时序 / 文本 / 图像 / 混合）
3. **按需初始化**：
   - 运行 `python setup.py` 装基础依赖、建目录
   - 如果数据包含图片 → 装 `opencv-python pillow`
   - 如果数据量非常大 → 考虑提示用户用采样或 `chunksize`
   - 如果数据需要特殊数据库连接 → 装对应驱动
4. **写初始化日志**到 `logs/`：
   - 题目类型判断
   - 数据概览（行数、列数、缺失情况）
   - 已安装的额外依赖
   - 发现的风险点

### Step 3：初始化报告 → 请用户确认

将 Step 1-2 的结果整理成一份清晰报告呈现给用户，确认后再进入拆题。

---

## 二、拆题流程

### Step 4：深度分析题目 → 填写框架（先猜后确认）

逐字逐句读题目要求，然后**你来做结构化分析**，不要丢给用户填空题：

1. 读题后，调用 `phase0_context.run(problem_text=原文, agent_guess=你的推断)` 生成框架
2. 框架包含 6 个维度，你的推断填入 `proposed_entries`：
   - **system_components** — 题目涉及哪些物理实体/子系统？（风电、光伏、电解槽、储能...）
   - **decision_variables** — 要决策什么变量？（符号、单位、类型、范围）
   - **constraints** — 受什么限制？（功率平衡、上下限、绿电比例...）
   - **objective** — 目标是什么？（吨氨成本最小化、利润最大化...）
   - **external_parameters** — 哪些是外部给定的？（出力曲线、电价...）
   - **subproblems** — 分几问？每问要什么输出？

3. 每个维度加上 confidence：`high` 表示你很有把握、`medium` 表示需要人确认、`low` 表示不确定

**示例输出（不用这种空格式）：**
```
❌ 不要空着让人填：

decision_variables:
  entries: []
```

**应该是这样的：**
```
✅ 你读完题后写好的：

decision_variables:
  proposed_entries:
    - symbol: P_wind
      description: 风电出力功率
      units: MW
      type: continuous
      range: "[0, 40]"
    - symbol: P_elec
      description: 电解槽功率
      units: MW
      type: continuous
      range: "[0, 20]"
  confidence: high
  note: "题目附件2给出了典型日出力曲线"
```

### Step 5：框架 → 请用户确认

呈现给用户，逐项确认：
- **系统组件** — "我猜有这些子系统，对吗？漏了什么？"
- **决策变量** — "我猜要决策这些变量，方向对吗？"
- **约束条件** — "我总结了这些约束，有没有漏掉重要的？"
- **目标** — "目标是这个，确认？"
- **外部参数** — "这些是题目给定的，我理解对吗？"
- **子问题** — "题目的 Q1-Q5 我这样拆分，合理吗？"

用户确认或修正后，框架正式确定，进入编码阶段。**在用户确认之前，不要进入编码阶段。**

---

## 三、执行流程

---

## 三、执行流程

用户确认拆题后，逐问执行。**每完成一问，立即展示结果，再进入下一问。**

### Step 6：新建问题目录

对每一问 Q1/Q2/Q3...，用脚手架脚本创建：

```bash
python scripts/new_problem.py 1 --desc "问题一：功率预测"
python scripts/new_problem.py 2 --desc "问题二：风电场选址" --deps problem_1
```

这会在 `problems/problem_N/` 下自动生成：

```
main.py         # 求解骨架（已 import 所有模板工具）
verify.py       # 校验骨架（已 import validation 工具）
config.yaml     # 本问参数
results/
  ├── figures/
  ├── data/
  └── report.md
```

`main.py` 用 `try/except` 处理了路径导入，可以直接 `python problems/problem_N/main.py` 运行。

如果某问依赖前一问的结果，用 `--deps problem_prev` 标注（会生成 DEPENDS_ON 文件记录依赖关系）。

### Step 7：编写并运行求解脚本

1. 参考 `templates/` 下的脚手架代码编写 `main.py`
2. 选择方法时遵循建模第一原则：先问物理对象，再选数学工具
3. 运行 `main.py`，输出结果到 `problems/problem_N/results/`
4. 图表保存到 `paper/figures/`，命名规则：`fig{N}_{描述}.png`
5. 每完成一小步写日志到 `logs/`

### Step 8：编写并运行校验脚本

1. 参考 `templates/validation.py` 编写 `verify.py`
2. 必须包含：
   - 数值合理性检查（数量级、正负号、边界情况）
   - 交叉验证（如果有多种方法可用）
   - 物理一致性检查（结果是否符合现实直觉）
3. 运行 `verify.py`，结果写入 `logs/`

### Step 9：敏感性分析

1. 参考 `templates/sensitivity.py`
2. 对模型中的关键参数做扰动分析（至少 ±5%、±10%、±20%）
3. 出敏感性分析图 → `paper/figures/`
4. 分析哪些参数对结果影响最大，写入日志

### Step 10：展示当前问结果

整理结果呈现给用户：
- 核心结论
- 关键图表
- 校验结果
- 敏感性分析发现
- 存在风险 / 待决策点

**用户确认后，进入下一问。**

---

## 四、论文流程

### Step 11：生成论文

所有问题求解完成后：

1. 复制 `paper/template/template.md` 到 `paper/draft.md`
2. 填入内容：摘要、问题分析、模型假设、符号说明、模型建立与求解、检验与敏感性分析、优缺点
3. **摘要最后写**，但它是第一印象

### Step 12：导出论文

优先用 `templates/paper_tools.py`：
- `md_to_pdf()` — 如果环境有 Pandoc + LaTeX
- `md_to_docx()` — Word 格式，兼容性最好
- `write_docx_fallback()` — 纯 Python 应急方案

**论文初稿完成后，请用户审阅修改。**

---

## 五、评分导向（建模铁律）

1. **假设的合理性优先于方法的高级程度**。脱离实际的假设是最大扣分项。
2. **建模的创造性强调针对具体问题的原创性思考**，物理意义比数学形式更重要。
3. **敏感性分析是论文的重要区分点**。系统化参数扫描，展示对参数的理解深度。
4. **完整性和逻辑闭环比单点突破更重要**。假设→建模→求解→验证→分析，完整闭环。

---

## 六、铁律（建模第一原则）

**先问物理对象是什么，再问数学工具有哪些，最后用数据或机理验证匹配度。**

永远不要先选模型再硬凑假设。手里有个锤子就到处找钉子——这是最大的扣分项。

---

## 七、src/ 使用原则（不可妥协）

src/ 目录提供的是 **基础工具链，不是算法库**。它的作用是消除重复劳动（读数据、画图、出表格、交叉验证分割），不是替你选择解题方法。

**三条铁则：**

1. **算法选择服务于问题，不是服务于 src/。** 如果当前问题最适合的方法 src/ 里没有，直接现场写代码实现，不要退而求其次用 src/ 里有的次优方案。src/ 里只有线性回归≠你只能用线性回归。

2. **可以混用。** 允许且鼓励的做法：用 src/ 做数据加载和出图，但核心求解算法自己写。例如 `phase1_data.py` 读数据 → 自定义一个 XGBoost 模型 → `phase5_viz.py` 出图 → `phase6_report.py` 出报告。src/ 的各个模块可以独立使用，不需要绑定整个流水线。

3. **永远不要因为"src/ 里有现成的"而推荐一个不合适的算法。** 这是"锤子找钉子"在代码层面的具体表现形式，直接违反建模第一原则。

## 八、批判性思维

- 用户的假设如果不合理，直接指出来，解释为什么，给出替代方案
- 如果某个方法不适合当前问题，说明原因，不要为了迁就用户而硬做
- 每个结论都要问自己：这个结论有没有其他可能的解释？数据是否支持？
- 发现自己犯错时立即纠正，不要试图掩盖或合理化

---

## 九、交叉验证

- 模型结果要用多种方式验证：换算法、换数据子集、用物理直觉检验
- 对于关键数值结论（最优解、预测精度、参数敏感度），至少用两种方法独立求解对比
- 数值结果要做 sanity check：数量级对不对？正负号对不对？边界情况对不对？
- 结论之间要自洽：如果问题1的结论和问题3的结论矛盾，必须停下来排查

---

## 十、日志规范

每做一个小步骤，必须写入 `logs/` 目录下的 md 文件。

文件命名规则：`logs/YYYYMMDD_HHMM_主题.md`

每个日志文件结构：

```markdown
# [简短标题]

## 时间
YYYY-MM-DD HH:MM

## 做了什么
[具体操作]

## 为什么这样做
[理由和依据]

## 结果
[关键发现/输出]

## 下一步
[计划做什么]

## 备注
[需要用户确认的点、发现的问题、潜在风险]
```

日志写给你自己看——假设读日志的人完全不知道之前发生了什么，也能通过日志还原整个过程。

---

## 十一、用户决策点（必须停下来问）

以下情况**必须**停下来问用户，不能自主决定：

1. 初始化报告确认（数据发现、风险点）
2. 问题拆解确认（子问题划分、理解是否准确）
3. 模型的关键假设方向
4. 特征选择的取舍
5. 算法选择（当多种方法都合理时）
6. 论文的整体结构和重点
7. 发现数据质量问题需要丢弃或修改数据时
8. 需要补充外部数据或资料时

### 可以自主决定

- 代码实现细节
- 数据清洗的具体操作（但要记录原因）
- 可视化的样式
- 评价指标的选择（可以全部计算，让用户看）

---

## 十二、执行规范

- 每完成一小步，立即写日志（不要攒着一起写）
- 遇到需要用户决策的点，停下来问用户
- 发现之前某个步骤有错误，立即回溯纠正并记录
- 代码每写完一个可运行的版本就测试，不要写一大堆再测
- 不同问题之间可能存在依赖关系（如 Q2 要用 Q1 的结果），注意执行顺序

---

## 可用工具速查

以下是本项目提供的所有可用函数。按需 import 使用：

### templates/（脚手架代码）

| 模块 | 函数 | 用途 |
|------|------|------|
| `data_preprocessing` | `read_data(path, sheet=0)` | 读取 Excel/CSV |
| | `read_multi_sheet(path)` | 读取多 sheet Excel |
| | `data_summary(df)` | 数据概览（shape, 缺失, 统计量） |
| | `normalize(df, columns, method)` | 归一化/标准化 |
| `visualization` | `set_paper_style()` | 设置论文级 matplotlib 样式 |
| | `plot_lines(x, y_dict, ...)` | 折线图（多组对比） |
| | `plot_bar(categories, values_dict, ...)` | 柱状图（多组对比） |
| | `plot_heatmap(data, row_labels, col_labels, ...)` | 热力图 |
| | `subplots_grid(nrows, ncols)` | 多子图布局 |
| `metrics` | `rmse(y_true, y_pred)` | 均方根误差 |
| | `mae(y_true, y_pred)` | 平均绝对误差 |
| | `mape(y_true, y_pred)` | 平均绝对百分比误差 |
| | `r2(y_true, y_pred)` | R² 决定系数 |
| | `regression_report(y_true, y_pred, name)` | 回归指标报告 |
| | `compare_models(y_true, pred_dict)` | 多模型对比 |
| `prediction` | `train_sklearn(X_train, y_train, X_test, type)` | ML 预测（RF/Ridge/XGB/LGB） |
| | `train_arima(train_data, test_len, order)` | ARIMA 时序预测 |
| | `train_lstm(data, seq_len, epochs)` | LSTM 时序预测（返回 `y_pred, y_true, model, scaler`） |
| | `compare_models(X_train, y_train, X_test, y_test)` | 多模型自动对比 |
| `solvers` | `solve_lp(c, A_ub, b_ub, ...)` | 线性规划 |
| | `solve_dp_example(stages, states, cost)` | 动态规划示例 |
| | `solve_assignment(cost_matrix)` | 指派问题（匈牙利算法） |
| | `solve_ga(fitness, init_pop, ...)` | 遗传算法 |
| | `pareto_front(scores)` | Pareto 前沿 |
| `sensitivity` | `scan_param(func, name, values, ...)` | 单参数扫描 |
| | `plot_sensitivity(result, ...)` | 敏感性可视化 |
| | `perturbation_analysis(func, params, pct)` | 扰动分析 |
| `validation` | `sanity_check(val, name, range, ...)` | 数值合理性检查 |
| | `power_balance(supply, demand, tolerance)` | 供需平衡检查 |
| | `cross_validate(results_dict)` | 多方法交叉验证 |
| `paper_tools` | `md_to_pdf(md_path)` | MD → PDF（需 Pandoc + LaTeX） |
| | `md_to_tex(md_path)` | MD → .tex |
| | `md_to_docx(md_path)` | MD → .docx（需 Pandoc） |
| | `write_docx_fallback(title, sections)` | 纯 Python 应急生成 Word |

### utils/（通用工具）

| 模块 | 函数 | 用途 |
|------|------|------|
| `file_utils` | `ensure_dir(path)` | 确保目录存在 |
| | `read_file(path)` | 自动识别格式读取（Excel/CSV/JSON/YAML） |
| | `save_output(data, path)` | 自动识别格式保存（CSV/JSON/YAML） |
| `logger` | `write_log(topic, content)` | 写 markdown 日志（给本工作流用） |
| | `setup_logger(name, log_dir)` | 配置实时日志（控制台+文件） |
| `batch` | `run_scenarios(solver_fn, param_grid)` | 多场景批量执行，返回结果列表 |
| | `aggregate_scenarios(results)` | 聚合批处理结果（均值/方差/分位数） |
| | `categorize_scenarios(agg, field, threshold)` | 三档分类（全满足/部分/不满足） |

### src/（Phase 流水线）

所有 Phase 模块通过 `PhaseRunner` 编排，也可单独 import 使用：

| Phase | 模块 | 核心函数 | 用途 |
|-------|------|----------|------|
| **0 — 题意分析** | `phase0_context` | `run(problem_id)` | 输出题目结构化框架（组件/变量/约束/目标/参数），由人确认填空 |
| **1 — 数据** | `phase1_data` | `load_raw_data(path)` | 加载 CSV / Excel / TXT |
| | | `quick_eda(df)` | 数据概览（shape、缺失率、统计量） |
| | | `clean_data(df, strategy)` | 清洗（drop / fill_mean / fill_median） |
| **2 — 模型** | `phase2_model` | `build_model(type, params)` | 从注册表构建模型规范 |
| | | 内置模型 | linear_regression / arima / svm |
| **3 — 求解** | `phase3_solve` | `solve_lr(x, y, alpha)` | 线性回归（最小二乘 + L2正则） |
| | | `solve_lp(c, A_ub, b_ub, bounds)` | **线性规划**（min c@x, 约束 A_ub@x <= b_ub） |
| | | `solve_milp(c, integrality, ...)` | **混合整数线性规划**（整数/0-1变量） |
| | | `solve_scipy_minimize(obj, x0)` | 通用非线性优化（L-BFGS-B / SLSQP） |
| | | `solve_curve_fit(model, x, y)` | 非线性最小二乘拟合 |
| | | `solve_odeint(deriv, y0, t)` | ODE 微分方程求解（RK45） |
| | | `solve_root(func, x0)` | 非线性方程组求根 |
| | | `solve_ttest(sample1, sample2)` | 两样本 t 检验 |
| **4 — 验证** | `phase4_validate` | `residual_analysis(residuals)` | 残差诊断（均值、标准差、极值） |
| | | `compute_aic(n, rss, k)` | AIC 模型选择准则 |
| | | `compute_bic(n, rss, k)` | BIC 模型选择准则 |
| | | `kfold_cv(x, y, k)` | K 折交叉验证 |
| | | `check_state_variables(traj, bounds)` | **状态变量校验**（SOC 含储能系统用） |
| | | `sensitivity_by_noise(x, y)` | 噪声扰动敏感性分析 |
| **5 — 可视化** | `phase5_viz` | `plot_residuals(res, path)` | 残差图（散点 + 直方图） |
| | | `plot_fit(x, y, y_pred, path)` | 拟合图（数据 + 回归线） |
| **6 — 报告** | `phase6_report` | `build_summary_table(...)` | Markdown 结果汇总表 |
| | | `build_latex_table(...)` | LaTeX 表格（可直接粘论文） |
| | | `export_markdown_report(...)` | 完整 Markdown 报告 |
| | | `export_latex_report(...)` | 完整 LaTeX 报告（可编译） |
| **模板** | `problem_templates` | `get_template(id)` | 获取 MCM A/B/C/D 模板 |
| | | `apply_template_to_config(id, cfg)` | 合并模板配置 |

### config/（全局配置）

| 模块 | 导出 | 用途 |
|------|------|------|
| `settings` | `PATHS` | 项目路径字典 |
| | `RANDOM_SEED` | 全局随机种子（42） |
| | `set_plot_style()` | 设置 matplotlib 样式 |

## 目录速查

| 目录 | 用途 | 操作 |
|------|------|------|
| `config/` | 全局参数配置 | 需要时修改 `params.yaml` |
| `data/raw/` | 原始数据（只读） | 用户放入题目材料的位置 |
| `data/processed/` | 清洗后数据 | 自动生成 |
| `templates/` | 脚手架代码 | 参考/调用/复制修改 |
| `problems/` | 问题求解 | 每问自动建一个文件夹 |
| `problems/problem_N/main.py` | 求解脚本 | 自动生成并运行 |
| `problems/problem_N/verify.py` | 校验脚本 | 自动生成并运行 |
| `problems/problem_N/config.yaml` | 本题参数 | 自动生成 |
| `problems/problem_N/results/` | 输出结果 | 自动生成 |
| `logs/` | 过程日志 | 每步自动写入 |
| `paper/` | 论文 | 自动从模板生成 |
| `paper/figures/` | 图表 | 自动保存 |
| `utils/` | 小工具 | 直接 import |