---
name: markitdown-enhanced
description: "Enhanced file & document to Markdown conversion (based on markitdown 0.1.6). Supports DOCX, PDF, PPTX, XLSX, HTML, CSV, JSON, XML, images (OCR), audio, YouTube, EPubs. Enhancements: auto fix formula escaping ($...$), encrypted file detection & decryption via Windows Credential Manager, complex table structure validation with FULLY AUTOMATIC AI correction (no user prompt for known defects). Use when: 转换文件, 文档转md, docx转markdown, SOR转换, 技术文件转换, convert to markdown, file to md, document extraction, 文件提取, 格式转换, 加密文件解密转换."
---

# MarkItDown-Enhanced — File to Markdown Conversion

Enhanced version of Microsoft MarkItDown (v0.1.6). Converts files to Markdown
with baked-in fixes for known issues, encrypted file handling, and table
structure validation.

## Quick Start

### Installation

```bash
pip install "markitdown[all]" msoffcrypto-tool keyring mammoth
```

### Command-Line

```bash
# Single file with all enhancements (formula fix + table detect + metadata header)
# Exit codes: 0 = clean; 1 = table errors detected (sidecar .errors.md written).
# IMPORTANT: exit code 1 means the AI MUST auto-fix the .md immediately per
# the Stage-2 AUTO-FIX POLICY below — do NOT ask the user, do NOT wait.
python scripts/_convert_core.py document.docx -o output.md

# Batch convert a directory in parallel — same full pipeline as single-file
# (encryption + formula fix + table detect + metadata header), via per-file
# delegation to _convert_core.convert_file(). Skips MS Office lock files (~$*).
# Exit codes: 0 = clean; 1 = any failure OR any sidecar written (stage-2 fix needed).
python scripts/batch_convert.py input_dir/ output_dir/ --extensions .docx --workers 4

# Scan for encrypted files (no conversion)
python scripts/_convert_core.py --scan-encrypted input_dir/

# Convert with table detection disabled (faster for simple docs)
python scripts/_convert_core.py document.docx --no-table-detect -o output.md

# Convert without the metadata header (Source/Format/--- block)
python scripts/_convert_core.py document.docx --no-metadata -o output.md
python scripts/batch_convert.py input_dir/ output_dir/ --no-metadata

# Standalone: fix formula escaping in existing .md files
python scripts/fix_formula_escaping.py output.md
python scripts/fix_formula_escaping.py --dir md_output/

# Standalone: scan for encrypted files and credential status
python scripts/_decrypt.py input_dir/
```

### Python API

```python
from markitdown import MarkItDown

# Basic usage with enhanced post-processing
from fix_formula_escaping import fix_formulas_in_text

md = MarkItDown()
result = md.convert("document.docx")
text, n_fixes = fix_formulas_in_text(result.text_content)
print(f"Fixed {n_fixes} formula escaping issue(s)")

# Encrypted file handling
from _decrypt import detect_encrypted, decrypt_docx

encrypted = detect_encrypted("input_dir/")
for f in encrypted:
    buf = decrypt_docx(f)  # reads password from Credential Manager
    if buf:
        result = md.convert_stream(buf, file_extension=".docx")

# Table structure validation (B+D architecture)
import mammoth
from _table_detect import detect_table_issues, format_issues_for_ai

with open("document.docx", "rb") as f:
    mammoth_html = mammoth.convert_to_html(f).value
issues = detect_table_issues(mammoth_html, result.text_content)
print(format_issues_for_ai(issues))
```

## Enhancement Pipeline

Every conversion runs through three stages automatically:
1. **Pre-conversion**: detect encrypted files, prompt for credentials
2. **Conversion**: standard markitdown docx→md
3. **Post-conversion**: formula escaping fix, table structure validation

## ⛔ Do NOT — Anti-patterns & Red Lights

> **Read this before any conversion.** These are recurring failure modes from real
> incidents (2026-06..07). Doing any of these silently corrupts output or leaks secrets.

