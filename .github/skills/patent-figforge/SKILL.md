---
name: patent-figforge
description: "Patent-ready technical diagrams via Python graphviz. 专利附图：流程图、系统框图、架构图。"
---

# Patent Figforge

Generate patent figures (USPTO/CNIPA) using the Python `graphviz` package. Requires `dot` (Graphviz) as backend.

## Required Dependencies

**System Graphviz (backend — required)**:

| OS | Command |
|----|---------|
| Windows | `choco install graphviz` |
| Linux | `sudo apt install graphviz` |
| Mac | `brew install graphviz` |

**Python package (frontend — used by this skill)**:

```bash
pip install graphviz
```

## Workflow

### Step 1: Determine diagram type

| User says | Type | Direction | Node shapes | Skeleton |
|-----------|------|-----------|-------------|----------|
| 流程图/方法/flowchart | **Flowchart** | `rankdir='TB'` | ellipse → box → diamond → ellipse | `flowchart-skeleton.py` |
| 框图/系统/block diagram | **Block Diagram** | `rankdir='TB'` | All `shape='box'` | `block-diagram-skeleton.py` |
| 架构/层级/hierarchy | **Hierarchy** | `rankdir='TB'` or `'LR'` | `shape='box'`, cluster groups | `hierarchy-skeleton.py` |

🔴 **CHECKPOINT**: confirm type before Step 2. If unsure, show this table to user.

### Step 2: Build graph with Python

```python
import graphviz

g = graphviz.Digraph(
    name='PatentFigure',
    graph_attr={'rankdir': 'TB', 'bgcolor': 'white', 'fontname': 'Microsoft YaHei'},
    node_attr={'fontname': 'Microsoft YaHei', 'fontsize': '14', 'fontcolor': 'black',
               'color': 'black', 'penwidth': '0.6'},
    edge_attr={'fontname': 'Microsoft YaHei', 'fontsize': '11', 'fontcolor': 'black',
               'color': 'black', 'penwidth': '0.6'},
)
g.attr(label='图1', labelloc='b', fontsize='14')

# Example: box + lead-line reference number
g.node('cpu', 'Processor', shape='box')
g.node('r10', '10', shape='plaintext', fontsize='11')
g.edge('r10', 'cpu', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
```

Skeletons: `assets/flowchart-skeleton.py`, `assets/block-diagram-skeleton.py`, `assets/hierarchy-skeleton.py`.

#### Hierarchy specifics

- Use `subgraph cluster_*` for layer grouping with `label='层名'`, `labeljust='l'`, `style='dashed'`
- Set `newrank='true'` in `graph_attr` to prevent rank/cluster conflicts
- **⚠️ Do NOT use `rank='same'` subgraphs inside clusters** — Graphviz drops clusters silently. Use invisible edges (`style='invis'`) for intra-layer alignment instead
- Layer labels: `fontsize='13'`, top-left justified
- Inter-layer arrows: connect specific components, not layer-to-layer; label in Chinese (CNIPA) or English (USPTO)
- See `references/shape-specs.md` § Hierarchy for full layout rules

#### Flowchart specifics

**Decision exit convention** (critical for patent compliance):

| Branch | Exits from | Port hint |
|--------|-----------|-----------|
| **是 (Yes)** | Diamond **right** tip | `:e` |
| **否 (No)** | Diamond **bottom** tip (or left) | `:s` or `:w` |

```python
# ✅ RIGHT — port hints control exit direction:
g.edge('dec1:e', 'step_yes', label='是')
g.edge('dec1:s', 'step_no',  label='否')

# ❌ WRONG — no port hint: graphviz may route 是 left, 否 right
g.edge('dec1', 'step_yes', label='是')
```

**Loop-back routing** (e.g., "否" returns to an earlier step):

Loop-backs are the most common flowchart pattern and the hardest to route correctly. Use invisible intermediate nodes to create "safe channel" paths:

```python
# Step 1: Create invisible routing node in the inter-row gap
g.node('route_back', '', shape='point', width='0')

# Step 2: Route the loop-back through the invisible node
g.edge('dec1:w', 'route_back', label='否', constraint='false')
g.edge('route_back', 'earlier_step', constraint='false')
```

> **Principle**: Every horizontal edge segment travels in an inter-row safe channel. Never cut diagonally across boxes. See `references/shape-specs.md` § Arrow Routing Rule.

### Step 3: Render

```python
g.render('output', format='svg')  # also 'png', 'pdf'
```

Or specify engine: `g.render('output', format='svg', engine='neato')`.
Engines: `dot` / `neato` / `fdp` / `circo` / `twopi`.

🔴 **CHECKPOINT**: verify (a) no Python exception (b) output file > 0 bytes (c) opens correctly. Fail → see Failure Modes.

