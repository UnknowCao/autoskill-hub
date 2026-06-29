---
name: llm-wiki
description: "Karpathy's LLM Wiki: build/query interlinked markdown KB."
license: MIT
metadata:
  hermes:
    tags: [wiki, knowledge-base, research, notes, markdown, rag-alternative]
    category: research
    related_skills: [obsidian, arxiv, markitdown]
---

# Karpathy's LLM Wiki

Build and maintain a persistent, compounding knowledge base as interlinked markdown files.
Based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Unlike traditional RAG (which rediscovers knowledge from scratch per query), the wiki
compiles knowledge once and keeps it current. Cross-references are already there.
Contradictions have already been flagged. Synthesis reflects everything ingested.

**Division of labor:** The human curates sources and directs analysis. The agent
summarizes, cross-references, files, and maintains consistency.

## When This Skill Activates

Use this skill when the user:
- Asks to create, build, or start a wiki or knowledge base
- Asks to ingest, add, or process a source into their wiki
- Asks a question and an existing wiki is present at the configured path
- Asks to lint, audit, or health-check their wiki
- References their wiki, knowledge base, or "notes" in a research context

## Wiki Location

**Location:** Set via `WIKI_PATH` environment variable (e.g. in `${HERMES_HOME:-~/.hermes}/.env`).

If unset, defaults to `~/wiki`.

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
```

The wiki is just a directory of markdown files — open it in Obsidian, VS Code, or
any editor. No database, no special tooling required.

## Architecture: Three Layers

```
wiki/
├── SCHEMA.md           # Conventions, structure rules, domain config
├── index.md            # Sectioned content catalog with one-line summaries
├── log.md              # Chronological action log (append-only, rotated yearly)
├── raw/                # Layer 1: Immutable source material
│   ├── articles/       # Web articles, clippings
│   ├── papers/         # PDFs, arxiv papers
│   ├── presentations/  # PPTX slides (via markitdown)
│   ├── spreadsheets/   # XLSX, CSV (via markitdown)
│   ├── documents/      # DOCX (via markitdown)
│   ├── transcripts/    # Meeting notes, interviews; audio transcriptions
│   ├── assets/         # Images, diagrams referenced by sources
│   └── other/          # Low-frequency formats: EPUB, ZIP, JSON, XML
├── entities/           # Layer 2: Entity pages (people, orgs, products, models)
├── concepts/           # Layer 2: Concept/topic pages
├── comparisons/        # Layer 2: Side-by-side analyses
└── queries/            # Layer 2: Filed query results worth keeping
```

**Layer 1 — Raw Sources:** Immutable. The agent reads but never modifies these.
**Layer 2 — The Wiki:** Agent-owned markdown files. Created, updated, and
cross-referenced by the agent.
**Layer 3 — The Schema:** `SCHEMA.md` defines structure, conventions, and tag taxonomy.

## Checkpoint Summary

> 🔴 = STOP and wait for user confirmation. 🛑 = hard stop, do not proceed.

| # | Operation | When | What the agent must ask |
|---|-----------|------|------------------------|
| C1 | Init | Step 3 | Confirm domain scope before writing SCHEMA |
| C2 | Format Conversion | L2 images | Ask before enabling AI image description (API key required) |
| C3 | Ingest | After source analysis | Discuss key takeaways, contradictions, page-creation candidates |
| C4 | Ingest (mass update) | ≥10 pages affected | Confirm scope before batch-creating/updating pages |
| C5 | Reconciliation | After impact report | User decides accept / revise / re-ingest |
| C6 | Query | Before filing answer | Confirm before creating queries/ or comparisons/ page |
| C7 | Archiving | Before moving pages | Confirm archive candidates; user may veto individual pages |
| C8 | Bulk Ingest | Before execution | Confirm batch scope (N sources, estimated page impact) |

## Resuming an Existing Wiki (CRITICAL — do this every session)

When the user has an existing wiki, **always orient yourself before doing anything**:

① **Read `SCHEMA.md`** — understand the domain, conventions, and tag taxonomy.
② **Read `index.md`** — learn what pages exist and their summaries.
③ **Scan recent `log.md`** — read the last 20-30 entries to understand recent activity.

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
# Orientation reads at session start
read_file "$WIKI/SCHEMA.md"
read_file "$WIKI/index.md"
read_file "$WIKI/log.md" offset=<last 30 lines>
```

Only after orientation should you ingest, query, or lint. This prevents:
- Creating duplicate pages for entities that already exist
- Missing cross-references to existing content
- Contradicting the schema's conventions
- Repeating work already logged

