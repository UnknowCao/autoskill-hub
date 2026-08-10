# Changelog

All notable changes to this skill are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for its
own scripts (the wrapped `markitdown` is versioned independently and called
out per release).

Categories we use: **Added**, **Changed**, **Fixed**, **Removed**, **Security**,
**Docs**. Each entry states *why* the change was made, not just *what* changed —
this is the project's iteration-discipline rule (see SKILL.md "回炉").

---

## [Unreleased]

### Changed — Skill rename: markitdown-enhanced → x2md (2026-08-10)
- **Skill name** changed to `x2md`. The old name implied a pure patch-set
  for markitdown; the new name foregrounds what the skill *does*
  (anything → Markdown) and lets the upstream-vs-enhanced differentiator
  live in the README rather than the name.
- **README reworked** per the rename: lead screen now opens with a
  **supported-formats table** (Office / web / data / image-OCR / audio /
  YouTube / Visio), then foregrounds **what upstream markitdown cannot do**
  (formula escaping, rowspan table columns, encrypted files, XLSX NaN,
  nested tables, resumable batch, size-aware timeouts, metadata header) —
  each row is a real upstream failure mode with a one-line fix description.
- **keyring service** changed from `'markitdown-enhanced'` to `'x2md'`
  (clean switch, option B). Passwords previously stored under the old
  service name are NOT migrated — re-enter once on first encrypted-file
  conversion after upgrade. Affected: `_decrypt.py` (6 call sites),
  `_convert_core.py` (chat-routing keyring one-liner), SKILL.md
  (3 references), README cross-platform note.
- **Task template** renamed `assets/tasks/md-enh-dyn.jsonc` →
  `assets/tasks/x2md-dyn.jsonc`; workspace path inside updated to
  `.github/skills/x2md/scripts/...`.
- **banner.svg** + **demo_showcase.py** title strings updated to `x2md`.
- **Downstream consumers** updated: `patent-forge` and `patent-forge-2`
  reference paths in `SKILL.md` and `references/shared_workflow.md`
  changed from `markitdown-enhanced` → `x2md` (both the directory path
  and the skill name in prose).

### Added — Luban polish round (2026-08-10)
- **LICENSE** file now ships with the skill (README badge previously claimed
  MIT without the actual text — a legal blocker for redistribution). Includes
  a third-party-license notice block for all runtime dependencies.
- **.gitignore** to stop polluting commits with regenerable test output
  (`tests/output/*.md`), `__pycache__/`, local venvs, and the `.__dec_*`
  pre-decrypted temp files written by `batch_convert_dynamic.py`.
- **CHANGELOG.md** (this file) — prior darwin optimization rounds had no
  user-facing record; new users could not tell what changed or why.
- **XLSX partial-evaluation warning**: new
  `_xlsx_formula_eval.evaluate_xlsx_with_report()` returns
  `(bytes, EvaluationReport)` where `Report.unresolved_cells` lists the
  sheet+cell refs whose formulas could not be computed (e.g. unsupported
  functions, array formulas). Previously this was a silent graceful no-op
  — the agent had no signal that cells would still emit `NaN`, which is
  exactly the C-4 silent-data-loss class the skill warns against.
  `_convert_core._maybe_eval_xlsx()` surfaces the report as a single stdout
  line in the summary (e.g. `XLSX formula eval: 15/15 cells resolved` or
  `... 13/15 cells resolved, 2 unresolved → will emit NaN: sheet1!B6, ...`).
  Live-verified: sample xlsx reports `15/15 resolved`; missing-library path
  reports `formulas library not installed — ... C-4 STOP policy`. The script
  still never raises — signalling only, the agent decides whether to STOP.
- **Showcase reproducibility**: `scripts/demo_showcase.py` (cross-platform,
  no bash dependency) regenerates all README-cited evidence from the frozen
  `tests/samples/` — formula before/after, table D2 sidecar, xlsx eval log,
  and a `summary.txt` digest. Anyone can re-record by running one command.
  Output lands in gitignored `tests/output/showcase/`.
- **Banner**: `assets/banner.svg` — dark-theme banner leading the README
  with the four-fix hook (公式不乱码 / 表格不错列 / 加密不卡壳 / NaN 变实数).

