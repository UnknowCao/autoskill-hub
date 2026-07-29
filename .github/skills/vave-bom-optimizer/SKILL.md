---
name: vave-bom-optimizer
version: 2.0.0
updated: 2026-07-29
description: "对汽车电子 BOM（ECU/BMS/域控制器/PCBA/连接器/线束）执行 VAVE 优化，输出 ABC 高杠杆清单、FAST 功能-成本矩阵、Should-Cost 差距报告、VAVE 提案与新 BOM Cost Rollup。也提供 VAVE 方法论原理（6 心智模型 + 8 决策启发式）、降本决策判断、失败反例知识库。当用户说「优化 BOM 成本」「BOM 降本」「做 VAVE 分析」「should-cost 分析」「二供评估/P2P」「FAST 功能分析」「ABC 筛选/帕累托」「降本」「cost down」「VA/VE」「价值工程」「国产化替代」「VAVE 该不该做」「降本有什么坑」「被动件能降级吗」「teardown 竞品拆解」「DFMA 零件合并」「平台化降本」时使用。"
---

# VAVE BOM Optimizer

基于 `Value = Function / Cost` 第一性原理，把汽车电子 BOM 重构为「功能-成本映射」，经 5 阶段流程落地为可批准的 VAVE 提案。

**核心杠杆定理**：BOM 占 PCBA 成本 50-70%，BOM 降本 10% -> 总成本降 5-7%，杠杆是装配优化的 7-10 倍。

---

## 🚀 快速启动（5 分钟上手）

> 第一次用？按这 4 步走，细节遇到问题时再查对应阶段。

| 步骤 | 做什么 | 工具/文件 | 预计时间 |
|---|---|---|---|
| **① 跑基线** | 把 BOM (Excel/CSV) 跑 Cost Rollup → 看 BOM 占比 ≥40%？ | `python scripts/cost_rollup.py bom.csv --annual-volume 100000` | 5 min |
| **② 锁定 A 类** | ABC 帕累托筛选 Top 20（10-20% 物料占 70-80% 成本） | `assets/abc_screening_template.csv` | 10 min |
| **③ 做 FAST** | 对 Top 20 写「动词+可测量名词」→ 标记非必要功能 | `assets/fast_worksheet_template.md` | 30-60 min |
| **④ 建 Should-Cost** | 对高杠杆物料按七要素估算「应当成本」→ 算 Gap | `assets/should_cost_template.csv` | 30 min/物料 |

> ⚠️ **进门先看门**：BOM 占总成本 < 40%（线束/结构件/包装典型场景）→ 跳过本 skill，优先做 DFMA 装配工艺优化。详见下方「适用域」节。

### 5 阶段总览

| 阶段 | 目标 | 核心动作 | STOP 条件 |
|---|---|---|---|
| **1. 基线建立** | 锁定 Top 20 高杠杆物料 | Cost Rollup + ABC + BOM≥40% 门控 | 80/20 占比核对不通过 → 重查数据 |
| **2. 功能重构** | 识别非必要/过度设计 | FAST + 功能-成本矩阵 | FAST 未完成 → 🚫 禁止进阶段 3 |
| **3. 成本还原** | 量化谈判空间 | Should-Cost 七要素 + Gap 分析 | 利润 < 行业基准 → 需用户签字 |
| **4. 替代执行** | 匹配降本杠杆 | 二供/平台化/DFMA/Teardown 四选一 | 二供 Qual 周期不可低估（≥16 周） |
| **5. 验证固化** | 守住质量底线 | PPAP + EMC 重测 + 季度评审 | 无 PPAP → 🚫 禁止上线 |

> 各阶段详细规则见 `references/stage1-baseline.md` ~ `references/stage5-validation.md`。如果你已熟悉 VAVE 方法论，下方理论框架可跳过，直接进 Workflow 阶段 1。

---

## 问题路由（先读这里）

根据用户意图跳到对应 section，避免「执行问题 dump 理论」或「理论问题误入流程」。

| 用户意图 | 跳转到 | 示例问法 |
|---|---|---|
| **执行 VAVE 流程** | → Workflow 5 阶段 | 「帮我做 ABC 筛选」「跑 should-cost」「出 VAVE 提案」「二供评估」 |
| **判断该不该做** | → 理论框架（心智模型 + 启发式） | 「这项目适合 VAVE 吗？」「二供值不值得？」「BOM 占比 35% 怎么切入？」 |
| **学习方法论 / 避坑** | → 理论框架 + 反模式 + 诚实边界 | 「VAVE 原理是什么？」「降本有什么坑？」「被动件能降级吗？」 |
| ⚠️ **被动件合并/降级** | → 🚫 先查反模式 #1 — 阻容通常是 B/C 类，ROI 极低 | 「电阻电容合并降本」「被动件降级」「换个便宜电容/电阻」 |

