"""Flowchart skeleton — copy, fill in your steps, render."""
import graphviz

g = graphviz.Digraph(
    name='Flowchart',
    graph_attr={'rankdir': 'TB', 'bgcolor': 'white', 'fontname': 'Microsoft YaHei'},
    node_attr={'fontname': 'Microsoft YaHei', 'fontsize': '14', 'fontcolor': 'black',
               'color': 'black', 'penwidth': '0.6'},
    edge_attr={'fontname': 'Microsoft YaHei', 'fontsize': '11', 'fontcolor': 'black',
               'color': 'black', 'penwidth': '0.6'},
)
g.attr(label='图1', labelloc='b', fontsize='12')

# Start (flat ellipse)
g.node('start', '开始', shape='ellipse', width='1.8', height='0.5')

# Process steps (wide sharp box, w/h ≥ 3:1)
g.node('step1', '步骤一', shape='box', width='3.0', height='0.6')

# Decision (flat diamond, w/h ≈ 2:1)
g.node('dec1', '条件?', shape='diamond', width='2.8', height='1.4')

# End
g.node('end', '结束', shape='ellipse', width='1.8', height='0.5')

# Flow edges
g.edge('start', 'step1')
g.edge('step1', 'dec1')
g.edge('dec1', 'step2', label='是')
g.edge('dec1', 'end', label='否')

# Lead lines — see references/numbering.md for pattern
# g.node('r10', '10', shape='plaintext', fontsize='11')
# g.edge('r10', 'step1', style='dotted', penwidth='0.35', arrowhead='none', constraint='false')

g.render('flowchart_output', format='svg')
