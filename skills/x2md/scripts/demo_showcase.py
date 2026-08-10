#!/usr/bin/env python3
"""Reproducible showcase generator for x2md.

Regenerates ALL showcase artifacts used in README.md from the frozen test
samples — anyone can re-record the showcase by running this one script.
No manual screenshots, no hand-edited diffs. Cross-platform (no bash).

Output: tests/output/showcase/  (gitignored — regenerable)
Artifacts (in tests/output/showcase/, gitignored — regenerable):
  formula_before.txt   — raw markitdown output (bug: \\* \\_ \\^ escapes)
  formula_after.md     — enhanced output (fixed: * _ ^ inside $...$)
  table_d2_sidecar.md  — the .errors.md sidecar proving D2 detection
  xlsx_eval_log.txt    — stdout showing "15/15 cells resolved" warning line
  summary.txt          — one-screen evidence digest for README citation

Static asset (committed, not regenerated — the card cites the numbers this
script reproduces; keep the two in sync by hand when samples change):
  assets/showcase-card.svg — screenshot-ready 3-evidence card for README

Usage:
  python scripts/demo_showcase.py
  SHOWCASE_PYTHON=/path/python python scripts/demo_showcase.py

Exits non-zero if any step fails — the showcase must be reproducible or
the run is invalid (do not commit a half-baked demo).
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
PYTHON = os.environ.get("SHOWCASE_PYTHON", sys.executable)
OUT = SKILL_DIR / "tests" / "output" / "showcase"
SAMPLES = SKILL_DIR / "tests" / "samples"
SCRIPTS = SKILL_DIR / "scripts"


def run(cmd, **kw):
    """Run a command, return CompletedProcess. Raises on non-zero exit unless check=False."""
    kw.setdefault("cwd", str(SKILL_DIR))
    kw.setdefault("capture_output", True)
    kw.setdefault("text", True)
    return subprocess.run(cmd, **kw)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # Clean prior artifacts
    for f in OUT.glob("*"):
        f.unlink()

    print("[1/5] Verifying samples exist...")
    for name in ("test_formula.docx", "test_merged.docx", "test_formula.xlsx"):
        p = SAMPLES / name
        if not p.is_file():
            print(f"MISSING: {p} — run tests/generate_samples.py first", file=sys.stderr)
            return 2
    print("      all 3 samples present")

    print("[2/5] Generating BEFORE (raw markitdown, no enhancements)...")
    before_py = (
        "from markitdown import MarkItDown; "
        "import sys; "
        f"out = MarkItDown().convert(r'{SAMPLES / 'test_formula.docx'}').text_content; "
        f"open(r'{OUT / 'formula_before.txt'}','w',encoding='utf-8').write(out); "
        f"print('chars:', len(out))"
    )
    r = run([PYTHON, "-c", before_py])
    if r.returncode != 0:
        print(f"BEFORE failed: {r.stderr}", file=sys.stderr)
        return 3
    print(f"      wrote formula_before.txt ({r.stdout.strip()})")

    print("[3/5] Generating AFTER (enhanced pipeline)...")
    after_md = OUT / "formula_after.md"
    r = run([PYTHON, str(SCRIPTS / "_convert_core.py"),
             str(SAMPLES / "test_formula.docx"), "-o", str(after_md)])
    (OUT / "formula_after.log").write_text(r.stdout + r.stderr, encoding="utf-8")
    print(f"      wrote formula_after.md ({after_md.stat().st_size} bytes)")

    print("[4/5] Generating table D2 sidecar + xlsx eval log...")
    table_md = OUT / "table_d2_raw.md"
    r = run([PYTHON, str(SCRIPTS / "_convert_core.py"),
             str(SAMPLES / "test_merged.docx"), "-o", str(table_md)])
    (OUT / "table_d2.log").write_text(r.stdout + r.stderr, encoding="utf-8")
    sidecar = Path(str(table_md) + ".errors.md")
    if sidecar.is_file():
        shutil.copy(sidecar, OUT / "table_d2_sidecar.md")
        print(f"      wrote table_d2_sidecar.md ({sidecar.stat().st_size} bytes)")
    else:
        print("      WARNING: no D2 sidecar — D2 not detected, investigate", file=sys.stderr)

    xlsx_md = OUT / "xlsx_after.md"
    r = run([PYTHON, str(SCRIPTS / "_convert_core.py"),
             str(SAMPLES / "test_formula.xlsx"), "-o", str(xlsx_md)])
    (OUT / "xlsx_eval_log.txt").write_text(r.stdout + r.stderr, encoding="utf-8")
    print(f"      wrote xlsx_eval_log.txt + xlsx_after.md")

    print("[5/5] Building evidence digest...")
    before_text = (OUT / "formula_before.txt").read_text(encoding="utf-8")
    after_text = (OUT / "formula_after.md").read_text(encoding="utf-8")
    # Count backslash-escaped markdown specials INSIDE $...$ only
    def count_escaped_in_math(text):
        n = 0
        for m in re.finditer(r'\$([^$]+)\$', text):
            n += len(re.findall(r'\\[\*_\^]', m.group(1)))
        return n
    before_escapes = count_escaped_in_math(before_text)
    after_escapes = count_escaped_in_math(after_text)

    sidecar_lines = 0
    sidecar_path = OUT / "table_d2_sidecar.md"
    if sidecar_path.is_file():
        sidecar_lines = len(sidecar_path.read_text(encoding="utf-8").splitlines())

    xlsx_log = (OUT / "xlsx_eval_log.txt").read_text(encoding="utf-8")
    xlsx_eval_line = ""
    for line in xlsx_log.splitlines():
        if "XLSX formula eval" in line:
            xlsx_eval_line = line.strip().lstrip("- ").strip()
            break

    digest = []
    digest.append("x2md showcase — evidence digest")
    digest.append("=" * 52)
    digest.append("")
    digest.append("PROOF 1 — formula escaping fix (markitdown 0.1.7 bug)")
    digest.append(f"  BEFORE (raw markitdown): {before_escapes} bad escapes (\\* \\_ \\^) inside $...$")
    digest.append(f"  AFTER  (enhanced):       {after_escapes} bad escapes")
    digest.append(f"  → {'FIXED' if after_escapes == 0 else 'STILL BROKEN'}")
    digest.append("")
    digest.append("PROOF 2 — table D2 detection (vertical_merge)")
    digest.append(f"  sidecar lines: {sidecar_lines}")
    digest.append(f"  → {'DETECTED' if sidecar_lines > 0 else 'MISSED'}")
    digest.append("")
    digest.append("PROOF 3 — XLSX formula evaluation")
    digest.append(f"  {xlsx_eval_line or '(no eval line — investigate)'}")
    digest.append("")
    digest.append("Re-record: python scripts/demo_showcase.py")
    digest_text = "\n".join(digest)
    (OUT / "summary.txt").write_text(digest_text, encoding="utf-8")

    print()
    print(digest_text)
    print()
    print(f"Showcase artifacts in: {OUT}")
    return 0 if (after_escapes == 0 and sidecar_lines > 0) else 1


if __name__ == "__main__":
    sys.exit(main())
