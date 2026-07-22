# Patent-Figforge Skill Evaluation Report — Test #2 V2 (Charging Flowchart, POST-OPTIMIZATION)

**Date**: 2026-07-22
**Evaluator**: Independent Judge (GitHub Copilot / DeepSeek V4 Pro)
**Skill Version**: Post-optimization (flowchart port hints, loop-back routing with invisible nodes, anti-patterns #11-13)
**Test Prompt**: "画一个充电控制流程图：开始→检测连接→判断是否连接成功（是→启动充电，否→返回检测）→监测充满→判断是否充满（是→停止充电→结束，否→继续充电）"
**Script**: `c:\AI\.github\skills\patent-figforge\assets\examples\test2_v2_charging_flow.py`

---

## Execution Summary

1. **Skill workflow followed**: Step 1 (Flowchart) → Step 2 (built graph with port hints + invisible routing nodes per updated conventions) → Step 3 (rendered SVG 12.4 KB + PNG 52.2 KB). ✅
2. **UPDATED conventions applied**:
   - ✅ Decision exit table: `dec:e` for 是, `dec:s`/`:w` for 否 — Anti-Pattern #11
   - ✅ Loop-back routing: invisible `shape='point'` nodes — Anti-Pattern #12
   - ✅ All decision branches labeled 是/否 — Anti-Pattern #13
   - ✅ `splines='polyline'` in graph_attr
3. **Render result**: SVG (12,447 bytes) and PNG (52,165 bytes) generated. No Python exceptions.
4. **Baseline comparison**: Baseline SVG was 10,800 bytes; V2 is 12,447 bytes (+15% — additional routing nodes).

---

## What Changed from Baseline: Detailed Analysis

### Baseline Problems (from original evaluation)

| # | Baseline Issue | Severity | V2 Status |
|---|---------------|:--------:|:---------:|
| 1 | Decision exits REVERSED (是 left, 否 right from dec_full) | 🔴 | ✅ FIXED — port hints enforce convention |
| 2 | Loop-back routing = "conceded failure" (no technique provided) | 🔴 | ⚠️ PATTERN EXISTS but produces snaking paths |
| 3 | No `splines` guidance in main SKILL.md | 🟡 | ✅ FIXED — `splines='polyline'` in graph_attr |
| 4 | Skeleton too trivial (single decision, no loop-backs) | 🟡 | ⚠️ STILL trivial (skeleton unchanged) |
| 5 | Critical reference content siloed in shape-specs.md | 🟡 | ✅ FIXED — exit table + loop-back code now in main SKILL.md |

### Decision Exit Routing: COMPARISON

**Baseline** (`test2_charging_flow.py`):
```python
# NO port hints — graphviz auto-routed:
g.edge('dec_full', 'stop_chg', label='是')       # 是 exited LEFT ❌
g.edge('dec_full', 'continue_chg', label='否')   # 否 exited RIGHT ❌
```
→ Exits were REVERSED from patent convention (Yes→right, No→left).

**V2** (`test2_v2_charging_flow.py`):
```python
g.edge('dec_full:e', 'stop_chg', label='是')      # 是 exits right ✅
g.edge('dec_full:s', 'continue_chg', label='否')  # 否 exits bottom ✅
```
→ Exits follow convention. SVG confirms: `dec_full:e` at x=376 (right tip), `dec_full:s` at y=-195 (bottom tip).

### Loop-Back Routing: COMPARISON

**Baseline**:
```python
g.edge('dec_conn', 'detect', label='否', constraint='false')
g.edge('continue_chg', 'monitor', constraint='false')
```
→ Simple `constraint='false'` edges. Paths were not clean but were relatively short.

**V2** (invisible routing nodes):
```python
g.node('route_l1', '', shape='point', width='0')
g.edge('dec_conn:w', 'route_l1', label='否', constraint='false')
g.edge('route_l1', 'detect', constraint='false')
```
→ **PROBLEM**: Invisible nodes with `constraint='false'` float to rank 0 (top of diagram). Both `route_l1` and `route_r1` ended up at y≈-744 (same as `start`), causing edges to snake from bottom to top and back.

**SVG path trace for `continue_chg→route_r1→monitor`**:
```
continue_chg(x=216,y=-140) → right(x=388) → up past start_chg(y=-456) 
→ up past detect(y=-688) → route_r1 at top(y=-744)
→ DOWN through detect zone → through dec_conn zone → through start_chg zone 
→ monitor(x=274,y=-355)
```
→ Path snakes through 4 rank levels, crosses box boundaries. **Violation of safe-channel rule.**

**SVG path trace for `dec_conn:w→route_l1→detect`**:
```
dec_conn:w(x=71,y=-558) → left then right(x=290) → up to route_l1(y=-744)
→ down to detect(y=-667)
```
→ "否" label appears at x=295 (RIGHT side of flow), despite exiting from LEFT tip of diamond.

### Visual Comparison Summary

| Aspect | Baseline | V2 | Winner |
|--------|:--------:|:--:|:------:|
| Decision exit direction | REVERSED ❌ | CORRECT ✅ | **V2** |
| Main flow edge cleanliness | Clean vertical | Clean vertical | Tie |
| Loop-back edge cleanliness | Short diagonal paths | Snaking around entire diagram ❌ | **Baseline** |
| Edge label placement | Auto, reasonable | 否 label on wrong side | **Baseline** |
| B&W / shape compliance | ✅ | ✅ | Tie |
| Reference number placement | All right side | All right side | Tie |

---

## Dimension Scores

### A. Guidance Clarity — Score: 8/10 (was 7, +1)

**What improved**:
- The **decision exit convention table** in the main SKILL.md is crystal clear: 是→`:e` (right), 否→`:s`/`:w` (bottom/left). No more digging through shape-specs.md.
- The **loop-back routing code block** is explicit: invisible `shape='point'` node, route through it with `constraint='false'`.
- The **code examples** use actual Chinese labels (是/否), matching patent use.

**What's still ambiguous**:
- The loop-back pattern doesn't address **invisible node rank placement**. With `constraint='false'`, these nodes float to rank 0, causing snaking paths. A user who copies the pattern exactly gets bad routing.
- No guidance on **how many invisible nodes** are needed per loop-back (one? two? depends on rank distance?).
- The skeleton file was NOT updated — still shows trivial 3-node flow without loop-backs.

**Verdict**: Exit convention is now unambiguous. Loop-back pattern is described but its practical limitation (node floats to top) is undocumented — this would confuse users who get snaking paths from the exact code they copied.

---

### B. Executable Specificity — Score: 8/10 (was 7, +1)

**What improved**:
- Port hints (`:e`, `:w`, `:s`) are mechanically precise — copy, paste, works.
- Invisible node pattern code (`shape='point', width='0'`) is directly copyable.
- `splines='polyline'` is now in the main SKILL.md code block.

**What still requires guesswork**:
- Invisible node **rank placement**: The skill doesn't mention that you might need to anchor invisible nodes to a rank. For the test case, both invisible nodes floated to rank 0, degrading routing. A user would need to discover `rank='same'` or `rank='min'` constraints experimentally.
- **Number of routing nodes**: For `continue_chg→monitor` (2 rank levels apart), one invisible node wasn't enough. The skill doesn't provide a heuristic ("1 invisible node per rank level crossed").

**Verdict**: The code patterns are specific and copyable. The invisible node limitation is an execution gap — the code runs but the output quality depends on undocumented rank-placement knowledge.

---

### C. Completeness — Score: 7/10 (was 5, +2)

This is the biggest improvement. Two 🔴 gaps from baseline are now addressed:

| Baseline Gap | V2 Status |
|-------------|-----------|
| 🔴 Decision yes/no routing convention | ✅ FIXED — exit table with port hints |
| 🔴 Loop-back routing technique ("conceded failure") | ⚠️ HAS PATTERN — but produces suboptimal routing for multi-level loop-backs |
| 🟡 Edge label positioning | ⚠️ Still no guidance (labels placed automatically) |
| 🟡 Safe-channel routing how-to | ⚠️ Pattern exists but invisible node limitation undermines it |
| 🟡 Multi-branch flowchart template | ⚠️ Skeleton still trivial |
| 🟡 Clockwise reference number placement | ⚠️ Still all on right side (known limitation) |

**Verdict**: The two critical gaps are addressed. Exit convention is now complete. Loop-back has graduated from "conceded failure" to "has a pattern with known limitation." The skeleton template and clockwise numbering remain gaps but are less critical.

---

### D. Anti-Pattern Prevention — Score: 7/10 (was 8, -1)

The baseline had 10 static anti-patterns (all effective). The updated skill adds 3 dynamic-routing anti-patterns:

| # | Anti-Pattern | Did it prevent the mistake? |
|---|-------------|:---------------------------:|
| 11 | 是 exits left / 否 exits right | ✅ **YES** — port hints enforce correct direction |
| 12 | Loop-back cuts through flow | ❌ **NO** — invisible nodes float to top, edges snake through diagram |
| 13 | Decision branches not labeled | ✅ **YES** — all edges have 是/否 labels |

**Why #12 failed in practice**: The anti-pattern correctly identifies the problem ("loop-back cuts through flow") and prescribes invisible intermediate nodes. But the prescription is incomplete — it doesn't address rank placement of those invisible nodes. Without rank anchoring, the nodes float to the top, making the routing **worse** than the simple `constraint='false'` approach in the baseline.

**Verdict**: #11 and #13 are effective additions. #12 is directionally correct but the fix is incomplete, and in this test case, the prescribed pattern produced worse routing than the baseline. Score drops from 8 to 7 because the most critical dynamic anti-pattern (#12) isn't reliably prevented.

---

### E. Output Quality — Score: 7/10 (was 6, +1)

**Would the V2 output meet patent standards?**

| Checklist Item | Baseline | V2 | Notes |
|---------------|:--------:|:--:|-------|
| ☐ 1. Black lines, 0.5–0.8pt | ✅ | ✅ | |
| ☐ 2. Font ≥14pt | ✅ | ✅ | |
| ☐ 3. DPI≥300, legible at 2/3 scale | ⚠️ | ⚠️ | DPI not explicitly set |
| ☐ 4. Arabic numbers, lead lines, outside | ✅ | ✅ | |
| ☐ 5. Lead lines clockwise, no cross | ❌ | ❌ | All on right side |
| ☐ 6. "图1" below diagram | ✅ | ✅ | |
| ☐ 7. No extra text outside boxes | ✅ | ✅ | |
| ☐ 8. Lines don't cross boxes | ⚠️ | ❌ | V2 loop-back edges snake through boxes |
| ☐ 9. Consistent proportions | ✅ | ✅ | |
| ☐ 10. No smudges | ✅ | ✅ | |
| ☐ 11. B&W only, no color fills | ✅ | ✅ | |
| ☐ 12. Same component same number | N/A | N/A | |

**Key quality trade-off**:
- **Baseline wins on**: Loop-back edge cleanliness (short paths, though wrong exit sides)
- **V2 wins on**: Decision exit convention (correct, fundamental to patent readability)
- **Net**: Correct exits are more fundamental to patent quality than clean loop-backs. A patent examiner/draftsman would fix the loop-back paths but would be confused by reversed exits. V2 is a net improvement.

**Verdict**: The output is a **better draft** than baseline because the primary flow logic (decision exits) is correct. The loop-back routing degradation is significant but fixable. A patent draftsman would say: "The logic is right — let me clean up these loop-back edges."

---

## Overall D8 Score: 7.4/10

### Change from baseline (6.5): **+0.9**

### Key Improvements Observed

1. **Decision exit convention is now CORRECT and UNAMBIGUOUS** — the single biggest improvement. Port hints (`:e`/`:s`/`:w`) are mechanically enforced, preventing the reversed-exit error that plagued the baseline.
2. **Loop-back routing has graduated from "conceded failure" to "has a defined pattern"** — the invisible node technique is conceptually sound, even if the implementation needs refinement for multi-level loop-backs.
3. **Anti-patterns #11 and #13 are effective** — reversed exits and unlabeled branches are reliably prevented by the new rules.
4. **Critical routing rules are now in the MAIN SKILL.md** — no more digging through reference files to find the exit convention or `splines` setting.
5. **`splines='polyline'` is now a default** — orthogonal routing is enforced, which is the correct direction for patent figures.

### Remaining Gaps

1. **🔴 Invisible routing nodes float to rank 0** — The loop-back pattern's invisible `shape='point'` nodes have no rank constraint, so they float to the top of the diagram. This causes edges to snake through the entire figure, **violating safe-channel routing**. The fix: document that invisible nodes may need `rank='min'`, `rank='same'` with a nearby anchor node, or explicit `pos` attributes for clean placement.

2. **🟡 Loop-back routing degrades with rank distance** — The 1-invisible-node pattern works for adjacent-rank loop-backs but breaks down for multi-level loop-backs (e.g., `continue_chg→monitor` spanning 2+ ranks). A heuristic ("use N invisible nodes for N rank levels crossed") would help.

3. **🟡 Skeleton file is still trivial** — The flowchart skeleton shows a single decision with no loop-backs. It should be updated to demonstrate the invisible-node loop-back pattern, since that's now the prescribed technique.

4. **🟡 "否" label positioning is uncontrolled** — For `dec_conn:w→route_l1→detect`, the "否" label appeared on the RIGHT side of the flow (x=295) despite the edge exiting from the LEFT tip. `labelangle` or `labeldistance` guidance would help.

5. **🟡 Clockwise reference numbers remain aspirational** — All 6 reference numbers still cluster on the right side. This is a known graphviz limitation; documenting a manual SVG post-processing step would be pragmatic.

6. **🟡 Anti-pattern #12 fix is incomplete** — The warning is correct but the prescribed solution doesn't work reliably. Consider: (a) adding rank-anchoring to the invisible node pattern, or (b) offering an alternative technique (e.g., `splines='ortho'` with explicit intermediate nodes at each rank level).

---

## Recommendation for Next Iteration

The updated skill is **directionally correct** — all the right concepts are present. The gap is in **implementation robustness** for the loop-back pattern. The single highest-impact fix:

```python
# CURRENT pattern (node floats to rank 0):
g.node('route_l1', '', shape='point', width='0')           # no rank → floats to top
g.edge('dec_conn:w', 'route_l1', label='否', constraint='false')
g.edge('route_l1', 'detect', constraint='false')

# SUGGESTED pattern (anchor invisible node to intermediate rank):
g.node('route_l1', '', shape='point', width='0')
# Anchor invisible node to same rank as an existing process node:
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('route_l1')
    s.node('start_chg')  # anchor to rank between dec_conn and detect
g.edge('dec_conn:w', 'route_l1', label='否', constraint='false')
g.edge('route_l1', 'detect', constraint='false')
```

This would place the invisible node in the inter-row gap between `dec_conn` and `start_chg`, creating a clean left-side channel for the loop-back edge — eliminating the snaking paths observed in this test.
