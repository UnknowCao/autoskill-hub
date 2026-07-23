# Shared Workflow (Phase 0-2 + Output Format + Principles)

> **用途**: 此文件包含 `application`（专利申请表）与 `disclosure`（技术交底书）两种输出格式**共同需要**的工作流内容。
> SKILL.md 中的 Phase 0 / Phase 1 / Phase 2 / 输出格式说明 / 共通质量原则以此文件为单一事实源。
> 任一 doc-type 都必须先走完 Phase 0 → Phase 1 → Phase 2，再在 Phase 3 分支。
>
> **位置**: `references/shared_workflow.md`（相对于 skill 根目录）。同目录还有 `api_and_terminology.md`（SerpAPI/Exa.ai + 中文专利术语）、`application_example.md`（申请表示例）、`test-prompts.json`（3 条测试 prompt）。模板位于 `../assets/templates/`，原始 .docx 位于 `../assets/raw_templates/`。

---

## Output Format (`--md` / `--docx`)

Parse `$ARGUMENTS` to determine output format:

| Argument | Mode | Output | When to Use |
|----------|------|--------|-------------|
| `--md` (default) | Local Markdown | Save as `.md` file | 内部审阅、版本控制 |
| `--docx` | **Word（填充模板）** | Save as `.docx` by filling an agency template | **提交给外部代理机构时优先使用** —— 格式 100% 匹配对方模板 |

### `--md` Mode（共通）

Save the generated document as a local Markdown file:
- Filename pattern:
  - `application` → `Patent-[ShortTitle]-[YYYYMMDD].md`
  - `disclosure` → `Disclosure-ACIP-[ShortTitle]-[YYYYMMDD].md`
- 保存到 `docs/` 或 `patents/` 目录；若两者均不存在，使用当前工作目录
- 附图由 `patent-figforge` skill 生成 SVG/PNG，文末标注"正式申请/提交需替换为专利制图 / Visio (.vsd) 原图"

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
1. **Domain Analysis**: Identify the technical field (技术领域) AND classify into one of: **软件/算法、机械/结构、电子/电路、化学/材料、混合**。此分类将驱动 Phase 3 的实施例变化维度和附图类型选择
2. **Problem Identification**: Define what technical problem is being solved (技术问题)
3. **Solution Extraction**: Extract the proposed technical solution (技术方案)
4. **Effect Assessment**: Determine the technical effects and advantages (技术效果)
5. **Structured Interview** (when user description is vague): ask follow-up questions until each of the following is concrete:
   - 核心技术特征（novel elements / modules / steps）
   - 新颖性主张（what is believed new vs. existing solutions）
   - 解决的问题与现有方案的差距（gap）
   - 所有关键组件 / 步骤 / 数据流 / 触发条件
   - 至少 3 个可区分的实施场景
6. **Interview Guardrail（最多 3 轮）**：若经过 3 轮追问仍无法满足 5 项中的 ≥4 项：
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

**Actions**:

### Step 2.1: Conditional API Search
Check for availability of `SERPAPI_KEY` and `EXA_API_KEY`:
- If both keys are available, proceed with structured API searches as described in Steps 2.2-2.5
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

### Step 2.3: API Failure Handling

**When SerpAPI returns 0 results or rate-limit error (HTTP 429)**:
1. **Retry once** with synonym-expanded keywords and `num=50`
2. **If still 0 results after retry** → inform user with diagnostic (keywords tried + API status) → fall through to Step 2.4 (WebSearch) automatically
3. **If rate-limit persists (HTTP 429 after retry)** → skip SerpAPI, proceed with Exa.ai only (if available) + Step 2.4 WebSearch

**When Exa.ai returns 0 results**:
1. Attempt `type: "fast"` retry with shorter query (first 5 terms only)
2. **If still 0 results** → inform user → fall through to Step 2.4 WebSearch

**When both SerpAPI and Exa.ai are unavailable or both return 0 results**:
- Automatically proceed to Step 2.5 (Parallel Web Search) and Step 2.6 (Novelty Analysis)
- In the Checkpoint 2 report, note that novelty analysis is based solely on web search results, and recommend professional patent search for filing

### Step 2.4: WebSearch Fallback (Used when APIs unavailable)
When API keys are not available, automatically use the available web search tool (e.g. `WebSearch` / `tavily_search` / `mcp_playwright_browser`):
- Search for relevant patent and technical information using a general web search tool
- Query format: "[user's invention description] prior art patent search comparative analysis"
- Example: search for "[specific technical concept] prior art patent 2025"

### Step 2.5: Parallel Web Search
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
5. **不可跳过此步**——即使 API key 缺失，也需通过 WebSearch 以 `"[分类号] patent"` 格式完成。Anti-Pattern #14 对应

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
| 3 | focus time recommendation prior art | WebSearch | 网页 | 5 | 1 | ✅ |
| 4 | IPC:G06F3/01 patent | WebSearch | 分类号二次 | 7 | 2 | ✅ |

**审计要求**：
- 每条查询记录来源 + 类型（关键词 / 语义 / 分类号二次）
- 至少包含一次分类号二次检索（Step 2.7.1）
- 在 Checkpoint 2 中向用户报告三计数摘要：「共发送 N 条查询，收到 M 条结果，最终引用 K 条对比文件」
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
- **Precision**: Avoid vague marketing terms; use precise technical descriptions from `api_and_terminology.md`
- **Honesty**: Explicitly list potential defects and alternatives
- **Completeness**: All required sections must be present and substantive

---

## Language Conventions

语言规范（避免使用的产品名/UI 术语/品牌名/口语化列表、应使用的设备/通用术语/专利表述列表、Standard Phrases 如 "一种..." / "用于..." / "其特征在于..." 等）的**单一事实源**在 [`api_and_terminology.md`](./api_and_terminology.md) § Language Conventions。两种 doc-type 都必须遵循，此处不再重复以避免漂移。
