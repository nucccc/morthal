import tempfile
from datetime import datetime
from pathlib import Path

from git import Repo

from morthal.analyze.collect import collect_repo_data
from morthal.analyze.recap import Commit, RepoHistory, build_repo_recap
from morthal.vcs import iter_pyfile_commits, extract_py_files


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