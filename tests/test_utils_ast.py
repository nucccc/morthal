import ast

from morthal.utils.ast import parentify

def verify_parents(ast_node: ast.AST, parent: ast.AST | None = None):
    if parent is not None:
        assert ast_node.parent is parent
    for child in ast.iter_child_nodes(ast_node):
        verify_parents(ast_node=child, parent=ast_node)

def test_parentify():
    ast_mod = ast.parse('''a = 0
def a_func():
    if True:
        return None''')
    
    parentify(ast_mod)

    verify_parents(ast_node=ast_mod)