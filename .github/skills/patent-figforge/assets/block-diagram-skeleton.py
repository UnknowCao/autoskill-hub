"""Block diagram skeleton — copy, fill in your components, render."""
import graphviz

g = graphviz.Digraph(
    name='BlockDiagram',
    graph_attr={'rankdir': 'TB', 'bgcolor': 'white', 'fontname': 'Arial'},
    node_attr={'fontname': 'Arial', 'fontsize': '14', 'fontcolor': 'black',
               'color': 'black', 'penwidth': '0.6'},
    edge_attr={'fontname': 'Arial', 'fontsize': '11', 'fontcolor': 'black',
               'color': 'black', 'penwidth': '0.6'},
)
g.attr(label='图1', labelloc='b', fontsize='12')

# Components (sharp box, different border styles per type)
g.node('sensor',  'Sensor\n(10)',  shape='box', style='solid',  width='2.5', height='0.7')
g.node('cpu',     'Processor\n(20)', shape='box', style='solid',  width='2.5', height='0.7')
g.node('storage', 'Memory\n(30)',  shape='box', style='dashed', width='2.5', height='0.7')
g.node('output',  'Display\n(40)', shape='box', style='solid', penwidth='1.5', width='2.5', height='0.7')

# Connections
g.edge('sensor', 'cpu', label='data')
g.edge('cpu', 'storage', label='store')
g.edge('storage', 'cpu', label='retrieve')
g.edge('cpu', 'output', label='display')

g.render('block_diagram_output', format='svg')
