# 子Agent Prompt 模板（Parallel Dispatch 用）

> 主Agent在调用 `runSubagent` 时，使用此模板。`{变量}` 由主Agent在运行时替换。
> 文件位置：`references/vc-subagent-prompt.md`

---

## 完整 Prompt 模板

复制以下内容作为 `runSubagent` 的 `prompt` 参数值，替换 `{变量}` 后发送：

```
You are generating Verification Criteria (VC) for a subset of system requirements.

## 你的任务

为主Agent分派给你的那批需求逐条生成 Verification Criteria (VC)。这批需求
存放在一个独立文件中（由主Agent预先用 `scripts/split_req.py` 拆分得到），
**你需要先 `read_file` 把它读进来**，再执行 VC-First 循环。**不要等待主Agent在
prompt 里内联需求全文**——prompt 只携带文件路径。

你需要：
1. **第一步（MANDATORY）**：`read_file {requirements_file_path}` 加载本批次需求
   - 该文件顶部有自动生成的元信息行（`> Source:` / `> Domain:` / `> IDs:` / `> ID range:`），
     据此核对本批次覆盖的 ID 范围是否与下方 "本批次概览" 一致；不一致立即标注
     `⚠️ degraded: 拆分文件 ID 范围与 prompt 不符` 并以**文件内容**为准继续工作。
2. 用 `read_file` 加载下方 📁 参考文件（方法论与模板）
3. 对每条需求执行 VC-First 循环（选择模板 → 填写5元素 → Source Depth标注 → SMARTR-OC自检）
4. 将所有结果写入文件 `{output_file_path}`

## 本批次概览（主Agent预填，详细内容在文件中）

- **需求文件路径**: `{requirements_file_path}` ← **必须 read_file 此路径**
- 功能域: {functional_domain_name}
- 需求数量: {N} 条  |  ID 范围: {id_range}（如 `BMS-016..BMS-030`）

> ⚠️ 跨需求引用：若某条需求引用了**本批次之外**的 ID（如 `参见 BMS-050`），
> 不要去读原需求全文，按字面信息处理并在该 VC 的 Source Depth 标 `[A]` +
> 注明 `cross-ref to {ID} outside batch`。

## 领域上下文

- 功能域: {functional_domain_name}
- 行业: {industry_context}
- 惯例: {conventions}

## � 必须加载的参考文件（用 read_file）

按以下顺序加载，加载失败则标注 `⚠️ degraded: 缺少 {filename}` 继续工作。
其中前 4 个为**强制加载**，其余按主Agent标注选择性加载：

1. `{skill_base_path}/references/vc-smartr-oc.md` — SMARTR-OC 8维评分标准（强制）
2. `{skill_base_path}/references/vc-source-depth.md` — Source Depth 标注规则（强制）
3. `{skill_base_path}/assets/vc-template.md` — VC 表格模板 + 4种类型模板（强制）
4. `{skill_base_path}/references/vc-hard-gates.md` — 11条硬门控 + 全部规则（强制，**Gates 不在此 prompt 中内联，需从文件完整加载**）
5. `{skill_base_path}/references/vc-safety-patterns.md` — **仅当本批次含 ASIL/安全需求时加载**（主Agent会在下方标注 `📌 REQUIRED: vc-safety-patterns.md` 或 `⏭️ SKIP: vc-safety-patterns.md — 本批次无ASIL需求`）
6. `{skill_base_path}/references/vc-sequence-guide.md` — **仅当本批次含多场景/因果链需求时加载**（主Agent标注）
7. `{skill_base_path}/references/vc-exceptions.md` — 遇异常时加载

{reference_file_hints}

## Hard Gates & 质量标准

所有 Gates 和评分规则从 `vc-hard-gates.md` 和 `vc-smartr-oc.md` 完整加载，不在此内联。必须逐条对照执行。

## 输出格式

写入文件 `{output_file_path}`，对每条 VC 使用以下格式。

**关键规则**：
- 表格内 Test Conditions / Pass/Fail Criterion 用 `<br>` 换行，每行一个独立条件项
- ⛔ **SMARTR-OC 只输出总分**；禁止输出完整的 8 维表格。仅当 <8/8 时追加 `> ✗ {dim}: {reason}` 行（每行 ≤80 chars）。8/8 时只写 `**SMARTR-OC**: **8/8** ✅`，不列维度
- ⛔ **Gate Compliance Checklist 只列出未通过的 Gate**（⚠️ 或 ✗），通过的 Gate 不输出。若全部通过则写 `All 11 Gates: ✅ PASS` 一行即可
- **Source Depth 列出所有带标签的数值**（含 `[R]`/`[D]`/`[S]`/`[E]`/`[A]`），每值一行 bullet。
  标签格式**必须**符合 `vc-source-depth.md` §The Five Source Depth Levels：
  | 标签 | 格式要求 | ✅ 正确示例 | ❌ 错误示例 |
  |------|---------|------------|-----------|
  | `[R]` | `[R: BMS-XXXX]` 含具体需求 ID | `4.10V [R: BMS-0126]` | `4.10V [R]` |
  | `[D]` | `[D: derivation logic]` 含推导逻辑 | `BOL/MOL/EOL [D: BMS-039 "全生命周期"]` | `[D]`（空） |
  | `[S]` | `[S: standard name, §clause]` 含标准名称+条款 | `FTTI [S: ISO 26262-4 §6.4.2.3]` | `[S: ISO 26262]` |
  | `[E]` | `[E: full derivation chain]` 完整推导链，**禁止缩写** | `N=100 [E: binomial 95% conf → <3% failure → N=100]` | `N=100 [E: 行业惯例]` |
  | `[A]` | `[A: assumption, resolution plan]` 含假设描述+解决方案 | `100ms [A: 待整车FTTI分配确认, 暂取典型安全断开时间]` | `100ms [A: 待确认]` |
  - ⚠️ **`[E]` 无完整推导链 → 自动降级为 `[A]`**（vc-source-depth.md Quick Decision Flow）
  - ⚠️ **`[R]` 不带 REQ-ID → M = ✗**（无法追溯，视为无源标注）
- 文件末尾输出 Assumption Log 表（如有任何 `[A]`）

```
# VC — {domain_name}

