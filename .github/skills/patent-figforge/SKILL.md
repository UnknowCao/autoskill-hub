---
name: patent-figforge
description: "Generate compliant patent figures (flowcharts, block diagrams, hierarchies, schematics) with Python graphviz, satisfying 37 CFR §1.84 (USPTO) and CNIPA 中国专利审查指南. Use when user asks: 画专利图, 画附图, 做专利附图, 生成专利图, patent figure, patent drawing, draw flowchart for patent, 画流程图, 系统框图, 原理图, 架构图, USPTO drawing, CNIPA drawing, 附图标记, reference numbers, lead lines, FIG. 1, 图1. Outputs B&W SVG/PNG ready for patent filing. Requires system Graphviz (`dot`) + `pip install graphviz`."
---

# Patent Figforge

Generate patent figures (USPTO/CNIPA) using Python `graphviz`. Requires `dot` (Graphviz) backend.

> ⚖️ **37 CFR §1.84** + **中国专利审查指南**. Violations may cause formal rejection.
> 🧭 **Design constitution**: 法律支持 > 技术揭示 > 再现鲁棒 > 美观. Never sacrifice marker clarity for aesthetics.

---

## §0 — Three Root Functions (附图存在论)

Every element must be defensible by one of these; otherwise delete it.

- **法律支持** — Visual evidence for every technical feature in the claims. Failure → claims narrowed/rejected/invalidated.
- **技术揭示** — Convey the inventive-step causal chain with minimal visual noise. Failure → examiner misreads; competitor designs around.
- **再现鲁棒** — Still readable in B&W print, shrunk to A4 width, scanned, read 10 years later.

Priority when conflict: **法律 > 技术 > 再现 > 美观**.

---

## §1 — Four Figure Types

Types differ in their **relation predicate** — the verb connecting nodes. Visual grammar must match the predicate.

| Type | Answers | Relation | Time | Direction |
|------|---------|----------|:----:|-----------|
| **流程图** (Flowchart) | 怎么做 | 「→ 然后」temporal trigger | Strong | `TB` vertical |
| **系统框图** (Block Diagram) | 是什么 | 「——属于/耦合于」structural | None | `LR` horizontal |
| **层级架构图** (Hierarchy) | 怎么分层 | 「属于层/跨层调用」layer | None | `TB` vertical |
| **原理图** (Schematic) | 为什么 | 「⇒ 导致/⇢ 转化为」causal | Chain | Causal axis (`LR`) |

**Type determination** — confirm before building:
- 流程图/方法/flowchart/步骤/时序 → Flowchart
- 框图/系统/block diagram/组件/模块 → Block Diagram
- 架构/层级/hierarchy/感知层→决策层→执行层 → Hierarchy
- 原理图/schematic/信号流/因果/反馈环路 → Schematic

---

## §2 — Five Layout Axioms (布局公理)

Apply to all four types. Violating any = design defect.

### Axiom 1 — 正交性 (Orthogonality)
All lines horizontal or vertical. Zero diagonals.
- `splines='polyline'` (NOT `ortho` — drops edge labels + ports)
- Every edge MUST specify `tailport`/`headport` (`n`/`s`/`e`/`w`)

### Axiom 2 — 主流向 (Main Flow Axis)
Core path = single visual centerline; auxiliary elements hang outside. Flowchart: vertical. Block diagram: horizontal. Auxiliary never on centerline.

### Axiom 3 — 通道隔离 (Channel Isolation)
Lines of different semantics travel in separate physical channels:

| Channel | Semantic | Style | Position |
|:-------:|:---------|:------|:---------|
| 🔵 | Main flow / signal | solid, arrowhead, 0.8pt | Center axis |
| 🟢 | Loop-back / feedback | solid, arrowhead, 0.8pt | Outermost left/right |
| 🟡 | Signal/data + label | solid, arrowhead + label | Inter-row channel |
| ⚪ | Reference number lead | dotted, 0.5pt, no arrow | Opposite of loop-back |
| ⚫ | Bus / aggregation | double/thick + slash + count | Dedicated bus channel |

🔴 Loop-back and reference channels **must never share the same lane** — root cause of lead-line crossing.

### Axiom 4 — 最短引线 (Shortest Lead)
Lead line ≤ 10mm / ≤ 1.5× box height. Ref numbers share target's rank; lead = short segment from border outward.