## Critical Rules

- `shape='box'` (**sharp**, NEVER rounded), B&W only, no color fills
- Flowchart: `rankdir='TB'`, box w/h ≥ 3:1, diamond w/h ≈ 2:1, flat ellipse start/end
- Block diagram: sensor=`style='solid'`, processor=`style='solid'`, storage=`style='dashed'`, decision=`style='dotted'`, output=`style='solid', penwidth='1.5'`
- Hierarchy: cluster border `style='dashed', penwidth='0.6'`, all component boxes `shape='box', style='solid'`
- Lines: `penwidth='0.6'` outlines, `penwidth='0.35'` lead lines
- Font: `fontsize='14'` box text, `fontsize='11'` labels
- Reference numbers **outside** boxes, thin dotted lead lines, `arrowhead='none'`
- `label='图1'`, `labelloc='b'` — no title on diagram

## 🛑 Pre-Submission Checklist (BLOCKING)

```
☐ 1. Black lines, 0.5–0.8pt          ☐ 7. No extra text outside boxes
☐ 2. Font ≥14pt                       ☐ 8. Lines don't cross boxes (safe channels)
☐ 3. DPI≥300, legible at 2/3 scale    ☐ 9. Consistent proportions
☐ 4. Arabic numbers, lead lines, outside  ☐ 10. No smudges
☐ 5. Lead lines clockwise, no cross    ☐ 11. B&W only, no color fills
☐ 6. "图1" below diagram              ☐ 12. Same component same number across figures
```

## 🚫 Anti-Patterns (DO NOT)

| # | Don't | Sev | Do instead |
|---|-------|:---:|------|
| 1 | Rounded corners | 🔴 | `shape='box'` |
| 2 | Lines >1.5pt | 🔴 | `penwidth='0.6'` |
| 3 | Arrows through boxes | 🔴 | Safe-channel routing |
| 4 | Numbers inside boxes | 🔴 | Outside + lead lines |
| 5 | Color fills | 🔴 | White fill, B&W |
| 6 | Title on diagram | 🟡 | Only `label='图1'` below |
| 7 | Lead lines cross | 🟡 | Clockwise, `constraint='false'` |
| 8 | Box w/h ≈ 1:1 | 🟡 | ≥ 3:1 via `width`/`height` |
| 9 | Tall diamond | 🟡 | Flat, w/h ≈ 2:1 |
| 10 | Gradients/shadows | 🟡 | Pure black lines |
| 11 | 是 exits left / 否 exits right | 🔴 | Port hints: `dec1:e` (是→right), `dec1:w` or `:s` (否→left/bottom) |
| 12 | Loop-back cuts through flow | 🔴 | Invisible intermediate node in safe channel (see Flowchart specifics) |
| 13 | Decision branches not labeled | 🟡 | Always `label='是'` / `label='否'` on decision edges |

## Failure Modes

| Symptom | First fix | Still failing? |
|---------|-----------|----------------|
| `graphviz.backend.ExecutableNotFound` | Install system Graphviz (see Dependencies) | https://graphviz.org/download/ |
| `graphviz` import error | `pip install graphviz` | Check Python environment |
| Syntax / attribute error | Check quotes, commas, `->` in edge calls | Simplify to minimal graph |
| Blank output | Verify `bgcolor='white'`, nodes have `label` | Try `format='png'` |
| Chinese garbled | `fontname='Microsoft YaHei'` (Win) / `fontname='WenQuanYi Micro Hei'` (Linux) | Fall back to English labels |
| Lead lines overlap | `constraint='false'`, `weight='0'` | Use invisible intermediate nodes for routing; last resort: manual editing |
| Output file too large | PNG: reduce DPI; SVG: simplify nodes | Split into sub-figures |
| Cluster disappears (hierarchy) | Set `newrank='true'` in `graph_attr` | Replace `rank='same'` inside clusters with `style='invis'` edges (see shape-specs.md § Hierarchy) |
| Decision branch exits wrong side | Set `splines='polyline'`; add port hints `:e`/`:w` on edges | Route through invisible intermediate nodes placed beside diamond |

## References

- `references/shape-specs.md` — flowchart, block diagram & hierarchy shape tables, layout rules, arrow routing
- `references/patent-standards.md` — USPTO/CNIPA paper, margin, font, line specs, output formats
- `references/numbering.md` — numbering conventions, lead line specs, Python implementation, examples
- `assets/flowchart-skeleton.py` — copy-paste flowchart template
- `assets/block-diagram-skeleton.py` — copy-paste block diagram template
- `assets/hierarchy-skeleton.py` — copy-paste hierarchy/architecture template

