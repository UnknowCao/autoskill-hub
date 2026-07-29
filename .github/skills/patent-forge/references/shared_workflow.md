# Shared Workflow (Phase -1 to 2 + Output Format + Principles)

> **用途**: 此文件包含 `application`（专利申请表）与 `disclosure`（技术交底书）两种输出格式**共同需要**的工作流内容。
> SKILL.md 中的 Phase -1 / Phase 0 / Phase 1 / Phase 2 / 输出格式说明 / 共通质量原则以此文件为单一事实源。
> 任一 doc-type 都必须先走完 Phase **-1** → 0 → 1 → 2，再在 Phase 3 分支。
>
> **位置**: `references/shared_workflow.md`（相对于 skill 根目录）。同目录还有 `patent_search_apis.md`（专利检索 API 端点）、`language_conventions.md`（撰写语言规范）、`application_example.md` / `application_example_mechanical.md` / `application_example_hybrid.md`（申请表 dogfood 示例：软件 / 机械 / 混合 HW+SW 三类）。模板位于 `../assets/templates/`，原始 .docx 位于 `../assets/raw_templates/`。

---

## Output Format（按 doc-type 强制分流）

**输出格式由 doc-type 唯一决定，不再由用户参数 `--md` / `--docx` 选择：**

| doc-type | 输出格式 | Filename pattern | 何时用 |
|----------|----------|------------------|--------|
| `application` | **`.md`**（唯一路径）| `Patent-[ShortTitle]-[YYYYMMDD].md` | 公司内部申请表（无代理机构专属模板）|
| `disclosure` | **`.docx`**（唯一常规路径）| `Disclosure-[Agency]-[ShortTitle]-[YYYYMMDD].docx`（例：`Disclosure-ACIP-[ShortTitle]-[YYYYMMDD].docx`） | 提交外部代理机构，100% 匹配对方 .docx 版式 |

### `application` → `--md` Mode

Save the generated document as a local Markdown file:
- Filename pattern：`Patent-[ShortTitle]-[YYYYMMDD].md`
- 保存到 `docs/` 或 `patents/` 目录；若两者均不存在，使用当前工作目录
- 附图由 `patent-figforge` skill 生成 SVG/PNG，文末标注"正式申请/提交需替换为专利制图 / Visio (.vsd) 原图"

### `disclosure` → `--docx` Mode（强制）

**disclosure 不再有常规 md 输出**。用户即使未显式说 `--docx`，disclosure 一律填充代理机构 .docx 模板生成。详细步骤见 [`docx_mode.md`](./docx_mode.md)。

**唯一例外**：`.docx` 生成失败（`fill_acip_template.py` 报错）时，按 `docx_mode.md` § 3 错误矩阵处理后的最终兜底输出为 `.md`（filename: `Disclosure-[Agency]-[ShortTitle]-[YYYYMMDD].md`，**不加 `-generic-` 后缀** —— 该后缀随 Anti-Pattern #18 修改已废止）。

#### `.md` 强制后处理（保存前必跑，适用范围：application 常规输出 + disclosure 异常兜底输出）

交付的 `.md` 不能含内部工作流符号（🔴🟠🟡🟢⚠️✅❌ 等），且需把附图内嵌为 Markdown 图片（而非仅文字清单）。保存前**必须**对 .md 跑 [`scripts/postprocess_md.py`](../scripts/postprocess_md.py)：

```bash
# application 常规输出
python scripts/postprocess_md.py final/Patent-X-YYYYMMDD.md \
    --output final/Patent-X-YYYYMMDD.md \
    --figures-dir 04-diagrams \
    --inplace

# disclosure 异常兜底输出（仅当 .docx 生成失败时）
python scripts/postprocess_md.py final/Disclosure-ACIP-X-YYYYMMDD.md \
    --output final/Disclosure-ACIP-X-YYYYMMDD.md \
    --figures-dir 04-diagrams \
    --inplace
```

该脚本做两件事：
1. **剥离 emoji/状态符号** — 与 `fill_acip_template.py` 的剥离规则字节一致（同一正则），保证 `.md` 与 `.docx` 同步。
2. **内嵌附图** — 扫描 `04-diagrams/` 下 `fig<N>_*.png`，在每条图题（如 `- 图 1：...`）下方插入 `![图 N](path)` Markdown 图片。

注：postprocess 只作用于**最终交付的 .md**（`final/` 下），不应用于内部草稿（如 `01-phase1-understanding/`），草稿中可保留 emoji 以辅助评审。

### Output Layout（输出目录结构）

每次运行产出按 6 级目录组织，确保产物可追溯：

