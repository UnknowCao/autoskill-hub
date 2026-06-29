#!/usr/bin/env python3
"""Generic llm-wiki health-check lint — covers all 14 checks defined in SKILL.md.

Usage: python _lint.py [wiki_path]

If wiki_path is omitted, defaults to the parent directory of this script.
Works for any wiki instance following the llm-wiki schema.
"""

import os, re, sys, hashlib, yaml
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

# ---- Config ----
WIKI = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent)

# ---- Locate SCHEMA.md ----
schema_path = WIKI / "SCHEMA.md"
if not schema_path.exists():
    print(f"ERROR: SCHEMA.md not found at {schema_path}")
    print("This script must run inside a valid llm-wiki instance (needs SCHEMA.md).")
    sys.exit(1)

schema_text = schema_path.read_text(encoding="utf-8")

# ---- Parse SCHEMA for page directories ----
page_dirs_match = re.findall(r"│\s+├──\s+(\w+)/\s+#.*Layer 2", schema_text)
if not page_dirs_match:
    # Fallback: try broader pattern
    page_dirs_match = re.findall(r'^\s*(\w+)/\s+#\s*Layer 2', schema_text, re.MULTILINE)
PAGE_DIRS = page_dirs_match if page_dirs_match else ["entities", "concepts", "comparisons", "queries"]

# ---- Parse SCHEMA for raw directories ----
raw_dirs_match = re.findall(r"│\s+├──\s+(\w+)/\s+#.*Layer 1.*raw", schema_text)
if not raw_dirs_match:
    raw_dirs_match = [d for d in ["articles", "papers", "presentations", "spreadsheets",
                                    "documents", "transcripts", "assets", "other"]
                      if (WIKI / "raw" / d).is_dir()]
RAW_DIRS = [f"raw/{d}" for d in raw_dirs_match] if raw_dirs_match else []
# If still empty, scan raw/ for actual subdirs
if not RAW_DIRS:
    raw_root = WIKI / "raw"
    if raw_root.is_dir():
        RAW_DIRS = [f"raw/{d.name}" for d in raw_root.iterdir() if d.is_dir()]

# ---- Parse SCHEMA for required frontmatter fields ----
fm_section = re.search(r"## Frontmatter.*?\n  ```yaml\n(.*?)```", schema_text, re.DOTALL)
REQUIRED_FIELDS = []
if fm_section:
    for line in fm_section.group(1).strip().split("\n"):
        line = line.strip()
        if line and not line.startswith("#"):
            key = line.split(":")[0].strip()
            if key:
                REQUIRED_FIELDS.append(key)

# ---- Parse SCHEMA for valid types ----
type_match = re.search(r"type:\s*(\S.*)", schema_text)
VALID_TYPES = set()
if type_match:
    for t in type_match.group(1).split("|"):
        t = t.strip()
        if t and t != "--":
            VALID_TYPES.add(t)

# ---- Parse SCHEMA for tag taxonomy ----
tag_taxonomy = set()
tag_section = re.search(r"## Tag Taxonomy\n(.*?)(?=\n## |\Z)", schema_text, re.DOTALL)
if tag_section:
    for line in tag_section.group(1).split("\n"):
        tags = re.findall(r'`([a-z][a-z0-9_/-]+)`', line)
        tag_taxonomy.update(tags)

# ---- Defaults ----
if not PAGE_DIRS:
    PAGE_DIRS = ["entities", "concepts", "comparisons", "queries"]
if not REQUIRED_FIELDS:
    REQUIRED_FIELDS = ["title", "created", "updated", "type", "tags", "sources"]
if not VALID_TYPES:
    VALID_TYPES = {"entity", "concept", "comparison", "query", "summary"}

# ---- Gather all wiki pages ----
all_pages = []
for wd in PAGE_DIRS:
    d = WIKI / wd
    if not d.is_dir():
        continue
    for f in sorted(d.iterdir()):
        if f.suffix == ".md":
            rel = str(f.relative_to(WIKI)).replace("\\", "/")
            all_pages.append(rel)

all_slugs = {Path(p).stem for p in all_pages}

issues_p0 = []   # blocking
issues_p1 = []   # should fix
issues_info = [] # informational


