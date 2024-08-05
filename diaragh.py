from graphviz import Digraph

dot = Digraph(comment='The Test Table', format='png')

# 设置图的属性
dot.attr(rankdir='LR', size='8,5')

# 设置节点的属性
dot.attr('node', shape='rectangle', style='filled', color='lightblue2', fontname='Helvetica')

# 添加节点
dot.node('A', 'Start')
dot.node('B', 'Step 1: Choose Model')
dot.node('C', 'Step 2: Set Parameters')
dot.node('D', 'Step 3: Fit Model')
dot.node('E', 'Step 4: Evaluate Model')
dot.node('F', 'End', shape='Msquare', color='lightgrey')

# 添加边
dot.edges(['AB', 'BC', 'CD', 'DE'])
dot.edge('E', 'F', label='process done', fontsize='10')

# 输出图形
dot.render('test-output/round-table-styled', view=True)
