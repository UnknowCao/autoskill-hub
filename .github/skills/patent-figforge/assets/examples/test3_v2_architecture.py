"""Test #3 v2 — Three-Tier System Architecture (Hierarchy)
三层系统架构图 — using UPDATED patent-figforge skill with hierarchy-skeleton pattern

Architecture: 感知层(传感器+数据采集) → 决策层(域控制器+算法) → 执行层(电机+制动)
Perception → Decision → Execution

Written following the UPDATED SKILL.md workflow:
  Step 1: Diagram type = Hierarchy (架构/层级/hierarchy)
  Step 2: Based on assets/hierarchy-skeleton.py pattern
          - cluster_* for layer grouping (dashed borders)
          - newrank='true' to prevent rank/cluster conflicts
          - invisible edges for intra-layer alignment (NOT rank='same')
          - reference numbers outside with thin dotted lead lines
  Step 3: Render SVG + PNG

Key changes from v1 (baseline):
  - Hierarchical numbering: 110,120 / 210,220 / 310,320 (not linear 10–60)
  - Clockwise lead-line arrangement per numbering.md
  - Explicit intra-layer invisible edges only (not mixed with ref-number alignment)
  - Layer labels at 13pt, top-left justified per shape-specs.md § Hierarchy
  - Inter-layer arrows labeled in Chinese for CNIPA compliance
  - All hierarchy-specific prohibitions from shape-specs.md observed

Font: 'Microsoft YaHei' (Windows). Linux: 'WenQuanYi Micro Hei'. Mac: 'PingFang SC'.
"""
import graphviz
import os

# ============================================================
# Step 2: Build graph — Hierarchy type per SKILL.md workflow
# ============================================================
g = graphviz.Digraph(
    name='SystemArchitectureV2',
    graph_attr={
        'rankdir': 'TB',
        'bgcolor': 'white',
        'fontname': 'Microsoft YaHei',
        'newrank': 'true',       # 🔑 Fixes rank/cluster conflicts (SKILL § Hierarchy specifics)
        'splines': 'polyline',   # Clean orthogonal routing
    },
    node_attr={
        'fontname': 'Microsoft YaHei',
        'fontsize': '14',
        'fontcolor': 'black',
        'color': 'black',
        'penwidth': '0.6',
        'shape': 'box',           # Sharp box per patent convention
        'style': 'solid',
        'width': '3.0',
        'height': '0.8',
    },
    edge_attr={
        'fontname': 'Microsoft YaHei',
        'fontsize': '11',
        'fontcolor': 'black',
        'color': 'black',
        'penwidth': '0.6',
    },
)
g.attr(label='图1', labelloc='b', fontsize='14', fontname='Microsoft YaHei')

# ============================================================
# Components — all nodes declared globally (referenced inside clusters)
# Hierarchical numbering per references/numbering.md:
#   100-series = Perception, 200-series = Decision, 300-series = Execution
# ============================================================
# --- Layer 1: Perception (感知层) ---
g.node('sensor', '传感器\n(Sensor)',       shape='box', width='3.0', height='0.8')
g.node('daq',    '数据采集\n(DAQ)',         shape='box', width='3.0', height='0.8')

# --- Layer 2: Decision (决策层) ---
g.node('ecu',    '域控制器\n(Domain ECU)',  shape='box', width='3.0', height='0.8')
g.node('algo',   '算法模块\n(Algorithm)',    shape='box', width='3.0', height='0.8')

# --- Layer 3: Execution (执行层) ---
g.node('motor',  '电机\n(Motor)',            shape='box', width='3.0', height='0.8')
g.node('brake',  '制动\n(Brake)',            shape='box', width='3.0', height='0.8')

# ============================================================
# Reference numbers — plaintext nodes, smaller font, OUTSIDE boxes
# Hierarchical: 110,120 | 210,220 | 310,320 (max 4 digits)
# Positioned clockwise per numbering.md convention
# ============================================================
# Left-side ref numbers (for left-column components)
g.node('r110', '110', shape='plaintext', fontsize='11', fontname='Microsoft YaHei')
g.node('r210', '210', shape='plaintext', fontsize='11', fontname='Microsoft YaHei')
g.node('r310', '310', shape='plaintext', fontsize='11', fontname='Microsoft YaHei')

