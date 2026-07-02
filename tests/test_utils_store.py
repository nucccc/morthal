from pathlib import Path

import polars as pl

from morthal.analyze.recap import CodeRecap
from morthal.utils.store import Store


def test_store_starts_empty(tmpdir):
    store = Store(Path(tmpdir), "some/target")
    assert not store.has_cached_recap


def test_store_caches_and_loads_recap(tmpdir):
    store = Store(Path(tmpdir), "some/target")
    recap = CodeRecap(
        total_funcs=10,
        avg_depth=2.5,
        median_depth=2.0,
        avg_lines=15.0,
        total_args=20,
        annotated_args=15,
        arg_coverage=75.0,
        return_coverage=80.0,
        deep_funcs=1,
        long_funcs=2,
        unannotated_funcs=3,
        depth_threshold=5,
        lines_threshold=50,
        funcs_df=pl.DataFrame({"x": [1, 2, 3]}),
    )
    store.save_recap(recap)
    assert store.has_cached_recap

    loaded = store.load_recap()
    assert loaded.total_funcs == 10
    assert loaded.avg_depth == 2.5


def test_store_mismatched_target_clears_cache(tmpdir):
    tmppath = Path(tmpdir)
    store = Store(tmppath, "first/target")
    recap = CodeRecap(
        total_funcs=5,
        avg_depth=1.0,
        median_depth=1.0,
        avg_lines=10.0,
        total_args=5,
        annotated_args=5,
        arg_coverage=100.0,
        return_coverage=100.0,
        deep_funcs=0,
        long_funcs=0,
        unannotated_funcs=0,
        depth_threshold=5,
        lines_threshold=50,
        funcs_df=pl.DataFrame({"x": [1]}),
    )
    store.save_recap(recap)
    assert store.has_cached_recap

    store2 = Store(tmppath, "different/target")
    assert not store2.has_cached_recap


def test_store_force_clears_cache(tmpdir):
    tmppath = Path(tmpdir)
    store = Store(tmppath, "some/target")
    recap = CodeRecap(
        total_funcs=5,
        avg_depth=1.0,
        median_depth=1.0,
        avg_lines=10.0,
        total_args=5,
        annotated_args=5,
        arg_coverage=100.0,
        return_coverage=100.0,
        deep_funcs=0,
        long_funcs=0,
        unannotated_funcs=0,
        depth_threshold=5,
        lines_threshold=50,
        funcs_df=pl.DataFrame({"x": [1]}),
    )
    store.save_recap(recap)
    assert store.has_cached_recap

    store2 = Store(tmppath, "some/target", force=False)
    assert store2.has_cached_recap


def test_store_force_clears_cache(tmpdir):
    tmppath = Path(tmpdir)
    store = Store(tmppath, "some/target")
    recap = CodeRecap(
        total_funcs=5,
        avg_depth=1.0,
        median_depth=1.0,
        avg_lines=10.0,
        total_args=5,
        annotated_args=5,
        arg_coverage=100.0,
        return_coverage=100.0,
        deep_funcs=0,
        long_funcs=0,
        unannotated_funcs=0,
        depth_threshold=5,
        lines_threshold=50,
        funcs_df=pl.DataFrame({"x": [1]}),
    )
    store.save_recap(recap)
    assert store.has_cached_recap

    store2 = Store(tmppath, "some/target", force=True)
    assert not store2.has_cached_recap