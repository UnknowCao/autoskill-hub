#!/usr/bin/env python3
"""Quick validate content-research-writer SKILL.md structure and frontmatter."""
from pathlib import Path
import sys
import yaml

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"

errors = []

# 1. File exists
if not SKILL_MD.exists():
    errors.append(f"MISSING: {SKILL_MD}")

# 2. Frontmatter
text = SKILL_MD.read_text(encoding="utf-8")
if not text.startswith("---\n"):
    errors.append("MISSING: YAML frontmatter (must start with ---)")

parts = text.split("---", 2)
if len(parts) < 3:
    errors.append("MISSING: closing --- for frontmatter")

try:
    fm = yaml.safe_load(parts[1])
    if "name" not in fm:
        errors.append("MISSING: frontmatter 'name'")
    if "description" not in fm:
        errors.append("MISSING: frontmatter 'description'")
    desc = fm.get("description", "")
    if len(desc) > 1024:
        errors.append(f"description too long: {len(desc)} chars (max 1024)")
except yaml.YAMLError as e:
    errors.append(f"YAML parse error: {e}")

# 3. Required sections
body = parts[2] if len(parts) >= 3 else ""
required_sections = [
    "## Workflow",
    "### Step 1:",
    "### Step 2:",
    "### Step 3:",
    "### Step 4:",
    "### Step 5:",
    "### Step 6:",
    "🔴 **CHECKPOINT**",
    "## ⛔ 不要做",
    "## 引用管理",
    "## Runtime 适配",
]
for section in required_sections:
    if section not in body:
        errors.append(f"MISSING section: {section}")

# 4. Checkpoint count
checkpoint_count = body.count("🔴 **CHECKPOINT**")
if checkpoint_count < 4:
    errors.append(f"Too few CHECKPOINT markers: {checkpoint_count} (min 4)")

# 5. Fallback table count
fallback_tables = body.count("| 严重度 | 触发 | 处理 |")
if fallback_tables < 5:
    errors.append(f"Too few fallback tables: {fallback_tables} (min 5)")

# 6. References directory
refs_dir = SKILL_DIR / "references"
if not refs_dir.is_dir():
    errors.append("MISSING: references/ directory")
else:
    for ref_file in ["examples.md", "workflows.md"]:
        if not (refs_dir / ref_file).exists():
            errors.append(f"MISSING: references/{ref_file}")

if errors:
    print(f"FAIL: {len(errors)} validation errors:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print(f"OK: {SKILL_MD.name} passes all checks")
    print(f"   - Frontmatter: valid YAML")
    print(f"   - CHECKPOINT markers: {checkpoint_count}")
    print(f"   - Fallback tables: {fallback_tables}")
    print(f"   - References: present")
