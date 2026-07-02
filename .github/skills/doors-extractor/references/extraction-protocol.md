# Extraction Protocol — Three-Phase Sequence

## Mandatory Order (Zero Exceptions)

```
PHASE 1 → PHASE 2 → PHASE 3
```

Any out-of-order action is a **PROCESS VIOLATION**.

---

## PHASE 1 — COM Recovery Polling

- Script attempts COM connection to an active DOORS session (fast path, ~seconds).
- If COM is unavailable: launches DOORS GUI for manual login (slow path, requires user login).
- After login: polls `doors.runStr('""')` every 10 s for up to 10 min (60 attempts).
- **STRICTLY FORBIDDEN during this phase**: any file existence or file size check.
- Exit criterion: `doors.runStr('')` succeeds → "DOORS recovery confirmed".

## PHASE 2 — File I/O Completion Wait

- After COM recovery confirmed, wait a fixed **10 seconds** for the DXL file write to complete.
- **MUST NOT be skipped**, even if partial output is already visible in the terminal.

## PHASE 3 — File Validation

- Only enters after PHASE 1 **and** PHASE 2 are complete.
- Checks `os.path.exists(output_abs)` and `os.path.getsize(output_abs) > 0`.
- **Official success indicator** (the only valid success criterion):
  ```
  COM extraction successful (X.XX MB): <filepath>
  ```
- If this message is absent after timeout → extraction failed; check error output.

---

## Fallback File Check (terminal instability only)

If terminal command resolution is unstable, use this as a last resort:

```powershell
Get-ChildItem "C:\person\project\10638_AI\report\doors\*_raw.json" | Select-Object Name, Length, LastWriteTime
```

This check is **supplementary only** and must not replace the official success indicator above.
