# Code Templates — 专利附图 Python Graphviz 代码模板

> Copy-paste ready templates for each figure type. All templates comply with SKILL.md axioms + §1.84.
> Use with `references/numbering.md` §6 for reference-number helpers.

---

## Universal Patent-Grade Attributes

Copy this block as the foundation for any patent figure:

```python
import os, graphviz

os.environ["PATH"] = r"C:\Program Files\Graphviz\bin;" + os.environ.get("PATH", "")

# ═══ Universal patent-grade attributes ═══
GRAPH_BASE = {
    'bgcolor': 'white', 'fontname': 'Microsoft YaHei',  # CNIPA. USPTO → 'Arial'
    'dpi': '300',               # §1.84(k): survives 2/3 reduction
    'margin': '1.0',            # §1.84(g): ≥2.5cm top/left
    'splines': 'polyline',      # Axiom 1: orthogonal-capable (NOT 'ortho')
    'nodesep': '0.6',           # Axiom 3: channel whitespace
    'ranksep': '0.8',           # Axiom 3: inter-row channel
}
NODE_BASE = {
    'fontname': 'Microsoft YaHei', 'fontsize': '14',   # §1.84(p)(3): ≥0.32cm
    'fontcolor': 'black', 'color': 'black', 'penwidth': '0.8',
    'shape': 'box', 'style': 'solid',  # sharp corners (§1.84, CNIPA)
    'width': '2.2', 'height': '0.8', 'fixedsize': 'true',  # equal-size nodes
}
EDGE_BASE = {
    'fontname': 'Microsoft YaHei', 'fontsize': '12',
    'fontcolor': 'black', 'color': 'black', 'penwidth': '0.8',
}
```

> 🔀 **USPTO variant**: `fontname='Arial'`, `label='FIG. 1'`, English labels. See `references/requirements-uspto-only.md`.

---

## Reference-Number Helpers (Axiom 4)

```python
def _rankdir(g):
    """Read rankdir from graph attrs (default TB)."""
    try:
        rd = g.graph_attr['rankdir']
        return rd if isinstance(rd, str) else 'TB'
    except Exception:
        return 'TB'


def add_ref_horizontal(g, rid, target, label, side='right'):
    """0° horizontal lead. Ref beside target on the SAME ROW.

    Rankdir-aware: works correctly in BOTH TB and LR modes.
      - TB mode: uses `rank='same'` to keep ref on the same row
      - LR mode: uses constraint-edge to place ref in adjacent rank
    """
    g.node(rid, label, shape='plaintext', fontsize='14',
           fontname='Microsoft YaHei', fontcolor='black')
    if _rankdir(g) == 'TB':
        spacer = rid + '_sp'
        g.node(spacer, '', shape='point', width='0.05')
        with g.subgraph() as s:
            s.attr(rank='same')
            if side == 'right':
                s.node(target); s.node(rid); s.node(spacer)
            else:
                s.node(spacer); s.node(rid); s.node(target)
        if side == 'right':
            g.edge(target, rid, style='dotted', penwidth='0.5', arrowhead='none',
                   weight='10', constraint='false', tailport='e', headport='w')
            g.edge(rid, spacer, style='invis', weight='10')
        else:
            g.edge(spacer, rid, style='invis', weight='10')
            g.edge(rid, target, style='dotted', penwidth='0.5', arrowhead='none',
                   weight='10', constraint='false', tailport='e', headport='w')
    else:  # LR
        if side == 'right':
            g.edge(target, rid, style='dotted', penwidth='0.5', arrowhead='none',
                   weight='10', constraint='true', tailport='e', headport='w')
        else:
            g.edge(rid, target, style='dotted', penwidth='0.5', arrowhead='none',
                   weight='10', constraint='true', tailport='e', headport='w')


def add_ref_vertical(g, rid, target, label, side='bottom'):
    """90° vertical lead. Ref above/below target.

    Rankdir-aware: works correctly in BOTH TB and LR modes.
      - LR mode: uses `rank='same'` (which in LR = same column = vertical)
      - TB mode: uses constraint-edge to place ref in adjacent rank
    """
    g.node(rid, label, shape='plaintext', fontsize='14',
           fontname='Microsoft YaHei', fontcolor='black')
    if _rankdir(g) == 'LR':
        spacer = rid + '_sp'
        g.node(spacer, '', shape='point', width='0.05')
        with g.subgraph() as s:
            s.attr(rank='same')
            if side == 'bottom':
                s.node(target); s.node(rid); s.node(spacer)
            else:
                s.node(spacer); s.node(rid); s.node(target)
        if side == 'bottom':
            g.edge(target, rid, style='dotted', penwidth='0.5', arrowhead='none',
                   weight='10', constraint='false', tailport='s', headport='n')
            g.edge(rid, spacer, style='invis', weight='10')
        else:
            g.edge(spacer, rid, style='invis', weight='10')
            g.edge(rid, target, style='dotted', penwidth='0.5', arrowhead='none',
                   weight='10', constraint='false', tailport='s', headport='n')
    else:  # TB
        if side == 'bottom':
            g.edge(target, rid, style='dotted', penwidth='0.5', arrowhead='none',
                   weight='10', constraint='true', tailport='s', headport='n')
        else:
            g.edge(rid, target, style='dotted', penwidth='0.5', arrowhead='none',
                   weight='10', constraint='true', tailport='s', headport='n')


# ── Back-compat aliases (existing templates call these) ─────────────────────
# ⚠️ Note: add_ref_top/bottom in old code used `rank='same'` which produced
#    HORIZONTAL leads (bug). The aliases below now route to the CORRECT
#    vertical helper. To get the OLD (buggy) horizontal behavior, use
#    add_ref_horizontal instead. See CHANGELOG note in numbering.md §6.
def add_ref_right(g, rid, target, label):
    """Back-compat alias for add_ref_horizontal(side='right')."""
    add_ref_horizontal(g, rid, target, label, side='right')


def add_ref_left(g, rid, target, label):
    """Back-compat alias for add_ref_horizontal(side='left')."""
    add_ref_horizontal(g, rid, target, label, side='left')


def add_ref_top(g, rid, target, label):
    """Back-compat alias for add_ref_vertical(side='top').

    🔴 FIXED (R5, 2026-07-23): old implementation used `rank='same'` which
    produced HORIZONTAL leads (90° rotation bug). Now correctly vertical."""
    add_ref_vertical(g, rid, target, label, side='top')


def add_ref_bottom(g, rid, target, label):
    """Back-compat alias for add_ref_vertical(side='bottom').

    🔴 FIXED (R5, 2026-07-23): same bug as add_ref_top — now correctly vertical."""
    add_ref_vertical(g, rid, target, label, side='bottom')
```

