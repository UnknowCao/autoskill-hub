# 真实案例 · Real Examples

每个案例都是 `scripts/demo_showcase.py` 或真实转换任务跑出来的产物，挂链接到源文件。不自造虚构样例。

---

## 案例 1：公式逃逸修复（markitdown 0.1.7 上游 bug）

**输入**：`tests/samples/test_formula.docx`（含 `$a * b = c^2$` 等内联公式）

**本家 markitdown 输出**（19 处错误转义，KaTeX 渲染报错）：

```
Multiplication: \*a\ * b = c^2\
```

**x2md 输出**（0 处错误，正常渲染）：

```
Multiplication: $a * b = c^2$
```

**复录**：

```bash
python scripts/demo_showcase.py
# 产物：tests/output/showcase/formula_before.txt（19 bad escapes）
#       tests/output/showcase/formula_after.md（0 escapes）
```

**事故来源**：2026-08-06 实测确认 markitdown 0.1.7 仍存在此 bug。

---

## 案例 2：表格 D2（vertical_merge）检测 + AI 修复

**输入**：`tests/samples/test_merged.docx`（含 rowspan 纵向合并单元格）

**问题**：markitdown 丢掉 rowspan 占位单元格 → 数据行只有 1 列（应为 2 列）→ 数值左移到错误列。**转了，但数据错了，而且不报错**（静默数据损坏）。

**x2md 检测**：`_table_detect.py` 写出 35 行 sidecar（`test_merged.md.errors.md`），含：

- **CAUSE**：rowspan 占位丢失，列左移
- **MD_LOCATION**：line 14-18，expected 2 cols / actual 1
- **HTML_REFERENCE**：mammoth HTML 真值，可重建正确结构

**AI 修复**：读 sidecar → 按 HTML 重对齐 → 标 `<!-- AI-corrected -->` → 删 sidecar → 一行总结。不问用户。

**复录**：

```bash
python scripts/demo_showcase.py
# 产物：tests/output/showcase/table_d2_sidecar.md（35 行，三段式）
```

---

## 案例 3：XLSX 公式求值（=A+B → 实数，非 NaN）

**输入**：`tests/samples/test_formula.xlsx`（openpyxl 生成，含 `=A2+B2` 等公式，无缓存值）

**本家 markitdown 输出**：所有公式格显示 `NaN`（markitdown 只读 `<v>` 缓存，程序生成的 xlsx 不写缓存）。

**x2md 输出**：`_xlsx_formula_eval.py` 用 `formulas` 库算出 15/15 cells，写回 `<v>` → markitdown 读到实数。

**复录**：

```bash
python scripts/demo_showcase.py
# 产物：tests/output/showcase/xlsx_eval_log.txt（15/15 cells resolved）
#       tests/output/showcase/xlsx_after.md（实数表格）
```

---

## 三证据汇总卡

见 [`assets/showcase-card.svg`](../assets/showcase-card.svg)——可截图传播，数字与上述案例一致。

**一键复录全部**：

```bash
python scripts/demo_showcase.py
# 打印 evidence digest + 写入 tests/output/showcase/
```

---

## 真实使用场景（非测试样例）

x2md 在以下真实任务中验证过（产物见各自项目）：

- **汽车电子 SOR/技术文件批量转 md**：`batch_convert_dynamic.py` 跑数千文件，断点续跑
- **加密 docx 解密转换**：CredUI 弹窗（Windows）或 keyring 预注册（Linux/CI）
- **BMS 标准文档**：复杂表格（rowspan/nested）→ sidecar + AI 修复
- **专利交底书**：docx 含 OMML 公式 → 公式逃逸修复 + 表格检测

如需添加你的案例，提 PR 挂产物链接即可。
