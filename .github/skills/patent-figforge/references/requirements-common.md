# Patent Drawing Requirements — USPTO & CNIPA Common

> **Scope**: Requirements **identical or functionally equivalent** between
> **37 CFR §1.84** (USPTO) and **中国专利审查指南** (CNIPA).
> Full legal text quoted for both jurisdictions. Where they agree, a single Graphviz setting satisfies both.
>
> 🔗 **Implements**: SKILL.md §8 (Legal Rules table). These are the **legal floor** — the five axioms (SKILL.md §2) are the **design ceiling** above this floor.

---

## 1. Black & White / Black Ink Only

| Source | Full text |
|--------|-----------|
| **USPTO §1.84(a)(1)** | Black and white drawings are normally required. India ink, or its equivalent that secures solid black lines, must be used. |
| **CNIPA Rule 2** | 计算机绘图，**黑色墨水**，线条均匀清晰，无涂改，周围无无关框线。 |

> Both: 不得着色 (no color). No gradients, no shading, no decorative fills.

**Graphviz**: `bgcolor='white'`, all `color='black'`, `fontcolor='black'`.

---

## 2. Line Quality — Uniform, Clean, Well-Defined

| Source | Full text |
|--------|-----------|
| **USPTO §1.84(l)** | Every line, number, and letter must be durable, clean, **black**, sufficiently dense and dark, **uniformly thick** and well-defined. Heavy enough to permit adequate reproduction. Different thicknesses are permitted when they convey **different meanings**. |
| **CNIPA Rule 2** | 线条应当**均匀清晰、足够深**，不得着色。线条粗细可以有区别（不同粗细表示不同含义）。 |

**Graphviz**: Main outlines `penwidth='0.8'`, lead lines `penwidth='0.5'`.

---

## 3. Page Margins

| Source | Requirement |
|--------|-------------|
| **USPTO §1.84(g)** | Top margin ≥ **2.5 cm** (1 inch), Left ≥ **2.5 cm**, Right ≥ **1.5 cm** (5/8 inch), Bottom ≥ **1.0 cm** (3/8 inch). |
| **CNIPA** | 完全一致 — 上 ≥2.5cm, 左 ≥2.5cm, 右 ≥1.5cm, 下 ≥1.0cm. |

**Graphviz**: `margin='1.0'` in `graph_attr` (≈2.54 cm, meets ≥2.5 cm top/left requirement).

---

## 4. Scale / Legibility at 2/3 Reduction

| Source | Full text |
|--------|-----------|
| **USPTO §1.84(k)** | The scale must be large enough to show the mechanism **without crowding** when the drawing is reduced in size to **two-thirds (2/3)** in reproduction. |
| **CNIPA Rule 5** | 缩至 **67%** 仍清晰可辨（= USPTO §1.84(k) — 完全一致）。附图大小应保证在图中缩小到 2/3 时仍能清楚地分辨出各个细节。 |

**Graphviz**: `dpi='300'` (PNG). SVG is resolution-independent but must be sized so text remains legible at 2/3 zoom. Nodes must be generous — never squeeze.

---

## 5. Font / Character Height ≥ 0.32 cm (≈14 pt)

| Source | Full text |
|--------|-----------|
| **USPTO §1.84(p)(3)** | Numbers, letters, and reference characters must measure at least **0.32 cm (1/8 inch)** in height. Must not cross or mingle with lines. Must not be placed upon hatched or shaded surfaces. |
| **CNIPA** | 字体高度 ≥ **3.2 mm**（约 14 pt）— 与 USPTO §1.84(p)(3) 完全一致。 |

**Graphviz**:
- **Node text**: `fontsize='14'` (≥0.32 cm)
- **Reference number characters**: `fontsize='14'` — 🔴 **MANDATORY**, NOT 12pt. Reference numbers ARE reference characters under §1.84(p)(3) and must meet the same 0.32 cm minimum.
- **Edge labels** (flow conditions like 是/否, signal names): `fontsize='12'` is acceptable — these are annotations, not reference characters. They are not subject to §1.84(p)(3) but should still be legible at 2/3 reduction.

> 🔴 **R5 fix (2026-07-23)**: prior version stated `fontsize='12'` for reference numbers — this violates §1.84(p)(3). The `add_ref_*` helpers in `code-templates.md` already correctly use `fontsize='14'`; only this doc was wrong.

---