For large wikis (100+ pages), also run a quick `search_files` for the topic
at hand before creating anything new.

## Initializing a New Wiki

When the user asks to create or start a wiki:

1. Determine the wiki path (from `$WIKI_PATH` env var, or ask the user; default `~/wiki`)
2. Create the directory structure above
3. 🔴 CHECKPOINT — ask the user what domain the wiki covers. Be specific: industry, sub-discipline, key technologies, regulatory framework. Do NOT assume or auto-generate a generic schema.
4. Write `SCHEMA.md` customized to the domain (see template below)
5. Write initial `index.md` with sectioned header
6. Write initial `log.md` with creation entry
7. Confirm the wiki is ready and suggest first sources to ingest

> **Quick scaffold:** Run `scripts/_init.py <path>` to create the directory skeleton
> and empty skeleton files in one shot. Then customize SCHEMA.md.

### SCHEMA.md Template

> Load `references/schema-template.md` for the full customizable template
> (SCHEMA.md, index.md, and log.md). Customize to the user's domain.

## Core Operations

### 0. Format Conversion (auto-triggered before ingest)

When the user provides a non-Markdown file, **invoke the markitdown skill** to convert it
to Markdown before proceeding with ingest. This is transparent to the user — part of the
automatic ingest pipeline.

**Format → raw/ subdirectory mapping:**

| Extension | raw/ subdirectory | Notes |
|-----------|-------------------|-------|
| .pdf | papers/ | Also supports URL-based ingest via `web_extract` |
| .docx | documents/ | |
| .pptx | presentations/ | |
| .xlsx, .csv | spreadsheets/ | |
| .html | articles/ | |
| .jpg, .png, .gif, .webp | assets/ | Extract EXIF + OCR |
| .mp3, .wav | transcripts/ | Transcribe to text |
| .epub | other/ | |
| .zip, .json, .xml | other/ | |

**Dual-file storage:** Both the original file AND the converted .md are stored in the
same raw/ subdirectory, with the same base name. Example: `raw/presentations/bms-design.pptx`
+ `raw/presentations/bms-design.md`.

**Embedded image handling (three levels):**

- **L0 Ignore (not recommended):** Skip images, mark placeholder `[Image]`.
- **L1 Extract (default):** Extract embedded images to `raw/assets/`, reference in
  .md via `![[image-name.png]]`. Zero additional cost, preserves visual evidence.
- **L2 AI Description (on-demand):** Use markitdown's LLM mode (requires OpenRouter API key)
  to generate text descriptions of images. 🔴 CHECKPOINT — ask the user per ingest:
  "Detected N images. Generate AI descriptions? (requires OpenRouter API key)".
  Descriptions are embedded in the .md output, dramatically improving wiki page quality
  for diagram-heavy sources. Do NOT auto-enable L2 without user consent.

**Conversion failure handling:**

- **Hard failure (markitdown throws):** Store the original file in raw/ with
  `status: unconverted` and no .md companion. Log the failure. The source is archived
  but not ingested into wiki pages. Lint reports unconverted files.
- **Partial failure (output looks garbled/empty):** Generate the .md but set
  `quality: low` in frontmatter and prepend `<!-- ⚠️ Low-quality conversion. Review before citing. -->`.
  Lint flags low-quality conversions for user review.

### 1. Ingest

When the user provides a source (URL, file, paste), integrate it into the wiki:

① **Capture and convert the raw source:**
   - **URL →** use `web_extract` to get markdown, save to `raw/articles/`
   - **Pasted text →** save to appropriate `raw/` subdirectory
   - **Markdown file (.md) →** copy directly to the appropriate raw/ subdirectory
   - **Non-Markdown file (.pdf, .docx, .pptx, .xlsx, .csv, .jpg, .png, .mp3, .wav,
     .html, .epub, .zip, .json, .xml) →** invoke the **markitdown skill** to convert
     to Markdown (see Format Conversion above for subdirectory mapping, image
     handling levels, and failure modes). Store both the original file and the
     converted .md in the same raw/ subdirectory with matching base names.
   - **On first ingest:** Name the file descriptively. Compute `sha256:` of the .md
     body. For markitdown conversions, also compute `original_sha256:` of the
     original file and record `original_file:`.
   - **On re-ingest:** Compare `original_sha256:` (or `sha256:` for URL/pasted sources).
     If unchanged → skip conversion and ingestion. If changed → reconvert (if needed),
     then proceed to **Reconciliation Pass** (section 1a below) instead of normal ingest.

