"""Morthal CLI — Python code analysis toolkit"""

import argparse
import tempfile
from datetime import datetime
from pathlib import Path

from git import Repo

from .analyze.collect import collect_repo_data
from .analyze.recap import Commit, RepoHistory, build_repo_recap
from .reporter import HTMLReporter
from .utils.store import Store
from .vcs import normalize_url, clone_repo, iter_pyfile_commits, extract_py_files


def _walk_commit_history(repo_path: Path) -> RepoHistory:
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


def handle(
    target_path: Path,
    support_path: Path,
    force: bool,
    report: bool,
    history: bool,
    # args: argparse.Namespace,
) -> None:
    store = Store(support_path, str(target_path.resolve()), force=force)

    if store.has_cached_recap:
        recap = store.load_recap()
    else:
        repo_data = collect_repo_data(target_path)
        recap = build_repo_recap(repo_data)
        store.save_recap(recap)

    if report:
        reporter = HTMLReporter(recap)
        reporter.generate(store.path / "report.html")

    if history:
        print("Walking commit history ...")
        history = _walk_commit_history(target_path)
        csv_path = store.path / "commit_history.csv"
        history.to_csv(csv_path)
        print(f"Commit history saved to: {csv_path.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze Python codebases and generate reports",
    )
    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument(
        "--path", "-p",
        type=Path,
        default=None,
        help="Local directory to analyze (default: current directory)",
    )
    target_group.add_argument(
        "--github", "-g",
        type=str,
        default=None,
        help="GitHub URL — owner/repo, github.com/owner/repo, or full URL",
    )
    parser.add_argument(
        "--support-dir",
        "-s",
        type=Path,
        default=None,
        help="Cache/working directory (default: {target}/.morthal for local, ./.morthal for GitHub)",
    )
    parser.add_argument(
        "--report",
        "-r",
        action="store_true",
        help="Generate HTML report in the support directory",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force re-collection, ignoring cached data",
    )
    parser.add_argument(
        "--history",
        "-H",
        action="store_true",
        help="Walk commit history and output CSV",
    )

    args = parser.parse_args()

    if args.github:
        url = normalize_url(args.github)
        print(f"Cloning {url} ...")
        with tempfile.TemporaryDirectory(prefix="morthal_") as tmp:
            clone_path = Path(tmp) / "repo"
            clone_repo(url, clone_path)
            print(f"Cloned to {clone_path}")
            if not args.support_dir:
                args.support_dir = Path(".morthal")
            handle(
                target_path=clone_path,
                support_path=args.support_dir,
                force=args.force,
                report=args.report,
                history=args.history,
            )
    else:
        target_path = args.path or Path(".")
        if not args.support_dir:
            args.support_dir = target_path / ".morthal"
        handle(
            target_path=target_path,
            support_path=args.support_dir,
            force=args.force,
            report=args.report,
            history=args.history,
        )


if __name__ == "__main__":
    main()