> 📋 **Helper selection cheat-sheet** (rankdir-aware):
>
> | Want lead direction | Helper | Native mode | Also works in |
> |---|---|---|---|
> | Horizontal (0°) | `add_ref_horizontal` | TB | LR (via constraint) |
> | Vertical (90°) | `add_ref_vertical` | LR | TB (via constraint) |
>
> **Rule of thumb**: in TB figures (flowchart, hierarchy) refs go LEFT/RIGHT of node; in LR figures (block diagram, schematic) refs go ABOVE/BELOW. Pick the helper matching the lead direction you want — the helper handles rankdir internally.
>
> See `references/numbering.md` §6 for the geometry rationale + `add_ref_angled()` (non-orthogonal angles for special cases).

---

## Template 1: Flowchart (流程图)

```python
g = graphviz.Digraph(name='FIG1',
    graph_attr={**GRAPH_BASE, 'rankdir': 'TB'},
    node_attr=NODE_BASE, edge_attr=EDGE_BASE)
g.attr(label='图1', labelloc='b', fontsize='14')

# Main flow (high weight keeps vertical straight)
g.edge('start', 's10', weight='100')
g.edge('s10', 's20', weight='100')

# Decision: 是→right (:e), 否→left (:w) — ISO 5807
g.edge('dec', 's40', label='是', tailport='e')
g.edge('dec', 's50', label='否', tailport='w')

# Loop-back: anchor s50 to dec's rank, force s50 LEFT
with g.subgraph() as s:
    s.attr(rank='same'); s.node('s50'); s.node('dec')
g.edge('s50', 'dec', style='invis', weight='10', constraint='true')
g.edge('dec', 's50', tailport='w', headport='n', constraint='false')
g.edge('s50', 's20', headport='w', constraint='false')

# Refs on RIGHT (loop-back is left)
add_ref_right(g, 'r10', 's10', '10')
add_ref_right(g, 'r30', 's30', '30')

g.render('output', format='svg')
g.render('output', format='png')
```

