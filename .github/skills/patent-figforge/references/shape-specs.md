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
