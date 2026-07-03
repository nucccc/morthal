'''
testing codebase utilities
'''

from pathlib import Path

import pytest

from morthal.utils.codebase import LocalCodebase


# TODO: check the best way to have a temporary directory in this project
def test_local_codebase(tmp_path):
    lc = LocalCodebase(path=Path(tmp_path))
    
    assert lc.path == Path(tmp_path)
    assert lc.name == str(tmp_path)
