---
name: patent-figforge
description: Create patent-style technical diagrams including flowcharts, block diagrams, and system architectures using Graphviz with reference numbering. 触发词：专利附图、流程图、框图、架构图、reference numbers、patent figures、专利图、方法流程图、系统框图
---

# Patent Diagram Generator Skill

Create patent-style technical diagrams including flowcharts, block diagrams, and system architectures using Graphviz.

## When to Use

Invoke this skill when users ask to:
- Create flowcharts for method claims
- Generate block diagrams for system claims
- Draw system architecture diagrams
- Create technical illustrations for patents
- Add reference numbers to diagrams
- Generate patent figures

## What This Skill Does

1. **Flowchart Generation**:
   - Method step flowcharts
   - Decision trees
   - Process flows with branches
   - Patent-style step numbering

2. **Block Diagram Creation**:
   - System component diagrams
   - Hardware architecture diagrams
   - Software module diagrams
   - Component interconnections

3. **Custom Diagram Rendering**:
   - Render Graphviz DOT code
   - Support multiple formats (SVG, PNG, PDF)
   - Multiple layout engines (dot, neato, fdp, circo, twopi)

4. **Patent-Style Formatting**:
   - Add reference numbers (10, 20, 30, etc.)
   - Use clear labels and connections
   - Professional formatting for USPTO filing

## Required Dependencies

This skill requires Graphviz to be installed:

**Windows**:
```bash
choco install graphviz
```

**Linux**:
```bash
sudo apt install graphviz
```

**Mac**:
```bash
brew install graphviz
```

**Python Package**:
```bash
pip install graphviz
```

## How to Use

When this skill is invoked:

1. **Load diagram generator** (self-locating: works in any runtime, no env var needed):
   ```python
   import os, sys
   # Resolve skill root = the folder containing this SKILL.md (parent of python/).
   # Walk up from CWD or __file__ until we find python/diagram_generator.py.
   _SKILL_ROOT = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
   for _candidate in (_SKILL_ROOT, os.getcwd(), r"c:\AI\.github\skills\patent-figforge"):
       if os.path.exists(os.path.join(_candidate, "python", "diagram_generator.py")):
           _SKILL_ROOT = _candidate
           break
   sys.path.insert(0, _SKILL_ROOT)
   from python.diagram_generator import PatentDiagramGenerator

   # Ensure Graphviz `dot` is on PATH (it ships NOT on PATH by default on Windows).
   for _dot_dir in (r"C:\Program Files\Graphviz\bin", r"/usr/bin", "/usr/local/bin"):
       if os.path.exists(os.path.join(_dot_dir, "dot.exe")) or os.path.exists(os.path.join(_dot_dir, "dot")):
           os.environ["PATH"] = _dot_dir + os.pathsep + os.environ.get("PATH", "")
           break

   generator = PatentDiagramGenerator(output_dir=".")
   ```

2. **Create flowchart** from steps:
   ```python
   steps = [
       {"id": "start", "label": "Start", "shape": "ellipse", "next": ["step1"]},
       {"id": "step1", "label": "Initialize System", "shape": "box", "next": ["decision"]},
       {"id": "decision", "label": "Is Valid?", "shape": "diamond", "next": ["step2", "error"]},
       {"id": "step2", "label": "Process Data", "shape": "box", "next": ["end"]},
       {"id": "error", "label": "Handle Error", "shape": "box", "next": ["end"]},
       {"id": "end", "label": "End", "shape": "ellipse", "next": []}
   ]

   diagram_path = generator.create_flowchart(
       steps=steps,
       filename="method_flowchart",
       output_format="svg"
   )
   ```

3. **Create block diagram**:
   ```python
   blocks = [
       {"id": "input", "label": "Input\\nSensor", "type": "input"},
       {"id": "cpu", "label": "Central\\nProcessor", "type": "process"},
       {"id": "memory", "label": "Memory\\nStorage", "type": "storage"},
       {"id": "output", "label": "Output\\nDisplay", "type": "output"}
   ]

   connections = [
       ["input", "cpu", "raw data"],
       ["cpu", "memory", "store"],
       ["memory", "cpu", "retrieve"],
       ["cpu", "output", "processed data"]
   ]

   diagram_path = generator.create_block_diagram(
       blocks=blocks,
       connections=connections,
       filename="system_diagram",
       output_format="svg"
   )
   ```

4. **Render custom DOT code**:
   ```python
   dot_code = """
   digraph PatentSystem {
       rankdir=LR;
       node [shape=box, style=rounded];

       Input [label="User Input\\n(10)"];
       Processor [label="Processing Unit\\n(20)"];
       Output [label="Display\\n(30)"];

       Input -> Processor [label="data"];
       Processor -> Output [label="result"];
   }
   """

   diagram_path = generator.render_dot_diagram(
       dot_code=dot_code,
       filename="custom_diagram",
       output_format="svg",
       engine="dot"
   )
   ```

