"""Block diagram skeleton — copy, fill in your components, render.

Font: 'Microsoft YaHei' (Windows). Linux: 'WenQuanYi Micro Hei'. Mac: 'PingFang SC'.
"""
import graphviz

g = graphviz.Digraph(
    name='BlockDiagram',
    graph_attr={'rankdir': 'TB', 'bgcolor': 'white', 'fontname': 'Microsoft YaHei'},
    node_attr={'fontname': 'Microsoft YaHei', 'fontsize': '14', 'fontcolor': 'black',
               'color': 'black', 'penwidth': '0.6'},
    edge_attr={'fontname': 'Microsoft YaHei', 'fontsize': '11', 'fontcolor': 'black',
               'color': 'black', 'penwidth': '0.6'},
)
g.attr(label='图1', labelloc='b', fontsize='14')

# --- Components (sharp box, different border styles per type) ---
# Note: 'style=solid' is the default; only non-default styles are explicit.
g.node('sensor',  'Sensor',    shape='box', width='2.5', height='0.7')
g.node('cpu',     'Processor', shape='box', width='2.5', height='0.7')
g.node('storage', 'Memory',    shape='box', style='dashed', width='2.5', height='0.7')
g.node('output',  'Display',   shape='box', penwidth='1.5', width='2.5', height='0.7')

# --- Reference numbers (outside boxes: plaintext nodes) ---
# See references/numbering.md for conventions.
g.node('r10', '10', shape='plaintext', fontsize='11')
g.node('r20', '20', shape='plaintext', fontsize='11')
g.node('r30', '30', shape='plaintext', fontsize='11')
g.node('r40', '40', shape='plaintext', fontsize='11')

# --- Align ref numbers beside their components (rank=same subgraphs) ---
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('sensor'); s.node('r10')
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('cpu'); s.node('r20')
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('storage'); s.node('r30')
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('output'); s.node('r40')

# --- Lead lines: thin dotted, no arrowhead, constraint=false ---
g.edge('r10', 'sensor',  style='dotted', penwidth='0.35', arrowhead='none', constraint='false')
g.edge('r20', 'cpu',     style='dotted', penwidth='0.35', arrowhead='none', constraint='false')
g.edge('r30', 'storage', style='dotted', penwidth='0.35', arrowhead='none', constraint='false')
g.edge('r40', 'output',  style='dotted', penwidth='0.35', arrowhead='none', constraint='false')

# --- Connections between components ---
g.edge('sensor', 'cpu', label='data')
g.edge('cpu', 'storage', label='store')
g.edge('storage', 'cpu', label='retrieve')
g.edge('cpu', 'output', label='display')

g.render('block_diagram_output', format='svg')
g.render('block_diagram_output', format='png')
