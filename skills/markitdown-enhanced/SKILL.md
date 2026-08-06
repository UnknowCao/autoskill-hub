---
name: markitdown-enhanced
description: "Enhanced file & document to Markdown conversion (based on markitdown 0.1.5). Supports DOCX, PDF, PPTX, XLSX, HTML, CSV, JSON, XML, images (OCR), audio, YouTube, EPubs. Enhancements: auto fix formula escaping ($...$), encrypted file detection & decryption via keyring + native Windows CredUI dialog, complex table structure validation with FULLY AUTOMATIC AI correction (no user prompt for known defects), XLSX formula evaluation (converts =A+B cells from NaN to real values). Single-file, parallel batch, size-aware resumable batch for large sets/network drives. Use when: 转换文件, 文档转md, docx转markdown, SOR转换, 技术文件转换, convert to markdown, file to md, document extraction, 文件提取, 格式转换, 加密文件解密转换, 批量转换, 文件夹转md, 目录转markdown, bulk convert, parallel conversion, resumable batch."
---

# MarkItDown-Enhanced — File to Markdown Conversion

Enhanced version of Microsoft MarkItDown (v0.1.5). Converts files to Markdown
with baked-in fixes for known issues, encrypted file handling, and table
structure validation.

## Quick Start

### TL;DR — the whole flow on one screen

```
USER: "convert this file"  →  run: _convert_core.py <file> -o <out.md>
                                     │
        ┌────────────────────┬───────┴────────┬─────────────────────┐
        ▼                    ▼                ▼                     ▼
  exit 0 (clean)      exit 1 (table errs)  encrypted file     no output / err
  → 1-line summary    → read .errors.md    → keyring lookup    → see ⛔ Do NOT
                       → AUTO-FIX silently  → if None: CredUI     (rows 5,6,7,8:
                         (Known + Unknown-  dialog (Win)         regex-repad /
                          with-HTML; STOP                            pipeline-order /
                          only if no HTML)   → "remember" → keyring CJK-mojibake /
                       → delete sidecar      → cancel → skip file   sidecar-timing)
                                                                    CJK-mojibake /
                                                                    sidecar-timing)
```

**Golden rules**: (1) never ask the user before fixing a KNOWN defect;
(2) secrets go through `keyring` / CredUI, never chat; (3) end with one summary line.
Full anti-pattern list: see **⛔ Do NOT** below.

### Installation

```bash
pip install "markitdown[all]" msoffcrypto-tool keyring mammoth pywin32
# For XLSX formula evaluation (converts =A+B cells from NaN to real values):
pip install formulas
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

# Dynamic batch — SIZE-AWARE per-file subprocess isolation for large file sets
# (thousands of files / network drives). Inherits all enhancements (encryption +
# formula fix + table detect + metadata). Adds: dynamic timeout by file size,
# small-files-first ordering, large-file concurrency cap, lenient retry, resume.
# Driver pre-decrypts encrypted files IN-PROCESS so _PASSWORD_CACHE is shared
# (one CredUI prompt per password across all files). Sidecars collected to
# _sidecars.txt.  Exit codes: 0 = clean; 1 = any failure OR any sidecar written.
python scripts/batch_convert_dynamic.py --source standards_dir/ --recursive \
    --outdir output_md/ --workers 13 --heavy-max 3
# List input also accepted (JSON {"files":[...]} or TXT one-path-per-line):
python scripts/batch_convert_dynamic.py --source file_list.json --outdir output_md/
# Slow machine (markitdown cold-start per format import dominates) — multiply
# every timeout band; office formats (doc/xlsx/pptx) already get an automatic
# 40s cold-start floor, so this is mainly for csv/html/pdf on a very slow host:
python scripts/batch_convert_dynamic.py --source standards_dir/ --outdir output_md/ \
    --workers 6 --timeout-mult 2
```

**Slow-machine angle (2026-08-06)**: the size→timeout ladder was calibrated on
a fast host (1382-record failure log; small file ≈ 5s parse). On a slower host
markitdown's **per-format import** (mammoth/openpyxl/python-pptx), reissued in
every subprocess, dominates → a small `report.docx` measured **~31s** just to
import (before parsing even starts). The `<0.5MB→8s` band then misfires on
office files. **Mitigation, layered (do NOT start at row 14):**