```
patent-forge-output/
├── 01-phase1-understanding/
│   └── invention_4_elements.md          # Phase 1: 4 要素提炼 + 用户确认记录
├── 02-phase2-prior-art/
│   ├── search_audit_log.md              # 检索审计日志（三计数）
│   ├── closest_prior_art.md             # 最接近现有技术分析
│   └── ipc_classification.md            # IPC/CPC 分类号及候选理由
├── 03-phase3-document/
│   ├── claims_draft_v1.md               # (application) 权利要求书草案
│   ├── specification_full.md            # 说明书全文
│   └── prior_art_reference_list.md      # 现有技术文献清单
├── 04-diagrams/
│   ├── fig1_architecture.svg            # 整体架构图（patent-figforge 生成）
│   ├── fig2_method_flow.svg             # 方法流程图（patent-figforge 生成）
│   └── fig3_key_module.svg              # 关键模块示意图（patent-figforge 生成）
├── 05-compliance/
│   ├── checklist_A_or_D.md              # 清单 A/D 逐项核对结果
│   └── compliance_report.md             # 合规审查报告
└── final/
    └── Patent-[ShortTitle]-[YYYYMMDD].md   # 最终输出
```

> SKILL.md § Output File Organization 引用本节。强制最低产物：`final/` + `02-phase2-prior-art/` 必须生成，其余按 Phase 进度填充。

---

## Phase -1: Material Intake（素材收集，技能启动第一步）

> **位置**：在 Phase 0（文档类型选择）之前。这是技能与用户的**第一次交互**。
> **目的**：明确告知用户可以提供文件/文档作为输入，而不只是文字描述。一份好的原始材料能让后续 Phase 1-3 的质量提升数倍，且大幅减少访谈轮次。
> **原则**：可选——用户可跳过（"我没有文件，直接聊"），但必须**主动询问一次**，禁止假定用户只能用对话输入。

### M.1 主动询问（与 Phase 0 合并为一次 `vscode_askQuestions`）

技能被触发后，**立即**用 `vscode_askQuestions` 向用户发起第一次询问，**把"素材收集"和"文档类型选择"合并到同一次提问**（Token 优化原则：不分散成多轮打断）。问题结构：

| Header | Question | Options（`allowFreeformInput: true`） |
|--------|----------|--------------------------------------|
| `material-input` | "你是否有现成的技术材料可以提供？这会让交底书/申请表写得更准、更快。" | ① **有文件，我来上传/给路径**<br>② **有文字描述，直接粘贴**<br>③ **什么都没有，从零开始访谈**<br><br>⚠️ 三个选项平等呈现，**禁止预设**用户走①（Anti-Pattern #21）|

- 选 ① → 进入 M.2（等待用户提供文件路径或附件）
- 选 ② → 用户在 freeform 框粘贴文字，进入 Phase 0
- 选 ③ → 直接进入 Phase 0（纯访谈模式）

> **同一轮**的第二个问题（Header `doc-type`）按 Phase 0 § Actions 3 提出。两个问题合并到一次 `vscode_askQuestions` 调用。

### M.2 接受的文件类型（用户选 ① 时展示）

若用户选择"有文件"，向用户展示以下**接受材料清单**（用文字 + 表格，不用 askQuestions），并等待用户提供路径或附件：

| 材料类型 | 文件格式 | 用途（skill 如何使用）|
|---------|---------|---------------------|
| **技术方案文档** | `.md` / `.docx` / `.pdf` / `.txt` | 提取发明 4 要素（技术领域/问题/方案/效果），直接进入 Phase 1，跳过大部分访谈 |
| **需求规格/设计文档** | `.md` / `.docx` / `.xlsx` / `.pdf` | 提取技术细节（参数、流程、数据结构），填充第四节详细阐述 |
| **已有专利草稿/交底书** | `.md` / `.docx` | 作为基础改写/扩充，保留已确认的内容 |
| **会议纪要/技术评审记录** | `.md` / `.docx` / `.txt` | 提取发明点讨论、技术决策依据 |
| **论文/期刊文章** | `.pdf` / `.md` | 提取技术背景 + 作为 Phase 2 现有技术锚点 |
| **已知对比专利** | 公开号/申请号（文字）或 `.pdf` | 作为 Phase 2 最接近现有技术锚点（命中率提升 3-5 倍）|
| **附图/草图** | `.png` / `.jpg` / `.svg` / `.vsd` | 作为第四节附图参考；若可编辑(.svg/.vsd)直接采用 |
| **实验数据/测试报告** | `.xlsx` / `.csv` / `.pdf` | 提取技术效果量化数据（第五节）|
| **代码/算法实现** | `.py` / `.c` / `.cpp` / `.m` / `.md` | 提取算法步骤细节（软件/算法类发明）|

> **处理方式**：按下方 **M.2.1 文件转换集成** 的扩展名决策表选择处理器（`read_file` 纯文本 / `markitdown-enhanced` skill 富格式），提取结构化信息后纳入 Phase 1 的 4 要素提炼。

### M.2.1 文件转换集成（File Conversion Integration，单一事实源）

> **目的**：把"何时用 `read_file`、何时调用 `markitdown-enhanced` skill、怎么调用、失败怎么办"固化为一处规范，供 Phase -1 M.3、Phase 1 Action 0、Anti-Pattern #20 统一引用。
> **关联 skill**：[`markitdown-enhanced`](../../markitdown-enhanced/SKILL.md)（基于 markitdown 0.1.6，支持 .docx/.pdf/.pptx/.xlsx/.html/.csv/.json/.xml/图片(OCR)/音频/YouTube/EPub，含公式转义修复 + 加密文件解密 + 表格结构校验）。

