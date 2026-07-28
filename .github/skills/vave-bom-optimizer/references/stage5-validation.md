# 阶段 5：验证固化 —— 守住质量底线

> 阶段目标：把 VAVE 提案转化为批准的新 BOM，严守 APQP / PPAP / 二供 Qual 节奏，建立季度 VAVE 评审机制。

## 5.1 二供 Qualification 7 阶段时间表（汽车级）

来自 SupplyICs 行业基准：

| 阶段 | 活动 | 时长 |
|---|---|---|
| 1. 候选识别 | 交叉引用分析、datasheet 比对 | 2–4 周 |
| 2. 样品获取 | 工程样件、商业谈判、NDA | 4–12 周 |
| 3. 电气特性 | 温度 / 电压 / 频率角参数测试 | 4–8 周 |
| 4. 软件集成 | HAL / 驱动适配、寄存器映射 | 8–16 周 |
| 5. 可靠性测试 | HTOL / HAST / TC / ESD（AEC-Q100 / JEDEC） | 12–20 周 |
| 6. 系统级验证 | EMC / EMI、田间试验 | 8–16 周 |
| 7. 生产批准 | PPAP / FAI 提交、AVL 更新 | 4–8 周 |
| **总计关键路径** | | **14–18 个月** |

**关键洞察**：危机来临才启动 Qual 已经晚了 14 个月。**有前瞻性的公司提前 4.7× 更可能避免停产**（SIA 2025 调研）。

## 5.2 必须的验证清单

- [ ] AEC-Q100（IC）/ AEC-Q200（被动件）可靠性报告
- [ ] PPAP Level 3 文档包
- [ ] EMC / EMI 重测（关键变更）
- [ ] 功能安全影响评估（ISO 26262）
- [ ] 田间可靠性数据（小批量先验证）
- [ ] AVL（Approved Vendor List）更新

## 5.3 防止过度降本的安全阀

> "Lower margin does not mean better value" —— 把供应商压到不可持续是供应链风险，不是采购成就。

- 偷工减料常发生在看不见的地方（检验简化、材料降级、利薄到 reorder 找回）
- 必须配套：变更后缺陷率、客户抱怨数、田间退货率监控
- KPI 平衡：成本下降 vs 质量风险

## 5.4 阶段 5 输出

- `vave_proposal_scorecard.xlsx`：提案 + 年节省 + 采纳率 + Qual 周期 + 风险 + 批准状态
- `new_bom_cost_rollup.xlsx`：批准后的新 BOM Cost Rollup（复算收益）
- `change_control_package.zip`：PPAP / EMC 报告 / AVL 更新

## 5.5 季度 VAVE 评审节奏（防一次性项目）

```
Q1: 选 1-2 个 A 类 BOM → 基线 → FAST → Should-Cost
Q2: 杠杆匹配 → VAVE 提案 → Steering 批准
Q3: Qual 启动 → 小批量验证
Q4: 新 BOM 上线 → Rollup 复算 → 转下一轮
```

## 5.6 🔴 Checkpoint

- **无 PPAP / EMC 重测禁止批量上线** → 田间失效 / 召回
- 关键变更（BOM 主芯片 / 电源拓扑）必须重做功能安全影响评估（ISO 26262）
- 新 BOM 上线后 90 天内必须监控田间缺陷率，异常立即回滚
