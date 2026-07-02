#!/usr/bin/env python3
"""hash_diff.py — Per-object SHA256 change detection for DOORS raw JSON.

Two subcommands:
  gen  <raw.json> [--module-path PATH] [--check]
      Compute per-object hashes and write <raw.json>.sha256.json.
      --module-path  Optional DOORS module path stored in the product for cross-check.
      --check        Compare computed hashes against an existing .sha256.json
                     (verify raw was not tampered); do NOT overwrite.

  diff <raw.json> [--against OTHER_RAW]
      Compare <raw.json> against the previous extraction of the same module
      (auto-discovered by filename prefix) and print a change report.
      Writes <raw.json>.diff.json (machine-readable full report).
      --against  Override auto-discovery; compare against this specific raw file.

Hashing scheme (N3):
  sha256(json.dumps({"id":..,"abs_ref":..,"attrs":..}, sort_keys=True, ensure_ascii=False))

Exit codes:
  0  success (including first-extraction E3 case)
  1  user-level problem (no previous to diff, all objects malformed, etc.)
  2  data corruption (raw JSON unreadable)

See SKILL.md §4.7 for invocation context.
"""

import argparse
import glob
import hashlib
import json
import os
import re
import sys
from datetime import datetime

# Threshold for abs_ref listing in stdout summary (L4 adaptive truncation)
LIST_THRESHOLD = 20

# Filename pattern: <PREFIX>_<YYYYMMDD>_<HHMMSS>_raw.json
# Timestamp segment = last 3 underscore-separated tokens before .json
TIMESTAMP_RE = re.compile(r'^(?P<prefix>.+?)_(?P<date>\d{8})_(?P<time>\d{6})_raw\.json$')


# =============================================================================
# CORE HASHING
# =============================================================================