> ⚠️ **频率约束**：仅在用户问「为什么」「该不该」「原理」「风险」「方法」时才展开理论层（心智模型 / 启发式 / 张力 / 智识谱系）。执行类问题（「帮我做 X」「跑 X 分析」）直接走 Workflow 5 阶段，**不主动 dump 理论层**。反模式在阶段红灯 STOP 触发时才引用，不预加载。

> 🚀 如果你已有 BOM 数据（Excel/CSV，含 Qty + Unit Cost），直接跳到 Workflow 阶段 1。

---

## 理论框架（为什么这样做）

> 本节是 Skill 的「思维层」，与下方 5 阶段「执行层」配套。理论层回答「为什么」与「该不该做」，执行层回答「怎么做」。理论提炼自 6 维度调研（Miles/SAVE/FAST 起源 + 流派分歧 + 行业实战 + 工具边界 + 失败反例 + SDV/AI 趋势），详见 `references/07-vave-synthesis.md`。

### 6 个心智模型（Value=Function/Cost 的工程化展开）

每个模型都经过三重验证（跨域复现 / 生成力 / 排他性）。理解这些模型，才能判断「这个 VAVE 动作该不该做」。

| # | 心智模型 | 一句话 | 失效条件 |
|---|---|---|---|
| 1 | **BOM 是第一杠杆** | BOM 占 50-70%，是降本 ROI 最高的点；但「最高」≠「唯一」，装配/工艺是次级 | 纯结构件/线束 BOM 占比 < 40% 时失效；SDV 「软件替代硬件」可能重写占比 |
| 2 | **Function = 动词+可测量名词** | FAST 的精髓不是画图，是质疑「这颗料真的在做必要功能吗？」 | 软件/算法功能无法用「可测量名词」描述 |
| 3 | **Should-Cost 是相对基准** | SC 是谈判依据不是定价判决；当压价武器会摧毁供应商关系 → 偷工减料/断供 | 垄断/单源供应商失效（没谈判筹码） |
| 4 | **二供 = 成本 × 韧性** | 2024 缺芯后二供升级为韧性资产；单源现在 = 系统性风险 | 小批量物料不值得做二供（Qual 成本 > 节省） |
| 5 | **PPAP 是硬约束** | 任何 BOM 变更（含 drop-in）都必须走 PPAP 重测；跳过验证 = 召回 root cause | 非安全件（标签/包装）可降级，但需明示理由 |
| 6 | **SDV+AI 重写执行层** | ECU 数量 -50%+、生成式 AI 让 SC 工程师产能 10×；但 V=F/C 不变 | AI 数据新鲜度/可追溯性仍是短板 |

### 决策启发式（8 条「如果X则Y」）

| # | 场景 | 启发式 | 案例支撑 |
|---|---|---|---|
| 1 | 拿到降本任务 | **先算 BOM 占比再动手**；BOM < 40% 优先做装配/工艺 | 電路計画：杠杆是装配 7-10× |
| 2 | 想砍某颗料 | **先写 FAST 再砍**；「这料在做什么功能？必要吗？客户感知吗？」 | 反模式 #2；BAIC 6 件→1 件 |
| 3 | SC 算出 Gap | **Gap 是谈判起点不是压价目标**，标注 ±15-20% 不确定性 | Rossi 2024 实证；McKinsey 派被证伪 |
| 4 | 关键 IC 单源 | **交期 > 26 周 = 系统性风险**，强制启动二供评估 | Renesas 火灾；Hyundai×Mobis |
| 5 | 选二供 | **先查 Convergence**——Tier-1 名字不同但向上两层汇合 = 假二供 | TRW/KEMET 共性 root cause |
| 6 | 选降本杠杆 | **按场景匹配**：单源→二供 / 跨项目→平台化 / 零件多→DFMA / 报价高→teardown | 阶段 4 决策矩阵 |
| 7 | 被动件降级 | **省 $0.05 可能召回 $50M+**——AEC-Q200 是底线不是优化项 | GM Cobalt / Takata / Taycan 反例 |
| 8 | 提案批准后 | **必须走 PPAP**——drop-in 也要 EMC 重测，14-18 月是汽车级硬约束 | TRW/KEMET/Takata 召回 root cause |

