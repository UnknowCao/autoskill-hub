#!/usr/bin/env python3
"""Initialize a new llm-wiki instance with the standard directory structure.

Usage: python _init.py <wiki_path>

Creates the directory tree and empty skeleton files only.
Content is populated by the Agent per the llm-wiki SKILL.md templates.
"""

import sys
from pathlib import Path


RAW_DIRS = [
    "articles",
    "papers",
    "presentations",
    "spreadsheets",
    "documents",
    "transcripts",
    "assets",
    "other",
]

PAGE_DIRS = [
    "entities",
    "concepts",
    "comparisons",
    "queries",
]

SKELETON_FILES = ["SCHEMA.md", "index.md", "log.md"]


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    wiki = Path(sys.argv[1]).resolve()

    if wiki.exists():
        print(f"ERROR: path already exists: {wiki}")
        print("Remove it first or choose a different path.")
        sys.exit(1)

    wiki.mkdir(parents=True)
    print(f"Wiki: {wiki}\n")

    # Layer 1: raw/ subdirectories
    for d in RAW_DIRS:
        (wiki / "raw" / d).mkdir(parents=True, exist_ok=True)
    print(f"  raw/ ({len(RAW_DIRS)} subdirs)")

    # Layer 2: page directories
    for d in PAGE_DIRS:
        (wiki / d).mkdir(parents=True, exist_ok=True)
    print(f"  pages/ ({len(PAGE_DIRS)} dirs)")

    # Archive
    (wiki / "_archive").mkdir(parents=True, exist_ok=True)
    print(f"  _archive/")

    # Skeleton files (empty)
    for f in SKELETON_FILES:
        (wiki / f).touch()
    print(f"  skeleton files ({len(SKELETON_FILES)} empty .md)")

    print(f"\nDone. Run the llm-wiki skill to populate SCHEMA.md, index.md, log.md.")


if __name__ == "__main__":
    main()
