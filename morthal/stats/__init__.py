import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator

import polars as pl
from pydantic import BaseModel

from morthal.utils.ast import identify_tab_offset, parentify
from morthal.utils.calc import max_and_avg
from morthal.utils.path import iter_pyfiles


# args out of which the depth is calculated
DEPTH_ARGS = ['body', 'handlers', 'orelse', 'finalbody']


def calc_func_depth(func_ast: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    return max(calc_depth(expr) for expr in func_ast.body)


def calc_depth(expr : ast.AST) -> int:
    # TODO: add functionality to have nodes stopping stuff, like if you meet
    # a function def stop there don't go further

    depth = 0

    for arg in DEPTH_ARGS:
        if not hasattr(expr, arg):
            continue

        for child_expr in getattr(expr, arg):
            new_depth = 1 if arg != 'handlers' else 0
            new_depth += calc_depth(child_expr)
            depth = max(depth, new_depth)

    return depth


@dataclass
class RepoData:
    n_files: int
    funcs_df: pl.DataFrame


def collect_repo_data(root_path: Path) -> RepoData:
    n_files = 0
    dicts_list: list[dict[str, Any]] = []

    for pypath in iter_pyfiles(root_path):
        n_files += 1

        for fdata in collect_stats(pypath):
            # NOTE: maybe at a point use extend
            dicts_list.append(fdata)

    return RepoData(
        n_files=n_files,
        funcs_df=pl.DataFrame(dicts_list)
    )



# NOTE: a little bit of over engineering...  
@dataclass
class FuncArgsStats:
    n_func_args : int
    n_func_args_annotated : int

def get_func_args_stats(func_ast : ast.FunctionDef | ast.AsyncFunctionDef) -> FuncArgsStats:
    '''
    returns statistics ragarding a function's arguments
    '''
    return FuncArgsStats(
        n_func_args = len(func_ast.args.args),
        n_func_args_annotated = sum(arg.annotation is not None for arg in func_ast.args.args)
    )


def count_exprs(func_ast: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    count = 0
    for elem in ast.walk(func_ast):
        if isinstance(elem, ast.expr):
            count += 1
    return count


class FuncStats(BaseModel):
    name: str
    parent_name: str | None
    name_len: int
    max_node_depth: int
    max_stmt_depth: int
    avg_node_depth: float
    avg_stmt_depth: float
    n_codelines: int
    n_exprs: int
    n_nodes: int
    n_func_args : int
    n_func_args_annotated : int
    return_annotated : bool
    docstring: str | None = None

    @classmethod
    def from_ast(cls, func_ast : ast.FunctionDef, tab_offset: int) -> 'FuncStats':
        '''
        this shall assume the ast was "parentified"
        '''
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
    

# NOTE: at the moment only func stats are returned for a pypath, but one day if
# class stats or other stuff is collected
def collect_stats(pypath: Path) -> Generator[dict[str, Any], None, None]:
    ast_mod = ast.parse(pypath.read_text())
    parentify(ast_mod)

    tab_offset = identify_tab_offset(ast_mod)
    pypath_add = {"fpath":str(pypath)}

    for fstats in collect_func_stats(ast_mod, tab_offset):
        fdata = fstats.model_dump()
        fdata.update(pypath_add)
        yield fdata

def collect_func_stats(ast_mod: ast.Module, tab_offset: int) -> Generator[FuncStats, None, None]:
    for ast_node in ast.walk(ast_mod):
        if isinstance(ast_node, ast.FunctionDef) or isinstance(ast_node, ast.AsyncFunctionDef):
            yield FuncStats.from_ast(ast_node, tab_offset)
