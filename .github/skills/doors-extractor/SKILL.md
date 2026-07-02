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
2.  **Check Configuration**: Verify local configuration is set (run `credential_manager.py status`). If not configured, guide user through `setup`.
3.  **🔴 CHECKPOINT · Cache Scan**: Search the workspace with glob `**/*_raw.json` for existing raw data. Match by module name, prefer the most recent date.
    *   If raw data exists: STOP and ask ONLY "Found existing raw data `X.json`. Use this or re-extract from DOORS?" (binary choice, via `vscode_askQuestions`)
    *   If user chooses existing data: Skip Phase 2, proceed to Phase 3 (Processing).
4.  **Extract** (only if no usable cache): Proceed to Phase 2.

### 4.6 Phase 2: Extraction (Infrastructure)

**🔴 CHECKPOINT · Pre-Extraction Gate**: Only proceed if (a) user explicitly requests fresh data OR (b) no usable cache exists. If neither, do NOT extract.

1.  **Naming Convention**: Raw data file MUST include **Project Name** and **DateTime (YYYYMMDD_HHMMSS)**. The time part (HHMMSS) is **MANDATORY** — date-only filenames (e.g., `_20260605_raw.json`) are a violation. Always use the full current datetime, e.g., `VW_10638_SysRS_20260605_143052_raw.json`. The `.done` sentinel file created by DXL will automatically have the same name with `.done` appended.
2.  **Output Location**: Default to `report/doors/` under the project root.
3.  **Command** (Recommended - clean output):
    ```bash
    cmd /c python .github/skills/doors-extractor/scripts/doors_manager.py extract --url <TARGET_URL> --output report/doors/<PROJECT_NAME>_<MODULE_NAME>_<YYYYMMDD_HHMMSS>_raw.json
    # fallback (legacy layout)
    cmd /c python .claude/skills/doors-extractor/scripts/doors_manager.py extract --url <TARGET_URL> --output report/doors/<PROJECT_NAME>_<MODULE_NAME>_<YYYYMMDD_HHMMSS>_raw.json
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

### 4.7 Phase 3: Processing (Business Logic)

**🔴 CHECKPOINT · Post-Extraction Gate**: Only enter Phase 3 after the official success indicator (§4.6 step 6) is confirmed. If extraction failed, go to §6 Error Handling — do NOT attempt to process a missing/partial raw file.

**Never use generic tools (jq/grep/python one-liners) on raw JSON. Always use a dedicated `scripts/library/` script.**

#### Library Script Catalog (Quick-Ref)

> Current scripts in `scripts/library/`. For any new query not covered here, go to OPTION B. Run `ls scripts/library/` to detect scripts added after this doc.

| Script | Filters By | Output | When to use |
|---|---|---|---|
| `get_released_reqs.py` | `Object_Status == "Released"` | JSON | "get released requirements" / "已发布需求" |
| `extract_nondeleted_reqs.py` | objects without deletion flags (heuristic on `id`/`text`/`deleted` keys) | Markdown | "get all non-deleted requirements as doc" / raw dump to readable form |
| `get_swt_impact.py` | `AllocTestAuthority == "SwT"` | JSON | "get SwT-allocated requirements" / "software test authority items" |

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
1.  **Read Schema**: Load `references/raw-data-schema.md` for JSON structure reference.
2.  **Implement**: Add a reviewed script directly under `scripts/library/`.
3.  **Run**: Execute it with the same pattern as OPTION A.
4.  **Maintain**: Keep script naming stable and reusable for future requests.

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

**Step 0 — Classify failure via `diag_com.py` output (objective anchors):**

Run `diag_com.py` and read its output. Classify into exactly one branch using these **string-match anchors** (not free interpretation):

| diag_com.py output contains | Classification | Meaning |
|---|---|---|
| `GetActiveObject('DOORS.Application'): SUCCESS` AND `runStr test: 'DOORS COM OK'` | **COM_HEALTHY** | COM is fine; failure was transient — retry extraction once |
| `Dispatch('DOORS.Application'): SUCCESS` but `runStr test FAIL` | **COM_HALF_OPEN** | DOORS GUI launched but not ready — wait 60s, retry once |
| `No doors.exe process found!` | **NO_PROCESS** | DOORS not running — ask user to launch GUI + login, then retry once |
| `doors.exe` in tasklist BUT all GetActiveObject/Dispatch FAIL | **PROCESS_HUNG** | DOORS hung — ask user to kill PID via Task Manager, then retry once |
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
