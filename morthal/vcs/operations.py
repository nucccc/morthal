from pathlib import Path

from git import Repo


def clone_repo(url: str, dest: Path) -> Repo:
    dest.mkdir(parents=True, exist_ok=True)
    return Repo.clone_from(url, dest)


def _commit_touches_py(commit) -> bool:
    if not commit.parents:
        return any(
            entry.type == 'blob' and entry.path.endswith('.py')
            for entry in commit.tree.traverse()
        )
    for path in commit.stats.files:
        if path.endswith('.py'):
            return True
    return False


def iter_pyfile_commits(repo: Repo):
    for commit in repo.iter_commits():
        if _commit_touches_py(commit):
            yield commit


def extract_py_files(repo: Repo, commit_hexsha: str, dest: Path) -> None:
    commit = repo.commit(commit_hexsha)
    for entry in commit.tree.traverse():
        if entry.type == 'blob' and entry.path.endswith('.py'):
            file_path = dest / entry.path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(entry.data_stream.read())
