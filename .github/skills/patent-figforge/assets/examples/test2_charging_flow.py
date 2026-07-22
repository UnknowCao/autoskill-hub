"""Test #2 — Charging Control Flowchart
充电控制流程图

Flow: 开始→检测连接→判断是否连接成功（是→启动充电，否→返回检测）
      →监测充满→判断是否充满（是→停止充电→结束，否→继续充电）

Patent figure standards (CNIPA/USPTO):
  - B&W only, no color fills
  - Sharp box (shape='box'), flat diamond (w/h ≈ 2:1), flat ellipse start/end
  - Reference numbers outside boxes with thin dotted lead lines
  - 图1 label below diagram

Font: 'Microsoft YaHei' (Windows). Linux: 'WenQuanYi Micro Hei'. Mac: 'PingFang SC'.
"""
import graphviz
import os

g = graphviz.Digraph(
    name='ChargingFlowchart',
    graph_attr={
        'rankdir': 'TB',
        'bgcolor': 'white',
        'fontname': 'Microsoft YaHei',
        'splines': 'polyline',
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
# Nodes
# ============================================================
# Shape specs per SKILL.md:
#   Start/End: flat ellipse  width=1.8, height=0.5
#   Process:    sharp box    width=3.0, height=0.6  (w/h = 5:1 ≥ 3:1)
#   Decision:   flat diamond width=2.8, height=1.4  (w/h = 2:1)

# --- Terminal nodes (flat ellipse) ---
g.node('start', '开始', shape='ellipse', width='1.8', height='0.5')
g.node('end',   '结束', shape='ellipse', width='1.8', height='0.5')

# --- Process steps (sharp box, w/h ≥ 3:1) ---
g.node('detect',       '检测连接', shape='box', width='3.0', height='0.6')
g.node('start_chg',    '启动充电', shape='box', width='3.0', height='0.6')
g.node('monitor',      '监测充满', shape='box', width='3.0', height='0.6')
g.node('stop_chg',     '停止充电', shape='box', width='3.0', height='0.6')
g.node('continue_chg', '继续充电', shape='box', width='3.0', height='0.6')

# --- Decision nodes (flat diamond, w/h ≈ 2:1) ---
g.node('dec_conn', '连接成功?', shape='diamond', width='2.8', height='1.4')
g.node('dec_full', '充满?',     shape='diamond', width='2.8', height='1.4')

# ============================================================
# Main flow edges (top-to-bottom, constraint=true by default)
# ============================================================
g.edge('start', 'detect')
g.edge('detect', 'dec_conn')
g.edge('dec_conn', 'start_chg', label='是')
g.edge('start_chg', 'monitor')
g.edge('monitor', 'dec_full')
g.edge('dec_full', 'stop_chg', label='是')
g.edge('stop_chg', 'end')

# ============================================================
# Branch / loop-back edges
# ============================================================
# Convention (shape-specs.md): Yes→right tip, No→left tip of diamond
# Loop-backs use constraint='false' to avoid distorting vertical rank order

# 否 from 连接成功? → loop back to 检测连接 (exits left, goes up)
g.edge('dec_conn', 'detect', label='否', constraint='false')

# 否 from 充满? → 继续充电 (exits left, goes to side branch)
g.edge('dec_full', 'continue_chg', label='否')

# 继续充电 → loop back to 监测充满
g.edge('continue_chg', 'monitor', constraint='false')

# ============================================================
# Rank alignment: keep stop_chg and continue_chg on same row
# ============================================================
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('stop_chg')
    s.node('continue_chg')

# ============================================================
# Reference numbers — linear encoding (10, 20, 30...)
# Placed OUTSIDE boxes with thin dotted lead lines (penwidth=0.35)
# Arranged clockwise per numbering.md convention
# ============================================================

# Reference number nodes (plaintext, smaller font)
g.node('r10', '10', shape='plaintext', fontsize='11')
g.node('r20', '20', shape='plaintext', fontsize='11')
g.node('r30', '30', shape='plaintext', fontsize='11')
g.node('r40', '40', shape='plaintext', fontsize='11')
g.node('r50', '50', shape='plaintext', fontsize='11')
g.node('r60', '60', shape='plaintext', fontsize='11')

# Align reference numbers beside their components (rank=same subgraphs)
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('detect')
    s.node('r10')

with g.subgraph() as s:
    s.attr(rank='same')
    s.node('dec_conn')
    s.node('r20')

with g.subgraph() as s:
    s.attr(rank='same')
    s.node('start_chg')
    s.node('r30')

with g.subgraph() as s:
    s.attr(rank='same')
    s.node('monitor')
    s.node('r40')

with g.subgraph() as s:
    s.attr(rank='same')
    s.node('dec_full')
    s.node('r50')

with g.subgraph() as s:
    s.attr(rank='same')
    s.node('continue_chg')
    s.node('r60')

# Lead lines: thin dotted, no arrowhead, no rank constraint
g.edge('r10', 'detect',       style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r20', 'dec_conn',     style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r30', 'start_chg',    style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r40', 'monitor',      style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r50', 'dec_full',     style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r60', 'continue_chg', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')

# ============================================================
# Render — SVG for editing, PNG for preview
# ============================================================
out_dir = os.path.dirname(os.path.abspath(__file__))
g.render(os.path.join(out_dir, 'test2_charging_flow_output'), format='svg')
g.render(os.path.join(out_dir, 'test2_charging_flow_output'), format='png')
