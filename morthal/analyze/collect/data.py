from dataclasses import dataclass, field
from typing import Any

import polars as pl
from pydantic import BaseModel

from .utils import dicts_to_df


@dataclass
class CodebaseData:
    files_df: pl.DataFrame
    funcs_df: pl.DataFrame


@dataclass
class CodebaseDataBuilder:
    _files_dicts: list[dict] = field(default_factory=lambda:[])
    _funcs_dicts: list[dict] = field(default_factory=lambda:[])

    def build(self) -> CodebaseData:
        return CodebaseData(
            files_df=pl.DataFrame(self._files_dicts),
            funcs_df=dicts_to_df(self._funcs_dicts, FuncStats),
        )


    def add_file(self, file_dict: dict[str, Any]):
        self._files_dicts.append(file_dict)


    def add_func(self, func_dict: dict[str, Any]):
        self._funcs_dicts.append(func_dict)


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

"""
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
"""
