# `--docx` Mode（Template Filling）

> **用途**: patent-forge `--docx` 输出模式的详细步骤、错误处理、新代理机构接入流程。SKILL.md § Output Format 仅保留判定逻辑与指针，本文件为单一事实源。
>
> **适用范围**: disclosure **默认且唯一常规输出路径**为 `.docx`。`application` 使用 `.md`（标准申请表格式无代理机构专属模板）。
>
> **位置**: `references/docx_mode.md`（相对于 skill 根目录）。

---

## § 1 何时使用 `.docx`

disclosure 一律输出 `.docx`，不再有常规 `.md` 路径。skill 直接填充代理机构 .docx 模板，保证 100% 匹配对方期望的版式。

**前置条件**：
- `--doc-type` 已确认为 `disclosure`
- 目标代理机构在 `assets/templates/template_registry.md` 中已注册（未注册 → Anti-Pattern #18：**仅允许暂停**等用户放入专属 .docx 后重试，不再提供通用模板 fallback）

---

## § 2 填充流程（4 步）

### Step 1: Locate template（定位模板）

`assets/raw_templates/<agency>_invention_disclosure.docx`（例如 `acip_invention_disclosure.docx`）

**若模板文件不存在** → 告知用户"[agency] 专属 .docx 模板未放入 `assets/raw_templates/`" → 🔴 **触发 Checkpoint**：暂停技能，等用户手动放入 `<agency>_invention_disclosure.docx` 后重试。**不再自动回退到 `.md`**（`--md` 仅作为 `.docx` 生成失败的异常兜底，不作为模板缺失的默认动作）

### Step 2: Build content JSON（构建内容 JSON）

将 Phase 1-3 产出转换为结构化 dict，字段名匹配 `scripts/fill_acip_template.py` 中的 `TEMPLATES[<id>].fields`

### Step 3: Run the fill script（运行填充脚本）

```bash
python scripts/fill_acip_template.py fill \
    --template acip \
    --content invention_content.json \
    --output "Disclosure-ACIP-[ShortTitle]-[YYYYMMDD].docx"
```

> **附图默认嵌入**（自 2026-07-27 起）：`fill` 子命令**默认自动发现并嵌入附图**，无需手动传 `--figures-dir`。附图来源优先级：(1) 显式 `--figures-dir <path>` 参数；(2) `PATENT_FIGURES_DIR` 环境变量；(3) `<skill_root>/../04-diagrams/` 标准 Phase 3 输出目录。嵌入位置为第四节（`details`）单元格末尾，每张图以「图 N」加粗居中标题 + 居中图片形式渲染。**SVG 被跳过**（Word 无法内联嵌入 SVG），始终使用同名的 PNG。如需生成纯文本 .docx（后期手工插图），传 `--no-figures`。

### Step 4: Verify filled fields（校验填充字段）

脚本打印 filled/skipped 列表；确保所有表头 + 内容字段都已填充。同时检查 `Figures embedded:` 行：应列出实际嵌入的图号（如 `[1, 2, 3, 4, 5]`）；若显示 `(none found — no default dir matched)` 说明未找到默认附图目录，需传 `--figures-dir` 或设置 `PATENT_FIGURES_DIR`。

**表格内容约束（重要）**：脚本允许 `terminology`（第 7 节术语表）、`references`（第 8 节参考文献）、`details`（第 4 节技术方案的详细阐述）三个字段渲染为原生 Word 表格。其他章节（背景技术/最接近现有技术/技术问题/发明点/技术效果/替代方案）即使内容中含 markdown 管道符 `|...|`，也会按纯文本输出（`|` 字符保留为字面量），不渲染为嵌套表格。`details` 被纳入白名单是因为第 4 节常含决策树表、Hard Gate 表、参数表等需要 2D 布局的内容。约束实现在 `fill_acip_template.py` 的 `set_cell_text(..., allow_tables=...)` 参数 + `fill_template` 中的 `_TABLE_ALLOWED_FIELDS = {"terminology", "references", "details"}` 白名单。

