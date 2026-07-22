"""BMS Battery Management System — Block Diagram v2 (Post-Optimization Test)
Patent-style figure: B&W, sharp boxes, reference numbers outside with lead lines.

Follows updated patent-figforge SKILL.md + references/shape-specs.md § Block Diagram Types
+ references/numbering.md § Hierarchical encoding.

Font: 'Microsoft YaHei' (Windows). Linux: 'WenQuanYi Micro Hei'. Mac: 'PingFang SC'.
"""
import graphviz

g = graphviz.Digraph(
    name='BMS_BlockDiagram_v2',
    graph_attr={'rankdir': 'TB', 'bgcolor': 'white', 'fontname': 'Microsoft YaHei',
                'nodesep': '0.6', 'ranksep': '0.8'},
    node_attr={'fontname': 'Microsoft YaHei', 'fontsize': '14', 'fontcolor': 'black',
               'color': 'black', 'penwidth': '0.6'},
    edge_attr={'fontname': 'Microsoft YaHei', 'fontsize': '11', 'fontcolor': 'black',
               'color': 'black', 'penwidth': '0.6'},
)
g.attr(label='图1', labelloc='b', fontsize='14')

# ============================================================
# Components (all shape='box', border styles per shape-specs.md § Block Diagram Types)
# ============================================================
# Sensor/Input — solid outline (shape-specs.md: style=solid)
g.node('v_sensor', '电压传感器\nVoltage Sensor', shape='box',
       style='solid', width='2.5', height='0.8')
g.node('t_sensor', '温度传感器\nTemp Sensor', shape='box',
       style='solid', width='2.5', height='0.8')

# Processor/Controller — solid outline, standard width (shape-specs.md: style=solid)
g.node('mcu', '主控 MCU\nMain Controller', shape='box',
       style='solid', width='2.8', height='0.8')

# Memory/Storage — dashed outline (shape-specs.md: style=dashed)
g.node('storage', '存储器\nMemory', shape='box',
       style='dashed', width='2.5', height='0.8')

# CAN communication module — solid (processor-type, shape-specs.md: style=solid)
g.node('can', 'CAN 通信模块\nCAN Module', shape='box',
       style='solid', width='2.5', height='0.8')

# Output/Display — bold solid outline (shape-specs.md: style=solid, penwidth=1.5)
g.node('display', '显示面板\nDisplay Panel', shape='box',
       style='solid', penwidth='1.5', width='2.5', height='0.8')

# ============================================================
# Reference numbers (outside boxes, plaintext nodes)
# Hierarchical encoding per numbering.md § Hierarchical encoding:
#   110–120: Sensor subsystem
#   130:     Processor/Controller
#   140:     Memory
#   150:     Communication
#   160:     Output/Display
# ============================================================
g.node('r110', '110', shape='plaintext', fontsize='11')
g.node('r120', '120', shape='plaintext', fontsize='11')
g.node('r130', '130', shape='plaintext', fontsize='11')
g.node('r140', '140', shape='plaintext', fontsize='11')
g.node('r150', '150', shape='plaintext', fontsize='11')
g.node('r160', '160', shape='plaintext', fontsize='11')

# ============================================================
# Row alignment via rank=same subgraphs
# (Safe for ref-number alignment per hierarchy-skeleton.py note)
# Layout: 2–3 column grid per shape-specs.md § Block Diagram Layout
# ============================================================
# Row 1: Sensors (2 columns, equal width per shape-specs)
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('v_sensor'); s.node('r110')
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('t_sensor'); s.node('r120')

# Row 2: MCU (centered, full-width)
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('mcu'); s.node('r130')

# Row 3: Storage + CAN (2 columns, equal width)
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('storage'); s.node('r140')
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('can'); s.node('r150')

# Row 4: Display (centered)
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('display'); s.node('r160')

# ============================================================
# Lead lines: thin dotted, no arrowhead, constraint=false
# Specs per numbering.md § Lead Line Specs: 0.35pt (visibly thinner than 0.6pt outlines)
# Clockwise arrangement per numbering.md § Rules
# ============================================================
g.edge('r110', 'v_sensor', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r120', 't_sensor', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r130', 'mcu', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r140', 'storage', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r150', 'can', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r160', 'display', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')

# ============================================================
# Data-flow connections between components
# ============================================================
# Sensors → MCU
g.edge('v_sensor', 'mcu', label='电压')
g.edge('t_sensor', 'mcu', label='温度')

# MCU ↔ Storage (bidirectional)
g.edge('mcu', 'storage', label='写入')
g.edge('storage', 'mcu', label='读取')

# MCU ↔ CAN (bidirectional)
g.edge('mcu', 'can', label='发送')
g.edge('can', 'mcu', label='接收')

# MCU → Display
g.edge('mcu', 'display', label='显示数据')

# ============================================================
# Render
# ============================================================
g.render('test1_v2_bms_block_output', format='svg')
g.render('test1_v2_bms_block_output', format='png')
print('Done: test1_v2_bms_block_output.svg + .png')