## 6. Plain Arabic Numerals for Reference Characters

| Source | Full text |
|--------|-----------|
| **USPTO §1.84(p)(1)** | Reference characters (**numerals are preferred**) must be plain and legible, **not in brackets, inverted commas, or enclosed within outlines** (e.g., encircled). Oriented same direction as the view. |
| **CNIPA** | 附图标记使用**阿拉伯数字**编号，不应放在方框内。编号不应放在括号、引号或圆圈中。 |

**Graphviz**: `shape='plaintext'` for reference number nodes (no boxes, circles, or brackets).

---

## 7. Same Component = Same Reference Number Across All Views

| Source | Full text |
|--------|-----------|
| **USPTO §1.84(p)(4)** | The same part appearing in more than one view must always be designated by the **same reference character**. |
| **CNIPA Rule 6** | **同部件同标记**，说明书与附图标记一致。同一部件在不同图中使用相同的附图标记。 |

**Graphviz**: Use the same node ID for the same component across all figures in the patent document.

---

## 8. Lead Lines MUST NOT Cross 🔴

| Source | Full text |
|--------|-----------|
| **USPTO §1.84(q)** | **Lead lines MUST NOT cross each other.** Lead lines are the lines between the reference characters and the details referred to. May be straight or curved. Should be **as short as possible**. Must originate in the immediate proximity of the reference character and extend to the feature indicated. Lead lines must be executed in the same way as lines in the drawing (same ink quality and durability — not necessarily same dash pattern; dotted lead lines are ISO 128-22 compliant and universally accepted). |
| **CNIPA** | **引线不得交叉**。引线应尽可能短。引线从附图标记指向所指部件。引线用与图中线条相同的方式绘制（指墨水质量和耐久性，非线型图案；虚线引线符合 ISO 128-22，USPTO 和 CNIPA 均接受）。 |

> This is the single most severe violation in both jurisdictions. Crossing lead lines = formal rejection.

**Graphviz**: Maximum **2–3 reference numbers per diagram**. Place on **opposite sides**, far apart. `style='dotted'`, `penwidth='0.5'`, `arrowhead='none'`, `constraint='false'`.

---

## 9. Lead Lines — As Short As Possible

| Source | Full text |
|--------|-----------|
| **USPTO §1.84(q)** | Lead lines should be **as short as possible**. Must originate in immediate proximity of reference character. |
| **CNIPA** | 引线应尽可能短。 |

**Graphviz**: Lead line length ≤ 1.5× box height. Place reference number nodes close to target components.

---

## 10. Arrow Meaning Must Be Clear

| Source | Full text |
|--------|-----------|
| **USPTO §1.84(r)** | Arrows may be used at the ends of lines, **provided their meaning is clear**: (1) freestanding arrow on lead line → entire section; (2) arrow touching a line → surface indicated; (3) arrow → direction of movement. |
| **CNIPA** | 箭头含义必须清楚。 |

**Graphviz**: Arrowheads on flow edges only. Lead lines: `arrowhead='none'`. Never mix arrow semantics.

---

## 11. Text in Drawings — As Few Words As Possible

| Source | Full text |
|--------|-----------|
| **USPTO §1.84(o)** | Drawings shall contain **as few words as possible**. Only single words or short phrases absolutely indispensable for understanding may appear (e.g., "water," "steam," "open," "closed"). |
| **CNIPA Rule 7** | 图中不应有文字注释，必要的简单词语（如"水""开""关"）除外。注释仅用必要词语。 |

**Graphviz**: Keep all `label` values concise — single words or short verb-noun phrases. No sentences, paragraphs, or explanatory notes.

---

## 12. No Photographs

| Source | Full text |
|--------|-----------|
| **USPTO** | Photographs are not ordinarily permitted in utility patent applications. |
| **CNIPA Rule 1** | 🚫 禁止照片/蓝图。 |

> Both allow photographs only by petition when it is the only feasible method (e.g., metallography, electrophoresis gels).

---

## 13. Sharp Corners Only — No Rounded Corners

| Source | Full text |
|--------|-----------|
| **USPTO** | Convention: sharp rectangular boxes in utility patent drawings. |
| **CNIPA** | 方框应使用实线（sharp corners），不得使用圆角。 |

**Graphviz**: `shape='box'` (sharp). NEVER `style='rounded'`.

---

## 14. No Color Fills, Gradients, Shadows, or Decorative Elements

