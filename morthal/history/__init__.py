import tempfile
from datetime import datetime
from pathlib import Path

from git import Repo

from morthal.analyze.collect import collect_repo_data
from morthal.analyze.recap import Commit, RepoHistory, build_repo_recap


def walk_commit_history(repo_path: Path) -> RepoHistory:
    repo = Repo(repo_path)
    history = RepoHistory(history=[])
    py_commits = list(iter_pyfile_commits(repo))

    for i, git_commit in enumerate(reversed(py_commits)):
        commit = Commit(
            hash=git_commit.hexsha,
            dt=datetime.fromtimestamp(git_commit.committed_date),
            author=git_commit.author.name,
            message=git_commit.message.strip(),
        )

        with tempfile.TemporaryDirectory(prefix="morthal_extract_") as xtmp:
            extract_py_files(repo, git_commit.hexsha, Path(xtmp))
            cd = collect_repo_data(Path(xtmp))
            cr = build_repo_recap(cd)
            history.history.append((commit, cr))

        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(py_commits)} commits")

    print(f"Processed {len(history.history)} commits")
    return history


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
