---
name: vave-bom-optimizer
description: "对汽车电子 BOM（ECU/BMS/域控制器/PCBA/连接器/线束）执行 VAVE 优化，输出 ABC 高杠杆清单、FAST 功能-成本矩阵、Should-Cost 差距报告、VAVE 提案与新 BOM Cost Rollup。当用户说「优化 BOM 成本」「BOM 降本」「做 BOM VAVE 分析」「should-cost 分析」「二供评估/P2P 分析」「FAST 功能分析」「ABC 筛选/帕累托分析」时使用。"
---

# VAVE BOM Optimizer

基于 `Value = Function / Cost` 第一性原理，把汽车电子 BOM 重构为「功能-成本映射」，经 5 阶段流程落地为可批准的 VAVE 提案。

**核心杠杆定理**：BOM 占 PCBA 成本 50-70%，BOM 降本 10% -> 总成本降 5-7%，杠杆是装配优化的 7-10 倍。

## 适用域

汽车电子（ECU、BMS、域控制器、PCBA、连接器、线束）。其他电子制造可降级使用，但汽车级 Qual 周期、AEC-Q、PPAP 等约束不适用。

## 输入 / 输出契约

| 项 | 说明 |
|---|---|
| **必选输入** | 现有 BOM（Excel/CSV/ERP 导出，含 Qty + Unit Cost）、供应商报价、年采购量 |
| **可选输入** | 竞品 BOM、scrap rate、loaded labor rate、目标降本率 |
| **输出** | (1) ABC 高杠杆清单 (2) FAST 功能-成本矩阵 (3) Should-Cost 差距报告 (4) VAVE 提案清单（年节省/采纳率/Qual 周期/风险）(5) 新 BOM Cost Rollup |

## Workflow（5 阶段，严格顺序，不可跳步）

每阶段详细规则见 `references/`；本 body 只给执行骨架。

### 阶段 1：基线建立 -> `references/stage1-baseline.md`
1. 跑 Cost Rollup（用 `scripts/cost_rollup.py`）：`Sigma(Qty x Unit x Scrap) + Labor + Overhead + Logistics + Indirect`
2. ABC/Pareto 筛选 -> 锁定 Top 20 物料（A 类 10-20% 物料 / 70-80% 成本）
3. **铁律**：从 A 类（IC/连接器）开始，C 类（螺丝/标签）缓做
4. 红灯 STOP：输出 ABC 清单前确认物料数占比 vs 成本占比是否对得上 80/20

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

## Checkpoints（必须显式执行）

- 红灯 STOP 阶段 1：ABC 清单占比核对（80/20 是否成立）
- 红灯 STOP 阶段 2：FAST 完成前禁止砍 BOM
- 红灯 STOP 阶段 3：利润压到行业基准以下需用户签字确认风险
- 红灯 STOP 阶段 5：无 PPAP/EMC 重测禁止批量上线
- 红灯 STOP 全局：跨职能评审缺失禁止提交 Steering Committee
