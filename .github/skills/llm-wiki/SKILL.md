---
name: llm-wiki
description: "Markdown wiki builder — create, ingest, query, lint, archive interlinked knowledge bases. Use when user asks to create a wiki/build a knowledge base/ingest sources/query existing wiki/lint wiki/archive stale pages. Triggers: wiki, knowledge base, 知识库, ingest, 摄入, 创建wiki, lint wiki, 归档, archive."
---

# LLM Wiki

Build and maintain a compounding interlinked markdown knowledge base.
Based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
Human curates sources; agent summarizes, cross-references, files, and maintains consistency.

## Triggers

- create, build, start wiki
- ingest, add source
- query existing wiki
- lint, audit, health-check
- user references their wiki / knowledge base

## Wiki Location

Set via `WIKI_PATH` env var; defaults to `~/wiki`. The wiki is a directory of markdown files — no database, no special tooling.

## Architecture

> Full tree: `references/architecture.md`

Three layers: **raw/** (immutable sources), **wiki pages** (entities/concepts/comparisons/queries, agent-owned), **SCHEMA.md** (conventions + tag taxonomy). Run `scripts/_init.py <path>` to scaffold.

## Checkpoints

> Full catalog: `references/checkpoints.md`. 🔴 = STOP for user confirmation. 🛑 = hard stop, do not proceed.

## Session Orientation (every session)

1. Read `SCHEMA.md` — domain, conventions, tag taxonomy
2. Read `index.md` — existing pages and summaries
3. Scan recent `log.md` — last 20-30 entries
4. For large wikis (100+ pages): `search_files` for the topic at hand

## Init

1. Determine wiki path (`$WIKI_PATH` or ask; default `~/wiki`)
2. 🔴 CHECKPOINT — domain discovery. Ask: industry? key technologies? standards? source types? controversies? Do NOT auto-generate a generic schema.
3. Write `SCHEMA.md` customized to the domain → load `assets/schema-template.md`
4. Write `index.md` + `log.md`; suggest first sources

## Format Conversion (auto-triggered before ingest)

> Full spec: `references/format-conversion.md`

Invoke **markitdown skill** for non-.md files. Dual-file storage: original + converted .md in same `raw/` subdirectory. Image handling: **L1 Extract default** (no cost); L2 AI description requires 🔴 CHECKPOINT + OpenRouter API key.

On first ingest: compute `sha256:` (md body) + `original_sha256:` (original file). On re-ingest: if unchanged → skip; if changed → reconvert + Reconciliation Pass.

Conversion failure: hard → `.meta.json` companion + log; partial → `quality: low` frontmatter + lint flag.

## Ingest

1. Capture source → `raw/` (URL→web_extract, paste→file, .md→copy, non-.md→markitdown). Compute sha256 hashes.
2. 🔴 CHECKPOINT — discuss takeaways: key claims, contradictions, entity/concept candidates.

   **Entity extraction:** scan for named entities, defined terms, recurring concepts (≥2 sections), boundary objects. Discard footnote-only mentions, list items without elaboration, generic jargon. Each must clear SCHEMA.md Page Thresholds.
3. Check existing pages via index.md + `search_files`. 🔴 CHECKPOINT if ≥10 pages affected → 🛑 STOP.
4. Write/update pages: meet SCHEMA.md Page Thresholds; ≥2 `[[wikilinks]]`; tags from taxonomy only; `^[raw/...]` provenance on 3+ source pages; `confidence: low/medium` for single-source claims. Follow Update Policy on contradictions.
5. Update index.md + log.md (`## [YYYY-MM-DD HH:MM] ingest | Source Title`). Report all files created/updated.

A single source can trigger updates across 5-15 wiki pages.

## Reconciliation Pass (re-ingest with changed source)

When `original_sha256:` changed — fact-check, don't blind-diff:

1. Overwrite raw/ files with new versions
2. Find all wiki pages referencing this source (frontmatter `sources:` + grep `^[raw/...]` inline markers)
3. Fact-check each cited claim against new .md
4. Categorize: **no-change** (log/skip), **minor** (update inline + note), **substantive** (mark `contested: true`, add ⚠️ warning — never silently rewrite)
5. New v2 content → normal page creation (follow ingest steps 3-6)
6. 🔴 CHECKPOINT — report impact summary. User decides accept/revise/re-ingest. 🛑 STOP.

## Update Policy

> Full table: `references/update-policy.md`

Never silently overwrite curated knowledge. Contradiction → keep both + `contested: true`. Refinement → update + audit-trail comment. Replacement → supersede with `<!-- Superseded: ... -->`. Single-source → `confidence: low/medium`. ≥3 sources agree → `confidence: high`. Contested pages surfaced by lint for periodic review.

## Query

1. **Scope:** Read index.md → identify candidate pages. For 100+ page wikis, also `search_files` with topic keywords.
2. **Read (cap ≤8 pages):** Prioritize — ① exact entity/concept match → ② same-tag pages → ③ `[[wikilink]]`-connected pages → ④ comparisons/ involving the topic. If >8 candidates, read top-8 by tag overlap.
3. **Synthesize:**
   - **Survey** ("tell me about X"): Summarize across pages. Note `confidence` levels. Surface `contested: true` conflicts with both sides + dates + sources — do NOT pick a winner.
   - **Specific** ("what is X's Y?"): Direct answer from best-matching page, cite `[[page]]`. If multiple pages disagree → treat as Survey.
4. 🔴 CHECKPOINT — file-worthy? Criteria: **comparisons/** if ≥3 pages synthesized; **queries/** if novel cross-page insight; skip if simple lookup. User approves or declines.
5. Update log.md: `## [date] query | topic | N pages consulted`

## Lint

> Full check catalog: `references/lint-spec.md` (checks 1-15). P0=must-fix, P1=should-fix, Info.

1. **Mechanical:** Run `scripts/_lint.py <wiki_path>`. Fix all P0 before proceeding.
2. **Semantic (MANDATORY):** Spot-check ⌈√N⌉ pages across entity/concept/comparison/query types. Verify: content completeness, stale content (>90d), quality signals, contradictions, provenance.
3. **Report:** Semantic first, then mechanical. Group by severity. Log: `## [date] lint | N semantic + M mechanical issues found`

## Failure Modes

> Full chains: `references/failure-modes.md`. Log every failure, inform user, offer alternatives, continue batch remainder.

## Bulk Ingest

1. 🔴 CHECKPOINT — batch scope (N sources, estimated page impact). 🛑 STOP.
2. Cross-source entity/concept extraction (one pass)
3. 🔴 CHECKPOINT — analysis summary: creates vs updates, contradictions. 🛑 STOP.
4. Create/update pages in one pass; update index.md once
5. Single log entry: `## [date] bulk-ingest | N sources` listing creates, updates, cross-references

## Archiving

1. 🔴 CHECKPOINT — archive candidates with reasons; user may veto
2. Move to `_archive/` preserving path; remove from index.md
3. Rewrite inbound wikilinks → `archived-page (archived)`. If replacement exists, ask: redirect `[[old]]` → `[[new]]`?
4. Log

## Bulk Archive

1. 🔴 CHECKPOINT — candidates + reasons. 🛑 STOP.
2. Build inbound-link map; 🔴 CHECKPOINT — dry-run blast radius preview (referring pages, wikilink counts, redirect candidates). 🛑 STOP.
3. Archive + rewrite wikilinks in one pass per file. Redirect old→new standards if approved.
4. Rebuild index.md; single log entry

## Obsidian

Works as Obsidian vault out of the box. Set attachment folder to `raw/assets/`. Headless sync: `references/obsidian-headless.md`.

## Anti-Patterns

> Full catalog (14 items): `references/anti-patterns.md`

- **Don't modify `raw/`** — corrections go in wiki pages
- **Don't skip session orientation** — SCHEMA → index → log, every session
- **Don't skip index.md or log.md updates** — after every ingest, query, archive, lint
- **Don't create orphan pages** — ≥2 `[[wikilinks]]` per page; follow Page Thresholds
- **Don't silently overwrite contradictions** — use Update Policy and Reconciliation Pass

## Resources

### `references/`

- `architecture.md` — full directory tree + layer descriptions
- `checkpoints.md` — full C1-C10 checkpoint catalog with decision rules
- `format-conversion.md` — extension mapping, L0-L2 image handling, failure modes
- `update-policy.md` — conflict resolution 7-scenario table
- `lint-spec.md` — complete 15-check catalog (semantic + mechanical)
- `failure-modes.md` — 12 if-then fallback chains (F1–F12)
- `anti-patterns.md` — full 14-item anti-pattern catalog
- `obsidian-headless.md` — server-side Obsidian Sync setup

### `scripts/`

- `_init.py` — scaffold new wiki: `python _init.py <path>`
- `_lint.py` — mechanical health-check: `python _lint.py <wiki_path>` covers checks 1–4, 8–13, 15
- `_sha256.py` — compute SHA256: `--md <file>` (hash .md body) or `--raw <file>` (hash binary)

### `assets/`

- `schema-template.md` — full SCHEMA.md, index.md, log.md templates for new wikis