def _normalize_fm(obj):
    """Recursively convert date/datetime objects in frontmatter to ISO strings.

    PyYAML parses bare YYYY-MM-DD values as datetime.date, which breaks
    downstream string operations (len, slice, comparison). This normalizer
    runs once at load time so all 15 checks see plain strings.
    """
    if isinstance(obj, date):
        return obj.strftime("%Y-%m-%d") if type(obj) is date else obj.isoformat()
    if isinstance(obj, dict):
        return {k: _normalize_fm(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_normalize_fm(v) for v in obj]
    return obj


def read_page(path):
    """Read a .md file, return (text, frontmatter_dict, body)."""
    text = (WIKI / path).read_text(encoding="utf-8", errors="replace")
    fm, body = {}, text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
                fm = _normalize_fm(fm)
            except yaml.YAMLError:
                pass
            body = parts[2]
    return text, fm, body


# ========== 1. ORPHAN PAGES ==========
print("=== 1. ORPHAN PAGES ===")
outgoing = defaultdict(set)
incoming = defaultdict(set)
for p in all_pages:
    slug = Path(p).stem
    text = (WIKI / p).read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r'\[\[([^\]|#]+?)(?:\|[^\]]+)?\]\]', text):
        target = m.group(1).strip().lower()
        outgoing[p].add(target)
        incoming[target].add(p)

orphan_count = 0
for p in all_pages:
    slug = Path(p).stem
    if slug not in incoming or len(incoming[slug]) == 0:
        msg = f"  ORPHAN: {p}"
        issues_p1.append(msg)
        print(msg)
        orphan_count += 1
if orphan_count == 0:
    print("  None.")


# ========== 2. BROKEN WIKILINKS ==========
print("\n=== 2. BROKEN WIKILINKS ===")
broken_count = 0
for p in all_pages:
    for target in sorted(outgoing[p]):
        if target not in all_slugs:
            msg = f"  BROKEN: {p} -> [[{target}]]"
            issues_p0.append(msg)
            print(msg)
            broken_count += 1
if broken_count == 0:
    print("  None.")


# ========== 3. INDEX COMPLETENESS ==========
print("\n=== 3. INDEX COMPLETENESS ===")
index_path = WIKI / "index.md"
if index_path.exists():
    index_text = index_path.read_text(encoding="utf-8")
    index_pages = set()
    for m in re.finditer(r'\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]', index_text):
        index_pages.add(m.group(1).strip().lower())

    main_slugs = {Path(p).stem for p in all_pages}

    pages_not_in_index = main_slugs - index_pages
    if pages_not_in_index:
        msg = f"  Main pages NOT in index: {sorted(pages_not_in_index)}"
        issues_p1.append(msg)
        print(msg)
    else:
        print("  All pages are in the index.")

    index_entries_not_pages = index_pages - all_slugs
    if index_entries_not_pages:
        msg = f"  Index entries with no page: {sorted(index_entries_not_pages)}"
        issues_p0.append(msg)
        print(msg)
    else:
        print("  All index entries have corresponding pages.")

    total_match = re.search(r"Total pages:\s*(\d+)", index_text)
    claimed = total_match.group(1) if total_match else "?"
    actual = len(main_slugs)
    print(f"  Index claims {claimed} pages, actual: {actual}")
    if str(actual) != claimed:
        msg = f"  INDEX DRIFT: claims {claimed} but actual = {actual}"
        issues_p1.append(msg)
        print(msg)
else:
    print("  SKIP: index.md not found.")


# ========== 4. FRONTMATTER VALIDATION ==========
print("\n=== 4. FRONTMATTER VALIDATION ===")
for p in all_pages:
    _, fm, _ = read_page(p)
    missing = [f for f in REQUIRED_FIELDS if f not in fm]
    if missing:
        msg = f"  MISSING in {p}: {missing}"
        issues_p0.append(msg)
        print(msg)
    t = fm.get("type", "")
    if t and t not in VALID_TYPES:
        msg = f"  INVALID TYPE: {p} type={t}"
        issues_p0.append(msg)
        print(msg)

# ---- raw/ file frontmatter ----
raw_fm_issues = 0
for rd in RAW_DIRS:
    d = WIKI / rd
    if not d.is_dir():
        continue
    for f in d.iterdir():
        if f.suffix != ".md":
            continue
        rel = str(f.relative_to(WIKI)).replace("\\", "/")
        text, fm, _ = read_page(rel)
        raw_missing = []
        if "created" not in fm:
            raw_missing.append("created")
        if "sha256" not in fm:
            raw_missing.append("sha256")
        # Markitdown-produced files need extra fields
        if fm.get("original_file"):
            if "original_sha256" not in fm:
                raw_missing.append("original_sha256")
        if raw_missing:
            msg = f"  RAW-MISSING in {rel}: {raw_missing}"
            issues_p1.append(msg)
            print(msg)
            raw_fm_issues += 1
