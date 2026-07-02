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

## 3. Usage Workflow

### Terminal Execution Policy (MANDATORY)

- All terminal commands in this workflow MUST be executed via `cmd /c`.
- All terminal commands MUST be executed in PowerShell-compatible form.
- **NEVER prepend `^U` (Ctrl+U control character) to any command.** Commands starting with `^U` are a copy-paste artifact and will cause the shell to clear the line or fail. Always inspect the command string before sending and strip any leading control characters.
- The following command pattern is prohibited and MUST be replaced:
    - `cmd /c "c:/person/project/10638_AI/.venv/Scripts/python.exe -c \"import pathlib; ... print('exists=', ...); print('size=', ...)\""`
- Mandatory replacement format for file verification:
    - `Get-ChildItem "C:\person\project\10638_AI\report\doors\*HSI*_raw.json" | Select-Object Name, Length, LastWriteTime`

### run_in_terminal Mode Policy (MANDATORY — Credit Conservation)

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

### ABSOLUTE ENFORCEMENT (ZERO EXCEPTIONS)

- The extraction sequence is MANDATORY and NON-NEGOTIABLE.
- Any out-of-order action is a PROCESS VIOLATION.
- NEVER perform file checks before COM recovery is confirmed.
- NEVER declare success unless the script prints the official success indicator.
- If uncertain, DO NOT guess; continue waiting for the script lifecycle.

### User Interaction Policy (Min Questions)

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

### Phase 1: Determine Target

1.  **Identify**: Find the DOORS Module Path (e.g., `/Project/X/Requirements`) or URL (`doors://`).
    *   If no URL/Path found: Ask only "Please provide the DOORS Module URL or Path (location)."
2.  **Check Configuration**: Verify local configuration is set (run `credential_manager.py status`). If not configured, guide user through `setup`.
3.  **Scan Cache**: Search the workspace with glob `**/*_raw.json` for existing raw data. Match by module name, prefer the most recent date.
    *   If raw data exists: Ask only "Found existing raw data `X.json`. Use this or re-extract from DOORS?"
    *   If user chooses existing data: Skip Phase 2, proceed to Phase 4.
4.  **Extract** (only if no usable cache): Proceed to Phase 2.

### Phase 2: Extraction (Infrastructure)

**Only proceed if user requests fresh data or no raw data exists.**

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

7.  **Success Verification**: The script output is the authoritative indicator.
    - **Success indicator**: Terminal contains `"COM extraction successful (XXX MB): <filepath>"`
    - If this exact signal is not present, treat extraction as NOT successful.
    - See **[references/extraction-protocol.md](references/extraction-protocol.md)** for fallback file-check syntax.

### Phase 3: Processing (Business Logic)

**Never use generic tools. Always use a dedicated script.**

1.  **List Available Scripts**: List `scripts/library/` directory and present available scripts to user.
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

## 4. Security & Stability Rules

1.  **IMMUTABLE CORE SCRIPT**: `scripts/doors_manager.py` is **LOCKED / READ-ONLY**. No modifications, no exceptions (unless user explicitly commands "Unlock core script for maintenance").

2.  **READ-ONLY INTERACTION**: Any DXL or Python code that performs `write`, `update`, `delete`, `purge`, `create`, `link`, or `save` within DOORS is **prohibited**. Refuse with: "Sorry, I am restricted to Read-Only operations on DOORS to prevent data corruption."

3.  **NO PASSWORD STORAGE**: Username/password must not be stored or passed via command-line arguments. Login is GUI-only.

4.  **No Passwords In Logs**: NEVER print DOORS passwords in any output stream.

5.  **Wait Mechanism**: Trust the manager script's built-in sentinel file mechanism. Do not interrupt.

6.  **ORDER INTEGRITY**: Follow the three-phase protocol in [references/extraction-protocol.md](references/extraction-protocol.md). COM recovery → I/O wait → file validation. This order MUST be preserved.

7.  **Separation**: Keep `doors_manager.py` untouched. Put all custom logic in reviewed scripts under `scripts/library/`.

8.  **Diagnostics**: `scripts/diag_com.py` provides COM environment diagnostics. Run it when COM connection fails unexpectedly to gather environment details before reporting an error.

## 5. Error Handling

Refer to **[references/error-handling.md](references/error-handling.md)** for the full troubleshooting table.

| Scenario | Symptom | Action |
|----------|---------|--------|
| Configuration missing | DOORS launch fallback cannot find executable/data settings | Guide user: `cmd /c "python credential_manager.py setup"` |
| DOORS client already running | COM path unavailable or extraction still fails | Keep existing DOORS session. If COM reuse fails and subprocess fallback also fails, do not close/retry in this workflow; capture logs and report failure with environment checks. |
| `& cmd.exe` syntax used | PowerShell restricted mode rejects `&` operator | Use `cmd /c python ...` (without `&`) or use PowerShell-native commands directly. |
| Python pathlib exists/size check attempted | Command uses `python -c` with `pathlib` for file exists/size verification | Replace with: `Get-ChildItem "C:\person\project\10638_AI\report\doors\*HSI*_raw.json" | Select-Object Name, Length, LastWriteTime` |
| Fake "errors" from redirection | Red error-like lines appear even though extraction succeeds | This is a stderr/stdout redirection artifact. Do NOT use `2>&1` in your command. Run without stderr redirection for clean output. |
| COM recovery timeout | Script waits 10 mins polling for DOORS to recover after large file export, then fails | Normal for very large modules. Indicates DOORS is busy with I/O. Retry after DOORS becomes responsive (manual observation). |