### 4 对内在张力（VAVE 的深度来源）

这些张力无法消解，只能在不同场景下权衡。遇到判断困难时，识别属于哪对张力有助于思考。

| 张力 | 说明 | 权衡指南 |
|---|---|---|
| 降本 vs 安全 | VAVE 使命是降本，但过度降本导致召回 | PPAP/APQP 是硬边界 |
| 速度 vs 验证 | 市场要快，PPAP 要 14-18 月 | drop-in 二供是折中 |
| 谈判 vs 关系 | SC 是谈判武器还是关系毒药？ | 相对基准而非绝对真理 |
| 标准化 vs 差异化 | 平台化降本牺牲差异化；SDV 让软件差异化但硬件标准化 | 按总成（assembly）切分 |

### 智识谱系（这个方法论从哪里来）

```
Lawrence Miles (1947 GE, 二战物资短缺)
   ↓ SAVE International (1959) + Value Methodology Standard
Charles Bytheway - FAST (1964/1971)
   ↓
Boothroyd-Dewhurst DFMA (1980s)  ←→  日本 VA/VE (丰田/本田 1970s)
   ↓                                    ↓
SAE 技术论文 (1990s)                  lean VE / TDS
   ↓                                    ↓
should-cost 工具 (aPriori 2000s)      中国 OEM VAVE (2020s, 数据稀缺)
   ↓
生成式 AI should-cost (Nyotta/PartSpace/Autobom, 2024+)
   ↓
SDV zonal 架构 (2025+)
```

**关键澄清**：调研中发现网络流传的「SAE J1900 汽车行业 VE 标准」**不存在**——实际 SAE J1900 是《密封件粘合测试》（1990/2000/2002 三版，2002 已取消），与 VE 无关。真实的汽车 VE 标准载体是 SAE 技术论文（如 SAE 970767）。

### 诚实边界（这个 Skill 做不到什么）

1. **不能预测 OEM 内部 VAVE 流程的具体细节**（大众 Formel Q、丰田 VA、比亚迪内部流程都是黑箱）
2. **不能替代真实 PPAP/EMC 测试**——Qual 周期是经验估算，以 IATF 16949 + 客户 CSR 为准
3. **不能保证 should-cost 数字的精确性**——本质 ±15-20% 不确定性（Rossi 2024 实证）
4. **不能覆盖中国 OEM 的最新实践**（比亚迪/蔚来/小鹏/理想公开案例极稀缺）
5. **不能预测 SDV/AI 对 VAVE 的长期影响**（趋势快速演化，调研截止 2026-07-29）

> 调研时间：2026-07-29 | 建议更新频率：每 6 个月（SDV/AI 变化快）

---

## 术语表

> 以下术语在正文中高频出现。非汽车行业背景读者建议先通读。

| 术语 | 全称 | 一句话 | 为什么重要 |
|---|---|---|---|
| **VAVE** | Value Analysis / Value Engineering | 基于 V=F/C 的系统性降本方法；VA 用于现有产品，VE 用于新产品 | 本 skill 的核心方法论 |
| **FAST** | Function Analysis System Technique | 用「动词+可测量名词」拆解产品为功能树（How-Why 逻辑链） | VAVE 起点；跳过 FAST = 砍错功能 |
| **Should-Cost** | — | 基于物料/人工/设备/利润独立估算的「应当成本」 | 与供应商报价对比，量化谈判空间 |
| **DFMA** | Design for Manufacturing and Assembly | 面向制造与装配的设计；核心是零件最少化三问 | BOM<40% 时的替代降本路径 |
| **P2P** | Pin-to-Pin | 二供替代的兼容性分级（Tier 1 drop-in → Tier 4 架构重设） | 决定二供 Qual 周期（16 周 ~ 52 周+） |
| **PPAP** | Production Part Approval Process | 生产件批准程序；Level 3 = 完整提交（尺寸/材料/性能报告） | 任何 BOM 变更上线的硬约束 |
| **APQP** | Advanced Product Quality Planning | 先期产品质量策划；PPAP 的前置流程 | 与 PPAP 组成汽车级质量门 |
| **AEC-Q100** | Automotive Electronics Council Q100 | 汽车级 IC 可靠性认证（温度/寿命/ESD 等） | 非 AEC-Q 的 IC 不能上车 |
| **AEC-Q200** | Automotive Electronics Council Q200 | 汽车级被动元件认证 | 被动件降级的底线——省 $0.05 可能召回 $50M+ |
| **HARA** | Hazard Analysis and Risk Assessment | ISO 26262 危害分析与风险评估，确定 ASIL 等级 | 涉及功能安全件的变更必须做 HARA |
| **ASIL** | Automotive Safety Integrity Level | ISO 26262 安全完整性等级（A/B/C/D，D 最严） | 决定安全件验证强度 |
| **IATF 16949** | International Automotive Task Force 16949 | 汽车行业质量管理体系标准 | 汽车供应商必须通过 |
| **AVL** | Approved Vendor List | 批准供应商清单 | 二供替代的终点：新供应商进入 AVL |
| **Convergence 陷阱** | — | 两个 Tier-1 名字不同但向上追溯到同源 → 假二供 | 选二供时必须查供应链深度 |
| **NRE** | Non-Recurring Engineering | 一次性工程费（工装/模具/首件），按产量摊销 | Should-Cost 七要素之一，高产量趋近 0 |
| **TCO** | Total Cost of Ownership | 总拥有成本 = 单价 + Qual + 库存 + 保修 + 断供风险 | 反模式 #10：只比单价漏掉 TCO |

