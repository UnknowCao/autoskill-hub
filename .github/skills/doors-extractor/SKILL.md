---
name: doors-extractor
description: Extracts raw data from IBM DOORS and processes it using reusable library Python scripts. Use this skill for tasks like "get released requirements", "filter test cases", "export DOORS data", "extract DOORS data", "search DOORS requirements", "analyze DOORS module", "query DOORS attributes", "get test cases from DOORS", "提取DOORS数据", "导出需求", "查询DOORS模块", "获取已发布需求", "筛选测试用例" or similar requests in a strictly Read-Only manner.
---

# DOORS Extractor

Extracts and processes data from IBM DOORS via DXL. Read-Only only.

## 1. References (load as needed)

- **[references/raw-data-schema.md](references/raw-data-schema.md)**: JSON structure and attribute names. Read before generating processing scripts.
- **[references/error-handling.md](references/error-handling.md)**: Troubleshooting table for extraction failures. Read when errors occur.
- **[references/extraction-protocol.md](references/extraction-protocol.md)**: Mandatory three-phase extraction sequence (COM recovery → I/O wait → file validation). Read before any extraction.

## 2. Local Configuration

Local DOORS launcher configuration is stored in `~/.doors/config.json`.
Only non-secret fields are stored: `doors_data` and `doors_path`.
Username/password are never stored; login is done manually in DOORS GUI.

Path compatibility note:
- Primary path in this repo: `.github/skills/doors-extractor/`
- Legacy compatible path: `.claude/skills/doors-extractor/`

### First-Time Setup

```bash
cmd /c "python .github/skills/doors-extractor/scripts/credential_manager.py setup"
# fallback (legacy layout)
cmd /c "python .claude/skills/doors-extractor/scripts/credential_manager.py setup"
```

This opens:
1. **tkinter dialog**: Configure DOORS Data (`port@hostname`) and executable path

### Check Status

```bash
cmd /c "python .github/skills/doors-extractor/scripts/credential_manager.py status"
# fallback (legacy layout)
cmd /c "python .claude/skills/doors-extractor/scripts/credential_manager.py status"
```

### Remove Credentials

```bash
cmd /c "python .github/skills/doors-extractor/scripts/credential_manager.py clear"
# fallback (legacy layout)
cmd /c "python .claude/skills/doors-extractor/scripts/credential_manager.py clear"
```

## 3. Anti-Patterns (RED LINES — Read First)

> Consolidated blacklist of **forbidden actions**. Every entry below is expanded with rationale in its referenced section; this table is the authoritative quick-scan checklist. Any single violation is a PROCESS VIOLATION.

| # | ❌ Never do this | ✅ Do this instead | Why | See § |
|---|---|---|---|---|
| A1 | `run_in_terminal(mode="async")` + `get_terminal_output` loop | `mode=sync, timeout=1200000` | Async polling wastes credits on unchanged output | 4.2 |
| A2 | `2>&1` stderr redirection | Omit redirection | stderr carries diagnostics; mixing yields false errors | 4.6 |
| A3 | `^U` prefix on any command | Strip leading control chars before send | `^U` is copy-paste artifact that clears the shell line | 4.1 |
| A4 | `python -c "import pathlib; ..."` for file checks | `Get-ChildItem ... \| Select-Object Name,Length,LastWriteTime` | `python -c` pathlib probe is fragile and verbose | 4.1, 6.1 |
| A5 | File existence check BEFORE COM recovery confirmed | Wait for `"COM extraction successful (XXX MB)"` signal | Early checks during DXL processing are prohibited | 4.3 |
| A6 | Declare success without the official signal | Treat absence of signal as NOT successful | Authoritative indicator only | 4.6 |
| A7 | Any `write`/`update`/`delete`/`create`/`link`/`save` in DOORS | Refuse: "Read-Only only" | Data corruption prevention | 5 |
| A8 | Store/pass username or password via CLI args | GUI login only | Security | 5 |
| A9 | Modify `scripts/doors_manager.py` | Put custom logic in `scripts/library/` | Core script is LOCKED/READ-ONLY | 5 |
| A10 | Close/restart DOORS client on COM failure | Keep session; run `diag_com.py`; classify via §6.2 Step 0 anchors | Restart loses state; §6.2 gives objective classification + 1-retry escalation | 5, 6.2 |
| A11 | Ask >1 question during extraction intent | At most 1 required (module location) | Credit conservation | 4.4 |
| A12 | Use generic tools (jq/grep) for processing raw JSON | Always use a `scripts/library/` script | Schema-aware processing | 4.7 |
| A13 | Call `doors_manager.py extract` when DOORS is not running, without user consent | Pre-flight check COM + `Get-Process doors`; if DOORS not running, ask user via `vscode_askQuestions` before launching GUI. **Always use `--no-gui` by default** — only drop the flag after explicit user consent. | GUI launch requires manual login; auto-launching without consent disrupts user's workflow. `--no-gui` provides script-level defense-in-depth. | 4.5.1, 4.6 |

