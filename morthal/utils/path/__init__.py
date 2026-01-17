'''
utilities for path
'''

from pathlib import Path
from typing import Generator


def iter_pyfiles(root_path: Path) -> Generator[Path, None, None]:
    for elem in root_path.iterdir():
        if elem.is_dir():
            for pyfile in iter_pyfiles(elem):
                yield pyfile
        elif elem.is_file() and elem.name.endswith('.py'):
            yield elem