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

| User says | Type | Direction | Node shapes |
|-----------|------|-----------|-------------|
| 流程图/方法/flowchart | **Flowchart** | `rankdir='TB'` | ellipse → box → diamond → ellipse |
| 框图/系统/block diagram | **Block Diagram** | `rankdir='TB'` | All `shape='box'` |
| 架构/层级/hierarchy | **Hierarchy** | `rankdir='TB'` or `'LR'` | `shape='box'`, `rank='same'` |

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
g.attr(label='图1', labelloc='b', fontsize='12')

# Example: box + lead-line reference number
g.node('cpu', 'Processor', shape='box')
g.node('r10', '10', shape='plaintext', fontsize='11')
g.edge('r10', 'cpu', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
```

Skeletons: `assets/flowchart-skeleton.py`, `assets/block-diagram-skeleton.py`.

### Step 3: Render

```python
g.render('output', format='svg')  # also 'png', 'pdf'
```

Or specify engine: `g.render('output', format='svg', engine='neato')`.
Engines: `dot` / `neato` / `fdp` / `circo` / `twopi`.

🔴 **CHECKPOINT**: verify (a) no Python exception (b) output file > 0 bytes (c) opens correctly. Fail → see Failure Modes.

### Step 4: Checklist

🛑 **STOP · BLOCKING GATE**: run 12-item checklist below. **Do NOT deliver until all pass.**

## Critical Rules

- `shape='box'` (**sharp**, NEVER rounded), B&W only, no color fills
- Flowchart: `rankdir='TB'`, box w/h ≥ 3:1, diamond w/h ≈ 2:1, flat ellipse start/end
- Block diagram: sensor=`style='solid'`, processor=`style='solid'`, storage=`style='dashed'`, decision=`style='dotted'`, output=`style='solid', penwidth='1.5'`
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

## Failure Modes

| Symptom | First fix | Still failing? |
|---------|-----------|----------------|
| `graphviz.backend.ExecutableNotFound` | Install system Graphviz (see Dependencies) | https://graphviz.org/download/ |
| `graphviz` import error | `pip install graphviz` | Check Python environment |
| Syntax / attribute error | Check quotes, commas, `->` in edge calls | Simplify to minimal graph |
| Blank output | Verify `bgcolor='white'`, nodes have `label` | Try `format='png'` |
| Chinese garbled | `fontname='Microsoft YaHei'` (Win) / `fontname='WenQuanYi Micro Hei'` (Linux) | Fall back to English labels |
| Lead lines overlap | `constraint='false'`, `weight='0'` | Note: manual editing in vector editor |
| Output file too large | PNG: reduce DPI; SVG: simplify nodes | Split into sub-figures |

## References

- `references/shape-specs.md` — flowchart & block diagram shape tables, layout rules, arrow routing
- `references/patent-standards.md` — USPTO/CNIPA paper, margin, font, line specs, output formats
- `references/numbering.md` — numbering conventions, lead line specs, Python implementation, examples
- `assets/flowchart-skeleton.py` — copy-paste flowchart template
- `assets/block-diagram-skeleton.py` — copy-paste block diagram template
- `assets/examples/` — 5 complete patent diagram scripts covering typical scenarios
