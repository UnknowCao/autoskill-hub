# Shared Workflow (Phase 0-2 + Output Format + Principles)

> **用途**: 此文件包含 `application`（专利申请表）与 `disclosure`（技术交底书）两种输出格式**共同需要**的工作流内容。
> SKILL.md 中的 Phase 0 / Phase 1 / Phase 2 / 输出格式说明 / 共通质量原则以此文件为单一事实源。
> 任一 doc-type 都必须先走完 Phase 0 → Phase 1 → Phase 2，再在 Phase 3 分支。
>
> **位置**: `references/shared_workflow.md`（相对于 skill 根目录）。同目录还有 `api_and_terminology.md`（SerpAPI/Exa.ai + 中文专利术语）、`application_example.md`（申请表示例）、`test-prompts.json`（3 条测试 prompt）。模板位于 `../assets/templates/`，原始 .docx 位于 `../assets/raw_templates/`。

---

## Output Format (`--md` / `--docx` / `--lark`)

Parse `$ARGUMENTS` to determine output format:

| Argument | Mode | Output | When to Use |
|----------|------|--------|-------------|
| `--md` (default) | Local Markdown | Save as `.md` file | 内部审阅、版本控制 |
| `--docx` | **Word（填充模板）** | Save as `.docx` by filling an agency template | **提交给外部代理机构时优先使用** —— 格式 100% 匹配对方模板 |
| `--lark` | Feishu Cloud Doc | Create via `lark-cli`, using Lark rich-text features | 团队协作、富文本展示 |

### `--md` Mode（共通）

Save the generated document as a local Markdown file:
- Filename pattern:
  - `application` → `Patent-[ShortTitle]-[YYYYMMDD].md`
  - `disclosure` → `Disclosure-ACIP-[ShortTitle]-[YYYYMMDD].md`
- Prefer `docs/` or `patents/` directory, otherwise current working directory
- 附图用 Mermaid 草图，文末标注"正式申请/提交需替换为专利制图 / Visio (.vsd) 原图"

### `--lark` Mode（共通）

Create the document as a Feishu cloud document:

1. **CRITICAL** — Read `${CLAUDE_PLUGIN_ROOT}/skills/lark/lark-shared/SKILL.md` for authentication
2. Read `${CLAUDE_PLUGIN_ROOT}/skills/lark/lark-doc/references/lark-doc-create.md` for Lark-flavored Markdown syntax and `docs +create` parameters
3. Convert the document to Lark-flavored Markdown, applying these enhancements:

| Section | Feishu Feature | Purpose |
|---------|---------------|---------|
| Document metadata (inventor/date/field) | `<lark-table>` | Structured header info with proper column widths |
| Creative points / novelty claims | `<callout emoji="..." background-color="light-blue">` | Highlight distinguishing features |
| Technical problem statement | `<callout emoji="..." background-color="light-yellow">` | Emphasize the problem being solved |
| Architecture / data flow in embodiments | `<whiteboard type="blank">` | Visualize system architecture or process flow |
| Prior art comparison | `<grid cols="2">` | Side-by-side comparison: prior art vs invention |
| Defects / alternatives | `<callout emoji="..." background-color="light-red">` | Clearly mark limitations |
| Claims hierarchy (application only) | Nested ordered lists with `<text color="blue">` for independent claims | Visual distinction between independent and dependent claims |

4. Create the document:
   ```bash
   lark-cli docs +create --title "Patent-[ShortTitle]-[YYYYMMDD]" \
     [--folder-token TOKEN_OR_URL | --wiki-node TOKEN_OR_URL | --wiki-space ID_OR_URL] \
     --markdown "<lark-flavored-markdown>"
   ```
5. For long forms, split creation: `docs +create` for the first half, then `docs +update --mode append` for the rest
6. If `board_tokens` are returned (whiteboards were created):
   - Read `${CLAUDE_PLUGIN_ROOT}/skills/lark/lark-whiteboard/SKILL.md`
   - Fill each whiteboard with actual content (architecture diagrams, flowcharts)
   - All whiteboards must have real content before task is complete
7. Report the document URL

`--lark` mode accepts optional location arguments (mutually exclusive), supporting token or Feishu URL:
- `--folder-token` -- Target folder (token like `fldcnXXXX` or URL like `https://xxx.feishu.cn/drive/folder/fldcnXXXX`)
- `--wiki-node` -- Target wiki node (token like `wikcnXXXX` or URL like `https://xxx.feishu.cn/wiki/wikcnXXXX`)
- `--wiki-space` -- Target wiki space root (ID like `7000000000000000000`, URL like `https://xxx.feishu.cn/wiki/settings/7000000000000000000`, or `my_library`)

Pass URL directly to `lark-cli` — no manual token extraction needed. Defaults to user's personal space root when no location is specified.

### Lark Format Principles（共通）

- Title layer depth max 4 levels
- Do NOT write a top-level heading duplicating the title (Feishu auto-generates it)
- Use `---` dividers between major sections for visual rhythm
- Use `<text color="...">` for key terms and claim markers
- Feishu auto-generates table of contents — do not add manually
- Proactively insert whiteboards for embodiment architectures and process flows

---

## Phase 0: Document Type Selection

**Goal**: Determine which document type the user needs before any work begins.

**Actions**:
1. Parse `$ARGUMENTS` for `--doc-type application|disclosure`
2. If not specified, infer from keywords in the user's prompt:
   - Mentioned agency name (华进 / ACIP / 华进联合 / 其他代理机构) → `disclosure`
   - Mentioned "交底书" / "交底" / "代理" / "代理人" → `disclosure`
   - Mentioned "申请表" / "申请文件" / "权利要求" / "直接申请" → `application`
