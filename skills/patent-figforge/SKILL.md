---
name: patent-figforge
description: Create patent-style technical diagrams including flowcharts, block diagrams, and system architectures using Graphviz with reference numbering. 触发词：专利附图、流程图、框图、架构图、reference numbers、patent figures、专利图、方法流程图、系统框图
---

# Patent Diagram Generator Skill

Create patent-style technical diagrams including flowcharts, block diagrams, and system architectures using Graphviz.

> 🎨 **Style alignment with patent-forge**: font (SimHei/黑体, 14pt), line weight (penwidth=1.3), arrow style (vee), color (B&W only) are hard-coded in `diagram_generator.py` — no caller configuration needed, always consistent. See [`references/compliance.md`](references/compliance.md) for full anti-patterns & failure modes.

## When to Use

Invoke this skill when users ask to:
- Create flowcharts for method claims
- Generate block diagrams for system claims
- Draw system architecture diagrams
- Create technical illustrations for patents
- Add reference numbers to diagrams
- Generate patent figures

## When NOT to Use

Do **not** invoke this skill for:
- General-purpose flowcharts or architecture diagrams unrelated to patent filing — use a generic Mermaid/Graphviz skill instead
- UI mockups, wireframes, or design comps — use Excalidraw or Draw.io skills
- Diagrams that require color coding, gradient fills, or photographic elements — these are rejected by patent offices
- Figures that already exist as hand-drawn sketches needing only digitization — use a vector tracing tool, not de novo generation

## Quick Reference

- **Flowchart**: `create_flowchart(steps, filename, output_format="svg")` — rankdir fixed TB
- **Block diagram**: `create_block_diagram(blocks, connections, filename, output_format="svg", rankdir="LR", title="")` — rankdir default LR
- **Custom DOT**: `render_dot_diagram(dot_code, filename, output_format="svg", engine="dot")`
- **Dual output**: every render emits **both SVG + PNG** automatically. PDF NOT supported — convert externally.
- **Templates**: `generator.get_diagram_templates()` → `simple_flowchart`, `system_block`, `method_steps`, `component_hierarchy`
- **Reference numbers**: prefer in-label `ref=` (e.g. `{"id":"cpu","label":"处理器","ref":20}`). Numbering: main=10/20/30, sub=12/14/16. Each number = exactly ONE element per figure.

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

### Bootstrap (self-locating, works in any runtime)

```python
import os, sys
# Resolve skill root = the folder containing this SKILL.md (parent of python/).
_SKILL_ROOT = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
for _candidate in (_SKILL_ROOT, os.getcwd(), r"c:\AI\.github\skills\patent-figforge"):
    if os.path.exists(os.path.join(_candidate, "python", "diagram_generator.py")):
        _SKILL_ROOT = _candidate; break
sys.path.insert(0, _SKILL_ROOT)
from python.diagram_generator import PatentDiagramGenerator

# Ensure Graphviz `dot` on PATH (Windows ships it NOT on PATH by default).
for _dot_dir in (r"C:\Program Files\Graphviz\bin", "/usr/bin", "/usr/local/bin"):
    if os.path.exists(os.path.join(_dot_dir, "dot.exe")) or os.path.exists(os.path.join(_dot_dir, "dot")):
        os.environ["PATH"] = _dot_dir + os.pathsep + os.environ.get("PATH", ""); break

generator = PatentDiagramGenerator(output_dir=".")
```

### Flowchart — `create_flowchart(steps, filename, output_format="svg")`

Rankdir **fixed TB** (no caller arg). Each step's `next` entry: bare `str` (id) or dict `{id, label?, style?, constraint?}`. Set **`constraint="false"`** for loop-back edges so graphviz routes them as back-arcs outside the main rank chain (prevents crossing).

```python
steps = [
    {"id":"start","label":"开始","shape":"ellipse","ref":10,"next":["s1"]},
    {"id":"s1","label":"采样","shape":"box","ref":20,"next":["dec"]},
    {"id":"dec","label":"过压?","shape":"diamond","ref":30,"next":[
        {"id":"protect","label":"是"},
        {"id":"s1","label":"否","constraint":"false"},
    ]},
    {"id":"protect","label":"保护模式","shape":"box","ref":40,"next":["end"]},
    {"id":"end","label":"结束","shape":"ellipse","ref":50,"next":[]},
]
generator.create_flowchart(steps=steps, filename="bms_method")
```

### Block diagram — `create_block_diagram(blocks, connections, filename, output_format="svg", rankdir="LR", title="")`

Rankdir defaults **LR** (system blocks); pass `rankdir="TB"` only for top-down hierarchies. `type` field on blocks is **ignored by renderer** (all render as boxes; exists for forward-compat). Connections: `[from, to, label?, style?]`.

```python
blocks = [{"id":"vadc","label":"电压采集","ref":10},{"id":"mcu","label":"主控MCU","ref":20}]
connections = [["vadc","mcu","SPI"]]
generator.create_block_diagram(blocks=blocks, connections=connections, filename="bms_block")
```

### Custom DOT — `render_dot_diagram(dot_code, filename, output_format="svg", engine="dot")`

Pass raw DOT source. Engine: `dot` (hierarchical, default), `neato`, `fdp`, `circo`, `twopi`.