② 🔴 CHECKPOINT — **Discuss takeaways** with the user: key claims, surprising findings,
   contradictions with existing wiki content, entities/concepts that meet page-creation
   thresholds. (Skip this checkpoint in automated/cron contexts — proceed directly.)

③ **Check what already exists** — search index.md and use `search_files` to find
   existing pages for mentioned entities/concepts. This is the difference between
   a growing wiki and a pile of duplicates.
   🔴 CHECKPOINT — if the analysis shows ≥10 existing pages would be created or
   updated, 🛑 STOP and confirm scope with the user before proceeding to step ④.

④ **Write or update wiki pages:**
   - **New entities/concepts:** Create pages only if they meet the Page Thresholds
     in SCHEMA.md (2+ source mentions, or central to one source)
   - **Existing pages:** Add new information, update facts, bump `updated` date.
     When new info contradicts existing content, follow the Update Policy.
   - **Cross-reference:** Every new or updated page must link to at least 2 other
     pages via `[[wikilinks]]`. Check that existing pages link back.
   - **Tags:** Only use tags from the taxonomy in SCHEMA.md
   - **Provenance:** On pages synthesizing 3+ sources, append `^[raw/articles/source.md]`
     markers to paragraphs whose claims trace to a specific source.
   - **Confidence:** For opinion-heavy, fast-moving, or single-source claims, set
     `confidence: medium` or `low` in frontmatter. Don't mark `high` unless the
     claim is well-supported across multiple sources.

⑤ **Update navigation:**
   - Add new pages to `index.md` under the correct section, alphabetically
   - Update the "Total pages" count and "Last updated" date in index header
   - Append to `log.md`: `## [YYYY-MM-DD HH:MM] ingest | Source Title`
   - List every file created or updated in the log entry

⑥ **Report what changed** — list every file created or updated to the user.

A single source can trigger updates across 5-15 wiki pages. This is normal
and desired — it's the compounding effect.

### 1a. Reconciliation Pass (re-ingest with changed source)

When re-ingesting a file whose `original_sha256:` has changed, do NOT blindly
diff old vs. new .md. Instead, perform a **fact-checking reconciliation**:

① **Overwrite raw/ files:** Replace both the original file and the .md with the new versions.

② **Identify affected wiki pages:** Search all wiki pages whose `sources:` frontmatter
   references this raw file. Read each affected page.

③ **Fact-check each assertion:** For each claim in the affected wiki pages that cites
   this source (via `^[raw/...]` provenance markers), read the corresponding section
   in the new .md and determine: does v2 still support this claim?

④ **Categorize impact:**
   - **No change needed:** Format-only changes, typo fixes, renumbering — wiki pages
     are still correct. Log and skip.
   - **Minor update:** A value/date/parameter changed — update the wiki page inline,
     bump `updated` date, append to the paragraph: "(updated per v2: [brief note])".
   - **Substantive change:** A claim is contradicted, a requirement was removed, a
     new entity appears — mark the affected wiki page `contested: true` and add a
     note at the top: `<!-- ⚠️ Source updated. Claims citing [source] need review. -->`.
     Do NOT silently delete or rewrite the user's curated knowledge.

⑤ **New content from v2:** Any entities/concepts/sections that are entirely new in v2
   should trigger normal page creation (follow ingest steps ③-⑥).

⑥ 🔴 CHECKPOINT — **Report to user:** Summarize what changed (no-change / minor / substantive
   categories), which pages are affected, and which need manual review. 🛑 STOP and wait.
   The user decides whether to accept, revise, or re-ingest. Do NOT proceed until confirmed.

### 2. Query

When the user asks a question about the wiki's domain:

① **Read `index.md`** to identify relevant pages.
② **For wikis with 100+ pages**, also `search_files` across all `.md` files
   for key terms — the index alone may miss relevant content.
③ **Read the relevant pages** using `read_file`.
④ **Synthesize an answer** from the compiled knowledge. Cite the wiki pages
   you drew from: "Based on [[page-a]] and [[page-b]]..."
⑤ **File valuable answers back** — if the answer is a substantial comparison,
   deep dive, or novel synthesis, create a page in `queries/` or `comparisons/`.
   Don't file trivial lookups — only answers that would be painful to re-derive.
   🔴 CHECKPOINT — confirm with the user before creating the page. Suggest a
   filename and section; let the user approve or decline.
⑥ **Update log.md** with the query and whether it was filed.

### 3. Lint

