from typing import Any

import polars as pl
from pydantic import BaseModel

from morthal.utils.df import empty_df_from_model


def dicts_to_df(
    dicts_list: list[dict[str, Any]],
    row_model: BaseModel,
) -> pl.DataFrame:
    if len(dicts_list) == 0:
        return empty_df_from_model(row_model)
    return pl.DataFrame(dicts_list)