**Angle discipline** (full derivation: `references/numbering.md` §2):
- Allowed: {0°, 15°, 30°, 45°, 60°, 75°, 90°} — 15° increments from human visual acuity at patent scale
- Priority: 0° (horizontal) > 90° (vertical) > 15° > 30° > 45° (last resort)
- 🔴 Prohibited: non-15°-multiple angles, angles parallel to main flow lines

### Axiom 5 — 回流外侧 (Outer Return)
Loop-backs travel outermost edge: vertical rise then horizontal fold-back. Never cross main flow.

---

## §3 — Channel Allocation Matrix

Which physical lane carries which semantic line per figure type:

| Lane | Flowchart | Block Diagram | Hierarchy | Schematic |
|:----:|:---------:|:-------------:|:---------:|:---------:|
| Center vertical | Main flow | — | Inter-layer call | Causal chain |
| Center horizontal | — | Main signal | Same-layer nodes | Same-stage nodes |
| Left outer | (reserved) | Auxiliary | Reference numbers | Feedback loop |
| Right outer | Loop-back **OR** refs | Reference numbers | (reserved) | Reference numbers |
| Below | — | Auxiliary | — | Ground/reference |
| Above | — | — | — | Power/source |

🔴 Loop-back and reference numbers **never share a lane**. If loop-back is right, refs go left (vice versa).

---

## §4 — Style Quick Reference

**Shapes** (full spec: `references/shape-specs.md`, `references/best-practices.md`):
- Rectangle (`shape='box'`, sharp) → module/component/step. CNIPA: sharp corners preferred.
- Ellipse (`shape='ellipse'`, flat, w:h≈3:1) → start/end. Diamond (`shape='diamond'`, flat, w:h≈2:1) → decision (exactly 2 exits).
- Parallelogram → data I/O. Cylinder → storage. Circle → physical state. Double-box (`peripheries=2`) → subroutine.

**Lines** (full spec: `references/best-practices.md` §B):
- Solid thick (0.8pt) → main structure/power. Solid thin (0.5pt) → signal/data/control.
- Dashed → optional/feedback/wireless. Dotted (0.5pt, no arrow) → lead line.
- Arrowhead only on flow edges; `arrowhead='none'` on lead lines.

**Node content rule**: Flowchart = verb-noun ("采集温度数据"). Block diagram / hierarchy = noun phrases ("电池监测单元"), verbatim from claims.

---

## §5 — Dependencies

System Graphviz (backend — required): `choco install graphviz` (Win) / `apt install graphviz` (Linux) / `brew install graphviz` (Mac).

Python: `pip install graphviz`.

---

## §6 — Build Workflow

### Step 1: Jurisdiction + type decision (5 seconds, before any code)

**Jurisdiction** — pick one, set ONCE at script top:

| Jurisdiction | `fontname` | Figure label | Decision branch labels |
|---|---|---|---|
| 🇨🇳 CNIPA | `'Microsoft YaHei'` (Win) / `'Noto Sans CJK SC'` (Linux/Mac) | `label='图1'` | `'是'`/`'否'` |
| 🇺🇸 USPTO | `'Arial'` | `label='FIG. 1'` | `'YES'`/`'NO'` |

If user doesn't specify → ask. Do NOT silently default.

**Figure type** — match the user's request verb to the relation predicate (§1 table):

| User says | Type | rankdir |
|---|---|---|
| 怎么做 / 步骤 / 时序 / flowchart / 流程 / 方法 | Flowchart | `TB` |
| 是什么 / 组件 / 模块 / block / system | Block Diagram | `LR` |
| 怎么分层 / 架构 / hierarchy / 感知→决策→执行 | Hierarchy | `TB` |
| 为什么 / 信号流 / 因果 / 反馈 / schematic / 原理 | Schematic | `LR` |

If ambiguous → ask the user one clarifying question.

### Step 2: Reference-number triage (the legal gate)

Before writing any node, decide WHICH components get ref numbers. The legal limit is **max 2–3 per figure** (§1.84(q) — root cause of lead-line crossing when exceeded).

**Triage decision tree**:
1. List all components from the claims/spec.
2. Mark each as **claim-essential** (appears in independent claim) vs **supporting** (only in dependent claims or description).
3. Number only the **claim-essential** components first. If > 3 claim-essential components → **split the figure** (see §14), do NOT cram.
4. Assign numbers per `references/numbering.md` §1 (hierarchical `100/110/111` for systems, linear `10/20/30` for simple figures).
5. Reserve the lane OPPOSITE the loop-back channel for ref numbers (Axiom 3).

