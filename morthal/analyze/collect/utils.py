import ast
from dataclasses import dataclass
from typing import Any

import polars as pl
from pydantic import BaseModel

from morthal.utils.df import empty_df_from_model


@dataclass
class FuncArgsStats:
    n_func_args : int
    n_func_args_annotated : int


def get_func_args_stats(func_ast : ast.FunctionDef | ast.AsyncFunctionDef) -> FuncArgsStats:
    return FuncArgsStats(
        n_func_args = len(func_ast.args.args),
        n_func_args_annotated = sum(arg.annotation is not None for arg in func_ast.args.args)
    )


def dicts_to_df(
    dicts_list: list[dict[str, Any]],
    row_model: BaseModel,
) -> pl.DataFrame:
    if len(dicts_list) == 0:
        return empty_df_from_model(row_model)
    return pl.DataFrame(dicts_list)