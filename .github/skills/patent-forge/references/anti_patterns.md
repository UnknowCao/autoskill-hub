# Anti-Patterns & Error Handling（禁止行为与错误处理）

> **用途**: patent-forge 完整 21 条 Anti-Patterns 大表 + Error Handling Matrix 的单一事实源。SKILL.md 仅保留**高频 8 条**（#1/#2/#3/#4/#17/#18/#20/#21）作为快速警示，完整内容在本文件。
>
> **位置**: `references/anti_patterns.md`（相对于 skill 根目录）。

---

## 🚫 Anti-Patterns（21 条硬性红线）

**以下行为在 patent-forge 中绝对不允许。** 违反任一条 → 立即中止当前 Phase 并纠正。

| # | 禁止 | 正确做法 | 后果 |
|---|------|---------|------|
| 1 | **在 `disclosure` 中撰写权利要求书** | 交底书由代理师后续撰写权利要求，发明人只需交底技术方案（`shared_workflow.md` § Phase 3D Actions） | 侵占代理师职责 → 文档作废 |
| 2 | **在等待用户确认的 🔴 CHECKPOINT 处继续执行** | 每个 CHECKPOINT 标记处**必须暂停**并等待用户明确"通过/修改/重写"，不自动继续（`SKILL.md` § Phase 3A/3D） | 未经确认的输出不可用 → 重做 |
| 3 | **在 Phase 0 未确认 doc-type 时默认走 `application`** | 若用户 prompt 经关键词过滤（排除发明内容描述中的词汇）后仍无法唯一确定 doc-type，必须 `vscode_askQuestions` 询问（`shared_workflow.md` § Phase 0 Actions 2-3）。**发明内容描述中的关键词（如"权利要求"在"一种专利权利要求自动撰写的方法"中）不作为 doc-type 信号** | 产出的文档类型错误 → 全部重做 |
| 4 | **跳过 Phase 2 现有技术检索** | 即使 API key 缺失也必须按搜索工具分层 fallback（anysearch skill → tavily skill → fetch_webpage）执行检索，且必须输出「最接近现有技术 + 区别特征 + 技术效果」三步分析（`shared_workflow.md` § Step 2.4-2.6 + Checkpoint 2） | 权利要求失去新颖性支撑 → 驳回风险 |
| 5 | **使用产品名 / 品牌名 / UI 术语**（如 iPhone、Google、点击按钮） | 替换为通用设备术语 / 标准专利表述，详见 [`api_and_terminology.md`](./api_and_terminology.md) § Language Conventions | 不符合中国专利法用语规范 → 形式审查驳回 |
| 6 | **对从属权利要求的引用基础（antecedent basis）不做校验** | 每条从属权利要求引用的对象必须在此前已定义，为引入新术语前必须引用附图中对应的标记号（10/20/30...） | 引用无基础 → 驳回（实施细则第 22 条） |
| 7 | **生成无文字描述的"裸图"** | 每张附图必须有对应的详细文字说明（含参考标号、功能描述、连接关系）。`disclosure` 中每个附图编号输出一次图题 + 一次文字描述 | 附图不清楚 → 驳回（专利法第 26 条第 3 款） |
| 8 | **在权利要求中使用"优选地 / 优选的 / 大约 / 较佳"等模糊限定语** | 权利要求必须使用"用于...的...装置"/"包括...的步骤"等确定性语言，模糊限定语只可用于说明书中 | 权利要求不定 → 驳回（专利法第 26 条第 4 款） |
| 9 | **在摘要中引用权利要求编号或使用"如权利要求 1 所述的..."句式** | 摘要独立于权利要求，≤300 字单段，无引用编号。摘要附图仅标注最有代表性的一幅 | 摘要格式不合格 → 形式审查驳回 |
| 10 | **在 `--doc-type application` 中不提供 IPC 分类号** | Phase 2 Step 2.7 必须识别 1-3 个 IPC 主分类号 + CPC 对应号（`shared_workflow.md` § Step 2.7） | 申请表不完整 → 不予受理 |
| 11 | **把 Phase 1 中用户未确认的发明的理解直接用于 Phase 2 检索** | Phase 1 结束后必须经 🔴 CHECKPOINT 1 显示 4 要素并获用户确认，再进入 Phase 2 | 检索方向错误 → 对比文件不相关 |
| 12 | **在 `--docx` 模式中跳过模板填充验证** | 运行 `fill_acip_template.py fill` 后必须检查其 stdout 的 `filled` / `skipped` 清单，任何 `skipped` 字段必须告知用户并征求处理方式（详见 [`docx_mode.md`](./docx_mode.md) § 3） | 字段缺失 → 代理师退回 |
| 13 | **混淆申请日/优先权日/公开日/授权日** | 在对比文件分析中**必须**标注每件专利的优先权日（新颖性判断的法律依据），不可用申请日或公开日替代。详见 `shared_workflow.md` § Date Discipline | 新颖性判断依据错误 → 权利要求保护范围失准 |
| 14 | **仅用关键词检索现有技术，不跑 IPC/CPC 分类号二次检索** | 初始关键词检索后，必须从 top 5 命中中提取 IPC/CPC 分类号，再跑一次分类号限定检索（`shared_workflow.md` § Step 2.7.1）。关键词检索平均遗漏 15-30% 相关现有技术 | 漏检关键对比文件 → 授权后被无效 |
| 15 | **不生成现有技术文献清单** | `application` 模式必须输出「现有技术文献清单」（含公开号/标题/优先权日/相关性），供代理师和审查员核查检索充分性（`SKILL.md` § Phase 3A Action 8） | 检索不可追溯 → 审查员质疑检索质量 |
| 16 | **对非软件类发明强制使用软件维度（数据流/触发条件/架构）的实施例变化** | 根据 Phase 1 识别的技术领域选择匹配的实施例变化维度（详见 [`domain_matrix.md`](./domain_matrix.md) § 2） | 实施例与发明类型不匹配 → 公开不充分（专利法第 26 条第 3 款） |
| 17 | **在 Phase 1 信息不足时编造技术细节（核心技术特征 / 技术效果 / 实施场景）填补空白以推进 Phase 2** | 触发 Checkpoint 1-warning，向用户展示已收集信息 + 缺失项清单，由用户选择 ① 补充信息后继续 / ② 缩减保护范围继续（用户明确确认风险）（`shared_workflow.md` § Phase 1 Action 6-7）。**禁止自行编造"技术问题/技术效果/核心模块"细节填补 4 要素空白** | 编造内容 → 说明书不支持权利要求 → 驳回（专利法第 26 条第 3/4 款）；编造的"现有技术对比"构成虚假陈述 |
| 18 | **在 `disclosure` 遇未注册代理机构时提供 ACIP 通用模板 fallback** | 当用户提及的代理机构（如"三环"/"中科"）在 `assets/templates/template_registry.md` 中无注册时，**仅允许暂停**等用户放入专属 .docx 模板（`<agency>_invention_disclosure.docx`）后重试。**禁止提供 ACIP 通用模板作为 fallback**，**禁止生成 `-generic-` 文件名文档**（详见 [`docx_mode.md`](./docx_mode.md) § 1 + `template_registry.md` 决策树） | 产出不匹配代理模板的文档 → 退回重做 |
| 19 | **调用 CNIPA.AI 的撰写端点**（`POST /patent-writing/analyze`、`POST /patent-writing/generate-claims`）**生成权利要求或技术分析** | CNIPA.AI **仅可使用检索端点**（`GET /patents/search`、`GET /patents/:id`）用于 Phase 2 现有技术检索。撰写端点生成的权利要求不受 Checkpoint 3A-claims 管控，且存在用语不规范 / 不支持说明书的风险（专利法 26.4）。权利要求必须由本 skill 按中国专利法实施细则自行撰写并经用户确认（详见 [`api_and_terminology.md`](./api_and_terminology.md) § CNIPA.AI「本 skill 不使用的端点」） | 外部 AI 生成的权利要求不合规 → 驳回风险；绕过 Checkpoint 3A 红线 |
| 20 | **在 Phase -1（Material Intake）用户已提供文件后，Phase 1 跳过读取直接进入访谈，或访谈中忽略文件已覆盖的要素反复追问** | Phase 1 Action 0（Material Pre-load）：用户在 Phase -1 提供的文件**必须先按 `shared_workflow.md` § M.2.1 文件转换集成的扩展名决策表选择处理器**（纯文本 `read_file`；富格式 .docx/.pdf/.xlsx/.pptx/图片/音频用 `markitdown-enhanced` skill 的 `_convert_core.py` 转 `.md`）读取并摘要，再进入 Action 1-7 访谈。已由文件覆盖的 4 要素（技术领域/问题/方案/效果）直接采用，访谈只针对文件未覆盖的空白项（`shared_workflow.md` § Phase -1 M.2.1 + M.3 + Phase 1 Action 0） | 忽略用户提供的高质量材料 → 重复追问惹恼用户 + 文件中的关键细节丢失 → 交底书/申请表质量下降 |
| 21 | **用"提醒新颖性风险" / "建议检索" / "建议委托专业机构" 等措辞代替实际执行 Phase 2 检索步骤**（提醒 ≠ 执行）| Phase 2 Step 2.1-2.7 必须实际执行（即使 API key 缺失也要按搜索工具分层 fallback 跑完，并在 Checkpoint 2 产出**三计数审计日志 + 最接近现有技术 + 区别特征**）。**仅在以下两种明确情境下才可使用"建议委托专业机构"**：(1) 主搜索分层全部不可用（Layer 3 fetch_webpage 无 URL 可抓）；(2) 命中数 < 3 条。在其他情境下仅写"建议检索"而未实际执行 = 等同 Anti-Pattern #4（跳过检索）| 提醒不产出检索证据 → 权利要求失去新颖性支撑 → 驳回风险（与 #4 同等严重）|

