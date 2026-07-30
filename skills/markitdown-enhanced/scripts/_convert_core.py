r"""markitdown-enhanced single-file conversion entry point.

Orchestrates the full enhancement pipeline:
  1. Pre-conversion: detect encrypted files, decrypt via Credential Manager
  2. Conversion: standard markitdown docx->md
  3. Post-conversion: formula escaping fix, table structure detection

Usage:
    python _convert_core.py input.docx [-o output.md] [--scan-encrypted INPUT_DIR]
    python _convert_core.py --scan-encrypted INPUT_DIR
"""
from __future__ import annotations
import argparse
import io
import sys
from pathlib import Path

# Ensure scripts/ is importable (relative-path strategy)
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from markitdown import MarkItDown
import warnings
warnings.filterwarnings("ignore")  # suppress ffmpeg warning


def _format_metadata_header(title: str, source_name: str, suffix: str) -> str:
    """Build the metadata header block prepended to every converted .md file.

    Mirrors batch_convert.py's header so single-file and batch outputs share
    the same shape. Returns the header text WITHOUT a trailing content separator
    line (caller appends the body directly after a blank line).
    """
    header = f"# {title or source_name}\n\n"
    header += f"**Source**: {source_name}\n"
    header += f"**Format**: {suffix}\n\n"
    header += "---\n\n"
    return header


def _post_process(text: str, enable_table_detect: bool = True,
                  mammoth_html: str | None = None,
                  md_path: str = "") -> tuple[str, str, str]:
    """Run all post-processing steps and return (fixed_text, report, error_report).

    - report: short human-readable summary printed to stdout (always returned)
    - error_report: full structured error report (empty string if no issues),
      to be written to a sidecar .errors.md file for the AI to read.
    """
    report_parts: list[str] = []
    error_report = ""

    # 1. Formula escaping fix
    try:
        from fix_formula_escaping import fix_formulas_in_text
        text, n_fixes = fix_formulas_in_text(text)
        if n_fixes:
            report_parts.append(f"- Formula escaping fix: {n_fixes} occurrence(s) corrected")
    except ImportError:
        pass

    # 2. Table structure detection (two-stage pipeline: detect here, fix by AI)
    if enable_table_detect and mammoth_html:
        try:
            from _table_detect import detect_table_issues, format_error_report
            issues = detect_table_issues(mammoth_html, text)
            if issues:
                report_parts.append(
                    f"- Table errors detected: {len(issues)} table(s) need AI fixing "
                    f"(see sidecar .errors.md)"
                )
                error_report = format_error_report(issues, md_path=md_path)
        except ImportError:
            pass

    report = "\n".join(report_parts) if report_parts else ""
    return text, report, error_report


def _maybe_eval_xlsx(raw: bytes, suffix: str) -> bytes:
    """Pre-evaluate XLSX formulas so markitdown reads real values, not NaN.

    Best-effort: returns the original bytes unchanged if the file is not
    an .xlsx, has no formulas, or the `formulas` library is not available.
    Never raises — if anything fails, the original bytes come back untouched.
    """
    if suffix.lower() not in (".xlsx",):
        return raw
    try:
        from _xlsx_formula_eval import evaluate_xlsx
        return evaluate_xlsx(raw)
    except Exception:
        return raw


def _get_mammoth_html(file_path: Path, decrypted_bytes: bytes | None = None) -> str | None:
    """Get mammoth HTML output for table structure reference.

    For encrypted files, pass the already-decrypted bytes (decrypted_bytes);
    otherwise mammoth would re-open the encrypted file on disk and raise
    BadZipFile, silently suppressing table detection.
    """
    try:
        import mammoth
        import io
        source = decrypted_bytes if decrypted_bytes is not None else file_path
        return mammoth.convert_to_html(io.BytesIO(source) if decrypted_bytes is not None else source).value
    except Exception:
        return None