### Reference numbers

Prefer in-label `ref=` on node/block dict (e.g. `{"id":"cpu","label":"处理器","ref":20}`) — appends `(20)` cleanly, no lead lines. The post-hoc `add_reference_numbers()` API exists but is discouraged (Anti-Pattern #6). **Numbering**: main=10/20/30, sub=12/14/16. Each number = exactly ONE element per figure.

### Chinese / CJK example (CNIPA filing)

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

> **PDF note**: this skill does not emit PDF. If the filing office requires PDF, convert the SVG externally (`rsvg-convert -f pdf`, Inkscape CLI, or `dot -Tpdf`).

## Shape / Engine / Format quick reference

- **Flowchart shapes**: `ellipse` (start/end), `box` (process), `diamond` (decision), `parallelogram` (I/O), `cylinder` (DB). **Block types** (documentation only): `input`/`output`/`process`/`storage`/`decision`/`default` — all render as `box`.
- **Layout engines**: `dot` (hierarchical — default for patents), `neato`, `fdp`, `circo`, `twopi`.
- **Output formats**: **dual-output is automatic** — every render (`create_flowchart` / `create_block_diagram` / `render_dot_diagram`) emits BOTH `.svg` (primary, editable, the patent filing vector source) AND `.png` (for the `view_image` verification gate + docx/pptx embedding), regardless of the `output_format` argument. The `output_format` arg only selects which path string the method *returns*; both files always land in `output_dir`. You therefore never need a second render call to get a PNG for the visual gate.
- **Templates**: `generator.get_diagram_templates()` returns `simple_flowchart`, `system_block`, `method_steps`, `component_hierarchy`.

## Workflow (gated)

Each 🔴 is a blocking gate — do not proceed until it passes.

**🔴 GATE 1 · Plan & confirm** (before generating any code):
- List nodes/blocks, edges, and reference-number assignment aloud.
- For **block diagrams**: state `rankdir` (LR default; TB only for top-down hierarchies). For **flowcharts**: rankdir is fixed TB internally.
- If **>3** independent reference numbers with lead lines → STOP, split into multiple figures (Anti-Pattern #3).
- Confirm with user before rendering if structure is non-trivial (≥8 nodes, decision branches, or loop-back edges).

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

## Failure Modes & Anti-Patterns

If your render fails, diagnose with the table first (top 3 most common). For the full 8-failure-mode + 10-anti-pattern tables, see [`references/compliance.md`](references/compliance.md).

### 🔧 Top 3 failure branches — if X fails → Y

| 如果 (symptom) | 原因 (root cause) | 一线修复 (first fix) | 仍失败兜底 (fallback) |
|---|---|---|---|
| `ExecutableNotFound: failed to execute 'dot'` | Graphviz `dot` 不在 PATH（Windows 安装器默认不加）| 导入 recipe 已自动探测 `C:\Program Files\Graphviz\bin`。若仍失败：跑 `dot -V` 确认安装→未安装则 `choco install graphviz` / `brew install graphviz` / `apt install graphviz` | 安装后重启终端使 PATH 生效；若 `dot -V` 已可用但仍报错，检查是否被杀毒软件拦截 |
| 中文渲染为 □□□ / `???` / 空白 | 字体配置缺失：fontconfig 找不到 CJK 字体文件（Windows 上 Graphviz 不带 fonts.conf）| `_resolve_cjk_font()` 在导入时自动写入 fonts.conf 并设 `FONTCONFIG_FILE`。若仍乱码：(1) `Test-Path C:\Windows\Fonts\simhei.ttf` 确认字体存在；(2) 验证 `$env:FONTCONFIG_FILE` 指向正确 conf；(3) GATE2 grep 中文 label 重验 | Linux: `apt install fonts-noto-cjk`；macOS: 确认 PingFang 可用。若所有候选字体缺，跑 `fc-list :lang=zh` 找可用 CJK 字体加入 `_CJK_CANDIDATES` |
| Unicode 符号（✓ ✗ ⚠ ⭐ ➜）渲染为码点（如 "2713" 替换了 ✓）— **仅在 HTML-like label**（`<TD>`, `<TABLE>`）| SimHei 缺少 misc-symbols 范围 (U+2600–U+27BF) 字形；Graphviz HTML label 字体查找无 fallback 链 → 直接输出码点 | 替换为中文（`已覆盖`/`未覆盖`/`警告`）或 ASCII（`[OK]`/`[X]`/`[!]`） | **不要**给 HTML label fontname 追加符号字体——HTML label 只认单字体，追加会丢失 CJK。纯文本 node label 不受此影响 |

### 🚫 5 most-violated anti-patterns

1. **No color** — black ink on white only (§1.84(a)(1)). `bgcolor="white"`, `fillcolor="white"`.
2. **≤2–3 reference numbers per figure** with lead lines; for more, split into a second figure. Prefer in-label `ref=` (no lead lines).
3. **`splines="polyline"`** — never `"ortho"` (drops edge labels) or `"curved"` (not reproducible).
4. **Reference numbers unique** within a figure; each `ref` value denotes exactly one element.
5. **No Unicode symbols inside HTML-like labels** — see failure branch row 3 above. For non-HTML plain node labels, most symbols are fine but verify via GATE3.
