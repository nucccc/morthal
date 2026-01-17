import ast
import sys
from pathlib import Path
from typing import Any

import polars as pl

from .stats import collect_func_stats
from .utils.path import iter_pyfiles

def get_funcs_df(root_path: Path) -> pl.DataFrame:
    dicts_list: list[dict[str, Any]] = []

    for pypath in iter_pyfiles(root_path):
        ast_mod = ast.parse(pypath.read_text())

        pypath_add = {"fpath":str(pypath)}

        for fstats in collect_func_stats(ast_mod):
            fdata = fstats.model_dump()
            fdata.update(pypath_add)
            dicts_list.append(fdata)

    return pl.DataFrame(dicts_list)

default_path = "/home/nucccc/cod/projs/sqlmodelgen"

get_funcs_df(Path("/home/nucccc/cod/projs/sqlmodelgen")).write_csv("data.csv")