#### M.2.1a 扩展名 → 处理器决策表（必查）

| 文件扩展名 | 处理器 | 理由 |
|-----------|--------|------|
| `.md` `.txt` `.csv` `.json` `.xml` `.py` `.c` `.cpp` `.h` `.java` `.js` `.ts` `.m` `.svg` `.dot` `.gv` | **`read_file`**（内置工具）| 纯文本/代码/矢量源码，无需格式转换 |
| `.docx` `.doc` `.pdf` `.pptx` `.xlsx` `.xls` `.html` `.htm` `.epub` | **`markitdown-enhanced` skill** | 富格式（二进制/排版/表格/公式），需 markitdown 引擎转换 |
| `.png` `.jpg` `.jpeg` `.gif` `.webp` `.bmp` `.tiff` | **`markitdown-enhanced` skill**（含 OCR）| 图片需 OCR 提取文字（附图/扫描件/截图）|
| `.mp3` `.wav` `.m4a` | **`markitdown-enhanced` skill**（含转录）| 音频需转录（如会议录音）|
| `.vsd` `.vsdx` | **`markitdown-enhanced` skill** 或提示用户导出 `.svg` | Visio 图档；附图场景优先请用户导出可编辑 `.svg` |
| 其他/未知扩展名 | **`read_file`** 尝试；失败 → `markitdown-enhanced` 兜底 | 二次尝试策略 |

#### M.2.1b 调用命令（markitdown-enhanced skill）

当决策表指向 `markitdown-enhanced` 时，用以下命令把文件转成 `.md`，再用 `read_file` 读取产物：

```bash
# 单文件转换（含公式修复 + 表格检测 + 元数据头，全管线自动）
# 退出码：0 = 干净；1 = 检测到表格问题（已写 .errors.md 旁车文件，按下方 M.2.1c 自动修复）
python C:\AI\.github\skills\markitdown-enhanced\scripts\_convert_core.py <input_file> -o <output.md>
```

**示例**（用户提供 `技术方案.docx`）：
```bash
python C:\AI\.github\skills\markitdown-enhanced\scripts\_convert_core.py "C:\path\to\技术方案.docx" -o "C:\AI\patent-forge-output\01-phase1-understanding\技术方案.md"
# 转换成功后用 read_file 读取产物，纳入 4 要素提炼
```

> **加密文件**：若 `_convert_core.py` 检测到加密文件（.docx/.xlsx），它会自动通过 `keyring` 查密码；若无密码则弹 Windows CredUI 对话框让用户输入。密码经 `keyring` 存储，**绝不经 chat 明文传递**（详见 markitdown-enhanced SKILL.md §Encrypted File Handling + 仓库记忆 `keyring-vs-cmdkey-pitfall.md`）。若用 `--no-prompt` 则只查 keyring 不弹窗（CI/无人值守场景）。

#### M.2.1c 转换后处理（markitdown 已知缺陷自动修复）

markitdown-enhanced 的 `_convert_core.py` 已内置自动修复，但 AI 须知晓以下已知缺陷（转换后若 sidecar `.errors.md` 存在，按此处理）：

| 缺陷 | 现象 | 处理 |
|------|------|------|
| **公式错误转义** | `$I = C * dV/dt$` 被转义成 `$I = C \* dV/dt$` | `_convert_core.py` 已自动用 `fix_formula_escaping.py` 修复；若仍见残留，单独跑 `python scripts/fix_formula_escaping.py <output.md>` |
| **纵向合并表格列错位** | rowspan 被丢弃，合并行数据左移 | sidecar `.errors.md` 会标注；AI 需对照原文件人工核对数据列（后处理无法区分纵向合并缺列 vs 横向合并少列）|
| **旧版 .doc** | markitdown 不直接支持 | 先用 Word COM 转 `.docx` 再跑 `_convert_core.py` |

> 完整缺陷清单 + 边界条件见 markitdown-enhanced SKILL.md §"⛔ Do NOT" + 仓库记忆 `markitdown-docx-test-pattern.md` / `markitdown-encrypted-table-detect-bug.md`。

#### M.2.1d 失败兜底（Fallback）