> 此清单不是建议——是硬性红线。所有 Anti-Patterns 在 `quality_checklists.md` 的清单 A / 清单 D 中有对应的 checklist 项作为双重校验。每次 Checkpoint 4A / 4D 触发时，除加载 `quality_checklists.md` 外，还应快速回顾本表对应行。
>
> **2026-07-27 darwin 优化新增 #21**：基于 dim8 实测发现——baseline assistant 知道该做 Phase 2 检索，但仅用"提醒新颖性风险"代替实际执行。skill 现明确编码：**提醒 ≠ 执行检索**。

---

## ⚠️ Error Handling Matrix（错误处理矩阵）

系统级故障处理规则——发生故障时按如下策略应对，不中断用户体验：

| 故障类型 | 行为 |
|----------|------|
| CNIPA.AI 返回 HTTP 401/403 | key 无效或额度耗尽 → 告知用户检查 `CNIPA_API_KEY` → 降级到 SerpAPI/Exa.ai（若可用）+ 主搜索层兜底。审计日志中记录 CNIPA.AI 状态 |
| CNIPA.AI 返回 0 结果或 HTTP 429 | 用同义词扩展关键词或加 IPC 码（如 `q=H01M battery`）重试一次 → 仍失败则跳过 CNIPA.AI，交由 SerpAPI/Exa.ai（若可用）+ 当前搜索工具层（anysearch/tavily/fetch_webpage）兜底。审计日志中记录 API 状态 |
| SerpAPI 返回 0 结果或 HTTP 429 | 等待 3s → 用同义词扩展关键词重试一次 → 仍失败则跳过 SerpAPI，交由 Exa.ai（若可用）+ 当前搜索工具层（anysearch/tavily/fetch_webpage）兜底。审计日志中记录 API 状态 |
| Exa.ai 返回 0 结果 | 尝试 `type: "fast"` 重试（缩短 query 至前 5 词）→ 仍失败则交由当前搜索工具层（anysearch/tavily/fetch_webpage）兜底 |
| 所有专利 API（CNIPA.AI + SerpAPI + Exa.ai）均不可用（或未配置 key） | 不影响主检索——按搜索工具分层 fallback 运行（anysearch skill → tavily skill → fetch_webpage），Checkpoint 2 中注明「未使用专利专用 API，仅基于分层工具检索结果，建议委托专业检索机构」 |
| 主搜索工具分层全部不可用（anysearch/tavily skill 缺失 + fetch_webpage 无 URL 可抓） | 标记为「新颖性初步确认（无已知现有技术，检索能力降级）」，**禁止断言「全球首创」**——必须在 Checkpoint 2 中告知用户检索工具不可用，建议委托专业机构。不可跳过 Phase 2（违反 Anti-Pattern #4） |
| 无法精确确定 IPC 分类号 | 列出 3-5 个候选分类号 + 候选理由 → Checkpoint 2 中请用户确认 → 若用户也无法确定，保留所有候选号，标注"建议代理师复核 IPC" |
| DOCX 生成失败（`fill_acip_template.py` 报错） | 根据错误类型处理（见 [`docx_mode.md`](./docx_mode.md) § 3），最终兜底方案为回退到 `.md`（**仅作异常兜底**，需征得用户同意后采用，输出文件名不加 `-generic-` 后缀） |
| 3 次连续工具调用失败（跨所有搜索源） | 停止检索，向用户说明已尝试的方法 + 缺失的信息，询问是否：① 补充 API key 后重试 ② 基于已有结果继续 ③ 跳过检索直接撰写（用户承担新颖性风险） |
| 用户拒绝回答 Phase 1 已知现有技术访谈 | 不强求，标注"用户未提供已知现有技术"，以"冷启动"模式进入 Phase 2 |
| 检索命中数 < 3 条 | 在 Checkpoint 2 中明确告知用户"可能为小众领域或检索策略需调整"，**禁止编造对比文件** |