| # | Do NOT | Why it breaks | Do instead |
|---|--------|---------------|------------|
| 1 | **Ask the user before fixing a KNOWN defect** (D1 formula, D2 column-shift, D6 degenerate-merge, nested, D3, D4) | Violates the AUTO-FIX POLICY — default is **fully automatic**. Asking per-table creates noise the user explicitly opted out of. | Fix/annotate silently, end with a **one-line summary**. Only UNKNOWN/novel defects may prompt. (See "Stage 2 — AUTO-FIX POLICY".) |
| 2 | **Store passwords via `cmdkey` or the Credential Manager GUI** | These store *Windows Generic Credentials*, which `keyring`'s default backend cannot read → lookup returns `None` → "No credential found" even though `cmdkey /list` shows it (confirmed S06_protected, 2026-07-03). | Store via Python `keyring` only: `keyring.set_password('markitdown-enhanced', '<stem>', '<pw>')`. |
| 3 | **Type/copy a plaintext password into chat or `vscode_askQuestions`** | Password routes through the model → ends up in chat history/logs. | Never read secrets yourself. Give the user the keyring one-liner to run in their own terminal; reload after. |
| 4 | **Leave only an HTML comment for a nested table** (`<!-- ... -->`) | Downstream LLM/RAG pipelines often strip HTML comments → the flattened md table alone is semantic garbage. | Write a **body blockquote** description + keep the flattened table below + `<!-- AI-describe ... -->` comment. (See nested_table in Stage 2.) |
| 5 | **Naively regex-repad columns when you see a short row** | Cannot distinguish D2 vertical-merge (needs repad) from a legitimately fewer-column row or horizontal merge → silent data corruption on T9/T7-type tables. | Trust the Stage-1 sidecar (`Fixable by AI: YES/NO`) — only fix what the sidecar flags; never heuristic-guess. |
| 6 | **Reorder pipeline: formula-fix / table-detect BEFORE the metadata header** | Sidecar absolute line numbers would no longer match the final file → AI edits the wrong lines. | Header is injected **before** table-detect by design — do not change this order. |
| 7 | **Use PowerShell `Set-Content -Encoding UTF8` / `Add-Content` on the `.md` output or `.errors.md`** | Corrupts CJK → mojibake; on TSV/CSV also destroys separators (see AGENTS.md). | Edit `.md` only with `replace_string_in_file` / `multi_replace_string_in_file` / `create_file`. |
| 8 | **Delete the sidecar `.errors.md` before fixing, or skip deleting it after** | Before-fix delete → you lose the CAUSE/HTML_REFERENCE needed to fix. After-fix skip → Stage-1 re-flags stale issues on rescan. | Read sidecar → fix all Known issues → **then** delete sidecar (signals Stage-2 complete). |
| 9 | **Report a per-table prompt / multi-paragraph status** | User opted into silent auto-fix; per-table prompts are exactly what they disabled. | One-line summary at the end (e.g. "5 tables auto-fixed, 1 annotated, sidecar deleted"). |

**Decision shortcut**: if an action is about to ask the user something other than an
UNKNOWN defect or a missing credential, STOP — it's almost certainly an anti-pattern above.

## Encrypted File Handling

Detects password-protected `.docx` files and attempts decryption via
**Windows Credential Manager** (password never touches AI chat history).

