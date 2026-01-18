import ast

def parentify(ast_node: ast.AST):
    for ast_child in ast.iter_child_nodes(ast_node):
        ast_child.parent = ast_node
        parentify(ast_child)