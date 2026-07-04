from pathlib import Path

import polars as pl

from morthal.analyze.recap import CodeRecap, RecapFields
from morthal.utils.store import Store


recap = CodeRecap(
    recap=RecapFields(
        total_funcs=10,
        avg_depth=2.5,
        median_depth=2.0,
        avg_lines=15.0,
        avg_node_depth_per_func=2.0,
        avg_node_depth=2.0,
        total_args=20,
        annotated_args=15,
        arg_coverage=75.0,
        return_coverage=80.0,
        unannotated_funcs=3,
    ),
    funcs_df=pl.DataFrame({"x": [1, 2, 3]}),
)


def test_store_starts_empty(tmpdir):
    store = Store(Path(tmpdir), "some/target")
    assert not store.has_cached_recap


def test_store_caches_and_loads_recap(tmpdir):
    store = Store(Path(tmpdir), "some/target")
    store.save_recap(recap)
    assert store.has_cached_recap

    loaded = store.load_recap()
    assert loaded.total_funcs == 10
    assert loaded.avg_depth == 2.5


def test_store_mismatched_target_clears_cache(tmpdir):
    tmppath = Path(tmpdir)
    store = Store(tmppath, "first/target")
    store.save_recap(recap)
    assert store.has_cached_recap

    store2 = Store(tmppath, "different/target")
    assert not store2.has_cached_recap


def test_store_force_clears_cache(tmpdir):
    tmppath = Path(tmpdir)
    store = Store(tmppath, "some/target")
    store.save_recap(recap)
    assert store.has_cached_recap

    store2 = Store(tmppath, "some/target", force=False)
    assert store2.has_cached_recap


def test_store_force_clears_cache(tmpdir):
    tmppath = Path(tmpdir)
    store = Store(tmppath, "some/target")
    store.save_recap(recap)
    assert store.has_cached_recap

    store2 = Store(tmppath, "some/target", force=True)
    assert not store2.has_cached_recap