| 场景 | 兜底动作 |
|------|---------|
| `markitdown-enhanced` skill 不存在（`C:\AI\.github\skills\markitdown-enhanced\` 缺失）| 告知用户"富格式转换 skill 不可用"，请用户：(1) 把文件另存为 `.md`/`.txt` 后重新提供，或 (2) 直接在 chat 粘贴关键内容。**禁止强行用 `read_file` 读 .docx/.pdf**（会得到乱码二进制）|
| `_convert_core.py` 报错（依赖缺失/文件损坏）| 读 stderr，告知用户具体错误；建议 `pip install "markitdown[all]" msoffcrypto-tool keyring mammoth pywin32` |
| 转换产物为空 / 明显残缺 | 退回 M.4 无文件兜底，用 Phase 1 访谈补齐；告知用户"文件转换失败，将改用访谈收集信息" |

> **红线**：禁止在 `markitdown-enhanced` 不可用时静默用 `read_file` 读取富格式文件并假装成功（会产出乱码，污染 4 要素提炼）。必须显式告知用户降级。

### M.3 读取与摘要（用户提供文件后）

用户提供文件后，技能执行：
1. **读取**：按 **M.2.1a 扩展名决策表** 选择处理器——纯文本扩展名用 `read_file`；富格式扩展名(.docx/.pdf/.pptx/.xlsx/.html/.epub/图片/音频)用 **M.2.1b 的 `_convert_core.py` 命令**转换为 `.md` 后再 `read_file` 读取产物
2. **摘要**：对每个文件生成 ≤200 字摘要，标注"来源：[文件名]"
3. **映射**：将摘要内容映射到 Phase 1 的 4 要素（技术领域/技术问题/技术方案/技术效果），标注哪些要素已"由文件覆盖"、哪些仍需访谈
4. **进入 Phase 0**：带着已摘要的材料，继续文档类型选择 + 后续流程

> ⚠️ **保密提示**：若文件含敏感商业信息，技能应在摘要前提示用户"文件内容仅用于本会话生成交底书/申请表，不会上传外部"。用户确认后继续。

### M.4 无文件兜底（用户选 ② 或 ③）

用户无文件时，进入 Phase 0 正常流程，Phase 1 的结构化访谈将承担全部信息收集职责（访谈深度更深，可能触发 Interview Guardrail 最多 3 轮）。

**Output**: 已读取的材料摘要清单（若有） + 进入 Phase 0。

---

## Phase 0: Document Type Selection

**Goal**: Determine which document type the user needs before any work begins.

**Actions**:
1. Parse `$ARGUMENTS` for `--doc-type application|disclosure`
2. If not specified, infer from keywords in the user's prompt:
   - Mentioned agency name (华进 / ACIP / 华进联合 / 其他代理机构) → `disclosure`
   - Mentioned "交底书" / "交底" / "代理" / "代理人" → `disclosure`
   - Mentioned "申请表" / "申请文件" / "直接申请" → `application`
   - ⚠️ **关键规则：仅匹配用户显式意图中的关键词**（如"请帮我生成专利申请表"中的"申请表"），**发明内容描述中的词汇不作为 doc-type 信号**（如"一种专利权利要求自动撰写的方法"中的"权利要求"是发明主题，不是 doc-type 选择）。若无法区分，回退到 Actions 3（askQuestions）
3. If still ambiguous after keyword filtering, **ask the user explicitly** using `vscode_askQuestions`:
   - Question: "你需要哪种文档？"
   - Options:
     - `application` — **专利申请表**（含权利要求书/摘要，公司内部直接申请用）
     - `disclosure` — **技术交底书**（发明人→代理师交底用，如华进 ACIP）
     - Let user pick; do NOT proceed without a clear answer
4. Once decided, load the corresponding template from `assets/templates/<template>.md`
5. 向用户显式确认文档类型与输出格式："将以 **[文档类型]** 模板生成文档，输出格式：[md/docx]"

**Output**: Confirmed `doc-type` + loaded template path.

---

## Phase 1: Understand the Invention

**Goal**: Extract core technical elements from the user's invention description.

**Actions**:
0. **Material Pre-load（素材预载）**：若 Phase -1（Material Intake）中用户提供了文件，**必须先按 § M.2.1 文件转换集成的扩展名决策表选择处理器**读取并摘要这些文件（纯文本用 `read_file`；富格式 .docx/.pdf/.xlsx/.pptx/图片/音频用 `markitdown-enhanced` skill 的 `_convert_core.py` 转 `.md` 后读取），再进入下述 Action 1-7。已由文件覆盖的要素（技术领域/问题/方案/效果）可直接采用，访谈只针对文件未覆盖的空白项。**禁止忽略已提供的文件直接进入访谈**（Anti-Pattern #20）。若用户未提供文件，跳过本步，Action 1-7 的访谈承担全部信息收集。
1. **Domain Analysis**: Identify the technical field (技术领域) AND classify into one of **6 类**（与 [`domain_matrix.md`](./domain_matrix.md) § 领域判定单一事实源一致）：**软件/算法、机械/结构、电子/电路、化学/材料、混合（HW+SW）、不确定领域**。此分类将驱动 Phase 3 的实施例变化维度和附图类型选择。**混合类判定补充**：除"系统+方法/装置+控制"显式配对词外，"硬件为常规载体 + 算法/控制逻辑为核心创新"（如 BMS 算法、传感器信号处理+估计算法）也归混合类——两类权利要求（硬件含参考标号 + 方法）都要写
2. **Problem Identification**: Define what technical problem is being solved (技术问题)
3. **Solution Extraction**: Extract the proposed technical solution (技术方案)
4. **Effect Assessment**: Determine the technical effects and advantages (技术效果)
5. **Structured Interview** (when user description is vague): ask follow-up questions until each of the following is concrete。**本步的 5 个访谈项与 Action 1-4 的 4 要素对应关系**（消除术语歧义）：
   - 核心技术特征（novel elements / modules / steps）↔ 技术方案
   - 新颖性主张（what is believed new vs. existing solutions）↔ 技术效果（创新点依据）
   - 解决的问题与现有方案的差距（gap）↔ 技术问题
   - 所有关键组件 / 步骤 / 数据流 / 触发条件 ↔ 技术方案（细化）
   - 至少 3 个可区分的实施场景 ↔ 技术方案 × 技术效果（验证）
   - **技术领域**（Action 1 已收集）不计入 5 项访谈项
6. **Interview Guardrail（最多 3 轮）**：若经过 3 轮追问仍无法满足 5 项中的 ≥4 项（等价于 4 要素中 ≥3 项不完整）：
   - 🔴 触发 **Checkpoint 1-warning**：向用户展示已收集的信息 + 缺失项清单，告知"当前信息不足以撰写可专利的完整文档"
   - 请用户选择：① 补充缺失信息后继续 / ② 缩减保护范围，基于现有信息继续（需用户明确确认风险）
   - **禁止在用户选择前继续 Phase 2**
7. **Known Prior Art Anchoring（已知现有技术锚定）**：在 CHECKPOINT 1 之前，向用户提问：
   > "你是否已见过接近本发明的现有技术？如有，请提供专利号或论文标题。没有也没关系，直接说'没有'即可。"
   - 若用户提供已知现有技术（专利号/论文标题/产品名）→ 以此为锚点，在 Phase 2 中优先检索其周边技术，大幅提升检索精度
   - 若用户回答"没有"→ 以"冷启动"模式进入 Phase 2
   - 接受非正式引用（论文标题、产品名称、发明人姓名均可）
   - 若用户拒绝回答 → 不强求，标注"用户未提供已知现有技术"后继续
   - **为什么这一步关键**：patent skill 的经验表明，已知一件相关专利可让检索从"大海捞针"变为"定点扩展"，检索命中率提升 3-5 倍

🔴 **CHECKPOINT 1 — 必须暂停**：向用户复述提炼出的 4 要素 + 访谈要点，等待用户明确确认通过后再进入 Phase 2。若用户指出偏差，回到 Actions 1-5 修正。**禁止在用户确认前继续 Phase 2。**

**Output**: Structured understanding of the four key elements.

---

## Phase 2: Prior Art Search

**Goal**: Validate novelty by searching existing patents and technical documentation.

**搜索工具分层（关键）**——在 Step 2.1 之前，按以下优先级**探测并选定本会话使用的搜索工具**。检索全程使用同一工具层，不混用：

| 层级 | 工具 | 探测方式 | 能力 | 用于哪些 Step |
|------|------|---------|------|--------------|
| **Layer 1（首选）** | `anysearch` skill | 检查 `.github/skills/anysearch/SKILL.md` 是否存在 | 多引擎关键词检索 + 内容提取（最全面）| 2.2-2.7 全部 |
| **Layer 2（次选）** | `tavily` skill | anysearch 不存在时，检查 `.github/skills/tavily/SKILL.md` 是否存在 | Tavily 关键词检索 + URL 内容提取 | 2.2-2.7 全部 |
| **Layer 3（兜底）** | `fetch_webpage`（内置工具）| 上述两个 skill 均不存在时使用 | **仅能抓取已知 URL，不能关键词检索** | 仅 2.5（已知 URL） |
| **Optional 增强（专利 API，优先级递减）** | ① **CNIPA.AI**（首选，中国专利中心）→ ② SerpAPI → ③ Exa.ai | 检测 `CNIPA_API_KEY` / `SERPAPI_KEY` / `EXA_API_KEY` 环境变量（可多选叠加）| 专利专用 API，CNIPA.AI 中国专利覆盖最佳 | 叠加在任一主搜索层上，增强 2.2/2.7.1 |

**探测顺序**（必须严格执行，禁止跳级）：
1. 先查 `anysearch` skill 是否存在 → 存在则选定 Layer 1，跳到 Step 2.1
2. 再查 `tavily` skill 是否存在 → 存在则选定 Layer 2，跳到 Step 2.1
3. 两个 skill 均不存在 → 选定 Layer 3（`fetch_webpage`），**必须在 Checkpoint 2 中显式告知用户「当前仅有 fetch_webpage 兜底，无法做关键词检索，新颖性分析基于有限已知来源，强烈建议委托专业专利检索」**
4. **专利专用 API 探测**（与上面主搜索层独立，可叠加）：按优先级检测 `CNIPA_API_KEY`（首选）→ `SERPAPI_KEY` → `EXA_API_KEY`，**有 key 则启用对应 API 作为增强层**（可多个同时启用，CNIPA.AI 优先调用）。端点详见 [`patent_search_apis.md`](./patent_search_apis.md) § CNIPA.AI / SerpAPI / Exa.ai

**禁止行为**：
- 禁止跳过探测直接假定某 skill 或 API key 存在
- 禁止在 Layer 3（仅 fetch_webpage）下声称做了「关键词检索」——fetch_webpage 只能抓 URL
- 禁止因为某个 skill 或 API key 不存在就跳过 Phase 2（违反 Anti-Pattern #4）
- **禁止调用 CNIPA.AI 的撰写端点**（`/patent-writing/analyze`、`/patent-writing/generate-claims`）—— 仅用其检索端点（Anti-Pattern #19）

**Actions**:

### Step 2.1: Conditional API Search
Check for availability of `CNIPA_API_KEY` / `SERPAPI_KEY` / `EXA_API_KEY`（按优先级，CNIPA.AI 首选）:
- If any key is available, the corresponding API (Step 2.2) is layered ON TOP of whichever search tool layer (1/2/3) was selected above — it does NOT replace the layer selection. **CNIPA.AI 若可用则优先调用**（中国专利覆盖最佳），其次 SerpAPI，再次 Exa.ai
- If keys are missing, skip Step 2.2 entirely; the selected search-tool layer (1/2/3) handles Steps 2.3-2.7 alone

### Step 2.2: API Patent Search (Optional Enhancement, only if API keys present)
Execute only if API keys are available. **调用顺序：CNIPA.AI → SerpAPI → Exa.ai**（按可用性，全部结果合并去重）。CNIPA.AI 作为首选因其中国专利覆盖最佳；SerpAPI 补全球覆盖；Exa.ai 补语义模糊场景：

**Method A（首选）: CNIPA.AI**（中英双语自动翻译匹配，中国专利中心）— 端点详见 [`patent_search_apis.md`](./patent_search_apis.md) § CNIPA.AI
```bash
# Example: Search for AR gesture recognition patents (英文输入自动匹配中文专利)
curl -X GET "https://api.cnipa.ai/v1/patents/search?q=(augmented%20reality)%20gesture%20recognition" \
  -H "Authorization: Bearer ${CNIPA_API_KEY}" \
  -H "Content-Type: application/json"