## VC-{REQ-ID} — {brief_title}

| VC ID | Linked Requirement | Verification Method | Test Conditions | Measurement Target | Pass/Fail Criterion |
|-------|-------------------|---------------------|-----------------|--------------------|---------------------|
| VC-{REQ-ID} | ... | ... | ...<br>...<br>... | ... | ...<br>...<br>... |

**SMARTR-OC**: **X/8**
> ✗ {dim}: {1-line reason}   ← 仅当 <8/8 时出现，每行 ≤80 chars；8/8 时不输出维度行

**Source Depth**:
- {value} [R: BMS-XXXX]
- {value} [D: derivation logic, 推导链]
- {value} [S: standard name §clause]
- {value} [E: full derivation chain — 禁止缩写]
- {value} [A: assumption, resolution plan]

> Assumption Log（如有 `[A]`）→ 见文件末尾

---

## 🔍 Gate Compliance Checklist（仅列出 ⚠️ / ✗）

| Gate | Status | Issue |
|------|--------|-------|
| Gate X | ⚠️ | {1-line reason} |

> 若全部通过：`All 11 Gates: ✅ PASS`

---

## Assumption Log

| VC ID | Field | Assumed Value | Rationale | Resolution | Owner | Due Date |
|-------|-------|---------------|-----------|------------|-------|----------|
| VC-BMS-XXXX | ... | ... | ... | ... | ... | ... |
```

## 行为约束

- ⛔ **禁止等待用户确认** — 一次性输出完整结果，不设 CHECKPOINT
- VC-BLOCKED → 标记 🔴 + 阻塞原因，继续下一条
- 异常 → 标注 `⚠️ degraded: {reason}`，继续
- 禁止编造数值；未知时标记 `[A]` 并记录假设
- SMARTR-OC < 6/8 修订3次仍不合格 → 标记 VC-BLOCKED，继续下一条

## 最终输出

完成后，将完整的 VC 文档写入 `{output_file_path}`，并在你的最终回复中返回：
1. 已处理的需求数量和 ID 范围
2. VC-BLOCKED 清单（如有）
3. 平均 SMARTR-OC 分数
4. `[S]`/`[E]`/`[A]` 来源值总数（对应 Source Depth 显示条目数）
```

