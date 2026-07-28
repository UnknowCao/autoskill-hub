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
   - **Dual output: SVG + PNG** (every render emits both; SVG is the editable primary, PNG is the `view_image` verification gate). **PDF is NOT supported** — if filing requires PDF, convert the SVG externally (e.g. `rsvg-convert -f pdf in.svg -o out.pdf` or Inkscape CLI).
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

2. **Create flowchart** from steps. **Signature: `create_flowchart(steps, filename="flowchart", output_format="svg")`** — `rankdir` is **auto-applied as TB** (correct for method flowcharts per GATE 1); there is no `rankdir` argument. Each step's `next` entry accepts either a bare `str` (id only) **or** a dict with fields: `id` (required), `label` (edge text, e.g. `"是"`/`"否"`), `style` (`solid`|`dashed`|`dotted`, default `solid`), `constraint` (`"true"` default; set **`"false"` for loop-back / back-edges** so graphviz routes them as a back-arc outside the rank chain — prevents the back-edge from forcing rank reordering and from crossing the main flow). `constraint="false"` is a **layout tip**, not a compliance rule (no Anti-Pattern governs it); the relevant compliance defaults are `splines="polyline"` (Anti-Pattern #2/#5 fix) and `bgcolor="white"` (Anti-Pattern #1).
   ```python
   # A monitor-and-retry loop: the "No" branch loops back to step1 with
   # constraint="false" so graphviz routes it as a back-arc and the main
   # TB chain stays clean (no rank reordering, no crossing).
   steps = [
       {"id": "start", "label": "Start", "shape": "ellipse", "next": ["step1"]},
       {"id": "step1", "label": "Initialize System", "shape": "box", "next": ["decision"]},
       {"id": "decision", "label": "Is Valid?", "shape": "diamond", "next": [
           {"id": "step2", "label": "Yes"},
           # Back-edge: id points back to step1 (re-initialize on failure).
           {"id": "step1", "label": "No", "constraint": "false"},
       ]},
       {"id": "step2", "label": "Process Data", "shape": "box", "next": ["end"]},
       {"id": "end", "label": "End", "shape": "ellipse", "next": []}
   ]

   diagram_path = generator.create_flowchart(
       steps=steps,
       filename="method_flowchart",
       output_format="svg"   # always emits svg + png; see Step 3 note
   )
   ```