🔴 **If you find yourself wanting > 3 ref numbers in one figure → STOP. This is the historical bug (R1 root cause). Split per §14.**

### Step 3: Build with Python (single file, self-contained)

Write ONE script that contains, in this order:
```python
import os, graphviz
os.environ["PATH"] = r"C:\Program Files\Graphviz\bin;" + os.environ.get("PATH", "")  # Win; omit on Linux/Mac if dot in PATH

# 1. Universal attrs (copy verbatim from references/code-templates.md §"Universal Patent-Grade Attributes")
GRAPH_BASE = {...}; NODE_BASE = {...}; EDGE_BASE = {...}

# 2. Helpers (copy verbatim from references/code-templates.md §"Reference-Number Helpers")
#    Includes _rankdir, add_ref_horizontal, add_ref_vertical, and back-compat aliases
#    add_ref_right/left/top/bottom (now rankdir-aware, B1 bug FIXED in R5)

def _rankdir(g): ...
def add_ref_horizontal(g, rid, target, label, side='right'): ...
# ... (full code in code-templates.md)

# 3. Figure (use the matching template)
g = graphviz.Digraph(name='FIG1',
    graph_attr={**GRAPH_BASE, 'rankdir': '<TB|LR>'},
    node_attr=NODE_BASE, edge_attr=EDGE_BASE)
g.attr(label='<图1|FIG. 1>', labelloc='b', fontsize='14')
# ... nodes, edges, add_ref_* calls (max 2-3)

# 4. Render
g.render('output', format='svg')
g.render('output', format='png')
```

🔴 **The script MUST be self-contained** — define GRAPH_BASE/NODE_BASE/EDGE_BASE and helpers IN the script. Do NOT rely on imports from the skill folder (those are reference docs, not importable modules). Copying a template alone without the helpers → `NameError`.

### Step 4: Render + 🔴 MANDATORY view_image verification

```python
g.render('output', format='svg')
g.render('output', format='png')
```

🔴🔴 **BLOCKING CHECKPOINT — DO NOT CLAIM COMPLIANCE WITHOUT THIS**:

1. **Confirm render succeeded**: no Python exception, both files exist and > 0 bytes.
2. **🔴 CALL `view_image` ON THE PNG** — this is non-negotiable. Do NOT claim "looks good" from reading code. Do NOT skip because "the code follows the rules". The historical R1 bug (lead lines crossing) was caused exactly by skipping visual verification.
3. **While viewing the PNG**, verify each item against §9 Pre-Submission Checklist. Pay special attention to:
   - (c) lead lines do NOT cross each other
   - (d) loop-back does NOT cross main flow
   - (e) every edge is orthogonal (no diagonals)
   - lead lines exit at the angle matching their helper (horizontal for left/right, vertical for top/bottom)
4. **If ANY item fails** → see §11 Failure Modes, fix, re-render, re-view_image. Do not iterate more than 3 times on the same defect — if still failing, escalate to user with the PNG attached.

> ⚠️ **Why this is a CHECKPOINT**: claims of patent-figure compliance without visual verification are worthless. The R1/R2/R3 history of this skill is a sequence of "I followed the rules but the output was wrong" bugs that only view_image catches.

---

## §7 — Type-Specific Critical Rules

### 7.1 Flowchart
- Main axis: vertical (`TB`), high-weight edges keep centerline straight
- Decision: `:e`=是, `:w`=否 (ISO 5807). Never 3+ exits per diamond.
- Loop-back in left lane → refs in right lane (or swap). Loop node anchored to decision rank via `rank='same'`.
- ❌ One node = one action (split multi-action nodes). ❌ Node size ≠ importance indicator.

### 7.2 Block Diagram
- Main signal: horizontal left→right (`LR`), sensor → processor → actuator
- Auxiliary (memory, protection) hang **below** main axis via `tailport='s'`
- Bus: thick line + slash + count, or merge-then-branch
- Solid = physical/data; Dashed = wireless/optional; No arrow = structural coupling
- ❌ Arrow for containment → use cluster. ❌ Module name ≠ claims wording (legal support).

### 7.3 Hierarchy
- Each layer = one horizontal cluster (`style='dashed'`, `labeljust='l'`)
- Cross-layer calls strictly vertical (`tailport='s'`, `headport='n'`)
- ⚠️ **CRITICAL**: never `rank='same'` inside clusters — Graphviz silently drops them. Use `style='invis'` edges for intra-layer alignment. `newrank='true'` required.
- Refs: left side of layer, 2–3 per figure.

