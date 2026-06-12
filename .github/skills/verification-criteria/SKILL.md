---
name: verification-criteria
description: "Generate, audit, and trace verification criteria (VC) for functional system requirements. Three modes: (A) VC Generation — write VCs with 5-element structure, SMARTR-OC self-check, Source Depth annotation; (B) VC Quality Audit — score existing VCs against SMARTR-OC 8-point rubric + CK-01~CK-10 peer review checklist; (C) Coverage Audit — traceability matrix, orphan detection, 100% coverage verification. Follows ASPICE SYS.2 BP5, ISO/IEC 29148, VC-First methodology. Use when user mentions: '生成VC', '验证标准', '审核VC', 'SMARTR-OC', '覆盖率', 'traceability', 'verification criteria', 'VC质量', 'VC评分', 'verification audit', '需求验证', '测试标准'."
---

# Verification Criteria Generator & Auditor

Generate, review, and audit verification criteria (VC) for functional system requirements. Follows ASPICE SYS.2 BP5, ISO/IEC 29148, and VC-First methodology.

## Mode Selection

```mermaid
flowchart TD
    START["用户请求"] --> Q1{"意图？"}
    Q1 -->|"生成VC / 编写验证标准"| A["Workflow A: VC Generation"]
    Q1 -->|"审核VC质量 / SMARTR-OC"| B["Workflow B: VC Quality Audit"]
    Q1 -->|"覆盖率审计 / 追溯检查"| C["Workflow C: Coverage Audit"]
    Q1 -->|"不明确"| ASK["反问用户确认模式"]
```

Never assume the user's intent. "review my VCs" → Mode B, not A. If ambiguous, use `vscode_askQuestions` to confirm which mode: "Which would you like me to do — generate new VCs, audit existing VC quality, or audit VC coverage?"

🔴 **CHECKPOINT · 🛑 STOP** — 模式确认后，暂停向用户复述所选模式及下一步操作，等用户说"继续"/"OK"后再加载对应 workflow 文件。**绝不自行跳转模式。**

## VC-First Methodology

**Core Principle**: Write the VC simultaneously with every requirement, not after. VC is the requirement's "other half" — the requirement says "what"; the VC says "how we prove it."

> "Every requirement is a hypothesis awaiting verification. If you can't write a VC, the requirement isn't ready."

> See `references/vc-anti-patterns.md` for common VC-First mistakes and corrective examples.

### Requirement Maturity Gate

When a VC **cannot** be written for a requirement, the requirement is immature. Flag it:

- 🔴 **VC-BLOCKED**: No VC can be defined at all → **Rewrite the requirement**
- 🟡 **VC-PARTIAL**: VC exists but only covers normal conditions → Add boundary (-40°C/+85°C) and abnormal (fault, overvoltage) scenarios
- 🟠 **VC-ASSUMPTION**: VC depends on unconfirmed assumptions → Document the assumption explicitly, escalate; write provisional VC

**Escalation rule**: If ≥3 requirements in a review session are flagged VC-BLOCKED, stop and reassess the requirements baseline.

🔴 **CHECKPOINT · 🛑 STOP** — 若触发升级规则（≥3 VC-BLOCKED），暂停所有 VC 工作，向用户报告问题需求清单，等用户决定"修订需求后继续"或"终止本次会话"后再行动。

## Workflows

Determine mode from the flowchart above.

### ⚡ MANDATORY: Create Todo List Before Starting

**Before executing any workflow step**, you MUST call `manage_todo_list` to create a todo list. Each workflow file defines its own todo items — copy them from the workflow file's "## Todo List Template" section. Mark each item `in-progress` before starting it and `completed` immediately after.

> **Why**: The todo list gives the user real-time visibility into progress, ensures no steps are skipped, and makes the workflow resumable across long sessions. A workflow without a todo list is a protocol violation.

| Mode | Workflow | Load |
|------|----------|------|
| A — Generate VC | VC Generation (A.0~A.4) | `references/vc-workflow-a.md` |
| B — Audit VC Quality | SMARTR-OC + CK-01~CK-10 Audit (B.0~B.4) | `references/vc-workflow-b.md` |
| C — Audit Coverage | Coverage completeness & orphan detection (C.0~C.5) | `references/vc-workflow-c.md` |

🔴 **CHECKPOINT · 🛑 STOP** — 加载 workflow 文件后、执行第一步之前，向用户展示 todo list，确认后再开始执行。

## Key Principles

