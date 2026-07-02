import datetime
import types
import typing
from typing import get_args, get_origin

import polars as pl
from pydantic import BaseModel


def pydantic_to_polars_schema(model: type[BaseModel]) -> dict[str, pl.DataType]:
    """Build a Polars schema dict from a Pydantic BaseModel class."""
    schema = {}
    for name, field in model.model_fields.items():
        schema[name] = _map_type(field.annotation)
    return schema


def _map_type(annotation) -> pl.DataType:
    # Unwrap Optional[X] / X | None
    origin = get_origin(annotation)
    if origin is typing.Union or origin is types.UnionType:
        args = [a for a in get_args(annotation) if a is not type(None)]
        if len(args) == 1:
            return _map_type(args[0])
        # fallback for multi-type unions
        return pl.Object

    # Lists / sequences -> pl.List
    if origin in (list, set, frozenset, tuple):
        args = get_args(annotation)
        inner = _map_type(args[0]) if args else pl.Object
        return pl.List(inner)

    # Dicts -> pl.Struct is awkward without concrete keys; fall back to Object
    if origin is dict:
        return pl.Object

    # Nested pydantic model -> pl.Struct
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return pl.Struct(pydantic_to_polars_schema(annotation))

    mapping = {
        int: pl.Int64,
        float: pl.Float64,
        str: pl.Utf8,
        bool: pl.Boolean,
        bytes: pl.Binary,
        datetime.datetime: pl.Datetime,
        datetime.date: pl.Date,
        datetime.time: pl.Time,
        datetime.timedelta: pl.Duration,
    }
    return mapping.get(annotation, pl.Object)


def empty_df_from_model(model: type[BaseModel]) -> pl.DataFrame:
    return pl.DataFrame(schema=pydantic_to_polars_schema(model))