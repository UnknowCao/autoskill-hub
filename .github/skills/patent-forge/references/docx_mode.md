# `--docx` Mode（Template Filling）

> **用途**: patent-forge `--docx` 输出模式的详细步骤、错误处理、新代理机构接入流程。SKILL.md § Output Format 仅保留判定逻辑与指针，本文件为单一事实源。
>
> **适用范围**: `--docx` **仅适用于 `--doc-type disclosure`**。对于 `--doc-type application`，使用 `--md`（标准申请表格式无代理机构专属模板）。
>
> **位置**: `references/docx_mode.md`（相对于 skill 根目录）。

---

## § 1 何时使用 `--docx`

当用户指定 `--docx` 时，skill 直接填充代理机构 .docx 模板，而非生成 Markdown。这保证 100% 匹配对方期望的版式。

**前置条件**：
- `--doc-type` 已确认为 `disclosure`
- 目标代理机构在 `assets/templates/template_registry.md` 中已注册（Anti-Pattern #18：未注册时触发 Checkpoint）

---

## § 2 填充流程（4 步）

### Step 1: Locate template（定位模板）

`assets/raw_templates/<agency>_invention_disclosure.docx`（例如 `acip_invention_disclosure.docx`）

**若模板文件不存在** → 告知用户"[agency] 模板文件缺失" → 自动回退到 `--md` 模式，使用 `Disclosure-[Agency]-[ShortTitle]-[YYYYMMDD].md` 文件名 → 若有可编辑模板路径，告知用户手动放入 `assets/raw_templates/` 后可重试 `--docx`

### Step 2: Build content JSON（构建内容 JSON）

将 Phase 1-3 产出转换为结构化 dict，字段名匹配 `scripts/fill_acip_template.py` 中的 `TEMPLATES[<id>].fields`

### Step 3: Run the fill script（运行填充脚本）

```bash
python scripts/fill_acip_template.py fill \
    --template acip \
    --content invention_content.json \
    --output "Disclosure-ACIP-[ShortTitle]-[YYYYMMDD].docx"
```

### Step 4: Verify filled fields（校验填充字段）

脚本打印 filled/skipped 列表；确保所有表头 + 内容字段都已填充。

---

## § 3 错误处理矩阵

| 错误类型 | 处理动作 |
|---|---|
| `FileNotFoundError` | 告知用户模板文件路径错误 → 回退到 `--md` 模式 |
| `RuntimeError`（table index mismatch）| 运行 `python scripts/fill_acip_template.py inspect --docx <template>` 打印诊断 → 将诊断输出 + 错误信息一并告知用户 → 回退到 `--md` 模式 |
| `ValueError`（JSON 字段缺失）| 列出缺失字段清单 → 询问用户：① 手动补充后重试 ② 跳过缺失字段直接输出 .docx（标记空字段为 `[待补充]`）③ 回退到 `--md` 模式 |
| stdout 出现 `skipped` 字段 | 列出被跳过的字段清单 → 告知用户 → 询问处理方式（同上 ①②③）|

**最终兜底**：所有 .docx 生成失败的兜底方案均为回退到 `--md` 模式（Anti-Pattern #12：禁止跳过模板填充验证）。

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
- Anti-Pattern #18（未注册代理静默替换）→ `anti_patterns.md` #18
- 代理机构关键词映射 → `assets/templates/template_registry.md`
- 填充脚本 → `scripts/fill_acip_template.py`（subcommands: `fill` / `inspect` / `list`）
- 原始 ACIP .docx 模板 → `assets/raw_templates/acip_invention_disclosure.docx`