def obj_hash(obj):
    """Compute canonical SHA256 of a single DOORS object (N3 scheme).

    Includes id + abs_ref + attrs. sort_keys for order-stability;
    ensure_ascii=False so CJK attribute values hash consistently across platforms.
    """
    canonical = {
        "id": obj.get("id", ""),
        "abs_ref": obj.get("abs_ref"),
        "attrs": obj.get("attrs", {}),
    }
    s = json.dumps(canonical, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def build_hash_index(data):
    """Build {abs_ref_str: hash} from a raw JSON object list.

    Objects with missing/non-integer abs_ref are skipped (E15).
    Returns (index, skipped_count).
    """
    index = {}
    skipped = 0
    for obj in data:
        abs_ref = obj.get("abs_ref")
        if abs_ref is None or not isinstance(abs_ref, (int, float)):
            skipped += 1
            continue
        # Normalize to int if it's a whole float (e.g. 12345.0 -> 12345)
        if isinstance(abs_ref, float) and abs_ref.is_integer():
            abs_ref = int(abs_ref)
        key = str(abs_ref)
        index[key] = obj_hash(obj)
    return index, skipped


def load_raw(path):
    """Load raw JSON. Friendly error on corruption (E8).

    Uses utf-8-sig to tolerate a leading BOM (some extraction pipelines emit one).
    """
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: raw file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: raw JSON corrupted: {path}", file=sys.stderr)
        print(f"  detail: {e}", file=sys.stderr)
        print("  See references/error-handling.md (JSON corrupted row).", file=sys.stderr)
        sys.exit(2)


# =============================================================================
# GEN SUBCOMMAND
# =============================================================================

def extract_timestamp(filename):
    """Extract (prefix, 'YYYYMMDD_HHMMSS') from raw filename, or (None, None)."""
    m = TIMESTAMP_RE.match(os.path.basename(filename))
    if not m:
        return None, None
    return m.group('prefix'), m.group('date') + '_' + m.group('time')


def cmd_gen(args):
    raw_path = os.path.abspath(args.raw)
    sha_path = raw_path + ".sha256.json"

    data = load_raw(raw_path)
    index, skipped = build_hash_index(data)

    # Extract timestamp from filename for the extracted_at field
    _, ts = extract_timestamp(raw_path)
    extracted_at = ts if ts else datetime.now().strftime("%Y%m%d_%H%M%S")

    if args.check:
        # E10 --check mode: compare against existing, do NOT overwrite
        if not os.path.exists(sha_path):
            print(f"ERROR: --check requires existing {sha_path}, none found.", file=sys.stderr)
            sys.exit(1)
        with open(sha_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        existing_hashes = existing.get("hashes", {})
        # Compare
        all_keys = set(index) | set(existing_hashes)
        mismatch = [k for k in all_keys if index.get(k) != existing_hashes.get(k)]
        if not mismatch:
            print(f"OK: {len(index)} hashes match stored .sha256.json (raw not tampered).")
            return
        print(f"MISMATCH: {len(mismatch)} of {len(all_keys)} hashes differ from stored.", file=sys.stderr)
        print(f"  raw may have been modified after extraction, or abs_ref schema changed.", file=sys.stderr)
        print(f"  first 10 differing abs_ref: {sorted(mismatch)[:10]}", file=sys.stderr)
        sys.exit(1)

    # Normal gen: write product
    product = {
        "source_file": os.path.basename(raw_path),
        "extracted_at": extracted_at,
        "module_path": args.module_path or "",
        "object_count": len(data),
        "hash_count": len(index),
        "skipped_count": skipped,
        "hashes": index,
    }
    with open(sha_path, 'w', encoding='utf-8') as f:
        json.dump(product, f, ensure_ascii=False, indent=2)
    print(f"GEN: wrote {sha_path}")
    print(f"  objects: {len(data)}  hashed: {len(index)}  skipped: {skipped}")
    if skipped:
        print(f"  WARNING: {skipped} objects skipped (missing/non-numeric abs_ref).",
              file=sys.stderr)


# =============================================================================
# DIFF SUBCOMMAND
# =============================================================================

def find_previous_raw(raw_path):
    """Auto-discover the previous raw file of the same module (M4).

    Strategy:
      1. Match by filename prefix (strip _YYYYMMDD_HHMMSS_raw).
      2. Among prefix-matched files with earlier timestamp, pick the newest.
      3. If both have module_path in their .sha256.json, cross-check; warn on mismatch.
    Returns (prev_raw_path, prev_sha_path) or (None, None).
    """
    prefix, cur_ts = extract_timestamp(raw_path)
    if prefix is None:
        print(f"ERROR: raw filename does not match <PREFIX>_<YYYYMMDD>_<HHMMSS>_raw.json: "
              f"{os.path.basename(raw_path)}", file=sys.stderr)
        return None, None

    raw_dir = os.path.dirname(raw_path)
    pattern = os.path.join(raw_dir, f"{prefix}_*_raw.json")
    candidates = []
    for p in glob.glob(pattern):
        p_abs = os.path.abspath(p)
        if p_abs == raw_path:
            continue
        _, ts = extract_timestamp(p)
        if ts and ts < cur_ts:
            candidates.append((ts, p_abs))
    if not candidates:
        return None, None
    # Newest among earlier = previous
    candidates.sort(reverse=True)
    prev_ts, prev_raw = candidates[0]
    return prev_raw, prev_raw + ".sha256.json"


def crosscheck_module_path(raw_sha_path, prev_sha_path):
    """If both .sha256.json files have module_path set, warn on mismatch (M4)."""
    try:
        with open(raw_sha_path, 'r', encoding='utf-8') as f:
            raw_meta = json.load(f)
        with open(prev_sha_path, 'r', encoding='utf-8') as f:
            prev_meta = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return
    rp = raw_meta.get("module_path", "")
    pp = prev_meta.get("module_path", "")
    if rp and pp and rp != pp:
        print(f"WARNING: module_path mismatch — current='{rp}' vs previous='{pp}'. "
              f"Prefix matched but module paths differ; diff may be across modules.",
              file=sys.stderr)


def render_abs_ref_list(items, threshold=LIST_THRESHOLD):
    """L4 adaptive: show all if <=threshold, else first `threshold` + total note."""
    if len(items) <= threshold:
        return "[" + ", ".join(str(x) for x in items) + "]"
    head = ", ".join(str(x) for x in items[:threshold])
    return f"[{head}, ... (共 {len(items)} 个，详见 .diff.json)]"


def cmd_diff(args):
    raw_path = os.path.abspath(args.raw)
    sha_path = raw_path + ".sha256.json"

    data = load_raw(raw_path)
    cur_index, cur_skipped = build_hash_index(data)

    # Ensure current raw has a .sha256.json (gen if missing)
    if not os.path.exists(sha_path):
        print(f"NOTE: {os.path.basename(sha_path)} missing; generating now for future use.",
              file=sys.stderr)
        _write_sha_product(raw_path, sha_path, cur_index, data, cur_skipped, args.module_path)

    # Resolve previous raw
    if args.against:
        prev_raw = os.path.abspath(args.against)
        prev_sha = prev_raw + ".sha256.json"
        if not os.path.exists(prev_raw):
            print(f"ERROR: --against file not found: {prev_raw}", file=sys.stderr)
            sys.exit(1)
    else:
        prev_raw, prev_sha = find_previous_raw(raw_path)

    if prev_raw is None:
        # E3: first extraction — still wrote current hash above
        print("首次抽取: 同模块无历史 raw 可对比。")
        print(f"  已生成 {os.path.basename(sha_path)}，下次抽取后即可 diff。")
        return

    # E5: if previous has no .sha256.json, auto-gen it
    if not os.path.exists(prev_sha):
        print(f"NOTE: previous raw lacks .sha256.json; auto-generating for {os.path.basename(prev_raw)}.",
              file=sys.stderr)
        prev_data = load_raw(prev_raw)
        prev_index, prev_skipped = build_hash_index(prev_data)
        _write_sha_product(prev_raw, prev_sha, prev_index, prev_data, prev_skipped, "")
    else:
        with open(prev_sha, 'r', encoding='utf-8') as f:
            prev_product = json.load(f)
        prev_index = prev_product.get("hashes", {})
        prev_skipped = prev_product.get("skipped_count", 0)

    # M4 cross-check module_path if both have it
    if os.path.exists(sha_path):
        crosscheck_module_path(sha_path, prev_sha)

    # Compute diff
    cur_keys = set(cur_index)
    prev_keys = set(prev_index)
    added_keys = sorted(cur_keys - prev_keys, key=lambda k: int(k))
    removed_keys = sorted(prev_keys - cur_keys, key=lambda k: int(k))
    modified_keys = sorted(
        [k for k in (cur_keys & prev_keys) if cur_index[k] != prev_index[k]],
        key=lambda k: int(k)
    )
    unchanged = len(cur_keys & prev_keys) - len(modified_keys)

    added = [{"abs_ref": int(k), "hash": cur_index[k]} for k in added_keys]
    removed = [{"abs_ref": int(k), "hash": prev_index[k]} for k in removed_keys]
    modified = [{"abs_ref": int(k), "old_hash": prev_index[k], "new_hash": cur_index[k]}
                for k in modified_keys]

    total_changes = len(added) + len(removed) + len(modified)

    # Write machine-readable .diff.json
    diff_path = raw_path + ".diff.json"
    diff_product = {
        "current": os.path.basename(raw_path),
        "previous": os.path.basename(prev_raw),
        "compared_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": {
            "unchanged": unchanged,
            "added": len(added),
            "removed": len(removed),
            "modified": len(modified),
            "skipped": cur_skipped + prev_skipped,
        },
        "added": added,
        "removed": removed,
        "modified": modified,
        "skipped": cur_skipped + prev_skipped,
    }
    with open(diff_path, 'w', encoding='utf-8') as f:
        json.dump(diff_product, f, ensure_ascii=False, indent=2)

    # Print stdout summary (L4 adaptive)
    _, cur_ts = extract_timestamp(raw_path)
    _, prev_ts = extract_timestamp(prev_raw)
    cur_label = cur_ts or os.path.basename(raw_path)
    prev_label = prev_ts or os.path.basename(prev_raw)

    # Derive module label from prefix
    prefix, _ = extract_timestamp(raw_path)
    module_label = prefix or os.path.basename(raw_path)

    print(f"模块 {module_label} 变更报告")
    print(f"对比: {cur_label} (当前)  vs  {prev_label} (上次)")
    print("─" * 40)
    total_objects = unchanged + len(added) + len(modified)
    print(f"✓ 未变: {unchanged} / {total_objects + len(removed)}")
    print(f"+ 新增: {len(added)}   {render_abs_ref_list(added_keys)}")
    print(f"- 删除: {len(removed)}   {render_abs_ref_list(removed_keys)}")
    print(f"~ 修改: {len(modified)}  {render_abs_ref_list(modified_keys)}")
    if cur_skipped + prev_skipped > 0:
        print(f"⚠ 跳过: {cur_skipped + prev_skipped} 个畸形对象 (abs_ref 缺失/非数值)")
    if total_changes == 0:
        print("结论: 内容未变 (无差异)")
    else:
        print(f"结论: 内容已变更 ({total_changes} 处差异)")
    print(f"机读全文: {diff_path}")


def _write_sha_product(raw_path, sha_path, index, data, skipped, module_path):
    """Shared helper: write .sha256.json product (used by cmd_diff for auto-gen)."""
    _, ts = extract_timestamp(raw_path)
    extracted_at = ts if ts else datetime.now().strftime("%Y%m%d_%H%M%S")
    product = {
        "source_file": os.path.basename(raw_path),
        "extracted_at": extracted_at,
        "module_path": module_path or "",
        "object_count": len(data),
        "hash_count": len(index),
        "skipped_count": skipped,
        "hashes": index,
    }
    with open(sha_path, 'w', encoding='utf-8') as f:
        json.dump(product, f, ensure_ascii=False, indent=2)


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        prog="hash_diff.py",
        description="Per-object SHA256 change detection for DOORS raw JSON.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("gen", help="Generate .sha256.json for a raw file.")
    p_gen.add_argument("raw", help="Path to *_raw.json")
    p_gen.add_argument("--module-path", default=None,
                       help="Optional DOORS module path (e.g. /VW/10638/SysRS) for cross-check.")
    p_gen.add_argument("--check", action="store_true",
                       help="Verify against existing .sha256.json without overwriting.")
    p_gen.set_defaults(func=cmd_gen)

    p_diff = sub.add_parser("diff", help="Compare raw against previous extraction.")
    p_diff.add_argument("raw", help="Path to *_raw.json (current)")
    p_diff.add_argument("--against", default=None,
                        help="Override: compare against this specific raw file.")
    p_diff.add_argument("--module-path", default=None,
                        help="Optional DOORS module path (used if auto-gen of current hash is needed).")
    p_diff.set_defaults(func=cmd_diff)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