# Right-side ref numbers (for right-column components)
g.node('r120', '120', shape='plaintext', fontsize='11', fontname='Microsoft YaHei')
g.node('r220', '220', shape='plaintext', fontsize='11', fontname='Microsoft YaHei')
g.node('r320', '320', shape='plaintext', fontsize='11', fontname='Microsoft YaHei')

# ============================================================
# Layer 1 — Perception Layer (感知层)
# Cluster with dashed border, label top-left per shape-specs.md § Hierarchy
# ============================================================
with g.subgraph(name='cluster_L1') as layer1:
    layer1.attr(
        label='感知层',
        labeljust='l',         # Top-left justified per convention
        fontsize='13',         # 13pt per shape-specs.md
        fontname='Microsoft YaHei',
        fontcolor='black',
        style='dashed',        # Dashed distinguishes layer from components
        color='black',
        penwidth='0.6',
    )
    layer1.node('sensor')
    layer1.node('daq')

# ============================================================
# Layer 2 — Decision Layer (决策层)
# ============================================================
with g.subgraph(name='cluster_L2') as layer2:
    layer2.attr(
        label='决策层',
        labeljust='l',
        fontsize='13',
        fontname='Microsoft YaHei',
        fontcolor='black',
        style='dashed',
        color='black',
        penwidth='0.6',
    )
    layer2.node('ecu')
    layer2.node('algo')

# ============================================================
# Layer 3 — Execution Layer (执行层)
# ============================================================
with g.subgraph(name='cluster_L3') as layer3:
    layer3.attr(
        label='执行层',
        labeljust='l',
        fontsize='13',
        fontname='Microsoft YaHei',
        fontcolor='black',
        style='dashed',
        color='black',
        penwidth='0.6',
    )
    layer3.node('motor')
    layer3.node('brake')

# ============================================================
# ⚠️ Intra-layer alignment: invisible edges (NOT rank='same'!)
# Per shape-specs.md § Hierarchy: rank='same' + clusters = silent drop.
# Invisible edges enforce same-row alignment safely.
# ============================================================
g.edge('sensor', 'daq',   style='invis')
g.edge('ecu',    'algo',  style='invis')
g.edge('motor',  'brake', style='invis')

# ============================================================
# Inter-layer connections — component-to-component, NOT layer-to-layer
# Labels in Chinese (CNIPA convention per SKILL.md § Hierarchy specifics)
# ============================================================
# Perception → Decision (data flows upward conceptually, arrow = data flow direction)
g.edge('sensor', 'ecu',  label='传感数据')
g.edge('daq',    'algo', label='采集数据')

# Decision → Execution (control flows downward)
g.edge('ecu',  'motor', label='驱动指令')
g.edge('algo', 'brake', label='制动指令')

# ============================================================
# Lead lines — thin dotted, no arrowhead, constraint=false
# Reference numbers placed outside boxes per numbering.md
# Clockwise arrangement: left-column refs on left, right-column refs on right
# ============================================================
# Left side — align ref numbers beside their components (rank='same' OK outside cluster)
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('sensor'); s.node('r110')
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('ecu'); s.node('r210')
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('motor'); s.node('r310')

# Right side
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('daq'); s.node('r120')
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('algo'); s.node('r220')
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('brake'); s.node('r320')

# Lead lines: thin (0.35pt), dotted, no arrowhead, no rank constraint
for ref_id, comp_id in [
    ('r110', 'sensor'), ('r120', 'daq'),
    ('r210', 'ecu'),    ('r220', 'algo'),
    ('r310', 'motor'),  ('r320', 'brake'),
]:
    g.edge(ref_id, comp_id,
           style='dotted', penwidth='0.35',
           arrowhead='none', constraint='false')

# ============================================================
# Step 3: Render — SVG for editing, PNG for preview
# ============================================================
out_dir = os.path.dirname(os.path.abspath(__file__))
svg_path = os.path.join(out_dir, 'test3_v2_architecture_output')
g.render(svg_path, format='svg')
g.render(svg_path, format='png')
print(f"Rendered to: {out_dir}")
print("Files: test3_v2_architecture_output.svg, test3_v2_architecture_output.png")