## 4. Usage Workflow

### 4.1 Terminal Execution Policy (MANDATORY)

- All terminal commands in this workflow MUST be executed via `cmd /c`.
- All terminal commands MUST be executed in PowerShell-compatible form.
- **NEVER prepend `^U` (Ctrl+U control character) to any command.** Commands starting with `^U` are a copy-paste artifact and will cause the shell to clear the line or fail. Always inspect the command string before sending and strip any leading control characters.
- The following command pattern is prohibited and MUST be replaced:
    - `cmd /c "c:/person/project/10638_AI/.venv/Scripts/python.exe -c \"import pathlib; ... print('exists=', ...); print('size=', ...)\""`
- Mandatory replacement format for file verification:
    - `Get-ChildItem "C:\person\project\10638_AI\report\doors\*HSI*_raw.json" | Select-Object Name, Length, LastWriteTime`

### 4.2 run_in_terminal Mode Policy (MANDATORY — Credit Conservation)

- **ALWAYS use `mode=sync` with `timeout=1200000` for extraction commands.** DOORS extraction completes in 30s–3min; 5 minutes is a safe upper bound.
- **NEVER use `mode=async` for extraction.** Async mode requires manual polling via `get_terminal_output`, which wastes AI credits when the output has not changed.
- **NEVER call `get_terminal_output` in a loop.** The system automatically notifies when a sync command completes or times out. Repeated polling of unchanged output is a process violation.
- Correct pattern:
    ```
    run_in_terminal(command=..., mode="sync", timeout=1200000)
    → Tool waits and returns the complete output in one call. No polling needed.
    ```
- Prohibited pattern (wastes credits):
    ```
    run_in_terminal(mode="async") → get_terminal_output → get_terminal_output → ...
    ```

### 4.3 ABSOLUTE ENFORCEMENT (ZERO EXCEPTIONS)

- The extraction sequence is MANDATORY and NON-NEGOTIABLE.
- Any out-of-order action is a PROCESS VIOLATION.
- NEVER perform file checks before COM recovery is confirmed.
- NEVER declare success unless the script prints the official success indicator.
- If uncertain, DO NOT guess; continue waiting for the script lifecycle.

### 4.4 User Interaction Policy (Min Questions)

When user intent is extraction, ask at most one required question:

1. Required: DOORS module location (`doors://...` or `/Project/...` path).
2. Optional: output path only if user explicitly requests custom location.

Do not ask unrelated or speculative questions. Prefer defaults:
- output directory: `report/doors/`
- output naming: `<PROJECT>_<MODULE>_<YYYYMMDD_HHMMSS>_raw.json`
- extraction mode: run immediately once module location is known.

If cache files exist, do not ask open-ended questions. Ask one binary choice only:
- "Use latest cached raw file or re-extract from DOORS?"

All clarification questions must use the dedicated `vscode_askQuestions` interface.
Do not ask clarifying questions as plain chat text.
Question style requirements:
- concise prompt text
- fixed options when applicable (for cache/use vs re-extract)
- allow freeform input only when asking for module location path/URL

