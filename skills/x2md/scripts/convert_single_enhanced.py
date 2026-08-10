# -*- coding: utf-8 -*-
"""Enhanced single-file converter (runs as an isolated subprocess).

Thin CLI wrapper around ``_convert_core.convert_file()`` so the dynamic
batch driver (``batch_convert_dynamic.py``) can convert each file in its
own isolated Python process. Any hang / memory leak / native-handle leak
stays confined to this short-lived process; the driver kills it via
``subprocess.run(timeout=...)`` and moves on.

**Pre-decrypt scenario.** The driver may have already decrypted an
encrypted file to a temp path (e.g. ``.__decrypted_foo.docx``) and passes
that temp path as ``src``. In that case the driver also passes
``--original-name foo.docx`` so the metadata header, reports, and sidecar
reference the user-visible filename instead of the temp file.

Communication contract with the driver:
    stdout : the ``report`` returned by ``convert_file()`` (multi-line).
             A ``[SIDECAR] <path>`` line indicates a table-error sidecar.
    exit codes:
        0  success (clean — no table errors)
        1  success BUT table errors detected (sidecar written; stage-2 fix
           needed) OR conversion failure
        2  file not found / not a regular file
        3  unsupported extension
        5  output already exists (skipped by driver, not by this script)

Usage:
    python convert_single_enhanced.py <src> <outdir> <out_name> \\
        [--no-table-detect] [--no-metadata] [--original-name FILENAME]

Examples:
    # Plain file
    python convert_single_enhanced.py report.docx output/ report.md

    # Pre-decrypted temp file; keep original name in metadata
    python convert_single_enhanced.py .__decrypted_secret.docx output/ secret.md \\
        --original-name secret.docx --no-prompt

    # Disable table detection (faster, no sidecar)
    python convert_single_enhanced.py slide.pptx output/ slide.md --no-table-detect
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure scripts/ is importable (sibling modules: _convert_core, _decrypt, ...)
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))


def _parse_args(argv: list[str]):
    """Minimal manual parser (avoids argparse overhead in a hot subprocess path).

    Returns (src, outdir, out_name, no_table_detect, no_metadata,
             no_prompt, original_name) or raises SystemExit on bad usage.
    """
    if len(argv) < 4:
        sys.stderr.write(
            "ERR: usage convert_single_enhanced.py <src> <outdir> <out_name> "
            "[--no-table-detect] [--no-metadata] [--no-prompt] "
            "[--original-name FILENAME]\n"
        )
        raise SystemExit(1)

    src = argv[1]
    outdir = argv[2]
    out_name = argv[3]

    no_table_detect = False
    no_metadata = False
    no_prompt = False
    original_name: str | None = None

    rest = argv[4:]
    i = 0
    while i < len(rest):
        tok = rest[i]
        if tok == "--no-table-detect":
            no_table_detect = True
            i += 1
        elif tok == "--no-metadata":
            no_metadata = True
            i += 1
        elif tok == "--no-prompt":
            no_prompt = True
            i += 1
        elif tok == "--original-name":
            if i + 1 >= len(rest):
                sys.stderr.write("ERR: --original-name requires a value\n")
                raise SystemExit(1)
            original_name = rest[i + 1]
            i += 2
        else:
            sys.stderr.write(f"ERR: unknown argument '{tok}'\n")
            raise SystemExit(1)

    return (src, outdir, out_name,
            no_table_detect, no_metadata, no_prompt, original_name)


def main() -> int:
    (src, outdir, out_name,
     no_table_detect, no_metadata, no_prompt, original_name) = _parse_args(sys.argv)

    # Pre-flight file checks (return distinct exit codes for the driver).
    try:
        if not Path(src).is_file():
            return 2
    except OSError:
        return 2

    ext = Path(src).suffix.lower()
    supported = {".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls",
                 ".csv", ".txt", ".html", ".htm", ".json", ".xml",
                 ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
                 ".zip", ".epub"}
    if ext not in supported:
        return 3

    # Resolve the absolute output path.
    out_path = Path(outdir) / out_name

    # Import the enhancement engine (expected to be siblings of this file).
    try:
        from _convert_core import convert_file
    except ImportError as exc:
        sys.stderr.write(f"IMPORT_ERR: cannot import _convert_core: {exc}\n")
        return 4

    success, report, errors_path = convert_file(
        input_path=Path(src),
        output_path=out_path,
        enable_table_detect=not no_table_detect,
        enable_metadata=not no_metadata,
        allow_prompt=not no_prompt,
        original_name=original_name,
    )

    # Emit the report so the driver can parse sidecar markers.
    sys.stdout.write(report + "\n")

    if not success:
        return 1
    # Exit 1 even on success when a sidecar was written — signals the driver
    # that stage-2 AI fixing is needed (mirrors _convert_core.py main()).
    if errors_path:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