| Lever | Scope | When to use |
|-------|-------|-------------|
| `--workers N` (lower it) | All formats | First thing to try — N simultaneous cold-start imports fight for CPU/disk; halving N often lets each finish within its existing band. Default 13. |
| Built-in `office_floor=40s` (automatic) | doc/docx/xls/xlsx/ppt/pptx only | Already on by default; nothing to pass. Handles the common case (office cold-start). PDF is **excluded** (its small-file fast-fail is a deliberately hung-PDF detector). |
| `--timeout-mult MULT` (escape hatch) | Every format, every band | Genuine slow host where even csv/html/pdf exceed a band. MULT applies to all files AFTER the office floor. e.g. `--timeout-mult 2` doubles every timeout. Default 1.0. |
| `_convert_core.py <file> -o out.md` (single-file, no ladder) | One file at a time | Small doc/xlsx where the run isn't worth a batch call; `_convert_core.py` has **no subprocess timeout** so a 30s import just succeeds. |

> **⚠️ CRITICAL — how to RUN `batch_convert_dynamic.py`.**
> It is a **long-running job** (thousands of files can take hours). **Never**
> run it as a foreground command / inline terminal command — it will block the
> whole session and time out (see ⛔ Do NOT row 12). **Always launch it as a
> background VS Code task** (`isBackground: true`), then poll progress with
> `get_task_output`.
>
> **Use the FROZEN task template — do NOT hand-write the task dict.** A
> copy-paste-ready task definition lives at
> [`assets/tasks/md-enh-dyn.jsonc`](assets/tasks/md-enh-dyn.jsonc) with the
> python.exe path, script path, `"type": "shell"`, `"isBackground": true`,
> `heavy-max`, and the optional flags all **frozen** (these are the
> error-prone parts and rarely change). Invoke in 4 steps:
>
> 1. **Read** `assets/tasks/md-enh-dyn.jsonc`.
> 2. **Replace exactly these 5 placeholders** (search-and-replace,
>    case-sensitive) — everything else stays verbatim:
>    | Placeholder | Replace with | Example |
>    |-------------|--------------|---------|
>    | `<LABEL>` | auto timestamp label `md-enh-dyn-YYYYMMDD-HHMM` | `md-enh-dyn-20260806-1117` |
>    | `<SOURCE>` | `--source` value: a directory, `list.json`, or `list.txt` | `K:/standards/` |
>    | `<OUTDIR>` | `--outdir` value: output markdown directory | `output/md_v1/` |
>    | `<WORKERS>` | `--workers` value (lower for slow hosts, see Slow-machine angle) | `13` (or `6`) |
>    | `<TIMEOUT_MULT>` | `--timeout-mult` value | `1` (normal) or `2` (slow host) |
>    For **list mode** (json/txt source): also delete the `"--recursive"` line.
>    `heavy-max=3` is FROZEN in the template (tuned for typical sets); the other
>    optional flags stay commented out — uncomment one only when its condition
>    holds (see the inline comments in the template).
> 3. **Pass the result to `create_and_run_task`** (workspaceFolder = the
>    workspace root). Use the `<LABEL>` you generated as the task label so you
>    can poll it in step 4.
> 4. **Monitor (do NOT block):** poll with `get_task_output` using the
>    `<LABEL>`. Every 10 files it prints
>    `[N/M] 1234s ok=.. skip=.. fail=.. timeout=.. sidecars=.. eta=..s | filename`.
>
> **The script must NOT be launched via:** in-process `_convert_core.convert_file()`
> loop, foreground terminal, non-background shell, or hand-writing the task dict
> instead of using the template — any of these wedges the session on large sets
> or reintroduces the very path/quoting mistakes the template exists to prevent.
>
> **Why a template, not a script?** The VS Code task system writes to
> `<workspace>/.vscode/tasks.json`; the skill cannot auto-write there without
> polluting each workspace. The frozen jsonc is a **portable artifact**: the
> agent reads it, fills 5 slots, and the long-running job + `get_task_output`
> monitoring loop is preserved unchanged. If the workspace venv lives outside
> `${workspaceFolder}/.venv`, see the `Environment assumption` note at the top
> of the template.
>
> **Resume after interruption:** relaunch the *same command* with a **new task
> label**. It auto-skips files whose `.md` already exists, so prior progress is
> preserved. First confirm no leftover `batch_convert_dynamic` /
> `convert_single_enhanced` python processes are still running (avoid two drivers
> writing the same `--outdir`); kill stragglers before relaunch. Pre-decrypt temp
> files (`.__dec_*`) from the prior run are cleaned up by the new run's exit.
>
> **Encrypted-set caveat:** if the set contains many encrypted files, keep
> pre-decrypt ON (default). The driver prompts CredUI **once per password** and
> shares the result across all files via `_PASSWORD_CACHE`; subprocess-per-file
> decryption (the `--no-predecrypt` path) would re-prompt N times (see ⛔ Do NOT
> row 13).

