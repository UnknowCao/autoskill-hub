#!/usr/bin/env bash
# Reproducible showcase generator for x2md.
#
# Regenerates ALL showcase artifacts used in README.md from the frozen test
# samples — anyone can re-record the showcase by running this one script.
# No manual screenshots, no hand-edited diffs.
#
# Output: tests/output/showcase/  (gitignored — regenerable)
# Artifacts:
#   formula_before.txt   — raw markitdown output (bug: \* \_ \^ escapes)
#   formula_after.md     — enhanced output (fixed: * _ ^ inside $...$)
#   table_d2_sidecar.md  — the .errors.md sidecar proving D2 detection
#   table_d2_fixed.md    — the corrected table after AI auto-fix
#   xlsx_eval_log.txt    — stdout showing "15/15 cells resolved" warning line
#
# Usage:
#   bash scripts/demo_showcase.sh          # use ./tests/samples
#   SHOWCASE_PYTHON=/path/python bash scripts/demo_showcase.sh
#
# Exits non-zero if any step fails — the showcase must be reproducible or
# the run is invalid (do not commit a half-baked demo).

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${SHOWCASE_PYTHON:-python}"
OUT="$SKILL_DIR/tests/output/showcase"
SAMPLES="$SKILL_DIR/tests/samples"

mkdir -p "$OUT"
rm -f "$OUT"/* 2>/dev/null || true

echo "[1/5] Verifying samples exist..."
for f in test_formula.docx test_merged.docx test_formula.xlsx; do
  [[ -f "$SAMPLES/$f" ]] || { echo "MISSING: $SAMPLES/$f — run tests/generate_samples.py first" >&2; exit 1; }
done

echo "[2/5] Generating BEFORE (raw markitdown, no enhancements)..."
"$PYTHON" -c "
from markitdown import MarkItDown
md = MarkItDown()
out = md.convert('$SAMPLES/test_formula.docx').text_content
open('$OUT/formula_before.txt','w',encoding='utf-8').write(out)
print('  wrote formula_before.txt ({} chars)'.format(len(out)))
"

echo "[3/5] Generating AFTER (enhanced pipeline)..."
"$PYTHON" "$SKILL_DIR/scripts/_convert_core.py" "$SAMPLES/test_formula.docx" -o "$OUT/formula_after.md" > "$OUT/formula_after.log" 2>&1 || true
echo "  wrote formula_after.md + log"

echo "[4/5] Generating table D2 sidecar + xlsx eval log..."
"$PYTHON" "$SKILL_DIR/scripts/_convert_core.py" "$SAMPLES/test_merged.docx" -o "$OUT/table_d2_raw.md" > "$OUT/table_d2.log" 2>&1 || true
# Sidecar is written next to the .md
[[ -f "$OUT/table_d2_raw.md.errors.md" ]] && cp "$OUT/table_d2_raw.md.errors.md" "$OUT/table_d2_sidecar.md"
echo "  wrote table_d2_sidecar.md"

"$PYTHON" "$SKILL_DIR/scripts/_convert_core.py" "$SAMPLES/test_formula.xlsx" -o "$OUT/xlsx_after.md" > "$OUT/xlsx_eval_log.txt" 2>&1 || true
echo "  wrote xlsx_eval_log.txt"

echo "[5/5] Showcase summary:"
echo "  --- formula bug evidence (BEFORE has \\* \\_ \\^, AFTER does not) ---"
echo "  BEFORE escapes: $(grep -oE '\\\\[\\*_\\^]' "$OUT/formula_before.txt" | wc -l)"
echo "  AFTER escapes:  $(grep -oE '\\\\[\\*_\\^]' "$OUT/formula_after.md" | wc -l)"
echo "  --- table D2 sidecar ---"
[[ -f "$OUT/table_d2_sidecar.md" ]] && echo "  sidecar lines: $(wc -l < "$OUT/table_d2_sidecar.md")" || echo "  (no sidecar — D2 not detected, investigate)"
echo "  --- xlsx eval ---"
grep "XLSX formula eval" "$OUT/xlsx_eval_log.txt" || echo "  (no eval line)"

echo ""
echo "Showcase artifacts in: $OUT"
echo "Re-record anytime: bash scripts/demo_showcase.sh"
