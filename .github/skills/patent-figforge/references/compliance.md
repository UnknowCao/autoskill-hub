# Compliance Reference — patent-figforge

Detailed failure-mode and anti-pattern tables referenced by SKILL.md.
The SKILL.md body keeps only the most-likely-violated trigger rules; this file
holds the full tables for diagnosis and audit.

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

## Legal basis (selected)

- **37 CFR §1.84(a)(1)**: black ink on white — no color.
- **37 CFR §1.84(p)(3)**: figure text ≥ ~14pt.
- **37 CFR §1.84(q)**: no crossing lead lines.
- **CNIPA 专利审查指南 第一部分第一章**: black/white line drawings, sharp rectangles preferred for block diagrams.
