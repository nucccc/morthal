import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Generator

import polars as pl
from pydantic import BaseModel


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


@dataclass
class ModExploration:
    pass


def explore_mod(ast_mod: ast.Module, code: str) -> ModExploration:
    pass


class FuncStats(BaseModel):
    name: str
    max_depth : int
    n_codelines : int
    n_exprs : int
    n_func_args : int
    n_func_args_annotated : int
    return_annotated : bool
    _docstring: str | None = None

    @classmethod
    def from_ast(cls, func_ast : ast.FunctionDef) -> 'FuncStats':
        n_codelines = func_ast.end_lineno - func_ast.lineno
        func_arg_stats = get_func_args_stats(func_ast)

        return FuncStats(
            name=func_ast.name,
            max_depth=calc_func_depth(func_ast),
            n_codelines = n_codelines,
            n_exprs=count_exprs(func_ast),
            n_func_args = func_arg_stats.n_func_args,
            n_func_args_annotated = func_arg_stats.n_func_args_annotated,
            return_annotated = func_ast.returns is not None,
            _docstring = ast.get_docstring(func_ast)
        )


def collect_func_stats(ast_mod : ast.Module) -> Generator[FuncStats, None, None]:
    for ast_node in ast.walk(ast_mod):
        if isinstance(ast_node, ast.FunctionDef) or isinstance(ast_node, ast.AsyncFunctionDef):
            yield FuncStats.from_ast(ast_node)


def eval_pypath_mod(pypath) -> pl.DataFrame:
    with open(pypath, 'r') as f:
        code = f.read()
    ast_mod = ast.parse(code)
    mod_stats = collect_modstats(ast_mod=ast_mod)
    for func_name, func_stats in mod_stats.funcs_stats.items():
        print_func_stats(func_name, func_stats)
    # wouldn't it be nice to return the dataframe
    df = mod_stats.gen_df()
    return df



if __name__ == '__main__':
    print('codestats')
    n = len(sys.argv)
    for i in range(1, n):
        print(sys.argv[i])
    if n < 2:
        print('not enough commands')
    folderpath = Path(sys.argv[1])
    
    dir = build_dir(folderpath)
    dfs: list[pl.DataFrame] = list()
    dfs_by_path: dict[Path, pl.DataFrame] = dict()
    for pypath in dir.iter_all_pyfiles():
        df = eval_pypath_mod(pypath)
        dfs.append(df)
        dfs_by_path[pypath] = df

    # generate the final dataframe
    final_df = pl.concat(df.with_columns() for path, df in dfs_by_path.items() )
