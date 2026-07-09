---
name: doors-extractor
description: Extracts raw data from IBM DOORS and processes it using reusable library Python scripts. Use this skill for tasks like "get released requirements", "filter test cases", "export DOORS data", "extract DOORS data", "search DOORS requirements", "analyze DOORS module", "query DOORS attributes", "get test cases from DOORS", "提取DOORS数据", "导出需求", "查询DOORS模块", "获取已发布需求", "筛选测试用例" or similar requests in a strictly Read-Only manner.
---

# DOORS Extractor

Extracts and processes data from IBM DOORS via DXL. **Read-Only only.**

## Quick Reference

| Intent (EN / 中文) | Go to |
|---|---|
| "Extract / export from DOORS" · "导出/提取DOORS数据" | [§1.1 Phase 1](#11-phase-1--prepare) → [§1.2 Phase 2](#12-phase-2--extract) |
| "Filter / process already-extracted data" · "筛选/处理已提取数据" | [§1.3 Phase 3](#13-phase-3--process) |
| "Extraction failed / error" · "提取失败/报错" | [§2 Error Recovery](#2-error-recovery) |
| "First-time setup" · "首次配置" | [§4 Configuration](#4-configuration) |
| "Add custom processing logic" · "添加自定义处理脚本" | [§1.3 OPTION B](#option-b-extend-library) |

**Key rules at a glance** (full table in [§3 Anti-Patterns](#3-anti-patterns-red-lines)):

- 🔴 Always `mode=sync, timeout=1200000` for extraction — never async
- 🔴 Always `cmd /c python ...` — never `& cmd.exe` or `python -c "import pathlib..."`
- 🔴 Never `2>&1` — stderr carries diagnostics
- 🔴 Default to `--no-gui` — only drop after explicit user consent via [§1.1 Step 4](#step-4-com-pre-flight-check--consent-gate)
- 🔴 Never declare success without `"COM extraction successful (XXX MB): <filepath>"`

---

## 1. Core Workflow

### 1.1 Phase 1 — Prepare

#### Step 1: Identify Target Module

Find the DOORS Module Path (e.g., `/Project/X/Requirements`) or URL (`doors://`).

- If no path found: ask **only** "Please provide the DOORS Module URL or Path (location)."
- **Question policy**: At most 1 required question during extraction. All questions via `vscode_askQuestions` — never plain chat text. Use fixed options for binary choices; freeform only for module path.

#### Step 2: Verify Configuration

```bash
cmd /c python .github/skills/doors-extractor/scripts/credential_manager.py status
# fallback (legacy layout)
cmd /c python .claude/skills/doors-extractor/scripts/credential_manager.py status
```

- **`configured`** (both `doors_data` and `doors_path` present) → proceed to Step 3.
- **`not configured`** or errors → run `setup`:
  ```bash
  cmd /c python .github/skills/doors-extractor/scripts/credential_manager.py setup
  ```
  This opens a tkinter dialog for `doors_data` (port@hostname) and executable path. **Do NOT proceed to extraction until `status` confirms `configured`** — running extract on a missing config causes a silent DOORS-launch fallback that wastes several minutes.

#### Step 3: 🔴 CHECKPOINT · Cache Scan

Search `**/*_raw.json` for existing raw data. Match by module name, prefer the most recent date.

- **Freshness rule**: Cache ≤ 7 days old is "fresh" and preferred. Cache > 7 days old is "stale" — still offer the binary choice but append a staleness warning: `"Found X.json (N days old, may be stale). Use this or re-extract?"`
- If raw data exists: STOP and ask **only** `"Found existing raw data X.json. Use this or re-extract from DOORS?"` (binary choice, via `vscode_askQuestions`).
  - User chooses existing data → skip Phase 2, go to [§1.3 Phase 3](#13-phase-3--process).
- If no usable cache → proceed to Step 4.

#### Step 4: COM Pre-Flight Check & Consent Gate

**MANDATORY before every Phase 2 extraction.** Do NOT skip even if the user just said "extract now."

1. **Check if DOORS is already running**:
   ```powershell
   Get-Process doors -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, Responding
   ```
   - Running AND `Responding=True` → proceed directly to Phase 2 (COM fast path, ~30 s). No consent needed.

2. **If DOORS is NOT running**, STOP and ask via `vscode_askQuestions`:
   - **Header**: "Launch DOORS?"
   - **Question**: "DOORS is not running. The extraction will launch the DOORS GUI — you'll need to log in manually. Launch DOORS now?"
   - **Options** (single-select):
     - `"Launch DOORS now (I'll log in manually)"` (recommended)
     - `"Cancel — I'll start DOORS myself first"`

3. **Branch on answer**:
   - **"Launch DOORS now"** → proceed to Phase 2 **without `--no-gui`**:
     ```bash
     cmd /c python .github/skills/doors-extractor/scripts/doors_manager.py extract --url <TARGET_URL> --output report/doors/<PROJECT>_<MODULE>_<YYYYMMDD_HHMMSS>_raw.json
     ```
     The `doors_manager.py` script handles the full lifecycle: (a) launches DOORS GUI if needed, (b) polls COM every 10 s for up to 10 min until the user completes login, (c) runs DXL extraction, (d) writes output. **The agent does NOT need to wait separately or check for GUI login — one sync `run_in_terminal` call (`mode=sync, timeout=1200000`) covers the entire sequence.**
   - **"Cancel"** → STOP. Tell the user: "Please start DOORS and log in manually, then ask me to extract again. With DOORS already running, the COM fast path (~30s) will be used and `--no-gui` will remain in effect."

**Rationale**: The GUI launch requires manual login (username/password never stored — see [§5 Security](#5-security-rules)). Auto-launching without the user present produces a hung login screen.

---

### 1.2 Phase 2 — Extract

**🔴 CHECKPOINT · Pre-Extraction Gate**: Only proceed if (a) user explicitly requests fresh data OR (b) no usable cache exists. If neither, do NOT extract.

#### Execution Rules

These apply to **every** terminal command in the extraction workflow:

| Rule | Requirement | Rationale |
|------|-------------|-----------|
| Shell | Always `cmd /c python ...` (PowerShell-compatible) | Avoids `& cmd.exe` rejection in restricted mode |
| Mode | Always `mode=sync, timeout=1200000` | Extraction completes in 30 s–3 min; async wastes credits on polling |
| Stderr | Never `2>&1` | stderr carries diagnostics; mixing yields false errors |
| Control chars | Never prepend `^U` | Copy-paste artifact that clears the shell line |
| File checks | Use `Get-ChildItem ... \| Select Name,Length,LastWriteTime` | Never `python -c "import pathlib..."` — fragile and verbose |

#### Naming Convention

Raw data files MUST include **Project Name** and **DateTime (YYYYMMDD_HHMMSS)**:

```
<PROJECT>_<MODULE>_<YYYYMMDD_HHMMSS>_raw.json
```

- HHMMSS is **MANDATORY** — date-only filenames (e.g., `_20260605_raw.json`) are a violation.
- Example: `VW_10638_SysRS_20260605_143052_raw.json`
- Output location: `report/doors/` (default).

#### Run Extraction

**Default (`--no-gui`, COM-only safety net):**

```bash
cmd /c python .github/skills/doors-extractor/scripts/doors_manager.py extract --url <TARGET_URL> --output report/doors/<PROJECT>_<MODULE>_<YYYYMMDD_HHMMSS>_raw.json --no-gui
# fallback (legacy layout)
cmd /c python .claude/skills/doors-extractor/scripts/doors_manager.py extract --url <TARGET_URL> --output report/doors/<PROJECT>_<MODULE>_<YYYYMMDD_HHMMSS>_raw.json --no-gui
```

- `--no-gui` means: ONLY attempt COM extraction on an already-running DOORS instance. If COM is unavailable, the script exits with a clear error — no auto-launch.

**After user consents to GUI launch** (via [§1.1 Step 4](#step-4-com-pre-flight-check--consent-gate)): re-run the SAME command **without `--no-gui`**.

> **⚠️ PowerShell quoting**: Do NOT use `\"` inside `cmd /c "..."` — cmd.exe doesn't recognize backslash-escaped quotes. Omit the outer `"..."` wrapper or use `""` for inner quoting.

**Expected duration**: Fast path (COM available) ~30 s. Slow path (GUI launch + login + extraction) 2–5 min for small modules, up to 25 min total.

#### Verify Success

The script output is the **only** authoritative indicator:

- ✅ **Success**: Terminal contains `"COM extraction successful (XXX MB): <filepath>"`
- ❌ **Not successful**: This exact signal is absent.

**Never** check file existence/size before this signal appears — early file checks during DXL processing are PROHIBITED. If the signal is absent after timeout, extraction failed; go to [§2 Error Recovery](#2-error-recovery).

#### Follow-up: Change Detection Baseline

After a successful extraction, generate the per-object SHA256 baseline for future diffs:

```bash
cmd /c python .github/skills/doors-extractor/scripts/library/hash_diff.py gen "report/doors/<PROJECT>_<MODULE>_<YYYYMMDD_HHMMSS>_raw.json" --module-path /<PROJECT>/<MODULE>
```

Then to see what changed vs the previous extraction:

```bash
cmd /c python .github/skills/doors-extractor/scripts/library/hash_diff.py diff "report/doors/<...>_raw.json"
```

---

### 1.3 Phase 3 — Process

**🔴 CHECKPOINT · Post-Extraction Gate**: Only enter after the success indicator ([§1.2 Verify Success](#verify-success)) is confirmed. If extraction failed, go to [§2 Error Recovery](#2-error-recovery).

**Entry Condition**: Phase 3 runs only when the user wants a **derived view** of the data (filtered subset, format conversion, change report). If the user's deliverable IS the raw JSON itself (e.g., "导出到本地 JSON 文件"), the raw file from Phase 2 is already the deliverable — **skip Phase 3 entirely** and report success.

**Never use generic tools (jq/grep/python one-liners) on raw JSON. Always use a dedicated `scripts/library/` script.**

#### Library Script Catalog

| Script | Filters By | Output | When to use |
|---|---|---|---|
| `get_released_reqs.py` | `Object_Status == "Released"` | JSON | "get released requirements" / "已发布需求" |
| `extract_nondeleted_reqs.py` | objects without deletion flags | Markdown | "get all non-deleted requirements as doc" |
| `get_swt_impact.py` | `AllocTestAuthority == "SwT"` | JSON | "get SwT-allocated requirements" |
| `hash_diff.py gen <raw>` | per-object SHA256 | `<raw>.sha256.json` | baseline for next diff / "hash the extraction" |
| `hash_diff.py diff <raw>` | abs_ref comparison | `<raw>.diff.json` | "what changed since last extraction" |

> Run `ls .github/skills/doors-extractor/scripts/library/` to detect scripts added after this doc. **If no row matches the user's intent → go directly to OPTION B; do NOT ask the user to choose a script.**

**Invocation pattern (all library scripts):**

```bash
cmd /c python .github/skills/doors-extractor/scripts/library/<SCRIPT_NAME> "<RAW_JSON>" "report/doors/<OUTPUT>.<EXT>"
# fallback (legacy layout)
cmd /c python .claude/skills/doors-extractor/scripts/library/<SCRIPT_NAME> "<RAW_JSON>" "report/doors/<OUTPUT>.<EXT>"
```

(`<EXT>` = `json` for JSON-output scripts, `md` for `extract_nondeleted_reqs.py`)

#### Output Naming Convention

Library script outputs MUST follow: `<PROJECT>_<MODULE>_<FILTER>_<YYYYMMDD_HHMMSS>.<EXT>`

- `<FILTER>` = short slug of the filter applied (e.g., `Released`, `SwT`, `NonDeleted`).
- The timestamp segment (`YYYYMMDD_HHMMSS`) is **MANDATORY** — never reuse a prior output filename.
- Example: `report/doors/VW_10638_SysRS_Released_20260702_153012.json`

**Sidecar exemption**: Artifacts emitted as `<raw_filename>.<suffix>.json` next to the raw file (e.g., `hash_diff.py` outputs `.sha256.json` / `.diff.json`) are exempt from the deliverable naming pattern — they are anchored to a specific extraction and must share its filename.

#### OPTION B: Extend Library

1. **Read schema**: Load [`references/raw-data-schema.md`](references/raw-data-schema.md) for JSON structure (attribute names, sparse-omission rule, `abs_ref` semantics).
2. **Implement**: Add a new script under `scripts/library/`. A script is considered valid when it satisfies ALL of:
   - **Read-Only**: No `write`/`update`/`delete` on DOORS objects. Only reads the raw JSON file.
   - **Stable signature**: First positional arg MUST be the raw JSON path. Any flags MUST be optional with documented defaults. Fixed arity + stable flag names across versions.
   - **Schema-aware**: Reads attribute names from the JSON `attrs` map per `raw-data-schema.md`; never hardcodes positional indices.
3. **Run**: Same invocation pattern as OPTION A, using the Output Naming Convention above.
4. **Maintain**: Add a row to the Library Script Catalog table so the next session discovers it.

---

## 2. Error Recovery

### 2.1 Quick-Ref Table

| Scenario | Symptom | First Response | If Still Failing |
|---|---|---|---|
| Config missing | DOORS launch fallback cannot find exe/data | `cmd /c python credential_manager.py setup` | Verify `DOORS_PATH` env var; check `~/.doors/config.json` exists |
| DOORS already running | COM unavailable; extraction fails | Keep session; do NOT close/restart. Run `diag_com.py`. **Most common outcome (≥90%): COM_HALF_OPEN** — wait 60 s, retry extraction once ([§2.2](#22-com-diagnostics--escalation)). | If not COM_HALF_OPEN: classify via [§2.2 Step 0](#step-0--classify-failure) anchors; follow escalation |
| `& cmd.exe` rejected | PowerShell restricted mode error | Use `cmd /c python ...` (no `&`) | Use PowerShell-native cmdlets directly |
| pathlib check attempted | `python -c "import pathlib..."` | Replace with `Get-ChildItem ... \| Select Name,Length,LastWriteTime` | — (one-shot fix) |
| Fake red "errors" | Red lines despite successful extraction | Omit `2>&1` redirection; rerun | — (artifact, not real error) |
| COM recovery timeout | Script polls 10 min then fails | Wait for DOORS GUI to become responsive (manual) | Retry extraction after DOORS idle confirmed |
| JSON corrupted | `json.JSONDecodeError` in processing | Delete corrupted `*_raw.json` | Re-extract from DOORS (Phase 2) |

For the full troubleshooting table, see [`references/error-handling.md`](references/error-handling.md).

### 2.2 COM Diagnostics & Escalation

When extraction fails AND `diag_com.py` confirms COM is unrecoverable, follow this closed-loop escalation. Do NOT leave the user at "capture logs and report failure" with no next step.

#### Step 0 — Classify Failure

Run `diag_com.py` AND `Get-Process doors`. Classify into exactly one branch using **string-match anchors** (not free interpretation):

| Combined diagnostic signals | Classification | Meaning |
|---|---|---|
| `GetActiveObject('DOORS.Application'): SUCCESS` AND `runStr test: 'DOORS COM OK'` | **COM_HEALTHY** | COM is fine; failure was transient — retry extraction once |
| `Dispatch('DOORS.Application'): SUCCESS` but `runStr test FAIL` | **COM_HALF_OPEN** | DOORS GUI launched but not ready — wait 60 s, retry once |
| `Get-Process`: no doors process AND `No doors.exe process found!` | **NO_PROCESS** | DOORS not running — ask user to launch GUI + login, then retry once |
| `Get-Process`: doors exists, `Responding=False`, AND all GetActiveObject/Dispatch FAIL | **PROCESS_HUNG** | DOORS hung — ask user to kill PID via Task Manager, then retry once |
| `ERROR: pywin32 not installed` | **ENV_BROKEN** | Python env issue — stop, ask user to reinstall pywin32; do NOT retry |

#### Step 1 — Collect Diagnostics

Save `diag_com.py` stdout + failed extraction's stderr to `report/doors/_diag_<YYYYMMDD_HHMMSS>.log`.

#### Step 2 — Branch Action

- `COM_HEALTHY`: retry extraction (Phase 2) **exactly ONCE** — COM is fine, failure was transient.
- `COM_HALF_OPEN`: wait 60 s for DOORS GUI to finish initializing, then retry extraction (Phase 2) **exactly ONCE**.
- `NO_PROCESS`: ask user to launch DOORS GUI + log in manually, then retry extraction (Phase 2) **exactly ONCE**.
- `PROCESS_HUNG`: ask user to kill the hung DOORS process (PID from `Get-Process doors`) via Task Manager, re-launch DOORS + log in, then retry extraction (Phase 2) **exactly ONCE**.
- `ENV_BROKEN`: do NOT retry; stop and report. Ask user to `pip install pywin32` in the Python environment used by the skill scripts.

#### Step 3 — Hard Limit & Hand-Off

If the single retry also fails, STOP. Do not enter a retry loop. Hand off using this exact template:

```
DOORS extraction failed twice. Diagnostic classification: <CLASSIFICATION>.
Diag log: report/doors/_diag_<TIMESTAMP>.log
DOORS process: <PID from tasklist, or "not running">
Requested action: <launch DOORS / kill PID / reinstall pywin32 / escalate to DOORS admin for licensing>
```

**Process check command** (for PID lookup — use this, not `python -c`):

```powershell
Get-Process doors -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, Responding
```

(`Responding=False` = hung.)

---

## 3. Anti-Patterns (RED LINES)

> **Read before any DOORS operation.** Every entry is a PROCESS VIOLATION. The three-phase extraction sequence ([§1.1→§1.2](#1-core-workflow)) MUST be preserved — early file checks before COM recovery confirmation are PROHIBITED, and success MUST be declared only by the official signal.

| # | ❌ Never do this | ✅ Do this instead | Why | See § |
|---|---|---|---|---|
| A1 | `run_in_terminal(mode="async")` + `get_terminal_output` loop | `mode=sync, timeout=1200000` | Async polling wastes credits on unchanged output | 1.2 |
| A2 | `2>&1` stderr redirection | Omit redirection | stderr carries diagnostics; mixing yields false errors | 1.2 |
| A3 | `^U` prefix on any command | Strip leading control chars before send | `^U` is copy-paste artifact that clears the shell line | 1.2 |
| A4 | `python -c "import pathlib; ..."` for file checks | `Get-ChildItem ... \| Select Name,Length,LastWriteTime` | `python -c` pathlib probe is fragile and verbose | 1.2, 2.1 |
| A5 | File existence check BEFORE COM recovery confirmed | Wait for `"COM extraction successful (XXX MB)"` signal | Early checks during DXL processing are prohibited | 1.2 |
| A6 | Declare success without the official signal | Treat absence of signal as NOT successful | Authoritative indicator only | 1.2 |
| A7 | Any `write`/`update`/`delete`/`create`/`link`/`save` in DOORS | Refuse: "Read-Only only" | Data corruption prevention | 5 |
| A8 | Store/pass username or password via CLI args | GUI login only | Security | 5 |
| A9 | Modify `scripts/doors_manager.py` | Put custom logic in `scripts/library/` | Core script is LOCKED/READ-ONLY | 5 |
| A10 | Close/restart DOORS client on COM failure | Keep session; run `diag_com.py`; classify via [§2.2](#22-com-diagnostics--escalation) | Restart loses state; [§2.2](#22-com-diagnostics--escalation) gives objective classification + 1-retry escalation | 2.2, 5 |
| A11 | Ask >1 question during extraction intent | At most 1 required (module location) | Credit conservation | 1.1 |
| A12 | Use generic tools (jq/grep) for processing raw JSON | Always use a `scripts/library/` script | Schema-aware processing | 1.3 |
| A13 | Call `doors_manager.py extract` when DOORS is not running, without user consent | Pre-flight check COM + `Get-Process doors`; if DOORS not running, ask user via `vscode_askQuestions` before launching GUI. **Always use `--no-gui` by default** — only drop the flag after explicit user consent. | GUI launch requires manual login; auto-launching without consent disrupts user's workflow. `--no-gui` provides script-level defense-in-depth. | 1.1, 1.2 |

---

## 4. Configuration

Local DOORS launcher configuration is stored in `~/.doors/config.json`. Only non-secret fields: `doors_data` (port@hostname) and `doors_path`. Username/password are never stored; login is GUI-only.

**Path compatibility**: Primary path `.github/skills/doors-extractor/`; legacy fallback `.claude/skills/doors-extractor/`.

### Setup

```bash
cmd /c python .github/skills/doors-extractor/scripts/credential_manager.py setup
# fallback (legacy layout)
cmd /c python .claude/skills/doors-extractor/scripts/credential_manager.py setup
```

Opens a tkinter dialog for `doors_data` and executable path.

### Check Status

```bash
cmd /c python .github/skills/doors-extractor/scripts/credential_manager.py status
```

### Clear

```bash
cmd /c python .github/skills/doors-extractor/scripts/credential_manager.py clear
```

---

## 5. Security Rules

1. **IMMUTABLE CORE**: `scripts/doors_manager.py` is LOCKED/READ-ONLY. No modifications.
2. **READ-ONLY**: Any DXL or Python code performing `write`/`update`/`delete`/`create`/`link`/`save` in DOORS is prohibited. Refuse with: "Sorry, I am restricted to Read-Only operations on DOORS to prevent data corruption."
3. **NO PASSWORD STORAGE**: Username/password never stored or passed via CLI. Login is GUI-only.
4. **NO PASSWORDS IN LOGS**: Never print DOORS passwords in any output stream.
5. **TRUST SENTINEL**: The manager script uses a sentinel file mechanism. Do not interrupt.
6. **ORDER INTEGRITY**: COM recovery → I/O wait → file validation. See [`references/extraction-protocol.md`](references/extraction-protocol.md).
7. **SEPARATION**: Custom logic in `scripts/library/` only.
8. **DIAGNOSTICS**: Run `scripts/diag_com.py` when COM fails unexpectedly.

---

## 6. References

Load as needed:

- **[`references/raw-data-schema.md`](references/raw-data-schema.md)**: JSON structure and attribute names. Read before generating processing scripts.
- **[`references/error-handling.md`](references/error-handling.md)**: Full troubleshooting table. Read when errors occur beyond the [§2.1 Quick-Ref](#21-quick-ref-table).
- **[`references/extraction-protocol.md`](references/extraction-protocol.md)**: Mandatory three-phase extraction sequence (COM recovery → I/O wait → file validation). Read before any extraction.