### 4.5 Phase 1: Determine Target

1.  **Identify**: Find the DOORS Module Path (e.g., `/Project/X/Requirements`) or URL (`doors://`).
    *   If no URL/Path found: Ask only "Please provide the DOORS Module URL or Path (location)."
2.  **Check Configuration**: Verify local configuration is set (run `cmd /c python .github/skills/doors-extractor/scripts/credential_manager.py status`).
    *   **If status reports `configured`** (both `doors_data` and `doors_path` present): proceed to step 3.
    *   **If status reports `not configured` OR errors out** (e.g. `~/.doors/config.json` missing, `DOORS_PATH` env unset): run `cmd /c python .github/skills/doors-extractor/scripts/credential_manager.py setup`, which opens a tkinter dialog to capture `doors_data` (port@hostname) and executable path. Only non-secret fields are stored. **Do NOT proceed to extraction until `status` confirms `configured`** — running extract on a missing config causes a silent DOORS-launch fallback that wastes several minutes.
3.  **🔴 CHECKPOINT · Cache Scan**: Search the workspace with glob `**/*_raw.json` for existing raw data. Match by module name, prefer the most recent date.
    *   If raw data exists: STOP and ask ONLY "Found existing raw data `X.json`. Use this or re-extract from DOORS?" (binary choice, via `vscode_askQuestions`)
    *   If user chooses existing data: Skip Phase 2, proceed to Phase 3 (Processing).
4.  **Extract** (only if no usable cache): Proceed to Phase 2.

### 4.5.1 Pre-Flight COM Check + User Consent Gate (MANDATORY — before Phase 2)

**When**: This gate MUST be executed whenever Phase 2 extraction is about to begin (i.e., user confirmed they want fresh data, or no cache exists). Do NOT skip this gate even if the user just said "extract now."

**Purpose**: The `doors_manager.py extract` command will auto-launch DOORS GUI if COM is unavailable. This is a heavy operation — it opens a GUI window, requires manual login, and disrupts the user's workflow. The user MUST explicitly consent before this happens.

**Procedure (sequential, do not parallelize):**

1. **Check if DOORS is already running**:
   ```powershell
   Get-Process doors -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, Responding
   ```
   If DOORS is running AND `Responding=True` → proceed to Phase 2 extraction (no consent needed; COM fast path will be used).

2. **If DOORS is NOT running**, STOP and ask the user via `vscode_askQuestions`:
   - **Question header**: "Launch DOORS?"
   - **Question**: "DOORS is not running. The extraction will launch the DOORS GUI — you'll need to log in manually. Launch DOORS now?"
   - **Options** (single-select):
     - `"Launch DOORS now (I'll log in manually)"` (recommended)
     - `"Cancel — I'll start DOORS myself first"`

3. **Branch on answer**:
   - **"Launch DOORS now"** → proceed to Phase 2 extraction. Re-run the extraction command **without `--no-gui`** so the script is authorized to launch the DOORS GUI:
     ```bash
     cmd /c python .github/skills/doors-extractor/scripts/doors_manager.py extract --url <TARGET_URL> --output report/doors/<PROJECT>_<MODULE>_<YYYYMMDD_HHMMSS>_raw.json
     ```
     The `doors_manager.py` script will handle the GUI launch and COM polling.
   - **"Cancel"** → STOP. Inform the user: "Please start DOORS and log in manually, then ask me to extract again. With DOORS already running, the COM fast path (~30s) will be used and `--no-gui` will remain in effect."

**Rationale**: This gate prevents the agent from auto-launching a DOORS GUI window without the user's knowledge. The GUI launch requires manual login (username/password, which the skill never stores), so launching without the user present just produces a hung login screen and wastes time. This aligns with §5 Rule 3 (NO PASSWORD STORAGE) — the skill never auto-authenticates, so it must never auto-launch the authentication UI either.

### 4.6 Phase 2: Extraction (Infrastructure)

**🔴 CHECKPOINT · Pre-Extraction Gate**: Only proceed if (a) user explicitly requests fresh data OR (b) no usable cache exists. If neither, do NOT extract.