**表头居中样式（固化）**：所有 markdown 表格渲染为原生 Word 表格时，**表头行单元格文字水平居中**（`para.alignment = WD_ALIGN_PARAGRAPH.CENTER`），数据行保持默认左对齐。表头同时有浅蓝底色（`D9E2F3`）+ 加粗 + 9pt 字号。此样式由 `_render_md_table._write(is_header=True)` 强制，不需调用方传参。

---

## § 3 错误处理矩阵

| 错误类型 | 处理动作 |
|---|---|
| `FileNotFoundError` | 告知用户模板文件路径错误 → 询问用户：① 手动指定正确路径后重试 ② 🔴 **暂停**等用户放入模板（不自动回退 md） ③ 异常兜底：回退到 `--md`（仅在用户明确要求时）|
| `RuntimeError`（table index mismatch）| 运行 `python scripts/fill_acip_template.py inspect --docx <template>` 打印诊断 → 将诊断输出 + 错误信息一并告知用户 → 询问用户：① 手动修正模板后重试 ② 异常兜底：回退到 `--md` |
| `ValueError`（JSON 字段缺失）| 列出缺失字段清单 → 询问用户：① 手动补充后重试 ② 跳过缺失字段直接输出 .docx（标记空字段为 `[待补充]`）③ 异常兜底：回退到 `--md` 模式 |
| stdout 出现 `skipped` 字段 | 列出被跳过的字段清单 → 告知用户 → 询问处理方式（同上 ①②③）|
| stdout 显示 `Figures embedded: (none found ...)` | 默认附图目录无匹配 `fig<N>_*.png` 文件 → 询问用户：① 显式传 `--figures-dir <path>` 指向实际附图目录 ② 设置 `PATENT_FIGURES_DIR` 环境变量 ③ 接受纯文本 .docx 后期手工插图 |
| `--figures-dir` 指向不存在的目录 | 脚本打印 `[WARN] figure N missing: <path>` 并跳过该图 → 检查路径拼写与文件名模式（必须为 `fig<N>_*.png`）→ 重试 |
| SVG 文件被忽略 | 正常行为（Word 无法内联嵌入 SVG）→ 确保 PNG 同名同目录存在；SVG 作为矢量原图保留在 `04-diagrams/` 供代理师后期转 Visio 使用 |

**最终兜底**：所有 .docx 生成失败的兜底方案为回退到 `--md` 模式（输出 `Disclosure-[Agency]-[ShortTitle]-[YYYYMMDD].md`，**不加 `-generic-` 后缀**）。但这是**异常路径**，需在告知用户失败原因 + 征得用户同意后才采用，不作为常规默认动作（Anti-Pattern #12：禁止跳过模板填充验证）。

---

## § 4 添加新代理机构模板（4 步，全脚本化）

```bash
# Step 1: Inspect the new template's table layout
python scripts/fill_acip_template.py inspect --docx new_agency.docx

# Step 2: From the inspect output, derive (row, col) for each field
#         (CRITICAL: merged cells share the same _tc — only fill the
#          first occurrence to avoid overwriting question labels)

# Step 3: Register in TEMPLATES dict (scripts/fill_acip_template.py)
#         AND in assets/templates/template_registry.md (keyword mapping)

# Step 4: Copy .docx to assets/raw_templates/<agency>_invention_disclosure.docx
```

**关键陷阱（合并单元格）**：ACIP 模板 Row 7/8 是「问题-答案」两列结构——cell 0 = 问题标题（**不可覆盖**），cell 2 = 答案栏。其他内容行是全宽合并单元格，写入 cell 0。详见 `scripts/fill_acip_template.py` 的 `TEMPLATES["acip"]["fields"]` 映射表。

---

## 交叉引用

- Anti-Pattern #12（跳过模板填充验证）→ `anti_patterns.md` #12
- Anti-Pattern #18（未注册代理：**仅允许暂停**，不再提供通用模板 fallback）→ `anti_patterns.md` #18
- 代理机构关键词映射 → `assets/templates/template_registry.md`
- 填充脚本 → `scripts/fill_acip_template.py`（subcommands: `fill` / `inspect` / `list`）
- 原始 ACIP .docx 模板 → `assets/raw_templates/acip_invention_disclosure.docx`