### 7.4 Schematic
- Causal chain along main axis: input → process → output. Feedback in outermost lane.
- Three line types MUST be visually distinct: physical connection (solid, thickness-graded), causal signal lead (thin/dashed), feedback lead (dashed + reverse arrow).
- Every signal line labeled with physical quantity + unit (`I_bat [A]`, `ΔT [°C/s]`). **Legend mandatory**.
- ❌ Physical & causal same style. ❌ Mixing structural info → block diagram. ❌ Omitting units → fatal.

Full type specs: `references/shape-specs.md`, schematic: `references/schematic.md`.

---

## §8 — Critical Legal Rules (37 CFR §1.84 / 中国专利审查指南)

| § Clause | Requirement | Graphviz |
|----------|-------------|----------|
| §1.84(a)(1) | **Black ink only**, B&W | `bgcolor='white'`, all `color='black'` |
| §1.84(g) | Margins top/left ≥2.5cm | `margin='1.0'` |
| §1.84(k) | Legible at **2/3** reduction | `dpi='300'` |
| §1.84(l) | Lines durable, clean, uniformly thick | main 0.8pt, lead 0.5pt |
| §1.84(o) | **As few words as possible** | concise labels, no sentences |
| §1.84(p)(1) | Ref chars = plain Arabic numerals | `shape='plaintext'` |
| §1.84(p)(3) | Ref chars ≥ 0.32cm (≈14pt) | `fontsize='14'` |
| §1.84(p)(4) | Same part = same ref across views | same node ID across all figures |
| §1.84(p)(5) | Refs in desc ↔ drawings match | cross-ref audit before submission |
| §1.84(q) | 🔴 **Lead lines MUST NOT cross** | max 2–3 refs, opposite sides |
| §1.84(r) | Arrow meaning clear | `arrowhead='none'` on leads |
| §1.84(u) | Consecutive numbering: FIG./图 | `label='图1'`/`'FIG. 1'`, `labelloc='b'` |

> 🔴 **§1.84(q) anti-pattern**: `g.edge('r10', 'cpu', style='dotted', constraint='false')` → ref floats, leads cross. **Fix**: `add_ref_right(g, 'r10', 'cpu', '10')` — anchors to rank via `rank='same'`.

---

## §9 — Pre-Submission Checklist (BLOCKING)

```
☐ §1.84/审查指南   Black ink only, B&W               ☐ Axiom 1   All edges orthogonal (no diagonals)
☐ §1.84(l)         0.8pt main / 0.5pt lead           ☐ Axiom 2   Main flow on centerline
☐ §1.84(p)(3)      Font ≥14pt                        ☐ Axiom 3   Loop-back & refs SEPARATE lanes
☐ §1.84(k)         DPI≥300, legible at 2/3           ☐ Axiom 4   Lead lines ≤1.5× box height
☐ §1.84(p)(1)      Arabic numbers, plain, outside    ☐ Axiom 5   Loop-back on outermost edge
☐ §1.84(g)         Margins top/left ≥2.5cm           ☐           Lines don't cross boxes
☐ §1.84(q)         Lead lines DO NOT cross           ☐           Same component = same number
☐ §1.84(p)(5)      Cross-ref desc ↔ drawings         ☐           Equal-size nodes
☐ 🀄               中文标注 (Chinese labels)          ☐           Node names match claims verbatim
☐ §0               Every element defensible by a root function
```

---

## §10 — Anti-Patterns (DO NOT)

| # | Don't | Sev | Do instead |
|---|-------|:---:|------------|
| 1 | Rounded corners | 🟡 | `shape='box'` (sharp) — CNIPA |
| 2 | Lines <0.8pt main | 🔴 | 0.8pt main, 0.5pt lead |
| 3 | Diagonal lines | 🔴 | `splines='polyline'` + ports on every edge |
| 4 | Arrows through boxes | 🔴 | Safe-channel routing (Axiom 3) |
| 5 | Ref numbers inside boxes | 🔴 | Outside + dotted lead |
| 6 | Color fills / gradients | 🔴 | Pure B&W (§1.84(a)(1)) |
| 7 | Title inside diagram | 🟡 | `label='图1'`, `labelloc='b'` |
| 8 | Lead lines cross | 🔴 | §1.84(q): max 2–3 refs, opposite sides |
| 9 | Loop-back & refs share lane | 🔴 | Axiom 3: opposite lanes |
| 10 | Box w:h ≈ 1:1 | 🟡 | ≥ 3:1 via `width='2.2'`, `height='0.8'` |
| 11 | Tall diamond | 🟡 | Flat, w:h ≈ 2:1 |
| 12 | Decision 3+ exits | 🔴 | Cascade, max 2 exits |
| 13 | 是=left, 否=right | 🔴 | ISO 5807: `:e`=是, `:w`=否 |
| 14 | Unlabeled decision branches | 🟡 | `label='是'`/`label='否'` |
| 15 | Node size/color = importance | 🔴 | No importance concept in patent figures |
| 16 | Arrow for containment | 🔴 | Use cluster (nested boxes) |
| 17 | Module name ≠ claims | 🔴 | Verbatim match (legal support) |
| 18 | Physical & causal same style | 🔴 | Visually distinguish (schematic) |
| 19 | Claim compliance without viewing | 🔴 | ALWAYS open PNG and verify |

