# 模板注册表（Template Registry）

> **用途**: 此文件是 `patent-architect` skill 的模板分发入口。所有第三方公司模板在此注册后即可通过 `--template` 参数调用。
> **新增模板流程**: 见本文件末尾"如何添加新公司模板"。

---

## 已注册模板

| Template ID | 名称 | 适用场景 | 输出本质 | 支持 `--docx` | 文件位置 |
|-------------|------|---------|---------|-------------|---------|
| `standard` ⭐ | 标准专利申请表 | 公司内部直接申请，含权利要求书/摘要 | 最终专利申请文件 | ❌（仅 `--md` / `--lark`） | `assets/templates/standard_application.md` |
| `acip` | ACIP（华进）技术交底书 | 通过华进知识产权代理申请 | 发明人 → 代理师的交底材料 | ✅（`fill_acip_template.py`） | `assets/templates/acip_invention_disclosure.md` |

⭐ `standard` 为默认模板，未指定 `--template` 时使用。

---

## 模板选择决策树

```
用户提到要生成专利文档
       │
       ├─ 提到具体代理机构名称？
       │     ├─ 是 → 检查是否在下方"代理机构映射表"中 → 使用对应 template
       │     └─ 否 ↓
       │
       ├─ 文档用途明确？
       │     ├─ 用于外部代理机构提交 → 使用对应代理机构 template（默认 acip）
       │     └─ 用于公司内部直接申请 → 使用 standard
       │
       └─ 仍未明确 → 询问用户："此文档是用于公司内部直接申请，
                                       还是通过代理机构（华进等）提交？"
```

---

## 代理机构关键词映射（自动识别）

当用户在描述中提到以下关键词时，自动切换到对应模板：

| 关键词（不区分大小写） | 模板 |
|---------------------|------|
| 华进 / ACIP / 华进知识产权 / 华进联合知识产权 | `acip` |
| 标准申请 / 内部申请 / 直接申请 | `standard` |
| _（待扩展其他公司）_ | _..._ |

---

## 模板规范（新增模板必须遵循）

每个模板文件必须包含以下章节，确保 skill 行为一致：

1. **元信息块**（文件开头）
   - 来源公司
   - 适用类型
   - 文档本质（交底书 / 申请文件 / 其他）
   - 参考原文路径

2. **撰写须知**（原文摘录或精炼）
   - 来自原模板的撰写指引、注意事项

3. **输出结构**（严格按此顺序）
   - 表头字段（如适用）
   - 各章节标题与撰写要求
   - 章节间的对应关系（如"问题—方案—效果"对应表）

4. **质量自检清单**（模板专属）
   - 与该模板章节一一对应的检查项

5. **输出模式适配**
   - `--md` 模式的文件命名与附图处理
   - `--lark` 模式的飞书富文本特性使用

---

## 如何添加新公司模板

### 步骤 1：获取原始模板

取得第三方公司的原始 `.doc` / `.docx` 模板文件，存放到：
```
c:\AI\.github\skills\patent-architect\assets\raw_templates\<公司简称>_<模板类型>.<原扩展名>
```

例如：`assets/raw_templates/acip_invention_disclosure.doc`

### 步骤 2：转换为 Markdown

使用 markitdown-enhanced 转换（如果是旧版 .doc，先用 Word COM 转 .docx）：

```bash
# 旧版 .doc → .docx（需 Windows + Word）
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("<input.doc>")
$doc.SaveAs2("<output.docx>", 16)
$doc.Close(); $word.Quit()

# .docx → .md
cd c:\AI\.github\skills\markitdown-enhanced
python scripts/_convert_core.py "<output.docx>" -o "assets/templates/<new_template>.md"
```

### 步骤 3：规范化 Markdown

将转换后的 Markdown 按"模板规范"重新组织：
- 补全元信息块、撰写须知
- 提炼输出结构与质量清单
- 删除示例内容，保留模板骨架
- 处理 markitdown 转换副作用（表格错位、公式转义等，详见 markitdown-enhanced SKILL.md）

### 步骤 4：注册到本文件

在"已注册模板"表中追加一行，并在"代理机构关键词映射"表中加入识别关键词。

### 步骤 5：更新 SKILL.md

确保 SKILL.md 的 `--template` 参数文档中已列出新模板。

---

## 已知限制

1. **旧版 .doc 转换**：markitdown 不直接支持 `.doc`，需先用 Word COM 转 `.docx`。
2. **嵌套表格**：ACIP 模板含嵌套表格，markitdown 会压平（已知缺陷 D2/D3，详见 markitdown-enhanced 记忆）。规范化阶段需手工补齐为标准 Markdown 表格。
3. **公式转义**：markitdown 会把 `$...$` 内的 `*` `_` `^` 错误转义，规范化阶段需用 `fix_formula_escaping.py` 后处理。
4. **附图原图**：交底书通常要求提供 `.vsd` 等可编辑图档，skill 只能输出 Mermaid 草图或飞书白板，需在输出末尾明确提示用户补交原图。