def convert_file(input_path: Path, output_path: Path | None = None,
                 enable_table_detect: bool = True,
                 enable_metadata: bool = True,
                 allow_prompt: bool = True,
                 original_name: str | None = None,
                 ) -> tuple[bool, str, str]:
    """Convert a single file with all enhancements.

    Returns (success, report, errors_path):
      - success: True if conversion completed
      - report: human-readable summary (stdout)
      - errors_path: path to sidecar .errors.md if table errors were detected,
                     empty string otherwise. Caller (AI) should read this file,
                     fix the .md, then delete it.

    enable_metadata: prepend a metadata header (# title / Source / Format) to
    the output. The header is injected BEFORE table detection so the sidecar
    .errors.md line numbers match the final written file.

    allow_prompt: when True (default), encrypted files without a keyring
    credential will show a Windows CredUI dialog for password input. Set
    False to skip prompting (use only keyring) — useful in agent/CI contexts.

    original_name: when the driver pre-decrypts an encrypted file to a temp
    path (e.g. ``.__decrypted_foo.docx``) and passes that temp path as
    ``input_path``, set ``original_name`` to the **original** filename
    (e.g. ``foo.docx``) so the metadata header, reports, and sidecar reference
    the user-visible name rather than the temp file. When None, the
    ``input_path`` name/stem is used (default behaviour for direct callers).
    """
    md = MarkItDown()
    report: list[str] = []
    errors_path = ""

    # Display name overridden by the dynamic driver (pre-decrypt temp-file
    # scenario). Falls back to the real input_path attributes for direct use.
    disp_name = original_name or input_path.name
    disp_stem = Path(disp_name).stem if original_name else input_path.stem

    # Pre-conversion: check for encryption
    from _decrypt import decrypt_docx
    from _decrypt import is_encrypted as _is_encrypted

    if _is_encrypted(input_path):
        report.append(f"[ENCRYPTED] {disp_name}")
        try:
            buf = decrypt_docx(input_path, allow_prompt=allow_prompt)
        except RuntimeError as e:
            # pywin32 missing — surface a clear actionable message.
            return False, "\n".join(report + [f"  {e}"]), ""
        if buf is None:
            if not allow_prompt:
                report.append(
                    "  Skipped (no keyring credential; use --no-prompt to skip"
                    " prompting, or pre-store via:"
                    f" python -c \"import keyring; keyring.set_password('markitdown-enhanced','{disp_stem}','<pw>')\"")
            else:
                report.append("  Skipped (user cancelled or decryption failed).")
            return False, "\n".join(report), ""
        # Convert decrypted stream + capture bytes for table detection
        decrypted_bytes: bytes | None = None
        try:
            decrypted_bytes = buf.getvalue()
            # Pre-evaluate XLSX formulas on the decrypted bytes
            raw = _maybe_eval_xlsx(decrypted_bytes, input_path.suffix)
            buf2 = io.BytesIO(raw) if raw != decrypted_bytes else buf
            result = md.convert_stream(buf2, file_extension=input_path.suffix)
            text = result.text_content or ""
        finally:
            buf.close()
    else:
        decrypted_bytes = None
        # Pre-evaluate XLSX formulas for non-encrypted .xlsx files
        raw_bytes = input_path.read_bytes()
        eval_bytes = _maybe_eval_xlsx(raw_bytes, input_path.suffix)
        if eval_bytes != raw_bytes:
            result = md.convert_stream(io.BytesIO(eval_bytes), file_extension=input_path.suffix)
        else:
            result = md.convert(str(input_path))
        text = result.text_content or ""

    # Resolve output path first (needed for error report path hint)
    if output_path:
        output_path = Path(output_path)
    else:
        output_path = input_path.with_suffix(".md")

    # Inject metadata header BEFORE _post_process so table-detection line
    # numbers in the sidecar .errors.md match the final written file.
    if enable_metadata:
        title = getattr(result, "title", None) or disp_stem
        text = _format_metadata_header(title, disp_name, input_path.suffix) + text

    # Post-conversion: pass decrypted bytes for encrypted files so mammoth
    # can actually parse the document (instead of re-opening the encrypted file)
    mammoth_html = _get_mammoth_html(input_path, decrypted_bytes) if enable_table_detect else None
    fixed_text, post_report, error_report = _post_process(
        text, enable_table_detect, mammoth_html, md_path=str(output_path)
    )
    if post_report:
        report.append(post_report)

    # Write md output
    output_path.write_text(fixed_text, encoding="utf-8")
    report.append(f"[OK] {output_path}")

    # Write sidecar .errors.md for AI consumption (stage 2 input)
    if error_report:
        errors_path = str(output_path.with_suffix(output_path.suffix + ".errors.md"))
        Path(errors_path).write_text(error_report, encoding="utf-8")
        report.append(f"[TABLE_ERRORS] {errors_path}")
        report.append(
            "  AI: read this sidecar file, fix the .md using the HTML_REFERENCE,"
            " then delete the sidecar file."
        )

    return True, "\n".join(report), errors_path


def scan_encrypted(input_path: Path) -> str:
    """Scan for encrypted files and report credential status."""
    from _decrypt import detect_encrypted, scan_and_report

    result = scan_and_report(input_path)
    lines = [f"Scan: {input_path}", f"  Encrypted files found: "
             f"{len(result['decryptable']) + len(result['missing_credential']) + len(result['failed'])}"]
    if result["decryptable"]:
        lines.append(f"  Decryptable (credential found): {len(result['decryptable'])}")
        for f in result["decryptable"]:
            lines.append(f"    {f.name}")
    if result["missing_credential"]:
        lines.append(f"  Missing credential: {len(result['missing_credential'])}")
        for f in result["missing_credential"]:
            lines.append(f"    {f.name} -> add credential '{f.stem}'")
    if result["failed"]:
        lines.append(f"  Failed (wrong password?): {len(result['failed'])}")
        for f in result["failed"]:
            lines.append(f"    {f.name}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="markitdown-enhanced single-file converter")
    ap.add_argument("input", nargs="?", help="Input file path")
    ap.add_argument("-o", "--output", help="Output file path (default: input.md)")
    ap.add_argument("--scan-encrypted", help="Scan directory for encrypted files (no conversion)")
    ap.add_argument("--no-table-detect", action="store_true",
                    help="Skip table structure detection")
    ap.add_argument("--no-metadata", action="store_true",
                    help="Skip the metadata header (# title / Source / Format)")
    ap.add_argument("--no-prompt", action="store_true",
                    help="Skip encrypted-file password dialog; use only keyring (agent/CI safe)")
    args = ap.parse_args()

    if args.scan_encrypted:
        print(scan_encrypted(Path(args.scan_encrypted)))
        return

    if not args.input:
        ap.error("input file or --scan-encrypted required")

    success, report, errors_path = convert_file(
        Path(args.input),
        Path(args.output) if args.output else None,
        enable_table_detect=not args.no_table_detect,
        enable_metadata=not args.no_metadata,
        allow_prompt=not args.no_prompt,
    )
    print(report)
    if not success:
        sys.exit(1)
    # Exit code 1 when table errors were detected — signals the AI driver
    # that stage 2 (md fixing) is needed. The conversion itself succeeded.
    if errors_path:
        sys.exit(1)


if __name__ == "__main__":
    main()