---

## §11 — Failure Modes

| Symptom | First fix | Still failing? |
|---------|-----------|----------------|
| `ExecutableNotFound` | Install system Graphviz (§5) | graphviz.org/download |
| `graphviz` import error | `pip install graphviz` | Check Python env |
| Syntax/attribute error | Check quotes, commas, `->` | Simplify to minimal graph |
| Blank output | `bgcolor='white'`, nodes have `label` | Try `format='png'` |
| Chinese garbled | `fontname='Microsoft YaHei'` (Win) | Fall back to English |
| Lead lines cross | `add_ref_left/right()`; max 2–3 refs | `rank='same'` + invisible spacer |
| Loop-back crosses flow | Anchor loop node via `rank='same'` + invisible edge | Route through outermost lane |
| Diagonal lines | `tailport`/`headport` on every edge | `splines='polyline'` (not `'true'`) |
| Edge labels missing | `splines='polyline'` (NOT `'ortho'`) | Label on short edge segment |
| Cluster disappears | `newrank='true'` | `style='invis'` edges (not `rank='same'` in cluster) |
| Decision exits wrong side | `dec:e`=是, `dec:w`=否 | Route through invisible node |
| Equal-size nodes broken | `fixedsize='true'` + `width`/`height` | Truncate labels with `\n` |
| Output too large | Reduce DPI; simplify nodes | Split into sub-figures (图2a/2b) |

---

## §12 — Multi-Figure Collaboration (拆图 + 多视图)

When one figure isn't enough — either because > 3 components need ref numbers, or the same component appears in multiple views.

### 12.1 Splitting a figure (图2a / 图2b) — when |refs| > 3

🔴 Triggered by §6 Step 2 triage: more than 3 claim-essential components in ONE figure. Cramming them all in = guaranteed lead-line crossing (violates §1.84(q)).

**Splitting protocol**:
1. **Group components by subsystem** (e.g., power-path vs control-path). Each sub-figure gets ≤ 3 refs.
2. **Sub-figure naming**: 图2a, 图2b (CNIPA) / FIG. 2A, FIG. 2B (USPTO). Same base number, alphabetic suffix.
3. **Cross-figure refs**: a component numbered `110` in 图2a keeps `110` if it re-appears in 图2b (§1.84(p)(4)). Do NOT renumber.
4. **Shared connectors**: draw a dashed "system boundary" box in each sub-figure showing where the OTHER sub-figure connects. Label it with the other figure's name (e.g., "→ 见图2b").
5. **Independent scripts**: each sub-figure = its own `graphviz.Digraph` + its own `render()`. Do NOT try to render both in one call.

```python
# 图2a: power path (refs 110, 120, 130)
g_a = graphviz.Digraph(name='FIG2a', ...)
add_ref_right(g_a, 'r110', 'battery', '110')
add_ref_right(g_a, 'r120', 'inverter', '120')
add_ref_right(g_a, 'r130', 'motor', '130')
g_a.render('fig2a', format='svg')

# 图2b: control path (refs 210, 220) — borrows '120' from fig2a
g_b = graphviz.Digraph(name='FIG2b', ...)
g_b.node('inverter_ref', '逆变器\n(见图2a, 120)', shape='box', style='dashed')  # boundary marker
add_ref_right(g_b, 'r210', 'mcu', '210')
add_ref_right(g_b, 'r220', 'sensor', '220')
g_b.render('fig2b', format='svg')
```

### 12.2 Multi-view drawings (§1.84(p)(4) — same ref across views)

Same component, different angles/perspectives (e.g., 图3 = 外观图, 图4 = 内部结构图). The SAME component MUST carry the SAME number across all views.

