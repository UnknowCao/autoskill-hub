# Patent-Figforge Skill Evaluation Report — Test #2 (Charging Flowchart)

**Date**: 2026-07-22
**Evaluator**: Independent Judge (GitHub Copilot / DeepSeek V4 Pro)
**Test Prompt**: "画一个充电控制流程图：开始→检测连接→判断是否连接成功（是→启动充电，否→返回检测）→监测充满→判断是否充满（是→停止充电→结束，否→继续充电）"

---

## Execution Summary

1. **Skill workflow followed**: Step 1 (determined type: Flowchart) → Step 2 (built graph with Python graphviz) → Step 3 (rendered SVG + PNG). Both checkpoints passed.
2. **Script produced**: `c:\AI\.github\skills\patent-figforge\assets\examples\test2_charging_flow.py`
3. **Render result**: SVG (10.8 KB) and PNG (38.4 KB) generated successfully. No Python exceptions. Files > 0 bytes.
4. **Dependency issue encountered**: System Graphviz `dot` not on PATH — exactly matches the skill's Failure Mode #1 (`ExecutableNotFound`). Resolved by adding `C:\Program Files\Graphviz\bin` to PATH. The skill's guidance here was accurate.

---

## Skill Quality Assessment

### A. Guidance Clarity — Score: 7/10

**What worked**:
- The diagram-type selection table (Step 1) is clear and correctly guided me to choose "Flowchart" with `rankdir='TB'`
- The shape sequence "ellipse → box → diamond → ellipse" is unambiguous
- The skeleton file (`flowchart-skeleton.py`) provides a copy-paste starting point with all boilerplate (graph_attr, node_attr, edge_attr, g.attr for 图1)

**Ambiguities encountered**:
- The skeleton only shows a trivial 3-node linear flow (start→step→decision→step→end with simple yes/no edges). It provides **zero guidance** on how to handle loop-back edges or decision branching beyond a single yes/no fork
- The main SKILL.md says nothing about where "是" and "否" labels should exit from the diamond. The shape-specs reference says "Yes→diamond right tip, No→diamond left tip" but this is **buried in a reference file**, not surfaced in the workflow steps
- No mention of `splines` in the main SKILL.md — I had to discover `splines='polyline'` from the references/shape-specs.md

**Verdict**: Clear for trivial flowcharts; under-specified for anything with loop-backs.

---

### B. Executable Specificity — Score: 7/10

**What was specific enough**:
- Exact `width`/`height` values for all three shape types (ellipse: 1.8×0.5, box: 3.0×0.6, diamond: 2.8×1.4) — directly copyable
- `penwidth='0.6'` for outlines, `penwidth='0.35'` for lead lines — unambiguous
- Font sizes: 14pt for box text, 11pt for labels/ref numbers — specific
- Reference number + lead line pattern with `shape='plaintext'`, `style='dotted'`, `constraint='false'` — mechanically precise

