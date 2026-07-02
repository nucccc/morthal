import polars as pl

from morthal.analyze.collect import FuncStats
from morthal.utils.df import empty_df_from_model

def test_empty_db_from_model() -> pl.DataFrame:
    empty_df = empty_df_from_model(FuncStats)

    assert empty_df.shape[0] == 0
    assert 'name' in empty_df.columns
    assert 'n_exprs' in empty_df.columns
    assert 'n_nodes' in empty_df.columns