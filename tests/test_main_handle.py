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

    assert history_df['message'][0] == 'second commit'
    assert history_df['message'][1] == 'third commit'
    assert history_df['message'][2] == 'fourth commit'
    assert history_df['message'][3] == 'fifth commit'

    assert history_df['return_coverage'][3] == 100.0

    assert history_df['avg_lines'][1] == 1.0
    assert history_df['avg_lines'][2] == 1.0
    assert history_df['avg_lines'][3] == 1.5

    codebase.dispose()
