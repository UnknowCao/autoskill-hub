# VAVE Proposal Scorecard

> Stage 5 deliverable. One row per proposal; submit to Steering Committee for approval.

## Proposal Table

| ID | Part / Function | Current State | Lever | Proposed Alternative | Annual Savings | Adoption Rate | Qual Weeks | Risk Level | Cross-Functional Review | Approved |
|---|---|---|---|---|---|---|---|---|---|---|
| P01 | MCU STM32F103RET6 | single-source, 26w lead | 2nd-source Tier 1 | GD32F103RET6 (P2P) | $18,000 | 85% | 20w | low | HW/SW/SQE/QA | pending |
| P02 | 0.1µF cap × 24 | duplicated across projects | platform-merge | standardize to 1 vendor, single reel | $4,200 | 95% | 4w | low | HW/QA | pending |
| P03 | Blue LED × 2 | customer-blind decoration | delete | remove from BOM | $3,000 | 100% | 0w | none | Product/QA | pending |
| P04 | Redundant OVP IC | over-engineered, safety | HARA + evaluate cancel | (pending HARA result) | $12,000 | 50% | 36w+ | high | FS/SQE/QA | pending |
| __FILL__ | | | | | | | | | | |

## Column Definitions

- **Lever** — one of: `2nd-source` / `platform-merge` / `DFMA-merge` / `should-cost` / `teardown` / `delete`
- **Annual Savings** = `(old_cost − new_cost) × annual_volume × adoption_rate`
- **Adoption Rate** — realistic % of BOMs that will adopt (not 100% by default; Tier 2 software fixes have 60-85%)
- **Qual Weeks** — full path to AVL update (Tier 1: 16-26w / Tier 2: 26-52w / Tier 3+: 26-52w+)
- **Risk Level** — `none`/`low`/`med`/`high` (high = touches safety function or single-source critical)
- **Cross-Functional Review** — must include: VAVE eng + Purchasing/SQE + HW + SW (if Tier 2) + QA + FS (if safety part)

## Risk-Adjusted ROI

```
Risk-Adjusted Savings = Annual Savings × Adoption Rate × (1 − Risk_Penalty)

Risk_Penalty:
  none = 0%
  low  = 5%
  med  = 15%
  high = 30%
```

| ID | Annual Savings | × Adoption | × Risk Adj | Risk-Adjusted Savings | Qual Cost | Net ROI |
|---|---|---|---|---|---|---|
| P01 | $18,000 | 85% | × 0.95 | $14,535 | $15,000 (Qual) | profitable in year 2 |
| __FILL__ | | | | | | |

## Steering Committee Submission Checklist

- [ ] Each proposal has all 11 columns filled (no `TBD` on Risk or Qual Weeks)
- [ ] Risk-Adjusted ROI computed for every proposal
- [ ] Safety-touching proposals (P04) have HARA reference or pending-HARA status
- [ ] Cross-functional review signatures captured (HW / SW / SQE / QA / FS as applicable)
- [ ] Qual timeline realistic (Tier 2 software fix ≥ 26 weeks, not "few weeks")
- [ ] New BOM Cost Rollup prepared for post-approval recomputation

## 🔴 Hard Stops

- **No PPAP/EMC retest plan** → reject submission (Stage 5 violation)
- **Single-department proposal** (e.g., Purchasing-only) → reject, require cross-functional
- **Qual weeks < 16 for any 2nd-source** → invalid, Tier 1 minimum is 16 weeks
- **Adoption rate = 100% by default** → unrealistic; must justify each line