**Consistency protocol**:
1. **Centralize node IDs**: define a Python dict mapping component → ref number, used by ALL figure scripts.
2. **Single source script**: prefer ONE `.py` file that builds all views and renders each. If you must split into multiple files, the dict MUST be copy-pasted verbatim (or imported via `from ref_table import REFS`).
3. **Verify before submission**: run `references/numbering.md` §7.1 checklist view-by-view. Specifically: every ref in the description appears in ≥ 1 view, and every ref in any view appears in the description (§1.84(p)(5) bidirectional match).

```python
# ref_table.py — single source of truth, shared across all view scripts
REFS = {
    'battery': '110', 'inverter': '120', 'motor': '130',
    'mcu': '210', 'sensor': '220', 'housing': '310',
}

# In each view script:
from ref_table import REFS
add_ref_right(g_view1, 'r110', 'battery', REFS['battery'])
```

### 12.3 Anti-patterns for multi-figure

| Don't | Sev | Do instead |
|---|:---:|---|
| Renumber a shared component per-view | 🔴 | §1.84(p)(4): same number across all views |
| Render multiple figures in one `g.render()` call | 🔴 | One Digraph per figure, separate render calls |
| Re-describe the same component differently per-view | 🟡 | Use identical node label text (or "name (见 figureX)" suffix) |
| Skip cross-ref desc↔drawings audit at submission | 🔴 | §1.84(p)(5) bidirectional match is a frequent rejection cause |

---

## §13 — References

- **`references/code-templates.md`** — 🆕 **Single source of truth** for: universal attrs (`GRAPH_BASE`/`NODE_BASE`/`EDGE_BASE`), rankdir-aware helpers (`add_ref_horizontal`/`add_ref_vertical` + back-compat aliases), 4 figure-type templates. Always copy helpers FROM HERE.
- **`references/numbering.md`** — 🆕 引线第一性原理几何学: 五条公理, 15°角度学, 走线学, 形式化约束 C1–C8, 设计协议, 合规验证. §6 now points to code-templates.md as the helper single-source (R5).
- **`references/best-practices.md`** — ISO 5807/ISO 128 conventions: shapes, decision exits, line types, lead lines
- **`references/requirements-common.md`** — USPTO & CNIPA shared requirements: full legal text with Graphviz settings (R5: ref-number fontsize corrected to 14pt)
- **`references/requirements-uspto-only.md`** — USPTO-only: FIG. format, English, §1.84(p)(5) cross-ref
- **`references/requirements-cnipa-only.md`** — CNIPA-only: 图1 format, Chinese labels, box-text mandate
- **`references/shape-specs.md`** — Per-type shape tables, layout grids, channel routing, funnel convergence
- **`references/schematic.md`** — Schematic spec: physical symbols, causal-chain annotation, feedback loops, legend
- **`专利附图设计哲学_第一性原理.md`** — Design constitution: first-principles derivation of all rules

---

## §14 — Change Log

- **R5 (2026-07-23)** — Fact-grounded audit + 7 fixes:
  - 🔴 Fixed B1: `add_ref_top`/`add_ref_bottom` used `rank='same'` which produced horizontal leads (claimed 90° vertical). Rewrote as rankdir-aware `_rankdir` + `add_ref_horizontal`/`add_ref_vertical` + back-compat aliases. Verified 8/8 (TB+LR × 4 aliases) via `_verify_helpers.py`.
  - 🔴 Fixed B2 (same root cause): `add_ref_right`/`left` in LR mode flipped to vertical — now also rankdir-aware.
  - 🔴 Fixed B3: `requirements-common.md` §5 said ref-number `fontsize='12'`, violating §1.84(p)(3). Corrected to 14pt; clarified edge-labels can stay 12pt.
  - Eliminated C1 drift: `numbering.md` §6 was a second copy of helpers. Now marked "single source = code-templates.md", old code kept as deprecated reference.
  - dim1: expanded frontmatter description with trigger words (画专利图/patent figure/附图/FIG. 1/图1/etc).
  - Rewrote §6 Build Workflow: jurisdiction+type decision tables (Step 1), reference-number triage decision tree (Step 2), self-contained script requirement (Step 3), mandatory `view_image` checkpoint (Step 4).
  - Added §12 Multi-Figure Collaboration (split-when->3-refs + multi-view-same-ref).
- **R4 (2026-07-22)** — loop-back invisible node fix.
- **R1–R3 (2026-07-22)** — five axioms, channel allocation matrix, type-specific rules, anti-patterns, failure modes.
