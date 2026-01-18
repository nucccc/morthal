import ast

ELDEN_TYPES: list[type] = [
    ast.Module,
    ast.ClassDef,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
]

def parentify(
    ast_node: ast.AST,
    parent: ast.AST | None = None,
    elden: ast.AST | None = None,
):
    ast_node.parent = parent
    ast_node.elden = elden

    # updating elden in case the node type is of type elden
    for elden_type in ELDEN_TYPES:
        if isinstance(ast_node, elden_type):
            elden = ast_node

    for ast_child in ast.iter_child_nodes(ast_node):
        # ast_child.parent = ast_node
        parentify(ast_child, parent=ast_node, elden=elden)