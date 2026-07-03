import shutil
import tempfile
from pathlib import Path
from typing import Protocol

from morthal.vcs import clone_repo, normalize_url


# TODO: elegant method to verify if a git repositoy is found
# or not, so that when using with history an elegant error
# can be given to the user
class Codebase(Protocol):
    '''
    Codebase is meant to be a protocol for classes serving
    properties of the actual repo
    '''

    def dispose(self) -> None: ...

    @property
    def repo_path(self) -> Path: ...

    @property
    def name(self) -> str: ...


class LocalCodebase:

    def __init__(self, path: Path) -> None:
        self._target_path = path

    def dispose(self) -> None:
        pass 

    @property
    def repo_path(self) -> Path:
        return self._target_path
    
    @property
    def name(self) -> str:
        return str(self._target_path)


class GitCodebase:

    def __init__(self, url: str) -> None:
        # TODO: elegantly reject and report invalid urls
        self._url = normalize_url(url)

        self._tmpdir = tempfile.mkdtemp(prefix='morthal_')
        self._target_path = Path(self._tmpdir) / 'repo'
        
        clone_repo(normalize_url(url), self._target_path)

    def dispose(self) -> None:
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    @property
    def repo_path(self) -> Path:
        return self._target_path
    
    @property
    def name(self) -> str:
        return self._url
