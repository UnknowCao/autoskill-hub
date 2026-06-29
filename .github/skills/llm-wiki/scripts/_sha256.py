#!/usr/bin/env python3
"""Compute SHA256 hash of a file for llm-wiki frontmatter.

Usage:
  python _sha256.py <file>          # auto-detect: .md → hash body only; binary → hash full file
  python _sha256.py --md <file>     # force .md mode: hash body after frontmatter
  python _sha256.py --raw <file>    # force raw mode: hash entire file as-is

Output: 64-char lowercase hex digest.
"""

import sys, hashlib
from pathlib import Path


def hash_md_body(path: Path) -> str:
    """Hash the body of a .md file (everything after the second '---')."""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        body = parts[2] if len(parts) >= 3 else text
    else:
        body = text
    return hashlib.sha256(body.encode("utf-8")).hexdigest().lower()


def hash_raw(path: Path) -> str:
    """Hash the entire file as raw bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest().lower()


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    mode = None
    file_arg = None

    if sys.argv[1] == "--md":
        mode = "md"
        if len(sys.argv) < 3:
            print("ERROR: --md requires a file path")
            sys.exit(1)
        file_arg = sys.argv[2]
    elif sys.argv[1] == "--raw":
        mode = "raw"
        if len(sys.argv) < 3:
            print("ERROR: --raw requires a file path")
            sys.exit(1)
        file_arg = sys.argv[2]
    else:
        file_arg = sys.argv[1]

    path = Path(file_arg)
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        sys.exit(1)

    if mode == "md":
        digest = hash_md_body(path)
    elif mode == "raw":
        digest = hash_raw(path)
    else:
        # Auto-detect
        if path.suffix.lower() in (".md", ".MD"):
            digest = hash_md_body(path)
        else:
            digest = hash_raw(path)

    print(digest)


if __name__ == "__main__":
    main()