**🔴 CHECKPOINT · DOORS Launch Consent Gate**: Before running `doors_manager.py extract`, execute the Pre-Flight COM Check + User Consent Gate from §4.5.1. This gate is MANDATORY — never call `doors_manager.py extract` when DOORS is not running without first obtaining explicit user consent. The gate output determines whether to proceed or stop.

1.  **Naming Convention**: Raw data file MUST include **Project Name** and **DateTime (YYYYMMDD_HHMMSS)**. The time part (HHMMSS) is **MANDATORY** — date-only filenames (e.g., `_20260605_raw.json`) are a violation. Always use the full current datetime, e.g., `VW_10638_SysRS_20260605_143052_raw.json`. The `.done` sentinel file created by DXL will automatically have the same name with `.done` appended.
2.  **Output Location**: Default to `report/doors/` under the project root.
3.  **Command** (Recommended - clean output, COM-only safety net):
    ```bash
    cmd /c python .github/skills/doors-extractor/scripts/doors_manager.py extract --url <TARGET_URL> --output report/doors/<PROJECT_NAME>_<MODULE_NAME>_<YYYYMMDD_HHMMSS>_raw.json --no-gui
    # fallback (legacy layout)
    cmd /c python .claude/skills/doors-extractor/scripts/doors_manager.py extract --url <TARGET_URL> --output report/doors/<PROJECT_NAME>_<MODULE_NAME>_<YYYYMMDD_HHMMSS>_raw.json --no-gui
    ```

    **`--no-gui` is the DEFAULT safety net.** When set, the script ONLY attempts COM extraction on an already-running DOORS instance. If COM is unavailable (DOORS not running), the script exits with a clear error instead of auto-launching the GUI. This prevents accidental GUI launch without user consent.

    **After user consents to GUI launch** (via §4.5.1 gate), re-run the SAME command but **omit `--no-gui`**:
    ```bash
    cmd /c python .github/skills/doors-extractor/scripts/doors_manager.py extract --url <TARGET_URL> --output report/doors/<PROJECT_NAME>_<MODULE_NAME>_<YYYYMMDD_HHMMSS>_raw.json
    ```
    **⚠️ Quote escaping note (PowerShell)**: When running from PowerShell via `cmd /c "..."`, do NOT use `\"` to quote inner arguments — cmd.exe does not recognize backslash-escaped quotes. Either omit inner quotes (works when paths have no spaces), or use `""` for inner quoting: `cmd /c "python ... --url ""<URL>"" --output ""<PATH>"""`. The safest approach is to omit the outer `"..."` wrapper and let cmd.exe parse arguments directly as shown above.

    **⚠️ Important**: Do NOT use `2>&1` to redirect stderr. The script uses stderr for diagnostic messages, and mixing stderr into stdout causes false "error" displays in some terminals. Omit the redirection for clean output.

4.  **Extraction Flow**: Follow the mandatory three-phase protocol — see **[references/extraction-protocol.md](references/extraction-protocol.md)**.

    Key constraint: File validation MUST occur strictly after DOORS recovery confirmation. Early file checks during DXL processing are PROHIBITED.

5.  **Expected Duration**: 
   - Fast path (COM available): 30 seconds
   - Slow path (GUI launch + login + extraction): 2-5 minutes for small modules, up to 25 minutes total wait window

6.  **Success Verification**: The script output is the authoritative indicator.
    - **Success indicator**: Terminal contains `"COM extraction successful (XXX MB): <filepath>"`
    - If this exact signal is not present, treat extraction as NOT successful.
    - See **[references/extraction-protocol.md](references/extraction-protocol.md)** for fallback file-check syntax.

