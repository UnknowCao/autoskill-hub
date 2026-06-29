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

### 1b. Update Policy

When new information from an ingested source conflicts with existing wiki content,
follow this policy. Never silently overwrite curated knowledge.

| Scenario | Action |
|----------|--------|
| New claim **contradicts** existing claim | Keep both. Note each with date + source. Set `contested: true` in frontmatter. Add `<!-- ⚠️ Contradiction: [claim A] (source X, date) vs [claim B] (source Y, date). Review needed. -->` at page top. Flag for user review. |
| New claim **refines** existing claim (more recent data, more precise) | Update the claim. Append "(updated: [date], per [source])" to the sentence. Keep the old claim as an HTML comment for audit trail. Bump `updated` date. |
| New claim **replaces** existing claim (source explicitly retracts or supersedes) | Replace the claim. Add `<!-- Superseded: [old claim] ([old source], [old date]) -->` above the new text. Bump `updated` date. |
| New source **adds** orthogonal information | Append to the page as a new section or paragraph. Link to source via `^[raw/...]` provenance marker. |
| Single-source claim, fast-moving domain | Set `confidence: low` or `medium`. Never `high` for single-source claims. |
| ≥3 sources agree on a claim | Set `confidence: high`. Add `^[raw/...]` markers for each supporting source. |
| Source is opinion/editorial (not research/standard) | Set `confidence: low`. Note in text: "(industry opinion)" or "(vendor claim)". |

**Contested pages:** When `contested: true` is set, lint reports it as Info severity.
The user should periodically review contested pages and resolve conflicts.

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

## Failure Modes

When an operation fails, follow the if-then fallback chain. Do NOT silently skip or guess.

| # | Operation | Trigger condition | First-line fix | Still fails → fallback |
|---|-----------|-------------------|---------------|----------------------|
| F1 | URL extraction | `web_extract` returns empty or error | Retry once after 5s. If the URL redirects, follow the redirect and retry. | Try `archive.org` snapshot of the URL. If that also fails → ask user to paste the content directly. Log failure in `log.md`. |
| F2 | markitdown conversion | Conversion throws exception | Store original file in `raw/` with frontmatter `status: unconverted`. No `.md` companion file. | Inform user which file failed and why. Suggest alternative: manual copy-paste, OCR re-scan, or skip. Lint check ⑨ will surface unconverted files. |
| F3 | markitdown partial output | Output is garbled, empty, or truncated | Generate `.md` but set `quality: low` in frontmatter. Prepend `<!-- ⚠️ Low-quality conversion. Review before citing. -->`. | Inform user. Suggest re-converting with different markitdown settings or manual correction. Lint check ⑩ flags low-quality conversions. |
| F4 | _lint.py execution | Script not found or Python unavailable | Run manual checks: read `index.md`, scan `[[wikilinks]]`, check frontmatter fields individually. | Report which checks could not be automated. Perform the 5 most critical checks manually (broken links, index completeness, orphans, frontmatter, stale). |
| F5 | index.md corruption | `index.md` missing, empty, or unparseable | Rebuild `index.md` by scanning all `.md` files in `entities/`, `concepts/`, `comparisons/`, `queries/`. Extract titles from frontmatter. | If frontmatter is also missing from pages, use first `# heading` as title. Warn user about degraded index quality. |
| F6 | Query returns no results | No relevant pages found in index or via `search_files` | Tell the user: "No existing wiki pages cover this topic." Suggest related pages if any partial matches exist. | Offer to create a stub page from the user's question. Do NOT fabricate content. |
| F7 | Archive target missing | Page to archive doesn't exist at expected path | Check `_archive/` — was it already archived? Check for renamed files. | Report to user: "Page X not found at expected path. Already archived or renamed?" Skip this page, continue with remaining archive candidates. |
| F8 | Bulk ingest partial failure | ≥1 source in a batch fails (extraction, conversion, or parse) | Continue processing remaining sources. Log each failure with the specific source and error. | After batch completes, report: "N/M sources ingested successfully. K failed: [list]." Offer to retry failures individually. |
| F9 | sha256 computation failure | `_sha256.py` missing or file unreadable | Compute inline: `hashlib.sha256(file_content.encode()).hexdigest()`. | If file too large for memory, read in chunks. If still fails, skip sha256 verification for this ingest — mark `sha256: unverified` in frontmatter. |
| F10 | log.md rotation | `log.md` ≥500 entries or write fails | Rename `log.md` → `log-YYYY.md`. Create fresh `log.md` with header `# Log — YYYY`. | If rename fails (permissions), append `<!-- LOG ROTATION NEEDED: ≥500 entries -->` to top of log.md and continue. |
| F11 | Page size exceeds 200 lines | Lint flags page for split | Propose split candidates to user: identify logical sub-topics within the page. | If no logical split point exists, add a "Quick Navigation" table of contents at the top instead. Lint check ⑪ reports it as P1 but does not block. |
| F12 | Inbound wikilink update (mass archive) | Archiving a page that has ≥20 inbound `[[wikilinks]]` across the wiki | Present the full inbound-link list to user. Ask: "Update all N inbound links to '(archived)' or handle manually?" | If user chooses auto-update, replace each `[[archived-page]]` with `archived-page (archived)` in all referring pages. Log every page modified. |

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

