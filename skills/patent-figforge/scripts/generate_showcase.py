#!/usr/bin/env python3
"""Generate hero comparison image for patent-figforge README showcase.

Creates a side-by-side "Before vs After" comparison:
  LEFT:  Non-compliant diagram (raw graphviz — colored, curved, tofu Chinese)
  RIGHT: Compliant diagram via PatentDiagramGenerator (B&W, polyline, SimHei)

Output: assets/showcase/hero-comparison.png
"""

import os, sys

# Locate skill root
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SKILL_ROOT)

from python.diagram_generator import PatentDiagramGenerator, CJK_FONT
import graphviz
from PIL import Image

OUTPUT_DIR = os.path.join(SKILL_ROOT, "assets", "showcase")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Common diagram content ──────────────────────────────────────────
BLOCKS = [
    {"id": "vadc", "label": "电压采集单元", "ref": 10},
    {"id": "mcu",  "label": "主控MCU",     "ref": 20},
    {"id": "comm", "label": "通信模块",     "ref": 30},
    {"id": "bal",  "label": "均衡驱动",     "ref": 40},
]
CONNS = [["vadc", "mcu"], ["mcu", "comm"], ["mcu", "bal"]]

# ── LEFT: Non-compliant (deliberately bad) ──────────────────────────
bad = graphviz.Digraph("bad", format="png")
bad.attr(rankdir="LR", splines="curved", bgcolor="#f0fff0", dpi="150")
bad.attr("node", fontname="Times-Roman", fontsize="12",
         style="filled", color="blue", fillcolor="#e0ffe0")
bad.attr("edge", fontname="Times-Roman", color="red", arrowhead="diamond")
for b in BLOCKS:
    # Deliberately: no ref numbers, wrong font, colored
    bad.node(b["id"], b["label"])
for c in CONNS:
    bad.edge(c[0], c[1])
bad_path = os.path.join(OUTPUT_DIR, "_bad_temp")
bad.render(bad_path, cleanup=True)
bad_png = bad_path + ".png"

# ── RIGHT: Compliant — render with dpi=150 for showcase quality ─────
good_raw = graphviz.Digraph("good", format="png")
good_raw.attr(rankdir="LR", dpi="150",
              splines="polyline", nodesep="0.35", ranksep="0.55",
              bgcolor="white", fontname=CJK_FONT, fontsize="14", penwidth="1.3")
good_raw.attr("node", style="filled", fillcolor="white",
              fontname=CJK_FONT, fontsize="14", penwidth="1.3",
              shape="box", margin="0.15,0.1")
good_raw.attr("edge", fontname=CJK_FONT, fontsize="13",
              arrowhead="vee", arrowsize="0.9")
for b in BLOCKS:
    label = f"{b['label']}\\n({b['ref']})"
    good_raw.node(b["id"], label)
for c in CONNS:
    good_raw.edge(c[0], c[1])
good_path = os.path.join(OUTPUT_DIR, "bms-block-compliant")
good_raw.render(good_path, cleanup=True)
good_png = good_path + ".png"

# ── Combine side-by-side ────────────────────────────────────────────
bad_img = Image.open(bad_png)
good_img = Image.open(good_png)

# Resize to same height
h = max(bad_img.height, good_img.height)
bad_img = bad_img.resize((int(bad_img.width * h / bad_img.height), h), Image.LANCZOS)
good_img = good_img.resize((int(good_img.width * h / good_img.height), h), Image.LANCZOS)

# Add 20px labels at top of each side
from PIL import ImageDraw, ImageFont
label_h = 36
canvas_w = bad_img.width + good_img.width + 4  # 4px divider
canvas_h = h + label_h
canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
draw = ImageDraw.Draw(canvas)

# Labels
try:
    font = ImageFont.truetype("C:\\Windows\\Fonts\\simhei.ttf", 20)
except Exception:
    font = ImageFont.load_default()
draw.rectangle([0, 0, bad_img.width, label_h], fill="#ffcccc")
draw.text((bad_img.width // 2, 6), "❌ 没有 patent-figforge", fill="black", font=font, anchor="ma")
draw.rectangle([bad_img.width + 4, 0, canvas_w, label_h], fill="#ccffcc")
draw.text((bad_img.width + 4 + good_img.width // 2, 6), "✅ 使用 patent-figforge", fill="black", font=font, anchor="ma")

# Paste images below labels
canvas.paste(bad_img, (0, label_h))
# Red divider line
for y in range(label_h, canvas_h):
    canvas.putpixel((bad_img.width + 1, y), (200, 0, 0))
    canvas.putpixel((bad_img.width + 2, y), (200, 0, 0))
canvas.paste(good_img, (bad_img.width + 4, label_h))

hero_path = os.path.join(OUTPUT_DIR, "hero-comparison.png")
canvas.save(hero_path)
print(f"Hero comparison saved: {hero_path} ({canvas_w}x{canvas_h})")

# Cleanup temp
os.remove(bad_png)
# Also remove the .svg variant if any
for ext in [".svg", ""]:
    tmp = bad_path + ext
    if os.path.exists(tmp):
        os.remove(tmp)

# ── Also copy individual showcase images ────────────────────────────
import shutil
for src_name, dst_name in [
    ("bms_method_fixed.png", "bms-method-flowchart.png"),
    ("bms_block_compliant.png", "bms-block-diagram.png"),
]:
    src = os.path.join(SKILL_ROOT, "python", src_name)
    dst = os.path.join(OUTPUT_DIR, dst_name)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copied: {dst_name}")