---

## 适用域

汽车电子（ECU、BMS、域控制器、PCBA、连接器）。**线束/结构件/包装类** BOM 占比常 < 40%，不属于 BOM 优先路径的标准适用对象——此时应优先做装配工艺/DFMA，仅在 BOM 占比 ≥ 40% 的子总成（如连接器组件）上降级使用本 Skill 的 5 阶段。

> ⚠️ **适用域约束（对应心智模型 1 的失效边界）**：本 Skill 的 5 阶段流程以「BOM 优先」为默认路径，仅适用于 BOM 占总成本 ≥ 40% 的对象（ECU/BMS/域控/PCBA 典型 50-70%）。若 BOM < 40%，阶段 1 的前置判断会拦截并引导转 DFMA/工艺路径，不走 ABC 筛选主流程。其他电子制造（消费电子/工业控制）可降级使用执行层，但汽车级 Qual 周期、AEC-Q、PPAP 等约束不适用。

## 输入 / 输出契约

| 项 | 说明 |
|---|---|
| **必选输入** | 现有 BOM（Excel/CSV/ERP 导出，含 Qty + Unit Cost）、供应商报价、年采购量 |
| **可选输入** | 竞品 BOM、scrap rate、loaded labor rate、目标降本率 |
| **输出** | (1) ABC 高杠杆清单 (2) FAST 功能-成本矩阵 (3) Should-Cost 差距报告 (4) VAVE 提案清单（年节省/采纳率/Qual 周期/风险）(5) 新 BOM Cost Rollup |

## Workflow（5 阶段，严格顺序，不可跳步）

每阶段详细规则见 `references/`；本 body 只给执行骨架。

### 阶段 1：基线建立 -> `references/stage1-baseline.md`
> 🔴 **先建基线再砍**：在给出任何降本建议前，必须先完成 Cost Rollup + ABC 筛选。用户催降本方案时回应：「我先建立成本基线，锁定 Top 20 高杠杆物料——确保砍的是 MCU/PMIC，而不是螺丝标签。」
1. 跑 Cost Rollup（用 `scripts/cost_rollup.py`）：`Sigma(Qty x Unit x Scrap) + Labor + Overhead + Logistics + Indirect`
2. **前置判断（强制，不通过则转路径）**：算完 Rollup 后先看 BOM 占总成本比例。
   - **BOM ≥ 40%** → 继续 ABC 筛选走 BOM VAVE 主路径
   - **BOM < 40%**（线束/结构件/包装典型场景）→ 🔴 **STOP：不适用 BOM 优先路径**。告知用户原因，转阶段 4 DFMA 路径（零件合并/装配优化为主），不走 ABC 筛选。DFMA 入口：对 Top 10 零件数最多的总成跑三问（运动？不同材料？必须分离？），零件数每减 1 个 ≈ 降本 $0.5-2。可在 BOM ≥ 40% 的子总成（如连接器组件）降级使用本 Skill。**此为非可选分支，禁止跳过。**