# Scan for encrypted files (no conversion)
python scripts/_convert_core.py --scan-encrypted input_dir/

# Convert with table detection disabled (faster for simple docs)
python scripts/_convert_core.py document.docx --no-table-detect -o output.md

# Convert without the metadata header (Source/Format/--- block)
python scripts/_convert_core.py document.docx --no-metadata -o output.md
python scripts/batch_convert.py input_dir/ output_dir/ --no-metadata

# Agent/CI safe: skip encrypted-file password dialog (keyring only)
python scripts/_convert_core.py encrypted.xlsx --no-prompt -o output.md
python scripts/batch_convert.py input_dir/ output_dir/ --no-prompt

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

from pathlib import Path

encrypted = detect_encrypted(Path("input_dir/"))
for f in encrypted:
    # allow_prompt=False by default: reads keyring only, never pops a dialog.
    # Pass allow_prompt=True (e.g. from an interactive converter) to fall back
    # to the Windows CredUI dialog when no keyring credential decrypts.
    buf = decrypt_docx(f)
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

Every conversion runs through three stages **automatically** (no flags needed):

| Stage | What happens | Details |
|-------|--------------|---------|
| 1. Pre-conversion | Detect encrypted files; resolve credentials; **evaluate XLSX formulas** | [Encrypted File Handling](#encrypted-file-handling), [XLSX Formula Evaluation](#xlsx-formula-evaluation) |
| 2. Conversion | Standard markitdown `docx/pdf/pptx/xlsx/... → md` | [Command-Line](#command-line) |
| 3. Post-conversion | (a) prepend [Metadata Header](#metadata-header) → (b) [Formula escaping fix](#formula-escaping-fix) → (c) [Table structure validation](#table-structure-validation) | order matters: header must come **before** table-detect so sidecar line numbers stay valid (⛔ Do NOT #6) |

## ⛔ Do NOT — Anti-patterns & Red Lights

> **Read this before any conversion.** These are recurring failure modes from real
> incidents (2026-06..07). Doing any of these silently corrupts output or leaks secrets.

| # | Do NOT | Why it breaks | Do instead |
|---|--------|---------------|------------|
| 1 | **Ask the user before fixing a KNOWN defect** (D1 formula, D2 column-shift, D6 degenerate-merge, nested, D3, D4) | Violates the AUTO-FIX POLICY — default is **fully automatic**. Asking per-table creates noise the user explicitly opted out of. | Fix/annotate silently, end with a **one-line summary**. Only an Unknown defect **with no HTML_REFERENCE** to infer from may prompt (see "Stage 2 — AUTO-FIX POLICY"). |
| 2 | **Store passwords via `cmdkey` or the Credential Manager GUI** | These store *Windows Generic Credentials*, which (a) `keyring`'s default backend cannot read → lookup returns `None` → "No credential found" even though `cmdkey /list` shows it, AND (b) CredUI silently reuses them on the next prompt → the dialog never appears. Confirmed S06_protected, 2026-07-03. | On the desktop, just let the **CredUI dialog** pop and check "remember" — it persists to keyring automatically. For CI/headless only, use the Python `keyring` one-liner (see "Headless / CI fallback"). |
| 3 | **Type/copy a plaintext password into chat or `vscode_askQuestions`** | Password routes through the model → ends up in chat history/logs. | Let the **CredUI dialog** collect the password (default desktop flow). Only for headless/CI may you point the user at the keyring one-liner to run in their own terminal; never read the password yourself. |
| 4 | **Leave only an HTML comment for a nested table** (`<!-- ... -->`) | Downstream LLM/RAG pipelines often strip HTML comments → the flattened md table alone is semantic garbage. | Write a **body blockquote** description + keep the flattened table below + `<!-- AI-describe ... -->` comment. (See nested_table in Stage 2.) |
| 5 | **Naively regex-repad columns when you see a short row** | Cannot distinguish D2 vertical-merge (needs repad) from a legitimately fewer-column row or horizontal merge → silent data corruption on T9/T7-type tables. | Trust the Stage-1 sidecar (`Fixable by AI: YES/NO`) — only fix what the sidecar flags; never heuristic-guess. |
| 6 | **Reorder pipeline: formula-fix / table-detect BEFORE the metadata header** | Sidecar absolute line numbers would no longer match the final file → AI edits the wrong lines. | Header is injected **before** table-detect by design — do not change this order. |
| 7 | **Use PowerShell `Set-Content -Encoding UTF8` / `Add-Content` on the `.md` output or `.errors.md`** | Corrupts CJK → mojibake; on TSV/CSV also destroys separators (see AGENTS.md). | Edit `.md` only with `replace_string_in_file` / `multi_replace_string_in_file` / `create_file`. |
| 8 | **Delete the sidecar `.errors.md` before fixing, or skip deleting it after** | Before-fix delete → you lose the CAUSE/HTML_REFERENCE needed to fix. After-fix skip → Stage-1 re-flags stale issues on rescan. | Read sidecar → fix all Known issues → **then** delete sidecar (signals Stage-2 complete). |
| 9 | **Report a per-table prompt / multi-paragraph status** | User opted into silent auto-fix; per-table prompts are exactly what they disabled. | One-line summary at the end (e.g. "5 tables auto-fixed, 1 annotated, sidecar deleted"). |
| 10 | **Call CredUI without first clearing stale Windows Generic Credentials** | A previous dialog "Save" (or `cmdkey /generic`) writes to the LegacyGeneric store, which CredUI silently reuses on the next prompt → **the dialog never appears** and the (possibly wrong) cached password is returned. This is the mirror of the keyring-vs-cmdkey pitfall. | `_delete_generic_credentials([stem, name, target])` runs before every `CredUIPromptForCredentials`. Persistence is managed via keyring, never via CredUI's own Save. |
| 11 | **Verify a CredUI-entered password by decrypting the whole document inside the prompt loop** | msoffcrypto's ECMA376-Agile `decrypt().finalize()` hangs for a long time on large files; doing it per-retry makes the dialog look frozen / "no UI appears". | `prompt_and_get_password` returns the user's input unverified. Correctness is checked once by the real decryption in `decrypt_docx` step 4 (cancel/wrong = skip file, per row 5/Q11). |
| 12 | **Run dynamic batch (`batch_convert_dynamic.py`) in the foreground / terminal** | Thousands of files can take hours; a foreground run blocks the session and is killed by timeout. A hang in one subprocess wedges the whole run if not backgrounded. | Launch as a **background VS Code task** (`isBackground: true`); poll progress with `get_task_output`. Resume by re-launching (it skips files whose `.md` already exists). **See the `⚠️ CRITICAL` block above the Command-Line examples for the exact task config and monitoring steps.** |
| 13 | **Skip the in-driver pre-decrypt pass (`--no-predecrypt`) for batch sets with many encrypted files** | Without it, each subprocess re-resolves the password independently → N CredUI dialogs / keyring lookups instead of 1. The `_PASSWORD_CACHE` (per-process) is lost across subprocess boundaries. | Leave pre-decrypt ON (default). It writes temp files (`.__dec_*`) to `--outdir`, cleans them up at the end. Only use `--no-predecrypt` when you know there are zero encrypted files (pure speed opt). |
| 14 | **Train the size→timeout ladder on small office files, then ship the default bands unchanged to a much slower host** | The `<0.5MB→8s` band is calibrated for a DB-less, single-PDF fast machine. On a slow host markitdown pulls in heavy per-format deps (mammoth/openpyxl/python-pptx) **per converted subprocess**, so a small `report.docx` legitimately takes ~30s just to import → the 8s band misfires and **kills every office file mid-cold-start** (the file was NOT hung; it would finish ~2s later). Treating this as a timeout list grows the fail-log with false positives. | `batch_convert_dynamic.py` already applies an **automatic 40s floor to office formats** (`.doc/.docx/.xls/.xlsx/.ppt/.pptx`); PDF is intentionally excluded (its small-file fast-fail band is a deliberately calibrated hang-detector — do NOT add `.pdf` to the floor without re-running the failure analysis). For a genuinely slow host across ALL formats (csv/html/pdf too), pass **`--timeout-mult 2`** (multiples every band; default 1.0). The [INFO] startup banner prints `office_floor=40s (...)` so you can confirm the floor is active. |

**Decision shortcut**: if an action is about to ask the user something other than an
**Unknown defect with no HTML_REFERENCE** to infer from, or a missing credential,
STOP — it's almost certainly an anti-pattern above. (A Known defect, or an Unknown
defect that still has HTML_REFERENCE, must be fixed silently.)

## Encrypted File Handling

**🔴 Routing rule (read first):**
- ℹ️ **Script-vs-agent note**: `convert_file()` defaults to `allow_prompt=True`
  (it is the script's own default). The "do NOT let a dialog pop in chat context"
  rule below is therefore enforced by the **agent** — you decide whether to call
  the script on a path that can trigger CredUI. The script itself does not know
  whether it is in chat or desktop context.
- **Chat / agent context** (no direct desktop session on the user's machine — e.g. you
  are an AI running `_convert_core.py` on the user's behalf): if keyring lookup returns
  `None`, **do NOT let a dialog pop**. Instead hand the user the one-line
  `keyring.set_password('markitdown-enhanced', '<stem>', '<pw>')` command and stop.
  Resume after they confirm they ran it.
- **Interactive desktop context** (the user is running the script themselves in a
  real Windows terminal): the CredUI dialog may pop (`allow_prompt=True`).

Detects password-protected `.docx` files and, when no usable credential is
already stored, prompts the user through the **native Windows CredUI dialog**
(in interactive desktop context only — see the routing rule above)
(`win32cred.CredUIPromptForCredentials`). The password never touches AI chat
history, the terminal, or disk.

**Runtime flow** (`decrypt_docx`, password resolution order — first that decrypts wins):
1. explicit `password=` argument (programmatic callers only)
2. process-in-memory cache (per file stem, then any previously-entered password)
3. keyring — **file stem only** (a legacy shared `default` entry was removed
   for security — one credential leak should not compromise all files; see
   `_decrypt.py` line 14 "There is intentionally NO 'default' shared fallback")
4. **CredUI dialog** — *only on the interactive conversion path*
   (`convert_file()` passes `allow_prompt=True`). The dialog shows which file
   the password is for and a "记住 / remember" checkbox. Before each prompt,
   any stale Windows Generic Credential (LegacyGeneric store, written by a
   previous dialog's "Save" or by `cmdkey`) is deleted — otherwise CredUI
   silently reuses it and **skips the dialog entirely**. Correctness of the
   entered password is verified only by the actual decryption in step 4
   (msoffcrypto), NOT inside the prompt loop — a full-document verify per
   retry hangs on large ECMA376-Agile files.
5. If the user checks "remember" → the password is persisted to keyring
   (overwriting any stale entry). If unchecked → used once in memory and dropped.

**Read-only paths never prompt.** `decrypt_docx(allow_prompt=False)` is the
default, so `--scan-encrypted` and `scan_and_report()` simply report
`missing_credential` instead of popping a dialog.

**User cancels the dialog** → that file is skipped and the run continues with
the rest (see batch_convert aggregation). The AI reports a one-line summary,
not a per-file prompt.

**pywin32 is a hard dependency** for the dialog. If missing, `convert_file`
returns an actionable error (`pip install pywin32`) instead of a raw ImportError.

### Headless / CI fallback (NOT for desktop use)

CredUI cannot display a dialog in headless environments (SSH, Windows Server
Core, Docker, CI runners, disconnected RDP sessions). For those cases only,
pre-register the password via Python `keyring` — the next desktop conversion
will then read it silently and skip the dialog:
```bash
python -c "import keyring; keyring.set_password('markitdown-enhanced', '<stem>', '<password>')"
# <stem> = filename without extension (e.g. 'S06_protected' for 'S06_protected.docx')
```
Do NOT use `cmdkey` / Credential Manager GUI for this — those store Windows
Generic Credentials that keyring's default backend cannot read (see Do-NOT #2).

### Password Security
- Passwords stored via Python `keyring` (service: `markitdown-enhanced`, name: file stem).
  On Windows the default backend stores in the user's DPAPI-encrypted profile.
- The CredUI dialog is rendered by Windows itself (not by this skill), so its
  input cannot be intercepted by skill/Python code beyond the returned string —
  this is the security rationale for choosing CredUI over a self-built tkinter window.
- Passwords live in Python memory only for the duration of decryption; the
  process cache is in-memory and cleared when the process exits. Nothing is
  written to the converted `.md` or logs.
- AI never sees plaintext passwords.

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
| Vertical-merge column misalignment (D2) | P1 | Realign md table columns using the **deterministic pad rule**: for each flagged row, (1) pad cells to `MD_LOCATION.expected_cols`; (2) map each md cell to the HTML_REFERENCE `<tr>` by document order, using `rowspan` to carry a cell into subsequent rows and `colspan` to consume `n` md columns; (3) any md column with no HTML source → fill an empty cell (`|  |`, blank between pipes — NOT escaped `\|`). Do NOT heuristic-guess alignment (see ⛔ Do NOT row 5). **Worked example** — HTML `<tr><td rowspan="2">A</td><td>B</td></tr><tr><td>C</td></tr>` over a 2-col table → md row 1 `\| A \| B \|`, md row 2 `\|   \| C \|` (the `rowspan=2` cell A carries into row 2; mark the carry with blank, not `^`). |
| Degenerate full-merge (D6) | P1 | Drop orphaned continuation row, keep single merged cell **[⚠️ roadmap — `_table_detect.py` does NOT currently emit this issue_type; only `vertical_merge` and `nested_table` are detected. Listed for completeness; detection is not yet implemented]** |
| Nested table collapse | P2 | **LLM-describe**: write a natural-language description of the nesting in the md BODY (the flattened md table alone is semantic garbage for downstream LLMs). See the AUTO-FIX POLICY for the required template. |
| Cell multiline flattening (D3) | P2 | Accepted (no semantic loss) |
| Cell sublist flattening (D4) | P2 | Accepted (no semantic loss) |

### Stage 2 — AI Correction Flow

#### ⚡ AUTO-FIX POLICY (read first)

**Default behavior is FULLY AUTOMATIC correction — do NOT ask the user, do NOT
pause for confirmation.** The user has explicitly opted into auto-fix.

The flow below distinguishes three cases (staying quiet unless structure is
truly un-inferrable):

| Case | Trigger | Action |
|------|---------|--------|
| **Known defect** (D2/D6/nested/D3/D4 — see table in Stage 1) | `Fixable by AI: YES` **or** `Fixable by AI: NO (LLM-describe ...)` | **Fix immediately, silently.** Apply the documented fix (D2 realign / D6 drop orphan) or the LLM-describe treatment (nested — write a body description), mark with the `<!-- AI-corrected ... -->` / `<!-- AI-describe ... -->` comment, delete the sidecar, report only a one-line summary at the end. Never ask. |
| **Unknown defect, has HTML_REFERENCE** | A row whose `CAUSE` does not match the known set, but the sidecar still provides a usable `HTML_REFERENCE` block | **Best-effort fix silently, do NOT stop.** Infer the correct structure from HTML_REFERENCE, apply it, and mark with `<!-- AI-uncertain: verify — <one-line reason; no documented defect matched> -->`. Surface it only in the one-line end summary (e.g. "...plus 1 uncertain best-effort fix, please verify"). This keeps the tool quiet for the ~99% of unknowns that still have ground-truth HTML to reason from. A worked example of how to best-effort is in the "Steps" section below (the **Unknown best-effort example** block). |
| **Unknown defect, NO HTML_REFERENCE** | The sidecar is missing or its `HTML_REFERENCE` block is empty/corrupt (the AI cannot safely infer structure) | 🔴 **STOP — ASK USER** (the ONLY stopping case): briefly state that no ground-truth HTML is available to infer from, show the `CAUSE` + `CURRENT_MD`, and ask whether to (a) leave annotated `<!-- AI-blocked: no HTML_REFERENCE -->` or (b) skip that table. |

If unsure whether a defect is "known": the known set **currently detected by
`_table_detect.py`** is exactly `{vertical_merge (D2), nested_table}`.
D6 / D3 / D4 are documented for completeness but **not currently emitted** —
treat any sidecar row whose `issue_type` is not `vertical_merge`/`nested_table`
as Unknown. Then apply the two-level triage in the table
(has HTML_REFERENCE → best-effort; no HTML_REFERENCE → STOP). The tool stays quiet
unless the ground-truth HTML is genuinely missing.

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
   - **Unknown**: split into two sub-branches (see table above) — if HTML_REFERENCE
     is usable, best-effort fix silently with `<!-- AI-uncertain: verify -->`;
     only if HTML_REFERENCE is missing/corrupt, `🔴 STOP — ASK USER`.

   **Unknown best-effort example** (a defect NOT in the known set, but HTML is usable):

   Sidecar `CAUSE` = "header row dropped, no defect id"; `HTML_REFERENCE` shows
   `<thead><tr><th>A</th><th>B</th><th>C</th></tr></thead>` over a 3-col table;
   `CURRENT_MD` has data rows but no header/separator. Best-effort reconstruction:

   ```markdown
   <!-- AI-uncertain: verify — header row dropped; reconstructed from HTML <thead> (no documented defect matched) -->
   | A | B | C |
   |---|---|---|
   | 1 | 2 | 3 |
   ```

   Then continue to the next error block (do not stop); surface it only in the
   end summary. If the HTML is ambiguous enough that you cannot confidently
   reconstruct (e.g. multiple plausible layouts), prefer the **LLM-describe
   blockquote** treatment (see nested_table above) over a guessed realignment —
   a wrong guess silently corrupts data, whereas a description preserves the
   source trace.
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

## XLSX Formula Evaluation

**Problem**: When an XLSX is produced programmatically (openpyxl, database export),
formula cells like `=A2+B2` are written with an **empty cached value** (`<v></v>`).
markitdown reads only the cached value (not the formula string), so all formula
cells appear as `NaN` in the Markdown output.

**Fix** (automatic, no flags needed): `_xlsx_formula_eval.py` computes every
formula cell with the pure-Python [`formulas`](https://pypi.org/project/formulas/)
library and writes the results back into the `<v>` cache tags before markitdown
reads the file. This is a **pre-conversion** step — it modifies the XLSX bytes
in-memory before handing them to the converter.

**Scope**: Only `.xlsx` files with formula cells are processed. Non-xlsx files
and xlsx files without formulas pass through unchanged. Encryption handling:
formulas are evaluated on the already-decrypted bytes.

**Dependency**: `pip install formulas`. **Before converting any `.xlsx`
containing formulas**, verify the library is present:

```bash
python -c "from _xlsx_formula_eval import is_available; print(is_available())"
```

If this prints `False`, **do NOT silently proceed and emit `NaN`** — the
`formulas` library is the only way this skill fills the `<v>` cache that
markitdown reads. Missing it is a **degraded mode**, not a transparent no-op:

> ⚠️ **Script behavior vs agent duty (claim-vs-code note — read first).**
> `_convert_core._maybe_eval_xlsx` is a *graceful no-op* wrapper: on **any**
> exception (including `ImportError` when `formulas` is missing) it returns
> the original bytes **unchanged and silently**. Therefore:
> - If you (the agent) skip the pre-check below and just call the converter,
>   the user gets `NaN`-filled output with **no warning from the script**.
> - The 🔴 STOP below is an **agent-side guardrail YOU must enforce**, not an
>   automatic script behavior — the script will not stop for you.

- 🔴 **STOP and tell the user**: "XLSX formula evaluation is disabled
  (`formulas` not installed). Formula cells will show as `NaN`. Install with
  `pip install formulas`, then re-run." Append this note to the one-line
  conversion summary. Do not return exit 0 with `NaN`-filled output as if
  the conversion succeeded cleanly.

If running in batch/CI where a stop is undesirable, document the degraded
run explicitly in the summary (e.g. "12 files converted, 2 xlsx had `NaN`
formula cells — `formulas` library not installed"). Never hide the degraded
state; silent `NaN` is a data-correctness bug (the C-4 audit issue was
precisely this class of silent loss).

**Caveat**: The `formulas` library supports a large subset of Excel functions
but not 100% (e.g. some financial functions, array formulas). Cells it cannot
evaluate are left as-is (they will still show `NaN`).

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

## References (load as needed)

- **Per-format capabilities / limitations / dependencies** (e.g. when deciding if a given PDF needs OCR, which XLSX features convert cleanly): see [references/file_formats.md](references/file_formats.md)
- **Full MarkItDown Python API** (MarkItDown class constructor, convert/convert_stream signatures, plugin options): see [references/api_reference.md](references/api_reference.md)
- **Usage examples** (common conversion patterns): see [assets/example_usage.md](assets/example_usage.md)

> Regression-test prompts (darwin rubric) live in [test-prompts.json](test-prompts.json) at the skill root.

## Runtime Warnings

The skill auto-handles all known conditions silently — **no runtime prompts**.
Table-structure conditions (D2/D6/nested/unknown) and their actions are fully
specified in **Stage 1 issue table** + **Stage 2 AUTO-FIX POLICY** + **⛔ Do NOT**
(rows 1, 5, 8, 9) — refer there, not here. The two non-table conditions are:

| Condition (non-table) | Action |
|-----------------------|--------|
| Formula `\*` / `\_` / `\^` detected | Auto-fix silently (see Formula Escaping Fix) |
| Cell multiline/sublist flattened (D3/D4) | No action — semantically harmless |

## Scripts

| Script | Purpose |
|--------|---------|
| `_convert_core.py` | Single-file enhanced conversion (recommended entry). Full pipeline: encryption + formula eval + formula fix + table detect + metadata header. |
| `_decrypt.py` | Credential Manager integration for encrypted files |
| `_table_detect.py` | Table structure issue detection (B+D architecture) |
| `_xlsx_formula_eval.py` | Evaluates XLSX formulas with `formulas` library → writes cached values so markitdown reads real numbers, not NaN |
| `fix_formula_escaping.py` | Shared post-processing module (imported by converters) |
| `batch_convert.py` | Batch (parallel) conversion — delegates to `_convert_core.convert_file()` so capability is identical to single-file. Skips `~$*` lock files. Collects sidecar `.errors.md` paths for stage-2 fixing. |
| `batch_convert_dynamic.py` | **Large-set / network-drive batch** — size-aware per-file **subprocess isolation** (dynamic timeout, small-files-first, large-file cap, retry, resume) with full enhancement pipeline. Driver pre-decrypts encrypted files in-process (`_PASSWORD_CACHE` shared → one CredUI prompt per password). Accepts `--source dir`, `--source list.json`, or `--source list.txt`. Sidecars collected to `_sidecars.txt`. |
| `convert_single_enhanced.py` | **Subprocess entry** called by `batch_convert_dynamic.py`. Thin CLI wrapper around `_convert_core.convert_file()`; emits `[SIDECAR]` markers on stdout; exit-code protocol mirrors the original markitdown batch converter. Supports `--original-name` for pre-decrypted temp files. |
| `convert_literature.py` | Literature conversion with formula fix injected |
| `convert_with_ai.py` | AI-enhanced conversion with formula fix injected |
| `generate_schematic.py` | Schematic diagram generation |
| `generate_schematic_ai.py` | AI schematic generation |
