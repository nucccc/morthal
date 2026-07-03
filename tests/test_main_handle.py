import tempfile
import zipfile
from pathlib import Path

import pytest

from morthal.main import handle
from morthal.utils.codebase import LocalCodebase
from morthal.utils.store import Store


def test_handle(tmpdir):
    extract_dir = tempfile.mkdtemp()
    with zipfile.ZipFile('tests/examples/test_repo.zip', 'r') as zref:
        zref.extractall(extract_dir)
    target_path = Path(extract_dir) / 'morthal_test_repo'

    codebase = LocalCodebase(target_path)
    store = Store(path=Path(tmpdir), target=codebase.name, force=True)
    handle(target=codebase, store=store, report=False, history=True)

    history_df = store.load_history()

    assert history_df.shape[0] == 4

    codebase.dispose()