3. ABC/Pareto 筛选 -> 锁定 Top 20 物料（A 类 10-20% 物料 / 70-80% 成本）
4. **铁律**：从 A 类（IC/连接器）开始，C 类（螺丝/标签）缓做
5. 红灯 STOP：输出 ABC 清单前确认物料数占比 vs 成本占比是否对得上 80/20

> 🔴 **CHECKPOINT · 🛑 STOP**：ABC 清单展示后暂停，等用户确认 Top 20 优先级排序合理（A 类是否真的是高杠杆 IC/连接器），再进入阶段 2 FAST。跳过此确认 = 可能对着 C 类螺丝做功能分析，浪费 30-60 分钟。

### 阶段 2：功能重构 -> `references/stage2-function.md`
1. 对 Top 20 物料做 FAST（两词规则：动词 + 可测量名词，如「Regulate 5V」）
2. 建功能-成本矩阵：每个功能节点 -> 承载物料 + 成本 + 必要性（必要/客户不感知/过度设计）
3. 标记高成本 + 低必要度 = 首要 VAVE 目标
4. 红灯 STOP：跳过 FAST 直接砍 BOM 会砍掉必要功能 -> 质量事故

### 阶段 3：成本还原 -> `references/stage3-should-cost.md`
1. 对高杠杆 BOM 建 Should-Cost 七要素模型（直接物料 50-70% / 人工 / Overhead 2-4x / 设备 / NRE / 利润 5-15% / 其他）
2. 物料询价走授权分销商（Digi-Key/Mouser/Arrow），按实际采购量
3. 算 Gap = Will - Should
4. **铁律**：Should-Cost 是相对基准不是绝对真理，作为谈判依据而非压价武器
5. 红灯 STOP：把供应商压到利润不可持续 = 偷工减料 + 断供风险

### 阶段 4：替代执行 -> `references/stage4-levers.md`
四大降本杠杆，**按场景匹配决策矩阵**（与 `references/stage4-levers.md` 同步）：

| 场景 | 选定杠杆 |
|---|---|
| 关键 IC 单源 / 交期长 | 二供替代（P2P 四级） |
| 同类零件跨项目重复 | 平台化合并 |
| 零件数多 / 装配复杂 | DFMA 零件合并 |
| 报价高于行业基准 | Should-Cost + Teardown |
| 供应商不愿让价 | Should-Cost 谈判 + 二供威胁 |
| 国产化窗口打开 | 国产 P2P + Qual 加速 |

各杠杆细则：
- **二供替代**：P2P 四级（Tier 1 drop-in 16-26 周 / Tier 2 footprint 兼容 26-52 周 / Tier 3 需 PCB 改版 / Tier 4 架构重设）
- **平台化合并**：跨车型共用物料，集中需求量议价
- **DFMA 零件合并**：三问全「否」则合并（运动？不同材料？必须分离？）
- **Teardown 对标**：竞品拆解 + BOM 还原 -> 识别优势 -> VAVE 提案

> 🔴 **CHECKPOINT · 🛑 STOP**：选定降本杠杆后暂停，展示 Qual 周期 + 风险等级 + 预期年节省，等用户签字确认再启动阶段 5 验证。二供 Qual 不可逆（16-52 周），确认后再改方向代价极高。

### 阶段 5：验证固化 -> `references/stage5-validation.md`
1. VAVE 提案量化：年节省 / 采纳率 / Qual 周期 / 风险等级（用 `assets/vave_proposal_scorecard.md`）
2. 跨职能评审 + Steering Committee 批准
3. 启动 APQP/PPAP + 二供 Qual（汽车级关键路径 **14-18 个月**）
4. 新 BOM Cost Rollup 复算收益
5. 归档 + 转入下一轮 VAVE（按季度节奏：Q1 基线/Q2 分析/Q3 提案/Q4 上线复算）
6. 红灯 STOP：无 PPAP/EMC 重测就上线 -> 田间失效 / 召回

## 资源索引

