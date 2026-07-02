# Error Handling Guide

| Scenario | Symptom | Action |
|----------|---------|--------|
| DOORS not installed | `FileNotFoundError: DOORS executable not found` | Inform user: "DOORS client not found. Verify DOORS executable path in local config (`python .github/skills/doors-extractor/scripts/credential_manager.py setup`) or `DOORS_PATH` environment variable." |
| DOORS not logged in | COM unavailable or fallback run does not complete extraction | Inform user: "Login is GUI-only. Open DOORS and log in manually, then retry extraction." Do NOT print passwords. |
| Extraction timeout (>20 min) | `DOORS timed out after 20 minutes` | Suggest: 1) Check if module is very large; 2) Verify DOORS server connectivity; 3) Try again during off-peak hours. |
| Output JSON missing after exit | `.done` sentinel not found | The DXL script likely failed silently. Ask user to check DOORS client for error dialogs. Review the log file path printed in stderr. |
| Corrupted/incomplete JSON | `json.JSONDecodeError` in processing script | Raw data was truncated. Delete the corrupted `*_raw.json` and re-extract from DOORS. |
| DOORS client already running | COM path unavailable or extraction still fails | Keep existing DOORS session. If COM reuse fails and subprocess fallback also fails, do not close/retry in this workflow; capture logs and report failure with environment checks. |
| Network/server unreachable | Connection errors in log | Inform user: "Cannot reach DOORS server. Check VPN connection and optional DOORS Data Server setting in local config (`python .github/skills/doors-extractor/scripts/credential_manager.py setup`)." |
