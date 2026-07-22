"""BMS Battery Management System — Block Diagram (Test #1)
Patent-style figure: B&W, sharp boxes, reference numbers outside with lead lines.

Font: 'Microsoft YaHei' (Windows). Linux: 'WenQuanYi Micro Hei'. Mac: 'PingFang SC'.
"""
import graphviz

g = graphviz.Digraph(
    name='BMS_BlockDiagram',
    graph_attr={'rankdir': 'TB', 'bgcolor': 'white', 'fontname': 'Microsoft YaHei',
                'nodesep': '0.6', 'ranksep': '0.8'},
    node_attr={'fontname': 'Microsoft YaHei', 'fontsize': '14', 'fontcolor': 'black',
               'color': 'black', 'penwidth': '0.6'},
    edge_attr={'fontname': 'Microsoft YaHei', 'fontsize': '11', 'fontcolor': 'black',
               'color': 'black', 'penwidth': '0.6'},
)
g.attr(label='图1', labelloc='b', fontsize='14')

# ============================================================
# Components (all shape='box', different border styles per type)
# ============================================================
# Sensors — solid outline
g.node('v_sensor', '电压传感器\nVoltage Sensor', shape='box',
       style='solid', width='2.5', height='0.8')
g.node('t_sensor', '温度传感器\nTemp Sensor', shape='box',
       style='solid', width='2.5', height='0.8')

# Processor/MCU — solid outline (standard)
g.node('mcu', '主控 MCU\nMain Controller', shape='box',
       style='solid', width='2.8', height='0.8')

# Storage — dashed outline
g.node('storage', '存储器\nMemory', shape='box',
       style='dashed', width='2.5', height='0.8')

# CAN communication module — solid outline (processor-type)
g.node('can', 'CAN 通信模块\nCAN Module', shape='box',
       style='solid', width='2.5', height='0.8')

# Output/Display — bold solid outline
g.node('display', '显示面板\nDisplay Panel', shape='box',
       style='solid', penwidth='1.5', width='2.5', height='0.8')

# ============================================================
# Reference numbers (outside boxes, plaintext nodes)
# ============================================================
g.node('r10', '10', shape='plaintext', fontsize='11')
g.node('r20', '20', shape='plaintext', fontsize='11')
g.node('r30', '30', shape='plaintext', fontsize='11')
g.node('r40', '40', shape='plaintext', fontsize='11')
g.node('r50', '50', shape='plaintext', fontsize='11')
g.node('r60', '60', shape='plaintext', fontsize='11')

# ============================================================
# Row alignment via rank=same subgraphs
# ============================================================
# Row 1: Sensors (left-to-right)
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('v_sensor'); s.node('r10')
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('t_sensor'); s.node('r20')

# Row 2: MCU (center)
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('mcu'); s.node('r30')

# Row 3: Storage + CAN (left-to-right)
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('storage'); s.node('r40')
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('can'); s.node('r50')

# Row 4: Display
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('display'); s.node('r60')

# ============================================================
# Lead lines: thin dotted, no arrowhead, constraint=false
# ============================================================
g.edge('r10', 'v_sensor', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r20', 't_sensor', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r30', 'mcu', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r40', 'storage', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r50', 'can', style='dotted', penwidth='0.35',
       arrowhead='none', constraint='false')
g.edge('r60', 'display', style='dotted', penwidth='0.35',
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
g.render('test1_bms_block_output', format='svg')
g.render('test1_bms_block_output', format='png')
print('Done: test1_bms_block_output.svg + .png')