| 类型 | 文件 | 用途 |
|---|---|---|
| **theory** | **`references/07-vave-synthesis.md`** | **理论框架提炼（6心智模型+8启发式+4张力+诚实边界）** |
| **theory** | **`references/01-vave-origin.md`** | **VAVE 方法论起源（Miles/SAVE/FAST 考据）** |
| reference | `references/stage1-baseline.md` | 阶段 1：Cost Rollup 公式 + ABC 矩阵 |
| reference | `references/stage2-function.md` | 阶段 2：FAST 规则 + 功能-成本矩阵 |
| reference | `references/stage3-should-cost.md` | 阶段 3：Should-Cost 七要素建模 |
| reference | `references/stage4-levers.md` | 阶段 4：四大降本杠杆 + 决策矩阵 |
| reference | `references/stage5-validation.md` | 阶段 5：Qual 时间表 + PPAP 清单 |
| reference | `references/anti-patterns.md` | 8 大反模式 + 90 天启动 checklist |
| asset | `assets/should_cost_template.csv` | Should-Cost 七要素建模模板 |
| asset | `assets/abc_screening_template.csv` | ABC 筛选 + 战略重要度矩阵 |
| asset | `assets/fast_worksheet_template.md` | FAST 功能-成本工作表 |
| asset | `assets/vave_proposal_scorecard.md` | VAVE 提案评分卡 |
| script | `scripts/cost_rollup.py` | 多层 BOM Cost Rollup 计算器 |

## Anti-patterns（不要做什么 — 详细见 `references/anti-patterns.md`）

> SkillLens risk-action blacklist 维度要求：反模式必须显式列出，不能只写「应该做 X」。

| # | 症状（用户会这样说） | 后果 | 拦截点（强制 STOP / 引导） |
|---|---|---|---|
| 1 | 「帮我把电阻电容合并降本」 | C 类优先，投入产出比差 | 反问 ABC 类别；阻容通常 B/C 类，引导先做 A 类 IC/连接器 |
| 2 | 「跳过功能分析直接砍 BOM」 | 砍掉必要功能，质量事故 | 🔴 STOP 阶段 2：FAST 完成前禁止砍 BOM |
| 3 | 「等缺料了再找二供」 | 14-18 个月后才能用，已停产 | 提前批量启动；交期 >26 周即视为单源风险 |
| 4 | 「should-cost 算出来直接压价」 | 供应商关系紧张 + 偷工减料 | SC 是相对基准不是绝对真理，作谈判依据 |
| 5 | 「把供应商利润压到最低」 | 偷工减料 / 断供 | 🔴 STOP 阶段 3：利润 < 行业基准需用户签字 |
| 6 | 「VAVE 做完了直接换料上线」 | 田间失效 / 召回 | 🔴 STOP 阶段 5：无 PPAP/EMC 重测禁止上线 |
| 7 | 「采购自己搞 VAVE 就行」 | 提案被否 / 落地难 | 🔴 STOP 全局：跨职能评审缺失禁提交 Steering |
| 8 | 「做完一轮就收工」 | 降本不可持续 | 强制季度节奏 Q1/Q2/Q3/Q4 循环 |
| 9 | 「被动件换个便宜的吧，省 $0.05 也是肉」 | 省 $0.05/件 → 召回 $50M+（放大 1000-10000×）；AEC-Q200 是底线不是优化项 | 🔴 STOP：被动件（MLCC/电解/钽电容/薄膜电阻）降级需独立安全评审 + 调用反例（GM Cobalt/Takata/Taycan）提醒风险 |
| 10 | 「只比 BOM 单价选供应商」 | TCO 截断误算，漏掉 PPAP/模具/库存/保修，隐藏成本 3-5× | 强制 TCO 表格（单价 + Qual 摊销 + 库存持有 + 保修预留 + 断供概率×召回期望损失） |

## Checkpoints

> 各阶段 STOP 条件详见上方「5 阶段总览」表和阶段内 `红灯 STOP` 标记。此处仅汇总全局约束。

- 🔴 **全局**：跨职能评审缺失禁止提交 Steering Committee
- 🔴 **全局**：任何 BOM 变更无 PPAP/EMC 重测禁止上线

---

## Changelog

| 版本 | 日期 | 变更 |
|---|---|---|
| **2.0.0** | 2026-07-29 | 新增理论框架层（6 心智模型 + 8 决策启发式 + 4 内在张力 + 智识谱系 + 诚实边界），基于 6 维度调研（30 条 anysearch 查询，~180 URL 来源）；新增反模式 #9（被动件降级）和 #10（TCO 截断误算）；新增术语表 + 问题路由 + 快速启动 + 5 阶段总览；修正 openBOM 公式措辞（教学 vs 产品公式区分）；修正适用域线束为非标准对象。 |
| **1.x** | 2026-07 前 | 初始版本：5 阶段执行器 + 8 反模式 + checkpoints。 |
