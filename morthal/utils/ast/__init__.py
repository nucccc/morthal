import ast

ELDEN_TYPES: list[type] = [
    ast.Module,
    ast.ClassDef,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
]


def skip_depth_aug(
    ast_node: ast.AST,
    parent: ast.AST | None,
) -> bool:
    return isinstance(ast_node, ast.ExceptHandler) or isinstance(ast_node, ast.Module) or isinstance(parent, ast.Module)


def parentify(
    ast_node: ast.AST,
    parent: ast.AST | None = None,
    elden: ast.AST | None = None,
    depth: int = 0
):
    if not skip_depth_aug(ast_node=ast_node, parent=parent):
        depth += 1

    ast_node.parent = parent
    ast_node.elden = elden
    ast_node.depth = depth

    # updating elden depths in case there is actually an elden
    if elden:
        relative_depth = depth - elden.depth
        elden.relative_node_depths.append(relative_depth)
        if isinstance(ast_node, ast.expr):
            elden.relative_expr_depths.append(relative_depth)

    # updating elden in case the node type is of type elden
    for elden_type in ELDEN_TYPES:
        if isinstance(ast_node, elden_type):
            # make ast_node an elden
            ast_node.relative_node_depths = []
            ast_node.relative_expr_depths = []
            # set elden to the ast_node
            elden = ast_node

            # no need to go on
            break

    for ast_child in ast.iter_child_nodes(ast_node):
        # ast_child.parent = ast_node
        parentify(
            ast_node=ast_child,
            parent=ast_node,
            elden=elden,
            depth=depth,
        )