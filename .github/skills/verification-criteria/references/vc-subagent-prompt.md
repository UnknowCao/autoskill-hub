# 子Agent Prompt 模板（Parallel Dispatch 用）

> 主Agent在调用 `runSubagent` 时，使用此模板。`{变量}` 由主Agent在运行时替换。
> 文件位置：`references/vc-subagent-prompt.md`

---

## 完整 Prompt 模板

复制以下内容作为 `runSubagent` 的 `prompt` 参数值，替换 `{变量}` 后发送：

```
You are generating Verification Criteria (VC) for a subset of system requirements.

## 你的任务

为以下 {N} 条需求逐条生成 Verification Criteria (VC)。你需要：
1. 先用 `read_file` 加载下方 📁 参考文件
2. 对每条需求执行 VC-First 循环（选择模板 → 填写5元素 → Source Depth标注 → SMARTR-OC自检）
3. 将所有结果写入文件 `{output_file_path}`

## 需求列表

{requirement_subset_with_full_text_and_cross_references}

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
4. `{skill_base_path}/references/vc-hard-gates.md` — 10条硬门控 + 全部规则（强制，**Gates 不在此 prompt 中内联，需从文件完整加载**）
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
- SMARTR-OC 只输出总分；仅当 <8/8 时追加 `> ✗ {dim}: {reason}` 行（每行 ≤80 chars）
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
> ✗ {dim}: {1-line reason}   ← 仅当 <8/8 时出现，每行 ≤80 chars

**Source Depth**:
- {value} [R: BMS-XXXX]
- {value} [D: derivation logic, 推导链]
- {value} [S: standard name §clause]
- {value} [E: full derivation chain — 禁止缩写]
- {value} [A: assumption, resolution plan]

> Assumption Log（如有 `[A]`）→ 见文件末尾

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

| 变量 | 说明 | 示例值 |
|------|------|--------|
| `{N}` | 本批次需求数量 | `15` |
| `{output_file_path}` | 子Agent输出文件路径 | `output/vc-batch-01.md` |
| `{requirement_subset_with_full_text_and_cross_references}` | 需求子集完整文本 | 逐条列出 |
| `{functional_domain_name}` | 功能域名 | `电池保护` |
| `{industry_context}` | 行业背景 | `汽车电子` |
| `{conventions}` | 领域惯例 | `ISO 26262, ASPICE` |
| `{skill_base_path}` | skill 根目录绝对路径 | `c:\AI\.github\skills\verification-criteria` |

---

## 主Agent调度规则

> 以下规则原位于 `../SKILL.md §并行子Agent调度`，外置到此以精简主文件。主Agent在并行分派时必须遵循。

### 主Agent职责

- **分派**: 读取需求文档 → 按功能域拆分 → 并行启动子Agent
- **合并**: 收集所有子Agent输出 → 拼接为完整 VC 文档
- **分层复核** (SMARTR-OC):
  - 8/8 → 信任（低风险，错判仍是 ≥6/8）
  - 6-7/8 → 随机抽样 20%，1 条不一致则扩至全量
  - <6/8 → 全量复核（高风险，决定需求是否重写）
  - 异常检测: 任一子Agent均分偏离全局 >1.0 → 全量复核该Agent
- **覆盖率审计 (A.4)**: 主Agent独立执行
- **CHECKPOINT 展示**: 合并后一次性展示批量结果（不逐条打断）

### 主Agent合并流程

所有 `runSubagent` 返回后，主Agent执行：

1. **读取输出文件**：对每个子Agent的 `{output_file_path}` 执行 `read_file`
2. **合并**：将所有子文件内容拼接为主 VC 文档
3. **分层复核**（SMARTR-OC 抽样审计）：
   - 8/8 子Agent批次 → 信任，跳过复核
   - 6-7/8 子Agent批次 → 随机抽样 20% VC，重新评分；1 条不一致 → 全量复核该批次
   - <6/8 子Agent批次 → 全量复核
   - 异常检测: 任一子Agent均分偏离全局 >1.0 → 全量复核该批次
4. **A.4 覆盖率审计**：主Agent独立执行
5. **CHECKPOINT**：向用户展示合并结果 + 覆盖率报告
