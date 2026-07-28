# 阶段 2：功能重构 —— FAST 驱动的「非增值识别」

> 阶段目标：用 FAST（Function Analysis System Technique）把 BOM 行重新定义为「功能载体」，识别非必要 / 过度设计 / 客户不感知的功能。

## 2.1 FAST 基本规则

- **两词规则**：每个功能 = 一个**动词 + 可测量名词**（如 `Transmit signal` / `Regulate 5V` / `Filter ripple`）
- **主动语态**，禁止被动；禁止 `Get` / `Equip` / `Give`
- **功能 ≠ 特征**：识别功能而非典型特征（功能是「做什么」，特征是「是什么」）

## 2.2 How-Why 逻辑链

```
Why higher-level ←── How lower-level
  Basic function
       ↑ Why
   Critical function 1
       ↑ Why
   Critical function 2
       ↓ How
   Critical function 1
       ↓ How
  Basic function
```

**电源管理示例**：
- Basic：`Regulate 5V`（电源调控）
- Why → `Convert 12V→5V`（电压转换，Critical）
- Why → `Filter ripple`（纹波滤波，Critical）

## 2.3 FAST 在 BOM 优化的特殊用法 —— 功能-成本矩阵

把 FAST 图的每个功能节点，关联其**承载物料的成本**：

| 功能 | 承载物料 | 成本 | 是否必要 | 优化方向 |
|---|---|---|---|---|
| Regulate 5V | LDO X | $0.8 | ✅ 必要 | 二供替代 |
| Filter noise | 0.1μF × 8 颗 | $0.4 | ✅ 必要 | 平台化合并 |
| Aesthetic LED | 蓝色 LED × 2 | $0.3 | ❌ 客户不感知 | 删除 |
| Redundant OVP | 第二路保护 IC | $1.2 | ⚠️ 过度设计 | 评估取消 |

**价值公式 V = F / C 的实操化**：
- 高成本 + 低必要度 = **首要 VAVE 目标**（❌删除 / ⚠️评估取消）
- 高成本 + 高必要度 = 走 Should-Cost + 二供（✅降本不删功能）
- 低成本 + 低必要度 = 次要目标（合并即可）

## 2.4 阶段 2 输出

- `fast_diagram.mmd`（FAST 图，可绘制）
- `function_cost_matrix.csv`：功能 + 承载物料 + 成本 + 必要性 + 优化方向

## 2.5 🔴 Checkpoint

- **跳过 FAST 直接砍 BOM = 砍掉必要功能 → 质量事故**。强制 FAST 完成才能进阶段 3
- 必要性判定需功能安全视角：涉及 ISO 26262 的功能（如 OVP、看门狗、断路）即便「过度设计」也慎删，需做 HARA 评估
- 「客户不感知」类（Aesthetic LED / 装饰件）需先与产品定义团队确认，不能单方面删
