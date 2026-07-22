"""Flowchart skeleton — copy, fill in your steps, render.

Font: 'Microsoft YaHei' (Windows). Linux: 'WenQuanYi Micro Hei'. Mac: 'PingFang SC'.
"""
import graphviz

g = graphviz.Digraph(
    name='Flowchart',
    graph_attr={'rankdir': 'TB', 'bgcolor': 'white', 'fontname': 'Microsoft YaHei'},
    node_attr={'fontname': 'Microsoft YaHei', 'fontsize': '14', 'fontcolor': 'black',
               'color': 'black', 'penwidth': '0.6'},
    edge_attr={'fontname': 'Microsoft YaHei', 'fontsize': '11', 'fontcolor': 'black',
               'color': 'black', 'penwidth': '0.6'},
)
g.attr(label='图1', labelloc='b', fontsize='14')

# Start (flat ellipse)
g.node('start', '开始', shape='ellipse', width='1.8', height='0.5')

# Process steps (wide sharp box, w/h ≥ 3:1)
g.node('step1', '步骤一', shape='box', width='3.0', height='0.6')

# Decision (flat diamond, w/h ≈ 2:1)
g.node('dec1', '条件?', shape='diamond', width='2.8', height='1.4')

# Another process step
g.node('step2', '步骤二', shape='box', width='3.0', height='0.6')

# End
g.node('end', '结束', shape='ellipse', width='1.8', height='0.5')

# Flow edges — use port hints (:e/:w/:s/:n) to control exit direction
g.edge('start', 'step1')
g.edge('step1', 'dec1')
g.edge('dec1:e', 'step2', label='是')    # Yes → right tip of diamond
g.edge('dec1:w', 'end',   label='否')    # No  → left tip of diamond

# === Loop-back pattern (uncomment to use) ===
# For "否 returns to earlier step" patterns, use invisible routing nodes:
# g.node('route1', '', shape='point', width='0')         # invisible node in safe channel
# g.edge('dec1:s', 'route1', label='否', constraint='false')
# g.edge('route1', 'step1', constraint='false')           # route back to earlier step

# Reference numbers — see references/numbering.md for pattern
# g.node('r10', '10', shape='plaintext', fontsize='11')
# g.edge('r10', 'step1', style='dotted', penwidth='0.35', arrowhead='none', constraint='false')

g.render('flowchart_output', format='svg')
g.render('flowchart_output', format='png')