---

## 高频违规 Top 8（SKILL.md 内嵌的快速警示）

以下 8 条是实测中 LLM 最易违反的，已内嵌在 SKILL.md 主体作为快速警示；完整 21 条见上表。

| # | 一句话摘要 | 触发场景 |
|---|---|---|
| 1 | disclosure 不写权利要求书 | 交底书场景 |
| 2 | CHECKPOINT 必须暂停 | 每个 🔴 标记处 |
| 3 | doc-type 不默认 application | Phase 0 关键词过滤后仍歧义 |
| 4 | 禁止跳过 Phase 2 检索（API key 缺失也要分层 fallback） | Phase 2 API 不可用时 |
| 17 | 信息不足禁止编造 | Phase 1 访谈不足 |
| 18 | disclosure 未注册代理 **只允许暂停**（不再提供通用模板 fallback） | 未注册代理机构 |
| 20 | 用户提供的文件必须读取，禁止忽略 | Phase -1 提供文件后 Phase 1 跳过读取 |
| 21 | **"提醒新颖性风险" ≠ 执行检索**（提醒不产出证据）| Phase 2 仅写"建议检索"未实际跑 |

---

## 交叉引用

- 清单 A / 清单 D（双重校验）→ `quality_checklists.md`
- `--docx` 错误处理 → `docx_mode.md` § 3
- 领域相关禁令（#16）→ `domain_matrix.md` § 2
- Phase 流程相关禁令（#3/#4/#11/#13/#14）→ `shared_workflow.md`
- CNIPA.AI 检索/撰写边界（#19）→ `api_and_terminology.md` § CNIPA.AI
