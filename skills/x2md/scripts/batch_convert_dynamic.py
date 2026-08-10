# -*- coding: utf-8 -*-
"""Size-aware dynamic batch converter for x2md.

Each file converts in its **own isolated Python subprocess** (via
``convert_single_enhanced.py``), so a native-handle hang / memory leak /
CredUI freeze in markitdown or pywin32 never degrades the driver process.
The driver kills the subprocess via ``subprocess.run(timeout=...)`` and
moves on.

Three dynamic behaviours driven by file size (inherited from the original
markitdown dynamic converter, re-calibrated from a 1382-record failure log):

  1. **Dynamic timeout** — small files get a short timeout (fail fast);
     large files get a long timeout (avoid killing slow-but-valid big PDFs).
  2. **Small-files-first ordering** — tiny files run first so the completed
     count rises quickly; big / slow files go last.
  3. **Large-file concurrency cap** — a semaphore limits how many "heavy"
     (>= 10 MB) files convert at once, preventing memory blow-ups.
  4. **Lenient retry** — a file that times out on the first attempt is
     retried once at 3x the timeout before being given up (only for files
     >= 2 MB; small hung files never recover, so retry wastes time).

**Enhanced-pipeline additions** (vs. the plain markitdown dynamic converter):

  * **Pre-decrypt** — the driver pre-scans encrypted files and decrypts them
    *in-process* (so ``_decrypt._PASSWORD_CACHE`` is shared across all
    same-password files — one CredUI prompt per password, not per file).
    Decrypted bytes are written to a temp file (``.__dec_<stem>.docx``) in
    the output dir; the subprocess receives the temp path plus
    ``--original-name`` so metadata / sidecars still show the real filename.
    Temp files are cleaned up at the end of the run.
  * **Sidecar collection** — each subprocess may emit a ``[SIDECAR] <path>``
    marker on stdout. The driver collects all sidecar paths and writes them
    to ``_sidecars.txt`` in the output dir for stage-2 AI fixing, and prints
    a summary list at the end.
  * **Flag pass-through** — the driver's ``--no-table-detect`` /
    ``--no-metadata`` / ``--no-prompt`` flags are forwarded to every
    subprocess so batch control matches single-file ``_convert_core.py``.

Supports **resume** (skips files whose ``.md`` output already exists) and
writes a fail-log (``_conversion_failures_dynamic.log``).

Usage:
    python batch_convert_dynamic.py \\
        --source <dir | list.json | list.txt> \\
        [--outdir OUTDIR] [--workers N] [--heavy-max N] [--limit N]
        [--recursive] [--extensions .pdf .docx ...] \\
        [--no-table-detect] [--no-metadata] [--no-prompt] [--keep-temp]

JSON source format:
    {"files": ["path/a.pdf", "path/b.docx", ...]}   # or a bare JSON array
TXT source format: one file path per non-blank line (# comments allowed)
Directory mode: ``--source <directory>`` (optionally ``--recursive``) plus
``--extensions`` to filter; defaults to all supported office formats.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
SINGLE = str(HERE / "convert_single_enhanced.py")
PYTHON = sys.executable

# Default extensions when --source points at a directory.
DEFAULT_EXTENSIONS = [".pdf", ".docx", ".pptx", ".xlsx", ".html",
                      ".jpg", ".jpeg", ".png", ".csv"]

# Temp-decrypt file prefix — cleaned up at end of run unless --keep-temp.
TEMP_PREFIX = ".__dec_"


# --- Size -> timeout ladder (bytes, seconds) -------------------------------
# RECALIBRATED from real failure-log analysis (_conversion_failures_dynamic.log,
# 1382 records after partial full-run):
#   - 57% of files are <0.5MB (parse ~5s), but 280 of them TIME OUT at 15s.
#     -> these are corrupt/scanned/hung PDFs, NOT slow. 8s is enough to either
#        finish or confirm a hang; the previous 15s (x3 retry = up to 45s each)
#        burned ~70 min on files that never convert. Fast-fail is correct.
#   - NO timeout observed above 6.6MB. Large-file bands keep generous timeouts.
#   - Retry logic (RETRY_MULTIPLIER) is now restricted to files >=2MB: tiny hung
#        files won't suddenly succeed with more time.
# Parse baseline remains ~9.5 s/MB; bands give ample headroom for valid files.
SIZE_TIMEOUT_LADDER: list[tuple[int, int]] = [
    # (up_to_bytes, timeout_seconds)
    (512 * 1024, 8),              # < 0.5 MB -> 8s   (hung small files fail fast)
    (2 * 1024 * 1024, 30),        # < 2 MB   -> 30s  (30%, parse <19s)
    (5 * 1024 * 1024, 100),       # < 5 MB   -> 100s (9%, parse <47.5s)
    (10 * 1024 * 1024, 200),      # < 10 MB  -> 200s (2.7%, parse <95s)
    (50 * 1024 * 1024, 540),      # < 50 MB  -> 540s (0.9%, parse <475s)
    (float("inf"), 1200),         # >= 50 MB -> 1200s (0.1%)
]
HEAVY_THRESHOLD = 10 * 1024 * 1024   # files >= 10 MB count as "heavy"
RETRY_MULTIPLIER = 3                 # timed-out file retried at 3x its timeout
RETRY_MIN_BYTES = 2 * 1024 * 1024    # retry only files >= 2MB (small hangs are deterministic)

# --- Cold-start-aware timeout floor (2026-08-06) ---------------------------
# markitdown's import chain pulls in heavy, lazily-imported deps per FORMAT
# (mammoth for docx, openpyxl for xlsx, python-pptx for pptx ...). Each converted
# file runs in its OWN subprocess (convert_single_enhanced.py), so with N workers
# there are N simultaneous cold-start imports competing for CPU/disk. On a slow
# machine a single small docx was measured at **~31s** (just the import, before
# any parsing); the <0.5MB→8s band then misfires — every office file is killed
# mid-cold-start even though it would finish ~2s later.
#
# Two safeguards (both applied in ``classify_size``):
#   1. HEAVY_IMPORT_TIMEOUT_FLOOR — for office formats, raise the effective
#      timeout to at least this floor. PDF is INTENTIONALLY excluded: the
#      1382-record calibration showed small PDFs that time out are genuinely
#      hung (scanned → OCR trigger), not slow-to-import, so fast-fail must
#      stay (do NOT add ".pdf" here without re-running the failure analysis).
#   2. timeout_mult — a global CLI multiplier (--timeout-mult) for a slow
#      machine where even the cold start of lighter formats (csv/html) or PDF
#      exceeds the calibrated band. Default 1.0 (off).
# A normal/fast machine is unaffected: a 6s-cold-start docx still clears the
# 40s floor handily, and csv/html bands are untouched.
HEAVY_IMPORT_EXTS = {".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt"}
HEAVY_IMPORT_TIMEOUT_FLOOR = 40   # seconds; office cold-start floor


def safe_stem(name: str) -> str:
    base = os.path.splitext(os.path.basename(name))[0]
    base = re.sub(r'[\\/:*?"<>|]', "_", base)
    base = re.sub(r"\s+", " ", base).strip()
    if len(base) > 120:
        base = base[:120]
    return base or "unnamed"


def classify_size(path: str, timeout_mult: float = 1.0) -> tuple[int, int]:
    """Return (size_bytes, timeout_seconds) for a path. Missing file -> 0.

    Applies two corrections on top of ``SIZE_TIMEOUT_LADDER``:
      1. ``HEAVY_IMPORT_TIMEOUT_FLOOR`` — office formats (doc/xlsx/pptx) pull in
         heavy deps (mammoth/openpyxl/python-pptx) on first import; their
         cold-start (~6-31s observed) shouldn't be misjudged as a hang on small
         files. PDF is excluded (its fast-fail band is deliberately calibrated).
      2. ``timeout_mult`` — a global multiplier (from ``--timeout-mult``) for a
         slow-machine escape hatch.
    The floor is applied BEFORE the multiplier, so the floor is an absolute
    minimum and a slowed-down machine may still raise it via ``timeout_mult``.
    """
    try:
        size = os.path.getsize(path)
    except OSError:
        size = 0
    for up_to, secs in SIZE_TIMEOUT_LADDER:
        if size <= up_to:
            break
    else:
        secs = SIZE_TIMEOUT_LADDER[-1][1]
    # Format-aware cold-start floor (office formats only — see module docstring).
    ext = Path(path).suffix.lower()
    if ext in HEAVY_IMPORT_EXTS:
        secs = max(secs, HEAVY_IMPORT_TIMEOUT_FLOOR)
    # Global slow-machine multiplier.
    if timeout_mult != 1.0:
        secs = int(secs * timeout_mult)
    return (size, secs)


def build_subprocess_args(src: str, outdir: str, out_name: str,
                          no_table_detect: bool, no_metadata: bool,
                          no_prompt: bool,
                          original_name: str | None = None) -> list[str]:
    """Assemble the argv list for convert_single_enhanced.py."""
    cmd = [PYTHON, SINGLE, src, outdir, out_name]
    if no_table_detect:
        cmd.append("--no-table-detect")
    if no_metadata:
        cmd.append("--no-metadata")
    if no_prompt:
        cmd.append("--no-prompt")
    if original_name:
        cmd += ["--original-name", original_name]
    return cmd


def run_convert(src: str, outdir: str, out_name: str,
                timeout: int, *, no_table_detect: bool, no_metadata: bool,
                no_prompt: bool, original_name: str | None = None,
                ) -> tuple[str, str, str | None]:
    """Invoke convert_single_enhanced.py.

    Returns (status, message, sidecar_path).
      status ∈ {"ok", "skip", "miss", "unsupported", "fail", "timeout"}
      sidecar_path is set when the subprocess emitted ``[SIDECAR] <path>``.
    """
    cmd = build_subprocess_args(src, outdir, out_name,
                                no_table_detect, no_metadata, no_prompt,
                                original_name)
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        code = proc.returncode
        # Parse [SIDECAR] marker from stdout regardless of exit code.
        sidecar: str | None = None
        for ln in (proc.stdout or "").splitlines():
            if "[SIDECAR]" in ln:
                # Take the LAST sidecar marker (a file can have at most one).
                sidecar = ln.split("[SIDECAR]", 1)[1].strip()
        if code == 0:
            return ("ok", "", sidecar)
        # Exit-code mapping mirrors convert_single_enhanced.py contract.
        if code == 5:
            return ("skip", "already_exists", None)
        if code == 2:
            return ("miss", "not_found", None)
        if code == 3:
            return ("unsupported", "unsupported_ext", None)
        # code 1 = conversion failure OR table errors (sidecar already parsed).
        if code == 1 and sidecar:
            return ("ok", "table_errors", sidecar)  # conversion ok, needs fix
        # Real failure — surface the last meaningful stderr line.
        err_lines = [
            ln for ln in (proc.stderr or "").splitlines()
            if ln.strip()
            and "RuntimeWarning" not in ln
            and "Couldn't find ffmpeg" not in ln
            and "warn(" not in ln
        ]
        msg = (err_lines[-1] if err_lines else "empty_or_warn")[:80]
        return ("fail", msg, sidecar)
    except subprocess.TimeoutExpired:
        return ("timeout", f">{timeout}s", None)
    except Exception as exc:
        return ("fail", repr(exc)[:80], None)


def convert_one(src: str, outdir: str, size: int, timeout: int,
                heavy_sem: threading.Semaphore, *,
                no_table_detect: bool, no_metadata: bool, no_prompt: bool,
                original_name: str | None = None,
                ) -> tuple[str, str, str | None]:
    """Convert one file. Heavy files are gated by the large-file semaphore;
    a timed-out LARGE file (>= 2MB) is retried once with a lenient timeout.
    Small files that time out are genuinely hung (confirmed by failure-log
    analysis), so retrying wastes time — bail out immediately."""
    out_name = safe_stem(src) + ".md"
    held_heavy = False
    if size >= HEAVY_THRESHOLD:
        heavy_sem.acquire()
        held_heavy = True
    try:
        status, msg, sidecar = run_convert(
            src, outdir, out_name, timeout,
            no_table_detect=no_table_detect, no_metadata=no_metadata,
            no_prompt=no_prompt, original_name=original_name,
        )
        # Lenient retry ONLY for files >= 2MB: small hung files never recover.
        if status == "timeout" and size >= RETRY_MIN_BYTES:
            status, msg, sidecar = run_convert(
                src, outdir, out_name, timeout * RETRY_MULTIPLIER,
                no_table_detect=no_table_detect, no_metadata=no_metadata,
                no_prompt=no_prompt, original_name=original_name,
            )
        return status, msg, sidecar
    finally:
        if held_heavy:
            heavy_sem.release()


# --- Input source collection -----------------------------------------------

def collect_from_directory(directory: Path, extensions: list[str],
                           recursive: bool) -> list[str]:
    """List files under ``directory`` (optionally recursive), filtered by
    ``extensions``. Skips MS Office lock files (``~$``) and the driver's own
    temp-decrypt files (``__dec_``)."""
    files: list[Path] = []
    globber = directory.rglob if recursive else directory.glob
    for ext in extensions:
        ext_norm = ext if ext.startswith(".") else f".{ext}"
        for f in globber(f"*{ext_norm}"):
            files.append(f)
    # Filter lock/temp files, and deduplicate (case-insensitive FS safe).
    seen: set[str] = set()
    result: list[str] = []
    for f in files:
        name = f.name
        if name.startswith("~$"):
            continue
        if name.startswith(TEMP_PREFIX):
            continue
        key = str(f).lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(str(f))
    return result


def read_paths_from_list(source: Path) -> list[str]:
    """Read file paths from a JSON or TXT source list."""
    if source.suffix.lower() == ".json":
        with source.open("r", encoding="utf-8-sig", errors="replace") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and "files" in data:
            raw = [str(p).strip() for p in data["files"] if str(p).strip()]
        elif isinstance(data, list):
            raw = [str(p).strip() for p in data if str(p).strip()]
        else:
            raw = []
    else:
        with source.open("r", encoding="utf-8-sig", errors="replace") as fh:
            raw = [ln.strip() for ln in fh
                   if ln.strip() and not ln.strip().startswith("#")]
    seen, paths = set(), []
    for p in raw:
        if p not in seen:
            seen.add(p)
            paths.append(p)
    return paths


def resolve_source(source: Path, extensions: list[str],
                   recursive: bool) -> list[str]:
    """Resolve ``--source`` into an absolute file-path list.

    Auto-detect: if source is a directory -> directory scan; otherwise treat
    as a JSON/TXT path-list file.
    """
    if source.is_dir():
        return collect_from_directory(source, extensions, recursive)
    return read_paths_from_list(source)


# --- Pre-decrypt pass --------------------------------------------------------

def pre_decrypt_encrypted(paths: list[str], outdir: Path,
                          allow_prompt: bool, keep_temp: bool,
                          ) -> dict[str, tuple[str, str]]:
    """Pre-scan ``paths`` for encrypted office files and decrypt them in-process.

    Doing this in the **driver process** (not in each subprocess) preserves
    the ``_decrypt._PASSWORD_CACHE`` benefit: all files sharing the same
    password prompt CredUI / keyring only once, and the in-memory cache avoids
    repeated dialogs within the run.

    Returns a mapping ``original_path -> (temp_decrypted_path, original_filename)``
    for every file that was successfully decrypted. Non-encrypted files (and
    files whose decryption was skipped or failed) are NOT in the map — they are
    passed to subprocesses as-is and may re-attempt decryption there.

    Temp files are written to ``outdir`` with the prefix ``.__dec_`` and the
    original extension, so the subprocess picks the correct format handler.
    """
    outdir.mkdir(parents=True, exist_ok=True)
    try:
        sys.path.insert(0, str(HERE))
        from _decrypt import is_encrypted, decrypt_docx  # type: ignore
    except ImportError:
        # _decrypt.py unavailable (e.g. non-Windows) -> skip pre-decrypt;
        # subprocesses will handle encryption on their own (best-effort).
        return {}

    # Only office files are even candidates for encryption.
    office_exts = {".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls"}
    encrypted_paths: list[str] = []
    for p in paths:
        ext = Path(p).suffix.lower()
        if ext not in office_exts:
            continue
        try:
            if is_encrypted(Path(p)):
                encrypted_paths.append(p)
        except Exception:
            pass  # treat unreadable / non-zip files as non-encrypted

    if not encrypted_paths:
        return {}

    print(f"[INFO] Encrypted files found : {len(encrypted_paths)}", flush=True)
    mapping: dict[str, tuple[str, str]] = {}
    for orig in encrypted_paths:
        orig_path = Path(orig)
        stem = safe_stem(orig_path.name)
        original_filename = orig_path.name
        temp_name = f"{TEMP_PREFIX}{stem}{orig_path.suffix}"
        temp_path = outdir / temp_name
        try:
            buf = decrypt_docx(Path(orig), allow_prompt=allow_prompt)
        except Exception as exc:
            print(f"  [PRE-DECRYPT] {original_filename}: error {repr(exc)[:60]}", flush=True)
            continue
        if buf is None:
            print(f"  [PRE-DECRYPT] {original_filename}: skipped (no credential/cancelled)", flush=True)
            continue
        try:
            with open(temp_path, "wb") as tf:
                tf.write(buf.getvalue())
            mapping[orig] = (str(temp_path), original_filename)
            print(f"  [PRE-DECRYPT] {original_filename} -> {temp_name}", flush=True)
        finally:
            buf.close()
    print(f"[INFO] Pre-decrypted          : {len(mapping)}/{len(encrypted_paths)}", flush=True)
    return mapping


def cleanup_temp_files(outdir: Path, keep_temp: bool) -> None:
    """Delete all ``.__dec_*`` temp files from ``outdir`` unless --keep-temp."""
    if keep_temp:
        return
    removed = 0
    for f in outdir.glob(f"{TEMP_PREFIX}*"):
        try:
            f.unlink()
            removed += 1
        except OSError:
            pass
    if removed:
        print(f"[INFO] Cleaned up {removed} temp_decrypt file(s).", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Size-aware dynamic batch converter (x2md)")
    ap.add_argument("--source", required=True,
                    help="Directory (auto-scanned), or JSON/TXT file-list")
    ap.add_argument("--outdir", default=r"C:\download")
    ap.add_argument("--workers", type=int, default=13)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--heavy-max", type=int, default=3,
                    help="Max concurrent heavy (>=10MB) files")
    ap.add_argument("--recursive", "-r", action="store_true",
                    help="Recurse subdirectories (directory mode only)")
    ap.add_argument("--extensions", "-e", nargs="*", default=None,
                    help="Filter extensions (directory mode); default: office set")
    ap.add_argument("--no-table-detect", action="store_true",
                    help="Disable table structure detection (faster, no sidecar)")
    ap.add_argument("--no-metadata", action="store_true",
                    help="Skip the metadata header (# title / Source / Format)")
    ap.add_argument("--no-prompt", action="store_true",
                    help="Skip encrypted-file password dialog (keyring only; agent/CI safe)")
    ap.add_argument("--no-predecrypt", action="store_true",
                    help="Skip the driver-side pre-decrypt pass (each subprocess decrypts on its own)")
    ap.add_argument("--keep-temp", action="store_true",
                    help="Keep pre-decrypted temp files after the run (debug)")
    ap.add_argument("--timeout-mult", type=float, default=1.0, metavar="MULT",
                    help="Multiply ALL per-file timeouts by MULT (slow-machine escape). "
                         "Default 1.0. e.g. --timeout-mult 2 doubles every timeout band; "
                         "use when markitdown import/cold-start is slow on this host. "
                         "Office formats (doc/xlsx/pptx) already get an automatic 40s floor.")
    args = ap.parse_args()

    source = Path(args.source)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    fail_log = outdir / "_conversion_failures_dynamic.log"
    sidecar_list = outdir / "_sidecars.txt"

    exts = args.extensions if args.extensions else list(DEFAULT_EXTENSIONS)

    # Resolve the full input list.
    paths = resolve_source(source, exts, args.recursive)
    if args.limit:
        paths = paths[: args.limit]

    # --- Pre-decrypt pass (driver-side, preserves password cache) ----------
    pre_map: dict[str, tuple[str, str]] = {}
    if not args.no_predecrypt:
        pre_map = pre_decrypt_encrypted(
            paths, outdir,
            allow_prompt=not args.no_prompt,
            keep_temp=args.keep_temp,
        )

    # Skip files whose output already exists (resume)
    existing = {f.name for f in outdir.glob("*.md")}
    # Exclude temp files, sidecars, and our own summary files from "existing".
    existing = {n for n in existing if not n.startswith(TEMP_PREFIX)}
    todo_paths = [p for p in paths
                  if (safe_stem(p) + ".md") not in existing]

    print(f"[INFO] Unique paths : {len(paths)}", flush=True)
    print(f"[INFO] Already done : {len(paths) - len(todo_paths)} (skip)", flush=True)
    print(f"[INFO] To convert   : {len(todo_paths)}", flush=True)
    print(f"[INFO] Pre-decrypt  : {len(pre_map)} file(s) decrypted in-driver", flush=True)
    print(f"[INFO] Workers      : {args.workers}", flush=True)
    print(f"[INFO] Heavy cap    : {args.heavy_max} (>=10MB)", flush=True)
    print(f"[INFO] Retry mult   : x{RETRY_MULTIPLIER} on timeout", flush=True)
    floor_note = (f"office_floor={HEAVY_IMPORT_TIMEOUT_FLOOR}s "
                  f"({','.join(sorted(HEAVY_IMPORT_EXTS))})")
    if args.timeout_mult != 1.0:
        floor_note += f"  timeout_mult=x{args.timeout_mult:g}"
    print(f"[INFO] Timeout cfg  : {floor_note}", flush=True)
    print(f"[INFO] Mode         : DYNAMIC ENHANCED (size->timeout, small-first, subprocess-isolated)",
          flush=True)
    print(f"[INFO] Flags        : table_detect={not args.no_table_detect} "
          f"metadata={not args.no_metadata} prompt={not args.no_prompt}", flush=True)

    if not todo_paths:
        print("[INFO] Nothing to do.")
        cleanup_temp_files(outdir, args.keep_temp)
        return 0

    # Pre-scan sizes (threaded for network drives) and sort small-first.
    print("[INFO] Scanning file sizes...", flush=True)
    t_scan = time.time()
    sized: list[tuple[str, int, int]] = []  # (path, size, timeout)

    def _scan(p: str) -> tuple[str, int, int]:
        sz, secs = classify_size(p, timeout_mult=args.timeout_mult)
        return (p, sz, secs)

    with ThreadPoolExecutor(max_workers=32) as ex:
        for p, sz, secs in ex.map(_scan, todo_paths):
            sized.append((p, sz, secs))
    # Small files first; missing (size 0) sorted early so they fail fast.
    sized.sort(key=lambda t: t[1])
    scan_elapsed = time.time() - t_scan

    # Size distribution summary (matches survey bands: 0.5/2/5/10/50 MB).
    HMB = 1024 * 1024
    bands = {"<0.5MB": 0, "0.5-2MB": 0, "2-5MB": 0, "5-10MB": 0,
             "10-50MB": 0, ">=50MB": 0, "missing": 0}
    for _p, sz, _s in sized:
        if sz == 0:
            bands["missing"] += 1
        elif sz < 0.5 * HMB:
            bands["<0.5MB"] += 1
        elif sz < 2 * HMB:
            bands["0.5-2MB"] += 1
        elif sz < 5 * HMB:
            bands["2-5MB"] += 1
        elif sz < 10 * HMB:
            bands["5-10MB"] += 1
        elif sz < 50 * HMB:
            bands["10-50MB"] += 1
        else:
            bands[">=50MB"] += 1
    total = sum(bands.values())
    band_summary = "  ".join(
        f"{k}:{v}({v*100//max(total,1)}%)" if total else f"{k}:{v}"
        for k, v in bands.items())
    print(f"[INFO] Scan done : {scan_elapsed:.0f}s  total={len(sized)}",
          flush=True)
    print(f"[INFO] Bands    : {band_summary}", flush=True)

    fail_log.write_text("", encoding="utf-8")

    heavy_sem = threading.Semaphore(args.heavy_max)
    counts = {"ok": 0, "skip": 0, "miss": 0, "fail": 0, "timeout": 0,
              "unsupported": 0}
    reasons: dict[str, int] = {}
    all_sidecars: list[str] = []
    t0 = time.time()
    done = 0
    todo = sized  # list of (path, size, timeout)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {}
        for (p, sz, secs) in todo:
            # If pre-decrypted, pass the temp path + original filename so the
            # subprocess does NOT attempt decryption again (and keeps the real
            # name in metadata / sidecar).
            if p in pre_map:
                temp_path, original_name = pre_map[p]
                fut = ex.submit(
                    convert_one, temp_path, str(outdir), sz, secs, heavy_sem,
                    no_table_detect=args.no_table_detect,
                    no_metadata=args.no_metadata,
                    no_prompt=True,  # already decrypted; never prompt again
                    original_name=original_name,
                )
            else:
                fut = ex.submit(
                    convert_one, p, str(outdir), sz, secs, heavy_sem,
                    no_table_detect=args.no_table_detect,
                    no_metadata=args.no_metadata,
                    no_prompt=args.no_prompt,
                )
            futures[fut] = (p, sz, secs)

        for fut in as_completed(futures):
            p, sz, secs = futures[fut]
            status, msg, sidecar = fut.result()
            counts[status] = counts.get(status, 0) + 1
            if sidecar:
                all_sidecars.append(sidecar)
            if status not in ("ok", "skip"):
                reasons[msg[:30]] = reasons.get(msg[:30], 0) + 1
                tsize = f"{sz/1024/1024:.1f}MB" if sz else "0"
                with fail_log.open("a", encoding="utf-8") as fl:
                    fl.write(f"[{status}] {p}  ({tsize}, >{secs}s) -- {msg}\n")

            done += 1
            if done % 10 == 0 or done == len(todo):
                el = time.time() - t0
                rate = done / el if el > 0 else 0
                eta = (len(todo) - done) / rate if rate > 0 else 0
                nm = os.path.basename(p)[:40]
                print(f"[{done}/{len(todo)}] {el:.0f}s "
                      f"ok={counts['ok']} skip={counts['skip']} "
                      f"miss={counts['miss']} fail={counts['fail']} "
                      f"timeout={counts['timeout']} "
                      f"sidecars={len(all_sidecars)} "
                      f"eta={eta:.0f}s | {nm}", flush=True)

    # Write the sidecar list for stage-2 AI consumption.
    if all_sidecars:
        sidecar_list.write_text(
            "\n".join(all_sidecars) + "\n", encoding="utf-8")

    # Clean up pre-decrypt temp files.
    cleanup_temp_files(outdir, args.keep_temp)

    print("\n" + "=" * 60)
    el = time.time() - t0
    print(f"DONE  elapsed   : {el:.0f}s")
    print(f"DONE  success   : {counts['ok']}")
    print(f"DONE  skipped   : {counts['skip']}")
    print(f"DONE  missing   : {counts['miss']}")
    print(f"DONE  unsupported: {counts['unsupported']}")
    print(f"DONE  failed    : {counts['fail']}")
    print(f"DONE  timeout   : {counts['timeout']}")
    print(f"DONE  sidecars  : {len(all_sidecars)} (table errors waiting for stage-2 fix)")
    print(f"DONE  output    : {outdir}")
    print(f"DONE  failures  : {fail_log}")
    if all_sidecars:
        print(f"DONE  sidecar list: {sidecar_list}")
        print("Table errors detected (sidecar .errors.md written for stage-2 AI fix):")
        for sc in all_sidecars:
            print(f"  - {sc}")
    if reasons:
        print("Failure/timeout reasons:")
        for k, v in sorted(reasons.items(), key=lambda x: -x[1]):
            print(f"   {v:5d}  {k}")
    # Exit code: 0 if all ok/skip; 1 if any failure OR any sidecar needs fixing.
    has_failures = counts.get("fail", 0) + counts.get("timeout", 0) \
        + counts.get("miss", 0) + counts.get("unsupported", 0)
    return 0 if (has_failures == 0 and not all_sidecars) else 1


if __name__ == "__main__":
    sys.exit(main())
