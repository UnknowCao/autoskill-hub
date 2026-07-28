# FAST Function-Cost Worksheet

> Stage 2 deliverable. Use after ABC screening locks the Top 20 high-leverage parts.
> Goal: re-express each BOM line as a *function carrier*, then judge necessity vs. cost.

## Step 1 — Function Definition (Two-Word Rule)

For each Top 20 part, write the function as **Verb + Measurable Noun** (active voice).

| Part Number | Description | Verb | Noun | Full Function | Basic/Critical/Support |
|---|---|---|---|---|---|
| MCU-STM32F103RET6 | Main MCU | Execute | control-logic | Execute control logic | Basic |
| PMIC-TPS653853A | Multi-rail power | Regulate | voltage-rails | Regulate voltage rails | Critical |
| CAN-SN65HVD230 | CAN xcvr | Transmit | can-frames | Transmit CAN frames | Critical |
| LED-BLUE-0805 | Blue LED | Indicate | status-blue | Indicate status blue | Support |
| __FILL__ | | | | | |

Rules:
- Forbidden verbs: `Get` / `Equip` / `Give` (too vague)
- Function ≠ feature: "RGB LED" is a feature; "Indicate charging state" is a function
- One function per row; if a part has multiple functions, split rows

## Step 2 — How-Why Logic Chain

Link functions in `How higher-level ← Why lower-level` chain. Mermaid template:

```mermaid
flowchart LR
    B["Regulate 5V<br/>Basic"]:::basic
    C1["Convert 12V→5V<br/>Critical"]:::critical
    C2["Filter ripple<br/>Critical"]:::critical

    B -- Why --> C1
    C1 -- Why --> C2
    C2 -- How --> C1
    C1 -- How --> B

    classDef basic fill:#7B1FA2,stroke:#4A148C,color:#fff,stroke-width:3px
    classDef critical fill:#00897B,stroke:#004D40,color:#fff,stroke-width:2px
```

## Step 3 — Function-Cost Matrix

The core VAVE artifact: function × cost × necessity.

| Function | Carrier Part | Annual Cost | Necessity | Cost x Necessity | VAVE Direction |
|---|---|---|---|---|---|
| Regulate 5V | LDO X | $0.80 | ✅ necessary | high cost + high need | 2nd-source (Tier 1) |
| Filter noise | 0.1µF × 8 | $0.40 | ✅ necessary | medium + high need | platform merge |
| Aesthetic LED | Blue LED × 2 | $0.30 | ❌ customer-blind | low + low need | **delete** |
| Redundant OVP | 2nd OVP IC | $1.20 | ⚠️ over-engineered | high + uncertain | **HARA review** |
| __FILL__ | | | | | |

### Necessity decision rules
- ✅ **necessary** — directly serves Basic/Critical function; cannot delete
- ❌ **customer-blind** — no user value (decorative); candidate for deletion (confirm with product team)
- ⚠️ **over-engineered** — likely redundant safety margin; requires HARA / functional-safety review before touching

## Step 4 — Prioritize VAVE Targets

Sort by `cost DESC, necessity ASC`. Top targets = **high cost + low necessity**.

| Rank | Function | Action |
|---|---|---|
| 1 | __FILL__ | __FILL__ |
| 2 | __FILL__ | __FILL__ |

## 🔴 Checkpoint before exiting Stage 2

- [ ] Every A-class part has at least one function row
- [ ] No function uses `Get`/`Equip`/`Give` verbs
- [ ] ⚠️ over-engineered rows touching safety functions (OVP / watchdog / breaker) flagged for HARA
- [ ] ❌ customer-blind deletions confirmed with product definition team
- [ ] FAST diagram committed before any BOM cut