7.  **Recommended Follow-up · Change Detection Baseline**: After a successful extraction, generate the per-object SHA256 baseline so the next extraction can be diffed:
    ```bash
    cmd /c python .github/skills/doors-extractor/scripts/library/hash_diff.py gen "report/doors/<PROJECT>_<MODULE>_<YYYYMMDD_HHMMSS>_raw.json" --module-path /<PROJECT>/<MODULE>
    # fallback (legacy layout)
    cmd /c python .claude/skills/doors-extractor/scripts/library/hash_diff.py gen "report/doors/<PROJECT>_<MODULE>_<YYYYMMDD_HHMMSS>_raw.json" --module-path /<PROJECT>/<MODULE>
    ```
    Then to see what changed vs the previous extraction:
    ```bash
    cmd /c python .github/skills/doors-extractor/scripts/library/hash_diff.py diff "report/doors/<...>_raw.json"
    ```

### 4.7 Phase 3: Processing (Business Logic)

**🔴 CHECKPOINT · Post-Extraction Gate**: Only enter Phase 3 after the official success indicator (§4.6 step 6) is confirmed. If extraction failed, go to §6 Error Handling — do NOT attempt to process a missing/partial raw file.

**Entry Condition**: Phase 3 runs only when the user wants a **derived view** of the data (filtered subset, format conversion, change report). If the user's deliverable IS the raw JSON itself (e.g. "导出到本地 JSON 文件" / "export the module"), the raw file from §4.6 is already the deliverable — **skip Phase 3 entirely** and report success. Do not invent processing work that the user did not ask for.

**Never use generic tools (jq/grep/python one-liners) on raw JSON. Always use a dedicated `scripts/library/` script.**

#### Library Output Naming Convention (Mandatory — prevents overwriting)

Library script outputs MUST follow: `<PROJECT>_<MODULE>_<FILTER>_<YYYYMMDD_HHMMSS>.<EXT>`
- `<FILTER>` = short slug of the filter applied (e.g. `Released`, `SwT`, `NonDeleted`).
- `<EXT>` = `json` for JSON-output scripts, `md` for `extract_nondeleted_reqs.py`.
- The timestamp segment (`YYYYMMDD_HHMMSS`) is **MANDATORY** — never reuse a prior output filename, since library runs are not cached and silent overwrite would lose the previous result.
- Example: `report/doors/VW_10638_SysRS_Released_20260702_153012.json`

**Sidecar exemption**: The convention above applies to **deliverable outputs** (filter/conversion results the user consumes). **Sidecar artifacts** that augment a raw file — emitted as `<raw_filename>.<suffix>.json` next to the raw file — are exempt. Examples: `hash_diff.py` emits `VW_10638_SysRS_..._raw.json.sha256.json` (per-object hash baseline) and `VW_10638_SysRS_..._raw.json.diff.json` (change report), both anchored to their raw file by sharing its full name. Sidecar naming is intentional — it ties the artifact to a specific extraction and survives renames, so it must NOT be reformatted into the deliverable pattern.

#### Library Script Catalog (Quick-Ref)

> Current scripts in `scripts/library/`. Run `ls .github/skills/doors-extractor/scripts/library/` to detect scripts added after this doc. **If no row matches the user's intent → go directly to OPTION B (Extend Library); do NOT ask the user to choose a script.**

| Script | Filters By | Output | When to use |
|---|---|---|---|
| `get_released_reqs.py` | `Object_Status == "Released"` | JSON | "get released requirements" / "已发布需求" |
| `extract_nondeleted_reqs.py` | objects without deletion flags (heuristic on `id`/`text`/`deleted` keys) | Markdown | "get all non-deleted requirements as doc" / raw dump to readable form |
| `get_swt_impact.py` | `AllocTestAuthority == "SwT"` | JSON | "get SwT-allocated requirements" / "software test authority items" |
| `hash_diff.py gen <raw>` | —(全量 per-object SHA256) | `<raw>.sha256.json` | 抽取后跑一次，为下次 diff 建基线 / "hash the extraction" |
| `hash_diff.py diff <raw>` | abs_ref 索引对比 vs 上次抽取 | stdout 摘要 + `<raw>.diff.json` | "上次抽取后变了哪些需求" / "what changed since last extraction" |

