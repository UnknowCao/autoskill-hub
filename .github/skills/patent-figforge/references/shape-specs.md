# Shape Specifications — Patent Figure Shapes

## Flowchart Shapes

| Shape | Patent use | Graphviz | Key rule |
|-------|-----------|----------|----------|
| Ellipse | Start/End | `shape=ellipse` | **Flat oval**, not circle |
| Box (rectangle) | Process step | `shape=box` | **w/h ≥ 3:1** (patent convention), sharp corners |
| Diamond | Decision branch | `shape=diamond` | **Flat diamond** (w/h ≈ 2:1) |
| Parallelogram | Data I/O | `shape=parallelogram` | Slant 10–15° |
| Double box | Subroutine/DB | `shape=box, peripheries=2` | Outer+inner border |
| Cylinder | Database/storage | `shape=cylinder` | — |

**Critical prohibitions**: rounded corners, gradients, shadows, color fills. See `🚫 反例与黑名单` in SKILL.md.

## Flowchart Layout

- Vertical (top-to-bottom), `rankdir=TB`
- Same-level nodes center-aligned
- Inter-row spacing ≥ 2× node height
- Decision exits: Yes→diamond right tip, No→diamond left tip
- Arrow path: vertical segment → horizontal segment (in inter-row gap) → vertical segment

### Arrow Routing Rule

Horizontal segments must travel in inter-row "safe channels" (lane gaps). **Never** pass through any box boundary.

> **❌ WRONG**: Arrow A→C cuts diagonally through box B — fatal drafting error.
> 
> **✅ RIGHT**: Arrow exits A bottom → travels horizontally in row gap → enters C top. All segments stay in safe channels.

In Python, use `splines='ortho'` or `splines='polyline'` and avoid port constraints that force cross-box routing:

```python
# WRONG — don't do this:
g.edge('A', 'C')  # if A and C are separated by B in rank, arrow crosses B

# RIGHT — route through intermediate nodes:
g.edge('A', 'B')
g.edge('B', 'C')  # explicit safe-channel path
```

## Block Diagram Types

| Component type | Border style | Graphviz |
|----------------|-------------|----------|
| Sensor/Input | Solid (─) | `style=solid` |
| Processor/Controller | Solid (─), standard width | `style=solid` |
| Memory/Storage | Dashed (--) | `style=dashed` |
| Decision logic | Dotted (-·-) | `style=dotted` |
| Output/Display | Solid (─), bold | `style=solid, penwidth=1.5` |

## Block Diagram Layout

- Grid 2–3 columns
- Same-row boxes top/bottom aligned, equal width
- Leave "safe channels" (lanes) between rows for horizontal connections
- All horizontal lines in safe channels (midpoint Y between rows)
- Vertical lines exit directly from box edge anchor points

## Hierarchy / Architecture Layout

Hierarchy diagrams show layered system architectures (感知层→决策层→执行层).

### Layer Grouping

Use `subgraph cluster_*` to group components within each layer. Set `newrank='true'` in `graph_attr` to prevent rank/cluster conflicts:

```python
g = graphviz.Digraph(
    graph_attr={'rankdir': 'TB', 'newrank': 'true', ...},
    ...
)

with g.subgraph(name='cluster_L1') as c:
    c.attr(label='感知层', labeljust='l', fontsize='13',
           style='dashed', color='black', penwidth='0.6')
    c.node('sensor', '传感器')
    c.node('daq', '数据采集')
```

### ⚠️ CRITICAL: Do NOT mix rank='same' subgraphs with cluster subgraphs

Graphviz will silently drop clusters when both `rank='same'` and `subgraph cluster_*` are used on the same nodes. Use **invisible edges** for intra-layer alignment instead:

```python
# ✅ RIGHT — invisible edge for alignment:
g.edge('sensor', 'daq', style='invis')

# ❌ WRONG — will break clusters:
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('sensor')
    s.node('daq')
# ... inside a cluster, this causes "was already in a rankset" warning
```

`rank='same'` subgraphs are still safe for **reference number alignment outside clusters** (see `assets/hierarchy-skeleton.py`).

### Layer Label Convention

| Property | Value | Notes |
|----------|-------|-------|
| Position | Top-left of cluster | `labeljust='l'` |
| Font size | 13pt | Slightly smaller than box text (14pt) |
| Border style | Dashed (`style='dashed'`) | Distinguishes layer grouping from component borders |
| Pen width | 0.6pt | Same as component outlines |

### Inter-Layer Connections

- Arrows flow top→bottom following `rankdir='TB'`
- Each arrow connects specific components across layers (not layer-to-layer)
- Edge labels describe data/control flow (Chinese for CNIPA, English for USPTO)
- **Minimum 2 rows of vertical space between layers** for arrow routing clearance
- Avoid diagonal arrows that cross multiple layer boundaries without a clear path

### Hierarchy-Specific Prohibitions

| # | Don't | Do instead |
|---|-------|------|
| 1 | Mix rank='same' + cluster on same nodes | `newrank='true'` + invisible edges |
| 2 | Skip layer labels | Every cluster gets `label='层名'` |
| 3 | Arrows that skip layers (L1→L3 directly) | Route through intermediate layer |
| 4 | Inconsistent intra-layer node widths | Same `width`/`height` for all nodes in a layer |
