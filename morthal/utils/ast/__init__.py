import ast
from dataclasses import dataclass, field


@dataclass
class NodeSink:
    funcs: list[ast.FunctionDef | ast.AsyncFunctionDef] = field(
        default_factory=lambda:[]
    )


# as a concept an "elden" is supposed to be an abstract syntax
# tree node at which the depth calculations "reset". the idea is
# that if a function is defined inside another function, then the
# nodes of that function shall count for it and not the parent
# function. just to give an example:
#
#   def a():
#
#       def b():
#
#           return 42
#
# in this example "b" has just one node, which is an ast.Return
# actually returning 42. I wouldn't like its depth to be measured
# considering function "a" as its "root"; instead I want its root
# to be "b", so I named this root concept as "elden", and function
# "b" is the elden of the return node. in case these example
# functions were to be more complicated the nodes inside "b" would
# refer to "b", and the other nodes inside "a" refer to "a"... to
# continue on the example:
# 
#   def a():
#       var2 = 1                    <- "a" is the elden
#
#       def b():
#           var2 = 2                <- "b" is the elden
#           return 42               <- "b" is the elden
#
#       var3 = 3                    <- "a" is the elden
#       return var1 + b() + var3    <- "a" is the elden
#
# this I hope gives an idea of what I consider as an elden... that
# is used mainly to avoid methods suffer from having one more level
# of depth just because they are children of a class node
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


# TODO: find a smart way to let this function accumulate somewhere
# elden nodes so that a second traversal is avoided
def enrich(
    ast_node: ast.AST,
    parent: ast.AST | None = None,
    elden: ast.AST | None = None,
    depth: int = 0,
    node_sink: NodeSink | None = None,
):
    '''
    enrich shall augment an abstract syntax tree with several
    attributes necessary for stats calculation

    it is designed to perform several important activities in
    just one passage, and that's why a lot of references to
    other nodes are provided in input, together with the depth

    the references to parent and elden ast nodes are used to
    let their attributes be directly modified by the child the
    function is currently working on. in this way we avoid
    a second tree traversal in which the child nodes would be
    counted and their depths summed up to obtain the average
    indicators on which this project relies

    so in practics this function recursively visits all ast
    nodes in an abstract syntax tree and calculates their
    depths (there are different types of depth) and attaches
    that data to their elden/parent-functions/whatever

    anyways a second node traversal is necessary to then retrieve
    the eldens, so maybe it could become smart at one point to just
    store theme in a buffer passed on from invocation to invocation
    '''
    if not skip_depth_aug(ast_node=ast_node, parent=parent):
        depth += 1

    ast_node.parent = parent
    ast_node.elden = elden
    ast_node.depth = depth

    # TODO: at the moment to calculate average value lists are
    # used... for performance reasons at one point it could be
    # smart to just have numerical attributes in elden nodes to
    # which depth values and counters are added, these numbers can
    # be used to calculate the averages without the neccessity of
    # having a list (whose usage might involve dynamic memory
    # allocation, hurting the performances)

    # updating elden depths in case there is actually an elden
    if elden:
        relative_depth = depth - elden.depth
        elden.relative_node_depths.append(relative_depth)
        if isinstance(ast_node, ast.stmt):
            elden.relative_expr_depths.append(relative_depth)
            
            elden_col_offset = 0 if isinstance(elden, ast.Module) else elden.col_offset

            elden.relative_stmt_depths.append(ast_node.col_offset - elden_col_offset)

    # updating elden in case the node type is of type elden
    if any(isinstance(ast_node, elden_type) for elden_type in ELDEN_TYPES):
        # make ast_node an elden, which basically means
        # adding some list attributes to let depths be appended
        # to it
        ast_node.relative_node_depths = []
        ast_node.relative_expr_depths = []
        ast_node.relative_stmt_depths = []
        # set elden to the ast_node
        elden = ast_node

    if node_sink is not None and (isinstance(ast_node, ast.FunctionDef) or isinstance(ast_node, ast.AsyncFunctionDef)):
        node_sink.funcs.append(ast_node)

    # recursive step: for every child of the current node, invoke
    # enrich on it
    for ast_child in ast.iter_child_nodes(ast_node):
        # ast_child.parent = ast_node
        enrich(
            ast_node=ast_child,
            parent=ast_node,
            elden=elden,
            depth=depth,
            node_sink=node_sink,
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