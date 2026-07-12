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