3. If still ambiguous, **ask the user explicitly** using `vscode_askQuestions`:
   - Question: "你需要哪种文档？"
   - Options:
     - `application` — **专利申请表**（含权利要求书/摘要，公司内部直接申请用）
     - `disclosure` — **技术交底书**（发明人→代理师交底用，如华进 ACIP）
     - Let user pick; do NOT proceed without a clear answer
4. Once decided, load the corresponding template from `assets/templates/<template>.md`
5. Briefly confirm to the user: "将以 **[文档类型]** 模板生成文档，输出格式：[md/lark]"

**Output**: Confirmed `doc-type` + loaded template path.

---

## Phase 1: Understand the Invention

**Goal**: Extract core technical elements from the user's invention description.

**Actions**:
1. **Domain Analysis**: Identify the technical field (技术领域)
2. **Problem Identification**: Define what technical problem is being solved (技术问题)
3. **Solution Extraction**: Extract the proposed technical solution (技术方案)
4. **Effect Assessment**: Determine the technical effects and advantages (技术效果)
5. **Structured Interview** (when user description is vague): ask follow-up questions until each of the following is concrete:
   - 核心技术特征（novel elements / modules / steps）
   - 新颖性主张（what is believed new vs. existing solutions）
   - 解决的问题与现有方案的差距（gap）
   - 所有关键组件 / 步骤 / 数据流 / 触发条件
   - 至少 3 个可区分的实施场景

🔴 **CHECKPOINT 1 — 必须暂停**：向用户复述提炼出的 4 要素 + 访谈要点，等待用户明确确认通过后再进入 Phase 2。若用户指出偏差，回到 Actions 1-5 修正。**禁止在用户确认前继续 Phase 2。**

**Output**: Structured understanding of the four key elements.

---

## Phase 2: Prior Art Search

**Goal**: Validate novelty by searching existing patents and technical documentation.

**Actions**:

### Step 2.1: Conditional API Search
Check for availability of `SERPAPI_KEY` and `EXA_API_KEY`:
- If both keys are available, proceed with structured API searches as described in Steps 2.2-2.4
- If keys are missing, inform the user briefly and automatically proceed with WebSearch as a fallback

### Step 2.2: API Patent Search (Conditional)
Execute only if API keys are available:

**Method A: SerpAPI Google Patents** (Keyword-based)
```bash
# Example: Search for AR gesture recognition patents
curl -s "https://serpapi.com/search.json?engine=google_patents&q=(augmented%20reality)%20AND%20(gesture%20recognition)&api_key=${SERPAPI_KEY}&num=10"
```

**Method B: Exa.ai** (Semantic)
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

### Step 2.3: WebSearch Fallback (Used when APIs unavailable)
When API keys are not available, automatically use Claude's WebSearch tool:
- Use the `WebSearch` tool to find relevant patent and technical information
- Query format: "[user's invention description] prior art patent search comparative analysis"
- Example: `WebSearch("[specific technical concept] prior art patent 2025")`

### Step 2.4: Parallel Web Search
Perform web searches to gather comprehensive context regardless of API availability:

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

### Step 2.5: Novelty Analysis

**Synthesize findings** from both API and web search results:
1. **Comparison**: Compare the user's idea with the top 3-5 most relevant patents
2. **Prior Art Identification**: Identify the closest prior art (最接近的现有技术)
3. **Distinguishing Features**: Determine distinguishing features (区别技术特征)
4. **Novelty Gaps**: Note any potential novelty gaps or white spaces
5. **Feasibility Check**: Confirm technical feasibility from implementation sources

### Step 2.6: IPC Classification

**Identify the IPC (International Patent Classification) symbols** for the invention:
- 确定 1-3 个主分类号（IPC subclass / group），用于检索扩展与申请表填写
- 若无法精确确定，给出 3-5 个候选分类号并说明取舍理由
- 同步识别 CPC 分类号以便检索 US/EP 现有技术

**Output**: IPC classification list with rationale.

### Step 2.7: Novelty Articulation

明确陈述以下三点（后续权利要求书与发明内容的撰写基础）：
1. **最接近的现有技术**：1 篇，记录申请号 + 技术方案 + 技术效果
2. **区别技术特征**：列出本发明与最接近现有技术的区别（≥ 1 项）
3. **区别带来的技术效果**：每个区别特征对应的技术效果

🔴 **CHECKPOINT 2 — 必须暂停**：向用户展示新颖性分析结论（最接近现有技术 + 区别特征 + 技术效果），等待用户明确确认通过后再进入 Phase 3。若新颖性弱或区别模糊，回到 Phase 2 重新检索或请用户补充技术细节。**禁止在用户确认前进入 Phase 3。**

**Output**: Comprehensive prior art analysis with novelty assessment.

---

## 共通质量原则（Common Quality Principles）

适用于所有 doc-type 与输出格式：

- **Grantability**: Focus on technical solutions, not abstract ideas
- **Precision**: Avoid vague marketing terms; use precise technical descriptions from `api_and_terminology.md`
- **Honesty**: Explicitly list potential defects and alternatives
- **Completeness**: All required sections must be present and substantive

---

## Language Conventions

语言规范（避免使用的产品名/UI 术语/品牌名/口语化列表、应使用的设备/通用术语/专利表述列表、Standard Phrases 如 "一种..." / "用于..." / "其特征在于..." 等）的**单一事实源**在 [`api_and_terminology.md`](./api_and_terminology.md) § Language Conventions。两种 doc-type 都必须遵循，此处不再重复以避免漂移。