5. **Add reference numbers**:
   ```python
   # After creating a diagram, add patent-style reference numbers
   reference_map = {
       "Input Sensor": 10,
       "Central Processor": 20,
       "Memory Storage": 30,
       "Output Display": 40
   }

   annotated_path = generator.add_reference_numbers(
       svg_path=diagram_path,
       reference_map=reference_map
   )
   ```

## Diagram Templates

Get common templates:
```python
templates = generator.get_diagram_templates()

# Available templates:
# - simple_flowchart: Basic process flow
# - system_block: System architecture
# - method_steps: Sequential method
# - component_hierarchy: Hierarchical structure
```

## Shape Types

### Flowchart Shapes
- `ellipse`: Start/End points
- `box`: Process steps
- `diamond`: Decision points
- `parallelogram`: Input/Output operations
- `cylinder`: Database/Storage

### Block Diagram Types
- `input`: Input devices/sensors
- `output`: Output devices/displays
- `process`: Processing units
- `storage`: Memory/storage
- `decision`: Control logic
- `default`: General components

## Layout Engines

- `dot`: Hierarchical (top-down/left-right)
- `neato`: Spring model layout
- `fdp`: Force-directed layout
- `circo`: Circular layout
- `twopi`: Radial layout

## Output Formats

- `svg`: Scalable Vector Graphics (best for editing)
- `png`: Raster image (good for viewing)
- `pdf`: Portable Document Format (USPTO compatible)

## Patent-Style Reference Numbers

Convention:
- Main components: 10, 20, 30, 40, ...
- Sub-components: 12, 14, 16 (under 10)
- Elements: 22, 24, 26 (under 20)

Example labeling:
```
"Input Sensor (10)"
"  - Detector Element (12)"
"  - Signal Processor (14)"
"Central Unit (20)"
"  - CPU Core (22)"
"  - Cache (24)"
```

## Workflow (gated)

Each 🔴 is a blocking gate — do not proceed until it passes.