1. **VC-First**: VC is written simultaneously with requirements, not after
2. **VC is a design activity**, not a documentation task
3. **If you can't write a VC, the requirement isn't mature enough** — flag it
4. **VC ownership**: Requirements engineer writes VC; test engineer reviews for testability
5. **One VC verifies one independently verifiable aspect** — don't merge unrelated checks
6. **Source Depth — No Unsourced Content**: Every value in a VC (thresholds, sample sizes, environment ranges, fault types, equipment precision) must be traceable to one of five source depths. See `references/vc-source-depth.md` for the full annotation system.
   - `[R]` **Requirement-text**: value appears verbatim in the requirement
   - `[D]` **Derived**: logically derived from the requirement (e.g. "全生命周期" → BOL/MOL/EOL)
   - `[S]` **Standard**: cited from a named standard, regulation, or upstream specification
   - `[E]` **Engineering judgment**: domain convention (e.g. automotive three-temperature -40/+25/+85°C, N=20 for functional tests)
   - `[A]` **Assumption / unknown**: value is unconfirmed — **MUST** document the assumption; this flag triggers an automatic `A = ✗` in SMARTR-OC scoring
   - 🔴 **Hard Gate**: If ≥3 values in a single VC carry `[A]`, that VC is VC-BLOCKED and the requirement must be revised before the VC can proceed.

🔴 **CHECKPOINT** — 每条 VC 生成后、进入下一条之前：向用户展示该 VC 及其 SMARTR-OC 自检结果。若用户不满意，当场修订后再继续。

🔴 **CHECKPOINT** — Workflow 最终输出前：展示完整 VC 文档 + 覆盖率报告摘要，等用户确认后再输出最终文件。

## References

Load on demand — only when the corresponding workflow step is reached.

| File | When to Load |
|------|-------------|
| `references/vc-workflow-a.md` | Workflow A selected (mode confirmed) |
| `references/vc-workflow-b.md` | Workflow B selected (mode confirmed) |
| `references/vc-workflow-c.md` | Workflow C selected (mode confirmed) |
| `references/vc-smartr-oc.md` | **A.3 / B.2**: SMARTR-OC 8-point scoring rubric with operational checklist |
| `references/vc-source-depth.md` | **A.2a / B.2**: Source Depth 5-level annotation system + threshold provenance check |
| `assets/vc-template.md` | **A.2**: VC table template + 4 type-specific structured templates (functional, performance, safety, interface) |
| `references/vc-safety-patterns.md` | **A.2**: requirement has ASIL level — safety margin rules, double-100 verification, test coverage matrix |
| `assets/vc-checklist.md` | **B.2**: printable SMARTR-OC scoring form + peer review checklist (CK-01~CK-10) |
| `references/vc-report-templates.md` | **A.4 / B.4 / C.5**: quality audit or coverage audit report templates |
| `references/vc-handbook.md` | Deep-dive on 5-element structure, Top 10 pitfalls, or peer review checklist details |
| `references/vc-framework.md` | User asks about VC-First methodology theory, SMARTR-OC model rationale |
| `references/vc-anti-patterns.md` | User asks for VC examples, or a generated VC looks suspicious |
| `references/vc-sequence-guide.md` | **A.2**: VC involves multi-scenario / causal-chain / baseline recovery — 4-question decision framework for Sequence constraints |

## ⛔ Do Not — 反例黑名单

以下反模式在执行任何 workflow 时**一律禁止**。遇到即标记为错误，必须修正。

| # | 反模式 | 为什么禁止 | 替代做法 |
|---|--------|-----------|---------|
| 1 | **把需求原文复述为 VC** | 零信息增量，无法指导测试 | VC 必须比需求更具体：加上方法、条件、数值判据 |
| 2 | **VC 中引用 Test Case 编号**（"详见 TC-001"） | 循环引用——VC 是 TC 的上游输入 | 在 VC 中直接写明方法/条件/判据 |
| 3 | **使用主观形容词**（"良好"/"合理"/"足够"/"正常"/"快速"/"稳定"/robust/sufficient/adequate） | 无法客观判定 pass/fail | 必须用 `≤/≥/=` + 数值 + 单位 |
| 4 | **跳过覆盖率审计直接结束**（A.4 不执行） | 遗漏未覆盖需求，ASPICE 不合格 | 每次生成 VC 后必须跑 A.4，直到 100% 覆盖 |
| 5 | **所有 VC 统一用 "Test" 方法** | 不同需求类型需不同验证方法 | 用决策树选择：物理测量→Test；理论推导→Analysis；文档/布局→Inspection；操作演示→Demonstration |
| 6 | **编造无来源的数值**（凭感觉写阈值/样本量/温度） | 看似专业实则不可验证 | 每个数值标注 `[R]/[D]/[S]/[E]/[A]` 来源（见 `references/vc-source-depth.md`） |
| 7 | **只在常温(25°C)测试** | 边界和异常条件是失效高发区 | 至少覆盖：常温 + 需求工作域下限 + 上限（如 -40°C/+85°C） |
| 8 | **静默跳过异常或错误** | 破坏流程完整性，用户无法察觉 | 遇到异常必须向用户报告，按 fallback 规则处理 |
| 9 | **跳过 SMARTR-OC 自检直接输出** | 质量无保障，可能产出不可测试的 VC | 每条 VC 必须 SMARTR-OC ≥ 6/8 才能进入下一步 |

> 完整反例库见 `references/vc-anti-patterns.md`。本表为主文件必看的最小集。