### Docs — README restructure for first-screen clarity
- Reordered README so the **correctness comparison table**
  (本家 markitdown vs enhanced) sits above the fold, replacing the weaker
  "你和本家之间选谁" framing. Full capability matrix moved into a
  collapsible `<details>` block to keep the first screen scannable.
- Added a "为什么不直接问 Agent？" lead — the agent cannot know
  markitdown's bugs on its own; installing this skill injects the 14-Do-NOT
  incident library into its reasoning.
- Added a "看得见的证据" section with the live showcase digest and a
  before/after formula diff, so the differentiator is visible without
  running anything.
- File-structure tree updated to list LICENSE, CHANGELOG, .gitignore,
  banner.svg, and demo_showcase.py.

---

## [0.1.7-r3] — 2026-08-06

### Fixed — darwin R3 (dim5/8 boundary, +0.9 over R2)
- **Stage-1 issue table split**: the original table listed 5 defect types
  (D2/D6/nested/D3/D4) but `_table_detect.py` only emits 2. Split into
  "Currently emitted" (`vertical_merge`=D2, `nested_table`=nested, with
  explicit `issue_type` → `defect_id` mapping column) and "Roadmap — not
  yet emitted" (D6/D3/D4 + Status column). Do-NOT row 1, AUTO-FIX case 1,
  and the Runtime Warnings overview sentence were aligned to emitted-only
  so the agent never waits for a defect that cannot appear.
- *Why*: judges kept flagging "documented but not emitted" defects as
  stale references; the split makes the actual detection surface explicit.

### Changed — darwin R2 (dim7 architecture, +1.2 over R1)
- **Do-NOT row 14** (slow-machine timeout bands) compressed from ~250 chars
  of narrative to the 3-column contract; the full lever table moved up to
  the "Slow-machine angle" section. Row 14 now cross-references it. No
  information loss (verified by independent judge cross-ref check).
- *Why*: the narrative row was longer than the table it summarised.

### Fixed — darwin R1 (dim1 frontmatter, +2.6 over baseline)
- **Version contradiction resolved**: frontmatter said 0.1.5, body said
  0.1.5, Formula section said 0.1.6, but the venv actually had 0.1.7
  installed. Unified to "tested on 0.1.7" with a dated verification note
  (2026-08-06 live test: `$a * b = c^2$` → `\ * b = c^2\` bug still
  present in 0.1.7). Trigger words deduplicated (merged folder-batch
  synonyms).
- *Why*: an agent reading three different versions cannot decide which
  behaviour to expect.

---

## [0.1.6-r3] — 2026-07-03 (legacy version, pre-fork)

### Fixed — darwin round 2 (independent re-eval, baseline 81.7 → R3 87.4)
- **D2 deterministic pad rule** (dim8, +2.3): vertical-merge fix now pads
  to `expected_cols`, maps md cells to HTML `<tr>` by document order using
  `rowspan`/`colspan`, and fills empty cells with `|  |` (blank, not `\|`).
  Added D2 worked example.
- **Encrypted chat-vs-desktop routing** (dim8): chat context → keyring
  one-liner, never pops CredUI; interactive desktop → CredUI dialog.
- **Runtime Warnings dedup** (dim7, +1.2): 6-row repeated table → 1-line
  cross-reference + 2-line non-table conditions.
- **Unknown-defect two-level triage** (dim1+dim4, +2.2): Unknown with
  `HTML_REFERENCE` → best-effort silent fix + `<!-- AI-uncertain -->`;
  Unknown without `HTML_REFERENCE` → 🔴 STOP ASK USER (the single stopping
  point). Narrowed trigger, kept the stop.
- *Why first round was discarded*: self-eval scores (92.1) were optimistically
  biased by dim9 anti-pattern #1 (self-grade self-edit dry_run); independent
  judge re-eval landed at 81.7 — a 10.4-point delta. SkillLens empirically
  shows LLM-as-judge accuracy of 46.4%, so all rounds after this use
  independent judge agents.

### Removed
- Legacy shared `default` keyring fallback in `_decrypt.py` (line 14):
  one credential leak should not compromise all files. Each file now
  resolves by stem only.

---

## Historical incidents encoded as Do-NOT rules

The 14 `⛔ Do NOT` rules in SKILL.md are each grounded in a real incident
(2026-06..07). They are not theoretical — every rule has a date and a file.
When adding a new rule, state the incident in the CHANGELOG so the next
maintainer understands why the rule exists.
