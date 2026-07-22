"""Hierarchy / Architecture skeleton — copy, fill in your layers, render.

Font: 'Microsoft YaHei' (Windows). Linux: 'WenQuanYi Micro Hei'. Mac: 'PingFang SC'.

IMPORTANT: Do NOT use rank='same' subgraphs together with cluster subgraphs —
Graphviz will silently drop clusters. Use invisible edges for alignment instead.
"""
import graphviz

g = graphviz.Digraph(
    name='Hierarchy',
    graph_attr={'rankdir': 'TB', 'bgcolor': 'white', 'fontname': 'Microsoft YaHei',
                'newrank': 'true'},   # newrank=true fixes many rank/cluster conflicts
    node_attr={'fontname': 'Microsoft YaHei', 'fontsize': '14', 'fontcolor': 'black',
               'color': 'black', 'penwidth': '0.6', 'shape': 'box',
               'width': '2.5', 'height': '0.7'},
    edge_attr={'fontname': 'Microsoft YaHei', 'fontsize': '11', 'fontcolor': 'black',
               'color': 'black', 'penwidth': '0.6'},
)
g.attr(label='图1', labelloc='b', fontsize='14')

# === Layer 1: Perception (感知层) ===
with g.subgraph(name='cluster_L1') as c1:
    c1.attr(label='感知层', labeljust='l', fontsize='13',
            style='dashed', color='black', penwidth='0.6')
    c1.node('sensor', '传感器\nSensor')
    c1.node('daq',    '数据采集\nDAQ')

# === Layer 2: Decision (决策层) ===
with g.subgraph(name='cluster_L2') as c2:
    c2.attr(label='决策层', labeljust='l', fontsize='13',
            style='dashed', color='black', penwidth='0.6')
    c2.node('ecu',  '域控制器\nDomain ECU')
    c2.node('algo', '算法模块\nAlgorithm')

# === Layer 3: Actuation (执行层) ===
with g.subgraph(name='cluster_L3') as c3:
    c3.attr(label='执行层', labeljust='l', fontsize='13',
            style='dashed', color='black', penwidth='0.6')
    c3.node('motor',  '电机\nMotor')
    c3.node('brake',  '制动\nBrake')

# === Horizontal alignment within each layer (invisible edges) ===
# Use invisible edges instead of rank='same' subgraphs when using clusters.
# rank='same' + cluster = Graphviz drops the cluster silently.
g.edge('sensor', 'daq',    style='invis')
g.edge('ecu',    'algo',   style='invis')
g.edge('motor',  'brake',  style='invis')

# === Inter-layer connections (top → bottom data flow) ===
g.edge('sensor', 'ecu',  label='感知数据')
g.edge('daq',    'algo', label='采集数据')
g.edge('ecu',    'motor', label='控制指令')
g.edge('algo',   'brake', label='制动指令')

# === Reference numbers (outside boxes: plaintext nodes + lead lines) ===
# See references/numbering.md for conventions.
g.node('r10', '10', shape='plaintext', fontsize='11')
g.node('r20', '20', shape='plaintext', fontsize='11')
g.node('r30', '30', shape='plaintext', fontsize='11')

# Align ref numbers with their components
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('sensor'); s.node('r10')
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('ecu'); s.node('r20')
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('motor'); s.node('r30')

# Lead lines: thin dotted, no arrowhead
g.edge('r10', 'sensor', style='dotted', penwidth='0.35', arrowhead='none', constraint='false')
g.edge('r20', 'ecu',    style='dotted', penwidth='0.35', arrowhead='none', constraint='false')
g.edge('r30', 'motor',  style='dotted', penwidth='0.35', arrowhead='none', constraint='false')

g.render('hierarchy_output', format='svg')
g.render('hierarchy_output', format='png')