---

## 变量清单

- `{N}` — 本批次需求数量，e.g. `15`
- `{output_file_path}` — 子Agent输出文件路径，e.g. `output/vc-batch-01.md`
- `{requirements_file_path}` — **本批次需求拆分文件的绝对路径**，e.g.
  `c:\AI\BMS_Requirements_5000\_vc_batches\req-split-02-电池保护功能-Battery-Protection.md`。
  由主Agent在 A.1a 步骤通过 `scripts/split_req.py` 生成（见 `vc-workflow-a.md` §A.1a）。
  子Agent**必须** `read_file` 此路径获取需求全文；**禁止**把全文复制进 prompt。
- `{id_range}` — 本批次需求 ID 范围，e.g. `BMS-016..BMS-030`（用于概览校验）
- `{functional_domain_name}` — 功能域名，e.g. `电池保护`
- `{industry_context}` — 行业背景，e.g. `汽车电子`
- `{conventions}` — 领域惯例，e.g. `ISO 26262, ASPICE`
- `{skill_base_path}` — skill 根目录绝对路径，e.g. `c:\AI\.github\skills\verification-criteria`

---

## 主Agent调度规则

> 以下规则原位于 `../SKILL.md §并行子Agent调度`，外置到此以精简主文件。主Agent在并行分派时必须遵循。

### 主Agent职责

- **拆分 (A.1a)**: 读取需求文档 → 运行 `scripts/split_req.py` 按功能域拆分为独立 `.md` 文件 → 核对 ID 完整性 → 构造分派映射（split_file → domain → ids → output_file）
- **分派**: 对分派映射中每条记录调用 `runSubagent`，prompt **只填 `{requirements_file_path}`**（拆分文件路径），需求全文不内联
- **合并**: 收集所有子Agent输出 → 拼接为完整 VC 文档
- **分层复核** (两阶段门控，由 `merge_vc.py` tiered_review 自动执行):
  - 阶段一 SMARTR-OC 抽样：8/8 → 进入阶段二 / 6-7/8 → 随机抽样 20%，1 条不一致则扩至全量 / <6/8 → 全量复核
  - 阶段二 Gate 11 格式抽查（仅 8/8 候选）：独立检测 Test Conditions/Pass-Fail 列是否误用 `; ` 而非 `<br>`，命中则降级到抽样桶（不依赖子Agent 自报告，弥补纵深防御缺口）
  - 异常检测: 任一子Agent均分偏离全局 >1.0 → 全量复核该Agent
- **覆盖率审计 (A.4)**: 主Agent独立执行
- **CHECKPOINT 展示**: 合并后一次性展示批量结果（不逐条打断）

### 主Agent合并流程

所有 `runSubagent` 返回后，主Agent执行：

1. **读取输出文件**：对每个子Agent的 `{output_file_path}` 执行 `read_file`
2. **合并**：将所有子文件内容拼接为主 VC 文档
3. **分层复核**（两阶段门控，由 `merge_vc.py` tiered_review 自动执行）：
   - 阶段一 SMARTR-OC 抽样：8/8 子Agent批次 → 进入阶段二 / 6-7/8 → 随机抽样 20%，1 条不一致 → 全量复核 / <6/8 → 全量复核
   - 阶段二 Gate 11 格式抽查（仅 8/8 候选）：独立检测表格 Test Conditions/Pass-Fail 列是否误用 `; ` 而非 `<br>`（违反 Gate 11），命中则降级到抽样桶。此检查不依赖子Agent 自报告，弥补“8/8 被信任跳过但格式违规漏过”的缺口
   - 异常检测: 任一子Agent均分偏离全局 >1.0 → 全量复核该批次
4. **A.4 覆盖率审计**：主Agent独立执行
5. **CHECKPOINT**：向用户展示合并结果 + 覆盖率报告
