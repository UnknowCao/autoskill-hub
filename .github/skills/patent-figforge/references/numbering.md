# Reference Numbers & Lead Lines

Lead lines connect reference numbers to components — the defining feature that distinguishes patent figures from ordinary diagrams.

## Numbering Convention

### Hierarchical encoding (recommended)

- `100` — Overall system
  - `110` — Subsystem A
    - `111` — Component A1
    - `112` — Component A2
  - `120` — Subsystem B
    - `121` — Component B1

### Linear encoding (simple diagrams)

- `10, 20, 30, 40...` — Main components
- `12, 14, 16...` — Sub-components of 10
- `22, 24, 26...` — Sub-components of 20

### Rules

- Reference numbers are Arabic numerals
- Maximum **4 digits** (longer reduces readability)
- Same component gets same number across all figures in the document

## Lead Line Specs

| Spec | Requirement |
|------|-------------|
| Position | **Outside** the box — numbers never inside boxes |
| Length | Moderate, ≤ 1.5× box height |
| Arrangement | **Clockwise** (conforms to reading habit) |
| Crossing | **Must not cross** |
| Style | Curved preferred (distinguishes from main lines) |
| Width | **0.3–0.4pt**, visibly thinner than shape outlines |
| Number position | At end of lead line, outside box |

### Correct vs Wrong

> **❌ WRONG**: Number `110` written inside the component label — violates patent convention.
> 
> **✅ CORRECT**: Number `110` placed outside the box, connected by a thin (0.35pt) dotted lead line.

In Python:

```python
# ❌ WRONG — number crammed inside label:
g.node('c', 'Component\n(110)')   # bad: "110" is part of box content

# ✅ CORRECT — number as separate node, lead line outside:
g.node('component', 'Component', shape='box')
g.node('r10', '110', shape='plaintext', fontsize='11')
g.edge('r10', 'component', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
```

### Python Implementation

```python
import graphviz

g = graphviz.Digraph()
# ... setup graph_attr, node_attr ...

# Reference numbers as plaintext nodes
g.node('r10', '10', shape='plaintext', fontsize='11')

# Invisible edges for alignment
g.edge('r10', 'component_node', style='invis')
# Group same rank
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('r10')
    s.node('component_node')

# Lead lines: thin, dotted, no arrowhead, constraint=false
g.edge('r10', 'component_node', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false', color='black')
```

### Example Labeling

```
Input Sensor (10)
  - Detector Element (12)
  - Signal Processor (14)
Central Unit (20)
  - CPU Core (22)
  - Cache (24)
```
