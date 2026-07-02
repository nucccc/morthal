from pathlib import Path

import pytest

from morthal.utils.store import Store


def test_store_manifest(tmpdir):
    tmppath = Path(tmpdir)

    store = Store(tmppath)

    assert not store.manifest_matches('whatver-target')