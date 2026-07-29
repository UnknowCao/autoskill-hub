# 阶段 1：基线建立 —— BOM Cost Rollup + ABC 筛选

> 阶段目标：从原始 BOM 建立可量化、可对比的成本基线，锁定 VAVE 高杠杆物料。

## 1.1 BOM Cost Rollup 公式（教学综合公式，来自 openBOM blog）

> ⚠️ **公式准确性澄清（2026-07 调研修正）**：openBOM **原生产品**的 Rollup 只做 `Qty × Cost`；下列含 Yield/Scrap/Labor/Overhead 的完整公式来自 openBOM **教学 blog**，是 VAVE 实践中的「应该这么做」的综合公式，不是 openBOM 软件内置功能。实施时需在 ERP/自建脚本中自行扩展。

```
Total BOM Cost = Σ(Component Qty × Unit Cost × Yield/Scrap Factor)
               + Direct Labor
               + Manufacturing Overhead
               + Logistics
               + Indirect Costs
```

**关键修正项**（不可省略，否则基线严重失真）：

- **Yield/Scrap Factor**：100 颗需求 + 5% scrap = 实际采购 105 颗。`Scrap = Demand / (1 - ScrapRate)`
- **Direct Labor**：`cycle_time × loaded_rate`，loaded_rate 含社保 30–40%
- **Manufacturing Overhead**：通常为直接人工的 **2–4×**（电子装配行业基准）
- **Logistics**：进项运费 + 关税 + 仓促加急费
- **Indirect Costs**：质量检验 + 库存持有成本

## 1.2 多层级 BOM 的层级 Rollup

```
顶层产品成本
   ↑ roll up
子装配体成本（= 其下所有零件 Rollup）
   ↑ roll up
   …
   ↑ roll up
最底层元器件（Qty × Unit Cost × Scrap）
```

**杠杆放大效应**：一个被多个子装配体共用的零件，其 10% 成本上涨会被 N 倍放大到顶层。**平台化物料应优先 VAVE**。

## 1.3 ABC / Pareto 筛选（80/20）

按「成本占比 vs 物料数占比」做帕累托：

| 类别 | 物料数占比 | 成本占比 | VAVE 优先级 |
|---|---|---|---|
| **A 类** | 10–20% | **70–80%** | 🔴 P0 必做（MCU、电源 IC、连接器） |
| **B 类** | 30–40% | 15–25% | 🟡 P1 应做（阻容、二极管） |
| **C 类** | 40–50% | 5–10% | 🟢 P2 缓做（标签、包装） |

**铁律**：永远从 A 类开始。C 类降本收益低且验证成本相对高。

## 1.4 ABC 扩展维度：成本 × 战略重要度 二维矩阵

|  | 高成本 | 低成本 |
|---|---|---|
| **高战略重要度**（安全件 / 单一供应商） | 🔴 **A1 立即做**（高成本 + 高风险） | 🟡 B1 关注（功能安全件，需双供） |
| **低战略重要度**（通用件 / 多供应商） | 🟠 A2 优先做（降本空间大） | 🟢 C2 平台化合并 |

## 1.5 阶段 1 输出

- `baseline_cost_rollup.xlsx`（含 scrap / labor / overhead / logistics）
- `abc_top20.csv`（Top 20 高杠杆物料清单 + 类别 + 战略重要度 + VAVE 优先级 P0/P1/P2）

## 1.6 🔴 Checkpoint

- 确认物料数占比 + 成本占比是否对得上 80/20。若 A 类成本占比 < 60%，说明 BOM 数据可能不全或散落，需重查
- 多层级 BOM 必须跑完层级 Rollup，禁止只算最底层元器件简单加总