**Invocation pattern (all library scripts share this signature):**
```bash
cmd /c python .github/skills/doors-extractor/scripts/library/<SCRIPT_NAME> "<RAW_JSON>" "report/doors/<OUTPUT>.<EXT>"
```
(`<EXT>` = `json` for JSON-output scripts, `md` for `extract_nondeleted_reqs.py`)

1.  **Select Script**: Match user's intent to a library script from the catalog above.
    - If no matching script exists, proceed directly to **OPTION B** without asking the user.

#### OPTION A: Use Existing Library Script (Preferred)
1.  **Check**: Match user's intent to a library script (e.g., `get_released_reqs.py` for "get released requirements").
2.  **Run**:
    ```bash
    cmd /c "python .github/skills/doors-extractor/scripts/library/<SCRIPT_NAME> \"<RAW_JSON>\" \"report/doors/<OUTPUT>.json\""
    # fallback (legacy layout)
    cmd /c "python .claude/skills/doors-extractor/scripts/library/<SCRIPT_NAME> \"<RAW_JSON>\" \"report/doors/<OUTPUT>.json\""
    ```

#### OPTION B: Extend Library (For Custom Queries)
1.  **Read Schema**: Load `references/raw-data-schema.md` for JSON structure reference (attribute names, sparse-omission rule, `abs_ref` semantics).
2.  **Implement**: Add a new script directly under `scripts/library/`. A script is considered "reviewed" (and may be committed) only when it satisfies ALL of:
    - **Read-Only**: no `write`/`update`/`delete` on DOORS objects (consistent with §5 Rule 2); it only reads the raw JSON file.
    - **Stable signature**: Either `python <script>.py "<RAW_JSON>" "<OUTPUT>"` (pure positional args, like `get_released_reqs.py`) **or** positional args plus a fixed set of flags (like `hash_diff.py gen <raw> --module-path /<P>/<M>`). The requirement is **fixed arity + stable flag names across versions** — the first positional argument MUST be the raw JSON path, and any flags MUST be optional with documented defaults. Do not introduce positional args that change meaning, or flags that rename between releases.
    - **Schema-aware**: reads attribute names from the JSON `attrs` map per `raw-data-schema.md`; never hardcodes positional indices or assumes a fixed column order.
3.  **Run**: Execute it with the same pattern as OPTION A, using the Library Output Naming Convention above.
4.  **Maintain**: Keep script naming stable and reusable for future requests. Add a row to the Library Script Catalog table above so the next session discovers it.

## 5. Security & Stability Rules

1.  **IMMUTABLE CORE SCRIPT**: `scripts/doors_manager.py` is **LOCKED / READ-ONLY**. No modifications, no exceptions (unless user explicitly commands "Unlock core script for maintenance").

2.  **READ-ONLY INTERACTION**: Any DXL or Python code that performs `write`, `update`, `delete`, `purge`, `create`, `link`, or `save` within DOORS is **prohibited**. Refuse with: "Sorry, I am restricted to Read-Only operations on DOORS to prevent data corruption."

3.  **NO PASSWORD STORAGE**: Username/password must not be stored or passed via command-line arguments. Login is GUI-only.

4.  **No Passwords In Logs**: NEVER print DOORS passwords in any output stream.

5.  **Wait Mechanism**: Trust the manager script's built-in sentinel file mechanism. Do not interrupt.

6.  **ORDER INTEGRITY**: Follow the three-phase protocol in [references/extraction-protocol.md](references/extraction-protocol.md). COM recovery → I/O wait → file validation. This order MUST be preserved.

7.  **Separation**: Keep `doors_manager.py` untouched. Put all custom logic in reviewed scripts under `scripts/library/`.

8.  **Diagnostics**: `scripts/diag_com.py` provides COM environment diagnostics. Run it when COM connection fails unexpectedly to gather environment details before reporting an error.

## 6. Error Handling

Refer to **[references/error-handling.md](references/error-handling.md)** for the full troubleshooting table. The inline table below covers only the highest-frequency scenarios for immediate fallback without loading the reference.