**Setup** (one-time per file) — uses Python `keyring`, **not** cmdkey/Credential Manager GUI
(which stores Windows Generic Credentials that keyring's default backend cannot read):
```bash
python -c "import keyring; keyring.set_password('markitdown-enhanced', '<stem>', '<password>')"
# <stem> = filename without extension (e.g. 'S06_protected' for 'S06_protected.docx')
# Fallback: store one shared password under name 'default' for multiple files.
```

**Runtime flow**:
1. Scan input for encrypted files
2. For each encrypted file, query Credential Manager by filename
3. If credential found → decrypt in-memory → convert
4. If not found → report the file and give the user the **keyring one-liner** to run
   in their own terminal (see "Encrypted File Handling → Setup"). Do NOT ask the user
   to type the password into chat. (See Do-NOT row 3.)

### Password Security
- Passwords stored via Python `keyring` (service: `markitdown-enhanced`, name: file stem).
  On Windows the default backend stores in the user's DPAPI-encrypted profile.
- Passwords loaded directly into Python memory, never written to disk or logs
- AI never sees plaintext passwords

## Table Structure Validation

After conversion, the skill scans md output for known table issues and runs a
**two-stage pipeline**: a deterministic Python script (stage 1) detects and
reports errors with precise locations, then an AI agent (stage 2) reads the
structured report and fixes the .md file directly.

### Stage 1 — Detection (Python script `scripts/_table_detect.py`)

Scans mammoth's HTML output (ground truth, preserves rowspan/colspan) vs
the markitdown md output. When an issue is found, the script emits a
**structured error report** (written to a sidecar `<output>.md.errors.md` file
and `_convert_core.py` exits with code 1).

Each error report contains exactly three sections the AI needs:

| Section | Contents |
|---------|----------|
| **CAUSE** | Why the md is wrong (root cause + what to restore) |
| **MD_LOCATION** | `md_path` + absolute line range + affected row indices + expected/actual column counts |
| **HTML_REFERENCE** | The full untruncated `<table>` block from mammoth (ground truth to reproduce) |
| **CURRENT_MD** | The full broken md table block (for side-by-side comparison) |

Detected issue types:

| Issue | Severity | AI action |
|-------|----------|-----------|
| Vertical-merge column misalignment (D2) | P1 | Realign md table columns using HTML_REFERENCE |
| Degenerate full-merge (D6) | P1 | Drop orphaned continuation row, keep single merged cell |
| Nested table collapse | P2 | **LLM-describe**: write a natural-language description of the nesting in the md BODY (the flattened md table alone is semantic garbage for downstream LLMs). See the AUTO-FIX POLICY for the required template. |
| Cell multiline flattening (D3) | P2 | Accepted (no semantic loss) |
| Cell sublist flattening (D4) | P2 | Accepted (no semantic loss) |

### Stage 2 — AI Correction Flow

#### ⚡ AUTO-FIX POLICY (read first)

**Default behavior is FULLY AUTOMATIC correction — do NOT ask the user, do NOT
pause for confirmation.** The user has explicitly opted into auto-fix.

The flow below distinguishes only two cases:

| Case | Trigger | Action |
|------|---------|--------|
| **Known defect** (D2/D6/nested/D3/D4 — see table in Stage 1) | `Fixable by AI: YES` **or** `Fixable by AI: NO (LLM-describe ...)` | **Fix immediately, silently.** Apply the documented fix (D2 realign / D6 drop orphan) or the LLM-describe treatment (nested — write a body description), mark with the `<!-- AI-corrected ... -->` / `<!-- AI-describe ... -->` comment, delete the sidecar, report only a one-line summary at the end. Never ask. |
| **Unknown defect** | A row whose `CAUSE` does not match any defect type in the Stage-1 table | **This is the ONLY case that may stop and ask the user.** Briefly state the unknown issue, show the CAUSE + HTML_REFERENCE, and ask whether to (a) attempt best-effort fix or (b) leave annotated. |

If unsure whether a defect is "known": the known set is exactly
{D2 vertical_merge, D6 degenerate full-merge, nested_table, D3 multiline, D4 sublist}.
Anything else → treat as Unknown and ask.

#### Steps

1. Run `_convert_core.py input.docx -o output.md` (exit code 1 = table errors).
2. If `[TABLE_ERRORS] output.md.errors.md` appears in stdout, **read the sidecar file
   immediately — do not ask the user first.**
3. For each error block, classify as Known (auto-fix) or Unknown (may ask):
   - Read **CAUSE** → map to a known defect type from the Stage-1 table, or mark Unknown.
   - Read **MD_LOCATION** → open `output.md` at the exact line range.
   - Read **HTML_REFERENCE** → reproduce the correct structure in md.
   - **Known & `Fixable by AI: YES`** (e.g. D2): edit the md table in place with
     `replace_string_in_file` / `multi_replace_string_in_file`; mark with
     `<!-- AI-corrected: please verify — <defect id>: <one-line reason> -->`.
   - **Known & `Fixable by AI: NO (LLM-describe ...)`** (nested_table): the flattened
     md table is semantic garbage for downstream LLMs, so DO NOT leave only an HTML
     comment. Instead **write a natural-language description in the md BODY** above
     the broken table, then keep the flattened output below it for traceability.
     Use this exact shape (replace the bracketed parts from HTML_REFERENCE):

     ```markdown
     > **[嵌套表格说明 / Nested-table description]**
     > 本表为嵌套结构，无法用标准 markdown 表格表达。结构如下：
     > 外层为 <N> 列表格（<外层列名，逗号分隔>）。
     > 在「<承载嵌套的单元格列名>」单元格内嵌套了一个 <R>×<C> 内表，内容为：<逐行列出内表>；
     > 其余列对应：<逐列列出其他列的内容>。

     <!-- AI-describe: nested table — natural-language description above; flattened markitdown output preserved below for traceability -->
     <flattened markitdown table verbatim>
     ```

     Rules for the description: (a) it MUST be in the BODY (a blockquote `>` is
     fine — it renders as normal text and is read by LLMs, unlike HTML comments);
     (b) it MUST let a reader reconstruct the full nesting without seeing the HTML;
     (c) write in the source document's language (Chinese doc → Chinese description);
     (d) keep the flattened table below it (do NOT delete it — it is the raw
     extraction trace). Never ask the user before describing; this is auto-applied.
   - **Unknown**: this is the only branch that may stop and ask the user (see table above).
4. After fixing/annotating all known errors, **delete the sidecar `.errors.md` file**
   (signals stage 2 is complete; avoids re-detection on rescan).
5. Report a single concise summary to the user (e.g. "5 tables auto-fixed, 1 annotated,
   sidecar deleted") — not a per-table prompt. Do NOT ask "是否修复" / "should I fix?".

## Formula Escaping Fix

markitdown 0.1.6 incorrectly escapes `*` `_` `^` inside `$...$` math formulas
as `\*` `\_` `\^`, causing KaTeX parse errors. The fix runs automatically
after every conversion — no user action needed.

Applied to: `batch_convert.py`, `convert_literature.py`, `convert_with_ai.py`,
and `_convert_core.py`.

## Metadata Header

Every converted `.md` gets a small header prepended (mirroring `batch_convert.py`):

```markdown
# <title or file stem>

**Source**: <input filename>
**Format**: <input suffix>

---

<body...>
```

The header is injected **before** table-structure detection, so the absolute
line numbers reported in the sidecar `.errors.md` match the final written file.
Disable with `--no-metadata` (single-file) or `--no-metadata` (batch).

## Runtime Warnings

When converting, the skill checks for these known boundaries and warns only
when they affect semantic understanding:

| Condition | Action |
|-----------|--------|
| Vertical-merge tables found | Write sidecar `.errors.md`, exit code 1 → AI **auto-fixes** md (stage 2, no user prompt) |
| Degenerate full-merge (D6) | Write sidecar `.errors.md`, exit code 1 → AI **auto-fixes** (drop orphan row) |
| Nested tables found | Write sidecar `.errors.md`, exit code 1 → AI **auto-describes** the nesting in the md BODY (for LLM consumption), no user prompt |
| Undocumented / novel table defect | AI may stop and ask the user (the ONLY asking case) |
| Formula `\*` detected | Auto-fix silently |
| Cell multiline/sublist flattened | No action (semantically harmless) |

## Scripts

| Script | Purpose |
|--------|---------|
| `_convert_core.py` | Single-file enhanced conversion (recommended entry). Full pipeline: encryption + formula fix + table detect + metadata header. |
| `_decrypt.py` | Credential Manager integration for encrypted files |
| `_table_detect.py` | Table structure issue detection (B+D architecture) |
| `fix_formula_escaping.py` | Shared post-processing module (imported by converters) |
| `batch_convert.py` | Batch (parallel) conversion — delegates to `_convert_core.convert_file()` so capability is identical to single-file. Skips `~$*` lock files. Collects sidecar `.errors.md` paths for stage-2 fixing. |
| `convert_literature.py` | Literature conversion with formula fix injected |
| `convert_with_ai.py` | AI-enhanced conversion with formula fix injected |
| `generate_schematic.py` | Schematic diagram generation |
| `generate_schematic_ai.py` | AI schematic generation |