Both jurisdictions prohibit decorative elements that do not convey technical information. Drawings must be pure black-and-white line art.

**Graphviz**: Pure B&W. `bgcolor='white'`. No `fillcolor`, no `gradient`, no `style='filled'` with color, no `shadow`.

---

## 15. Reference Numbers Outside Boxes, Connected by Lead Lines

| Source | Full text |
|--------|-----------|
| **USPTO §1.84(p)(3)** | Reference characters must not cross or mingle with lines. Must not be placed upon hatched or shaded surfaces. |
| **CNIPA** | 编号不应放在图中方框内。 |

**Graphviz**: Reference number nodes decoupled from component nodes. Lead lines connect them. `constraint='false'` on lead edges.

---

## 16. No Title on Diagram Itself

Figure number/identifier placed **below** the figure, not as a title within the drawing area.

| Source | Convention |
|--------|------------|
| **CNIPA** | 图号写在图的下方居中。 |
| **USPTO §1.84(u)** | Preceded by "FIG." — placed below or adjacent to the figure. |

**Graphviz**: `label='图1'` (CNIPA) or `label='FIG. 1'` (USPTO), `labelloc='b'`. No heading text inside the graph.

---

## 17. Vertical Orientation Preferred

| Source | Full text |
|--------|-----------|
| **USPTO §1.84** | Views must be upright. Same-page views must be in the same direction. |
| **CNIPA Rule 4** | **竖直**绘制，各图明显分开；横向图顶部置于左侧。 |

**Graphviz**: `rankdir='TB'` (top-to-bottom) by default.

---

## 18. Lines Must Not Cross Through Boxes

| Source | Full text |
|--------|-----------|
| **Both** | Arrows/routing lines must not pass through component boundaries. |

**Graphviz**: Use safe-channel routing with `splines='polyline'`. Horizontal segments travel in inter-row gaps.

---

## 19. Paper Size — A4 Accepted by Both

| Source | Full text |
|--------|-----------|
| **USPTO §1.84(f)** | A4 (21.0 × 29.7 cm) **or** US Letter (21.6 × 27.9 cm). |
| **CNIPA** | A4 (21.0 × 29.7 cm) only. |

> **Common subset**: A4 is accepted by both. Use A4 for dual-jurisdiction filings. US Letter is USPTO-only.

---

## 20. No Borders / Frames Around Drawing Area

| Source | Full text |
|--------|-----------|
| **USPTO** | No frame lines around the usable area; only corner crop marks. |
| **CNIPA** | 周围无无关框线。 |

**Graphviz**: No enclosing `boundingbox` or frame. `margin='1.0'` provides whitespace without a visible border.

---

## 21. Output Formats

| Format | Use case | Requirement |
|--------|----------|-------------|
| **SVG** | Editing, archiving | Vector preferred |
| **PDF** | Formal submission | USPTO/CNIPA direct |
| **PNG** | Preview, embedding | DPI ≥ 300 |

> SVG is the recommended working format (resolution-independent, editable). Render to PDF for final submission. PNG at DPI≥300 is acceptable for previews.

---

## Summary: Dual-Compliance Graphviz Baseline

| Setting | Value | Satisfies |
|---------|-------|-----------|
| Background / color | `bgcolor='white'`, `color='black'` | §1.84(a)(1), CNIPA R2 |
| Main line width | `penwidth='0.8'` | §1.84(l), CNIPA R2 |
| Lead line width | `penwidth='0.5'` | §1.84(q), CNIPA |
| Node font size | `fontsize='14'` | §1.84(p)(3), CNIPA |
| Reference number font | `fontsize='14'` (🔴 NOT 12pt) | §1.84(p)(3), CNIPA |
| Edge label font (non-ref) | `fontsize='12'` | legibility guideline |
| DPI | `dpi='300'` | §1.84(k), CNIPA R5 |
| Margins | `margin='1.0'` | §1.84(g), CNIPA |
| Reference numbers | `shape='plaintext'`, max 2–3 | §1.84(p)(1), CNIPA |
| Lead lines | `style='dotted'`, `penwidth='0.5'`, `arrowhead='none'` | §1.84(q), CNIPA |
| Routing | `splines='polyline'` | Both |
| Guard rails | `style='invis'` edges between same-rank nodes | Both |

> **Language-dependent settings** (figure label format, decision branch labels, label language) → see jurisdiction-specific files below.
