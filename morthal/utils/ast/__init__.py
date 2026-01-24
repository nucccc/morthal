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
        if isinstance(ast_node, ast.stmt):
            elden.relative_expr_depths.append(relative_depth)
            
            elden_col_offset = 0 if isinstance(elden, ast.Module) else elden.col_offset

            elden.relative_stmt_depths.append(ast_node.col_offset - elden_col_offset)

    # updating elden in case the node type is of type elden
    for elden_type in ELDEN_TYPES:
        if isinstance(ast_node, elden_type):
            # make ast_node an elden
            ast_node.relative_node_depths = []
            ast_node.relative_expr_depths = []
            ast_node.relative_stmt_depths = []
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


def identify_tab_offset(ast_expr: ast.stmt) -> int:
    '''
    identify_tab_offset's duty is to recognise inside a module which is the
    offset corresponding to an indentation
    '''
    child_exprs: list[ast.expr] = []
    for ast_child in ast.iter_child_nodes(ast_expr):

        if isinstance(ast_child, ast.stmt):
            # check necessary to avoid column offset on ast.Module on first
            # invocation
            if isinstance(ast_expr, ast.stmt):
                off_diff = ast_child.col_offset - ast_expr.col_offset
                if off_diff != 0:
                    return off_diff
            child_exprs.append(ast_child)

    for child_expr in child_exprs:
        tab_offset = identify_tab_offset(child_expr)
        if tab_offset != 0:
            return tab_offset
            
    return 0