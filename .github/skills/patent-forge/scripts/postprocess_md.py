#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
postprocess_md.py — Post-process a generated patent disclosure/application .md

Two transforms applied to the FINAL .md deliverable (not to internal drafts):
  1. Strip internal workflow emoji/status glyphs (🔴🟠🟡🟢⚠️✅❌⛔🛑⚡🔒 ...).
     Patent documents are formal; internal markers must not leak into the
     deliverable. Reuses the SAME regex logic as fill_acip_template.py so the
     .md and .docx outputs are byte-identical in terms of stripped symbols.
  2. Embed figures: replace standalone figure-list bullet lines of the form
       `- 图 N：...` / `* 图 N ...` / `（图 N）...`
     OR inline references like `见图 N` / `（图 N）` / `图 N 所示` with a
     Markdown image when a matching PNG is found in --figures-dir.

Usage
-----
    python postprocess_md.py INPUT.md --output OUTPUT.md \
        [--figures-dir DIR] [--inplace]

If --output is omitted, writes INPUT stripped of a `.md` suffix + `_clean.md`.
Figures are matched by `fig<N>_*.png` (same convention as fill_acip_template.py).
"""
from __future__ import annotations

import argparse
import os
import re
import sys


# ---------------------------------------------------------------------------
# 1. Emoji stripping — kept in sync with fill_acip_template._EMOJI_RE
# ---------------------------------------------------------------------------
_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"   # symbols & pictographs
    "\U00002600-\U000027BF"   # misc symbols
    "\U0001F000-\U0001F2FF"   # mahjong / dominoes / cards
    "\U00002B00-\U00002BFF"   # arrows/stars (➜ ⭐) — note: → U+2192 preserved
    "\u200D"                  # ZWJ
    "\uFE0F"                  # VS-16
    "\u20E3"                  # combining enclosing keycap
    "]+",
    flags=re.UNICODE,
)


def _strip_status_symbols(text: str) -> str:
    """Remove emoji / status glyphs and tidy surrounding whitespace. Mirrors
    fill_acip_template._strip_status_symbols exactly."""
    cleaned = _EMOJI_RE.sub("", text)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"([（(])\s+", r"\1", cleaned)
    cleaned = re.sub(r"\s+([）)])", r"\1", cleaned)
    return cleaned


# ---------------------------------------------------------------------------
# 1b. Template boilerplate hint stripping (mirrors fill_acip_template)
# ---------------------------------------------------------------------------
# Patent agency .docx templates ship answer cells with instruction hints
# (e.g. ACIP row 20 "请对本交底书中提及的关键术语..." and row 22 "（对于理解
# 交底书中的技术方案有帮助的专利/论文/期刊）"). When AI-generated content
# echoes these hints as a prefix, they leak into the .md deliverable. These
# prefixes are stripped so the .md and .docx outputs stay consistent.

_BOILERPLATE_HINT_PREFIXES = (
    "请对本交底书中提及的关键术语、技术缩略语进行解释说明",
    "请对本交底书中提及的关键术语、技术缩略语进行解释",
    "请对本交底书",
    "（对于理解交底书中的技术方案有帮助的专利/论文/期刊",
    "(对于理解交底书中的技术方案有帮助的专利/论文/期刊",
    "（对于理解交底书中的技术方案有帮助的专利",
    "(对于理解交底书中的技术方案有帮助的专利",
    "对于理解交底书中的技术方案有帮助的专利/论文/期刊",
)


def _strip_boilerplate_hints(text: str) -> str:
    """Remove template boilerplate instruction hints from the start of `text`.
    Mirrors fill_acip_template._strip_boilerplate_hints exactly (kept in sync
    so .md and .docx outputs are byte-identical for stripped prefixes)."""
    if not isinstance(text, str) or not text:
        return text
    for hint in _BOILERPLATE_HINT_PREFIXES:
        if text.startswith(hint):
            rest = text[len(hint):]
            rest = re.sub(r"^[：:）)\s]*", "", rest, count=1)
            rest = re.sub(
                r"\A(?:[^|\[\n]*?)(?=\||\[|\n\n|\Z)", "", rest, count=1,
                flags=re.DOTALL,
            )
            text = rest.lstrip(" \t")
            break
    return text.lstrip("\n").strip()


# ---------------------------------------------------------------------------
# 2. Figure embedding
# ---------------------------------------------------------------------------
# The patent-forge workflow emits figure references in the form
#   **【图 N】标题**（详见 `path/figN_xxx.svg`）
# sometimes inline within a paragraph, sometimes as a standalone caption.
# We match the bracketed marker 【图 N】 (full-width) or [图 N] (half-width),
# with optional surrounding bold ** and an optional caption/title after it.
# Group 1 = the figure number.
_FIG_MARKER_RE = re.compile(r"\*{0,2}\s*[【\[]\s*图\s*(\d+)\s*[】\]]\s*\*{0,2}")


def _discover_figures(figures_dir: str) -> dict:
    """Return {N: absolute_path} for fig<N>_*.png in figures_dir.

    Also tolerates `figN.png` (no underscore suffix) for hand-named files.
    """
    mapping = {}
    if not figures_dir or not os.path.isdir(figures_dir):
        return mapping
    pat = re.compile(r"^fig(\d+)[_.-].*\.png$", re.IGNORECASE)
    pat_bare = re.compile(r"^fig(\d+)\.png$", re.IGNORECASE)
    for p in os.listdir(figures_dir):
        m = pat.match(p) or pat_bare.match(p)
        if m:
            mapping[int(m.group(1))] = os.path.join(figures_dir, p)
    return mapping


def _embed_figures(text: str, figures: dict, figures_base_for_md: str = None) -> str:
    """Append a Markdown image right after the FIRST line that mentions each
    figure marker `【图 N】` / `[图 N]`. Each figure is embedded exactly once
    (the first occurrence), so later inline references stay as prose.

    `figures_base_for_md`: how to render the path in the .md. Defaults to the
    raw figures_dir (absolute). Caller may pass a relative path for cleaner md.
    """
    if not figures:
        return text
    embedded: set = set()
    out_lines = []
    for line in text.split("\n"):
        out_lines.append(line)
        # Find all figure markers on this line; embed each once.
        for m in _FIG_MARKER_RE.finditer(line):
            fig_num = int(m.group(1))
            if fig_num in figures and fig_num not in embedded:
                embedded.add(fig_num)
                png = figures[fig_num]
                if figures_base_for_md:
                    png = os.path.join(figures_base_for_md, os.path.basename(png))
                out_lines.append("")
                out_lines.append(f"![图 {fig_num}]({png.replace(chr(92), '/')})")
                out_lines.append("")
    return "\n".join(out_lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[2])
    ap.add_argument("input", help="Input .md file to post-process.")
    ap.add_argument("--output", help="Output .md path (default: <stem>_clean.md).")
    ap.add_argument("--figures-dir", help="Directory with fig<N>_*.png to embed.")
    ap.add_argument(
        "--figures-rel",
        help="Optional base path to render image links as relative (e.g. ../04-diagrams).",
    )
    ap.add_argument(
        "--inplace",
        action="store_true",
        help="Overwrite the input file in place (implies --output=INPUT).",
    )
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Strip status symbols
    text = _strip_status_symbols(text)

    # 1b. Strip template boilerplate hints (terminology / references prefixes)
    text = _strip_boilerplate_hints(text)

    # 2. Embed figures
    figures = _discover_figures(args.figures_dir) if args.figures_dir else {}
    text = _embed_figures(text, figures, args.figures_rel)

    # Resolve output path
    if args.inplace:
        out_path = args.input
    elif args.output:
        out_path = args.output
    else:
        stem = args.input[:-3] if args.input.lower().endswith(".md") else args.input
        out_path = f"{stem}_clean.md"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"[OK] Post-processed: {args.input} -> {out_path}")
    if figures:
        print(f"     Figures embedded: {sorted(figures.keys())}")
    else:
        print("     Figures embedded: (none — no --figures-dir or no matches)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