## Anti-Patterns（不要做的事）

> ⚠️ Each of these degrades the wiki. Violating any of them triggers lint or data loss.

| # | ❌ Don't | Why it's harmful | ✅ Do instead |
|---|---------|-----------------|--------------|
| A1 | **Modify files in `raw/`** | Breaks source immutability. Sha256 drift. Lost audit trail. | Corrections go in wiki pages. If the source itself is wrong, note it in the wiki page: "Source claims X, but [reason]." |
| A2 | **Skip orientation on session start** | Creates duplicate pages. Misses cross-references. Contradicts schema conventions. | Always read SCHEMA → index → recent log before any operation. See Resuming section. |
| A3 | **Skip updating index.md or log.md** | Wiki becomes unnavigable. Search breaks. No activity history. | Update both after every ingest, query filing, archive, or lint run. |
| A4 | **Create pages for passing mentions** | Noise drowns signal. Index bloat. Broken wikilinks multiply. | Follow SCHEMA.md Page Thresholds. A name in a footnote ≠ an entity page. |
| A5 | **Create pages without `[[wikilinks]]`** | Orphan pages are invisible. No graph connectivity. Unfindable. | Every page must link to ≥2 other pages. Check that existing pages link back. |
| A6 | **Skip frontmatter on wiki pages** | No searchability. No staleness detection. No tag filtering. | Every page: `title`, `type`, `tags`, `created`, `updated`, `sources`, `confidence`. |
| A7 | **Use freeform tags** | Tag sprawl. Inconsistent filtering. Lint check ⑫ flags unknowns. | Only use tags from SCHEMA.md taxonomy. Add new tags to SCHEMA.md first. |
| A8 | **Silently overwrite contradictory claims** | Destroys curated knowledge. Loses provenance. User never sees the conflict. | Follow Update Policy: keep both claims with dates+ sources, set `contested: true`, flag for user. |
| A9 | **Mechanically diff source versions** | Format noise (pagination, numbering changes) triggers false positives. Misses semantic changes. | Perform fact-checking reconciliation (see Reconciliation Pass). Compare claims, not text. |
| A10 | **Re-convert unchanged files** | Wastes compute. Overwrites stable .md with identical output. | Compare `original_sha256:` first. If unchanged → skip conversion and ingestion entirely. |
| A11 | **Skip asking before mass-updating (≥10 pages)** | User loses control. Accidental bulk changes without review. | 🔴 CHECKPOINT C4: present scope, wait for confirmation. |
| A12 | **Let log.md grow unbounded** | Unreadable. Slow to parse. Hard to find recent activity. | Rotate at ≥500 entries: rename `log-YYYY.md`, start fresh. Lint check ⑬. |
| A13 | **Create pages from single low-confidence source without marking** | Misleads future queries. Reader assumes well-supported claim. | Set `confidence: low` or `medium` for single-source, opinion, or fast-moving claims. |
| A14 | **File every query answer as a wiki page** | Clutters queries/ and comparisons/. Trivial lookups pollute the knowledge base. | Only file answers that are substantial (comparison, deep dive, novel synthesis). Use C6 checkpoint. |

## Best Practices（应该做的事）

- **Orient first, every session** — SCHEMA → index → recent log. Non-negotiable.
- **Frontmatter on every page** — `title`, `type`, `tags`, `created`, `updated`, `sources`, `confidence`.
- **Tags from taxonomy only** — extend SCHEMA.md before using new tags.
- **Cross-reference aggressively** — ≥2 `[[wikilinks]]` per page. Check backlinks.
- **Provenance for synthesis** — `^[raw/...]` markers when ≥3 sources contribute to a page.
- **Confidence for every claim** — low/medium/high based on source count and quality.
- **Log everything** — every ingest, query filing, archive, lint run. Append-only.
- **Keep pages under 200 lines** — split at logical boundaries. Add TOC if unsplittable.
- **Reconciliation, not diff** — fact-check claims against new source version. Categorize impact.
- **Rotate log at 500 entries** — rename to `log-YYYY.md`, start fresh.