---

## Template 2: Block Diagram (系统框图)

```python
g = graphviz.Digraph(name='FIG1',
    graph_attr={**GRAPH_BASE, 'rankdir': 'LR'},  # horizontal signal flow
    node_attr=NODE_BASE, edge_attr=EDGE_BASE)
g.attr(label='图1', labelloc='b', fontsize='14')

# Main signal flow (horizontal, left→right)
g.edge('v_sens', 'afe', weight='100')
g.edge('afe', 'mcu', label='采样数据', weight='100')
g.edge('mcu', 'comm', label='状态', weight='100')
g.edge('comm', 'vcu', label='CAN', weight='100')

# Auxiliary components hang BELOW main axis
g.edge('mcu', 'mem', label='存储', tailport='s')
g.edge('mcu', 'prot', label='保护', tailport='s')

# Reference numbers (right side, 2–3 only)
add_ref_right(g, 'r110', 'v_sens', '110')
add_ref_right(g, 'r220', 'mcu', '220')

g.render('output', format='svg')
g.render('output', format='png')
```

---

## Template 3: Hierarchy (层级架构图)

```python
g = graphviz.Digraph(name='FIG1',
    graph_attr={**GRAPH_BASE, 'rankdir': 'TB', 'newrank': 'true'},
    node_attr=NODE_BASE, edge_attr=EDGE_BASE)
g.attr(label='图1', labelloc='b', fontsize='14')

with g.subgraph(name='cluster_L1') as c:
    c.attr(label='感知层', labeljust='l', fontsize='14',
           style='dashed', color='black', penwidth='0.8')
    c.node('cam', '摄像头'); c.node('radar', '毫米波雷达')
    c.edge('cam', 'radar', style='invis')  # alignment — NOT rank='same' in cluster!

with g.subgraph(name='cluster_L2') as c:
    c.attr(label='决策层', labeljust='l', fontsize='14',
           style='dashed', color='black', penwidth='0.8')
    c.node('fusion', '数据融合'); c.node('plan', '路径规划')

# Cross-layer vertical calls
g.edge('cam', 'fusion', label='图像', tailport='s', headport='n')
g.edge('radar', 'fusion', label='点云', tailport='s', headport='n')

# Refs on left side of key components
add_ref_left(g, 'r10', 'cam', '10')
add_ref_left(g, 'r20', 'fusion', '20')

g.render('output', format='svg')
g.render('output', format='png')
```

> ⚠️ **CRITICAL**: Do NOT use `rank='same'` subgraphs inside clusters — Graphviz silently drops clusters. Use `style='invis'` edges for intra-layer alignment.

---

## Template 4: Schematic (原理图)

```python
g = graphviz.Digraph(name='FIG1',
    graph_attr={**GRAPH_BASE, 'rankdir': 'LR'},  # causal chain left→right
    node_attr=NODE_BASE, edge_attr=EDGE_BASE)
g.attr(label='图1', labelloc='b', fontsize='14')

# Physical entities (use engineering symbols or annotated boxes)
g.node('bat', '电池\nV_bat [V]', shape='circle')
g.node('load', '负载\nI_load [A]', shape='box')
g.node('ctrl', 'C', shape='circle')  # controller

# Physical connection (solid, thick)
g.edge('bat', 'load', penwidth='0.8', label='I_bat [A]')

# Causal/signal lead (thin/dashed)
g.edge('bat', 'ctrl', style='dashed', penwidth='0.5', label='V_bat')

# Feedback lead (dashed, reverse direction)
g.edge('ctrl', 'load', style='dashed', penwidth='0.5', label='调整信号',
       tailport='s', headport='s', constraint='false')

# Reference numbers
add_ref_right(g, 'r10', 'bat', '10')
add_ref_right(g, 'r30', 'ctrl', '30')

g.render('output', format='svg')
g.render('output', format='png')
```

---

## Rendering & Verification

```python
# Render to SVG (vector, preferred for submission) and PNG (preview)
g.render('output', format='svg')
g.render('output', format='png')

# 🔴 CHECKPOINT: Open and visually inspect before claiming compliance.
# Verify: (a) no Python exception (b) file > 0 bytes
# (c) lead lines do NOT cross (d) loop-back does not cross main flow
# (e) every edge is orthogonal (no diagonals)
```

For full verification checklist, see SKILL.md §9 and `references/numbering.md` §7.
