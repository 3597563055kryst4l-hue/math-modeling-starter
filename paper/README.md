# paper/ — 论文写作规范

## 工作流

```
1. draft.md 写内容（MD 起手，内容优先）
2. 图表 → figures/ 
3. Pandoc 转 .tex → 手动调格式 → PDF
4. 应急出口：Pandoc 转 .docx 或 write_docx_fallback()
```

## 目录

```
paper/
├── template/
│   ├── template.md      # MD 起手框架（赛时从这里复制）
│   └── template.tex     # LaTeX 模板（含电工杯标准格式）
├── figures/             # 论文正式插图（汇总用）
└── README.md            # 本文件
```

`draft.md` 和最终 `.tex`/`.pdf` 直接在 `paper/` 根目录下，不在 `template/` 里。

## 写作要点

- **摘要决定第一印象**，最后写，但要认真写
- 每个问题单独一节：问题分析 → 假设 → 模型建立 → 求解 → 结果 → 敏感性分析
- 图表有编号有标题，公式有编号
- 敏感性分析是正文，不是附录
- 结论要回应假设的合理性，形成逻辑闭环
- **MD 中插入图片**：`![图1 功率曲线](figures/fig1_功率曲线.png)`
