"""Test #3 — Three-Tier System Architecture (Hierarchy)
三层系统架构图

Architecture: 感知层(传感器+数据采集) → 决策层(域控制器+算法) → 执行层(电机+制动)

Perception Layer (感知层): 传感器 + 数据采集
Decision Layer (决策层): 域控制器 + 算法
Execution Layer (执行层): 电机 + 制动

Patent figure standards (CNIPA/USPTO):
  - B&W only, no color fills
  - Sharp box (shape='box'), w/h ≥ 3:1 (via width=3.0, height=0.8)
  - Hierarchy: layer clusters with dashed borders, rank='same' via invisible edges
  - Reference numbers outside boxes with thin dotted lead lines
  - 图1 label below diagram

Font: 'Microsoft YaHei' (Windows). Linux: 'WenQuanYi Micro Hei'. Mac: 'PingFang SC'.

Design notes:
  Graphviz cluster subgraphs group nodes visually (drawn with a dashed bounding box).
  However, putting a node in BOTH a cluster AND a rank=same subgraph causes
  "was already in a rankset, deleted from cluster" warnings and removes the cluster.
  
  Fix: define all nodes globally, use clusters to group them, and use invisible
  edges (style=invis) instead of rank=same subgraphs to enforce intra-layer alignment.
"""
import graphviz
import os

g = graphviz.Digraph(
    name='SystemArchitecture',
    graph_attr={
        'rankdir': 'TB',
        'bgcolor': 'white',
        'fontname': 'Microsoft YaHei',
        'splines': 'polyline',
        'newrank': 'true',   # Better rank handling with clusters
    },
    node_attr={
        'fontname': 'Microsoft YaHei',
        'fontsize': '14',
        'fontcolor': 'black',
        'color': 'black',
        'penwidth': '0.6',
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
# Define ALL nodes globally first (so we can reference them in clusters)
# ============================================================
# Component nodes (sharp box, w/h ≈ 3.75:1, meets ≥ 3:1 requirement)
g.node('sensor', '传感器\n(Sensor)',         shape='box', width='3.0', height='0.8')
g.node('daq',    '数据采集\n(DAQ)',           shape='box', width='3.0', height='0.8')
g.node('ecu',    '域控制器\n(Domain ECU)',    shape='box', width='3.0', height='0.8')
g.node('algo',   '算法\n(Algorithm)',          shape='box', width='3.0', height='0.8')
g.node('motor',  '电机\n(Motor)',              shape='box', width='3.0', height='0.8')
g.node('brake',  '制动\n(Brake)',              shape='box', width='3.0', height='0.8')

# Reference number nodes (plaintext, smaller font)
g.node('r10', '10', shape='plaintext', fontsize='11')
g.node('r20', '20', shape='plaintext', fontsize='11')
g.node('r30', '30', shape='plaintext', fontsize='11')
g.node('r40', '40', shape='plaintext', fontsize='11')
g.node('r50', '50', shape='plaintext', fontsize='11')
g.node('r60', '60', shape='plaintext', fontsize='11')

# ============================================================
# Layer 1 — Perception Layer (感知层)
# Cluster groups nodes visually with dashed border
# ============================================================
with g.subgraph(name='cluster_perception') as layer1:
    layer1.attr(
        label='感知层',
        style='dashed',
        color='black',
        penwidth='0.6',
        fontname='Microsoft YaHei',
        fontsize='13',
        fontcolor='black',
        labeljust='l',
    )
    # Reference existing nodes (do NOT redefine — just include in cluster)
    layer1.node('sensor')
    layer1.node('daq')

# ============================================================
# Layer 2 — Decision Layer (决策层)
# ============================================================
with g.subgraph(name='cluster_decision') as layer2:
    layer2.attr(
        label='决策层',
        style='dashed',
        color='black',
        penwidth='0.6',
        fontname='Microsoft YaHei',
        fontsize='13',
        fontcolor='black',
        labeljust='l',
    )
    layer2.node('ecu')
    layer2.node('algo')

# ============================================================
# Layer 3 — Execution Layer (执行层)
# ============================================================
with g.subgraph(name='cluster_execution') as layer3:
    layer3.attr(
        label='执行层',
        style='dashed',
        color='black',
        penwidth='0.6',
        fontname='Microsoft YaHei',
        fontsize='13',
        fontcolor='black',
        labeljust='l',
    )
    layer3.node('motor')
    layer3.node('brake')

# ============================================================
# Intra-layer alignment: use invisible edges instead of rank=same
# (rank=same would pull nodes out of their clusters)
# ============================================================
g.edge('sensor', 'daq', style='invis')
g.edge('ecu',    'algo', style='invis')
g.edge('motor',  'brake', style='invis')
# Also align reference numbers with their components via invisible edges
g.edge('r10', 'sensor', style='invis')
g.edge('r20', 'daq',    style='invis')
g.edge('r30', 'ecu',    style='invis')
g.edge('r40', 'algo',   style='invis')
g.edge('r50', 'motor',  style='invis')
g.edge('r60', 'brake',  style='invis')

# ============================================================
# Inter-layer connections (top-to-bottom data flow)
# ============================================================
# Perception → Decision
g.edge('sensor', 'ecu', label='传感数据')
g.edge('daq',    'ecu', label='采集数据')

# Decision → Execution
g.edge('ecu',  'motor', label='驱动指令')
g.edge('algo', 'ecu',   label='控制策略', constraint='false')

# Execution internal signal
g.edge('motor', 'brake', label='协同', constraint='false')

# ============================================================
# Lead lines: thin dotted, no arrowhead, no rank constraint
# ============================================================
g.edge('r10', 'sensor', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r20', 'daq',    style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r30', 'ecu',    style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r40', 'algo',   style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r50', 'motor',  style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r60', 'brake',  style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')

# ============================================================
# Render — SVG for editing, PNG for preview
# ============================================================
out_dir = os.path.dirname(os.path.abspath(__file__))
g.render(os.path.join(out_dir, 'test3_architecture_output'), format='svg')
g.render(os.path.join(out_dir, 'test3_architecture_output'), format='png')
print(f"Rendered to: {out_dir}")