### 6.1 High-Frequency Failure Modes (Inline Quick-Ref)

| Scenario | Symptom | First Response | If Still Failing |
|---|---|---|---|
| Config missing | DOORS launch fallback cannot find exe/data | `cmd /c "python credential_manager.py setup"` | Verify `DOORS_PATH` env var; check `~/.doors/config.json` exists |
| DOORS already running | COM unavailable; extraction fails | Keep session; do NOT close/restart | Run `diag_com.py`; classify output via §6.2 Step 0 anchors; follow §6.2 escalation |
| `& cmd.exe` rejected | PowerShell restricted mode error | Use `cmd /c python ...` (no `&`) | Use PowerShell-native cmdlets directly |
| pathlib check attempted | `python -c "import pathlib..."` | Replace with `Get-ChildItem ... \| Select Name,Length,LastWriteTime` | — (one-shot fix) |
| Fake red "errors" | Red lines despite successful extraction | Omit `2>&1` redirection; rerun | — (artifact, not real error) |
| COM recovery timeout | Script polls 10 min then fails | Wait for DOORS GUI to become responsive (manual) | Retry extraction after DOORS idle confirmed |
| JSON corrupted | `json.JSONDecodeError` in processing | Delete corrupted `*_raw.json` | Re-extract from DOORS (Phase 2) |

### 6.2 P3 Escalation Path (Failure Terminal State)

When extraction fails AND `diag_com.py` confirms COM is unrecoverable in the current session, follow this closed-loop escalation (do NOT leave the user at "capture logs and report failure" with no next step):

**Step 0 — Classify failure via `diag_com.py` + `Get-Process` output (objective anchors):**

Run `diag_com.py` AND `Get-Process doors` (see Step 3 command). Classify into exactly one branch using these **string-match anchors** (not free interpretation). The first two columns are inputs; the classification is the output:

| Combined diagnostic signals | Classification | Meaning |
|---|---|---|
| `GetActiveObject('DOORS.Application'): SUCCESS` AND `runStr test: 'DOORS COM OK'` | **COM_HEALTHY** | COM is fine; failure was transient — retry extraction once |
| `Dispatch('DOORS.Application'): SUCCESS` but `runStr test FAIL` | **COM_HALF_OPEN** | DOORS GUI launched but not ready — wait 60s, retry once |
| `Get-Process`: no doors process AND `No doors.exe process found!` | **NO_PROCESS** | DOORS not running — ask user to launch GUI + login, then retry once |
| `Get-Process`: doors exists, `Responding=False`, AND all GetActiveObject/Dispatch FAIL | **PROCESS_HUNG** | DOORS hung — ask user to kill PID via Task Manager, then retry once |
| `ERROR: pywin32 not installed` | **ENV_BROKEN** | Python env issue — stop, ask user to reinstall pywin32; do NOT retry |

**Step 1 — Collect**: Save `diag_com.py` stdout + failed extraction's stderr to `report/doors/_diag_<YYYYMMDD_HHMMSS>.log`.

**Step 2 — Branch action** (follow Step 0 classification, do NOT deviate):
- `COM_HEALTHY` / `COM_HALF_OPEN` / `NO_PROCESS` / `PROCESS_HUNG`: perform the stated action, then retry extraction (Phase 2) **exactly ONCE**.
- `ENV_BROKEN`: do NOT retry; stop and report.

**Step 3 — Hard limit + hand-off message template**:
If the single retry also fails, STOP. Do not enter a retry loop. Hand off to the user / DOORS admin using this exact template (fill in `<...>`):

```
DOORS extraction failed twice. Diagnostic classification: <CLASSIFICATION>.
Diag log: report/doors/_diag_<TIMESTAMP>.log
DOORS process: <PID from tasklist, or "not running">
Requested action: <launch DOORS / kill PID / reinstall pywin32 / escalate to DOORS admin for licensing>
```

**Process check command** (use this exact form for PID lookup, not `python -c`):
```powershell
Get-Process doors -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, Responding
```
(`Responding` field gives objective hung detection: `False` = hung.)
