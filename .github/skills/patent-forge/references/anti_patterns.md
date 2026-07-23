# Anti-Patterns & Error Handling（禁止行为与错误处理）

> **用途**: patent-forge 完整 18 条 Anti-Patterns 大表 + 9 行 Error Handling Matrix 的单一事实源。SKILL.md 仅保留**高频 5 条**（#1/#2/#3/#17/#18）作为快速警示，完整内容在本文件。
>
> **位置**: `references/anti_patterns.md`（相对于 skill 根目录）。

---

## 🚫 Anti-Patterns（18 条硬性红线）

**以下行为在 patent-forge 中绝对不允许。** 违反任一条 → 立即中止当前 Phase 并纠正。

| # | 禁止 | 正确做法 | 后果 |
|---|------|---------|------|
| 1 | **在 `disclosure` 中撰写权利要求书** | 交底书由代理师后续撰写权利要求，发明人只需交底技术方案（`shared_workflow.md` § Phase 3D Actions） | 侵占代理师职责 → 文档作废 |
| 2 | **在等待用户确认的 🔴 CHECKPOINT 处继续执行** | 每个 CHECKPOINT 标记处**必须暂停**并等待用户明确"通过/修改/重写"，不自动继续（`SKILL.md` § Phase 3A/3D） | 未经确认的输出不可用 → 重做 |
| 3 | **在 Phase 0 未确认 doc-type 时默认走 `application`** | 若用户 prompt 经关键词过滤（排除发明内容描述中的词汇）后仍无法唯一确定 doc-type，必须 `vscode_askQuestions` 询问（`shared_workflow.md` § Phase 0 Actions 2-3）。**发明内容描述中的关键词（如"权利要求"在"一种专利权利要求自动撰写的方法"中）不作为 doc-type 信号** | 产出的文档类型错误 → 全部重做 |
| 4 | **跳过 Phase 2 现有技术检索** | 即使 API key 缺失也必须走 WebSearch 兜底，且必须输出「最接近现有技术 + 区别特征 + 技术效果」三步分析（`shared_workflow.md` § Step 2.4-2.6 + Checkpoint 2） | 权利要求失去新颖性支撑 → 驳回风险 |
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
| 18 | **在 `disclosure` 模式下，遇到未注册的代理机构时静默替换为 ACIP 通用模板并直接生成文档** | 当用户提及的代理机构（如"三环"/"中科"）在 `assets/templates/template_registry.md` 中无注册时，**必须先触发 Checkpoint** 向用户告知「[agency] 专属模板未注册，将使用 ACIP 通用交底书模板生成，输出文件名标注为 `Disclosure-[Agency]-generic-[ShortTitle]-[YYYYMMDD].md`」，等待用户选择 ① 继续用通用模板 / ② 暂停待用户放入专属 .docx 模板后重试（详见 [`docx_mode.md`](./docx_mode.md) § 1 + `template_registry.md` 决策树） | 静默替换模板 → 文档格式与目标代理机构不匹配 → 退回重做 |

> 此清单不是建议——是硬性红线。所有 Anti-Patterns 在 `quality_checklists.md` 的清单 A / 清单 D 中有对应的 checklist 项作为双重校验。每次 Checkpoint 4A / 4D 触发时，除加载 `quality_checklists.md` 外，还应快速回顾本表对应行。

---

## ⚠️ Error Handling Matrix（错误处理矩阵）

系统级故障处理规则——发生故障时按如下策略应对，不中断用户体验：

| 故障类型 | 行为 |
|----------|------|
| SerpAPI 返回 0 结果或 HTTP 429 | 等待 3s → 用同义词扩展关键词重试一次 → 仍失败则跳过 SerpAPI，交由 Exa.ai（若可用）+ WebSearch 兜底。审计日志中记录 API 状态 |
| Exa.ai 返回 0 结果 | 尝试 `type: "fast"` 重试（缩短 query 至前 5 词）→ 仍失败则交由 WebSearch 兜底 |
| SerpAPI + Exa.ai 均不可用 | 自动进入 Step 2.5 WebSearch 兜底，Checkpoint 2 中注明"新颖性分析仅基于网页搜索结果，建议委托专业检索机构" |
| 所有搜索方法均返回 0 结果 | 标记为"新颖性初步确认（无已知现有技术）"，**禁止断言"全球首创"**——网络搜索覆盖有限。建议用户委托专业机构做全面专利性检索 |
| 无法精确确定 IPC 分类号 | 列出 3-5 个候选分类号 + 候选理由 → Checkpoint 2 中请用户确认 → 若用户也无法确定，保留所有候选号，标注"建议代理师复核 IPC" |
| DOCX 生成失败（`fill_acip_template.py` 报错） | 根据错误类型处理（见 [`docx_mode.md`](./docx_mode.md) § 3），最终兜底方案为回退到 `--md` 模式 |
| 3 次连续工具调用失败（跨所有搜索源） | 停止检索，向用户说明已尝试的方法 + 缺失的信息，询问是否：① 补充 API key 后重试 ② 基于已有结果继续 ③ 跳过检索直接撰写（用户承担新颖性风险） |
| 用户拒绝回答 Phase 1 已知现有技术访谈 | 不强求，标注"用户未提供已知现有技术"，以"冷启动"模式进入 Phase 2 |
| 检索命中数 < 3 条 | 在 Checkpoint 2 中明确告知用户"可能为小众领域或检索策略需调整"，**禁止编造对比文件** |

---

## 高频违规 Top 5（SKILL.md 内嵌的快速警示）

以下 5 条是实测中 LLM 最易违反的，已内嵌在 SKILL.md 主体作为快速警示；完整 18 条见上表。

| # | 一句话摘要 | 触发场景 |
|---|---|---|
| 1 | disclosure 不写权利要求书 | 交底书场景 |
| 2 | CHECKPOINT 必须暂停 | 每个 🔴 标记处 |
| 3 | doc-type 不默认 application | Phase 0 关键词过滤后仍歧义 |
| 17 | 信息不足禁止编造 | Phase 1 访谈不足 |
| 18 | 非 ACIP 代理必须 Checkpoint | 未注册代理机构 |

---

## 交叉引用

- 清单 A / 清单 D（双重校验）→ `quality_checklists.md`
- `--docx` 错误处理 → `docx_mode.md` § 3
- 领域相关禁令（#16）→ `domain_matrix.md` § 2
- Phase 流程相关禁令（#3/#4/#11/#13/#14）→ `shared_workflow.md`