**🔴 GATE 1 · Plan & confirm** (before generating any code):
- List the nodes/blocks, the edges, the `rankdir` (TB for method flowcharts, LR for system blocks), and the intended reference-number assignment aloud.
- State how many independent reference numbers the figure needs. If **>3** with lead lines → STOP, tell the user you will split into multiple figures (Anti-Pattern #3).
- Confirm with the user before rendering if the structure is non-trivial (≥8 nodes, decision branches, or loop-back edges).

**Step 2 · Generate**: run the import recipe + the chosen API method (`create_flowchart` / `create_block_diagram` / `render_dot_diagram`). Use in-label `ref=` for reference numbers (Anti-Pattern #6).

**🔴 GATE 2 · Render sanity** (after `_render` returns):
- Confirm the SVG file exists and is non-empty (size > 500 bytes — a tofu/empty render is typically <200 bytes).
- Confirm Chinese labels are present in the SVG source (grep one label, e.g. `Select-String start.svg -Pattern "开始"`). Garbled/`???`/tofu here = fontconfig failed → Failure Mode row 3.

**🔴 GATE 3 · view_image verification** (MANDATORY before declaring done):
- **Render a PNG** of the figure by calling the API with `output_format="png"` (graphviz renders PNG directly and reliably — same `format=` switch as SVG; if SVG works, PNG works). Then **open the PNG with the `view_image` tool** to visually inspect. Note: `view_image` only accepts raster formats — SVG cannot be inspected this way, so produce a PNG for the visual gate even though SVG remains the primary deliverable.
- Do NOT declare success based on "the file exists" alone.
- Verify in the image: (a) Chinese glyphs render (no □□□/tofu), (b) edges don't cross except intentional branches, (c) reference numbers are legible, (d) no color (black on white). If any fail → fix and re-render before proceeding.
- This gate exists because graphviz auto-layout can produce geometrically broken output (crossing lead lines, overlapping labels) that a file-size check will not catch.

**Step 4 · Report**: show the file path and list the reference numbers used:
   ```
   Diagram created: ./method_flowchart.svg
   Reference Numbers:
   - 开始/Start (10)
   - 采样 Sample (20)
   - 判定 Decide (30)
   ```
🛑 **STOP**: present the verified figure to the user. Do not auto-generate additional figures or modify claims text without confirmation.

## Common Use Cases

1. **Method Claims** → Flowcharts
   - Show sequential steps
   - Include decision branches
   - Number steps (S1, S2, S3...)

2. **System Claims** → Block Diagrams
   - Show components and connections
   - Use reference numbers
   - Indicate data flow directions

3. **Architecture Diagrams** → Custom DOT
   - Complex system layouts
   - Multiple interconnections
   - Hierarchical structures

## Failure Modes

When a render fails, diagnose by symptom → fix per the table. Each row is an explicit
"if X fails → Y" branch, not a generic suggestion.

| Symptom | Root cause | Fix |
|---|---|---|
| `ExecutableNotFound: failed to execute WindowsPath('dot')` | Graphviz `dot` not on PATH (common on Windows — installer does not add it) | The import recipe already probes `C:\Program Files\Graphviz\bin`. If still failing, run `dot -V`; if not found, install (`choco install graphviz` Windows / `brew install graphviz` Mac / `apt install graphviz` Linux) and re-run. |
| `FileNotFoundError: ... python/diagram_generator.py` | SKILL root not resolved (import recipe walked up but did not find the module) | Hardcode `_SKILL_ROOT = r"<absolute path to patent-figforge folder>"` as a last-resort override at the top of the recipe. |
| Chinese renders as tofu □□□ / `???` / empty boxes in SVG/PNG | Fontconfig cannot resolve a CJK family (no fonts.conf mapping) | `_resolve_cjk_font()` auto-writes a fonts.conf on Windows. If still garbled: confirm a candidate font exists (`Test-Path C:\Windows\Fonts\simhei.ttf`) and that `FONTCONFIG_FILE` points at the written conf. On Linux install `fonts-noto-cjk`. |
| Edge labels (是/否/data) disappear | `splines="ortho"` silently drops edge labels (Graphviz known limitation) | Use `splines="polyline"` (already the skill default). Do NOT switch to `"ortho"`. |
| `cairosvg` / `OSError: no library 'cairo-2'` when converting SVG→PNG via a **post-processing** library | This is a **separate** Python library (`cairosvg`), NOT Graphviz's own renderer. It needs a system `libcairo` that stock Windows lacks. | Do NOT use `cairosvg`. For PNG, use **Graphviz directly** (`output_format="png"` on the API, or `dot -Tpng`) — its built-in cairo backend works on stock Windows (verified: graphviz 15.1.0 renders PNG in <0.5s, 5500–7700B). SVG and PNG are the same `format=` switch; if SVG works, PNG works. |
| Lead lines (reference-number dotted edges) cross each other | More than ~3 independent reference-number annotations on one figure; graphviz auto-layout cannot route them cleanly | Keep **≤ 2–3 reference numbers per figure** (USPTO/CNIPA convention). For more, split into multiple figures. Prefer in-label `ref=` over post-hoc `add_reference_numbers` lead lines. |
| Output file very large / render slow | Hundreds of nodes in one diagram | Split into sub-figures or use `rankdir=LR` with subgraph clustering. One figure per independent claim element. |

## 🚫 Anti-Patterns & Blacklist

Hard prohibitions — violating any one makes the figure non-compliant or unusable.

| # | ❌ Don't | Why | ✅ Do instead |
|---|---|---|---|
| 1 | Use **color** (red/green/blue fills or strokes) | 37 CFR §1.84(a)(1) + CNIPA: **black ink on white only**; color figures are rejected | `bgcolor="white"`, `fillcolor="white"`, default black strokes. No `color=` attribute. |
| 2 | Use **curved** splines (`splines="curved"`/`"spline"`) | Patent figures must be reproducible line drawings; curves overlap and are hard to read | `splines="polyline"` (orthogonal, sharp). |
| 3 | Add **>3 reference numbers** with lead lines to one figure | Graphviz cannot route that many lead lines without crossing → §1.84(q) violation (no crossing lead lines) | ≤2–3 ref numbers per figure; split excess into a second figure. |
| 4 | **Duplicate** a reference number across different elements | CNIPA/USPTO: each number denotes exactly ONE element; duplicates confuse the description | Each `ref` value unique within the figure. Reuse a number only for the same element across figures. |
| 5 | Use `splines="ortho"` for diagrams with edge labels | `ortho` silently drops edge labels (是/否/data vanish) | `splines="polyline"` — keeps labels, stays orthogonal. |
| 6 | Use `add_reference_numbers` (post-hoc SVG injection) for new figures | Brittle string matching on SVG `<text>`; lead lines cross (see Failure Mode row 6) | Use the in-label `ref=` parameter on the node/block dict — clean, no lead lines. |
| 7 | Raster output (PNG) as the **primary** deliverable | Not editable; §1.84 prefers reproducible vector | Primary = **SVG** (editable) + **PDF** (filing). PNG is fine as preview and for `view_image` verification — graphviz renders it directly and reliably (verified <0.5s on stock Windows). |
| 8 | Set `fontsize` < 14 on reference numbers | §1.84(p)(3): figure text must be ≥ ~14pt for legibility | Default `fontsize="14"` (graph/node); `13` only for diamond decision nodes (narrow). |
| 9 | Omit the figure entirely and describe it in prose | A picture is required for system/method claims with multiple components | Always emit an SVG + PDF. |
| 10 | Mix `rankdir` mid-diagram via subgraphs | Breaks the single主流向 (main-flow) direction, causes routing chaos | One `rankdir` per figure (TB for method flowcharts, LR for system block diagrams). |

## Tools Available

- **Bash**: To run Python diagram generation
- **Write**: To save DOT code or diagrams
- **Read**: To load existing diagrams or templates