**What required guesswork**:
- **Decision branching routing**: How do I make the "否" edge loop back without crossing the main flow? The skill says `constraint='false'` and falls back to "manual editing in vector editor" — this is a **concession of failure**, not executable guidance
- **Loop-back edge path**: I used `constraint='false'` on both loop-back edges as the skill suggests. The result: the `dec_conn→detect` (否) edge routes slightly right-then-up (not from the diamond's left tip as the reference convention prescribes), and the `continue_chg→monitor` edge goes up along the right side — functional but not patent-elegant
- **Which graphviz engine?** The skill mentions `dot/neato/fdp/circo/twopi` but doesn't recommend one for flowcharts. I used default `dot`, which worked
- The **ellipse "flat" spec**: is given as exact numbers (1.8×0.5) rather than a ratio, which is fine for copy-paste but doesn't explain the underlying principle

**Verdict**: Static node specs are excellent; dynamic edge routing is a gap.

---

### C. Completeness — Score: 5/10

**Covered**:
- Node shapes and dimensions ✓
- B&W compliance, font specs, line widths ✓
- Reference numbers with lead lines ✓
- 图1 label placement ✓
- Pre-submission checklist (12 items) ✓
- Failure modes table (7 entries) ✓

**Missing for flowchart-specific needs**:

| Gap | Impact | Severity |
|-----|--------|:--------:|
| **Decision yes/no routing convention** | "是" exited left, "否" exited right from `dec_full` — exactly backwards from the patent convention (Yes→right, No→left). This happened because graphviz placed `stop_chg` left and `continue_chg` right via `rank=same`. | 🔴 |
| **Loop-back edge routing technique** | No graphviz technique provided for routing backward edges cleanly (invisible nodes, port-based routing `:w`/`:e`, intermediate routing nodes). Fallback "manual editing" means the skill doesn't actually produce patent-ready flowcharts with loops. | 🔴 |
| **Edge label positioning** | 是/否 labels placed automatically by graphviz — no guidance on controlling label offset or position | 🟡 |
| **Safe-channel routing how-to** | Mentioned in shape-specs reference ("horizontal segments in inter-row gaps") but no graphviz implementation strategy. The rendered flowchart has diagonal edges (`dec_full→stop_chg`) rather than strict vertical-horizontal-vertical routing. | 🟡 |
| **Clockwise reference number placement** | All 6 reference numbers ended up on the right side. The skill says "clockwise" but provides no graphviz technique to achieve left-side placement. | 🟡 |
| **Multi-branch flowchart template** | The skeleton is too trivial (one decision, no loops). A realistic skeleton with one loop-back would be far more useful. | 🟡 |

**Verdict**: Solid for static visual specs; significantly incomplete for flowchart-specific routing logic.

---

### D. Anti-Pattern Prevention — Score: 8/10

**What the 🚫 table prevented well**:
- #1 (rounded corners) — I used `shape='box'` ✓
- #2 (lines >1.5pt) — I used `penwidth='0.6'` ✓
- #3 (arrows through boxes) — I was conscious of this, though the rendered result still has diagonal edges that come close to box boundaries
- #4 (numbers inside boxes) — I used external reference numbers with lead lines ✓
- #5 (color fills) — no fills used ✓
- #6 (title on diagram) — only `label='图1'` below ✓
- #8 (box w/h ≈ 1:1) — used 3.0×0.6 (5:1) ✓
- #9 (tall diamond) — used 2.8×1.4 (2:1) ✓
- #10 (gradients/shadows) — none used ✓

**What the table did NOT prevent**:
- **Loop-back edges that don't follow safe-channel routing**: The `continue_chg→monitor` edge goes at a shallow angle through the right-side space — not terrible, but the skill offers no anti-pattern like "loop-back edge cuts across vertical flow"
- **Decision branches exiting wrong sides**: The rendered output has 是 exiting left and 否 exiting right from `dec_full`, reversed from convention — the anti-pattern table doesn't catch this
- **All reference numbers clustered on one side**: No anti-pattern for "reference numbers not arranged clockwise"

**Verdict**: Strong on static visual quality; missing anti-patterns for dynamic routing issues.

---

### E. Output Quality Expectation — Score: 6/10

**Would the flowchart meet patent standards?** — **Partially, with caveats.**

| Checklist Item | Status | Notes |
|---------------|:------:|-------|
| ☐ 1. Black lines, 0.5–0.8pt | ✅ | penwidth=0.6 |
| ☐ 2. Font ≥14pt | ✅ | 14pt nodes, 11pt labels |
| ☐ 3. DPI≥300, legible at 2/3 scale | ⚠️ | PNG rendered; DPI not explicitly set |
| ☐ 4. Arabic numbers, lead lines, outside | ✅ | 10–60 with dotted lead lines |
| ☐ 5. Lead lines clockwise, no cross | ❌ | All ref numbers on right side; not clockwise |
| ☐ 6. "图1" below diagram | ✅ | Correct placement |
| ☐ 7. No extra text outside boxes | ✅ | Clean |
| ☐ 8. Lines don't cross boxes | ⚠️ | Loop-back edges pass near box boundaries; diagonal 是 edge could be cleaner |
| ☐ 9. Consistent proportions | ✅ | Uniform box/diamond/ellipse sizes |
| ☐ 10. No smudges | ✅ | Clean vector rendering |
| ☐ 11. B&W only, no color fills | ✅ | Compliant |
| ☐ 12. Same component same number | N/A | Single figure |

**Specific output issues**:
1. **Reversed decision exits**: `dec_full` has 是 exiting left (to `stop_chg`) and 否 exiting right (to `continue_chg`) — opposite of the shape-specs convention. A patent examiner might not reject this, but a skilled draftsman would flag it.
2. **Non-orthogonal edges**: The `dec_full→stop_chg` (是) edge goes diagonally rather than straight down with a horizontal segment. Patent convention prefers orthogonal routing.
3. **All reference numbers on right**: The clockwise convention is not met. This would need manual SVG editing to fix.

**Verdict**: The output is a **reasonable draft** that demonstrates correct shapes and conventions, but would require **manual vector-editor cleanup** (which the skill itself acknowledges) to meet formal patent submission quality.

---

## Overall D8 Score: **6.5/10**

---

## Key Observations

### What Worked Well
- **Shape specifications are precise and actionable**: The exact width/height values for ellipses, boxes, and diamonds are directly copyable and produce correct proportions
- **Skeleton files save time**: The flowchart skeleton eliminated ~20 lines of boilerplate and ensured correct font/color/penwidth defaults
- **Anti-pattern table is effective for static issues**: During scripting, I consciously checked each 🚫 item — it prevented rounded corners, color fills, numbers-inside-boxes, and wrong line widths
- **Reference number + lead line pattern is solid**: The block-diagram skeleton's approach (plaintext nodes + rank=same + dotted constraint=false edges) works mechanically and produces patent-convention-compliant lead lines
- **Failure Modes table was accurate**: The `ExecutableNotFound` error was exactly what I hit, and the fix guidance was correct
- **Reference documentation (shape-specs.md, numbering.md, patent-standards.md) is thorough**: These contain more detailed guidance than the main SKILL.md — the patent-standards.md in particular is well-researched

### What Was Confusing or Missing

1. **🔴 Critical: No decision-branch routing convention in main workflow**
   The shape-specs reference says "Yes→diamond right tip, No→diamond left tip" but the main SKILL.md workflow (Steps 1–3) never mentions this. As a result, my rendered output has the branches exiting the wrong sides because graphviz's automatic layout overrode the convention. The skill needs an explicit Step 2.5: "Route decision branches: 是 from east port, 否 from west port."

2. **🔴 Critical: Loop-back routing is a conceded failure mode**
   The Failure Modes table says "Lead lines overlap → Note: manual editing in vector editor." This effectively means the skill **cannot produce patent-ready flowcharts with loops** through graphviz alone. For a skill named "patent-figforge," this is a significant gap. At minimum, provide concrete graphviz techniques: invisible intermediate routing nodes, port-based edge routing (`:w`/`:e`/`:n`/`:s`), or `splines='ortho'` with explicit path control.

3. **🟡 The skeleton is too trivial for realistic use**
   The flowchart skeleton shows start→step→decision→step→end with a single yes/no fork and no loop-backs. It doesn't demonstrate:
   - How to route a "否" branch that loops back upward
   - How to handle two decision nodes in sequence
   - How to use `rank='same'` for side branches
   A more realistic skeleton would save significant trial-and-error.

4. **🟡 Critical reference content is siloed**
   The shape-specs.md contains vital routing rules (safe channels, exit directions, splines) that should be surfaced in the main SKILL.md workflow. As written, a user who only reads SKILL.md will miss:
   - `splines='polyline'` or `splines='ortho'` requirement
   - Arrow routing: "vertical → horizontal (in inter-row gap) → vertical"
   - Decision exit convention (yes=east, no=west)

5. **🟡 Clockwise reference number placement is aspirational, not actionable**
   The numbering.md says "clockwise" but provides no graphviz technique. In practice, `rank='same'` subgraphs with `constraint='false'` edges always place reference numbers to the right in a TB layout. To get left-side placement, you'd need to place numbers before the component in document order or use explicit positioning — neither technique is documented.

6. **🟡 No guidance on edge label positioning**
   The 是/否 labels are placed by graphviz automatically. For patent figures, label position relative to the edge midpoint matters for legibility. The skill offers no `labeldistance` or `labelangle` guidance.

### What Would Improve the Skill

1. **Add a "Flowchart Routing Patterns" section** to the main SKILL.md or as a prominent Step 2.5:
   ```markdown
   ### Decision Branch Routing
   - 是 (yes): exits diamond **right tip** → goes to next step below
     - `g.edge('dec', 'next', label='是')` 
   - 否 (no): exits diamond **left tip** → loops back or branches sideways
     - `g.edge('dec', 'target', label='否', constraint='false')`
   - For loop-backs that go upward: use invisible routing node to guide edge around the left side
   ```

2. **Replace the trivial skeleton** with a realistic one that includes:
   - One loop-back (否 → previous step)
   - Two decision nodes in sequence
   - A side branch with `rank='same'`
   - Invisible routing nodes for clean loop-back paths

3. **Surface `splines='polyline'` as a default** in the main SKILL.md Step 2 code block — don't bury it in references.

4. **Add an anti-pattern**: "Loop-back edge crosses main vertical flow" → "Route around left side via invisible nodes or accept manual SVG cleanup"

5. **Document the clockwise reference number limitation**: State clearly that automatic graphviz placement puts all ref numbers on one side, and that manual SVG editing (or explicit `pos` attributes) is needed for true clockwise arrangement.

6. **Add a flowchart-specific test to the pre-submission checklist**:
   - ☐ Decision yes/no branches exit correct sides (yes=east/right, no=west/left)
   - ☐ Loop-back edges don't cross the main vertical flow
   - ☐ All edges use orthogonal routing (no diagonals through box zones)

7. **Consider adding a `--engine=neato` or `splines='ortho'` recommendation** for flowcharts, since `dot` with default splines produces curved/diagonal edges that violate patent orthogonal-routing conventions.

---

## Appendix: Script Produced

**File**: `c:\AI\.github\skills\patent-figforge\assets\examples\test2_charging_flow.py`
**Output**: `test2_charging_flow_output.svg` (10.8 KB), `test2_charging_flow_output.png` (38.4 KB)
**Nodes**: 9 (start, end, 5 process boxes, 2 decision diamonds) + 6 reference numbers
**Edges**: 10 (7 main flow + 1 branch + 2 loop-backs) + 6 lead lines
**Render engine**: dot (default)
**Dependencies resolved**: Python graphviz ✅, system Graphviz ✅ (via `C:\Program Files\Graphviz\bin`)
