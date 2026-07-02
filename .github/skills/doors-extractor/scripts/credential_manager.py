"""DOORS Configuration Manager (non-secret settings only).

Stores only local launcher settings for DOORS GUI startup:
    - doors_data (optional)
    - doors_path (optional)

No username/password is collected or persisted.

Usage:
    cmd /c "python credential_manager.py setup"
    cmd /c "python credential_manager.py status"
    cmd /c "python credential_manager.py clear"
"""
import argparse
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Platform guard
# ---------------------------------------------------------------------------
if sys.platform != "win32":
    print("ERROR: This configuration manager requires Windows.", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# File ACL protection
# ---------------------------------------------------------------------------

def _set_file_acl_current_user_only(path: Path):
    """Use icacls to restrict access to current Windows user only."""
    import subprocess

    userdomain = os.environ.get("USERDOMAIN", "")
    username = os.environ.get("USERNAME", "")
    if not username:
        return

    account = f"{userdomain}\\{username}" if userdomain else username
    is_dir = path.is_dir()
    perm = f"{account}:(OI)(CI)(F)" if is_dir else f"{account}:(F)"

    try:
        subprocess.run(
            [
                "icacls", str(path),
                "/inheritance:r",
                "/grant:r", perm,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print(
            f"  WARNING: Could not set ACL on {path}. "
            f"Run manually: icacls \"{path}\" /inheritance:r /grant:r \"{account}:(F)\"",
            file=sys.stderr,
        )


# ---------------------------------------------------------------------------
# Credential file management
# ---------------------------------------------------------------------------
CREDENTIALS_DIR = Path.home() / ".doors"
CREDENTIALS_FILE = CREDENTIALS_DIR / "config.json"  # Plain JSON — NOT encrypted; contains non-secret settings only


def _load_credentials() -> dict:
    """Load encrypted credentials from user home directory."""
    if not CREDENTIALS_FILE.exists():
        return {}
    with open(CREDENTIALS_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save_credentials(data: dict):
    """Save encrypted credentials to user home directory."""
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    _set_file_acl_current_user_only(CREDENTIALS_FILE)
    _set_file_acl_current_user_only(CREDENTIALS_DIR)


def get_credentials() -> dict:
    """
    Get DOORS launcher configuration.

    Returns:
        {"doors_data": str, "doors_path": str}
        or {} if not configured.
    """
    all_creds = _load_credentials()
    if not all_creds:
        return {}

    entry = all_creds.get("default")
    if not entry:
        return {}

    return {
        "doors_data": entry.get("doors_data", ""),
        "doors_path": entry.get("doors_path", ""),
    }


# ---------------------------------------------------------------------------
# tkinter configuration dialog
# ---------------------------------------------------------------------------

def _tkinter_doors_config(existing: dict):
    """Show a tkinter dialog for DOORS non-secret configuration.

    Returns (doors_data, doors_path) or raises KeyboardInterrupt.
    """
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog

    result = {"doors_data": None, "doors_path": None}

    root = tk.Tk()
    root.title("DOORS Configuration")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    w, h = 500, 260
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)

    # DOORS Data field (format: port@hostname)
    ttk.Label(frame, text="DOORS Data (format: port@hostname):").grid(row=0, column=0, sticky="w", pady=(0, 4))
    data_var = tk.StringVar(value=existing.get("doors_data", ""))
    data_entry = ttk.Entry(frame, textvariable=data_var, width=45)
    data_entry.grid(row=1, column=0, sticky="ew", pady=(0, 8))
    if not data_var.get():
        data_var.set("36677@doors.prehgad.local")
    data_entry.focus_set()

    # DOORS Path field
    ttk.Label(frame, text="DOORS Executable Path:").grid(row=2, column=0, sticky="w", pady=(0, 4))

    path_frame = ttk.Frame(frame)
    path_frame.grid(row=3, column=0, sticky="ew", pady=(0, 12))

    path_var = tk.StringVar(value=existing.get("doors_path", ""))
    path_entry = ttk.Entry(path_frame, textvariable=path_var, width=35)
    path_entry.pack(side="left", fill="x", expand=True)

    def _browse():
        chosen = filedialog.askopenfilename(
            parent=root,
            title="Select DOORS executable",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
            initialdir=r"C:\Program Files\IBM\Rational\DOORS",
        )
        if chosen:
            path_var.set(chosen)

    ttk.Button(path_frame, text="Browse...", command=_browse, width=10).pack(side="left", padx=(8, 0))

    if not path_var.get():
        path_var.set(r"C:\Program Files\IBM\Rational\DOORS\9.7\bin\doors.exe")

    # Buttons
    btn_frame = ttk.Frame(frame)
    btn_frame.grid(row=4, column=0, sticky="e")

    def _ok():
        d = data_var.get().strip()
        p = path_var.get().strip()
        if not d:
            messagebox.showwarning("Validation", "DOORS Data is required (format: port@hostname).", parent=root)
            return
        result["doors_data"] = d
        result["doors_path"] = p
        root.destroy()

    def _cancel():
        root.destroy()

    ttk.Button(btn_frame, text="OK", command=_ok, width=10).pack(side="left", padx=(0, 8))
    ttk.Button(btn_frame, text="Cancel", command=_cancel, width=10).pack(side="left")

    root.protocol("WM_DELETE_WINDOW", _cancel)
    root.bind("<Return>", lambda e: _ok())
    root.bind("<Escape>", lambda e: _cancel())

    root.mainloop()

    if result["doors_data"] is None:
        raise KeyboardInterrupt("User cancelled the configuration dialog.")
    return result["doors_data"], result["doors_path"]


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_setup(args):
    """Interactive configuration setup for non-secret DOORS settings."""
    print("=" * 50)
    print("DOORS Configuration Setup")
    print("=" * 50)
    print(f"Configuration file: {CREDENTIALS_FILE}")
    print()

    # Load existing
    all_creds = _load_credentials()
    existing = all_creds.get("default", {})

    # tkinter dialog for DOORS Data + Path
    print("Opening DOORS configuration dialog ...")
    try:
        doors_data, doors_path = _tkinter_doors_config(existing)
    except KeyboardInterrupt:
        print("Cancelled.", file=sys.stderr)
        sys.exit(0)

    print(f"  DOORS Data: {doors_data}")
    print(f"  DOORS Path: {doors_path}")

    # Save
    all_creds["default"] = {
        "doors_data": doors_data,
        "doors_path": doors_path,
    }

    _save_credentials(all_creds)
    print()
    print("Configuration saved.")


def cmd_status(args):
    """Show configuration status."""
    all_creds = _load_credentials()
    if not all_creds:
        print("No configuration found. Run 'cmd /c \"python credential_manager.py setup\"' first.")
        return

    entry = all_creds.get("default", {})

    print(f"Config file: {CREDENTIALS_FILE}")
    print(f"  DOORS Data: {entry.get('doors_data', 'N/A')}")
    print(f"  DOORS Path: {entry.get('doors_path', 'N/A')}")


def cmd_clear(args):
    """Remove stored credentials."""
    if CREDENTIALS_FILE.exists():
        CREDENTIALS_FILE.unlink()
        print(f"Credentials removed: {CREDENTIALS_FILE}")
    else:
        print("No credentials file found.")


def main():
    parser = argparse.ArgumentParser(description="DOORS Configuration Manager")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("setup", help="Configure DOORS Data/Path (interactive)")
    sub.add_parser("status", help="Show configuration status")
    sub.add_parser("clear", help="Remove stored configuration")

    args = parser.parse_args()

    if args.command == "setup":
        cmd_setup(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "clear":
        cmd_clear(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