> **Automated check:** Run `scripts/_lint.py <wiki_path>` for a complete health check.
> The script covers all 14 checks below. No need to run manual Python for any of these.

When the user asks to lint, health-check, or audit the wiki:

| # | Check | Severity |
|---|-------|----------|
| ① | Orphan pages (no inbound wikilinks) | P1 |
| ② | Broken wikilinks (target page missing) | P0 |
| ③ | Index completeness (every page in index.md) | P0 |
| ④ | Frontmatter validation (required fields, types, tags) | P0 |
| ⑤ | Stale content (>90 days since update) | P1 |
| ⑥ | Contradictions / contested pages | Info |
| ⑦ | Quality signals (low confidence, single-source) | P1 |
| ⑧ | Source drift (sha256 mismatch in raw/) | P1 |
| ⑨ | Unconverted files (raw/ originals without .md) | P1 |
| ⑩ | Low-quality conversions (tagged + heuristic) | P1 |
| ⑪ | Page size (>200 lines → split candidate) | P1 |
| ⑫ | Tag audit (unknown vs SCHEMA taxonomy) | Info |
| ⑬ | Log rotation (≥500 entries) | P1 |
| ⑭ | Provenance markers (3+ sources, none marked) | Info |

Report findings grouped by severity. Append to log.md: `## [YYYY-MM-DD HH:MM] lint | N issues found`

## Working with the Wiki

### Bulk Ingest

When ingesting multiple sources at once, batch the updates:
1. 🔴 CHECKPOINT — present batch scope: N sources, estimated entities/concepts,
   estimated page impact (create + update). 🛑 STOP until user confirms.
2. Read all sources first
3. Identify all entities and concepts across all sources
4. Check existing pages for all of them (one search pass, not N)
5. Create/update pages in one pass (avoids redundant updates)
6. Update index.md once at the end
7. Write a single log entry covering the batch

### Archiving

When content is fully superseded or the domain scope changes:
1. 🔴 CHECKPOINT — present archive candidates to the user with reasons for each.
   User may veto individual pages. Do NOT auto-archive without confirmation.
2. Create `_archive/` directory if it doesn't exist
3. Move the page to `_archive/` with its original path (e.g., `_archive/entities/old-page.md`)
4. Remove from `index.md`
5. Update any pages that linked to it — replace wikilink with plain text + "(archived)"
6. Log the archive action

### Obsidian Integration

The wiki directory works as an Obsidian vault out of the box (`[[wikilinks]]`, Graph View, Dataview).
Set Obsidian's attachment folder to `raw/assets/`. For headless server sync, see `references/obsidian-headless.md`.

## Pitfalls

- **Never modify files in `raw/`** — sources are immutable. Corrections go in wiki pages.
- **Always orient first** — read SCHEMA + index + recent log before any operation in a new session.
  Skipping this causes duplicates and missed cross-references.
- **Always update index.md and log.md** — skipping this makes the wiki degrade. These are the
  navigational backbone.
- **Don't create pages for passing mentions** — follow the Page Thresholds in SCHEMA.md. A name
  appearing once in a footnote doesn't warrant an entity page.
- **Don't create pages without cross-references** — isolated pages are invisible. Every page must
  link to at least 2 other pages.
- **Frontmatter is required** — it enables search, filtering, and staleness detection.
- **Tags must come from the taxonomy** — freeform tags decay into noise. Add new tags to SCHEMA.md
  first, then use them.
- **Keep pages scannable** — a wiki page should be readable in 30 seconds. Split pages over
  200 lines. Move detailed analysis to dedicated deep-dive pages.
- **Ask before mass-updating** — if an ingest would touch 10+ existing pages, confirm
  the scope with the user first.
- **Rotate the log** — when log.md exceeds 500 entries, rename it `log-YYYY.md` and start fresh.
  The agent should check log size during lint.
- **Handle contradictions explicitly** — don't silently overwrite. Note both claims with dates,
  mark in frontmatter, flag for user review.
- **Don't manually edit raw/ binary files** — raw/ is immutable. If a .docx needs correction,
  fix the original and re-ingest. If a .md conversion looks wrong, flag it with `quality: low`
  and consider re-converting with different settings.
- **markitdown conversion is deterministic** — same input file → same output .md. If the
  original file hasn't changed, skip re-conversion. Use `original_sha256:` to check.
- **Reconciliation over diff** — when a source updates, do NOT mechanically diff old vs. new
  .md. Perform fact-checking against affected wiki pages (see Reconciliation Pass). format
  noise (pagination, renumbering) should never trigger contested flags.
