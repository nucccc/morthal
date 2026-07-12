import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator

from .data import (
    CodebaseData,
    CodebaseDataBuilder,
    FuncStats,
)
from morthal.utils.ast import (
    ModCounts,
    NodeSink,
    identify_tab_offset,
    enrich
)
from morthal.utils.path import iter_pyfiles
from morthal.utils.calc import max_and_avg

from .utils import get_func_args_stats


def collect_codebase_data(codebase_path: Path) -> CodebaseData:
    cbuilder = CodebaseDataBuilder()

    for pypath in iter_pyfiles(codebase_path):
        local_path_str = str(pypath.relative_to(codebase_path))
        collect_pyfile(pypath, cbuilder, local_path_str)
    
    return cbuilder.build()


def collect_pyfile(
    filepath: Path,
    cbuilder: CodebaseDataBuilder,
    local_path_str: str,
):
    ast_mod = ast.parse(filepath.read_text())
    mcounts = ModCounts()
    # declaring a nodesink where nodes of interest can be
    # stored during enrichment in order to avoid iterating
    # again the tree
    nsink = NodeSink()
    # enriching the abstract syntax tree of the module,
    # passing the node sink to avoid rewalking again the tree
    enrich(ast_mod, node_sink=nsink, cpf=mcounts)

    tab_offset = identify_tab_offset(ast_mod)
    pypath_add = {"fpath":str(local_path_str)}

    for func_ast in nsink.funcs:
        fstats = collect_func_stats(func_ast, tab_offset)
        fdata = fstats.model_dump()
        fdata.update(pypath_add)
        cbuilder.add_func(fdata)

    # collecting filedata in the end
    cbuilder.add_file({
        'fpath':str(local_path_str),
        'n_nodes':mcounts.n_nodes,
        'n_startements':mcounts.n_stmts,
    })


def collect_func_stats(
    func_ast : ast.FunctionDef | ast.AsyncFunctionDef,
    tab_offset: int,
) -> FuncStats:
    n_codelines = func_ast.end_lineno - func_ast.lineno
    func_arg_stats = get_func_args_stats(func_ast)

    max_node_depth, avg_node_depth = max_and_avg(func_ast.relative_node_depths)
    max_stmt_depth, avg_stmt_depth = max_and_avg(func_ast.relative_stmt_depths)

    if tab_offset > 0:
        max_stmt_depth = int(max_stmt_depth / tab_offset)
        avg_stmt_depth = avg_stmt_depth / tab_offset

    parent_name = None
    if hasattr(func_ast, 'elden') and hasattr(func_ast.elden, 'name'):
        parent_name = func_ast.elden.name

    return FuncStats(
        name=func_ast.name,
        parent_name=parent_name,
        name_len=len(func_ast.name),
        max_node_depth=max_node_depth,
        max_stmt_depth=max_stmt_depth,
        avg_node_depth=avg_node_depth,
        avg_stmt_depth=avg_stmt_depth,
        n_codelines = n_codelines,
        n_exprs=len(func_ast.relative_stmt_depths),
        n_nodes=len(func_ast.relative_node_depths),
        n_func_args = func_arg_stats.n_func_args,
        n_func_args_annotated = func_arg_stats.n_func_args_annotated,
        return_annotated = func_ast.returns is not None,
        docstring = ast.get_docstring(func_ast)
    )
