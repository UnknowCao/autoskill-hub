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

```
WRONG (arrow through box):          RIGHT (safe channel):
┌───┐                               ┌───┐
│ A │──╲                             │ A │
└───┘   ╲  ← crosses B!            └─┬─┘
┌───┐     ╲                           │
│ B │──────▶ C                      ┌─▽─┐
└───┘                               │ B │────────▶ C
                                    └───┘
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