3. **Create block diagram**. **Signature: `create_block_diagram(blocks, connections, filename="block", output_format="svg", rankdir="LR", title="")`** — `rankdir` defaults to **LR** (correct for system block diagrams per GATE 1); pass `rankdir="TB"` only if you need a top-down component hierarchy. `title` renders an optional graph-level label above the diagram. (Note: the `type` field on each block dict — `input`/`output`/`process`/`storage`/`decision`/`default` — is **currently ignored by the renderer**; all blocks render as plain boxes per Anti-Pattern convention. It exists for forward-compat and template population.)
   ```python
   blocks = [
       {"id": "input", "label": "Input\\nSensor", "type": "input"},
       {"id": "cpu", "label": "Central\\nProcessor", "type": "process"},
       {"id": "memory", "label": "Memory\\nStorage", "type": "storage"},
       {"id": "output", "label": "Output\\nDisplay", "type": "output"}
   ]

   connections = [
       ["input", "cpu", "raw data"],       # [from, to, label?]
       ["cpu", "memory", "store"],         # optional 4th slot: style (solid|dashed|dotted)
       ["memory", "cpu", "retrieve"],
       ["cpu", "output", "processed data"]
   ]

   diagram_path = generator.create_block_diagram(
       blocks=blocks,
       connections=connections,
       filename="system_diagram",
       output_format="svg",
       rankdir="LR",        # explicit; matches GATE 1 rule "LR for system blocks"
       title=""              # optional graph-level label
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

**Reference numbers (in-label `ref=`)**: prefer the in-label `ref=` parameter on each node/block dict (e.g. `{"id": "cpu", "label": "处理器", "ref": 20}`) — it appends `(20)` cleanly with no lead lines. The post-hoc `add_reference_numbers()` API exists for editing existing SVGs but is discouraged for new figures (Anti-Pattern #6).

**Numbering convention**: main components 10/20/30/40…; sub-components 12/14/16 under 10; elements 22/24/26 under 20. Each number denotes exactly ONE element (no duplicates within a figure; reusing a number across figures is OK only for the same element).

## Shape / Engine / Format quick reference

- **Flowchart shapes**: `ellipse` (start/end), `box` (process), `diamond` (decision), `parallelogram` (I/O), `cylinder` (DB). **Block types** (documentation only): `input`/`output`/`process`/`storage`/`decision`/`default` — all render as `box`.
- **Layout engines**: `dot` (hierarchical — default for patents), `neato`, `fdp`, `circo`, `twopi`.
- **Output formats**: **dual-output is automatic** — every render (`create_flowchart` / `create_block_diagram` / `render_dot_diagram`) emits BOTH `.svg` (primary, editable, the patent filing vector source) AND `.png` (for the `view_image` verification gate + docx/pptx embedding), regardless of the `output_format` argument. The `output_format` arg only selects which path string the method *returns*; both files always land in `output_dir`. You therefore never need a second render call to get a PNG for the visual gate.
- **Templates**: `generator.get_diagram_templates()` returns `simple_flowchart`, `system_block`, `method_steps`, `component_hierarchy`.

## Chinese / CJK example (CNIPA filing)

A typical CNIPA BMS system block diagram — SimHei font is auto-resolved on Windows via `_resolve_cjk_font()`, so Chinese labels render without tofu □□□.

```python
blocks = [
    {"id": "vadc", "label": "电压采集单元", "ref": 10},
    {"id": "mcu",  "label": "主控 MCU",     "ref": 20},
    {"id": "comm", "label": "通信模块",      "ref": 30},
    {"id": "bal",  "label": "均衡驱动",      "ref": 40},
]
connections = [
    ["vadc", "mcu"],
    ["mcu",  "comm"],
    ["mcu",  "bal"],
]
diagram_path = generator.create_block_diagram(
    blocks=blocks,
    connections=connections,
    filename="bms_block",
    output_format="svg",
    rankdir="LR",        # CNIPA block diagrams default to LR
)
# Rendered: 4 boxes (电压采集单元(10) / 主控MCU(20) / 通信模块(30) / 均衡驱动(40)),
# black-on-white, splines=polyline, SimHei glyphs — CNIPA §第一部分第一章 compliant.
```

For CNIPA filing, if a PDF is required, convert the SVG externally (see Step 3 PDF note).

## Workflow (gated)

Each 🔴 is a blocking gate — do not proceed until it passes.

**🔴 GATE 1 · Plan & confirm** (before generating any code):
- List the nodes/blocks, the edges, and the intended reference-number assignment aloud. For **system block diagrams**, also state the `rankdir` (LR default; pass TB only for top-down hierarchies); for **method flowcharts**, `rankdir` is fixed TB internally and not caller-controlled.
- State how many independent reference numbers the figure needs. If **>3** with lead lines → STOP, tell the user you will split into multiple figures (Anti-Pattern #3).
- Confirm with the user before rendering if the structure is non-trivial (≥8 nodes, decision branches, or loop-back edges).

**Step 2 · Generate**: run the import recipe + the chosen API method (`create_flowchart` / `create_block_diagram` / `render_dot_diagram`). Use in-label `ref=` for reference numbers (Anti-Pattern #6).

**🔴 GATE 2 · Render sanity** (after `_render` returns):
- Confirm the SVG file exists and is non-empty (size > 500 bytes — a tofu/empty render is typically <200 bytes).
- Confirm Chinese labels are present in the SVG source (grep one label, e.g. `Select-String start.svg -Pattern "开始"`). Garbled/`???`/tofu here = fontconfig failed → Failure Mode row 3.

**🔴 GATE 3 · view_image verification** (MANDATORY before declaring done):
- Because the generator now emits both SVG and PNG on every render (dual-output), the PNG is already in `output_dir` — open it directly with the `view_image` tool to visually inspect. (If for any reason only an SVG is present, call the API with `output_format="png"` to produce the raster copy.) Note: `view_image` only accepts raster formats — SVG cannot be inspected this way, which is exactly why the PNG companion is produced automatically.
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

## Failure Modes (quick) & Anti-Patterns (quick)

**Full tables**: see [`references/compliance.md`](references/compliance.md) (8 failure-mode rows + 10 anti-pattern rows + legal basis). The 5 rules below are the most-violated — keep them in mind at all times:

1. **No color** — black ink on white only (§1.84(a)(1)). `bgcolor="white"`, `fillcolor="white"`.
2. **≤2–3 reference numbers per figure** with lead lines; for more, split into a second figure. Prefer in-label `ref=` (no lead lines).
3. **`splines="polyline"`** — never `"ortho"` (drops edge labels) or `"curved"` (not reproducible).
4. **Reference numbers unique** within a figure; each `ref` value denotes exactly one element.
5. **No Unicode symbols (✓ ✗ ⚠ ⭐ ➜) inside HTML-like labels** (`<TD>`, `<TABLE>`) — SimHei lacks these glyphs and Graphviz emits the raw codepoint (e.g. "2713") instead of the glyph → garbage in the figure. Use CJK text (`已覆盖`/`未覆盖`) or ASCII (`[OK]`/`[X]`). Plain node labels are usually fine; only HTML labels are affected. See [`references/compliance.md`](references/compliance.md) Failure Modes row 4.

For any render failure (ExecutableNotFound / tofu / Unicode-symbol-codepoint / oversize / cairosvg), look up the symptom→cause→fix row in [`references/compliance.md`](references/compliance.md#failure-modes).

## Tools Available

- **Bash**: To run Python diagram generation
- **Write**: To save DOT code or diagrams
- **Read**: To load existing diagrams or templates