if raw_fm_issues == 0:
    print("  All raw/.md files have required frontmatter.")


# ========== 5. STALE CONTENT ==========
print("\n=== 5. STALE CONTENT ===")
cutoff = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
stale_count = 0
for p in all_pages:
    _, fm, _ = read_page(p)
    updated = fm.get("updated", "")
    if updated and len(updated) >= 10 and updated[:10] < cutoff:
        msg = f"  STALE (>{abs((datetime.now() - datetime.strptime(updated[:10], '%Y-%m-%d'))).days}d): {p}"
        issues_p1.append(msg)
        print(msg)
        stale_count += 1
if stale_count == 0:
    print("  No stale pages (>90 days).")


# ========== 6. CONTRADICTIONS ==========
print("\n=== 6. CONTRADICTIONS / CONTESTED ===")
found = False
for p in all_pages:
    _, fm, _ = read_page(p)
    if fm.get("contested") is True:
        msg = f"  CONTESTED: {p}"
        issues_info.append(msg)
        print(msg)
        found = True
    contras = fm.get("contradictions", [])
    if contras:
        msg = f"  CONTRADICTIONS in {p}: {contras}"
        issues_info.append(msg)
        print(msg)
        found = True
if not found:
    print("  No contested/contradiction pages.")


# ========== 7. QUALITY SIGNALS ==========
print("\n=== 7. QUALITY SIGNALS ===")
low_conf, single_source_no_conf = [], []
for p in all_pages:
    _, fm, _ = read_page(p)
    conf = fm.get("confidence", "")
    if conf == "low":
        low_conf.append(p)
    elif not conf:
        sources = fm.get("sources", [])
        if isinstance(sources, list) and len(sources) <= 1:
            single_source_no_conf.append(p)
        elif isinstance(sources, str):
            single_source_no_conf.append(p)

if low_conf:
    msg = f"  LOW confidence: {low_conf}"
    issues_p1.append(msg)
    print(msg)
if single_source_no_conf:
    msg = f"  Single-source, NO confidence set: {single_source_no_conf}"
    issues_info.append(msg)
    print(msg)
if not low_conf and not single_source_no_conf:
    print("  All pages have appropriate confidence signals.")


# ========== 8. SOURCE DRIFT (SHA256) ==========
print("\n=== 8. SOURCE DRIFT (SHA256) ===")
for rd in RAW_DIRS:
    d = WIKI / rd
    if not d.is_dir():
        continue
    for f in d.iterdir():
        if f.suffix != ".md":
            continue
        rel = str(f.relative_to(WIKI)).replace("\\", "/")
        text, fm, body = read_page(rel)
        stored_sha = fm.get("sha256", "")
        if stored_sha:
            computed = hashlib.sha256(body.encode("utf-8")).hexdigest().lower()
            if computed != stored_sha.lower():
                msg = f"  DRIFT: {rel}  stored={stored_sha[:12]}… computed={computed[:12]}…"
                issues_p1.append(msg)
                print(msg)
            else:
                print(f"  MATCH: {rel}  ({computed[:12]}…)")
        else:
            print(f"  NO-SHA: {rel}")
        # Cross-validate original_sha256
        orig_file = fm.get("original_file")
        orig_sha = fm.get("original_sha256")
        if orig_file and orig_sha:
            orig_path = d / orig_file
            if orig_path.exists():
                orig_body = orig_path.read_bytes()
                computed_orig = hashlib.sha256(orig_body).hexdigest().lower()
                if computed_orig != orig_sha.lower():
                    msg = f"  ORIGINAL-DRIFT: {rel} → {orig_file}  stored={orig_sha[:12]}… computed={computed_orig[:12]}…"
                    issues_p1.append(msg)
                    print(msg)
            else:
                msg = f"  MISSING-ORIGINAL: {rel} references {orig_file} not found"
                issues_p1.append(msg)
                print(msg)


# ========== 9. UNCONVERTED FILES ==========
print("\n=== 9. UNCONVERTED FILES ===")
known_originals = set()
for rd in RAW_DIRS:
    d = WIKI / rd
    if not d.is_dir():
        continue
    for f in d.iterdir():
        if f.suffix == ".md":
            rel = str(f.relative_to(WIKI)).replace("\\", "/")
            _, fm, _ = read_page(rel)
            if fm.get("status") == "unconverted":
                msg = f"  UNCONVERTED: {rel}"
                issues_p1.append(msg)
                print(msg)
            orig = fm.get("original_file")
            if orig:
                known_originals.add(str((d / orig).resolve()))
        elif f.suffix != ".md":
            # Non-.md file — check if it has a companion .md
            companion = d / (f.stem + ".md")
            if not companion.exists():
                msg = f"  UNCONVERTED (orphan original): {str(f.relative_to(WIKI)).replace(chr(92), '/')}"
                issues_p1.append(msg)
                print(msg)