# 可加 IPC 码：q=G06F gesture recognition
# 详情：GET /patents/:id 获取权利要求/说明书/法律状态
```

**Method B: SerpAPI Google Patents** (Keyword-based, 全球专利补覆盖)
```bash
# Example: Search for AR gesture recognition patents
curl -s "https://serpapi.com/search.json?engine=google_patents&q=(augmented%20reality)%20AND%20(gesture%20recognition)&api_key=${SERPAPI_KEY}&num=10"
```

**Method C: Exa.ai** (Semantic, 概念模糊场景)
```bash
# Example: Semantic search for similar inventions
curl -X POST 'https://api.exa.ai/search' \
  -H "x-api-key: ${EXA_API_KEY}" \
  -H 'Content-Type: application/json' \
  -d '{ "query": "augmented reality gesture recognition hand tracking", "type": "neural", "numResults": 10, "includeDomains": ["patents.google.com"] }'
```

**Extract from API results**:
- Patent IDs and titles
- Publication dates
- Key claims and technical solutions
- Assignees and filing dates

### Step 2.3: API Failure Handling

**When CNIPA.AI returns 0 results or HTTP 401/403/429**:
1. **Retry once** with synonym-expanded keywords 或加 IPC 码（如 `q=H01M battery`）
2. **HTTP 401/403** → key 无效或额度耗尽 → 告知用户检查 `CNIPA_API_KEY` → 降级到 Method B/C（SerpAPI/Exa.ai）
3. **0 结果重试仍失败 / HTTP 429** → 跳过 CNIPA.AI，继续调用 SerpAPI/Exa.ai（若可用）+ Step 2.4 主搜索层。审计日志记录 CNIPA.AI 状态

**When SerpAPI returns 0 results or rate-limit error (HTTP 429)**:
1. **Retry once** with synonym-expanded keywords and `num=50`
2. **If still 0 results after retry** → inform user with diagnostic (keywords tried + API status) → fall through to Step 2.4 (current search-tool layer) automatically
3. **If rate-limit persists (HTTP 429 after retry)** → skip SerpAPI, proceed with Exa.ai only (if available) + Step 2.4 (current search-tool layer)

**When Exa.ai returns 0 results**:
1. Attempt `type: "fast"` retry with shorter query (first 5 terms only)
2. **If still 0 results** → inform user → fall through to Step 2.4 (current search-tool layer)

**When all patent APIs (CNIPA.AI + SerpAPI + Exa.ai) are unavailable or all return 0 results**:
- Automatically proceed to Step 2.5 (Parallel Search via current search-tool layer) and Step 2.6 (Novelty Analysis)
- In the Checkpoint 2 report, note that novelty analysis is based solely on the selected search-tool layer results (not patent-specific API), and recommend professional patent search for filing

### Step 2.4: Search-Tool Layer Fallback (replaces old "WebSearch Fallback")
This step uses the search-tool layer selected in the **搜索工具分层** block above (not a generic `WebSearch`):
- **Layer 1 (anysearch skill)**: 调用 anysearch skill 执行关键词检索；query format: `"[user's invention description] prior art patent search comparative analysis"`
- **Layer 2 (tavily skill)**: 调用 tavily skill 执行关键词检索；query format 同上
- **Layer 3 (fetch_webpage)**: **不能做关键词检索**——只能抓取用户已知/已提供的 URL（如 Phase 1 锚定的已知现有技术专利链接）。若用户未提供任何 URL，此层只能基于 Phase 1 访谈内容进行推理，必须在 Checkpoint 2 中显式标注「未执行关键词检索」

### Step 2.5: Parallel Search (using selected layer)
Using the search-tool layer selected above (Layer 1/2 only; Layer 3 跳过本步并标注降级), gather comprehensive context:

1. **Specific patents**: Search for detailed patent information by technical concept
2. **Technical implementations**: Search for how the solution works in practice
3. **Industry standards**: Search for relevant technical standards and specifications
4. **Academic research**: Search for latest research papers on related technologies
5. **Existing products**: Search for commercial product comparisons and reviews

Search query patterns (customize based on invention):
- "[user's specific technical concept] vs [similar concept] patent"
- "[user's solution approach] implementation challenges and approaches"
- "[domain] technical standards and requirements 2025"
- "recent research [user's technical concept] academic papers"
- "[user's solution category] commercial implementation comparison"

### Step 2.6: Novelty Analysis

**Synthesize findings** from both API and web search results:
1. **Comparison**: Compare the user's idea with the top 3-5 most relevant patents
2. **Prior Art Identification**: Identify the closest prior art (最接近的现有技术)
3. **Distinguishing Features**: Determine distinguishing features (区别技术特征)
4. **Novelty Gaps**: Note any potential novelty gaps or white spaces
5. **Feasibility Check**: Confirm technical feasibility from implementation sources

**Date Discipline（日期纪律）**：对每件命中专利，必须区分四类日期并标注：

| 日期类型 | 定义 | 在新颖性分析中的作用 |
|----------|------|---------------------|
| **优先权日** (Priority Date) | 最早主张优先权的日期 | **新颖性判断的唯一依据**——优先权日早于本发明 = 构成现有技术 |
| **申请日** (Filing Date) | 首次提交申请的日期 | 用于确定审查顺序，**不可**用于新颖性判断 |
| **公开日** (Publication Date) | 申请文件公开的日期（通常优先权日后 18 个月） | 技术进入公共领域的时间点 |
| **授权日** (Grant Date) | 专利被授予的日期 | 权利生效日期，与新颖性判断无关 |

> **铁律**：在对比文件分析（Step 2.8）中，**必须标注每件对比文件的优先权日**，并以优先权日为准判断其是否构成本发明的现有技术。绝不可用申请日或公开日替代。

**若未找到任何相关现有技术**（所有搜索方法均返回 0 结果）：
- 将此标记为"新颖性初步确认（无已知现有技术）"
- 🔴 在 Checkpoint 2 中向用户说明此情况，并建议委托专业专利检索机构做全面的专利性检索
- **禁止直接得出结论为"全球首创"**——网络搜索覆盖范围有限，可能存在未收录的专利/论文

### Step 2.7: IPC Classification

**Identify the IPC (International Patent Classification) symbols** for the invention:
- 确定 1-3 个主分类号（IPC subclass / group），用于检索扩展与申请表填写
- 同步识别 CPC 分类号以便检索 US/EP 现有技术

**若无法精确确定 IPC 分类号**：
1. 列出 3-5 个候选分类号，逐一说明候选理由及不确定原因
2. 🔴 在 Checkpoint 2 中向用户展示候选列表，请用户选择或确认
3. **若用户也无法确定** → 保留所有候选号，在申请表中标注"建议由代理师复核 IPC 分类"
4. **禁止在用户确认 IPC 候选前进入 Phase 3**（IPC 错误导致检索方向偏移 → 驳回风险）

**Output**: IPC classification list with rationale.

### Step 2.7.1: IPC/CPC Class-Restricted Secondary Search（分类号二次检索）

> **核心 Insight（源自 patent skill）**：关键词检索存在固有盲区——不同申请人用不同术语描述相同技术概念。纯关键词检索平均遗漏 15-30% 的相关现有技术。分类号二次检索能找回其中大部分遗漏。

1. 从初始关键词检索的 **top 5 命中专利**中提取 IPC/CPC 分类号
2. 选取出现频次最高的 1-2 个分类号，**在所有可用搜索源中再跑一次分类号限定检索**
3. 若分类号检索发现新对比文件 → 并入 Step 2.6 新颖性分析，在 Step 2.8 中标注来源为"IPC/CPC 二次检索"
4. 若分类号检索未发现新对比文件 → 记录在审计日志（Step 2.9）："IPC/CPC 二次检索无新增对比文件"（这是正面信号，说明关键词检索覆盖较全）
5. **不可跳过此步**——即使 API key 缺失，也需通过当前搜索工具层（Layer 1/2）以 `"[分类号] patent"` 格式完成；Layer 3（fetch_webpage）下无法执行关键词分类号检索，审计日志显式标注降级。Anti-Pattern #14 对应

### Step 2.8: Novelty Articulation

明确陈述以下三点（后续权利要求书与发明内容的撰写基础）：
1. **最接近的现有技术**：1 篇，记录申请号 + 优先权日 + 技术方案 + 技术效果
2. **区别技术特征**：列出本发明与最接近现有技术的区别（≥ 1 项）
3. **区别带来的技术效果**：每个区别特征对应的技术效果

🔴 **CHECKPOINT 2 — 必须暂停**：向用户展示新颖性分析结论（最接近现有技术 + 区别特征 + 技术效果 + 三计数审计摘要），等待用户明确确认通过后再进入 Phase 3。若新颖性弱或区别模糊，回到 Phase 2 重新检索或请用户补充技术细节。**禁止在用户确认前进入 Phase 3。**

**Output**: Comprehensive prior art analysis with novelty assessment.

### Step 2.9: Audit Trail（检索审计日志）

记录检索过程完整轨迹，用于证明检索充分性（三计数规则：查询发送数 / 专利收到数 / 专利引用数）：

| # | 查询语句 | 来源 | 类型 | 返回结果数 | 引用结果数 | 状态 |
|---|---------|------|------|-----------|-----------|------|
| 1 | (ML) AND (recommendation) | SerpAPI | 关键词 | 10 | 3 | ✅ |
| 2 | neural calendar scheduling | Exa.ai | 语义 | 8 | 2 | ✅ |
| 3 | focus time recommendation prior art | anysearch/tavily | 关键词 | 5 | 1 | ✅ |
| 4 | IPC:G06F3/01 patent | anysearch/tavily | 分类号二次 | 7 | 2 | ✅ |

**审计要求**：
- 每条查询记录来源 + 类型（关键词 / 语义 / 分类号二次）+ **使用的工具层**（Layer 1 anysearch / Layer 2 tavily / Layer 3 fetch_webpage / Optional SerpAPI / Optional Exa.ai）
- 至少包含一次分类号二次检索（Step 2.7.1）—— Layer 3（fetch_webpage）下若无法执行分类号检索，审计日志必须显式标注「IPC 二次检索因工具能力降级未执行」
- 在 Checkpoint 2 中向用户报告三计数摘要：「共发送 N 条查询，收到 M 条结果，最终引用 K 条对比文件」+ **本次会话使用的搜索工具层**
- 此审计日志同时作为「现有技术文献清单」（Phase 3A Action 8）的数据源

---

## 说明书章节粒度指南（Section Granularity Guide）

> **来源**：参考 patent-application-creator 的最佳实践。以下粒度标准适用于 `--doc-type application` 的各章节撰写，确保输出标准化、不遗漏关键内容。

| 章节 | 目标篇幅 | 内容要点 |
|------|---------|---------|
| **技术领域** | 1-2 段 | 明确所属技术领域，引用 Phase 2 确定的 IPC 分类号 |
| **背景技术** | 2-3 段 | ① 现有技术状况概述 ② 现有技术存在的问题与不足 ③ 引述最接近现有技术（含公开号 + 优先权日） |
| **发明内容** | 3-5 段 | ① 要解决的技术问题（对应背景技术中的不足）② 技术方案概述（对应独立权利要求）③ 有益效果（逐一对应区别技术特征） |
| **附图说明** | 每图 1 句 | 格式：「图 N 是……的示意图/流程图/框图」，仅描述图的内容，不展开技术说明 |
| **具体实施方式** | ≥ 全文 50% | 至少 3 个实施例，贯穿参考标号（10/20/30...）。变化维度按技术领域选择（详见 SKILL.md § Phase 3A Action 5）：软件类—数据流/触发条件/架构；机械类—驱动方式/几何构型/材料；电子类—电路拓扑/元件选型；化学类—配比/合成条件；不确定领域—实现机制/结构配置/操作条件 |
| **权利要求书** | 独立 1-3 条 + 从属 10-20 条 | 独立权利要求二段式（前序部分 + 其特征在于）；从属权利要求逐层限定，覆盖优选实施方式与 fallback 位置 |
| **摘要** | ≤ 300 字，单段 | 技术方案概述 + 主要用途，不得包含权利要求式限定语，不得引用权利要求编号，指明一幅最有代表性的摘要附图 |

> 以上粒度标准已纳入 `quality_checklists.md` 清单 A 作为逐项核对依据。

---

## 共通质量原则（Common Quality Principles）

适用于所有 doc-type 与输出格式：

- **Grantability**: Focus on technical solutions, not abstract ideas
- **Precision**: Avoid vague marketing terms; use precise technical descriptions from `language_conventions.md`
- **Honesty**: Explicitly list potential defects and alternatives
- **Completeness**: All required sections must be present and substantive

---

## Language Conventions

语言规范（避免使用的产品名/UI 术语/品牌名/口语化列表、应使用的设备/通用术语/专利表述列表、Standard Phrases 如 "一种..." / "用于..." / "其特征在于..." 等）的**单一事实源**在 [`language_conventions.md`](./language_conventions.md)。两种 doc-type 都必须遵循，此处不再重复以避免漂移。
