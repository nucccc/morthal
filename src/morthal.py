import ast
import inspect
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import polars as pl
from pydantic import BaseModel


def is_py_file(filename : str) -> bool:
    '''
    is_py_file returns True if the filename is a python file
    '''
    return filename[-3:] == '.py'


def calc_func_depth(func_ast: ast.FunctionDef) -> int:
    return max(calc_depth(expr) for expr in func_ast.body)


def calc_depth(expr : ast.AST) -> int:
    depth = 0
    
    if hasattr(expr, 'body'):
        for child_expr in expr.body:
            new_depth = 1 + calc_depth(child_expr)
            depth = max(depth, new_depth)
    # i shall recursively handle also the elsexprs
    if hasattr(expr, 'orelse'):
        for elsexpr in expr.orelse:
            new_depth = calc_depth(elsexpr)
            depth = max(depth, new_depth)                        

    return depth

    
@dataclass
class FuncArgsStats:
    n_func_args : int
    n_func_args_annotated : int

def get_func_args_stats(func_ast : ast.FunctionDef) -> FuncArgsStats:
    '''
    returns statistics ragarding a function's arguments
    '''
    return FuncArgsStats(
        n_func_args = len(func_ast.args.args),
        n_func_args_annotated = sum(arg.annotation is not None for arg in func_ast.args.args)
    )



class FuncStats(BaseModel):
    name: str
    max_depth : int
    n_codelines : int
    n_func_args : int
    n_func_args_annotated : int
    return_annotated : bool
    _docstring: str | None = None

def collect_func_stats(func_ast : ast.FunctionDef) -> FuncStats:
    n_codelines = func_ast.end_lineno - func_ast.lineno
    func_arg_stats = get_func_args_stats(func_ast)

    return FuncStats(
        name=func_ast.name,
        max_depth=calc_func_depth(func_ast),
        n_codelines = n_codelines,
        n_func_args = func_arg_stats.n_func_args,
        n_func_args_annotated = func_arg_stats.n_func_args_annotated,
        return_annotated = func_ast.returns is not None,
        _docstring = ast.get_docstring(func_ast)
    )

def iter_func_asts(ast_mod : ast.Module) -> Iterable[ast.FunctionDef]:
    return filter(lambda x : type(x) is ast.FunctionDef, ast_mod.body)
    
@dataclass
class Dir:
    dirpath : Path
    subfolders : list['Dir']
    pypaths : list[Path]


    @property
    def name(self) -> str:
        return self.dirpath.name

    
    def iter_all_pyfiles(self) -> Iterable[Path]:
        '''
        iterates through all the pyfiles, first by passing through the ones in
        the subfolders and then its pyfiles
        '''
        for subfolder in self.subfolders:
            for pypath in subfolder.iter_all_pyfiles():
                yield pypath
        for pypath in self.pypaths:
            yield pypath


def build_dir(dirpath : Path) -> Dir:
    subfolders : list[Dir] = list()
    pypaths : list[Path] = list()

    for elem in dirpath.iterdir():
        if elem.is_dir():
            subfolders.append( build_dir(elem) )
        elif elem.is_file() and is_py_file(elem.name):
            pypaths.append( elem )

    return Dir(
        dirpath=dirpath,
        subfolders=subfolders,
        pypaths=pypaths
    )

    
@dataclass
class ModStats:
    funcs_stats : dict[str, FuncStats]

    def gen_df(self) -> pl.DataFrame:
        # import pdb; pdb.set_trace()

        for stat in self.funcs_stats.values():
            for name, member in inspect.getmembers(stat):
                if isinstance(member, property):
                    print(name)
                    print(member)
                    print()

        return pl.DataFrame(stat for stat in self.funcs_stats.values())

def collect_modstats(ast_mod : ast.Module) -> ModStats:
    funcs_stats : dict[str, FuncStats] = dict()
    for func_ast in iter_func_asts(ast_mod):
        funcs_stats[func_ast.name] = collect_func_stats(func_ast)
    return ModStats(
        funcs_stats=funcs_stats
    )


def print_func_stats(func_name : str, func_stats : FuncStats):
    print('-'*32)
    print(func_name)
    print('-'*32)
    print(f'\tmax_depth - {func_stats.max_depth}')
    print(f'\tn_codelines - {func_stats.n_codelines}')
    print(f'\tn_func_args - {func_stats.n_func_args}')
    print(f'\tn_func_args_annotated - {func_stats.n_func_args_annotated}')
    print(f'\treturn_annotated - {func_stats.return_annotated}')
    print('-'*32)
    print()


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