# ========== 10. LOW-QUALITY CONVERSIONS ==========
print("\n=== 10. LOW-QUALITY CONVERSIONS ===")
for rd in RAW_DIRS:
    d = WIKI / rd
    if not d.is_dir():
        continue
    for f in d.iterdir():
        if f.suffix != ".md":
            continue
        rel = str(f.relative_to(WIKI)).replace("\\", "/")
        _, fm, body = read_page(rel)
        if fm.get("quality") == "low":
            msg = f"  LOW-QUALITY (tagged): {rel}"
            issues_p1.append(msg)
            print(msg)
        # Heuristic: large original but tiny output
        orig_file = fm.get("original_file")
        if orig_file:
            orig_path = d / orig_file
            if orig_path.exists():
                orig_size = orig_path.stat().st_size
                body_words = len(body.split())
                if orig_size > 100_000 and body_words < 100:
                    msg = f"  LOW-QUALITY (heuristic: {orig_size}B → {body_words} words): {rel}"
                    issues_p1.append(msg)
                    print(msg)


# ========== 11. PAGE SIZE ==========
print("\n=== 11. PAGE SIZE (>200 lines = candidate for split) ===")
oversize = 0
for p in all_pages:
    lines = (WIKI / p).read_text(encoding="utf-8").split("\n")
    if len(lines) > 200:
        msg = f"  OVERSIZE ({len(lines)} lines): {p}"
        issues_p1.append(msg)
        print(msg)
        oversize += 1
if oversize == 0:
    print("  No oversized pages.")


# ========== 12. TAG AUDIT ==========
print("\n=== 12. TAG AUDIT ===")
all_tags_used = defaultdict(list)
for p in all_pages:
    _, fm, _ = read_page(p)
    tags = fm.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]
    for t in tags:
        if t:
            all_tags_used[t].append(p)

unknown_tags = {t for t in all_tags_used if t not in tag_taxonomy}
if tag_taxonomy and unknown_tags:
    print(f"  UNKNOWN tags (not in SCHEMA taxonomy):")
    for t in sorted(unknown_tags):
        msg = f"    `{t}` — used in: {all_tags_used[t]}"
        issues_info.append(msg)
        print(msg)
elif not tag_taxonomy:
    print("  SKIP: No tag taxonomy found in SCHEMA.md.")
else:
    print("  All tags in SCHEMA taxonomy.")


# ========== 13. LOG ROTATION ==========
print("\n=== 13. LOG ROTATION ===")
log_path = WIKI / "log.md"
if log_path.exists():
    log_lines = log_path.read_text(encoding="utf-8").split("\n")
    entry_count = sum(1 for l in log_lines if re.match(r"## \[\d{4}-\d{2}-\d{2}", l))
    print(f"  Log entries: {entry_count} (threshold: 500)")
    if entry_count > 500:
        msg = f"  LOG ROTATION NEEDED: {entry_count} entries"
        issues_p1.append(msg)
        print(msg)
else:
    print("  SKIP: log.md not found.")


# ========== 14. PROVENANCE MARKERS ==========
print("\n=== 14. PROVENANCE MARKERS ===")
pages_missing_prov = []
for p in all_pages:
    text, fm, _ = read_page(p)
    sources = fm.get("sources", [])
    if isinstance(sources, str):
        sources = [s.strip() for s in sources.split(",")]
    source_count = len([s for s in sources if s])
    if source_count >= 3:
        has_prov = bool(re.search(r"\^\[raw/", text))
        if not has_prov:
            pages_missing_prov.append(p)
if pages_missing_prov:
    msg = f"  3+ sources but NO provenance markers: {pages_missing_prov}"
    issues_info.append(msg)
    print(msg)
else:
    print("  All 3+ source pages have provenance markers (or none qualify).")


# ========== SUMMARY ==========
print(f"\n{'='*50}")
print(f"SUMMARY")
print(f"{'='*50}")
print(f"  Wiki:        {WIKI}")
print(f"  Pages:       {len(all_pages)}")
print(f"  P0 (blocking):    {len(issues_p0)}")
print(f"  P1 (should fix):  {len(issues_p1)}")
print(f"  Info:             {len(issues_info)}")

exit_code = 1 if issues_p0 else 0
sys.exit(exit_code)
